"""Approved reference snapshot tooling for the M2 Proof (DR-0021 option A).

Usage:
    uv run python toolbox/scripts/reference_snapshot.py generate --out PATH [--measurement]
    uv run python toolbox/scripts/reference_snapshot.py verify-baseline PATH
    uv run python toolbox/scripts/reference_snapshot.py compare OLD NEW
    uv run python toolbox/scripts/reference_snapshot.py measure-deviation CANDIDATE --out JSON

``generate`` records every reference value of the M2 Proof and of the GMAT M2
evaluation into a CANDIDATE file. It never writes the approved artifact and never
changes the pinned digest (DR-0021 condition 3): installing a new baseline is a
reviewed commit that copies the candidate, updates
``tars.validation.approved_digests.APPROVED_REFERENCE_SNAPSHOT_SHA256``, and records
the justification, the comparison with the previous baseline (``compare``) and an
independent review. A baseline candidate requires a clean git tree (the pinned
commit), a passing Proof and GMAT evaluation, and ``verify-baseline`` to pass;
``--measurement`` drops the clean-tree requirement and marks the file as a
cross-platform measurement, not a candidate (VAL-0015).

``verify-baseline`` checks a snapshot against the committed GMAT evidence and the
physical invariants, from the snapshot's own values (DR-0021 condition 2).

``compare`` reports the largest |a - b| per value class and any keys present in only
one file (the baseline-change comparison).

``measure-deviation`` runs the Proof and the GMAT evaluation in VERIFY mode against a
candidate with unlimited tolerances, so every within-run value is substituted exactly
as in a real verification, and reports the largest |runtime - approved| per value class:
the quantity the reproducibility tolerances bound (VAL-0015, DR-0021 condition 4).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from collections import defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from tars.validation import reference_snapshot as snap
from tars.validation.thresholds import REPO_ROOT


def _load_module(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _environment() -> dict[str, Any]:
    import platform

    import scipy

    from tars.validation.cross_platform import platform_info

    lock = REPO_ROOT / "uv.lock"
    return {
        **platform_info(),
        "python_full": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "uv_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None,
    }


def merge(sessions: list[snap.Session]) -> dict[str, dict[str, Any]]:
    """One record set from several entrypoints. A key computed by two entrypoints must
    be bit-identical (same process, same inputs): anything else is non-determinism."""
    records: dict[str, dict[str, Any]] = {}
    for s in sessions:
        for key, rec in s.recorded.items():
            if key in records:
                old = records[key]
                if (old["seed"], old["exact"], old["parts"]) != (
                    rec["seed"],
                    rec["exact"],
                    rec["parts"],
                ):
                    raise SystemExit(f"non-deterministic reference value {key}")
                old["entrypoints"].append(s.entrypoint)
            else:
                records[key] = {**rec, "entrypoints": [s.entrypoint]}
    return dict(sorted(records.items()))


def cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    if out == snap.snapshot_path().resolve():
        print("refusing to write the approved artifact; write a candidate", file=sys.stderr)
        return 2
    dirty = _git("status", "--porcelain")
    if dirty and not args.measurement:
        print("a baseline candidate needs a clean tree (pinned commit):\n" + dirty, file=sys.stderr)
        return 2

    proof = _load_module("m2_proof", "toolbox/validators/m2_proof.py")
    cli = _load_module("gmat_m2_cli", "toolbox/scripts/gmat_m2.py")
    sessions = [snap.Session("record", "m2_proof")]
    report_path = out.parent / (out.name.split(".")[0] + ".proof.json")
    rc = proof.main(["--out", str(report_path)], recorder=sessions[0])
    failures = [] if rc == 0 else ["M2 Proof failed"]
    for name in cli.gmat_m2.GMAT_MISSIONS:
        rec = snap.Session("record", f"gmat_m2:{name}")
        reasons, check = cli._evaluate(name, recorder=rec)
        sessions.append(rec)
        if reasons or check is None or not check.passed:
            failures.append(f"GMAT M2 {name}: {reasons[:5] or 'O9 check failed'}")
    for s in sessions:
        failures += [f"{s.entrypoint}: {p}" for p in s.finish(complete=False)]
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    records = merge(sessions)
    data = {
        "schema": snap.SCHEMA,
        "artifact": "M2 approved reference snapshot (DR-0021 option A)",
        "kind": "measurement" if args.measurement else "baseline candidate",
        "provenance": {
            "tars_git_revision": _git("rev-parse", "HEAD"),
            "tree_clean": not dirty,
            "environment": _environment(),
            "proof_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "gmat_m2_manifest_sha256": hashlib.sha256(
                (REPO_ROOT / "toolbox/references/gmat/m2/APPROVED_DIGESTS.json").read_bytes()
            ).hexdigest(),
            "entrypoints": [s.entrypoint for s in sessions],
        },
        "records": records,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    snap.write_json(out, data)
    # The candidate IS this recording, so its inventory matches by construction; the
    # standalone verify-baseline of the file to be pinned re-records independently.
    problems = verify_baseline(data, expected=records)
    if problems and not args.measurement:
        out.unlink()  # never leave a failed candidate behind
        print("baseline verification failed:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    values = sum(len(p["values"]) for r in records.values() for p in r["parts"].values())
    print(f"{data['kind']}: {out} ({len(records)} records, {values} values)")
    print(f"sha256 {digest}")
    if problems:
        print("baseline verification (measurement only, not a candidate):")
        print("\n".join(problems))
    elif not args.measurement:
        print("baseline verification: PASS")
    return 0


# --------------------------------------------------------------- baseline verification
#
# DR-0021 condition 2 (and review M2-T6 F53): every pinned value is recomputed from its
# pinned inputs and the scenario with implementations independent of the runtime
# references (tars.astro.kepler, SciPy DOP853, the validator's RK4 anchor), and
# checked against the committed GMAT evidence and the physical invariants.

# Agreement limits between the snapshot and the independent recomputation. Measured
# on baseline 2 (VAL-0015): universal-variable Kepler vs tars Kepler <= 2.9e-7 m and
# 4.1e-10 m/s (the longest O5 and GMAT arcs; 2.8e-9 m on <= 60 s segments); LSODA vs
# the RK4 anchors in burns <= 6.5e-7 m and 1.1e-9 m/s; node crossings on z = 0 to
# 2.2e-8 m; scenario-only values exact or <= 1e-15 relative. Each limit sits above the
# measured agreement and far below any physical corruption and the O9 gates.
INDEP_POS_M = 1e-6
INDEP_VEL_MPS = 2e-9
INDEP_BURN_POS_M = 1e-5
INDEP_BURN_VEL_MPS = 1e-8
INDEP_MASS_KG = 1e-9
INDEP_REL = 1e-12
NODE_T_S = 1e-6  # crossing time vs the independent enumeration (measured: VAL-0015)


def _stumpff(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    c, s = np.empty_like(z), np.empty_like(z)
    pos, neg = z > 1e-6, z < -1e-6
    small = ~(pos | neg)
    sz = np.sqrt(z[pos])
    c[pos], s[pos] = (1.0 - np.cos(sz)) / z[pos], (sz - np.sin(sz)) / sz**3
    sn = np.sqrt(-z[neg])
    c[neg], s[neg] = (np.cosh(sn) - 1.0) / -z[neg], (np.sinh(sn) - sn) / sn**3
    zs = z[small]
    c[small] = 0.5 - zs / 24.0 + zs**2 / 720.0
    s[small] = 1.0 / 6.0 - zs / 120.0 + zs**2 / 5040.0
    return c, s


def kepler_uv(r0, v0, dts, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Two-body states at every dt from (r0, v0): universal variables with Lagrange
    f and g (Curtis, Orbital Mechanics, Algorithms 3.3-3.4), vectorized. Written here,
    independent of tars.astro.kepler."""
    r0, v0 = np.asarray(r0, dtype=float), np.asarray(v0, dtype=float)
    dts = np.atleast_1d(np.asarray(dts, dtype=float))
    rn0 = float(np.linalg.norm(r0))
    vr0 = float(r0 @ v0) / rn0
    alpha = 2.0 / rn0 - float(v0 @ v0) / mu
    smu = math.sqrt(mu)
    chi = smu * abs(alpha) * dts
    for _ in range(100):
        z = alpha * chi**2
        c, s = _stumpff(z)
        f = rn0 * vr0 / smu * chi**2 * c + (1.0 - alpha * rn0) * chi**3 * s + rn0 * chi - smu * dts
        df = rn0 * vr0 / smu * chi * (1.0 - z * s) + (1.0 - alpha * rn0) * chi**2 * c + rn0
        step = f / df
        chi = chi - step
        if np.all(np.abs(step) <= 1e-14 * np.maximum(np.abs(chi), 1.0)):
            break
    z = alpha * chi**2
    c, s = _stumpff(z)
    f = 1.0 - chi**2 / rn0 * c
    g = dts - chi**3 / smu * s
    r = f[:, None] * r0 + g[:, None] * v0
    rn = np.linalg.norm(r, axis=1)
    fdot = smu / (rn * rn0) * (z * s - 1.0) * chi
    gdot = 1.0 - chi**2 / rn * c
    v = fdot[:, None] * r0 + gdot[:, None] * v0
    return r, v


