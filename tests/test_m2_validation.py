"""M2 Proof validators (T5): they pass on the reference missions, and each one fails
on a deliberately broken log or a physics mutant (false-pass guards)."""

from __future__ import annotations

import dataclasses
import json
import math

import numpy as np
import pytest

from tars.sim import propulsion as propulsion_module
from tars.sim import simulator as simulator_module
from tars.sim.propulsion import Prograde
from tars.sim.runner import run_scenario
from tars.sim.scenario import ScenarioV2
from tars.validation import m2
from tars.validation.m2_missions import ACCEPT, MISSIONS, Expected, reject
from tars.validation.thresholds import M2_THRESHOLDS, load_scoped_thresholds

BY_NAME = {m.name: m for m in MISSIONS}
LIMITS = json.loads(M2_THRESHOLDS.read_text())["limits"]


@pytest.fixture(scope="module")
def runs():
    out = {}
    for mission in MISSIONS:
        scenario = mission.build()
        out[mission.name] = (mission, scenario, run_scenario(scenario))
    return out


def _contract(mission, scenario, run):
    events = run.events
    predicted = m2.predict_burns(scenario, mission.expected)
    return (
        m2.check_event_order(scenario, events)
        + m2.check_traceability(scenario, events, mission.expected, run)
        + m2.check_outcomes(scenario, events, predicted)
        + m2.accounting_metrics(scenario, events)[1]
    )


# ------------------------------------------------------------------ reference missions


@pytest.mark.parametrize("name", list(BY_NAME))
def test_reference_missions_satisfy_every_contract_check(runs, name):
    assert _contract(*runs[name]) == []


@pytest.mark.parametrize("name", list(BY_NAME))
def test_reference_missions_succeed_with_the_declared_receipts(runs, name):
    mission, _, run = runs[name]
    assert run.status == "success"
    got = [(str(r.status), r.reason and str(r.reason)) for r in run.receipts]
    assert got == [(e.status, e.reason) for e in mission.expected]


def test_every_rejection_code_is_exercised_by_a_reference_mission(runs):
    from tars.sim.propulsion import BurnRejection

    seen = {e.reason for m in MISSIONS for e in m.expected if e.status == "rejected"}
    assert seen == {code.value for code in BurnRejection}


def test_rejected_commands_change_nothing(runs):
    for name in (
        "m2_invalid_commands",
        "m2_burn_to_depletion",
        "m2_invalid_commands_empty_tank",
        "m2_invalid_commands_no_propulsion",
    ):
        mission, scenario, run = runs[name]
        control = run_scenario(m2.control_scenario(scenario, mission.expected))
        assert m2.physical_projection(control.events) == m2.physical_projection(run.events)


def test_physical_projection_detects_a_physical_difference(runs):
    slice_events = runs["m2_prograde_burn"][2].events
    retro_events = runs["m2_retrograde_burn"][2].events
    assert m2.physical_projection(slice_events) != m2.physical_projection(retro_events)


def test_depletion_leaves_the_dr0017_residual_not_an_empty_tank(runs):
    """DR-0017 D1a: the cutoff is the last representable time not after depletion, so
    up to mdot * 2 ulp(cutoff) stays in the tank; later burns are not 'no_propellant'."""
    _, scenario, run = runs["m2_burn_to_depletion"]
    end = next(e for e in run.events if e.type == "BurnEnded")
    mdot = m2.vehicle(scenario).mass_flow_kgps
    assert end.end_cause == "propellant_depleted"
    assert 0.0 <= end.propellant_kg <= mdot * 2 * math.ulp(end.event_t_s)
    assert [r.reason for r in run.receipts[1:]] == [
        "insufficient_propellant",
        "burn_unschedulable",
    ]


# ------------------------------------------------------------------ same-tick reporting


def _one_burn(submit_t_s: float, ignition_t_s: float) -> ScenarioV2:
    raw = BY_NAME["m2_prograde_burn"].build().model_dump(mode="json")
    raw["commands"][0]["submit_t_s"] = submit_t_s
    raw["commands"][0]["command"]["ignition_t_s"] = ignition_t_s
    raw["stop"] = {"duration_s": 1200.0}
    return ScenarioV2.model_validate(raw)


def test_same_tick_submission_and_ignition_is_reported_at_the_next_tick():
    """T3 semantics (approved, unchanged): a burn submitted at tick k for ignition at
    k*dt executes at the start of step k+1 and is reported at tick k+1 with
    event_t_s = k*dt. Submitted earlier, the same ignition is reported at tick k."""
    same = run_scenario(_one_burn(600.0, 600.0)).events
    earlier = run_scenario(_one_burn(590.0, 600.0)).events
    started = [next(e for e in ev if e.type == "BurnStarted") for ev in (same, earlier)]
    assert [(s.tick, s.event_t_s) for s in started] == [(61, 600.0), (60, 600.0)]
    for ev, scenario in ((same, _one_burn(600.0, 600.0)), (earlier, _one_burn(590.0, 600.0))):
        assert m2.check_event_order(scenario, ev) == []
    # The validator predicts the tick independently: swapping the rule is detected.
    moved = [
        e.model_copy(update={"tick": 60, "t": 600.0}) if e.type == "BurnStarted" else e
        for e in same
    ]
    assert any("expected 61" in v for v in m2.check_event_order(_one_burn(600.0, 600.0), moved))


@pytest.mark.parametrize(
    ("event_t", "same_tick", "want"),
    [(600.0, False, 60), (600.0, True, 61), (600.1, False, 61), (677.3, False, 68), (0.0, True, 1)],
)
def test_expected_report_tick(event_t, same_tick, want):
    assert m2._expected_report_tick(event_t, 10.0, same_tick) == want


