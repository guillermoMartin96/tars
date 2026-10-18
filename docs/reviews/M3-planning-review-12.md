# M3 Planning Review 12 (independent)

**Scope:** the correction authorized by the Tech Lead's instruction "I-11 — Resolve Review 11 Findings and Authorize Review 12" (I-11), in commits `7860316` and `bd6c8b4`. That covers M3P11-F1 (defect-specific mutation exercise, with an independent probe, its controls and the regression demonstration against `c16b3b5`) and M3P11-F2 (the classification of the 18 assertions, now 11 A / 4 B / 3 C, with five new targeted mutants). The review also covered the earlier findings, the DR-0028 mathematics, M1/M2 preservation, scope and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a14c3b-c8ae-7620-86bc-ab0b04193120`, run at **`5b12eece4d952450fc47a13c75059ef748fc007e`** (the prompt commit; parent `bd6c8b4`) on a fresh git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review12-prompt.md`. It carries I-1 to I-11 verbatim: I-1 to I-10 were checked byte for byte against the review 11 prompt, and I-11 against the instruction text. It requires the reviewer to reproduce the regression controls independently and to attempt its own counterexamples, and does not ask the reviewer to approve the package.
- Raw output: `raw/M3-planning-codex-review12.md`.

**Instruction for this outcome (I-11 §9):** "If Review 12 returns REQUEST_CHANGES: Record every finding. Do not fix the new findings. Do not start Review 13. Do not prepare an acceptance report. Stop and request my authorization." and "Under no circumstances merge or begin T0/T1/T2."
- **None of the findings below has been applied.**
- No review 13 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** two new MINOR findings, both unsound verification claims. There is no BLOCKER or MAJOR finding, and no defect in the committed mathematical results, the production code or the M1/M2 baselines.

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P11-F1 | **NOT RESOLVED** | The reassociated fallback is now rejected correctly, but a first-step-only oracle defect is certified as an all-steps defect (M3P12-F1) |
| M3P11-F2 | **NOT RESOLVED** | All five reclassified assertions have meaningful protection, but the E6-sign redundancy argument has a counterexample (M3P12-F2) |
| M3P10-F1 | **NOT RESOLVED** | The historical exception counterexamples are handled correctly; the broader intended-reason guarantee remains unsound through M3P12-F1 |
| M3P10-F2 | **NOT RESOLVED** | The inventory is correct, but E6-sign is still treated as redundant (M3P12-F2) |

### The reviewer also confirmed independently
- **Historical counterexample:** review 11's suppressed-import, reassociated-fallback construction, rebuilt from files read from git, is "expected rejection" at `c16b3b5` and "invalid mutation setup" at HEAD.
- **Regression demonstration:** all five M3P10-F1 and four M3P11-F1 historical failures reproduce; all 23 controls receive their declared category and exercise result. A further probe-only import failure of the reviewer's own is classified "invalid mutation setup", not detection.
- **Mutation suite:** committed output reproduced byte for byte: 109 attempted, 109 exercised, 109 detected; 23/23 controls; all other categories 0; 0 of 77 direct predicates met at baseline. Both exception allowances were rechecked against type, message and stack.
- **Classification and sweep:** 35 assertion sites, the same 18 historical survivors, 11 A / 4 B / 3 C; sweep 28 detected / 7 surviving / 0 exceptions. All 11 A demonstrations, including the five new ones, are sound. W1, W4 and E6-value have adequate redundancy arguments within the documented scope; the W3, W6 and E2a rationales are reasonable. E6-sign is disputed (M3P12-F2).
- **Numerical preservation:** verification twice, byte-identical; against an independent run of `cadccd8`, zero changed or removed pre-existing values and 315 added keys. AST comparison: oracle, formulas, wrap, grid, checks, tolerances and minima unchanged. Order 506/532 and sign 560/504 enforced separately; the 1 % Δi oracle mutant still gives one E3 and one E4 failure.
- **Mathematics:** 10 000 cases of conjugated Cartesian rotations, maximum oracle disagreement 1.78e-15 rad, no inclination-bound excess; central differences confirm both signed derivatives; ΔΩ = +0.259805543688° and the crossing example (Δi ≈ +1°, ΔΩ = 180°) reproduced; 9 997 finite random binary64 inputs match rational wrapping.
- **Research reruns:** sensitivity and atmosphere-residual outputs byte-identical; all 27 density jumps recomputed (at most 1.11e-16); lowest-band ratio 1.0013804525694443.
- **History and scope:** reviews 01–11 and the full amendment chain read; prior records and raw outputs preserved against `cadccd8`; I-1 to I-10 identical in the new prompt; all 78 whole-branch changed files under `docs/`; protected paths unchanged; registers 218/0 and 43/0; Ruff and relative links pass.
- **Preservation gates (standalone validators):** m1_proof 7/7; full m2_proof 228/228; both GMAT committed-reference comparisons; snapshot verify-baseline; local cross-platform checks and the M2 cross-platform record; five determinism runs; focused pytest 21 passed.
- **Partial or unavailable, as the reviewer reported:**
  - these were complete standalone validator executions, not complete Proof-wrapper executions; the full pytest suite was not rerun by the reviewer;
  - CI could not be checked (no GitHub API access for run 39075007905);
  - fresh GMAT executable runs, external-source retrieval and three-platform execution were not performed.

