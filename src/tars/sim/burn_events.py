"""Build machine-readable propulsion events from simulator outputs (DR-0014 section 5; T3).

Pure, deterministic functions: receipts, engine transitions, snapshots and specs in,
immutable events out. Commanded intent (from the command and plan) is kept separate
from the executed outcome (from the integrated state at the exact event time). When
events are emitted is the runner's concern (T4).
"""

from __future__ import annotations

from tars.events.schema import (
    BurnEnded,
    BurnStarted,
    CommandAccepted,
    CommandRejected,
    PropellantDepleted,
    PropulsionSampled,
    SpacecraftConfigured,
)
from tars.sim.commands import CommandReceipt, CommandStatus
from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.propulsion import (
    DIRECTION_LAWS,
    TIMING_DELTA_V_BUDGET_MPS,
    BurnEndCause,
    EngineSpec,
    EngineTransition,
    PropulsionSnapshot,
    SpacecraftSpec,
    rocket_equation_delta_v,
)


def _vec(values: object) -> tuple[float, float, float]:
    x, y, z = (float(v) for v in values)  # type: ignore[union-attr]
    return (x, y, z)


def command_event(receipt: CommandReceipt) -> CommandAccepted | CommandRejected:
    """CommandAccepted or CommandRejected, at the submission time recorded in the receipt."""
    if receipt.status is CommandStatus.REJECTED:
        assert receipt.reason is not None
        return CommandRejected(
            tick=receipt.tick,
            t=receipt.t,
            command_id=receipt.command_id,
            issuer=receipt.issuer,
            reason=receipt.reason.value,
            detail=receipt.detail,
        )
    cmd, plan = receipt.command, receipt.plan
    assert cmd is not None and plan is not None and receipt.burn_id is not None
    return CommandAccepted(
        tick=receipt.tick,
        t=receipt.t,
        command_id=cmd.command_id,
        issuer=cmd.issuer,
        burn_id=receipt.burn_id,
        direction=cmd.direction,
        on_insufficient_propellant=cmd.on_insufficient_propellant,
        commanded_ignition_t_s=cmd.ignition_t_s,
        commanded_duration_s=cmd.duration_s,
        planned_burn_duration_s=plan.burn_duration_s,
        planned_cutoff_t_s=plan.cutoff_t_s,
        planned_propellant_used_kg=plan.propellant_used_kg,
        planned_end_cause=plan.end_cause.value,
        timing_delta_v_error_mps=plan.timing_delta_v_error_mps,
    )


def burn_started_event(
    ignition: EngineTransition, *, tick: int, t: float, dry_mass_kg: float
) -> BurnStarted:
    """BurnStarted from an ignition transition. ``tick``/``t`` are the step it occurred in."""
    if ignition.kind != "ignition" or ignition.burn_id is None:
        raise ValueError("expected an ignition transition with a burn ID")
    plan = ignition.plan
    thrust_unit = DIRECTION_LAWS[ignition.direction].direction(ignition.t, ignition.r, ignition.v)
    return BurnStarted(
        tick=tick,
        t=t,
        command_id=ignition.command_id,
        burn_id=ignition.burn_id,
        direction=ignition.direction,
        commanded_ignition_t_s=plan.ignition_t_s,
        commanded_duration_s=plan.commanded_duration_s,
        planned_cutoff_t_s=plan.cutoff_t_s,
        planned_end_cause=plan.end_cause.value,
        event_t_s=ignition.t,
        r=_vec(ignition.r),
        v=_vec(ignition.v),
        thrust_unit_vector=_vec(thrust_unit),
        propellant_kg=ignition.propellant_kg,
        total_mass_kg=dry_mass_kg + ignition.propellant_kg,
    )


def burn_ended_event(
    ignition: EngineTransition,
    cutoff: EngineTransition,
    *,
    tick: int,
    t: float,
    dry_mass_kg: float,
    engine: EngineSpec,
) -> BurnEnded:
    """BurnEnded from the matching ignition and cutoff transitions (same burn ID)."""
    if ignition.kind != "ignition" or cutoff.kind != "cutoff":
        raise ValueError("expected an ignition and a cutoff transition")
    if ignition.burn_id is None or ignition.burn_id != cutoff.burn_id:
        raise ValueError("ignition and cutoff must belong to the same burn")
    assert cutoff.end_cause is not None
    m0 = dry_mass_kg + ignition.propellant_kg
    mf = dry_mass_kg + cutoff.propellant_kg
    return BurnEnded(
        tick=tick,
        t=t,
        command_id=cutoff.command_id,
        burn_id=cutoff.burn_id,
        direction=cutoff.direction,
        end_cause=cutoff.end_cause.value,
        commanded_duration_s=cutoff.plan.commanded_duration_s,
        ignition_t_s=ignition.t,
        event_t_s=cutoff.t,
        executed_duration_s=cutoff.t - ignition.t,
        planned_propellant_used_kg=cutoff.plan.propellant_used_kg,
        propellant_used_kg=ignition.propellant_kg - cutoff.propellant_kg,
        sensed_delta_v_mps=cutoff.delta_v_sensed_mps - ignition.delta_v_sensed_mps,
        rocket_equation_delta_v_mps=rocket_equation_delta_v(engine.exhaust_velocity_mps, m0, mf),
        r=_vec(cutoff.r),
        v=_vec(cutoff.v),
        propellant_kg=cutoff.propellant_kg,
        total_mass_kg=mf,
    )


def propellant_depleted_event(
    cutoff: EngineTransition, *, tick: int, t: float
) -> PropellantDepleted:
    """PropellantDepleted for a cutoff whose cause is depletion (DR-0017 safeguard 6)."""
    if cutoff.kind != "cutoff" or cutoff.end_cause is not BurnEndCause.PROPELLANT_DEPLETED:
        raise ValueError("not a depletion cutoff")
    assert cutoff.burn_id is not None
    return PropellantDepleted(
        tick=tick,
        t=t,
        command_id=cutoff.command_id,
        burn_id=cutoff.burn_id,
        event_t_s=cutoff.t,
        residual_propellant_kg=cutoff.propellant_kg,
    )


def spacecraft_configured_event(
    spec: SpacecraftSpec, *, tick: int, t: float
) -> SpacecraftConfigured:
    engine = spec.engine
    return SpacecraftConfigured(
        tick=tick,
        t=t,
        dry_mass_kg=spec.dry_mass_kg,
        propellant_kg=spec.tank.propellant_kg,
        thrust_n=engine.thrust_n,
        isp_s=engine.isp_s,
        standard_gravity_mps2=STANDARD_GRAVITY,
        exhaust_velocity_mps=engine.exhaust_velocity_mps,
        mass_flow_kgps=engine.mass_flow_kgps,
        timing_delta_v_budget_mps=TIMING_DELTA_V_BUDGET_MPS,
        direction_laws=tuple(sorted(DIRECTION_LAWS)),
    )


def propulsion_sampled_event(snapshot: PropulsionSnapshot) -> PropulsionSampled:
    return PropulsionSampled(
        tick=snapshot.tick,
        t=snapshot.t,
        propellant_kg=snapshot.propellant_kg,
        total_mass_kg=snapshot.total_mass_kg,
        delta_v_sensed_mps=snapshot.delta_v_sensed_mps,
        engine_state=snapshot.engine_state.value,
        active_burn_id=snapshot.active_burn_id,
        pending_burn_ids=snapshot.pending_burn_ids,
    )