def _burn_path(y0, times, mu: float, veh, sign: float) -> np.ndarray:
    """Powered two-body states at ``times`` (the first is the start): ODEPACK LSODA via
    scipy.integrate.odeint, with its own equations of motion -- independent of the
    runtime DOP853 reference and of the validator's RK4 anchor."""
    from scipy.integrate import odeint

    from tars.sim.constants import STANDARD_GRAVITY

    mdot = veh.thrust_n / (veh.isp_s * STANDARD_GRAVITY)

    def rhs(y, t):
        r, v = y[:3], y[3:6]
        m = veh.dry_mass_kg + y[6]
        a = -mu * r / np.linalg.norm(r) ** 3 + sign * veh.thrust_n / m * v / np.linalg.norm(v)
        return np.concatenate([v, a, [-mdot]])

    return odeint(
        rhs, np.asarray(y0, float), np.asarray(times, float), rtol=1e-13, atol=1e-12, mxstep=100000
    )


def _free_space_closed_form(veh, t: float) -> tuple[float, float]:
    """Free-space delta-v and displacement, re-derived in 40-digit decimal (the float
    form cancels): dv = c ln(m0/m), x = c (m/mdot) (m0/m - 1 - ln(m0/m))."""
    from decimal import Decimal, localcontext

    from tars.sim.constants import STANDARD_GRAVITY

    with localcontext() as ctx:
        ctx.prec = 40
        c = Decimal(veh.isp_s) * Decimal(STANDARD_GRAVITY)
        mdot = Decimal(veh.thrust_n) / c
        m0 = Decimal(veh.initial_mass_kg)
        m = m0 - mdot * Decimal(t)
        ratio = m0 / m
        ln = ratio.ln()
        return float(c * ln), float(c * (m / mdot) * (ratio - 1 - ln))


def _independent_burns(scenario, expected) -> list[dict[str, float]]:
    """Accepted burns from the scenario and DR-0017 D1a, re-derived here."""
    from tars.sim.constants import STANDARD_GRAVITY

    sc = scenario.spacecraft
    out: list[dict[str, float]] = []
    if sc is None:
        return out
    c = sc.engine.isp_s * STANDARD_GRAVITY
    mdot = sc.engine.thrust_n / c
    prop = sc.propellant_kg
    for entry, exp in zip(scenario.commands, expected, strict=True):
        if exp.status != "accepted":
            continue
        cmd = entry.command
        ign, dur = float(cmd["ignition_t_s"]), float(cmd["duration_s"])
        depl = prop / mdot
        intended = dur if dur <= depl else depl
        cut = ign + intended
        while cut - ign > depl:
            cut = math.nextafter(cut, -math.inf)
        executed = cut - ign
        used = min(mdot * executed, prop)
        after = 0.0 if used >= prop else prop - used
        m0, mf = sc.dry_mass_kg + prop, sc.dry_mass_kg + after
        out.append(
            {"ign": ign, "dur": dur, "intended": intended, "cut": cut, "executed": executed,
             "before": prop, "used": used, "after": after, "m0": m0, "mf": mf,
             "dv": c * math.log(m0 / mf), "sign": 1.0 if cmd["direction"] == "prograde" else -1.0}
        )  # fmt: skip
        prop = after
    return out


