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
import math
import sys
from pathlib import Path
from typing import Any

import tars
from tars.events.schema import ValidationResult
from tars.sim.runner import RunResult, run_scenario
from tars.sim.scenario import ScenarioV2
from tars.validation import gmat_m2, m2
from tars.validation.cross_platform import platform_info
from tars.validation.m2_missions import ACCEPT, MISSIONS, Mission
from tars.validation.thresholds import Check, load_scoped_thresholds, load_thresholds

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


def _result(check: Check) -> dict[str, Any]:
    """A check as a ValidationResult. The event schema requires finite metrics, so a
    non-finite one is moved into the notes and the result is a failure; the report is
    always written (T6 review F28)."""
    bad = {k: repr(v) for k, v in check.metrics.items() if not math.isfinite(v)}
    if not bad:
        return check.to_event().model_dump(mode="json")
    notes = "; ".join([f"non-finite metrics {bad}", *check.failures, check.notes])
    return ValidationResult(
        tick=0,
        t=0.0,
        validator=check.validator,
        passed=False,
        metrics={k: v for k, v in check.metrics.items() if k not in bad},
        thresholds=check.thresholds,
        threshold_status=check.threshold_status,
        notes=notes,
    ).model_dump(mode="json")


def _ungated(metrics: dict[str, float], limits: dict[str, float]) -> list[str]:
    return m2.ungated_metrics(metrics, limits)  # shared rule (review M2-T5 F15, M2-T6 F12)


class Gates:
    """Builds numerical checks and records metrics that would escape gating."""

    def __init__(self, thresholds: Any) -> None:
        self.thresholds = thresholds
        self.missing: list[str] = []
        self.non_finite_report_only: list[str] = []

    def check(
        self, group: str, name: str, mission: str, metrics: dict[str, float], notes: str = ""
    ) -> Check:
        limits = self.thresholds.for_validator(group, mission)
        self.missing += [f"{name}: {k}" for k in _ungated(metrics, limits)]
        # Report-only metrics are not gated, but must still be finite (T6 review notes).
        self.non_finite_report_only += [
            f"{name}: {k}={x!r}"
            for k, x in metrics.items()
            if k not in limits and not math.isfinite(x)
        ]
        return Check(name, metrics, limits, self.thresholds.status, notes)


def _audit_checks(gates: Gates, tag: str, mission: str, audit: m2.Audit) -> list[Check]:
    checks = [_exact(f"{k}[{tag}]", v) for k, v in audit.violations.items()]
    for group, metrics in audit.metrics.items():
        checks.append(gates.check(group, f"{group}[{tag}]", mission, metrics))
    return checks


def _merge_audits(audits: list[tuple[str, m2.Audit]]) -> m2.Audit:
    """Auxiliary runs: violations concatenated (prefixed), metrics maximized."""
    violations: dict[str, list[str]] = {}
    metrics: dict[str, dict[str, float]] = {}
    for name, a in audits:
        for k, v in a.violations.items():
            violations.setdefault(k, []).extend(f"{name}: {x}" for x in v)
        for g, ms in a.metrics.items():
            dst = metrics.setdefault(g, {})
            for k, x in ms.items():
                # No -inf sentinel: any non-finite value becomes +inf (F19, F20).
                dst[k] = m2.worst(x) if k not in dst else m2.worst(dst[k], x)
    return m2.Audit(violations, metrics, {})


