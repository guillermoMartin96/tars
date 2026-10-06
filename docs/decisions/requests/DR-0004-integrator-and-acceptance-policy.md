# Decision Request: Integrator and M1 acceptance policy

**Status:** RESOLVED (final tolerances pending a follow-up DR)  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
We need a numerical integrator and a principled way to decide what "acceptable stability" means for 10 orbits.

The planning experiment below is indicative only and is not a Proof result. It measured the position error after 10 orbits against the exact Kepler solution:

| Method | dt | Position error |
|---|---|---|
| Explicit Euler | 1 s | 3 972 km |
| Velocity Verlet | 10 s | 19 km |
| RK4 | 60 s | 1.16 km |
| RK4 | 30 s | 43.5 m |
| RK4 | 10 s | 0.30 m |
| RK4 | 5 s | 0.015 m |

## Constraints
- The simulation must be deterministic and replayable.
- Future burns need predictable step boundaries.
- Tolerances must not be invented.

## Options
### A — Fixed-step RK4
**Pros**
- Simple and 4th-order.
- Its predictable tick suits replay and burn scheduling.
- Its convergence order is easy to prove.

**Cons**
- Not symplectic, so it has a small secular energy drift.

### B — Adaptive (for example, DOP853)
**Pros**
- High accuracy per unit of cost.

**Cons**
- Variable step sequence that depends on tolerances, which complicates tick-based simulation and replay.

### C — Symplectic (Velocity Verlet)
**Pros**
- Bounded energy error.

**Cons**
- Large phase error at a practical dt.

## Recommendation
A, with dt = 10 s as the candidate. Finalize dt and tolerances from a measured convergence study.

## Impact
- Architecture: an `Integrator` protocol, so methods can be swapped.
- Science/validation: convergence study, plus invariant and reference-error metrics.
- Dependencies: none.
- Development effort: low.
- Token/compute impact: none.
- Reversibility: high.

## Blocked work
- Final Proof thresholds only.

## Work continuing independently
- All implementation.

## Requested response
`A` / `B` / `C` / `discuss`

## Resolution
**Decision:** APPROVED WITH MEASUREMENT — A.  
**Reasoning/notes:** Use fixed-step RK4. Treat dt = 10 s as the candidate timestep and finalize it from the convergence study. Do not block implementation waiting for final numerical tolerances. When the implementation is ready, present the measured results and recommended thresholds for approval.  
**Follow-up:** ADR-0004. A tolerance DR follows once the convergence data exists.
