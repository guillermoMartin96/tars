You are an independent reviewer from a separate provider; you did not write these documents. This is the TARS Milestone 3 **planning checkpoint, review round 05**. The Tech Lead authorized the corrections of review 04's two findings, and the implementer has recorded them. This review also assesses whether the planning package is ready for acceptance. No M3 implementation exists or is authorized.

The snapshot is the current directory: a git clone of the planning branch at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/`, which is git-ignored.

**Verify independently.** Recompute and re-derive the corrections yourself; do not rely on the recorded dispositions or the implementer's evidence. You may report any newly discovered correctness or consistency issue of any severity, anywhere in the planning package. Acceptance criteria are not relaxed for this round.

## Context and review history
- **Baseline:** `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M1/M2 accepted, CLOSED). Whole-branch scope: `git diff d92ab89..HEAD`.
- **Changes under review:** `git diff 16b6888..HEAD`.
  - The correction commit is `b411b5f784830f6bb21c3840e9baa9aa1cb7cdbe`. The commit after it adds only this prompt.
  - Earlier rounds: `git diff 8496ac1..16b6888` (round 04 corrections, `58f0d18`), `git diff 23bafd2..8496ac1` (round 03) and `git diff 6dbb22b..23bafd2` (round 02).
- **Previous reviews.** Read each record and its raw output in full; every earlier finding must remain recorded with its disposition.
  - **Round 01** (`docs/reviews/M3-planning-review-01.md`, raw `raw/M3-planning-codex-review01.md`):
    - M3P-F1 MAJOR, density table discontinuous, not C0;
    - M3P-F2 MINOR, drag along-track sign;
    - M3P-F3 MINOR, decay-oracle approximations;
    - M3P-F4 MINOR, rejected atmosphere cutoff in the task plan;
    - M3P-F5 MINOR, rotation-rate difference understated.
    - All ACCEPTED and corrected.
  - **Round 02** (`docs/reviews/M3-planning-review-02.md`, raw `raw/M3-planning-codex-review02.md`):
    - M3P2-F1 BLOCKER, unaddressed choices recorded as approved: ACCEPTED, then resolved by owner decisions;
    - M3P2-F2 BLOCKER, T0 authorization: REJECTED_WITH_REASONING, with the review prompt corrected;
    - M3P2-F3 MINOR, lowest band: ACCEPTED, corrected.
  - **Round 03** (`docs/reviews/M3-planning-review-03.md`, raw `raw/M3-planning-codex-review03.md`):
    - M3P3-F1 MINOR, velocity transformation needs a fixed-pole qualification;
    - M3P3-F2 MINOR, amendment log abbreviated the withdrawn Q4 attribution.
    - Both ACCEPTED and corrected in `58f0d18`.
  - **Round 04** (`docs/reviews/M3-planning-review-04.md`, raw `raw/M3-planning-codex-review04.md`):
    - M3P4-F1 MINOR, the pole tilt does not bound the ascending-node error;
    - M3P4-F2 MINOR, local solar time does not inherently need an Earth rotation angle.
    - Both ACCEPTED. Corrected in `b411b5f`; see "Resolution of findings" in that record.
- **Files changed in `b411b5f`:**
  - DR-0028: a status-header line, a pointer under each of the two corrected bullets, and an appended "Resolution amendment 1";
  - DR-0024: one amendment-log entry about the §11 node sentence;
  - `docs/science/assumptions.md`: SCI-0013 "status update 3";
  - `docs/reviews/M3-planning-review-04.md`: appended resolution;
  - `docs/milestones/M3-decision-matrix.md`, `M3-proposal.md`, `README.md`: status;
  - `docs/science/experiments/m3-planning/`: new `dr0028_node_sensitivity.py`, its results JSON and a README entry.
