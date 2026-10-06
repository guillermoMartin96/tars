# ADR-0002: Simulation core architecture (state ownership, units, time)

**Status:** Accepted  
**Date:** 2026-10-05  
**Decision owners:** implementing engineer (Level-1 local architecture)

## Context
`playbook/architecture.md` sets two invariants: "the simulator owns reality" and a deterministic core. M1 establishes the core that every later milestone builds on.

## Options considered
### Option A — Simulator-owned private state; read-only snapshots; SI units; integer tick time
### Option B — Plain mutable spacecraft object passed around

## Decision
**Package layout**
- `src/tars/sim/`: core (constants, state, forces, integrators, simulator, scenario).
- `src/tars/astro/`: orbital element conversion and an analytic Kepler propagator.
  - The Kepler propagator is used as a validation oracle.
  - It is not part of the stepping loop.
- `src/tars/events/`: machine-readable event schemas.

**Units and frame**
- SI internally: metres, seconds, float64.
- Cartesian ECI state. The frame is defined in SCI-0003.
- Kilometres appear only at external boundaries (GMAT, display).

**State ownership**
- `Simulator` holds the only physical state.
- Consumers receive `StateSnapshot`: a frozen dataclass whose arrays are copies marked read-only.
- There is no public setter.
- Future commands (burns) will enter as forces through the force-model boundary (ADR-0003). They never assign velocity directly.

**Time**
- Simulation time is `t = tick * dt`, using an integer tick counter. Time is never accumulated as `t += dt`.
- The epoch is metadata (SCI-0007).

## Reasoning
- The Option A boundaries enforce the architecture invariants in code, before agents exist.
- Integer ticks avoid floating-point time drift and make replay exact.

## Consequences
### Positive
- No external code can mutate physics.
- Bit-identical replay is achievable.

### Negative / tradeoffs
- Snapshot copies cost a small amount of performance.

## Validation
- Tests show snapshots are immutable.
- The architecture validator finds no public state setters.
- The determinism validator passes.

## Reconsider when
- Multi-body or multi-spacecraft simulation requires a different state container.

## Related
- Proof: proof/architecture.md
- Scientific assumptions: SCI-0003, SCI-0007
