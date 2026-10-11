"""M2 task T3: command and event schema (DR-0014, ADR-0007).

BurnCommand -> Simulator.submit() -> CommandReceipt; engine transitions -> events.
Commanded intent is kept separate from executed outcome; correlation IDs are stable.
"""

import json
import math

import pytest
from pydantic import ValidationError

from tars.astro.elements import circular_orbit_state
from tars.events import parse_event, read_jsonl, to_jsonl
from tars.events.schema import (
    BurnEnded,
    BurnStarted,
    CommandAccepted,
    CommandRejected,
    PropellantDepleted,
    PropulsionSampled,
    SpacecraftConfigured,
)
from tars.sim.burn_events import (
    burn_ended_event,
    burn_started_event,
    command_event,
    propellant_depleted_event,
    propulsion_sampled_event,
    spacecraft_configured_event,
)
from tars.sim.commands import BurnCommand, CommandReceipt, CommandStatus
from tars.sim.constants import WGS84
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import (
    BurnRejection,
    EngineSpec,
    SpacecraftSpec,
    TankSpec,
    rocket_equation_delta_v,
)
from tars.sim.simulator import Simulator

ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
DRY, PROP = 1000.0, 300.0
R0, V0 = circular_orbit_state(
    radius=WGS84.equatorial_radius + 250_000.0,
    inclination=math.radians(51.6),
    raan=0.0,
    arg_latitude=0.0,
    mu=WGS84.mu,
)
APPROVED_REJECTION_CODES = {
    "schema_invalid",
    "non_positive_duration",
    "ignition_in_past",
    "overlaps_scheduled_burn",
    "engine_busy",
    "no_propellant",
    "insufficient_propellant",
    "duplicate_command_id",
    "no_propulsion_configured",
    "burn_unschedulable",
}


def _sim(propellant=PROP, spacecraft=True):
    sc = (
        SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=propellant))
        if spacecraft
        else None
    )
    return Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0, spacecraft=sc)


def _cmd(**overrides):
    fields = {
        "command_id": "burn-001",
        "issuer": "scenario_timeline",
        "ignition_t_s": 600.0,
        "direction": "prograde",
        "duration_s": 77.3,
        **overrides,
    }
    return fields


def _run_until(sim, t_end):
    while sim.t < t_end:
        sim.step()


# ------------------------------------------------------------------- BurnCommand schema


def test_burn_command_is_versioned_strict_and_immutable():
    cmd = BurnCommand(**_cmd())
    assert cmd.schema_version == 1
    assert cmd.type == "BurnCommand"
    assert cmd.on_insufficient_propellant == "reject"
    with pytest.raises(ValidationError):
        cmd.duration_s = 1.0  # frozen
    assert BurnCommand.model_validate_json(cmd.model_dump_json()) == cmd


@pytest.mark.parametrize(
    "overrides",
    [
        {"ignition_t_s": "600"},
        {"ignition_t_s": True},
        {"ignition_t_s": math.nan},
        {"duration_s": math.inf},
        {"duration_s": None},
        {"direction": "sideways"},
        {"on_insufficient_propellant": "sometimes"},
        {"command_id": ""},
        {"command_id": "has space"},
        {"command_id": "x" * 65},
        {"issuer": ""},
        {"extra_field": 1},
        {"schema_version": 2},
    ],
)
def test_malformed_commands_fail_schema_validation(overrides):
    with pytest.raises(ValidationError):
        BurnCommand(**_cmd(**overrides))


def test_duration_sign_is_not_a_schema_matter():
    """Non-positive duration keeps its own approved code (DR-0014), not schema_invalid."""
    assert BurnCommand(**_cmd(duration_s=-1.0)).duration_s == -1.0


# ----------------------------------------------------------------- submit and receipts


def test_accepted_receipt_correlates_command_plan_and_burn_id():
    sim = _sim()
    receipt = sim.submit(BurnCommand(**_cmd()))
    assert receipt.status is CommandStatus.ACCEPTED
    assert receipt.command_id == "burn-001"
    assert receipt.burn_id == "burn#000001"
    assert receipt.reason is None
    assert receipt.plan.ignition_t_s == 600.0
    assert receipt.plan.commanded_duration_s == 77.3
    assert receipt.command.duration_s == 77.3  # commanded intent preserved verbatim
    assert receipt.tick == 0 and receipt.t == 0.0
    with pytest.raises(AttributeError):
        receipt.status = CommandStatus.REJECTED  # type: ignore[misc]


def test_submit_accepts_a_raw_mapping_and_validates_it():
    sim = _sim()
    receipt = sim.submit(_cmd())
    assert receipt.status is CommandStatus.ACCEPTED
    assert isinstance(receipt.command, BurnCommand)


