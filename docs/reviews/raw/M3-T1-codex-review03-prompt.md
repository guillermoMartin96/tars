You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T1 Review 03** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T1 (the J2 force model). It is a fresh review of the correction pass made after T1 Review 02. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct. This covers the corrected code's docstrings, tests and comments; VAL-0020 and its two correction sections; the DR-0025 owner-disposition note; the T1 authorization packet's erratum; the Review 01 and Review 02 records and their appended sections; the T1 report; and the experiment scripts and result files. You are not limited to the Review 01 and Review 02 findings.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t1-j2-force-model`, detached at the pinned head **`4b85ded298e521f5c72b606cd012dec8b56e9c5e`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available. GMAT is not provided; T1 contains no GMAT work (T5 scope).
  - The implementer made two checkouts of `src/` with `git archive <sha> src`; you can recreate them yourself from git:
    - `review_scratch/reviewed_src_b1566ae/src`, the Review 02 state (`b1566aea7d4b74ea785d6433a3bc6da37c67e23a`; its `forces.py` equals `1cf0ce9`'s). It is the first argument of `docs/science/experiments/m3-t1/t1_review02_correction_check.py`.
    - `review_scratch/reviewed_src_97b69ef/src`, the Review 01 state. It is the first argument of `t1_review01_correction_check.py`.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Prefer writing experiment output into `review_scratch/`; every T1 script takes an output path. If you re-run anything in place, record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- <path>`, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`.
  - You may run:
    - `pytest` (the full suite takes about 25–30 min on this host; `tests/test_constants.py tests/test_zonal_j2.py` takes about 5 s);
    - `ruff check .` and `ruff format --check .`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0*.py` (about 4 min);
    - the scripts in `docs/science/experiments/m3-t1/`:
      - `t1_j2_informational.py` (about 35 s);
      - `t1_mutation_check.py` (about 4 min; it copies `src/` to a temporary directory);
      - `t1_review01_correction_check.py`, `t1_review02_correction_check.py` and `t1_review02_survivors.py`.
  - Finish with a clean tracked tree.
- **I-20 §6 preconditions were checked by the implementer, not by you.** You have no network and cannot authenticate CI or the implementer's local runs. The implementer's statements of these facts are in "The implementer's claims" below. The exported GitHub run metadata (`gh run view --json`) is in `review_scratch/ci/`. Treat all of these as implementer-supplied claims: inspect them for internal consistency and list their authenticity as a verification limit. **This is not a reason to stop.** Perform the complete review; everything that can be checked locally must be checked.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect. You must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.
- **Decision boundaries (I-20 §9; I-19 §9).** You may recommend, but do not resolve, and do not record as approved, any of the following:
  - DR-0029 P1–P9; Q-G2-1/P6; Q-G2-2; DR-0028 P6(b);
  - the secular-rate tolerance or presentation; T4/T5 comparison requirements; the M3 final time step; the axis representation (T3); external corroboration.

  The owner has already decided several things (I-19 §7, I-20 §2–§3); assess whether each is **accurately recorded** and implemented, and do not re-decide it:
  - the dual-number disposition;
  - the choice of `float` conversion for R2-F2;
  - the acceptance of the exploratory mutation survivors and the classifier observation as documented limitations.

