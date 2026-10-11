"""Runner timeline, M2 event emission and duration stop (M2 task T4).

Mission-level checks on version-2 scenarios: the slice burn (P1), command correlation,
commanded vs executed values, emission order, stop boundaries, rejected commands,
depletion, failures and determinism. The M1 path is covered by test_mission_m1.py and
the golden-hash validators.
"""

import json
from collections import Counter

import numpy as np
import pytest

from tars.events import read_jsonl, to_jsonl
from tars.sim import runner
from tars.sim.propulsion import EngineState
from tars.sim.scenario import load_scenario, parse_scenario
from tests.conftest import M1_SCENARIO, M2_SLICE_SCENARIO

M1_GOLDEN_SHA256 = "7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4"
BURN_EVENTS = {"BurnStarted", "BurnEnded", "PropellantDepleted"}


def _slice() -> dict:
    return json.loads(M2_SLICE_SCENARIO.read_text())


def _cmd(command_id="c1", ignition=600.0, duration=77.3, **extra) -> dict:
    return {
        "schema_version": 1,
        "type": "BurnCommand",
        "command_id": command_id,
        "issuer": "scenario_timeline",
        "ignition_t_s": ignition,
        "direction": "prograde",
        "duration_s": duration,
        **extra,
    }


def _scenario(commands=None, stop_s=1000.0, spacecraft="default", **overrides):
    data = _slice()
    if commands is not None:
        data["commands"] = [
            c if "command" in c else {"submit_t_s": 0.0, "command": c} for c in commands
        ]
    data["stop"] = {"duration_s": stop_s} if isinstance(stop_s, float) else stop_s
    if spacecraft is None:
        del data["spacecraft"]
    elif spacecraft != "default":
        data["spacecraft"] = spacecraft
    data.update(overrides)
    return parse_scenario(json.dumps(data))


def _run(scenario):
    return runner.run_scenario(scenario, record_samples=False)


def _of(result, kind):
    return [e for e in result.events if e.type == kind]


def _check_log_invariants(result):
    """Properties every M2 log must have, whatever the scenario."""
    events, dt = result.events, result.scenario.dt_s
    assert events[0].type == "SimulationStarted" and events[-1].type == "SimulationCompleted"
    ticks = [e.tick for e in events]
    assert ticks == sorted(ticks), "envelope ticks never go backwards"
    for e in events:
        assert e.t == e.tick * dt  # envelope time is the tick time
        if e.type in BURN_EVENTS:
            # The envelope is the end of the step that executed the transition.
            assert e.t - dt <= e.event_t_s <= e.t
    for kind in ("StateSampled", "PropulsionSampled"):
        counts = Counter(e.tick for e in _of(result, kind))
        assert not counts or max(counts.values()) == 1, f"duplicate {kind}"
    assert read_jsonl(to_jsonl(events)) == events  # JSONL round trip
    started = Counter(e.burn_id for e in _of(result, "BurnStarted"))
    ended = Counter(e.burn_id for e in _of(result, "BurnEnded"))
    assert set(started.values()) <= {1} and set(ended.values()) <= {1}
    assert set(ended) <= set(started)


@pytest.fixture(scope="module")
def slice_run():
    return _run(load_scenario(M2_SLICE_SCENARIO))


# ------------------------------------------------------------------ the vertical slice


def test_slice_event_sequence(slice_run):
    _check_log_invariants(slice_run)
    head = [e.type for e in slice_run.events[:5]]
    assert head == [
        "SimulationStarted",
        "SpacecraftConfigured",
        "StateSampled",
        "PropulsionSampled",
        "CommandAccepted",
    ]
    milestones = [
        e.type for e in slice_run.events if e.type not in ("StateSampled", "PropulsionSampled")
    ]
    assert milestones[:5] == [
        "SimulationStarted",
        "SpacecraftConfigured",
        "CommandAccepted",
        "BurnStarted",
        "BurnEnded",
    ]
    done = slice_run.completed
    assert (done.status, done.failure_cause, done.tick, done.t) == ("success", None, 5370, 53700.0)
    assert slice_run.unsubmitted_command_ids == []