def _reject(sim, payload):
    receipt = sim.submit(payload)
    assert receipt.status is CommandStatus.REJECTED
    assert receipt.plan is None and receipt.burn_id is None
    return receipt


def test_every_approved_rejection_code_is_reachable_through_submit():
    seen = set()

    seen.add(_reject(_sim(), _cmd(direction="sideways")).reason)
    seen.add(_reject(_sim(), _cmd(duration_s=0.0)).reason)
    sim = _sim()
    _run_until(sim, 100.0)
    seen.add(_reject(sim, _cmd(ignition_t_s=50.0)).reason)
    sim = _sim()
    sim.submit(_cmd(command_id="a", ignition_t_s=600.0, duration_s=50.0))
    seen.add(_reject(sim, _cmd(command_id="b", ignition_t_s=620.0, duration_s=5.0)).reason)
    _run_until(sim, 610.0)
    seen.add(_reject(sim, _cmd(command_id="c", ignition_t_s=620.0, duration_s=5.0)).reason)
    seen.add(_reject(_sim(propellant=0.0), _cmd()).reason)
    seen.add(_reject(_sim(), _cmd(duration_s=3000.0)).reason)
    sim = _sim()
    sim.submit(_cmd(command_id="dup"))
    seen.add(_reject(sim, _cmd(command_id="dup", ignition_t_s=900.0)).reason)
    seen.add(_reject(_sim(spacecraft=False), _cmd()).reason)
    seen.add(_reject(_sim(), _cmd(ignition_t_s=1e15, duration_s=0.1)).reason)

    assert {r.value for r in seen} == APPROVED_REJECTION_CODES
    assert all(isinstance(r, BurnRejection) for r in seen)


def test_schema_rejection_keeps_the_command_id_when_it_is_readable():
    receipt = _reject(_sim(), _cmd(command_id="ok-id", duration_s="5"))
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert receipt.command_id == "ok-id"
    assert receipt.command is None
    receipt = _reject(_sim(), {"command_id": 7})
    assert receipt.command_id is None


def test_rejected_submissions_change_nothing():
    sim = _sim()
    _run_until(sim, 100.0)
    before = (sim.snapshot().r.tobytes(), sim.propulsion_snapshot())
    for payload in (_cmd(ignition_t_s=50.0), _cmd(direction="x"), "not a mapping", None):
        _reject(sim, payload)
    assert (sim.snapshot().r.tobytes(), sim.propulsion_snapshot()) == before


def test_duplicate_ids_include_previously_rejected_commands():
    """A command ID is single use once it has been seen, accepted or rejected, so that
    receipts and events correlate unambiguously."""
    sim = _sim()
    _reject(sim, _cmd(command_id="once", duration_s=0.0))
    receipt = _reject(sim, _cmd(command_id="once"))
    assert receipt.reason is BurnRejection.DUPLICATE_COMMAND_ID


def test_burn_ids_are_deterministic_and_shared_with_engine_level_scheduling():
    """schedule_burn (T2 interface, unchanged) and submit draw from one sequence."""
    sim = _sim()
    p1 = sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=10.0)
    r2 = sim.submit(_cmd(command_id="c2", ignition_t_s=700.0, duration_s=10.0))
    assert p1.ignition_t_s == 600.0  # T2 return type unchanged
    assert r2.burn_id == "burn#000002"
    events = []
    while sim.t < 750.0:
        sim.step()
        events.extend(sim.engine_transitions)
    assert [(e.kind, e.burn_id, e.command_id) for e in events] == [
        ("ignition", "burn#000001", None),
        ("cutoff", "burn#000001", None),
        ("ignition", "burn#000002", "c2"),
        ("cutoff", "burn#000002", "c2"),
    ]


# ---------------------------------------------------------------------------- events


def _executed_burn(command_overrides=None, propellant=PROP, t_end=700.0):
    sim = _sim(propellant=propellant)
    receipt = sim.submit(_cmd(**(command_overrides or {})))
    transitions = {}
    while sim.t < t_end:
        sim.step()
        for e in sim.engine_transitions:
            transitions[e.kind] = (e, sim.tick, sim.t)
    return sim, receipt, transitions


def test_command_events_from_receipts():
    sim = _sim()
    accepted = command_event(sim.submit(_cmd()))
    rejected = command_event(sim.submit(_cmd(command_id="bad", duration_s=-1.0)))
    assert isinstance(accepted, CommandAccepted) and isinstance(rejected, CommandRejected)
    assert accepted.command_id == "burn-001" and accepted.burn_id == "burn#000001"
    assert accepted.commanded_duration_s == 77.3
    assert accepted.planned_cutoff_t_s == 600.0 + 77.3
    assert rejected.reason == "non_positive_duration"
    assert rejected.command_id == "bad"


