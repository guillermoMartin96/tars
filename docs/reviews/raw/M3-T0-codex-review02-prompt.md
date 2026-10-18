You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 02** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of a correction pass made after Review 01. You review; you do not fix.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`ead2a8417edfbb0855034098c8d85566e3fe7938`**, with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). The implementer states it is byte-identical to the implementer's installation (console sha256 `1162803d…52e2`, atmosphere table `75762f67…a85e`). Check this yourself. Pass the console as an absolute path; the harness changes directory.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files. That is allowed. Afterwards, record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run `pytest`, the validators in `toolbox/validators/` with `--out` into `review_scratch/`, `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`, and the T0 checks `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review01.py`.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records (DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, the Review 01 dispositions) are claims to verify, not evidence. Re-execute, write independent checks, and attempt counterexamples, especially against the new derivations.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 before the correction (reviewed by Review 01 at `ca84986`, then recorded):**
  - `3729ffd`, `294e1f5`, `ca84986`;
  - `bdcaacf`: the Review 01 record and the P1–P10 decision matrix.
- **Correction pass (under review now):**
  - `03e8f63`: corrections for M3T0-F1…F4 and the regression checks;
  - `ead2a84`: the validation record of `03e8f63` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff bdcaacf..ead2a84`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..ead2a84`. The implementer claims nothing outside `docs/` changed.

