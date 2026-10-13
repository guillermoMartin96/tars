"""Approved reference snapshot for the M2 Proof (DR-0021 option A).

Every reference-derived value that reaches an M2 Proof check, a reported result or an
acceptance decision is produced by one of the reference oracles (DOP853, the Kepler
and RK4 anchors, Kepler in O5/O6/node bisection/GMAT alignment, and the scenario-only
predictions). Each oracle passes its outputs through :func:`pin`, which, inside an
active :class:`Session`:

- **verify** (Proof, ``gmat_m2.py compare`` and ``run``): compares the freshly computed
  values with the approved artifact, value by value, within the measured
  reproducibility tolerance of the value's class. A missing, unexpected, non-finite or
  out-of-tolerance value is a problem, and the session's check fails.
- **record** (only ``toolbox/scripts/reference_snapshot.py``): collects the values for
  a candidate artifact.

Outside a session (unit tests calling a helper directly) :func:`pin` returns its inputs
unchanged and checks nothing.

**What the checks consume.** For values computed from scenario inputs ("ref") or from
the committed GMAT rows ("gmat"), :func:`pin` returns the *approved* value once the
runtime value agrees with it, so a deviation inside the tolerance changes no metric and
cannot alter an acceptance decision. Values seeded by simulator output ("sim": the
Kepler states of O5 and O6) depend on the platform's simulator output, so they are
verified but not substituted; :func:`margin_problems` then requires every gated metric
built on them to keep a margin to its limit larger than the worst shift a
within-tolerance deviation could cause.

The artifact is authenticated against the sha256 pinned in
``tars.validation.approved_digests`` before use and is never written by tests, CI or
the Proof (DR-0021 conditions 3 and 5). Agreement with it is not evidence of physical
correctness: that rests on the checks and the GMAT comparison that approved it
(condition 2).
"""

from __future__ import annotations

import contextlib
import contextvars
import gzip
import hashlib
import json
import math
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = 1
SEEDS = ("ref", "sim", "gmat")
# Part names end with their unit; the unit selects the tolerance.
UNIT_SUFFIXES = ("_mps", "_kg", "_m", "_s", "_1")

# Reproducibility tolerances, |runtime - approved| per value, by (seed, unit) (VAL-0015).
# MEASURED: the largest verify-mode deviation over 24 measurements (the reference host,
# GitHub ubuntu-latest and macos-latest hosts; proof/records/evidence/M2-T6/
# reference-snapshot-measurements). Rule (review M2-T6 F59): the smallest 1-2-5 value
# >= max(10 x measured, 10 ulp of the class's largest value in the approved snapshot).
# Counts are exact. Unused classes are 0 (exact): a new value in one fails closed until
# it is measured.
MEASURED: dict[tuple[str, str], float] = {
    ("ref", "m"): 2.7939677238464355e-09,
    ("ref", "mps"): 4.092726157978177e-12,
    ("ref", "kg"): 1.1368683772161603e-13,
    ("ref", "s"): 0.0,
    ("gmat", "m"): 2.016313374042511e-07,  # AVX-512 hosts (Kepler over long GMAT arcs)
    ("gmat", "mps"): 2.523847797419876e-10,
    ("gmat", "s"): 0.0,
    ("sim", "m"): 5.366746336221695e-07,  # inherits the simulator's platform variation
    ("sim", "mps"): 6.589289114344865e-10,
    ("sim", "s"): 0.0,
}
TOLERANCES: dict[tuple[str, str], float] = {
    **{(seed, unit): 0.0 for seed in SEEDS for unit in ("m", "mps", "kg", "s", "1")},
    ("ref", "m"): 5e-8,  # 10 x measured 2.8e-8
    ("ref", "mps"): 5e-11,  # 10 x measured 4.1e-11
    ("ref", "kg"): 5e-12,  # 10 ulp(1300 kg) = 2.3e-12
    ("ref", "s"): 1e-10,  # 10 ulp(53 100 s) = 7.3e-11
    ("gmat", "m"): 5e-6,  # 10 x measured 2.0e-6
    ("gmat", "mps"): 5e-9,  # 10 x measured 2.5e-9
    ("gmat", "s"): 1e-10,  # 10 ulp(53 100 s)
    ("sim", "m"): 1e-5,  # 10 x measured 5.4e-6
    ("sim", "mps"): 1e-8,  # 10 x measured 6.6e-9
    ("sim", "s"): 1e-10,  # 10 ulp(53 700 s)
}

MAX_LISTED = 20  # problems listed per kind; the count is always reported


class SnapshotError(RuntimeError):
    """The approved artifact is missing, unauthenticated or malformed."""


def unit_of(name: str) -> str:
    for suffix in UNIT_SUFFIXES:
        if name.endswith(suffix):
            return suffix[1:]
    raise ValueError(f"reference part {name!r} has no unit suffix {UNIT_SUFFIXES}")


def snapshot_path() -> Path:
    from tars.validation.thresholds import REPO_ROOT

    return REPO_ROOT / "toolbox" / "references" / "snapshot" / "m2" / "REFERENCE_SNAPSHOT.json.gz"


