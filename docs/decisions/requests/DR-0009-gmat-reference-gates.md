# Decision Request: Harden the M1 GMAT reference gate (external review REV-001, REV-003)

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit; follow-up to DR-0008; review `docs/reviews/M1-orbit-review-01.md`

## Problem
The external review (REV-001, High) showed that the approved GMAT gate, `gmat_reference.position_error_max_m ≤ 0.6 m`, cannot by itself detect a μ mismatch between our model and the GMAT reference.

The DR-0008 rationale I wrote was numerically wrong:
- **What I claimed.** A GMAT-default-μ mismatch "adds about 0.16 m along-track".
- **What actually happens.** The comparison starts both tools from the same Cartesian state, so a different μ also changes GMAT's semi-major axis: Δa/a ≈ −Δμ/μ. The period then shifts by ΔT/T ≈ −2·Δμ/μ, which is 8.1e-6 s per orbit, not 2.0e-6 s. That is about **0.63 m** after 10 orbits.
- **The consequence.** Whether ours-vs-GMAT passes 0.6 m then depends on the sign of the error relative to our RK4 lag. The reviewer showed a mismatch of the same size but opposite sign passes, at 0.33 m.

Separately, the "initial-SMA check" that DR-0008 said would catch a mismatch was computed but never gated.

**Current results are not affected.** The committed GMAT R2026a reference shows an initial SMA difference of 1.9e-9 m (a mismatch would give 5 mm), and GMAT agrees with the exact Kepler solution to 7.2 µm.

**Already fixed without new tolerances (exact checks):**
- The committed GMAT script must equal the script regenerated from the current scenario, so the `Earth.Mu` line must match.
- The metadata constants must equal the scenario constants.
- The script and report sha256 values must match.
- The report must cover the full 60 s grid (REV-002).

What remains is gating the **numerical** evidence that GMAT actually *applied* those constants and that the reference is accurate. That needs new tolerances, and tolerances need your approval (DR-0004).

## Constraints
- Tolerances must be justified (playbook/testing.md).
- The gate must not depend on the sign coincidence described above.
- GMAT may change slightly across versions.

## Options
### A — Fixed engineering bounds, far above measured values and far below any meaningful mismatch (recommended)

| `gmat_reference` metric | Threshold | Measured | What it detects |
|---|---|---|---|
| `gmat_vs_kepler_position_error_max_m` | 1e-4 | 7.2e-6 | GMAT not reproducing our two-body model (μ, frame, forces, accuracy); detects relative μ errors above about 1e-13 |
| `gmat_vs_kepler_velocity_error_max_mps` | 1e-7 | 8.4e-9 | Same, in velocity |
| `initial_sma_difference_m` | 1e-6 | 1.9e-9 | The μ actually applied by GMAT. The GMAT default would give 5.0e-3, 5 000× the limit. |
| `initial_state_difference_m` | 1e-6 | 0.0 | A different initial state. The 16-digit km report resolution is about 1e-9 m. |
| `period_difference_s` | 1e-8 | 9e-13 | μ or SMA mismatch (the default μ gives 8.1e-6) |
| `velocity_error_max_mps` (ours vs GMAT) | 7e-4 | 3.49e-4 | Same bound as the approved Kepler velocity limit |

**Pros**
- Each gate is sign-independent and targets a specific failure mode.
- Bounds are 10–1 000× above measured values, so they survive GMAT version noise.
- They remain 3–4 orders of magnitude below any physically meaningful configuration error.

**Cons**
- Not the "≈2× measured" convention of DR-0008.

### B — ≈2× measured (the DR-0008 convention)
**Pros**
- Consistent with DR-0008.

**Cons**
- The SMA and initial-state values are at the report's printing resolution (about 1e-9 m), so 2× is noise-dominated and fragile.
- A GMAT update would likely force re-approval.

## Also requested
1. **REV-003, CI scope.** ADR-0006 said CI compares against the committed GMAT CSV; your DR-0007 instruction was to keep GMAT external validation outside required CI. The comparison needs only committed files, not a GMAT install. I recommend **adding `gmat_m1.py compare` to CI**, so every push is checked against GMAT; GMAT itself is never run in CI. Until you decide, I have aligned ADR-0006 with your instruction: compare runs locally via `toolbox/scripts/run_m1_proof.sh`.
2. **Initial-state literal bound (REV-014).**
   - The provenance check compares the six initial-state literals in the committed GMAT script with this platform's regenerated values. They differ by about 1 ulp across CPUs (measured: 0 m and 1.29e-12 m/s on CI).
   - It currently uses, as an **interim**, the approved final-state cross-platform bound (1e-4 m, 1e-7 m/s), which was approved for a different quantity.
   - Proposed explicit bound: **1e-6 m and 1e-9 m/s**, more than 700× the measured spread and still about 1.5e-13 rad.
3. **Re-confirm the 0.6 m GMAT position threshold** now that its approval rationale has been corrected. Under option A the new gates catch a μ mismatch, so 0.6 m only needs to bound our RK4 error, as for the Kepler gate. I recommend keeping it.

## Recommendation
Option A, add compare to CI, approve the initial-state literal bound, and keep 0.6 m.

**Independent check:** the reviewer re-derived the corrected physics and ran option A against the real reference (passes) and against μ mismatches of ±7.5e-10, 1e-12 and 2e-13 relative (all fail, regardless of sign). See the review addendum.

## Impact
- Architecture: none.
- Science/validation: strengthens VAL-0004.
- Dependencies: none.
- Development effort: a few lines in `proof/thresholds/m1.json` and `ci.yml`.
- Token/compute impact: about 3 s of CI.
- Reversibility: high.

## Blocked work
- Resolution of REV-001 (High). Under proof/review.md, M1 Proof stays **BLOCKED** until this is decided.

## Work continuing independently
- None remaining for M1; all other review findings are fixed.

## Requested response
`A` / `B` / `discuss`; CI compare `yes` / `no`; initial-state bound `approve` / `change`; 0.6 m `keep` / `change`

## Resolution
**Decision:** APPROVED — Option A (Tech Lead, 2026-10-05).  
**Reasoning/notes:**
1. All proposed sign-independent GMAT reference gates and limits are approved.
2. CI runs the comparison against the committed reference. GMAT itself is not required in CI.
3. The REV-014 initial-state literal bounds are approved: 1e-6 m and 1e-9 m/s.
4. The 0.6 m GMAT position threshold is kept. The reference and initial-state gates now cover reference correctness, so this threshold mainly accommodates the expected RK4 error.
5. Regenerating or replacing the committed GMAT reference data requires explicit review. It is never updated automatically in response to a failing comparison.

**Follow-up:**
- The gates are in `proof/thresholds/m1.json` under `gmat_reference`.
- The CI step is "GMAT reference comparison".
- `gmat_m1.py run` refuses to replace an existing reference without `--replace-reason`, which is recorded in the metadata.
- The policy is documented in the GMAT README and playbook/science.md.
- Regression test: `test_approved_gates_reject_mu_mismatch_of_either_sign`.
