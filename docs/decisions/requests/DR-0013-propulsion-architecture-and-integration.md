# Decision Request: Propulsion architecture, simulator state, and integration across engine events

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion ([plan](../../milestones/M2-propulsion.md))

## Problem
Thrust is the first force that:
- depends on state beyond (t, r, v), namely spacecraft mass. This is the explicit ADR-0003 reconsider trigger.
- switches on and off at commanded times, so it is **discontinuous in time**.
- changes simulator-owned state other than r and v (propellant).

Three architectural choices follow:
1. where propellant lives and how it is integrated;
2. how thrust enters the derivative;
3. how a fixed-step RK4 handles the on/off discontinuity.

These touch ADR-0002 (state ownership, integer-tick time), ADR-0003 (force boundary) and ADR-0004 (fixed-step RK4).

## Evidence
VAL-0008, reference burn, RK4 dt = 10 s:

| Integration of the cutoff inside a step | Error after ≈10 orbits |
|---|---|
| Step split at the exact cutoff time | 0.290 m (≈ M1 coast error 0.298 m); burn adds 0.8 mm |
| RK4 straddling the cutoff | **168 km**, 193 m/s |

Quantizing burn duration to whole ticks would cause a Δv error up to a·dt ≈ 3.8 m/s.

## Constraints
- Simulator owns reality. There is no API that sets r, v, or mass. Commands may only change engine state, and only through validated interfaces (architecture invariant 1).
- `t = tick·dt` stays exact (ADR-0002). Same-platform byte-identical replay (DR-0006).
- **M1 is untouched:** the M1 scenario's `events.jsonl` must stay byte-identical to the golden hash `7a4e1877…`, and every M1 gate keeps passing unchanged.
- No new dependencies; physics core stays free of nondeterminism (architecture scan).

## Options
### 1. Propellant state and integration
**1A — Augmented integrated state y = [r, v, m_prop] (+ auxiliary sensed-Δv accumulator during a burn) (recommended)**
- Mass is integrated by the same RK4 step as r and v. RK4 is exact for the linear mass law (VAL-0008: ≤ 5e-12 kg).
- Generalizes to throttling or variable Isp later.
- The auxiliary accumulator ∫F/m dt is the "ideal accelerometer" Δv. It is telemetry only, checked against the rocket equation (3.5e-13 m/s).

**1B — Analytic mass m(t) = m0 − ṁ(t − t_ign); only r, v integrated**
- Exact and simple for constant thrust.
- Does not generalize to throttling. Hides mass from the integrator, which makes later models a redesign.

**1C — Mass updated once per tick, outside the integrator (operator splitting)**
- First-order error in the force law. **Not recommended.**

### 2. How thrust enters the derivative
**2A — Separate propulsion subsystem; ForceModel unchanged (recommended)**
- Derivative = [v, Σ ForceModel.acceleration(t, r, v) + a_thrust(t, r, v, m, engine), ṁ(engine)].
- Gravity and every M1 class stay exactly as they are.
- The engine is a simulator-owned object (state machine) that commands act on.

**2B — Extend the ForceModel protocol with a context object (t, r, v, m, …)**
- ADR-0003's anticipated path. It touches every force model and M1 tests now, for a capability only thrust needs. Revisit when drag needs mass and area.

### 3. Engine on/off inside a fixed step
**3A — Split the tick at scheduled engine events (recommended)**
- Ignition, commanded cutoff, and propellant-depletion time are all known exactly in advance under DR-0011 (depletion = t_ign + m_prop/ṁ). No root-finding is needed.
- If an event falls strictly inside [tick·dt, (tick+1)·dt], the tick is integrated as consecutive RK4 sub-steps whose right-hand side is smooth in each piece.
- The tick counter, telemetry grid and `t = tick·dt` are unchanged. Event times are recorded exactly.

**3B — Quantize ignition and cutoff to tick boundaries**
- Simplest. Up to 3.8 m/s Δv error (≈ 1 dt of thrust). Command durations would silently change. **Not acceptable.**

**3C — Adaptive or variable-step integrator during burns**
- Changes ADR-0004 and replay semantics. Unnecessary given 3A's measured accuracy.

### 4. Preserving M1
**4A — When a scenario has no spacecraft/propulsion block, the simulator runs the existing 6-state code path unchanged (recommended)**
- Proven by the golden events hash on the reference host plus the full M1 gate suite.

**4B — Always use the augmented state (mass constant when there is no engine)**
- Element-wise IEEE arithmetic would *probably* leave r, v bits unchanged, but that is an argument, not proof. Adding fields to existing events would change the bytes anyway.

### 5. Read-only views
- **Recommended:** keep `StateSnapshot` (r, v) unchanged. Add a frozen `PropulsionSnapshot`: propellant mass, total mass, engine state, active command id, and burn accumulators.
- Commands enter through a single `Simulator.submit(command) -> CommandReceipt` method (DR-0014). There is still no setter for any physical quantity.
- The architecture scan and tests are extended to prove no public mass/propellant setter exists.

## Recommendation
**1A + 2A + 3A + 4A + 5.** This keeps every approved M1 boundary intact and adds the thrust path planned in the playbook:
`command → engine state → thrust acceleration & mass flow → RK4 (split at engine events) → new state → events`.

A new ADR records the result after approval. ADR-0003's reconsider trigger is answered as "satisfied by a separate subsystem; protocol unchanged".

## Impact
- Architecture: new `tars.sim.propulsion` (engine, tank, pointing, mass flow). Simulator gains sub-step scheduling, `submit()`, and `PropulsionSnapshot`. ForceModel, RK4, StateSnapshot and M1 events are unchanged.
- Science/validation: preserves 4th-order accuracy through burns (VAL-0008); enables exact mass and rocket-equation oracles.
- Dependencies: none.
- Development effort: moderate. Step scheduling is the subtle part; it gets dedicated unit tests (event exactly on a tick, two events in one tick, ignition and depletion in the same tick).
- Token/compute impact: negligible (≤ 2 extra RK4 sub-steps per event).
- Reversibility: medium. It defines the pattern later discontinuous forces will follow.

## Blocked work
- Simulator integration of propulsion.

## Work continuing independently
- Propulsion pure-model unit tests (DR-0011), command schema drafting (DR-0014), REV-012 investigation.

## Requested response
`Recommended (1A+2A+3A+4A+5)` / alternatives per item / `discuss`.

## Resolution
**Decision:** APPROVED — 1A + 2A + 3A + 4A + 5 (Tech Lead, 2026-10-09):
- separate propulsion subsystem;
- exact engine-event step splitting;
- M1 execution path preserved (golden hash unchanged).

**Reasoning/notes:** As recommended.  
**Follow-up:**
- ADR-0007 records the architecture.
- T1 (standalone model) is authorized. Simulator integration (T2) needs separate approval.

