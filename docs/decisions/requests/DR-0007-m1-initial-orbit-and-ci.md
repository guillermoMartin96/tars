# Decision Request: M1 initial orbit and CI

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
The milestone states "approximately 250 km LEO". The concrete initial state and the CI policy both need to be fixed.

## Constraints
- The orbit should avoid element singularities where possible.
- The orbit should remain meaningful once J2 is added later.
- CI must not require GMAT.

## Options
### A — Circular orbit, 250 km above R_E, i = 51.6°, Ω = 0, u = 0, epoch 2026-01-01T00:00:00 TT; GitHub Actions for lint, tests, determinism, and non-GMAT Proof
**Pros**
- Inclined, so the equatorial Ω singularity is avoided.
- ISS-like.
- Its node crossings define orbit counting cleanly.

**Cons**
- Circular, so ω and ν are undefined. The argument of latitude is used instead.

### B — Equatorial orbit
**Pros**
- Simpler geometry.

**Cons**
- Ω is undefined.
- Node-crossing orbit counting is impossible.

## Recommendation
A.

## Impact
- Architecture: none.
- Science/validation: the scenario file is the single source of the initial state.
- Dependencies: GitHub Actions.
- Development effort: low.
- Token/compute impact: CI replaces manual checking.
- Reversibility: high.

## Blocked work
- Scenario file and CI workflow.

## Work continuing independently
- Everything else.

## Requested response
`A` / `B` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:**
- Use the proposed circular 250 km, 51.6° inclination orbit and epoch.
- Enable GitHub Actions for linting, tests, determinism checks, and the M1 Proof checks that do not require GMAT.
- Keep GMAT external validation outside required CI for M1.

**Follow-up:** `scenarios/m1_leo_250km.json`; `.github/workflows/ci.yml`.
