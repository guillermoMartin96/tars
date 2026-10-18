You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 01**, the independent review of Task T0 (the reference-configuration spike) of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag). You review; you do not fix.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`ca84986595fe904883a37f13bf9be64ad75a35fc`**, with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). It is byte-identical to the implementer's: console sha256 `1162803d…52e2`, atmosphere table `75762f67…a85e`. Check this yourself. You may run it.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files (`docs/science/experiments/m3-t0/*_results.json` and `gmat_runs/`). That is allowed: afterwards, record `git status --porcelain` and `git diff --stat` (the implementer claims both are empty), then restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh` here; they write into `proof/records/evidence/`. You may run `pytest`, the validators in `toolbox/validators/` with `--out` pointing into `review_scratch/`, and `toolbox/scripts/gmat_m1.py compare` / `gmat_m2.py compare`.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** Inspect the actual files, re-execute experiments where practical, write your own independent checks and attempt counterexamples. The implementer's records (VAL-0019, DR-0029, the T0 report, the experiment README) are claims to verify, not evidence.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed.

## Commits under review
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline; parents `d92ab89`, `93e356a`).
- **T0 commits:**
  - `3729ffd`: the spike (`docs/science/experiments/m3-t0/`: code, results, GMAT runs, a copy of the pinned atmosphere table);
  - `294e1f5`: DR-0029, VAL-0019, append-only status amendments and DR pointer notes, README, a spike fix;
  - `ca84986`: the checkpoint report `docs/milestones/M3-T0-report.md`.
- **Authoritative diff:** `git diff 86df2c3..ca84986`. Run it yourself. The implementer claims nothing outside `docs/` changed.

