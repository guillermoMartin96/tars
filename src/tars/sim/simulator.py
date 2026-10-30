"""The simulator: sole owner of physical state (ADR-0002, ADR-0007).

Physical state changes only through ``step()``, which integrates the configured
force model and, when a spacecraft is configured, the propulsion subsystem.
External code receives read-only snapshots. There is deliberately no API that
assigns position, velocity, mass or propellant. ``schedule_burn`` only schedules
engine activity, after validation (DR-0013, DR-0014).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray
from pydantic import ValidationError

from tars.sim.commands import (
    BurnCommand,
    CommandReceipt,
    CommandStatus,
    PayloadTypeError,
    parse_command,
    readable_field,
    safe_text,
    schema_errors,
)
from tars.sim.forces import ForceContext, ForceModel, LegacyForceAdapter
from tars.sim.integrators import Derivative, Integrator
from tars.sim.propulsion import (
    DIRECTION_LAWS,
    BurnPlan,
    BurnRejectedError,
    BurnRejection,
    DirectionLaw,
    EngineState,
    EngineTransition,
    InsufficientPropellantPolicy,
    PropulsionSnapshot,
    SpacecraftSpec,
    _describe,
    burn_scalar,
    plan_burn,
    thrust_acceleration,
)
from tars.sim.state import StateSnapshot, Vector, frozen_vector

# Augmented state layout with a spacecraft: y = [r(3), v(3), m_prop, dv_sensed].
_PROP, _DV = 6, 7
_COAST_RATES = np.zeros(2)


def _read_only(arr: NDArray[np.float64]) -> NDArray[np.float64]:
    arr.flags.writeable = False
    return arr


@dataclass(frozen=True)
class AscendingNodeCrossing:
    """Spacecraft crossed the equatorial plane going north (z: - -> +)."""

    crossing_t: float
    tick: int  # first tick at or after the crossing


class AscendingNodeDetector:
    """Detects ascending-node crossings between consecutive steps.

    The crossing time is refined inside the step by finding the root of the cubic
    Hermite interpolant of z(t) built from (z, dz/dt) at both step ends. Its
    interpolation error is O(dt^4), far below the integrator's own error.
    """

    def observe(self, prev: StateSnapshot, curr: StateSnapshot) -> AscendingNodeCrossing | None:
        z0, z1 = float(prev.r[2]), float(curr.r[2])
        if not (z0 < 0.0 <= z1):
            return None
        h = curr.t - prev.t
        s = _hermite_root(z0, float(prev.v[2]) * h, z1, float(curr.v[2]) * h)
        return AscendingNodeCrossing(crossing_t=prev.t + s * h, tick=curr.tick)


def _hermite_root(p0: float, m0: float, p1: float, m1: float) -> float:
    """Root in [0, 1] of the cubic Hermite polynomial with p(0)=p0<0<=p1=p(1).

    m0, m1 are the end slopes with respect to the normalized parameter s.
    Uses safeguarded Newton (falls back to bisection), so it always converges.
    """

    def poly(s: float) -> tuple[float, float]:
        s2, s3 = s * s, s * s * s
        value = (
            (2 * s3 - 3 * s2 + 1) * p0
            + (s3 - 2 * s2 + s) * m0
            + (-2 * s3 + 3 * s2) * p1
            + (s3 - s2) * m1
        )
        slope = (
            (6 * s2 - 6 * s) * p0
            + (3 * s2 - 4 * s + 1) * m0
            + (-6 * s2 + 6 * s) * p1
            + (3 * s2 - 2 * s) * m1
        )
        return value, slope

    lo, hi = 0.0, 1.0
    s = p0 / (p0 - p1)  # linear-interpolation starting guess
    for _ in range(100):
        value, slope = poly(s)
        if value < 0.0:
            lo = s
        else:
            hi = s
        s_new = s - value / slope if slope != 0.0 else 0.5 * (lo + hi)
        if not lo < s_new < hi:
            s_new = 0.5 * (lo + hi)
        if abs(s_new - s) <= 1e-15:
            return s_new
        s = s_new
    return s


@dataclass(frozen=True)
class _ScheduledBurn:
    plan: BurnPlan
    direction: str
    law: DirectionLaw
    propellant_after_kg: float  # analytic remaining propellant once this burn ends
    burn_id: str  # simulator-assigned, deterministic (T3)
    command_id: str | None  # set when scheduled through submit()


class _EngineCursor:
    """Engine schedule being advanced within one tick (local until step() commits)."""

    def __init__(self, active: _ScheduledBurn | None, pending: list[_ScheduledBurn]) -> None:
        self.active = active
        self.pending = pending

    def transitions_at(
        self, t: float, y: NDArray[np.float64], events: list[EngineTransition]
    ) -> NDArray[np.float64]:
        """Apply engine transitions at time t: cutoff first, then ignition."""
        if self.active is not None and self.active.plan.cutoff_t_s == t:
            burn = self.active
            # Propellant floor (SCI-0012): an emptied tank is exactly empty, and
            # integration round-off can never leave it negative.
            floor = 0.0 if burn.propellant_after_kg == 0.0 else max(float(y[_PROP]), 0.0)
            if floor != y[_PROP]:
                y = y.copy()
                y[_PROP] = floor
            events.append(_transition("cutoff", t, burn, y))
            self.active = None
        if self.pending and self.pending[0].plan.ignition_t_s == t:
            self.active = self.pending.pop(0)
            events.append(_transition("ignition", t, self.active, y))
        return y


def _transition(
    kind: str, t: float, burn: _ScheduledBurn, y: NDArray[np.float64]
) -> EngineTransition:
    return EngineTransition(
        kind=kind,
        t=t,
        plan=burn.plan,
        direction=burn.direction,
        r=y[:3],
        v=y[3:6],
        propellant_kg=float(y[_PROP]),
        delta_v_sensed_mps=float(y[_DV]),
        end_cause=burn.plan.end_cause if kind == "cutoff" else None,
        burn_id=burn.burn_id,
        command_id=burn.command_id,
    )


class Simulator:
    """Fixed-step propagation of one spacecraft's translational state.

    Without a spacecraft the state is y = [r, v], and stepping is exactly the M1 path.
    With a spacecraft, y = [r, v, m_prop, dv_sensed]. Ticks containing an engine
    event are integrated as consecutive RK4 sub-steps split at the exact event times
    (DR-0013 3A); time stays ``tick * dt``.
    """

    def __init__(
        self,
        r0: Vector,
        v0: Vector,
        force_model: ForceModel,
        integrator: Integrator,
        dt: float,
        detectors: Sequence[AscendingNodeDetector] = (),
        spacecraft: SpacecraftSpec | None = None,
    ) -> None:
        if not dt > 0.0:
            raise ValueError("dt must be positive")
        if spacecraft is not None and not isinstance(spacecraft, SpacecraftSpec):
            raise TypeError("spacecraft must be a SpacecraftSpec")
        self._force_model = force_model
        self._integrator = integrator
        self._dt = float(dt)
        self._detectors = tuple(detectors)
        self._tick = 0
        self._spacecraft = spacecraft
        self._engine_events: tuple[EngineTransition, ...] = ()
        self._pending: list[_ScheduledBurn] = []
        self._active: _ScheduledBurn | None = None
        self._burn_count = 0  # accepted burns; source of deterministic burn IDs
        self._used_command_ids: set[str] = set()  # IDs of accepted commands
        state = [frozen_vector(r0), frozen_vector(v0)]
        if spacecraft is not None:
            state.append(np.array([spacecraft.tank.propellant_kg, 0.0]))
            self._committed_propellant_kg = spacecraft.tank.propellant_kg
        self._y: NDArray[np.float64] = _read_only(np.concatenate(state))

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def t(self) -> float:
        # Time from the integer tick counter, never accumulated (ADR-0002).
        return self._tick * self._dt

    @property
    def engine_transitions(self) -> tuple[EngineTransition, ...]:
        """Engine ignitions and cutoffs that occurred during the last ``step()``."""
        return self._engine_events

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(tick=self._tick, t=self.t, r=self._y[:3], v=self._y[3:6])

    def propulsion_snapshot(self) -> PropulsionSnapshot | None:
        if self._spacecraft is None:
            return None
        if self._active is not None:
            state = EngineState.BURNING
        elif self._pending:
            state = EngineState.SCHEDULED
        else:
            state = EngineState.IDLE
        propellant = float(self._y[_PROP])
        return PropulsionSnapshot(
            tick=self._tick,
            t=self.t,
            propellant_kg=propellant,
            total_mass_kg=self._spacecraft.dry_mass_kg + propellant,
            delta_v_sensed_mps=float(self._y[_DV]),
            engine_state=state,
            active_plan=None if self._active is None else self._active.plan,
            pending_plans=tuple(b.plan for b in self._pending),
            active_burn_id=None if self._active is None else self._active.burn_id,
            active_direction=None if self._active is None else self._active.direction,
            pending_burn_ids=tuple(b.burn_id for b in self._pending),
        )

    # ------------------------------------------------------------------ commands

    def schedule_burn(
        self,
        direction: str,
        ignition_t_s: float,
        duration_s: float,
        policy: InsufficientPropellantPolicy | str = InsufficientPropellantPolicy.REJECT,
    ) -> BurnPlan:
        """Validate and schedule one burn; the engine-level command entry point.

        T2 interface, unchanged. Burns scheduled here have ``command_id = None``; command
        correlation exists only through ``submit()`` (review REV-T3-05). Every accepted
        burn receives a deterministic simulator-assigned burn ID (``burn#000001``, ...).

        It never changes r, v, mass or propellant; only the engine schedule. There
        is one engine, and burns execute in submission order: a new burn may not
        ignite before the cutoff of any burn already scheduled or in progress
        (``engine_busy`` if that is the active burn, else
        ``overlaps_scheduled_burn``). Propellant sufficiency is checked against the
        propellant left after every burn already accepted.

        Raises:
            BurnRejectedError: with a DR-0014 reason code; the schedule is unchanged.
        """
        return self._schedule(direction, ignition_t_s, duration_s, policy, command_id=None)

    def _schedule(
        self,
        direction: str,
        ignition_t_s: float,
        duration_s: float,
        policy: InsufficientPropellantPolicy | str,
        command_id: str | None,
    ) -> BurnPlan:
        if self._spacecraft is None:
            raise BurnRejectedError(
                BurnRejection.NO_PROPULSION_CONFIGURED, "simulator has no spacecraft"
            )
        if not isinstance(direction, str) or direction not in DIRECTION_LAWS:
            raise BurnRejectedError(
                BurnRejection.SCHEMA_INVALID, f"unknown direction {direction!r}"
            )
        # Schema first (DR-0014 amendment): type and finiteness precede chronology
        # and engine-conflict checks (REV-T2-02).
        ignition = burn_scalar("ignition_t_s", ignition_t_s)
        duration = burn_scalar("duration_s", duration_s)
        try:
            policy = InsufficientPropellantPolicy(policy)
        except ValueError:
            raise BurnRejectedError(
                BurnRejection.SCHEMA_INVALID, f"unknown policy {_describe(policy)}"
            ) from None
        # Precedence (stable, documented): schema; command-intrinsic (duration);
        # chronology; engine conflicts; then propellant and schedulability (plan_burn).
        if not duration > 0.0:
            raise BurnRejectedError(
                BurnRejection.NON_POSITIVE_DURATION, f"duration_s = {duration!r}"
            )
        if ignition < self.t:
            raise BurnRejectedError(
                BurnRejection.IGNITION_IN_PAST, f"ignition {ignition!r} < now {self.t!r}"
            )
        last = self._pending[-1] if self._pending else self._active
        if last is not None and ignition < last.plan.cutoff_t_s:
            if self._active is not None and ignition < self._active.plan.cutoff_t_s:
                raise BurnRejectedError(
                    BurnRejection.ENGINE_BUSY,
                    f"engine burning until {self._active.plan.cutoff_t_s!r}",
                )
            raise BurnRejectedError(
                BurnRejection.OVERLAPS_SCHEDULED_BURN,
                f"ignition {ignition!r} before scheduled cutoff {last.plan.cutoff_t_s!r}",
            )
        plan = plan_burn(
            self._spacecraft.engine,
            self._committed_propellant_kg,
            ignition,
            duration,
            policy=policy,
            earliest_t_s=self.t,
            dry_mass_kg=self._spacecraft.dry_mass_kg,
        )
        if plan.propellant_used_kg >= self._committed_propellant_kg:
            after = 0.0  # tank exactly empty at cutoff (SCI-0012)
        else:
            after = self._committed_propellant_kg - plan.propellant_used_kg
        self._burn_count += 1
        burn_id = f"burn#{self._burn_count:06d}"
        self._pending.append(
            _ScheduledBurn(plan, direction, DIRECTION_LAWS[direction], after, burn_id, command_id)
        )
        self._committed_propellant_kg = after
        return plan

    def submit(self, command: BurnCommand | dict) -> CommandReceipt:
        """Validate a BurnCommand (or raw mapping) and schedule it (DR-0014; T3).

        Never raises for a bad command: the receipt carries an approved reason code.
        A rejected command changes nothing, including the command-ID registry
        (REV-T3-01). Every submission, including model instances, is re-validated into
        a fresh canonical command (REV-T3-02). Precedence: schema
        (``schema_invalid``), duplicate ID (``duplicate_command_id``, i.e. an ID
        already used by an accepted command), then every ``schedule_burn`` rule.
        """
        tick, t = self._tick, self.t
        try:
            cmd = parse_command(command)
        except ValidationError as err:
            return self._schema_rejection(command, schema_errors(err), tick, t)
        except PayloadTypeError as err:
            return self._schema_rejection(command, err.errors, tick, t)
        except Exception:  # hostile payload object; process-control exceptions propagate
            return self._schema_rejection(command, ("<payload>: unprocessable",), tick, t)

        def rejected(reason: BurnRejection, detail: str) -> CommandReceipt:
            return CommandReceipt(
                status=CommandStatus.REJECTED,
                command_id=cmd.command_id,
                issuer=cmd.issuer,
                command=cmd,
                reason=reason,
                detail=safe_text(detail, 400),
                burn_id=None,
                plan=None,
                tick=tick,
                t=t,
            )

        if cmd.command_id in self._used_command_ids:
            return rejected(
                BurnRejection.DUPLICATE_COMMAND_ID,
                f"command_id {cmd.command_id!r} already used by an accepted command",
            )
        try:
            plan = self._schedule(
                cmd.direction,
                cmd.ignition_t_s,
                cmd.duration_s,
                cmd.on_insufficient_propellant,
                command_id=cmd.command_id,
            )
        except BurnRejectedError as err:
            return rejected(err.reason, err.detail)
        self._used_command_ids.add(cmd.command_id)  # consumed only on acceptance
        return CommandReceipt(
            status=CommandStatus.ACCEPTED,
            command_id=cmd.command_id,
            issuer=cmd.issuer,
            command=cmd,
            reason=None,
            detail="accepted",
            burn_id=self._pending[-1].burn_id,
            plan=plan,
            tick=tick,
            t=t,
        )

    @staticmethod
    def _schema_rejection(
        payload: object, errors: tuple[str, ...], tick: int, t: float
    ) -> CommandReceipt:
        def echo(name: str) -> str | None:
            try:
                return readable_field(payload, name) if type(payload) is dict else None
            except Exception:  # never let diagnostics escape (re-verification N2)
                return None

        return CommandReceipt(
            status=CommandStatus.REJECTED,
            command_id=echo("command_id"),
            issuer=echo("issuer"),
            command=None,
            reason=BurnRejection.SCHEMA_INVALID,
            detail="; ".join(errors),
            burn_id=None,
            plan=None,
            tick=tick,
            t=t,
            schema_errors=errors,
        )

    def _derivative(self, t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
        r, v = y[:3], y[3:]
        # No spacecraft: the context carries no mass (I-40 OD-4).
        model = LegacyForceAdapter(self._force_model)
        return np.concatenate([v, model.acceleration(t, r, v, ForceContext())])

    def _powered_derivative(self, burn: _ScheduledBurn | None) -> Derivative:
        """RHS for y = [r, v, m_prop, dv_sensed] with the engine off or on."""
        spacecraft = self._spacecraft
        assert spacecraft is not None
        force_model = LegacyForceAdapter(self._force_model)

        if burn is None:

            def coast(t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
                r, v = y[:3], y[3:6]
                # Stage mass, validated only when a model reads it (I-41): a coast stage of
                # infinite length carries NaN propellant and must fail as before. The stored
                # element is read through the base-class indexer, so a float64 ndarray subclass
                # (masked or otherwise) cannot warn or raise here, and the context owns a
                # binary64 snapshot instead of a reference to the stage (I-44, U-1).
                prop = float(np.ndarray.__getitem__(y, _PROP))
                ctx = ForceContext.deferred(spacecraft.dry_mass_kg + max(prop, 0.0))
                return np.concatenate([v, force_model.acceleration(t, r, v, ctx), _COAST_RATES])

            return coast

        engine, law, mdot = spacecraft.engine, burn.law, burn.plan.mass_flow_kgps

        def powered(t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
            if not np.all(np.isfinite(y)):
                # A diverging RK4 stage must fail as on the coast path (non-finite
                # state), not as a ValueError from the pointing law (T4 finding).
                raise FloatingPointError(f"non-finite state during a burn at t = {t!r}")
            r, v = y[:3], y[3:6]
            # RK4 stages near depletion can carry ~1e-17 kg of negative round-off;
            # the dynamics use the physical, non-negative propellant (review N4).
            mass = spacecraft.dry_mass_kg + max(float(y[_PROP]), 0.0)
            if not math.isfinite(engine.thrust_n / mass):  # F/m overflows (K4)
                raise FloatingPointError(f"thrust acceleration overflows at t = {t!r}")
            thrust = thrust_acceleration(engine, law.direction(t, r, v), mass)
            a = force_model.acceleration(t, r, v, ForceContext(mass)) + thrust
            return np.concatenate([v, a, [-mdot, engine.thrust_n / mass]])

        return powered

    def step(self) -> list[AscendingNodeCrossing]:
        """Advance one tick atomically; return detections that occurred during the step.

        If integration fails, nothing changes: not the state, the tick, the engine
        schedule or the recorded transitions (REV-T2-01).
        """
        prev = self.snapshot()
        try:
            if self._spacecraft is None:
                y_next = self._integrator.step(self._derivative, prev.t, self._y, self._dt)
                engine = (self._active, self._pending, ())
            else:
                y_next, engine = self._step_with_propulsion(prev.t)
        except (OverflowError, ZeroDivisionError) as err:
            # Python float arithmetic raises where NumPy would return inf: the same
            # numerical failure, reported the same way (T4 re-verification 3, K1).
            raise FloatingPointError(f"numerical overflow at tick {self._tick + 1}: {err}") from err
        self._require_finite(y_next)
        # Commit point. Read-only so no force model can mutate simulator-owned state
        # through the r/v views it receives (REV-004); only step() replaces the state.
        self._y = _read_only(y_next)
        self._active, self._pending, self._engine_events = engine
        self._tick += 1
        curr = self.snapshot()
        detections = []
        for detector in self._detectors:
            found = detector.observe(prev, curr)
            if found is not None:
                detections.append(found)
        return detections

    def _step_with_propulsion(
        self, t0: float
    ) -> tuple[NDArray[np.float64], tuple[_ScheduledBurn | None, list[_ScheduledBurn], tuple]]:
        """Integrate one tick on local copies of the engine schedule (nothing is
        committed here; step() commits the result only if integration succeeded)."""
        t1 = (self._tick + 1) * self._dt
        events: list[EngineTransition] = []
        engine = _EngineCursor(self._active, list(self._pending))
        y = engine.transitions_at(t0, self._y, events)
        burns = [*engine.pending, *([engine.active] if engine.active else [])]
        inside = sorted(
            {t for b in burns for t in (b.plan.ignition_t_s, b.plan.cutoff_t_s) if t0 < t < t1}
        )
        if not inside:
            # No engine event in this tick: one full step of exactly dt, as in M1.
            y = self._integrator.step(self._powered_derivative(engine.active), t0, y, self._dt)
            self._require_finite(y)
            y = engine.transitions_at(t1, y, events)
        else:
            for a, b in pairwise([t0, *inside, t1]):
                y = self._integrator.step(self._powered_derivative(engine.active), a, y, b - a)
                self._require_finite(y)
                y = engine.transitions_at(b, y, events)
        return y, (engine.active, engine.pending, tuple(events))

    def _require_finite(self, y: NDArray[np.float64]) -> None:
        """The state and its magnitudes |r|, |v| must be finite.

        A state whose components are finite but whose norm overflows cannot be used by
        gravity, telemetry or events, so it is a numerical failure too (K3).
        """
        if not (
            np.all(np.isfinite(y))
            and math.isfinite(np.linalg.norm(y[:3]))
            and math.isfinite(np.linalg.norm(y[3:6]))
        ):
            raise FloatingPointError(f"non-finite state produced at tick {self._tick + 1}")
