You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 10** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 09. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct. You are not limited to the findings listed below.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`3c565e62e8257040b48bdd1d0d74fffc370d56d2`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). The implementer states that it is byte-identical to the implementer's installation (console sha256 `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`, atmosphere table `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`). Check this yourself. Pass the console as an absolute path, because the harness changes directory.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files. That is allowed. Afterwards:
    - record `git status --porcelain` and `git diff --stat`;
    - restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed;
    - report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run:
    - `pytest`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6,7,8,9}.py` (about 3 min).
  - `mutation_check_review02.py` (about 55 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a justified subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify:
  - `check_review08.py` and the new `check_review09.py`;
  - the `stage_lower_heights` docstring;
  - VAL-0019, DR-0029, the T0 report, the decision matrix and the experiment README;
  - the appended amendments to the Review 07 and Review 08 records;
  - the Review 09 record's correction and validation sections;
  - the acceptance dossier prepared after Review 09.

  Re-derive, re-execute, write independent checks and attempt counterexamples, in particular outside the implementer's sweeps.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Correction passes and records:**

  | Pass | Commits | Reviewed by | Record |
  |---|---|---|---|
  | Review 01 correction | `03e8f63`, `ead2a84` | Review 02 | `5548d11` |
  | Review 02 correction | `14d98f0`, `51e110b` | Review 03 | `c6c0fff` |
  | Review 03 correction | `489d4e7`, `44260ef` | Review 04 | `c15fbd4` |
  | Review 04 correction | `a1feb79`, `88f9752` | Review 05 | `17b2229` |
  | Review 05 correction | `411cabd`, `fcd5997` | Review 06 | `30a4e8d` |
  | Review 06 correction | `9e44850`, `0357196` | Review 07 | `72f9e00` |
  | Review 07 correction | `9afbbbf`, `95fff22` | Review 08 | `115e747` |
  | Review 08 correction | `0254664`, `f04f995` | Review 09 | `5978bfedcdfc67b8dc920176c7eaa63057e61fd9` (the Review 09 record and the acceptance dossier) |
- **Review 09 correction pass (under review now):**
  - `cc82ae7107b22a9c033bb7d03316f4e5655724b5`: the corrections for M3T0-R9-F1 (checks) and R9-F2 (check and documentation), with `check_review09.py`, the extended mutation harness and the records;
  - `3c565e62e8257040b48bdd1d0d74fffc370d56d2`: the validation record of `cc82ae7` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 5978bfe..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–09:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,…,9}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,…,9}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria) and Authorizations I-4 to I-11. Authorization I-12, which covers both the correction pass under review and this review, is reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{1,…,9}-evidence/` (Review 09's includes the implementer's reproduction in `implementer-reproduction/`);
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,…,9}.md`. The Review 09 record ends with this pass's correction section and its validation section;
  - the acceptance dossier prepared after Review 09: `docs/reviews/M3-T0-acceptance-dossier.md`. It predates this pass and is not yet updated.
- **Implementer correction evidence:** `docs/reviews/raw/M3-T0-review09-findings-correction-evidence/`. It holds:
  - the red-before logs, including the reviewer's mutant against the new checks, and the green-after log;
  - the mutation run and the R9 smoke run;
  - the docstring-free AST comparison, the docstring diff and the termination-results regeneration;
  - the default-envelope M4 sweep;
  - the precondition digests and `SHA256SUMS`.

  The Proof, pytest, reproducibility and digest logs are added by the validation commit. Earlier passes: `docs/reviews/raw/M3-T0-review0{2,3,4,5}-correction-evidence/`, `docs/reviews/raw/M3-T0-review0{5,6,7,8}-findings-correction-evidence/`.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Experiment code:** `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_oracle.py`, `t0_termination.py`, `check_review01.py` … `check_review09.py`, `mutation_check_review02.py`, the README and the committed result files).

## Findings so far, with their current dispositions
- **Review 01:**
  - M3T0-F1 (MAJOR): the missed-crossing bound;
  - F2 (MAJOR): P1 sufficiency, thresholds and the speed proxy;
  - F3 (MINOR): stage numbering;
  - F4 (MINOR): a misquoted residual;
  - F5 (NOTE): the dependency map against the owner gate.
- **Review 02:**
  - R2-F1 (MINOR): sampled maxima presented as bounds;
  - R2-F2 (MINOR): the co-rotation term evaluated at the lower height bound;
  - R2-F3 (NOTE): checks that passed with zeroed evidence;
  - IM-1: the P6 "0.99 m" figure without a procedure.
- **Review 03:** R3-F1 (MINOR): the numerical height error at density discontinuities.
- **Review 04:** R4-F1 (MINOR): the floating-point drag enclosure drops underflow errors.
- **Implementer item IM-2 (NOTE, from the Review 04 pass):** the drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The record is clarified and no floor is changed; the Tech Lead ordered the existing disposition kept.
- **Review 05:**
  - R5-F1 (MINOR): the b ↔ mass conversion kept a relative-only factor;
  - R5-F2 (MINOR): 0.983 quoted for the wrong population.
- **Review 06:**
  - R6-F1 (MINOR): b = 0 under C1 divided by zero;
  - R6-F2 (NOTE): `_up`/`_dn` at infinite and out-of-range values;
  - R6-F3 (NOTE): E4b's cap inherits A-FP-2;
  - remarks: the 5 287-point random search unreproduced and unmarked; b* for the stored versus the exact φ_B.
- **Review 07:**
  - R7-F1 (NOTE): finite need on the M2 ≤ 0 path, documented as +∞;
  - R7-F2 (NOTE): "b_R ≤ b" without b > 0.
- **Review 08:**
  - R8-F1 (NOTE): a computed h0 ≤ β, attainable by exterior states, raises `ValueError`, while the records excluded it;
  - reviewer observation: an M3-dropped mutant passed all checks.
- **Review 09 (verdict PASS, unconditional)** found every item above RESOLVED and raised two NOTEs, both ACCEPTED:
  - **M3T0-R9-F1 (NOTE):** a mutant of `stage_need` that drops M3 from the minimum only when M3 is finite passed all 288 checks. With an injected envelope of 10^8 at the first call and 0 after it, at h0 = 200 km and B_V1, the code returns need = +2 499 855 380.144757 and the mutant −89 239.71048326683, a false certification. The Review 08 finite control always had M4 < M3;
  - **M3T0-R9-F2 (NOTE):** the pole check of `check_review08.py` took A·(1 − F) as the exact polar radius, while the model's height and the oracle use A·√(1 − E2). These differ by 2.4767e-13 m, so the quoted mathematical height of [0, 0, fl(b)], −2.03e-10 m, is −2.04e-10 m on the model's ellipsoid.
- **Outstanding discrepancy:** the GMAT geodetic-drag configuration sensitivity remains ESCALATED (DR-0029 Q-G2-1 / P6); it is not to be closed by this review. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided.

## The implementer's claims for this pass (to verify, not to trust)
- **Checks and documentation only.** No executable statement of `t0_model.py`, `t0_oracle.py` or `t0_termination.py` changed: the docstring-free AST of `t0_termination.py` equals `5978bfe`, the model and oracle are byte-identical, and `t0_termination_results.json` regenerates byte for byte. No floor, bracket, margin, threshold, constant or published value changed. No defect in the numerical implementation was found.
- **R9-F1:** `check_review09.py` calls the production `stage_lower_heights` and `stage_need`, with only the force bound injected through their `envelope` argument.
  - It asserts need = −M3 wherever a finite M3 is the strict minimum: the Review 09 counterexample, plus 14 cases at 200 km, 1 000 km and 10 000 km with first-call envelopes 10^4 … 10^8, of both signs of M3.
  - It distinguishes the three outcomes +∞, finite ≥ 0 and certification.
  - With the default envelope M4 < M3 < M2 at the pinned heights and in a sampled sweep (8 835 path-2 cases, all three vehicles), and the published results regenerate byte for byte with M3 dropped. So no published value is decided by M3.
  - Three R9-F1 mutants are in the harness: the reviewer's finite-only mutant, a positive-only mutant, and a narrowed case grid.
- **R9-F2:**
  - **The model's ellipsoid.** At the pole, `geodetic_iterative` returns z − fl(a·√(1 − e2)), and fl(a·√(1 − e2)) = fl(b). The model's ellipsoid is therefore (binary64 a, e2), with polar radius a·√(1 − e2), as in `t0_oracle`.
  - **The check.** The pole reference of `check_review08.py` is now b² = a²(1 − e2) (exact), with heights to 80 digits. fl(b) − b ∈ (−2.03737e-10, −2.03736e-10) m.
  - **The quotation.** It is corrected to −2.04e-10 m in the `stage_lower_heights` docstring and the pole-check docstring, and amended (appended) in the Review 07 and Review 08 records and VAL-0019.
  - **The consistency regression.** It ties the reference to the model's computed polar radius and to the oracle. Ten R9-F2 and record mutants are in the harness (13 R9 mutants in all).
- **Checks:** `check_review09.py` has 26 checks. Red before at `5978bfe`: 3 fail (the pole reference, the docstrings and the records) and 23 pass. Under the reviewer's mutant, its 16 R9-F1 checks fail. Green after: 314/314.
- **Mutation:** the implementer reports control 314/314; 100/100 non-equivalent mutants detected, each by a declared check (87 earlier + 13 R9); 2 declared equivalent (`r6f2_float_nan_accepted`, `script_two_body_without_stationary_points`); no survivors (`mutation_check_review09.json`).
- **Validation claims you cannot fully see:** M1 Proof and M2 Proof in fresh clones at `cc82ae7`; full pytest; pinned and spike digests; the T0 experiments byte-identical over two runs including GMAT; CI runs 39695797213 (`cc82ae7`) and 39701788045 (`3c565e6`). You cannot access CI; state that. CI does not collect the T0 checks (`testpaths = ["tests"]`).

## Tech Lead's authorization (I-12), verbatim
# Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10

## 1. Authorization

Authorize correction of M3T0-R9-F1 and M3T0-R9-F2, full revalidation, and one independent Codex Review 10.

T0 remains NOT ACCEPTED and BLOCKED pending my next decision.

Expected repository state:
- Branch: `milestone-3-t0-reference-spike`
- HEAD and origin: `5978bfedcdfc67b8dc920176c7eaa63057e61fd9`
- Worktree: clean
- Main ancestor: `86df2c3`
- Review 09: unconditional PASS, with two accepted NOTEs

Verify all preconditions before changing anything. Stop on discrepancies.

## 2. R9-F1 — Close the M3 finite-only verification gap

Reproduce the Review 09 mutant that includes the M3 stage minimum only when M3 is finite.

Add a deterministic regression that:

1. Uses the reviewer's exact counterexample.
2. Passes with the committed implementation.
3. Fails with the finite-only M3 mutant.
4. Demonstrates the incorrect negative `need` produced by the mutant.
5. Verifies that the committed implementation does not incorrectly certify the step.
6. Distinguishes positive infinity, finite positive values, and negative certification results.

Ensure the test exercises the actual production-equivalent calculation rather than merely testing a copied formula.

Add the mutant to the tracked mutation harness, and demonstrate red-before/green-after evidence for the coverage correction.

Do not modify the numerical implementation unless an independently verified defect makes that necessary. If one is found, stop for authorization.

## 3. R9-F2 — Correct polar-radius reference evidence

Identify the exact polar-radius expression used by the committed model.

Recompute the Review 09 pole example using that expression, preserving sufficient precision to distinguish the approximately 2.48e-13 m difference between the two ellipsoid definitions.

Correct the reported discrepancy and associated explanation.

Preserve the original evidence and append a traceable amendment.

Add a regression checking consistency between the reference calculation and the model's ellipsoid definition.

Do not modify the model's constants or ellipsoid implementation.

## 4. Preserve evidence and scope

All corrections must be narrowly scoped.

Preserve:
- Original Review 09 PASS verdict.
- Original reviewer findings and raw output.
- Existing validation evidence.
- Historical review records.
- Existing scientific limitations.
- Existing DR statuses.

Document amendments rather than silently rewriting historical findings.

Do not alter protected paths, numerical thresholds, floors, physics constants, or reference configurations.

## 5. Full revalidation

Perform:

1. Red-before/green-after regression demonstrations.
2. All T0 checks.
3. Complete mutation harness, with all non-equivalent mutants detected.
4. Full pytest suite.
5. Fresh-clone M1 Proof.
6. Fresh-clone M2 Proof.
7. Five pinned digest checks and all currently tracked spike digest checks.
8. Two reproducibility runs of all tracked T0 experiments, including GMAT.
9. Numerical-output comparison against the I-11 baseline.
10. Four-job CI verification.

Report exact counts, failures, equivalent mutants, and any changes from the previous baseline.

Do not represent green CI as evidence that T0-specific checks ran in CI unless they actually did.

## 6. Independent Codex Review 10

After successful correction and validation, start a fresh independent Codex session.

Require the reviewer to:

- Verify R9-F1 is resolved.
- Verify R9-F2 is resolved.
- Confirm the finite-only M3 mutant is detected.
- Independently inspect the polar-radius calculation.
- Check earlier findings for regressions.
- Search for additional numerical, scientific, documentation, and verification defects.
- Return an explicit PASS or REQUEST_CHANGES verdict.

Do not constrain the reviewer to the two known findings.

## 7. Stop conditions

If Review 10 returns REQUEST_CHANGES:

- Record and independently reproduce new findings.
- Do not correct them.
- Do not start Review 11.
- Do not prepare final acceptance.
- Stop for authorization.

If Review 10 returns PASS:

- Update the acceptance dossier.
- Report remaining limitations and open decisions.
- Stop for my explicit final T0 acceptance decision.

Under either outcome:

- Do not merge.
- Do not start T1 or T2.
- Do not decide DR-0029 P1–P10.
- Do not decide DR-0028 P6(b).
- Do not change branch protection.
- Do not begin a new milestone.

## 8. Final report

Provide the repository state, commits, changed files, finding dispositions, regression results, mutation results, complete validation matrix, Review 10 verdict, updated acceptance readiness, remaining scientific limitations, and exact next authorization required.

Use fast-forward pushes only. No force-pushes.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical argument**: for every bound or semantic claim, give or check the proof against the code, and use sweeps only to seek counterexamples. **Actively try to falsify soundness**: construct inputs designed to produce a false certification (need < 0 for a step whose stages can leave the domain, or an envelope below the model's computed drag), not only random samples. You are not limited to the two Review 09 findings.
1. **R9-F1, independently.**
   - Read `stage_lower_heights`, `stage_need` and every consumer.
   - Verify that `check_review09.py` exercises the production calculation, not a copied formula.
   - Check that the finite-only M3 mutant (`r9f1_m3_dropped_when_finite`) is detected, for the right reason, and that the regression distinguishes +∞, finite positive and negative (certification) outcomes.
   - Look for other corruptions of the stage minimum, of M2/M3/M4 or of the stage bounds that still pass every check, and write your own.
   - Judge the statement that no published value is decided by M3.
2. **R9-F2, independently.**
   - Identify for yourself the polar-radius expression the committed model uses, in its height function and in the oracle.
   - Recompute the pole example with enough precision to separate the two ellipsoid definitions (≈ 2.48e-13 m).
   - Check that `check_review08.py`'s reference and the new consistency regression agree with the model's ellipsoid, and that the corrected quotations and the appended amendments state it exactly.
   - Look for any other place in the code, checks or records that uses a different ellipsoid definition where the model's is meant.
3. **Every earlier finding, individually.** Check each of these for regressions individually, not by implication from another finding:
   - R8-F1, R7-F1, R7-F2;
   - R6-F1, R6-F2, R6-F3, and the two Review 06 remarks;
   - R5-F1, R5-F2, R4-F1, R3-F1;
   - R2-F1, R2-F2, R2-F3;
   - IM-1, IM-2, F1–F5;
   - the Review 08 M3 coverage observation.

   Check at least to the extent the new commits could affect them, and re-run the key counterexamples of each.
4. **Soundness, adversarially.** Try to break each bound and condition:
   - the E4a bound: C1 and C2; b = 0 and subnormal boundaries; huge and subnormal cd·area;
   - the drag envelope: subnormal densities, band bases, the top band, speed extremes;
   - E4b: cd·area ≤ η₀; LIBM_ULP near 91910196476947;
   - the stage condition: stage heights near and below the lower edge, near the early-return edge, overflow, and injected envelopes that make each of M2, M3 and M4 the minimum.

   Write your own probes and new mutants. Search for new numerical, scientific, floating-point, verification and documentation defects, and identify any certification claim not supported by the code and its stated premises.
5. **Records and provenance.**
   - Verify that the historical review records were amended append-only (`git diff 5978bfe..HEAD -- docs/reviews`), and that the superseded wording is preserved.
   - Verify that the Review 09 verdict and raw output are unchanged.
   - Verify that the 5 287-point search stays UNREPRODUCED, that IM-2 keeps its disposition, and that the GMAT geodetic-drag discrepancy remains escalated.
6. **Assumptions and scope.** Wherever the guarantee is quoted, check the following conditions:
   - A-FP-1, A-FP-2 and A-FP-3;
   - the C1/C2-only contract scope;
   - the no-overflow and negative two-body energy conditions;
   - the absence of a certified J2-plus-drag missed-crossing bound.

   Host measurements must not be presented as a platform guarantee.
7. **Validation and integrity.**
   - Run:
     - the Review 01–09 checks;
     - the mutation harness or a justified subset, with your own new mutants;
     - your own adversarial probes;
     - the T0 experiments' reproducibility byte for byte, including the GMAT harness where practical;
     - pytest, the M1/M2 validators and the GMAT compares, with output into `review_scratch/`.
   - Verify:
     - the five pinned digests and the VAL-0019 spike digests;
     - that no protected path changed (`git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`);
     - that the published floors, root brackets, margins, physics constants, vehicle definitions, contracts, baselines and goldens are unchanged (your own diff of the result files against `5978bfe`).
   - Check every number quoted in the I-12 records against the code, the result files and your own computation. Look for checks whose expected values come from the implementation.
8. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table.** Cover each of these items:
   - M3T0-R9-F1, R9-F2;
   - R8-F1, R7-F1, R7-F2;
   - R6-F1, R6-F2, R6-F3, and the two Review 06 remarks (provenance of the 5 287-point search; b* and φ_B);
   - M3T0-R5-F1, R5-F2, R4-F1, R3-F1;
   - R2-F1, R2-F2, R2-F3;
   - IM-1, IM-2, M3T0-F1 … F5;
   - the Review 08 M3 coverage observation.

   Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence and your reasoning for each separately. State separately the status of the escalated GMAT geodetic-drag discrepancy (it is to remain escalated, not resolved here).
3. **Assumptions and scope:** for A-FP-1, A-FP-2, A-FP-3, the C1/C2 scope, the overflow exclusion and the negative-energy condition, state whether each is stated honestly and completely, and what exactly is guaranteed unconditionally versus conditionally.
4. **New findings.** Number them `M3T0-R10-F1`, `M3T0-R10-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Adversarial attempts:** what you tried in order to falsify soundness, and the outcome of each.
6. **Verification limits:** what you could not check.
7. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
8. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review10.md`, and save your own scripts and logs under `review_scratch/`.
