"""M2 task T3: command and event schema (DR-0014, ADR-0007).

BurnCommand -> Simulator.submit() -> CommandReceipt; engine transitions -> events.
Commanded intent is kept separate from executed outcome; correlation IDs are stable.
"""

import json
import math

import numpy as np
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


def test_rejected_commands_do_not_consume_their_id():
    """REV-T3-01: a rejection changes nothing, including the command-ID registry; the
    corrected command may be resubmitted under the same ID. IDs are consumed only on
    acceptance."""
    sim = _sim()
    _reject(sim, _cmd(command_id="once", duration_s=0.0))
    assert sim.submit(_cmd(command_id="once")).status is CommandStatus.ACCEPTED
    receipt = _reject(sim, _cmd(command_id="once", ignition_t_s=900.0))
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
    sample = propulsion_sampled_event(sim.propulsion_snapshot(), sim.snapshot(), sc)
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
        propulsion_sampled_event(
            sim.propulsion_snapshot(), sim.snapshot(), SpacecraftSpec(DRY, ENGINE, TankSpec(PROP))
        ),
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


def _sample_events():
    sim, receipt, tr = _executed_burn()
    (ign, it, itt), (cut, ct, ctt) = tr["ignition"], tr["cutoff"]
    sc = SpacecraftSpec(DRY, ENGINE, TankSpec(PROP))
    return {
        CommandAccepted: command_event(receipt),
        CommandRejected: command_event(sim.submit(_cmd(command_id="z", duration_s=-1.0))),
        BurnStarted: burn_started_event(ign, tick=it, t=itt, dry_mass_kg=DRY),
        BurnEnded: burn_ended_event(ign, cut, tick=ct, t=ctt, dry_mass_kg=DRY, engine=ENGINE),
        PropulsionSampled: propulsion_sampled_event(sim.propulsion_snapshot(), sim.snapshot(), sc),
    }


@pytest.mark.parametrize(
    "event_type", [CommandAccepted, CommandRejected, BurnStarted, BurnEnded, PropulsionSampled]
)
def test_new_events_reject_extra_fields(event_type):
    """REV-T3-07: one property per test; Python input keeps tuples (model_dump)."""
    data = _sample_events()[event_type].model_dump()
    assert event_type.model_validate(data) == _sample_events()[event_type]  # control
    with pytest.raises(ValidationError) as err:
        event_type.model_validate({**data, "unexpected": 1})
    assert [e["type"] for e in err.value.errors()] == ["extra_forbidden"]


@pytest.mark.parametrize(
    "event_type", [CommandAccepted, CommandRejected, BurnStarted, BurnEnded, PropulsionSampled]
)
def test_new_events_reject_non_finite_numbers_from_json(event_type):
    sample = _sample_events()[event_type]
    data = json.loads(sample.model_dump_json())
    assert event_type.model_validate_json(json.dumps(data)) == sample  # control
    text = json.dumps({**data, "t": 1.0}).replace('"t": 1.0', '"t": 1e999')
    with pytest.raises(ValidationError) as err:
        event_type.model_validate_json(text)
    assert [(e["loc"], e["type"]) for e in err.value.errors()] == [(("t",), "finite_number")]


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
                out.append(
                    propulsion_sampled_event(
                        sim.propulsion_snapshot(),
                        sim.snapshot(),
                        SpacecraftSpec(DRY, ENGINE, TankSpec(PROP)),
                    )
                )
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


# ------------------------------------------------- review M2-T3-review-01 regressions


class _AnnotatedCommand(BurnCommand):
    """A subclass carrying a mutable extra field (REV-T3-02)."""

    model_config = {**BurnCommand.model_config, "extra": "allow"}  # noqa: RUF012
    annotations: list = []  # noqa: RUF012


@pytest.mark.parametrize(
    "update",
    [{"schema_version": 2}, {"command_id": []}, {"issuer": []}, {"duration_s": "5"}],
)
def test_prebuilt_commands_are_revalidated(update):
    """REV-T3-02: model_copy(update=...) skips validation; submit must not trust it."""
    sim = _sim()
    forged = BurnCommand(**_cmd()).model_copy(update=update)
    receipt = sim.submit(forged)  # must not raise
    assert receipt.status is CommandStatus.REJECTED
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert sim.propulsion_snapshot().pending_plans == ()


