You are an independent verifier from a separate provider; you did not write any of the files under review. This is the **focused closure verification** of the TARS spacecraft simulator's Milestone 3, Task T1 (J2 force model), after Codex T1 Review 03.
- Review 03 returned `VERDICT: PASS (unconditional)` with two NOTE findings and one observation.
- The Tech Lead's authorization I-21 (verbatim below) approved a limited closure pass and this verification (§7). This is **not** a full Review 04. Verify the closure changes and their claims.
- You verify; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t1-j2-force-model`, detached at the pinned head **`e404b0f40a3a46c0a71041636e0f87eb5fa247f3`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`.
  - You may run:
    - `pytest`, including `tests/test_constants.py tests/test_zonal_j2.py` (about 5 s); the full suite takes about 25–30 min, so run it only if you judge it necessary;
    - `ruff check .`, `ruff format --check .`;
    - `docs/science/experiments/m3-t1/t1_mutation_check.py OUT` (about 4 min) with OUT under `review_scratch/`;
    - any script of your own.
  - Finish with a clean tracked tree.
- **The implementer's validation and CI cannot be authenticated by you** (no network). They are listed under "The implementer's claims" below, and the exported GitHub run metadata is in `review_scratch/ci/`. Treat them as claims: check them for internal consistency, and list their authenticity as a verification limit. **This is not a reason to stop.**
- **Decision boundaries.** Do not resolve, and do not record as approved, any open DR item: DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular tolerances, T4/T5 requirements, the M3 final time step, the T3 axis representation or external corroboration. T1 acceptance and merge are the owner's decisions, not yours.

## Commits
- `main` = `60648b93385a9954194730006aeac29ea14875ad`.
- **Review 03** reviewed `4b85ded298e521f5c72b606cd012dec8b56e9c5e`; recorded in `d01d6aaf008dc63b8b509fa1b0855bbac626a718`:
  - `docs/reviews/M3-T1-review-03.md`;
  - `docs/reviews/M3-T1-acceptance-dossier.md`;
  - `docs/reviews/raw/M3-T1-codex-review03{,-prompt}.md` and `-evidence/`;
  - `docs/reviews/raw/M3-T1-review03-reproduction/`.
- **I-21 closure** (`git log d01d6aa..e404b0f40a3a46c0a71041636e0f87eb5fa247f3`):

  | Commit | Content (as claimed) |
  |---|---|
  | `481a62e` | `tests/test_zonal_j2.py`: two tests for R3-O1 (upper-subnormal-band underflow, and its exact companion). Test-only |
  | `e404b0f` | VAL-0020 correction 3 (R3-F1, R3-O1); Review 02 provenance note (R3-F2); harness mutant 47 and `t1_mutation_check_results_i21.json`; README addendum |
  | later commits, if any | records only (docs); check |

## Findings being closed (dispositions by the owner, I-21)
| ID | Review 03 finding | Owner disposition | Claimed closure |
|---|---|---|---|
| M3T1-R3-F1 | NOTE: VAL-0020 correction 2 "Cost" says the exact-rational comparison is reached by no realistic state; exact-zero products do reach it (canonical example r = (12756274, 0, 6378137) m) | ACCEPTED; documentation only | VAL-0020 correction 3, first bullet |
| M3T1-R3-F2 | NOTE: the `mu_alias_set_-1` row of the Review 02 reproduction records μ read after the later mutation to 0 | ACCEPTED; appended clarification, raw files preserved | `docs/reviews/M3-T1-review-02.md`, last section |
| M3T1-R3-O1 | Observation: mutant `upper_subnormal_ignored` (threshold `_MIN_NORMAL / 2` in `_underflows`) survived all 107 T1 tests | ACCEPTED; test-only coverage of the existing coefficient-chain contract (I-21 §4–§5) | the two tests in `481a62e`; harness mutant `r3_upper_subnormal_band_ignored` |

