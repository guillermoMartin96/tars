# ADR-0003: Extensible force-model boundary and centralized constants

**Status:** Accepted  
**Date:** 2026-10-05  
**Decision owners:** Guillermo (Tech Lead, via DR-0002/DR-0003); implementing engineer

## Context
M1 uses point-mass gravity only (DR-0002), but J2, drag, and thrust must be addable without redesigning the simulator. DR-0003 requires constants to be centralized and configurable.

## Options considered
### Option A
A `ForceModel` protocol; the simulator sums the accelerations of all configured models.

### Option B
Gravity hard-coded into the integrator's derivative function.

## Decision
- `ForceModel` is a protocol: `acceleration(t, r, v) -> ndarray[3]`.
- `CompositeForceModel` sums its components.
- M1 provides `PointMassGravity(mu)`.
- `EarthConstants` (frozen dataclass) is defined once in `tars/sim/constants.py`:
  - `WGS84` is the canonical instance.
  - Scenarios may supply overrides, and the effective constants are recorded in the `SimulationStarted` event.
  - Physics code receives constants as parameters and never imports magic numbers.

## Reasoning
Additive forces match the physics: Newton's second law with superposition. The planned command path (burn → propulsion → force → integration) slots in as another `ForceModel`.

## Consequences
### Positive
- Adding J2, drag, or thrust is additive work.
- Constants are auditable in one place.

### Negative / tradeoffs
- A small indirection cost per evaluation.

## Validation
- Unit tests check gravity magnitude and direction.
- Tests check that composite models sum correctly.
- A grep-style test confirms that no WGS 84 literal appears outside `constants.py`.

## Reconsider when
- A force needs state beyond (t, r, v), for example mass or attitude for thrust or drag.
- At that point, extend the signature with a context object.

## Related
- Decision Requests: DR-0002, DR-0003
- Scientific assumptions: SCI-0001, SCI-0004, SCI-0005