def test_subclassed_commands_with_extra_mutable_fields_are_rejected():
    sim = _sim()
    receipt = sim.submit(_AnnotatedCommand(**_cmd(), annotations=["x"]))
    assert receipt.reason is BurnRejection.SCHEMA_INVALID


def test_receipt_owns_a_canonical_copy_of_the_command():
    cmd = BurnCommand(**_cmd())
    receipt = _sim().submit(cmd)
    assert receipt.command == cmd
    assert receipt.command is not cmd
    assert type(receipt.command) is BurnCommand


def test_rejected_event_keeps_commanded_intent_or_structured_schema_errors():
    """REV-T3-03: intent for schema-valid rejections; bounded schema errors otherwise."""
    sim = _sim()
    valid = command_event(sim.submit(_cmd(command_id="neg", duration_s=-1.0)))
    assert valid.reason == "non_positive_duration"
    assert valid.commanded_duration_s == -1.0
    assert valid.commanded_ignition_t_s == 600.0
    assert valid.direction == "prograde" and valid.on_insufficient_propellant == "reject"
    assert valid.schema_errors == ()
    bad = command_event(sim.submit(_cmd(command_id="bad", duration_s="5", direction="up")))
    assert bad.reason == "schema_invalid"
    assert bad.commanded_duration_s is None and bad.direction is None
    assert bad.schema_errors == ("direction: literal_error", "duration_s: float_type")


def test_propulsion_sample_carries_the_truth_thrust_acceleration():
    """REV-T3-03: F/m along the active direction law while burning; zero otherwise."""
    sim = _sim()
    sc = SpacecraftSpec(DRY, ENGINE, TankSpec(PROP))
    sim.submit(_cmd(direction="retrograde"))
    idle = propulsion_sampled_event(sim.propulsion_snapshot(), sim.snapshot(), sc)
    assert idle.thrust_acceleration_mps2 == (0.0, 0.0, 0.0)
    _run_until(sim, 620.0)
    p, s = sim.propulsion_snapshot(), sim.snapshot()
    sample = propulsion_sampled_event(p, s, sc)
    expected = -(ENGINE.thrust_n / p.total_mass_kg) * s.v / np.linalg.norm(s.v)
    np.testing.assert_allclose(sample.thrust_acceleration_mps2, expected, rtol=1e-15, atol=0)


@pytest.mark.parametrize(
    "payload",
    [
        {"issuer": "\ud800"},
        {"command_id": "ok", "issuer": "\ud800"},
        {"\ud800": 1},
        {"command_id": "ok", "issuer": "x", "unexpected\udfff": 1},
    ],
)
def test_rejection_events_from_malformed_unicode_serialize(payload):
    """REV-T3-04: nothing echoed into receipts can break JSONL serialization."""
    receipt = _sim().submit(payload)
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    line = command_event(receipt).model_dump_json()
    assert parse_event(line) == command_event(receipt)


def test_command_with_invalid_unicode_issuer_is_schema_invalid():
    with pytest.raises(ValidationError):
        BurnCommand(**_cmd(issuer="ok\ud800"))


def test_schedule_burn_keeps_its_t2_signature_and_null_command_ids():
    """REV-T3-05: correlation by command ID only through submit()."""
    import inspect

    params = list(inspect.signature(Simulator.schedule_burn).parameters)
    assert params == ["self", "direction", "ignition_t_s", "duration_s", "policy"]
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=10.0)
    _run_until(sim, 620.0)
    assert sim.engine_transitions == () or all(e.command_id is None for e in sim.engine_transitions)
    assert sim.submit(_cmd(command_id="same", ignition_t_s=700.0, duration_s=5.0)).burn_id


@pytest.mark.parametrize("version", [True, 1.0, "1", 2])
def test_command_schema_version_must_be_the_integer_one(version):
    """REV-T3-06: Literal[1] alone matches True and 1.0 by equality."""
    with pytest.raises(ValidationError):
        BurnCommand(**_cmd(schema_version=version))
    with pytest.raises(ValidationError):
        BurnCommand.model_validate_json(json.dumps(_cmd(schema_version=version)))