def _scenarios() -> dict[str, tuple[Any, Any]]:
    """Every audited scenario by name, with its expectations."""
    from tars.validation import m2
    from tars.validation.m2_missions import ACCEPT, MISSIONS

    out: dict[str, tuple[Any, Any]] = {}
    for mission in MISSIONS:
        base = mission.build()
        out[base.name] = (base, mission.expected)
        for dt in m2.O8_DTS[1:]:
            v = m2.convergence_variant(base, dt)
            out[v.name] = (v, mission.expected)
        if mission.impulsive_limit:
            for v in m2.impulsive_variants(base):
                out[v.name] = (v, (ACCEPT,))
        if mission.name == "m2_prograde_burn":
            for case in m2.BOUNDARY_CASES:
                v = m2.boundary_variant(base, case)
                out[v.name] = (v, (ACCEPT,))
    return out


def _arr(rec: dict, name: str) -> np.ndarray:
    part = rec["parts"][name]
    return np.asarray(part["values"], dtype=float).reshape(part["shape"])


def _split(key: str) -> tuple[str, str, int]:
    prefix, _, n = key.rpartition("#")
    scope, _, label = prefix.rpartition("/")
    return scope, label, int(n)


def _rel(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return math.inf
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))) if a.size else 0.0


# Parts that are INPUTS of a pinned value: they come from the simulator or the scenario
# schedule, never from a reference. verify-baseline takes their expected values from a
# fresh recording of the reviewed code (bit-identical on the generating host, within
# the measured reproducibility tolerance elsewhere) and recomputes every OUTPUT part
# independently from them (review M2-T6 F54, F56).
INPUT_PARTS = {
    "dop853.marks": ("marks_s",),
    "simpson_bound": ("window_s",),
    "timing_bound": ("durations_s", "propellant_before_kg"),
    "o5.kepler": ("seed_r_m", "seed_v_mps", "flight_s"),
    "o6.midpoint": ("seed_r_m", "seed_v_mps", "flight_s"),
    "o3.expected_cutoff": ("start_r_m", "start_v_mps", "duration_s"),
}


class _Coverage:
    """Every (record, part) must be verified explicitly, after its check ran."""

    def __init__(self, records: dict[str, dict[str, Any]]) -> None:
        self.parts = {(k, p) for k, r in records.items() for p in r["parts"]}
        self.done: set[tuple[str, str]] = set()

    def add(self, key: str, *parts: str) -> None:
        self.done.update((key, p) for p in parts)

    def missing(self) -> list[tuple[str, str]]:
        return sorted(self.parts - self.done)


def record_all() -> tuple[dict[str, dict[str, Any]], list[str]]:
    """A fresh recording of every entrypoint by the current code: the expected
    inventory and inputs (never the reference outputs) for verify-baseline."""
    proof = _load_module("m2_proof", "toolbox/validators/m2_proof.py")
    cli = _load_module("gmat_m2_cli", "toolbox/scripts/gmat_m2.py")
    import tempfile

    sessions = [snap.Session("record", "m2_proof")]
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        if proof.main(["--out", str(Path(tmp) / "m2.json")], recorder=sessions[0]) != 0:
            failures.append("M2 Proof failed")
    for name in cli.gmat_m2.GMAT_MISSIONS:
        rec = snap.Session("record", f"gmat_m2:{name}")
        reasons, check = cli._evaluate(name, recorder=rec)
        sessions.append(rec)
        if reasons or check is None or not check.passed:
            failures.append(f"GMAT M2 {name}: {reasons[:5] or 'O9 check failed'}")
    for s in sessions:
        failures += [f"{s.entrypoint}: {p}" for p in s.finish(complete=False)]
    return merge(sessions), failures


def _inventory_problems(records, expected, cov: _Coverage) -> list[str]:
    """The candidate holds exactly the expected records -- keys (counters included),
    seeds, exactness, entrypoints, part names and shapes -- and its input parts are
    match the fresh recording's within their class's reproducibility tolerance (exact
    for exact records) (F54, F56)."""
    out: list[str] = []
    missing, extra = sorted(set(expected) - set(records)), sorted(set(records) - set(expected))
    if missing:
        out.append(f"inventory: {len(missing)} expected records missing, e.g. {missing[:3]}")
    if extra:
        out.append(f"inventory: {len(extra)} unexpected records, e.g. {extra[:3]}")
    for key in sorted(set(records) & set(expected)):
        got, want = records[key], expected[key]
        if (got["seed"], got["exact"], sorted(got["entrypoints"])) != (
            want["seed"],
            want["exact"],
            sorted(want["entrypoints"]),
        ):
            out.append(f"{key}: seed, exactness or entrypoints differ from the inventory")
            continue
        shapes = {p: v["shape"] for p, v in got["parts"].items()}
        if shapes != {p: v["shape"] for p, v in want["parts"].items()}:
            out.append(f"{key}: parts or shapes differ from the inventory")
            continue
        label = _split(key)[1]
        for part in INPUT_PARTS.get(label, ()):
            # Inputs agree within the measured reproducibility tolerance of their
            # class (exact for exact records): the fresh recording may run on another
            # platform, whose simulator-seeded inputs differ within it (VAL-0015).
            tol = 0.0 if got["exact"] else snap.TOLERANCES[(got["seed"], snap.unit_of(part))]
            g = np.asarray(got["parts"][part]["values"], dtype=float)
            w = np.asarray(want["parts"][part]["values"], dtype=float)
            if g.shape == w.shape and bool(np.all(np.isfinite(g) & (np.abs(g - w) <= tol))):
                cov.add(key, part)
            else:
                out.append(f"{key}.{part}: input differs from the fresh recording")
    return out


