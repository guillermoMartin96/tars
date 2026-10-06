# Decision Request: Canonical Earth constants source

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
- Earth's gravitational parameter (GM) differs slightly between standards. WGS 84 uses 398600.4418 km³/s². GMAT's default Earth Mu is 398600.4415 km³/s².
- The difference shifts the 250 km orbital period by about 2×10⁻⁶ s per orbit, which is about 0.16 m along-track after 10 orbits.
- That is comparable to the expected RK4 error. Mismatched constants would therefore be misread as integrator error.

## Constraints
- Reference comparisons must use identical constants.
- Scientific values must come from authoritative sources.

## Options
### A — WGS 84 (GM = 3.986004418e14 m³/s², a = 6 378 137 m); configure GMAT to match
**Pros**
- WGS 84 is an authoritative published standard (NGA.STND.0036).
- Its GM equals the IERS Conventions (2010) value.

**Cons**
- GMAT scripts must override the defaults explicitly.

### B — Adopt GMAT defaults
**Pros**
- No GMAT configuration needed.

**Cons**
- The project's physics would be defined by a tool's default rather than by a standard.

## Recommendation
A.

## Impact
- Architecture: constants live in one module and are injectable through configuration.
- Science/validation: SCI-0005.
- Dependencies: none.
- Development effort: low.
- Token/compute impact: none.
- Reversibility: high.

## Blocked work
- SCI-0005 and the GMAT script.

## Work continuing independently
- Everything else.

## Requested response
`A` / `B` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:** Use WGS 84 as the canonical Earth constants source. Configure GMAT validation cases to use matching constants. Keep physical constants centralized and configurable rather than scattered through implementation code.  
**Follow-up:** `src/tars/sim/constants.py`; SCI-0005; GMAT script overrides.