## Commits
- **`main`** = `60648b93385a9954194730006aeac29ea14875ad`.
- **T1 implementation:** `5fd24a2`, `e23675c`, `81a0d56`, `97b69ef` (Review 01 at `97b69ef92e589ebd1b71016f49c4c9816d8c724b`).
- **Review 01 record:** `dbb960a`.
- **Review 01 corrections (I-19):** `62d3684`, `a27f288`, `b0164fd`, `16a8e63`, `1cf0ce9`. Review 02 was at `1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4`.
- **Review 02 record:** `b1566ae` (`docs/reviews/M3-T1-review-02.md`, `docs/reviews/raw/M3-T1-codex-review02*`, `docs/reviews/raw/M3-T1-review02-reproduction/`).
- **Review 02 corrections (I-20)** (`git log b1566ae..4b85ded298e521f5c72b606cd012dec8b56e9c5e`):

  | Commit | Content (as claimed) |
  |---|---|
  | `56ad329` | Tests for R2-F1, R2-F2 (red against `b1566ae`) |
  | `bbcf40e` | Test adjustment: float16 tested on J2 only |
  | `304d796` | `src/tars/sim/forces.py`: owned binary64 parameters; product-underflow checks |
  | `308f126` | Tests: one coefficient-chain case per product; acceptance asserted, not erroring |
  | `a4dfda1` | Evidence: mutation harness (+ results), `t1_review02_correction_check.py` (+ results), `t1_review02_survivors.py` (+ results), R2-F3 docstring |
  | `2f82c00` | Records: VAL-0020 correction 2, Review 01 erratum (R2-O1), Review 02 record appendices, README addendum, status notes |
  | `c456881` | Records: count corrections |
  | later commits, if any | validation records only (docs); check |

## Review findings and their current dispositions
| ID | Severity | Finding | Disposition |
|---|---|---|---|
| M3T1-R1-F1 | MINOR | Mutable `mu`/`equatorial_radius`/`j2`; cached coefficient stale | ACCEPTED (I-19); corrected `a27f288`; Review 02: PARTIALLY RESOLVED (caller-owned inputs, R2-F2) |
| M3T1-R1-F2 | MINOR | Silent numerical-domain loss (DR-0024 R6) | ACCEPTED (I-19); corrected `a27f288`; Review 02: PARTIALLY RESOLVED (R2-F1) |
| M3T1-R1-F3 | NOTE | Test docstring a·r ∝ r⁻⁴ should be r⁻³ | Review 02: RESOLVED |
| M3T1-R1-F4 | NOTE | Finite mutation coverage; four survivors; hex literal | Review 02: RESOLVED |
| M3T1-R2-F1 | MINOR | Component-product underflow: k (1 − 5 s²) rounds to zero with representable exact component | ACCEPTED (I-20); claimed corrected `304d796` |
| M3T1-R2-F2 | MINOR | Accepted NumPy parameters stored by reference (caller-side mutation); float32 arithmetic persists | ACCEPTED (I-20), conversion to built-in `float` chosen; claimed corrected `304d796` |
| M3T1-R2-F3 | NOTE | `t1_review01_correction_check.py` docstring claims trajectory states | ACCEPTED (I-20); claimed corrected `a4dfda1` |
| M3T1-R2-O1 | NOTE | Review 01 record says "8 F2" protection mutants; actual 7 | ACCEPTED (I-20); claimed corrected by an appended erratum |

Review 02's raw output, prompt and reviewer evidence (including its three exploratory mutant diffs under `own_mutants/`) are in `docs/reviews/raw/M3-T1-codex-review02*`.

## The implementer's claims for this pass (to verify, not to trust)
1. **R2-F2.** μ, R and J2 are converted to built-in `float` at construction, before validation.
   - Supported types: `int` (not `bool`), `float`, NumPy integer and floating scalars, and zero-dimensional arrays of those.
   - Every other type raises `TypeError`. An out-of-range `int` raises `ValueError`.
   - Mutating a caller's array after construction has no effect. float32 inputs give binary64 arithmetic and results equal to the same values passed as floats. Python-float inputs are unchanged bit for bit.
2. **R2-F1.** A binary64 product that is below the normal range and inexact is called an underflow, and raises `ValueError`. This applies to:
   - k (1 − 5 s²) and k (3 − 5 s²) in the acceleration;
   - −(3/2) J2, × μ and × R in the constructor's coefficient chain. This case was found by the implementer, not reported by Review 02, and was included under R2-F1. The implementer flags it as a possible scope question for the owner; judge it yourself.
   - Exact zeros and exact subnormal products are not underflow, and a final component may be subnormal.
   - The implementer states a limitation: a latitude factor that is mathematically 0 but computed non-zero, together with a tiny k, raises.
   - The implementer states that, with the canonical constants, |k × factor| ≥ 1.6e-299 inside the accepted domain, so the checks cannot trigger. Near the factor zeros a component has only absolute accuracy, relative to the |k|·|r| majorant; this is unchanged.
   - The evaluation order is unchanged.
