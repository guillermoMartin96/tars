"""Run the Milestone 2 Proof checks O1-O8 and the event-log contract checks (T5).

Usage:
    uv run python toolbox/validators/m2_proof.py [--out PATH] [--quick]

Missions: the reference missions in tars.validation.m2_missions (prograde slice,
retrograde, burn to depletion, invalid commands and two derived variants), plus the
DR-0018 stop-time variants of the slice and the O3 free-space case.

Two kinds of check:
- **Contract checks** (exact; no tolerance): event order and cadence, command/burn
  traceability, declared receipts and predicted burn lifecycle, mass bookkeeping
  identities, rejected commands change nothing (control run), in-process determinism,
  DR-0018 observation boundary. Their requirement comes from approved contracts, so
  they report threshold_status "approved", as M1's mission/determinism checks do.
- **Numerical oracles** O1-O8 against proof/thresholds/m2.json, which is
  PROVISIONAL until the T7 threshold DR. O9 (GMAT) is T6.

``--quick`` skips O6 and O8 (the multi-run studies). It is for local iteration only;
the Proof report must be produced without it.

Output: a JSON report. Exit code 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import tars
from tars.sim.runner import RunResult, run_scenario
from tars.sim.scenario import ScenarioV2
from tars.validation import m2
from tars.validation.cross_platform import platform_info
from tars.validation.m2_missions import ACCEPT, MISSIONS, Mission
from tars.validation.thresholds import Check, load_scoped_thresholds

O3_DURATION_S = 77.3  # the slice burn, in free space


def _exact(name: str, violations: list[str]) -> Check:
    """A contract check: zero violations required (not a tolerance)."""
    return Check(
        name,
        {"violations": float(len(violations))},
        {"violations": 0.0},
        "approved",
        "; ".join(violations[:10]),
    )


def _burn_table(scenario: ScenarioV2, run: RunResult) -> list[dict[str, Any]]:
    accepted = {e.burn_id: e for e in run.events if e.type == "CommandAccepted"}
    ends = {e.burn_id: e for e in run.events if e.type == "BurnEnded"}
    rows = []
    for burn_id, acc in accepted.items():
        end = ends.get(burn_id)
        rows.append(
            {
                "burn_id": burn_id,
                "command_id": acc.command_id,
                "direction": acc.direction,
                "commanded_ignition_t_s": acc.commanded_ignition_t_s,
                "commanded_duration_s": acc.commanded_duration_s,
                # DR-0017: per-burn timing-induced delta-v error, reported at acceptance.
                # A bound on thrust-integrated speed change only, not on trajectory error.
                "dr0017_timing_delta_v_error_mps": acc.timing_delta_v_error_mps,
                "end_cause": None if end is None else end.end_cause,
                "cutoff_t_s": None if end is None else end.event_t_s,
                "executed_duration_s": None if end is None else end.executed_duration_s,
                "propellant_used_kg": None if end is None else end.propellant_used_kg,
                "sensed_delta_v_mps": None if end is None else end.sensed_delta_v_mps,
            }
        )
    return rows


def mission_checks(
    mission: Mission, thresholds: Any, quick: bool
) -> tuple[list[Check], dict[str, Any]]:
    scenario = mission.build()
    run = run_scenario(scenario)
    events = run.events
    tag = mission.name

    def check(group: str, metrics: dict[str, float], notes: str = "") -> Check:
        return Check(
            f"{group}[{tag}]",
            metrics,
            thresholds.for_validator(group, tag),
            thresholds.status,
            notes,
        )

    predicted = m2.predict_burns(scenario, mission.expected)
    checks = [
        _exact(f"event_order[{tag}]", m2.check_event_order(scenario, events)),
        _exact(
            f"traceability[{tag}]",
            m2.check_traceability(scenario, events, mission.expected, run),
        ),
        _exact(f"outcomes[{tag}]", m2.check_outcomes(scenario, events, predicted)),
    ]
    accounting, identities = m2.accounting_metrics(scenario, events)
    checks.append(_exact(f"accounting_identities[{tag}]", identities))
    if scenario.spacecraft is not None:
        checks.append(check("accounting", accounting))

    first = m2.events_sha256(events)
    second = m2.events_sha256(run_scenario(scenario).events)
    checks.append(
        _exact(
            f"determinism[{tag}]",
            [] if first == second else [f"in-process replay differs: {first} vs {second}"],
        )
    )
    if mission.control_of:
        control = run_scenario(m2.control_scenario(scenario, mission.expected))
        same = m2.physical_projection(control.events) == m2.physical_projection(events)
        checks.append(
            _exact(
                f"rejections_change_nothing[{tag}]",
                [] if same else ["physical events differ from the accepted-only control run"],
            )
        )

    info: dict[str, Any] = {
        "scenario_hash": scenario.config_hash(),
        "events_sha256": first,
        "events": len(events),
        "status": run.status,
        "final_state": {"t": run.final.t, "r": run.final.r.tolist(), "v": run.final.v.tolist()},
        "final_propellant_kg": accounting.get("final_propellant_kg"),
        "receipts": [
            {
                "command_id": r.command_id,
                "status": str(r.status),
                "reason": r.reason and str(r.reason),
            }
            for r in run.receipts
        ],
        "burns": _burn_table(scenario, run),
    }
    if mission.physics:
        o1, o2, residual = m2.mass_and_rocket_metrics(scenario, events, predicted)
        checks.append(_exact(f"o1_identities[{tag}]", residual))
        checks.append(check("o1_mass_law", o1))
        checks.append(check("o2_rocket_equation", o2))
        o4, ref = m2.reference_metrics(scenario, events, predicted)
        checks.append(check("o4_reference", o4, "SciPy DOP853 rtol 1e-13, independent RHS"))
        checks.append(check("o5_coast_kepler", m2.coast_metrics(scenario, events)))
        o7 = m2.direction_metrics(scenario, events)
        checks.append(check("o7_direction", o7))
        if not quick:
            o8 = m2.convergence_metrics(scenario, ref[events[-1].t])
            checks.append(check("o8_convergence", o8, "dt 10 -> 5 -> 2.5 s vs DOP853"))
    if mission.impulsive_limit and not quick:
        rows = m2.impulsive_family(scenario)
        checks.append(check("o6_impulsive_limit", m2.impulsive_metrics(rows)))
        info["impulsive_family"] = rows
    return checks, info


def boundary_checks() -> tuple[list[Check], dict[str, Any]]:
    """DR-0018 option A on stop-time variants of the slice, and the same-tick rule."""
    slice_mission = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
    base = slice_mission.build()
    checks: list[Check] = []
    info: dict[str, Any] = {}
    for case in m2.BOUNDARY_CASES:
        variant = m2.boundary_variant(base, case)
        longer = m2.boundary_variant(base, case, stop_s=base.stop.duration_s)
        run, longer_run = run_scenario(variant), run_scenario(longer)
        violations = m2.boundary_violations(variant, run, longer_run, (ACCEPT,))
        checks.append(_exact(f"dr0018_boundary[{case.name}]", violations))
        last = [e for e in run.events if e.type == "PropulsionSampled"][-1]
        info[case.name] = {
            "stop_s": case.stop_s,
            "burn_events": [e.type for e in run.events if e.type in m2.ENGINE_EVENTS],
            "final_engine_state": last.engine_state,
            "active_burn_id": last.active_burn_id,
            "pending_burn_ids": list(last.pending_burn_ids),
        }

    # Same-tick submission and ignition (T3 semantics, approved; documented, unchanged):
    # a burn submitted at tick k for ignition at k*dt is reported at tick k + 1.
    depletion = next(m for m in MISSIONS if m.name == "m2_burn_to_depletion").build()
    events = run_scenario(depletion).events
    accepted = next(e for e in events if e.type == "CommandAccepted")
    started = next(e for e in events if e.type == "BurnStarted")
    k = round(accepted.commanded_ignition_t_s / depletion.dt_s)
    same_tick = []
    if accepted.tick != k or accepted.commanded_ignition_t_s != k * depletion.dt_s:
        same_tick.append("mission no longer submits at its ignition tick")
    if (started.tick, started.event_t_s) != (k + 1, accepted.commanded_ignition_t_s):
        same_tick.append(f"BurnStarted at tick {started.tick} t={started.event_t_s!r}")
    checks.append(_exact("same_tick_submission_reporting", same_tick))
    info["same_tick_submission"] = {
        "submitted_tick": accepted.tick,
        "ignition_t_s": started.event_t_s,
        "reported_tick": started.tick,
    }
    return checks, info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("runs") / "proof" / "m2.json")
    parser.add_argument("--quick", action="store_true", help="skip O6 and O8 (not for Proof)")
    args = parser.parse_args(argv)

    thresholds = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
    checks: list[Check] = []
    missions: dict[str, Any] = {}
    for mission in MISSIONS:
        mission_checks_, info = mission_checks(mission, thresholds, args.quick)
        checks += mission_checks_
        missions[mission.name] = info
    boundary, boundary_info = boundary_checks()
    checks += boundary

    veh = m2.vehicle(MISSIONS[0].build())
    assert veh is not None
    checks.append(
        Check(
            "o3_free_space",
            m2.free_space_metrics(veh, O3_DURATION_S),
            thresholds.for_validator("o3_free_space"),
            thresholds.status,
            "production Simulator, zero force, velocity tracking along v0",
        )
    )
    unused = [] if args.quick else thresholds.unused()
    checks.append(_exact("thresholds_all_consumed", [f"unused {u}" for u in unused]))

    report = {
        "milestone": "M2",
        "task": "T5",
        "software_version": tars.__version__,
        "platform": platform_info(),
        "threshold_status": thresholds.status,
        "quick": args.quick,
        "missions": missions,
        "dr0018_boundary": boundary_info,
        "results": [c.to_event().model_dump(mode="json") for c in checks],
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
        if not c.passed and c.notes:
            print(f"        {c.notes}")
    print(
        f"thresholds: {thresholds.status}{' (quick: O6/O8 skipped)' if args.quick else ''}; "
        f"overall: {'PASS' if report['passed'] else 'FAIL'} -> {args.out}"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