# ------------------------------------------------------------------ log mutations


def _slice(runs):
    return runs["m2_prograde_burn"]


def _replace(events, predicate, **update):
    return [e.model_copy(update=update) if predicate(e) else e for e in events]


def test_missing_burn_end_is_detected(runs):
    mission, scenario, run = _slice(runs)
    events = [e for e in run.events if e.type != "BurnEnded"]
    trace = m2.check_traceability(scenario, events, mission.expected, run)
    assert any("not active at the stop" in v for v in trace)
    predicted = m2.predict_burns(scenario, mission.expected)
    assert m2.check_outcomes(scenario, events, predicted)


def test_samples_out_of_order_are_detected(runs):
    _, scenario, run = _slice(runs)
    events = list(run.events)
    i = next(i for i, e in enumerate(events) if e.type == "StateSampled" and e.tick == 6)
    events[i], events[i + 1] = events[i + 1], events[i]
    assert any(
        "StateSampled after PropulsionSampled" in v for v in m2.check_event_order(scenario, events)
    )


def test_burn_reported_at_the_wrong_tick_is_detected(runs):
    _, scenario, run = _slice(runs)
    events = _replace(run.events, lambda e: e.type == "BurnEnded", tick=69, t=690.0)
    assert any("expected 68" in v for v in m2.check_event_order(scenario, events))


@pytest.mark.parametrize("change", ["drop", "duplicate"])
def test_propulsion_cadence_errors_are_detected(runs, change):
    _, scenario, run = _slice(runs)
    events = list(run.events)
    i = next(i for i, e in enumerate(events) if e.type == "PropulsionSampled" and e.tick == 64)
    if change == "drop":
        del events[i]
    else:
        events.insert(i, events[i])
    assert any("cadence" in v for v in m2.check_event_order(scenario, events))


def test_wrong_declared_reason_is_detected(runs):
    mission, scenario, run = runs["m2_invalid_commands"]
    wrong = list(mission.expected)
    wrong[5] = reject("engine_busy")  # actually overlaps_scheduled_burn
    assert any(
        "declared rejected/engine_busy" in v
        for v in m2.check_traceability(scenario, run.events, wrong, run)
    )


def test_tampered_commanded_intent_is_detected(runs):
    mission, scenario, run = _slice(runs)
    events = _replace(run.events, lambda e: e.type == "CommandAccepted", commanded_duration_s=77.4)
    assert m2.check_traceability(scenario, events, mission.expected, run)


def test_burn_ids_must_be_sequential(runs):
    mission, scenario, run = runs["m2_invalid_commands"]
    events = _replace(
        run.events,
        lambda e: getattr(e, "burn_id", None) == "burn#000002",
        burn_id="burn#000005",
    )
    assert any(
        "sequential" in v for v in m2.check_traceability(scenario, events, mission.expected, run)
    )


def test_tampered_propellant_breaks_accounting_and_o1(runs):
    mission, scenario, run = _slice(runs)
    events = _replace(
        run.events, lambda e: e.type == "BurnEnded", propellant_used_kg=12.3794 + 1e-6
    )
    assert any("propellant_used_kg" in v for v in m2.accounting_metrics(scenario, events)[1])
    predicted = m2.predict_burns(scenario, mission.expected)
    o1, _, _ = m2.mass_and_rocket_metrics(scenario, events, predicted)
    assert (
        o1["propellant_used_rel_error_max"]
        > LIMITS["o1_mass_law"]["all"]["propellant_used_rel_error_max"]
    )


def test_tampered_sensed_delta_v_fails_o2(runs):
    mission, scenario, run = _slice(runs)
    end = next(e for e in run.events if e.type == "BurnEnded")
    events = _replace(
        run.events,
        lambda e: e.type == "BurnEnded",
        sensed_delta_v_mps=end.sensed_delta_v_mps * (1 + 1e-10),
    )
    _, o2, _ = m2.mass_and_rocket_metrics(
        scenario, events, m2.predict_burns(scenario, mission.expected)
    )
    assert (
        o2["sensed_delta_v_excess_over_simpson_rel_max"]
        > LIMITS["o2_rocket_equation"]["all"]["sensed_delta_v_excess_over_simpson_rel_max"]
    )


def test_thrust_while_idle_is_detected(runs):
    _, scenario, run = _slice(runs)
    events = _replace(
        run.events,
        lambda e: e.type == "PropulsionSampled" and e.tick == 0,
        thrust_acceleration_mps2=(1e-9, 0.0, 0.0),
    )
    assert any("while not burning" in v for v in m2.accounting_metrics(scenario, events)[1])


def test_propellant_change_while_idle_is_detected(runs):
    _, scenario, run = _slice(runs)
    events = _replace(
        run.events,
        lambda e: e.type == "PropulsionSampled" and e.tick == 300,
        propellant_kg=287.0,
        total_mass_kg=1287.0,
    )
    assert any("while idle" in v for v in m2.accounting_metrics(scenario, events)[1])


def test_missing_receipt_is_detected_independently_of_the_runner(runs):
    """The submitted count comes from the timeline, not the runner's own list."""
    mission, scenario, run = runs["m2_invalid_commands"]
    i = next(i for i, e in enumerate(run.events) if e.type == "CommandRejected")
    events = run.events[:i] + run.events[i + 1 :]
    assert any(
        "receipts" in v for v in m2.check_traceability(scenario, events, mission.expected, run)
    )
    tampered = dataclasses.replace(run, unsubmitted_command_ids=["inv-past-001"])
    assert any(
        "unsubmitted" in v
        for v in m2.check_traceability(scenario, run.events, mission.expected, tampered)
    )


