# Decision Request: Threat model for the independent false-pass review of M2 validators

**Status:** APPROVED — option B (Tech Lead, 2026-10-11)  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-11  
**Related milestone/issue:** M2 T6 (O9); review record `docs/reviews/M2-T6-review-01.md`; T5 review `M2-T5-review-01.md`

## Problem
T6 requires an unconditional Codex PASS before completion. The review was asked to sweep **potential false passes**, and it has found real defects. They fall into two groups.

**1. Real defects, all now fixed**
- Reference acceptance, provenance, publication atomicity, the replacement guard and coverage.
- Thresholds that disable gates.
- Unchecked oracle outputs at the trust boundary: DOP853 states and dense output, and Kepler propagation in node bisection.
- Non-finite metrics passing the final gate.

**2. An open-ended class (re-verifications 3–7: F16, F18–F20, F22–F23, F26)**
The probes now monkeypatch an internal arithmetic helper *of the validator itself* to return a non-finite value. Some downstream arithmetic then turns that value into a finite passing number:
- `_ulp → ±inf` made a residual ratio zero (F26);
- `simpson_bound → inf` made `max(err − inf, 0)` zero (F23);
- builtin `max(x, nan)` returned `x` (F16, F19);
- an inner reducer was bypassed through an alias (F27).

Each finding is fixed with a runtime check at that site. The space is every arithmetic expression in about 2 000 lines of validator code, so the class has no natural end. Seven re-verification rounds so far have each produced one to three new instances.

The terminal gates already reject any non-finite **result**:
- `Check` rejects any non-finite gated metric;
- `report_only_metrics_finite` and standalone O9 reject any non-finite reported metric;
- the oracles validate their outputs where they are produced and where they are consumed.

What remains reachable only by **editing the validator's own code** (replacing one of its helpers) is: a non-finite *intermediate* that arithmetic maps to a finite pass.

The decision is whether that remainder is in the scope of the runtime false-pass review, or is governed by code review, tests and static guards like any other change to validator source.

## Constraints
- The Tech Lead's T6 conditions require an unconditional PASS, and approved validation contracts may not be changed silently. Changing the review's scope is therefore escalated here, not decided by the implementer.
- No gate, threshold or measured value may be weakened by this decision.
- M1 and T5 behavior must be preserved. They are: the 212 prior Proof checks are bit-identical.

## Options
### A — Keep the open-ended scope; continue rounds until PASS
**Pros**
- Maximal runtime defense in depth.

**Cons**
- Unbounded effort: each round finds new expressions, and each fix adds runtime invariant checks for the validator's own internals.
- Diminishing value: the probes simulate a corrupted validator, which source review and tests already guard against.

### B — Define the threat model explicitly, then one final review round under it (recommended)
**In scope, as runtime checks** (all currently implemented and tested):
- **Wrong or tampered simulator outputs:** events, `RunResult`, the CLI summary.
- **Wrong simulator physics:** mutants.
- **Committed artifacts:** GMAT scripts, reports, logs, metadata, the manifest and its history, thresholds.
- **Workflows:** generate, run, compare, publication and its interruptions.
- **Invalid outputs of the independent references at their trust boundary:** DOP853 states and dense output, Kepler propagation, GMAT rows. These are validated where produced and where consumed.
- **The terminal guarantee:** every gated or reported metric is finite, otherwise the check fails.

**Out of scope for runtime checks; covered by code review, unit tests and the AST guard:**
- Replacing a validator-internal arithmetic helper (for example `_ulp`, `simpson_bound`, `excess_over`, unit conversions) with arbitrary return values.
- This is equivalent to modifying validator source.
- The AST guard (reviewed max/min allowlist, ufunc methods, aliases and bindings) and the targeted tests protect the known hazards.

Then **one final Codex re-verification under this threat model**, requiring an unconditional PASS within it.

**Pros**
- Bounded, explicit and reviewable: the guarantee a passing Proof gives is stated precisely.
- Keeps every defense already built.

**Cons**
- Accepts that a deliberately corrupted validator helper could, in principle, produce a false pass that runtime checks would not see. That risk is mitigated by source review and tests.

### C — Accept T6 now with the remainder documented as residual risk
**Pros**
- No further review cost.

**Cons**
- No unconditional PASS, contrary to the T6 condition, unless explicitly waived.

## Recommendation
**B.** The last six rounds' findings all require editing the validator's own helpers. The defects that matter for the M2 Proof are closed:
- wrong simulator outputs or physics;
- tampered or unproven references;
- unsafe workflows;
- invalid oracle outputs;
- any non-finite metric.

Stating the threat model makes the PASS meaningful and bounded. It also preserves the T6 condition that an unconditional PASS is required, within a scope the Tech Lead has approved.

## Impact
- **Architecture:** none.
- **Science/validation:** documents precisely what the M2 false-pass review guarantees. No gate or value changes.
- **Dependencies:** none.
- **Development effort:**
  - A: open-ended;
  - B: one review round plus any in-scope findings;
  - C: none.
- **Token/compute impact:** A is high; B and C are low.
- **Reversibility:** high. The scope can be widened later, for example for T8's external review.

## Blocked work
- T6 completion: the final review round and the PASS. All T6 implementation is done and pushed.

## Work continuing independently
- The re-verification 7 findings (F26–F28) are fixed, mutation-tested and pushed; they are in scope under every option.
- Nothing else is started. T7 needs authorization.

## Requested response
`A` / `B` / `C` / `discuss`, with any changes to the in-scope list.

## Resolution
**Decision:** APPROVED — option B (Tech Lead, 2026-10-11).

**Recorded review scope:**
- **In scope:**
  - incorrect simulator output or physics;
  - tampered or corrupted GMAT references or threshold files;
  - failures in the generate/run/compare workflows;
  - invalid outputs from independent references;
  - missing observations or thresholds;
  - any non-finite metric (NaN, +∞, −∞) reaching the validation or Proof boundaries.
- **Out of scope:** adversarially replacing or modifying the validator's own internal helper implementations. This is treated as equivalent to editing validator source, a risk covered by code review, unit and mutation tests, and the automated validator checks (AST guard, terminal finiteness gates).
- **Constraint (Tech Lead):** the boundary must **not** let bad simulator, GMAT, independent-reference, threshold or workflow data pass merely because it travels through an internal helper. The exclusion applies only to attacks that require modifying or replacing validator implementation code. Bad *data* flowing through unmodified helpers stays fully in scope.

**Reasoning/notes:** this states the guarantee of a passing M2 Proof precisely, keeps every existing defense, and bounds the review. No gate, threshold or measured value changes.

**Follow-up:**
- One final Codex re-verification of T6 under this scope; an unconditional PASS is required.
- The scope is recorded in the T6 review record and VAL-0014.
- It can be widened later, for example for T8's external review.
