You are an independent reviewer from a separate provider; you did not write these documents. This is the TARS Milestone 3 **planning checkpoint, review round 03**. The Tech Lead has answered the findings of review 02 and resolved DR-0027, and the implementer has recorded those decisions and corrections. No M3 implementation exists or is authorized.

The snapshot is the current directory: a git clone of the planning branch at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/`, which is git-ignored.

## Context
- **Baseline:** `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M1/M2 accepted, CLOSED).
- **Previous reviews:** round 01 (`docs/reviews/M3-planning-review-01.md`) and round 02 (`docs/reviews/M3-planning-review-02.md`; raw output and prompt in `docs/reviews/raw/`).
  - The review 02 prompt gave the reviewer only sections 1–5 of the first instruction. **This prompt gives both instructions complete and verbatim** (Tech Lead's correction of M3P2-F2).
- **What changed since review 02:** `git diff 23bafd2..HEAD`. Whole-branch scope: `git diff d92ab89..HEAD`.
- **Key files:**
  - DR-0024 (Resolution: Q4 row, the new "Q4 coordinate conventions" subsection, the amendment log; §3.4 correction);
  - DR-0026 (Q-G3-9 row, notes, amendment log, §5.7 note);
  - DR-0027 (Resolution);
  - new DR-0028;
  - ADR-0009 (items 14–16);
  - `docs/science/assumptions.md` (status updates appended to SCI-0013, 0014, 0015, 0017);
  - `docs/milestones/M3-decision-matrix.md` (new), `M3-proposal.md`, `README.md`;
  - the appended "Resolution of findings" in `docs/reviews/M3-planning-review-02.md`;
  - `docs/science/experiments/m3-planning/q10_residual_consequences.py` and its results.
- **Q10 inputs:** the per-row values of both atmosphere sources are in `docs/science/experiments/m3-planning/q10_table_check_results.json`. The author's file is `software/misc/pascal/ATMOSEXP.DAT` in https://github.com/CelesTrak/fundamentals-of-astrodynamics at commit `49df0479c950917c0a2c5ac31f2db6477bba57f6`; fetch it if you have network access.
- **Validation evidence** for this commit is recorded by the implementer outside the snapshot. You may re-run any check, for example `PYTHONPATH=src .venv/bin/python -m pytest -q`, `.venv/bin/python toolbox/validators/cross_platform.py` or `.venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`. Write any output only under `review_scratch/`.

## The Tech Lead's applicable instructions (complete and verbatim)
### Instruction I-1: "M3 planning decision checkpoint" (2026-10-15), sections 1–8
Sections 6–8 are partly superseded by I-2 §7, which requires explicit approval before any merge or T0.

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

### Instruction I-2: "M3 planning checkpoint continuation" (2026-10-15), sections 1–7. It is the latest instruction and governs where it differs from I-1.
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

## Review focus (required)
1. **Decision authorization and traceability.**
   - Is every owner decision in I-1 and I-2 represented exactly, with nothing added, dropped, softened or strengthened, in the DR Resolutions, SCI entries, ADR-0009, the decision matrix and the milestone documents?
   - Is every OPEN, DEFERRED or NOT AUTHORIZED item kept so, with no default? Examples: DR-0028; DR-0027 A-4, A-5, A-6, A-s, B-4; Q-G2-1, 5, 6, 7; Q9 values; Q-G3-7.
   - Was creating DR-0028, rather than reading the Q4 approval as J-ax-1, justified by the decision text?
   - Are withdrawn attributions preserved verbatim (amendment logs) rather than erased?
2. **Coordinate-frame and physics consistency.**
   - Are the Q4 coordinate conventions (inertial vs Earth-fixed representations, R(t), v_EF = R(v − ω × r), ω along +Z) correct and internally consistent?
   - Is the axisymmetry claim (J2, geodetic height and v_rel independent of the rotation angle about a shared +Z) correct?
   - Are the frame-consistency tests FC-1…FC-9 sufficient and correctly stated, including the signs in FC-5?
   - Is the Q-G3-9 constraint described correctly (what ε = v²/2 − μ/r omits)?
3. **Atmospheric table provenance and numerical consequences.**
   - Recompute the M3P2-F3 ratio exp(0.010/7.249), the 25 km jump under the author's base altitude, the 900 km scale-height effect and the above-1000 km divergence.
   - Check that the disputed cells, the absent 1000 km row, the printed-edition uncertainty and the pinned digest are stated accurately, and that no record claims agreement with the printed textbook or silently repairs a value.
4. **Termination and domain-boundary behaviour.**
   - Does the DR-0027 Resolution implement the owner's conditions exactly: explicit per-scenario value, metres, geodetic, no implicit default, no universal number; ranges, crossing and boundary interactions to be proposed at T0; unsupported-altitude behaviour defined explicitly, not by default?
   - Is the withdrawal of the "top band applies" statement correct and complete?
5. **Preservation of M1/M2 validation contracts.**
   - `git diff d92ab89..HEAD --stat` must show only `docs/`.
   - Existing lines of `docs/science/assumptions.md` and `docs/science/validation.md` relative to `d92ab89` must be unchanged (additions only).
   - The SCI-0005 and VAL-0007 correction notes must be unchanged since review 02.
   - No threshold, reference, golden or validation semantics may be altered.
6. **Completeness of T0 prerequisites.** Given I-1 §8 and I-2 §7: is everything T0 needs decided or explicitly assigned to T0? Is anything that T0 needs still missing, ambiguous or blocking? Do the records state correctly that T0 has not started and needs the Tech Lead's explicit approval?
7. **Absence of unauthorized implementation or scope expansion.** No M3 code, no T0 work, no merge, no Rust/C/FFI/RTOS/embedded decision. AC-1 accepted; AT-1…AT-7 open. The new research script must be a planning artifact only.

## Output
Your final message, in Markdown. One block per finding, numbered from M3P3-F1:

### M3P3-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Category:** one of the seven focus areas above (by name)
**Where:** file and section
**Claim:** ...
**Evidence:** ... (quote the text, show the computation or the command and its output)
**Suggested resolution:** ...

**Severity scale:**
- **BLOCKER:** must not go to the Tech Lead as is. Examples: a misrepresented owner decision, a hidden M1/M2 change, implementation introduced, a decision taken on the owner's behalf.
- **MAJOR:** a substantive error or gap.
- **MINOR:** a local inaccuracy that should be corrected.
- **NOTE:** an observation needing no change.

Then a **Summary** with exactly one verdict:
- **PASS:** no BLOCKER, MAJOR or MINOR finding; NOTEs only, or none.
- **REQUEST_CHANGES:** any BLOCKER, MAJOR or MINOR finding.

List what you verified, with recomputed numbers. State in one line whether the planning branch is ready to be presented to the Tech Lead for checkpoint approval as planning/documentation evidence.
