You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 03** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 02. You review; you do not fix.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`51e110bf1981f9761042f5cf0e87c9f0c7c1962e`**, with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). The implementer states it is byte-identical to the implementer's installation (console sha256 `1162803d…52e2`, atmosphere table `75762f67…a85e`). Check this yourself. Pass the console as an absolute path; the harness changes directory.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files. That is allowed. Afterwards, record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run `pytest`, the validators in `toolbox/validators/` with `--out` into `review_scratch/`, `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`, and the T0 checks `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review01.py docs/science/experiments/m3-t0/check_review02.py` (about 2 min). `mutation_check_review02.py` (about 12 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree; you may run it.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records (DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the Review 02 dispositions) are claims to verify, not evidence. Re-execute, write independent checks, and attempt counterexamples, especially against the corrected derivations and the new checks.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3` (merge commit of PR #4, the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5`, `ca84986` (reviewed by Review 01); `bdcaacf` (Review 01 record and the P1–P10 decision matrix).
- **Review 01 correction pass (reviewed by Review 02 at `ead2a84`):** `03e8f63` (corrections), `ead2a84` (validation record); `5548d11` (Review 02 record).
- **Review 02 correction pass (under review now):**
  - `14d98f0`: corrections for M3T0-R2-F1…F3 and IM-1, the new checks and the mutation harness;
  - `51e110b`: the validation record of `14d98f0` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff 5548d11..51e110b`. Run it yourself. **Full T0 diff:** `git diff 86df2c3..51e110b`; the implementer claims nothing outside `docs/` changed.

## Records to read
- **Review 01:** raw output `docs/reviews/raw/M3-T0-codex-review01.md`; prompt `docs/reviews/raw/M3-T0-codex-review01-prompt.md` (contains both I-15 Tech Lead texts verbatim: the T0 authorization, whose scope, constraints and validation requirements are T0's acceptance criteria, and the T0 review instruction); record and dispositions `docs/reviews/M3-T0-review-01.md`.
- **Review 02:** raw output `docs/reviews/raw/M3-T0-codex-review02.md`; prompt `docs/reviews/raw/M3-T0-codex-review02-prompt.md` (contains the Review 01 correction authorization verbatim); reviewer evidence `docs/reviews/raw/M3-T0-codex-review02-evidence/`; record, new findings, the implementer's reproduction and the appended dispositions `docs/reviews/M3-T0-review-02.md`.
- **Decision and assumption registers:** `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; two correction logs at the end), `docs/decisions/requests/` DR-0024…DR-0028, `docs/science/assumptions.md`, `docs/science/validation.md` VAL-0019, `docs/milestones/M3-T0-report.md`, `docs/milestones/M3-T0-decision-matrix.md`.
- **Review 01 findings:** M3T0-F1 (MAJOR, missed-crossing bound), F2 (MAJOR, P1 sufficiency, thresholds, speed proxy), F3 (MINOR, stage numbering), F4 (MINOR, misquoted residual), F5 (NOTE, dependency map vs owner gate). Review 02 judged F1 and F2 PARTIALLY RESOLVED and F3–F5 RESOLVED.
- **Review 02 findings:** M3T0-R2-F1 (MINOR: sampled maxima of U presented as bounds), M3T0-R2-F2 (MINOR: drag envelope at the lower height bound underestimates the co-rotation term), M3T0-R2-F3 (NOTE: `check_review01.py` passes with the sweep and floors zeroed), plus implementer item IM-1 (the DR-0029 P6 "0.99 m" figure had no committed procedure).