def verify_baseline(
    data: dict[str, Any], expected: dict[str, dict[str, Any]] | None = None
) -> list[str]:
    """Independent verification of a snapshot (DR-0021 condition 2; F53-F56).

    1. Inventory: exactly the records, counters, entrypoints and part schemas of a
       fresh recording of the reviewed code; input parts within their class's
       reproducibility tolerance of it (exact for exact records).
    2. Every output part recomputed independently of the runtime references:
       scenario values re-derived (initial state, predicted burns, Simpson and DR-0017
       bounds, O3 closed forms, O6 delta-v, segment bounds from the marks, tick
       grids, O9 schedule, row labels, epoch and mass); propagated values from their
       inputs by the universal-variable Kepler (coasts, anchor ticks, O5, O6, GMAT
       alignment) and LSODA (burns); node crossings independently ENUMERATED (count,
       order, powered intervals, times).
    3. DOP853 against the committed GMAT rows within the O9 gates; coast energy
       conserved; extrema equal to the pinned anchor ticks'.
    Every (record, part) must be verified; anything unevaluable fails closed.
    """
    problems: list[str] = []
    records = data["records"]
    cov = _Coverage(records)
    if expected is None:
        problems.append("inventory: no fresh recording to verify against")
    else:
        problems += _inventory_problems(records, expected, cov)
    scen = _scenarios()
    stats: dict[str, float] = defaultdict(float)

    def note(kind: str, value: float) -> None:
        stats[kind] = max(stats[kind], value)

    def bad(where: str, what: str) -> None:
        problems.append(f"{where}: {what}")

    by_scope: dict[str, list[tuple[str, int, str, dict]]] = defaultdict(list)
    for key, rec in records.items():
        scope, label, n = _split(key)
        by_scope[scope].append((label, n, key, rec))
    for items in by_scope.values():
        items.sort(key=lambda x: (x[0], x[1]))

    for scope, items in sorted(by_scope.items()):
        try:
            _verify_scope(scope, items, scen, cov, note, bad)
        except Exception as exc:  # corrupted values must fail, never crash (F53)
            bad(scope, f"verification raised {exc!r}")
    from tars.validation import gmat_m2
    from tars.validation.thresholds import load_scoped_thresholds

    limits = load_scoped_thresholds(missions=frozenset(scen))
    for name in gmat_m2.GMAT_MISSIONS:
        try:
            _verify_gmat_mission(name, records, scen, cov, note, bad, limits)
        except Exception as exc:  # fail closed (F53)
            bad(name, f"verification raised {exc!r}")

    unverified = cov.missing()
    if unverified:
        bad(
            "coverage",
            f"{len(unverified)} record parts not independently verified, e.g. {unverified[:3]}",
        )
    for k, v in sorted(stats.items()):
        print(f"  independent agreement, max {k}: {v:.3g}")
    return problems


def _bisect_root(r0, v0, span: float, mu: float) -> float:
    """The flight time in (0, span) where z changes from < 0 to >= 0, by bisection on
    the independent Kepler (as precise as the doubles allow)."""
    lo, hi = 0.0, span
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid in (lo, hi):
            break
        z = float(kepler_uv(r0, v0, [mid], mu)[0][0, 2])
        if z < 0.0:
            lo = mid
        else:
            hi = mid
    return hi


def _enumerate_crossings(states: dict[float, np.ndarray], mu: float, burns) -> tuple[list, int]:
    """Ascending-node crossings between consecutive states, timed on coasts and only
    counted when the interval meets a burn (the contract of orbit_checks)."""
    timed, powered = [], 0
    ts = sorted(states)
    for a, b in pairwise(ts):
        if states[a][2] < 0.0 <= states[b][2]:
            if any(x["ign"] < b and a < x["cut"] for x in burns):
                powered += 1
                continue
            timed.append(a + _bisect_root(states[a][:3], states[a][3:6], b - a, mu))
    return timed, powered


def _verify_crossings(key, rec, timed, powered, cov, note, bad) -> None:
    got = _arr(rec, "crossings_s")
    if len(got) != len(timed):
        bad(key, f"{len(got)} crossings pinned, {len(timed)} enumerated independently")
        return
    err = float(np.max(np.abs(got - np.array(timed)))) if timed else 0.0
    note("node crossing time s", err)
    if not (err <= NODE_T_S and np.all(np.diff(got) > 0)):
        bad(key, f"crossing times differ from the independent enumeration ({err:.3g} s)")
        return
    if "powered_1" in rec["parts"]:
        if float(_arr(rec, "powered_1")[0]) != float(powered):
            bad(key, "powered-interval count differs from the independent enumeration")
            return
        cov.add(key, "powered_1")
    cov.add(key, "crossings_s")


def _independent_arcs(scenario, burns, horizon: float) -> list[tuple[float, float, float]]:
    """The DR-0016 aligned schedule, re-derived: burns at 1 s steps, coasts on the
    telemetry grid with one-step realignment arcs."""
    grid = scenario.telemetry.sample_interval_s
    cuts = sorted(
        {0.0, horizon}
        | {x["ign"] for x in burns if x["ign"] < horizon}
        | {min(x["cut"], horizon) for x in burns if x["ign"] < horizon}
    )
    arcs: list[tuple[float, float, float]] = []
    for a, b in pairwise(cuts):
        if any(x["ign"] <= a and b <= x["cut"] for x in burns):
            arcs.append((a, b, min(1.0, b - a)))
            continue
        first, last = math.ceil(a / grid) * grid, math.floor(b / grid) * grid
        if first >= last:
            arcs.append((a, b, b - a))
            continue
        for x, y, h in ((a, first, first - a), (first, last, grid), (last, b, b - last)):
            if y > x:
                arcs.append((x, y, h))
    return arcs


def _arc_rows(arcs) -> list[float]:
    out: list[float] = []
    for i, (a, b, h) in enumerate(arcs):
        n = math.floor((b - a) / h + 1e-9)
        steps = n if math.isclose(n * h, b - a, rel_tol=0, abs_tol=1e-9) else n + 1
        out += ([a] if i == 0 else []) + [a + k * h for k in range(1, steps)] + [b]
    return out


