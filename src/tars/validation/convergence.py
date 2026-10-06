"""Integrator convergence study against the exact Kepler solution (DR-0004).

Global error of an order-p method scales as C * dt^p. Measuring the error at
several step sizes and fitting log(error) vs log(dt) recovers p; for a correct
RK4 implementation the fitted order must be ~4. At very small dt the error
reaches the floating-point round-off floor and stops decreasing, so the fit uses
only step sizes in the asymptotic regime.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from tars.astro import kepler
from tars.astro.elements import keplerian_period, specific_energy
from tars.sim.integrators import INTEGRATORS
from tars.sim.runner import build_force_model, initial_state
from tars.sim.scenario import Scenario
from tars.sim.simulator import Simulator


@dataclass(frozen=True)
class ConvergencePoint:
    dt_s: float
    steps: int
    position_error_m: float
    velocity_error_mps: float
    energy_rel_error: float


def propagation_error(scenario: Scenario, dt_s: float, duration_s: float) -> ConvergencePoint:
    steps = round(duration_s / dt_s)
    if not np.isclose(steps * dt_s, duration_s, rtol=0, atol=1e-9):
        raise ValueError(f"duration {duration_s} is not a whole number of {dt_s} s steps")
    mu = scenario.constants.mu
    r0, v0 = initial_state(scenario)
    sim = Simulator(
        r0, v0, build_force_model(scenario), INTEGRATORS[scenario.integrator](), dt=dt_s
    )
    for _ in range(steps):
        sim.step()
    final = sim.snapshot()
    r_ref, v_ref = kepler.propagate(r0, v0, final.t, mu)
    e0 = specific_energy(r0, v0, mu)
    return ConvergencePoint(
        dt_s=dt_s,
        steps=steps,
        position_error_m=float(np.linalg.norm(final.r - r_ref)),
        velocity_error_mps=float(np.linalg.norm(final.v - v_ref)),
        energy_rel_error=abs((specific_energy(final.r, final.v, mu) - e0) / e0),
    )


def study_duration(scenario: Scenario, coarsest_dt: float) -> float:
    """The scenario's orbit count in seconds, rounded to whole coarsest steps."""
    c = scenario.constants
    period = keplerian_period(c.equatorial_radius + scenario.initial_orbit.altitude_m, c.mu)
    return round(scenario.stop.orbits * period / coarsest_dt) * coarsest_dt


def fitted_order(points: Sequence[ConvergencePoint]) -> float:
    dts = np.log([p.dt_s for p in points])
    errs = np.log([p.position_error_m for p in points])
    return float(np.polyfit(dts, errs, 1)[0])


def convergence_study(
    scenario: Scenario,
    dts: Sequence[float],
    fit_dts: Sequence[float],
    duration_s: float | None = None,
) -> tuple[list[ConvergencePoint], float]:
    if not set(fit_dts) <= set(dts):
        raise ValueError("fit_dts must be a subset of dts")
    duration = duration_s if duration_s is not None else study_duration(scenario, max(dts))
    points = [propagation_error(scenario, dt, duration) for dt in sorted(dts, reverse=True)]
    order = fitted_order([p for p in points if p.dt_s in set(fit_dts)])
    return points, order