## Correction evidence supplied by the implementer (claims to verify)
- **R2-F1** (`t0_termination.py`; DR-0029 P2; VAL-0019): perturbed-motion (J2 + drag) values are relabelled `sampled_estimate_m` with `estimate_kind` "…not a bound"; `bound_m` remains only on two-body rows, labelled certified. The two-body maximisation of g(r) over [r_p, r_a] is now closed-form: endpoints plus the real roots in range of the cubic r³ + (2Ks − 4s)r² + (2sc − 4Ksc)r + 2Ksc² = 0 (c = a − b²/a, K = cos δ_max, s = sma), derived from g'(r) = 0. A between-sample refinement is recorded. DR-0029 states that no certified perturbed bound is derived in T0, that the A5-b recommendation does not rely on one, and that any use needing a guaranteed perturbed magnitude stays blocked.
- **R2-F2** (`t0_termination.py` `drag_envelope`, `stage_lower_heights`, `sufficient_stage_condition`; DR-0029 P1): drag at a stage is bounded by sup over h ≥ L of ρ(h)(s + ω_E(a + h))²/(2B), using |v_rel| ≤ s + ω_E|r| ≤ s + ω_E(a + h); inside each band the product is claimed decreasing when a > 2H, so the supremum is at L or at a band base above L. Monotonicity of the condition in h0 is claimed derived (single root, no scan). Floors: 124 456.69 m (B 25.8, moved 1.1e-7 m), 118 633.51 m (B 100), 111 511.96 m (drag-free). Domain: every committed state with negative two-body energy, any direction, no thrust; lower edge 0 m. An empirical stress test is in `termination` → `sufficient_stage_condition` → `stress`.
- **R2-F3:** `check_review02.py` (38 checks) is claimed to recompute what it protects; two F1 checks in `check_review01.py` were amended for the relabelling. `mutation_check_review02.py`: 16 mutants plus an unmodified control, each mutant with declared detecting checks; claimed 15/15 detected and 1 declared equivalent (dropping the stationary points of the two-body maximisation; justified by a domain scan check, not a proof). Evidence: `docs/reviews/raw/M3-T0-review03-correction-evidence/` (`checks_before_5548d11.log`: 11 of 50 fail at `5548d11`; `checks01_amended_before_bdcaacf.log`: 11 failed, 1 passed at `bdcaacf`; `checks_after.log`: 50 passed; `mutation_check_review02.json`).
- **IM-1:** `t0_axis_ablation.py` → `t0_axis_ablation_results.json` reproduces 0.9856650955520649 m RMS (quadratic-only axis fit) from the committed GMAT report, tolerance 1e-6 m; DR-0029 P6 documents quantity, data, frames, units, sampling, RMS definition, command and tolerance.
- **Validation claims you cannot fully see:** M1 Proof and M2 Proof at `14d98f0` in separate fresh clones; five pinned digests; byte-identical double runs of all T0 experiments including the GMAT harness; CI on `14d98f0`. Logs: `docs/reviews/raw/M3-T0-review03-correction-evidence/`. You cannot access CI; state that.