def _verify_o3(scope, items, scen, cov, note, bad) -> None:
    from tars.sim.constants import STANDARD_GRAVITY
    from tars.validation import m2

    proof = _load_module("m2_proof_o3", "toolbox/validators/m2_proof.py")
    veh = m2.vehicle(scen["m2_prograde_burn"][0])
    sign = {"o3_free_space/prograde": 1.0, "o3_free_space/retrograde": -1.0}[scope]
    mdot = veh.thrust_n / (veh.isp_s * STANDARD_GRAVITY)
    closed = {n: (key, rec) for label, n, key, rec in items if label == "o3.closed_form"}
    for label, n, key, rec in items:
        if label != "o3.expected_cutoff":
            continue
        t = float(_arr(rec, "duration_s")[0])
        if t != proof.O3_DURATION_S:
            bad(key, f"O3 duration {t} is not the Proof's {proof.O3_DURATION_S}")
            continue
        dv, disp = _free_space_closed_form(veh, t)
        x0, v0 = _arr(rec, "start_r_m"), _arr(rec, "start_v_mps")
        u = v0 / np.linalg.norm(v0)
        want_v, want_r = v0 + sign * dv * u, x0 + v0 * t + sign * disp * u
        err = max(
            _rel(_arr(rec, "v_mps"), want_v),
            float(np.max(np.abs(_arr(rec, "r_m") - want_r)))
            / max(float(np.linalg.norm(want_r)), 1.0),
            _rel(_arr(rec, "propellant_kg"), [veh.propellant_kg - mdot * t]),
        )
        note("closed form rel", err)
        if err <= INDEP_REL:
            cov.add(key, "v_mps", "r_m", "propellant_kg")
        else:
            bad(key, f"O3 expected cutoff differs from the independent one ({err:.3g})")
        ckey, crec = closed.get(n, (None, None))
        if crec is None:
            bad(key, "no closed form for this expected cutoff")
            continue
        err = max(_rel(_arr(crec, "dv_mps"), [dv]), _rel(_arr(crec, "disp_m"), [disp]))
        note("closed form rel", err)
        if err <= INDEP_REL:
            cov.add(ckey, "dv_mps", "disp_m")
        else:
            bad(ckey, f"O3 closed form differs from the independent one ({err:.3g})")