def mission_checks(
    mission: Mission, gates: Gates, quick: bool
) -> tuple[list[Check], dict[str, Any]]:
    scenario = mission.build()
    run = run_scenario(scenario)
    events = run.events
    tag = mission.name
    audit = m2.audit_run(scenario, mission.expected, run)
    checks = _audit_checks(gates, tag, tag, audit)
    checks.append(
        _exact(f"cli_summary[{tag}]", m2.cli_summary_violations(events, _cli_summary(run)))
    )

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
        "final_propellant_kg": audit.metrics.get("accounting", {}).get("final_propellant_kg"),
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
    if mission.name in gmat_m2.GMAT_MISSIONS:
        # O9 (T6): committed GMAT reference, verified before use (DR-0016, DR-0009).
        gates_m1 = load_thresholds().for_validator("gmat_reference")
        o9 = gmat_m2.compare_committed(
            mission.name,
            scenario,
            mission.expected,
            events,
            gates_m1["script_initial_position_difference_m"],
            gates_m1["script_initial_velocity_difference_mps"],
        )
        checks.append(_exact(f"o9_reference_integrity[{tag}]", o9.violations))
        if not o9.violations:
            checks.append(gates.check("o9_gmat", f"o9_gmat[{tag}]", tag, o9.metrics))
    has_burns = any(e.type == "BurnEnded" for e in events)
    if has_burns and not quick:
        # O8: auxiliary runs at smaller dt are audited like the mission (review F6).
        finals = {scenario.dt_s: run.final.r}
        aux = []
        for dt in m2.O8_DTS[1:]:
            variant = m2.convergence_variant(scenario, dt)
            vrun = run_scenario(variant)
            finals[dt] = vrun.final.r
            aux.append((variant.name, m2.audit_run(variant, mission.expected, vrun)))
        horizon = m2.horizon_s(scenario, events)
        o8 = m2.convergence_metrics(finals, audit.reference[horizon])
        checks.append(gates.check("o8_convergence", f"o8_convergence[{tag}]", tag, o8))
        checks += _audit_checks(gates, f"{tag}/o8_aux", tag, _merge_audits(aux))
    if mission.impulsive_limit and not quick:
        rows, aux = [], []
        for variant in m2.impulsive_variants(scenario):
            vrun = run_scenario(variant)
            rows.append(m2.impulsive_row(scenario, variant, vrun))
            aux.append((variant.name, m2.audit_run(variant, (ACCEPT,), vrun)))
        checks.append(
            gates.check(
                "o6_impulsive_limit", f"o6_impulsive_limit[{tag}]", tag, m2.impulsive_metrics(rows)
            )
        )
        checks += _audit_checks(gates, f"{tag}/o6_aux", tag, _merge_audits(aux))
        info["impulsive_family"] = rows
    return checks, info


def _cli_summary(run: RunResult) -> dict[str, Any]:
    """The CLI's own propulsion summary builder, reconciled with the events."""
    import importlib.util

    from tars.validation.thresholds import REPO_ROOT

    spec = importlib.util.spec_from_file_location(
        "run_mission", REPO_ROOT / "toolbox" / "scripts" / "run_mission.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._propulsion_summary(run)


def boundary_checks(gates: Gates) -> tuple[list[Check], dict[str, Any]]:
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
        # The variant is a run like any other: full audit (review F6).
        audit = m2.audit_run(variant, (ACCEPT,), run)
        checks += _audit_checks(gates, f"dr0018/{case.name}", base.name, audit)
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
    gates = Gates(thresholds)
    checks: list[Check] = []
    missions: dict[str, Any] = {}
    for mission in MISSIONS:
        mission_checks_, info = mission_checks(mission, gates, args.quick)
        checks += mission_checks_
        missions[mission.name] = info
    boundary, boundary_info = boundary_checks(gates)
    checks += boundary

    veh = m2.vehicle(MISSIONS[0].build())
    assert veh is not None
    checks.append(
        gates.check(
            "o3_free_space",
            "o3_free_space",
            "all",
            m2.free_space_metrics(veh, O3_DURATION_S),
            "production Simulator, zero force, velocity tracking along v0",
        )
    )
    unused = [] if args.quick else thresholds.unused()
    checks.append(_exact("thresholds_all_consumed", [f"unused {u}" for u in unused]))
    # Every emitted metric is gated unless declared report-only (review F15): a
    # missing threshold group or metric fails instead of silently passing.
    checks.append(_exact("thresholds_cover_all_metrics", [f"ungated {m}" for m in gates.missing]))
    checks.append(_exact("report_only_metrics_finite", gates.non_finite_report_only))

    report = {
        "milestone": "M2",
        "task": "T5",
        "software_version": tars.__version__,
        "platform": platform_info(),
        "threshold_status": thresholds.status,
        "quick": args.quick,
        "missions": missions,
        "dr0018_boundary": boundary_info,
        "results": [_result(c) for c in checks],
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
