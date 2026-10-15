# Decision Request: GMAT time-alignment method for M2 finite-burn references, and REV-012 disposition

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** M2 Propulsion; REV-012 (M1 review); DR-0015 (conditional); VAL-0009, VAL-0010

## Problem
DR-0015 conditions every GMAT acceptance gate on investigating REV-012. VAL-0010 found two verified GMAT mechanisms; neither is an error in our code:
- **M-a:** each `Propagate` command re-rounds the double A.1 MJD epoch. The epoch column and `Sat.ElapsedSecs` drift linearly with the number of commands (M1: −1.06e-4 s). The states themselves are at the requested elapsed times.
- **M-b:** GMAT rounds the final step to a time stop condition to whole microseconds. Each time-stopped `Propagate` (ignition, burn end, coast end) can land up to about 0.81 µs off. At 53 700 s this costs 6.2 cm per µs of burn duration, which explains the 1.17 cm VAL-0009 residual.

Two decisions are needed:
1. how M2 GMAT references must be generated and aligned before any gate is set;
2. how REV-012 is dispositioned.

## Constraints
- Committed reference data is evidence; replacement requires review (DR-0009).
- No silent change to M1 baselines or GMAT thresholds.
- Gates must test our physics, not GMAT's time bookkeeping.

## Options — M2 reference generation
### A — Aligned stepping plus mandatory alignment verification (recommended)
- Generated M2 scripts use `InitialStepSize = MaxStep` equal to a divisor of every stop time (coasts 60 s; burns 1 s, or a divisor of the commanded duration's microsecond grid). Every stop then lands on a natural step and M-b rounding is a no-op.
- Report rows come from one streaming `Propagate` per arc (`Report` per step), not chains of short commands, so M-a never accumulates.
- Each generated reference is **verified before use**:
  - burn duration from GMAT mass vs commanded;
  - ignition and stop times vs Kepler on coast arcs;
  - per-step rows confirming MaxStep-limited steps.
- The verification limits are a separate item in the M2 threshold DR. VAL-0010 measured ≤ 6e-10 s duration and ≤ 1e-9 s stop error.
- Measured: GMAT vs independent DOP853 **12 µm / 1.4e-8 m/s, uncorrected**, identical at three epochs.

**Pros**
- No post-hoc correction of reference data.
- GMAT agreement improves about 1000×, so a GMAT gate can be tight enough to test our RK4 error (≈ 0.3 m) independently.

**Cons**
- Fixed small steps during burns (1 s) slow GMAT. Measured runtime is still seconds.
- Alignment can fail silently in stiffer cases; hence the mandatory verification.

### B — Natural stepping; measure GMAT's actual boundary times and compare against a reference propagated with those times
**Pros**
- Uses GMAT's default propagator configuration. 6.8 µm after correction.

**Cons**
- The comparison depends on numbers extracted from GMAT's own output, which is more complex and easier to get wrong.
- Our simulator would be compared against GMAT at non-commanded times.

### C — Natural stepping; bound the effect analytically and widen the gate
**Pros**
- No new tooling.

**Cons**
- The gate needs about 5 cm of slack for timing alone (0.81 µs × 6.2 cm/µs). That hides real differences of the same size, so it is weaker evidence.

## Options — REV-012 disposition
- **R1 (recommended):** mark REV-012 **resolved (cause verified: GMAT M-a)**. No M1 change: M1's approved comparison aligns on `ElapsedS` labels, at states verified to 9e-10 s, and the committed reference reproduces byte-for-byte. Update the GMAT README deferral note to cite VAL-0010.
- **R2:** keep it deferred until a gated time-dependent force exists.

## Effect on DR-0015 candidates (informational; nothing changed)
- The O9 rationale "1 MJD ulp per burn boundary" (mass candidate 1e-7 kg) rests on the refuted VAL-0009 hypothesis.
- The 2.5e-2 m GMAT-vs-DOP853 candidate reflects unaligned stepping.
- Both must be re-derived from measurements under the chosen option and submitted in the M2 threshold DR.

## Recommendation
**A + R1.**

## Impact
- Architecture: none in the simulator. The GMAT M2 script generator (T6) adopts aligned stepping and verification.
- Science/validation: GMAT gates can resolve our RK4 error rather than GMAT timing.
- Dependencies: none.
- Development effort: low to moderate (T6 generator plus verification checks).
- Token/compute impact: negligible.
- Reversibility: high until the M2 GMAT reference is committed.

## Blocked work
- T6 (GMAT M2 reference) and every O9 threshold.

## Work continuing independently
- T2–T5 if authorized; analytic and DOP853 oracles do not depend on this.

## Requested response
`A` / `B` / `C`; `R1` / `R2`.

## Resolution
**Decision:** APPROVED, A + R1 (Tech Lead, 2026-10-10).
- **Aligned GMAT stepping** with mandatory alignment verification is approved for M2 burn reference comparisons.
- **The VAL-0010 investigation is accepted:** per-command epoch re-rounding (M-a) and final-step microsecond rounding (M-b).

**Conditions:**
- Preserve the original reproduction and document why aligned stepping is appropriate.
- Keep reproducible verification of the reported improvement (≈ 1.2 cm → 12 µm).
- Mark REV-012 resolved **only after** evidence, tests and documentation are integrated into the M2 branch and verified.
- Do not silently loosen any physics accuracy threshold.

**Follow-up:**
- The investigation branch was merged into M2 in `391985f`, with its original commits `e47ce31` and `ba42395` preserved.
- A verification test and the REV-012 status update follow in the M2 branch.
- T6 must generate the M2 GMAT reference with aligned stepping.
- DR-0015 O9 candidate values are re-derived under this method in the threshold DR.
