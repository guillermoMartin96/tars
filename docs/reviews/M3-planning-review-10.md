# M3 Planning Review 10 (independent)

**Scope:** the corrections authorized by the Tech Lead's instruction "I-9 — M3 Planning Verification Hardening and Codex Review 10" (I-9), in commits `03707a8` and `6396141`. Those are M3P9-F1 (oracle ±∞), M3P9-F2 (order and sign assertions per formula) and the E3/E4 coverage for M3P9-F3, together with the revised mutation check and the new assertion-removal sweep. The review also covered all earlier findings, the DR-0028 mathematics, M1/M2 preservation, scope and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a14adc-471a-7c92-998b-ec9389a96028`, run at `1f1383b` on a fresh git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review10-prompt.md`. It carries I-1 to I-9 verbatim, the full review history, the corrections, the M1/M2 preservation evidence and the decision state. It requires a concrete counterexample for every new defect wherever feasible, and does not ask the reviewer to approve the package.
- Raw output: `raw/M3-planning-codex-review10.md`.

**Instruction for this outcome (I-9 §9):** "If Review 10 returns REQUEST_CHANGES or identifies any new BLOCKER, MAJOR, or MINOR finding: Record every finding and its evidence. Record the disposition as pending or accepted, as appropriate. Do not implement further corrections. Do not run Review 11. Do not prepare an acceptance report. Stop and request my next authorization."
- **None of the findings below has been applied.**
- No review 11 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** one new MINOR finding (a verification defect) and one NOTE (an optional improvement). There is no BLOCKER or MAJOR finding, and no mathematical or documentation defect. **M3P9-F1 and M3P9-F2 are RESOLVED, and the E3/E4 coverage for M3P9-F3 is in place.**

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P9-F1 | **RESOLVED** | Oracle ±∞ in either component gives 600 non-finite failures over the grid, or 1 at the single sample, plus both coverage failures. Independent weakenings to `isnan` and `isinf` exit 1, and review 09's partial-infinity counterexample exits 1 |
| M3P9-F2 | **RESOLVED** | Doubled coefficients give 560 (Δi) or 504 (ΔΩ) order failures; reversed signs give the corresponding sign failures. Removing each component's order or sign assertion, either whole assertion, or both together exits 1 |
| M3P9-F3 | **RESOLVED (E3/E4 coverage)** | Removing E3 or E4 alone exits 1. Their checks are unchanged, and the smallest-step limitation is documented accurately as intentional |

### The reviewer also confirmed independently
- **Preservation:** two runs are byte-identical. Against an independent run of `faba9d6`, no pre-existing output value changed. AST comparison shows only `EXACT_MUTANTS`, `by_formula_test` and `main` changed among the existing definitions; the oracle, formulas, wrap, grid, tolerances, checks and minima are unchanged.
- **Coverage:** 506/532 order samples and 560/504 sign checks recomputed, each equal to its separately enforced minimum; the zero sets exclude 40 and 96 of 600 series.
- **Mutation suite:** two runs byte-identical and equal to the committed report: 109/109 detected, no vacuous expectation, 5/5 controls classified correctly. The reconstructed 60-case matrix matches review 09's described structure. Exact equivalence with review 09's scratch files cannot be established, because those files were not retained.
- **Order and sign:** doubled and halved coefficients give 560/504 order failures with no sign failure; reversed signs give 560/504 sign failures.
- **Mathematics:** the signed derivatives, the line-of-nodes regimes and node reversal, the perpendicular-axis closed form and the inclination bound were rederived. 20 000 cases against an independent rotation implementation agree to 4.44e-16 (rotation), 8.88e-16 (line-of-nodes inclination) and 1.33e-15 (closed-form node); 99 938 finite inputs match exact rational wrapping. The i = 2°, δ = 5° and review-04 examples reproduce.
- **Research reruns:** the sensitivity and Q10 outputs are byte-identical.
- **History and scope:**
  - all earlier records and raw outputs are unchanged or appended to;
  - the corrections and dispositions remain recorded, and superseded statements keep their pointers;
  - all whole-branch changes are under `docs/`, and the protected paths are unchanged;
  - registers 218/0 and 43/0; only status or index rows removed.
