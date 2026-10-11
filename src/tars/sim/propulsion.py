"""Standalone propulsion model (ADR-0007; DR-0011, DR-0012, DR-0014).

Ideal chemical engine (SCI-0008..SCI-0012):

- constant thrust F [N] and specific impulse Isp [s] while the engine is on;
- effective exhaust velocity c = Isp * g0, with g0 the exact standard gravity
  (SCI-0009);
- mass flow mdot = F / c, so propellant falls linearly in time;
- thrust acceleration a = F / m along a unit direction, where m = dry + propellant.
  There is no mdot*v term (SCI-0010).

Every number here is a configurable input (DR-0010). The module holds no engine
or vehicle values. A ``BurnPlan`` is computed exactly in advance: ignition,
cutoff, and depletion times are known before integration, so the simulator can
split RK4 steps at them (DR-0013, task T2). This module never touches simulator
state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from numbers import Real
from typing import Protocol

import numpy as np

from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.state import Vector

# A direction law must return a unit vector; allow only round-off in its norm.
_UNIT_NORM_TOLERANCE = 1e-12

# Largest accepted difference between a burn's intended duration and the interval
# that float64 event times can represent, cutoff - ignition (REV-T2-03). 1 us is the
# stop-time granularity GMAT and STK use (GMAT TIME_ROUNDOFF; VAL-0010). For the
# reference engine its delta-v effect, a * 1 us ~ 4e-7 m/s, is below the burn's own
# integration error (1.2e-6 m/s at dt = 10 s, VAL-0008). Float64 time keeps
# sub-microsecond resolution for t < 2**33 s (~272 years).
EVENT_TIME_RESOLUTION_S = 1.0e-6


class PropulsionSpecError(ValueError):
    """Invalid engine, tank, or spacecraft configuration."""


def _require_real(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise PropulsionSpecError(f"{name} must be a real number, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise PropulsionSpecError(f"{name} must be finite, got {value!r}")
    return value


def _require_positive(name: str, value: object) -> float:
    value = _require_real(name, value)
    if not value > 0.0:
        raise PropulsionSpecError(f"{name} must be positive, got {value!r}")
    return value


@dataclass(frozen=True)
class EngineSpec:
    """Ideal constant-thrust, constant-Isp engine (SCI-0008).

    Attributes:
        thrust_n: Vacuum thrust F [N].
        isp_s: Vacuum specific impulse [s].
    """

    thrust_n: float
    isp_s: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "thrust_n", _require_positive("thrust_n", self.thrust_n))
        object.__setattr__(self, "isp_s", _require_positive("isp_s", self.isp_s))
        # Finite inputs can still overflow or underflow the derived physics (REV-T1-02).
        _require_positive("exhaust velocity Isp*g0", self.exhaust_velocity_mps)
        _require_positive("mass flow F/(Isp*g0)", self.mass_flow_kgps)

    @property
    def exhaust_velocity_mps(self) -> float:
        """Effective exhaust velocity c = Isp * g0 [m/s] (SCI-0009)."""
        return self.isp_s * STANDARD_GRAVITY

    @property
    def mass_flow_kgps(self) -> float:
        """Propellant mass flow mdot = F / (Isp * g0) [kg/s] while the engine is on."""
        return self.thrust_n / self.exhaust_velocity_mps


@dataclass(frozen=True)
class TankSpec:
    """Single tank; all loaded propellant is usable (SCI-0012)."""

    propellant_kg: float

    def __post_init__(self) -> None:
        value = _require_real("propellant_kg", self.propellant_kg)
        if value < 0.0:
            raise PropulsionSpecError(f"propellant_kg must be >= 0, got {value!r}")
        object.__setattr__(self, "propellant_kg", value)


@dataclass(frozen=True)
class SpacecraftSpec:
    """Spacecraft mass properties and propulsion hardware (DR-0010 reference-case inputs)."""

    dry_mass_kg: float
    engine: EngineSpec
    tank: TankSpec

    def __post_init__(self) -> None:
        object.__setattr__(self, "dry_mass_kg", _require_positive("dry_mass_kg", self.dry_mass_kg))
        if not isinstance(self.engine, EngineSpec) or not isinstance(self.tank, TankSpec):
            raise PropulsionSpecError("engine and tank must be EngineSpec and TankSpec")
        _require_positive("initial mass dry + propellant", self.initial_mass_kg)

    @property
    def initial_mass_kg(self) -> float:
        return self.dry_mass_kg + self.tank.propellant_kg


def thrust_acceleration(engine: EngineSpec, direction: object, total_mass_kg: float) -> Vector:
    """Thrust acceleration a = (F / m) u_hat [m/s^2] (SCI-0010), returned read-only.

    Raises ValueError (never TypeError) for a mass that is not a finite positive real,
    a direction that is not a finite 3-vector of unit length, or a result that
    overflows (REV-T1-06).
    """
    mass = _require_positive("total mass", total_mass_kg)
    u = np.asarray(direction, dtype=np.float64)
    if u.shape != (3,) or not np.all(np.isfinite(u)):
        raise ValueError("thrust direction must be a finite 3-vector")
    if abs(float(np.linalg.norm(u)) - 1.0) > _UNIT_NORM_TOLERANCE:
        raise ValueError("thrust direction must be a unit vector")
    magnitude = engine.thrust_n / mass
    if not math.isfinite(magnitude):
        raise ValueError(f"thrust acceleration F/m overflows for mass {mass!r}")
    a = magnitude * u
    a.flags.writeable = False
    return a


def rocket_equation_delta_v(exhaust_velocity_mps: float, m0_kg: float, mf_kg: float) -> float:
    """Ideal (thrust-only) velocity change c ln(m0/mf) [m/s]: the Tsiolkovsky equation.

    It holds for any pointing history and any gravity field, so it is an exact oracle
    for the integrated thrust acceleration (DR-0015 O2).

    Evaluated as c log1p((m0 - mf)/mf). This stays accurate for tiny mass changes,
    where m0/mf would round to 1 + ulp. If the ratio overflows it falls back to
    c (ln m0 - ln mf), so wide ratios stay finite (REV-T1-04).
    """
    c = _require_positive("exhaust velocity", exhaust_velocity_mps)
    m0 = _require_positive("m0", m0_kg)
    mf = _require_positive("mf", mf_kg)
    if mf > m0:
        raise ValueError("require m0 >= mf")
    excess = (m0 - mf) / mf
    log_ratio = math.log1p(excess) if math.isfinite(excess) else math.log(m0) - math.log(mf)
    dv = c * log_ratio
    if not math.isfinite(dv):
        raise ValueError("delta-v overflows")
    return dv


# ------------------------------------------------------------------- direction laws


class DirectionLaw(Protocol):
    """Unit thrust direction (ECI) as a function of read-only (t, r, v) (DR-0012).

    The M2 modes are prograde and retrograde. Future guidance modes add
    implementations without changing the propulsion model or the command path.
    """

    name: str

    def direction(self, t: float, r: Vector, v: Vector) -> Vector: ...


def _velocity_unit(v: Vector) -> Vector:
    """v/|v| as a new array, never aliasing the caller's state.

    The vector is pre-scaled by its largest component so |v| cannot overflow or
    underflow for any finite, nonzero 3-vector (REV-T1-06).
    """
    v = np.asarray(v, dtype=np.float64)
    if v.shape != (3,) or not np.all(np.isfinite(v)):
        raise ValueError("velocity-tracking direction needs a finite 3-vector velocity")
    scale = float(np.max(np.abs(v)))
    if scale == 0.0:
        raise ValueError("velocity-tracking direction is undefined for zero velocity")
    w = v / scale
    return w / float(np.linalg.norm(w))


class Prograde:
    """+V of the Earth-centred VNB frame: u = v/|v| (inertial velocity; SCI-0011)."""

    name = "prograde"

    def direction(self, t: float, r: Vector, v: Vector) -> Vector:
        u = _velocity_unit(v)
        u.flags.writeable = False
        return u


class Retrograde:
    """-V of the Earth-centred VNB frame: u = -v/|v|."""

    name = "retrograde"

    def direction(self, t: float, r: Vector, v: Vector) -> Vector:
        u = -_velocity_unit(v)
        u.flags.writeable = False
        return u


DIRECTION_LAWS: dict[str, DirectionLaw] = {law.name: law for law in (Prograde(), Retrograde())}


# ------------------------------------------------------------------------ burn plans


class InsufficientPropellantPolicy(StrEnum):
    """What a burn does when it needs more propellant than is loaded (DR-0014 3C)."""

    REJECT = "reject"
    BURN_TO_DEPLETION = "burn_to_depletion"


class BurnRejection(StrEnum):
    """Stable reason codes; a subset of the DR-0014 vocabulary (incl. 2026-10-10 amendment).

    ``SCHEMA_INVALID``: non-real/non-finite numbers, unknown enums, malformed values.
    ``BURN_UNSCHEDULABLE``: a structurally valid burn that has no exact, representable
    plan (cutoff not finite or not after ignition; consumption underflows).
    """

    SCHEMA_INVALID = "schema_invalid"
    BURN_UNSCHEDULABLE = "burn_unschedulable"
    NON_POSITIVE_DURATION = "non_positive_duration"
    IGNITION_IN_PAST = "ignition_in_past"
    NO_PROPELLANT = "no_propellant"
    INSUFFICIENT_PROPELLANT = "insufficient_propellant"
    OVERLAPS_SCHEDULED_BURN = "overlaps_scheduled_burn"
    ENGINE_BUSY = "engine_busy"
    NO_PROPULSION_CONFIGURED = "no_propulsion_configured"


class BurnRejectedError(ValueError):
    """A burn that cannot be planned; ``reason`` is machine-readable."""

    def __init__(self, reason: BurnRejection, detail: str) -> None:
        super().__init__(f"{reason.value}: {detail}")
        self.reason = reason
        self.detail = detail


class BurnEndCause(StrEnum):
    COMPLETED = "completed"
    PROPELLANT_DEPLETED = "propellant_depleted"


@dataclass(frozen=True)
class BurnPlan:
    """Exact schedule of one burn, computed before integration.

    Attributes:
        ignition_t_s: Engine-on time [s since epoch].
        commanded_duration_s: Duration requested by the command [s].
        burn_duration_s: Interval the engine actually runs, cutoff - ignition [s], as
            represented by float64 event times. It equals the commanded duration to
            within ``EVENT_TIME_RESOLUTION_S``; it is shorter only for
            ``PROPELLANT_DEPLETED``.
        cutoff_t_s: Engine-off time, ignition + burn duration [s].
        propellant_used_kg: Propellant consumed [kg]. Equals the loaded amount exactly
            on depletion, so propellant never goes negative.
        mass_flow_kgps: Mass flow while burning [kg/s].
        end_cause: How the burn ends.
    """

    ignition_t_s: float
    commanded_duration_s: float
    burn_duration_s: float
    cutoff_t_s: float
    propellant_used_kg: float
    mass_flow_kgps: float
    end_cause: BurnEndCause
    policy: InsufficientPropellantPolicy = field(default=InsufficientPropellantPolicy.REJECT)

    def propellant_used_by(self, t: float) -> float:
        """Analytic cumulative propellant used at time ``t`` [kg] (oracle O1)."""
        if t <= self.ignition_t_s:
            return 0.0
        if t >= self.cutoff_t_s:
            return self.propellant_used_kg
        return min(self.mass_flow_kgps * (t - self.ignition_t_s), self.propellant_used_kg)


def burn_scalar(name: str, value: object) -> float:
    """Validate one numeric burn input and normalize it to float64 (DR-0014 amendment).

    Non-real values (bool, str, None, arrays, numpy bools), non-finite values and
    values that overflow float64 (e.g. 10**1000) are ``schema_invalid``.
    """
    if isinstance(value, bool) or not isinstance(value, Real):
        raise BurnRejectedError(BurnRejection.SCHEMA_INVALID, f"{name} must be real, got {value!r}")
    try:
        number = float(value)
    except (OverflowError, ValueError, TypeError):
        number = math.nan
    if not math.isfinite(number):
        raise BurnRejectedError(
            BurnRejection.SCHEMA_INVALID, f"{name} must be finite, got {value!r}"
        )
    return number


def plan_burn(
    engine: EngineSpec,
    propellant_kg: float,
    ignition_t_s: float,
    duration_s: float,
    policy: InsufficientPropellantPolicy | str = InsufficientPropellantPolicy.REJECT,
    earliest_t_s: float = 0.0,
) -> BurnPlan:
    """Validate a duration-based burn and compute its exact schedule (DR-0014 1A, 2A, 3C).

    Sufficiency is decided in the time domain against the depletion time
    t_dep = fl(propellant / mdot). A burn is sufficient iff duration <= t_dep, and its
    consumption is clamped to the loaded propellant. A burn one ulp longer is
    insufficient. This rule is exact, not a tolerance (REV-T1-03).

    Raises:
        BurnRejectedError: with a machine-readable reason. No plan exists for a
            rejected burn.
    """
    # All arithmetic below is float64, whatever scalar type was passed (REV-T1-01).
    propellant_kg = burn_scalar("propellant_kg", propellant_kg)
    ignition_t_s = burn_scalar("ignition_t_s", ignition_t_s)
    duration_s = burn_scalar("duration_s", duration_s)
    earliest_t_s = burn_scalar("earliest_t_s", earliest_t_s)
    if propellant_kg < 0.0:
        raise BurnRejectedError(BurnRejection.SCHEMA_INVALID, "propellant_kg must be >= 0")
    try:
        policy = InsufficientPropellantPolicy(policy)
    except ValueError:
        raise BurnRejectedError(
            BurnRejection.SCHEMA_INVALID, f"unknown policy {policy!r}"
        ) from None
    if not duration_s > 0.0:
        raise BurnRejectedError(BurnRejection.NON_POSITIVE_DURATION, f"duration_s = {duration_s!r}")
    if ignition_t_s < earliest_t_s:
        raise BurnRejectedError(
            BurnRejection.IGNITION_IN_PAST, f"ignition {ignition_t_s!r} < {earliest_t_s!r}"
        )
    if propellant_kg == 0.0:
        raise BurnRejectedError(BurnRejection.NO_PROPELLANT, "tank is empty")

    mdot = engine.mass_flow_kgps
    depletion_s = propellant_kg / mdot
    if duration_s <= depletion_s:
        burn, cause = duration_s, BurnEndCause.COMPLETED
        used = min(mdot * duration_s, propellant_kg)
    elif policy is InsufficientPropellantPolicy.REJECT:
        raise BurnRejectedError(
            BurnRejection.INSUFFICIENT_PROPELLANT,
            f"duration {duration_s!r} s exceeds depletion time {depletion_s!r} s "
            f"({propellant_kg!r} kg loaded)",
        )
    else:
        # Flame-out at the exact depletion time (SCI-0012).
        burn, used, cause = depletion_s, propellant_kg, BurnEndCause.PROPELLANT_DEPLETED

    # Step splitting needs a finite cutoff strictly after ignition (DR-0013, REV-T1-01).
    cutoff_s = ignition_t_s + burn
    if not (math.isfinite(cutoff_s) and cutoff_s > ignition_t_s):
        raise BurnRejectedError(
            BurnRejection.BURN_UNSCHEDULABLE,
            f"cutoff {cutoff_s!r} is not representable after ignition {ignition_t_s!r}",
        )
    # The simulator integrates exactly the represented interval, so the plan describes
    # that interval and its consumption (REV-T2-03).
    represented = cutoff_s - ignition_t_s
    if abs(represented - burn) > EVENT_TIME_RESOLUTION_S:
        raise BurnRejectedError(
            BurnRejection.BURN_UNSCHEDULABLE,
            f"event times represent {represented!r} s for a {burn!r} s burn at t = "
            f"{ignition_t_s!r} (resolution limit {EVENT_TIME_RESOLUTION_S} s)",
        )
    burn = represented
    if cause is BurnEndCause.COMPLETED:
        used = min(mdot * burn, propellant_kg)
    # A burn with thrust must consume propellant; mdot*duration can underflow (N1).
    if not used > 0.0:
        raise BurnRejectedError(
            BurnRejection.BURN_UNSCHEDULABLE,
            f"propellant consumption {used!r} kg is not representable for this burn",
        )
    return BurnPlan(
        ignition_t_s=ignition_t_s,
        commanded_duration_s=duration_s,
        burn_duration_s=burn,
        cutoff_t_s=cutoff_s,
        propellant_used_kg=used,
        mass_flow_kgps=mdot,
        end_cause=cause,
        policy=policy,
    )


# ------------------------------------------------------- simulator-facing state views


class EngineState(StrEnum):
    """Engine state machine: IDLE -> SCHEDULED -> BURNING -> IDLE (or SCHEDULED)."""

    IDLE = "idle"
    SCHEDULED = "scheduled"
    BURNING = "burning"


@dataclass(frozen=True)
class PropulsionSnapshot:
    """Read-only view of simulator-owned propulsion state at the end of a tick.

    Attributes:
        tick: Integer step counter.
        t: Elapsed time [s].
        propellant_kg: Propellant remaining (integrated state; never negative).
        total_mass_kg: Dry mass plus propellant.
        delta_v_sensed_mps: Cumulative ideal-accelerometer delta-v (integral of F/m)
            since the start of the simulation [m/s].
        engine_state: Current engine state.
        active_plan: The burn in progress, if any.
        pending_plans: Accepted burns not yet ignited, in execution order.
    """

    tick: int
    t: float
    propellant_kg: float
    total_mass_kg: float
    delta_v_sensed_mps: float
    engine_state: EngineState
    active_plan: BurnPlan | None
    pending_plans: tuple[BurnPlan, ...]


@dataclass(frozen=True)
class EngineTransition:
    """An engine event at its exact time, which may lie inside a tick (DR-0013 3A).

    The state is the integrated state at ``t``, the boundary of an RK4 sub-step.
    T3 maps these to BurnStarted / BurnEnded events.
    """

    kind: str  # "ignition" | "cutoff"
    t: float
    plan: BurnPlan
    direction: str
    r: Vector
    v: Vector
    propellant_kg: float
    delta_v_sensed_mps: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "r", _frozen3(self.r))
        object.__setattr__(self, "v", _frozen3(self.v))


def _frozen3(values: object) -> Vector:
    """Read-only copy backed by immutable bytes: the writeable flag cannot be
    re-enabled, so retained event evidence cannot be rewritten (REV-T2-04)."""
    data = np.asarray(values, dtype=np.float64)
    if data.shape != (3,):
        raise ValueError(f"expected a 3-vector, got shape {data.shape}")
    return np.frombuffer(data.tobytes(), dtype=np.float64)
