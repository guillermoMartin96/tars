# Decision Request: Definition of simulation determinism

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
Floating-point results can differ in the last bits across CPUs, operating systems, compilers, and library builds (for example, through fused multiply-add or vectorized math). "Deterministic" needs a precise, testable definition.

## Constraints
- Replay must be exact enough to debug failures.
- CI may run on a different platform from development.

## Options
### A — Bit-identical on the same platform with pinned dependencies; cross-platform agreement within a measured, documented tolerance
**Pros**
- Achievable and testable.
- Strict where it matters (replay on one machine).

**Cons**
- Cross-platform replay is not bit-exact.

### B — Bit-identical everywhere
**Pros**
- Strongest guarantee.

**Cons**
- Would require avoiding platform math libraries or using fixed-point arithmetic. Disproportionate for M1.

## Recommendation
A.

## Impact
- Architecture: no hidden randomness; integer tick time.
- Science/validation: the determinism validator compares hashes.
- Dependencies: pinned with `uv.lock`.
- Development effort: low.
- Token/compute impact: none.
- Reversibility: high.

## Blocked work
- Determinism validator threshold.

## Work continuing independently
- Everything else.

## Requested response
`A` / `B` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:** Require bit-identical repeatability on the same platform with pinned dependencies. Cross-platform results must agree within a documented, measured tolerance.  
**Follow-up:** `toolbox/validators/determinism.py`; record the cross-platform tolerance once measured (macOS dev vs Linux CI).
