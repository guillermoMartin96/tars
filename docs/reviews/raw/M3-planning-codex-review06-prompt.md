You are an independent reviewer from a separate provider; you did not write these documents. This is the TARS Milestone 3 **planning checkpoint, review round 06**. It is a **targeted** review of the correction of review 05's single finding, M3P5-F1, and of the stronger signed verification that the Tech Lead required. It also covers regression, planning-package consistency and authorization boundaries. No M3 implementation exists or is authorized.

The snapshot is the current directory: a git clone of the planning branch at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/`, which is git-ignored.

**Verify independently.** Derive and check the signed formulas yourself, with your own code and your own rotation matrix. The new script's output is not proof, and neither are the recorded dispositions. You may report any newly discovered correctness defect of any severity, anywhere in the planning package. Acceptance criteria are not relaxed for this round.

## Context and review history
- **Baseline:** `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M1/M2 accepted, CLOSED). Whole-branch scope: `git diff d92ab89..HEAD`.
- **Changes under review:** `git diff cf0e24f..HEAD`.
  - The correction commit is `bcb7f9bff6b79ad22f01eaa6a2cac3e444f55ecf`. The commit after it adds only this prompt.
  - Earlier rounds: `git diff 16b6888..cf0e24f` (round 05: M3P4 corrections in `b411b5f`, record in `cf0e24f`), `git diff 8496ac1..16b6888` (round 04), `git diff 23bafd2..8496ac1` (round 03) and `git diff 6dbb22b..23bafd2` (round 02).
- **Previous reviews.** Each has a record `docs/reviews/M3-planning-review-0N.md` and raw output `docs/reviews/raw/M3-planning-codex-review0N.md`. Every finding must remain recorded with its disposition and its correction intact.
  - **Round 01:**
    - M3P-F1 MAJOR, density table discontinuous, not C0;
    - M3P-F2 MINOR, drag along-track sign;
    - M3P-F3 MINOR, decay-oracle approximations;
    - M3P-F4 MINOR, rejected atmosphere cutoff in the task plan;
    - M3P-F5 MINOR, rotation-rate difference understated.
    - All ACCEPTED and corrected.
  - **Round 02:**
    - M3P2-F1 BLOCKER, unaddressed choices recorded as approved: ACCEPTED, resolved by owner decisions;
    - M3P2-F2 BLOCKER, T0 authorization: REJECTED_WITH_REASONING, with the prompt corrected;
    - M3P2-F3 MINOR, lowest band: ACCEPTED, corrected.
  - **Round 03:**
    - M3P3-F1 MINOR, velocity transformation qualification;
    - M3P3-F2 MINOR, abbreviated withdrawn Q4 quotation.
    - Both ACCEPTED and corrected (`58f0d18`).
  - **Round 04:**
    - M3P4-F1 MINOR, the pole tilt does not bound the node error;
    - M3P4-F2 MINOR, local solar time needs no Earth rotation angle.
    - Both ACCEPTED and corrected (`b411b5f`, DR-0028 "Resolution amendment 1").
  - **Round 05:**
    - M3P5-F1 MINOR, the signed first-order formulas Δi ≈ δ cos(Ω − φ) and ΔΩ ≈ −δ cot i sin(Ω − φ) are reversed for the passive convention R = Rot(e, −δ). ACCEPTED; corrected in `bcb7f9b` (DR-0028 "Resolution amendment 2").
- **Files changed in `bcb7f9b`:**
  - DR-0028: a status-header line, a pointer under amendment 1's formula table, and the appended "Resolution amendment 2";
  - `docs/reviews/M3-planning-review-05.md`: appended resolution;
  - the decision matrix, `M3-proposal.md` and the milestones `README.md`: status;
  - `docs/science/experiments/m3-planning/`: new `dr0028_node_signed_verification.py`, its results JSON and a README entry. The earlier `dr0028_node_sensitivity.py` is unchanged.
- **Validation evidence (implementer, at `bcb7f9b`)**, for you to check, not to accept:
  - **Isolated clone:** M1 Proof overall PASS (exit 0), including full pytest (1185 passed). M2 Proof overall PASS (21 steps, exit 0). Regenerated Proof evidence differed only in run metadata (revision, tree_clean, record sha256, dates, temporary paths, uv build messages).
  - **Worktree:**
    - `dr0028_node_signed_verification.py`: exit 0, verdict PASS, rerun byte-identical;
    - `dr0028_node_sensitivity.py` and `q10_residual_consequences.py`: reruns byte-identical;
    - Ruff format and lint pass; relative links, 0 broken;
    - docs-only against `d92ab89`; registers 218/0 and 43/0;
    - no change since `cf0e24f` to the registers, DR-0024…DR-0027, ADR-0009, `src/`, `tests/`, `toolbox/`, `scenarios/` or `proof/`.
  - **Live mutations:** editing the formula under test to reverse the Δi sign, the ΔΩ sign, or both made the script exit 1 (1120, 1008 and 2128 failing checks).
  - **CI for `bcb7f9b`** (GitHub Actions; you may not have network access): run 38947344104: completed success.

