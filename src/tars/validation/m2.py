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

import dataclasses
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
from tars.events.schema import parse_event, to_jsonl
from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec, SpacecraftSpec, TankSpec
from tars.sim.runner import RunResult
from tars.sim.scenario import ScenarioV2
from tars.sim.simulator import Simulator
from tars.validation import reference_snapshot as snap
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

    ``intended_s`` is the commanded duration, or the analytic depletion time P / mdot
    for a burn_to_depletion burn that runs the tank dry. ``cutoff_t_s`` is the
    represented cutoff: fl(ignition + intended), stepped back one ulp at a time while
    it would run past depletion (DR-0017 D1a, re-implemented from the decision text).
    ``executed_s = cutoff - ignition`` is the represented interval.
    """

    burn_id: str
    command_id: str
    direction: str
    submit_tick: int
    ignition_t_s: float
    commanded_duration_s: float
    policy: str
    end_cause: str
    intended_s: float
    cutoff_t_s: float
    executed_s: float
    propellant_before_kg: float
    propellant_used_kg: float
    propellant_after_kg: float
    mass_before_kg: float
    mass_after_kg: float
    delta_v_mps: float

    @property
    def burn_time_s(self) -> float:
        return self.intended_s


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
            cause, burn_time = "completed", duration
        elif cmd.get("on_insufficient_propellant", "reject") == "burn_to_depletion":
            cause, burn_time = "propellant_depleted", depletion
        else:
            raise ValueError(f"{cmd['command_id']}: declared accepted but insufficient")
        ignition = float(cmd["ignition_t_s"])
        cutoff = ignition + burn_time
        while cutoff - ignition > depletion:  # D1a: never past depletion
            cutoff = math.nextafter(cutoff, -math.inf)
        executed = cutoff - ignition
        used = min(mdot * executed, propellant)
        after = 0.0 if used >= propellant else propellant - used  # SCI-0012
        m0 = veh.dry_mass_kg + propellant
        mf = veh.dry_mass_kg + after
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
                intended_s=burn_time,
                cutoff_t_s=cutoff,
                executed_s=executed,
                propellant_before_kg=propellant,
                propellant_used_kg=used,
                propellant_after_kg=after,
                mass_before_kg=m0,
                mass_after_kg=mf,
                delta_v_mps=c * math.log(m0 / mf),
            )
        )
        propellant = after
    if any(b.ignition_t_s < a.cutoff_t_s for a, b in pairwise(burns)):
        raise ValueError("declared accepted burns overlap")
    return _pin_burns(burns)


_BURN_TIMES = ("ignition_t_s", "commanded_duration_s", "intended_s", "cutoff_t_s", "executed_s")
_BURN_MASSES = (
    "propellant_before_kg", "propellant_used_kg", "propellant_after_kg",
    "mass_before_kg", "mass_after_kg",
)  # fmt: skip


def _pin_burns(burns: list[PredictedBurn]) -> list[PredictedBurn]:
    """The predicted burns, pinned to the approved reference snapshot (DR-0021)."""
    p = snap.pin(
        "predicted_burns",
        "ref",
        times_s=np.array([[getattr(b, f) for f in _BURN_TIMES] for b in burns]).reshape(-1, 5),
        masses_kg=np.array([[getattr(b, f) for f in _BURN_MASSES] for b in burns]).reshape(-1, 5),
        delta_v_mps=np.array([b.delta_v_mps for b in burns]),
    )
    return [
        dataclasses.replace(
            b,
            **{f: float(p["times_s"][i, j]) for j, f in enumerate(_BURN_TIMES)},
            **{f: float(p["masses_kg"][i, j]) for j, f in enumerate(_BURN_MASSES)},
            delta_v_mps=float(p["delta_v_mps"][i]),
        )
        for i, b in enumerate(burns)
    ]


def _of(events: Sequence[Any], *types: str) -> list[Any]:
    return [e for e in events if e.type in types]


def events_sha256(events: Sequence[Any]) -> str:
    return hashlib.sha256(to_jsonl(events).encode()).hexdigest()


def _ulp(x: float) -> float:
    return math.ulp(x)


def worst(*values: float) -> float:
    """Max that never discards an invalid value: any non-finite argument (NaN, +inf or
    -inf) gives +inf, so the gate fails (reviews M2-T6 F16, F18, F19, F20; builtin
    max(x, nan) returns x, and max(x, -inf) returns x)."""
    if not all(math.isfinite(v) for v in values):
        return math.inf
    return max(values)


def excess_over(err: float, allowance: float) -> float:
    """Error beyond an analytic allowance, clamped at 0. Both inputs must be finite:
    max(err - inf, 0.0) would turn any error into a pass (review M2-T6 F23)."""
    if not (math.isfinite(err) and math.isfinite(allowance)):
        return math.inf
    return max(err - allowance, 0.0)


def worst_of(values, default: float = 0.0) -> float:
    """``worst`` over an iterable (NaN anywhere gives +inf; empty gives ``default``)."""
    out: float | None = None
    for value in values:
        out = worst(value) if out is None else worst(out, value)
    return default if out is None else out


def simpson_bound(
    veh: Vehicle, burn: PredictedBurn, dt: float, until: float | None = None
) -> float:
    """Analytic RK4 truncation bound on the sensed delta-v integral [m/s].

    Sensed delta-v obeys dv/dt = f(t) = F/m(t), a function of time only, so RK4
    reduces to Simpson's rule on each sub-step h (the tick grid split at ignition and
    cutoff, DR-0013 3A). Its error is h^5/2880 |f|, with f = 24 F mdot^4 / m^5
    (largest at the sub-step's end mass). Negligible for the reference vehicle
    (5e-13 m/s), it grows as mdot^4 for the high-thrust O6 variants (VAL-0013).
    ``until`` truncates the burn at a sample time.
    """
    end = burn.cutoff_t_s if until is None else min(until, burn.cutoff_t_s)
    total = 0.0
    if end > burn.ignition_t_s:
        total = _simpson_total(veh, burn, dt, end)
    # The window is pinned with the bound so the baseline can be recomputed (F53).
    p = snap.pin("simpson_bound", "ref", bound_mps=[total], window_s=[burn.ignition_t_s, end])
    return float(p["bound_mps"][0])


def _simpson_total(veh: Vehicle, burn: PredictedBurn, dt: float, end: float) -> float:
    mdot = veh.mass_flow_kgps
    first = math.ceil(burn.ignition_t_s / dt)
    grid = [k * dt for k in range(first, math.floor(end / dt) + 1)]
    pts = sorted({burn.ignition_t_s, end, *(g for g in grid if burn.ignition_t_s < g < end)})
    total = 0.0
    for a, b in pairwise(pts):
        m_end = burn.mass_before_kg - mdot * (b - burn.ignition_t_s)
        total += (b - a) ** 5 / 2880.0 * 24.0 * veh.thrust_n * mdot**4 / m_end**5
    return total


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
        # Schema contract (review F18): integer version 1 and a strict re-validation of
        # the serialized event, which in-memory copies could otherwise bypass.
        if type(e.schema_version) is not int or e.schema_version != 1:
            v.append(f"event {i} {e.type}: schema_version {e.schema_version!r}")
        try:
            if parse_event(e.model_dump_json()) != e:
                v.append(f"event {i} {e.type}: does not round-trip through the schema")
        except ValueError as err:
            v.append(f"event {i} {e.type}: invalid against the schema ({type(err).__name__})")
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
        if (
            b.type == "BurnEnded"
            and b.end_cause == "propellant_depleted"
            and not (
                a.type == "PropellantDepleted"
                and (a.burn_id, a.command_id, a.event_t_s) == (b.burn_id, b.command_id, b.event_t_s)
            )
        ):
            v.append(f"event {i + 1}: depleted BurnEnded without its PropellantDepleted")
    if events and events[0].type == "BurnEnded" and events[0].end_cause == "propellant_depleted":
        v.append("depleted BurnEnded without its PropellantDepleted")

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


def expected_submissions(scenario: ScenarioV2, events: Sequence[Any]) -> int:
    """Number of timeline entries the contract says were submitted, from the timeline.

    Entries due at tick k are submitted only if the run continues past k (contract
    "Emission order"). A non-finite step at k + 1 fails after the tick-k submissions,
    so for that cause entries due at the final tick were submitted too.
    """
    done = events[-1]
    final = done.tick
    inclusive = done.failure_cause == "non_finite"
    ticks = [scenario.submit_tick(e) for e in scenario.commands]
    return sum(k < final or (inclusive and k == final) for k in ticks)


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
    # The submitted count is derived from the timeline, not from the runner's own
    # unsubmitted list; that list is then checked against the remainder.
    n = expected_submissions(scenario, events)
    if len(receipts) != n:
        v.append(f"{len(receipts)} receipts, {n} timeline entries due before the end")
    rest = [e.command.get("command_id") for e in entries[n:]]
    rest = [c if isinstance(c, str) else None for c in rest]
    if list(result.unsubmitted_command_ids) != rest:
        v.append(f"unsubmitted {result.unsubmitted_command_ids}, expected {rest}")
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
    # The predicted lifecycle uses the scenario's stop time, not the log's final time.
    stop_t = scenario.stop.duration_s if scenario.stop.duration_s is not None else done.t
    if done.t != stop_t:
        v.append(f"run ended at {done.t!r}, scenario stop {stop_t!r}")
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
        thrust_rel = worst(thrust_rel, abs(float(np.linalg.norm(a)) - want) / want)
        st = states.get(p.tick)
        if st is not None and p.active_burn_id in starts:
            sign = SIGN[starts[p.active_burn_id].direction]
            u = sign * np.array(st.v) / np.linalg.norm(st.v)
            dir_err = worst(dir_err, float(np.linalg.norm(a / np.linalg.norm(a) - u)))
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
    o2 = {
        "sensed_delta_v_rel_error_max": 0.0,
        "sensed_delta_v_excess_over_simpson_rel_max": 0.0,
        "reported_rocket_equation_rel_error_max": 0.0,
    }
    v: list[str] = []
    for b in predicted:
        e = ends.get(b.burn_id)
        if e is None:
            continue
        o1["propellant_used_rel_error_max"] = worst(
            o1["propellant_used_rel_error_max"],
            abs(e.propellant_used_kg - b.propellant_used_kg) / m0_total,
        )
        if b.end_cause == "propellant_depleted":
            bound = veh.mass_flow_kgps * 2.0 * _ulp(b.cutoff_t_s)
            # F26: a ratio to a non-finite or non-positive bound is not evidence.
            ratio = e.propellant_kg / bound if math.isfinite(bound) and bound > 0.0 else math.inf
            o1["depletion_residual_over_bound_max"] = worst(
                o1["depletion_residual_over_bound_max"], ratio
            )
            if e.propellant_kg < 0.0:
                v.append(f"{b.burn_id}: negative residual")
        err = abs(e.sensed_delta_v_mps - b.delta_v_mps)
        o2["sensed_delta_v_rel_error_max"] = worst(
            o2["sensed_delta_v_rel_error_max"], err / b.delta_v_mps
        )
        # Gated: the error beyond the analytic Simpson truncation bound (round-off).
        o2["sensed_delta_v_excess_over_simpson_rel_max"] = worst(
            o2["sensed_delta_v_excess_over_simpson_rel_max"],
            excess_over(err, simpson_bound(veh, b, scenario.dt_s)) / b.delta_v_mps,
        )
        o2["reported_rocket_equation_rel_error_max"] = worst(
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
        dv, disp = c * ln, c * (tt - (m / mdot) * ln)
    # Decimal arithmetic is platform independent: pinned exactly, used as computed.
    snap.pin("o3.closed_form", "ref", exact=True, dv_mps=[float(dv)], disp_m=[float(disp)])
    return dv, disp


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
    ignition = cutoff = None
    while cutoff is None and sim.tick * dt <= duration_s + 2 * dt:
        sim.step()
        for tr in sim.engine_transitions:
            if tr.kind == "ignition":
                ignition = tr
            elif tr.kind == "cutoff":
                cutoff = tr
    # The expectation uses the requested interval [0, duration], never the reported
    # cutoff time; the reported times must equal it exactly (review F5).
    burn_t = duration_s
    timing = 0.0
    if ignition is None or cutoff is None or ignition.t != 0.0 or cutoff.t != burn_t:
        timing = 1.0
        if cutoff is None:
            return {"timing_violations": 1.0, "velocity_rel_error": math.inf,
                    "position_error_m": math.inf, "propellant_error_kg": math.inf,
                    "displacement_m": 0.0}  # fmt: skip
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
        m_exp = (
            Decimal(veh.propellant_kg)
            - Decimal(veh.thrust_n) / (Decimal(veh.isp_s) * Decimal(STANDARD_GRAVITY)) * t
        )
        m_err = Decimal(cutoff.propellant_kg) - m_exp
        v_exp = [Decimal(v0[k]) + sign * dv * Decimal(u[k]) for k in range(3)]
        x_exp = [
            Decimal(x0[k]) + Decimal(v0[k]) * t + sign * disp * Decimal(u[k]) for k in range(3)
        ]
    snap.pin(
        "o3.expected_cutoff",
        "ref",
        exact=True,
        v_mps=[float(x) for x in v_exp],
        r_m=[float(x) for x in x_exp],
        propellant_kg=[float(m_exp)],
        start_r_m=x0,
        start_v_mps=v0,
        duration_s=[burn_t],
    )
    return {
        "timing_violations": timing,
        "velocity_rel_error": math.hypot(*map(float, v_err)) / float(dv),
        "position_error_m": math.hypot(*map(float, x_err)),
        "propellant_error_kg": abs(float(m_err)),
        "displacement_m": float(disp),
    }


def free_space_metrics(veh: Vehicle, duration_s: float) -> dict[str, float]:
    out: dict[str, float] = {
        "velocity_rel_error_max": 0.0,
        "propellant_rel_error_max": 0.0,
        "timing_violations": 0.0,
    }
    for direction in ("prograde", "retrograde"):
        with snap.scope("o3_free_space", direction):
            r10 = free_space_run(veh, direction, duration_s, 10.0)
            r5 = free_space_run(veh, direction, duration_s, 5.0)
        out["timing_violations"] += r10["timing_violations"] + r5["timing_violations"]
        out["velocity_rel_error_max"] = worst(
            out["velocity_rel_error_max"], r10["velocity_rel_error"], r5["velocity_rel_error"]
        )
        out["propellant_rel_error_max"] = worst(
            out["propellant_rel_error_max"],
            r10["propellant_error_kg"] / veh.initial_mass_kg,
            r5["propellant_error_kg"] / veh.initial_mass_kg,
        )
        order = math.log2(r10["position_error_m"] / r5["position_error_m"])
        out[f"{direction}_position_error_dt10_m"] = r10["position_error_m"]
        out[f"{direction}_position_order"] = order
    out["position_order_deviation_from_4_max"] = worst(
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


class Reference(dict):
    """Reference states by mark time, plus the reference's altitude extrema over every
    tick of the executed grid (review M2-T5 F17)."""

    alt_min: float = math.inf
    alt_max: float = -math.inf


def mass_law_propellant(t: float, veh: Vehicle | None, predicted: Sequence[PredictedBurn]) -> float:
    """Analytic propellant at t from the scenario inputs (mass law, burns in order)."""
    if veh is None:
        return 0.0
    prop = veh.propellant_kg
    for b in predicted:
        if t <= b.ignition_t_s:
            break
        if t >= b.cutoff_t_s:
            prop = b.propellant_after_kg
            continue
        return b.propellant_before_kg - veh.mass_flow_kgps * (t - b.ignition_t_s)
    return prop


def _check_reference_states(
    times, states, veh: Vehicle | None, predicted: Sequence[PredictedBurn], where: str
) -> None:
    """Every reference state component is finite, and the reference propellant is
    non-negative and on the analytic mass law to the O1 round-off class (reviews
    M2-T6 F16, F29, F31). An invalid reference never reaches a comparison."""
    states = np.atleast_2d(states)
    if not np.all(np.isfinite(states)):
        raise RuntimeError(f"DOP853 produced a non-finite state on {where}")
    times = np.atleast_1d(np.asarray(times, dtype=float))
    if not np.all(np.isfinite(times)):  # F34: a NaN time would make the law check NaN
        raise RuntimeError(f"DOP853 produced a non-finite time on {where}")
    tol = 1e-12 * (veh.initial_mass_kg if veh is not None else 1.0)
    for t, m_p in zip(times, states[6], strict=True):
        err = abs(m_p - mass_law_propellant(float(t), veh, predicted))
        if not (m_p >= 0.0 and err <= tol):  # NaN-safe: any NaN fails
            raise RuntimeError(f"DOP853 reference propellant {m_p!r} invalid at t={t!r} ({where})")


# Reference self-consistency tolerances (not Proof gates). Measured residuals: 9e-16
# (Kepler invariants) and 2.6e-10 (dense velocity vs its position derivative). The
# limits sit far above round-off and far below any physical corruption.
KEPLER_INVARIANT_REL_TOL = 1e-12
KEPLER_ROUNDTRIP_REL_TOL = 1e-10  # measured 8.1e-14
DENSE_VELOCITY_REL_TOL = 1e-8
DENSE_TERMINAL_REL_TOL = 1e-12


def kepler_state(r0, v0, dt: float, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Kepler propagation whose output is validated (reviews M2-T6 F30, F36): it must be
    finite and conserve two-body energy and angular momentum (vector) relative to the
    input state. Otherwise every component becomes +inf, so any comparison fails. A
    finite but physically wrong position or velocity cannot pass silently."""
    r, v = kepler.propagate(r0, v0, dt, mu)
    r0, v0 = np.asarray(r0, float), np.asarray(v0, float)
    bad = (np.full(3, math.inf), np.full(3, math.inf))
    if not (np.all(np.isfinite(r)) and np.all(np.isfinite(v))):
        return bad
    e0, e1 = specific_energy(r0, v0, mu), specific_energy(r, v, mu)
    h0, h1 = np.cross(r0, v0), np.cross(r, v)
    e_err = abs(e1 - e0) / abs(e0)
    h_err = float(np.linalg.norm(h1 - h0)) / float(np.linalg.norm(h0))
    if not (e_err <= KEPLER_INVARIANT_REL_TOL and h_err <= KEPLER_INVARIANT_REL_TOL):
        return bad
    # F38: invariants do not fix the orbital phase; propagating back by -dt must
    # recover the input state, which pins the time of flight.
    rb, vb = kepler.propagate(r, v, -dt, mu)
    r_err = float(np.linalg.norm(rb - r0)) / float(np.linalg.norm(r0))
    v_err = float(np.linalg.norm(vb - v0)) / float(np.linalg.norm(v0))
    if not (r_err <= KEPLER_ROUNDTRIP_REL_TOL and v_err <= KEPLER_ROUNDTRIP_REL_TOL):
        return bad
    return r, v


def _check_solver_nodes(sol, where: str) -> None:
    """The interpolant reproduces every solver node, so interior nodes and the dense
    trajectory cannot be corrupted independently (reviews M2-T6 F39, F40; measured
    residual 0). Run for every segment, with or without telemetry ticks (F45)."""
    nodes = sol.sol(sol.t)
    scale = np.maximum(np.abs(sol.y), 1.0)
    if not within(np.abs(nodes - sol.y), DENSE_TERMINAL_REL_TOL * scale):  # finite-safe
        raise RuntimeError(f"DOP853 dense output disagrees with its solver nodes on {where}")


DENSE_STENCIL_VELOCITY_REL_TOL = 1e-5  # velocity changes ~1.2e-6 relative over 1 ms


def _check_dense_consistency(
    sol, ticks, dense, terminal, b: float, where: str, veh=None, predicted=()
) -> None:
    """Dense velocities agree with a central difference of the dense position, the
    stencil states are valid reference states, and the dense state at the segment end
    equals the terminal state (reviews M2-T6 F35, F39, F44)."""
    step = 1e-3
    a = float(sol.t[0])
    # Stencil points inside the segment's domain (no extrapolation past its ends).
    lo, hi = np.maximum(ticks - step, a), np.minimum(ticks + step, b)
    plus, minus = sol.sol(hi), sol.sol(lo)
    for t_s, st in ((hi, plus), (lo, minus)):
        # Finite, mass law (F44), and velocity continuous with the tick's velocity.
        _check_reference_states(t_s, st, veh, predicted, f"stencil {where}")
        speed = np.linalg.norm(dense[3:6], axis=0)
        dv = np.linalg.norm(st[3:6] - dense[3:6], axis=0)
        if not within(dv, DENSE_STENCIL_VELOCITY_REL_TOL * speed):
            raise RuntimeError(f"DOP853 stencil velocity inconsistent on {where}")
    # Central difference about the stencil midpoint (second order even where the
    # stencil is clipped to the segment), compared with the velocity there.
    mid_t = 0.5 * (hi + lo)
    mid = sol.sol(mid_t)
    _check_reference_states(mid_t, mid, veh, predicted, f"stencil midpoint {where}")
    fd = (plus[:3] - minus[:3]) / (hi - lo)
    speed = np.linalg.norm(mid[3:6], axis=0)
    err = np.linalg.norm(mid[3:6] - fd, axis=0)
    if not within(err, DENSE_VELOCITY_REL_TOL * speed):  # finite-safe (F48)
        raise RuntimeError(f"DOP853 dense velocity inconsistent with its position on {where}")
    if ticks[-1] == b:
        end = dense[:, -1]
        if not within(
            np.abs(end - terminal), DENSE_TERMINAL_REL_TOL * np.maximum(np.abs(terminal), 1.0)
        ):
            raise RuntimeError(f"DOP853 dense output disagrees with the terminal state on {where}")


# Independent anchors for every DOP853 segment (review M2-T6 F47). Measured residuals:
# coast segment end vs Kepler <= 2.9e-9 m and 2.9e-12 m/s; burn segment end vs the
# fixed-step RK4 below (h = 0.01 s) <= 3.8e-8 m, 1.1e-10 m/s and 1.5e-10 kg (RK4
# round-off over up to 12 500 steps). The per-segment limits keep the cumulative drift
# over ~900 coast segments (~1e-4 m) and a few burns far below every Proof limit.
# Every consumed anchor tick is also reconciled with the DOP853 dense output with the
# same limits (review F49); measured tick residuals <= 2.8e-8 m (coast, 15 362 segment
# maxima) and 2.4e-8 m (burn, 299).
ANCHOR_POS_TOL_M = 1e-7
ANCHOR_VEL_TOL_MPS = 1e-10
ANCHOR_BURN_POS_TOL_M = 1e-6
ANCHOR_BURN_VEL_TOL_MPS = 1e-9
ANCHOR_BURN_MASS_TOL_KG = 1e-9
ANCHOR_BURN_STEP_S = 0.01


def within(err, bound) -> bool:
    """err <= bound elementwise with both finite: inf <= tol * inf, or NaN, never
    passes a tolerance check (review M2-T6 F48)."""
    err, bound = np.asarray(err, dtype=float), np.asarray(bound, dtype=float)
    return bool(np.all(np.isfinite(err) & np.isfinite(bound) & (err <= bound)))


def _rk4_path(f, y: np.ndarray, times: Sequence[float]) -> list[np.ndarray]:
    """Fixed-step RK4 written here, independent of SciPy: states at each time in
    ``times`` (first is the start), with steps <= ANCHOR_BURN_STEP_S."""
    out = [y.copy()]
    for a, b in pairwise(times):
        n = max(1, math.ceil((b - a) / ANCHOR_BURN_STEP_S))
        h, t = (b - a) / n, a
        for _ in range(n):
            k1 = f(t, y)
            k2 = f(t + h / 2, y + h / 2 * k1)
            k3 = f(t + h / 2, y + h / 2 * k2)
            k4 = f(t + h, y + h * k3)
            y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            t = a + (b - a) * (_ + 1) / n
        out.append(y.copy())
    return out


def _anchor_segment(mu, veh, sign, y_a, y_b, a, b, ticks, where) -> tuple[np.ndarray, np.ndarray]:
    """Check the DOP853 segment end against an independent propagation from the
    segment start; return the anchor's positions at ``ticks`` and its end state
    (review F47)."""
    ticks = np.asarray(ticks, dtype=float)
    if sign == 0.0:
        r_b, v_b = kepler_state(y_a[:3], y_a[3:6], b - a, mu)
        ok = within(np.linalg.norm(y_b[:3] - r_b), ANCHOR_POS_TOL_M) and within(
            np.linalg.norm(y_b[3:6] - v_b), ANCHOR_VEL_TOL_MPS
        )
        if not ok:
            raise RuntimeError(f"DOP853 coast segment end disagrees with Kepler on {where}")
        rows = [kepler_state(y_a[:3], y_a[3:6], float(t) - a, mu)[0] for t in ticks]
        anchor_end = np.concatenate([r_b, v_b])
    else:
        path = _rk4_path(_independent_rhs(mu, veh, sign), y_a.copy(), [a, *ticks.tolist(), b])
        end = path[-1]
        ok = (
            within(np.linalg.norm(y_b[:3] - end[:3]), ANCHOR_BURN_POS_TOL_M)
            and within(np.linalg.norm(y_b[3:6] - end[3:6]), ANCHOR_BURN_VEL_TOL_MPS)
            and within(abs(y_b[6] - end[6]), ANCHOR_BURN_MASS_TOL_KG)
        )
        if not ok:
            raise RuntimeError(f"DOP853 burn segment end disagrees with the RK4 anchor on {where}")
        rows = [st[:3] for st in path[1:-1]]
        anchor_end = end[:7].copy()
    tick_r = np.array(rows, dtype=float).reshape(-1, 3)
    if not np.all(np.isfinite(tick_r)):
        raise RuntimeError(f"anchor positions non-finite on {where}")
    return tick_r, anchor_end


def dop853_reference(
    scenario: ScenarioV2,
    r0: Sequence[float],
    v0: Sequence[float],
    predicted: Sequence[PredictedBurn],
    marks: Sequence[float],
) -> Reference:
    """States [r, v, m_p] at each mark time, integrated segment by segment.

    Segment boundaries are the predicted ignition and cutoff times (scenario inputs),
    so no step straddles a thrust discontinuity. SciPy DOP853, rtol 1e-13, atol 1e-9
    (VAL-0008 settings). The altitude at every tick k*dt up to the last mark is taken
    from each segment's dense output (7th-order interpolant).
    """
    from scipy.integrate import solve_ivp  # dev-only dependency (DR-0015)

    veh = vehicle(scenario)
    mu = scenario.constants.mu
    # Integrate only up to the last requested time: a burn predicted to end after an
    # observation stop must not extend the reference (or its extrema) past it.
    horizon = max(marks)
    # Segments never exceed the telemetry interval, the length the per-segment anchor
    # tolerances were measured for (review M2-T6 F47): split at every grid time.
    grid = scenario.telemetry.sample_interval_s
    grid_times = [k * grid for k in range(1, math.floor(horizon / grid) + 1)]
    bounds = sorted(
        t
        for t in {
            0.0,
            *marks,
            *grid_times,
            *(b.ignition_t_s for b in predicted),
            *(b.cutoff_t_s for b in predicted),
        }
        if t <= horizon
    )
    y = np.concatenate(
        [np.asarray(r0, float), np.asarray(v0, float), [0.0 if veh is None else veh.propellant_kg]]
    )
    # DR-0021: every evaluation time and consumed output is pinned to the approved
    # reference snapshot; inside a Proof session the approved values are used.
    snap.pin("dop853.bounds", "ref", exact=True, bounds_s=bounds)
    p = snap.pin("dop853.start", "ref", r_m=y[:3], v_mps=y[3:6], propellant_kg=y[6:])
    y = np.concatenate([p["r_m"], p["v_mps"], p["propellant_kg"]])
    out = Reference()
    if 0.0 in marks:
        out[0.0] = y.copy()
    dt, radius = scenario.dt_s, scenario.constants.equatorial_radius
    alt0 = float(np.linalg.norm(y[:3])) - radius
    out.alt_min = out.alt_max = alt0
    for a, b in pairwise(bounds):
        burn = next((p for p in predicted if p.ignition_t_s <= a and b <= p.cutoff_t_s), None)
        sign = 0.0 if burn is None else SIGN[burn.direction]
        y_start = y.copy()
        sol = solve_ivp(
            _independent_rhs(mu, veh, sign),
            (a, b),
            y,
            method="DOP853",
            rtol=1e-13,
            atol=1e-9,
            dense_output=True,
        )
        if not sol.success:
            raise RuntimeError(f"DOP853 failed on [{a}, {b}]: {sol.message}")
        y = sol.y[:, -1].copy()
        # F34: solver times are finite, strictly increasing and span exactly [a, b].
        st = np.asarray(sol.t, dtype=float)
        if not (
            np.all(np.isfinite(st)) and np.all(np.diff(st) > 0.0) and st[0] == a and st[-1] == b
        ):
            raise RuntimeError(f"DOP853 solver times invalid on [{a}, {b}]")
        _check_reference_states(sol.t, sol.y, veh, predicted, f"[{a}, {b}]")
        if not np.array_equal(sol.y[:, 0], y_start):  # the segment starts where asked
            raise RuntimeError(f"DOP853 first node differs from the segment start on [{a}, {b}]")
        _check_solver_nodes(sol, f"[{a}, {b}]")  # every segment (F45)
        ticks = np.arange(math.floor(a / dt) + 1, math.floor(b / dt) + 1) * dt
        ticks = ticks[(ticks > a) & (ticks <= b)]
        # The tick grid is pinned exactly as its index range: ticks are k * dt for
        # every k in it, bit for bit (DR-0021 evaluation times).
        k0 = math.floor(a / dt) + 1
        idx = np.round(ticks / dt).astype(np.int64)
        k_first, k_last = (int(idx[0]), int(idx[-1])) if ticks.size else (k0, k0 - 1)
        if not np.array_equal(ticks, np.arange(k_first, k_last + 1) * dt):
            raise RuntimeError(f"tick grid is not k * dt on [{a}, {b}]")
        snap.pin("dop853.ticks", "ref", exact=True, index_1=[k_first, k_last], dt_s=[dt])
        if ticks.size:
            dense = sol.sol(ticks)
            # F18/F29: the complete dense-output state is validated, not only altitude.
            _check_reference_states(ticks, dense, veh, predicted, f"dense output [{a}, {b}]")
            # F35: the dense velocity is the derivative of the dense position, and the
            # dense state at the segment end is the integrator's terminal state.
            _check_dense_consistency(sol, ticks, dense, y, b, f"[{a}, {b}]", veh, predicted)
        # F47: every segment end is anchored independently of SciPy, and the tick
        # radii used for the altitude extrema come from the anchor, not from the dense
        # output: exact Kepler on coasts, the RK4 above during burns.
        tick_r, anchor_end = _anchor_segment(mu, veh, sign, y_start, y, a, b, ticks, f"[{a}, {b}]")
        if tick_r.size:
            # F49: every consumed anchor tick agrees with the validated dense output, so
            # the two independent references (Kepler/RK4 and DOP853) must both be
            # corrupted, consistently, to move an extremum.
            tol = ANCHOR_POS_TOL_M if sign == 0.0 else ANCHOR_BURN_POS_TOL_M
            if not within(np.linalg.norm(tick_r - dense[:3].T, axis=1), tol):
                raise RuntimeError(f"anchor tick positions disagree with DOP853 on [{a}, {b}]")
        # DR-0021: the segment end (the next segment's start and any mark), the dense
        # and anchor tick positions and the anchor end are pinned; the approved values
        # are used from here on (the extrema and every later segment).
        p = snap.pin(
            "dop853.segment",
            "ref",
            end_r_m=y[:3],
            end_v_mps=y[3:6],
            end_propellant_kg=y[6:],
            anchor_ticks_m=tick_r,
            anchor_end_r_m=anchor_end[:3],
            anchor_end_v_mps=anchor_end[3:6],
            anchor_end_propellant_kg=anchor_end[6:],  # empty on coasts (Kepler)
        )
        y = np.concatenate([p["end_r_m"], p["end_v_mps"], p["end_propellant_kg"]])
        tick_r = p["anchor_ticks_m"]
        if tick_r.size:
            alts = np.linalg.norm(tick_r, axis=1) - radius
            out.alt_min = -worst(-out.alt_min, -float(alts.min()))
            out.alt_max = worst(out.alt_max, float(alts.max()))
        if b in marks:
            out[b] = y.copy()
    ext = snap.pin("dop853.extrema", "ref", altitude_m=[out.alt_min, out.alt_max])["altitude_m"]
    out.alt_min, out.alt_max = float(ext[0]), float(ext[1])
    return out


def expected_initial_state(scenario: ScenarioV2) -> tuple[np.ndarray, np.ndarray]:
    """Circular-orbit initial state from the scenario elements (textbook rotation).

    r = R (cos W cos u - sin W sin u cos i, sin W cos u + cos W sin u cos i, sin u sin i)
    v = sqrt(mu/R) (-cos W sin u - sin W cos u cos i, -sin W sin u + cos W cos u cos i,
                    cos u sin i)
    with R = equatorial radius + altitude, W = RAAN, u = argument of latitude.
    Written independently of tars.astro.elements (review M2-T5 F1).
    """
    orbit, c = scenario.initial_orbit, scenario.constants
    radius = c.equatorial_radius + orbit.altitude_m
    inc, raan, u = (
        math.radians(orbit.inclination_deg),
        math.radians(orbit.raan_deg),
        math.radians(orbit.arg_latitude_deg),
    )
    cw, sw, cu, su, ci, si = (
        math.cos(raan), math.sin(raan), math.cos(u), math.sin(u), math.cos(inc), math.sin(inc)
    )  # fmt: skip
    speed = math.sqrt(c.mu / radius)
    r = radius * np.array([cw * cu - sw * su * ci, sw * cu + cw * su * ci, su * si])
    v = speed * np.array([-cw * su - sw * cu * ci, -sw * su + cw * cu * ci, cu * si])
    p = snap.pin("initial_state", "ref", r_m=r, v_mps=v)
    return p["r_m"], p["v_mps"]


def horizon_s(scenario: ScenarioV2, events: Sequence[Any]) -> float:
    """The requested end time: the scenario's duration stop (review M2-T5 F2)."""
    return scenario.stop.duration_s if scenario.stop.duration_s is not None else events[-1].t


_O4_KEYS = (
    "initial_position_rel_error", "initial_velocity_rel_error",
    "ignition_position_error_max_m", "ignition_velocity_error_max_mps",
    "thrust_direction_vs_reference_max", "cutoff_position_error_max_m",
    "cutoff_velocity_error_max_mps", "sample_position_error_max_m",
    "sample_velocity_error_max_mps", "final_position_error_m", "final_velocity_error_mps",
)  # fmt: skip


def reference_metrics(
    scenario: ScenarioV2, events: Sequence[Any], predicted: Sequence[PredictedBurn]
) -> tuple[dict[str, float], dict[float, np.ndarray]]:
    """O4: simulator vs DOP853 seeded from the independently derived initial state.

    Compared: the initial state, every cutoff (BurnEnded), every StateSampled (coast
    and powered), and the final state at the scenario's requested horizon. A log that
    ends early is compared at the horizon's reference state and fails.
    """
    start = events[0]
    done = events[-1]
    r0, v0 = expected_initial_state(scenario)
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    samples = _of(events, "StateSampled")
    end_t = horizon_s(scenario, events)
    starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
    burning = [p for p in _of(events, "PropulsionSampled") if p.engine_state == "burning"]
    marks = sorted(
        {b.cutoff_t_s for b in predicted if b.burn_id in ends}
        | {b.ignition_t_s for b in predicted if b.burn_id in starts}
        | {s.t for s in samples}
        | {p.t for p in burning}
        | {end_t}
    )
    ref = dop853_reference(scenario, r0, v0, predicted, marks)
    if any(not np.all(np.isfinite(ref[t])) for t in marks):  # F16: invalid reference
        return {k: math.inf for k in _O4_KEYS}, ref
    ign_pos = ign_vel = 0.0
    for b in predicted:
        st = starts.get(b.burn_id)
        if st is None:
            continue
        y = ref[b.ignition_t_s]
        ign_pos = worst(ign_pos, float(np.linalg.norm(np.array(st.r) - y[:3])))
        ign_vel = worst(ign_vel, float(np.linalg.norm(np.array(st.v) - y[3:6])))
    # Thrust direction at every burning sample against the reference velocity (F10).
    direction = 0.0
    for p in burning:
        a = np.array(p.thrust_acceleration_mps2)
        st = starts.get(p.active_burn_id)
        norm = float(np.linalg.norm(a))
        if st is None or norm == 0.0:
            direction = math.pi
            continue
        u = SIGN[st.direction] * ref[p.t][3:6] / np.linalg.norm(ref[p.t][3:6])
        direction = worst(direction, float(np.linalg.norm(a / norm - u)))
    cut_pos = cut_vel = 0.0
    for b in predicted:
        e = ends.get(b.burn_id)
        if e is None:
            continue
        y = ref[b.cutoff_t_s]
        cut_pos = worst(cut_pos, float(np.linalg.norm(np.array(e.r) - y[:3])))
        cut_vel = worst(cut_vel, float(np.linalg.norm(np.array(e.v) - y[3:6])))
    traj_pos = traj_vel = 0.0
    for smp in samples:
        y = ref[smp.t]
        traj_pos = worst(traj_pos, float(np.linalg.norm(np.array(smp.r) - y[:3])))
        traj_vel = worst(traj_vel, float(np.linalg.norm(np.array(smp.v) - y[3:6])))
    y = ref[end_t]
    metrics = {
        "initial_position_rel_error": float(np.linalg.norm(np.array(start.r) - r0))
        / float(np.linalg.norm(r0)),
        "initial_velocity_rel_error": float(np.linalg.norm(np.array(start.v) - v0))
        / float(np.linalg.norm(v0)),
        "ignition_position_error_max_m": ign_pos,
        "ignition_velocity_error_max_mps": ign_vel,
        "thrust_direction_vs_reference_max": direction,
        "cutoff_position_error_max_m": cut_pos,
        "cutoff_velocity_error_max_mps": cut_vel,
        "sample_position_error_max_m": traj_pos,
        "sample_velocity_error_max_mps": traj_vel,
        "final_position_error_m": float(np.linalg.norm(np.array(done.r) - y[:3])),
        "final_velocity_error_mps": float(np.linalg.norm(np.array(done.v) - y[3:6])),
    }
    return metrics, ref


def check_final_consistency(events: Sequence[Any], result: RunResult) -> list[str]:
    """The end of the log tells one story (review M2-T5 F3): SimulationCompleted, the
    final StateSampled, RunResult.final, the last PropulsionSampled and
    RunResult.final_propulsion all describe the same final tick."""
    v: list[str] = []
    done = events[-1]
    last_state = _of(events, "StateSampled")[-1]
    if last_state.tick != done.tick or (last_state.r, last_state.v) != (done.r, done.v):
        v.append("SimulationCompleted state differs from the final StateSampled")
    final = result.final
    if final is None or (final.tick, tuple(final.r), tuple(final.v)) != (
        done.tick,
        tuple(done.r),
        tuple(done.v),
    ):
        v.append("RunResult.final differs from SimulationCompleted")
    props = _of(events, "PropulsionSampled")
    fp = result.final_propulsion
    if (fp is None) != (not props):
        v.append("final propulsion presence differs between log and result")
    elif fp is not None:
        last = props[-1]
        got = (
            last.tick,
            last.propellant_kg,
            last.total_mass_kg,
            last.delta_v_sensed_mps,
            last.engine_state,
            last.active_burn_id,
            tuple(last.pending_burn_ids),
        )
        want = (
            fp.tick,
            fp.propellant_kg,
            fp.total_mass_kg,
            fp.delta_v_sensed_mps,
            str(fp.engine_state),
            fp.active_burn_id,
            tuple(fp.pending_burn_ids),
        )
        if got != want or last.tick != done.tick:
            v.append(f"last PropulsionSampled {got} differs from final_propulsion {want}")
    return v


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
        arc = [(t, r, v) for t, r, v in samples if t0 <= t <= t_end]
        kep = [kepler_state(r0, v0, t - t0, mu) for t, _, _ in arc]
        # DR-0021: seeded by simulator output, so verified against the snapshot within
        # the sim-seeded tolerance, not substituted (margin_problems covers the gates).
        p = snap.pin(
            "o5.kepler",
            "sim",
            seed_r_m=r0,
            seed_v_mps=v0,
            flight_s=[t - t0 for t, _, _ in arc],
            r_m=np.array([k[0] for k in kep]).reshape(-1, 3),
            v_mps=np.array([k[1] for k in kep]).reshape(-1, 3),
        )
        for (_, r, v), rk, vk in zip(arc, p["r_m"], p["v_mps"], strict=True):
            dp = float(np.linalg.norm(r - rk))
            pos = worst(pos, dp)
            vel = worst(vel, float(np.linalg.norm(v - vk)))
            if i > 0:
                post_pos = worst(post_pos, dp)
    return {
        "coast_position_error_max_m": pos,
        "coast_velocity_error_max_mps": vel,
        "post_burn_coast_position_error_max_m": post_pos,
    }


# --------------------------------------------------------------- O6 impulsive limit


def impulsive_variants(scenario: ScenarioV2, levels: int = 5) -> list[ScenarioV2]:
    """Runs at fixed delta-v with burn duration T/2^k and thrust F*2^k, centred on the
    original burn midpoint (VAL-0008 method). Each variant stops on the telemetry grid
    after its burn and is audited like a reference mission (review F6)."""
    veh = vehicle(scenario)
    assert veh is not None and len(scenario.commands) == 1
    cmd = scenario.commands[0].command
    duration, ignition = float(cmd["duration_s"]), float(cmd["ignition_t_s"])
    mid = ignition + duration / 2.0
    grid = scenario.telemetry.sample_interval_s
    stop = math.ceil((mid + duration) / grid) * grid
    out = []
    for k in range(levels):
        scale = 2.0**k
        raw = scenario.model_dump(mode="json")
        raw["name"] += f"_o6_k{k}"
        raw["spacecraft"]["engine"]["thrust_n"] = veh.thrust_n * scale
        raw["commands"][0]["command"] = {
            **cmd,
            "command_id": f"o6-k{k}",
            "duration_s": duration / scale,
            "ignition_t_s": mid - duration / scale / 2.0,
        }
        raw["stop"] = {"duration_s": stop}
        out.append(ScenarioV2.model_validate(raw))
    return out


def impulsive_row(base: ScenarioV2, variant: ScenarioV2, run: RunResult) -> dict[str, float]:
    """Finite vs impulsive SMA for one variant.

    Impulsive reference (textbook): Kepler-propagate the simulator's ignition state to
    the midpoint, add the rocket-equation delta-v (from the base scenario's inputs)
    along +-v, take the SMA. The ignition state itself is checked by O4 (audit).
    """
    veh = vehicle(base)
    assert veh is not None
    cmd = base.commands[0].command
    vcmd = variant.commands[0].command
    mu = base.constants.mu
    duration = float(cmd["duration_s"])
    mid = float(cmd["ignition_t_s"]) + duration / 2.0
    sign = SIGN[cmd["direction"]]
    s = _of(run.events, "BurnStarted")[0]
    e = _of(run.events, "BurnEnded")[0]
    a0 = rv_to_elements(np.array(s.r), np.array(s.v), mu).a
    a_fin = rv_to_elements(np.array(e.r), np.array(e.v), mu).a
    m0 = veh.initial_mass_kg
    with snap.scope(variant.name, "o6"):
        dv = veh.exhaust_velocity_mps * math.log(m0 / (m0 - veh.mass_flow_kgps * duration))
        dv = float(snap.pin("o6.delta_v", "ref", dv_mps=[dv])["dv_mps"][0])
        r_m, v_m = kepler_state(np.array(s.r), np.array(s.v), mid - s.event_t_s, mu)
        v_imp = v_m + sign * dv * v_m / np.linalg.norm(v_m)
        a_imp = -mu / (2.0 * specific_energy(r_m, v_imp, mu))
        # DR-0021: seeded by the simulator's ignition state, so verified within the
        # sim-seeded tolerance (F51), not substituted; margin_problems covers the gates.
        snap.pin(
            "o6.midpoint",
            "sim",
            seed_r_m=s.r,
            seed_v_mps=s.v,
            flight_s=[mid - s.event_t_s],
            r_m=r_m,
            v_mps=v_m,
            sma_impulsive_m=[a_imp],
        )
    return {
        "burn_duration_s": float(vcmd["duration_s"]),
        "sma_finite_minus_impulsive_m": a_fin - a_imp,
        "sma_change_finite_m": a_fin - a0,
        "sma_change_impulsive_m": a_imp - a0,
    }


def impulsive_family(scenario: ScenarioV2, levels: int = 5) -> list[dict[str, float]]:
    from tars.sim.runner import run_scenario

    return [
        impulsive_row(scenario, variant, run_scenario(variant, record_samples=False))
        for variant in impulsive_variants(scenario, levels)
    ]


def impulsive_metrics(rows: Sequence[dict[str, float]]) -> dict[str, float]:
    orders = [
        math.log2(a["sma_finite_minus_impulsive_m"] / b["sma_finite_minus_impulsive_m"])
        for a, b in pairwise(rows)
    ]
    r0 = rows[0]
    out = {
        "order_deviation_from_2_max": worst_of(abs(p - 2.0) for p in orders),
        "slice_sma_change_ratio_deviation": abs(
            r0["sma_change_finite_m"] / r0["sma_change_impulsive_m"] - 1.0
        ),
        "slice_finite_minus_impulsive_sma_m": r0["sma_finite_minus_impulsive_m"],
    }
    for i, p in enumerate(orders):
        out[f"order_pair_{i}"] = p
    return out


def o6_snapshot_shifts(rows: Sequence[dict[str, float]], delta: float) -> dict[str, float]:
    """Worst change of the gated O6 metrics if every impulsive SMA moves by at most
    ``delta`` (the sim-seeded snapshot tolerance, DR-0021 condition 4). Each metric is
    monotone in each SMA, so the corners of the interval give the bound."""

    def d(row: dict[str, float], e: float) -> float:
        return row["sma_finite_minus_impulsive_m"] - e

    order = 0.0
    for a, b in pairwise(rows):
        p = math.log2(d(a, 0.0) / d(b, 0.0))
        for ea in (-delta, delta):
            for eb in (-delta, delta):
                da, db = d(a, ea), d(b, eb)
                q = math.log2(da / db) if da * db > 0.0 and d(a, 0.0) * da > 0.0 else math.inf
                order = worst(order, abs(q - p))
    r0 = rows[0]
    fin, imp = r0["sma_change_finite_m"], r0["sma_change_impulsive_m"]
    ratio = 0.0
    for e in (-delta, delta):
        moved = imp + e
        ratio = worst(ratio, abs(fin / moved - fin / imp) if moved * imp > 0.0 else math.inf)
    return {"order_deviation_from_2_max": order, "slice_sma_change_ratio_deviation": ratio}


def o5_snapshot_shifts() -> dict[str, float]:
    """O5 compares simulator samples with Kepler states by Euclidean norm. The snapshot
    tolerance bounds each COMPONENT, so a within-tolerance Kepler vector can move by
    up to sqrt(3) x the tolerance, and each gated metric with it (review M2-T6 F52)."""
    return {
        "coast_position_error_max_m": math.sqrt(3.0) * snap.TOLERANCES[("sim", "m")],
        "coast_velocity_error_max_mps": math.sqrt(3.0) * snap.TOLERANCES[("sim", "mps")],
    }


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
        out["plane_rotation_max_rad"] = worst(
            out["plane_rotation_max_rad"],
            float(np.linalg.norm(np.cross(h0, h1)) / (np.linalg.norm(h0) * np.linalg.norm(h1)))
            if cosang > 0
            else math.pi,
        )
        out["inclination_change_max_rad"] = worst(
            out["inclination_change_max_rad"], abs(el1.i - el0.i)
        )
        tag = e.burn_id.replace("#", "")
        out[f"{tag}_sma_change_m"] = el1.a - el0.a
        out[f"{tag}_apoapsis_alt_km"] = (el1.a * (1 + el1.e) - re) / 1e3
        out[f"{tag}_periapsis_alt_km"] = (el1.a * (1 - el1.e) - re) / 1e3
    return out


# --------------------------------------------------------------- O8 convergence


O8_DTS = (10.0, 5.0, 2.5)


def convergence_variant(scenario: ScenarioV2, dt: float) -> ScenarioV2:
    """The scenario at another step, telemetry grid unchanged, so every sample has a
    reference state and the run is audited like a reference mission (review F6)."""
    if dt == scenario.dt_s:
        return scenario
    raw = scenario.model_dump(mode="json")
    raw["name"] += f"_o8_dt{dt:g}"
    raw["dt_s"] = dt
    return ScenarioV2.model_validate(raw)


def convergence_metrics(
    finals: dict[float, np.ndarray], reference_final: np.ndarray
) -> dict[str, float]:
    """O8: final-position error vs DOP853 at several dt; observed order per halving.

    The 20 -> 10 s pair is pre-asymptotic (VAL-0008/0012) and is not used. dt = 1 s
    is not used either: its error (~2e-5 m) approaches the DOP853 reference's
    cross-platform floor (11-15 um at 53 700 s, VAL-0010 addendum).
    """
    dts = sorted(finals, reverse=True)
    errs = [float(np.linalg.norm(finals[dt][:3] - reference_final[:3])) for dt in dts]
    out = {f"position_error_dt{dt:g}_m": e for dt, e in zip(dts, errs, strict=True)}
    orders = [math.log2(a / b) for a, b in pairwise(errs)]
    for (a, b), p in zip(pairwise(dts), orders, strict=True):
        out[f"order_{a:g}_to_{b:g}"] = p
    out["order_deviation_from_4_max"] = worst_of(abs(p - 4.0) for p in orders)
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
    with snap.scope(variant.name, "dr0018"):
        predicted = predict_burns(variant, expected)
    v += check_outcomes(variant, events, predicted)
    v += check_final_consistency(events, run)
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


# --------------------------------------------------------------- full-output audit
# Review M2-T5 re-verification (F5-F15): every simulator output the Proof consumes is
# checked against an independent expectation or an exact consistency rule.

# DR-0017 B (approved): per-burn timing delta-v budget, written from the decision.
DR0017_BUDGET_MPS = 1.0e-7


def check_start_identity(scenario: ScenarioV2, events: Sequence[Any]) -> list[str]:
    """SimulationStarted and SpacecraftConfigured provenance against the scenario."""
    import tars

    s = events[0]
    c = scenario.constants
    want = {
        "scenario_name": scenario.name,
        "scenario_hash": scenario.config_hash(),
        "software_version": tars.__version__,
        "epoch": scenario.epoch,
        "time_scale": scenario.time_scale,
        "seed": scenario.seed,
        "earth_constants": {"name": c.name, "mu": c.mu, "equatorial_radius": c.equatorial_radius},
        "force_models": list(scenario.force_models),
        "integrator": scenario.integrator,
        "dt": scenario.dt_s,
        "tick": 0,
        "t": 0.0,
    }
    v = [
        f"SimulationStarted.{k} {getattr(s, k)!r} != {w!r}"
        for k, w in want.items()
        if getattr(s, k) != w
    ]
    cfg = _of(events, "SpacecraftConfigured")
    if cfg:
        if tuple(cfg[0].direction_laws) != ("prograde", "retrograde"):
            v.append(f"direction_laws {cfg[0].direction_laws}")
        if cfg[0].timing_delta_v_budget_mps != DR0017_BUDGET_MPS:
            v.append(f"timing budget {cfg[0].timing_delta_v_budget_mps!r} != DR-0017 1e-7")
    return v


def _timing_bound(veh: Vehicle, b: PredictedBurn) -> float:
    """DR-0017 definition: F |D - d| / m_end, m_end after the longer interval."""
    dt = abs(b.executed_s - b.intended_s)
    bound = 0.0
    if dt != 0.0:
        m_end = veh.dry_mass_kg + max(
            b.propellant_before_kg - veh.mass_flow_kgps * max(b.executed_s, b.intended_s), 0.0
        )
        bound = veh.thrust_n * dt / m_end
    p = snap.pin(
        "timing_bound",
        "ref",
        bound_mps=[bound],
        durations_s=[b.executed_s, b.intended_s],
        propellant_before_kg=[b.propellant_before_kg],
    )
    return float(p["bound_mps"][0])


def check_receipt_details(
    scenario: ScenarioV2,
    events: Sequence[Any],
    expected: Sequence[Expected],
    predicted: Sequence[PredictedBurn],
) -> tuple[dict[str, float], list[str]]:
    """Issuer, diagnostics, schema-invalid intent, and every accepted-plan field."""
    v: list[str] = []
    veh = vehicle(scenario)
    receipts = _of(events, *COMMAND_EVENTS)
    for i, (entry, rec, exp) in enumerate(zip(scenario.commands, receipts, expected, strict=False)):
        payload = entry.command
        issuer = payload.get("issuer")
        want_issuer = issuer if isinstance(issuer, str) else None
        if rec.issuer != want_issuer:
            v.append(f"entry {i}: issuer {rec.issuer!r} != {want_issuer!r}")
        errors = tuple(getattr(rec, "schema_errors", ()))
        if errors != exp.schema_errors:
            v.append(f"entry {i}: schema_errors {errors} != declared {exp.schema_errors}")
        if exp.reason == "schema_invalid":
            intent = (
                rec.direction,
                rec.on_insufficient_propellant,
                rec.commanded_ignition_t_s,
                rec.commanded_duration_s,
            )
            if intent != (None, None, None, None):
                v.append(f"entry {i}: schema-invalid receipt echoes intent {intent}")
    by_burn = {b.burn_id: b for b in predicted}
    plan_rel = 0.0
    for acc in _of(events, "CommandAccepted"):
        b = by_burn.get(acc.burn_id)
        if b is None or veh is None:
            v.append(f"{acc.burn_id}: accepted but not predicted")
            continue
        got = (acc.planned_cutoff_t_s, acc.planned_burn_duration_s, acc.planned_end_cause)
        want = (b.cutoff_t_s, b.executed_s, b.end_cause)
        if got != want:
            v.append(f"{acc.burn_id}: plan {got} != predicted {want}")
        plan_rel = worst(
            plan_rel,
            abs(acc.planned_propellant_used_kg - b.propellant_used_kg) / veh.initial_mass_kg,
        )
        bound = _timing_bound(veh, b)
        reported = acc.timing_delta_v_error_mps
        if reported is None or not reported <= DR0017_BUDGET_MPS:
            v.append(f"{acc.burn_id}: timing bound {reported!r} missing or over budget")
        elif bound == 0.0:
            if reported != 0.0:
                v.append(f"{acc.burn_id}: timing bound {reported!r}, intervals equal")
        elif not bound <= reported <= bound * (1.0 + 1e-9):
            v.append(f"{acc.burn_id}: timing bound {reported!r} != F|D-d|/m_end {bound!r}")
    for s in _of(events, "BurnStarted"):
        b = by_burn.get(s.burn_id)
        if b is not None and (s.planned_cutoff_t_s, s.planned_end_cause) != (
            b.cutoff_t_s,
            b.end_cause,
        ):
            v.append(f"{s.burn_id}: BurnStarted plan differs from prediction")
    for e in _of(events, "BurnEnded"):
        b = by_burn.get(e.burn_id)
        if b is not None and e.event_t_s != b.cutoff_t_s:
            v.append(f"{e.burn_id}: cutoff {e.event_t_s!r} != predicted {b.cutoff_t_s!r} (D1a)")
    return {"plan_propellant_rel_error_max": plan_rel}, v


def transition_checks(
    scenario: ScenarioV2, events: Sequence[Any], predicted: Sequence[PredictedBurn]
) -> tuple[dict[str, float], list[str]]:
    """Payloads of BurnStarted, BurnEnded and PropellantDepleted (review F11)."""
    v: list[str] = []
    veh = vehicle(scenario)
    out = {"transition_propellant_rel_error_max": 0.0, "thrust_unit_vector_error_max": 0.0}
    if veh is None:
        return out, v
    by_burn = {b.burn_id: b for b in predicted}
    m0 = veh.initial_mass_kg
    for s in _of(events, "BurnStarted"):
        b = by_burn.get(s.burn_id)
        if b is None:
            continue
        out["transition_propellant_rel_error_max"] = worst(
            out["transition_propellant_rel_error_max"],
            abs(s.propellant_kg - b.propellant_before_kg) / m0,
        )
        if s.total_mass_kg != veh.dry_mass_kg + s.propellant_kg:
            v.append(f"{s.burn_id}: BurnStarted mass != dry + propellant")
        u = SIGN[s.direction] * np.array(s.v) / np.linalg.norm(s.v)
        out["thrust_unit_vector_error_max"] = worst(
            out["thrust_unit_vector_error_max"],
            float(np.linalg.norm(np.array(s.thrust_unit_vector) - u)),
        )
    ends = {e.burn_id: e for e in _of(events, "BurnEnded")}
    for e in ends.values():
        b = by_burn.get(e.burn_id)
        if b is None:
            continue
        out["transition_propellant_rel_error_max"] = worst(
            out["transition_propellant_rel_error_max"],
            abs(e.propellant_kg - b.propellant_after_kg) / m0,
        )
        if e.total_mass_kg != veh.dry_mass_kg + e.propellant_kg:
            v.append(f"{e.burn_id}: BurnEnded mass != dry + propellant")
        if (
            e.planned_propellant_used_kg != b.propellant_used_kg
            and abs(e.planned_propellant_used_kg - b.propellant_used_kg) > 1e-12 * m0
        ):
            v.append(f"{e.burn_id}: BurnEnded planned consumption differs from prediction")
    for d in _of(events, "PropellantDepleted"):
        e = ends.get(d.burn_id)
        if e is None or d.residual_propellant_kg != e.propellant_kg:
            v.append(f"{d.burn_id}: depletion residual != BurnEnded propellant")
    return out, v


def propulsion_sample_checks(
    scenario: ScenarioV2, events: Sequence[Any], predicted: Sequence[PredictedBurn]
) -> tuple[dict[str, float], list[str]]:
    """Engine schedule, propellant and sensed delta-v at every PropulsionSampled,
    predicted from the accepted commands and elapsed burn time (review F9)."""
    v: list[str] = []
    veh = vehicle(scenario)
    out = {
        "sample_propellant_rel_error_max": 0.0,
        "sample_delta_v_rel_error_max": 0.0,
        "sample_delta_v_excess_over_simpson_rel_max": 0.0,
    }
    if veh is None:
        return out, v
    dt = scenario.dt_s
    c, mdot, m0 = veh.exhaust_velocity_mps, veh.mass_flow_kgps, veh.initial_mass_kg
    ticks = {
        b.burn_id: (
            b.submit_tick,
            _expected_report_tick(b.ignition_t_s, dt, b.submit_tick * dt == b.ignition_t_s),
            _expected_report_tick(b.cutoff_t_s, dt, False),
        )
        for b in predicted
    }
    total_dv = sum(b.delta_v_mps for b in predicted) or 1.0
    for p in _of(events, "PropulsionSampled"):
        k, t = p.tick, p.tick * dt
        active, pending = None, []
        prop, dv, allowance = veh.propellant_kg, 0.0, 0.0
        for b in predicted:
            sub, ign_k, cut_k = ticks[b.burn_id]
            if sub > k:
                continue
            if ign_k > k:
                pending.append(b.burn_id)
                continue
            if k < cut_k:
                active = b.burn_id
                used = mdot * (t - b.ignition_t_s)
                prop = b.propellant_before_kg - used
                dv += c * math.log(b.mass_before_kg / (veh.dry_mass_kg + prop))
                allowance += simpson_bound(veh, b, dt, until=t)
            else:
                prop = b.propellant_after_kg
                dv += b.delta_v_mps
                allowance += simpson_bound(veh, b, dt)
        state = "burning" if active else ("scheduled" if pending else "idle")
        got = (p.engine_state, p.active_burn_id, list(p.pending_burn_ids))
        if got != (state, active, pending):
            v.append(f"tick {k}: schedule {got}, expected {(state, active, pending)}")
        out["sample_propellant_rel_error_max"] = worst(
            out["sample_propellant_rel_error_max"], abs(p.propellant_kg - prop) / m0
        )
        err = abs(p.delta_v_sensed_mps - dv)
        out["sample_delta_v_rel_error_max"] = worst(
            out["sample_delta_v_rel_error_max"], err / total_dv
        )
        out["sample_delta_v_excess_over_simpson_rel_max"] = worst(
            out["sample_delta_v_excess_over_simpson_rel_max"],
            excess_over(err, allowance) / total_dv,
        )
    return out, v


def check_result_consistency(
    scenario: ScenarioV2, events: Sequence[Any], result: RunResult
) -> list[str]:
    """Every returned RunResult field agrees with the event log (review F8)."""
    v = check_final_consistency(events, result)
    receipts = _of(events, *COMMAND_EVENTS)
    if len(result.receipts) != len(receipts):
        v.append(f"{len(result.receipts)} returned receipts, {len(receipts)} receipt events")
    if result.scenario is not scenario and result.scenario.config_hash() != scenario.config_hash():
        v.append("returned scenario differs from the audited scenario")
    veh = vehicle(scenario)
    by_burn = {b.burn_id: b for b in predict_burns_or_empty(scenario, receipts)}
    for i, (r, e) in enumerate(zip(result.receipts, receipts, strict=False)):
        payload = scenario.commands[i].command if i < len(scenario.commands) else {}
        schema_invalid = getattr(e, "reason", None) == "schema_invalid"
        if schema_invalid:
            if r.command is not None:
                v.append(f"receipt {i}: schema-invalid receipt carries a command")
        else:
            want_cmd = {**payload}
            want_cmd.setdefault("on_insufficient_propellant", "reject")
            if r.command is None or r.command.model_dump(mode="json") != want_cmd:
                v.append(f"receipt {i}: returned command differs from the scenario payload")
        want_detail = getattr(e, "detail", "accepted")  # accepted receipts: "accepted"
        if (r.detail, tuple(r.schema_errors)) != (
            want_detail,
            tuple(getattr(e, "schema_errors", ())),
        ):
            v.append(f"receipt {i}: detail or schema_errors differ from the event")
        if e.type == "CommandRejected" and (r.plan is not None or r.burn_id is not None):
            v.append(f"receipt {i}: rejected receipt carries a plan or burn ID")
        if e.type == "CommandAccepted" and r.plan is not None:
            v += _plan_violations(f"receipt {i}", r.plan, e, by_burn.get(e.burn_id), veh)

        status = "accepted" if e.type == "CommandAccepted" else "rejected"
        got = (
            str(r.status),
            r.command_id,
            r.issuer,
            r.reason and str(r.reason),
            r.burn_id,
            r.tick,
            r.t,
        )
        want = (
            status,
            e.command_id,
            e.issuer,
            getattr(e, "reason", None),
            getattr(e, "burn_id", None),
            e.tick,
            e.t,
        )
        if got != want:
            v.append(f"returned receipt {got} != event {want}")
        if (
            status == "accepted"
            and r.plan is not None
            and (
                r.plan.cutoff_t_s,
                r.plan.burn_duration_s,
                r.plan.propellant_used_kg,
                str(r.plan.end_cause),
            )
            != (
                e.planned_cutoff_t_s,
                e.planned_burn_duration_s,
                e.planned_propellant_used_kg,
                e.planned_end_cause,
            )
        ):
            v.append(f"{e.burn_id}: returned plan differs from CommandAccepted")
        if status == "accepted" and r.plan is None:
            v.append(f"{e.burn_id}: accepted receipt without a plan")
    states = _of(events, "StateSampled")
    got_samples = [(s.tick, s.t, tuple(s.r), tuple(s.v)) for s in result.samples]
    if got_samples != [(s.tick, s.t, tuple(s.r), tuple(s.v)) for s in states]:
        v.append("returned samples differ from StateSampled events")
    crossings = [o.crossing_t for o in _of(events, "OrbitCompleted")]
    if list(result.crossing_times) != crossings:
        v.append("returned crossing_times differ from OrbitCompleted events")
    start, init = events[0], result.initial
    if init is None or (init.tick, init.t, tuple(init.r), tuple(init.v)) != (
        0,
        0.0,
        tuple(start.r),
        tuple(start.v),
    ):
        v.append("returned initial state differs from SimulationStarted")
    done = events[-1]
    if (result.status, result.failure_cause) != (done.status, done.failure_cause):
        v.append("returned status differs from SimulationCompleted")
    if result.final is not None and result.final.t != done.t:
        v.append("returned final time differs from SimulationCompleted")
    fp = result.final_propulsion
    if fp is not None:
        if (fp.tick, fp.t) != (done.tick, done.t):
            v.append("final_propulsion time differs from SimulationCompleted")
        accepted = {e.burn_id: e for e in _of(events, "CommandAccepted")}
        starts = {e.burn_id: e for e in _of(events, "BurnStarted")}
        plans = ([fp.active_plan] if fp.active_burn_id else []) + list(fp.pending_plans)
        ids = ([fp.active_burn_id] if fp.active_burn_id else []) + list(fp.pending_burn_ids)
        if (fp.active_plan is None) != (fp.active_burn_id is None) or len(plans) != len(ids):
            v.append("final_propulsion plans do not match its burn IDs")
        else:
            for burn_id, plan in zip(ids, plans, strict=True):
                acc = accepted.get(burn_id)
                if acc is None:
                    v.append(f"final_propulsion plan for {burn_id} has no CommandAccepted")
                    continue
                v += _plan_violations(
                    f"final_propulsion {burn_id}", plan, acc, by_burn.get(burn_id), veh
                )
        want_dir = starts[fp.active_burn_id].direction if fp.active_burn_id in starts else None
        if fp.active_direction != want_dir:
            v.append(f"final_propulsion active_direction {fp.active_direction!r} != {want_dir!r}")
    return v


def predict_burns_or_empty(scenario: ScenarioV2, receipts: Sequence[Any]) -> list[PredictedBurn]:
    """Burn predictions from the receipts' accept/reject pattern (declared outcomes are
    checked separately against the receipts by check_traceability)."""
    declared = [
        Expected("accepted") if e.type == "CommandAccepted" else Expected("rejected", e.reason)
        for e in receipts
    ]
    declared += [Expected("rejected")] * (len(scenario.commands) - len(declared))
    try:
        return predict_burns(scenario, declared)
    except ValueError:
        return []


def _plan_violations(
    where: str, plan: Any, acc: Any, b: PredictedBurn | None, veh: Vehicle | None
) -> list[str]:
    """Every BurnPlan field against the prediction and the CommandAccepted event."""
    if b is None or veh is None:
        return [f"{where}: plan without a predicted burn"]
    got = (
        plan.ignition_t_s,
        plan.commanded_duration_s,
        plan.burn_duration_s,
        plan.cutoff_t_s,
        plan.propellant_used_kg,
        plan.mass_flow_kgps,
        str(plan.end_cause),
        str(plan.policy),
        plan.timing_delta_v_error_mps,
    )
    want = (
        b.ignition_t_s,
        b.commanded_duration_s,
        b.executed_s,
        b.cutoff_t_s,
        acc.planned_propellant_used_kg,
        veh.mass_flow_kgps,
        b.end_cause,
        b.policy,
        acc.timing_delta_v_error_mps,
    )
    return [] if got == want else [f"{where}: plan {got} != expected {want}"]


def cli_summary_violations(
    events: Sequence[Any], summary: dict[str, Any], scenario: ScenarioV2
) -> list[str]:
    """The CLI's propulsion summary agrees with the event log and, for the never
    submitted entries, with the scenario timeline (reviews M2-T5 F8, M2-T6 F37)."""
    v: list[str] = []
    n = expected_submissions(scenario, events)
    rest = [e.command.get("command_id") for e in scenario.commands[n:]]
    rest = [c if isinstance(c, str) else None for c in rest]
    if "unsubmitted_command_ids" not in summary or summary["unsubmitted_command_ids"] != rest:
        v.append(f"CLI summary unsubmitted_command_ids != {rest}")
    receipts = _of(events, *COMMAND_EVENTS)
    want = [
        {
            "command_id": e.command_id,
            "status": "accepted" if e.type == "CommandAccepted" else "rejected",
            "reason": getattr(e, "reason", None),
            "burn_id": getattr(e, "burn_id", None),
            "submit_tick": e.tick,
        }
        for e in receipts
    ]
    if summary.get("commands") != want:
        v.append("CLI summary commands differ from the receipt events")
    props = _of(events, "PropulsionSampled")
    fields = (
        "final_propellant_kg", "final_total_mass_kg", "final_engine_state",
        "active_burn_id_at_stop", "pending_burn_ids_at_stop",
    )  # fmt: skip
    if any(f not in summary for f in fields):
        v.append("CLI summary lacks a final propulsion field")
        return v
    if not props:
        # No propulsion (F41): every final propulsion field is explicitly empty.
        got = tuple(summary[f] for f in fields)
        if got != (None, None, None, None, []):
            v.append(f"CLI summary claims propulsion state {got} without propulsion")
        return v
    if props:
        last = props[-1]
        got = (
            summary.get("final_propellant_kg"),
            summary.get("final_total_mass_kg"),
            summary.get("final_engine_state"),
            summary.get("active_burn_id_at_stop"),
            summary.get("pending_burn_ids_at_stop"),
        )
        if got != (
            last.propellant_kg,
            last.total_mass_kg,
            last.engine_state,
            last.active_burn_id,
            list(last.pending_burn_ids),
        ):
            v.append("CLI summary final propulsion differs from the last PropulsionSampled")
    return v


def orbit_checks(
    scenario: ScenarioV2,
    events: Sequence[Any],
    ref: dict[float, np.ndarray],
    predicted: Sequence[PredictedBurn],
) -> tuple[dict[str, float], list[str]]:
    """Orbit events, counts and altitude reporting (review F14).

    - OrbitCompleted numbers run 1..N; N equals SimulationCompleted.orbits_completed.
    - Ascending-node crossings are located independently: upward z sign changes of
      the DOP853 reference between consecutive reference marks, refined by bisection
      on exact Kepler propagation of the reference state (coast intervals). Their
      count must equal N; the crossing-time error is a metric.
    - altitude_m = |r| - R exactly; the completion extrema bracket every sample and
      match the reference's extrema over every executed tick (dense output).
    """
    v: list[str] = []
    mu, radius = scenario.constants.mu, scenario.constants.equatorial_radius
    orbits = _of(events, "OrbitCompleted")
    done = events[-1]
    dt = scenario.dt_s
    if [o.orbit_number for o in orbits] != list(range(1, len(orbits) + 1)):
        v.append("orbit numbers are not 1..N")
    if done.orbits_completed != len(orbits):
        v.append(f"orbits_completed {done.orbits_completed} != {len(orbits)} OrbitCompleted")
    for o in orbits:
        if not (o.tick - 1) * dt < o.crossing_t <= o.tick * dt:
            v.append(f"orbit {o.orbit_number}: crossing_t outside its step")
    times = sorted(ref)
    burning = [(b.ignition_t_s, b.cutoff_t_s) for b in predicted]
    ref_crossings: list[float] = []
    for a, b in pairwise(times):
        za, zb = ref[a][2], ref[b][2]
        if za < 0.0 <= zb:
            if any(i < b and a < c for i, c in burning):
                ref_crossings.append(math.nan)  # powered interval: counted, not timed
                continue
            r0, v0 = ref[a][:3], ref[a][3:6]
            lo, hi = 0.0, b - a
            crossing = None
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                rr, vv = kepler_state(r0, v0, mid, mu)
                z = float(rr[2])
                # F22/F36: any invalid oracle output fails, never steers the bisection.
                if not (np.all(np.isfinite(rr)) and np.all(np.isfinite(vv))):
                    crossing = math.inf
                    break
                if z < 0.0:
                    lo = mid
                else:
                    hi = mid
            ref_crossings.append(a + hi if crossing is None else crossing)
    # DR-0021: the timed crossings are pinned (the bisection's Kepler states only steer
    # it); powered intervals are counted, not timed.
    timed = [i for i, c in enumerate(ref_crossings) if not math.isnan(c)]
    p = snap.pin(
        "orbit.node_crossings",
        "ref",
        crossings_s=[ref_crossings[i] for i in timed],
        powered_1=[float(len(ref_crossings) - len(timed))],
    )
    for i, c in zip(timed, p["crossings_s"], strict=True):
        ref_crossings[i] = float(c)
    if len(ref_crossings) != len(orbits):
        v.append(f"{len(orbits)} OrbitCompleted, reference has {len(ref_crossings)} node crossings")
    err = worst_of(
        (
            abs(o.crossing_t - c)
            for o, c in zip(orbits, ref_crossings, strict=False)
            if not math.isnan(c)
        ),
        default=0.0,
    )
    states = _of(events, "StateSampled")
    for s in states:
        if s.altitude_m != float(np.linalg.norm(s.r)) - radius:
            v.append(f"tick {s.tick}: altitude_m != |r| - R")
    alts = [s.altitude_m for s in states]
    if not (done.min_altitude_m <= min(alts) and done.max_altitude_m >= max(alts)):
        v.append("completion altitude extrema do not bracket the samples")
    # Extrema over every executed tick, against the reference's tick-grid extrema, in
    # both directions (review F17).
    alt_min = getattr(ref, "alt_min", math.inf)
    alt_max = getattr(ref, "alt_max", -math.inf)
    return {
        "node_crossing_time_error_max_s": err,
        "min_altitude_error_m": abs(done.min_altitude_m - alt_min),
        "max_altitude_error_m": abs(done.max_altitude_m - alt_max),
    }, v


# --------------------------------------------------------------- one audit per run


@dataclass
class Audit:
    """Everything checked for one run: exact violations by check, metrics by group."""

    violations: dict[str, list[str]]
    metrics: dict[str, dict[str, float]]
    reference: dict[float, np.ndarray]


def audit_run(scenario: ScenarioV2, expected: Sequence[Expected], run: RunResult) -> Audit:
    """All contract checks and trajectory oracles that apply to one run.

    Used for reference missions, derived variants and the O6/O8 auxiliary runs alike,
    so no simulator output escapes because of the run it came from (review F6, F7).
    """
    with snap.scope(scenario.name, "audit"):
        return _audit_run(scenario, expected, run)


def _audit_run(scenario: ScenarioV2, expected: Sequence[Expected], run: RunResult) -> Audit:
    events = run.events
    predicted = predict_burns(scenario, expected)
    acc, identities = accounting_metrics(scenario, events)
    plan_m, receipt_v = check_receipt_details(scenario, events, expected, predicted)
    trans_m, trans_v = transition_checks(scenario, events, predicted)
    samp_m, samp_v = propulsion_sample_checks(scenario, events, predicted)
    o4, ref = reference_metrics(scenario, events, predicted)
    orbit_m, orbit_v = orbit_checks(scenario, events, ref, predicted)
    violations = {
        "event_order": check_event_order(scenario, events),
        "traceability": check_traceability(scenario, events, expected, run),
        "outcomes": check_outcomes(scenario, events, predicted),
        "identities": identities
        + receipt_v
        + trans_v
        + samp_v
        + check_start_identity(scenario, events)
        + check_result_consistency(scenario, events, run),
        "orbit_events_contract": orbit_v,  # distinct from the numerical orbit_events gate
    }
    metrics: dict[str, dict[str, float]] = {
        "o4_reference": o4,
        "o5_coast_kepler": coast_metrics(scenario, events),
        "orbit_events": orbit_m,
    }
    if scenario.spacecraft is not None:
        metrics["accounting"] = {**acc, **plan_m, **trans_m, **samp_m}
    if any(e.type == "BurnEnded" for e in events):
        o1, o2, o1_v = mass_and_rocket_metrics(scenario, events, predicted)
        violations["identities"] += o1_v
        metrics["o1_mass_law"] = o1
        metrics["o2_rocket_equation"] = o2
        metrics["o7_direction"] = direction_metrics(scenario, events)
    return Audit(violations, metrics, ref)


# Metrics reported for evidence but deliberately not gated. Every other metric a
# validator emits must have a threshold, or the evaluation fails (reviews M2-T5 F15,
# M2-T6 F12). Shared by m2_proof.py and gmat_m2.py.
REPORT_ONLY = frozenset(
    {
        "final_propellant_kg", "slice_finite_minus_impulsive_sma_m",
        "prograde_position_error_dt10_m", "prograde_position_order",
        "retrograde_position_error_dt10_m", "retrograde_position_order",
        "post_burn_coast_position_error_max_m",
        "sensed_delta_v_rel_error_max", "sample_delta_v_rel_error_max",
        "gmat_rows", "mass_samples_compared",
    }
)  # fmt: skip
_REPORT_PREFIXES = ("burn0", "order_pair_", "order_10_to", "order_5_to", "position_error_dt")


def ungated_metrics(metrics: dict[str, float], limits: dict[str, float]) -> list[str]:
    return sorted(
        k
        for k in metrics
        if k not in limits and k not in REPORT_ONLY and not k.startswith(_REPORT_PREFIXES)
    )