@pytest.mark.parametrize("version", ["true", "1.0"])
def test_m2_event_schema_version_must_be_the_integer_one(version):
    sample = _sample_events()[BurnEnded]
    text = sample.model_dump_json().replace('"schema_version":1', f'"schema_version":{version}')
    with pytest.raises(ValidationError):
        BurnEnded.model_validate_json(text)


@pytest.mark.parametrize(
    ("field", "value"),
    [("command_id", "bad\n#"), ("command_id", ""), ("burn_id", ""), ("burn_id", "burn#1")],
)
def test_m2_event_correlation_ids_are_constrained(field, value):
    data = _sample_events()[BurnEnded].model_dump()
    with pytest.raises(ValidationError):
        BurnEnded.model_validate({**data, field: value})


def test_safe_text_escapes_invalid_unicode_and_bounds_length():
    """Contract of the echo sanitizer (defence in depth for REV-T3-04: current pydantic
    already reports invalid-Unicode keys without echoing them)."""
    from tars.sim.commands import safe_text

    assert safe_text("a\ud800b") == "a\\ud800b"
    json.dumps(safe_text("x\udfff")).encode("utf-8")
    assert safe_text("é ok") == "é ok"
    assert len(safe_text("y" * 500, limit=50)) == 50


# ------------------------------------------ re-verification (M2-T3-review-01) N1-N4


class _SelfDumpingCommand(BurnCommand):
    """N1: a subclass whose model_dump returns itself (caller-controlled serialization)."""

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        return self


class _RaisingDumpCommand(BurnCommand):
    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        raise RuntimeError("hostile dump")


class _RaisingDict(dict):
    def get(self, *args, **kwargs):
        raise RuntimeError("hostile get")

    def keys(self):
        raise RuntimeError("hostile keys")


def test_overridden_model_dump_cannot_bypass_validation():
    sim = _sim()
    forged = _SelfDumpingCommand(**_cmd()).model_copy(update={"schema_version": 2, "issuer": []})
    receipt = sim.submit(forged)
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert receipt.command is None
    assert sim.propulsion_snapshot().pending_plans == ()


def test_only_exact_burn_commands_or_plain_mappings_are_accepted():
    """A well-formed subclass instance is still not an exact BurnCommand."""
    receipt = _sim().submit(_SelfDumpingCommand(**_cmd()))
    assert receipt.reason is BurnRejection.SCHEMA_INVALID


@pytest.mark.parametrize(
    ("payload_factory", "expected"),
    [
        (lambda: _RaisingDumpCommand(**_cmd()), "schema_invalid"),
        (lambda: object(), "schema_invalid"),
        (lambda: 42, "schema_invalid"),
        # dict(payload) copies a dict subclass's storage without calling its overridden
        # methods, so its (valid) content is read safely and accepted.
        (lambda: _RaisingDict(_cmd()), None),
    ],
)
def test_hostile_payloads_never_escape_submit(payload_factory, expected):
    """N2: no ordinary exception escapes payload handling; every outcome is a writable
    record."""
    sim = _sim()
    receipt = sim.submit(payload_factory())
    assert (receipt.reason.value if receipt.reason else None) == expected
    command_event(receipt).model_dump_json()


@pytest.mark.parametrize(
    ("event_type", "field", "value"),
    [
        (CommandAccepted, "issuer", "x\ud800"),
        (CommandRejected, "issuer", "x\ud800"),
        (CommandRejected, "detail", "d\udfff"),
        (CommandRejected, "schema_errors", ("ok", "bad\ud800")),
    ],
)
def test_m2_event_strings_must_be_valid_unicode(event_type, field, value):
    """N3: an event that validates must also serialize."""
    data = _sample_events()[event_type].model_dump()
    with pytest.raises(ValidationError):
        event_type.model_validate({**data, field: value})


def test_spacecraft_event_direction_laws_must_be_valid_unicode():
    sc = SpacecraftSpec(DRY, ENGINE, TankSpec(PROP))
    data = spacecraft_configured_event(sc, tick=0, t=0.0).model_dump()
    with pytest.raises(ValidationError):
        SpacecraftConfigured.model_validate({**data, "direction_laws": ("prograde", "\ud800")})


def test_no_propulsion_configured_precedes_command_checks():
    """N4: documented precedence: without a spacecraft, every schema-valid, non-duplicate
    command is no_propulsion_configured (T2 behavior)."""
    receipt = _sim(spacecraft=False).submit(_cmd(duration_s=-1.0, ignition_t_s=-5.0))
    assert receipt.reason is BurnRejection.NO_PROPULSION_CONFIGURED