def test_run_ending_before_the_scenario_stop_is_detected(runs):
    mission, scenario, run = _slice(runs)
    k = next(i for i, e in enumerate(run.events) if e.type == "StateSampled" and e.tick == 600)
    done = run.events[-1].model_copy(update={"tick": 600, "t": 6000.0})
    events = [*run.events[: k + 2], done]
    predicted = m2.predict_burns(scenario, mission.expected)
    assert any("scenario stop" in v for v in m2.check_outcomes(scenario, events, predicted))


# ------------------------------------------------------------------ DR-0018 boundary


@pytest.mark.parametrize("case", m2.BOUNDARY_CASES, ids=lambda c: c.name)
def test_dr0018_boundary_cases_hold(case):
    base = BY_NAME["m2_prograde_burn"].build()
    variant = m2.boundary_variant(base, case)
    longer = m2.boundary_variant(base, case, stop_s=base.stop.duration_s)
    run = run_scenario(variant)
    assert m2.boundary_violations(variant, run, run_scenario(longer), (ACCEPT,)) == []


def test_fabricated_burn_end_at_the_stop_is_detected():
    """DR-0018 A: a stop inside a burn must not produce BurnEnded."""
    base = BY_NAME["m2_prograde_burn"].build()
    case = m2.BOUNDARY_CASES[0]
    variant = m2.boundary_variant(base, case)
    longer = run_scenario(m2.boundary_variant(base, case, stop_s=base.stop.duration_s))
    run = run_scenario(variant)
    real_end = next(e for e in longer.events if e.type == "BurnEnded")
    fake = real_end.model_copy(update={"tick": 66, "t": 660.0, "event_t_s": 660.0})
    i = next(i for i, e in enumerate(run.events) if e.tick == 66)
    run.events.insert(i, fake)
    assert m2.boundary_violations(variant, run, longer, (ACCEPT,))


def test_physics_change_before_the_stop_is_detected():
    """The stop is an observation boundary only: physics up to it equals a longer run."""
    base = BY_NAME["m2_prograde_burn"].build()
    case = m2.BOUNDARY_CASES[0]
    variant = m2.boundary_variant(base, case)
    run = run_scenario(variant)
    other = run_scenario(m2.boundary_variant(BY_NAME["m2_retrograde_burn"].build(), case, 53700.0))
    assert any("differ" in v for v in m2.boundary_violations(variant, run, other, (ACCEPT,)))


# ------------------------------------------------------------------ prediction


def test_prediction_uses_only_scenario_inputs():
    scenario = BY_NAME["m2_burn_to_depletion"].build()
    (burn,) = m2.predict_burns(scenario, BY_NAME["m2_burn_to_depletion"].expected)
    mdot = 490.0 / (312.0 * 9.80665)
    assert burn.end_cause == "propellant_depleted"
    assert burn.burn_time_s == 20.0 / mdot
    # D1a: the represented cutoff is not after depletion; the residual stays in the tank.
    assert burn.cutoff_t_s - burn.ignition_t_s <= burn.burn_time_s
    assert 0.0 < burn.propellant_after_kg <= mdot * 2 * math.ulp(burn.cutoff_t_s)
    assert burn.propellant_used_kg + burn.propellant_after_kg == pytest.approx(
        20.0, rel=1e-15, abs=0
    )
    assert burn.delta_v_mps == pytest.approx(
        312.0 * 9.80665 * math.log(1020.0 / 1000.0), rel=1e-14, abs=0
    )


def test_inconsistent_declarations_are_refused():
    scenario = BY_NAME["m2_invalid_commands"].build()
    with pytest.raises(ValueError, match="one expectation"):
        m2.predict_burns(scenario, (ACCEPT,))
    declared = [ACCEPT] * len(scenario.commands)  # would accept overlapping burns
    with pytest.raises(ValueError):
        m2.predict_burns(scenario, declared)


# ------------------------------------------------------------------ physics mutants


def _physics(name):
    mission = BY_NAME[name]
    scenario = mission.build()
    run = run_scenario(scenario)
    predicted = m2.predict_burns(scenario, mission.expected)
    o1, o2, _ = m2.mass_and_rocket_metrics(scenario, run.events, predicted)
    o4, _ = m2.reference_metrics(scenario, run.events, predicted)
    return run, scenario, mission, o1, o2, o4, m2.direction_metrics(scenario, run.events)


def _o4_fails(o4):
    limits = LIMITS["o4_reference"]["all"]
    return any(o4[k] > limits[k] for k in limits)


def test_thrust_magnitude_mutant_fails_o4(monkeypatch):
    """Sensed delta-v integrates F/m separately, so only the trajectory oracle (O4)
    can see a wrong thrust vector; this pins that it does."""
    original = simulator_module.thrust_acceleration
    monkeypatch.setattr(
        simulator_module, "thrust_acceleration", lambda *a: original(*a) * (1 + 1e-5)
    )
    *_, o2, o4, _ = _physics("m2_prograde_burn")
    assert o2["sensed_delta_v_rel_error_max"] < 1e-12  # O2 is blind to it
    assert _o4_fails(o4)


def test_frozen_pointing_mutant_fails_o4(monkeypatch):
    held = {}

    def frozen(self, t, r, v):
        held.setdefault("u", np.array(v) / np.linalg.norm(v))
        return held["u"]

    monkeypatch.setattr(Prograde, "direction", frozen)
    *_, o4, _ = _physics("m2_prograde_burn")
    assert _o4_fails(o4)