def test_burn_started_and_ended_separate_intent_from_outcome():
    _, receipt, tr = _executed_burn()
    (ign, ign_tick, ign_t), (cut, cut_tick, cut_t) = tr["ignition"], tr["cutoff"]
    started = burn_started_event(ign, tick=ign_tick, t=ign_t, dry_mass_kg=DRY)
    ended = burn_ended_event(ign, cut, tick=cut_tick, t=cut_t, dry_mass_kg=DRY, engine=ENGINE)
    # correlation
    assert started.command_id == ended.command_id == "burn-001"
    assert started.burn_id == ended.burn_id == receipt.burn_id
    # commanded intent
    assert ended.commanded_duration_s == 77.3
    assert started.commanded_ignition_t_s == 600.0
    # executed outcome
    assert started.event_t_s == 600.0 and ended.event_t_s == cut.t
    assert ended.executed_duration_s == cut.t - ign.t
    assert ended.end_cause == "completed"
    used = ign.propellant_kg - cut.propellant_kg
    assert ended.propellant_used_kg == used
    assert ended.planned_propellant_used_kg == receipt.plan.propellant_used_kg
    assert ended.sensed_delta_v_mps == cut.delta_v_sensed_mps - ign.delta_v_sensed_mps
    expected_dv = rocket_equation_delta_v(
        ENGINE.exhaust_velocity_mps, DRY + ign.propellant_kg, DRY + cut.propellant_kg
    )
    assert ended.rocket_equation_delta_v_mps == expected_dv
    assert ended.sensed_delta_v_mps == pytest.approx(expected_dv, rel=1e-12, abs=0)
    assert tuple(ended.r) == tuple(cut.r)
    assert ended.total_mass_kg == DRY + cut.propellant_kg


def test_depletion_is_distinguished_in_events():
    _, receipt, tr = _executed_burn(
        {"duration_s": 100.0, "on_insufficient_propellant": "burn_to_depletion"},
        propellant=5.0,
    )
    (ign, _, _), (cut, cut_tick, cut_t) = tr["ignition"], tr["cutoff"]
    ended = burn_ended_event(ign, cut, tick=cut_tick, t=cut_t, dry_mass_kg=DRY, engine=ENGINE)
    assert ended.end_cause == "propellant_depleted"
    assert ended.executed_duration_s < ended.commanded_duration_s
    depleted = propellant_depleted_event(cut, tick=cut_tick, t=cut_t)
    assert isinstance(depleted, PropellantDepleted)
    assert depleted.burn_id == receipt.burn_id and depleted.residual_propellant_kg >= 0.0
    _, _, tr_ok = _executed_burn()
    with pytest.raises(ValueError):
        propellant_depleted_event(tr_ok["cutoff"][0], tick=1, t=10.0)


def test_spacecraft_and_sample_events():
    sim = _sim()
    sc = SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=PROP))
    configured = spacecraft_configured_event(sc, tick=0, t=0.0)
    assert isinstance(configured, SpacecraftConfigured)
    assert configured.mass_flow_kgps == ENGINE.mass_flow_kgps
    assert configured.timing_delta_v_budget_mps == 1e-7
    sim.submit(_cmd())
    _run_until(sim, 620.0)
    sample = propulsion_sampled_event(sim.propulsion_snapshot())
    assert isinstance(sample, PropulsionSampled)
    assert sample.engine_state == "burning" and sample.active_burn_id == "burn#000001"
    assert sample.pending_burn_ids == ()


def test_new_events_round_trip_through_jsonl_and_are_immutable():
    sim, receipt, tr = _executed_burn()
    (ign, it, itt), (cut, ct, ctt) = tr["ignition"], tr["cutoff"]
    events = [
        spacecraft_configured_event(SpacecraftSpec(DRY, ENGINE, TankSpec(PROP)), tick=0, t=0.0),
        command_event(receipt),
        burn_started_event(ign, tick=it, t=itt, dry_mass_kg=DRY),
        burn_ended_event(ign, cut, tick=ct, t=ctt, dry_mass_kg=DRY, engine=ENGINE),
        propulsion_sampled_event(sim.propulsion_snapshot()),
    ]
    text = to_jsonl(events)
    assert read_jsonl(text) == events
    for line, event in zip(text.splitlines(), events, strict=True):
        assert parse_event(line) == event
        assert json.loads(line)["schema_version"] == 1
    started = events[2]
    with pytest.raises(ValidationError):
        started.burn_id = "other"
    assert isinstance(started.r, tuple)