## Dispositions (recorded; not applied)

### M3P12-F1 (MINOR, unsound verification claim): the oracle-value probe cannot see a defect missing after the first invalid step
**Where:** `dr0028_node_signed_mutation_check.py`, `observe_oracle_values()`; `dr0028_node_signed_verification.py`, `check_formulas()`; DR-0028 amendment 8, exercise criterion.

**Finding.** Amendment 8 requires the intended defect to be "never missing". The oracle-values probe observes each value where `check_formulas()` hands it to `nonfinite_reason()`. After a component's first invalid value, `check_formulas()` skips that component for the rest of the series (`if errs[name] is None: continue`), so later values are never observed and a missing defect there cannot be counted.
- **Counterexample:** the reviewer applied the edit of `review09_oracle_delta_i_nan_first_step` while declaring the exercise predicate and expected rejection of `review09_oracle_delta_i_nan_all`, and likewise for ΔΩ. Each was classified "expected rejection", with the probe reporting intended 600, missing 0, unintended 0, while an independent trace of every constructed oracle dictionary found 600 non-finite and 2 400 finite values of that component.
- **Full entrypoint:** with this single falsely described mutation and all 23 controls, the harness reports PASS: 1 attempted, 1 exercised, 1 detected for the intended reason, 23/23 controls. Nothing was forged in the recorder, flags, exceptions or output.
- **Not affected:** the committed mathematical results. The defect is in the strength of the exercise claim for the oracle-values family.

**Disposition: ACCEPTED.** The implementer reproduced it independently in the reviewer's clone at `5b12eec`: for both components, classification "expected rejection", probe counts intended 600 / missing 0 / unintended 0, traced oracle values 600 non-finite and 2 400 finite.
- **Cause:** the observation point for oracle values (the finite validation) is downstream of the discard logic it is meant to be independent of, so the probe only sees the values the tested code chooses to validate. "Missing = 0" is therefore not evidence that the defect was present at every step it claims.
- **Relation to M3P11-F1:** the reassociated-fallback route is closed; this is a remaining route by which a mutation is credited with a stronger exercise than it had, so M3P11-F1 (and with it M3P10-F1) is not fully resolved.

**Proposed change (not made):**
- Observe every oracle value where it is produced (at the `oracle(...)` call in `check_formulas()`, or by wrapping the injected oracle in the probe), before any discard logic, and check observation coverage against the expected input schedule (every grid point and every step).
- Add, as negative controls for both components, the first-step-only injection declared as the all-steps mutation; they must be "invalid mutation setup".
- Review the other three exercise families for the same pattern (an observation point that tested code can skip).

### M3P12-F2 (MINOR, unsound verification claim): E6-sign alone protects the formula's sign at the preserved example
**Where:** `dr0028_node_signed_assertion_classification.py`, `premises_e6_sign()` and the E6-sign entry; DR-0028 amendment 8, category B argument.