def test_unforeseen_payload_failures_are_contained_but_interrupts_propagate(monkeypatch):
    """N2 contract: any ordinary exception while handling a payload becomes a
    schema_invalid receipt; process-control exceptions are not swallowed."""
    import tars.sim.simulator as simulator_module

    def boom(payload):
        raise RuntimeError("unforeseen")

    monkeypatch.setattr(simulator_module, "parse_command", boom)
    receipt = _sim().submit(_cmd())
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert receipt.schema_errors == ("<payload>: unprocessable",)
    assert receipt.command_id == "burn-001"  # still echoed from a plain dict

    def interrupt(payload):
        raise KeyboardInterrupt

    monkeypatch.setattr(simulator_module, "parse_command", interrupt)
    with pytest.raises(KeyboardInterrupt):
        _sim().submit(_cmd())


# ---------------------------------- second re-verification (M2-T3-review-01) N5, N6


class _SelfSerializer:
    def __init__(self, payload):
        self.payload = payload

    def to_python(self, *args, **kwargs):
        return self.payload


class _ThrowSerializer:
    def to_python(self, *args, **kwargs):
        raise RuntimeError("hostile serializer")


class _HashBomb(str):
    def __hash__(self):
        raise RuntimeError("caller hash escaped")


class _HostileKey:
    __hash__ = object.__hash__

    def __repr__(self):
        raise RuntimeError("repr")

    def __eq__(self, other):
        raise RuntimeError("eq")


def _forged(update, serializer=None):
    payload = BurnCommand(**_cmd()).model_copy(update=update)
    object.__setattr__(payload, "__pydantic_serializer__", serializer or _SelfSerializer(payload))
    return payload


def test_instance_serializer_hooks_cannot_bypass_validation():
    """N5: no pydantic serialization hook of the untrusted instance is used."""
    sim = _sim()
    forged = _forged({"schema_version": 2, "issuer": []})
    receipt = sim.submit(forged)
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert sim.propulsion_snapshot().pending_plans == ()
    # A per-instance serializer means tampering: rejected, and its hook is never called.
    receipt = sim.submit(_forged({}, _ThrowSerializer()))
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert receipt.schema_errors == ("<payload>: tampered_instance",)


def test_receipt_intent_cannot_be_changed_through_the_submitted_instance():
    payload = BurnCommand(**_cmd())
    receipt = _sim().submit(payload)
    payload.__dict__["duration_s"] = 1.0  # mutate the caller's object afterwards
    assert receipt.command.duration_s == 77.3


@pytest.mark.parametrize(
    "payload_factory",
    [
        lambda: _forged({"command_id": _HashBomb("burn-001")}),
        lambda: {**_cmd(), "command_id": _HashBomb("burn-001")},
        lambda: {**_cmd(), "issuer": _HashBomb("x")},
        lambda: {**_cmd(), _HostileKey(): 1},
        lambda: {**_cmd(), "duration_s": type("F", (float,), {})(77.3)},
    ],
)
def test_non_builtin_values_and_keys_are_rejected_without_escaping(payload_factory):
    """N5: only exact str/int/float values and str keys reach validation; nothing echoed
    into the receipt is a caller-defined object."""
    sim = _sim()
    receipt = sim.submit(payload_factory())
    assert receipt.reason is BurnRejection.SCHEMA_INVALID
    assert sim.propulsion_snapshot().pending_plans == ()
    assert receipt.command_id is None or type(receipt.command_id) is str
    assert receipt.issuer is None or type(receipt.issuer) is str
    command_event(receipt).model_dump_json()


def test_non_string_keys_are_rejected_explicitly():
    receipt = _sim().submit({**_cmd(), _HostileKey(): 1})
    assert receipt.schema_errors == ("<payload>: non_string_key",)


def test_any_mapping_type_is_accepted():
    """N6: the contract accepts mappings; they are copied into a plain dict."""
    from collections import UserDict
    from types import MappingProxyType

    for payload in (UserDict(_cmd(command_id="u")), MappingProxyType(_cmd(command_id="m"))):
        sim = _sim()
        assert sim.submit(payload).status is CommandStatus.ACCEPTED
