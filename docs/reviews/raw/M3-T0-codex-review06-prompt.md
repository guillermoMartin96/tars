You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 06** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 05. You review; you do not fix. The implementer's records are claims, not evidence: nothing in them is presumed correct.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`fcd5997cd120c8834651d3c0da2e52899f2d9ffc`** (full SHA), with git metadata.
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
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5}.py` (about 2.5 min).
  - `mutation_check_review02.py` (about 31 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify: DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the Review 04 amendment and the Review 05 record's correction and validation sections, and the implementer's own assessment of R4-F1 and the related items in that record. Re-derive, re-execute, write independent checks and attempt counterexamples, in particular outside the implementer's sweeps.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass:** `489d4e7`, `44260ef` (reviewed by Review 04); `c15fbd4` (the Review 04 record).
- **Review 04 correction pass:** `a1feb79`, `88f9752` (reviewed by Review 05); `17b2229` (the Review 05 record).
- **Review 05 correction pass (under review now):**
  - `411cabd0e7a2be57ee59baa040d0ea5607d8f00a`: the correction for M3T0-R5-F1 and M3T0-R5-F2, with the new checks, the extended mutation harness, the regenerated termination results and the records;
  - `fcd5997cd120c8834651d3c0da2e52899f2d9ffc`: the validation record of `411cabd0e7a2be57ee59baa040d0ea5607d8f00a` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 17b2229..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–05:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4,5}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria) and Authorizations I-4 and I-5. Authorizations I-7 (this review) and I-6 (the correction pass under review) are reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{2,3,4,5}-evidence/`;
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,2,3,4,5}.md`. The Review 05 record ends with this pass's correction section (approach, derivation, counterexamples, A-FP status, evidence classification, regression and mutation evidence, the implementer's assessment of R4-F1 and related items) and its validation section.
- **Implementer correction evidence:** `docs/reviews/raw/M3-T0-review05-findings-correction-evidence/` (red-before and green-after logs, two mutation runs, an exhaustive E4a sweep script and log, the termination-results diff, the Proof/pytest/digest/reproducibility logs, `SHA256SUMS`). Earlier passes: `docs/reviews/raw/M3-T0-review0{2,3,4,5}-correction-evidence/`.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; five correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Experiment code:** `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_oracle.py`, `t0_termination.py`, `check_review01.py` … `check_review05.py`, `mutation_check_review02.py`, the README and the committed result files).

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

## The implementer's claims for this pass (to verify, not to trust)
- **R5-F1, option (b) chosen by the Tech Lead:** no vehicle prerequisite; the conversion carries its absolute error (E4a in `t0_termination.py`: `inverse_ballistic_bound`, `envelope_ballistic_coefficient`, `drag_envelope`).
  - C1: P = fl(cd·area), b = fl(mass/P). C2: Q = fl(b·cd), mass = fl(Q·area).
  - R1 (C1) = [min(max(1/(1−u), cd·area/(cd·area−η₀)), cd·area/(2η₀))] · max((1+u)/b, 1/(b−η₀)); R2 (C2) = cd·area/M_lo with Q_lo = max(2η₀, min(b·cd(1−u), b·cd−η₀)) and M_lo = max(2η₀, min(Q_lo·area(1−u), Q_lo·area−η₀)); R = max(φ_B/b, R1, R2), η₀ = 2^-1075.
  - Claimed: R bounds cd·area/mass for either construction; R = φ_B/b for normal conversions (so the envelope and every result are unchanged to the bit for B 25.8 and B 100); switch point b* = cη₀/(c−1), c = φ_B(1−u), b* ≈ 7.42e-309 for the V1 shape; R non-increasing in b.
  - The envelope uses b_R = φ_B/R, rounded down in 60-digit decimals, in both the relative part and the R4-F1 absolute part (all vehicle dependence of E4 is claimed to enter through cd·area/mass).
  - **E4b:** cd·area ≤ η₀ ⇒ the model's force is exactly 0; relies on a derived constant c₀ = fl(0.5ρ̂) ≤ 5/8 (`zero_force_c0_max` ≈ 0.6125). C1 gives b = +∞ only for P = 0 or an overflowing quotient, which the existing "no overflow" domain condition excludes.
  - **`_up`** now returns +∞ when the exact bound exceeds the largest binary64 (it used to raise OverflowError).
  - The superseded envelope is kept as `drag_envelope_relative_conversion`; `sufficient_stage_condition.review05_counterexamples` records both Review 05 counterexamples (claimed 1.941 → 0.971 and 1.100 → 0.550).
- **R5-F2:** 0.983 (B 100) and 0.953 (B 25.8) are now scoped to the "coefficient-rounding subset" in DR-0029 P1, with the transition scan's subnormal-density maxima 0.99999999999886 (B 25.8) and 0.99999999999885 (B 100) stated next to them; the Review 04 record is amended by an appended note. The implementer reports that the 0.983 figure came from an ad-hoc, uncommitted measurement (±200 binary64 neighbours of `coefficient_flip_x` and 400 seeded uniform points, at three retrograde speeds), now re-implemented in `check_review05.py`. The "random search of 5 287 points" quoted in the Review 04 record (line 141) was also never committed; the implementer lists this as an open provenance gap.
- **Checks:** `check_review05.py`, 17 checks (counterexamples, the E4a lemma against exact rationals for 243 vehicles of both constructions, a second implementation of R and of the envelope, the switch, normal B unchanged, the model's drag within the envelope for subnormal conversions, zero force without area, R5-F2 record and recomputation checks). Red before: 17/17 fail at `17b2229` with no shim. Green after: checks 01–05 157/157.
- **Mutation:** 45 mutants plus a control against all five check files; claimed 44 detected by a declared check, 1 equivalent (`script_two_body_without_stationary_points`); all 10 R4-F1 mutants detected again. Two R5 mutants (C1 product term removed; C2 terms removed) are claimed detectable only by the lemma checks, and `r5_bound_applied_to_relative_part_only` only by the envelope second implementation. A first run left one R5-F2 mutant undetected; the check was strengthened and the run repeated (both kept).
- **Implementer-only evidence (not a test):** an exhaustive sweep over masses and coefficients k·2^-1074, k ≤ 20 000, on eight shapes (219 983 vehicles, no violation).
- **Floors:** unchanged to the last bit (124 456.68544510857, 118 633.50894662621, 111 511.96182508787 m); root brackets and margins (7.2e-7, 1.0e-6, 8.4e-7 m) unchanged; only two result keys added.
- **Implementer's assessment of R4-F1, R3-F1, R2-F2, F2:** Review 05's only stated ground was R5-F1; the implementer did not change their status and left it to this review, listing three remaining conditions (A-FP-2; the overflow exclusion; the C1/C2-only scope).
- **Validation claims you cannot fully see:** M1 Proof 9/9 and M2 Proof 20/20 at `411cabd0e7a2be57ee59baa040d0ea5607d8f00a` in separate fresh clones; pytest 1185 passed; the five pinned digests; byte-identical double runs of all 95 T0 experiment files including GMAT; CI on `411cabd0e7a2be57ee59baa040d0ea5607d8f00a` (run 39361891229) and `fcd5997cd120c8834651d3c0da2e52899f2d9ffc` (run 39370422938), four jobs each. You cannot access CI; state that. CI does not collect the T0 checks (`testpaths = ["tests"]`).

## Tech Lead's authorization for this review (I-7), verbatim

Authorization I-7 — M3 T0 Independent Review 06

I approve initiating independent Codex Review 06 of M3 T0 at fcd5997. This is REVIEW AUTHORIZATION ONLY, not acceptance of T0 or approval of any DR decision.

1. Preconditions
Verify branch milestone-3-t0-reference-spike, HEAD/origin fcd5997, clean worktree, successful CI for 411cabd and fcd5997, and unchanged protected paths and pinned digests. Stop if any precondition fails.

2. Independent review
Use a fresh independent Codex review context. Provide the original T0 contracts, decision matrix, reviews 01–05, correction records, experiment artifacts, and validation evidence. Do not present the corrections as presumptively correct.

Review must independently:
- Re-derive E4a for C1 and C2, including absolute rounding errors, gradual underflow, denominator positivity, and overflow-domain assumptions.
- Verify E4b and the exact-zero-force claim, including boundary conditions.
- Verify the derivation and downward rounding of B_R and its propagation through both relative and absolute drag-envelope terms.
- Challenge the monotonicity and switch-point claims and seek adversarial counterexamples outside the existing sweep.
- Verify the corrected scope and provenance of the 0.983 measurement and committed transition-scan maxima.
- Reassess R4-F1, R3-F1, R2-F2 and F2 individually, rather than upgrading their statuses by implication.
- Evaluate whether A-FP-2 remains an acceptable explicitly conditional assumption; do not convert host measurements into a platform guarantee.
- Check A-FP-1/A-FP-3, C1/C2-only contract scope, and overflow exclusions.
- Examine the _up behavior change to +infinity for downstream implications.
- Evaluate the uncommitted random-search provenance gap, existing IM-2 disposition, and escalated GMAT geodetic-drag discrepancy.
- Verify no floors, roots, margins, vehicle definitions, constants, baselines, goldens, or contracts were silently changed.

3. Review integrity
Use an independent reviewer, not the correction author's self-assessment. Preserve raw reviewer output verbatim. Do not weaken tests, thresholds, assumptions, or review criteria to obtain PASS.

Classify each finding as BLOCKER, MAJOR, MINOR or NOTE, with reproducible evidence where applicable. Explicitly state the disposition of every previously unresolved or partially resolved finding.

4. Validation and recording
Run appropriate existing checks and independent counterexample tests. Confirm reproducibility and protected-path integrity. Record Review 06 and its evidence append-only. Commit and push only authorized review records and supporting evidence, using fast-forward pushes. Confirm CI for the final commit.

5. Stop conditions
If Review 06 returns REQUEST_CHANGES, record and reproduce findings where possible, but DO NOT correct them or start Review 07. Stop and request my authorization.

If Review 06 returns PASS, prepare a T0 acceptance-candidate report, explicitly distinguishing unconditional findings from conditional guarantees. Do not declare T0 accepted.

6. Boundaries
Do not merge, start T1/T2, decide DR-0029 P1–P10 or DR-0028 P6(b), close the GMAT escalation without evidence, change protected physics or validation artifacts, or authorize implementation.

7. Final checkpoint
Report branch/HEAD, commits, CI, reviewer verdict, finding-by-finding dispositions, independent evidence, unresolved assumptions, exact scope of guarantees, and a recommendation on T0 acceptance readiness.

Stop and await my decision.

## Tech Lead's authorization for the correction pass under review (I-6), verbatim

Authorization I-6 — M3 T0 Review 05 corrections only

You are authorized to perform one bounded correction pass for the two ACCEPTED
MINOR findings from Review 05:

- M3T0-R5-F1
- M3T0-R5-F2

T0 remains BLOCKED and NOT ACCEPTED.

This authorization does NOT authorize Review 06, acceptance, merge, T1, T2,
or any decision on DR-0029 P1–P10 or DR-0028 P6(b).

Baseline
- Branch: milestone-3-t0-reference-spike
- Expected starting HEAD:
  17b2229d9673812857c01c669cae5f3d1161ee6d
- Expected origin HEAD: same
- Expected working tree: clean
- Review 05 record:
  docs/reviews/M3-T0-review-05.md

Before changing anything, verify the branch, HEAD, origin HEAD and clean tree.
If any of those differ materially from this authorization, STOP and report the
difference.

1. R5-F1 decision: use option (b)

Preserve the unrestricted drag-envelope domain.

Do NOT introduce a vehicle prerequisite merely to make the existing
relative-only ballistic-coefficient conversion proof valid.

Correct the proof/model so that conversion from vehicle parameters to the
ballistic coefficient carries the necessary absolute floating-point error,
including the subnormal regime.

The corrected reasoning must compose correctly with the absolute-underflow
terms already introduced by the R4-F1 correction.

Specifically:

- identify the exact operations involved in deriving the ballistic coefficient;
- model normal-result rounding and subnormal/underflow behavior explicitly;
- propagate the resulting error into the downstream drag-envelope derivation;
- remove or correct any false prerequisite claims associated with the two
  Review 05 counterexamples;
- demonstrate that both Review 05 counterexamples are covered by the corrected
  envelope;
- check boundary/transition cases where the relative and absolute terms switch
  dominance;
- preserve the unrestricted supremum intended by the existing envelope contract.

Do not silently strengthen A-FP-1, A-FP-2 or A-FP-3. If the correction actually
requires a new assumption or a stronger version of an existing assumption,
STOP and report it rather than adopting it.

2. R5-F2 correction

Correct the statement that characterizes 0.983 as the tightest observed
drag/envelope ratio "in the subnormal regime."

Re-scope it precisely to the subset for which 0.983 was actually observed
(the coefficient-rounding subset, if the evidence confirms that wording).

The committed transition scan reaching approximately 0.999999... must remain
visible and must not be misrepresented.

Preserve the historical Review 04 material according to the project's
append-only/amendment convention. Do not rewrite historical review evidence
as though the old statement had never existed.

3. Hard scope constraints

This is a documentation/proof/validation correction pass only.

Do NOT change:
- published stage floors;
- vehicle definitions or vehicle parameters;
- physics;
- atmosphere data;
- reference baselines;
- goldens;
- pinned constants;
- M1/M2 contracts;
- production simulator behavior;
- acceptance thresholds;
- DR-0029 decisions;
- DR-0028 P6(b).

No files outside the already authorized T0 documentation/proof-validation
scope should change unless strictly required to validate these two findings.
If a correction appears to require a substantive code, physics, baseline,
vehicle, floor or contract change, STOP and report it.

In particular, do not alter a published floor merely because IM-2 shows that
111511.96 m is 1.8 mm below the rigorous bound. Keep the existing recorded
disposition unless separately authorized.

4. Regression requirements

Add or extend focused regression checks that fail against the pre-correction
Review 05 state and pass after the correction.

At minimum cover:

- the Review 05 subnormal-ballistic-coefficient counterexample producing about
  1.94× the old envelope;
- the second construction using mass = 30 × 2^-1074 kg producing about 1.10×;
- representative normal ballistic coefficients;
- transition cases around normal/subnormal conversion behavior;
- cases exercising the new absolute conversion-error term;
- the transition-scan evidence relevant to R5-F2.

Record red-before and green-after evidence.

Do not weaken an existing assertion simply to obtain green results.

5. Mutation / sensitivity validation

Extend the existing mutation strategy to demonstrate that the new
ballistic-coefficient absolute-error contribution is necessary.

Include focused mutants that remove, reduce or incorrectly apply the new
absolute term. The relevant regression checks must detect them.

Also verify that the R5-F2 evidence would detect a future accidental return to
the incorrect "tightest in the subnormal regime" characterization.

Record the mutation definitions and results.

6. Revalidate earlier R4-F1 work

Because R5-F1 composes with the R4-F1 correction, rerun the relevant R4-F1
regressions and mutations.

Determine explicitly whether R4-F1 and its associated partially-resolved items
can now be classified RESOLVED, or whether some independent condition still
prevents that classification.

Do not upgrade their status merely because R5-F1 was edited.

7. Floors and numerical invariants

Recompute the three published floors and their margins using the existing
procedure.

They must remain unchanged within the previously established reproducibility
criteria.

Explicitly report:
- each floor;
- its recomputed root;
- its safety margin;
- whether any bit-level or stated-tolerance change occurred.

If a published floor, vehicle, physics result or baseline changes unexpectedly,
STOP.

8. A-FP-2 remains unresolved

Do not treat this correction as resolving the maths-library guarantee issue.

Preserve the distinction between:
- observed host measurements;
- the weakened required ulp limits;
- actual platform guarantees;
- CI coverage.

Do not claim portability or unconditional proof where only the existing
conditional A-FP-2 argument exists.

9. Full validation

After the focused correction passes, run the applicable T0 validation plus the
established M1/M2 non-regression suite, including:

- focused R5 regression checks;
- relevant R4 regression checks;
- mutation checks;
- reproducibility checks;
- M1 Proof;
- M2 Proof;
- pytest/full established repository test suite;
- pinned digest checks.

Confirm that no unauthorized baseline or golden changed.

Push only by normal fast-forward operation. No force-push.

10. Commit discipline

Keep the correction append-only and auditable.

Prefer separate commits for:
1. R5-F1/R5-F2 correction;
2. validation/evidence for the correction.

Do not create a Review 06 prompt or Review 06 record in this authorization.

11. STOP conditions

STOP immediately and report instead of improvising if:

- the starting branch/HEAD/tree does not match the authorization materially;
- option (b) cannot be made valid without narrowing the envelope domain;
- a new or stronger floating-point assumption is required;
- a floor, vehicle, physics model, baseline, golden or pinned constant would
  need to change;
- M1 or M2 Proof regresses;
- a pinned digest changes unexpectedly;
- the corrected envelope still fails either Review 05 counterexample;
- relevant mutants survive unexpectedly and cannot be explained without
  changing scope;
- the correction requires deciding DR-0029 P1–P10 or DR-0028 P6(b).

12. Final report and mandatory stop

When the bounded correction and validation are complete, report:

- branch, final HEAD, origin HEAD and working-tree status;
- commits created;
- exact R5-F1 derivation change and how the absolute conversion error propagates;
- results for both Review 05 counterexamples;
- R5-F2 corrected scope and the actual transition-scan maximum;
- red-before / green-after results;
- mutation results;
- R4-F1 regression results and updated finding statuses;
- all three floors, roots and margins;
- A-FP-1/A-FP-2/A-FP-3 status, clearly separating assumptions from measured
  evidence;
- M1 Proof, M2 Proof, pytest and digest results;
- reproducibility results;
- complete changed-file list;
- CI status for every new commit;
- remaining open findings, assumptions, decisions and risks;
- whether T0 is technically ready for an independent Review 06.

Then STOP.

Do NOT start Review 06.
Do NOT declare T0 accepted.
Do NOT merge.
Do NOT start T1 or T2.
Do NOT decide any DR-0029 item or DR-0028 P6(b).

Review 06 requires separate authorization after I inspect this correction report.

## What to review
Evaluate each of the following independently, with your own derivation, execution or computation wherever possible.
1. **E4a for C1 and C2.** Re-derive both bounds operation by operation against the code (`t0_model.py` for how the model uses the mass, `t0_termination.py` for the bound) under A-FP-1's mixed model, including:
   - the absolute rounding errors and gradual underflow of each product and quotient;
   - denominator positivity (P > 0, b − η₀ > 0, cd·area − η₀ > 0, Q and mass ≥ 2η₀) and whether every case in which a denominator could vanish or go negative is excluded by a stated, true argument;
   - the overflow-domain assumption, and whether any case is excluded silently;
   - whether R is truly an upper bound on cd·area/mass for every finite positive input of either construction, including subnormal cd or area, and mixed normal/subnormal intermediates.
2. **E4b and the exact-zero-force claim.** Verify it including its boundary conditions: cd·area exactly η₀ and its binary64 neighbours, the two sub-cases (area ≤ 1/4, otherwise), the derivation of c₀ ≤ 5/8 and of `zero_force_c0_max`, and whether "force exactly 0" holds for every state in the domain.
3. **b_R.** Verify its derivation, that it is rounded in the safe direction, that `envelope_ballistic_coefficient` returns the same binary64 b exactly when it claims to, and its propagation through both the relative and absolute drag-envelope terms (including W, N_ρ and S_max). Look for a term still evaluated with the original b.
4. **Monotonicity and switch point.** Challenge R being non-increasing in b and the b* ≈ 7.42e-309 switch claim. Seek adversarial counterexamples outside the existing sweeps (243-vehicle grid; k ≤ 20 000 exhaustive sweep on 8 shapes): other shapes, extreme cd or area, subnormal P, Q or mass, values near 2^-1022, near b*, near overflow, and other heights and velocities.
5. **R5-F2.** Verify the corrected scope and the provenance of the 0.983 measurement and of the committed transition-scan maxima, by recomputing them. Check that the transition-scan maximum is visible and not misrepresented, and that the Review 04 history was amended, not rewritten.
6. **Earlier items, individually.** Reassess R4-F1, R3-F1, R2-F2 and F2 each on its own merits, not by implication from R5-F1, and re-check the remaining earlier items (F1, F3–F5, R2-F1, R2-F3, IM-1, R3-F1).
7. **A-FP-2.** Evaluate whether it remains an acceptable, explicitly conditional assumption and whether every record states it so. Host measurements must not be presented as a platform guarantee.
8. **A-FP-1 and A-FP-3, the C1/C2-only contract scope and the overflow exclusions.** Are they stated correctly and completely, and is the contract scope (b formed by C1 or C2) adequate and disclosed wherever the guarantee is quoted?
9. **`_up` returning +∞.** Examine downstream implications: every caller, whether +∞ (or −∞) can reach a comparison, a sum, a Decimal or Fraction conversion, a root search, a stage condition or a result file, and whether `_dn` or other helpers have a matching unhandled case.
10. **Provenance and dispositions.** Evaluate the uncommitted 5 287-point random-search provenance gap, the existing IM-2 disposition, and the escalated GMAT geodetic-drag discrepancy (which must remain escalated unless closed with evidence).
11. **Nothing silently changed.** Verify that no floor, root, margin, vehicle definition, constant, baseline, golden, threshold or contract changed (`git diff 17b2229..HEAD`, `git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`, the termination-results diff, the five pinned digests).
12. **Regression and mutation evidence.** Re-run the red-before against `17b2229` if practical, re-run the checks, and check that each claimed detection is real and for the claimed reason. Look for corruptions of the new term that still pass, and for expected values derived from the implementation.
13. **Records.** Check every number quoted in DR-0029, VAL-0019, the T0 report, the decision matrix, the README, the Review 04 amendment and the Review 05 correction and validation sections against the committed result files and your own computation. Check scope and decision authority: no production change; no new dependency; no DR-0029 item or DR-0028 P6(b) treated as decided.

Also re-run the Python experiments (and the GMAT harness where practical), compare the outputs byte for byte, and re-check the five pinned digests.

## Required output
1. **Ledger:** every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and M3T0-F1 … F5. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence. For R4-F1, R3-F1, R2-F2 and F2, give the reasoning for each separately.
3. **Assumptions and scope:** for A-FP-1, A-FP-2, A-FP-3, the C1/C2 scope and the overflow exclusion, state whether each is stated honestly and completely, and what exactly is guaranteed unconditionally versus conditionally.
4. **New findings.** Number them `M3T0-R6-F1`, `M3T0-R6-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
5. **Verification limits:** what you could not check.
6. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
7. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review06.md`, and save your own scripts and logs under `review_scratch/`.