## Review 01 (the findings to evaluate)
- **Raw output:** `docs/reviews/raw/M3-T0-codex-review01.md`.
- **Prompt:** `docs/reviews/raw/M3-T0-codex-review01-prompt.md`. It contains both I-15 Tech Lead instruction texts verbatim: the T0 authorization (its scope, constraints and validation requirements are T0's acceptance criteria) and the T0 review instruction.
- **Reviewer evidence:** `docs/reviews/raw/M3-T0-codex-review01-evidence/` (Python files stored as `*.py.txt`).
- **Record and the updated disposition matrix:** `docs/reviews/M3-T0-review-01.md`. Review 01's original findings table is preserved; the dispositions are appended at the end.
- **Findings:**
  - M3T0-F1 (MAJOR): the missed-crossing "bound";
  - M3T0-F2 (MAJOR): the sufficiency of P1, the grid thresholds and the speed proxy;
  - M3T0-F3 (MINOR): the stage numbering;
  - M3T0-F4 (MINOR): the misquoted residual;
  - M3T0-F5 (NOTE): the dependency map against the owner's gate.
- **Disclosed and not corrected:** implementer item IM-1 (the unsupported "0.99 m" quadratic-fit figure in DR-0029 P6). The implementer states it is outside the authorized correction scope (the two MAJOR and two MINOR reviewer findings) and left it unchanged. Assess it as you see fit.

## Correction evidence supplied by the implementer (claims to verify)
- **New experiment:** `docs/science/experiments/m3-t0/t0_termination.py` → `t0_termination_results.json`. It contains:
  - a missed-crossing bound: dip ≤ (dt²/8) · sup max(ḧ, 0), and outside the ellipsoid ḧ ≤ n̂·a + |v_t|²/(h + b²/a);
  - a two-body bound over a whole orbit, plus worst-case constructions and a sweep (9 orbits × two-body / J2 + drag × 40 sampling phases);
  - exact drag-stiffness thresholds with the circular-speed proxy v_c and with V_b = √(2μ/(b + h)) + ω_E(a + h), claimed to be a bound on |v_rel| for every bound state;
  - the reviewer's P1 counterexamples;
  - a derived sufficient stage-domain condition (1-Lipschitz height; RK4 stage positions);
  - the stage order.
- **Changed experiment:** `t0_decay.py` relabels its missed-crossing output as a single-phase measurement and drops the "analytic bound". The implementer states its other outputs are unchanged; check `git diff bdcaacf..ead2a84 -- docs/science/experiments/m3-t0/t0_decay_results.json`.
- **Regression checks:** `docs/science/experiments/m3-t0/check_review01.py` (12 checks).
  - Claimed: 11 fail and 1 passes at `bdcaacf` (evidence `checks_before_bdcaacf.log`), and all 12 pass at `03e8f63`.
  - You can test the "fails before" claim yourself, for example in a scratch `git worktree` or an archive of `bdcaacf` under `review_scratch/`, with this file copied in.
  - Assess whether the checks test the underlying defects or only wording.
- **Further evidence:** `docs/reviews/raw/M3-T0-review02-correction-evidence/` (Hessian check of the curvature bound, a mutation that drops the ellipsoid curvature, Proof logs, digests, double-run reproducibility).
- **Validation claims you cannot fully see:**
  - M1 Proof 9/9 and M2 Proof 20/20 at `03e8f63` in separate fresh clones (pytest 1185 passed; m2_proof 228/228);
  - five pinned digests match;
  - all 85 tracked T0 experiment files reproduce byte-identically on two runs;
  - CI all four jobs successful on `03e8f63` (run 39168509344) and on `ead2a84` (run 39173057402).
  - You cannot access CI; state that.

## Tech Lead's correction authorization, verbatim
> # TARS M3 T0 — Review 01 Correction Authorization
> 
> I authorize a bounded correction pass for the four verified findings from Codex Review 01, followed by independent Codex Review 02.
> 
> **T0 remains unaccepted. T1 and T2 remain unauthorized.**
> 
> ## 1. Preflight
> 
> Read the following files completely:
> 
> - `docs/milestones/M3-T0-report.md`
> - `docs/milestones/M3-T0-decision-matrix.md`
> - `docs/reviews/M3-T0-review-01.md`
> - The original Codex Review 01 prompt and raw output, if available
> - Relevant accepted M3 planning decisions and validation contracts
> 
> Pay particular attention to item 12 of the checkpoint report.
> 
> Verify that the branch is `milestone-3-t0-reference-spike`, HEAD is `bdcaacf`, and the worktree is clean.
> 
> If the report requires a separate scientific or architectural decision before a finding can be corrected, stop and present that decision rather than choosing a default.
> 
> ## 2. Correction scope
> 
> For each of the two MAJOR and two MINOR findings:
> 
> 1. Identify the exact root cause.
> 2. Reproduce the finding against the current checkpoint.
> 3. Develop the smallest scientifically valid correction.
> 4. Add targeted regression coverage that fails before the correction and passes afterward, where practical.
> 5. Verify that the correction addresses the underlying defect rather than merely satisfying the existing test.
> 6. Preserve the original review finding and append its disposition.
> 
> Do not silently expand T0 scope.
> 
> Do not alter approved physics assumptions, constants, reference frames, thresholds, or M1/M2 validation contracts.
> 
> If a correction requires such a change, raise a decision request and stop.
> 
> ## 3. Validation
> 
> After implementing the authorized corrections:
> 
> - Run the targeted T0 tests.
> - Run the established M1 and M2 Proof suites.
> - Verify all five pinned reference digests.
> - Confirm that production code and protected reference files remain unchanged.
> - Confirm that all T0 experimental artifacts are reproducible.
> - Commit and push the correction checkpoint.
> - Wait for all four CI jobs to finish and verify their results.
> 
> Do not treat pending CI as success.
> 
> ## 4. Independent Codex Review 02
> 
> After validation passes, request a fresh independent Codex review.
> 
> Provide Codex with:
> 
> - The original Review 01 findings and raw output.
> - The complete correction diff.
> - Reproduction evidence and regression tests.
> - The updated finding disposition matrix.
> - The T0 scientific assumptions and acceptance criteria.
> - Relevant validation and CI evidence.
> 
> Require Codex to evaluate each Review 01 finding as RESOLVED, PARTIALLY RESOLVED, or NOT RESOLVED.
> 
> Also require an independent examination for new defects, especially scientific correctness, numerical behavior, reference-frame consistency, and test validity.
> 
> Do not instruct Codex to return PASS.
> 
> ## 5. Mandatory stop
> 
> If Review 02 returns REQUEST_CHANGES:
> 
> - Record every finding.
> - Independently reproduce new findings where practical.
> - Preserve the complete review output.
> - Do not automatically fix the new findings.
> - Do not begin Review 03.
> - Stop and request authorization.
> 
> If Review 02 returns an unconditional PASS, prepare a T0 acceptance report and stop for my approval.
> 
> In either case, do not merge T0, begin T1 or T2, or approve outstanding decision requests.
> 
> ## 6. Final report
> 
> Report:
> 
> 1. Branch and final commit.
> 2. Each original finding and its disposition.
> 3. Exact corrections and regression evidence.
> 4. M1/M2 Proof results.
> 5. Five pinned digest comparisons.
> 6. CI results and links.
> 7. Codex Review 02 verdict.
> 8. Any new findings.
> 9. Outstanding decision requests.
> 10. T0 READY or BLOCKED recommendation.
> 
> Proceed only within these boundaries.

## What to review
1. **Evaluate each Review 01 finding** (M3T0-F1…F5) as exactly one of **RESOLVED**, **PARTIALLY RESOLVED** or **NOT RESOLVED**, with your own evidence. Check that the correction addresses the root cause and not only the wording, and that the original finding text and record were preserved.
2. **Examine the correction independently for new defects**, especially:
   - **Scientific correctness of the new derivations:**
     - the dip bound and its convexity argument;
     - the Hessian bound for the distance to the WGS 84 ellipsoid (is b²/a the right extreme radius of curvature; is the bound valid for every exterior point);
     - the normal-angle term;
     - the two-body domain bound (is the maximisation over r correct);
     - V_b as a bound on |v_rel| (b + h ≤ |r| ≤ a + h; negative energy);
     - the λ = ρ|v_rel|/B stiffness interpretation;
     - the J2 factor 3 J2 (a/r)²;
     - the sufficient stage-domain condition (stage positions, Lipschitz argument, acceleration and density bounds, monotonicity in h0).
   - **Numerical behaviour:** dense-output sampling and refinement in the sweep; whether the sweep could miss a worst case; threshold root finding across band boundaries; determinism.
   - **Reference-frame consistency:** the J-ax-1 frame (+Z axis for J2, the ellipsoid and the atmosphere rotation) is used throughout; no rotating frame or other pole model is substituted.
   - **Test validity:**
     - whether `check_review01.py` would detect a reintroduction of each defect;
     - whether its record-wording checks are meaningful;
     - whether it can pass vacuously;
     - whether it really fails at `bdcaacf`.
   - **Record correctness:** every number now quoted in DR-0029, VAL-0019, the T0 report, the decision matrix and the README against the committed result files. Look for misquotes, overstated claims, defaults presented as decisions, changed option identifiers, or a DR-0029 item treated as decided.
3. **Scope:** no production change, no change to approved physics, constants, frames, thresholds, goldens, references or M1/M2 contracts, no new dependency, and nothing beyond T0. Check whether the correction silently expanded T0's scope, for example by changing a DR-0029 recommendation.
4. **Re-run** the Python experiments, and the GMAT harness where practical, and compare outputs byte for byte. Re-check the five pinned digests.

## Required output
1. **Ledger:**
   - every command you ran, with its key output;
   - every result file you inspected;
   - for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Finding-by-finding resolution table** for M3T0-F1…F5: RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with the evidence.
3. **New findings.** Number them `M3T0-R2-F1`, `M3T0-R2-F2`, …. Each gives:
   - severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.
4. **Verification limits:** what you could not check.
5. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`.
   - Any BLOCKER, MAJOR or MINOR finding, or any Review 01 finding that is not RESOLVED, requires REQUEST_CHANGES.
   - NOTEs alone permit PASS.
6. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review02.md`.