def test_slice_correlation_ids(slice_run):
    (accepted,) = _of(slice_run, "CommandAccepted")
    (started,) = _of(slice_run, "BurnStarted")
    (ended,) = _of(slice_run, "BurnEnded")
    assert accepted.command_id == started.command_id == ended.command_id == "slice-prograde-001"
    assert accepted.burn_id == started.burn_id == ended.burn_id == "burn#000001"
    (receipt,) = slice_run.receipts
    assert receipt.burn_id == "burn#000001" and receipt.tick == 0


def test_slice_commanded_vs_executed(slice_run):
    """P1: ignition at the commanded time, cutoff at ignition + duration (represented)."""
    spec = slice_run.scenario.spacecraft.to_spec()
    (accepted,) = _of(slice_run, "CommandAccepted")
    (started,) = _of(slice_run, "BurnStarted")
    (ended,) = _of(slice_run, "BurnEnded")
    # Commanded intent, verbatim.
    assert accepted.commanded_ignition_t_s == started.commanded_ignition_t_s == 600.0
    assert accepted.commanded_duration_s == ended.commanded_duration_s == 77.3
    # Executed: exact event times; the represented interval is cutoff - ignition.
    assert started.event_t_s == 600.0 and (started.tick, started.t) == (60, 600.0)
    assert ended.event_t_s == accepted.planned_cutoff_t_s == 600.0 + 77.3
    assert (ended.tick, ended.t) == (68, 680.0)  # first tick after 677.3 s
    assert ended.executed_duration_s == ended.event_t_s - started.event_t_s
    assert ended.executed_duration_s == accepted.planned_burn_duration_s
    assert ended.end_cause == "completed"
    assert abs(ended.executed_duration_s - 77.3) < 1e-12  # float representation only
    assert accepted.timing_delta_v_error_mps <= 1e-7  # DR-0017
    # Propellant follows mdot * T; sensed dv follows the rocket equation (O1, O2).
    used = spec.engine.mass_flow_kgps * ended.executed_duration_s
    assert ended.propellant_used_kg == pytest.approx(used, rel=1e-12, abs=0)
    assert ended.propellant_used_kg == pytest.approx(
        accepted.planned_propellant_used_kg, rel=1e-12, abs=0
    )
    assert ended.sensed_delta_v_mps == pytest.approx(
        ended.rocket_equation_delta_v_mps, rel=1e-12, abs=0
    )
    assert ended.sensed_delta_v_mps == pytest.approx(29.3, abs=0.1)
    assert started.propellant_kg == 300.0 and started.total_mass_kg == 1300.0
    assert ended.total_mass_kg == 1000.0 + ended.propellant_kg


def test_slice_raises_apoapsis(slice_run):
    """P3 sanity check (precise metrics are T5 validators): about 250 x 351 km."""
    done = slice_run.completed
    assert done.min_altitude_m == pytest.approx(250e3, abs=1.0)
    assert done.max_altitude_m == pytest.approx(351e3, abs=1e3)


def test_propulsion_sampled_every_tick_while_burning(slice_run):
    samples = {e.tick: e for e in _of(slice_run, "PropulsionSampled")}
    assert all(tick in samples for tick in range(60, 69))  # ticks 60..68 touch the burn
    assert [samples[k].engine_state for k in range(60, 68)] == ["burning"] * 8
    assert samples[68].engine_state == "idle" and samples[60].active_burn_id == "burn#000001"
    assert 69 not in samples  # back to the telemetry cadence after the cutoff tick
    burning = samples[61]
    assert np.linalg.norm(burning.thrust_acceleration_mps2) == pytest.approx(
        490.0 / burning.total_mass_kg, rel=1e-12, abs=0
    )
    assert samples[0].pending_burn_ids == ()  # sampled before the tick-0 submission
    assert samples[6].pending_burn_ids == ("burn#000001",)
    state_ticks = {e.tick for e in _of(slice_run, "StateSampled")}
    assert state_ticks == set(range(0, 5371, 6)) | {5370}


def test_final_propulsion_state(slice_run):
    final = slice_run.final_propulsion
    (ended,) = _of(slice_run, "BurnEnded")
    assert final.engine_state is EngineState.IDLE and final.tick == 5370
    assert final.propellant_kg == ended.propellant_kg
    last = _of(slice_run, "PropulsionSampled")[-1]
    assert last.tick == 5370 and last.propellant_kg == final.propellant_kg


# ------------------------------------------------------------------ determinism and M1


