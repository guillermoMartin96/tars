"""Fixed-step numerical integrators (ADR-0004).

An integrator advances y' = f(t, y) by one step of size dt. The simulator's
state vector is y = [r, v] (6 components), so f(t, y) = [v, a(t, r, v)].
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

Derivative = Callable[[float, NDArray[np.float64]], NDArray[np.float64]]


class Integrator(Protocol):
    name: str
    order: int

    def step(
        self, f: Derivative, t: float, y: NDArray[np.float64], dt: float
    ) -> NDArray[np.float64]: ...


class RK4:
    """Classical 4th-order Runge-Kutta: local error O(dt^5), global error O(dt^4)."""

    name = "rk4"
    order = 4

    def step(
        self, f: Derivative, t: float, y: NDArray[np.float64], dt: float
    ) -> NDArray[np.float64]:
        half = 0.5 * dt
        k1 = f(t, y)
        k2 = f(t + half, y + half * k1)
        k3 = f(t + half, y + half * k2)
        k4 = f(t + dt, y + dt * k3)
        return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


INTEGRATORS: dict[str, type[RK4]] = {RK4.name: RK4}