- **Preservation gates:** m1_proof 7/7; full m2_proof 228/228; both GMAT comparisons; snapshot verify-baseline; local cross-platform; all five determinism runs. All pass.
- **Partial or unavailable, as the reviewer reported:**
  - its pytest run was interrupted after 290 passed, so it is not a full-suite run;
  - the complete Proof wrappers, fresh GMAT executable runs and three-platform execution were not rerun;
  - CI could not be checked (no GitHub API access);
  - external source bytes were not retrieved.

## Dispositions (recorded; not applied)

### M3P10-F1 (MINOR, verification defect): a caught infrastructure exception can count as detection for the intended reason
**Where:** `dr0028_node_signed_mutation_check.py`, `holds()` and `classify()`; with `mutant_failures()` in `dr0028_node_signed_verification.py`.

**Finding.**
- `mutant_failures()` records a raising built-in mutant as not rejected. That is sound: the verdict fails closed.
- However, the harness's `not_rejected` predicate checks only that the rejection flag is false. `classify()` then reports the exception and still accepts the mutation as detected for its declared reason.
- **Counterexample:** the reviewer kept the order assertion intact and inserted an unrelated import inside `formula_scaled()`, raised only for factor 2. It then classified the run against the expected predicates of `order_assertion_disabled`. The run was accepted as detected ("expected rejection shown"), with both doubled-coefficient mutants recorded as raising `ModuleNotFoundError`, while all five supplied controls still passed. The reviewer reproduced the same with a `ZeroDivisionError` in the order and sign conditions.
- The existing import-failure control covers only a failure that ends the process.
- **Not affected:** the reviewer states this does not produce a false passing verdict from the verification script, and does not affect any mathematical result.

**Disposition: ACCEPTED.** The implementer reproduced it independently with the committed `run()` and `classify()`. The insertion was `import m3p10_unrelated_missing_module` inside `formula_scaled()` for factor 2, with the expectations of `order_assertion_disabled`. The result: classified as detected, with both doubled-coefficient mutants recorded as raising `ModuleNotFoundError`.
- **Cause:** amendment 6 made a raising built-in mutant count as not rejected, so that a crash would never count as a rejection. That fail-closed choice is correct for the verdict. The harness, however, uses "not rejected" as the evidence of an assertion's removal, and does not tell a raising mutant apart from one whose designated assertion stayed silent.
- **Affected mutations:** three committed mutations are detected through a raising mutant: the E2 and E5b finite-check removals (wrap guard ValueError) and the oracle check weakened to `isnan` (math domain error). They are now "detected" by the same mechanism the counterexample exploits. Their detection is not wrong, but the intended reason is not checked narrowly.

**Proposed change (not made):**
- Make `not_rejected` require that the designated mutant ran to completion with no exception, so that its designated checks were evaluated and stayed silent.
- Declare an expected exception explicitly, and narrowly, for the mutations that intentionally produce one: the exception type and message prefix, and the mutant that raises it.
- Add the caught-import-failure case, and a caught exception of another type, as negative controls that must be classified as not detected.

### M3P10-F2 (NOTE, optional improvement): the 18 surviving assertion removals remain a documented coverage limitation
**Finding.**
- The reviewer reran the sweep (35/17/18, identical) and inspected every survivor: E1's deviation bound; five in E2; three in E5; two in E6; six finite and one non-finite wrap assertion.
- All are present. Their independent geometry and wrapping checks found no corresponding correctness defect.
- The documentation records the limitation accurately, and the reviewer finds no basis for making all 18 mandatory corrections. Their scope disposition is the Tech Lead's.

**Disposition: ACCEPTED as a NOTE.** No change is proposed by this finding. Whether to add targeted mutants for the 18 survivors remains open for the Tech Lead.

