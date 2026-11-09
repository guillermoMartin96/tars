"""Force-model boundary (ADR-0003).

Every physical influence on the spacecraft enters the simulation as an
acceleration returned by a ``ForceModel``. Future J2, drag, and thrust
(burn -> propulsion -> force) models plug in here; agents never set velocity.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Protocol

import numpy as np

from tars.sim.state import Vector


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
    """

    name = "zonal_j2"
    version = 1

    def __init__(self, mu: float, equatorial_radius: float, j2: float) -> None:
        if not (mu > 0.0 and equatorial_radius > 0.0):
            raise ValueError("mu and equatorial_radius must be positive")
        if not math.isfinite(j2):
            raise ValueError("j2 must be finite")
        self.mu = mu
        self.equatorial_radius = equatorial_radius
        self.j2 = j2
        self._k = -1.5 * j2 * mu * equatorial_radius * equatorial_radius

    def acceleration(self, t: float, r: Vector, v: Vector) -> Vector:
        x, y, z = float(r[0]), float(r[1]), float(r[2])
        r2 = x * x + y * y + z * z
        if r2 == 0.0:
            raise ValueError("J2 gravity is singular at the origin")
        r_norm = math.sqrt(r2)
        s2 = z * z / r2
        k = self._k / (r2 * r2 * r_norm)
        c = 1.0 - 5.0 * s2
        return np.array([k * c * x, k * c * y, k * (3.0 - 5.0 * s2) * z])
