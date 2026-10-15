"""M2 cross-platform final-state gate (DR-0023 decision 4; DR-0015, DR-0006, DR-0008).

Usage:
    uv run python toolbox/validators/m2_cross_platform.py collect --out FILE
    uv run python toolbox/validators/m2_cross_platform.py gate FILE [FILE ...] \
        [--revision REV] [--run-id ID] [--report PATH]

``collect`` runs every canonical M2 mission on this platform and writes its evidence
record. ``gate`` validates records from the three required platforms (macOS x86_64,
Linux x86_64, macOS arm64), all at ``--revision`` (default: the checked-out HEAD) and,
with ``--run-id``, all produced by that CI run; then compares every pair of platforms
for every mission: Euclidean final position and velocity differences against the
approved ``cross_platform`` limits in proof/thresholds/m2.json. Missing, corrupted,
inconsistent or stale evidence fails the gate (exit 1).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from tars.validation import m2_cross_platform as xp
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import REPO_ROOT, Check, load_scoped_thresholds


def _read(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return f"unreadable: {exc}"  # rejected by record_problems (not a JSON object)


def cmd_collect(args: argparse.Namespace) -> int:
    record = xp.collect()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(
        f"wrote {args.out}: platform {record['platform']['id']} ({record['platform']['cpu']}), "
        f"revision {record['revision']}, clean tree {record['tree_clean']}"
    )
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    revision = (
        args.revision
        or subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    thresholds = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
    records = [(str(p), _read(p)) for p in args.evidence]
    result = xp.gate(records, revision=revision, run_id=args.run_id)
    platforms = [
        f"{r['platform']['id']}: {r['platform']['cpu']}"
        for _, r in records
        if isinstance(r, dict) and isinstance(r.get("platform"), dict)
    ]
    measured = Check(
        "m2_cross_platform",
        result.metrics,
        thresholds.for_validator("cross_platform"),
        thresholds.status,
        f"revision {revision}; platforms {platforms}",
    )
    contract = Check(
        "m2_cross_platform_evidence",
        {"violations": float(len(result.violations))},
        {"violations": 0.0},
        "approved",
        "; ".join(result.violations[:20]),
    )
    passed = measured.passed and contract.passed
    report = {
        "gate": "m2_cross_platform",
        "revision": revision,
        "run_id": args.run_id,
        "evidence": [label for label, _ in records],
        "platforms": platforms,
        # repr keeps a fail-closed +inf representable in JSON ("inf").
        "checks": [
            {
                "validator": c.validator,
                "passed": c.passed,
                "metrics": {k: repr(v) for k, v in c.metrics.items()},
                "thresholds": c.thresholds,
                "threshold_status": c.threshold_status,
                "failures": c.failures,
            }
            for c in (measured, contract)
        ],
        "per_mission": result.per_mission,
        "pairs": result.pairs,
        "violations": result.violations,
        "passed": passed,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    for c in (measured, contract):
        shown = ", ".join(f"{k}={v:.6g}" for k, v in c.metrics.items())
        print(f"[{'PASS' if c.passed else 'FAIL'}] {c.validator}: {shown}")
        for failure in c.failures:
            print(f"        limit exceeded: {failure}")
    for v in result.violations:
        print(f"        {v}")
    for mission, m in sorted(result.per_mission.items()):
        dr, dv = m[xp.POSITION], m[xp.VELOCITY]
        print(f"        {mission}: {xp.POSITION}={dr:.3g} {xp.VELOCITY}={dv:.3g}")
    print(f"platforms: {platforms}")
    print(f"overall: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("collect", help="run every M2 mission and write this platform's evidence")
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_collect)
    p = sub.add_parser("gate", help="three-platform gate at one revision")
    p.add_argument("evidence", type=Path, nargs="+")
    p.add_argument("--revision", help="gated revision (default: HEAD)")
    p.add_argument("--run-id", help="require every record to come from this CI run")
    p.add_argument("--report", type=Path)
    p.set_defaults(func=cmd_gate)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