3. **Bit identity.** Compared with `b1566ae`: 200 004 states give 0 differences, and three RK4 trajectories (6 001 states each) are bit-identical. The informational results and the Review 01 correction-check results reproduce byte for byte. The equatorial domain is unchanged.
4. **R2-F3, R2-O1.** The docstring is corrected with output unchanged; the erratum is appended. Count corrections are appended to the I-20 records: R2-F1 has 9 cases, and there are 107 T1 cases over both T1 test files.
5. **Red-first.** The final tests give 26 failed / 81 passed of 107 T1 cases against `b1566ae`.
6. **Mutation.**
   - 46 committed mutants: 14 original, 8 from Review 01, 10 R1 protection removals and 14 R2 protection removals (7 F1, 7 F2). All 46 are killed by assertion, with no survivors. Four original anchors were re-anchored with the same defects.
   - Review 02's exploratory mutants on the corrected code: `near_min_normal_zero` is killed; `canonical_one_ulp` and `narrow_band` survive, recorded as a limitation with a code-inspection argument.
   - The classifier is unchanged.
7. **Records.** All new record sections are append-only.
8. **Regression and CI.** The implementer reports the following, run locally on macOS (Apple silicon) at `c456881` (the later `4b85ded` changes only `docs/`):
   - full `pytest`: 1288 passed (1254 before this pass + 34 new T1 cases);
   - M1 Proof PASS 9/9 and M2 Proof PASS 20/20, each in a separate fresh clone;
   - the `m2_proof` validator 228/228;
   - the M1 golden digest `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`, and determinism;
   - T0 checks: 314 passed; T1 tests: 107 passed;
   - mutation 46/46 by assertion;
   - `t1_review01_correction_check.py`, `t1_review02_correction_check.py`, `t1_review02_survivors.py` and `t1_j2_informational.py` outputs byte-identical to the committed results. The re-run mutation results file differs from the committed one only in memory addresses inside 6 messages;
   - `ruff check .` and `ruff format --check .` clean;
   - `git diff 60648b9.. -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` empty.

   **GitHub Actions**, four required jobs each: `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform`. All are reported `success` on:
   - `a4dfda1` (run 40002590550), pushed together with `56ad329`…`308f126`, so the red-first and intermediate commits have no CI run of their own;
   - `2f82c00` (40002789138);
   - `c456881` (40002897696);
   - the pinned head `4b85ded298e521f5c72b606cd012dec8b56e9c5e` (40008016629);
   - the Review 02 record `b1566ae` (39906870674).

   Exported metadata is in `review_scratch/ci/run-<id>.json`. You cannot authenticate any of this: no network access, no signatures. Check the files for internal consistency (head SHAs, branch, conclusions, job names) and list their authenticity as a verification limit.

## Tech Lead's authorization I-20 (this review), verbatim

# I-20 — M3 T1 Review 02 Corrections and Review 03 Authorization

## 1. Checkpoint acceptance

I acknowledge the I-19 checkpoint.

Review 02 returned `REQUEST_CHANGES`. Its findings are independently reproduced and accepted for correction.

Current authoritative state:

- Branch: `milestone-3-t1-j2-force-model`
- HEAD/origin: `b1566aea7d4b74ea785d6433a3bc6da37c67e23a`
- Worktree: clean
- Main: `60648b9`, unchanged
- T1: IMPLEMENTED — REVIEW CHANGES REQUIRED — NOT ACCEPTED — NOT MERGED

The reported validation and CI evidence supports proceeding with a bounded correction pass. It does not constitute T1 acceptance.

## 2. Review 02 dispositions

**R2-F1 — MINOR: ACCEPTED**

Correct the remaining silent numerical underflow involving component products.

Requirements:

- Detect the demonstrated case where nonzero, representable mathematical acceleration is silently returned as zero.
- Cover the independently reproduced extreme-parameter case.
- Add off-axis and relevant component-level regression tests.
- Distinguish legitimate mathematical zeros from arithmetic underflow.
- Preserve bit-identical outputs for valid realistic-orbit cases.
- Avoid a blanket rejection of subnormal inputs or outputs.
- Do not claim complete IEEE-754 correctness from a finite test campaign.

