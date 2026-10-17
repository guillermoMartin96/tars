# M3 Planning Review 09 (independent)

**Scope:** the correction authorized by the Tech Lead's instruction "Continue TARS M3 planning from `milestone-3-planning` at `0ac630b`" (I-8), in commits `1208090` and `ff08ef9`. That is M3P8-F1: finite validation of the signed first-order checks and per-formula minimum valid-sample counts, together with the bounded audit of the same failure class (I-8 §4) and the entrypoint mutation harness. The review also covered the whole DR-0028 amendment chain, the earlier findings, the preservation gates, and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a14866-12b1-7172-b2d0-c6d01541fe33`, run at `5515a7a` on a fresh git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review09-prompt.md`. It carries I-1 to I-8 verbatim, the full review history, the M3P8-F1 correction, the M1/M2 preservation evidence and the decision state. It instructs the reviewer not to accept earlier conclusions and to classify every finding as a mathematical, verification or documentation defect, or an optional improvement.
- Raw output: `raw/M3-planning-codex-review09.md`.

**Instruction for this outcome (I-8 §7):** "If review 09 returns REQUEST_CHANGES: Record every finding. Do not fix automatically. Do not initiate review 10. Do not prepare an acceptance report. Stop for my decision."
- **None of the findings below has been applied.**
- No review 10 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** two new MINOR findings (both verification defects) and one NOTE (optional improvement), with no BLOCKER or MAJOR finding and no mathematical or documentation defect. **M3P8-F1 is RESOLVED.**

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P8-F1 | **RESOLVED** | The finite-value guard rejects invalid oracle and formula values, discards their series from coverage, and enforces the four minima separately. 60 independent injection cases (42 formula-path, 18 oracle-path; NaN, +∞ and −∞; partial injections by step, series, tilt sign, near-equatorial and near-polar subsets) each exited 1 through the entrypoint and returned failures from `check_formulas()` |

### The reviewer also confirmed independently
- **Determinism and preservation:** two runs are byte-identical. Against an independent run of `0ac630b`, exactly one pre-existing value changed (`cos_sin_swapped` failing checks, 1576 → 1578); every other difference is an added key. AST comparison shows the oracle, formulas, wrap, noise bound and step scale unchanged.
- **Coverage:** 506/532 order samples and 560/504 sign checks recomputed; the exact sign zero sets exclude 40 and 96 of the 600 series; the four minima are enforced separately; the nearest gate ratios (1.012333, 0.993963; 1.549770, 0.495320) clear the 10⁻³ rounding allowance; no coverage was reduced.
- **Mutation harness:** two runs byte-identical and equal to the committed result, 33/33 detected. The two `exception: ValueError` detections (E2 and E5b finite checks removed) are acceptable: they exit nonzero, are labelled as exceptions, and are never reported as a PASS verdict.
- **Mathematics:** the signed formulas, the five line-of-nodes regimes, the endpoint singularities, the node reversal, the perpendicular-axis closed form and the inclination bound were rederived. 20 000 cases against an independent rotation implementation agree to 3.33e-16 (matrix), 6.66e-16 (identity) and 3.18e-15 (closed form), with no bound excess; 99 955 finite inputs match exact rational wrapping.
- **Research reruns:** the sensitivity and Q10 outputs are byte-identical.
- **History and scope:**
  - records 01–07 are byte-identical to `0ac630b`, and record 08 keeps its earlier bytes as a prefix;
  - registers 218/0 and 43/0; only three status or index lines removed;
  - 0 broken relative links; Ruff and `git diff --check` pass;
  - all 63 whole-branch changed files are under `docs/`.
- **Preservation gates:** m1_proof 7/7; full m2_proof 228/228; both GMAT comparisons; the snapshot verify-baseline; local cross-platform; M1 determinism and all four M2 determinism checks. All pass.
- **Partial or unavailable, as the reviewer reported:**
  - its pytest run was interrupted after 267 passed, so it is not a full-suite run;
  - the complete Proof wrapper scripts and three-platform execution were not rerun;
  - CI could not be checked (no GitHub API access);
  - external source bytes were not retrieved.

## Dispositions (recorded; not applied)

### M3P9-F1 (MINOR, verification defect): oracle ±∞ rejection lacks regression protection
**Where:** `dr0028_node_signed_verification.py`, `nonfinite_reason()` and `FORMULA_DEFECT_MUTANTS`; `dr0028_node_signed_mutation_check.py`.

**Finding.** The current guard rejects oracle ±∞, but nothing fails if it is weakened. The reviewer replaced `if num is None or not math.isfinite(num):` with `if num is None or math.isnan(num):`.

