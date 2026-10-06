# Decision Request: GMAT validation workflow

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
GMAT is the project's initial primary orbital reference, but it is not installed. We need to decide:
- who installs and runs it;
- which version to pin;
- how its results enter the repository.

## Constraints
- No privileged or system-wide changes without approval.
- CI must not need GMAT.
- Comparisons must be reproducible.

## Options
### A — Engineer guides the install; engineer owns the scripts and outputs, which are committed to the repository
**Pros**
- Reproducible.
- CI uses the committed reference CSV.
- The Tech Lead keeps control of machine changes.

**Cons**
- Requires one manual install step.

### B — Run GMAT in CI
**Pros**
- Fully automated.

**Cons**
- Heavy, platform-fragile, and slow.

## Recommendation
A.

## Impact
- Architecture: none.
- Science/validation: GMAT two-body comparison is a gate. A realistic-model comparison is informational.
- Dependencies: GMAT is an external tool, not a code dependency.
- Development effort: moderate.
- Token/compute impact: none.
- Reversibility: high.

## Blocked work
- GMAT comparison results only.

## Work continuing independently
- GMAT script authoring and comparison tooling (testable on synthetic data).

## Requested response
`A` / `B` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:**
- Guide the Tech Lead through installing and pinning the latest stable GMAT release compatible with this Mac. Make no privileged or system-wide changes without approval.
- The engineer owns the GMAT scripts, exports, comparison tooling, and committed validation artifacts.
- A realistic GMAT model may be included as informational and non-gating, provided it does not materially expand M1 scope.
- When installation becomes necessary, stop and give the exact install steps.

**Follow-up:** `toolbox/references/gmat/`.