## The Tech Lead's governing instructions (complete and verbatim)
Each later instruction governs where it differs from an earlier one. I-5 is the latest.

### Instruction I-1: "M3 planning decision checkpoint" (2026-10-15), sections 1–8
````text
You are at the M3 planning decision checkpoint for the TARS spacecraft simulator.

M3 implementation is NOT yet authorized.

Resolve DR-0024, DR-0025, and DR-0026 using the owner decisions below. Update the planning documentation, decision records, science records, correction notes, and review dispositions as necessary. Do not implement J2, drag, atmosphere, new force interfaces, scenario v3 runtime behavior, or any other M3 production code during this task.

## 1. DR-0024 — G1 physical models and constants

Approve the following direction:

- J2: use the EGM2008 tide-free J2 value proposed in DR-0024.
- Continue using the project's existing WGS84 GM and WGS84 equatorial radius unless the research shows that doing so creates a mathematically inconsistent model that materially affects M3 acceptance. If such a conflict exists, stop and raise a new Decision Request rather than changing constants.
- Correct SCI-0005 with an explicit historical correction note: do not silently rewrite the old claim about TT/TCG compatibility.
- Atmosphere: use the proposed piecewise Vallado/GMAT atmosphere for M3, subject to Q10 verification against the printed/source material.
- Do NOT alter published/tabulated density values merely to force continuity at band boundaries. Preserve the source model faithfully. Document discontinuities, quantify them, and require tests at and immediately around every band boundary.
- Retain the simple one-band atmosphere subset for analytic/unit tests where useful.
- Height for atmospheric density: geodetic height relative to the WGS84 ellipsoid.
- Atmospheric relative velocity must include Earth rotation using the proposed pinned Earth rotation rate.
- Drag must use current spacecraft total mass.
- Earth/model constants are pinned physics configuration, not scenario overrides.
- Scenario parameters include Cd, reference area, initial mass, and initial state.
- Do not extrapolate the atmosphere indefinitely below its validated/modelled domain.
- Define an explicit validity boundary and re-entry/termination event. If research does not justify a defensible numerical altitude yet, leave the numerical value OPEN and raise/retain a Decision Request rather than inventing one.
- Cd and area values used by validation scenarios must be explicit scenario inputs, not hidden constants.

Before closing DR-0024, independently verify Q10 against the authoritative source available to the project and record exactly what was checked.

## 2. DR-0025 — G2 validation strategy

Approve the following principles:

- Separate validation evidence into:
  - independent external reference,
  - partially independent numerical reference,
  - same-model/invariant checks,
  - regression checks.
- GMAT may count as an independent external oracle only when its setup is independently specified and documented while representing the same intended physical problem. Record all GMAT force-model, frame, constants, atmosphere, drag, mass, propagation, and relevant solver settings needed to reproduce the comparison.
- DOP853 is partially independent, not fully independent, because it can share the same force equations/constants.
- Do not reuse the M2 measured-order acceptance rule blindly.
- Apply numerical-order/convergence tests only where the mathematical assumptions behind the test are valid, particularly smooth configurations.
- For discontinuous/piecewise atmosphere behavior, use appropriate convergence/error/stability evidence rather than requiring an artificial RK4 fourth-order measurement across discontinuities.
- dt = 10 s remains PROVISIONAL.
- Do not approve M3 numerical acceptance thresholds during planning.
- Measure candidate timesteps during the designated measurement task after the physical models and reference setup exist.
- Thresholds must be proposed in a later Decision Request from measured evidence, with margin and rationale.
- Preserve frozen M1/M2 evidence and require perturbations-off regression to reproduce it exactly where the existing contracts require exact reproduction.
- Add an explicit historical correction note for VAL-0007 explaining the actual GM used by that GMAT run. Do not rewrite the historical measurement itself.

Close each Q-G2 item explicitly so that there are no accidental implied decisions.

## 3. DR-0026 — G3 force/scenario/event architecture

Approve D3 with these constraints:

