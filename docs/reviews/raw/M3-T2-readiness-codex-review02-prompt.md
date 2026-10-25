You are an independent reviewer from a separate provider. You did not write any file under review. This is a **documentation-only independent Review 02** of the TARS spacecraft simulator's Milestone 3 "T2 decision readiness" planning package. It follows Review 01 (same reviewer provider, separate session; record `docs/reviews/M3-T2-readiness-review-01.md`, raw output `docs/reviews/raw/M3-T2-readiness-codex-review01.md`), which returned REQUEST_CHANGES with findings M3T2R-R1-F1 … F6. The implementer has now applied a correction pass under the Tech Lead's Authorization I-24 (verbatim at the end). The implementer's documents are claims, not evidence: verify them against the repository and against mathematics.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`f44a94fb09101f99dc380eaf1cff701a217b79d0`** (branch `milestone-3-t2-decision-readiness`), with git metadata. Its parent `d8270c248a00479fe715889eca4fcc8a208d8763` is the state Review 01 left (records only); `5ee6a6a2d78ef425687ba164bb32033947ee7c01` is the revision Review 01 reviewed; `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- A locked Python environment is in `./.venv` (numpy, scipy). Use `.venv/bin/python`. **The network is not available.**
- **Do not modify tracked files.** Put scratch files and your own scripts only under `./review_scratch/`, which is excluded from git. Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`. You may read any file, run `ruff check .` and `ruff format --check .`, import `docs/science/experiments/m3-t0/t0_model.py` read-only (run Python with `-I` and `sys.path` insertion, as the implementer's evidence script does), read committed T0 results JSON, and write your own computations. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo; you cannot reach the network):** I-24 §1 baseline verification (`git fetch`; HEAD = remote = `d8270c2`; `main` = `fc50aed`; clean tree; existing changes docs-only) and the push of `f44a94f`. Treat CI and remote facts as claims you cannot authenticate.
- **Decision boundaries.** You review; you do not decide. Do not record any DR item as approved (DR-0029 P1–P9, Q-GATE, DQ-1 … DQ-6, Q-G2-1/P6, DR-0028 P6(b), the proposed DR-0029 P5 wording amendment). Do not fix anything.

## What is under review (`git diff d8270c2..f44a94f`)
Corrected in place, with correction logs (the reviewed wording is preserved at `5ee6a6a`):
1. `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`: P1 item 14, P2 item 5, P4 items 8 and 14, P5 items 8 and 14, P8 matrix cell and items 12 and 14, N-1 cell; correction log at the end.
2. `docs/milestones/M3-T2-validation-strategy.md`: principle 1 additions; rows U-4 … U-7, U-12 … U-19, U-21, U-23, PM-1 … PM-6, I-2, I-7; §3.5; **new §3.9 bound audit (B-1 … B-15; assumptions A-LM-0 … A-LM-2)**; §4 gates; correction log.
3. `docs/milestones/M3-T2-authorization-packet.md` (must remain DRAFT — NOT AUTHORIZED): DQ-1, DQ-2 cells; §6; correction log.
Append-only: `docs/milestones/M3-T2-decision-readiness-report.md` (status update), `docs/milestones/M3-open-issues-register.md` (OI-20 … OI-22), `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (P5 wording note).
New: `docs/decisions/requests/DR-0029-P1-P9-owner-briefing.md` (I-24 §3), `docs/reviews/M3-T2-readiness-review-01-corrections.md` (correction matrix), `docs/reviews/raw/M3-T2-readiness-I24-evidence/` (`i24_reproduction.py.txt`, `.out`, `SHA256SUMS`).