def read_json(path: Path) -> dict[str, Any]:
    """A snapshot file: gzip-compressed JSON (the artifact) or plain JSON."""
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Deterministic bytes: sorted keys, compact, gzip without a timestamp."""
    text = (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(
        gzip.compress(text, compresslevel=9, mtime=0) if path.suffix == ".gz" else text
    )


def _check_structure(data: Any) -> dict[str, dict[str, Any]]:
    """The artifact's records, after validating their structure and values."""
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise SnapshotError("reference snapshot: unknown schema")
    records = data.get("records")
    if not isinstance(records, dict) or not records:
        raise SnapshotError("reference snapshot: no records")
    for key, rec in records.items():
        if not isinstance(rec, dict) or rec.get("seed") not in SEEDS:
            raise SnapshotError(f"reference snapshot: {key}: invalid seed")
        if not isinstance(rec.get("exact"), bool):
            raise SnapshotError(f"reference snapshot: {key}: invalid exact flag")
        eps = rec.get("entrypoints")
        if not isinstance(eps, list) or not eps or not all(isinstance(e, str) for e in eps):
            raise SnapshotError(f"reference snapshot: {key}: invalid entrypoints")
        parts = rec.get("parts")
        if not isinstance(parts, dict) or not parts:
            raise SnapshotError(f"reference snapshot: {key}: no parts")
        for name, part in parts.items():
            unit_of(name)
            shape, values = part.get("shape"), part.get("values")
            if not (isinstance(shape, list) and isinstance(values, list)):
                raise SnapshotError(f"reference snapshot: {key}.{name}: malformed")
            if math.prod(shape) != len(values):
                raise SnapshotError(f"reference snapshot: {key}.{name}: shape mismatch")
            if not all(
                isinstance(x, float) and not isinstance(x, bool) and math.isfinite(x)
                for x in values
            ):
                raise SnapshotError(f"reference snapshot: {key}.{name}: non-finite value")
    return records


def load_approved(path: Path | None = None, authenticate: bool = True) -> dict[str, Any]:
    """The approved artifact, authenticated against its pinned sha256 (condition 3)."""
    from tars.validation.approved_digests import APPROVED_REFERENCE_SNAPSHOT_SHA256

    path = snapshot_path() if path is None else path
    if not path.exists():
        raise SnapshotError(f"reference snapshot missing: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if authenticate and digest != APPROVED_REFERENCE_SNAPSHOT_SHA256:
        raise SnapshotError(
            f"reference snapshot is not the approved one (sha256 {digest}); a reviewed "
            "change must update tars.validation.approved_digests"
        )
    data = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
    _check_structure(data)
    return data


@dataclass
class Session:
    """One verification (or recording) pass over an entrypoint's references."""

    mode: str  # "verify" | "record"
    entrypoint: str
    approved: dict[str, dict[str, Any]] | None = None
    sha256: str | None = None
    scopes: list[str] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=dict)
    recorded: dict[str, dict[str, Any]] = field(default_factory=dict)
    consumed: set[str] = field(default_factory=set)
    compared: set[str] = field(default_factory=set)  # consumed AND compared (F57)
    problems: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    max_deviation: dict[str, float] = field(default_factory=dict)
    verified_values: int = 0

    def _problem(self, kind: str, text: str) -> None:
        n = self.counts.get(kind, 0)
        self.counts[kind] = n + 1
        if n < MAX_LISTED:
            self.problems.append(f"{kind}: {text}")

    def pin(
        self, label: str, seed: str, parts: dict[str, Any], exact: bool = False
    ) -> dict[str, np.ndarray]:
        if seed not in SEEDS:
            raise ValueError(f"unknown seed {seed!r}")
        prefix = "/".join([*self.scopes, label])
        n = self.counters.get(prefix, 0)
        self.counters[prefix] = n + 1
        key = f"{prefix}#{n}"
        runtime = {name: np.asarray(v, dtype=float) for name, v in parts.items()}
        for name, arr in runtime.items():
            unit_of(name)
            if not np.all(np.isfinite(arr)):
                self._problem("non-finite reference value", f"{key}.{name}")
        if self.mode == "record":
            self.recorded[key] = {
                "seed": seed,
                "exact": exact,
                "parts": {
                    name: {"shape": list(arr.shape), "values": [float(x) for x in arr.ravel()]}
                    for name, arr in runtime.items()
                },
            }
            return runtime
        self.consumed.add(key)
        if not isinstance(self.approved, dict):
            # Fail closed (review F57): a verify session without its authenticated
            # ledger -- never loaded, or lost after loading -- verifies nothing.
            self._problem("no authenticated reference ledger", key)
            return runtime
        rec = self.approved.get(key)
        if rec is None:
            self._problem("unexpected reference value", key)
            return runtime
        if rec["seed"] != seed or rec["exact"] != exact or set(rec["parts"]) != set(runtime):
            self._problem("reference value changed kind", key)
            return runtime
        approved: dict[str, np.ndarray] = {}
        ok = True
        for name, arr in runtime.items():
            part = rec["parts"][name]
            want = np.asarray(part["values"], dtype=float).reshape(part["shape"])
            if want.shape != arr.shape:
                self._problem("reference value changed shape", f"{key}.{name}")
                ok = False
                continue
            unit = unit_of(name)
            dev = np.abs(arr - want)
            worst = float(np.max(dev)) if dev.size else 0.0
            cls = f"{seed}:{unit}"
            if math.isfinite(worst):
                self.max_deviation[cls] = max(self.max_deviation.get(cls, 0.0), worst)
            tol = 0.0 if exact else TOLERANCES[(seed, unit)]
            # Finite-safe (F48): NaN or inf never passes.
            if not bool(np.all(np.isfinite(arr) & (dev <= tol))):
                self._problem(
                    "reference value outside its reproducibility tolerance",
                    f"{key}.{name}: max |runtime - approved| = {worst!r} > {tol!r}",
                )
                ok = False
            self.verified_values += int(arr.size)
            approved[name] = want
        self.compared.add(key)
        if not ok:
            return runtime
        # Approved values are consumed for ref/gmat seeds; sim-seeded ones depend on
        # the platform's simulator output and are verified only (see margin_problems).
        return approved if seed != "sim" else runtime

    def finish(self, complete: bool = True) -> list[str]:
        """All problems; with ``complete``, every approved value of this entrypoint
        must have been reproduced (a skipped or missing computation fails)."""
        if self.mode == "verify":
            if not isinstance(self.approved, dict):
                self._problem("no authenticated reference ledger", "session finished without it")
            unchecked = self.consumed - self.compared
            if unchecked and isinstance(self.approved, dict):
                for k in sorted(unchecked):
                    self._problem("reference value not compared", k)
        if complete and isinstance(self.approved, dict):
            missing = sorted(
                k
                for k, rec in self.approved.items()
                if self.entrypoint in rec["entrypoints"] and k not in self.consumed
            )
            for k in missing:
                self._problem("approved reference value not reproduced", k)
        summary = [
            f"{kind}: {n} in total" for kind, n in sorted(self.counts.items()) if n > MAX_LISTED
        ]
        return self.problems + summary

    def report(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "artifact_sha256": self.sha256,
            "records_consumed": len(self.consumed),
            "records_verified": len(self.compared),
            "values_verified": self.verified_values,
            "max_deviation_by_class": dict(sorted(self.max_deviation.items())),
        }


