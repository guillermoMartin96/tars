You are an independent reviewer from a separate provider; you did not write these documents. This is the TARS Milestone 3 **planning decision checkpoint**: the Tech Lead has decided G1–G3, and the implementer has recorded those decisions. No M3 implementation exists or is authorized. Review round 1 of this checkpoint (the only planned round).

The snapshot is the current directory: a git clone of branch `milestone-3-planning` at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/` (git-ignored).

## Context
- Baseline: `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M1/M2 accepted, CLOSED). The previous planning review (round 01, at `8096acd`) is recorded in `docs/reviews/M3-planning-review-01.md`.
- The commit under review records the owner's decisions: `git diff 6dbb22b..HEAD`. Whole-branch scope: `git diff d92ab89..HEAD`.
- Files: DR-0024, DR-0025, DR-0026 (Resolution sections and the new DR-0024 §3.4–§3.5), new DR-0027, new ADR-0009 (`docs/decisions/0009-…`), `docs/science/assumptions.md` (SCI-0005 appended note; SCI-0013…0017 appended), `docs/science/validation.md` (VAL-0007 appended note), `docs/milestones/*`, `docs/reviews/M3-planning-review-01.md`, `docs/science/experiments/m3-planning/q10_table_check.py` and its results.
- Q10 inputs: the GMAT table is reproduced in `docs/science/experiments/m3-planning/q10_table_check_results.json` (every row of both sources, with digests). The author's file is `software/misc/pascal/ATMOSEXP.DAT` in https://github.com/CelesTrak/fundamentals-of-astrodynamics at commit `49df0479c950917c0a2c5ac31f2db6477bba57f6`; if you have network access you may fetch it, otherwise check against the per-row values in the results JSON.

## The owner's decisions (verbatim from the Tech Lead's instruction; the records must represent these exactly)
### 1. DR-0024 — G1 physical models and constants

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

### 2. DR-0025 — G2 validation strategy

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

### 3. DR-0026 — G3 force/scenario/event architecture

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

### 4. Historical corrections

Record, without altering frozen evidence:

- SCI-0005's TT/TCG wording correction.
- VAL-0007's actual GMAT GM provenance.

Clearly distinguish:
- historical result,
- incorrect historical description,
- corrected interpretation,
- whether the correction changes any previous acceptance decision.

If either correction changes a prior acceptance decision, STOP and report it as a decision gate.

### 5. AT items and future flight architecture

Keep AT-1 through AT-7 OPEN for M3.

Preserve AC-1 as ACCEPTED:

Before software crosses into flight-runtime, embedded, firmware, or hardware execution, there must be an explicit architecture/runtime decision.

Do not make a Rust/C/FFI/RTOS/hardware decision in this task.

Do not merge research/flight-software-architecture into main. It remains research evidence unless separately authorized later.

## Look specifically for
1. Whether **every** owner decision above is represented correctly in the DR Resolutions, SCI entries, ADR-0009 and milestone documents, with nothing added, dropped, softened or strengthened. Pay attention to items the owner did not address: are they explicitly left open/deferred rather than silently decided? (Examples to examine: DR-0024 Q4 axis; DR-0025 Q-G2-1, Q-G2-5, Q-G2-6, Q-G2-7; DR-0026 Q-G3-7, Q-G3-9, Q-G3-10.) Judge whether the implementer's treatment of each is correct.
2. Whether any M3 implementation was introduced (`git diff d92ab89..HEAD --stat` must show only `docs/`; the Q10 script is a research artifact).
3. Whether historical M1/M2 evidence changed: existing lines of `docs/science/assumptions.md` and `docs/science/validation.md` must be unchanged (additions only); no artifact outside `docs/` changed. Check that the two correction notes distinguish historical result, incorrect historical description, corrected interpretation, and effect on prior acceptance, and that their factual claims are right (for example: do the gating M1/M2 GMAT scripts really use a point-mass force with `Earth.Mu`? does the JGM-3 `.cof` header really carry GM 3.986004415e14 and R 6378136.3 m — the latter is visible in VAL-0018/the probe results if GMAT is not installed).
4. Whether any unresolved numerical decision was accidentally converted into a default (termination altitude, C_d/A, dt, thresholds, reference missions, dataset cells).
5. Whether the atmosphere-table treatment faithfully represents its source: values preserved as published; discontinuities documented and quantified correctly (recompute the boundary jumps); the Q10 verification claims (what was and was not checked; 25/28 identical; the three residuals) are accurate and not overstated.
6. Whether any Rust/C/FFI/RTOS/embedded/hardware decision was accidentally made, and whether AC-1/PC-1 and AT-1…AT-7 are represented as the owner stated.
7. Correctness of the DR-0024 §3.5 analysis (the owner's stop condition on mixing WGS 84 GM/a with the EGM2008 J2), including the quoted relative magnitudes.

## Output
Your final message, in Markdown. One block per finding, numbered from M3P2-F1:

### M3P2-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Where:** file and section
**Claim:** ...
**Evidence:** ...
**Suggested resolution:** ...

Severity: BLOCKER — must not go to the Tech Lead as is (misrepresented owner decision, hidden M1/M2 change, implementation introduced, decision taken on the owner's behalf). MAJOR — substantive error or gap. MINOR — local inaccuracy. NOTE — observation.

Then a **Summary** with exactly one verdict: **PASS** (no findings at all, or NOTE only), **PASS_WITH_FINDINGS** (MINOR and/or NOTE), or **REQUEST_CHANGES** (any BLOCKER/MAJOR). List what you verified (with recomputed numbers) and state in one line whether the planning branch is ready to merge as planning/documentation evidence.