## Tech Lead's authorization for this pass, verbatim
> # Authorization: M3 T0 — Review 02 Corrections and Independent Review 03
>
> You are authorized to perform a narrowly scoped correction and verification pass on `milestone-3-t0-reference-spike`, followed by one independent Codex Review 03.
>
> **T0 remains BLOCKED. This is not authorization to accept T0, merge, begin T1/T2, or resolve any open decision on my behalf.**
>
> ## 1. Verify starting state
>
> Confirm:
>
> - Branch: `milestone-3-t0-reference-spike`
> - Expected HEAD: `5548d11`
> - Clean working tree
> - Review 02 verdict: `REQUEST_CHANGES`
> - All three new findings remain unresolved
> - No changes outside the authorized T0 scope
>
> If the repository differs materially from this checkpoint, stop and report the discrepancy.
>
> Preserve all M1/M2 baselines, thresholds, goldens, contracts, reference data, and validation semantics.
>
> ## 2. Correct R2-F1 — Perturbed-motion bound
>
> The current numerical maximum over sampled states is not a mathematically certified upper bound.
>
> Required actions:
>
> 1. Preserve the valid theorem and the existing analytical two-body bound.
> 2. Distinguish sampled numerical maxima from certified global bounds.
> 3. Either establish a rigorous bound covering the complete declared perturbation domain or explicitly classify the sampled result as empirical and remove any unsupported guarantee.
> 4. If a rigorous bound is necessary for the proposed decision rule and cannot be established, leave that rule blocked.
> 5. Add adversarial tests involving between-sample extrema, phase variation, and refinement.
>
> Do not introduce an arbitrary safety multiplier and describe it as a proof.
>
> ## 3. Correct R2-F2 — Drag-stage condition
>
> Correct the co-rotation-speed bound so it uses the appropriate maximum radius over the declared stage domain, not the lower-height boundary.
>
> Required actions:
>
> 1. Derive the corrected condition from the documented physical assumptions.
> 2. Check the supplied counterexample.
> 3. Test the corrected condition against near-escape, retrograde, and other boundary states.
> 4. Verify that the stated floors and guarantees actually follow from the corrected condition.
> 5. Explicitly document domain restrictions and any remaining uncertainty.
>
> Do not silently narrow the supported domain to make the condition pass.
>
> ## 4. Correct R2-F3 — Regression verification
>
> The existing 12 checks can pass when critical numerical evidence has been replaced by zero.
>
> Replace or strengthen the verification so that it independently recomputes the quantities supporting the relevant claims.
>
> Requirements:
>
> - Tests must fail when the sampled sweep results are corrupted.
> - Tests must fail when the drag floors are corrupted.
> - Include mutation tests for both cases.
> - Check calculation provenance and units.
> - Avoid self-referential tests that merely compare copied values.
> - Keep deterministic, reproducible outputs.
>
> Demonstrate red-before/green-after behavior for the relevant mutations.
>
> ## 5. Resolve IM-1 — P6 reproducibility
>
> The reported 0.98567 m RMS figure must have a documented, executable reproduction procedure.
>
> Determine and record:
>
> - The precise physical quantity being measured.
> - The reference trajectory and comparison trajectory.
> - The coordinate frame and units.
> - The RMS definition and sampling interval.
> - The source of the underlying data.
> - The exact command or procedure required to reproduce the result.
> - The expected result and an appropriately justified numerical tolerance.
>
> If the result cannot be independently reproduced, mark it unverified and keep DR-0028 P6(b) open.
>
> Do not convert the reproduced number into an approved engineering threshold without my decision.
>
> ## 6. Preserve decision authority
>
> DR-0029 P1–P10 remain OPEN.
>
> DR-0028 P6(b) remains OPEN.
>
> The unexplained GMAT geodetic-drag discrepancy remains an explicit escalation.
>
> Do not infer my approval from a recommendation, a passing test, or a Codex verdict.
>
> Update decision records only with verified evidence and clearly identified recommendations.
>
> ## 7. Validation
>
> After corrections:
>
> 1. Run focused regression tests.
> 2. Run the mutation tests.
> 3. Run the complete relevant test suite.
> 4. Run the full M1 and M2 Proof procedures in clean environments.
> 5. Verify pinned reference digests and tracked-file integrity.
> 6. Confirm no unauthorized changes to numerical baselines or validation semantics.
> 7. Commit and push the corrections.
> 8. Verify all required CI jobs are green.
>
> Record commands, results, commits, and evidence locations.
>
> A passing CI result is necessary but not sufficient for acceptance.
>
> ## 8. Independent Codex Review 03
>
> After validation, authorize exactly one independent Codex review.
>
> Provide Codex with:
>
> - The complete Review 01 and Review 02 records.
> - Original findings and dispositions.
> - The correction diff.
> - Relevant mathematical derivations.
> - Reproduction commands and evidence.
> - Mutation-test results.
> - Decision and assumption registers.
>
> Ask Codex to independently evaluate:
>
> 1. Whether R2-F1 is fully resolved.
> 2. Whether R2-F2 is fully resolved.
> 3. Whether R2-F3 is fully resolved.
> 4. Whether IM-1 is reproducible and correctly documented.
> 5. Whether previous findings remain resolved.
> 6. Whether the corrections introduce new defects.
> 7. Whether mathematical guarantees are stronger than the evidence supports.
> 8. Whether any unauthorized decision or scope change occurred.
>
> Do not request a favorable verdict. Require concrete evidence for findings and an explicit `PASS` or `REQUEST_CHANGES` verdict.
>
> Preserve the raw review output and record all findings without rewriting their substance.
>
> ## 9. Stop conditions
>
> If Review 03 returns `REQUEST_CHANGES`:
>
> - Record and independently reproduce each finding where feasible.
> - Do not automatically correct the new findings.
> - Do not start Review 04.
> - Do not declare T0 accepted.
> - Stop and request my authorization.
>
> If Review 03 returns unconditional `PASS`:
>
> - Prepare a T0 acceptance candidate report.
> - Include the final evidence matrix, outstanding decisions, limitations, and remaining risks.
> - Stop for my explicit acceptance.
>
> In either case:
>
> - Do not merge.
> - Do not begin T1 or T2.
> - Do not approve DR-0029 P1–P10 or DR-0028 P6(b).
> - Do not modify branch protection settings.
>
> ## 10. Final checkpoint report
>
> Report:
>
> 1. Branch, HEAD, commits, and working-tree status.
> 2. R2-F1, R2-F2, R2-F3, and IM-1 dispositions.
> 3. Mathematical guarantees versus empirical observations.
> 4. Regression and mutation-test results.
> 5. M1/M2 Proof results and digest verification.
> 6. CI results.
> 7. Independent Codex Review 03 verdict.
> 8. Remaining open decisions and escalations.
> 9. Whether T0 is eligible for my acceptance review.
> 10. The exact authorization required next.
>
> **Proceed with these corrections and Review 03 only. Stop at the next checkpoint.**

