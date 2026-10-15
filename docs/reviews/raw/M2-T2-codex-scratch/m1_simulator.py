"""The simulator: sole owner of physical state (ADR-0002).

Physical state changes only through ``step()``, which integrates the configured
force model. External code receives read-only ``StateSnapshot`` objects; there is
deliberately no API that assigns position or velocity.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from tars.sim.forces import ForceModel
from tars.sim.integrators import Integrator
from tars.sim.state import StateSnapshot, Vector, frozen_vector


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


class Simulator:
    """Fixed-step propagation of one spacecraft's translational state."""

    def __init__(
        self,
        r0: Vector,
        v0: Vector,
        force_model: ForceModel,
        integrator: Integrator,
        dt: float,
        detectors: Sequence[AscendingNodeDetector] = (),
    ) -> None:
        if not dt > 0.0:
            raise ValueError("dt must be positive")
        self._force_model = force_model
        self._integrator = integrator
        self._dt = float(dt)
        self._detectors = tuple(detectors)
        self._tick = 0
        self._y: NDArray[np.float64] = _read_only(
            np.concatenate([frozen_vector(r0), frozen_vector(v0)])
        )

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

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(tick=self._tick, t=self.t, r=self._y[:3], v=self._y[3:])

    def _derivative(self, t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
        r, v = y[:3], y[3:]
        return np.concatenate([v, self._force_model.acceleration(t, r, v)])

    def step(self) -> list[AscendingNodeCrossing]:
        """Advance one tick; return detections that occurred during the step."""
        prev = self.snapshot()
        y_next = self._integrator.step(self._derivative, prev.t, self._y, self._dt)
        if not np.all(np.isfinite(y_next)):
            raise FloatingPointError(f"non-finite state produced at tick {self._tick + 1}")
        # Read-only so no force model can mutate simulator-owned state through the
        # r/v views it receives (REV-004); only step() replaces the state.
        self._y = _read_only(y_next)
        self._tick += 1
        curr = self.snapshot()
        detections = []
        for detector in self._detectors:
            found = detector.observe(prev, curr)
            if found is not None:
                detections.append(found)
        return detections