Authoritative sources: DR-0024 (Q5a, Q8 Resolution), DR-0025 (Resolution principles), DR-0026 (AR-8, §5.8), DR-0027 (B-1 … B-5), DR-0029 (P1 … P10, notably P1's floating-point enclosure E1 … E6, assumptions A-FP-1 … A-FP-3), the T0 spike code and results in `docs/science/experiments/m3-t0/` (`t0_model.py`, `t0_termination.py` `rounding_allowances`, `t0_termination_results.json`), and Review 01's findings.

## What the reviewer must evaluate (I-24 §6)
1. **Whether F1–F6 are actually resolved**, each against Review 01's finding text and recommended correction. In particular:
   - F1: no remaining continuity requirement at any base; the 1000 km figures (left limit 3.0190482489066533e-15, row 3.019e-15, relative −1.598e-5; spike values at −1 ulp / exact / +1 ulp) are right; DR-0029 P5 is documented and amended only as a *proposal*, its table unchanged.
   - F2: E1's stated domain, assumptions and covered error match the T0 derivation and committed record; no E1 reuse outside true height ≥ 0; the U-17 reference construction (exact, model's ellipsoid) is sound; the b_model − b_WGS84 = +1.71e-12 m figure; the 1-Lipschitz argument for the δ_f term and its exterior condition.
   - F3: PM-4's non-increase argument (correctly rounded monotone operations, exp monotonicity as assumption A-LM-2) and the strict-decrease condition.
   - F4: the trap interval −2.475e-321 < h_m < 0 for the spike's km route; −0.0 handling; that the corrected guard leaves the arithmetic covered by the floors unchanged; proposed T2 requirement vs recorded T0 behaviour kept distinct.
   - F5: the stated regularity (h C¹, ḣ absolutely continuous, ḧ piecewise continuous) and the chord bound with an essential supremum; certified two-body numbers unaffected.
   - F6: each §3.9 entry's classification (Gate / Conditional / Deliverable), especially the new derivations B-1 (cross-product bound (2u/(1 − u))·|a_j|·|v_k|, sign of a·v_rel, PM-1 margin domain), B-2 (power-of-two exactness), B-10, B-11, B-13, B-15; whether any row still gates on an underived or arbitrary bound; whether zero cases and sample domains are stated.
2. **Whether any new mathematical or numerical defect was introduced** by the corrections (including the "related defects" the implementer reports: U-21 axis normal, U-23 parameter domain, U-6 signed zero, U-16 transition points).
3. **Whether proposed validation criteria match the authoritative scientific contracts** (DR-0024 Q5a, Q8; DR-0025 principles; DR-0029 P1–P5, P8).
4. **Whether unresolved decisions remain unresolved:** P1–P9 OPEN with unchanged classification; Q-GATE, DQ-1 … DQ-6 and the P6 investigation open; the briefing recommends without deciding or silently adopting.
5. **Whether the correction pass respected its scope:** docs only; historical review records (Review 01 record and raw files) unchanged; append-only files have their previous bytes as a prefix; no protected path (`src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`) touched; no T0 file edited.
6. **Whether the planning package is ready for owner decision review.**
7. Check the owner briefing (I-24 §3 items 1–7) for completeness and accuracy against the packet and DR-0029.