| Case | Exit | Verdict |
|---|---|---|
| Weakened guard alone | 0 | PASS |
| Current guard, oracle Δi = signed ∞ at i = 30°, Ω = φ = 0° only | 1 | FAIL |
| Weakened guard plus the same partial ∞ | 0 | PASS: 508 Δi order samples, observed-order range [NaN, NaN], no formula failures |

So after an undetected weakening, an invalid sample counts towards coverage. The oracle defect mutants exercise NaN only, and the harness has a weakened-to-`isnan` mutation for the formula check but not for the oracle check.

**Disposition: ACCEPTED.** The implementer reproduced the weakening independently: exit 0, verdict PASS.
- **Scope:** this is a regression-protection gap in the M3P8-F1 correction itself (I-8 §3 "Weakening an assertion so invalid samples escape detection fails"). It is not a mathematical defect, and the committed guard is correct.
- **Why it was missed:** the oracle mutants were added to make the oracle check load-bearing for NaN; ±∞ was covered only on the formula side.

**Proposed change (not made):**
- Add oracle +∞ and −∞ mutants for both components to `FORMULA_DEFECT_MUTANTS`, requiring designated `nonfinite` failures and exclusion from coverage.
- Add an entrypoint mutation weakening the oracle check to `math.isnan()`.

### M3P9-F2 (MINOR, verification defect): the order and sign assertions can each be disabled without rejection
**Where:** `dr0028_node_signed_verification.py`, `check_formulas()` (the `if p < P_MIN:` order assertion and the `if (n > 0.0) != (lin_v > 0.0):` sign assertion) and the formula-mutant acceptance checks; `dr0028_node_signed_mutation_check.py`.

**Finding.** Coverage stays satisfied when the assertion it is meant to accompany is disabled, and no mutant is required to be rejected by that specific assertion.
- Replacing either condition with `if False:` gives exit 0 and verdict PASS. The same holds for each of the four component-specific removals (order or sign, for Δi or ΔΩ).
- With the order assertion disabled, doubling both first-order coefficients (wrong formulas with the correct signs) still gives exit 0 and verdict PASS: 596 and 556 order samples, minimum observed orders 0.9948 and 0.9736, 560 and 504 sign checks, no formula failures.
- Sign-reversed mutants are still rejected by the sign check; with the sign check disabled, the order check rejects the existing mutants, which hides the missing sign assertion.

**Disposition: ACCEPTED.** The implementer reproduced both whole-check removals independently: exit 0, verdict PASS for each.
- **Scope:** this is the I-8 §4 class "coverage counters incrementing without valid assertions" and "missing assertions for one formula", which the bounded audit did not detect. Coverage counts samples that were gated into a check; they do not show that the check can fail. It is not a mathematical defect: the committed formulas pass both assertions genuinely.
- **Why it was missed:** the existing mutants each fail several checks at once, and their acceptance criteria did not require a failure from a designated assertion for each component.

**Proposed change (not made):**
- For each component, add a same-sign coefficient-error mutant (for example, a scaled first-order coefficient) that must be rejected by `order <component>`, and a sign-reversal mutant that must be rejected by `sign <component>`, each with a designated minimum failure count.
- Add four entrypoint mutations that disable the order or the sign assertion for Δi or for ΔΩ alone, each required to exit nonzero.

### M3P9-F3 (NOTE, optional improvement): further limits of the finite verification
**Where:** `dr0028_node_signed_verification.py`, the first-order checks and the E3/E4 mutation protection.

**Finding.** The following give exit 0 and verdict PASS:
- returning `(100.0, 100.0)` at the first three halving steps while keeping the formulas at the last two (order uses only the last two errors; sign uses only the last step);
- disabling E3's finite-deviation assertion;
- disabling E4's inclination-bound assertion.

The reviewer proposes no acceptance requirement; it asks that the limitations stay explicit, with protection added only if broader claims are intended.

**Disposition: ACCEPTED as a NOTE.** The first item is inherent to an asymptotic order test and does not contradict any committed claim. Whether to add E3/E4 assertion-removal mutations, in the same way as for M3P9-F2, is for the Tech Lead to decide.

## Validation evidence at the reviewed commits (implementer)
- **`ff08ef9`**, isolated clone:
  - M1 Proof overall PASS (10 steps, exit 0), with full pytest (1185 passed, 0 failed, 0 skipped);
  - M2 Proof overall PASS (20 steps, exit 0), with full pytest (1185 passed), the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism for four scenarios and m2_proof;
  - the evidence differs only in run metadata; without `revision`, `tree_clean` and `sha256`, the M2 final-state record is identical to the committed one; `toolbox/`, `tests/`, `scenarios/` and `src/` are unchanged.
