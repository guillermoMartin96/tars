# ADR-0007: Propulsion architecture (separate subsystem, augmented state, engine-event step splitting)

**Status:** Accepted  
**Date:** 2026-10-09  
**Decision owners:** Guillermo (Tech Lead, via DR-0011, DR-0012, DR-0013, DR-0014); implementing engineer

## Context
Thrust is the first force that depends on spacecraft mass. It also switches on and off at commanded times and changes simulator-owned state other than r and v. That hits the reconsider triggers in ADR-0003 ("a force needs state beyond (t, r, v)") and ADR-0004/DR-0008 ("revisit dt when finite burns arrive"). VAL-0008 measured that RK4 must not straddle an engine cutoff: doing so gave a 168 km error, against 0.290 m with splitting.

## Options considered
See DR-0013 (state, derivative boundary, discontinuity handling, M1 preservation, read-only views), DR-0012 (direction) and DR-0014 (commands).

## Decision
- **Separate propulsion subsystem** `tars.sim.propulsion`. The `ForceModel` protocol, `PointMassGravity`, `RK4` and `StateSnapshot` are unchanged. ADR-0003's trigger is answered by adding a subsystem, not by widening the protocol.
- **Model** (DR-0011): constant thrust F and Isp; ṁ = F/(Isp·g0) with `STANDARD_GRAVITY = 9.80665` m/s² in `tars.sim.constants`; thrust acceleration F/(m_dry + m_prop) along a unit direction.
- **Configurable specs** (DR-0010): engine and tank values are inputs (`EngineSpec`, `TankSpec`). The R-4D-11-class reference values live in scenarios and tests, never in physics code.
- **Direction interface** (DR-0012): a `DirectionLaw` protocol maps read-only (t, r, v) to a unit vector. `Prograde` and `Retrograde` (velocity-tracking, GMAT VNB ±V) are the M2 implementations. Future guidance modes add implementations.
- **Burn representation** (DR-0014): an immutable `BurnPlan` holds ignition time, commanded duration, cutoff time, the propellant it will use, and how it ends (`completed` | `propellant_depleted`). It is computed exactly in advance from the specs, so the simulator can split RK4 ticks at those times (DR-0013 3A).
  - Insufficient propellant is rejected by default.
  - `burn_to_depletion` must be requested explicitly.
- **Integration** (T2, not yet authorized):
  - augmented state y = [r, v, m_prop, Δv_sensed];
  - ticks split at engine events;
  - M1 6-state path unchanged when no propulsion is configured.

## Reasoning
- Keeps every approved M1 boundary and byte-identical M1 output.
- Gives exact analytic oracles (mass law, rocket equation, free-space motion).
- Follows the playbook chain: command → propulsion → force → integration → telemetry.

## Consequences
### Positive
- Propulsion is testable on its own (T1) before simulator integration (T2).
- Direction modes and engine models are extensible.

### Negative / tradeoffs
- The simulator gains a second derivative path (with propulsion) alongside the M1 path. Both must be maintained.

## Validation
- T1: unit tests against the rocket equation, mass conservation, the free-space closed form and an independent integrator.
- T2 onward: DR-0015 oracles; the M1 golden hash is unchanged.

## Reconsider when
- Throttling, multiple engines/tanks, attitude dynamics, or mass-dependent non-thrust forces (drag) are introduced.

## Related
- Decision Requests: DR-0010…DR-0015
- Scientific assumptions: SCI-0002 (revised), SCI-0008…SCI-0012
- Validation: VAL-0008, VAL-0009