## Output format
Markdown:
1. First line: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. Summary.
3. Findings table: ID (M3T2R-R2-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location, finding, evidence (commands or derivations you ran, with results), proposed disposition/correction.
4. Resolution status of each Review 01 finding F1 … F6 (RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED), with what you checked.
5. Evaluation items 2–7 above, each with what you checked and the result.
6. Your own computations (commands and outputs).
7. Limitations.
Severity guide: BLOCKER/MAJOR = a wrong technical claim that would mislead an owner decision or a T2 gate, an approval presented as made, or a scope violation; MINOR = an inaccurate or unsupported statement that does not change a classification or a gate; NOTE = clarity or completeness. A PASS verdict means no BLOCKER or MAJOR finding remains.

## Tech Lead authorization I-24 (verbatim)

# TARS — Authorization I-24
## M3 T2 Readiness: Review 01 Corrections and Independent Review 02

You are continuing the M3 T2 decision-readiness work following Authorization I-23.

I authorize a strictly scoped documentation correction pass addressing the six accepted findings from Independent Codex Review 01, followed by independent Review 02.

**This authorization does not approve DR-0029 decisions, change the T2 decision gate, authorize T2 implementation, or permit merging.**

## 1. Baseline and preconditions

Expected state:

- Branch: `milestone-3-t2-decision-readiness`
- HEAD: `d8270c2`
- Remote HEAD: `d8270c2`
- Main: `fc50aed`
- Working tree: clean
- Review: `docs/reviews/M3-T2-readiness-review-01.md`
- Review 01 verdict: REQUEST_CHANGES

Before editing:

1. Fetch remote references.
2. Verify branch, HEAD, remote, and worktree state.
3. Verify the six findings and their recorded dispositions.
4. Verify that all existing changes remain documentation-only.
5. Read the complete I-23 decision packet, validation strategy, and authorization draft.

Stop if any precondition fails. Do not reset or discard work.

## 2. Authorized corrections

Address all six Review 01 findings.

**F1 — Density continuity at 1,000 km**

Remove the unsupported continuity requirement.

Establish the expected behavior from the authoritative pinned atmospheric table and applicable decisions.

Distinguish continuity within a segment from discontinuities at table boundaries.

If DR-0029 P5 contains contradictory normative wording, document the contradiction and propose an explicit amendment. Do not silently change an approved requirement.

**F2 — Incorrect application of numerical bounds**

Identify the original derivation, its domain, and its assumptions.

Restrict the proposed validation criteria to the domain where the bound is justified.

Do not transfer T0-specific numerical safety floors to a different T2 algorithm without an independent derivation.

**F3 — Strict monotonicity**

Replace mathematically unjustified strict binary64 monotonicity assertions with appropriately scoped non-increasing behavior where supported.

Account for equal outputs from neighboring representable inputs.

Do not introduce arbitrary tolerances.

**F4 — Lower-domain edge**

Correct the P4 test criteria using the actual specified domain and recorded T0 behavior.

Explicitly address the observed `−5e-324` case.

Distinguish existing implementation behavior from proposed fail-closed T2 requirements.

Do not change production code.

**F5 — Differentiability**

Remove the unsupported global C² claim for height along trajectories crossing atmospheric band boundaries.

State the regularity assumptions required by any proposed test or numerical method.

Do not assume differentiability across a piecewise-model boundary.

**F6 — Unsupported numerical bounds**

Audit every affected bound and tolerance.

For each, provide its derivation, supporting evidence, assumptions, and valid domain.

If a bound cannot be justified, remove it as a mandatory acceptance criterion and mark it for further research.

Do not invent replacement thresholds.

## 3. Preserve unresolved owner decisions

Do not approve or change the status of DR-0029 P1–P9.

Preserve the distinction between:

- Ready for owner decision.
- Dependent on another decision.
- Requires additional evidence.

Keep Q-GATE, DQ-1 through DQ-6, and the P6 investigation open.

Prepare a concise owner-decision briefing explaining:

1. The precise alternatives for P1–P9.
2. Which decisions can be resolved together.
3. What κ and v̂ represent in P1 and how they should be selected.
4. The consequences of the P4 fail-closed alternative.
5. The evidence still required for P6.
6. The trade-offs of retaining versus narrowing the T2 decision gate.
7. The exact questions requiring owner approval.

Recommendations are permitted; decisions are not.

Do not invent owner choices or silently adopt implementer recommendations.

## 4. Documentation scope

Edit only the documentation necessary to correct the six findings and maintain consistency across the I-23 deliverables.

Preserve historical review records. Record corrections and dispositions in new documentation or clearly identified append-only amendments.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not change golden references, pinned constants, numerical contracts, or previously accepted decisions.

## 5. Validation

Before independent review:

1. Verify each correction against the original finding.
2. Check all six findings for complete disposition.
3. Audit the validation strategy for related unsupported assumptions.
4. Check consistency across the decision packet, validation strategy, readiness report, and authorization draft.
5. Confirm the changes remain documentation-only.
6. Run applicable documentation checks.

Use explicit evidence references rather than unsupported assertions.

## 6. Independent Codex Review 02

After the correction pass, invoke an independent Codex review using the established repository workflow.

The reviewer must evaluate:

- Whether F1–F6 are actually resolved.
- Whether any new mathematical or numerical defects were introduced.
- Whether proposed validation criteria match the authoritative scientific contracts.
- Whether unresolved decisions remain unresolved.
- Whether the correction pass respected its scope.
- Whether the planning package is ready for owner decision review.

Require an explicit verdict:

- PASS
- REQUEST_CHANGES

Record all findings with severity, evidence, and proposed disposition.

If Review 02 returns REQUEST_CHANGES, reproduce and record the findings, then STOP.

Do not automatically start Review 03.

If Review 02 passes, prepare the final readiness checkpoint. Do not treat review success as authorization to implement T2.

## 7. Version control

Commit the documentation corrections and review evidence separately.

Use ordinary, non-force pushes to the existing planning branch.

Do not create or merge a PR.

Do not change main.

Verify CI status on the final pushed HEAD. If CI is pending, report that status rather than claiming completion.

## 8. Final checkpoint

Report:

1. Branch, HEAD, remote HEAD, and working-tree status.
2. All commits and changed files.
3. F1–F6 correction matrix.
4. Independent Review 02 verdict.
5. Validation and CI results.
6. Remaining scientific uncertainties.
7. P1–P9 owner-decision readiness.
8. Q-GATE and DQ-1–DQ-6 questions.
9. Recommended next authorization.

Explicitly confirm:

- No DR-0029 decisions approved.
- No decision gate changed.
- No T2 or T3 implementation.
- No production or test changes.
- No merge.

**Stop and await owner review.**

## 9. Execution instruction

Begin with baseline verification.

If all preconditions pass, perform the narrowly scoped documentation corrections, validate them, conduct Independent Review 02, and stop at the required checkpoint.

Prioritize correctness, independent evidence, and preservation of existing contracts over speed.