- Introduce the proposed small immutable force-evaluation context containing the minimum shared runtime state needed by forces, including current total mass.
- Preserve the old force signature through an adapter so frozen M1/M2 behavior remains reproducible.
- Density is a separate component consumed by drag.
- PhysicsConfiguration must have deterministic canonical serialization and a SHA-256 identity.
- Model identifiers are explicitly versioned, e.g. zonal_j2@1.
- Scenario format v3 is additive and must not mutate historical scenario-v2 artifacts.
- Add PhysicsConfigured as proposed.
- Validation must fail closed when the expected physics identity does not match the active physics configuration.
- Force composition/order must be deterministic and documented.
- Do not introduce a general plugin framework in M3.
- Do not inject mutable mass directly into force implementations.
- Retain every historical physics/model version for as long as a frozen validation artifact or supported historical scenario depends on it. Do not choose an arbitrary time-based deletion period.
- A decay run ends at an explicitly defined event or model-validity boundary. Do not invent a universal re-entry altitude merely to close this DR. If its numerical definition still requires evidence, keep that subdecision OPEN.
- Write ADR-0009 after these architecture decisions are formally resolved.

Nothing in DR-0026 authorizes Rust, C, FFI, firmware, RTOS, real-time execution, or embedded deployment work.

## 4. Historical corrections

Record, without altering frozen evidence:

- SCI-0005's TT/TCG wording correction.
- VAL-0007's actual GMAT GM provenance.

Clearly distinguish:
- historical result,
- incorrect historical description,
- corrected interpretation,
- whether the correction changes any previous acceptance decision.

If either correction changes a prior acceptance decision, STOP and report it as a decision gate.

## 5. AT items and future flight architecture

Keep AT-1 through AT-7 OPEN for M3.

Preserve AC-1 as ACCEPTED:

Before software crosses into flight-runtime, embedded, firmware, or hardware execution, there must be an explicit architecture/runtime decision.

Do not make a Rust/C/FFI/RTOS/hardware decision in this task.

Do not merge research/flight-software-architecture into main. It remains research evidence unless separately authorized later.

## 6. Planning branch

After the documentation above is internally consistent:

1. Run all documentation checks.
2. Run the complete existing M1 and M2 regression/proof suites.
3. Confirm frozen M1/M2 artifacts, thresholds, goldens, reference snapshots, validation semantics, and acceptance logic were not modified or regenerated.
4. Commit the resolved planning checkpoint.
5. Run one independent Codex review focused on:
   - whether every owner decision above is represented correctly;
   - whether any M3 implementation was accidentally introduced;
   - whether historical M1/M2 evidence changed;
   - whether unresolved numerical decisions were accidentally converted into defaults;
   - whether the atmosphere-table treatment faithfully represents its source;
   - whether any Rust/embedded decision was accidentally made.

If Codex returns REQUEST_CHANGES, record the findings and STOP. Do not repair them automatically.

If it returns unconditional PASS and CI is green, report that the planning branch is ready to merge. Do not merge it unless already explicitly authorized by the instruction below.

## 7. Planning-branch merge authorization

If and only if:

- DR-0024/25/26 reflect the decisions above;
- all required correction notes exist;
- no prior M1/M2 acceptance decision changed;
- the independent review is an unconditional PASS;
- CI is green; and
- the diff remains planning/documentation/research evidence only,

then you are authorized to merge milestone-3-planning into main.

The merge does NOT declare M3 started and does NOT authorize M3 production implementation.

## 8. T0 authorization

After the planning merge succeeds, create a fresh M3 implementation branch from the new main and perform T0 only.

T0 is an implementation/research spike, not authorization for T1.

T0 must:

- establish executable reference configurations for the planned J2 and drag/atmosphere validation cases;
- verify the GMAT configurations actually represent the intended physical models;
- reproduce and explain the planning measurements where practical;
- exercise every atmosphere band boundary relevant to the model;
- quantify the effect of the source-model discontinuities;
- verify geodetic-height behavior;
- verify atmospheric-relative-velocity/Earth-rotation behavior;
- determine whether any unresolved G1/G2 assumptions need another Decision Request;
- verify perturbations-off compatibility with frozen M1/M2 behavior;
- collect evidence needed to make T1 safe to implement.

Do not establish final M3 acceptance thresholds in T0.
Do not regenerate M1/M2 goldens or references.
Do not implement production J2/drag architecture beyond the minimum isolated spike code required for T0.
Do not begin T1.

At the end of T0, run an independent review and stop at a checkpoint.

Report:

1. final planning decision matrix;
2. historical correction status;
3. planning review result;
4. planning merge commit;
5. T0 branch and commit(s);
6. every reference configuration tested;
7. measured results and discrepancies;
8. atmosphere-boundary findings;
9. M1/M2 regression status;
10. any new Decision Requests;
11. independent T0 review findings;
12. explicit recommendation: T1 READY or T1 BLOCKED.