def _verify_scope(scope, items, scen, cov, note, bad) -> None:
    from tars.astro.elements import circular_orbit_state
    from tars.validation import m2

    if scope.startswith("o3_free_space/"):
        _verify_o3(scope, items, scen, cov, note, bad)
        return
    found = scen.get(scope.split("/")[0])
    if found is None:
        bad(scope, "no scenario for this scope")
        return
    scenario, expected = found
    mu = scenario.constants.mu
    radius = scenario.constants.equatorial_radius
    veh = m2.vehicle(scenario)
    burns = _independent_burns(scenario, expected)
    grid, dt = scenario.telemetry.sample_interval_s, scenario.dt_s
    o6_dv = None

    for label, _n, key, rec in items:
        if label == "initial_state":
            o = scenario.initial_orbit
            r, v = circular_orbit_state(
                radius + o.altitude_m, math.radians(o.inclination_deg),
                math.radians(o.raan_deg), math.radians(o.arg_latitude_deg), mu,
            )  # fmt: skip
            err = max(_rel(_arr(rec, "r_m"), r), _rel(_arr(rec, "v_mps"), v))
            note("initial state rel", err)
            if err <= INDEP_REL:
                cov.add(key, "r_m", "v_mps")
            else:
                bad(key, f"initial state differs from elements_to_rv ({err:.3g})")
        elif label == "predicted_burns":
            want_t = [[b["ign"], b["dur"], b["intended"], b["cut"], b["executed"]] for b in burns]
            want_m = [[b["before"], b["used"], b["after"], b["m0"], b["mf"]] for b in burns]
            t, m_, dv = _arr(rec, "times_s"), _arr(rec, "masses_kg"), _arr(rec, "delta_v_mps")
            if t.shape == (len(burns), 5) and np.array_equal(t, np.array(want_t).reshape(-1, 5)):
                cov.add(key, "times_s")
            else:
                bad(key, "predicted burn times differ from the independent derivation")
            if _rel(m_, np.array(want_m).reshape(-1, 5)) <= INDEP_REL:
                cov.add(key, "masses_kg")
            else:
                bad(key, "predicted burn masses differ from the independent derivation")
            if _rel(dv, [b["dv"] for b in burns]) <= INDEP_REL:
                cov.add(key, "delta_v_mps")
            else:
                bad(key, "predicted burn delta-v differs from the rocket equation")
        elif label == "simpson_bound":
            a, e = _arr(rec, "window_s")
            b = next((x for x in burns if x["ign"] == a), None)
            if b is None:
                bad(key, "Simpson window does not start at a predicted ignition")
                continue
            total = 0.0
            if e > a:
                mdot = veh.mass_flow_kgps
                inner = (k * dt for k in range(math.ceil(a / dt), math.floor(e / dt) + 1))
                pts = sorted({a, e, *(g for g in inner if a < g < e)})
                for p, q in pairwise(pts):
                    m_end = b["m0"] - mdot * (q - a)
                    total += (q - p) ** 5 / 2880.0 * 24.0 * veh.thrust_n * mdot**4 / m_end**5
            got = float(_arr(rec, "bound_mps")[0])
            err = _rel([got], [total]) if total else float(got != 0.0)
            note("simpson rel", err)
            if err <= INDEP_REL:
                cov.add(key, "bound_mps")
            else:
                bad(key, f"Simpson bound differs from the independent one ({err:.3g})")
        elif label == "timing_bound":
            ex, it = _arr(rec, "durations_s")
            pb = float(_arr(rec, "propellant_before_kg")[0])
            d = abs(ex - it)
            want = 0.0
            if d:
                m_end = veh.dry_mass_kg + max(pb - veh.mass_flow_kgps * max(ex, it), 0.0)
                want = veh.thrust_n * d / m_end
            got = float(_arr(rec, "bound_mps")[0])
            if got == want or _rel([got], [want]) <= INDEP_REL:
                cov.add(key, "bound_mps")
            else:
                bad(key, "DR-0017 timing bound differs from the independent one")
        elif label == "o5.kepler":
            fl = _arr(rec, "flight_s")
            r, v = kepler_uv(_arr(rec, "seed_r_m"), _arr(rec, "seed_v_mps"), fl, mu)
            ep = float(np.max(np.linalg.norm(r - _arr(rec, "r_m"), axis=1))) if fl.size else 0.0
            ev = float(np.max(np.linalg.norm(v - _arr(rec, "v_mps"), axis=1))) if fl.size else 0.0
            note("o5 kepler m", ep), note("o5 kepler m/s", ev)
            if ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS:
                cov.add(key, "r_m", "v_mps")
            else:
                bad(key, f"O5 Kepler differs from the independent one ({ep:.3g} m, {ev:.3g} m/s)")
        elif label == "o6.delta_v":
            base, _ = scen[scope.split("/")[0].rsplit("_o6_", 1)[0]]
            bveh = m2.vehicle(base)
            dur = float(base.commands[0].command["duration_s"])
            m0 = bveh.initial_mass_kg
            want = bveh.exhaust_velocity_mps * math.log(m0 / (m0 - bveh.mass_flow_kgps * dur))
            if _rel(_arr(rec, "dv_mps"), [want]) <= INDEP_REL:
                cov.add(key, "dv_mps")
                o6_dv = want
            else:
                bad(key, "O6 delta-v differs from the rocket equation")
        elif label == "o6.midpoint":
            base, _ = scen[scope.split("/")[0].rsplit("_o6_", 1)[0]]
            cmd = base.commands[0].command
            sign = 1.0 if cmd["direction"] == "prograde" else -1.0
            fl = _arr(rec, "flight_s")
            r, v = kepler_uv(_arr(rec, "seed_r_m"), _arr(rec, "seed_v_mps"), fl, mu)
            rm, vm = _arr(rec, "r_m"), _arr(rec, "v_mps")
            ep, ev = float(np.linalg.norm(r[0] - rm)), float(np.linalg.norm(v[0] - vm))
            note("o6 kepler m", ep), note("o6 kepler m/s", ev)
            if ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS:
                cov.add(key, "r_m", "v_mps")
            else:
                bad(key, f"O6 midpoint differs from the independent propagation ({ep:.3g} m)")
                continue
            if o6_dv is None:
                bad(key, "no verified O6 delta-v")
                continue
            v_imp = v[0] + sign * o6_dv * v[0] / np.linalg.norm(v[0])
            a_imp = -mu / (2.0 * (float(v_imp @ v_imp) / 2.0 - mu / float(np.linalg.norm(r[0]))))
            err = _rel(_arr(rec, "sma_impulsive_m"), [a_imp])
            note("o6 sma rel", err)
            if err <= INDEP_REL:
                cov.add(key, "sma_impulsive_m")
            else:
                bad(key, f"O6 impulsive SMA differs from the independent one ({err:.3g})")

    # DOP853 chains in this scope, in call order.
    def of(name):
        return [it for it in items if it[0] == name]

    marks, starts, bounds = of("dop853.marks"), of("dop853.start"), of("dop853.bounds")
    segs, ticks, extrema = of("dop853.segment"), of("dop853.ticks"), of("dop853.extrema")
    if not (len(marks) == len(starts) == len(bounds) == len(extrema)) or len(segs) != len(ticks):
        bad(scope, "inconsistent DOP853 record counts")
        return
    init = next((it for it in items if it[0] == "initial_state"), None)
    cursor = 0
    chain_states: list[dict[float, np.ndarray]] = []
    for (_, _, _mkey, m_rec), (_, _, skey, s_rec), (_, _, bkey, b_rec), (_, _, ekey, e_rec) in zip(
        marks, starts, bounds, extrema, strict=True
    ):
        mk = _arr(m_rec, "marks_s")
        horizon = float(mk[-1])
        want_b = sorted(
            t
            for t in {
                0.0, *mk.tolist(), *(g * grid for g in range(1, math.floor(horizon / grid) + 1)),
                *(x["ign"] for x in burns), *(x["cut"] for x in burns),
            }
            if t <= horizon
        )  # fmt: skip
        b = _arr(b_rec, "bounds_s")
        if b.tolist() == want_b:
            cov.add(bkey, "bounds_s")
        else:
            bad(bkey, "segment bounds differ from the marks, grid and burn times")
            continue
        y = np.concatenate([_arr(s_rec, "r_m"), _arr(s_rec, "v_mps"), _arr(s_rec, "propellant_kg")])
        tank = 0.0 if veh is None else veh.propellant_kg
        if (
            init is not None
            and np.array_equal(y[:3], _arr(init[3], "r_m"))
            and np.array_equal(y[3:6], _arr(init[3], "v_mps"))
            and y[6] == tank
        ):
            cov.add(skey, "r_m", "v_mps", "propellant_kg")
        else:
            bad(skey, "DOP853 start is not the verified initial state and tank load")
        alt = [float(np.linalg.norm(y[:3])) - radius]
        states = {0.0: y.copy()}
        n = len(b) - 1
        for j in range(n):
            _, _, gkey, g = segs[cursor + j]
            _, _, tkey, t_rec = ticks[cursor + j]
            a_, b_ = float(b[j]), float(b[j + 1])
            k0, k1 = (int(x) for x in _arr(t_rec, "index_1"))
            lo_k = math.floor(a_ / dt) + 1
            cand = [q for q in range(lo_k, math.floor(b_ / dt) + 1) if a_ < q * dt <= b_]
            want_k = (cand[0], cand[-1]) if cand else (lo_k, lo_k - 1)
            if _arr(t_rec, "dt_s")[0] == dt and (k0, k1) == want_k:
                cov.add(tkey, "index_1", "dt_s")
            else:
                bad(tkey, "tick index range is not the dt grid of its segment")
            tt = np.arange(want_k[0], want_k[1] + 1) * dt
            end = np.concatenate(
                [_arr(g, "end_r_m"), _arr(g, "end_v_mps"), _arr(g, "end_propellant_kg")]
            )
            at, aend_p = _arr(g, "anchor_ticks_m"), _arr(g, "anchor_end_propellant_kg")
            burn = next((x for x in burns if x["ign"] <= a_ and b_ <= x["cut"]), None)
            if burn is None:
                r, v = kepler_uv(y[:3], y[3:6], np.concatenate([tt, [b_]]) - a_, mu)
                e_pos, e_vel, kind = INDEP_POS_M, INDEP_VEL_MPS, "coast"
                e0 = float(y[3:6] @ y[3:6]) / 2 - mu / float(np.linalg.norm(y[:3]))
                e1 = float(end[3:6] @ end[3:6]) / 2 - mu / float(np.linalg.norm(end[:3]))
                mass_ok = end[6] == y[6] and aend_p.size == 0
                phys_ok = abs(e1 - e0) <= 1e-11 * abs(e0)
            else:
                path = _burn_path(y, np.concatenate([[a_], tt, [b_]]), mu, veh, burn["sign"])
                r, v = path[1:, :3], path[1:, 3:6]
                e_pos, e_vel, kind = INDEP_BURN_POS_M, INDEP_BURN_VEL_MPS, "burn"
                want_p = burn["before"] - veh.mass_flow_kgps * (b_ - burn["ign"])
                mass_ok = (
                    abs(end[6] - want_p) <= INDEP_MASS_KG
                    and aend_p.size == 1
                    and abs(float(aend_p[0]) - want_p) <= INDEP_MASS_KG
                )
                phys_ok = True
            if at.shape != (len(tt), 3):
                bad(gkey, "anchor tick count is not the tick grid")
                y = end
                states[b_] = end.copy()
                continue
            ep = float(np.linalg.norm(end[:3] - r[-1]))
            ev = float(np.linalg.norm(end[3:6] - v[-1]))
            et = float(np.max(np.linalg.norm(at - r[:-1], axis=1))) if at.size else 0.0
            ea = float(np.linalg.norm(_arr(g, "anchor_end_r_m") - r[-1]))
            eav = float(np.linalg.norm(_arr(g, "anchor_end_v_mps") - v[-1]))
            note(f"{kind} segment end m", ep), note(f"{kind} segment end m/s", ev)
            note(f"{kind} anchor ticks m", et), note(f"{kind} anchor end m", ea)
            if ep <= e_pos and ev <= e_vel and et <= e_pos and ea <= e_pos and eav <= e_vel:
                if mass_ok and phys_ok:
                    cov.add(gkey, *g["parts"])
                else:
                    bad(gkey, f"{kind} segment breaks the mass law or energy conservation")
            else:
                bad(
                    gkey,
                    f"{kind} segment differs from the independent propagation "
                    f"({ep:.3g}, {et:.3g}, {ea:.3g} m; {ev:.3g}, {eav:.3g} m/s)",
                )
            if at.size:
                alt += list(np.linalg.norm(at, axis=1) - radius)
            y = end
            states[b_] = end.copy()
        cursor += n
        ext = _arr(e_rec, "altitude_m")
        if (float(ext[0]), float(ext[1])) == (min(alt), max(alt)):
            cov.add(ekey, "altitude_m")
        else:
            bad(ekey, "extrema are not the pinned ticks' extrema")
        # The reference's mark states, as the oracle sees them (the marks ARE inputs).
        chain_states.append({t: states[t] for t in mk.tolist() if t in states})
    if cursor != len(segs):
        bad(scope, "DOP853 segments without a reference")

    # Node crossings: enumerated independently over the reference marks (F55).
    for label, _n, key, rec in items:
        if label != "orbit.node_crossings":
            continue
        if not chain_states:
            bad(key, "no reference to enumerate crossings from")
            continue
        timed, powered = _enumerate_crossings(chain_states[0], mu, burns)
        _verify_crossings(key, rec, timed, powered, cov, note, bad)


