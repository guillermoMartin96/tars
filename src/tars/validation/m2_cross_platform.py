"""M2 cross-platform final-state gate (DR-0015 open row; DR-0023 decision 4).

Same-platform replay is byte-identical (``determinism``); across CPUs and operating
systems last-bit floating-point differences are expected (DR-0006), and a burn amplifies
them about 2.5x (VAL-0016). The gate bounds the Euclidean difference of every M2
mission's final position and velocity between platforms by the approved limits in
``proof/thresholds/m2.json`` group ``cross_platform`` (1e-4 m, 1e-7 m/s).

Evidence: each platform runs every canonical mission (``tars.validation.m2_missions``)
and writes one self-describing *evidence* record: provenance (revision, clean tree,
platform identity, environment, CI run), the canonical input digest of every mission,
and every final state. Two uses:

- ``gate``: evidence from the three required platforms (DR-0008 matrix: macOS x86_64,
  Linux x86_64, macOS arm64) at ONE revision is compared pairwise. CI produces it in
  one workflow run, so every record has the same revision and run id.
- ``compare_with_golden``: a single run is compared with the committed reference-host
  record (``proof/references/m2_final_states.json``, sha256-pinned in
  ``approved_digests``), as M1 does (``cross_platform``). The M2 Proof runs it on every
  platform.

Fail closed (DR-0023 implementation requirements): missing, corrupted, inconsistent or
stale evidence is a violation, never a skipped comparison. "Stale" means: a different
revision than the one being gated, a canonical input that no longer matches the
checkout, or a mission set that differs from the current one.

Threat model (DR-0019 B, DR-0022 B condition 1): the record digest detects corruption
and accidental edits; it does not authenticate a deliberately forged record. CI records
are produced and consumed within one workflow run; the committed golden is pinned by
a reviewed digest.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from tars.validation.thresholds import REPO_ROOT

SCHEMA = "tars.m2.final-state-evidence/1"
GOLDEN_M2 = REPO_ROOT / "proof" / "references" / "m2_final_states.json"

# DR-0008 / DR-0015 three-platform matrix: platform id -> (platform.system(), machine).
REQUIRED_PLATFORMS: dict[str, tuple[str, str]] = {
    "macos-x86_64": ("Darwin", "x86_64"),
    "linux-x86_64": ("Linux", "x86_64"),
    "macos-arm64": ("Darwin", "arm64"),
}
GOLDEN_PLATFORM = "macos-x86_64"  # the DR-0008 reference host

# GitHub runner architecture and OS names, cross-checked against platform.machine()
# and platform.system(); platform.platform() prefixes, cross-checked likewise
# (review T7-F7: a relabelled Linux record must not fill the macOS x86_64 slot).
_RUNNER_ARCH = {"X64": "x86_64", "ARM64": "arm64"}
_RUNNER_OS = {"Linux": "Linux", "macOS": "Darwin"}
_OS_PREFIX = {"Linux": "Linux-", "Darwin": "macOS-"}

_TOP_KEYS = frozenset(
    {"schema", "revision", "tree_clean", "platform", "environment", "ci", "inputs", "missions",
     "sha256"}
)  # fmt: skip
_PLATFORM_KEYS = frozenset({"id", "system", "machine", "cpu", "translated"})
_MISSION_KEYS = frozenset({"status", "final_tick", "final_t", "r", "v", "events_sha256"})

POSITION = "final_position_difference_m"
VELOCITY = "final_velocity_difference_mps"


# ------------------------------------------------------------------ collection


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _translated() -> bool:
    """True when a macOS process runs under Rosetta 2 translation. An x86_64 Python on
    Apple silicon reports machine "x86_64" and would otherwise pass for macOS x86_64."""
    if platform.system() != "Darwin":
        return False
    proc = subprocess.run(
        ["sysctl", "-n", "sysctl.proc_translated"], capture_output=True, text=True
    )
    return proc.stdout.strip() == "1"


def platform_id(system: str, machine: str) -> str | None:
    for pid, key in REQUIRED_PLATFORMS.items():
        if key == (system, machine):
            return pid
    return None


def platform_identity() -> dict[str, Any]:
    from tars.validation.cross_platform import platform_info

    info = platform_info()
    return {
        "id": platform_id(info["system"], info["machine"]),
        "system": info["system"],
        "machine": info["machine"],
        "cpu": info["cpu"],
        "translated": _translated(),
    }


def _environment() -> dict[str, Any]:
    import scipy

    return {
        "os": platform.platform(),
        "python": platform.python_version(),
        "python_compiler": platform.python_compiler(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "uv_lock_sha256": hashlib.sha256((REPO_ROOT / "uv.lock").read_bytes()).hexdigest(),
    }


def _ci() -> dict[str, Any] | None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return None
    return {
        key.lower(): os.environ.get(key)
        for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA", "GITHUB_JOB",
                    "RUNNER_OS", "RUNNER_ARCH")
    }  # fmt: skip


def canonical_inputs() -> dict[str, str]:
    """Config hash of every canonical mission scenario, as built from the checkout."""
    from tars.validation.m2_missions import MISSIONS

    return {m.name: m.build().config_hash() for m in MISSIONS}


def record_digest(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def collect() -> dict[str, Any]:
    """Run every canonical mission on this platform and return its evidence record."""
    from tars.sim.runner import run_scenario
    from tars.validation import m2
    from tars.validation.m2_missions import MISSIONS

    inputs: dict[str, str] = {}
    missions: dict[str, Any] = {}
    for mission in MISSIONS:
        scenario = mission.build()
        inputs[mission.name] = scenario.config_hash()
        run = run_scenario(scenario)
        missions[mission.name] = {
            "status": run.status,
            "final_tick": run.final.tick,
            "final_t": run.final.t,
            "r": run.final.r.tolist(),
            "v": run.final.v.tolist(),
            "events_sha256": m2.events_sha256(run.events),
        }
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "revision": _git("rev-parse", "HEAD"),
        "tree_clean": _git("status", "--porcelain") == "",
        "platform": platform_identity(),
        "environment": _environment(),
        "ci": _ci(),
        "inputs": inputs,
        "missions": missions,
    }
    record["sha256"] = record_digest(record)
    return record


# ------------------------------------------------------------------ validation


def _vector(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in value)
        and all(math.isfinite(x) for x in value)
    )


def _is_sha256(value: Any) -> bool:
    hexdigits = "0123456789abcdef"
    return isinstance(value, str) and len(value) == 64 and all(c in hexdigits for c in value)


def record_problems(
    record: Any,
    *,
    label: str,
    expected_inputs: dict[str, str],
    revision: str | None,
    run_id: str | None = None,
) -> list[str]:
    """Every reason one evidence record cannot be used (empty list: usable).

    ``revision``: the revision being gated (None: no revision requirement, as for the
    committed golden, whose staleness is decided by its inputs). ``run_id``: the CI
    run that must have produced the record (None: not produced in CI).
    """
    if not isinstance(record, dict):
        return [f"{label}: not a JSON object"]
    problems: list[str] = []
    keys = set(record)
    if keys != _TOP_KEYS:
        return [f"{label}: keys {sorted(keys ^ _TOP_KEYS)} missing or unexpected"]
    if record["schema"] != SCHEMA:
        problems.append(f"{label}: schema {record['schema']!r} is not {SCHEMA!r}")
    if record["sha256"] != record_digest(record):
        problems.append(f"{label}: record digest mismatch (corrupted or edited)")
    rev = record["revision"]
    if not (isinstance(rev, str) and len(rev) == 40 and all(c in "0123456789abcdef" for c in rev)):
        problems.append(f"{label}: revision {rev!r} is not a git commit id")
    elif revision is not None and rev != revision:
        problems.append(f"{label}: stale: revision {rev} is not the gated revision {revision}")
    if record["tree_clean"] is not True:
        problems.append(f"{label}: produced from a modified working tree")

    plat = record["platform"]
    if not isinstance(plat, dict) or set(plat) != _PLATFORM_KEYS:
        problems.append(f"{label}: malformed platform identity")
    else:
        expected_id = platform_id(plat["system"], plat["machine"])
        if expected_id is None or plat["id"] != expected_id:
            problems.append(
                f"{label}: platform {plat['id']!r} ({plat['system']}, {plat['machine']}) "
                "is not a required platform"
            )
        if plat["translated"] is not False:
            problems.append(f"{label}: produced under binary translation (Rosetta)")
        if not isinstance(plat["cpu"], str) or not plat["cpu"].strip():
            problems.append(f"{label}: CPU model not recorded")

    ci = record["ci"]
    if ci is not None:
        if not isinstance(ci, dict):
            problems.append(f"{label}: malformed CI provenance")
        else:
            if ci.get("github_sha") != rev:
                problems.append(f"{label}: CI commit {ci.get('github_sha')} != revision")
            machine = plat.get("machine") if isinstance(plat, dict) else None
            system = plat.get("system") if isinstance(plat, dict) else None
            if _RUNNER_ARCH.get(str(ci.get("runner_arch"))) != machine:
                problems.append(
                    f"{label}: runner architecture {ci.get('runner_arch')} does not "
                    f"match machine {machine}"
                )
            if _RUNNER_OS.get(str(ci.get("runner_os"))) != system:
                problems.append(
                    f"{label}: runner OS {ci.get('runner_os')} does not match system {system}"
                )
    if run_id is not None and (not isinstance(ci, dict) or ci.get("github_run_id") != run_id):
        problems.append(f"{label}: not produced by CI run {run_id}")

    env = record["environment"]
    if not isinstance(env, dict) or not _is_sha256(env.get("uv_lock_sha256")):
        problems.append(f"{label}: environment provenance missing")
    elif isinstance(plat, dict):
        # platform.platform(), e.g. "Linux-6.17.0-azure-x86_64-with-glibc2.39" or
        # "macOS-15.7.9-x86_64-i386-64bit": must name the declared OS and machine.
        os_name = env.get("os")
        prefix = _OS_PREFIX.get(str(plat.get("system")))
        if (
            not isinstance(os_name, str)
            or prefix is None
            or not os_name.startswith(prefix)
            or str(plat.get("machine")) not in os_name.split("-")
        ):
            problems.append(
                f"{label}: environment OS {os_name!r} contradicts platform "
                f"{plat.get('system')} {plat.get('machine')}"
            )

    inputs = record["inputs"]
    if inputs != expected_inputs:
        if not isinstance(inputs, dict):
            problems.append(f"{label}: malformed inputs")
        else:
            missing = sorted(set(expected_inputs) - set(inputs))
            extra = sorted(set(inputs) - set(expected_inputs))
            changed = sorted(
                k for k in set(inputs) & set(expected_inputs) if inputs[k] != expected_inputs[k]
            )
            problems.append(
                f"{label}: stale or mismatched inputs (missing {missing}, unexpected "
                f"{extra}, digest differs {changed})"
            )

    missions = record["missions"]
    if not isinstance(missions, dict) or set(missions) != set(expected_inputs):
        got = sorted(missions) if isinstance(missions, dict) else missions
        problems.append(f"{label}: incomplete mission set {got}")
    else:
        for name, m in sorted(missions.items()):
            if not isinstance(m, dict) or set(m) != _MISSION_KEYS:
                problems.append(f"{label}/{name}: malformed final state")
                continue
            if not (_vector(m["r"]) and _vector(m["v"])):
                problems.append(f"{label}/{name}: final position/velocity not 3 finite numbers")
            if not isinstance(m["final_tick"], int) or isinstance(m["final_tick"], bool):
                problems.append(f"{label}/{name}: final tick is not an integer")
            if not isinstance(m["final_t"], float) or not math.isfinite(m["final_t"]):
                problems.append(f"{label}/{name}: final time is not a finite number")
            if m["status"] != "success":
                problems.append(f"{label}/{name}: run status {m['status']!r}")
            if not _is_sha256(m["events_sha256"]):
                problems.append(f"{label}/{name}: event-log digest missing")
    return problems


# ------------------------------------------------------------------ comparison


@dataclass
class Comparison:
    """Worst pairwise final-state differences, plus contract violations (exact)."""

    metrics: dict[str, float] = field(default_factory=dict)
    per_mission: dict[str, dict[str, float]] = field(default_factory=dict)
    pairs: list[dict[str, Any]] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)


def _difference(a: dict[str, Any], b: dict[str, Any]) -> tuple[float, float]:
    dr = float(np.linalg.norm(np.array(a["r"], dtype=float) - np.array(b["r"], dtype=float)))
    dv = float(np.linalg.norm(np.array(a["v"], dtype=float) - np.array(b["v"], dtype=float)))
    # Any non-finite difference is +inf, so the gate fails (never NaN, never skipped).
    return (dr if math.isfinite(dr) else math.inf, dv if math.isfinite(dv) else math.inf)


def compare(records: Sequence[tuple[str, dict[str, Any]]], missions: Iterable[str]) -> Comparison:
    """Pairwise comparison of validated records. Discrete outcomes (status, final tick,
    final time) must agree exactly; positions and velocities are measured."""
    out = Comparison()
    worst_r = worst_v = 0.0
    for mission in sorted(missions):
        mr = mv = 0.0
        for (la, a), (lb, b) in combinations(records, 2):
            ma, mb = a["missions"][mission], b["missions"][mission]
            for key in ("status", "final_tick", "final_t"):
                if ma[key] != mb[key]:
                    out.violations.append(f"{mission}: {key} {la}={ma[key]!r} {lb}={mb[key]!r}")
            dr, dv = _difference(ma, mb)
            out.pairs.append({"mission": mission, "a": la, "b": lb, POSITION: dr, VELOCITY: dv})
            mr, mv = max(mr, dr), max(mv, dv)
        out.per_mission[mission] = {POSITION: mr, VELOCITY: mv}
        worst_r, worst_v = max(worst_r, mr), max(worst_v, mv)
    out.metrics = {POSITION: worst_r, VELOCITY: worst_v}
    return out


def gate(
    records: Sequence[tuple[str, Any]],
    *,
    revision: str,
    run_id: str | None = None,
    expected_inputs: dict[str, str] | None = None,
) -> Comparison:
    """The three-platform gate at one revision. Every record is validated; the set must
    cover every required platform; any problem is a violation (fail closed)."""
    expected = canonical_inputs() if expected_inputs is None else expected_inputs
    out = Comparison()
    problems: list[str] = []
    for label, record in records:
        problems += record_problems(
            record, label=label, expected_inputs=expected, revision=revision, run_id=run_id
        )
    digests = [r.get("sha256") for _, r in records if isinstance(r, dict)]
    if len(set(digests)) != len(digests):
        problems.append("duplicate evidence records")
    if not problems:
        present = {r["platform"]["id"] for _, r in records}
        missing = sorted(set(REQUIRED_PLATFORMS) - present)
        if missing:
            problems.append(f"required platforms without evidence: {missing}")
        envs = {r["environment"]["uv_lock_sha256"] for _, r in records}
        if len(envs) != 1:
            problems.append(f"records use different locked environments: {sorted(envs)}")
    if problems:
        # Nothing is compared on unusable evidence: the metrics are +inf (fail).
        out.metrics = {POSITION: math.inf, VELOCITY: math.inf}
        out.violations = problems
        return out
    return compare(records, expected)


def load_golden(path: Path = GOLDEN_M2) -> dict[str, Any]:
    """The committed reference-host record, authenticated against its reviewed digest."""
    from tars.validation.approved_digests import APPROVED_M2_GOLDEN_SHA256

    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != APPROVED_M2_GOLDEN_SHA256:
        raise ValueError(
            f"{path.name} is not the approved golden record (sha256 {digest}); a reviewed "
            "change must update tars.validation.approved_digests"
        )
    return json.loads(raw)


def golden_problems(golden: Any, expected_inputs: dict[str, str]) -> list[str]:
    problems = record_problems(
        golden, label="golden", expected_inputs=expected_inputs, revision=None
    )
    if not problems and golden["platform"]["id"] != GOLDEN_PLATFORM:
        problems.append(f"golden: platform {golden['platform']['id']} is not the reference host")
    if not problems and golden["ci"] is not None:
        problems.append("golden: not produced on the DR-0008 reference host (CI record)")
    return problems


def compare_with_golden(
    mission: str, scenario_hash: str, run: Any, golden: dict[str, Any]
) -> tuple[dict[str, float], list[str]]:
    """One run against the validated golden record (``golden_problems`` already empty).
    Returns the metrics and exact violations (stale input, status, tick, time)."""
    violations: list[str] = []
    entry = golden["missions"].get(mission)
    if entry is None or golden["inputs"].get(mission) != scenario_hash:
        return {POSITION: math.inf, VELOCITY: math.inf}, [f"{mission}: no golden for this input"]
    if run.status != entry["status"]:
        violations.append(f"{mission}: status {run.status!r} != golden {entry['status']!r}")
    if run.final.tick != entry["final_tick"] or run.final.t != entry["final_t"]:
        violations.append(f"{mission}: final tick/time differs from golden")
    dr, dv = _difference(entry, {"r": run.final.r.tolist(), "v": run.final.v.tolist()})
    return {POSITION: dr, VELOCITY: dv}, violations