**Finding.** E6-sign asserts `d_node > 0.0 and lin_node > 0.0`. The category B premise establishes E3's protection of the oracle's `d_node` at the same call, and states that the formula's sign "at this (i, Ω − φ) is covered on the first-order grid by the sign check". The first-order grid uses tilts `step_scale(inc) · 2^-k`, none of which is 0.15°, so the formula's sign at the review-04 example is protected only by E6-sign.
- **Counterexample:** in a scratch copy, the ΔΩ formula is multiplied by −1 only for 0.0026 < |δ| < 0.0027 (which contains 0.15° = 0.0026180 rad and no grid step). With E6-sign present: exit 1, verdict FAIL, exact failures `["E6 review-04 example sign disagreement"]`, no formula failures. With only E6-sign removed: exit 0, verdict PASS, no failures; order 506/532 and sign 560/504 and built-in defect exercise are unchanged.

**Disposition: ACCEPTED.** The implementer reran the reviewer's two entrypoints at `5b12eec` and obtained the same results (removed False: exit 1, FAIL, the single E6 sign failure; removed True: exit 0, PASS, none). The diff of the scratch copy against the committed script is exactly the formula line and the removed assertion.
- **Cause:** the premise for `lin_node > 0` was argued from coverage of the same (i, Ω − φ) on the grid, but the formula is also a function of δ, and the grid never evaluates it at E6's δ. The argument checked the oracle half of the conjunction at the same call and the formula half at a different call.
- **Effect:** the category B classification of E6-sign is not supported; by the reviewer's evidence it meets category A for its formula half. The totals would become 12 A / 3 B / 3 C (or E6-sign split into an oracle part, B, and a formula part, A), subject to the Tech Lead's decision. The sweep's surviving set would lose E6-sign.

**Proposed change (not made):**
- Reclassify E6-sign as category A (or split it as above) and add a narrowly targeted built-in formula mutant that reverses the ΔΩ sign only in a tilt interval containing 0.15° and no grid step, with the usual A evidence (exercised, no exception, rejected with the assertion, nothing reported without it).
- Correct amendment 8's classification totals and the E6-sign dependency statement with an appended amendment; recheck the remaining B premises (W1, W4, E6-value) for the same mistake (a premise established at a different call from the assertion's).
- No change to the order test's asymptotic design is needed; E6-sign already protects this sample.

## Validation evidence at the reviewed commits (implementer)
- **`bd6c8b4`**, isolated clone:
  - M1 Proof overall PASS (9 steps, exit 0), full pytest 1185 passed, 0 failed, 0 skipped;
  - M2 Proof overall PASS (20 steps, exit 0), full pytest 1185 passed, with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism for four scenarios and m2_proof;
  - the evidence differs only in run metadata; `m2_final_states_record.json` without `revision`, `tree_clean` and `sha256` is identical to the committed record. M2's `tree_clean: false` arises only because it ran in the same clone after M1 had rewritten M1's evidence log.
- **CI** for `bd6c8b4`: run 39075007905, workflow completed with conclusion success; each of the four jobs completed with conclusion success: check ubuntu-latest (117520220349), check macos-latest (117520220258), check macos-15-intel (117520220265), m2-cross-platform (117534128294). The reviewer could not verify this independently.
- **Worktree:** each of the five experiment tools ran twice with byte-identical outputs.

## Status after this review
- This is not an unconditional PASS, so the I-11 §9 stop condition applies.
- **No acceptance report has been prepared, and no review 13 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** decisions on M3P12-F1 and M3P12-F2, and on any further review.

## Resolution of findings (appended 2026-10-17; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "I-12 — M3 Planning: Review 12 Corrections and Review 13 Authorization" (2026-10-17), referred to as **I-12**.
- **It authorizes:**
  - the correction of exactly M3P12-F1 and M3P12-F2;
  - exactly one further independent review (review 13), after the corrections and local verification succeed.
- **It does not authorize:** planning acceptance, a merge, T0/T1/T2, changes to approved physics, resolution of outstanding decisions, or a review 14.