## The implementer's claims (to verify, not to trust)
1. **Production code unchanged:** `git diff 4b85ded..e404b0f40a3a46c0a71041636e0f87eb5fa247f3 -- src` is empty. Every protected path is unchanged since `60648b9`: `proof`, `toolbox`, `scenarios`, `.github`, `uv.lock`, `pyproject.toml` and `src/tars/validation`.
2. **R3-O1 construction**, in units u = 2⁻¹⁰⁷⁴: μ = (2⁵² + 1) u, which is the normal number MIN_NORMAL + u; J2 = 1/2; R = 2¹⁰.
   - −(3/2) J2 = −3/4 exactly.
   - The exact −(3/2) J2 μ is −(3·2⁵⁰ + 3/4) u. In binary64 it rounds, not as a tie, to −(3·2⁵⁰ + 1) u, so it is inexact.
   - Both values lie strictly between 2⁵¹ u = MIN_NORMAL/2 and 2⁵² u = MIN_NORMAL.
   - The products × R and × R are exact, and k is normal, so only the underflow check can reject. Production raises "intermediate product underflows".
   - The companion μ = 2⁵² u gives exactly −3·2⁵⁰ u in the same band. It is accepted, and its result is the formula within 2γ₁₆.
3. **Mutation:**
   - 47/47 committed mutants are killed by assertion, with no survivors.
   - `r3_upper_subnormal_band_ignored` fails exactly one test, `test_coefficient_product_underflow_in_the_upper_subnormal_band_raises`, with "DID NOT RAISE ValueError".
   - Compared with the I-20 results, the other 46 mutants only gained failing tests (the new tests); none lost one.
   - Against the Review 03 tests (107 cases) the same mutant passes.
   - `t1_mutation_check_results.json` (the 46-mutant I-20 results) is unchanged.
