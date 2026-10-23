"""Force-model boundary (ADR-0003).

Every physical influence on the spacecraft enters the simulation as an
acceleration returned by a ``ForceModel``. Future J2, drag, and thrust
(burn -> propulsion -> force) models plug in here; agents never set velocity.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Sequence
from fractions import Fraction
from typing import Protocol

import numpy as np

from tars.sim.state import Vector

_MIN_NORMAL = sys.float_info.min  # smallest positive normal binary64


def _owned_float(name: str, value: object) -> float:
    """Built-in float snapshot of a supported real scalar (M3T1-R2-F2): int (not bool), float,
    a NumPy integer or floating scalar, or a zero-dimensional array of one."""
    scalar = value[()] if isinstance(value, np.ndarray) and value.ndim == 0 else value
    if isinstance(scalar, bool) or not isinstance(scalar, int | float | np.integer | np.floating):
        raise TypeError(
            f"{name} must be a real number (int, float, or a NumPy integer or floating scalar "
            f"or zero-dimensional array), not {type(value).__name__}"
        )
    try:
        return float(scalar)
    except OverflowError:
        raise ValueError(f"{name} is not representable as a binary64 number") from None


def _underflows(product: float, a: float, b: float) -> bool:
    """True if the binary64 ``product`` of ``a`` and ``b`` underflowed (M3T1-R2-F1): it is
    below the normal range and inexact, so it has lost relative precision. An exact result,
    including an exact zero, is not an underflow. The exact comparison runs only for results
    below the normal range."""
    return abs(product) < _MIN_NORMAL and Fraction(a) * Fraction(b) != product


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

    Parameters (M3T1-R2-F2) are converted to built-in floats at construction, before
    validation, so the instance never refers to a caller's object. Supported: int (not bool),
    float, NumPy integer and floating scalars, and zero-dimensional arrays of those; any other
    type raises ``TypeError``.

    Numerical contract (DR-0024 R6; M3T1-R1-F2, M3T1-R2-F1); every violation raises
    ``ValueError``:
    - parameters: mu and R finite and positive, J2 finite, and -(3/2) J2 mu R^2 a finite
      normal binary64 unless J2 = 0, with no underflow in its intermediate products;
    - position: finite components, not the origin;
    - evaluation: |r|^5 and, for J2 != 0, the scaled coefficient k must be normal binary64
      numbers, the products k (1 - 5 z^2/r^2) and k (3 - 5 z^2/r^2) must not underflow, and
      the result must be finite. Outside that range the arithmetic would overflow, underflow
      or lose precision, so the call raises instead of returning a silent zero or a
      non-finite value. Inside it the result is the formula above, unchanged.
    "Underflow" means a result below the normal range that is inexact. Exact zeros (J2 = 0, a
    zero coordinate, a latitude factor that is exactly 0) and exact subnormal products are
    not underflow, and a final component may be subnormal. The checks cannot tell a latitude
    factor that is mathematically 0 from one that is only computed as a small non-zero value:
    in that case, which needs non-physical parameters, the call raises.
    The physical validity boundary (Earth's surface, termination) is not enforced here; it
    belongs to the scenario/termination design (DR-0029 P1-P9, open).
    """

    __slots__ = ("equatorial_radius", "j2", "mu")
    name = "zonal_j2"
    version = 1

    def __init__(self, mu: float, equatorial_radius: float, j2: float) -> None:
        mu = _owned_float("mu", mu)
        equatorial_radius = _owned_float("equatorial_radius", equatorial_radius)
        j2 = _owned_float("j2", j2)
        if not (
            math.isfinite(mu)
            and mu > 0.0
            and math.isfinite(equatorial_radius)
            and equatorial_radius > 0.0
        ):
            raise ValueError("mu and equatorial_radius must be finite and positive")
        if not math.isfinite(j2):
            raise ValueError("j2 must be finite")
        p1 = -1.5 * j2
        p2 = p1 * mu
        p3 = p2 * equatorial_radius
        k = p3 * equatorial_radius  # -1.5 * j2 * mu * R * R, evaluated left to right
        if not math.isfinite(k) or (j2 != 0.0 and abs(k) < _MIN_NORMAL):
            raise ValueError("-(3/2) J2 mu R^2 is not a finite normal binary64 number")
        if (
            _underflows(p1, -1.5, j2)
            or _underflows(p2, p1, mu)
            or _underflows(p3, p2, equatorial_radius)
        ):
            raise ValueError("-(3/2) J2 mu R^2: an intermediate product underflows")
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
        d = 3.0 - 5.0 * s2
        kc = k * c
        kd = k * d
        if _underflows(kc, k, c) or _underflows(kd, k, d):
            raise ValueError("outside the J2 numerical domain: a component product underflows")
        a = np.array([kc * x, kc * y, kd * z])
        if not np.all(np.isfinite(a)):
            raise ValueError("outside the J2 numerical domain: acceleration overflows")
        return a