def test_swapped_direction_mutant_fails_o7(monkeypatch):
    laws = dict(simulator_module.DIRECTION_LAWS)
    laws["retrograde"] = laws["prograde"]
    monkeypatch.setattr(simulator_module, "DIRECTION_LAWS", laws)
    *_, o4, o7 = _physics("m2_retrograde_burn")
    assert o7["sign_violations"] == 1.0
    assert _o4_fails(o4)


def test_wrong_g0_mutant_fails_o1_and_configuration(monkeypatch):
    monkeypatch.setattr(propulsion_module, "STANDARD_GRAVITY", 9.81)
    run, scenario, *_rest = _physics("m2_prograde_burn")
    o1 = _rest[1]
    assert o1["propellant_used_rel_error_max"] > 1e-12
    assert m2.check_spacecraft_configured(scenario, run.events)


def test_cutoff_timing_mutant_fails_traceability_and_o1(monkeypatch):
    original = simulator_module.plan_burn

    def late(engine, propellant, ignition, duration, *a, **k):
        return original(engine, propellant, ignition, duration * (1 + 1e-9), *a, **k)

    monkeypatch.setattr(simulator_module, "plan_burn", late)
    run, scenario, mission, o1, *_ = _physics("m2_prograde_burn")
    assert any(
        "ignition + commanded" in v
        for v in m2.check_traceability(scenario, run.events, mission.expected, run)
    )
    assert o1["propellant_used_rel_error_max"] > 1e-12


def test_free_space_oracle_detects_an_extra_force(monkeypatch):
    veh = m2.vehicle(BY_NAME["m2_prograde_burn"].build())
    clean = m2.free_space_metrics(veh, 77.3)
    assert clean["velocity_rel_error_max"] <= 1e-12
    assert clean["position_order_deviation_from_4_max"] <= 0.5
    monkeypatch.setattr(m2.FreeSpace, "acceleration", lambda self, t, r, v: np.full(3, 1e-9))
    assert m2.free_space_metrics(veh, 77.3)["velocity_rel_error_max"] > 1e-12


# ------------------------------------------------------------------ O6 / O8 (slow)


@pytest.mark.slow
def test_impulsive_limit_is_second_order_in_burn_duration():
    rows = m2.impulsive_family(BY_NAME["m2_prograde_burn"].build())
    metrics = m2.impulsive_metrics(rows)
    limits = LIMITS["o6_impulsive_limit"]["all"]
    assert all(metrics[k] <= v for k, v in limits.items())
    # Physical sign: a finite burn is less efficient than the impulsive ideal.
    assert all(r["sma_finite_minus_impulsive_m"] < 0 for r in rows)


@pytest.mark.slow
def test_rk4_converges_at_fourth_order_through_the_burn():
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    run = run_scenario(scenario)
    predicted = m2.predict_burns(scenario, mission.expected)
    _, ref = m2.reference_metrics(scenario, run.events, predicted)
    finals = {10.0: run.final.r}
    for dt in m2.O8_DTS[1:]:
        finals[dt] = run_scenario(m2.convergence_variant(scenario, dt)).final.r
    metrics = m2.convergence_metrics(finals, ref[run.final.t])
    assert (
        metrics["order_deviation_from_4_max"]
        <= LIMITS["o8_convergence"]["all"]["order_deviation_from_4_max"]
    )


# ------------------------------------------------------------------ thresholds


def test_m2_thresholds_are_provisional_and_scoped():
    names = frozenset(m.name for m in MISSIONS)
    thresholds = load_scoped_thresholds(missions=names)
    assert thresholds.status == "provisional"
    data = json.loads(M2_THRESHOLDS.read_text())
    assert data["approved_by"] is None and "NOT APPROVED" in data["basis"]
    merged = thresholds.for_validator("o4_reference", "m2_invalid_commands")
    assert merged["cutoff_position_error_max_m"] == 0.016
    assert merged["final_position_error_m"] == 0.6  # from "all"
    assert (
        thresholds.for_validator("o4_reference", "m2_prograde_burn")["cutoff_position_error_max_m"]
        == 0.002
    )


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda d: d["limits"].update({"o10_unknown": {"all": {}}}), "match no validator"),
        (lambda d: d["limits"]["o4_reference"].update({"m2_typo": {}}), "match no mission"),
        (lambda d: d.update({"status": "final"}), "invalid threshold status"),
    ],
)
def test_m2_threshold_loader_rejects_unknown_entries(tmp_path, edit, message):
    data = json.loads(M2_THRESHOLDS.read_text())
    edit(data)
    path = tmp_path / "m2.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=message):
        load_scoped_thresholds(path, missions=frozenset(m.name for m in MISSIONS))


def test_unconsumed_threshold_entries_are_reported():
    thresholds = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
    thresholds.for_validator("o1_mass_law")
    assert "o4_reference/m2_invalid_commands" in thresholds.unused()
    assert "o1_mass_law/all" not in thresholds.unused()


# ------------------------------------------------------------------ CLI


