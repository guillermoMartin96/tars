# Decision Request: Milestone 1 force-model scope

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
A real spacecraft at 250 km is strongly perturbed:
- J2 (Earth's oblateness) regresses the node by about −5.4°/day at i = 51.6°.
- Atmospheric drag causes noticeable decay within days.

M1 needs a defined force model so that "stable propagation" has a precise meaning.

## Constraints
- Never invent scientific behaviour.
- Every included force needs research, an assumption entry, and validation.
- M1 is the foundation milestone at the prototype bar.

## Options
### A — Point-mass two-body only
**Pros**
- Has an exact analytic solution (Kepler), so the integrator can be verified against truth.
- Smallest scientific surface area.

**Cons**
- Not a realistic prediction of a 250 km orbit. Diverges from reality by hundreds of km over 10 orbits.

### B — Two-body + J2
**Pros**
- Captures the dominant perturbation.

**Cons**
- No exact analytic oracle.
- Requires more research and validation work.

### C — Two-body + J2 + drag
**Pros**
- Closest to reality.

**Cons**
- Needs an atmosphere model, solar-activity inputs, and a ballistic coefficient, all of which significantly expand scope.

## Recommendation
A, with an extensible force-model boundary so B and C plug in later.

## Impact
- Architecture: the `ForceModel` protocol must support summing multiple forces.
- Science/validation: SCI-0001 to SCI-0004 document the omissions explicitly.
- Dependencies: none.
- Development effort: lowest.
- Token/compute impact: none.
- Reversibility: high (forces are additive).

## Blocked work
- Force model and M1 Proof criteria.

## Work continuing independently
- Tooling and decision records.

## Requested response
`A` / `B` / `C` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:** M1 uses point-mass two-body gravity only. J2 and atmospheric drag are explicitly deferred. Keep the force-model architecture extensible so additional forces can be added later without redesigning the simulator.  
**Follow-up:** ADR-0003 (force-model boundary); SCI-0001, SCI-0004.
