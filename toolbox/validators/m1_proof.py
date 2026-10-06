"""Run every M1 Proof check that does not require GMAT (DR-0007).

Usage:
    uv run python toolbox/validators/m1_proof.py [--scenario PATH] [--out PATH]

Checks: invariants, Kepler-reference error, node-crossing period, RK4 convergence
order, in-process determinism, and static architecture rules. Thresholds come from
proof/thresholds/m1.json; metrics without a threshold are reported, not gated.

Output: a JSON report (validator results as ValidationResult events, plus the
convergence table). Exit code 0 if all gated checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import tars
from tars.sim.runner import run_scenario
from tars.sim.scenario import load_scenario
from tars.validation import architecture, determinism, orbit
from tars.validation.convergence import convergence_study
from tars.validation.cross_platform import platform_info
from tars.validation.thresholds import REPO_ROOT, Check, load_thresholds

DEFAULT_SCENARIO = REPO_ROOT / "scenarios" / "m1_leo_250km.json"
STUDY_DTS = (60.0, 30.0, 20.0, 10.0, 5.0, 2.5, 1.0)
# Asymptotic regime: below ~2.5 s the error approaches the round-off floor.
FIT_DTS = (20.0, 10.0, 5.0, 2.5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--out", type=Path, default=Path("runs") / "proof" / "m1_non_gmat.json")
    args = parser.parse_args(argv)

    scenario = load_scenario(args.scenario)
    thresholds = load_thresholds()
    status = thresholds.status
    mu = scenario.constants.mu

    def check(name: str, metrics: dict[str, float], notes: str = "") -> Check:
        return Check(name, metrics, thresholds.for_validator(name), status, notes)

    run = run_scenario(scenario)
    # Mission success is a hard requirement, not a tunable tolerance.
    mission = Check(
        "mission",
        {
            "failed": float(run.status != "success"),
            "orbits_short_of_target": float(scenario.stop.orbits - run.completed.orbits_completed),
        },
        {"failed": 0.0, "orbits_short_of_target": 0.0},
        "approved",
        f"failure_cause={run.failure_cause}",
    )
    checks = [
        mission,
        check("invariants", orbit.invariant_metrics(run.samples, mu)),
        check(
            "kepler_reference",
            orbit.trajectory_error_metrics(run.samples, orbit.kepler_reference(run.initial, mu)),
        ),
        check("period", orbit.period_metrics(run.crossing_times, run.initial, mu)),
    ]

    points, order = convergence_study(scenario, STUDY_DTS, FIT_DTS)
    checks.append(
        check(
            "convergence",
            {"fitted_order": order, "order_deviation_from_4": abs(order - 4.0)},
            f"fit over dt={list(FIT_DTS)} s",
        )
    )

    hashes = determinism.repeat_hashes(scenario, runs=2)
    det = Check(
        "determinism",
        {"distinct_hashes_minus_one": float(len(set(hashes)) - 1)},
        {"distinct_hashes_minus_one": 0.0},
        "approved",
        f"sha256={hashes[0]}",
    )
    checks.append(det)

    violations = architecture.scan(REPO_ROOT / "src" / "tars")
    checks.append(
        Check(
            "architecture",
            {"violations": float(len(violations))},
            {"violations": 0.0},
            "approved",
            "; ".join(f"{v.path}:{v.line} {v.module} ({v.rule})" for v in violations),
        )
    )

    report = {
        "milestone": "M1",
        "scenario": scenario.name,
        "scenario_hash": scenario.config_hash(),
        "software_version": tars.__version__,
        "platform": platform_info(),
        "threshold_status": status,
        "final_state": {"t": run.final.t, "r": run.final.r.tolist(), "v": run.final.v.tolist()},
        "results": [c.to_event().model_dump(mode="json") for c in checks],
        "convergence_table": [asdict(p) for p in points],
        "passed": all(c.passed for c in checks),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")

    for c in checks:
        mark = "PASS" if c.passed else "FAIL"
        shown = ", ".join(f"{k}={v:.6g}" for k, v in c.metrics.items())
        print(f"[{mark}] {c.validator}: {shown}")
        for failure in c.failures:
            print(f"        limit exceeded: {failure}")
    print("convergence (dt s -> position error m, |dE/E|):")
    for p in points:
        print(f"    {p.dt_s:>5g} -> {p.position_error_m:.4e}, {p.energy_rel_error:.3e}")
    print(f"thresholds: {status}; overall: {'PASS' if report['passed'] else 'FAIL'} -> {args.out}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