@pytest.mark.slow
def test_m2_proof_cli_quick_passes(tmp_path):
    import importlib.util

    from tars.validation.thresholds import REPO_ROOT

    spec = importlib.util.spec_from_file_location(
        "m2_proof", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = tmp_path / "m2.json"
    assert module.main(["--quick", "--out", str(out)]) == 0
    report = json.loads(out.read_text())
    assert report["passed"] and report["threshold_status"] == "provisional" and report["quick"]
    assert {r["validator"].split("[")[0] for r in report["results"]} >= {
        "event_order", "traceability", "outcomes", "accounting", "determinism",
        "rejections_change_nothing", "o1_mass_law", "o2_rocket_equation", "o3_free_space",
        "o4_reference", "o5_coast_kepler", "o7_direction", "dr0018_boundary",
        "same_tick_submission_reporting",
    }  # fmt: skip


def test_expected_helpers():
    assert Expected("accepted") == ACCEPT
    assert reject("x") == Expected("rejected", "x")
    assert dataclasses.is_dataclass(m2.PredictedBurn)


# ------------------------------------------------------------------ review M2-T5 mutants


def _o4(scenario, events, mission):
    return m2.reference_metrics(scenario, events, m2.predict_burns(scenario, mission.expected))[0]


def _fails(group, metrics, mission="all"):
    limits = {**LIMITS[group]["all"], **LIMITS[group].get(mission, {})}
    return [k for k, v in limits.items() if not metrics[k] <= v]


def test_wrong_initial_orbit_fails_o4(monkeypatch):
    """F1: the reference is seeded from the scenario, not from SimulationStarted."""
    from tars.sim import runner

    original = runner.initial_state

    def rotated(scenario):
        r, v = original(scenario)
        rot = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        return rot @ r, rot @ v

    monkeypatch.setattr(runner, "initial_state", rotated)
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    run = run_scenario(scenario)
    failed = _fails("o4_reference", _o4(scenario, run.events, mission))
    assert "initial_position_rel_error" in failed and "final_position_error_m" in failed


def test_expected_initial_state_matches_the_production_state_to_round_off():
    from tars.sim.runner import initial_state

    scenario = BY_NAME["m2_prograde_burn"].build()
    (r, v), (r0, v0) = m2.expected_initial_state(scenario), initial_state(scenario)
    assert np.linalg.norm(r - r0) <= 1e-15 * np.linalg.norm(r)
    assert np.linalg.norm(v - v0) <= 1e-15 * np.linalg.norm(v)


def test_premature_success_fails_outcomes_and_o4():
    """F2: a run that stops early is judged at the scenario's requested horizon."""
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    raw = scenario.model_dump(mode="json")
    raw["stop"] = {"duration_s": 3000.0}
    short = run_scenario(ScenarioV2.model_validate(raw))
    predicted = m2.predict_burns(scenario, mission.expected)
    assert any("scenario stop" in v for v in m2.check_outcomes(scenario, short.events, predicted))
    assert "final_position_error_m" in _fails("o4_reference", _o4(scenario, short.events, mission))


def test_corrupted_powered_sample_fails_o4(runs):
    """F3: every StateSampled, including those during a burn, is checked."""
    mission, scenario, run = _slice(runs)
    events = [
        e.model_copy(update={"r": [2 * x for x in e.r]})
        if e.type == "StateSampled" and e.t == 660.0
        else e
        for e in run.events
    ]
    assert "sample_position_error_max_m" in _fails("o4_reference", _o4(scenario, events, mission))


def test_inconsistent_final_state_is_detected(runs):
    """F3: SimulationCompleted, the final samples and RunResult must agree."""
    _, _, run = _slice(runs)
    done = run.events[-1].model_copy(update={"r": [1e9, 0.0, 0.0], "v": [1e6, 0.0, 0.0]})
    events = [*run.events[:-1], done]
    assert m2.check_final_consistency(run.events, run) == []
    assert m2.check_final_consistency(events, run)
    stale = dataclasses.replace(
        run, final_propulsion=runs["m2_burn_to_depletion"][2].final_propulsion
    )
    assert any("final_propulsion" in v for v in m2.check_final_consistency(run.events, stale))


def test_bogus_completion_at_an_active_stop_is_detected():
    """F3: the DR-0018 boundary check reconciles the completion state with the samples."""
    base = BY_NAME["m2_prograde_burn"].build()
    case = m2.BOUNDARY_CASES[0]
    variant = m2.boundary_variant(base, case)
    longer = run_scenario(m2.boundary_variant(base, case, stop_s=base.stop.duration_s))
    run = run_scenario(variant)
    run.events[-1] = run.events[-1].model_copy(update={"r": [1e9, 0.0, 0.0]})
    assert m2.boundary_violations(variant, run, longer, (ACCEPT,))


@pytest.mark.parametrize("change", ["delete", "mismatch"])
def test_missing_or_mismatched_depletion_event_is_detected(runs, change):
    """F4: every depleted BurnEnded needs its PropellantDepleted immediately before."""
    _, scenario, run = runs["m2_burn_to_depletion"]
    if change == "delete":
        events = [e for e in run.events if e.type != "PropellantDepleted"]
    else:
        events = _replace(run.events, lambda e: e.type == "PropellantDepleted", event_t_s=724.0)
    assert any("PropellantDepleted" in v for v in m2.check_event_order(scenario, events))


# ------------------------------------------------------------------ re-verification mutants


def _audit(name, mutate=None, scenario=None):
    mission = BY_NAME[name]
    scenario = scenario or mission.build()
    run = run_scenario(scenario)
    if mutate is not None:
        mutate(run)
    return m2.audit_run(scenario, mission.expected, run), run


def _gate_failures(audit, mission):
    failed = []
    for group, metrics in audit.metrics.items():
        limits = {**LIMITS[group]["all"], **LIMITS[group].get(mission, {})}
        failed += [
            f"{group}.{k}" for k, lim in limits.items() if k in metrics and not metrics[k] <= lim
        ]
    return failed


def _violations(audit):
    return [x for v in audit.violations.values() for x in v]


def _edit(run, predicate, **update):
    run.events[:] = [e.model_copy(update=update) if predicate(e) else e for e in run.events]


def test_clean_audits_have_no_violations_or_gate_failures(runs):
    for name, (mission, scenario, run) in runs.items():
        audit = m2.audit_run(scenario, mission.expected, run)
        assert _violations(audit) == [], name
        assert _gate_failures(audit, name) == [], name


def test_o3_detects_a_wrong_burn_duration(monkeypatch):
    """F5: the closed form uses the requested interval, not the reported cutoff."""
    veh = m2.vehicle(BY_NAME["m2_prograde_burn"].build())
    original = simulator_module.Simulator.schedule_burn

    def doubled(self, direction, ignition_t_s, duration_s, *a, **k):
        return original(self, direction, ignition_t_s, 2 * duration_s, *a, **k)

    monkeypatch.setattr(simulator_module.Simulator, "schedule_burn", doubled)
    assert m2.free_space_metrics(veh, 77.3)["timing_violations"] > 0


def test_auxiliary_runs_are_audited():
    """F6: an O8 variant keeps the mission's telemetry grid, so every sample has a
    reference state; a corrupted sample in it fails like in the mission."""
    mission = BY_NAME["m2_prograde_burn"]
    variant = m2.convergence_variant(mission.build(), 5.0)
    assert variant.telemetry.sample_interval_s == 60.0
    audit, _ = _audit(
        "m2_prograde_burn",
        lambda run: _edit(
            run, lambda e: e.type == "StateSampled" and e.t == 660.0, r=[1.0, 2.0, 3.0]
        ),
        scenario=variant,
    )
    assert "o4_reference.sample_position_error_max_m" in _gate_failures(audit, "m2_prograde_burn")


@pytest.mark.parametrize(
    "name", ["m2_invalid_commands_empty_tank", "m2_invalid_commands_no_propulsion"]
)
def test_missions_without_burns_have_a_trajectory_gate(name):
    """F7: doubling every reported state of a coast-only mission fails O4."""

    def double(run):
        _edit(run, lambda e: e.type in ("StateSampled", "SimulationCompleted"), r=[0.0, 0.0, 1.0])

    audit, _ = _audit(name, double)
    assert any(f.startswith("o4_reference.") for f in _gate_failures(audit, name))


@pytest.mark.parametrize(
    "field",
    [
        "receipts",
        "samples",
        "crossing_times",
        "initial",
        "status",
        "final_t",
        "final_propulsion_t",
        "plans",
    ],
)
def test_returned_result_is_reconciled_with_events(runs, field):
    """F8: every RunResult field agrees with the event log."""
    _, scenario, run = runs["m2_invalid_commands"]
    bad = {
        "receipts": lambda r: dataclasses.replace(r, receipts=r.receipts[:-1]),
        "samples": lambda r: dataclasses.replace(r, samples=r.samples[:-1]),
        "crossing_times": lambda r: dataclasses.replace(r, crossing_times=[-999.0]),
        "initial": lambda r: dataclasses.replace(r, initial=r.final),
        "status": lambda r: dataclasses.replace(r, status="failure", failure_cause="impact"),
        "final_t": lambda r: dataclasses.replace(r, final=dataclasses.replace(r.final, t=1.0)),
        "final_propulsion_t": lambda r: dataclasses.replace(
            r, final_propulsion=dataclasses.replace(r.final_propulsion, t=1.0)
        ),
        "plans": lambda r: dataclasses.replace(
            r, receipts=[dataclasses.replace(x, plan=None) for x in r.receipts]
        ),
    }[field](run)
    assert m2.check_result_consistency(scenario, run.events, run) == []
    assert m2.check_result_consistency(scenario, run.events, bad)


def test_cli_summary_is_reconciled_with_events(runs):
    """F8: a CLI summary without the commands fails."""
    _, _, run = _slice(runs)
    good = {
        "commands": [
            {"command_id": "slice-prograde-001", "status": "accepted", "reason": None,
             "burn_id": "burn#000001", "submit_tick": 0}
        ],
        "final_propellant_kg": run.final_propulsion.propellant_kg,
        "final_total_mass_kg": run.final_propulsion.total_mass_kg,
        "final_engine_state": "idle",
        "active_burn_id_at_stop": None,
        "pending_burn_ids_at_stop": [],
    }  # fmt: skip
    assert m2.cli_summary_violations(run.events, good) == []
    assert m2.cli_summary_violations(run.events, {**good, "commands": []})


@pytest.mark.parametrize(
    ("tick", "update"),
    [
        (12, {"pending_burn_ids": ("burn#000009",)}),
        (64, {"delta_v_sensed_mps": 999.0}),
        (64, {"propellant_kg": 290.0, "total_mass_kg": 1290.0}),
        (
            64,
            {
                "engine_state": "idle",
                "active_burn_id": None,
                "thrust_acceleration_mps2": (0.0, 0.0, 0.0),
            },
        ),
    ],
)
def test_intermediate_propulsion_samples_are_predicted(tick, update):
    """F9: schedule, propellant and sensed delta-v are predicted at every sample."""
    audit, _ = _audit(
        "m2_prograde_burn",
        lambda run: _edit(
            run, lambda e: e.type == "PropulsionSampled" and e.tick == tick, **update
        ),
    )
    assert _violations(audit) or _gate_failures(audit, "m2_prograde_burn")


def test_reversed_thrust_between_state_samples_is_detected():
    """F10: direction is checked at every burning sample against the reference."""

    def reverse(run):
        _edit(
            run,
            lambda e: e.type == "PropulsionSampled" and e.tick == 61,
            thrust_acceleration_mps2=tuple(-x for x in next(
                p for p in run.events if p.type == "PropulsionSampled" and p.tick == 61
            ).thrust_acceleration_mps2),
        )  # fmt: skip

    audit, _ = _audit("m2_prograde_burn", reverse)
    assert "o4_reference.thrust_direction_vs_reference_max" in _gate_failures(
        audit, "m2_prograde_burn"
    )


@pytest.mark.parametrize(
    ("event", "update"),
    [
        ("BurnStarted", {"r": None}),
        ("BurnStarted", {"thrust_unit_vector": (0.0, 0.0, 0.0)}),
        ("BurnStarted", {"total_mass_kg": 999.0}),
        ("BurnEnded", {"total_mass_kg": 999.0}),
        ("PropellantDepleted", {"residual_propellant_kg": 999.0}),
    ],
)
def test_transition_payloads_are_checked(event, update):
    """F11: ignition state, thrust vector, transition masses and residuals."""

    def mutate(run):
        e = next(x for x in run.events if x.type == event)
        upd = dict(update)
        if upd.get("r", 1) is None:
            upd["r"] = tuple(1.000001 * x for x in e.r)
        _edit(run, lambda x: x is e, **upd)

    audit, _ = _audit("m2_burn_to_depletion", mutate)
    assert _violations(audit) or _gate_failures(audit, "m2_burn_to_depletion")


@pytest.mark.parametrize(
    ("event", "update"),
    [
        ("CommandAccepted", {"planned_burn_duration_s": 999.0}),
        ("CommandAccepted", {"planned_propellant_used_kg": 999.0}),
        ("CommandAccepted", {"timing_delta_v_error_mps": 999.0}),
        ("BurnStarted", {"planned_end_cause": "completed"}),
        ("SpacecraftConfigured", {"timing_delta_v_budget_mps": 1.0}),
    ],
)
def test_plans_and_timing_claims_are_checked(event, update):
    """F12: complete plans, the DR-0017 timing bound and the configured budget."""
    audit, _ = _audit(
        "m2_burn_to_depletion", lambda run: _edit(run, lambda e: e.type == event, **update)
    )
    assert _violations(audit) or _gate_failures(audit, "m2_burn_to_depletion")


def test_depletion_cutoff_shift_is_detected():
    """F12: the D1a cutoff is predicted exactly; a 10 us shift of every copy fails."""

    def shift(run):
        t = next(e for e in run.events if e.type == "BurnEnded").event_t_s
        _edit(run, lambda e: getattr(e, "event_t_s", None) == t, event_t_s=t + 1e-5)
        _edit(
            run, lambda e: getattr(e, "planned_cutoff_t_s", None) == t, planned_cutoff_t_s=t + 1e-5
        )

    audit, _ = _audit("m2_burn_to_depletion", shift)
    assert any("D1a" in v or "predicted" in v for v in _violations(audit))


@pytest.mark.parametrize(
    "update",
    [{"scenario_name": "x"}, {"seed": 7}, {"integrator": "euler"}, {"software_version": "9"}],
)
def test_start_provenance_is_checked(update):
    """F13: SimulationStarted identity against the scenario."""
    audit, _ = _audit(
        "m2_prograde_burn",
        lambda run: _edit(run, lambda e: e.type == "SimulationStarted", **update),
    )
    assert _violations(audit)


@pytest.mark.parametrize(
    "update",
    [{"issuer": "someone"}, {"schema_errors": ()}, {"commanded_duration_s": 10.0}],
)
def test_rejection_provenance_is_checked(update):
    """F13: issuer, diagnostics and the schema-invalid intent contract."""
    audit, _ = _audit(
        "m2_invalid_commands",
        lambda run: _edit(
            run, lambda e: e.type == "CommandRejected" and e.reason == "schema_invalid", **update
        ),
    )
    assert _violations(audit)


@pytest.mark.parametrize("change", ["delete", "crossing", "number", "count", "altitude", "extrema"])
def test_orbit_and_altitude_reporting_is_checked(change):
    """F14: orbit events vs independent node crossings; altitude vs position."""

    def mutate(run):
        if change == "delete":
            run.events[:] = [e for e in run.events if e.type != "OrbitCompleted"]
        elif change == "crossing":
            _edit(
                run,
                lambda e: e.type == "OrbitCompleted" and e.orbit_number == 3,
                crossing_t=e_shift(run),
            )
        elif change == "number":
            _edit(
                run, lambda e: e.type == "OrbitCompleted" and e.orbit_number == 3, orbit_number=999
            )
        elif change == "count":
            _edit(run, lambda e: e.type == "SimulationCompleted", orbits_completed=999)
        elif change == "altitude":
            _edit(run, lambda e: e.type == "StateSampled" and e.tick == 600, altitude_m=1.0)
        else:
            _edit(run, lambda e: e.type == "SimulationCompleted", min_altitude_m=1000.0)

    def e_shift(run):
        o = next(e for e in run.events if e.type == "OrbitCompleted" and e.orbit_number == 3)
        return o.crossing_t - 1e-3

    audit, _ = _audit("m2_prograde_burn", mutate)
    assert _violations(audit) or _gate_failures(audit, "m2_prograde_burn")


def test_missing_threshold_group_is_reported():
    """F15: a metric without a threshold is reported as ungated, not passed."""
    import importlib.util

    from tars.validation.thresholds import REPO_ROOT, ScopedThresholds

    spec = importlib.util.spec_from_file_location(
        "m2_proof", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads(M2_THRESHOLDS.read_text())
    del data["limits"]["o4_reference"]
    gates = module.Gates(ScopedThresholds(status="provisional", limits=data["limits"]))
    gates.check("o4_reference", "o4", "m2_prograde_burn", {"final_position_error_m": 0.3})
    assert gates.missing == ["o4: final_position_error_m"]


def test_simpson_bound_explains_high_thrust_sensed_delta_v_error():
    """VAL-0013: the O6 16x-thrust variant's sensed delta-v error is RK4 (Simpson)
    truncation, predicted by the analytic bound to a few percent."""
    base = BY_NAME["m2_prograde_burn"].build()
    variant = m2.impulsive_variants(base)[-1]
    run = run_scenario(variant)
    (b,) = m2.predict_burns(variant, (ACCEPT,))
    end = next(e for e in run.events if e.type == "BurnEnded")
    err = end.sensed_delta_v_mps - b.delta_v_mps
    bound = m2.simpson_bound(m2.vehicle(variant), b, variant.dt_s)
    assert 0.9 * bound <= abs(err) <= bound
    assert abs(err) / b.delta_v_mps > 1e-12  # why the raw relative error is not the gate


@pytest.mark.slow
def test_m2_proof_audits_auxiliary_and_boundary_runs():
    """F6: the Proof audits O8 auxiliary runs and DR-0018 variants, not only missions."""
    import importlib.util

    from tars.validation.thresholds import REPO_ROOT

    spec = importlib.util.spec_from_file_location(
        "m2_proof", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)))
    checks, _ = module.mission_checks(BY_NAME["m2_burn_to_depletion"], gates, quick=False)
    names = {c.validator for c in checks}
    assert {
        "o4_reference[m2_burn_to_depletion/o8_aux]",
        "identities[m2_burn_to_depletion/o8_aux]",
    } <= names
    assert all(c.passed for c in checks) and gates.missing == []
    boundary, _ = module.boundary_checks(gates)
    assert any(c.validator.startswith("o4_reference[dr0018/") for c in boundary)
    assert all(c.passed for c in boundary)