Do not start T1 even if T0 passes.
````

### Instruction I-2: "M3 planning checkpoint continuation" (2026-10-15), sections 1–7
````text
Continue the TARS spacecraft simulator M3 planning checkpoint. **Do not begin T0, implement M3 code, merge the planning branch, or modify frozen M1/M2 acceptance artifacts.**

### 1. Record my decisions

**DR-0024 Q4 — APPROVED with constraints**

Use the Earth-fixed +Z axis as the common physical symmetry/rotation axis for J2, the reference ellipsoid, and atmospheric rotation.

Explicitly distinguish Earth-fixed and inertial coordinate representations. Use correct frame transformations when evaluating dynamics and atmospheric relative velocity. Record coordinate conventions and required frame-consistency tests.

**DR-0026 Q-G3-9 — APPROVED with constraints**

Retain the two-body specific-energy escape diagnostic as an approximation. Do not interpret it as an exact escape criterion in perturbed dynamics or as independent authorization for safety-critical actions.

**M3P2-F2 — CORRECTION AUTHORIZED**

The next Codex review must receive the complete applicable instructions, including sections 1–8, rather than the truncated sections 1–5.

**M3P2-F3 — CORRECTION AUTHORIZED**

Correct the lowest atmospheric band explanation. A base-height discrepancy can affect density throughout the band. Quantify the consequences and preserve the historical finding.

### 2. Resolve DR-0027

**Termination altitude — APPROVED WITH CONDITIONS**

Require an explicit per-scenario termination altitude with no implicit default. Define its units as meters and its altitude convention as geodetic. At T0, propose and validate permitted ranges, event-crossing behavior, and interactions with atmospheric-domain boundaries. Do not invent or approve a universal numerical altitude.

**Atmosphere table — CONDITIONAL APPROVAL**

Pin the selected GMAT table verbatim as the initial reference, preserving its source identity and checksum.

Document the three disputed cells, the absent 1000 km row in the compared Vallado source, and the uncertainty about the printed edition.

Do not silently repair or substitute table values. Do not claim definitive agreement with the printed textbook without checking it.

Define domain behavior explicitly, including what happens when the simulator reaches an unsupported altitude.

### 3. Preserve existing approvals

Keep DR-0024, DR-0025, and DR-0026 approvals unchanged except for the newly authorized clarifications.

Keep deferred decisions deferred. Do not assign defaults to OPEN or DEFERRED questions.

Per-sample drag telemetry Q-G3-7 remains NOT AUTHORIZED.

Preserve the D3 model-version retention rule and ADR-0009.

Do not alter frozen M1/M2 thresholds, references, goldens, or validation semantics.

Preserve the historical SCI-0005 and VAL-0007 corrections as append-only records.

### 4. Apply documentation corrections

Resolve M3P2-F1, F2, and F3 in the planning documentation and decision registers.

For each finding, record:
- Original finding and severity
- Authorized decision
- Exact correction
- Evidence supporting the correction
- Any residual uncertainty
- Whether the correction changes an acceptance decision

Do not erase or rewrite historical review findings.

### 5. Validation

Run the existing applicable tests, M1 golden checks, M2 Proof, and cross-platform checks.

Confirm that the planning diff remains documentation-only.

Verify that every approved, open, and deferred decision is represented consistently across the decision matrix, science registers, ADRs, and planning documents.

Do not weaken any validation gate to obtain a PASS.

### 6. Independent review

Submit the complete applicable instructions, sections 1–8, and the corrected planning artifacts to Codex.

Request an independent review focused on:
1. Decision authorization and traceability
2. Coordinate-frame and physics consistency
3. Atmospheric table provenance and numerical consequences
4. Termination and domain-boundary behavior
5. Preservation of M1/M2 validation contracts
6. Completeness of T0 prerequisites
7. Absence of unauthorized implementation or scope expansion

Require Codex to return an explicit PASS or REQUEST_CHANGES with categorized findings and supporting evidence.

If Codex returns REQUEST_CHANGES, record the findings and stop. Do not automatically repair them or begin another review round.

### 7. Stop condition

If Codex returns an unconditional PASS and all required CI jobs are green, prepare the planning checkpoint acceptance report.

Report:
- Branch and commit SHA
- Decision matrix status
- Resolved findings
- Remaining deferred questions
- Test and CI evidence
- Diff scope
- Independent review verdict
- Whether the planning branch is ready to merge
- Whether T0 prerequisites are satisfied

Do not merge or begin T0 until I explicitly approve the checkpoint.

