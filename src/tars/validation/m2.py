"""Milestone 2 Proof: oracles O1-O8 (DR-0015) and event-log contract checks (T5).

Independence rule. Every *expected* physical quantity is computed here from the
scenario's raw inputs (thrust, Isp, masses, commanded times) with textbook relations,
or by an independently written reference integrator. Simulator outputs (event fields,
samples) are only ever the quantities *under test*; they are never fed back as the
expectation. The two exceptions are documented where they occur: O5 propagates the
simulator's own cutoff state (it tests the coast, not the burn), and O6 starts the
impulsive reference from the simulator's ignition state (so the pre-burn coast error,
measured by O4/O5, cancels).

Oracles (DR-0015):
- O1 mass law: propellant used = F T / (Isp g0), T the commanded or depletion time.
- O2 rocket equation: sensed delta-v = Isp g0 ln(m0 / mf).
- O3 free-space closed form with the production simulator and no gravity.
- O4 SciPy DOP853 on an independently written right-hand side.
- O5 coast arcs against exact Kepler propagation.
- O6 impulsive limit: finite - impulsive SMA is second order in burn duration.
- O7 direction signs and plane invariants.
- O8 RK4 convergence order through the burn.
O9 (GMAT) is task T6 and is not here.

DR-0017's timing-induced delta-v bound is a separate, per-burn quantity reported by
the simulator; nothing here treats it as a bound on trajectory error.

SciPy is a dev-only dependency (DR-0015): it is imported inside ``dop853_reference``.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, localcontext
from itertools import pairwise
from typing import Any

import numpy as np

from tars.astro import kepler
from tars.astro.elements import rv_to_elements, specific_energy
from tars.events.schema import to_jsonl
from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec, SpacecraftSpec, TankSpec
from tars.sim.runner import RunResult
from tars.sim.scenario import ScenarioV2
from tars.sim.simulator import Simulator
from tars.validation.m2_missions import Expected

SIGN = {"prograde": 1.0, "retrograde": -1.0}
ENGINE_EVENTS = ("BurnStarted", "BurnEnded", "PropellantDepleted")
COMMAND_EVENTS = ("CommandAccepted", "CommandRejected")
# Per-tick emission rank (contract, "Emission order").
_RANK = {
    "SimulationStarted": -2,
    "SpacecraftConfigured": -1,
    "BurnStarted": 0,
    "BurnEnded": 0,
    "PropellantDepleted": 0,
    "CommandAccepted": 1,
    "CommandRejected": 1,
    "StateSampled": 2,
    "PropulsionSampled": 3,
    "OrbitCompleted": 4,
}


# --------------------------------------------------------------- independent prediction


@dataclass(frozen=True)
class PredictedBurn:
    """A burn as predicted from the scenario inputs alone (no simulator output).

    ``burn_time_s`` is the commanded duration, or the analytic depletion time
    P / mdot for a burn_to_depletion burn that runs the tank dry.
    """

    burn_id: str
    command_id: str
    direction: str
    submit_tick: int
    ignition_t_s: float
    commanded_duration_s: float
    policy: str
    end_cause: str
    burn_time_s: float
    cutoff_t_s: float
    propellant_before_kg: float
    propellant_used_kg: float
    mass_before_kg: float
    mass_after_kg: float
    delta_v_mps: float


@dataclass(frozen=True)
class Vehicle:
    """Raw spacecraft inputs and the textbook derived quantities (SCI-0008/0009)."""

    dry_mass_kg: float
    propellant_kg: float
    thrust_n: float
    isp_s: float

    @property
    def exhaust_velocity_mps(self) -> float:
        return self.isp_s * STANDARD_GRAVITY

    @property
    def mass_flow_kgps(self) -> float:
        return self.thrust_n / (self.isp_s * STANDARD_GRAVITY)

    @property
    def initial_mass_kg(self) -> float:
        return self.dry_mass_kg + self.propellant_kg


def vehicle(scenario: ScenarioV2) -> Vehicle | None:
    sc = scenario.spacecraft
    if sc is None:
        return None
    return Vehicle(sc.dry_mass_kg, sc.propellant_kg, sc.engine.thrust_n, sc.engine.isp_s)


def predict_burns(scenario: ScenarioV2, expected: Sequence[Expected]) -> list[PredictedBurn]:
    """Accepted burns, in execution order, from the scenario and declared outcomes.

    Burns execute in acceptance order and never overlap (contract), so propellant is
    chained burn by burn: P_k+1 = P_k - used_k.
    """
    if len(expected) != len(scenario.commands):
        raise ValueError("one expectation per timeline entry is required")
    veh = vehicle(scenario)
    burns: list[PredictedBurn] = []
    propellant = 0.0 if veh is None else veh.propellant_kg
    for entry, exp in zip(scenario.commands, expected, strict=True):
        if exp.status != "accepted":
            continue
        if veh is None:
            raise ValueError("an accepted burn needs a spacecraft")
        cmd = entry.command
        c, mdot = veh.exhaust_velocity_mps, veh.mass_flow_kgps
        duration = float(cmd["duration_s"])
        depletion = propellant / mdot
        if duration <= depletion:
            cause, burn_time, used = "completed", duration, min(mdot * duration, propellant)
        elif cmd.get("on_insufficient_propellant", "reject") == "burn_to_depletion":
            cause, burn_time, used = "propellant_depleted", depletion, propellant
        else:
            raise ValueError(f"{cmd['command_id']}: declared accepted but insufficient")
        m0 = veh.dry_mass_kg + propellant
        mf = m0 - used
        ignition = float(cmd["ignition_t_s"])
        burns.append(
            PredictedBurn(
                burn_id=f"burn#{len(burns) + 1:06d}",
                command_id=cmd["command_id"],
                direction=cmd["direction"],
                submit_tick=scenario.submit_tick(entry),
                ignition_t_s=ignition,
                commanded_duration_s=duration,
                policy=cmd.get("on_insufficient_propellant", "reject"),
                end_cause=cause,
                burn_time_s=burn_time,
                cutoff_t_s=ignition + burn_time,
                propellant_before_kg=propellant,
                propellant_used_kg=used,
                mass_before_kg=m0,
                mass_after_kg=mf,
                delta_v_mps=c * math.log(m0 / mf),
            )
        )
        propellant = max(propellant - used, 0.0)
    if any(b.ignition_t_s < a.cutoff_t_s for a, b in pairwise(burns)):
        raise ValueError("declared accepted burns overlap")
    return burns


def _of(events: Sequence[Any], *types: str) -> list[Any]:
    return [e for e in events if e.type in types]


def events_sha256(events: Sequence[Any]) -> str:
    return hashlib.sha256(to_jsonl(events).encode()).hexdigest()


def _ulp(x: float) -> float:
    return math.ulp(x)


# --------------------------------------------------------------- event-log contract


def _expected_report_tick(event_t: float, dt: float, same_tick_submission: bool) -> int:
    """End tick of the step that executes an engine event at ``event_t``.

    An event exactly on a tick boundary k*dt is executed by the step reaching it
    (tick k). The one exception: a burn submitted at tick k for ignition at k*dt is
    executed at the start of the next step, so it is reported at tick k + 1
    (contract "Event times"; T3 semantics, unchanged).
    """
    k = math.ceil(event_t / dt)
    while k > 0 and (k - 1) * dt >= event_t:
        k -= 1
    while k * dt < event_t:
        k += 1
    if same_tick_submission and k * dt == event_t:
        return k + 1
    return k


def check_event_order(scenario: ScenarioV2, events: Sequence[Any]) -> list[str]:
    """Violations of the deterministic emission order and cadence (contract T4)."""
    v: list[str] = []
    dt, every = scenario.dt_s, scenario.sample_every_ticks
    if not events or events[0].type != "SimulationStarted":
        return ["first event is not SimulationStarted"]
    if events[-1].type != "SimulationCompleted":
        return ["last event is not SimulationCompleted"]
    if sum(e.type in ("SimulationStarted", "SimulationCompleted") for e in events) != 2:
        v.append("SimulationStarted/SimulationCompleted not unique")
    configured = scenario.spacecraft is not None
    has_cfg = [i for i, e in enumerate(events) if e.type == "SpacecraftConfigured"]
    if has_cfg != ([1] if configured else []):
        v.append(f"SpacecraftConfigured at {has_cfg}, expected {[1] if configured else []}")
    final_tick = events[-1].tick
    for i, e in enumerate(events):
        if e.t != e.tick * dt:
            v.append(f"event {i} {e.type}: t {e.t!r} != tick*dt")
        if i and e.tick < events[i - 1].tick:
            v.append(f"event {i} {e.type}: tick decreases")
    body = list(events[:-1])
    # End block (contract "End"): at an off-grid final tick the final StateSampled, and
    # a PropulsionSampled not already emitted that tick, follow the per-step block.
    if final_tick % every and final_tick != 0:
        idx = [i for i, e in enumerate(body) if e.tick == final_tick and e.type == "StateSampled"]
        if len(idx) != 1:
            v.append(f"final off-grid tick {final_tick}: {len(idx)} StateSampled")
        else:
            tail = body[idx[0] :]
            if any(e.type not in ("StateSampled", "PropulsionSampled") for e in tail):
                v.append("events between the final StateSampled and SimulationCompleted")
            body = body[: idx[0]]
    for i, (a, b) in enumerate(pairwise(body)):
        if a.tick == b.tick and _RANK[b.type] < _RANK[a.type]:
            v.append(f"tick {a.tick}: {b.type} after {a.type} (event {i + 1})")

    # Engine events: exact-time order; cutoff before ignition at equal times;
    # PropellantDepleted immediately before its BurnEnded.
    for i, (a, b) in enumerate(pairwise(events)):
        if a.type in ENGINE_EVENTS and b.type in ENGINE_EVENTS and a.tick == b.tick:
            if b.event_t_s < a.event_t_s:
                v.append(f"tick {a.tick}: engine events out of time order")
            if b.event_t_s == a.event_t_s and a.type == "BurnStarted" and b.type != "BurnStarted":
                v.append(f"tick {a.tick}: ignition before a cutoff at the same time")
        if a.type == "PropellantDepleted" and not (
            b.type == "BurnEnded"
            and b.burn_id == a.burn_id
            and b.end_cause == "propellant_depleted"
            and b.event_t_s == a.event_t_s
        ):
            v.append(f"event {i}: PropellantDepleted not followed by its BurnEnded")

    # Envelope: the report tick is computed independently of the simulator.
    submit_tick = {e.burn_id: e.tick for e in events if e.type == "CommandAccepted"}
    for e in _of(events, *ENGINE_EVENTS):
        same = (
            e.type == "BurnStarted"
            and submit_tick.get(e.burn_id) is not None
            and submit_tick[e.burn_id] * dt == e.event_t_s
        )
        want = _expected_report_tick(e.event_t_s, dt, same)
        if e.tick != want:
            v.append(f"{e.type} {e.burn_id} at t={e.event_t_s!r}: tick {e.tick}, expected {want}")

    # Cadence: StateSampled on the grid and at the final tick; PropulsionSampled also
    # on every tick whose step involved the engine (burn start tick..end tick).
    state_ticks = [e.tick for e in events if e.type == "StateSampled"]
    want_state = sorted({k for k in range(0, final_tick + 1, every)} | {final_tick})
    if state_ticks != want_state:
        v.append("StateSampled ticks differ from the telemetry grid plus the final tick")
    prop_ticks = [e.tick for e in events if e.type == "PropulsionSampled"]
    if configured:
        engine_ticks: set[int] = set()
        started = {e.burn_id: e.tick for e in events if e.type == "BurnStarted"}
        ended = {e.burn_id: e.tick for e in events if e.type == "BurnEnded"}
        for burn_id, k0 in started.items():
            engine_ticks |= set(range(k0, ended.get(burn_id, final_tick) + 1))
        want_prop = sorted(set(want_state) | engine_ticks)
        if prop_ticks != want_prop:
            extra = sorted(set(prop_ticks) - set(want_prop))
            missing = sorted(set(want_prop) - set(prop_ticks))
            dup = len(prop_ticks) - len(set(prop_ticks))
            v.append(
                f"PropulsionSampled cadence: extra {extra[:5]}, missing {missing[:5]}, dup {dup}"
            )
    elif prop_ticks:
        v.append("PropulsionSampled without a spacecraft")
    return v


def _payload_value(payload: dict[str, Any], name: str) -> Any:
    return payload.get(name)


def check_traceability(
    scenario: ScenarioV2,
    events: Sequence[Any],
    expected: Sequence[Expected],
    result: RunResult,
) -> list[str]:
    """Command -> receipt -> burn -> outcome correlation, and commanded vs executed."""
    v: list[str] = []
    receipts = _of(events, *COMMAND_EVENTS)
    entries = scenario.commands
    if len(receipts) != len(entries) - len(result.unsubmitted_command_ids):
        v.append(f"{len(receipts)} receipts for {len(entries)} timeline entries")
    for i, (entry, rec, exp) in enumerate(zip(entries, receipts, expected, strict=False)):
        payload = entry.command
        cid = payload.get("command_id")
        if rec.tick != scenario.submit_tick(entry):
            v.append(f"entry {i}: receipt at tick {rec.tick}, submitted at {entry.submit_t_s}")
        if rec.command_id != (cid if isinstance(cid, str) else None) and not (
            exp.reason == "schema_invalid" and rec.command_id is None
        ):
            v.append(f"entry {i}: receipt command_id {rec.command_id!r} != {cid!r}")
        status = "accepted" if rec.type == "CommandAccepted" else "rejected"
        if (status, getattr(rec, "reason", None)) != (exp.status, exp.reason):
            v.append(
                f"entry {i} ({cid}): {status}/{getattr(rec, 'reason', None)}, "
                f"declared {exp.status}/{exp.reason}"
            )
        schema_valid = status == "accepted" or rec.reason != "schema_invalid"
        if schema_valid:
            intent = {
                "commanded_ignition_t_s": payload.get("ignition_t_s"),
                "commanded_duration_s": payload.get("duration_s"),
                "direction": payload.get("direction"),
                "on_insufficient_propellant": payload.get("on_insufficient_propellant", "reject"),
            }
            for field_name, want in intent.items():
                if getattr(rec, field_name) != want:
                    v.append(f"entry {i}: {field_name} {getattr(rec, field_name)!r} != {want!r}")
        if not schema_valid and (
            rec.commanded_ignition_t_s is not None or rec.direction is not None
        ):
            v.append(f"entry {i}: schema-invalid receipt echoes intent")

    accepted = _of(events, "CommandAccepted")
    ids = [a.burn_id for a in accepted]
    if ids != [f"burn#{k:06d}" for k in range(1, len(ids) + 1)]:
        v.append(f"burn IDs not sequential in acceptance order: {ids}")
    if len({a.command_id for a in accepted}) != len(accepted):
        v.append("an accepted command_id was accepted twice")
    by_burn = {a.burn_id: a for a in accepted}
    starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    if len(starts) != len(_of(events, "BurnStarted")) or len(ends) != len(_of(events, "BurnEnded")):
        v.append("a burn started or ended more than once")
    for burn_id, s in starts.items():
        acc = by_burn.get(burn_id)
        if acc is None:
            v.append(f"{burn_id} started without an accepted command")
            continue
        for name in ("command_id", "direction", "commanded_ignition_t_s", "commanded_duration_s"):
            if getattr(s, name) != getattr(acc, name):
                v.append(f"{burn_id}: BurnStarted.{name} != CommandAccepted.{name}")
        if s.event_t_s != acc.commanded_ignition_t_s:
            v.append(
                f"{burn_id}: ignited at {s.event_t_s!r}, commanded {acc.commanded_ignition_t_s!r}"
            )
        if s.planned_cutoff_t_s != acc.planned_cutoff_t_s:
            v.append(f"{burn_id}: planned cutoff changed after acceptance")
    for burn_id, e in ends.items():
        s = starts.get(burn_id)
        if s is None:
            v.append(f"{burn_id} ended without starting")
            continue
        acc = by_burn[burn_id]
        if events.index(e) < events.index(s):
            v.append(f"{burn_id}: BurnEnded before BurnStarted")
        for name in ("command_id", "direction", "commanded_duration_s"):
            if getattr(e, name) != getattr(s, name):
                v.append(f"{burn_id}: BurnEnded.{name} != BurnStarted.{name}")
        if e.ignition_t_s != s.event_t_s:
            v.append(f"{burn_id}: BurnEnded.ignition_t_s != BurnStarted.event_t_s")
        if e.executed_duration_s != e.event_t_s - e.ignition_t_s:
            v.append(f"{burn_id}: executed_duration_s != event_t_s - ignition_t_s")
        if e.event_t_s != acc.planned_cutoff_t_s or e.end_cause != acc.planned_end_cause:
            v.append(f"{burn_id}: execution differs from the accepted plan")
        # Commanded vs executed, independent of the plan: the commanded duration is the
        # receipt's (checked against the scenario payload above), never the burn
        # event's own copy, which comes from the plan. A completed burn cuts off at the
        # represented commanded time; a depleted one burns no longer than commanded.
        commanded = acc.commanded_duration_s
        if e.end_cause == "completed":
            if e.event_t_s != e.ignition_t_s + commanded:
                v.append(f"{burn_id}: cutoff {e.event_t_s!r} != ignition + commanded duration")
        elif not e.executed_duration_s < commanded:
            v.append(f"{burn_id}: depleted burn not shorter than commanded")
    # DR-0018 (approved A): every accepted burn has ended, or is visibly active or
    # pending in the final propulsion sample. No fabricated end.
    final = _of(events, "PropulsionSampled")
    final_p = final[-1] if final else None
    for burn_id in by_burn:
        if burn_id in ends:
            continue
        if final_p is None:
            v.append(f"{burn_id}: no final propulsion sample")
        elif burn_id in starts:
            if final_p.active_burn_id != burn_id or final_p.engine_state != "burning":
                v.append(f"{burn_id}: started, not ended, not active at the stop")
        elif burn_id not in final_p.pending_burn_ids:
            v.append(f"{burn_id}: never started and not pending at the stop")
    for e in _of(events, "PropellantDepleted"):
        if ends.get(e.burn_id) is None or ends[e.burn_id].end_cause != "propellant_depleted":
            v.append(f"{e.burn_id}: PropellantDepleted without a depleted BurnEnded")
    return v


def check_outcomes(
    scenario: ScenarioV2,
    events: Sequence[Any],
    predicted: Sequence[PredictedBurn],
) -> list[str]:
    """Run status and the burn lifecycle predicted from the scenario alone."""
    v: list[str] = []
    done = events[-1]
    if done.status != "success" or done.failure_cause is not None:
        v.append(f"run ended {done.status}/{done.failure_cause}")
    stop_t = done.t
    starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    active: str | None = None
    pending: list[str] = []
    for b in predicted:
        if b.ignition_t_s > stop_t:
            pending.append(b.burn_id)
            if b.burn_id in starts:
                v.append(f"{b.burn_id}: started after the stop")
        elif b.cutoff_t_s > stop_t:
            active = b.burn_id
            if b.burn_id not in starts or b.burn_id in ends:
                v.append(f"{b.burn_id}: expected active at the stop")
        else:
            end = ends.get(b.burn_id)
            if end is None:
                v.append(f"{b.burn_id}: expected to end ({b.end_cause})")
            elif end.end_cause != b.end_cause:
                v.append(f"{b.burn_id}: ended {end.end_cause}, expected {b.end_cause}")
            if end is not None and (end.command_id, end.direction) != (b.command_id, b.direction):
                v.append(f"{b.burn_id}: command or direction differs from the scenario")
    finals = _of(events, "PropulsionSampled")
    if scenario.spacecraft is not None:
        want_state = "burning" if active else ("scheduled" if pending else "idle")
        last = finals[-1]
        got = (last.tick, last.engine_state, last.active_burn_id, list(last.pending_burn_ids))
        if got != (done.tick, want_state, active, pending):
            want = (done.tick, want_state, active, pending)
            v.append(f"final propulsion sample {got}, expected {want}")
    return v


def check_spacecraft_configured(scenario: ScenarioV2, events: Sequence[Any]) -> list[str]:
    veh = vehicle(scenario)
    cfg = _of(events, "SpacecraftConfigured")
    if veh is None:
        return [] if not cfg else ["SpacecraftConfigured without a spacecraft"]
    c = cfg[0]
    want = {
        "dry_mass_kg": veh.dry_mass_kg,
        "propellant_kg": veh.propellant_kg,
        "thrust_n": veh.thrust_n,
        "isp_s": veh.isp_s,
        "standard_gravity_mps2": STANDARD_GRAVITY,
        "exhaust_velocity_mps": veh.exhaust_velocity_mps,
        "mass_flow_kgps": veh.mass_flow_kgps,
    }
    out = [
        f"SpacecraftConfigured.{k} {getattr(c, k)!r} != {w!r}"
        for k, w in want.items()
        if getattr(c, k) != w
    ]
    return out


def accounting_metrics(
    scenario: ScenarioV2, events: Sequence[Any]
) -> tuple[dict[str, float], list[str]]:
    """Mass and delta-v bookkeeping from the telemetry (conservation invariants).

    - total mass = dry + propellant in every sample; never below dry; propellant never
      negative and non-increasing;
    - between samples with no burn activity, propellant and sensed delta-v are
      bit-identical;
    - initial - final propellant = sum of per-burn consumption (+ an active burn);
    - final sensed delta-v = sum of per-burn sensed delta-v (+ an active burn);
    - thrust acceleration is exactly zero unless burning, and F/m along +-v otherwise.
    """
    v: list[str] = []
    veh = vehicle(scenario)
    if veh is None:
        return {"propellant_accounting_rel_error": 0.0, "delta_v_accounting_rel_error": 0.0}, v
    v.extend(check_spacecraft_configured(scenario, events))
    samples = _of(events, "PropulsionSampled")
    states = {e.tick: e for e in events if e.type == "StateSampled"}
    starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    thrust_rel = 0.0
    dir_err = 0.0
    for p in samples:
        if p.total_mass_kg != veh.dry_mass_kg + p.propellant_kg:
            v.append(f"tick {p.tick}: total mass != dry + propellant")
        if p.propellant_kg < 0.0:
            v.append(f"tick {p.tick}: negative propellant")
        a = np.array(p.thrust_acceleration_mps2)
        if p.engine_state != "burning":
            if np.any(a != 0.0):
                v.append(f"tick {p.tick}: thrust acceleration while not burning")
            continue
        want = veh.thrust_n / p.total_mass_kg
        thrust_rel = max(thrust_rel, abs(float(np.linalg.norm(a)) - want) / want)
        st = states.get(p.tick)
        if st is not None and p.active_burn_id in starts:
            sign = SIGN[starts[p.active_burn_id].direction]
            u = sign * np.array(st.v) / np.linalg.norm(st.v)
            dir_err = max(dir_err, float(np.linalg.norm(a / np.linalg.norm(a) - u)))
    # Propellant and sensed delta-v change only while the engine runs.
    engine_ticks: set[int] = set()
    final_tick = events[-1].tick
    for burn_id, s in starts.items():
        engine_ticks |= set(
            range(s.tick, ends[burn_id].tick + 1 if burn_id in ends else final_tick + 1)
        )
    for a, b in pairwise(samples):
        if b.propellant_kg > a.propellant_kg:
            v.append(f"tick {b.tick}: propellant increased")
        quiet = not any(k in engine_ticks for k in range(a.tick + 1, b.tick + 1))
        if quiet and (
            b.propellant_kg != a.propellant_kg or b.delta_v_sensed_mps != a.delta_v_sensed_mps
        ):
            v.append(f"ticks {a.tick}->{b.tick}: propellant or delta-v changed while idle")
    used = sum(e.propellant_used_kg for e in ends.values())
    sensed = sum(e.sensed_delta_v_mps for e in ends.values())
    last = samples[-1]
    if last.active_burn_id is not None and last.active_burn_id in starts:
        s = starts[last.active_burn_id]
        used += s.propellant_kg - last.propellant_kg
        # Sensed delta-v of the active burn so far: rocket equation on its mass drop.
        sensed += veh.exhaust_velocity_mps * math.log(s.total_mass_kg / last.total_mass_kg)
    for e in ends.values():
        s = starts[e.burn_id]
        if e.propellant_used_kg != s.propellant_kg - e.propellant_kg:
            v.append(f"{e.burn_id}: propellant_used_kg != ignition - cutoff propellant")
    m0 = veh.initial_mass_kg
    metrics = {
        "propellant_accounting_rel_error": abs(veh.propellant_kg - last.propellant_kg - used) / m0,
        "delta_v_accounting_rel_error": (
            abs(last.delta_v_sensed_mps - sensed) / sensed
            if sensed
            else abs(last.delta_v_sensed_mps)
        ),
        "thrust_acceleration_rel_error_max": thrust_rel,
        "thrust_direction_error_max": dir_err,
        "final_propellant_kg": last.propellant_kg,
    }
    return metrics, v


# --------------------------------------------------------------- O1 / O2


def mass_and_rocket_metrics(
    scenario: ScenarioV2, events: Sequence[Any], predicted: Sequence[PredictedBurn]
) -> tuple[dict[str, float], dict[str, float], list[str]]:
    """O1 (mass law) and O2 (rocket equation) for every ended burn.

    Expected values come from ``predict_burns`` (scenario inputs only). For a
    depletion burn, DR-0017 D1a allows the cutoff up to 2 ulp(cutoff) before the
    analytic depletion time, leaving a residual of at most mdot * 2 ulp(cutoff); the
    ratio to that analytic bound is reported and must be <= 1.
    """
    veh = vehicle(scenario)
    assert veh is not None
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    m0_total = veh.initial_mass_kg
    o1 = {"propellant_used_rel_error_max": 0.0, "depletion_residual_over_bound_max": 0.0}
    o2 = {"sensed_delta_v_rel_error_max": 0.0, "reported_rocket_equation_rel_error_max": 0.0}
    v: list[str] = []
    for b in predicted:
        e = ends.get(b.burn_id)
        if e is None:
            continue
        o1["propellant_used_rel_error_max"] = max(
            o1["propellant_used_rel_error_max"],
            abs(e.propellant_used_kg - b.propellant_used_kg) / m0_total,
        )
        if b.end_cause == "propellant_depleted":
            bound = veh.mass_flow_kgps * 2.0 * _ulp(b.cutoff_t_s)
            o1["depletion_residual_over_bound_max"] = max(
                o1["depletion_residual_over_bound_max"], e.propellant_kg / bound
            )
            if e.propellant_kg < 0.0:
                v.append(f"{b.burn_id}: negative residual")
        o2["sensed_delta_v_rel_error_max"] = max(
            o2["sensed_delta_v_rel_error_max"],
            abs(e.sensed_delta_v_mps - b.delta_v_mps) / b.delta_v_mps,
        )
        o2["reported_rocket_equation_rel_error_max"] = max(
            o2["reported_rocket_equation_rel_error_max"],
            abs(e.rocket_equation_delta_v_mps - b.delta_v_mps) / b.delta_v_mps,
        )
    return o1, o2, v


# --------------------------------------------------------------- O3 free space


class FreeSpace:
    """No external force: isolates thrust, mass and integrator coupling (O3)."""

    name = "free_space"

    def acceleration(self, t: float, r: Any, v: Any) -> Any:
        return np.zeros(3)


def _closed_form(veh: Vehicle, t: float) -> tuple[Decimal, Decimal]:
    """Exact free-space solution along u (40-digit decimal): (delta-v, displacement).

    v = v0 + c ln(m0/m) u;  x = x0 + v0 t + c [t - (m/mdot) ln(m0/m)] u.
    """
    with localcontext() as ctx:
        ctx.prec = 40
        c = Decimal(veh.isp_s) * Decimal(STANDARD_GRAVITY)
        mdot = Decimal(veh.thrust_n) / c
        m0, tt = Decimal(veh.initial_mass_kg), Decimal(t)
        m = m0 - mdot * tt
        ln = (m0 / m).ln()
        return c * ln, c * (tt - (m / mdot) * ln)


def free_space_run(veh: Vehicle, direction: str, duration_s: float, dt: float) -> dict[str, float]:
    """O3 with the production Simulator, zero force, velocity-tracking pointing.

    The initial velocity is along u, so velocity tracking keeps the thrust direction
    fixed at +-u and the closed form applies exactly.
    """
    u = np.array([0.36, -0.48, 0.8])
    x0, v0 = np.array([1.0e6, -2.0e5, 3.0e4]), 100.0 * u
    spec = SpacecraftSpec(
        veh.dry_mass_kg, EngineSpec(veh.thrust_n, veh.isp_s), TankSpec(veh.propellant_kg)
    )
    sim = Simulator(x0, v0, FreeSpace(), RK4(), dt, spacecraft=spec)
    sim.schedule_burn(direction, ignition_t_s=0.0, duration_s=duration_s)
    cutoff = None
    while cutoff is None:
        sim.step()
        cutoff = next((tr for tr in sim.engine_transitions if tr.kind == "cutoff"), None)
    burn_t = cutoff.t  # ignition at 0: the represented burn interval
    dv, disp = _closed_form(veh, burn_t)
    sign = Decimal(SIGN[direction])
    with localcontext() as ctx:
        ctx.prec = 40
        t = Decimal(burn_t)
        v_err = [
            Decimal(cutoff.v[k]) - Decimal(v0[k]) - sign * dv * Decimal(u[k]) for k in range(3)
        ]
        x_err = [
            Decimal(cutoff.r[k]) - Decimal(x0[k]) - Decimal(v0[k]) * t - sign * disp * Decimal(u[k])
            for k in range(3)
        ]
        m_err = Decimal(cutoff.propellant_kg) - (
            Decimal(veh.propellant_kg)
            - Decimal(veh.thrust_n) / (Decimal(veh.isp_s) * Decimal(STANDARD_GRAVITY)) * t
        )
    return {
        "velocity_rel_error": math.hypot(*map(float, v_err)) / float(dv),
        "position_error_m": math.hypot(*map(float, x_err)),
        "propellant_error_kg": abs(float(m_err)),
        "displacement_m": float(disp),
    }


def free_space_metrics(veh: Vehicle, duration_s: float) -> dict[str, float]:
    out: dict[str, float] = {"velocity_rel_error_max": 0.0, "propellant_rel_error_max": 0.0}
    for direction in ("prograde", "retrograde"):
        r10 = free_space_run(veh, direction, duration_s, 10.0)
        r5 = free_space_run(veh, direction, duration_s, 5.0)
        out["velocity_rel_error_max"] = max(
            out["velocity_rel_error_max"], r10["velocity_rel_error"], r5["velocity_rel_error"]
        )
        out["propellant_rel_error_max"] = max(
            out["propellant_rel_error_max"],
            r10["propellant_error_kg"] / veh.initial_mass_kg,
            r5["propellant_error_kg"] / veh.initial_mass_kg,
        )
        order = math.log2(r10["position_error_m"] / r5["position_error_m"])
        out[f"{direction}_position_error_dt10_m"] = r10["position_error_m"]
        out[f"{direction}_position_order"] = order
    out["position_order_deviation_from_4_max"] = max(
        abs(out["prograde_position_order"] - 4.0), abs(out["retrograde_position_order"] - 4.0)
    )
    return out


# --------------------------------------------------------------- O4 DOP853 reference


def _independent_rhs(mu: float, veh: Vehicle | None, sign: float) -> Any:
    """Equations of motion written without production propulsion code (REV-T1-05).

    r' = v;  v' = -mu r/|r|^3 + sign F/(m_dry + m_p) v/|v|;  m_p' = -F/(Isp g0).
    ``sign = 0`` is a coast.
    """
    thrust = 0.0 if veh is None or sign == 0.0 else veh.thrust_n
    mdot = 0.0 if thrust == 0.0 else thrust / (veh.isp_s * STANDARD_GRAVITY)  # type: ignore[union-attr]
    dry = 0.0 if veh is None else veh.dry_mass_kg

    def f(t: float, y: np.ndarray) -> np.ndarray:
        r, vel, m_p = y[:3], y[3:6], y[6]
        a = -mu * r / math.sqrt(float(r @ r)) ** 3
        if thrust:
            a = a + (sign * thrust / (dry + m_p) / math.sqrt(float(vel @ vel))) * vel
        return np.concatenate([vel, a, [-mdot]])

    return f


def dop853_reference(
    scenario: ScenarioV2,
    r0: Sequence[float],
    v0: Sequence[float],
    predicted: Sequence[PredictedBurn],
    marks: Sequence[float],
) -> dict[float, np.ndarray]:
    """States [r, v, m_p] at each mark time, integrated segment by segment.

    Segment boundaries are the predicted ignition and cutoff times (scenario inputs),
    so no step straddles a thrust discontinuity. SciPy DOP853, rtol 1e-13, atol 1e-9
    (VAL-0008 settings).
    """
    from scipy.integrate import solve_ivp  # dev-only dependency (DR-0015)

    veh = vehicle(scenario)
    mu = scenario.constants.mu
    bounds = sorted(
        {0.0, *marks, *(b.ignition_t_s for b in predicted), *(b.cutoff_t_s for b in predicted)}
    )
    y = np.concatenate(
        [np.asarray(r0, float), np.asarray(v0, float), [0.0 if veh is None else veh.propellant_kg]]
    )
    out = {0.0: y.copy()} if 0.0 in marks else {}
    for a, b in pairwise(bounds):
        burn = next((p for p in predicted if p.ignition_t_s <= a and b <= p.cutoff_t_s), None)
        sign = 0.0 if burn is None else SIGN[burn.direction]
        sol = solve_ivp(
            _independent_rhs(mu, veh, sign), (a, b), y, method="DOP853", rtol=1e-13, atol=1e-9
        )
        if not sol.success:
            raise RuntimeError(f"DOP853 failed on [{a}, {b}]: {sol.message}")
        y = sol.y[:, -1].copy()
        if b in marks:
            out[b] = y.copy()
    return out


def reference_metrics(
    scenario: ScenarioV2, events: Sequence[Any], predicted: Sequence[PredictedBurn]
) -> tuple[dict[str, float], dict[float, np.ndarray]]:
    """O4: simulator vs DOP853 at every cutoff (BurnEnded state) and at the final tick."""
    start = events[0]
    done = events[-1]
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    marks = [b.cutoff_t_s for b in predicted if b.burn_id in ends] + [done.t]
    ref = dop853_reference(scenario, start.r, start.v, predicted, marks)
    cut_pos = cut_vel = 0.0
    for b in predicted:
        e = ends.get(b.burn_id)
        if e is None:
            continue
        y = ref[b.cutoff_t_s]
        cut_pos = max(cut_pos, float(np.linalg.norm(np.array(e.r) - y[:3])))
        cut_vel = max(cut_vel, float(np.linalg.norm(np.array(e.v) - y[3:6])))
    y = ref[done.t]
    metrics = {
        "cutoff_position_error_max_m": cut_pos,
        "cutoff_velocity_error_max_mps": cut_vel,
        "final_position_error_m": float(np.linalg.norm(np.array(done.r) - y[:3])),
        "final_velocity_error_mps": float(np.linalg.norm(np.array(done.v) - y[3:6])),
    }
    return metrics, ref


# --------------------------------------------------------------- O5 coast arcs


def coast_metrics(scenario: ScenarioV2, events: Sequence[Any]) -> dict[str, float]:
    """O5: every coast arc against exact Kepler propagation of its start state.

    Arc starts are the initial state and each cutoff state (BurnEnded). Samples are
    compared up to the next ignition. This tests the coast integration only; burn
    accuracy is O1/O2/O4.
    """
    mu = scenario.constants.mu
    start = events[0]
    arcs: list[tuple[float, np.ndarray, np.ndarray]] = [(0.0, np.array(start.r), np.array(start.v))]
    ignitions = sorted(e.event_t_s for e in _of(events, "BurnStarted"))
    for e in _of(events, "BurnEnded"):
        arcs.append((e.event_t_s, np.array(e.r), np.array(e.v)))
    arcs.sort(key=lambda a: a[0])
    samples = [(s.t, np.array(s.r), np.array(s.v)) for s in _of(events, "StateSampled")]
    pos = vel = post_pos = 0.0
    for i, (t0, r0, v0) in enumerate(arcs):
        t_end = next((t for t in ignitions if t >= t0), math.inf)
        for t, r, v in samples:
            if t0 <= t <= t_end:
                rk, vk = kepler.propagate(r0, v0, t - t0, mu)
                dp = float(np.linalg.norm(r - rk))
                pos = max(pos, dp)
                vel = max(vel, float(np.linalg.norm(v - vk)))
                if i > 0:
                    post_pos = max(post_pos, dp)
    return {
        "coast_position_error_max_m": pos,
        "coast_velocity_error_max_mps": vel,
        "post_burn_coast_position_error_max_m": post_pos,
    }


# --------------------------------------------------------------- O6 impulsive limit


def impulsive_family(scenario: ScenarioV2, levels: int = 5) -> list[dict[str, float]]:
    """Runs at fixed delta-v with burn duration T/2^k and thrust F*2^k, centred on the
    original burn midpoint (VAL-0008 method).

    Impulsive reference (textbook): Kepler-propagate the simulator's ignition state to
    the midpoint, add the rocket-equation delta-v along +-v, take the SMA.
    """
    from tars.sim.runner import run_scenario

    veh = vehicle(scenario)
    assert veh is not None and len(scenario.commands) == 1
    cmd = scenario.commands[0].command
    mu = scenario.constants.mu
    duration, ignition = float(cmd["duration_s"]), float(cmd["ignition_t_s"])
    mid = ignition + duration / 2.0
    sign = SIGN[cmd["direction"]]
    stop = math.ceil((mid + duration) / scenario.dt_s / 6.0) * 6.0 * scenario.dt_s
    rows = []
    for k in range(levels):
        scale = 2.0**k
        raw = scenario.model_dump(mode="json")
        raw["spacecraft"]["engine"]["thrust_n"] = veh.thrust_n * scale
        raw["commands"][0]["command"] = {
            **cmd,
            "command_id": f"o6-k{k}",
            "duration_s": duration / scale,
            "ignition_t_s": mid - duration / scale / 2.0,
        }
        raw["stop"] = {"duration_s": stop}
        variant = ScenarioV2.model_validate(raw)
        run = run_scenario(variant, record_samples=False)
        s = _of(run.events, "BurnStarted")[0]
        e = _of(run.events, "BurnEnded")[0]
        a0 = rv_to_elements(np.array(s.r), np.array(s.v), mu).a
        a_fin = rv_to_elements(np.array(e.r), np.array(e.v), mu).a
        r_m, v_m = kepler.propagate(np.array(s.r), np.array(s.v), mid - s.event_t_s, mu)
        m0 = veh.initial_mass_kg
        dv = veh.exhaust_velocity_mps * math.log(m0 / (m0 - veh.mass_flow_kgps * duration))
        v_imp = v_m + sign * dv * v_m / np.linalg.norm(v_m)
        a_imp = -mu / (2.0 * specific_energy(r_m, v_imp, mu))
        rows.append(
            {
                "burn_duration_s": duration / scale,
                "sma_finite_minus_impulsive_m": a_fin - a_imp,
                "sma_change_finite_m": a_fin - a0,
                "sma_change_impulsive_m": a_imp - a0,
            }
        )
    return rows


def impulsive_metrics(rows: Sequence[dict[str, float]]) -> dict[str, float]:
    orders = [
        math.log2(a["sma_finite_minus_impulsive_m"] / b["sma_finite_minus_impulsive_m"])
        for a, b in pairwise(rows)
    ]
    r0 = rows[0]
    out = {
        "order_deviation_from_2_max": max(abs(p - 2.0) for p in orders),
        "slice_sma_change_ratio_deviation": abs(
            r0["sma_change_finite_m"] / r0["sma_change_impulsive_m"] - 1.0
        ),
        "slice_finite_minus_impulsive_sma_m": r0["sma_finite_minus_impulsive_m"],
    }
    for i, p in enumerate(orders):
        out[f"order_pair_{i}"] = p
    return out


# --------------------------------------------------------------- O7 direction


def direction_metrics(scenario: ScenarioV2, events: Sequence[Any]) -> dict[str, float]:
    """O7: energy and SMA change sign per burn direction; plane unchanged.

    Prograde must raise energy and SMA, retrograde lower them. Thrust along +-v lies
    in the orbit plane, so the angular-momentum direction must not rotate beyond
    round-off. Apsides are reported (P3), not gated.
    """
    mu = scenario.constants.mu
    re = scenario.constants.equatorial_radius
    starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
    out = {
        "sign_violations": 0.0,
        "plane_rotation_max_rad": 0.0,
        "inclination_change_max_rad": 0.0,
    }
    for e in _of(events, "BurnEnded"):
        s = starts[e.burn_id]
        r0, v0, r1, v1 = (np.array(x) for x in (s.r, s.v, e.r, e.v))
        d_energy = specific_energy(r1, v1, mu) - specific_energy(r0, v0, mu)
        el0, el1 = rv_to_elements(r0, v0, mu), rv_to_elements(r1, v1, mu)
        sign = SIGN[e.direction]
        if not (sign * d_energy > 0.0 and sign * (el1.a - el0.a) > 0.0):
            out["sign_violations"] += 1.0
        h0, h1 = np.cross(r0, v0), np.cross(r1, v1)
        cosang = float(h0 @ h1) / float(np.linalg.norm(h0) * np.linalg.norm(h1))
        out["plane_rotation_max_rad"] = max(
            out["plane_rotation_max_rad"],
            float(np.linalg.norm(np.cross(h0, h1)) / (np.linalg.norm(h0) * np.linalg.norm(h1)))
            if cosang > 0
            else math.pi,
        )
        out["inclination_change_max_rad"] = max(
            out["inclination_change_max_rad"], abs(el1.i - el0.i)
        )
        tag = e.burn_id.replace("#", "")
        out[f"{tag}_sma_change_m"] = el1.a - el0.a
        out[f"{tag}_apoapsis_alt_km"] = (el1.a * (1 + el1.e) - re) / 1e3
        out[f"{tag}_periapsis_alt_km"] = (el1.a * (1 - el1.e) - re) / 1e3
    return out


# --------------------------------------------------------------- O8 convergence


def convergence_metrics(
    scenario: ScenarioV2, reference_final: np.ndarray, dts: Sequence[float] = (10.0, 5.0, 2.5)
) -> dict[str, float]:
    """O8: final-state error vs DOP853 at several dt; observed order per halving.

    The 20 -> 10 s pair is pre-asymptotic (VAL-0008/0012) and is not used. dt = 1 s
    is not used either: its error (~2e-5 m) approaches the DOP853 reference's
    cross-platform floor (11-15 um at 53 700 s, VAL-0010 addendum).
    """
    from tars.sim.runner import run_scenario

    errs = []
    for dt in dts:
        run = run_scenario(scenario.with_dt(dt), record_samples=False)
        errs.append(float(np.linalg.norm(run.final.r - reference_final[:3])))
    out = {f"position_error_dt{dt:g}_m": e for dt, e in zip(dts, errs, strict=True)}
    orders = [math.log2(a / b) for a, b in pairwise(errs)]
    for (a, b), p in zip(pairwise(dts), orders, strict=True):
        out[f"order_{a:g}_to_{b:g}"] = p
    out["order_deviation_from_4_max"] = max(abs(p - 4.0) for p in orders)
    return out


# --------------------------------------------------------------- control and boundary


def physical_projection(events: Sequence[Any]) -> list[str]:
    """Event lines that describe physics (not commands or the scenario identity)."""
    keep = ("StateSampled", "PropulsionSampled", "OrbitCompleted", *ENGINE_EVENTS)
    out = [e.model_dump_json() for e in events if e.type in keep]
    out.append(events[-1].model_dump_json())
    return out


def control_scenario(scenario: ScenarioV2, expected: Sequence[Expected]) -> ScenarioV2:
    """The same scenario with only the entries declared accepted."""
    raw = scenario.model_dump(mode="json")
    raw["commands"] = [
        c for c, exp in zip(raw["commands"], expected, strict=True) if exp.status == "accepted"
    ]
    raw["name"] += "_control"
    return ScenarioV2.model_validate(raw)


# --------------------------------------------------------------- DR-0018 boundary


@dataclass(frozen=True)
class BoundaryCase:
    """A stop-time variant of a one-burn mission (DR-0018, approved option A)."""

    name: str
    stop_s: float
    duration_s: float | None = None  # override the commanded duration


BOUNDARY_CASES = (
    BoundaryCase("stop_inside_burn", 660.0),
    BoundaryCase("stop_before_ignition", 300.0),
    BoundaryCase("stop_at_ignition", 600.0),
    BoundaryCase("stop_at_cutoff", 720.0, duration_s=120.0),
)


def boundary_variant(
    scenario: ScenarioV2, case: BoundaryCase, stop_s: float | None = None
) -> ScenarioV2:
    """The variant stopped at ``case.stop_s``, or at ``stop_s`` (the longer twin)."""
    raw = scenario.model_dump(mode="json")
    raw["name"] += f"_{case.name}"
    raw["stop"] = {"duration_s": case.stop_s if stop_s is None else stop_s}
    if case.duration_s is not None:
        raw["commands"][0]["command"] = {
            **raw["commands"][0]["command"],
            "duration_s": case.duration_s,
        }
    return ScenarioV2.model_validate(raw)


def boundary_violations(
    variant: ScenarioV2, run: RunResult, longer: RunResult, expected: Sequence[Expected]
) -> list[str]:
    """DR-0018 option A at one stop time.

    - The general contract checks hold (order, traceability, predicted lifecycle).
    - A stop never fabricates an end: a burn still active has BurnStarted only; a
      pending burn has neither event.
    - The stop is an observation boundary only: every physical event up to the stop is
      byte-identical to the same scenario observed for longer, except that the final
      tick's samples are always emitted (end block) and the longer run samples only on
      its grid.
    """
    events = run.events
    v = check_event_order(variant, events)
    v += check_traceability(variant, events, expected, run)
    predicted = predict_burns(variant, expected)
    v += check_outcomes(variant, events, predicted)
    stop_tick = events[-1].tick
    mine = [e.model_dump_json() for e in events if e.type in ("OrbitCompleted", *ENGINE_EVENTS)]
    theirs = [
        e.model_dump_json()
        for e in longer.events
        if e.tick <= stop_tick and e.type in ("OrbitCompleted", *ENGINE_EVENTS)
    ]
    if mine != theirs:
        v.append("engine/orbit events differ from the longer run up to the stop")
    longer_samples = {
        (e.type, e.tick): e.model_dump_json()
        for e in longer.events
        if e.type in ("StateSampled", "PropulsionSampled")
    }
    for e in events:
        if e.type in ("StateSampled", "PropulsionSampled"):
            twin = longer_samples.get((e.type, e.tick))
            if twin is not None and twin != e.model_dump_json():
                v.append(f"{e.type} at tick {e.tick} differs from the longer run")
    final_state = longer_samples.get(("StateSampled", stop_tick))
    if final_state is None:
        v.append("longer run has no StateSampled at the stop tick (choose a grid stop)")
    return v