## Validation evidence at the reviewed commits (implementer)
- **`6396141`**, isolated clone:
  - M1 Proof overall PASS (9 steps, exit 0), full pytest 1185 passed, 0 failed, 0 skipped;
  - M2 Proof overall PASS (20 steps, exit 0), full pytest 1185 passed, with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism for four scenarios and m2_proof;
  - the evidence differs only in run metadata, and the M2 final-state record is identical apart from `revision`, `tree_clean` and `sha256`.
- **CI** for `6396141`: run 39048537648, all four jobs success (check ubuntu-latest, macos-latest, macos-15-intel; m2-cross-platform). The reviewer could not verify this independently.
- **Worktree:** the verification script, the mutation check and the sweep each ran twice with byte-identical outputs; 109/109 mutations detected, and 5/5 controls classified as not detected; Ruff passes.

## Status after this review
- This is not an unconditional PASS, so the I-9 §9 stop condition applies.
- **No acceptance report has been prepared, and no review 11 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:**
  - a decision on M3P10-F1;
  - whether to protect the 18 surviving assertions (M3P10-F2, and the scope question from amendment 6);
  - any further review.

## Resolution of findings (appended 2026-10-17; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "I-10 — Resolve M3P10-F1 and authorize Review 11" (2026-10-17), referred to as **I-10**. It authorizes:
- the correction of M3P10-F1 and its regression and negative controls;
- the evaluation of the 18 assertions, with mutation coverage for those of category A;
- exactly one further review (review 11), after local verification succeeds.

It does not authorize planning acceptance, a merge, any implementation, or any change to approved formulas, constants, tolerances, thresholds or baselines.

### M3P10-F1 (MINOR): a caught infrastructure exception could count as detection
- **Reproduced before the fix:** the implementer's own reproduction (recorded above). `dr0028_node_signed_harness_regression.py` also reproduces it, by running the controls against the reviewed harness at `896d52d`.
- **Root cause:** amendment 6 recorded a raising built-in mutant as "not rejected", which is correct for the verdict. The mutation check, however, read "not rejected" as evidence that an assertion had been removed.
- **Correction:** DR-0028 "Resolution amendment 7" (appended), with pointers under amendment 6.
  - **Verification script:** each built-in mutant's injected function is recorded against its reference implementation, showing whether the defect was exercised. An unexercised mutant fails the run. An exception is recorded with its type, message and in-script call stack.
  - **Mutation check:** six classification categories. "Not rejected" requires a completed, exercised mutant. An exception is accepted only under an explicit allowance (mutant, type, message, stack).
  - **Allowances:** they cover the E2/E5b wrap guard and the order-estimate math domain error. The latter is the documented `isnan` case, which occurs in four mutations through one mechanism.
- **Controls:** 13, each with a declared category. The five M3P10-F1 regression controls fail against the original harness and pass against the corrected one: import failure and runtime exception inside a mutant; an exception suppressed inside a mutant; an allowed exception at the wrong location; an allowed exception of the wrong type.

### M3P10-F2 (NOTE): the 18 assertions
- **Evaluated under I-10 §4** (amendment 7), with executed evidence in `dr0028_node_signed_assertion_classification.py`.
- **Result:** 6 A, 9 B, 3 C, 0 D. The six of category A (W2, N1, E2b, E2c, E2d, E5d) gain built-in mutants, and the sweep now reports 23 detected and 12 surviving.
- **No category D**, so no decision is required by I-10 §4.

### Evidence
- **Repeatability:** two runs each of the verification script, the mutation check, the sweep, the classification and the regression demonstration are byte-identical.
- **Results:** 109/109 mutations are detected for their declared reason, and 13/13 controls receive their category.
- **Finite results and coverage:** every pre-existing output value is identical to `896d52d`; only keys were added. Coverage is unchanged: 506/532 order samples and 560/504 sign checks.

### Status
- **Residual uncertainty:** none known. The `isnan` allowance covers four mutations rather than one, and amendment 7 states this.
- **Changes an acceptance decision?** No decision changed.