The implementation may use additional checks or a numerically stable evaluation path, but must not introduce unbounded computational cost or unrelated numerical-policy changes.

If the proposed fix cannot preserve the established valid-state behavior, stop and report the tradeoff before proceeding.

**R2-F2 — MINOR: ACCEPTED**

Choose **conversion to built-in Python `float`**, not categorical rejection of all non-float numeric inputs.

Convert `mu`, `equatorial_radius`, and `j2` to owned Python float values at construction, before applying the governing physical-parameter validation.

Requirements:

- Store immutable scalar snapshots, not caller-owned mutable references.
- Ensure later mutation of a supplied zero-dimensional NumPy array cannot change the model's behavior.
- Prevent unintended persistence of `float32` arithmetic.
- Preserve the established validation contract for non-finite and physically invalid values.
- Reject unsupported or nonconvertible inputs with clear, consistent errors.
- Do not silently accept arbitrary containers or strings merely because `float()` can convert them; define and test the supported numeric input types.
- Preserve bit-identical behavior for existing valid Python-float inputs.

Add regression tests for caller-side mutation, supported NumPy numeric scalars, zero-dimensional arrays, `float32`, and invalid input types.

**R2-F3 — NOTE: ACCEPTED**

Correct the `t1_review01_correction_check.py` docstring.

Remove the unsupported claim that it checks RK4 trajectories. Preserve the actual check behavior.

Do not add trajectory work solely to justify the old wording.

**R2-O1 — NOTE: ACCEPTED**

Correct the historical mutant-count statement.

The correct protection-mutant breakdown is:

- F1: 3
- F2: 7
- Total: 10

Preserve the original review record's provenance. Use an explicit correction or erratum rather than silently rewriting historical evidence.

## 3. Mutation coverage disposition

Accept the reviewer's observation that three additional mutants survive the 73 T1 tests as a **documented verification limitation**, not an automatically blocking defect.

Do not claim that all possible or newly generated mutants are killed.

Distinguish:

1. The committed mutation campaign: 32/32 killed by meaningful assertions.
2. Additional exploratory mutants: three surviving.
3. The limits of finite sampling and mutation-based verification.

Record the three survivors, their triggering conditions, and why they do not presently invalidate the authorized T1 acceptance criteria.

Do not expand T1 into an exhaustive search for all possible mutation survivors.

If further analysis establishes that a survivor violates an explicit required invariant or acceptance gate, stop and elevate it for owner disposition.

The mutation-classifier observation is also accepted as a documented limitation for this pass. Do not modify the classifier solely on hypothetical runner behavior. If actual evidence shows misclassification, treat that as a new finding.

## 4. Preserve Review 01 corrections

Review 03 must verify that the original Review 01 defects remain resolved.

Specifically:

- R1-F1: parameter immutability, including caller-owned inputs.
- R1-F2: no demonstrated silent numerical loss.
- R1-F3: correct radial-dot-product scaling.
- R1-F4: previously surviving committed mutants killed by meaningful assertions.

Do not regress the previously validated dual-number disposition or positive-potential `+∇U` erratum.

## 5. Correction implementation constraints

Apply only changes necessary for R2-F1, R2-F2, R2-F3, R2-O1, their tests, and associated evidence.

Maintain the existing J2 physical formulation and governing constants.

Use red-first regression tests where practical.

For numerical corrections, provide evidence that distinguishes:

- the original failure;
- the corrected result;
- legitimate zero-valued components;
- underflow and overflow behavior;
- valid realistic-orbit preservation.

Do not introduce unrelated refactoring, new physics models, architecture changes, or broad changes to the M3 numerical contract.

## 6. Validation requirements

Before launching Review 03, run and record:

- Full pytest suite.
- T0 validation.
- M1 Proof and golden/determinism checks.
- M2 Proof and cross-platform validation.
- T1 numerical and physics tests.
- Committed mutation campaign.
- Reproduction tests for all Review 02 findings.
- Valid-state bitwise comparison against the appropriate pre-correction reference.
- Ruff and repository hygiene checks.