_SESSION: contextvars.ContextVar[Session | None] = contextvars.ContextVar(
    "tars_reference_snapshot_session", default=None
)


def active() -> Session | None:
    return _SESSION.get()


@contextlib.contextmanager
def session(
    entrypoint: str,
    recorder: Session | None = None,
    path: Path | None = None,
    authenticate: bool = True,
) -> Iterator[Session]:
    """Verify against the approved artifact, or record into ``recorder``. Nested calls
    reuse the outer session. Only toolbox/scripts/reference_snapshot.py passes a
    recorder or ``authenticate=False`` (a candidate's deviation measurement); the Proof
    and the GMAT evaluation always verify the pinned artifact."""
    outer = _SESSION.get()
    if outer is not None:
        yield outer
        return
    if recorder is not None:
        s = recorder
    else:
        s = Session("verify", entrypoint)
        try:
            p = snapshot_path() if path is None else path
            data = load_approved(p, authenticate)
            s.approved = data["records"]
            s.sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
        except (SnapshotError, OSError, ValueError) as exc:
            s.problems.append(f"approved reference snapshot unusable: {exc}")
    token = _SESSION.set(s)
    try:
        yield s
    finally:
        _SESSION.reset(token)


@contextlib.contextmanager
def scope(*parts: str) -> Iterator[None]:
    """Key prefix for the values pinned inside (scenario name, consumer)."""
    s = _SESSION.get()
    if s is None:
        yield
        return
    s.scopes.extend(parts)
    try:
        yield
    finally:
        del s.scopes[len(s.scopes) - len(parts) :]


def pin(label: str, seed: str, exact: bool = False, **parts: Any) -> dict[str, np.ndarray]:
    """Values to use for one oracle output: see the module docstring. ``exact`` values
    (evaluation-time grids, decimal closed forms) must reproduce bit for bit."""
    s = _SESSION.get()
    if s is None:
        return {name: np.asarray(v, dtype=float) for name, v in parts.items()}
    return s.pin(label, seed, parts, exact)


def margin_problems(
    name: str, metrics: dict[str, float], limits: dict[str, float], shifts: dict[str, float]
) -> list[str]:
    """DR-0021 condition 4 for sim-seeded values: a gated metric that passes must pass
    by more than the worst shift a within-tolerance reference deviation could cause, so
    no undetected deviation can turn a rejection into an acceptance."""
    out = []
    for k, shift in shifts.items():
        if k not in limits or k not in metrics:
            continue
        m, lim = metrics[k], limits[k]
        if not (math.isfinite(shift) and shift >= 0.0):
            out.append(f"{name}: {k}: invalid margin bound {shift!r}")
        elif m <= lim and not m + shift <= lim:
            out.append(f"{name}: {k}={m!r} within {shift!r} of its limit {lim!r}")
    return out
