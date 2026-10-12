# Decision Request: Coordinated corruption of independent references (follows DR-0019 B, DR-0020 A)

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-11  
**Related milestone/issue:** M2 T6; DR-0019 (approved B); DR-0020 (approved A); review record `docs/reviews/M2-T6-review-01.md`, re-verifications 12–14

## Problem
DR-0020 A makes a reference-output finding blocking when the corruption could affect a check, a reported value or an acceptance decision. Every consumed reference quantity is now validated against a second, independent reference:
- DOP853 segment ends against Kepler (coasts) or an in-validator RK4 (burns), F47;
- the anchor tick positions against the DOP853 dense output, F49;
- Kepler output in O5 and the GMAT alignment against the simulator and GMAT.

Round 14 shows the method's limit. Each cross-check holds only while the two references are not corrupted *consistently with each other*:

| Finding | Corruption | Consumed quantity changed | Effect |
|---|---|---|---|
| **F50** | Kepler tick states at 1.001 × the flight time **and** DOP853 dense positions moved to match, at 17,876 ticks. Endpoints, nodes and stencils unchanged | `max_altitude_error_m` (O9 orbit_events) | **Acceptance reversed:** 0.01301 m > 0.013 m rejected with clean references; 0.012976 m accepted with the corrupted pair |
| **F51** | O6 midpoint Kepler returns at 10 × the flight time, in both the forward and the round-trip call, so the round trip and the two-body invariants still hold | O6 post-impulse SMA, `order_deviation_from_2_max`, `slice_finite_minus_impulsive_sma_m` | Reported and gated O6 values change (prograde 0.004102 → 0.004192); every check still passes |

Both are fixable *as constructed*. F50 needs a positional-continuity check of each tick against its stencil neighbours. F51 needs a cross-check of the O6 midpoint against DOP853. But each fix adds one more reference to agree with, and the next round can corrupt that one consistently too. DR-0020 already noted this for its option B: "does not close consistent corruption of both references, so the same question returns." Rounds 12, 13 and 14 each followed that pattern: F47, then F49, then F50.

The decision is how far the runtime reference checks must go, and how T6 can reach a bounded, meaningful PASS.

## Options
### A — Approved reference snapshot (recommended)
Pin the reference itself, the way the GMAT manifest is pinned.
- At an approved commit, record every **consumed** reference quantity for every M2 mission:
  - the DOP853 states at all marks;
  - the anchored altitude extrema;
  - the O6 midpoint states and post-impulse SMAs;
  - the node-crossing reference times;
  - the Kepler states used by O5.
- Store them in `toolbox/references/dop853/m2/`, with their sha256 in `approved_digests.py`. Under DR-0020 condition 5, any update goes through a reviewed commit with a justification.
- At runtime, the freshly computed references must match the snapshot within a reproducibility tolerance, set from the measured difference between macOS and Ubuntu CI. Any runtime corruption that changes a consumed value is detected, however many references it corrupts consistently.
- All existing checks stay. The snapshot is an added layer.

**Pros**
- Closes the whole class, not one instance: F42, F43, F50 and F51, and any future coordinated corruption of runtime reference outputs.
- Also detects the realistic risk behind these findings: a SciPy or NumPy upgrade, or a refactor, silently changing the reference.
- Bounded effort, and it reuses the existing manifest, anchor and digest machinery.

**Cons**
- A new approved artifact to maintain. Any change to a scenario, mark or reference setting needs a reviewed pin update.
- The snapshot is produced by the same references at approval time. Its correctness rests on the existing checks and the GMAT O9 comparison at the marks, at that moment.
- The reproducibility tolerance is a new numerical limit. It concerns the reference reproducing itself, not a comparison with GMAT, so the 15 µm GMAT floor does not apply. It must still be measured and justified.

### B — Bound the threat model to single-reference corruption
- In scope: corruption of **one** independent reference, including within one call site's forward and inverse calls when the other reference is untouched.
- Out of scope, recorded as accepted residual risk with mechanisms: mutually consistent corruption of **two or more** independent references.
- Fix F51 (one reference: Kepler forward and inverse) with a DOP853 cross-check of the O6 midpoint. Accept F50 as a two-reference corruption.

**Pros**
- Cheapest. It states the limit already reached and keeps every check.

**Cons**
- Leaves a demonstrated acceptance reversal (F50) as accepted risk.
- "Independent reference" needs a precise, reviewable boundary, or this becomes the next escalation.

### C — Keep fixing each instance
- F50 positional continuity, F51 DOP853 cross-check, then the next round.

**Cons**
- Unbounded, as DR-0020 predicted. Runtime keeps growing: the M2 Proof is already about 114 s.

## Recommendation
**A.** It turns a regress at runtime into a single reviewed fact: the consumed reference values approved at a known commit. That is the same approach that already protects the GMAT references and the thresholds (F32, F33). It also guards against what actually happens in practice, which is library and refactoring drift rather than adversarial library output.

If A's maintenance cost is not wanted at this stage, **B** is acceptable, provided the "independent reference" boundary is stated in the review contract.

## Impact
- **Architecture:** A adds one approved reference artifact and its pin; B and C add none.
- **Science and validation:**
  - No gate or approved threshold changes under any option.
  - A adds one measured reproducibility tolerance, which needs justification.
  - M2 thresholds remain provisional.
- **Development effort:**
  - A: moderate, roughly the GMAT manifest work;
  - B: small;
  - C: open-ended.
- **Reversibility:** high for all three.

## Blocked work
- The final T6 review round and the T6 checkpoint (Proof record, PR scope update, completion report).

## Work continuing independently
- Round 14's documentation notes are fixed: the F43 rationale after F49, the inventory of unused values, and the description of the VAL-0014 epoch column.
- F50 and F51 are dispositioned `ESCALATED_FOR_INVESTIGATION`. No fix has started, because the fix depends on the option chosen.

## Requested response
`A` / `B` / `C` / `discuss`.