### M3P12-F1 (MINOR): the oracle-value probe could not see a defect missing after the first invalid step
- **Reproduced before the fix.** In the reviewer's clone at `5b12eec`: for both components, classification "expected rejection", probe counts intended 600 / missing 0 / unintended 0, while the traced oracle values were 600 non-finite and 2 400 finite. `dr0028_node_signed_harness_regression.py` reproduces it against the reviewed harness at `5b12eec`, run with that harness's own probe.
- **Root cause.** The observation point (the finite validation) was downstream of the discard logic in `check_formulas`, so the probe saw only the values the tested code chose to validate.
- **Correction.** DR-0028 "Resolution amendment 9" (appended), with a pointer under amendment 8.
  - The expected samples (3 000: every grid series × five steps) are built from the unmutated script before the copy runs.
  - The copy's `check_formulas` is run with an observing formula, which it calls at every step, after the oracle value and before any validation.
  - Each observation is identified by the formula's own arguments; the condition is evaluated on the scheduled sample, not on the copy's state.
  - Exercise requires every scheduled sample observed exactly once (none unobserved, duplicate or unscheduled), the defect confirmed wherever claimed (missing 0), nothing unintended and no exception.
  - On the unmutated script, all 22 oracle-value schedules are observed completely.
- **Controls.** Seven new ones (I-12 §3), each with its required reason; every one of the 30 controls now declares the reason it must show:
  - regression controls, failing against `5b12eec` and passing now: first-step-only corruption (Δi and ΔΩ), partial-step corruption (steps 0, 2, 4), missing intermediate observations (steps 1–3 skipped: unobserved 1 800), an incorrect observation count (last step twice: duplicate 600);
  - last-step-only corruption: invalid setup (missing 2 400); already rejected at `5b12eec`, so not a regression;
  - correctly injected all-step corruption: exercised at all 3 000 samples and detected.

### M3P12-F2 (MINOR): E6-sign alone protected the formula's sign at the preserved example
- **Reproduced before the fix.** The reviewer's two entrypoints at `5b12eec` give exit 1 / FAIL with E6-sign present and exit 0 / PASS with it removed. The classification now runs this counterexample before (`5b12eec`) and after.
- **Root cause.** The premise for the formula half was argued at the same (i, Ω − φ) but a different δ: the first-order grid never evaluates the formula at E6's tilt magnitude.
- **Correction.** DR-0028 "Resolution amendment 9", with a pointer under amendment 8's E6-sign argument.
  - E6's sign assertion is split into E6-sign-oracle and E6-sign-first-order, each its own assertion; together they reject exactly what the single one did.
  - E6-sign-oracle is category B (E3 at the same call, all five arguments). E6-sign-first-order is category A, with a new built-in mutant that reverses the first-order ΔΩ sign throughout the grid gap containing 0.15° ((0.1432°, 0.2245°)). E6 rejects it with exactly the first-order message, nothing rejects it without that assertion, and the first-order grid reports 0 failures for it.
  - W1, W4 and E6-value were re-examined for the same mismatch. Their premises are now checked at the same input as the assertion (W1: the same result in the same loop iteration, from the syntax tree; W4: the same inputs, relying on `wrap()`'s purity, stated; E6-value: the same call, all five arguments). All three stay B.
- **Classification:** 19 assertions, 12 A, 4 B, 3 C, 0 D; identities checked against the inventory and, mapped back, against the 18 survivors at `896d52d`.
- **Sweep:** 36 sites, 29 detected, 7 surviving (the 4 B and the 3 C).

### Evidence
- **Mutation check (corrected harness):** 109 attempted, 109 exercised, 109 detected for the intended reason. Not exercised, rejected for another reason, unexpected exception, process failure, invalid setup and normal execution: 0 each. 30/30 controls with category, exercise result and reason; 0 of 77 direct predicates met by the unmutated script; 22 of 22 oracle schedules fully observed there.
- **Regression demonstration:** the five M3P12-F1 controls fail at `5b12eec`, the four M3P11-F1 controls at `c16b3b5` and the five M3P10-F1 controls at `896d52d`; all 30 controls pass against the corrected harness.
- **Repeatability:** each of the five tools runs twice with byte-identical output.
- **Preservation:** against `5b12eec`, no pre-existing verification output value changed or was removed (23 keys added, all the new mutant's entry). Coverage is unchanged: 506/532 and 560/504.

### Status
- **Residual uncertainty:** none known.
- **Historical results** of amendment 8 (the oracle-value observations; 11/4/3 over 18 assertions) are kept as they were and are not relabelled.
- **Changes an acceptance decision?** No decision changed.
