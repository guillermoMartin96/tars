You are an independent reviewer from a separate provider. You did not write any file under review. This is a **documentation-only independent review** of the TARS spacecraft simulator's Milestone 3 "T2 decision readiness" planning package, prepared under the Tech Lead's Authorization I-23 (verbatim at the end). The implementer's documents are claims, not evidence: verify them against the repository and against mathematics.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`5ee6a6a2d78ef425687ba164bb32033947ee7c01`** (branch `milestone-3-t2-decision-readiness`), with git metadata. `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`, the parent of the reviewed commit.
- A locked Python environment is in `./.venv` (numpy, scipy). Use `.venv/bin/python`. **The network is not available.**
- **Do not modify tracked files.** Put scratch files and your own scripts only under `./review_scratch/`, which is excluded from git. Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may read any file, run `ruff check .`, `ruff format --check .`, read the committed T0/T1 results JSON files, run `docs/science/experiments/m3-t0/check_review0*.py` if useful, and write your own computations. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo them; you cannot reach the network):** I-23 §2 baseline verification (`git fetch`, `origin/main` = `fc50aed`, clean checkout, CI run 40053187537 on `main` all four jobs success, no branch protection) and the creation and push of the planning branch. Treat the CI and remote facts as claims you cannot authenticate; check them only for internal consistency.
- **Decision boundaries.** You review; you do not decide. Do not record any DR item as approved: DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), Q-G2-4, the T2 gate. Do not fix anything.