def _verify_gmat_mission(name, records, scen, cov, note, bad, limits) -> None:
    from tars.validation import gmat_m2, m2

    scenario, expected = scen[name]
    mu = scenario.constants.mu
    burns = _independent_burns(scenario, expected)
    horizon = scenario.stop.duration_s
    arcs = _independent_arcs(scenario, burns, horizon)
    rows_t = _arc_rows(arcs)
    files = gmat_m2.reference_files(name)
    plan = gmat_m2.plan_arcs(scenario, m2.predict_burns(scenario, expected), horizon)
    labelled, label_v = gmat_m2.label_rows(gmat_m2.parse_stream(files["report"].read_text()), plan)
    times = sorted(labelled)
    if label_v or times != rows_t:
        bad(name, "committed GMAT rows do not match the independently derived schedule")
        return
    scope = f"{name}/o9"
    recs = {
        (_split(k)[1], _split(k)[2]): (k, r)
        for k, r in records.items()
        if k.startswith(scope + "/o9.")
    }
    lim = limits.for_validator("o9_gmat", name)
    for (label, _n), (key, rec) in sorted(recs.items()):
        if label == "o9.arcs":
            got_b, got_h = _arr(rec, "bounds_s"), _arr(rec, "step_s")
            if got_b.tolist() == [[a, b] for a, b, _ in arcs] and got_h.tolist() == [
                h for _, _, h in arcs
            ]:
                cov.add(key, "bounds_s", "step_s")
            else:
                bad(key, "GMAT arcs differ from the independently derived schedule")
        elif label == "o9.label_times":
            if _arr(rec, "times_s").tolist() == rows_t:
                cov.add(key, "times_s")
            else:
                bad(key, "label times differ from the independently derived schedule")
        elif label == "o9.epoch_anchor":
            import datetime as _dt

            ep = _dt.datetime.fromisoformat(scenario.epoch)
            jd = (ep - _dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
            want = jd - 2430000.0 - (32.184 - 0.0343817) / 86400.0
            if abs(float(_arr(rec, "a1_mjd_1")[0]) - want) * 86400.0 <= 1e-6:
                cov.add(key, "a1_mjd_1")
            else:
                bad(key, "epoch anchor differs from the configured TT epoch in A.1")
        elif label == "o9.expected_mass":
            veh = m2.vehicle(scenario)
            want = []
            for t in rows_t:
                p = veh.propellant_kg
                for x in burns:
                    if t <= x["ign"]:
                        break
                    if t >= x["cut"]:
                        p = x["after"]
                        continue
                    p = x["before"] - veh.mass_flow_kgps * (t - x["ign"])
                    break
                want.append(veh.dry_mass_kg + p)
            got = _arr(rec, "mass_kg")
            err = float(np.max(np.abs(got - want))) if got.shape == (len(want),) else math.inf
            if err <= INDEP_MASS_KG:
                cov.add(key, "mass_kg")
            else:
                bad(key, f"expected mass differs from the mass law ({err:.3g} kg)")
        elif label == "o9.gmat_node_crossings":
            states = {t: np.concatenate([labelled[t].r, labelled[t].v]) for t in times}
            timed, _ = _enumerate_crossings(states, mu, [])
            _verify_crossings(key, rec, timed, 0, cov, note, bad)
    coast_arcs = [
        (a, b) for a, b, _ in arcs if not any(x["ign"] <= a and b <= x["cut"] for x in burns)
    ]
    kep = [recs[k] for k in sorted(k for k in recs if k[0] == "o9.alignment_kepler")]
    if len(kep) != len(coast_arcs):
        bad(name, f"{len(kep)} alignment records for {len(coast_arcs)} coast arcs")
    for (a, b), (key, rec) in zip(coast_arcs, kep, strict=False):
        in_arc = [t for t in times if a < t <= b]
        s0 = labelled[a]
        r, v = kepler_uv(s0.r, s0.v, np.array(in_arc) - a, mu)
        got_r, got_v = _arr(rec, "r_m"), _arr(rec, "v_mps")
        if got_r.shape != r.shape or got_v.shape != v.shape:
            bad(key, "alignment states do not match the arc's rows")
            continue
        ep = float(np.max(np.linalg.norm(r - got_r, axis=1))) if in_arc else 0.0
        ev = float(np.max(np.linalg.norm(v - got_v, axis=1))) if in_arc else 0.0
        note("gmat kepler m", ep), note("gmat kepler m/s", ev)
        if ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS:
            cov.add(key, "r_m", "v_mps")
        else:
            bad(key, f"alignment Kepler differs from the independent propagation ({ep:.3g} m)")
    # The snapshot's DOP853 states against the committed GMAT rows (O9 gates).
    segs = sorted(
        (_split(k)[2], r) for k, r in records.items() if k.startswith(scope + "/dop853.segment#")
    )
    bkey = f"{scope}/dop853.bounds#0"
    if bkey not in records:
        bad(name, "no O9 DOP853 reference")
        return
    b = _arr(records[bkey], "bounds_s")
    pos = vel = 0.0
    compared = 0
    for t, (_, seg) in zip(b[1:], segs, strict=True):
        row = labelled.get(float(t))
        if row is None:
            continue
        pos = max(pos, float(np.linalg.norm(row.r - _arr(seg, "end_r_m"))))
        vel = max(vel, float(np.linalg.norm(row.v - _arr(seg, "end_v_mps"))))
        compared += 1
    note("dop853 vs gmat m", pos), note("dop853 vs gmat m/s", vel)
    if compared != len(times) - 1:
        bad(name, f"{compared} GMAT rows compared of {len(times) - 1}")
    if not (
        pos <= lim["gmat_vs_dop853_position_error_max_m"]
        and vel <= lim["gmat_vs_dop853_velocity_error_max_mps"]
    ):
        bad(name, f"snapshot DOP853 vs GMAT {pos:.3g} m, {vel:.3g} m/s")


def cmd_verify_baseline(args: argparse.Namespace) -> int:
    data = snap.read_json(Path(args.path))
    snap._check_structure(data)
    expected, failures = record_all()  # a fresh recording: inventory and inputs
    if failures:
        print("fresh recording failed:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    problems = verify_baseline(data, expected)
    print("\n".join(problems) if problems else "baseline verification: PASS")
    return 1 if problems else 0


def compare(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ra, rb = a["records"], b["records"]
    worst: dict[str, float] = {}
    where: dict[str, str] = {}
    changed_kind = []
    for key in sorted(set(ra) & set(rb)):
        x, y = ra[key], rb[key]
        if (x["seed"], x["exact"], set(x["parts"])) != (y["seed"], y["exact"], set(y["parts"])):
            changed_kind.append(key)
            continue
        for name, part in x["parts"].items():
            other = y["parts"][name]
            if part["shape"] != other["shape"]:
                changed_kind.append(f"{key}.{name}")
                continue
            d = np.abs(np.asarray(part["values"]) - np.asarray(other["values"]))
            cls = f"{x['seed']}:{snap.unit_of(name)}{':exact' if x['exact'] else ''}"
            m = float(d.max()) if d.size else 0.0
            if m >= worst.get(cls, -1.0):
                worst[cls], where[cls] = m, f"{key}.{name}"
    return {
        "max_abs_difference_by_class": dict(sorted(worst.items())),
        "argmax_by_class": dict(sorted(where.items())),
        "only_in_first": sorted(set(ra) - set(rb)),
        "only_in_second": sorted(set(rb) - set(ra)),
        "changed_kind_or_shape": changed_kind,
    }


def cmd_compare(args: argparse.Namespace) -> int:
    a, b = (snap.read_json(Path(p)) for p in (args.first, args.second))
    result = compare(a, b)
    print(json.dumps(result, indent=2))
    structural = (
        result["only_in_first"] or result["only_in_second"] or result["changed_kind_or_shape"]
    )
    return 1 if structural else 0


def cmd_measure_deviation(args: argparse.Namespace) -> int:
    candidate = Path(args.candidate).resolve()
    proof = _load_module("m2_proof", "toolbox/validators/m2_proof.py")
    cli = _load_module("gmat_m2_cli", "toolbox/scripts/gmat_m2.py")
    saved = dict(snap.TOLERANCES)
    snap.TOLERANCES.update({k: math.inf for k in snap.TOLERANCES})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    structural: list[str] = []
    try:
        with snap.session("m2_proof", path=candidate, authenticate=False) as s:
            proof.main(["--out", str(out.with_suffix(".proof.json"))])
        results["m2_proof"] = s.report()
        structural += s.finish(complete=True)
        for name in cli.gmat_m2.GMAT_MISSIONS:
            ep = f"gmat_m2:{name}"
            with snap.session(ep, path=candidate, authenticate=False) as s:
                cli._evaluate(name)
            results[ep] = s.report()
            structural += s.finish(complete=True)
    finally:
        snap.TOLERANCES.clear()
        snap.TOLERANCES.update(saved)
    overall: dict[str, float] = {}
    for rep in results.values():
        for cls, v in rep["max_deviation_by_class"].items():
            overall[cls] = max(overall.get(cls, 0.0), v)
    summary = {
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "environment": _environment(),
        "max_deviation_by_class": dict(sorted(overall.items())),
        "by_entrypoint": results,
        "structural_problems": structural,
    }
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {k: summary[k] for k in ("max_deviation_by_class", "structural_problems")}, indent=2
        )
    )
    return 1 if structural else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--out", required=True)
    g.add_argument("--measurement", action="store_true")
    g.set_defaults(func=cmd_generate)
    v = sub.add_parser("verify-baseline")
    v.add_argument("path")
    v.set_defaults(func=cmd_verify_baseline)
    c = sub.add_parser("compare")
    c.add_argument("first")
    c.add_argument("second")
    c.set_defaults(func=cmd_compare)
    d = sub.add_parser("measure-deviation")
    d.add_argument("candidate")
    d.add_argument("--out", required=True)
    d.set_defaults(func=cmd_measure_deviation)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