If a decision remains ambiguous, create a new decision request rather than assuming approval.
````

### Instruction I-3: "M3 Planning — Resolve Review 03 and DR-0028" (2026-10-15), sections 1–8
````text
# M3 Planning — Resolve Review 03 and DR-0028

Continue the TARS spacecraft simulator M3 planning checkpoint.

**Current baseline**
- Branch: `milestone-3-planning`
- Reported HEAD: `8496ac1`
- Latest review: `docs/reviews/M3-planning-review-03.md`
- Codex review 03: REQUEST_CHANGES, 2 MINOR, 0 MAJOR, 0 BLOCKER
- Planning branch remains unmerged.
- M3 implementation has not started.

## 1. Authorization

I authorize only:

1. Correcting M3P3-F1.
2. Correcting M3P3-F2.
3. Resolving DR-0028 using J-ax-1, subject to the constraints below.
4. Updating directly affected planning documentation, tests specifications, decision matrices and traceability records.
5. Running planning validation and one new independent Codex review.

Do not merge, begin T0, implement M3 physics, modify approved M1/M2 behavior, or change pinned thresholds, reference baselines or goldens.

## 2. DR-0028 — Approved decision

APPROVED: J-ax-1.

For M3, use a simplified nonrotating Earth-axis-aligned reference model.

Requirements:

- Define the model's +Z axis as coincident with the selected Earth symmetry/spin axis by assumption.
- Treat this axis as fixed in the M3 inertial frame.
- Do not introduce time-dependent Earth orientation, precession, nutation or polar motion.
- Do not require an Earth rotation angle for M3.
- Do not identify this simplified frame as a physically accurate rotating Earth-fixed terrestrial frame.
- Document its approximation, limitations and implications for future mission capabilities.
- Preserve a clear architectural extension point for future Earth-fixed frame transformations.

No additional Earth-orientation implementation is authorized.

Record this decision in DR-0028 and the decision matrix, preserving append-only historical records.

## 3. Correct M3P3-F1

The current velocity-transformation formula is incomplete for time-dependent frame rotations.

Document the general relationship:

r_B = R(t) r_A

v_B = R(t) v_A + dR(t)/dt · r_A

Clarify that the simplified J-ax-1 model uses a constant identity rotation between its defined coincident axes, making the derivative term zero.

Distinguish this explicitly from future rotating or pole-of-date frames, where the derivative term generally cannot be omitted.

Update the applicable FC-1 through FC-9 frame-consistency specifications.

Include checks that would detect incorrectly omitting the derivative term in a future time-dependent rotation, without introducing that rotation into M3 implementation scope.

Do not weaken existing frame-consistency requirements.

## 4. Correct M3P3-F2

Repair the amendment-log traceability defect.

- Preserve the complete withdrawn DR-0024 Q4 text verbatim.
- Remove the ellipsis-based abbreviation from the historical quotation.
- Preserve the original decision history.
- Record the correction as an append-only amendment.
- Confirm the original and amended records remain distinguishable.

Do not silently rewrite historical decisions.

## 5. Validate planning consistency

Review DR-0024 through DR-0028, the decision matrix, science register, validation register, frame-consistency specifications and M3 planning dependencies.

Verify:

- Approved decisions are represented consistently.
- OPEN items remain OPEN.
- DEFERRED items remain DEFERRED.
- NOT AUTHORIZED items remain unauthorized.
- No default values have been invented.
- Previously approved physics constants and atmosphere constraints remain unchanged.
- T0, T1 and T2 dependencies are accurately represented.
- The scope remains planning and documentation only.

Check the actual repository state before making changes. Because the branch is checked out in another worktree, do not force checkout, overwrite worktree state or force-push.

Confirm the latest CI run on `8496ac1` has completed and report its individual job conclusions.

## 6. Independent review

After local validation:

1. Commit the authorized corrections.
2. Push the planning branch safely.
3. Run one fresh independent Codex review against the updated commit.
4. Provide the complete governing instructions, decision constraints, relevant diffs and review history.
5. Require Codex to evaluate physical correctness, mathematical consistency, historical traceability, decision completeness and scope compliance.

Do not summarize away any previous reviewer findings.

If Codex returns REQUEST_CHANGES, record every finding and stop without implementing further fixes.

If Codex returns an unconditional PASS, prepare a planning acceptance report for my review.

## 7. Stop conditions

Regardless of review outcome:

- Do not merge the planning branch.
- Do not begin T0.
- Do not start T1 or T2.
- Do not declare M3 planning accepted on my behalf.
- Do not change M1/M2 contracts, thresholds, reference baselines or goldens.
- Do not implement Earth rotation or additional frame physics.

