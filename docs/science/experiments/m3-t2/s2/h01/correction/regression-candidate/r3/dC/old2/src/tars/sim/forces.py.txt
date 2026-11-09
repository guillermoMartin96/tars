"""Force-model boundary (ADR-0003).

Every physical influence on the spacecraft enters the simulation as an
acceleration returned by a ``ForceModel``. Future J2, drag, and thrust
(burn -> propulsion -> force) models plug in here; agents never set velocity.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Sequence
from typing import Protocol

import numpy as np

from tars.sim.state import Vector

_MIN_NORMAL = sys.float_info.min  # smallest positive normal binary64


class ForceModel(Protocol):
    """Acceleration contribution [m/s^2] at time ``t`` [s] for ECI state (r, v)."""

    name: str

    def acceleration(self, t: float, r: Vector, v: Vector) -> Vector: ...


class PointMassGravity:
    """Newtonian point-mass central gravity: a = -mu r / |r|^3 (SCI-0001)."""

    name = "point_mass_gravity"

    def __init__(self, mu: float) -> None:
        if mu <= 0.0:
            raise ValueError("mu must be positive")
        self.mu = mu

    def acceleration(self, t: float, r: Vector, v: Vector) -> Vector:
        r_norm = float(np.linalg.norm(r))
        if r_norm == 0.0:
            raise ValueError("gravity is singular at the origin")
        return (-self.mu / r_norm**3) * r


class CompositeForceModel:
    """Sum of component force models (superposition of accelerations)."""

    name = "composite"

    def __init__(self, models: Sequence[ForceModel]) -> None:
        if not models:
            raise ValueError("at least one force model is required")
        self.models = tuple(models)

    def acceleration(self, t: float, r: Vector, v: Vector) -> Vector:
        total = np.zeros(3)
        for model in self.models:
            total = total + model.acceleration(t, r, v)
        return total

    @property
    def component_names(self) -> list[str]:
        return [m.name for m in self.models]


class ZonalJ2Gravity:
    """Degree-2 zonal (J2) perturbing acceleration about the frame +Z axis (SCI-0013).

    The gradient of the J2 term of U = (mu/r)[1 - J2 (R/r)^2 P2(z/r)]:

        a = -(3/2) J2 mu R^2 / r^5 * [x (1 - 5 z^2/r^2), y (1 - 5 z^2/r^2), z (3 - 5 z^2/r^2)]

    The point-mass term is not included; compose with ``PointMassGravity`` (point mass,
    then J2; ADR-0009 item 9). The symmetry axis is the frame +Z axis (DR-0028 J-ax-1)
    and is not configurable. Only basic IEEE 754 operations and ``math.sqrt`` are used
    (no ``pow``, no BLAS reductions), so the result does not depend on libm or BLAS.

    Immutable (M3T1-R1-F1): the instance has no ``__dict__`` and reassigning, deleting or
    adding any attribute raises ``AttributeError``. No derived value is cached: the
    coefficient is computed from the stored parameters on every call.

    Numerical contract (DR-0024 R6; M3T1-R1-F2); every violation raises ``ValueError``:
    - parameters: mu and R finite and positive, J2 finite, and -(3/2) J2 mu R^2 a finite
      normal binary64 unless J2 = 0;
    - position: finite components, not the origin;
    - evaluation: |r|^5 and, for J2 != 0, the scaled coefficient must be normal binary64
      numbers and the result finite. Outside that range the arithmetic would overflow,
      underflow or lose precision, so the call raises instead of returning a silent zero or
      a non-finite value. Inside it the result is the formula above, unchanged.
    The physical validity boundary (Earth's surface, termination) is not enforced here; it
    belongs to the scenario/termination design (DR-0029 P1-P9, open).
    """

    __slots__ = ("equatorial_radius", "j2", "mu")
    name = "zonal_j2"
    version = 1

    def __init__(self, mu: float, equatorial_radius: float, j2: float) -> None:
        if not (
            math.isfinite(mu)
            and mu > 0.0
            and math.isfinite(equatorial_radius)
            and equatorial_radius > 0.0
        ):
            raise ValueError("mu and equatorial_radius must be finite and positive")
        if not math.isfinite(j2):
            raise ValueError("j2 must be finite")
        k = -1.5 * j2 * mu * equatorial_radius * equatorial_radius
        if not math.isfinite(k) or (j2 != 0.0 and abs(k) < _MIN_NORMAL):
            raise ValueError("-(3/2) J2 mu R^2 is not a finite normal binary64 number")
        object.__setattr__(self, "mu", mu)
        object.__setattr__(self, "equatorial_radius", equatorial_radius)
        object.__setattr__(self, "j2", j2)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"ZonalJ2Gravity is immutable: cannot set {name!r}")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"ZonalJ2Gravity is immutable: cannot delete {name!r}")

    def acceleration(self, t: float, r: Vector, v: Vector) -> Vector:
        x, y, z = float(r[0]), float(r[1]), float(r[2])
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise ValueError("position must be finite")
        r2 = x * x + y * y + z * z
        if r2 == 0.0:
            if x == 0.0 and y == 0.0 and z == 0.0:
                raise ValueError("J2 gravity is singular at the origin")
            raise ValueError("outside the J2 numerical domain: |r|^2 underflows to zero")
        r_norm = math.sqrt(r2)
        s2 = z * z / r2
        r5 = r2 * r2 * r_norm
        if not _MIN_NORMAL <= r5 < math.inf:
            raise ValueError("outside the J2 numerical domain: |r|^5 is not a normal binary64")
        k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius
        k = k0 / r5
        if k0 != 0.0 and not _MIN_NORMAL <= abs(k) < math.inf:
            raise ValueError("outside the J2 numerical domain: coefficient not a normal binary64")
        c = 1.0 - 5.0 * s2
        a = np.array([k * c * x, k * c * y, k * (3.0 - 5.0 * s2) * z])
        if not np.all(np.isfinite(a)):
            raise ValueError("outside the J2 numerical domain: acceleration overflows")
        return a
