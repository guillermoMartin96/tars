"""Scenario runner: builds the simulator, runs it, and evaluates success.

Success/failure is decided by deterministic simulation logic (proof/mission.md),
and every important transition is emitted as a structured event.

Version-2 scenarios (M2 task T4) add a spacecraft, a command timeline and a duration
stop. Emission order is fixed (contract: docs/contracts/m2-commands-and-events.md):
- **Start (tick 0):** SimulationStarted, SpacecraftConfigured, command events of the
  submissions due at tick 0, then the samples.
- **After each committed step, at its end tick:**
  1. engine events of the step, in exact-time order;
  2. command events of the submissions due at that tick, unless the run ends there;
  3. StateSampled, then PropulsionSampled;
  4. OrbitCompleted.
Samples therefore always show the schedule in effect after the tick's submissions.
A version-1 scenario takes exactly the M1 path, with no new events.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

import numpy as np

import tars
from tars.astro.elements import circular_orbit_state, keplerian_period, specific_energy
from tars.events.schema import OrbitCompleted, SimulationCompleted, SimulationStarted, StateSampled
from tars.sim.burn_events import (
    burn_ended_event,
    burn_started_event,
    command_event,
    propellant_depleted_event,
    propulsion_sampled_event,
    spacecraft_configured_event,
)
from tars.sim.commands import CommandReceipt
from tars.sim.forces import CompositeForceModel, ForceModel, PointMassGravity
from tars.sim.integrators import INTEGRATORS
from tars.sim.propulsion import (
    BurnEndCause,
    EngineState,
    EngineTransition,
    PropulsionSnapshot,
    SpacecraftSpec,
)
from tars.sim.scenario import Scenario, ScenarioV2
from tars.sim.simulator import AscendingNodeDetector, Simulator
from tars.sim.state import StateSnapshot


@dataclass
class RunResult:
    """Outcome of one run. Built only by ``run_scenario``, which returns it only after
    the whole run, so a failed run never exposes a partial result.

    Attributes:
        receipts: Command receipts in submission order (version-2 scenarios).
        unsubmitted_command_ids: Timeline entries never submitted because the run
            ended first (failure or orbits stop), as their raw ``command_id`` (or None).
        final_propulsion: Propulsion snapshot at the final tick, if configured. A burn
            still active or pending at the stop is visible here (DR-0018).
    """

    scenario: Scenario
    events: list = field(default_factory=list)
    samples: list[StateSnapshot] = field(default_factory=list)
    crossing_times: list[float] = field(default_factory=list)
    initial: StateSnapshot | None = None
    final: StateSnapshot | None = None
    status: str = "failure"
    failure_cause: str | None = None
    receipts: list[CommandReceipt] = field(default_factory=list)
    unsubmitted_command_ids: list[str | None] = field(default_factory=list)
    final_propulsion: PropulsionSnapshot | None = None

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


def _raw_command_id(payload: dict) -> str | None:
    value = payload.get("command_id")
    return value if type(value) is str else None


class _BurnEventEmitter:
    """Turns committed engine transitions into burn events (one event per transition).

    It keeps each burn's ignition transition until its cutoff, so BurnEnded can report
    executed values against the ignition state, possibly many steps later.
    """

    def __init__(self, spacecraft: SpacecraftSpec) -> None:
        self._spacecraft = spacecraft
        self._ignitions: dict[str, EngineTransition] = {}

    def events(self, transitions: tuple[EngineTransition, ...], tick: int, t: float) -> list:
        out: list = []
        dry = self._spacecraft.dry_mass_kg
        for tr in transitions:
            assert tr.burn_id is not None
            if tr.kind == "ignition":
                if tr.burn_id in self._ignitions:
                    raise RuntimeError(f"duplicate ignition for {tr.burn_id}")
                self._ignitions[tr.burn_id] = tr
                out.append(burn_started_event(tr, tick=tick, t=t, dry_mass_kg=dry))
                continue
            ignition = self._ignitions.pop(tr.burn_id)  # KeyError: cutoff without ignition
            if tr.end_cause is BurnEndCause.PROPELLANT_DEPLETED:
                # The cause first, then the burn it ended.
                out.append(propellant_depleted_event(tr, tick=tick, t=t))
            out.append(
                burn_ended_event(
                    ignition, tr, tick=tick, t=t, dry_mass_kg=dry, engine=self._spacecraft.engine
                )
            )
        return out


def run_scenario(scenario: Scenario, record_samples: bool = True) -> RunResult:
    constants = scenario.constants
    r0, v0 = initial_state(scenario)
    v2 = scenario if isinstance(scenario, ScenarioV2) else None
    spacecraft = None if v2 is None or v2.spacecraft is None else v2.spacecraft.to_spec()
    sim = Simulator(
        r0,
        v0,
        force_model=build_force_model(scenario),
        integrator=INTEGRATORS[scenario.integrator](),
        dt=scenario.dt_s,
        detectors=[AscendingNodeDetector()],
        spacecraft=spacecraft,
    )
    stop_tick = None if v2 is None else v2.stop_tick
    if stop_tick is None:
        nominal_period = keplerian_period(
            constants.equatorial_radius + scenario.initial_orbit.altitude_m, constants.mu
        )
        target_orbits = scenario.stop.orbits
        max_ticks = math.ceil(
            scenario.stop.max_duration_periods * target_orbits * nominal_period / scenario.dt_s
        )
    radius = constants.equatorial_radius
    # Timeline in submission order. Payloads are exact JSON types (TimelineEntry), so a
    # deep copy is exact; the run cannot alias the scenario.
    entries = () if v2 is None else v2.commands
    timeline = [(v2.submit_tick(e), copy.deepcopy(e.command)) for e in entries]
    next_entry = 0
    burns = None if spacecraft is None else _BurnEventEmitter(spacecraft)

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
    if spacecraft is not None:
        result.events.append(spacecraft_configured_event(spacecraft, tick=start.tick, t=start.t))

    last_propulsion_tick = -1

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

    def sample_propulsion(snap: StateSnapshot) -> None:
        nonlocal last_propulsion_tick
        propulsion = sim.propulsion_snapshot()
        if propulsion is None or last_propulsion_tick == snap.tick:
            return  # no spacecraft, or this tick is already sampled
        assert spacecraft is not None
        result.events.append(propulsion_sampled_event(propulsion, snap, spacecraft))
        last_propulsion_tick = snap.tick

    def submit_due() -> None:
        nonlocal next_entry
        while next_entry < len(timeline) and timeline[next_entry][0] == sim.tick:
            receipt = sim.submit(timeline[next_entry][1])
            result.receipts.append(receipt)
            result.events.append(command_event(receipt))
            next_entry += 1

    # Submissions due at a tick precede that tick's samples, so a sample always shows
    # the schedule in effect after the tick (T4 review F1).
    submit_due()
    sample(start)
    sample_propulsion(start)
    min_alt = max_alt = _altitude(start, radius)
    orbits = 0
    cause: str | None = None
    snap = start

    def finished() -> bool:
        if stop_tick is not None:
            return sim.tick >= stop_tick
        return orbits >= target_orbits

    while not finished():
        if stop_tick is None and sim.tick >= max_ticks:
            cause = "timeout"
            break
        was_burning = _burning(sim.propulsion_snapshot())
        try:
            detections = sim.step()
        except FloatingPointError:
            cause = "non_finite"  # the step was not committed: no events from it
            break
        snap = sim.snapshot()
        if burns is not None:
            # Read only after a committed step: engine_transitions belongs to that step.
            transitions = sim.engine_transitions
            result.events.extend(burns.events(transitions, snap.tick, snap.t))
        alt = _altitude(snap, radius)
        min_alt, max_alt = min(min_alt, alt), max(max_alt, alt)
        first_orbit = orbits + 1
        orbits += len(detections)
        if alt <= 0.0:
            cause = "impact"
        elif specific_energy(snap.r, snap.v, constants.mu) >= 0.0:
            cause = "escape"
        # The run continues past this tick only if no failure, stop or timeout ends it
        # here; only then are this tick's submissions made.
        timing_out = stop_tick is None and sim.tick >= max_ticks
        if cause is None and not finished() and not timing_out:
            submit_due()
        if snap.tick % scenario.sample_every_ticks == 0:
            sample(snap)
            sample_propulsion(snap)
        elif burns is not None and (
            was_burning or transitions or _burning(sim.propulsion_snapshot())
        ):
            sample_propulsion(snap)  # every tick while burning (DR-0014 section 5)
        for number, crossing in enumerate(detections, start=first_orbit):
            result.crossing_times.append(crossing.crossing_t)
            result.events.append(
                OrbitCompleted(
                    tick=snap.tick, t=snap.t, orbit_number=number, crossing_t=crossing.crossing_t
                )
            )
        if cause is not None:
            break

    # The final state is always part of the telemetry and validated samples (REV-009).
    if snap.tick % scenario.sample_every_ticks != 0:
        sample(snap)
    sample_propulsion(snap)
    result.final = snap
    result.final_propulsion = sim.propulsion_snapshot()
    result.unsubmitted_command_ids = [_raw_command_id(p) for _, p in timeline[next_entry:]]
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


def _burning(snapshot: PropulsionSnapshot | None) -> bool:
    return snapshot is not None and snapshot.engine_state is EngineState.BURNING