Repeat the existing 200,004-state comparison where feasible.

For the existing Python-float realistic-orbit domain, require bit-identical behavior. If any differences occur, stop and explain them before requesting review.

Preserve the three RK4 trajectory comparisons where applicable.

Require all four CI jobs green on the final pre-review implementation/evidence head.

Do not launch Review 03 while required CI is pending or red.

## 7. Independent Codex Review 03

Once the correction pass is complete and validated, authorize one independent Codex Review 03.

Use a fresh review context pinned to the corrected implementation SHA.

The reviewer must independently examine:

1. R2-F1 underflow correction, including legitimate zero components.
2. R2-F2 owned-scalar conversion, input validation, and caller-side mutation.
3. R2-F3 documentation correction.
4. R2-O1 historical count erratum.
5. Preservation of R1-F1 through R1-F4.
6. Preservation of realistic-orbit numerical results.
7. Mutation claims versus actual verification coverage.
8. Accuracy of the dual-number and `+∇U` dispositions.
9. M1/M2 regression guarantees.
10. Any newly introduced correctness, verification, or provenance defects.

Provide repository-local evidence and clearly identify CI facts the reviewer cannot independently authenticate.

Do not bias the reviewer toward PASS.

## 8. Stop conditions

If Review 03 returns `REQUEST_CHANGES`, or raises a new finding requiring owner disposition:

- Independently reproduce and classify the finding.
- Record the evidence and proposed disposition.
- Do not fix the new finding.
- Do not launch Review 04.
- Stop for my decision.

If Review 03 returns an unconditional `PASS` without unresolved findings:

- Prepare the T1 acceptance dossier.
- Include the final validation, mutation limitations, and unresolved assumptions.
- Stop for my explicit acceptance decision.

Do not automatically accept or merge T1.

## 9. Existing unresolved decisions

All items preserved by I-19 §9 remain open.

This authorization does not resolve DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular-rate tolerances, T4/T5 comparison requirements, the M3 final time step, or external corroboration.

Do not start T2 or T3.

## 10. Repository and reporting requirements

Use ordinary commits and fast-forward pushes only. No force-push.

Preserve the existing review records, raw outputs, evidence, and reproduction history.

At the next checkpoint provide:

- Branch, HEAD/origin, and worktree state.
- Exact commits and changed paths.
- Before/after reproductions for each finding.
- Local validation and CI evidence.
- Valid-state bitwise comparison.
- Mutation results and limitations.
- Review 03 verdict and findings.
- Updated T1 status and outstanding decisions.

**Authorization granted for the bounded Review 02 correction pass and, after all required validation gates pass, Independent Review 03.**

## Earlier Tech Lead authorizations
- I-17 (T1 authorization) and I-18 (Review 01) are reproduced verbatim in `docs/reviews/raw/M3-T1-codex-review01-prompt.md`.
- I-19 (Review 01 corrections and Review 02) is reproduced verbatim in `docs/reviews/raw/M3-T1-codex-review02-prompt.md`.
- Read them there.

## What to review (I-20 §7 items 1–10)
Evaluate each item independently, with your own derivation, execution or computation wherever possible.
- **A numerical sweep is not a substitute for a valid mathematical argument.** For every exactness, bound or contract claim, check the proof against the code, and use sweeps to seek counterexamples.
- **Actively try to falsify.** Construct inputs, mutation paths and wrong implementations that the corrected tests accept.

1. **R2-F1 underflow correction, including legitimate zero components.**
   - Verify the definition and its implementation against IEEE 754 semantics and the code.
   - Search for any remaining path where a non-zero, representable exact component is returned as zero or as a precision-lost value without a diagnostic. Cover:
     - every multiplication, division and addition chain in the constructor and in `acceleration`;
     - off-axis points; both latitude factors; all components;
     - extreme but accepted parameters; subnormal inputs; J2 = 0; signed zeros.
   - Check that legitimate zeros and exact subnormal results are returned, and that subnormal inputs or outputs are not rejected wholesale.
   - Check the stated limitation and the canonical-constant reach argument, including the minimum non-zero factor magnitudes.
   - Check that the exact-rational comparison has bounded cost.
   - Judge whether the coefficient-chain extension is within I-20's authorized scope.