## What is under review (`git diff fc50aed..5ee6a6a`)
New:
1. `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md` (I-23 §9 B): decision matrix, readiness classification, corroboration C-1…C-7, implementer findings N-1…N-7, individual assessments, proposed analyses X-1…X-4.
2. `docs/milestones/M3-T2-decision-readiness-report.md` (§9 A).
3. `docs/milestones/M3-T2-validation-strategy.md` (§9 C).
4. `docs/milestones/M3-T2-authorization-packet.md` (§9 D; must be DRAFT — NOT AUTHORIZED), with design questions DQ-1…DQ-6.
5. `docs/milestones/M3-open-issues-register.md` (§9 E).
Append-only edits: `docs/reviews/M3-T1-acceptance-dossier.md` and `docs/milestones/M3-T1-report.md` (I-22 merge record), `docs/milestones/M3-decision-matrix.md`, `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (pointer), `docs/milestones/README.md` (one row extended).

Authoritative sources to check against include DR-0024 … DR-0029 (and the DR-0029 P10 packet), ADR-0009, `docs/milestones/M3-proposal.md`, `M3-T0-decision-matrix.md`, `M3-decision-matrix.md`, `M3-T1-*`, `docs/reviews/M3-T1-acceptance-dossier.md`, VAL-0019/VAL-0020 in `docs/science/validation.md`, SCI entries in `docs/science/assumptions.md`, the T0 spike code and results in `docs/science/experiments/m3-t0/`, the production code in `src/tars/`, and `docs/reviews/raw/M3-T0-codex-review01-prompt.md` (which quotes the Tech Lead's T2 gate at line 275).

## Specific claims to verify (not exhaustive)
1. Each P1–P9 row's question, options and status match DR-0029 and the home DR (DR-0027, DR-0025, DR-0024); no option is missing; no recommendation is presented as a decision; every number quoted from T0 matches the committed records.
2. The readiness classifications (READY P1, P2, P4, P8, P9; BLOCKED P3←P1, P5←P4/P1, P7←P1/P9; NEEDS EVIDENCE P6) are defensible. Are any couplings missing or wrong?
3. The governing-gate statement ("P1–P10 as prerequisites for T2") is quoted correctly and is not narrowed by the implementer; the technical dependency map is labelled as non-governing.
4. N-1: the T0 derived stage-domain floors depend on the spike's `geodetic_iterative` stopping rule and the km density route (`t0_termination.py` `rounding_allowances`, `t0_model.py`). Is the claim accurate and not overstated?
5. N-2: DR-0026 AR-8 / §5.8 ("runtime functions are total"; "density is total") versus DR-0029 P4 (ii). Is it a real tension, correctly described, including the claim about what DR-0026's Resolution adopts?
6. N-3, N-5, N-7: correctness (N-5: does `src/tars/validation/architecture.py` forbid `tars.validation` and `importlib` in the physics core? Is `pathlib` already used in `tars.sim`?).
7. C-1…C-4: recompute (RK4 real-axis stability limit; e^z − R(z) vs z^5/120; drag velocity-Jacobian eigenvalues; a − b for WGS 84). C-5: the forward transformation of φ = 53°48′33.82″ N, λ = 2°07′46.38″ E, h = 73.0 m on WGS 84 against X = 3 771 793.97, Y = 140 253.34, Z = 5 124 304.35 m; check that the packet's statement of the evidence's limits (input recalled, PDF unread) is honest. C-6/C-7: are they described without overclaiming?
8. Validation strategy: is every proposed gated bound exact, derived (with stated operation counts) or theory-based, and every measurement non-gating unless an owner-approved threshold exists? Flag any arbitrary tolerance or any test claim that cannot hold in binary64 (for example U-5's power-of-two exactness, U-12's exact base densities, U-3's dry-mass claim).
9. Draft authorization packet: preconditions complete; permitted/protected paths consistent with the T1 precedent and the M3 baseline-and-impact classes; stop conditions; review and merge gates; marked DRAFT — NOT AUTHORIZED; no scope expansion into T3/T4/T5.
10. Open-issues register: every item named in I-23 §9 E is present (Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular tolerances, T3 axis representation, T4/T5 requirements, M3 final time step, external corroboration), without resolving or expanding it.
11. Append-only edits: no earlier text altered (the README row is extended in place, following that file's existing pattern; judge whether that is acceptable). The I-22 merge record is internally consistent with git (`git rev-list --count 60648b9..fc50aed`, `--merges`).
12. Scope compliance: `git diff --stat fc50aed..5ee6a6a` touches only `docs/`; no production code, test, scenario, threshold, reference, constant, CI or lock change.

## Output format
Write your review in Markdown with these sections:
1. `VERDICT: PASS (unconditional)` or `VERDICT: PASS (conditional)` or `VERDICT: REQUEST_CHANGES` on the first line.
2. Summary.
3. Findings table: ID (M3T2R-R1-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location (file:section or line), finding, evidence (commands or derivations you ran, with results), recommended correction.
4. Verification of claims 1–12, each with what you checked and the result.
5. Your own computations (commands and outputs).
6. Limitations of this review (what you could not verify).
Severity guide: BLOCKER/MAJOR = a wrong technical claim that would mislead an owner decision, an approval presented as made, or a scope violation; MINOR = an inaccurate or unsupported statement that does not change a classification; NOTE = clarity or completeness.

## Tech Lead authorization I-23 (verbatim)

# TARS — Authorization I-23
## M3 T2 Decision Readiness and DR-0029 P1–P9 Resolution Preparation

You are the lead spacecraft dynamics engineer, numerical methods specialist, software architect, and verification engineer for the TARS spacecraft simulation project.

You are operating in a new Superset workspace following the successful acceptance and fast-forward merge of Milestone 3 Task T1.

Your responsibility is to prepare the next M3 decision gate through rigorous repository inspection, independent technical research, reproducible evidence, and explicit owner review.

**This authorization permits research, analysis, and planning documentation only. It does not authorize production implementation, approval of unresolved decisions, or merging.**

## 1. Verified historical checkpoint

The previous workspace reported the following completed state under Authorization I-22:

- M3 T0: ACCEPTED and MERGED.
- M3 T1: IMPLEMENTED, REVIEWED, ACCEPTED, and MERGED.
- Main HEAD: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- T1 accepted implementation commit: `65de33ffce72bb504dc28a3d17dbb0ae57b7a36b`.
- T1 acceptance commit: `fc50aed`.
- Merge method: fast-forward only.
- Four CI jobs passed on the acceptance commit and on main.
- Fresh-clone validation passed.
- The T1 numerical contract and accepted limitations remain documented.

Treat this as a historical report, not a substitute for independently verifying the repository.

T1's accepted limitations include surviving mutants, finite mutation evidence, and non-gating secular-rate comparisons. Do not silently strengthen the claims made by the acceptance record.

## 2. Mandatory baseline verification

Before creating or changing any files:

1. Locate the authoritative TARS repository and worktree.
2. Run `git fetch origin`.
3. Verify that `origin/main` equals `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
4. Verify that the checkout is clean.
5. Confirm that the T1 acceptance records and relevant M3 decision records are present.
6. Identify any repository instructions, development conventions, review procedures, or authorization requirements.
7. Verify the current M3 task dependency graph.