def test_slice_is_deterministic_and_repeatable(slice_run):
    """Repeated execution in one process: byte-identical, with no shared state."""
    scenario = load_scenario(M2_SLICE_SCENARIO)
    first = to_jsonl(_run(scenario).events)
    second = to_jsonl(_run(scenario).events)
    assert first == second == to_jsonl(slice_run.events)
    assert scenario.config_hash() == load_scenario(M2_SLICE_SCENARIO).config_hash()


def test_m1_scenario_is_unchanged_by_the_m2_runner():
    """P10 through the M2 runner: bit-identical to the golden log on the reference host
    (DR-0006); elsewhere within the approved cross-platform bounds (DR-0008), like the
    cross-platform validator. CI hosts differ from the reference CPU in the last bits."""
    from tars.validation.cross_platform import compare_to_golden, load_golden, platform_info
    from tars.validation.thresholds import load_thresholds

    result = _run(load_scenario(M1_SCENARIO))
    golden = load_golden()
    metrics = compare_to_golden(result, golden)
    for name, limit in load_thresholds().for_validator("cross_platform").items():
        assert metrics[name] <= limit, name
    here, ref = platform_info(), golden["platform"]
    if all(here[k] == ref[k] for k in ("system", "machine", "cpu")):
        assert golden["events_sha256"] == M1_GOLDEN_SHA256
        assert metrics["bit_identical_to_golden"] == 1.0


def test_version_2_without_propulsion_reproduces_m1_events():
    """A v2 scenario with the M1 content takes the M1 path: identical events except
    the scenario hash in SimulationStarted."""
    data = json.loads(M1_SCENARIO.read_text())
    data["schema_version"] = 2
    v2 = _run(parse_scenario(json.dumps(data)))
    m1 = _run(load_scenario(M1_SCENARIO))
    assert v2.events[1:] == m1.events[1:]
    assert v2.events[0].model_copy(update={"scenario_hash": "x"}) == m1.events[0].model_copy(
        update={"scenario_hash": "x"}
    )


def test_spacecraft_without_commands_coasts_like_m1():
    """With a spacecraft and no burn, r and v are bit-identical to the M1 path."""
    with_sc = _run(_scenario(commands=[], stop_s=3000.0))
    without = _run(_scenario(commands=[], stop_s=3000.0, spacecraft=None))
    np.testing.assert_array_equal(with_sc.final.r, without.final.r)
    np.testing.assert_array_equal(with_sc.final.v, without.final.v)
    assert not _of(without, "PropulsionSampled") and not _of(without, "SpacecraftConfigured")


# ------------------------------------------------------------------ stop boundaries


def test_burn_crossing_the_stop_time_is_not_ended():
    """The stop is an observation horizon, not an engine command (DR-0018): no
    BurnEnded is invented; the final sample shows the burn still active."""
    result = _run(_scenario(stop_s=650.0))
    _check_log_invariants(result)
    assert len(_of(result, "BurnStarted")) == 1 and not _of(result, "BurnEnded")
    last = _of(result, "PropulsionSampled")[-1]
    assert (last.tick, last.engine_state, last.active_burn_id) == (65, "burning", "burn#000001")
    assert result.final_propulsion.engine_state is EngineState.BURNING
    assert result.completed.status == "success" and result.completed.t == 650.0
    # Physics up to the stop is the same as in the full run.
    full = _run(_scenario(stop_s=1000.0))
    (same_tick,) = [e for e in _of(full, "PropulsionSampled") if e.tick == 65]
    assert last == same_tick


def test_ignition_exactly_at_the_stop_time():
    result = _run(_scenario(stop_s=600.0))
    _check_log_invariants(result)
    (started,) = _of(result, "BurnStarted")
    assert (started.tick, started.event_t_s) == (60, 600.0)
    assert result.final_propulsion.engine_state is EngineState.BURNING
    assert result.final_propulsion.propellant_kg == 300.0  # no time to burn anything


def test_cutoff_exactly_at_the_stop_time():
    result = _run(_scenario(commands=[_cmd(duration=80.0)], stop_s=680.0))
    _check_log_invariants(result)
    (ended,) = _of(result, "BurnEnded")
    assert (ended.tick, ended.event_t_s, ended.end_cause) == (68, 680.0, "completed")
    assert result.final_propulsion.engine_state is EngineState.IDLE