2. **R2-F2 owned-scalar conversion, input validation and caller-side mutation.**
   - Verify conversion before validation, the supported-type definition and its enforcement, and the error types and messages.
   - Test caller-side mutation, the NumPy scalar types (float16, float32, float64, longdouble, integer types, 0-d arrays, unsigned, NumPy `bool_`, object or string arrays), Python `int` extremes and subclasses, and any other path by which a non-binary64 or caller-owned value reaches the arithmetic.
   - Check that Python-float behaviour is bit-identical.
3. **R2-F3 documentation correction**, and that the script's behaviour and output are unchanged.
4. **R2-O1 historical count erratum**: correct, explicit and append-only, with the original preserved.
5. **Preservation of R1-F1 … R1-F4** (I-20 §4). R1-F1 includes caller-owned inputs; R1-F2 means no demonstrated silent numerical loss; R1-F3 is the r⁻³ scaling; R1-F4 means the previously surviving committed mutants are killed by meaningful assertions. Re-run the Review 01 and Review 02 reproductions.
6. **Preservation of realistic-orbit numerical results.** Bit identity with `b1566ae` and `97b69ef` on your own sampling, the 200 004-state set and RK4 trajectories; the equatorial domain bounds.
7. **Mutation claims versus actual coverage.**
   - Re-run `t1_mutation_check.py` and `t1_review02_survivors.py`. Verify that each kill is by a meaningful assertion, not by an unexpected exception, a collection error or source inspection.
   - Verify that the re-anchored mutants keep their defects.
   - Check the documented limitations and the code-inspection argument for the two survivors.
   - Write your own mutants against the corrected code, including ones aimed at the new protections.
8. **Dual-number and +∇U dispositions.** Verify that they are not regressed and that no record overstates them.
9. **M1/M2 regression guarantees.**
   - Run pytest, the M1/M2 validators (output into `review_scratch/`), and the M1 golden and determinism checks.
   - Verify that `git diff 60648b9..4b85ded298e521f5c72b606cd012dec8b56e9c5e -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty.
   - Verify that `src/` changes are confined to `src/tars/sim/constants.py` and `src/tars/sim/forces.py`; in `forces.py`, only `ZonalJ2Gravity`, its helpers and its imports.
10. **New defects.** Search for new correctness, verification, provenance or reproducibility defects introduced by the correction pass, including in the records.
    - Check every number quoted in the new record sections against the code, the result files and your own computation.
    - Check append-only status with `git diff b1566ae..4b85ded298e521f5c72b606cd012dec8b56e9c5e -- docs`.
    - Check that the records do not claim complete IEEE 754 correctness or complete mutation coverage.

Also record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran, with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation or only on documentation.
2. **Resolution table:** M3T1-R1-F1 … F4 and M3T1-R2-F1, F2, F3 and O1, each marked exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with evidence and reasoning.
3. **Assessment of I-20 §7 items 1–10**, each separately.
4. **New findings.** Number them `M3T1-R3-F1`, `M3T1-R3-F2`, …. Each gives:
   - severity: BLOCKER, MAJOR, MINOR or NOTE, as defined in I-18 §4;
   - exact file and line references;
   - a reproduction, or reasoning that can be checked independently;
   - the consequence;
   - the recommended correction;
   - the relevant decision or validation requirement;
   - whether it is a defect, a proposed enhancement or an unresolved decision;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Adversarial attempts** and their outcomes.
6. **Verification limits.**
7. **T1 acceptance-readiness assessment.**
8. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any Review 01 or Review 02 finding that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
9. **Files:** write the complete review, identical to your final message, to `review_scratch/M3-T1-codex-review03.md`. Save your scripts and logs under `review_scratch/`, and keep a command ledger in `review_scratch/COMMANDS.md`.
