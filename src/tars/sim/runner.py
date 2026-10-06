"""Scenario runner: builds the simulator, runs it, and evaluates success.

Success/failure is decided by deterministic simulation logic (proof/mission.md),
and every important transition is emitted as a structured event.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import tars
from tars.astro.elements import circular_orbit_state, keplerian_period, specific_energy
from tars.events.schema import OrbitCompleted, SimulationCompleted, SimulationStarted, StateSampled
from tars.sim.forces import CompositeForceModel, ForceModel, PointMassGravity
from tars.sim.integrators import INTEGRATORS
from tars.sim.scenario import Scenario
from tars.sim.simulator import AscendingNodeDetector, Simulator
from tars.sim.state import StateSnapshot


@dataclass
class RunResult:
    scenario: Scenario
    events: list = field(default_factory=list)
    samples: list[StateSnapshot] = field(default_factory=list)
    crossing_times: list[float] = field(default_factory=list)
    initial: StateSnapshot | None = None
    final: StateSnapshot | None = None
    status: str = "failure"
    failure_cause: str | None = None

    @property
    def completed(self) -> SimulationCompleted:
        return self.events[-1]


def build_force_model(scenario: Scenario) -> ForceModel:
    constants = scenario.constants
    registry = {"point_mass_gravity": lambda: PointMassGravity(constants.mu)}
    return CompositeForceModel([registry[name]() for name in scenario.force_models])


def initial_state(scenario: Scenario) -> tuple[np.ndarray, np.ndarray]:
    orbit = scenario.initial_orbit
    c = scenario.constants
    return circular_orbit_state(
        radius=c.equatorial_radius + orbit.altitude_m,
        inclination=math.radians(orbit.inclination_deg),
        raan=math.radians(orbit.raan_deg),
        arg_latitude=math.radians(orbit.arg_latitude_deg),
        mu=c.mu,
    )


def _altitude(snapshot: StateSnapshot, radius: float) -> float:
    return float(np.linalg.norm(snapshot.r)) - radius


def run_scenario(scenario: Scenario, record_samples: bool = True) -> RunResult:
    constants = scenario.constants
    r0, v0 = initial_state(scenario)
    sim = Simulator(
        r0,
        v0,
        force_model=build_force_model(scenario),
        integrator=INTEGRATORS[scenario.integrator](),
        dt=scenario.dt_s,
        detectors=[AscendingNodeDetector()],
    )
    nominal_period = keplerian_period(
        constants.equatorial_radius + scenario.initial_orbit.altitude_m, constants.mu
    )
    max_ticks = math.ceil(
        scenario.stop.max_duration_periods * scenario.stop.orbits * nominal_period / scenario.dt_s
    )
    radius = constants.equatorial_radius

    result = RunResult(scenario=scenario)
    start = sim.snapshot()
    result.initial = start
    result.events.append(
        SimulationStarted(
            tick=start.tick,
            t=start.t,
            scenario_name=scenario.name,
            scenario_hash=scenario.config_hash(),
            software_version=tars.__version__,
            epoch=scenario.epoch,
            time_scale=scenario.time_scale,
            seed=scenario.seed,
            earth_constants={
                "name": constants.name,
                "mu": constants.mu,
                "equatorial_radius": constants.equatorial_radius,
            },
            force_models=list(scenario.force_models),
            integrator=scenario.integrator,
            dt=scenario.dt_s,
            r=start.r.tolist(),
            v=start.v.tolist(),
        )
    )

    def sample(snap: StateSnapshot) -> None:
        if record_samples:
            result.samples.append(snap)
        result.events.append(
            StateSampled(
                tick=snap.tick,
                t=snap.t,
                r=snap.r.tolist(),
                v=snap.v.tolist(),
                altitude_m=_altitude(snap, radius),
            )
        )

    sample(start)
    min_alt = max_alt = _altitude(start, radius)
    orbits = 0
    cause: str | None = None
    snap = start

    while orbits < scenario.stop.orbits:
        if sim.tick >= max_ticks:
            cause = "timeout"
            break
        try:
            detections = sim.step()
        except FloatingPointError:
            cause = "non_finite"
            break
        snap = sim.snapshot()
        alt = _altitude(snap, radius)
        min_alt, max_alt = min(min_alt, alt), max(max_alt, alt)
        if snap.tick % scenario.sample_every_ticks == 0:
            sample(snap)
        for crossing in detections:
            orbits += 1
            result.crossing_times.append(crossing.crossing_t)
            result.events.append(
                OrbitCompleted(
                    tick=snap.tick, t=snap.t, orbit_number=orbits, crossing_t=crossing.crossing_t
                )
            )
        if alt <= 0.0:
            cause = "impact"
            break
        if specific_energy(snap.r, snap.v, constants.mu) >= 0.0:
            cause = "escape"
            break

    # The final state is always part of the telemetry and validated samples (REV-009).
    if snap.tick % scenario.sample_every_ticks != 0:
        sample(snap)
    result.final = snap
    result.status = "success" if cause is None else "failure"
    result.failure_cause = cause
    result.events.append(
        SimulationCompleted(
            tick=snap.tick,
            t=snap.t,
            status=result.status,
            failure_cause=cause,
            orbits_completed=orbits,
            r=snap.r.tolist(),
            v=snap.v.tolist(),
            min_altitude_m=min_alt,
            max_altitude_m=max_alt,
        )
    )
    return result