If the remote baseline differs, the checkout is dirty, or the documented task dependencies conflict with the historical report, STOP and report the discrepancy.

Do not reset, discard, overwrite, or otherwise modify existing work to force the expected baseline.

## 3. Establish the planning worktree

Only after baseline verification passes, create a dedicated planning branch and worktree from the verified main commit.

Suggested branch:

`milestone-3-t2-decision-readiness`

Suggested worktree:

`~/superset-worktrees/tars-m3-t2-decision-readiness`

Use repository conventions if they specify a different location.

Do not reuse the T1 implementation worktree.

Do not modify main directly.

All commits and pushes must be ordinary, non-force operations.

## 4. Reconstruct M3 technical context

Read the authoritative repository documentation before recommending decisions.

At minimum, inspect:

- M3 milestone plan and task breakdown.
- DR-0024 through DR-0029.
- DR-0028 amendments and outstanding P6(b).
- M3 T0 reports, decision matrix, and acceptance records.
- M3 T1 authorization packet, validation evidence, review records, and acceptance dossier.
- Relevant M1 and M2 numerical contracts and regression guarantees.
- Existing force-model, coordinate-frame, reference-configuration, and numerical validation documentation.

Locate the actual files rather than assuming filenames or paths.

Determine precisely:

- What T2 is intended to implement.
- Which decisions block T2.
- Which decisions are independent versus coupled.
- Which T0/T1 contracts T2 must preserve.
- What evidence already exists.
- What evidence is missing.
- What additional work would be required to make each decision defensible.

Do not infer technical requirements from task names alone.

## 5. DR-0029 P1–P9 decision-readiness analysis

For each unresolved decision P1 through P9, produce a structured assessment containing:

1. Exact decision question, with reference to its authoritative source.
2. Available alternatives.
3. Current documented status.
4. Dependencies on other decisions.
5. Relevant physical and mathematical assumptions.
6. Numerical consequences.
7. Software architecture consequences.
8. Verification and testing consequences.
9. Compatibility with accepted M1/M2/T0/T1 behavior.
10. Existing supporting evidence.
11. Missing evidence.
12. Recommended option, if justified.
13. Confidence and unresolved uncertainty.
14. Proposed acceptance criteria.
15. Whether the decision is ready for owner approval.

Recommendations must distinguish established facts, mathematical derivations, numerical experiments, engineering judgment, and unverified assumptions.

Do not record recommendations as approved decisions.

If the evidence is insufficient, explicitly mark the decision NOT READY and propose the smallest experiment or analysis needed to resolve it.

## 6. Independent technical corroboration

Do not rely exclusively on the existing TARS implementation or its own tests as evidence of physical correctness.

Where relevant, investigate authoritative independent references, such as:

- NASA and JPL technical publications.
- Vallado's *Fundamentals of Astrodynamics and Applications*.
- Publicly documented GMAT models and reference behavior.
- Orekit documentation and reference implementations.
- Authoritative WGS84, EGM2008, atmospheric, and orbital mechanics references.

Use these only where relevant to the actual P1–P9 questions.

For each external reference, record its exact identity, version or revision when available, applicability, assumptions, and limitations.

Distinguish independent corroboration from comparisons that share the same underlying equations, constants, or implementation assumptions.

Do not claim independent validation merely because two implementations agree.

## 7. Numerical and scientific rigor

Preserve the project's established approach to numerical validation.

Where relevant, analyze:

- Reference frames and transformations.
- Force-model assumptions.
- Units and physical constants.
- Floating-point precision and rounding.
- Numerical conditioning.
- Singularities and domain boundaries.
- Underflow and overflow.
- Error propagation.
- Cross-platform determinism.
- Integration-step sensitivity.
- Regression compatibility.

Do not introduce arbitrary numerical tolerances.

Any proposed tolerance must have a defensible mathematical, physical, or empirical basis.

Separate analytical bounds from sampled estimates.

Do not claim that a finite test suite proves correctness.

Do not modify accepted M1, M2, T0, or T1 numerical contracts.

## 8. Scope and experiment restrictions

This authorization permits:

- Reading repository files.
- Technical research.
- Mathematical derivations.
- Dependency analysis.
- Documentation-only planning changes.
- Preparing proposed experiments and validation matrices.
- Non-mutating inspection commands.

