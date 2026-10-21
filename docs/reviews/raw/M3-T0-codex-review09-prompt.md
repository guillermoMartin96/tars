You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 09** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 08. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`f04f9955d5ae714cc61144990395b8225a379968`** (full SHA), with git metadata.
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
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6,7,8}.py` (about 3 min).
  - `mutation_check_review02.py` (about 50 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a justified subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify: the `stage_lower_heights` docstring, DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the appended amendments to the Review 06 and Review 07 records, and the Review 08 record's correction and validation sections. Re-derive, re-execute, write independent checks and attempt counterexamples, in particular outside the implementer's sweeps.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass:** `489d4e7`, `44260ef` (reviewed by Review 04); `c15fbd4` (the Review 04 record).
- **Review 04 correction pass:** `a1feb79`, `88f9752` (reviewed by Review 05); `17b2229` (the Review 05 record).
- **Review 05 correction pass:** `411cabd`, `fcd5997` (reviewed by Review 06); `30a4e8d` (the Review 06 record).
- **Review 06 correction pass:** `9e44850`, `0357196` (reviewed by Review 07); `72f9e00` (the Review 07 record).
- **Review 07 correction pass:** `9afbbbf`, `95fff22` (reviewed by Review 08); `115e747960bfec12e3f83f6d7deb9638a55d6803` (the Review 08 record).
- **Review 08 correction pass (under review now):**
  - `0254664e300c84ae1d102bcf3f930a2dd2573428`: the documentation correction for M3T0-R8-F1 and the closure of the M3 coverage gap, with `check_review08.py`, the extended mutation harness and the records;
  - `f04f9955d5ae714cc61144990395b8225a379968`: the validation record of `0254664` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 115e747..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–08:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7,8}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7,8}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria) and Authorizations I-4 to I-10. Authorization I-11, which covers both the correction pass under review and this review, is reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6,7,8}-evidence/` (Review 08's includes the implementer's reproduction in `implementer-reproduction/`);
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,2,3,4,5,6,7,8}.md`. The Review 08 record ends with this pass's correction section and its validation section.
- **Implementer correction evidence:** `docs/reviews/raw/M3-T0-review08-findings-correction-evidence/` (red-before and green-after logs, the mutation run, the R8 smoke run, a seeded adversarial probe script and log, the docstring-free AST comparison, the docstring diff, the termination-results regeneration, the precondition digests, `SHA256SUMS`; the Proof/pytest/reproducibility/digest logs are added by the validation commit). Earlier passes: `docs/reviews/raw/M3-T0-review0{2,3,4,5}-correction-evidence/`, `docs/reviews/raw/M3-T0-review0{5,6,7}-findings-correction-evidence/`.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Experiment code:** `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_oracle.py`, `t0_termination.py`, `check_review01.py` … `check_review08.py`, `mutation_check_review02.py`, the README and the committed result files).

## Findings so far, with their current dispositions
- **Review 01:** M3T0-F1 (MAJOR): the missed-crossing bound; F2 (MAJOR): P1 sufficiency, thresholds and the speed proxy; F3 (MINOR): stage numbering; F4 (MINOR): a misquoted residual; F5 (NOTE): the dependency map against the owner gate.
- **Review 02:** R2-F1 (MINOR): sampled maxima presented as bounds; R2-F2 (MINOR): the co-rotation term evaluated at the lower height bound; R2-F3 (NOTE): checks that passed with zeroed evidence; IM-1: the P6 "0.99 m" figure without a procedure.
- **Review 03:** R3-F1 (MINOR): the numerical height error at density discontinuities.
- **Review 04:** R4-F1 (MINOR): the floating-point drag enclosure drops underflow errors.
- **Implementer item IM-2 (NOTE, from the Review 04 pass):** the drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The record is clarified and no floor is changed; the Tech Lead ordered the existing disposition kept.
- **Review 05:** R5-F1 (MINOR): the b ↔ mass conversion kept a relative-only factor; R5-F2 (MINOR): 0.983 quoted for the wrong population.
- **Review 06:** R6-F1 (MINOR): b = 0 under C1 divided by zero; R6-F2 (NOTE): `_up`/`_dn` at infinite and out-of-range values; R6-F3 (NOTE): E4b's cap inherits A-FP-2. Remarks: the 5 287-point random search unreproduced and unmarked; b* for the stored versus the exact φ_B.
- **Review 07:** R7-F1 (NOTE): when M2 ≤ 0 `stage_need` returns −M2, finite, although the docstring said need = +∞ for any infinite envelope; R7-F2 (NOTE): "b_R ≤ b" without b > 0.
- **Review 08 (verdict REQUEST_CHANGES), the current dispositions:**
  - RESOLVED: R7-F2, R6-F1, R6-F2, R6-F3, both Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5;
  - PARTIALLY RESOLVED: **R7-F1**, through R8-F1;
  - **M3T0-R8-F1 (NOTE):** the Review 07 correction record said a computed h0 ≤ β "is not the computed height of a state in the domain (outside the ellipsoid)". Strictly exterior bound states attain such heights (r = [nextafter(a, +∞), 0, 0], v = 0: height 2^-30 m), and for them `stage_need` raises `ValueError` for b = B_V1 and b = +∞ instead of returning the finite need stated for path 1 and the drag-free vehicle;
  - **Reviewer observation (not numbered):** a mutant dropping M3 from `stage_need`'s minimum (`-min(s["M2"], s["M4"])`) passed all 261 committed checks; with an injected envelope of +∞ at A0 only it yields a false certification.
- **Outstanding discrepancy:** the GMAT geodetic-drag configuration sensitivity remains ESCALATED (DR-0029 Q-G2-1 / P6); it is not to be closed by this review. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided.

## The implementer's claims for this pass (to verify, not to trust)
- **Documentation and checks only.** No executable statement changed: the docstring-free AST of `t0_termination.py` equals `115e747`; `t0_termination_results.json` regenerates byte for byte; no floor, bracket, margin, threshold, reference constant or published value changed.
- **R8-F1 (the stated precondition):** every value the stage condition returns needs a computed h0 > β = 8.877691069434738e-09 m; a computed h0 ≤ β raises `ValueError("the envelope is defined above the lower edge only")` from the A0 envelope before the M2 test, for B_V1 and the drag-free vehicle, including states just outside the ellipsoid (equator: r = [a + k·2^-30, 0, 0] raises for k = 1…9 and returns need = 55 993.323394842984 m at k = 10); the stage condition is not described as returning a finite need for every exterior state; the computed height (which decides) differs from the mathematical height (pole: [0, 0, fl(b)] is inside the ellipsoid, height −2.03e-10 m, computed height 0); a very negative h0 with b_lower + H0 ≤ 0 raises `decimal.InvalidOperation` and, by E1, is not the computed height of an exterior state; a returned finite need < 0 certifies only under the stated premises and A-FP-1 to A-FP-3. Corrected in the docstring; amendments appended to the Review 06 and Review 07 records; qualifications appended to VAL-0019, DR-0029 and the report.
- **M3 coverage gap:** `check_review08.py` asserts need = +∞ with an envelope that is +∞ at the first stage only (three heights × three finite values after it), and computes `-min(M2, M4)` alongside to show it would certify; the reviewer's mutant is `r8_m3_dropped_from_the_minimum` in the harness.
- **Checks:** `check_review08.py`, 27 checks; red before at `115e747` 2 fail (the docstring and record checks) and 25 pass; green after 288/288. Mutation: control 288/288; 87/87 non-equivalent mutants detected by a declared check (14 new R8 mutants: one numerical (M3 dropped), two lower-edge code mutants, eleven documentation/record mutants); 2 declared equivalent; no survivor.
- **Implementer-only evidence:** seeded adversarial probe (`adversarial_r8.py.txt`, seed 20261022): 37 541 near-surface states, 36 769 strictly exterior (exact rational test), 7 687 of them with computed h0 ≤ β; 15 374 rejections and 58 164 returned needs over both vehicles, none certified; E1 checked for every exterior state; 400 injected first-stage-infinity cases, all need = +∞.
- **Committed implementer evidence you can re-run:** `adversarial_r8.py.txt`, `smoke_r8.py.txt`, `ast_equal.py.txt` and `digests.py.txt` (`python -I <file> ...`), the mutation JSON and the red-before log.
- **Validation claims you cannot fully see:** M1 Proof and M2 Proof in fresh clones at `0254664`; full pytest; pinned and spike digests; the T0 experiments byte-identical over two runs including GMAT; CI runs 39641717044 (`0254664`) and 39652330844 (`f04f995`). You cannot access CI; state that. CI does not collect the T0 checks (`testpaths = ["tests"]`).

## Tech Lead's authorization (I-11), verbatim
# Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09

## 1. Authorization and scope

I authorize a targeted correction of M3T0-R8-F1, closure of the identified regression coverage gap, full validation, and one independent Codex Review 09.

This is **not** authorization to accept T0, merge, implement T1/T2, approve DR-0029 decisions, or modify the numerical model.

Baseline:
- Branch: `milestone-3-t0-reference-spike`
- Expected HEAD/origin: `115e747960bfec12e3f83f6d7deb9638a55d6803`
- Expected worktree: clean
- Review 08 verdict: `REQUEST_CHANGES`
- Finding: `M3T0-R8-F1`, NOTE, ACCEPTED

Verify these preconditions before making changes. Stop if they do not hold.

## 2. Correct M3T0-R8-F1

Apply the narrowly scoped documentation corrections proposed in the Review 08 checkpoint.

Explicitly document:

1. Every successfully returned finite `need` value is subject to the stated certification assumptions.
2. A computed initial height `h0 ≤ β` raises `ValueError`, including for states just outside the ellipsoid.
3. This behavior applies to both B_V1 and the drag-free vehicle.
4. The current implementation must not be described as returning a finite `need` for every state outside the ellipsoid.
5. The distinction between mathematical height and floating-point computed height must remain explicit.

Correct the `stage_lower_heights` docstring.

Append traceable amendments to the affected Review 06/07 records, VAL-0019, DR-0029, and T0 report. Preserve historical review evidence and clearly distinguish original claims from amendments.

Do not silently rewrite earlier findings.

## 3. Strengthen regression coverage

Add deterministic tests covering computed heights:

- At the ellipsoid surface.
- At successive representable floating-point values immediately above the relevant radius.
- Across the observed exception-to-finite-result transition.
- For B_V1 and the drag-free vehicle.

Verify actual computed heights rather than relying solely on requested mathematical offsets.

Add a regression using an injected envelope that is infinite only at the first stage. Assert that the returned `need` is positive infinity where the certification logic requires it.

Include the reviewer's M3-dropped mutant and ensure it is detected.

Add documentation mutants demonstrating that the corrected claims cannot silently regress.

The tests must distinguish:

- Valid finite certification.
- Intentional rejection through `ValueError`.
- Correct positive-infinity behavior.
- Invalid certification caused by omitting a required term.

Do not change numerical algorithms, floors, thresholds, or reference constants to make tests pass.

## 4. Preserve existing scientific limitations

Do not expand the certification claim.

Maintain explicit qualifications concerning:

- A-FP-1 through A-FP-3.
- Unresolved A-FP-2 libm accuracy assumptions.
- Platform-specific measurement evidence.
- C1/C2 vehicle scope.
- No-overflow and negative two-body energy assumptions.
- Absence of a certified missed-crossing bound for combined J2 and drag.
- Escalated GMAT geodetic-drag discrepancy, DR-0029 Q-G2-1.

Do not resolve DR-0029 P1–P10 or DR-0028 P6(b).

## 5. Validation

Run and record:

1. Red-before / green-after regression evidence.
2. All T0 checks, including new tests.
3. Full mutation harness, with surviving and equivalent mutants reported separately.
4. Full pytest suite.
5. Fresh-clone M1 Proof.
6. Fresh-clone M2 Proof.
7. Verification of all five pinned digests and twenty spike digests.
8. Two reproducibility runs of all tracked T0 experiments, including GMAT.
9. Four-job CI verification.

Explicitly report whether numerical outputs remain byte-identical.

Do not claim CI validates T0 checks unless those checks actually execute in CI.

Keep commits focused, append-only, and fast-forward. No force-push.

## 6. Independent Codex Review 09

Only after the correction and validation pass, start a fresh independent Codex review session.

Provide the reviewer with the complete relevant evidence, previous findings, scientific limitations, and I-11 authorization.

Require the reviewer to:

- Independently assess R8-F1.
- Check previously accepted findings for regressions.
- Evaluate the new near-surface and first-stage-infinity tests.
- Inspect the M3-dropped mutant.
- Search for new mathematical, floating-point, verification, and documentation defects.
- Identify unsupported certification claims.
- Return an explicit `PASS` or `REQUEST_CHANGES` verdict, with finding IDs and severity.

Do not coach the reviewer toward PASS.

## 7. Mandatory stop conditions

If Review 09 returns `REQUEST_CHANGES`:

- Record and independently reproduce findings.
- Classify and disposition each finding.
- Do not apply new corrections.
- Do not start Review 10.
- Do not prepare an acceptance dossier.
- Stop and request my authorization.

If Review 09 returns `PASS`:

- Prepare a T0 acceptance dossier with complete evidence and outstanding limitations.
- Do not declare T0 accepted.
- Do not merge.
- Do not start T1/T2.
- Stop for my explicit acceptance decision.

Any unexpected numerical change, protected-path modification, failed proof, digest mismatch, or unresolved validation failure requires an immediate stop and escalation.

## 8. Final checkpoint report

Report:

- Branch, HEAD, origin, worktree status.
- Commits and exact changed-file list.
- R8-F1 correction and evidence.
- New regression and mutation results.
- Full validation matrix.
- Independent Review 09 verdict and findings.
- Remaining scientific limitations and open DR items.
- Explicit T0 acceptance/merge status.
- The next authorization required.

Do not perform work beyond this authorization.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical argument**: for every bound or semantic claim, give or check the proof against the code, and use sweeps only to seek counterexamples. **Actively try to falsify soundness**: construct inputs designed to produce a false certification (need < 0 for a step whose stages can leave the domain, or an envelope below the model's computed drag), not only random samples.
1. **R8-F1, independently.** Read `stage_lower_heights`, `stage_need`, `drag_envelope`, the height functions and every consumer (the floor bisection in `sufficient_stage_condition`, `floor_comparison`, `libm_sensitivity`, `stage_stress`, the result writers). Verify from the code, not the docstring:
   - the lower-edge rejection: for which binary64 h0 a `ValueError` is raised, from where, before or after the M2 test, and for which b (B_V1, b = +∞, others);
   - which exterior states (and which interior states) reach a computed h0 ≤ β, at the equator, the pole and elsewhere; the relation between mathematical and computed height (E1) and whether the records state it correctly;
   - the very negative h0 case (`decimal.InvalidOperation`) and the claim that no exterior state reaches it;
   - that the docstring, VAL-0019, DR-0029, the report, the decision matrix, the README and the amendments to the Review 06 and Review 07 records now state exactly the implemented behaviour, neither broader nor narrower, and that the earlier wording is preserved and distinguishable from the amendments;
   - that no numerical behaviour changed (`git diff 115e747..0254664 -- docs/science/experiments/m3-t0/t0_termination.py`; your own AST or execution comparison).
2. **R7-F1 and the non-certification contract.** Reassess R7-F1 on its own merits: certification means need < 0 for every consumer; path 1 (M2 ≤ 0) and path 2 (M2 > 0) as stated; the early-return edge; infinite and out-of-range envelopes; NaN, negative, ±0, subnormal, huge and infinite b; non-finite and boundary h0.
3. **The new regression coverage.** Evaluate `check_review08.py` and the 14 R8 mutants:
   - whether the near-surface tests verify actual computed heights and whether their expected outcomes are derived independently of the implementation;
   - whether the first-stage-infinity tests pin M3's role, and whether the injected envelope is a meaningful test;
   - whether the tests distinguish valid finite certification, intentional `ValueError` rejection, correct +∞ behaviour and invalid certification from an omitted term;
   - inspect the M3-dropped mutant (`r8_m3_dropped_from_the_minimum`) and whether it is detected for the right reason; look for other corruptions of `stage_need`, `stage_lower_heights`, the lower-edge guard or the corrected text that still pass all checks, and write your own.
4. **Every earlier finding, individually.** Check each of R7-F2, R6-F1, R6-F2, R6-F3, the two Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5 for regressions individually (not by implication from another finding), at least to the extent the new commits could affect them. Re-run the key counterexamples of each.
5. **Soundness, adversarially.** Try to break the E4a bound (C1 and C2, b = 0 and subnormal boundaries, huge and subnormal cd·area), the drag envelope (subnormal densities, band bases, the top band, speed extremes), E4b (cd·area ≤ η₀, LIBM_ULP near 91910196476947) and the stage condition (stage heights near and below the lower edge, near the early-return edge, overflow). Write your own probes and new mutants. Search for new mathematical, floating-point, verification and documentation defects, and identify any certification claim not supported by the code and its stated premises.
6. **Records and provenance.** Verify that the historical review records were amended append-only (`git diff 115e747..HEAD -- docs/reviews`), that the superseded wording is preserved, that the 5 287-point search stays UNREPRODUCED, that IM-2 keeps its disposition, and that the GMAT geodetic-drag discrepancy remains escalated.
7. **Assumptions and scope.** Check A-FP-1, A-FP-2 and A-FP-3, the C1/C2-only contract scope, the no-overflow and negative two-body energy conditions and the absence of a certified J2-plus-drag missed-crossing bound wherever the guarantee is quoted. Host measurements must not be presented as a platform guarantee.
8. **Validation and integrity.**
   - Run: the Review 01–08 checks; the mutation harness or a justified subset, with your own new mutants; your own adversarial probes; the T0 experiments' reproducibility byte for byte, including the GMAT harness where practical; pytest and the M1/M2 validators and GMAT compares, with output into `review_scratch/`.
   - Verify: the five pinned digests and the VAL-0019 spike digests; that no protected path changed (`git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`); that the published floors, root brackets, margins, physics constants, vehicle definitions, contracts, baselines and goldens are unchanged (your own diff of the result files against `115e747`).
   - Check every number quoted in the I-11 records against the code, the result files and your own computation. Look for checks whose expected values come from the implementation.
9. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R8-F1, R7-F1, R7-F2, R6-F1, R6-F2, R6-F3, the two Review 06 remarks (provenance of the 5 287-point search; b* and φ_B), M3T0-R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2, M3T0-F1 … F5, and the Review 08 M3 coverage observation. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence and your reasoning for each separately. State separately the status of the escalated GMAT geodetic-drag discrepancy (it is to remain escalated, not resolved here).
3. **Assumptions and scope:** for A-FP-1, A-FP-2, A-FP-3, the C1/C2 scope, the overflow exclusion and the negative-energy condition, state whether each is stated honestly and completely, and what exactly is guaranteed unconditionally versus conditionally.
4. **New findings.** Number them `M3T0-R9-F1`, `M3T0-R9-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Adversarial attempts:** what you tried in order to falsify soundness, and the outcome of each.
6. **Verification limits:** what you could not check.
7. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
8. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review09.md`, and save your own scripts and logs under `review_scratch/`.