- **Source cited for the local-solar-time correction:** [McK] D. P. McKinley, "Long Term Mean Local Time of the Ascending Node Prediction", NTRS 20080012667, https://ntrs.nasa.gov/api/citations/20080012667/downloads/20080012667.pdf (the implementer's copy has sha256 `542421d3999804578c1bdd61ecb40a066937487448cf0cc925da25adf49f475c`). If you have no network access, say so and assess the derivation on its own.

## The Tech Lead's governing instructions (complete and verbatim)
Each later instruction governs where it differs from an earlier one. I-4 is the latest.

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

## Review focus (required)
1. **Correctness and completeness of M3P4-F1** (DR-0028 "Resolution amendment 1" item 1, SCI-0013 status update 3, the DR-0024 amendment-log entry).
   - Derive the exact bound |Δi| ≤ δ and the first-order estimates yourself: Δi ≈ δ cos(Ω − φ), node-point shift ≈ δ|sin(Ω − φ)|/sin i, ΔΩ ≈ −δ cot i sin(Ω − φ). Check their signs, validity conditions and dimensions.
   - Are geometric bounds clearly distinguished from approximations?
   - Is the relationship between the I-4 phrase "tilt / sin(inclination)" and the node-longitude measure δ|cot i| stated correctly?
   - Is the longitude-origin dependence correct?
   - Recompute the review-04 example and check that its stated assumptions match the computation.
   - Check the near-equatorial statements.
   - Run `python -I docs/science/experiments/m3-planning/dr0028_node_sensitivity.py review_scratch/node.json` and compare the output with the committed JSON. Inspect the script for errors.
   - Is the trajectory statement limited to what was measured?
   - Are all other references to the corrected claims, anywhere in `docs/`, corrected or correctly left as written?
2. **Correctness and completeness of M3P4-F2** (item 2).
   - Verify the hour-angle derivation and the cancellation of θ.
   - Is the MLTAN definition quoted accurately?
   - Is the list of what M3 lacks accurate: solar ephemeris, a time convention connecting simulation time to the ephemeris (with SCI-0007's TT-labelled epoch not consumed by any M3 model), and a mean-Sun convention?
   - Are the remaining longitude, ground-track and visibility restrictions still valid?
   - Are scope and non-authorization stated as I-4 requires?
3. **Regression against all earlier findings.** M3P-F1…F5, M3P2-F1…F3, M3P3-F1/F2 and M3P4-F1/F2 must remain recorded with their dispositions, and their corrections must be intact.
4. **Consistency of the approved J-ax-1 model.** The decision, the constant identity transformation, atmospheric co-rotation as air motion, FC-1…FC-10, constants, the atmosphere table and its digests must be unchanged. DR-0028, DR-0024, SCI-0013/0014/0017, ADR-0009, the decision matrix and the M3 proposal must be mutually consistent.
5. **Integrity of decision and science-assumption histories.** All changes since `16b6888` must be append-only or index/status cells: check `git diff -U0 16b6888..HEAD` for removed lines. Register lines existing at `d92ab89` must be unchanged (additions only). Superseded statements must be kept and explicitly linked to their amendments.
6. **Scope and authorization boundaries.**
   - `git diff d92ab89..HEAD --stat` must show only `docs/`.
   - No M1/M2 contract, threshold, reference, golden or validation semantics may change.
   - No M3 code, T0/T1/T2 work, merge, Earth-orientation, solar-ephemeris or local-solar-time implementation.
   - No OPEN, DEFERRED or NOT AUTHORIZED item may be promoted. These include DR-0027 A-4, A-5, A-6, A-s and B-4; Q-G2-1, 5, 6 and 7; the Q9 values; and Q-G3-7.
7. **Readiness.** Is the planning package, as documentation evidence, ready to be presented to the Tech Lead for planning acceptance? Which decisions still block T0, T1 and T2?

## Output
Your final message, in Markdown. One block per finding, numbered from M3P5-F1:

### M3P5-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Category:** Physical correctness | Mathematical consistency | Historical traceability | Decision completeness | Scope compliance
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