def test_pending_burn_at_the_stop_time():
    result = _run(_scenario(commands=[_cmd(ignition=700.0)], stop_s=650.0))
    _check_log_invariants(result)
    assert len(_of(result, "CommandAccepted")) == 1 and not _of(result, "BurnStarted")
    assert result.final_propulsion.pending_burn_ids == ("burn#000001",)
    assert _of(result, "PropulsionSampled")[-1].engine_state == "scheduled"


def test_stop_off_the_sampling_grid_still_samples_the_final_state():
    result = _run(_scenario(stop_s=650.0, commands=[]))
    assert result.events[-2].type == "PropulsionSampled" and result.events[-2].tick == 65
    assert result.events[-3].type == "StateSampled" and result.events[-3].tick == 65


def test_orbits_stop_with_a_spacecraft_records_unsubmitted_commands():
    late = {"submit_t_s": 6000.0, "command": _cmd("late-1", ignition=6000.0)}
    result = _run(_scenario(commands=[_cmd(), late], stop_s={"orbits": 1}))
    _check_log_invariants(result)
    assert result.completed.orbits_completed == 1 and result.completed.status == "success"
    assert [r.command_id for r in result.receipts] == ["c1"]
    assert result.unsubmitted_command_ids == ["late-1"]


@pytest.mark.parametrize("submit_t,expected_tick", [(0.0, 1), (100.0, 11)])
def test_ignition_at_the_submission_tick_is_reported_at_the_next_tick(submit_t, expected_tick):
    """The step that reached tick k ran before the submission, so an ignition at k*dt
    executes at the start of the next step (contract: envelope = end of that step)."""
    command = {"submit_t_s": submit_t, "command": _cmd(ignition=submit_t, duration=5.0)}
    result = _run(_scenario(commands=[command], stop_s=200.0))
    _check_log_invariants(result)
    started, ended = (e for e in result.events if e.type in BURN_EVENTS)
    assert (started.event_t_s, started.tick) == (submit_t, expected_tick)
    assert (ended.event_t_s, ended.tick) == (submit_t + 5.0, expected_tick)
    assert ended.executed_duration_s == 5.0


# ------------------------------------------------------------------ several burns


def test_two_burns_in_one_tick_in_exact_time_order():
    commands = [_cmd("a", ignition=601.0, duration=2.0), _cmd("b", ignition=603.0, duration=4.0)]
    result = _run(_scenario(commands=commands, stop_s=700.0))
    _check_log_invariants(result)
    burns = [(e.type, e.burn_id, e.event_t_s) for e in result.events if e.type in BURN_EVENTS]
    assert burns == [
        ("BurnStarted", "burn#000001", 601.0),
        ("BurnEnded", "burn#000001", 603.0),  # cutoff before the ignition at the same time
        ("BurnStarted", "burn#000002", 603.0),
        ("BurnEnded", "burn#000002", 607.0),
    ]
    assert {e.tick for e in result.events if e.type in BURN_EVENTS} == {61}


def test_command_ids_and_burn_ids_correlate_across_burns():
    commands = [
        _cmd("first", ignition=600.0, duration=10.0),
        _cmd("bad", duration=-1.0),  # rejected: consumes no burn number
        {"submit_t_s": 700.0, "command": _cmd("second", ignition=800.0, duration=5.0)},
    ]
    result = _run(_scenario(commands=commands, stop_s=900.0))
    _check_log_invariants(result)
    pairs = {(e.command_id, e.burn_id) for e in result.events if e.type in BURN_EVENTS}
    assert pairs == {("first", "burn#000001"), ("second", "burn#000002")}
    (rejected,) = _of(result, "CommandRejected")
    assert (rejected.command_id, rejected.reason, rejected.tick) == (
        "bad",
        "non_positive_duration",
        0,
    )
    (_, late) = _of(result, "CommandAccepted")
    assert (late.tick, late.t, late.burn_id) == (70, 700.0, "burn#000002")


# ------------------------------------------------------------------ rejected commands