## 8. Final report

Provide:

1. Final branch and commit SHA.
2. Exact files changed and why.
3. DR-0028 resolution and model limitations.
4. M3P3-F1 and M3P3-F2 dispositions.
5. Decision-matrix consistency results.
6. Local validation and completed CI results.
7. Independent Codex review verdict and findings.
8. Remaining OPEN/DEFERRED decisions and their blocking dependencies.
9. Whether the planning branch is ready for my acceptance.

Stop at the planning checkpoint and await my explicit authorization for the planning merge and, separately, T0.
````

### Instruction I-4: "M3 Planning — Review 04 Corrections and Final Verification" (2026-10-16), sections 1–7
````text
# M3 Planning — Review 04 Corrections and Final Verification

You are authorized to correct the two accepted MINOR findings from Codex review 04 and conduct one additional independent Codex review.

**This is not authorization to merge, begin T0, or implement M3.**

## 1. Authorized corrections

**M3P4-F1 — Ascending-node error bound**

Correct the statement claiming the ascending-node error is bounded by the pole offset.

Document that:
- Inclination error is bounded by the relative pole tilt.
- Ascending-node error can be amplified approximately by `tilt / sin(inclination)` for small tilts away from singular configurations.
- Near-equatorial orbits make the ascending node poorly conditioned or undefined.
- Preserve the numerical counterexample from review 04 and verify its assumptions.
- Clearly distinguish geometric bounds from approximation-based estimates.

Update DR-0028, SCI-0013, and any other affected references.

**M3P4-F2 — Local solar time**

Correct the claim that local solar time inherently requires an Earth-rotation angle.

Document that:
- Earth-rotation terms can cancel in the solar hour-angle relationship.
- M3 lacks the solar ephemeris and time convention needed to calculate meaningful local solar time.
- This remains outside M3 scope.
- No solar ephemeris, Earth-orientation provider, or local-solar-time implementation is authorized.

Update affected documents consistently.

## 2. Preserve approved decisions

Do not alter:
- DR-0028: APPROVED J-ax-1.
- The non-rotating Earth-axis-aligned model.
- The constant identity transformation in M3.
- Atmospheric co-rotation as a physical velocity-field model.
- Approved Earth constants, J2, atmosphere tables, or digests.
- DR-0024 coordinate conventions and validation requirements.
- Existing science and validation gates.
- Previously approved DR-0025 and DR-0026 decisions.

Preserve append-only decision history. Where a historical statement needs correction, use an explicitly linked amendment rather than silently rewriting historical evidence.

Do not promote OPEN, DEFERRED, or NOT AUTHORIZED decisions into approved status.

## 3. Validation

Before requesting Codex review:

1. Verify all references to the two corrected claims.
2. Check mathematical consistency and dimensional validity.
3. Confirm the numerical ascending-node example.
4. Verify DR-0028, DR-0024, SCI-0013, ADR-0009, the decision matrix, and M3 proposal remain consistent.
5. Confirm the changes are documentation-only.
6. Verify no approved contracts, thresholds, reference baselines, or validation semantics changed.
7. Run relevant documentation checks.

Record the validation evidence and exact commit SHA.

If validation fails, stop and report the failure without requesting Codex review.

## 4. Codex review 05

Request an independent review focused on:

- Correctness and completeness of M3P4-F1 and M3P4-F2.
- Regression against all earlier Codex findings.
- Consistency of the approved J-ax-1 model.
- Integrity of decision and science-assumption histories.
- Preservation of all M3 scope and authorization boundaries.
- Whether the planning package is ready for acceptance.

Provide Codex the relevant documents, previous review findings and dispositions, exact commit SHA, and diff.

Codex must independently verify the corrections rather than relying on their recorded dispositions.

The review may report any newly discovered correctness or consistency issue, regardless of severity.

Do not weaken acceptance criteria to obtain PASS.

## 5. Stop conditions

If Codex returns REQUEST_CHANGES:
- Record every finding and its severity.
- Do not implement further corrections.
- Do not run another review.
- Stop for my authorization.

If Codex returns unconditional PASS:
- Prepare a final M3 planning acceptance report.
- Include the review history, all findings and resolutions, decision status, validation evidence, CI status, remaining deferred decisions, and exact commit SHA.
- Explicitly identify which decisions remain blocking for T0, T1, and T2.
- Stop for my acceptance.

A PASS does not authorize a merge or implementation.

## 6. Git and scope

Work only on `milestone-3-planning`.

Preserve fast-forward-only pushes. Do not force-push.

Do not modify another worktree without authorization.

Do not merge to main.

