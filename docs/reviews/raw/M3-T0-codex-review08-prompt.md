You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 08** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 07. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`95fff220ea164f2d837005a68f881fbded7c624c`** (full SHA), with git metadata.
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
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6,7}.py` (about 3 min).
  - `mutation_check_review02.py` (about 50 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a justified subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify: DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the Review 06 amendment (I-10), and the Review 07 record's correction and validation sections. Re-derive, re-execute, write independent checks and attempt counterexamples, in particular outside the implementer's sweeps.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass:** `489d4e7`, `44260ef` (reviewed by Review 04); `c15fbd4` (the Review 04 record).
- **Review 04 correction pass:** `a1feb79`, `88f9752` (reviewed by Review 05); `17b2229` (the Review 05 record).
- **Review 05 correction pass:** `411cabd`, `fcd5997` (reviewed by Review 06); `30a4e8d` (the Review 06 record).
- **Review 06 correction pass:** `9e44850`, `0357196` (reviewed by Review 07); `72f9e001a2e1480e477d1801e0a6e938f4ce1087` (the Review 07 record).
- **Review 07 correction pass (under review now):**
  - `9afbbbf9bd274930cff9c5b777420062ed9c3d42`: the documentation correction for M3T0-R7-F1 and R7-F2, with `check_review07.py`, the extended mutation harness and the records;
  - `95fff220ea164f2d837005a68f881fbded7c624c`: the validation record of `9afbbbf` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 72f9e00..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–07:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria) and Authorizations I-4 to I-9. Authorization I-10, which covers both the correction pass under review and this review, is reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7}-evidence/` (Review 07's includes its `test_noncert_contract.py.txt` and `extra_boundaries.py.txt`);
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,2,3,4,5,6,7}.md`. The Review 07 record ends with this pass's correction section (dispositions, the stated semantics of both non-certification paths, the R7-F2 qualification, two implementer observations, evidence, unresolved assumptions) and its validation section.
- **Implementer correction evidence:** `docs/reviews/raw/M3-T0-review07-findings-correction-evidence/` (red-before and green-after logs, the mutation run, the R7 smoke run, a seeded adversarial probe script and log, the docstring-free AST comparison, the docstring diff, the termination-results regeneration, the reviewer's contract test rerun, the precondition digests, `SHA256SUMS`; the Proof/pytest/reproducibility logs are added by the validation commit). Earlier passes: `docs/reviews/raw/M3-T0-review0{2,3,4,5}-correction-evidence/`, `docs/reviews/raw/M3-T0-review0{5,6}-findings-correction-evidence/`.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; seven correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Experiment code:** `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_oracle.py`, `t0_termination.py`, `check_review01.py` … `check_review07.py`, `mutation_check_review02.py`, the README and the committed result files).

## Findings so far, with their current dispositions
- **Review 01:** M3T0-F1 (MAJOR): the missed-crossing bound; F2 (MAJOR): P1 sufficiency, thresholds and the speed proxy; F3 (MINOR): stage numbering; F4 (MINOR): a misquoted residual; F5 (NOTE): the dependency map against the owner gate.
- **Review 02:** R2-F1 (MINOR): sampled maxima presented as bounds; R2-F2 (MINOR): the co-rotation term evaluated at the lower height bound; R2-F3 (NOTE): checks that passed with zeroed evidence; IM-1: the P6 "0.99 m" figure without a procedure.
- **Review 03:** R3-F1 (MINOR): the numerical height error at density discontinuities.
- **Review 04:** R4-F1 (MINOR): the floating-point drag enclosure drops underflow errors.
- **Implementer item IM-2 (NOTE, from the Review 04 pass):** the drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The record is clarified and no floor is changed; the Tech Lead ordered the existing disposition kept.
- **Review 05:** R5-F1 (MINOR): the b ↔ mass conversion kept a relative-only factor (subnormal b: drag 1.94 and 1.10 times the envelope); R5-F2 (MINOR): 0.983 quoted for the wrong population.
- **Review 06:** R6-F1 (MINOR): b = 0 under C1 divided by zero; R6-F2 (NOTE): `_up`/`_dn` at infinite and out-of-range values; R6-F3 (NOTE): E4b's cap inherits A-FP-2. Remarks: the 5 287-point random search unreproduced and unmarked; b* for the stored versus the exact φ_B.
- **Review 07 (verdict REQUEST_CHANGES), the current dispositions:**
  - RESOLVED: R6-F1, R6-F3, both Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5;
  - PARTIALLY RESOLVED: **R6-F2** — the helpers are fixed and no false certification was found, but the universal "need = +∞" statement is untrue (R7-F1);
  - **R7-F1 (NOTE):** when M2 ≤ 0, `stage_lower_heights` returns before M4 and `stage_need` returns −M2, finite (h0 = 1 m, b = 2^-1074: A0 = +∞, need = 55 992.318990613036 m); the docstring (and records) said need = +∞ for any infinite envelope;
  - **R7-F2 (NOTE):** two summaries kept "b_R ≤ b" without b > 0 (`t0_termination.py:612`, `:963` at `72f9e00`); at b = 0, b_R = φ_B/R(0) = 1.497e-325 > 0.
- **Outstanding discrepancy:** the GMAT geodetic-drag configuration sensitivity remains ESCALATED (DR-0029 Q-G2-1 / P6); it is not to be closed by this review. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided.

## The implementer's claims for this pass (to verify, not to trust)
- **Documentation only.** No executable statement changed: the docstring-free AST of `t0_termination.py` equals `72f9e00`; `t0_termination_results.json` regenerates byte for byte; no floor, bracket, margin, threshold or published value changed. The code was deliberately **not** normalised to need = +∞ (I-10 §2 forbids changing numerical behaviour).
- **R7-F1 (the stated contract):** a step is certified only when need < 0; every need ≥ 0 is a non-certification. Path 1, M2 ≤ 0: need = −M2, finite and ≥ 0; M2 depends on h0 and the constants only (not on b or the envelope), and with the published constants M2 ≤ 0 up to h0 = 55 749.393 m (55 749.39300208564 the largest such binary64). Path 2, M2 > 0: need = −min(M2, M3, M4); an envelope of +∞ at A0 or A2, or a stage value outside the binary64 range, gives need = +∞; otherwise need is finite. b = +∞ (drag-free) has a finite need on both paths. A non-finite h0, or b NaN or < 0, raises ValueError on both paths.
- **R7-F2:** b_R ≤ b for b > 0 (b_R = b where the conversion is normal); at b = 0, b_R = φ_B/R(0) > 0. Qualified in the E4 summary and the `drag_envelope` docstring.
- **Records:** VAL-0019 and DR-0029 bodies corrected inline; Review 07 correction logs added; the Review 06 log entries kept as written and qualified; an amendment appended to the Review 06 record; report and decision-matrix notes appended.
- **Implementer observations, not corrected (outside I-10's scope):** (1) `check_review05.py:9` still describes the Review 05 pass as "the envelope uses b_R = phi_B / R <= b" (a check file's historical summary); (2) a computed h0 ≤ β = 8.877691069434738e-09 m raises ValueError from the envelope, and an h0 with b_lower + H0 ≤ 0 (for example −6.4e6 m) raises `decimal.InvalidOperation` from the square root in V; neither certifies, and the docstring claims nothing for them. Judge each yourself.
- **Checks:** `check_review07.py`, 23 checks; red before at `72f9e00` 3 fail (the docstring and record checks) and 20 pass (contract checks, which pin the unchanged behaviour); green after 261/261. The reviewer's Review 07 `test_noncert_contract.py` still fails on the corrected tree (it asserts the superseded claim). Mutation: control 261/261; 73/73 non-equivalent mutants detected, 2 declared equivalent; 14 new R7 mutants (one survivor in a first smoke run was closed by a stronger record check).
- **Implementer-only evidence:** seeded adversarial probe (`adversarial_r7.py.txt`, seed 20261021): 4 000 (h0, b) stage cases (1 391 on path 1, 727 of them with A0 = +∞; 2 609 on path 2, 1 212 with an infinite envelope; 1 014 certified), M2 compared across vehicles at 300 heights, and 18 969 random b_R cases.
- **Committed implementer evidence you can re-run:** `adversarial_r7.py.txt` and `ast_equal.py.txt` (`python -I <file> ...`), `smoke_r7.py.txt`, `digests.py.txt`, the mutation JSON and the red-before log.
- **Validation claims you cannot fully see:** M1 Proof and M2 Proof in fresh clones at `9afbbbf`; full pytest; pinned digests; the T0 experiments byte-identical over two runs including GMAT; CI runs 39537301986 (`9afbbbf`) and 39543277180 (`95fff22`). You cannot access CI; state that. CI does not collect the T0 checks (`testpaths = ["tests"]`).

## Tech Lead's authorization (I-10), verbatim
Authorization I-10 — M3 T0 Review 07 Corrections and Independent Review 08

You are authorized to correct only M3T0-R7-F1 and M3T0-R7-F2 and then conduct independent Codex Review 08.

Baseline: milestone-3-t0-reference-spike at 72f9e001a2e1480e477d1801e0a6e938f4ce1087.

1. Preconditions
Fetch and verify HEAD equals origin, the worktree is clean, Review 07 evidence is committed, CI is green, and all pinned digests match. Stop on any mismatch. Preserve fast-forward-only pushes and branch protection.

2. Correct R7-F1
Fix the stage_lower_heights docstring so it accurately describes the finite positive need returned when M2 <= 0. Explicitly distinguish finite positive need from +infinity cases, including overflow and infinite inputs, according to the actual validated implementation. Do not change numerical behavior or broaden the contract.

3. Correct R7-F2
Qualify both stale b_R <= b statements with b > 0. Preserve the documented b=0 boundary behavior. Do not change the implementation.

4. Regression evidence
Add focused executable checks for both documentation claims, including the reported counterexamples. Demonstrate red-before/green-after behavior for contract assertions and mutation sensitivity. Do not misrepresent a documentation-only change as a numerical algorithm fix.

5. Validation
Run all applicable Review 01–07 checks, new checks and mutants, pytest, ruff, M1/M2 Proof, pinned-digest verification, and reproducibility checks. Report exact counts and any failures. CI passing alone is not sufficient because CI does not collect all T0 checks. Preserve assumptions A-FP-1/2/3 and their limitations.

6. Independent Review 08
Only after corrections and validation pass, use a fresh independent Codex session against the committed candidate. Provide all prior findings and dispositions, executable evidence, precise scope and assumptions. Require individual reassessment of R7-F1, R7-F2, all earlier findings, remarks, and outstanding discrepancies. Require adversarial attempts to falsify soundness, not merely a sweep. Record the complete unedited reviewer output and evidence.

7. Stop conditions
If any validation fails, a finding is not resolved, or Codex returns REQUEST_CHANGES, record and reproduce findings without correcting new ones. Do not start Review 09. Stop for authorization.

If Review 08 returns PASS with no unresolved findings, prepare a T0 acceptance dossier and stop for my explicit review. Do not declare acceptance.

8. Prohibitions
Do not merge, start T1/T2, decide DR-0029 P1–P10 or DR-0028 P6(b), change protected baselines, weaken thresholds, silently change numerical semantics, or close the GMAT geodetic-drag escalation.

9. Final checkpoint
Report branch/HEAD/origin, commit history, tree state, exact diffs, red/green and mutation evidence, test counts, proof results, CI runs, digest checks, reviewer verdict and finding-by-finding dispositions, remaining assumptions, blockers, and precise next authorization needed.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical argument**: for every bound or semantic claim, give or check the proof against the code, and use sweeps only to seek counterexamples. **Actively try to falsify soundness**: construct inputs designed to produce a false certification (need < 0 for a step whose stages can leave the domain, or an envelope below the model's computed drag), not only random samples.
1. **R7-F1 — the non-certification contract.** Read `stage_lower_heights`, `stage_need` and every consumer (the floor bisection in `sufficient_stage_condition`, `floor_comparison`, `libm_sensitivity`, `stage_stress`, the result writers). Verify from the code, not the docstring:
   - that certification means need < 0 for every consumer, and that need ≥ 0 (including −0.0, finite positive and +∞) is never treated as certified;
   - that M2 is independent of b and the envelope, the early-return edge (55 749.393 m; 55 749.39300208564 the largest binary64 with M2 ≤ 0), and that on path 1 need = −M2 is finite and ≥ 0 for every b, including A0 = +∞;
   - that on path 2 an infinite envelope at A0 or A2, or a value beyond the binary64 range, gives need = +∞, and whether any other path yields a finite need from an unbounded enclosure in a way the docstring misstates;
   - the drag-free vehicle, NaN, negative, ±0, subnormal and huge b, non-finite and boundary h0 (including the implementer's observation on h0 ≤ β and very negative h0);
   - that the docstring, VAL-0019, DR-0029, the Review 06 amendment and the README now state exactly the implemented behaviour, neither broader nor narrower;
   - that no numerical behaviour changed (`git diff 72f9e00..9afbbbf -- docs/science/experiments/m3-t0/t0_termination.py`; your own AST or execution comparison).
2. **R7-F2 — b_R ≤ b.** Verify that every statement of b_R ≤ b in the code and records is qualified with b > 0 or states the b = 0 case, that b_R > 0 at b = 0 and b_R ≤ b for b > 0 (rounded down), and judge the implementer's observation on `check_review05.py:9`.
3. **R6-F2, and every earlier finding, individually.** Reassess R6-F2 (helpers and non-certification) on its own merits, and each of R6-F1, R6-F3, the two Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5 individually (not by implication from another finding), at least to the extent the new commits could affect them. Re-run the key counterexamples of each.
4. **Soundness, adversarially.** Try to break the E4a bound (C1 and C2, b = 0 and subnormal boundaries, huge and subnormal cd·area), the drag envelope (subnormal densities, band bases, the top band, speed extremes), E4b (cd·area ≤ η₀, LIBM_ULP near 91910196476947) and the stage condition (stage heights near the lower edge, near the early-return edge, overflow). Write your own probes and new mutants of the R7 contract.
5. **Records and provenance.** Verify that the historical review records were amended append-only (`git diff 72f9e00..HEAD -- docs/reviews`), that the superseded wording is preserved at `72f9e00`, that the 5 287-point search stays UNREPRODUCED, that IM-2 keeps its disposition, and that the GMAT geodetic-drag discrepancy remains escalated.
6. **Assumptions and scope.** Check A-FP-1, A-FP-2 and A-FP-3, the C1/C2-only contract scope and the overflow exclusion wherever the guarantee is quoted. Host measurements must not be presented as a platform guarantee.
7. **Validation and integrity.**
   - Run: the Review 01–07 checks; the mutation harness or a justified subset, with your own new mutants; your own adversarial probes; the T0 experiments' reproducibility byte for byte, including the GMAT harness where practical; pytest and the M1/M2 validators and GMAT compares, with output into `review_scratch/`.
   - Verify: the five pinned digests and the VAL-0019 spike digests; that no protected path changed (`git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`); that the published floors, root brackets, margins, physics constants, vehicle definitions, contracts, baselines and goldens are unchanged (your own diff of the result files against `72f9e00`).
   - Check every number quoted in the I-10 records against the code, the result files and your own computation. Look for checks whose expected values come from the implementation, and for corruptions of the corrected text or contract that still pass.
8. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R7-F1, R7-F2, R6-F1, R6-F2, R6-F3, the two Review 06 remarks (provenance of the 5 287-point search; b* and φ_B), M3T0-R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and M3T0-F1 … F5. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence and your reasoning for each separately. State separately the status of the escalated GMAT geodetic-drag discrepancy (it is to remain escalated, not resolved here).
3. **Assumptions and scope:** for A-FP-1, A-FP-2, A-FP-3, the C1/C2 scope and the overflow exclusion, state whether each is stated honestly and completely, and what exactly is guaranteed unconditionally versus conditionally.
4. **New findings.** Number them `M3T0-R8-F1`, `M3T0-R8-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Adversarial attempts:** what you tried in order to falsify soundness, and the outcome of each.
6. **Verification limits:** what you could not check.
7. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
8. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review08.md`, and save your own scripts and logs under `review_scratch/`.