- **CI** for `ff08ef9`: run 39003804587, all four jobs success (check ubuntu-latest, macos-latest, macos-15-intel; m2-cross-platform). The reviewer could not verify this independently.
- **Worktree:** script and mutation harness each run twice, byte-identical; 33/33 mutations detected; Ruff passes.

## Status after this review
- This is not an unconditional PASS, so the I-8 §7 stop condition applies.
- **No acceptance report has been prepared, and no review 10 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** decisions on M3P9-F1 and M3P9-F2, on whether M3P9-F3 warrants E3/E4 mutations, and on any further review.

## Resolution of findings (appended 2026-10-17; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "I-9 — M3 Planning Verification Hardening and Codex Review 10" (2026-10-17), referred to as **I-9**. It authorizes:
- the corrections of M3P9-F1 and M3P9-F2, and targeted mutation coverage for M3P9-F3 (E3 and E4);
- exactly one further review (review 10), after local validation passes.

It does not authorize planning acceptance, a merge, any implementation, or any change to approved formulas, constants, tolerances, thresholds or baselines.

### M3P9-F1 (MINOR): oracle ±∞ rejection lacks regression protection
- **Correction:** DR-0028 "Resolution amendment 6" (appended), with a pointer under amendment 5.
  - Eight built-in mutants: oracle Δi and ΔΩ each as +∞ and −∞, over the whole grid (600 non-finite failures, both coverage minima) and at a single sample (1 non-finite failure; both coverage minima, since that series is a valid sample of both checks).
  - File-level mutations: the oracle check weakened to `math.isnan` (all eight ±∞ mutants unrejected) and to `math.isinf` (both NaN oracle mutants unrejected); ±∞ injected into one oracle value of each formula through the entrypoint.
- **Review 09's counterexample** (oracle check weakened to `isnan`) is now detected for its declared reason.

### M3P9-F2 (MINOR): the order and sign assertions can each be disabled without rejection
- **Correction:** amendment 6. Per formula, a doubled first-order coefficient must fail that formula's order check in all 560 (Δi) or 504 (ΔΩ) series where the first-order term is nonzero, with no sign failure; a reversed sign must fail that formula's sign check in the same series.
- **File-level mutations:** each coefficient doubled through the entrypoint; the order and the sign assertion disabled for Δi only, for ΔΩ only, and for both. All six removals are detected because the designated mutant is no longer rejected.
- **Review 09's counterexample** (order assertion disabled, doubled coefficients) is now detected.

### M3P9-F3 (NOTE): further limits of the finite verification
- **E3 and E4 (I-9 §5):** a 1 % oracle inclination error must be rejected by E3 and by E4. Removing either assertion is a file-level mutation, and both are detected. E3 and E4 themselves are unchanged.
- **Step-size selection:** documented in amendment 6 as an intentional property of the asymptotic order test, and not changed, as I-9 §5 directs.

### Further changes under I-9 §6 (harness integrity)
- **Detection only for the declared reason.** The mutation check now accepts a detection only when the copy writes a FAIL verdict and the declared expected rejection holds. Five negative controls (syntax error, import failure, missing script, neutral edit, wrong reason) are each classified as not detected. There are 109 mutations in all: the 33 earlier ones, 16 new ones, and the 60 injection cases of review 09.
- **Built-in mutants that raise** are recorded as not rejected, so a crash never counts as a designated rejection.
- **Assertion-removal sweep (measurement).** Of the script's 35 assertions, 17 are detected when removed individually, including every assertion named by these findings. The other 18 survive alone: E1's deviation bound, five in E2, three in E5b/E5d, two in E6, six finite and one non-finite wrap assertion. Protecting them is outside I-9 §3–§5, so they are **recorded, not corrected**, for the Tech Lead's decision.

### Evidence
- Two runs each of the verification script, the mutation check and the sweep are byte-identical.
- Every pre-existing output value is identical to `faba9d6`; only keys were added. Coverage is unchanged: 506/532 order samples and 560/504 sign checks.

### Status
- **Residual uncertainty:** the 18 assertions that are not individually load-bearing (above).
- **Changes an acceptance decision?** No decision changed. The 18 survivors are an open scope question for the Tech Lead.

### Erratum (appended 2026-10-17)
"Validation evidence at the reviewed commits" above, and the review 09 prompt, give the M1 Proof as "10 steps". The wrapper runs **9** steps, all exit 0; the count wrongly included its final exit line. The result (overall PASS, 1185 tests passed) is unaffected.
