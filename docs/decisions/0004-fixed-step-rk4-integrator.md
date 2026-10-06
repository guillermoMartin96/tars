# ADR-0004: Fixed-step classical RK4 integrator

**Status:** Accepted (dt and tolerances to be finalized from the convergence study)  
**Date:** 2026-10-05  
**Decision owners:** Guillermo (Tech Lead, via DR-0004); implementing engineer

## Context
We need a numerical method to advance the state of the equations of motion. DR-0004 compares the alternatives.

## Options considered
### Option A — Classical 4th-order Runge–Kutta, fixed step
### Option B — Adaptive embedded RK (for example, DOP853)
### Option C — Symplectic Velocity Verlet

## Decision
- Option A, behind an `Integrator` protocol (`step(t, y, dt, deriv) -> y_next`).
- Candidate dt = 10 s. Final values come from the convergence study and need Tech Lead approval.
- Explicit Euler exists only in tests, as a documented negative control.

## Reasoning
- 4th-order global error. The planning experiment measured about 0.3 m after 10 orbits at dt = 10 s.
- A fixed tick supports replay and future burn scheduling.
- The convergence order (error ratio of about 16 when dt is halved) is a strong deterministic proof of correct implementation.

## Consequences
### Positive
- Simple to understand, implement, and verify.

### Negative / tradeoffs
- Not symplectic: energy drifts secularly, but slowly.
- No automatic error control. Step size must be chosen with evidence.

## Validation
- RK4 order measured on known ODEs and on the orbit.
- Invariants and analytic Kepler comparison.
- GMAT comparison.

## Reconsider when
- Long-duration propagation (days or weeks) or high-eccentricity orbits make fixed steps inefficient.

## Related
- Decision Request: DR-0004
- Proof: proof/physics.md