INVALID = [
    ({"submit_t_s": 0.0, "command": _cmd("dup", ignition=600.0)}, None),
    ({"submit_t_s": 0.0, "command": _cmd("dup", ignition=900.0)}, "duplicate_command_id"),
    ({"submit_t_s": 0.0, "command": _cmd("zero", duration=0.0)}, "non_positive_duration"),
    ({"submit_t_s": 0.0, "command": _cmd("ovl", ignition=650.0)}, "overlaps_scheduled_burn"),
    (
        {"submit_t_s": 0.0, "command": _cmd("big", ignition=700.0, duration=1e4)},
        "insufficient_propellant",
    ),
    (
        {"submit_t_s": 0.0, "command": _cmd("far", ignition=1e20, duration=1e-10)},
        "burn_unschedulable",
    ),
    ({"submit_t_s": 0.0, "command": _cmd("bool", duration=True)}, "schema_invalid"),
    ({"submit_t_s": 0.0, "command": _cmd("extra", unexpected=1)}, "schema_invalid"),
    ({"submit_t_s": 0.0, "command": _cmd("nested", ignition=[600.0])}, "schema_invalid"),
    ({"submit_t_s": 0.0, "command": {"type": "BurnCommand"}}, "schema_invalid"),
    ({"submit_t_s": 100.0, "command": _cmd("past", ignition=50.0)}, "ignition_in_past"),
    ({"submit_t_s": 620.0, "command": _cmd("busy", ignition=630.0)}, "engine_busy"),
]


def test_each_rejection_reason_from_the_timeline():
    result = _run(_scenario(commands=[c for c, _ in INVALID], stop_s=1000.0))
    _check_log_invariants(result)
    outcomes = [r.reason.value if r.reason else None for r in result.receipts]
    assert outcomes == [reason for _, reason in INVALID]
    rejected = _of(result, "CommandRejected")
    assert [e.reason for e in rejected] == [r for _, r in INVALID if r is not None]
    assert [(e.tick, e.command_id) for e in rejected][-2:] == [(10, "past"), (62, "busy")]
    (schema_bad,) = [e for e in rejected if e.command_id == "bool"]
    assert schema_bad.commanded_duration_s is None and schema_bad.schema_errors


def test_rejected_commands_change_nothing():
    """P7: the log with rejected commands equals the log without them, except for
    the CommandRejected events and the scenario hash."""
    with_invalid = _run(_scenario(commands=[c for c, _ in INVALID], stop_s=1000.0))
    valid_only = _run(_scenario(commands=[INVALID[0][0]], stop_s=1000.0))

    def physical(result):
        return [e for e in result.events[1:] if e.type != "CommandRejected"]

    assert physical(with_invalid) == physical(valid_only)


def test_rejected_command_id_can_be_resubmitted():
    commands = [
        _cmd("retry", duration=0.0),
        {"submit_t_s": 100.0, "command": _cmd("retry", ignition=600.0)},
    ]
    result = _run(_scenario(commands=commands))
    assert [r.status.value for r in result.receipts] == ["rejected", "accepted"]
    assert _of(result, "BurnStarted")[0].command_id == "retry"


def test_no_propulsion_configured():
    result = _run(_scenario(commands=[_cmd(duration=0.0)], spacecraft=None))
    _check_log_invariants(result)
    (rejected,) = _of(result, "CommandRejected")
    assert rejected.reason == "no_propulsion_configured"  # precedes the duration check
    assert not _of(result, "PropulsionSampled") and result.final_propulsion is None


def test_no_propellant():
    empty = {
        "dry_mass_kg": 1000.0,
        "propellant_kg": 0.0,
        "engine": {"thrust_n": 490.0, "isp_s": 312.0},
    }
    result = _run(_scenario(spacecraft=empty))
    (rejected,) = _of(result, "CommandRejected")
    assert rejected.reason == "no_propellant"


# ------------------------------------------------------------------ depletion


DEPLETING = {
    "dry_mass_kg": 1000.0,
    "propellant_kg": 5.0,
    "engine": {"thrust_n": 490.0, "isp_s": 312.0},
}


def test_insufficient_propellant_rejected_by_default():
    result = _run(_scenario(spacecraft=DEPLETING))
    (rejected,) = _of(result, "CommandRejected")
    assert rejected.reason == "insufficient_propellant" and rejected.commanded_duration_s == 77.3
    assert not [e for e in result.events if e.type in BURN_EVENTS]
    assert result.final_propulsion.propellant_kg == 5.0