## What to review
Evaluate each of the following independently, with your own execution or computation wherever possible:
1. **Whether M3T0-R2-F1 is fully resolved:** are certified bounds and sampled estimates correctly separated in code, result files and every record; is the closed-form two-body maximisation correct (derive g'(r) yourself; check root selection and the domain r_p ≤ r ≤ r_a); is any guarantee for perturbed motion still stated or implied; is the claim that A5-b does not need a perturbed bound accurate.
2. **Whether M3T0-R2-F2 is fully resolved:** is the corrected drag envelope a valid upper bound for every point at height ≥ L with speed ≤ s (including stages above h0, band jumps, the top band, and the floating-point evaluation of heights); is the per-band monotonicity argument correct; is the monotonicity of the condition in h0 correct; do the stated floors follow; was the domain narrowed. Attempt counterexamples (near-escape, retrograde equatorial, straight-down, polar, states exactly at the floor).
3. **Whether M3T0-R2-F3 is fully resolved:** do the checks recompute rather than read the protected quantities; do they fail for corrupted sweep results and corrupted floors; is the mutation harness's classification sound (could a mutant be counted as detected for an unrelated reason; is the declared equivalent mutant truly equivalent on the declared domain, and is declaring it acceptable); are there corruptions that still pass; are there self-referential or vacuous checks; are provenance and unit checks meaningful; are outputs deterministic.
4. **Whether IM-1 is reproducible and correctly documented:** reproduce the 0.986 m RMS independently; check the stated quantity, frames, units, sampling, RMS definition, data provenance, command and the justification of the 1e-6 m tolerance; check it is not presented as a threshold.
5. **Whether the previous findings remain resolved:** M3T0-F1…F5 (Review 01) including those Review 02 judged PARTIALLY RESOLVED, now that R2-F1/F2 are corrected.
6. **Whether the corrections introduce new defects** (scientific, numerical, reference-frame, test-validity, record-correctness: every number quoted in DR-0029, VAL-0019, the T0 report, the decision matrix, the README and the Review 02 dispositions against the committed result files).
7. **Whether any mathematical guarantee is stronger than the evidence supports** (anything called derived, certified, exact, guaranteed or bounded).
8. **Whether any unauthorized decision or scope change occurred:** no production change; no change to approved physics, constants, frames, thresholds, goldens, references, M1/M2 contracts or validation semantics; no new dependency; nothing beyond T0; no DR-0029 item (P1–P10) or DR-0028 P6 (b) treated as decided; no recommendation changed without disclosure; the geodetic-drag discrepancy still escalated.
Also re-run the Python experiments (and the GMAT harness where practical) and compare outputs byte for byte, and re-check the five pinned digests.

## Required output
1. **Ledger:** every command you ran with its key output; every result file you inspected; for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R2-F1, R2-F2, R2-F3 and IM-1, and for M3T0-F1…F5: each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence.
3. **New findings.** Number them `M3T0-R3-F1`, `M3T0-R3-F2`, …. Each gives severity (BLOCKER, MAJOR, MINOR or NOTE); file and line references; concrete evidence or a reproducible counterexample; a recommended correction; and **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**. Do not report a finding without concrete evidence.
4. **Verification limits:** what you could not check.
5. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any finding in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
6. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review03.md`.
