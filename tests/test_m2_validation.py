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
        o2["sensed_delta_v_rel_error_max"]
        > LIMITS["o2_rocket_equation"]["all"]["sensed_delta_v_rel_error_max"]
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
    assert burn.propellant_used_kg == 20.0
    assert burn.delta_v_mps == pytest.approx(312.0 * 9.80665 * math.log(1020.0 / 1000.0), rel=1e-15)


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
    metrics = m2.convergence_metrics(scenario, ref[run.final.t])
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
        (lambda d: d["limits"].update({"o9_gmat": {"all": {}}}), "match no validator"),
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
        e.model_copy(update={"r": tuple(2 * x for x in e.r)})
        if e.type == "StateSampled" and e.t == 660.0
        else e
        for e in run.events
    ]
    assert "sample_position_error_max_m" in _fails("o4_reference", _o4(scenario, events, mission))


def test_inconsistent_final_state_is_detected(runs):
    """F3: SimulationCompleted, the final samples and RunResult must agree."""
    _, _, run = _slice(runs)
    done = run.events[-1].model_copy(update={"r": (1e9, 0.0, 0.0), "v": (1e6, 0.0, 0.0)})
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
    run.events[-1] = run.events[-1].model_copy(update={"r": (1e9, 0.0, 0.0)})
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