Do not begin T0, T1, or T2.

Do not create M3 implementation code.

## 7. Final report

Return:

1. Corrections made and files affected.
2. Validation results.
3. Codex review 05 verdict and findings.
4. Decision and authorization matrix.
5. CI status for the final commit.
6. Exact branch and commit.
7. Remaining risks and blockers.
8. Whether M3 planning is ready for my acceptance.

**Stop at the planning acceptance checkpoint.**
````

### Instruction I-5: "M3 Planning — M3P5-F1 Correction and Review 06" (2026-10-16), sections 1–7
````text
# M3 Planning — M3P5-F1 Correction and Review 06

You are authorized to correct M3P5-F1, strengthen the independent mathematical verification, and run one additional targeted Codex review.

This authorization does not permit merging, implementing M3, or starting T0, T1, or T2.

## 1. Correct M3P5-F1

In DR-0028, amendment 1, item 1, correct the two signed first-order formulas to match the approved rotation convention:

- Δi ≈ −δ cos(Ω − φ)
- ΔΩ ≈ +δ cot(i) sin(Ω − φ)

Preserve the historical formulas and add a clearly linked correction amendment, consistent with the append-only decision-history policy.

Verify that the signed formulas agree with the existing numerical example and with the coordinate transformation defined by DR-0024.

Do not change the approved J-ax-1 model, physical constants, thresholds, or scope.

## 2. Strengthen mathematical verification

The previous script reproduced the numerical example but did not independently verify the signed analytical formulas.

Correct this weakness.

Add verification that:

1. Computes the transformed orbital plane using the explicitly defined rotation matrix and frame conventions.
2. Independently derives inclination and ascending-node longitude from the transformed orbital angular-momentum vector.
3. Compares the signed analytical first-order approximations against finite-rotation numerical results.
4. Exercises positive and negative pole tilts.
5. Exercises multiple node longitudes and pole-tilt directions.
6. Checks both signs, not only absolute magnitudes.
7. Covers inclined, near-polar, and near-equatorial cases with appropriate singularity handling.
8. Verifies that approximation errors decrease at the expected order as tilt approaches zero.
9. Preserves the previously verified numerical example.
10. Fails if either signed formula is deliberately reversed.

The numerical oracle must not reuse the analytical formulas under test.

Clearly separate exact geometric properties from first-order approximations.

Do not invent numerical tolerances without documenting their derivation.

## 3. Regression and scope validation

Verify that:

- All previous Codex findings remain resolved.
- DR-0028 remains APPROVED J-ax-1.
- DR-0024 conventions remain consistent.
- SCI-0013 and the decision matrix remain consistent.
- The local-solar-time correction remains intact.
- No Earth-orientation provider or solar ephemeris is implemented.
- All OPEN, DEFERRED, and NOT AUTHORIZED items retain their status.
- All changes remain documentation-only, including verification scripts under docs/.
- No approved contracts, reference baselines, digests, thresholds, or validation semantics change.

Run relevant tests, documentation checks, and existing M1/M2 regression gates.

If validation fails, stop and report the failure.

## 4. Codex review 06

Request one independent, targeted review of:

- M3P5-F1 correction.
- Signed rotation conventions.
- Numerical oracle independence.
- Regression tests and mutation sensitivity.
- Preservation of previous review resolutions.
- Planning-package consistency and authorization boundaries.

Provide the exact reviewed commit, diff, previous review findings, and validation evidence.

Codex must check the signed formulas independently rather than accepting the new script's output as proof.

Codex may report any newly discovered correctness defect, regardless of severity.

Do not modify review criteria to obtain PASS.

## 5. Stop conditions

If Codex returns REQUEST_CHANGES:

- Record the findings.
- Do not fix them.
- Do not start review 07.
- Stop for my decision.

If Codex returns unconditional PASS:

- Confirm CI is green on the exact final candidate commit.
- Prepare the final M3 planning acceptance report.
- Include all review findings and dispositions, remaining deferred decisions, validation evidence, and commit identifiers.
- Clearly state whether planning is ready for acceptance.
- Stop for my explicit authorization.

Do not merge or begin T0.

## 6. Git requirements

Remain on `milestone-3-planning`.

Use fast-forward-only pushes.

Preserve the other worktree.

Keep all changes within the authorized documentation and verification scope.

Do not merge to main.

## 7. Final response

Report:

1. Exact formula corrections.
2. Independent verification methodology.
3. Signed regression and mutation-test results.
4. Full validation results.
5. Codex review 06 verdict.
6. CI status on the final commit.
7. Remaining risks and unresolved decisions.
8. Whether the planning package is ready for acceptance.