@pytest.mark.parametrize(
    "event_type", [CommandAccepted, CommandRejected, BurnStarted, BurnEnded, PropulsionSampled]
)
def test_new_events_reject_non_finite_and_extra_fields(event_type):
    sim, receipt, tr = _executed_burn()
    (ign, it, itt), (cut, ct, ctt) = tr["ignition"], tr["cutoff"]
    sample = {
        CommandAccepted: command_event(receipt),
        CommandRejected: command_event(sim.submit(_cmd(command_id="z", duration_s=-1.0))),
        BurnStarted: burn_started_event(ign, tick=it, t=itt, dry_mass_kg=DRY),
        BurnEnded: burn_ended_event(ign, cut, tick=ct, t=ctt, dry_mass_kg=DRY, engine=ENGINE),
        PropulsionSampled: propulsion_sampled_event(sim.propulsion_snapshot()),
    }[event_type]
    data = json.loads(sample.model_dump_json())
    with pytest.raises(ValidationError):
        event_type.model_validate({**data, "unexpected": 1})
    with pytest.raises(ValidationError):
        event_type.model_validate_json(
            sample.model_dump_json().replace('"t":', '"t":1e999,"x":', 1)
        )


def test_event_stream_is_deterministic():
    def stream():
        sim = _sim()
        out = [command_event(sim.submit(_cmd()))]
        out.append(command_event(sim.submit(_cmd(command_id="r", duration_s=0.0))))
        open_ign = {}
        while sim.t < 800.0:
            sim.step()
            for e in sim.engine_transitions:
                if e.kind == "ignition":
                    open_ign[e.burn_id] = e
                    out.append(burn_started_event(e, tick=sim.tick, t=sim.t, dry_mass_kg=DRY))
                else:
                    out.append(
                        burn_ended_event(
                            open_ign[e.burn_id],
                            e,
                            tick=sim.tick,
                            t=sim.t,
                            dry_mass_kg=DRY,
                            engine=ENGINE,
                        )
                    )
            if sim.tick % 6 == 0:
                out.append(propulsion_sampled_event(sim.propulsion_snapshot()))
        return to_jsonl(out)

    assert stream() == stream()


def test_receipts_are_frozen_dataclasses():
    import dataclasses

    assert dataclasses.is_dataclass(CommandReceipt)
    assert CommandReceipt.__dataclass_params__.frozen


def test_rejection_precedence_is_stable():
    """schema > non_positive_duration > ignition_in_past > engine conflicts > propellant /
    schedulability. A command failing several rules reports the earliest one."""
    sim = _sim(propellant=1.0)
    sim.submit(_cmd(command_id="first", ignition_t_s=600.0, duration_s=5.0))
    _run_until(sim, 100.0)
    cases = [
        (_cmd(command_id="a", duration_s="x", ignition_t_s=50.0), "schema_invalid"),
        (_cmd(command_id="b", duration_s=-1.0, ignition_t_s=50.0), "non_positive_duration"),
        (_cmd(command_id="c", ignition_t_s=50.0, duration_s=1e6), "ignition_in_past"),
        (_cmd(command_id="d", ignition_t_s=601.0, duration_s=1e6), "overlaps_scheduled_burn"),
        (_cmd(command_id="e", ignition_t_s=700.0, duration_s=1e6), "insufficient_propellant"),
    ]
    for payload, code in cases:
        assert sim.submit(payload).reason.value == code


def test_rejected_submissions_do_not_consume_burn_ids():
    """Burn IDs are dense and deterministic: only accepted burns are numbered."""
    sim = _sim()
    for payload in (
        _cmd(command_id="r1", duration_s=0.0),
        {"bad": 1},
        _cmd(command_id="r2", direction="x"),
    ):
        assert sim.submit(payload).status is CommandStatus.REJECTED
    assert sim.submit(_cmd(command_id="ok")).burn_id == "burn#000001"


@pytest.mark.parametrize("bad", [True, "1.5", None])
def test_m2_event_fields_are_strictly_typed(bad):
    """No lax coercion of bool/str into numbers in machine-readable events."""
    _, _, tr = _executed_burn()
    ign, it, itt = tr["ignition"]
    data = burn_started_event(ign, tick=it, t=itt, dry_mass_kg=DRY).model_dump()
    with pytest.raises(ValidationError):
        BurnStarted.model_validate({**data, "propellant_kg": bad})
    with pytest.raises(ValidationError):
        BurnStarted.model_validate({**data, "r": [1.0, 2.0, 3.0]})  # tuple required in Python
