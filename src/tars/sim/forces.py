"""Force-model boundary (ADR-0003).

Every physical influence on the spacecraft enters the simulation as an
acceleration returned by a ``ForceModel``. Future J2, drag, and thrust
(burn -> propulsion -> force) models plug in here; agents never set velocity.
"""

from __future__ import annotations

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
