You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 07** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 06. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`03571961bc72cd41fe853ce0c4d686d783ee6938`** (full SHA), with git metadata.
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
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6}.py` (about 3 min).
  - `mutation_check_review02.py` (about 42 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify: DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the Review 04 and Review 05 amendments (I-8), and the Review 06 record's correction and validation sections. Re-derive, re-execute, write independent checks and attempt counterexamples, in particular outside the implementer's sweeps.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass:** `489d4e7`, `44260ef` (reviewed by Review 04); `c15fbd4` (the Review 04 record).
- **Review 04 correction pass:** `a1feb79`, `88f9752` (reviewed by Review 05); `17b2229` (the Review 05 record).
- **Review 05 correction pass:** `411cabd`, `fcd5997` (reviewed by Review 06); `30a4e8d` (the Review 06 record).
- **Review 06 correction pass (under review now):**
  - `9e44850c6c6594a63638027d24c77aeb484eb566`: the correction for M3T0-R6-F1, R6-F2 and R6-F3 and the provenance and switch-point records, with `check_review06.py`, the extended mutation harness, the regenerated termination results and the records;
  - `03571961bc72cd41fe853ce0c4d686d783ee6938`: the validation record of `9e44850` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 30a4e8d..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–06:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria) and Authorizations I-4 to I-7. The Review 07 authorization and I-8 (the correction pass under review) are reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5,6}-evidence/`;
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,2,3,4,5,6}.md`. The Review 06 record ends with this pass's correction section (dispositions, the R6-F1 derivation and domain, the helper semantics, the E4b dependency, provenance and b*, evidence, unresolved assumptions) and its validation section.
- **Implementer correction evidence:** `docs/reviews/raw/M3-T0-review06-findings-correction-evidence/` (red-before and green-after logs, two mutation runs, a seeded adversarial probe script and log, the termination-results diff, the Proof/pytest/digest/reproducibility logs, `SHA256SUMS`). Earlier passes: `docs/reviews/raw/M3-T0-review0{2,3,4,5}-correction-evidence/` and `docs/reviews/raw/M3-T0-review05-findings-correction-evidence/`.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; six correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Experiment code:** `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_oracle.py`, `t0_termination.py`, `check_review01.py` … `check_review06.py`, `mutation_check_review02.py`, the README and the committed result files).

## Findings so far
- **Review 01:** M3T0-F1 (MAJOR): the missed-crossing bound; F2 (MAJOR): P1 sufficiency, thresholds and the speed proxy; F3 (MINOR): stage numbering; F4 (MINOR): a misquoted residual; F5 (NOTE): the dependency map against the owner gate.
- **Review 02:** R2-F1 (MINOR): sampled maxima presented as bounds; R2-F2 (MINOR): the co-rotation term evaluated at the lower height bound; R2-F3 (NOTE): checks that passed with zeroed evidence; IM-1: the P6 "0.99 m" figure without a procedure.
- **Review 03:** R3-F1 (MINOR): the numerical height error at density discontinuities.
- **Review 04:** R4-F1 (MINOR): the floating-point drag enclosure drops underflow errors.
- **Implementer item IM-2 (NOTE, from the Review 04 pass):** the drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The record is clarified and no floor is changed; the Tech Lead ordered the existing disposition kept.
- **Review 05 (verdict REQUEST_CHANGES):**
  - **R5-F1 (MINOR):** the conversion between the ballistic coefficient b and the mass kept a relative-only factor φ_B/b. With a subnormal b (C1, mass 17·2^-1074 kg) the model's drag was 1.94 times the envelope; with C2 and mass 30·2^-1074 kg, 1.10 times. The floors were not shown to be affected.
  - **R5-F2 (MINOR):** 0.983 was presented as the tightest drag/envelope ratio "in the subnormal regime"; the committed transition scan reaches about 0.99999999999886.
  - Review 05 judged R4-F1, R3-F1, R2-F2 and F2 PARTIALLY RESOLVED, each on the ground of R5-F1, and the other earlier items RESOLVED.

- **Review 06 (verdict REQUEST_CHANGES):**
  - **R6-F1 (MINOR):** under C1 a positive mass ≤ 16·2^-1074 kg with cd·area = 33 rounds to b = 0; the model's drag was finite and nonzero and the envelope raised ZeroDivisionError (the E4a derivation assumed b ≥ 2η₀).
  - **R6-F2 (NOTE):** `_up`/`_dn` raised on, or mis-rounded, out-of-range and infinite values; `stage_lower_heights(1e7, 2^-1074)` raised OverflowError.
  - **R6-F3 (NOTE):** E4b's cap c₀ ≤ 5/8 inherits A-FP-2 through the density allowance; the Review 05 record classified it as derived under A-FP-1 only.
  - Remarks: the 5 287-point random search was unreproduced and unmarked; b* ≈ 7.42e-309 uses the stored φ_B (exact φ_B: 1.11e-308).
  - Review 06 judged R5-F1, R4-F1, R3-F1, R2-F2 and F2 PARTIALLY RESOLVED, each on the ground of the b = 0 boundary, and the other earlier items RESOLVED.

## The implementer's claims for this pass (to verify, not to trust)
- **R6-F1:** for b = 0, R(0) = max(cd·area/2^-1074, R(2^-1074)) (mass ≥ 2^-1074 for every positive binary64 mass); b > 0 unchanged; b_R = φ_B/R(0) > 0 rounded down; R non-increasing on b ≥ 0; inputs outside the domain (b NaN/negative/+∞ for the lemma, cd or area not positive finite) raise ValueError. Review 06 masses: ratio 0.9999999999988 (k = 1) … 0.0625 (k = 16); k = 17 unchanged at 0.9706.
- **R6-F2:** `_up`/`_dn` over the extended reals (+∞ above MAX for `_up`, −MAX below −MAX, MAX above MAX for `_dn`, ±∞ passthrough, +0.0), NaN → ValueError, other types → TypeError; envelope/stage input validation; an infinite envelope makes need(h0) = +∞ (not certified).
- **R6-F3:** c₀ ≤ 5/8 depends on A-FP-2; holds for LIBM_ULP ≤ 91910196476947 (≈ 2^46.4), published as `zero_force_cap`.
- **Records:** 5 287-point search marked UNREPRODUCED (Review 04 amendment); b* stated for stored (7.416912861690675e-309) and exact (1.1125369292536007e-308) φ_B (Review 05 amendment).
- **Checks:** `check_review06.py`, 81 checks; red before 55/81 fail at `30a4e8d`; green after 238/238. Mutation: 61 mutants + control, 59 detected, 2 declared equivalent (two-body stationary points; the float NaN guard). First run had two survivors (both kept).
- **Implementer-only evidence:** seeded adversarial probe (`adversarial_r6.py.txt`, seed 20261020): 79 951 C1 vehicles (37 241 with b = 0), 20 780 C2, 4 934 monotonicity pairs, 353 b = 0 force states.
- **Floors:** unchanged to the last bit; only `review06_counterexamples` and `zero_force_cap` added.
- **Not changed by the implementer:** the status of R5-F1, R4-F1, R3-F1, R2-F2 and F2 (left to this review).
- **Committed implementer evidence you can re-run:** `docs/reviews/raw/M3-T0-review06-findings-correction-evidence/adversarial_r6.py.txt` (`python -I <file> docs/science/experiments/m3-t0`), the two mutation-run JSON files, the red-before log and the termination-results diff.
- **Validation claims you cannot fully see:** M1 Proof 9/9 and M2 Proof 20/20 at `9e44850`; pytest 1185 passed; pinned digests; 96 T0 files byte-identical over two runs including GMAT; CI runs 39489593015 (`9e44850`) and 39499192586 (`0357196`), four jobs each. You cannot access CI; state that. CI does not collect the T0 checks (`testpaths = ["tests"]`).

## Tech Lead's authorization for this review (I-9), verbatim
Authorization I-9 — M3 T0 Independent Review 07

I authorize independent Codex Review 07 of M3 T0 at commit 0357196.

This is REVIEW AUTHORIZATION ONLY. T0 remains BLOCKED and NOT ACCEPTED. No merge, T1/T2 implementation, or DR decision is authorized.

1. Preconditions

Verify:
- Branch milestone-3-t0-reference-spike.
- HEAD and origin both at 0357196.
- Clean worktree.
- CI 4/4 green for 9e44850 and 0357196.
- Five pinned digests unchanged.
- No unauthorized protected-path changes since 86df2c3.

Stop if any precondition fails.

2. Independent reviewer

Start a fresh Codex session in an independent clean clone at 0357196.

Provide the original T0 contracts, DR-0029 proposals, decision matrix, Reviews 01–06, raw reviewer outputs, correction records, mathematical derivations, validation scripts, and supporting evidence.

Treat the I-8 corrections as claims to verify, not established facts.

The existing Review 07 candidate prompt may be used as reference material, but independently inspect it for omissions, bias, and consistency with this authorization before use.

3. R6-F1 — boundary proof

Independently re-derive the corrected E4a envelope for C1 and C2.

Specifically verify:
- Binary64 subnormal minimum and the b = 0 boundary.
- Correctness of R(0) and the monotonicity join with R(2^-1074).
- Conservativeness of all intermediate floating-point operations.
- The claimed tightness at k = 1.
- The positive downward-rounded effective coefficient B_R.
- The b = +infinity zero-force case and all domain exclusions.
- Behavior around subnormal/normal transitions, zero, signed zero, and overflow boundaries.

Seek new counterexamples beyond the existing seeded sweeps.

Do not accept a numerical sweep as a substitute for a valid mathematical bound.

4. R6-F2 — extended-real helpers

Independently test _up and _dn for:
- Positive and negative finite extremes.
- Overflow in both directions.
- Positive and negative infinity.
- Signed zero.
- NaN and unsupported input types.

Verify that +infinity propagates as an explicit non-certification result rather than an unsupported finite certification.

Inspect downstream consumers for incorrect assumptions about finite results.

5. R6-F3 — E4b dependency

Independently verify the c0 <= 5/8 proof, its dependence on A-FP-1 and A-FP-2, and the reported LIBM_ULP threshold.

Check both sides of the threshold and determine whether the implementation, documentation, and conditional guarantee agree.

Do not infer a cross-platform libm guarantee from host measurements.

6. Prior findings and provenance

Individually reassess:
- R5-F1.
- R4-F1.
- R3-F1.
- R2-F2.
- F2.
- All other findings previously marked RESOLVED or PARTIALLY RESOLVED where affected by the new corrections.

Explicitly determine whether each is RESOLVED, PARTIALLY RESOLVED, or NOT RESOLVED.

Verify:
- The 5,287-point search is accurately marked UNREPRODUCED.
- The stored versus exact phi_B switch-point values are correctly distinguished.
- Historical review records were amended append-only.
- IM-2 retains its justified disposition.
- The GMAT geodetic-drag discrepancy remains escalated.

7. Validation and integrity

Run the relevant independent tests, adversarial probes, Review 01–06 checks, mutation checks, and reproducibility checks.

Verify M1/M2 Proof, full pytest, pinned digests, and protected-path integrity.

Confirm the published floors, root brackets, margins, physics constants, vehicle definitions, contracts, baselines, and goldens are unchanged.

Record the precise environment and limitations of all numerical evidence.

8. Review outcome

Preserve the raw Codex output verbatim.

Classify new findings as BLOCKER, MAJOR, MINOR, or NOTE, with reproducible evidence.

If REQUEST_CHANGES:
- Record and independently reproduce findings where possible.
- Do not correct findings.
- Do not start Review 08.
- Do not prepare T0 acceptance.
- Stop and request my authorization.

If PASS:
- Prepare a T0 acceptance-candidate report.
- Clearly separate proven mathematical bounds from conditional floating-point assumptions and host-only measurements.
- Identify any remaining limitations, escalations, or decisions.
- Do not declare T0 accepted or merge.

9. Repository discipline

Only commit authorized review records and evidence.
Use append-only documentation, fast-forward pushes, and no force-push.
Verify CI on the final review-record commit.

Do not change protected scientific artifacts, weaken tests or thresholds, decide DR-0029 P1–P10 or DR-0028 P6(b), start T1/T2, or close the GMAT escalation without evidence.

10. Final checkpoint

Report:
- Branch, HEAD, origin, commits, clean-tree status, and CI.
- Independent reviewer identity and exact verdict.
- Finding-by-finding dispositions.
- New findings and independent reproductions.
- Mathematical and numerical evidence.
- Mutation, proof, pytest, digest, and reproducibility results.
- Remaining A-FP assumptions and contract limitations.
- Whether T0 is ready for my acceptance review.

Stop and await my decision.

## Authorization I-8 (the correction pass under review), verbatim
Authorization I-8 — M3 T0 Review 06 Corrections

I authorize a focused correction pass for Review 06 findings R6-F1, R6-F2, and R6-F3, plus the specifically identified provenance and switch-point documentation defects.

This is correction authorization only. T0 remains BLOCKED and NOT ACCEPTED. Do not start Review 07 without separate authorization.

1. Preconditions

Verify branch milestone-3-t0-reference-spike, HEAD/origin 30a4e8d, clean worktree, successful CI, and unchanged protected artifacts since 86df2c3.

Stop if any precondition fails.

2. R6-F1 — C1 subnormal boundary (MINOR)

Re-derive the E4a bound for all valid C1 constructions, including positive mass k × 2^-1074 for k = 1…17 and the b = 0 boundary.

Preferred approach: option (b), extending the conservative derivation to mass >= 2η₀ where mathematically justified, including the b = 0 case.

Do not assume that a proposed expression is safe merely because it passes the known counterexamples.

Independently prove denominator positivity, rounding-direction safety, conservativeness, and correct handling of subnormal arithmetic.

If a finite certified bound cannot be justified, return an explicit non-certification result such as +infinity, with documented semantics.

Add regressions for k = 1…17, neighboring transition values, both C1/C2 constructions, and adversarial boundary cases.

Add targeted mutation checks that would detect restoration of the defect.

3. R6-F2 — rounding helper robustness (NOTE)

Make _up and _dn safe for their documented input domains, including positive and negative finite extremes, signed zero, infinities, and overflow boundaries.

Distinguish an infinite conservative bound from invalid inputs or failed certification. Do not silently transform an invalid value into a certified result.

Document behavior for NaN and other unsupported inputs.

Add targeted regression and mutation coverage.

Do not change published numerical floors or weaken validation criteria.

4. R6-F3 — E4b assumption dependency (NOTE)

Correct the E4b documentation so the c₀ <= 5/8 claim explicitly depends on A-FP-2 wherever the density allowance relies on LIBM_ULP.

Verify the dependency algebraically and through a parameterized check that demonstrates the claim's behavior when LIBM_ULP is increased.

Do not strengthen A-FP-2, invent a platform guarantee, or describe the cap as libm-independent.

5. Provenance and switch-point corrections

Explicitly mark the 5,287-point random-search claim as UNREPRODUCED unless its original evidence can be recovered and independently verified.

Identify whether the reported b* ≈ 7.42e-309 uses stored or exact φ_B. Correct the derivation and wording so both values are distinguished where relevant.

Do not alter the underlying pinned constants or validated physics merely to reconcile documentation.

Preserve historical records through append-only amendments.

6. Validation

Use red-before/green-after regression evidence.

Run all Review 01–06 checks, mutation checks, M1 Proof, M2 Proof, full pytest, reproducibility checks, pinned digest checks, and protected-path comparisons.

Repeat the T0 experiments and GMAT comparisons where required by the established validation contract.

Record exact commands, outcomes, hashes, and any platform limitations.

Verify published floors, root brackets, margins, vehicle definitions, contracts, and golden references remain unchanged.

7. Independent review boundary

Do not start Review 07, reuse Review 06 as approval, or upgrade previously partially resolved findings yourself.

Prepare a Review 07 candidate package only after the correction pass and validation succeed.

If a new BLOCKER/MAJOR issue, changed scientific contract, altered published floor, or unprovable certification claim appears, stop and report before proceeding.

8. Repository discipline

Keep changes within the authorized T0 documentation, experiment code, tests, and evidence.

Preserve raw reviewer records. Use append-only corrections, clean commits, and fast-forward pushes. No force-push.

Do not merge, start T1/T2, decide DR-0029 P1–P10 or DR-0028 P6(b), or close the GMAT geodetic-drag escalation without evidence.

9. Final checkpoint

Report:
- Branch, HEAD, commit sequence, worktree, and CI.
- Exact mathematical correction for R6-F1 and its domain.
- R6-F2/R6-F3 dispositions and tests.
- Red-before/green-after results and mutation coverage.
- Full validation and reproducibility results.
- Provenance and b* documentation corrections.
- Unresolved assumptions and conditional guarantees.
- Any new findings or stop conditions.
- Whether the branch is technically ready for independently authorized Review 07.

Stop and await my decision.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical bound**: for every bound, give or check the proof, and use sweeps only to seek counterexamples.
1. **R6-F1 — the E4a boundary proof.** Re-derive the corrected E4a bound for C1 (b = fl(mass/fl(cd·area))) and C2 (mass = fl(fl(b·cd)·area)) against `t0_model.py` and `t0_termination.py` (`inverse_ballistic_bound`, `envelope_ballistic_coefficient`, `drag_envelope`). Verify specifically:
   - the binary64 subnormal minimum 2^-1074 and the b = 0 boundary (which C1 masses give b = 0 for which fl(cd·area); whether C2 can give b = 0 with a positive mass);
   - the correctness of R(0) = max(cd·area/2^-1074, R(2^-1074)), its monotonicity join with R(2^-1074), and that R is non-increasing on all b ≥ 0;
   - the conservativeness of every intermediate floating-point operation of the model's drag for b = 0 vehicles (the coefficient chain, its division by a subnormal mass, the velocity terms), and that the vehicle enters only through cd·area/mass;
   - the claimed tightness at k = 1 (ratio 0.9999999999988) and why the envelope still covers it;
   - that the effective coefficient B_R = φ_B/R is positive and rounded down, and that the same binary64 b is returned exactly when claimed;
   - the b = +∞ zero-force case (E4b) and every domain exclusion (NaN, negative, signed zero, non-positive or non-finite cd and area, overflow);
   - behaviour around the subnormal/normal transitions of b, P, b·cd and mass, at zero and signed zero, and at the overflow boundaries.

   Seek new counterexamples beyond the committed sweeps (the 17 Review 06 masses; k ≤ 20 000 on 10 shapes; the seeded probe): for example other shapes, masses near η₀·P for huge P, subnormal cd with a huge area, and other heights and velocities.
2. **R6-F2 — extended-real helpers.** Independently test `_up` and `_dn` for positive and negative finite extremes, overflow in both directions, ±∞, signed zero, NaN and unsupported input types, against exact comparisons. Verify that +∞ propagates as an explicit non-certification (need(h0) = +∞, never a finite certified value) and that invalid input raises rather than becoming a bound. Inspect every downstream consumer of `_up`, `_dn`, `drag_envelope` and `stage_lower_heights` (including `stage_need`, the floor bisection, `libm_sensitivity`, `floor_comparison`, `stage_stress` and the result writers) for incorrect assumptions that results are finite, and for any Decimal or Fraction conversion, comparison or sum that can receive ±∞ or NaN.
3. **R6-F3 — E4b dependency.** Independently verify the c₀ ≤ 5/8 proof and both E4b sub-cases (area ≤ 1/4, otherwise), its dependence on A-FP-1 and A-FP-2, and the reported limit LIBM_ULP ≤ 91910196476947. Check both sides of the limit, and whether the implementation, the documentation and the conditional guarantee agree. Do not infer a cross-platform libm guarantee from host measurements.
4. **Prior findings, individually.** Reassess R5-F1, R4-F1, R3-F1, R2-F2 and F2 each on its own merits (not by implication from R6-F1), and every other finding previously marked RESOLVED or PARTIALLY RESOLVED where the new corrections affect it (R5-F2, R2-F1, R2-F3, IM-1, IM-2, F1, F3, F4, F5).
5. **Provenance and records.** Verify:
   - that the 5 287-point search is accurately marked UNREPRODUCED;
   - that the stored-φ_B (7.416912861690675e-309) and exact-φ_B (1.1125369292536007e-308) switch points are correctly derived and distinguished;
   - that the historical review records (Reviews 04, 05 and 06) were amended append-only (`git diff 30a4e8d..HEAD -- docs/reviews`);
   - that IM-2 retains its justified disposition;
   - that the GMAT geodetic-drag discrepancy remains escalated.
6. **Assumptions and scope.** Check A-FP-1, A-FP-2 and A-FP-3, the C1/C2-only contract scope and the overflow exclusion: are they stated honestly and completely wherever the guarantee is quoted? Host measurements must not be presented as a platform guarantee.
7. **Validation and integrity.**
   - Run:
     - the Review 01–06 checks;
     - the mutation harness, or a justified subset, together with your own new mutants of the R6 corrections;
     - your own adversarial probes;
     - the reproducibility of the T0 experiments, byte for byte, including the GMAT harness where practical;
     - pytest and the M1/M2 validators and GMAT compares, with output into `review_scratch/` (not the Proof wrappers).
   - Verify:
     - the five pinned digests and the VAL-0019 spike digests;
     - that no protected path changed (`git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`);
     - that the published floors, root brackets, margins, physics constants, vehicle definitions, contracts, baselines and goldens are unchanged (`termination_results_diff.txt`, and your own diff of `t0_termination_results.json` against `30a4e8d`).
   - Check every number quoted in the I-8 records against the result files and your own computation.
   - Look for checks whose expected values come from the implementation, and for corruptions of the new terms that still pass.
8. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R6-F1, R6-F2, R6-F3, the two Review 06 remarks (provenance of the 5 287-point search; b* and φ_B), M3T0-R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and M3T0-F1 … F5. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence. For R5-F1, R4-F1, R3-F1, R2-F2 and F2, give the reasoning for each separately.
3. **Assumptions and scope:** for A-FP-1, A-FP-2, A-FP-3, the C1/C2 scope and the overflow exclusion, state whether each is stated honestly and completely, and what exactly is guaranteed unconditionally versus conditionally.
4. **New findings.** Number them `M3T0-R7-F1`, `M3T0-R7-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Verification limits:** what you could not check.
6. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
7. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review07.md`, and save your own scripts and logs under `review_scratch/`.
