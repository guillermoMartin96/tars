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

    @property
    def initial_mass_kg(self) -> float:
        return self.dry_mass_kg + self.tank.propellant_kg


def thrust_acceleration(engine: EngineSpec, direction: object, total_mass_kg: float) -> Vector:
    """Thrust acceleration a = (F / m) u_hat [m/s^2] (SCI-0010), returned read-only.

    Raises ValueError for a non-positive or non-finite mass, or a direction that is
    not a finite 3-vector of unit length.
    """
    if not (math.isfinite(total_mass_kg) and total_mass_kg > 0.0):
        raise ValueError(f"total mass must be finite and positive, got {total_mass_kg!r}")
    u = np.asarray(direction, dtype=np.float64)
    if u.shape != (3,) or not np.all(np.isfinite(u)):
        raise ValueError("thrust direction must be a finite 3-vector")
    if abs(float(np.linalg.norm(u)) - 1.0) > _UNIT_NORM_TOLERANCE:
        raise ValueError("thrust direction must be a unit vector")
    a = (engine.thrust_n / total_mass_kg) * u
    a.flags.writeable = False
    return a


def rocket_equation_delta_v(exhaust_velocity_mps: float, m0_kg: float, mf_kg: float) -> float:
    """Ideal (thrust-only) velocity change c ln(m0/mf) [m/s]: the Tsiolkovsky equation.

    It holds for any pointing history and any gravity field, so it is an exact oracle
    for the integrated thrust acceleration (DR-0015 O2).
    """
    values = (exhaust_velocity_mps, m0_kg, mf_kg)
    if not all(math.isfinite(x) and x > 0.0 for x in values) or mf_kg > m0_kg:
        raise ValueError("require finite c > 0 and m0 >= mf > 0")
    return exhaust_velocity_mps * math.log(m0_kg / mf_kg)


# ------------------------------------------------------------------- direction laws


class DirectionLaw(Protocol):
    """Unit thrust direction (ECI) as a function of read-only (t, r, v) (DR-0012).

    The M2 modes are prograde and retrograde. Future guidance modes add
    implementations without changing the propulsion model or the command path.
    """

    name: str

    def direction(self, t: float, r: Vector, v: Vector) -> Vector: ...


def _velocity_unit(v: Vector) -> Vector:
    v = np.asarray(v, dtype=np.float64)
    speed = float(np.linalg.norm(v))
    if not (math.isfinite(speed) and speed > 0.0):
        raise ValueError("velocity-tracking direction needs a finite, nonzero velocity")
    return v / speed  # new array; never aliases the caller's state


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
    """Stable reason codes; a subset of the DR-0014 command vocabulary."""

    INVALID_INPUT = "invalid_input"
    NON_POSITIVE_DURATION = "non_positive_duration"
    IGNITION_IN_PAST = "ignition_in_past"
    NO_PROPELLANT = "no_propellant"
    INSUFFICIENT_PROPELLANT = "insufficient_propellant"


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
        burn_duration_s: Duration the engine actually runs [s]. It is shorter than
            commanded only for ``PROPELLANT_DEPLETED``.
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


def plan_burn(
    engine: EngineSpec,
    propellant_kg: float,
    ignition_t_s: float,
    duration_s: float,
    policy: InsufficientPropellantPolicy | str = InsufficientPropellantPolicy.REJECT,
    earliest_t_s: float = 0.0,
) -> BurnPlan:
    """Validate a duration-based burn and compute its exact schedule (DR-0014 1A, 2A, 3C).

    Raises:
        BurnRejected: with a machine-readable reason. No plan exists for a rejected burn.
    """
    numbers = {
        "propellant_kg": propellant_kg,
        "ignition_t_s": ignition_t_s,
        "duration_s": duration_s,
        "earliest_t_s": earliest_t_s,
    }
    for name, value in numbers.items():
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise BurnRejectedError(
                BurnRejection.INVALID_INPUT, f"{name} must be finite, got {value!r}"
            )
    if propellant_kg < 0.0:
        raise BurnRejectedError(BurnRejection.INVALID_INPUT, "propellant_kg must be >= 0")
    try:
        policy = InsufficientPropellantPolicy(policy)
    except ValueError:
        raise BurnRejectedError(BurnRejection.INVALID_INPUT, f"unknown policy {policy!r}") from None
    if not duration_s > 0.0:
        raise BurnRejectedError(BurnRejection.NON_POSITIVE_DURATION, f"duration_s = {duration_s!r}")
    if ignition_t_s < earliest_t_s:
        raise BurnRejectedError(
            BurnRejection.IGNITION_IN_PAST, f"ignition {ignition_t_s!r} < {earliest_t_s!r}"
        )
    if propellant_kg == 0.0:
        raise BurnRejectedError(BurnRejection.NO_PROPELLANT, "tank is empty")

    mdot = engine.mass_flow_kgps
    required = mdot * duration_s
    if required <= propellant_kg:
        burn, used, cause = duration_s, required, BurnEndCause.COMPLETED
    elif policy is InsufficientPropellantPolicy.REJECT:
        raise BurnRejectedError(
            BurnRejection.INSUFFICIENT_PROPELLANT,
            f"needs {required!r} kg, {propellant_kg!r} kg loaded",
        )
    else:
        # Flame-out at the exact depletion time (SCI-0012).
        burn, used, cause = propellant_kg / mdot, propellant_kg, BurnEndCause.PROPELLANT_DEPLETED
    return BurnPlan(
        ignition_t_s=float(ignition_t_s),
        commanded_duration_s=float(duration_s),
        burn_duration_s=burn,
        cutoff_t_s=ignition_t_s + burn,
        propellant_used_kg=used,
        mass_flow_kgps=mdot,
        end_cause=cause,
        policy=policy,
    )