## Implementer's claims to verify, not to trust
- CI: four successful jobs (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`) on `294e1f5` (run 39138140001) and on `ca84986` (run 39144298212). You cannot access CI; state that.
- The full local M1 Proof (9 steps) and M2 Proof (20 steps) passed at `294e1f5` and at the baseline `86df2c3`: pytest 1185 passed, m2_proof 228/228. You cannot see those runs; you may run `pytest` and the validators yourself.
- The five pinned digests in `src/tars/validation/approved_digests.py` match their files.
- Every T0 experiment reruns byte-identically.

## Documents to read
- **Planning baseline and decisions:**
  - `docs/milestones/M3-proposal.md`, `M3-decision-matrix.md`, `M3-baseline-and-impact.md`;
  - DR-0024, DR-0025, DR-0026, DR-0027, DR-0028 and DR-0029 in `docs/decisions/requests/`;
  - ADR-0009;
  - SCI-0013…0017 in `docs/science/assumptions.md`;
  - VAL-0018 and VAL-0019 in `docs/science/validation.md`.
- **T0:**
  - `docs/milestones/M3-T0-report.md`;
  - `docs/science/experiments/m3-t0/` (README, scripts, results, `gmat_runs/`, `data/`).
- **Instruction history:**
  - I-1…I-12 are reproduced verbatim in `docs/reviews/raw/M3-planning-codex-review13-prompt.md`;
  - I-13 is summarised in the decision matrix;
  - I-14 (the planning-merge authorization) is not in the repository;
  - both I-15 texts are reproduced verbatim below.

## Tech Lead instruction I-15 (T0 authorization), verbatim as received by the implementer (the copy received ended at the start of §8)
```text
# TARS — M3 T0 Reference-Configuration Spike Authorization

You are the lead spacecraft simulation engineer responsible for executing Milestone 3, Task T0, under the accepted M3 planning baseline.

## 1. Authorization

I explicitly authorize **M3 T0 only**.

The M3 planning baseline was merged through PR #4:

- Merge commit: `86df2c3ff189db26f42bd273b6fe71de502c51a3`
- All four CI jobs passed.
- M1/M2 contracts, reference files, goldens, and numerical thresholds remain unchanged.

Create `milestone-3-t0-reference-spike` from the verified merge commit on `main`.

Do not begin T1, T2, or any subsequent M3 implementation task.

## 2. Preflight and repository hygiene

Before changing anything:

1. Fetch the latest remote state and verify `origin/main` contains the accepted merge commit.
2. Confirm the worktree is clean.
3. Check existing worktrees and avoid modifying the M3 planning worktree.
4. Read the merged M3 plan, decision registers, DR-0024 through DR-0028, review records, verification contracts, and T0 acceptance criteria.
5. Establish the existing M1/M2 validation baseline.
6. Confirm that no deferred decision has been silently treated as approved.

If repository evidence contradicts this authorization, stop and report the discrepancy.

Use a separate worktree for T0 if that provides better isolation.

## 3. Administrative corrections

Prepare a minimal, append-only documentation amendment recording that PR #4 was merged at `86df2c3`.

Update stale planning-merge status entries without rewriting historical decisions.

Do not modify the accepted technical decisions or retroactively alter their evidence.

Inspect GitHub branch protection and rulesets. Report the absence of enforcement and recommend appropriate protections, including required CI checks and PR reviews.

Do not change repository settings without separate authorization.

## 4. T0 technical scope

Implement the minimum isolated experimental code necessary to validate reference configurations and investigate the M3 planning assumptions.

### A. GMAT reference configurations

- Develop executable reference configurations for the planned J2 and atmospheric-drag cases.
- Verify that each GMAT configuration implements the intended physical assumptions.
- Identify configuration limitations and ambiguities.
- Reproduce relevant planning measurements where possible.
- Preserve provenance and reproducibility.

### B. Atmosphere and drag

- Exercise every atmospheric table band boundary.
- Characterize discontinuities and numerical sensitivity.
- Investigate RK4 intermediate-stage behavior near the lower atmosphere boundary.
- Validate geodetic-height calculations against independently justified test points.
- Verify atmosphere-relative velocity and its coordinate-frame interpretation.
- Investigate unsupported altitudes, impact conditions, and event-crossing behavior.

### C. Reference-frame consistency

Use the approved DR-0028 J-ax-1 non-rotating Earth-axis-aligned approximation.

Explicitly document its limitations.

Verify that reference configurations, initial states, force models, and comparisons use consistent frame conventions.

Do not silently substitute a rotating Earth-fixed frame or a different pole model.

### D. Regression behavior

With M3 perturbations disabled, demonstrate that the experimental configurations remain consistent with the applicable M1/M2 baselines.

Do not relax tolerances to obtain passing results.

## 5. Decision requests

Prepare evidence-backed proposals for the following unresolved items:

- DR-0027: A-4, A-5, A-6, A-s, B-4.
- Q-G2-1: GMAT exact-configuration methodology.
- Q-G2-5: Reference mission selection.
- Q-G2-7: Geodetic-height test points.
- DR-0024 Q9: Drag coefficient, reference area, initial mass, and associated initial-state parameters.

For each proposal, provide alternatives, evidence, numerical implications, risks, and a recommendation.

**Do not approve or close these decisions on my behalf.**

If additional scientific or architectural authority is required, open a new decision request and stop at the relevant boundary.

## 6. Engineering constraints

- Keep experimental code isolated from production architecture.
- Do not modify `src/`, `proof/`, pinned references, goldens, or approved contracts.
- Do not change numerical thresholds.
- Do not regenerate M1/M2 reference outputs.
- Preserve deterministic execution and reproducible inputs.
- Prefer existing dependencies and tooling.
- Do not introduce new dependencies or languages without justification and approval.
- Do not begin a Rust or C migration. Embedded/firmware architecture remains a separate research and decision concern.

## 7. Validation and checkpoints

Run the applicable M1 Proof and M2 Proof suites, including their established 9-step and 20-step procedures.

Verify:

1. All five pinned digests remain unchanged.
2. M1/M2 numerical behavior is preserved.
3. The T0 experiments are reproducible.
4. Reference configurations are traceable to documented assumptions.
5. All four CI jobs pass on checkpoint commits.
6. No unauthorized production changes are present.

Record commands, tool versions, configuration hashes, results, and deviations.

Do not describe a test as passed unless it was executed and its result verified.

## 8. Independent Codex review

After completing the experimental work and validation:
```

## Tech Lead instruction "TARS M3 — Instruction I-15: T0 Independent Review" (the completed §8), verbatim
```text
TARS M3 — Instruction I-15: T0 Independent Review

1. Authorization

You are authorized to complete the missing §8 independent Codex review for T0 on branch milestone-3-t0-reference-spike.

This authorization covers review preparation, evidence verification, independent review execution, and recording findings.

It does not authorize T0 acceptance, T1, T2, production implementation, or resolution of owner-level physics decisions.

2. Establish the checkpoint baseline

Verify:

* Branch HEAD is ca84986.
* Both 294e1f5 and ca84986 have four successful CI jobs.
* The full local M1/M2 Proof passed at 294e1f5.
* The worktree is clean before review.
* No prohibited production changes, threshold changes, golden regeneration, or reference-baseline modifications occurred.
* All five previously pinned digests remain unchanged.

If any verification fails, document the discrepancy and stop.

3. Prepare the independent Codex review

Provide Codex with the accepted M3 planning baseline, the T0 authorization, DR-0024 through DR-0029, the relevant reference-spike artifacts, experiment scripts, results, and validation evidence.

Codex must independently examine the actual repository and evidence rather than accepting Claude's summary as proof.

Require the review to address:

1. Scope compliance: T0 stayed within the authorized experimental/reference-spike boundary.
2. Physics correctness: Equations, constants, units, coordinate frames, orbital assumptions, and numerical methods are consistent.
3. GMAT/reference fidelity: Comparisons use equivalent initial conditions, epochs, reference frames, constants, and modeled forces.
4. Atmospheric modeling: Published density bands, boundaries, discontinuities, and interpolation assumptions are represented accurately.
5. Geodetic and Earth-axis conventions: Implementations and documentation respect the accepted DR-0024/DR-0028 decisions.
6. Experiment reproducibility: Inputs, scripts, commands, results, environment, and provenance allow independent reproduction.
7. Verification quality: Tests detect meaningful errors rather than merely reproducing implementation assumptions.
8. M1/M2 regression protection: Existing contracts, thresholds, references, and goldens are preserved.
9. Decision completeness: DR-0029 P1–P10 accurately reflect the experimental evidence, alternatives, uncertainties, and downstream dependencies.
10. T1/T2 readiness: Recommendations correctly distinguish established evidence from unresolved owner decisions.

For each finding, require a stable identifier, severity (BLOCKER, MAJOR, MINOR, NOTE), file/line references, evidence or a reproducible counterexample, and a recommended correction.

Codex must explicitly distinguish verified findings from concerns it could not independently reproduce.

4. Review execution

Run one independent Codex review against the pinned checkpoint.

Where practical, independently execute the relevant experiments and tests.

Record exactly which commands Codex ran, which results it inspected, and which conclusions rely on documentation rather than direct execution.

Do not silently modify experimental results to make the review pass.

5. Findings and stop conditions

If Codex returns REQUEST_CHANGES:

* Record every finding.
* Verify the reported evidence where feasible.
* Do not automatically correct findings.
* Do not start another review round.
* Do not declare T0 accepted.
* Stop and request authorization for the proposed corrections.

If Codex returns an unconditional PASS:

* Preserve the complete review output.
* Verify the reviewed commit and evidence are unchanged.
* Prepare the T0 acceptance report.
* Stop for owner acceptance.

An unconditional PASS does not itself authorize T1.

6. DR-0029 decision preparation

Do not assume P1–P10 are approved.

Prepare a decision matrix containing, for each proposal:

* Exact question and available options.
* Claude's recommended option.
* Supporting experiment results and evidence references.
* Quantitative tradeoffs, where available.
* Assumptions, limitations, and risks.
* Consequences for T1 and T2.
* Whether the decision is reversible without invalidating accepted reference evidence.

Preserve existing option identifiers and wording.

Do not invent default values for unresolved proposals.

Explicitly identify P10 as a prerequisite for T1 and P1–P10 as prerequisites for T2, consistent with the reported dependency structure.

Also reconcile any remaining dependencies from DR-0027, DR-0024, and DR-0025. Do not treat a DR-0029 decision as implicitly resolving a different decision request.

7. Final checkpoint report

Return:

1. Exact branch and HEAD SHA.
2. Worktree and scope-verification status.
3. CI results for both checkpoint commits.
4. M1/M2 Proof and digest-verification results.
5. Independent Codex verdict.
6. Findings and dispositions.
7. Experiment reproducibility assessment.
8. DR-0029 P1–P10 decision matrix.
9. T0 acceptance recommendation: READY or BLOCKED.
10. T1 readiness recommendation: READY or BLOCKED, with reasons.
11. T2 blockers and outstanding owner decisions.
12. Exact actions requiring my authorization.

Do not merge, begin T1, begin T2, or modify production architecture.

Stop at the checkpoint and wait for my decisions.
```

## What to review
Address each of the ten areas in I-15 (review) §3, items 1–10. For each one, state what you checked, how you checked it (your own commands or code), and your conclusion. In particular, attempt the following, where practical:
- Re-run the Python experiments, and the GMAT harness with the private GMAT copy, and compare outputs byte for byte.
- Check the spike model's equations and constants against DR-0024's Resolution, DR-0027 B-1 and DR-0028 J-ax-1, writing your own independent code where possible (J2 acceleration, density band rule, geodetic height, v_rel).
- Check that the GMAT configurations (`gmat_runs/*.script`, generated `.cof` and table files) represent the same physics, initial state, epoch, frame and constants as the spike they are compared with. Check that the identity regression really is byte identity against `toolbox/references/gmat/`.
- Check the axis-recovery method (two non-coplanar orbits; diurnal basis) and the attribution claims: J2 to 0.076 mm, the interval sensitivity, and the escalated geodetic-drag item.
- Check that the atmosphere results represent the pinned table: jumps, slope changes, band selection at bases, extrapolation, the below-zero behaviour, and the density-probe method and its bias.
- Check the RK4 stage, stiffness, crossing-location and missed-crossing analyses for correctness, including the derived formulas.
- Check whether the T0 checks would detect meaningful errors. For example: a wrong sign or axis in J2, v instead of v_rel, a wrong band rule, a km/m error, spherical instead of geodetic height. Do the comparisons actually discriminate?
- Check that DR-0029 P1–P10 state the evidence correctly. Look for misquoted numbers, unsupported claims, missing alternatives, defaults presented as decisions, and dependencies stated wrongly.
  - In particular: DR-0029 says T2 is blocked on P1–P5, P8 and P9, and T4/T5 need P6 and P7. The Tech Lead's §6 asks for P1–P10 to be identified as prerequisites for T2. Assess the dependency structure on the evidence.
- Check that the append-only amendments in DR-0024/0025/0027/0028, the decision matrix, the proposal and the milestones README did not alter accepted decisions or their evidence (`git diff 86df2c3..ca84986 -- docs/decisions docs/milestones docs/science/validation.md docs/science/assumptions.md`).
- Check scope: no production change, no threshold change, no golden or reference regeneration, no new dependency, and nothing beyond T0 (no T1/T2 implementation).

## Required output
1. **Ledger:**
   - every command you ran, with its key output;
   - every result file you inspected;
   - for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Area-by-area assessment** (items 1–10).
3. **Findings.** Number them `M3T0-F1`, `M3T0-F2`, …. Each finding gives:
   - severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - evidence or a reproducible counterexample (the edit or input, the command, and its output);
   - a recommended correction;
   - **VERIFIED** (you reproduced it) or **NOT INDEPENDENTLY REPRODUCED** (a concern you could not confirm).
4. **Verification limits:** what you could not check (for example CI, the Proof wrapper runs, network sources).
5. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding requires REQUEST_CHANGES. NOTEs alone permit PASS.
6. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review01.md`.
