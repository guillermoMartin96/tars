You are an independent reviewer from a separate provider; you did not write these documents. This is **M3 Planning Review 13** for the TARS Milestone 3 planning checkpoint. It reviews the correction of review 12's findings: M3P12-F1, the observation of oracle values injected inside the first-order check, and M3P12-F2, the classification of E6's sign assertion. It also covers every earlier tracked finding, the DR-0028 mathematics, M1/M2 preservation, and whether the planning package is ready to be presented for acceptance. No M3 implementation exists or is authorized.

The snapshot is the current directory: a git clone of the planning branch at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files, including mutated copies of scripts, only under `./review_scratch/`, which is git-ignored.

**Do not accept earlier conclusions.** Inspect the current files, attempt counterexamples, and verify independently with your own code. Earlier review verdicts and the implementer's evidence are inputs to check, not facts. You may report any newly discovered defect of any severity. For every new defect, give a concrete counterexample wherever feasible: the edit or input, the command, and its output. Acceptance criteria are not relaxed: a PASS must be unconditional.

## Commits under review
- **Baseline:** `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M1/M2 accepted, CLOSED). Whole-branch scope: `git diff d92ab89..HEAD`.
- **Review 12** ran at `5b12eece4d952450fc47a13c75059ef748fc007e`; its recording commit is `142b9df3937ac95311f6608159cbae751857c269` (the I-12 baseline, which I-12 §2 required `origin/milestone-3-planning` to be at; verified).
- **The correction:**
  - `1cef6ab` changes the verification script, the mutation check, the harness regression demonstration and the assertion classification, and regenerates every results file;
  - `24c2d98` records the correction in the documents (DR-0028 amendment 9, the review 12 record's "Resolution of findings", the decision matrix, status files);
  - `602ede0` adds one paragraph to amendment 9 and four docstring lines to the mutation check, stating the scope of the exercise probe (no output changes);
  - the commit after it, HEAD, adds only this prompt. Its parent is `602ede0`, and its hash is stated in the review record.
- **The complete correction diff:** `git diff 142b9df..HEAD` (the prompt aside: `git diff 142b9df..602ede0`). Run it yourself; it is the authoritative diff. `git diff --stat 142b9df..602ede0` lists 15 files, all under `docs/`.

## Review history
Each round has a record `docs/reviews/M3-planning-review-NN.md` and a raw output `docs/reviews/raw/M3-planning-codex-reviewNN.md`. Read them. Every finding must remain recorded, with its disposition and its correction intact.
- **Rounds 01–09:** M3P-F1…F5, M3P2-F1…F3, M3P3-F1/F2, M3P4-F1/F2, M3P5-F1, M3P6-F1…F3, M3P7-F1, M3P8-F1, M3P9-F1…F3. All are dispositioned and corrected (DR-0028 amendments 1–6).
- **Round 10** (`896d52d`): M3P10-F1 (MINOR) and M3P10-F2 (NOTE), corrected in amendment 7; review 11 found both NOT RESOLVED.
- **Round 11** (`c16b3b5`): M3P11-F1 and M3P11-F2 (MINOR), corrected in amendment 8; review 12 found both NOT RESOLVED, and with them M3P10-F1/F2.
- **Round 12** (`5b12eec`), REQUEST_CHANGES. Both findings were ACCEPTED and recorded, not applied, in `142b9df`. **The Review 12 raw findings are in `docs/reviews/raw/M3-planning-codex-review12.md`; read them in full.** In summary:
  - **M3P12-F1 (MINOR, unsound verification claim).** For an oracle value injected inside `check_formulas`, the probe observed only values reaching the finite validation (`nonfinite_reason`), which `check_formulas` skips for a component after its first invalid value. A first-step-only NaN, claimed as the all-steps NaN, was certified exercised (intended 600, missing 0) while 2 400 later values were correct.
  - **M3P12-F2 (MINOR, unsound verification claim).** E6-sign (`d_node > 0 and lin_node > 0`) was classified B; its first-order half was argued from the first-order grid, which never evaluates the formula at E6's tilt (0.15°). A formula sign reversal confined to 0.0026 < |δ| < 0.0027 rad passed the whole script with E6-sign removed.

## The correction (`1cef6ab`; DR-0028 "Resolution amendment 9")
- **M3P12-F1 (mutation check):**
  - `oracle_schedule` builds every sample at which `check_formulas` evaluates the oracle (3 000 = `SERIES_PER_COMPONENT` × `HALVINGS`) from the unmutated script, before the copy runs.
  - The probe runs the copy's `check_formulas` with an observing formula, which `check_formulas` calls at every step after the oracle value (and any injection) and before any validation. Each call is identified by the formula's own arguments; the copy's `num` is compared per component with the unmutated oracle at the scheduled sample; the defect's condition is evaluated on the scheduled sample with the unmutated script's names.
  - Counts: intended, unchanged, missing, unintended (per component), and per sample unobserved, duplicate, unscheduled. Exercise requires every scheduled sample observed exactly once, missing = unintended = 0, intended ≥ 1, and no exception.
  - On the unmutated script, every one of the 22 oracle-values predicates must observe its full schedule.
  - Every control now declares the reason its outcome must show (`CONTROL_REASONS`). Seven new controls (I-12 §3): first-step-only corruption (Δi and ΔΩ), partial-step corruption, missing intermediate observations, an incorrect observation count, last-step-only corruption, and correct all-step corruption. 30 controls in all.
  - `dr0028_node_signed_harness_regression.py` also runs every control against `5b12eec` (read from git, with its own probe). The five M3P12-F1 regression controls must fail there and pass now; the M3P11-F1 and M3P10-F1 regression controls must still fail at `c16b3b5` and `896d52d`.
- **M3P12-F2 (verification script and classification):**
  - E6's sign assertion is split into "…sign disagreement: oracle Delta Omega not > 0" and "…: first-order Delta Omega not > 0".
  - `exact_properties` gains `formula=formulas_amendment2`, used only by E6.
  - New built-in mutant `M3P12-F2_first_order_node_sign_reversed_in_e6_tilt_gap`: the first-order ΔΩ sign reversed for every |δ| in `E6_TILT_GAP` (the grid gap containing 0.15°, computed from the grid: (0.0025, 0.0039185) rad).
  - Classification: 19 assertions (E6-sign split into E6-sign-oracle, B, and E6-sign-first-order, A), 12 A / 4 B / 3 C / 0 D. The B premises of W1, W4 and E6-value are checked at the same input as their assertion (W1: same result, same loop iteration, from the syntax tree; W4: same inputs; E6-value and E6-sign-oracle: same oracle call, all five arguments). A formula mutant classified A must also produce 0 failures on the first-order grid. Review 12's counterexample is run through the entrypoint before (`5b12eec`) and after.
- **The complete DR-0028 amendment chain** is in `docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md`: the Resolution, then amendments 1–9 at the end. Read it in full.
- **Decision and authorization state:** the current decision matrix `docs/milestones/M3-decision-matrix.md` (it indexes DR-0024…DR-0028 and every review finding); `M3-proposal.md`; ADR-0009; and `docs/science/assumptions.md` (SCI-0013/0014/0017).

## Validation evidence (implementer), for you to check, not to accept
- **Full M1 Proof, isolated clone at `24c2d98`: overall PASS** (`UV=~/Library/Python/3.9/bin/uv bash toolbox/scripts/run_m1_proof.sh`; 9 steps, all exit 0): uv sync --locked, ruff check, ruff format --check, full pytest (1185 passed, 0 failed, 0 skipped; 3 warnings), cross-process determinism, cross-platform, m1_proof, the GMAT M1 comparison, run_mission.
- **Full M2 Proof, same clone: overall PASS** (`run_m2_proof.sh`; 20 steps, all exit 0):
  - uv sync --locked, the m2 cross-platform record, ruff check and format, full pytest (1185 passed, 0 failed, 0 skipped);
  - M1 determinism and cross-platform, m1_proof and the GMAT M1 comparison;
  - M2 determinism for four scenarios, the GMAT M2 comparison, the reference-snapshot verify-baseline (DR-0021), m2_proof (228 PASS, 0 FAIL: O1–O9, contract, golden cross-platform), and run_mission for four scenarios.
  - `602ede0` differs from `24c2d98` only in one DR-0028 paragraph and four docstring lines of the mutation check; the Proof was not rerun for it, but CI was (below).
- **Regenerated Proof evidence differs only in run metadata** (revision, branch, date, uv environment lines, temporary paths, `tree_clean`, `sha256`). With `revision`, `tree_clean` and `sha256` removed, `m2_final_states_record.json` is identical to the committed record. The M2 run reports `tree_clean: false` only because it ran in the same clone right after the M1 run had rewritten M1's evidence log.
- **Pinned references and goldens, unchanged since `d92ab89`** (sha256):
  - `proof/references/m1_final_state.json` c1a5e01be5ae1d7fa52b00ffe6e74a59fbd0b38f0618b4674f59fa31cdc3c45a;
  - `proof/references/m2_final_states.json` dc3baf7abb209a11ca463b9ca5001ce886c62b92b191ac76249d32924aa951dc (equal to `APPROVED_M2_GOLDEN_SHA256`);
  - `toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz` a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b;
  - `toolbox/references/gmat/m2/APPROVED_DIGESTS.json` f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585;
  - `toolbox/references/gmat/m1_two_body_report.txt` 9ac597c6922d3c8d1c089add3f22a081aa69c20fbfa56181f12768d36f15fd71.
  `git diff d92ab89..HEAD -- src tests toolbox scenarios proof` is empty.
- **M3 planning verification suite, worktree at `24c2d98`:** each of the five experiment tools ran twice, with byte-identical outputs and exit 0 both times; the mutation check was rerun at `602ede0` with output byte-identical to the committed results.
  - verification: PASS; 48 built-in mutants, each exercised and rejected by its designated checks;
  - mutation check: PASS. 109 attempted, 109 validly exercised, 109 detected for the intended reason; invalid mutation setup, process failure, normal execution, unexpected exception and rejected for another reason are each 0. 30/30 controls with their declared category, exercise result and reason. 0 of 77 direct predicates met by the unmutated script; 22 of 22 oracle schedules fully observed there;
  - sweep: 36 sites, 29 detected, 7 surviving (W1, W3, W4, W6, E2a, E6-value, E6-sign-oracle), 0 exceptions;
  - classification: PASS, 19 assertions, 12 A / 4 B / 3 C / 0 D, inventory matches the 18 survivors at `896d52d`; review 12's E6 counterexample: PASS at `5b12eec` with E6-sign removed, FAIL now through the first-order E6 message alone, and removal of E6-sign-first-order detected;
  - regression demonstration: PASS. The five M3P12-F1 regression controls fail at `5b12eec`; the four M3P11-F1 controls at `c16b3b5`; the five M3P10-F1 controls at `896d52d`; all 30 controls pass now.

    Further checks:
    - against `5b12eec`, no pre-existing verification output value changed or was removed; the 23 differences are added keys, all in the new mutant's entry. In the mutation check output only the 22 oracle-values observations (and their outcome texts), the exercise criterion and the control counts changed;
    - AST: in the verification script only `exact_properties` (formula parameter, docstring, split sign assertion), `defect_scaled` (optional `where`), `EXACT_MUTANTS`, the `DEFECTS.update` call and the docstring changed; `finite`, `formulas_amendment2`, `wrap`, `wrap_tests`, `check_formulas`, `nonfinite_reason`, `noise`, `step_scale`, the grid, `SIGNIFICANT`, `P_MIN`, `MIN_VALID_SAMPLES` are unchanged;
    - Ruff check and format pass; relative links in changed Markdown files, 0 broken; docs-only against `d92ab89`; registers `docs/science/assumptions.md` 218/0 and `docs/science/validation.md` 43/0 against `d92ab89`, unchanged since `142b9df`.
- **CI for `602ede0`:** run 39084190524, workflow status completed, conclusion success. Each of the four jobs completed with conclusion success: check ubuntu-latest (117547212389), check macos-latest (117547212242), check macos-15-intel (117547212343), m2-cross-platform (117557583723). An earlier run for `24c2d98` (39084025411) is superseded by it. You may not have network access.

## The Tech Lead's governing instructions (complete and verbatim)
Each later instruction governs where it differs from an earlier one. I-12 is the latest.

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

### Instruction I-6: "Continue M3 planning on `milestone-3-planning` from commit `dcabcb2`" (2026-10-16), sections 1–6
````text
Continue M3 planning on `milestone-3-planning` from commit `dcabcb2`.

I authorize corrections to M3P6-F1, M3P6-F2, and M3P6-F3, followed by exactly **one independent Codex review (review 07)**.

This is a narrowly scoped planning-correction authorization. It is **not** M3 planning acceptance, T0 authorization, or permission to begin implementation.

### 1. Correct the three findings

**M3P6-F1 — Domain of the line-of-nodes tilt claim**

- Preserve the existing text and append a clearly linked correction.
- State the exact domain in which the claimed inclination behavior holds, including the applicable rotation-sign and inclination conventions.
- Explain what happens when the inclination crosses an equatorial singularity or reaches an endpoint.
- Add tests for interior, crossing, and endpoint cases, including the counterexample `i = 2°`, `δ = 5°`.
- Distinguish exact geometric identities from first-order approximations.

**M3P6-F2 — Assert the 180° node discontinuity**

- Replace observation-only behavior with executable assertions.
- Assert the expected node-longitude jump under the documented convention.
- Use an explicitly justified numerical tolerance.
- Require a nonzero minimum number of qualifying crossing cases, so a vacuous test cannot pass.
- Include positive and negative tilt directions where applicable.
- Test that disabling the discontinuity assertion causes validation to fail.

**M3P6-F3 — Angle-wrapping endpoint convention**

- Make the wrapping implementation consistent with the documented interval `(−π, π]`.
- Explicitly test inputs at `−π`, `+π`, and equivalent angles differing by multiples of `2π`.
- Verify that boundary behavior is deterministic and documented.
- Add a mutation test proving that the previous `[−π, π)` implementation is rejected.

### 2. Preserve scientific and historical integrity

- Do not rewrite or delete prior amendments, review findings, or decision history.
- Use append-only corrections with explicit cross-references.
- Preserve the independently verified signed formulas:
  - `Δi ≈ −δ cos(Ω − φ)`
  - `ΔΩ ≈ +δ cot(i) sin(Ω − φ)`
- Preserve the passive coordinate-transformation convention.
- Do not change any approved physical constants, reference data, goldens, thresholds, or validation semantics outside the authorized corrections.
- Do not implement Earth orientation, solar ephemerides, local-solar-time output, or any M3 production code.

### 3. Validate before review

Run the relevant research scripts and mathematical verification suite.

Require:
- Exact and first-order checks pass.
- All mutation tests reject their intended defects.
- Each new regression test fails against its corresponding original defect.
- Ruff lint and format checks pass.
- Documentation links and registers remain consistent.
- M1 and M2 Proof gates remain unchanged and pass.
- GMAT comparisons and pinned golden/reference integrity remain intact.
- CI passes on all four required jobs.

If any validation fails, stop and report the failure. Do not request Codex review until the local validation gates pass.

### 4. Run exactly one independent Codex review

Label this **M3 Planning Review 07**.

Provide Codex with the complete relevant planning documents, amendment history, review 06 findings, verification scripts, and current diff.

Require Codex to:

1. Independently verify the mathematical correctness of all three corrections.
2. Reproduce the three original defects or demonstrate that the regression tests detect them.
3. Check singularities, angular wrapping, coordinate conventions, and signed first-order behavior.
4. Confirm the corrections introduce no new contradictions.
5. Verify preservation of approved decisions and scientific baselines.
6. Check for unauthorized implementation or scope expansion.
7. Return an explicit disposition for M3P6-F1, F2, and F3.
8. Identify any newly discovered findings with severity and concrete counterexamples.

A PASS must be unconditional. A review with unresolved findings is not an acceptance.

### 5. Stop conditions

If review 07 returns REQUEST_CHANGES:

- Record all findings and raw review output.
- Do not automatically fix them.
- Do not initiate review 08.
- Do not prepare an M3 planning acceptance report.
- Stop and request my authorization.

If review 07 returns an unconditional PASS:

- Record the review result and evidence.
- Prepare an **M3 planning acceptance candidate report** covering all open and deferred decisions, proof results, CI, commit hashes, and remaining authorization boundaries.
- Do not merge the planning branch.
- Do not start T0, T1, or T2.
- Stop and wait for my explicit planning acceptance.

### 6. Final report

Provide:

1. Corrections applied and associated commits.
2. Mathematical and regression-test evidence.
3. Mutation-testing results.
4. M1/M2 preservation evidence.
5. CI results and final commit SHA.
6. Codex review 07 verdict and finding dispositions.
7. Remaining OPEN and DEFERRED decisions.
8. Whether M3 planning is ready for acceptance.
9. Explicit confirmation that nothing was merged and no M3 implementation began.

Maintain the existing authorization boundaries throughout.
````

### Instruction I-7: "Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`" (2026-10-16), sections 1–6
````text
Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`.

## 1. Authorization

I approve the narrow correction of M3P7-F1 and authorize exactly one subsequent independent Codex review (review 08), conditional on successful local validation.

This is **not** approval of M3 planning, a merge, or M3 implementation.

Do not begin T0, T1, T2, or any production-code changes.

## 2. Correct M3P7-F1

The current wrap() contract claims exactness and interval guarantees for arbitrary inputs, but those guarantees hold only for finite floating-point inputs.

Implement the following narrowly scoped correction:

1. Explicitly define the input domain as finite floating-point angles.
2. Require non-finite inputs (`NaN`, `+∞`, `−∞`) to raise `ValueError`.
3. Preserve the existing behavior for all finite inputs.
4. Preserve the canonical interval (−π, π], including the existing endpoint convention.
5. Add focused tests for the three non-finite categories.
6. Verify that the previous finite-input regression and mutation tests remain unchanged and passing.
7. Append the correction to DR-0028 using the existing amendment convention, preserving historical records.
8. Update the review-resolution register and decision matrix where appropriate.

Do not change the signed first-order formulas, passive rotation convention, physical assumptions, acceptance thresholds, or existing planning decisions.

## 3. Validation

Before requesting review 08:

- Run the deterministic verification script twice and compare outputs.
- Run all focused wrap(), node-crossing, sign, and first-order tests.
- Verify that the existing mutation tests still reject their designated defects.
- Add a targeted mutation proving that removal of the non-finite input guard is detected.
- Verify that all existing finite-angle outputs remain unchanged.
- Check documentation consistency and amendment traceability.
- Confirm the planning diff contains only authorized changes.

Run the M1 and M2 preservation gates where feasible, including GMAT comparisons, reference snapshots, cross-platform validation, and determinism checks.

Report any unavailable or incomplete validation explicitly. Do not represent partial test execution as a full PASS.

## 4. Independent Codex review 08

Only after successful local validation, request one independent Codex review.

Provide Codex with:

- The review 07 findings and their dispositions.
- The precise M3P7-F1 correction.
- The complete amendment chain in DR-0028.
- The verification script and mutation evidence.
- The M1/M2 preservation evidence.
- The complete M3 planning decision and authorization state.

Ask Codex to independently verify mathematical correctness, domain contracts, regression protection, documentation consistency, and planning readiness.

Codex must not simply accept prior review conclusions. It should attempt counterexamples and inspect the current files.

## 5. Stop conditions

If review 08 returns REQUEST_CHANGES:

- Record every finding with severity, evidence, and proposed disposition.
- Do not automatically fix findings.
- Do not initiate review 09.
- Do not prepare a planning acceptance report.
- Stop and request my decision.

If review 08 returns an unconditional PASS:

- Prepare the M3 planning acceptance report.
- Include exact commit IDs, CI results, proof results, amendment history, review history, and outstanding OPEN/DEFERRED decisions.
- Explicitly distinguish planning acceptance from implementation authorization.
- Stop for my approval.

Do not merge, start T0, or begin implementation even after an unconditional PASS.

## 6. Required final report

Provide:

1. Commit and branch state.
2. Exact M3P7-F1 correction.
3. Focused test and mutation results.
4. M1/M2 preservation results.
5. CI results.
6. Codex review 08 verdict and findings.
7. Remaining OPEN, DEFERRED, and NOT AUTHORIZED items.
8. Planning acceptance readiness.
9. Confirmation that no merge or M3 implementation occurred.

Keep the worktree clean and preserve the existing fast-forward-only branch workflow.
````

### Instruction I-8: "Continue TARS M3 planning from `milestone-3-planning` at `0ac630b`" (2026-10-16), sections 1–8
````text
Continue TARS M3 planning from `milestone-3-planning` at `0ac630b`.

## 1. Authorization

I approve the narrow correction of M3P8-F1 and exactly one independent Codex review (review 09), conditional on successful validation.

M3 planning is not accepted. Do not merge, begin T0/T1/T2, modify production code, or change approved physics decisions.

## 2. Correct M3P8-F1

Update `docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`.

Implement:

1. Explicit `math.isfinite()` validation for numerical values produced by both first-order formulas before tolerance, ordering, or sign comparisons.
2. Treat NaN, positive infinity, and negative infinity as verification failures.
3. Ensure failures result in a nonzero process exit code.
4. Require independently enforced, nonzero minimum valid-sample counts for each formula's applicable order and sign checks.
5. Derive coverage minima from the existing legitimate test domains and record the rationale. Do not invent arbitrary thresholds or reduce existing coverage.
6. Ensure skipped, invalid, or non-finite samples cannot satisfy coverage requirements.
7. Preserve the current formulas, conventions, domains, and finite-input behavior.

Do not silently filter invalid values or substitute fallback numerical results.

## 3. Mutation and regression tests

Add targeted tests demonstrating that:

- NaN inclination output fails.
- Positive and negative infinity inclination outputs fail.
- NaN and infinity node-longitude outputs fail.
- Disabling either formula's coverage checks fails.
- Removing finite-value validation fails.
- Weakening an assertion so invalid samples escape detection fails.

Test each mutation independently and require the verification process to exit nonzero.

Where practical, exercise the actual script entrypoint rather than only isolated helper functions.

Preserve all existing signed-formula, node-crossing, wrapping, and amendment regression checks.

## 4. General numerical verification audit

Perform a bounded audit of the DR-0028 verification script for the same failure class:

- Non-finite values silently passing comparisons.
- Vacuous passes caused by empty sample sets.
- Coverage counters incrementing without valid assertions.
- Missing assertions for one formula or one sign.
- Exceptions being swallowed and reported as PASS.

Correct only directly analogous verification-harness defects within this script.

If the audit identifies a separate mathematical issue, a contract change, or work outside this narrow scope, document it and stop for authorization rather than expanding the repair.

## 5. Documentation and validation

Append the M3P8-F1 resolution to the existing DR-0028 amendment chain without rewriting historical records.

Update the finding register and decision matrix.

Then:

- Run the verification script twice and compare deterministic output.
- Run all focused tests and existing mutation tests.
- Verify that existing finite-input results and legitimate sample counts are preserved.
- Run Ruff and documentation consistency checks.
- Verify the diff contains only authorized planning and verification changes.
- Run M1/M2 preservation gates, including GMAT comparisons, reference-snapshot checks, cross-platform validation, and determinism.
- Verify CI completion and individual job results.

Report exact test counts, failures, skipped checks, and commit IDs. Do not describe interrupted or incomplete tests as passing.

## 6. Independent Codex review 09

After local validation passes, request exactly one independent Codex review.

Codex should:

1. Verify M3P8-F1 is resolved.
2. Independently inject NaN and infinity into both formula paths.
3. Attempt to create vacuous PASS results by removing or bypassing assertions.
4. Verify per-formula coverage requirements.
5. Review the complete DR-0028 amendment chain for consistency.
6. Confirm prior review findings remain resolved.
7. Check mathematical correctness and finite-input preservation.
8. Confirm M1/M2 preservation and M3 planning scope.

Codex must distinguish mathematical defects, verification defects, documentation defects, and optional improvements.

Require concrete counterexamples for correctness findings.

## 7. Stop conditions

If review 09 returns REQUEST_CHANGES:

- Record every finding.
- Do not fix automatically.
- Do not initiate review 10.
- Do not prepare an acceptance report.
- Stop for my decision.

If review 09 returns unconditional PASS:

Prepare the final M3 planning acceptance report, including all outstanding OPEN, DEFERRED, and NOT AUTHORIZED decisions.

Do not merge or begin T0. Await my explicit approval.

## 8. Final report

Include:

1. Branch, commits, and worktree state.
2. M3P8-F1 resolution.
3. Numerical validation audit results.
4. Mutation results and coverage counts.
5. M1/M2 preservation evidence.
6. CI results.
7. Codex review 09 verdict.
8. Outstanding decisions.
9. Planning acceptance readiness.
10. Confirmation that no implementation or merge occurred.

Preserve fast-forward-only pushes and leave the worktree clean.
````

### Instruction I-9: "I-9 — M3 Planning Verification Hardening and Codex Review 10" (2026-10-17), sections 1–10
````text
# I-9 — M3 Planning Verification Hardening and Codex Review 10

You are continuing the TARS spacecraft simulator's M3 planning checkpoint.

**Current baseline:** `origin/milestone-3-planning` at `faba9d6`.

**Current status:** M3 planning is NOT ACCEPTED. Review 09 returned REQUEST_CHANGES with two MINOR findings and one NOTE. No M3 implementation work is authorized.

## 1. Authority and scope

I authorize the following:

- Correct M3P9-F1.
- Correct M3P9-F2.
- Add targeted mutation coverage for M3P9-F3.
- Run exactly one new independent Codex review, Review 10, after local validation passes.
- Record all evidence and findings.

I do NOT authorize:

- Merging M3 planning into main.
- Starting T0, T1, or T2.
- Modifying production simulator code.
- Changing approved physics formulas, constants, tolerances, thresholds, or reference baselines.
- Resolving previously deferred or unauthorized decisions.
- Automatically fixing findings discovered by Review 10.

Preserve all existing M1/M2 validation gates.

## 2. Establish the baseline

Before editing:

1. Verify branch, commit, remote state, and worktree cleanliness.
2. Read the complete Review 09 record and raw Codex output.
3. Read DR-0028 and all relevant amendments.
4. Identify the existing verification script and mutation harness.
5. Inspect how assertion execution, coverage counts, and mutation detection are measured.
6. Verify that the proposed changes remain within planning documentation and verification artifacts.

If the baseline differs unexpectedly, stop and report the discrepancy.

Do not overwrite another worktree or force-push.

## 3. Resolve M3P9-F1 — Oracle finite-value enforcement

Implement mutations that test whether the oracle rejects positive and negative infinity.

Requirements:

- Exercise both Δi and ΔΩ.
- Include positive and negative infinity independently.
- Include partial corruption where only one oracle value is nonfinite.
- Include a mutation weakening the oracle's `math.isfinite` check to `math.isnan` or an equivalent defective condition.
- Verify every defective case causes a nonzero exit.
- Preserve the existing 60 NaN/∞ injection checks.

The test must demonstrate that the finite-value assertion is operational, not merely present in source code.

## 4. Resolve M3P9-F2 — Order and sign assertions

For each formula independently:

1. Introduce a wrong first-order coefficient that should violate the order property.
2. Introduce a reversed-sign mutation that should violate the sign property.
3. Disable the order assertion and verify the harness detects the missing assertion.
4. Disable the sign assertion and verify the harness detects the missing assertion.

There must be four independently tested assertion-removal cases:

- Δi order assertion disabled.
- ΔΩ order assertion disabled.
- Δi sign assertion disabled.
- ΔΩ sign assertion disabled.

A mutation is successful only when the harness detects the defect for the intended reason.

Do not accept a mutation as detected merely because it causes an unrelated syntax error, import failure, missing file, or infrastructure exception.

Retain the existing per-formula minimum coverage requirements.

## 5. Address M3P9-F3 — Exact-property assertion integrity

Add targeted mutations removing the E3 and E4 assertions individually.

Require the mutation harness to detect both removals.

Do not change the mathematical definitions of E3 or E4.

Do not broaden the order-test step-size selection in this instruction. Document that limitation as an intentional property of the current test design, unless existing evidence demonstrates it invalidates an approved requirement.

## 6. Mutation-harness integrity

Ensure that the harness:

- Detects each required mutant independently.
- Distinguishes an expected assertion failure from infrastructure failure.
- Fails closed when a required mutation is not detected.
- Does not rely exclusively on sample counters to establish assertion effectiveness.
- Produces deterministic results across two consecutive runs.
- Reports mutation identity, target property, expected rejection, observed outcome, and PASS/FAIL.
- Preserves all existing successful mutation cases.

Do not weaken assertions to make tests pass.

If implementation reveals that an approved test cannot meaningfully detect its target defect, stop and report the problem rather than inventing a weaker success criterion.

## 7. Local validation

Before requesting Review 10:

1. Run the complete verification script.
2. Run the full mutation suite twice.
3. Confirm all required mutants are detected.
4. Confirm all four existing order/sign coverage minima remain satisfied.
5. Run the relevant Python tests and Ruff checks.
6. Confirm no M1/M2 production or validation contracts changed.
7. Run M1 Proof and M2 Proof, including GMAT, reference-snapshot, cross-platform, and determinism checks, using the established procedures.
8. Record exact commands, commit identifiers, results, and any environmental limitations.

Do not describe an incomplete or interrupted test run as a full PASS.

If any required validation fails, stop before Review 10.

## 8. Commit and Review 10

Once local validation passes:

1. Commit the verification changes and evidence.
2. Push using fast-forward only.
3. Prepare a self-contained Review 10 prompt.
4. Preserve I-1 through I-9 verbatim in the review's instruction history, checking exactness against the authoritative records.
5. Request independent Codex verification.

Review 10 must examine:

- M3P9-F1, M3P9-F2, and M3P9-F3.
- All earlier findings and their claimed resolutions.
- Mathematical correctness and conventions in DR-0028.
- Mutation-harness effectiveness and resistance to false positives.
- Assertion-removal detection.
- Preservation of coverage minima.
- M1/M2 preservation.
- Scope boundaries and unresolved decisions.
- Whether the planning package is ready for acceptance.

Require Codex to produce concrete counterexamples for any newly identified defect wherever feasible.

Do not instruct Codex to approve the package.

## 9. Mandatory stop condition

If Review 10 returns REQUEST_CHANGES or identifies any new BLOCKER, MAJOR, or MINOR finding:

- Record every finding and its evidence.
- Record the disposition as pending or accepted, as appropriate.
- Do not implement further corrections.
- Do not run Review 11.
- Do not prepare an acceptance report.
- Stop and request my next authorization.

If Review 10 returns an unconditional PASS:

- Record the full review evidence.
- Prepare an M3 planning acceptance candidate report.
- Include the unresolved decision register and precise T0/T1/T2 authorization boundaries.
- Do not declare M3 planning accepted.
- Do not merge.
- Do not start T0.

Await my explicit acceptance.

## 10. Required final report

Provide:

1. Branch, commit, and worktree status.
2. Corrections implemented for each finding.
3. Mutation results, including newly added mutants and totals.
4. Per-formula coverage counts.
5. M1/M2 Proof and regression results.
6. CI status, distinguishing completed from pending jobs.
7. Codex Review 10 verdict and findings.
8. Remaining open/deferred decisions.
9. Planning acceptance readiness.
10. Explicit confirmation that no production code was modified, nothing was merged, and T0/T1/T2 remain unstarted.

Preserve the unresolved status of DR-0027 A-4, A-5, A-6, A-s, B-4; Q-G2-1, Q-G2-5, Q-G2-7 and Q9; Q-G2-6; and Q-G3-7.

**Primary objective:** Establish that the M3 planning verification harness detects the specific defects it claims to guard against, without changing the approved mathematical model or expanding milestone scope.
````

### Instruction I-10: "I-10 — Resolve M3P10-F1 and authorize Review 11" (2026-10-17), sections 1–10
````text
# I-10 — Resolve M3P10-F1 and authorize Review 11

You are continuing the TARS spacecraft simulator M3 planning verification process.

**This instruction authorizes only the work described below. It does not authorize M3 planning acceptance, merging, T0/T1/T2 implementation, or production code changes.**

## 1. Baseline and repository safety

Verify the following before making changes:

- Local branch: `m3-planning-checkpoint-037cfd34`
- Expected baseline: `896d52d`
- Remote planning branch: `origin/milestone-3-planning`
- Worktree clean
- All prior I-1 through I-9 instructions and decisions remain authoritative.
- No changes to approved M1/M2 contracts, numerical thresholds, references, goldens, or validation semantics.

If the expected baseline differs, stop and report the discrepancy. Do not reset, force-push, or overwrite another worktree.

## 2. Resolve M3P10-F1

Repair the mutation harness so that an unrelated exception can never count as successful mutation detection or proof that an assertion is necessary.

Requirements:

1. Distinguish normal execution, expected rejection, unexpected exception, and invalid mutation setup.
2. A mutant classified as "not rejected" must have completed execution without an exception.
3. An unexpected exception must fail the harness evaluation, not count as detection.
4. Expected exceptions must be explicitly allowlisted by mutation identity, exception type, and intended failure location.
5. Restrict exception allowances to the documented E2/E5b wrap guard and `isnan` cases where justified.
6. Preserve reason-specific detection: a mutant is detected only when the intended check rejects it for the intended reason.
7. Ensure exceptions swallowed inside mutant wrappers cannot be misclassified as valid detection.
8. Ensure malformed mutants, import failures, and harness infrastructure errors are distinguishable from legitimate mathematical rejection.

Do not broaden exception handling merely to make the suite pass.

## 3. Add regression and negative controls

Reproduce M3P10-F1 before applying the fix.

Add controls demonstrating that:

- An import failure inside a mutant is not detection.
- An unrelated runtime exception inside a mutant is not detection.
- An exception caught and suppressed by a mutant is not automatically detection.
- An expected exception from the wrong location is not accepted.
- An expected exception of the wrong type is not accepted.
- A mutant rejected for an unrelated reason is not detected.
- A valid mutant rejected by its targeted check is detected.
- A valid mutant that completes without rejection is classified correctly.

For each control, record its expected classification, actual classification, and pass/fail outcome.

Demonstrate that the regression controls fail against the original defective harness and pass against the corrected harness.

## 4. Evaluate the 18 unprotected assertions

Review the 18 assertions identified by the Review 10 assertion sweep.

For each assertion, classify it as:

- **A — Independently important:** Removing it could permit an otherwise undetected correctness defect.
- **B — Redundant:** Another independent check detects the same relevant failure.
- **C — Diagnostic:** It improves reporting or diagnostics without uniquely protecting a correctness property.
- **D — Uncertain:** Its independent verification value cannot yet be established.

Provide evidence for every classification.

For category A, propose and implement narrowly scoped additional mutation coverage within the existing verification harness.

For category B, identify the specific independent check and demonstrate the overlap where practical.

For categories C and D, document the implications. Do not delete or weaken assertions.

If a category D assertion may conceal a material correctness risk, stop and request a decision rather than assuming it is acceptable.

Do not pursue an arbitrary 100% assertion-mutation score. Prioritize meaningful, independent verification.

## 5. Rerun verification

Run:

1. The corrected mutation harness, including all previously established injection cases.
2. Every existing negative control and newly added regression control.
3. The built-in mutant suite.
4. The assertion-removal sweep.
5. Repeatability checks.
6. The normal M3 planning verification script.
7. Relevant Python tests and formatting checks.

Verify that:

- Previously valid mutation detections remain valid.
- The correction does not change mathematical formulas, oracle values, tolerance values, coverage minima, or established numerical results.
- The E3/E4 detection of the 1% Δi oracle error remains effective.
- Δi and ΔΩ coverage minima remain independently enforced.
- No exception is counted as mutation detection unless it is an explicitly authorized, correctly classified rejection.

Record before/after counts and explain every difference.

## 6. M1/M2 preservation

Confirm that the correction is limited to planning verification and supporting records.

Rerun the appropriate preservation checks, including the full M1 and M2 Proof workflows, using the established isolated execution procedure.

Do not silently replace a full proof with a partial test run.

If any proof cannot finish, record the limitation and stop before requesting acceptance.

## 7. Prepare independent Review 11

Once local verification succeeds:

- Commit the correction and its supporting tests.
- Update the append-only decision and finding registers.
- Prepare the Review 11 prompt.
- Include I-1 through I-10 verbatim and verify their integrity.
- Identify the exact commit under review.
- Require Codex to independently reproduce the M3P10-F1 regression and evaluate its correction.

Review 11 must specifically examine:

1. Exception classification correctness.
2. Whether any unrelated failure can still count as mutation detection.
3. The validity of expected-exception allowances.
4. Negative-control effectiveness.
5. The 18-assertion classification and any added protections.
6. Preservation of the mathematical and coverage checks from Reviews 01–10.
7. M1/M2 preservation.
8. Any new regression or acceptance-blocking defect.

Codex must return an explicit PASS or REQUEST_CHANGES with individually identified findings and severity.

## 8. CI and repository discipline

Use fast-forward-only pushes.

Verify all required CI jobs have completed successfully, including Ubuntu, macOS, Intel macOS, and the M2 cross-platform gate.

Do not infer success from a workflow-level status while individual jobs remain unfinished.

Keep unrelated worktrees untouched.

## 9. Mandatory stop conditions

If Review 11 returns REQUEST_CHANGES:

- Record every finding.
- Do not fix the new findings.
- Do not initiate Review 12.
- Do not prepare a planning acceptance report.
- Stop and return the findings for my authorization.

If Review 11 returns an unconditional PASS and all required verification is green:

- Prepare an M3 planning acceptance candidate report.
- Clearly identify remaining OPEN, DEFERRED, and NOT AUTHORIZED decisions.
- Distinguish planning acceptance from authorization to implement T0.
- Stop and wait for my explicit acceptance.

In either case, do not merge and do not begin T0, T1, or T2.

## 10. Final report

Provide:

1. Branch and exact commit hashes.
2. M3P10-F1 root cause and correction.
3. Regression and negative-control results.
4. Mutation results and before/after counts.
5. Classification of all 18 assertions.
6. Mathematical and coverage preservation evidence.
7. M1/M2 Proof results.
8. CI run IDs and individual job statuses.
9. Codex Review 11 verdict and findings.
10. Updated decision register and remaining open decisions.
11. Explicit readiness recommendation.
12. Confirmation that nothing was merged or implemented outside authorization.

**Do not declare M3 planning accepted. Final acceptance remains my decision.**
````

### Instruction I-11: "I-11 — Resolve Review 11 Findings and Authorize Review 12" (2026-10-17), sections 1–10
````text
# I-11 — Resolve Review 11 Findings and Authorize Review 12

Continue the TARS spacecraft simulator M3 planning verification process.

This instruction authorizes correction of M3P11-F1 and M3P11-F2, supporting verification changes, and one independent Codex Review 12.

It does NOT authorize M3 planning acceptance, merging, T0/T1/T2 implementation, changes to approved mathematical contracts, or expansion of M3 scope.

## 1. Verify baseline

Expected state:

- Local branch: `m3-planning-checkpoint-037cfd34`
- Remote: `origin/milestone-3-planning`
- HEAD: `cadccd8`
- Clean worktree
- Previous review baseline: `c16b3b5`
- All I-1 through I-10 instructions remain authoritative.

Confirm the baseline before modifying anything.

Do not reset, force-push, modify another worktree, or silently reconcile unexpected changes.

If the baseline differs, stop and report.

## 2. Resolve M3P11-F1 — Defect-specific mutation exercise

The current harness can classify a mutant as exercised because its output differs numerically, even when the difference does not demonstrate that the intended defect was introduced.

Replace this permissive criterion with defect-specific evidence.

Requirements:

1. Every mutation must identify its intended defect and the specific behavior it is supposed to change.
2. Define an explicit exercise predicate for each mutation or justified mutation family.
3. A mutation counts as exercised only when evidence establishes that the intended defect occurred.
4. Incidental floating-point differences, changed arithmetic evaluation order, or unrelated output differences are insufficient.
5. A suppressed import failure followed by a numerically different but mathematically equivalent fallback must not count as successful defect exercise.
6. An unexpected exception, invalid mutation setup, or infrastructure failure must not count as detection.
7. Successful detection requires both valid defect exercise and rejection by the intended verification check.
8. Preserve the narrowly scoped exception allowances from I-10. Revalidate each allowance against its mutation identity, exception type, and intended failure location.

Avoid circular verification: do not define defect exercise solely in terms of whether the targeted assertion fails.

Where feasible, use independent observations of the injected defect rather than relying on the same output comparison used for detection.

If the intended defect cannot be observed independently, classify the mutation as unverified and explain why.

### Regression controls

Reproduce the Review 11 counterexample before implementing the correction.

Add controls demonstrating that:

- A suppressed import failure with a slightly different arithmetic evaluation order is not valid defect exercise.
- A genuine intended defect is classified as exercised.
- A mutation that changes only unrelated numerical values is not exercised.
- A correctly exercised mutation rejected for the wrong reason is not detected.
- A correctly exercised mutation rejected by the intended check is detected.
- An invalid mutation cannot be counted as detection.
- Existing expected-exception cases remain correctly classified.

Demonstrate that the relevant new regression controls fail against the original harness and pass against the corrected harness.

## 3. Resolve M3P11-F2 — Assertion classification

Reclassify the five incorrectly categorized assertions as independently important:

- W5
- E1
- E2e
- E5b-nonfinite
- E5b-defined

The corrected classification should be:

| Category | Count |
|---|---:|
| A — Independently important | 11 |
| B — Redundant | 4 |
| C — Diagnostic | 3 |
| Total | 18 |

Verify the identities and totals against the actual assertion inventory rather than relying only on this report.

For each of the five newly classified A assertions:

1. Identify the specific correctness property it protects.
2. Construct a targeted mutant that violates that property.
3. Demonstrate that the intended defect is genuinely exercised.
4. Demonstrate that the relevant assertion detects it.
5. Demonstrate that removing the assertion permits the intended defect to escape the relevant check.
6. Verify that the mutant is not merely triggering an unrelated exception or incidental numerical difference.

Preserve the six category A protections added during I-10.

For the four category B assertions, document the independent checks providing equivalent protection.

For the three category C assertions, document their diagnostic purpose.

Do not remove, weaken, or redefine existing assertions to improve mutation results.

If an assertion cannot be reliably classified, report the uncertainty rather than inventing evidence.

## 4. Update records and verification evidence

Update DR-0028 through a new append-only amendment.

Preserve amendment 7 and its historical claims, but explicitly identify and correct the five invalid classifications.

Update:

- Review 11 finding dispositions.
- Decision matrix.
- Mutation inventory.
- Assertion classification.
- Verification evidence.
- Planning status.

Clearly distinguish historical results from results generated using the corrected harness.

Do not silently relabel historical detections as valid under the new criteria.

## 5. Verification requirements

Run:

1. Full mutation harness.
2. All existing and new regression controls.
3. Built-in mutation suite.
4. Assertion-removal sweep.
5. Repeatability checks.
6. Normal M3 planning verification.
7. Relevant Python tests and formatting checks.

Report separately:

- Mutants attempted.
- Mutants validly exercised.
- Mutants detected for the intended reason.
- Mutants not exercised.
- Mutants rejected for unrelated reasons.
- Mutants invalid because of exceptions or infrastructure failures.
- Assertions individually protected.
- Assertions intentionally redundant or diagnostic.

Do not collapse these categories into a single success percentage.

Verify that existing mathematical formulas, oracle values, numerical tolerances, coverage minima, and previously established result values remain unchanged.

Specifically preserve:

- Δi and ΔΩ coverage enforcement.
- E3/E4 detection of the 1% Δi oracle error.
- Sign and order checks.
- Nonfinite-value rejection.
- All existing M3 planning mathematical invariants.

If any existing check loses coverage, investigate and report the regression before proceeding.

## 6. M1/M2 preservation

Perform the established isolated preservation procedure.

Require:

- Full M1 Proof.
- Full M2 Proof.
- Relevant pytest suite.
- GMAT verification.
- Reference snapshot verification.
- Determinism verification.
- Cross-platform verification.

Distinguish complete proof executions from partial independent reviewer executions.

No approved M1/M2 thresholds, reference data, goldens, or contracts may change.

## 7. Independent Codex Review 12

After successful local verification:

- Commit the corrections.
- Prepare the Review 12 prompt.
- Carry I-1 through I-11 verbatim.
- Verify instruction integrity.
- Identify the exact reviewed commit.

Require Codex to independently evaluate:

1. Whether M3P11-F1 is fully resolved.
2. Whether defect exercise is independent of incidental numerical differences.
3. Whether exceptions and invalid mutants can still produce false detection claims.
4. Whether M3P11-F2 is fully resolved.
5. Whether all 11 category A assertions have meaningful targeted protection.
6. Whether the remaining category B and C classifications are justified.
7. Whether previous review findings remain resolved.
8. Whether the mathematical results and M1/M2 baselines are preserved.

Codex must independently reproduce the new regression controls and attempt adversarial counterexamples.

Require an explicit PASS or REQUEST_CHANGES verdict, with individually identified findings and severity.

### Review scope discipline

Review 12 must distinguish:

- A correctness defect.
- An unsound verification claim.
- A meaningful coverage gap.
- A documentation improvement.
- A hypothetical enhancement that is not required for planning acceptance.

Do not treat an optional enhancement as an acceptance blocker without explaining the concrete correctness or verification risk.

Do not instruct Codex to overlook genuine defects.

## 8. CI and repository discipline

Use fast-forward-only pushes.

Verify completion and success of all required CI jobs:

- Ubuntu
- macOS latest
- macOS Intel
- M2 cross-platform

Ensure that the CI evidence corresponds to the relevant verified commit and that no subsequent unverified code changes invalidate it.

Keep unrelated worktrees untouched.

## 9. Mandatory stop conditions

If Review 12 returns REQUEST_CHANGES:

- Record every finding.
- Do not fix the new findings.
- Do not start Review 13.
- Do not prepare an acceptance report.
- Stop and request my authorization.

If Review 12 returns unconditional PASS and all verification requirements are satisfied:

- Prepare an M3 planning acceptance candidate report.
- Summarize resolved findings and remaining risks.
- Identify all OPEN, DEFERRED, and NOT AUTHORIZED decisions.
- Explain which deferred decisions must be resolved before their relevant implementation stages.
- Stop and request my explicit acceptance.

Under no circumstances merge or begin T0/T1/T2.

## 10. Final report

Provide:

1. Exact branch and commit state.
2. M3P11-F1 root cause, correction, and regression evidence.
3. M3P11-F2 correction and all 18 assertion classifications.
4. Before/after mutation results.
5. Evidence that defect exercise and defect detection are independently established.
6. Mathematical preservation results.
7. M1/M2 Proof results.
8. CI run IDs and individual job statuses.
9. Codex Review 12 verdict.
10. Remaining findings and open decisions.
11. Readiness recommendation.
12. Explicit confirmation that nothing was merged and no M3 implementation began.

Final planning acceptance remains my decision.
````

### Instruction I-12: "I-12 — M3 Planning: Review 12 Corrections and Review 13 Authorization" (2026-10-17), sections 1–9
````text
# I-12 — M3 Planning: Review 12 Corrections and Review 13 Authorization

## 1. Authorization and scope

I authorize correcting exactly two findings:

- **M3P12-F1:** Oracle mutation probes fail to verify that the intended defect occurs at every required step.
- **M3P12-F2:** E6-sign is incorrectly classified as category B despite its sign defect being outside the first-order grid's exercised domain.

After implementing and validating these corrections, conduct **exactly one independent Codex Review 13**.

This authorization does not constitute acceptance of M3 planning or permission to begin implementation.

Do not merge, start T0/T1/T2, modify approved physics, or resolve outstanding decisions without separate authorization.

## 2. Repository and baseline safeguards

1. Verify `origin/milestone-3-planning` is at `142b9df`.
2. Confirm the worktree is clean and the branch is correct.
3. Preserve all historical review records, raw outputs, decisions, and evidence.
4. Use fast-forward-only pushes. Never force-push.
5. Do not modify another worktree.
6. Keep the existing M1/M2 contracts, references, thresholds, goldens, and verification semantics unchanged.

If the baseline differs unexpectedly, stop and report the discrepancy.

## 3. Correct M3P12-F1

The current probe can accept a mutation that corrupts only the first oracle value because it validates only values reached before the script stops.

Codex demonstrated 600 NaN values and 2,400 correct values being accepted as an all-steps mutant.

Required correction:

1. Observe the oracle independently at every required step, including steps the normal script would skip after an earlier failure.
2. Establish the expected observation count and step identities before checking mutation results.
3. Require the intended defect to be confirmed at **every step claimed by the mutant**.
4. Distinguish:
   - Intended defect observed
   - Unchanged output
   - Missing observation
   - Unintended defect
5. Fail closed when observations are missing, incomplete, nonfinite unexpectedly, or inconsistent with the declared mutation.
6. Preserve independent probe-process isolation.
7. Ensure the mutation detector cannot satisfy its own verification requirements by relying on the same incorrect assumption.

Add negative regression controls for:

- First-step-only corruption.
- Last-step-only corruption.
- Partial-step corruption.
- Missing intermediate observations.
- Incorrect observation counts.
- Correctly injected all-step corruption.

Every negative control must demonstrate rejection for the intended reason.

## 4. Correct M3P12-F2

E6-sign currently receives category B credit for an oracle sign test at the preserved 0.15° example, while the first-order grid does not exercise that tilt.

A sign inversion confined to the first-order formula can therefore escape detection.

Required correction:

1. Separate oracle-sign verification from first-order formula-sign verification.
2. Reclassify E6-sign according to what each verification path actually exercises.
3. Prefer splitting E6-sign into independently identified oracle and formula assertions if this makes coverage claims more precise.
4. Otherwise, move E6-sign into category C until its complete intended claim is demonstrated.
5. Add a targeted mutant that reverses only the first-order formula sign while preserving the oracle behavior.
6. Verify the mutant is rejected by the relevant first-order assertion, not by an unrelated check.
7. Re-examine the other category B assertions — W1, W4, and E6-value — for the same domain mismatch.

Do not upgrade an assertion's category merely because a new test exists. Its classification must follow demonstrated coverage.

Preserve the existing first-order mathematical convention and the previously corrected sign formulas.

## 5. Verification and regression requirements

Run the affected standalone validators and mutation harnesses.

Demonstrate:

- M3P12-F1 counterexamples fail before correction and pass after correction.
- M3P12-F2 targeted sign mutant is rejected for the intended reason.
- Existing M3P10-F1/F2 and M3P11-F1/F2 regression controls remain effective.
- Mutation totals and category classifications are regenerated from actual executions.
- Exercise coverage and detection coverage remain separately measured.
- All reported totals reconcile with underlying evidence.
- Existing verification results are neither silently dropped nor weakened.

Preserve the existing mathematical oracle, formulas, grids, tolerances, coordinate conventions, and coverage requirements.

If a mathematical or approved-contract change appears necessary, stop and request authorization.

## 6. Independent verification

After local corrections pass:

1. Run the full available M1 and M2 Proof workflows, not merely their standalone validators.
2. Confirm the pinned reference artifacts and numerical results remain unchanged.
3. Run the relevant M3 planning verification suite.
4. Confirm all required CI jobs finish successfully, including Ubuntu, macOS, Intel macOS, and cross-platform verification.
5. Record exact commands, commits, test counts, artifact checksums, and CI run/job IDs.

If the full Proof cannot run, distinguish an environmental limitation from a test failure. Do not claim full Proof success based on standalone checks.

## 7. Codex Review 13

Only after corrections and local verification succeed, prepare an independent Codex review.

Supply:

- The original I-1 through I-12 instructions and applicable decisions.
- The Review 12 raw findings.
- The exact baseline and corrected commit IDs.
- The complete correction diff.
- Regression demonstrations.
- Mutation classification and detection evidence.
- Full Proof results.
- CI results.
- The current decision matrix.

Ask Codex to independently verify:

1. M3P12-F1 and M3P12-F2 are genuinely resolved.
2. Previous M3P10/M3P11 findings remain resolved.
3. Oracle probes observe the entire claimed domain.
4. Category classifications match actual exercised domains.
5. Targeted mutants fail for their intended defects.
6. Verification code does not rely on circular or self-validating evidence.
7. No approved mathematical or numerical contract has changed.
8. Existing M1/M2 behavior remains protected.

Codex must report an explicit verdict, findings with severity, and resolution status for all tracked findings.

Do not instruct Codex to produce PASS.

## 8. Stop conditions

Stop immediately if:

- Any regression cannot be explained.
- A previously resolved finding reappears.
- An approved mathematical contract requires modification.
- The baseline or branch is inconsistent.
- A required verification gate fails.
- Codex returns REQUEST_CHANGES.
- Codex identifies any new BLOCKER, MAJOR, or MINOR finding.

For a REQUEST_CHANGES verdict, record all findings and reproduce counterexamples where feasible, but do not fix them or initiate Review 14.

Even if Review 13 returns PASS, do not merge or begin M3 implementation. Prepare an acceptance recommendation for my decision.

## 9. Final report

Report:

1. Branch, baseline, final commit, and worktree status.
2. Exact corrections to M3P12-F1 and M3P12-F2.
3. Before/after regression evidence.
4. Mutation detection counts and assertion classifications.
5. Resolution status of all outstanding verification findings.
6. M1/M2 Proof results and CI status.
7. Codex Review 13 verdict and raw-output location.
8. Any unresolved or deferred decision requests.
9. Whether M3 planning is ready for acceptance.

**Hard boundary:** This instruction authorizes two corrections and one independent review. It does not authorize acceptance, merging, T0, T1, T2, or Review 14.

Stop after reporting.
````

## Review focus (required)
I-12 §7 requires you to verify each of the following independently.

1. **Are M3P12-F1 and M3P12-F2 genuinely resolved?**
   - Reproduce review 12's oracle counterexample against the reviewed harness at `5b12eec` (`git show 5b12eec:<path>`), then apply it, and your own variants, to the corrected harness; confirm none is a detection.
   - Reproduce review 12's E6 counterexample before and after; confirm the first-order half of E6 is now protected and that its removal is detected.
   - Run `dr0028_node_signed_harness_regression.py` and check that each regression control tests what it claims.
2. **Do the previous M3P10 and M3P11 findings remain resolved?** Check rounds 01–12 and their records, and that amendments 1–9 are consistent, with superseded statements kept and linked by pointers.
3. **Do the oracle probes observe the entire claimed domain?**
   - Is the schedule correct and independent of the mutated copy? Is every step observed, including steps after an invalid value? Can a copy evade or spoof the observation (renamed or reordered locals, an injection after the formula call, extra or skipped steps, calls from elsewhere, exceptions)?
   - Is "missing = 0" now sufficient for every claimed step, and is any other family (built-in, formula, injected) open to the same class of defect?
4. **Do the category classifications match the actually exercised domains?**
   - Verify the 19 identities and the 12/4/3 totals against the actual inventory and the 896d52d survivors.
   - For each B assertion (W1, W4, E6-value, E6-sign-oracle), check that the premise holds at the same inputs as the assertion, and try defects that only the B assertion would reject. Check the C rationales.
5. **Do the targeted mutants fail for their intended defects?** For each of the 12 category A assertions: the protected property, whether the mutant violates it, genuine exercise without exception, detection with the assertion present (and by which message), escape without it, and for E6-sign-first-order, 0 failures on the first-order grid.
6. **Does the verification code rely on circular or self-validating evidence?** Consider the probe, `DEFECTS`, `observe()`, the schedule, `CONTROL_REASONS`, the regression demonstration and the classification's premises.
7. **Has any approved mathematical or numerical contract changed?**
   - Run the verification script twice and compare its output with `5b12eec`: only added keys are expected.
   - Confirm order 506/532 and sign 560/504, each enforced separately; E3/E4 rejection of the 1 % Δi oracle error; sign and order checks per formula; non-finite rejection; and that the oracle, formulas, wrap, grid, tolerances and minima are unchanged (AST).
   - Rederive or spot-check the DR-0028 mathematics.
8. **Is existing M1/M2 behaviour still protected?**
   - Run the M1/M2 Proof validators, the GMAT comparisons, the reference-snapshot verify-baseline, the cross-platform check and determinism as far as feasible. Say explicitly which runs were complete Proof executions and which were partial or interrupted.
   - Confirm that the change is `docs/` only, that register lines existing at `d92ab89` are unchanged, that the pinned references and goldens are unchanged, and that no OPEN, DEFERRED or NOT AUTHORIZED item is promoted:
     - DR-0027 A-4, A-5, A-6, A-s, B-4;
     - Q-G2-1, Q-G2-5, Q-G2-7 and the Q9 values;
     - Q-G2-6;
     - Q-G3-7.
9. **Any new regression or acceptance-blocking defect,** of any kind.
10. **Planning readiness.** Is the package, as documentation evidence, ready to be presented to the Tech Lead for planning acceptance? Give your own assessment; nothing here asks you to approve it. Which decisions still block T0, T1 and T2?

You must independently reproduce the new regression controls and attempt adversarial counterexamples of your own.

**Scope discipline.** Classify each finding as one of the following:
- a correctness defect;
- an unsound verification claim;
- a meaningful coverage gap;
- a documentation improvement;
- a hypothetical enhancement that is not required for planning acceptance.

Do not treat an optional enhancement as an acceptance blocker without explaining the concrete correctness or verification risk. Genuine defects must not be overlooked.

## Output
Your final message, in Markdown.

First, a **Resolution status of tracked findings** table: ID | RESOLVED / NOT RESOLVED | evidence. Include at least M3P12-F1, M3P12-F2, M3P11-F1, M3P11-F2, M3P10-F1 and M3P10-F2, and any earlier finding you find no longer resolved.

Then one block per new finding, numbered from M3P13-F1:

### M3P13-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Class:** Correctness defect | Unsound verification claim | Coverage gap | Documentation improvement | Optional enhancement
**Where:** file and section
**Claim:** ...
**Evidence:** ... (quote the text, show the computation or the command and its output; give a concrete counterexample wherever feasible)
**Concrete risk:** ... (for anything above NOTE: the correctness or verification risk if it is not fixed)
**Suggested resolution:** ...

**Severity scale:**
- **BLOCKER:** must not go to the Tech Lead as is.
- **MAJOR:** a substantive error or gap.
- **MINOR:** a local inaccuracy that should be corrected.
- **NOTE:** an observation needing no change.

An "Optional enhancement" is NOTE severity unless you show a concrete defect.

Then a **Summary** with exactly one explicit verdict:
- **PASS:** unconditional. Every tracked finding above is RESOLVED, and there is no BLOCKER, MAJOR or MINOR finding; NOTEs only, or none.
- **REQUEST_CHANGES:** otherwise.

List what you verified, including the commands run and recomputed results. Mark anything partial or interrupted as partial. State in one line whether the planning package is ready to be presented to the Tech Lead for planning acceptance as documentation evidence.
