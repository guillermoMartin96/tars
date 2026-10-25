You are an independent reviewer from a separate provider. You did not write any file under review. This is a **focused, documentation-only independent Review 03** of the TARS spacecraft simulator's Milestone 3 "T2 decision readiness" planning package. Review 02 (record `docs/reviews/M3-T2-readiness-review-02.md`, raw output `docs/reviews/raw/M3-T2-readiness-codex-review02.md`) returned REQUEST_CHANGES with M3T2R-R2-F1 (MAJOR), R2-F2 (MAJOR) and R2-F3 (MINOR). The implementer has applied a correction pass under the Tech Lead's Authorization I-25 (verbatim at the end). The implementer's documents are claims, not evidence: verify them against the repository and against mathematics.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`628623bdb5fdaee5da4167167be914a68a1734a9`** (branch `milestone-3-t2-decision-readiness`). Its parent `e769f9e24dcf619119c9c5d27ca70423e279bfc0` is the state Review 02 left (records only); `f44a94fb09101f99dc380eaf1cff701a217b79d0` is what Review 02 reviewed; `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- A locked Python environment is in `./.venv` (numpy, scipy). Use `.venv/bin/python -I`. **The network is not available.**
- **Do not modify tracked files.** Scratch only under `./review_scratch/` (excluded from git). Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`. You may import `docs/science/experiments/m3-t0/t0_model.py` and `t0_termination.py` read-only and write your own computations. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo; no network):** I-25 §1 baseline verification and the push of `628623b`. Treat CI and remote facts as claims you cannot authenticate.
- **Decision boundaries.** You review; you do not decide. Do not record any DR item, assumption (A-FP-2, A-LM-0 … A-LM-2) or proposed amendment as approved. Do not fix anything.

## What is under review (`git diff e769f9e..628623b`)
- `docs/milestones/M3-T2-validation-strategy.md`: U-13, U-19, PM-4, A-LM-1, B-9, B-11, G-T2-2; correction log (I-25).
- `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`: P4 item 8 wording; correction log (I-25).
- `docs/decisions/requests/DR-0029-P1-P9-owner-briefing.md`: closing note on conditional rows; append-only note.
- Append-only notes: `docs/milestones/M3-T2-authorization-packet.md` (must remain DRAFT — NOT AUTHORIZED), `docs/milestones/M3-T2-decision-readiness-report.md`.
- New: `docs/reviews/M3-T2-readiness-review-02-corrections.md` (correction matrix and consistency audit).

## What you must independently assess (I-25 §5)
1. **R2-F1 resolved?** Exact z-reflection equality must not gate; mathematical symmetry vs binary64 behaviour distinguished; assumptions and their limits documented; A-FP-2 and the library contract not silently strengthened. Check the narrowed A-LM-1 (hypot symmetry and evenness only) really suffices for exact quarter-turn equality in the path (α) operation sequence (`t0_model.geodetic_iterative`). Check the new bounded comparison B-11 (c), |ĥ(r) − ĥ(σr)| ≤ 2ε_h(h) with ε_h evaluated at (ĥ(r) + β)/(1 − α): is σ exact in binary64, is h_true(σr) = h_true(r) on the model's ellipsoid, is E1's domain respected, and is the ε_h upper-bound substitution valid (E1: |ĥ − h| ≤ αh + β)?
2. **R2-F2 resolved?** Strict decrease report-only; no lower error bound inferred from E3 (`t0_termination.rounding_allowances`) or samples; non-increase unchanged under its assumption; U-13 one-sided consistent with E3; promotion requires derivation and authorization.
3. **R2-F3 resolved?** Wording now accurate; trap interval (−2.475e-321 < h_m < 0), guard, signed-zero treatment, tests and historical evidence unchanged (word diff).
4. **New numerical or logical errors** introduced by the corrections.
5. **Are the proposed T2 validation gates scientifically justified?** Re-check that every row classed Gate in §3.9 (and every E row the gates G-T2-1 … G-T2-3a reference) rests on a stated derivation or on correctly rounded IEEE 754 operations, and that no contradictory unconditional gate remains in the strategy, the draft packet or the decision packet.
6. **Previously resolved findings remain closed:** Review 01 F1, F2, F4, F5 (RESOLVED in Review 02) and the parts of F3/F6 Review 02 accepted.
7. **Authorization boundaries respected:** docs only; historical review records (Review 01/02 records and raw files) unchanged; append-only prefixes intact; no protected path (`src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`) or T0 file touched; P1–P9 classifications unchanged (READY P1, P2, P4, P8, P9; dependent P3, P5, P7; evidence P6); Q-GATE, DQ-1 … DQ-6 and P6/X-1 open.

## Output format
Markdown:
1. First line: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. Summary.
3. Findings table: ID (M3T2R-R3-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location, finding, evidence (commands or derivations, with results), proposed disposition/correction.
4. Assessment of items 1–7, each with what you checked and the result (for 1–3: RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED).
5. Your own computations (commands and outputs).
6. Limitations.
Severity guide: BLOCKER/MAJOR = a wrong technical claim that would mislead an owner decision or a T2 gate, an approval presented as made, or a scope violation; MINOR = inaccurate or unsupported statement not changing a classification or gate; NOTE = clarity. PASS means no BLOCKER or MAJOR finding remains.

## Tech Lead authorization I-25 (verbatim)

# TARS — Authorization I-25
## M3 T2 Decision Readiness: Review 02 Corrections and Independent Review 03

You are continuing the TARS Milestone 3 T2 decision-readiness workflow following Authorization I-24.

I authorize a documentation-only correction pass for the three accepted findings from Independent Codex Review 02, followed by a focused Independent Codex Review 03.

This authorization does not approve any DR-0029 decisions, change the T2 decision gate, authorize implementation, or permit merging.

## 1. Mandatory preconditions

Expected state:

- Planning branch: `milestone-3-t2-decision-readiness`
- HEAD and remote: `e769f9e`
- Main: `fc50aed`
- Worktree: clean
- Review 02: REQUEST_CHANGES
- Open findings: R2-F1, R2-F2, R2-F3

Before editing:

1. Fetch remote references.
2. Verify the current branch and its relationship to the remote planning branch.
3. Verify HEAD, worktree cleanliness, and main.
4. Read the complete Review 02 record, its evidence, and the affected planning documents.
5. Verify the three findings against their recorded reproductions.
6. Confirm that no production code, tests, or protected paths changed.

If a precondition fails, stop and report the discrepancy. Do not reset, discard, or overwrite work.

## 2. Authorized corrections

### R2-F1 — Equatorial reflection and cosine symmetry

The proposed U-19 equatorial reflection test assumes exact cosine symmetry that is not established by the current library assumptions.

Correct the validation criteria so that:

- Exact reflection symmetry is not an unconditional gate without sufficient justification.
- Any mathematical symmetry claim is distinguished from floating-point implementation behavior.
- The relevant assumptions and their limitations are explicitly documented.
- The test remains report-only unless a defensible gating criterion can be derived.

Do not introduce an arbitrary tolerance to make the test pass.

Do not silently strengthen the T0 accuracy assumption or the mathematical-library contract.

If a valid bounded comparison is possible, document its derivation and assumptions. Otherwise preserve the test as diagnostic evidence.

### R2-F2 — Strict density decrease and one-sided error bounds

The proposed PM-4 strict-decrease gate relies on a two-sided numerical error allowance, but the existing T0 density error evidence supplies only an upper bound.

Correct the validation strategy so that:

- Strict-decrease testing is report-only pending a justified two-sided error bound.
- The existing non-increasing test remains subject to its documented assumptions.
- No unsupported lower error bound is inferred.
- The distinction between mathematical monotonicity and computed binary64 behavior is preserved.
- Any future promotion to a mandatory gate requires explicit supporting evidence and authorization.

Do not invent a tolerance or derive one from passing samples alone.

### R2-F3 — Negative subnormal wording

Correct the description of `−2.475e-321` to accurately distinguish the negative value's magnitude from its quotient behavior.

Verify that the correction changes only the wording.

Preserve:

- The documented trap interval.
- The proposed lower-domain guard.
- The signed-zero treatment.
- The existing test criteria.
- The historical reproduction evidence.

Do not modify implementation behavior.

## 3. Consistency audit

After making the corrections:

1. Search the planning documents for references to U-19, PM-4, and the affected negative subnormal boundary.
2. Verify that no contradictory unconditional gates remain.
3. Check that the authorization draft matches the validation strategy.
4. Check that the decision packet does not implicitly approve unsupported numerical assumptions.
5. Confirm that all previously resolved Review 01 findings remain resolved.
6. Confirm that all DR-0029 P1–P9 classifications remain unchanged.

Keep historical review records intact.

Use correction logs or append-only amendments where appropriate.

## 4. Scope restrictions

Only documentation changes directly required by R2-F1, R2-F2, R2-F3, and their consistency corrections are authorized.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify pinned constants, golden references, accepted numerical contracts, or previously approved decisions.

No new numerical experiment, production implementation, or tracked test change is authorized.

## 5. Validation and independent Review 03

First perform a self-audit of the corrections.

Then invoke independent Codex Review 03 using the established repository review procedure.

The reviewer must independently assess:

1. Whether R2-F1 is resolved.
2. Whether R2-F2 is resolved.
3. Whether R2-F3 is resolved.
4. Whether the corrections introduced new numerical or logical errors.
5. Whether the proposed T2 validation gates are scientifically justified.
6. Whether the previously resolved findings remain closed.
7. Whether all authorization boundaries were respected.

Require an explicit PASS or REQUEST_CHANGES verdict.

If Review 03 returns REQUEST_CHANGES:

- Record the findings.
- Reproduce them where feasible.
- Record their dispositions.
- Do not fix them in the same review cycle.
- Do not start Review 04.
- Stop for owner authorization.

If Review 03 returns PASS, prepare the final readiness report but do not approve decisions or start T2.

## 6. Version control

Commit the correction and review records separately.

Use ordinary, non-force pushes to the existing planning branch.

Verify the final pushed HEAD and CI results.

Do not create a PR or merge anything.

Do not modify main.

## 7. Final checkpoint

Report:

- Branch, HEAD, remote HEAD, and working-tree status.
- Commits and changed files.
- R2-F1 through R2-F3 correction matrix.
- Review 03 verdict and findings.
- Validation and CI results.
- Status of previous Review 01 and Review 02 findings.
- Remaining scientific uncertainties.
- P1–P9 decision readiness.
- Q-GATE and DQ-1–DQ-6 status.
- Recommended next authorization.

Explicitly confirm that no DR decisions were approved, no gate was changed, no implementation was started, and nothing was merged.

## 8. Stop condition

Stop after the authorized corrections, validation, independent Review 03, and checkpoint reporting.

Do not initiate another correction/review cycle without separate authorization.

Begin with baseline verification.
