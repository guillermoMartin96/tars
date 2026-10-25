You are an independent reviewer from a separate provider. You did not write any file under review. This is a **focused, documentation-only independent Review 02** of the TARS M3 owner-decision recording. Review 01 (record `docs/reviews/M3-T2-owner-decisions-review-01.md`; raw `docs/reviews/raw/M3-T2-owner-decisions-codex-review01.md`) returned REQUEST_CHANGES with M3T2OD-R1-F1 (MAJOR) and M3T2OD-R1-F2 (MINOR). The implementer applied a correction pass under the owner's Authorization I-27. I-26, I-27 and the Review 01 findings are reproduced verbatim at the end. The implementer's documents are claims, not evidence.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`f3ae3876825b2966faaced3281f638b6271572ad`** (branch `milestone-3-t2-owner-decisions`). Its parent `a22297d1ec719a58aeb7209f3d34256fa7b0756a` is the state Review 01 left (records only); `2cd1e6ec1bc2df13827c36d03fda5bf4b4150c09` is what Review 01 reviewed; `a57de3f` is the planning base; `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- A locked Python environment is in `./.venv`; use `.venv/bin/python -I`. **The network is not available.**
- **Do not modify tracked files.** Scratch only under `./review_scratch/` (excluded from git). Do not run the M1/M2 proof scripts. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo; no network):** I-27 §1 baseline verification and the push of `f3ae387`. Treat CI and remote facts as claims.
- **Decision boundaries.** You review; you do not decide or fix anything. Do not treat P6, DR-0028 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved.

## What is under review (`git diff a22297d..f3ae387`, 12 files, all under `docs/`)
- DR-0029 P3 and P7 "I-27 correction" blocks, in-place supersession markers, Resolution log entry.
- In-cell markers: DR-0027 "I-26 note" Names row; DR-0026 "I-26 note" §5.6 row; DR-0025 Q-G2-5 cell; owner briefing answer row 7; open-issues register OI-23 (+ I-27 status update incl. OI-9).
- Notes: `docs/milestones/M3-decision-matrix.md`, `docs/milestones/M3-T0-decision-matrix.md`.
- New: `docs/reviews/M3-T2-owner-decisions-review-01-corrections.md` (correction matrix; states why some RM-3b/`reentry` text was intentionally left unchanged and why packet r1's P8 limitation needed no change); `docs/reviews/raw/M3-T2-owner-decisions-I27-evidence/` (self-validation script, output, SHA256SUMS).

## What you must independently assess (I-27 §8)
1. **R1-F1 fully resolved?** The five clarifications of I-27 §2 are established (reentry DECIDED; precedence DECIDED; T3 implements, not re-approves; T3 fields/serialization only within the approved contract; future changes need a separate owner decision). Search **all** decision-recording documents (DR-0024 … DR-0029, ADR-0009, matrices, register, strategy, packets, briefing) for any remaining statement that leaves `reentry` or the precedence open, proposed or subject to T3 confirmation without an in-place supersession. Check the DR-0027 supersession is limited to the outcome name (field names remain T3 design) and that OI-23's resolution is justified by its exact wording.
2. **R1-F2 fully resolved?** RM-3b is described as an unmeasured candidate for evaluation during T4, not an accepted result, not a mandatory gate, promotion requiring evidence/review/authorization. Search all references to RM-3b for any statement implying measurement, certification, acceptance or a gate. Judge whether leaving the pre-I-26 recommendation text unchanged is correct.
3. **New inconsistencies** introduced by the corrections (wording, citations, authority strings, status labels).
4. **All I-26 owner decisions remain faithfully recorded** and unchanged (P1–P5, P7–P9 DECIDED; no decision added).
5. **P6 remains unresolved** (PROVISIONALLY SELECTED (d); geodetic drag ESCALATED; P6(b) OPEN; X-1 not authorized).
6. **Q-GATE unchanged**, and DQ-1 … DQ-6 and the floating-point policy unchanged (compare with `a22297d`).
7. **P8 conditional-validation limitation (I-27 §5).** Packet r1 must keep the A-FP-2-dependent geodetic accuracy tests (U-17, U-19 (c), PM-5, PM-6, U-18) report-only, keep justified domain/boundary/structural tests unconditional, invent no tolerance, and not present agreement with the T0 implementation as independent validation. Was "no change" the right outcome?
8. **Documentation-only scope**; append-only (in-cell appends before the closing `|` follow the established precedent); historical review records and evidence unchanged; no protected path (`src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`) touched.

## Output format
Markdown:
1. First line: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. Summary.
3. Findings table: ID (M3T2OD-R2-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location, finding, evidence, proposed disposition/correction.
4. Assessment of items 1–8 (for 1–2: RESOLVED / PARTIALLY RESOLVED / NOT RESOLVED).
5. Your own computations (commands and outputs).
6. Limitations.
Severity guide: BLOCKER/MAJOR = a recorded decision differing from the owner's text, an approval presented as made, a waived gate, a misleading technical claim, or a scope violation; MINOR = inaccurate or unsupported statement not changing a decision, classification or gate; NOTE = clarity. PASS means no BLOCKER or MAJOR finding remains.

## Review 01 findings (verbatim from `docs/reviews/raw/M3-T2-owner-decisions-codex-review01.md`)

## Findings

| ID | Severity | Location | Finding | Evidence and result | Proposed disposition/correction |
|---|---|---|---|---|---|
| M3T2OD-R1-F1 | MAJOR | DR-0029:292; DR-0027:146; DR-0026 I-26 outcome-name row; open-issues register OI-23 | The reconciliation leaves the approved outcome identifier `reentry` open for T3 confirmation. This narrows P3. | I-26 explicitly decides precedence `non_finite` → `reentry` → `impact` → `escape`. DR-0029 nevertheless says the historical outcome-name proposal was “not explicitly superseded”; OI-23 labels the identifier “Open.” Deferring implementation to T3 does not defer the owner’s choice. | Append a reconciliation recording `reentry` as decided and superseding the historical outcome-name proposal. Reconcile OI-23. Other field names and schema details may remain T3 design. No correction performed. |
| M3T2OD-R1-F2 | MINOR | DR-0029:526 | “RM-3b is a measured candidate only” incorrectly implies completed measurement. | The retained RM-3b row says “Not run.” The owner’s quoted decision says “a candidate to be measured during T4.” The reviewed decision packet also says not measured. | Clarify, in an authorized correction, that RM-3b remains an unmeasured candidate for T4, without a mandatory gate. |


## Owner authorization I-27 (verbatim)

# TARS — Authorization I-27
## M3 Owner Decisions: Review 01 Corrections and Independent Review 02

You are continuing the TARS Milestone 3 owner-decision recording workflow following Authorization I-26.

I authorize a narrowly scoped, documentation-only correction of the two accepted findings from Independent Codex Review 01, followed by a focused Independent Codex Review 02.

This authorization does not accept the I-26 decision reconciliation, authorize T2 implementation, approve new DR decisions, or permit merging.

## 1. Mandatory baseline verification

Expected state:

- Remote branch: `milestone-3-t2-owner-decisions`
- Superset local branch: `m3-t2-owner-decisions-972e4c7c`
- HEAD and remote: `a22297d1ec719a58aeb7209f3d34256fa7b0756a`
- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Worktree: clean
- I-26 Codex Review 01: REQUEST_CHANGES
- Open findings: M3T2OD-R1-F1 and M3T2OD-R1-F2

Before editing:

1. Fetch remote references.
2. Verify HEAD, remote HEAD, branch ancestry, and worktree cleanliness.
3. Read the complete I-26 authorization.
4. Read the owner-decision records, reconciliation notes, open-issues register, and revised T2 authorization packet.
5. Read `docs/reviews/M3-T2-owner-decisions-review-01.md`.
6. Verify the recorded reproductions and evidence checksums.
7. Verify that all I-26 changes remain documentation-only.
8. Verify that the reported CI results are green.

If any mandatory precondition fails, STOP and report the discrepancy. Do not reset or overwrite work.

## 2. Authorized correction: M3T2OD-R1-F1

### Problem

The I-26 decision explicitly approved the P3 outcome precedence:

`non_finite → reentry → impact → escape`

However, the recorded reconciliation still describes `reentry` as open for T3 confirmation.

That qualification incorrectly weakens the owner's approved decision.

### Required correction

Add an explicit, append-only clarification to the appropriate authoritative decision and reconciliation records.

The clarification must establish:

1. The `reentry` outcome name is DECIDED.
2. The P3 precedence order is DECIDED.
3. T3 is responsible for implementing these decisions, not approving them again.
4. T3 may define implementation-specific fields and serialization details only within the already approved contract.
5. Any future change to the outcome name or precedence requires a separate owner decision.

Supersede the contradictory "open for T3 confirmation" qualification only to the extent necessary.

Mark OI-23 resolved if, after inspecting its exact wording, this correction fully addresses it. Otherwise preserve the remaining scope explicitly.

Do not change any other P3 behavior.

Do not implement `reentry`.

## 3. Authorized correction: M3T2OD-R1-F2

### Problem

The I-26 reconciliation describes RM-3b as a measured candidate even though the proposed measurement has not been performed.

### Required correction

Replace the unsupported characterization with:

**RM-3b is an unmeasured candidate for evaluation during T4.**

Make clear that:

- RM-3b is not an accepted reference result.
- No measurement has been completed.
- It is not a mandatory acceptance gate.
- Any future promotion requires evidence and the applicable review and authorization.

Preserve the approved RM-0 through RM-8 reference-mission decision.

Do not create or execute an RM-3b experiment under I-27.

## 4. Consistency verification

After applying the corrections:

1. Search all I-26 decision-recording documents for contradictory statements about `reentry`.
2. Verify that the authoritative P3 resolution and dependency matrix agree.
3. Verify that the T3 implementation responsibility is distinguished from the already decided P3 contract.
4. Search for all references to RM-3b.
5. Verify that no document describes RM-3b as measured, certified, accepted, or mandatory without supporting evidence.
6. Verify that P1–P5 and P7–P9 retain their approved status.
7. Verify that P6 remains provisionally selected and unresolved.
8. Verify that the Q-GATE amendment is unchanged.
9. Verify that DQ-1 through DQ-6 are unchanged.
10. Verify that the floating-point validation policy is unchanged.

Do not use this pass to reconsider or expand the owner's decisions.

## 5. Preserve the P8 numerical-validation limitation

The I-26 checkpoint reports that A-FP-2 has not been justified on the supported CI platforms.

Consequently, the proposed numerical geodetic-height accuracy tests that depend on A-FP-2 cannot currently serve as unconditional acceptance gates.

Verify that the revised T2 authorization packet correctly preserves this limitation.

Do not:

- Accept A-FP-2 without evidence.
- Invent a replacement numerical tolerance.
- Promote conditional tests to unconditional gates.
- Claim that agreement with the T0 implementation constitutes independent validation.
- Weaken existing justified domain, boundary, or structural tests.

If the packet already represents this correctly, make no change.

If a contradiction is discovered outside the two authorized findings, record it and STOP rather than expanding scope.

The broader question of how T2 will obtain an independently justified numerical accuracy gate remains for the subsequent implementation authorization.

## 6. Documentation-only scope

Only changes necessary to correct R1-F1, R1-F2, and directly related documentary inconsistencies are authorized.

Historical review records and evidence must remain intact.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify accepted M1, M2, T0, or T1 implementation artifacts.

Do not change pinned constants, reference data, golden results, numerical thresholds, or approved scientific contracts.

No production implementation or numerical experiment is authorized.

## 7. Self-validation

Before independent review:

- Verify the corrected statements against the exact I-26 owner authorization.
- Verify all relevant decision statuses and dependencies.
- Verify append-only preservation of historical records.
- Verify that no unrelated decision was changed.
- Run applicable documentation and repository checks.
- Verify the changed-file scope.

Record the correction matrix and validation evidence.

Commit the corrections separately from the independent review record.

## 8. Independent Codex Review 02

Invoke an independent Codex reviewer using the established repository procedure.

Pin the exact correction commit SHA.

Provide the complete I-26 and I-27 authorizations and the relevant Review 01 findings.

The reviewer must evaluate:

1. Whether R1-F1 is fully resolved.
2. Whether R1-F2 is fully resolved.
3. Whether the corrections introduce new inconsistencies.
4. Whether all I-26 owner decisions remain faithfully recorded.
5. Whether P6 remains unresolved.
6. Whether Q-GATE is unchanged.
7. Whether the P8 conditional-validation limitation remains accurately represented.
8. Whether the changes comply with the documentation-only scope.

Require an explicit verdict:

- PASS
- REQUEST_CHANGES

If REQUEST_CHANGES:

- Record every finding.
- Reproduce it independently where feasible.
- Assign a documented disposition.
- Do not fix the new findings.
- Do not initiate Review 03.
- STOP for owner authorization.

If PASS:

- Prepare the final I-27 checkpoint.
- Do not independently accept the decision package.
- Do not merge.

## 9. Git and CI requirements

Use the existing owner-decision branch.

Commit the correction and review evidence separately.

Push with ordinary, non-force pushes.

Verify remote HEAD and worktree cleanliness.

Verify CI results on the pushed commits.

Do not create a PR.

Do not merge into main.

Do not create a T2 implementation branch.

## 10. Final checkpoint

Report:

- Branch and full HEAD SHA.
- Remote HEAD and worktree status.
- Exact commits and changed files.
- R1-F1 and R1-F2 correction matrix.
- Independent Review 02 verdict.
- Any new findings.
- CI results.
- P1–P9 status.
- Q-GATE and DQ-1 through DQ-6 status.
- Remaining P6 and P8 validation uncertainties.
- Readiness for owner acceptance of the I-26 reconciliation.
- Whether a fast-forward merge to main is possible.

Explicitly confirm:

- No new owner decision was made.
- No T2 implementation started.
- No protected file changed.
- No PR was opened.
- Nothing was merged.
- Main remains unchanged.

## 11. Mandatory STOP

Stop after the authorized corrections, independent Review 02, and checkpoint report.

Do not proceed to Review 03, acceptance, merge, or implementation without separate authorization.

Begin with baseline verification.

## Owner authorization I-26 (verbatim)

# TARS — Authorization I-26
## M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation

You are working on the TARS spacecraft simulation project.

This authorization follows I-23, I-24, and I-25, which prepared and independently reviewed the M3 T2 decision-readiness package.

The owner has reviewed the recommendations and explicitly approved the decisions specified below.

Your task is to record those decisions in their authoritative decision records, reconcile the resulting requirements, and prepare a revised T2 implementation authorization packet.

**This is a decision-recording authorization, NOT a T2 implementation authorization.**

## 1. Workspace and baseline

This is a new Superset workspace for the owner-decision phase.

Expected repository state:

- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Reviewed planning branch: `milestone-3-t2-decision-readiness`
- Reviewed planning HEAD: `a57de3f`
- I-25 Independent Codex Review 03: PASS, no findings
- Review 01: six findings resolved
- Review 02: three findings resolved
- T1: accepted and merged
- T2: not authorized
- DR-0029 P10: previously decided
- DR-0029 P1–P9: open before I-26

### Mandatory checks

1. Fetch all relevant remote references.
2. Verify the exact main and planning-branch SHAs.
3. Verify the reviewed planning worktree is clean.
4. Verify Review 03's verdict and the corresponding evidence.
5. Verify no protected paths changed during I-23 through I-25.
6. Read the complete authoritative decision records before editing.

Read at minimum:

- `DR-0029-m3-t0-proposals.md`
- `DR-0029-P1-P9-owner-decision-packet.md`
- `DR-0029-P1-P9-owner-briefing.md`
- `M3-T2-authorization-packet.md`
- `M3-T2-validation-strategy.md`
- DR-0024 through DR-0028, including applicable amendments
- The M3 proposal and milestone dependency matrix
- I-25 final readiness report and Review 03

The authoritative DR text governs where the briefing or packet differs.

If a discrepancy would materially change an approved choice, STOP and report it rather than guessing.

### Branching

Create a new decision-recording branch and worktree from the verified planning HEAD:

`milestone-3-t2-owner-decisions`

Follow the repository's established Superset worktree and remote-branch conventions.

Do not reuse the T1 implementation worktree.

Do not modify main directly.

## 2. Approved DR-0029 decisions

The following are explicit owner decisions.

Record them append-only in the authoritative DRs, preserving historical proposal text and decision provenance.

### P1 — Termination-altitude admissibility

**DECIDED: A4-b.**

Use:

- v̂ = V_b, the derived bound for bound-state relative velocity.
- κ = 0.01.
- Clause 1: a − b < h_f < h_geod(initial).
- Clause 2: ρ(h_f) × V_b × dt / B_min ≤ 0.01.

The ballistic coefficient uses dry mass.

Record that this is a necessary admissibility screen, not a sufficient numerical stability or trajectory-accuracy guarantee.

The derivation bounds the drag velocity-Jacobian contribution only. It does not bound the full coupled dynamics or ∂a/∂r.

κ is an owner-selected engineering constant, not a physically established universal threshold.

The final M3 timestep remains a separate decision.

### P2 — Termination crossing

**DECIDED: A5-b.**

Detect termination from committed states and report an additional scalar cubic-Hermite estimate of the crossing time.

The simulation ends at the committed state, not the interpolated crossing.

The reported crossing time is not a propagated state.

No final-step splitting is authorized.

Missed crossings or dips between committed states remain a documented limitation. Do not claim a certified perturbed-motion missed-dip bound.

T2 must expose the geodetic normal or latitude required for T3 to compute dh/dt.

### P3 — Outcome precedence

**DECIDED: Adopt the DR-0029 proposal.**

Precedence:

1. `non_finite`
2. `reentry`
3. `impact`
4. `escape`

Preserve `impact` as the legacy backstop.

Termination is determined from geodetic height, independently of atmospheric band selection.

Preserve the published density discontinuities.

This decision specifies future T3 behavior; do not implement it under I-26.

### P4 — Below-domain density

**DECIDED: Option (ii), fail closed.**

Any finite geodetic height below 0 m must cause a typed atmosphere-domain error.

The domain guard must compare height in metres before conversion to kilometres.

Negative zero is in range.

Non-finite heights receive a distinct error classification.

A failing RK4 stage must not commit a partial simulator state.

Explicitly reconcile DR-0026 AR-8 and §5.8: statements that density is total do not apply below the atmospheric table's lower edge.

T3 will define the versioned run-outcome mapping. Do not implement that mapping now.

Do not reproduce the T0 spike's negative-subnormal guard defect.

### P5 — Atmospheric altitude regions

**DECIDED: Adopt the DR-0029 P5 region table**, consistently with P1 and P4.

For heights above the 1000 km base, extrapolate the pinned top atmospheric band. Do not introduce a zero-density cutoff or a new upper-domain failure.

Preserve the pinned density table exactly.

Adopt the proposed wording amendment:

The top band's formula is continuous for h > 1000 km, but the 1000 km base retains its published relative density jump of approximately −1.598 × 10^-5.

Do not impose continuity across band boundaries.

Retain the published GMAT band-selection rule and exact-base behavior.

Explicitly label extrapolated densities above 1000 km as unverified.

### P6 — GMAT reference configuration

**NOT FULLY DECIDED.**

Approve decomposed exact-configuration method (d) as the preferred direction for subsequent validation planning, subject to its authoritative configuration requirements.

Do not mark P6 fully resolved.

The geodetic-drag discrepancy of approximately 0.14–0.38 m remains escalated.

Do not approve an independent geodetic GMAT acceptance gate.

Do not silently decide DR-0028 P6(b). Prepare a separate, explicit owner ruling on whether driving the validator with GMAT's reported axis is within the previously approved Earth-orientation scope.

The proposed X-1 investigation remains unexecuted and requires separate authorization.

Record the provisional method selection without converting unresolved evidence into a PASS.

### P7 — Reference missions

**DECIDED: RM-0 through RM-8.**

Use the P1 admissibility rule for RM-8.

Use the P9 illustrative vehicle definitions.

RM-3b is a candidate to be measured during T4, not a new mandatory gate without subsequent approval.

Preserve all previously accepted M1/M2 requirements.

### P8 — Geodetic-height reference points

**DECIDED: Options (a) and (a′), with the reviewed gating restrictions.**

Use exact mathematical answers as the primary gate source within their justified domain.

Use forward-constructed points as additional reference evidence.

Forward-constructed points become gating only after their numerical construction-error contribution has been derived and reviewed.

Negative-height cases remain report-only until appropriate bounds exist.

GeographicLib, GMAT and the identified IOGP/EPSG example are corroboration sources, not automatically authoritative inverse-height gates.

Do not claim independent verification from a reference that shares the same unexamined assumptions.

### P9 — Validation vehicles

**DECIDED: Option (i).**

Use the specified illustrative V1 and V2 vehicles from DR-0029.

V1:

- Mass: 850 kg
- Area: 15 m²
- C_d: 2.2
- Ballistic coefficient: approximately 25.8 kg/m²

V2 uses the accepted M2 vehicle mass configuration with area 15 m², as specified in DR-0029.

Every scenario and record must label these values:

**ILLUSTRATIVE — VALIDATION ONLY**

Do not claim they are validated representations of a real spacecraft.

## 3. Q-GATE — Approved amendment

The owner explicitly approves narrowing the original I-15 prerequisite for T2.

The replacement rule is:

**Before T2 implementation may be authorized:**

- P1–P5 must be decided.
- P8 and P9 must be decided.
- DQ-1 through DQ-6 must be decided.
- The resulting contracts must be recorded and reconciled.
- An explicit, separate T2 implementation authorization is required.

P10 remains previously decided and binding for T1.

P6 is not a T2 implementation prerequisite. Its unresolved scientific questions remain blockers for geodetic GMAT acceptance in T5.

P7 must be decided before its reference-mission obligations are implemented in T3/T4; it is already approved in this authorization.

This amendment supersedes only the broader T2 dependency statement from I-15. It does not waive any scientific, review, numerical or acceptance gate.

Record the supersession explicitly with provenance.

## 4. Approved T2 design decisions

### DQ-1 — Geodetic algorithm

**DECIDED: α.**

Reproduce the T0 iterative geodetic-height algorithm operation for operation within its applicable domain, including its starting latitude, convergence criterion and pole-safe height calculation.

The T0-specific error bounds may be reused only where their original assumptions and arithmetic sequences actually apply.

The T0 domain-guard defect must not be copied.

Record that this deterministic, data-dependent iterative algorithm satisfies the intended T2 geodetic design requirement.

### DQ-2 — Density arithmetic

**DECIDED: km route.**

Preserve the T0/GMAT kilometre-based density arithmetic for the applicable formula evaluation.

The lower-domain guard must still operate on height in metres before conversion.

Explicitly document the departure from DR-0024 §9's proposed convert-once-to-SI wording.

Do not change the pinned atmospheric table or silently substitute a mathematically equivalent but numerically different expression.

### DQ-3 — Simulator integration

**DECIDED: (a).**

T2 may add the context-aware force protocol and integrate immutable ForceContext construction into the simulator's derivative closures.

Current stage mass must be used.

Preserve the legacy force-model interface through an adapter.

Existing M1/M2 behavior must remain byte-identical on the specified same-platform regression gates.

No change to tick logic, engine scheduling, step splitting or atomicity is approved by this decision.

Implementation still requires separate authorization.

### DQ-4 — Dataset storage and digest

**DECIDED: Pinned data file under `src/tars/sim/data/`, with its SHA-256 digest pinned in `tars.sim`.**

Use the recorded GMAT R2026a source digest.

Do not import `tars.validation.approved_digests` from the physics core.

Use the approved file-access mechanism compatible with the static architecture guard.

Verify the data file is packaged correctly.

If packaging requires a protected `pyproject.toml` change, STOP. Do not silently adopt embedded Python bytes.

The embedded-bytes alternative requires separate approval.

### DQ-5 — J2 integration

**DECIDED: (a).**

Wrap the accepted T1 J2 implementation through the legacy adapter.

Do not rewrite the J2 force class, change its constants or create a replacement J2 model.

Preserve all T1 evidence and validation gates.

### DQ-6 — Drag parameter ownership

**DECIDED: Immutable drag-component constructor parameters.**

C_d and cross-sectional area belong to the drag force component.

Mass comes from ForceContext.

Scenario v3 schema and serialization remain T3 responsibilities.

No new spacecraft schema is authorized in T2.

## 5. Conditional floating-point gates

The owner approves the following policy:

- A-FP-2, A-LM-1 and A-LM-2 are not accepted as universal IEEE-754 guarantees.
- Tests depending on these assumptions may gate only when the precise assumption has been independently justified for the supported execution environment and the resulting criterion has been reviewed.
- Until then, those tests are report-only.
- Exact z-reflection symmetry and strict density decrease remain report-only regardless of the above assumptions.
- Do not promote an unproved numerical bound into a mandatory acceptance criterion.
- Do not invent tolerances.
- Preserve all unconditional, independently justified gates.

The revised T2 authorization must identify every conditional row and the evidence required to promote it.

## 6. Recording and reconciliation

Record the approved decisions in their authoritative home records.

Use append-only resolution entries or the repository's accepted decision-recording convention.

Update:

- DR-0024 through DR-0029 as applicable.
- The M3 decision matrix.
- The T2 dependency matrix.
- The owner-decision briefing and packet.
- The M3 open-issues register.
- The T2 validation strategy.
- The draft T2 authorization packet.
- The milestone index where needed.

Preserve historical proposal text, previous review records and prior owner decisions.

Do not retroactively rewrite the I-23/I-24/I-25 evidence.

Distinguish clearly between:

- DECIDED
- PROVISIONALLY SELECTED
- OPEN
- ESCALATED_FOR_INVESTIGATION
- NOT AUTHORIZED

In particular, P6 must not be recorded as fully decided.

## 7. Independent verification

Before requesting implementation authorization:

1. Verify every recorded decision against the owner's exact wording above.
2. Verify that all dependent DR entries are consistent.
3. Verify the new T2 gate does not waive T3/T4/T5 requirements.
4. Verify the validation strategy matches the selected algorithms and arithmetic.
5. Verify the accepted T0/T1/M1/M2 contracts are preserved.
6. Verify the revised T2 authorization draft contains no implied approval to execute.
7. Verify all changes are documentation-only.

Run applicable documentation checks.

Request an independent Codex review of the decision recording and reconciliation, including the revised dependency gate and conditional validation policy.

If the review returns REQUEST_CHANGES, record and reproduce the findings, then STOP. Do not begin an unapproved correction loop.

If the review returns PASS, prepare the final owner checkpoint.

## 8. Version-control restrictions

All changes under I-26 must be documentation-only.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify golden references, pinned constants, numerical thresholds or existing accepted implementation artifacts.

Commit the decision recording and independent review evidence separately.

Push using ordinary, non-force pushes.

Do not merge or open a PR.

Do not change main.

## 9. Final deliverables

Produce:

1. Recorded P1–P5, P7–P9 decisions.
2. P6 provisional method-selection record and unresolved investigation register.
3. Explicit Q-GATE amendment.
4. Recorded DQ-1 through DQ-6.
5. Reconciled authoritative decision documents.
6. Updated dependency matrix.
7. Revised T2 validation strategy.
8. Revised T2 implementation authorization packet, marked **DRAFT — NOT AUTHORIZED**.
9. Independent Codex review record.
10. Final I-26 checkpoint report.

The checkpoint must include:

- Branch and exact HEAD.
- Commit list.
- Changed-file list.
- CI results.
- Decision-by-decision recording matrix.
- Independent review verdict.
- Remaining blockers and scientific uncertainties.
- Exact recommended next authorization.

Explicitly confirm that T2 has not started, no implementation files have changed, and nothing has merged.

## 10. Mandatory STOP

Stop after documentation reconciliation, independent review and checkpoint reporting.

Do not create the T2 implementation branch.

Do not implement the drag force.

Do not merge the owner-decision branch.

Do not start the P6 investigation.

Do not approve DR-0028 P6(b).

Do not authorize T3, T4 or T5.

Await the owner's next explicit authorization.

Begin with baseline verification.