It does not permit:

- Changes to production code.
- Changes to tests, proof harnesses, scenarios, or golden references.
- Changes to pinned constants.
- Changes to CI configuration.
- Running experiments that generate or overwrite tracked artifacts.
- Implementing T2 or T3.
- Approving DR decisions.
- Changing previously accepted numerical thresholds.
- Merging branches.

If a new numerical experiment or code change is required to make a decision, describe the experiment, its expected outputs, isolation strategy, and acceptance criteria. Request separate authorization before executing it.

## 9. Required deliverables

Prepare documentation in repository-consistent locations covering the following.

### A. T2 decision-readiness report

Include:

- Verified repository baseline.
- T2 scope and intended outcome.
- Dependencies and blockers.
- Existing evidence.
- Evidence gaps.
- Scientific and architectural risks.
- Readiness assessment.
- Recommended next authorization.

### B. DR-0029 P1–P9 decision packet

Include a complete decision matrix and individual technical assessments.

Every decision must be classified as:

- READY FOR OWNER DECISION
- NEEDS ADDITIONAL EVIDENCE
- BLOCKED BY ANOTHER DECISION

Do not conflate readiness with approval.

### C. T2 validation strategy

Prepare a proposed validation matrix that maps requirements and proposed decisions to:

- Unit tests.
- Property-based or metamorphic tests, where appropriate.
- Independent reference comparisons.
- Numerical boundary tests.
- Cross-platform checks.
- Regression guarantees.
- Explicit acceptance gates.

This is a proposed strategy, not authorization to implement tests.

### D. T2 authorization packet

Draft the authorization required to begin T2 implementation after the relevant decisions are resolved.

It must identify:

- Preconditions.
- Approved scope required before implementation.
- Permitted files or components.
- Protected paths.
- Validation requirements.
- Independent review requirements.
- Stop conditions.
- Acceptance and merge gates.

Mark the packet DRAFT — NOT AUTHORIZED.

### E. Open-issues register

Preserve visibility of unresolved M3 items outside T2, including:

- Q-G2-1/P6 and Q-G2-2.
- DR-0028 P6(b).
- Secular tolerances.
- T3 axis representation.
- T4/T5 requirements.
- M3 final time step.
- External corroboration.

Do not resolve or expand these issues unless necessary to explain a direct T2 dependency.

## 10. Independent review

After preparing the documentation, conduct a self-audit for:

- Missing dependencies.
- Unsupported numerical claims.
- Contradictions with accepted decisions.
- Unjustified recommendations.
- Ambiguous acceptance criteria.
- Unintended scope expansion.

If an independent Codex review can be invoked using the established repository workflow, prepare the review request and execute a documentation-only independent review.

The reviewer must assess technical correctness, decision completeness, evidence quality, and scope compliance.

Do not describe a self-review as independent.

If independent review cannot be performed, record that limitation explicitly.

For findings requiring corrections, record the findings and proposed dispositions. Do not start an unbounded correction/review cycle without authorization.

## 11. Version control and reporting

Commit only authorized planning documentation.

Before each commit:

- Inspect the diff.
- Confirm no protected files changed.
- Confirm no accidental generated artifacts are included.
- Check for contradictions with accepted decisions.

Push only to the dedicated planning branch using an ordinary push, if permitted by repository conventions.

Do not create or merge a pull request.

Do not modify main.

## 12. Mandatory stop condition

Stop after:

1. Baseline verification.
2. Documentation research.
3. DR-0029 P1–P9 readiness assessment.
4. Preparation of the required planning deliverables.
5. Authorized documentation validation and independent review, if available.
6. Documentation-only commit and push.

At the checkpoint, report:

- Branch, worktree, HEAD, and remote status.
- Files changed.
- Validation and review results.
- P1–P9 decision-readiness matrix.
- Decisions ready for owner approval.
- Decisions requiring more evidence.
- Recommended next action.
- Explicit list of actions not performed.

**Do not implement T2, approve decisions, or merge anything.**

## 13. Final instruction

Begin with repository baseline verification.

If all preconditions pass, proceed with decision-readiness research and documentation.

Prioritize scientific correctness, traceable evidence, preservation of accepted numerical contracts, and narrowly scoped progress over implementation speed.

At the final checkpoint, provide your recommendation for the next authorization, but wait for explicit owner approval before proceeding.