def test_burn_to_depletion_is_reported_distinctly():
    """DR-0017 D1a / safeguard 6: depletion is a different end cause and its own event."""
    command = _cmd(on_insufficient_propellant="burn_to_depletion")
    result = _run(_scenario(commands=[command], spacecraft=DEPLETING))
    _check_log_invariants(result)
    burns = [e for e in result.events if e.type in BURN_EVENTS]
    assert [e.type for e in burns] == ["BurnStarted", "PropellantDepleted", "BurnEnded"]
    _, depleted, ended = burns
    (accepted,) = _of(result, "CommandAccepted")
    assert accepted.planned_end_cause == "propellant_depleted"
    assert ended.end_cause == "propellant_depleted" and ended.commanded_duration_s == 77.3
    assert depleted.event_t_s == ended.event_t_s == accepted.planned_cutoff_t_s
    assert depleted.tick == ended.tick and depleted.burn_id == ended.burn_id
    mdot = 490.0 / (312.0 * 9.80665)
    assert ended.executed_duration_s == pytest.approx(5.0 / mdot, abs=1e-9)
    assert ended.executed_duration_s < 77.3
    assert 0.0 <= depleted.residual_propellant_kg <= 1e-12  # step-down residual (D1a)
    assert depleted.residual_propellant_kg == ended.propellant_kg
    assert result.final_propulsion.propellant_kg >= 0.0


# ------------------------------------------------------------------ failures


def _with_extra_force(monkeypatch, accel):
    class Extra:
        name = "test_extra"

        def acceleration(self, t, r, v):
            return accel(t, r, v)

    original = runner.build_force_model

    def patched(s):
        from tars.sim.forces import CompositeForceModel

        return CompositeForceModel([*original(s).models, Extra()])

    monkeypatch.setattr(runner, "build_force_model", patched)


def test_non_finite_step_during_a_burn_emits_no_partial_or_duplicate_events(monkeypatch):
    _with_extra_force(
        monkeypatch, lambda t, r, v: np.array([np.inf, 0, 0]) if t > 620.0 else np.zeros(3)
    )
    result = _run(_scenario())
    _check_log_invariants(result)
    done = result.completed
    assert (done.status, done.failure_cause, done.tick) == ("failure", "non_finite", 62)
    assert len(_of(result, "BurnStarted")) == 1 and not _of(result, "BurnEnded")
    assert max(e.tick for e in result.events) == 62  # nothing from the failed step
    assert result.final_propulsion.tick == 62


def test_failure_before_a_submission_leaves_it_unsubmitted(monkeypatch):
    _with_extra_force(monkeypatch, lambda t, r, v: -2.0 * v / np.linalg.norm(v))
    late = {"submit_t_s": 5000.0, "command": _cmd("late", ignition=5000.0)}
    result = _run(_scenario(commands=[late], stop_s=6000.0))
    assert result.completed.failure_cause == "impact"
    assert result.receipts == [] and result.unsubmitted_command_ids == ["late"]


def test_unexpected_error_propagates_without_a_result(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("converter failure")

    monkeypatch.setattr(runner, "burn_ended_event", boom)
    with pytest.raises(RuntimeError, match="converter failure"):
        _run(_scenario())


def test_emitter_rejects_inconsistent_transitions(slice_run):
    """A cutoff without its ignition, or a repeated ignition, is a bug: never emitted."""
    from tars.sim.simulator import Simulator

    spec = slice_run.scenario.spacecraft.to_spec()
    sim = Simulator(
        *runner.initial_state(slice_run.scenario),
        runner.build_force_model(slice_run.scenario),
        runner.INTEGRATORS["rk4"](),
        10.0,
        spacecraft=spec,
    )
    sim.submit(_cmd(ignition=5.0, duration=2.0))
    sim.step()
    ignition, cutoff = sim.engine_transitions
    emitter = runner._BurnEventEmitter(spec)
    with pytest.raises(KeyError):
        emitter.events((cutoff,), 1, 10.0)
    emitter.events((ignition,), 1, 10.0)
    with pytest.raises(RuntimeError, match="duplicate ignition"):
        emitter.events((ignition,), 1, 10.0)


def test_runner_uses_only_the_command_entry_point():
    """Architecture: the runner submits commands and never schedules or mutates."""
    import inspect

    source = inspect.getsource(runner)
    assert "schedule_burn" not in source
    assert "sim._" not in source