4. **Counts:** 109 T1 cases now (97 in `tests/test_zonal_j2.py`, 12 in `tests/test_constants.py`). The 107 and 46 figures are kept as historical.
5. **Records** are append-only, and the Review 03 record and raw evidence are unchanged since `d01d6aa`.
6. **Remaining limitations:** the exploratory survivors `canonical_one_ulp` and `narrow_band` (Review 02) still survive and remain a documented, owner-accepted limitation. Complete mutation coverage is not claimed.
7. **Validation and CI:** The implementer reports the following, run on macOS x86_64 at `e404b0f40a3a46c0a71041636e0f87eb5fa247f3` in fresh clones with `uv sync --locked`:
   - M1 Proof: PASS 9/9 steps, `working_tree_clean_excluding_evidence: yes`.
   - M2 Proof (separate clone): PASS 20/20 steps, tree clean. `m2_proof` 228/228 PASS, threshold status approved. Full pytest **1290 passed**, 3 warnings (1288 + 2 new). M1 golden digest `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
   - The first attempt of both Proofs failed with exit 127 because the implementer's wrapper did not put `uv` on PATH. Both were re-run in new clones and passed; the failed attempt is kept in the implementer's notes.
   - T1 tests: 109 passed. T0 checks: 314 passed. Mutation: 47/47 by assertion.
   - `t1_review01_correction_check.py`, `t1_review02_correction_check.py`, `t1_review02_survivors.py` and `t1_j2_informational.py` outputs are byte-identical to the committed results.
   - `ruff check .` and `ruff format --check .` (238 files) are clean.
   - `git diff 60648b9..e404b0f40a3a46c0a71041636e0f87eb5fa247f3` on the protected paths, `git diff 4b85ded..e404b0f40a3a46c0a71041636e0f87eb5fa247f3 -- src`, and `git diff d01d6aa..e404b0f40a3a46c0a71041636e0f87eb5fa247f3` on the Review 03 record, dossier and `docs/reviews/raw` are all empty.

   **GitHub Actions**, four required jobs:
   - `e404b0f` = `e404b0f40a3a46c0a71041636e0f87eb5fa247f3`: run 40034728330, all success.
   - `d01d6aa` (the Review 03 record): run 40020290720. Attempt 1 failed `check (macos-15-intel)` only at "Upload Proof report", with `Failed to CreateArtifact: Unable to make request: ENOTFOUND`; every lint, test and Proof step of that job succeeded. Attempt 2 (re-run of the failed job) succeeded.
   - `481a62e` was pushed together with `e404b0f`.

   Exports are in `review_scratch/ci/`. You cannot authenticate them.

## What to verify (I-21 §7)
1. **R3-F1 and R3-F2 corrections.**
   - Accuracy, against the code and your own execution: the canonical exact-zero example, the Fraction-construction count, the result, the bounded-cost statement ("at most two … per evaluation, plus three at construction") and the non-zero reach argument.
   - Check that the corrections are appended, not rewrites, and that the raw reproduction files are byte-identical to `d01d6aa`.
2. **R3-O1 construction.**
   - Mathematical validity by exact integer or rational reasoning: representability of μ; exact values; inexactness; the no-tie claim; band membership of both the exact and the rounded product; exactness of the later products; normality of k.
   - That production raises for the stated reason and not through another check.
   - The same validity for the companion.
3. **The targeted mutant is killed for the intended reason.**
   - Re-run the harness, or apply the mutant yourself, and inspect the failure.
   - Check that the mutant is narrowly the reviewer's defect.
   - Check that the new test is not satisfiable by an unrelated rejection.
   - Try at least one alternative wrong implementation in the band, of your own, and report whether the tests catch it.
4. **No unintended production behavior or scope changes:**
   - `src/` and the protected paths;
   - test-only scope (I-21 §5): no new tolerance, no constant, API or domain change;
   - existing exact-zero and legitimate-subnormal tests are unchanged and pass.
5. **No unresolved new findings that block acceptance.** Check every number quoted in the new record sections. Check append-only status with `git diff d01d6aa..e404b0f40a3a46c0a71041636e0f87eb5fa247f3 -- docs`.

## Required output
1. **Ledger:** environment; commands run, with key output; files inspected. For each conclusion, say whether it rests on your own execution or computation, or only on documentation.
2. **Closure table:** M3T1-R3-F1, R3-F2 and R3-O1, each marked exactly one of CLOSED, PARTIALLY CLOSED or NOT CLOSED, with evidence.
3. **Assessment of items 1–5**, each separately.
4. **New findings,** numbered `M3T1-C1-F1`, …. Each gives:
   - severity: BLOCKER, MAJOR, MINOR or NOTE;
   - file and line references;
   - a reproduction;
   - the consequence;
   - the recommended correction;
   - whether it is a defect, an enhancement or an unresolved decision;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Verification limits.**
6. **Final verdict:** exactly one line, either `VERDICT: CLOSURE VERIFIED` or `VERDICT: CLOSURE NOT VERIFIED`. Any BLOCKER, MAJOR or MINOR finding, or any item not CLOSED, requires CLOSURE NOT VERIFIED. NOTEs alone permit CLOSURE VERIFIED.
7. **Files:** write the complete report, identical to your final message, to `review_scratch/M3-T1-codex-closure.md`. Save scripts and logs under `review_scratch/`, with a command ledger in `review_scratch/COMMANDS.md`.

## Tech Lead's authorization I-21 (this verification), verbatim

# Authorization I-21 — M3 T1 Review 03 Closure

**Decision: APPROVED — limited closure pass only.**

Review 03 returned unconditional PASS. I authorize the following narrowly scoped work on `milestone-3-t1-j2-force-model`.

T1 remains **IMPLEMENTED — REVIEW PASSED — NOT ACCEPTED — NOT MERGED** until I explicitly decide otherwise.

## 1. Preconditions

Before making changes:

1. Fetch and verify that local HEAD and origin both equal `d01d6aaf008dc63b8b509fa1b0855bbac626a718`.
2. Verify the working tree is clean.
3. Verify the reviewed production-code head remains `4b85ded298e521f5c72b606cd012dec8b56e9c5e`.
4. Verify `main` remains at the reported baseline `60648b9`, or stop and report any discrepancy.
5. Verify the existing Review 03 record, acceptance dossier, and evidence are present.

Stop on any unexpected discrepancy. Do not reset, rebase, force-push, or modify another worktree.

## 2. R3-F1 — Correct VAL-0020 wording

Disposition: **ACCEPTED.**

Correct the statement that the relevant fallback is "never reached" at realistic states.

Distinguish exact-zero products from non-zero products. Document the canonical exact-zero example and preserve the verified behavior.

This is a documentation correction only.

Do not change the numerical implementation.

## 3. R3-F2 — Correct reproduction evidence interpretation

Disposition: **ACCEPTED.**

Append a clarification explaining that the `mu_alias_set_-1` row records μ after the later mutation, rather than the value at the instant the earlier acceleration was computed.

Preserve all original raw reproduction files and historical records.

Do not silently rewrite prior observations.

## 4. R3-O1 — Close the boundary coverage gap

Disposition: **ACCEPTED.**

Add a deterministic regression test for an inexact coefficient-chain product strictly between `MIN_NORMAL/2` and `MIN_NORMAL`.

Requirements:

- Derive and document the input construction.
- Demonstrate that the intended intermediate product lies inside the specified interval.
- Demonstrate that the product is inexact under the relevant binary64 operation.
- Verify the current production implementation's expected behavior.
- Add one narrowly targeted mutation that violates that behavior.
- Demonstrate that the new regression test kills the mutant.
- Preserve existing exact-zero and legitimate subnormal behavior.

Avoid relying on rounded decimal approximations when exact binary64 constructions or integer-ratio reasoning are available.

If a valid deterministic construction cannot be established, stop and report the obstacle rather than weakening the test.

## 5. Coefficient-chain scope ruling

I authorize **test-only coverage of the existing R2-F1 coefficient-chain contract**.

This authorization does not permit:

- Changing production numerical behavior.
- Extending the supported input domain.
- Introducing new acceptance tolerances.
- Altering pinned constants.
- Modifying the M1/M2 compatibility contract.
- Changing the force-model API.

If the new test reveals a genuine production defect, record and reproduce it, then stop for my decision.

Do not fix it under this authorization.

## 6. Validation

After completing the permitted changes:

1. Run the targeted J2 regression suite.
2. Run the complete pytest suite.
3. Run the T0 checks.
4. Run the M1 and M2 Proof validations.
5. Verify the pinned golden digest.
6. Run Ruff.
7. Verify that production and other protected paths remain unchanged.
8. Run the targeted mutation and record its detection.
9. Confirm that the original Review 03 PASS evidence remains historically intact.

Preserve existing test counts and results as historical evidence; report fresh counts separately.

Wait for CI on the final closure commit. Require all four jobs to succeed. If an infrastructure-only failure occurs, document the failure and any rerun without rewriting the original result.

## 7. Independent verification

Perform a focused independent Codex verification of the I-21 closure changes.

The verification must confirm:

- R3-F1 and R3-F2 documentation corrections are accurate.
- R3-O1's boundary construction is mathematically valid.
- The targeted mutant is killed for the intended reason.
- No unintended production behavior or scope changes occurred.
- No unresolved new findings block acceptance.

This is a focused closure verification, not an automatic full Review 04.

If verification identifies a new defect, record and reproduce it, then stop. Do not initiate another correction/review cycle without authorization.

## 8. Acceptance dossier

Append the closure evidence to the existing T1 acceptance dossier.

Preserve the original Review 03 verdict and raw evidence.

Include:

- Exact branch and HEAD.
- Commit history for this authorization.
- Finding-by-finding dispositions.
- Boundary construction and mutant results.
- Fresh validation and CI results.
- Independent closure-verification verdict.
- Remaining limitations, including the previously accepted exploratory mutation survivors.
- Confirmation of production-code immutability.
- Explicit acceptance and merge eligibility assessment.

Do not describe the surviving exploratory mutants as resolved or claim complete mutation coverage.

## 9. Stop conditions

Stop immediately if:

- Production changes are required.
- A new numerical defect is discovered.
- The new boundary test cannot be justified.
- A protected-path change is needed.
- Independent verification returns a blocking finding.
- Required validation fails for a substantive reason.

Otherwise, stop after successful closure verification and dossier completion.

**Do not accept T1. Do not merge T1. Do not start T2 or T3. Do not make additional DR decisions.**

Return a final checkpoint report and wait for my explicit acceptance decision.

All authorized pushes must be ordinary fast-forward pushes. No force-pushes.

**Workspace instruction:** Continue using the existing T1 Superset workspace for this closure pass.