Stop at the planning acceptance checkpoint.
````

## Review focus (required)
1. **M3P5-F1 correction.**
   - Derive the first-order Δi and ΔΩ yourself under the convention stated in DR-0028 "Resolution amendment 2":
     - Rot is active right-hand;
     - B's axes are A's axes rotated by +δ about e = (cos φ, sin φ, 0);
     - v_B = R v_A with R = Rot(e, −δ);
     - i = atan2(√(h_x² + h_y²), h_z) and Ω = atan2(h_x, −h_y);
     - differences are B minus A.
   - Are the corrected signs right? Is the derivation right?
   - Is the convention consistent with DR-0024 "Q4 coordinate conventions, revision 2" (r_B = R r_A) and with the review-04 example (R = Rx(−0.15°))?
   - Check the signed exact cases in the amendment: the line-of-nodes tilt (Δi = −δ, ΔΩ = 0 exactly) and the φ = Ω − 90° closed form ΔΩ = atan(sin δ cot i), cos i_B = cos δ cos i.
   - Is the history preserved? Amendment 1's original formulas must be kept, with a linked pointer.
   - Are magnitudes, bounds and amendment 1 item 2 (local solar time) unchanged?
2. **Signed rotation conventions.** Is every place that states or uses the convention consistent? This covers DR-0028 amendments 1 and 2, both scripts, the review records and SCI-0013. Look for any remaining active/passive or sign inconsistency.
3. **Numerical oracle independence.** Read `dr0028_node_signed_verification.py`. Does the oracle (`finite`) avoid the formulas under test? Are the rotation matrix and the element definitions correct? Are the exact properties E1–E6 truly exact and correctly checked?
4. **Regression tests and mutation sensitivity.**
   - Run the script and confirm exit 0 and a byte-identical JSON.
   - Introduce your own mutations of the formulas under test, at least reversing each sign separately, and confirm the script exits 1.
   - Assess:
     - the grid coverage: inclined, near-polar and near-equatorial orbits, both tilt signs, node longitudes, tilt azimuths;
     - the step scaling and the near-equatorial singularity handling;
     - the order test (p ≥ 1.5);
     - the noise and significance tolerances, and whether their derivations are documented and sound.
   - Could a wrong formula pass? Could the tests pass vacuously, for example through samples silently excluded?
5. **Preservation of previous review resolutions.** All findings M3P-F1…M3P5-F1 must remain recorded with their dispositions, and their corrections must be intact.
   - Check `git diff -U0 cf0e24f..HEAD` for removed lines: only index or status cells may change.
   - Register lines existing at `d92ab89` must be unchanged.
6. **Planning-package consistency and authorization boundaries.**
   - DR-0028 remains APPROVED J-ax-1, with the identity transformation and co-rotation as air motion.
   - DR-0024 conventions, FC-1…FC-10, the constants, the atmosphere table and its digests are unchanged.
   - SCI-0013, the decision matrix, the M3 proposal and the milestones README are consistent.
   - The scope is `docs/` only.
   - No M1/M2 contract, threshold, reference, golden or validation semantics changed.
   - No Earth-orientation provider, solar ephemeris or local-solar-time implementation exists.
   - No OPEN, DEFERRED or NOT AUTHORIZED item has been promoted. These include DR-0027 A-4, A-5, A-6, A-s and B-4; Q-G2-1, 5, 6 and 7; the Q9 values; and Q-G3-7.
   - No merge, T0, T1 or T2 work.
7. **Readiness.** Is the planning package, as documentation evidence, ready to be presented to the Tech Lead for planning acceptance? Which decisions still block T0, T1 and T2?

## Output
Your final message, in Markdown. One block per finding, numbered from M3P6-F1:

### M3P6-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Category:** Physical correctness | Mathematical consistency | Verification adequacy | Historical traceability | Decision completeness | Scope compliance
**Where:** file and section
**Claim:** ...
**Evidence:** ... (quote the text, show the computation or the command and its output)
**Suggested resolution:** ...

**Severity scale:**
- **BLOCKER:** must not go to the Tech Lead as is.
- **MAJOR:** a substantive error or gap.
- **MINOR:** a local inaccuracy that should be corrected.
- **NOTE:** an observation needing no change.

Then a **Summary** with exactly one verdict:
- **PASS:** no BLOCKER, MAJOR or MINOR finding; NOTEs only, or none.
- **REQUEST_CHANGES:** any BLOCKER, MAJOR or MINOR finding.

List what you verified, including the commands run and recomputed results. State in one line whether the planning package is ready to be presented to the Tech Lead for planning acceptance as documentation evidence.