# ------------------------------------------------------------------ re-verification 2 mutants


@pytest.mark.parametrize(
    "change",
    ["command", "schema_errors", "detail", "rejected_plan", "plan_ignition", "plan_mass_flow",
     "plan_timing", "final_plan_policy", "scenario"],
)  # fmt: skip
def test_returned_receipts_and_plans_are_fully_reconciled(runs, change):
    """F16: complete receipts, every plan field, final-snapshot plans, scenario."""
    _, scenario, run = runs["m2_invalid_commands"]
    rec = run.receipts
    acc = next(i for i, r in enumerate(rec) if r.plan is not None)
    rej = next(i for i, r in enumerate(rec) if r.plan is None)

    def at(i, **kw):
        return [dataclasses.replace(r, **kw) if j == i else r for j, r in enumerate(rec)]

    def plan(**kw):
        return at(acc, plan=dataclasses.replace(rec[acc].plan, **kw))

    bad = {
        "command": lambda: dataclasses.replace(run, receipts=at(acc, command=None)),
        "schema_errors": lambda: dataclasses.replace(
            run, receipts=at(rej, schema_errors=("x: y",))
        ),
        "detail": lambda: dataclasses.replace(run, receipts=at(rej, detail="fabricated")),
        "rejected_plan": lambda: dataclasses.replace(run, receipts=at(rej, plan=rec[acc].plan)),
        "plan_ignition": lambda: dataclasses.replace(run, receipts=plan(ignition_t_s=999.0)),
        "plan_mass_flow": lambda: dataclasses.replace(run, receipts=plan(mass_flow_kgps=999.0)),
        "plan_timing": lambda: dataclasses.replace(
            run, receipts=plan(timing_delta_v_error_mps=999.0)
        ),
        "final_plan_policy": None,
        "scenario": lambda: dataclasses.replace(run, scenario=BY_NAME["m2_prograde_burn"].build()),
    }
    if change == "final_plan_policy":
        base = BY_NAME["m2_prograde_burn"].build()
        variant = m2.boundary_variant(base, m2.BOUNDARY_CASES[0])
        brun = run_scenario(variant)
        fp = brun.final_propulsion
        tampered = dataclasses.replace(
            brun,
            final_propulsion=dataclasses.replace(
                fp, active_plan=dataclasses.replace(fp.active_plan, policy="burn_to_depletion")
            ),
        )
        assert m2.check_result_consistency(variant, brun.events, brun) == []
        assert m2.check_result_consistency(variant, brun.events, tampered)
        return
    assert m2.check_result_consistency(scenario, run.events, run) == []
    assert m2.check_result_consistency(scenario, run.events, bad[change]())


def test_sample_only_altitude_extrema_are_detected():
    """F17: extrema must cover every executed tick, not only the telemetry samples."""

    def sample_extrema(run):
        alts = [e.altitude_m for e in run.events if e.type == "StateSampled"]
        _edit(
            run,
            lambda e: e.type == "SimulationCompleted",
            min_altitude_m=min(alts),
            max_altitude_m=max(alts),
        )

    audit, _ = _audit("m2_burn_to_depletion", sample_extrema)
    assert any(f.startswith("orbit_events.") for f in _gate_failures(audit, "m2_burn_to_depletion"))


def test_event_schema_version_is_enforced(runs):
    """F18: every event must carry the integer schema version 1 and re-validate."""
    _, scenario, run = _slice(runs)
    events = [e.model_copy(update={"schema_version": 999}) for e in run.events]
    assert any("schema_version" in v for v in m2.check_event_order(scenario, events))
