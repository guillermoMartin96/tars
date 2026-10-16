# Milestone 3 — planning proposal (G0 approved: Option A; implementation not authorized)

**Status:** PLANNING. **G0 APPROVED (Tech Lead, 2026-10-15): Option A, J2 + atmospheric drag.** **G1–G3 RESOLVED (Tech Lead, 2026-10-15):** DR-0024, DR-0025 and DR-0026, recorded as ADR-0009; DR-0027 (termination value, table residuals) OPEN. The T0 spike is authorized after the planning branch merges; **T1 and later are not authorized**, and nothing here changes validated M1/M2 behaviour.  
**Status update (2026-10-15, second checkpoint):** DR-0024 Q4 and DR-0026 Q-G3-9 decided explicitly by the owner, with constraints. DR-0027 resolved with conditions (no numerical altitude; domain behaviour and crossing semantics proposed at T0). **DR-0028 OPEN** (Earth-fixed frame realization). **The planning merge and T0 both now need the Tech Lead's explicit approval of the planning checkpoint** ("Do not merge or begin T0 until I explicitly approve the checkpoint"). M3 implementation has not started; T1 and later are not authorized.  
**Status update (2026-10-15, third checkpoint):**
- **DR-0028 APPROVED: J-ax-1**, a non-rotating Earth-axis-aligned model with no Earth rotation angle and no Earth-orientation implementation.
- Review 03 findings M3P3-F1/F2 corrected.
- The planning merge and T0 each still need the Tech Lead's separate explicit authorization.  

**Status update (2026-10-16, seventh checkpoint):** review 07 finding M3P7-F1 corrected as DR-0028 Resolution amendment 4 (the verification script's `wrap()` domain is restricted to finite angles; non-finite inputs raise ValueError). No decision changed. Planning acceptance, the planning merge and T0 each still need the Tech Lead's separate explicit authorization; T1 and later are not authorized.  
**Status update (2026-10-16, sixth checkpoint):** review 06 findings M3P6-F1..F3 corrected as DR-0028 Resolution amendment 3 (line-of-nodes identity domain; asserted node discontinuity; angle wrapping), with the verification script revised. No decision changed. Planning acceptance, the planning merge and T0 each still need the Tech Lead's separate explicit authorization; T1 and later are not authorized.  
**Status update (2026-10-16, fifth checkpoint):** review 05 finding M3P5-F1 corrected as DR-0028 Resolution amendment 2 (signs of two first-order formulas; no decision changed), with a signed verification script. The planning merge and T0 each still need the Tech Lead's separate explicit authorization; T1 and later are not authorized.  
**Status update (2026-10-16, fourth checkpoint):** review 04 findings M3P4-F1/F2 corrected as an append-only DR-0028 Resolution amendment 1 (limitation statements only; no decision changed). The planning merge and T0 each still need the Tech Lead's separate explicit authorization; T1 and later are not authorized.  
**Planning baseline:** `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (verified in `M3-baseline-and-impact.md`).  
**Date:** 2026-10-15  
**Prepared after:** M2 accepted (2026-10-15) and merged (PR #3, merge commit `d92ab89`).  
**Requested by:** the Tech Lead's instruction "M2 Final Acceptance and M3 Planning Authorization", section C.

## 0. What the repository says about M3 (and what it does not)
- **No "original M3 objective" is recorded in this repository.**
  - There is no roadmap document (`docs/milestones/README.md`; DR-0010 #1).
  - The M2 plan lists only "Milestone 3 or later work" as a non-goal.
  - The only forward commitments on record are:
    - **M5:** Mission Laboratory alongside AI Navigator capabilities, with isolated mission forks, maneuver comparisons and safe recommendations (Tech Lead, 2026-10-15);
    - the architectural direction of ADR-0008 (TL-1…TL-9; research branch);
    - the playbook's ordering: headless simulator and AI crew Proof before any 3D work.
- **Consequently, §2 does not claim to restate an original objective.** It proposes candidate objectives derived from repository evidence. If the Tech Lead holds an M3 objective outside the repository, that objective supersedes this proposal (decision **G0** below).
- **Forward-looking evidence in the repository:**
  - **VAL-0007:** the M1/M2 model departs from realistic LEO physics by 0.7–1.3 thousand km in 15 hours. "J2 and drag must precede any mission that depends on real ground tracks, node timing, or orbit lifetime."
  - **SCI-0004:** drag and other perturbations are omitted "to be added later".
  - **ADR-0003:** the force-model boundary was designed for J2 and drag. Its reconsider trigger is "a force needs state beyond (t, r, v)", which drag meets because it needs mass.
  - **The M2 deferred list:** Δv-target and abort/cancel commands (DR-0014); sensors, attitude, thermal, multiple engines.
  - **The architecture chain:** `… propulsion → propellant/thermal effects → force → integration → state → sensors/telemetry`.

## 1. Relationship to M1 and M2
| Milestone | Delivered | What it leaves open |
|---|---|---|
| M1 Orbit | Deterministic point-mass two-body propagation (RK4, dt = 10 s), JSONL events, GMAT reference, cross-platform golden | No perturbations (SCI-0004); orbit never decays |
| M2 Propulsion | Simulator-owned mass and propellant, finite burns with exact step splitting, `BurnCommand` via `submit()`, O1–O9 validation, approved thresholds, reference snapshot, three-platform gate | Burns act in an idealized environment; maneuvers cannot be judged against realistic drift, decay or node regression |
| M3 (proposed) | Continue the simulator-first progression | — |

## 2. Candidate objectives (decision G0)
### Option A — Orbital environment: J2 and atmospheric drag (**recommended**)
**Objective:** add the two dominant LEO perturbations as validated force models, so that orbits and M2 maneuvers evolve realistically:
- node regression and apsidal motion from J2;
- orbit decay from drag.

**Why first:**
- It is the gap the repository's own evidence ranks highest (VAL-0007).
- It is pure physics behind an existing, designed boundary (ADR-0003).
- It reuses the GMAT workflow: VAL-0007 already ran J2 and Jacchia-Roberts drag informationally.
- It is a prerequisite for meaningful M5 maneuver comparisons. Comparing maneuvers in an environment without decay or J2 would mislead the Navigator.

### Option B — Command authority and maneuver operations (alternative)
- **Scope:** Δv-target cutoff and abort/cancel commands (DR-0014 candidates), plus a deterministic `CommandProposal` → authorization → `submit()` boundary (ADR-0008 TL-4), with role permissions enforced in code (architecture invariant 2). No LLM.
- **Pros:** prepares the crew and M5 interfaces, and the Flight Core command boundary.
- **Cons:**
  - It defines crew-permission semantics before the crew milestone exists, and risks pre-empting M5 design.
  - Its physics is unchanged, so it adds little scientific capability.
  - It needs the AT-2 decision (where authorization runs).

### Option C — Sensors and navigation state (not recommended now)
- Sensor models (noise, bias) and an onboard navigation estimate, replacing truth-state telemetry.
- Large new science.
- Depends on Flight Core requirements that do not exist yet (ADR-0008 AT-5).

**Recommendation: Option A.** The rest of this proposal details Option A. Option B could follow as M4, before M5.

**G0 decision (Tech Lead, 2026-10-15): Option A APPROVED.** M3's purpose is to improve orbital and environmental fidelity before later sensors, navigation, AI Navigator and Mission Laboratory work. This proposal remains planning material, not implementation authorization. Where the G1–G3 drafts refine §3–§5 below, the Decision Requests take precedence.

## 3. Proposed M3 scope (Option A)
### In scope
1. **J2 zonal gravity:**
   - an additive force model behind the `ForceModel` boundary;
   - an Earth pole aligned with the frame's z-axis (a new SCI entry: no precession or nutation, consistent with SCI-0003);
   - J2, μ and R_e from one cited constant set (WGS 84 vs EGM/JGM values: a science decision, G1).
2. **Atmospheric drag:**
   - a = −½ ρ (Cd·A/m) |v_rel| v_rel, with v_rel relative to an atmosphere co-rotating with Earth (ω_E, cited);
   - spacecraft Cd and area added to the spacecraft spec;
   - mass from the M2 state, which meets the ADR-0003 reconsider trigger and needs a reviewed extension of the force signature.
3. **One deterministic atmosphere model, chosen by DR (G1):**
   - **exponential/static (recommended first):** deterministic, analytic oracles, available in GMAT;
   - or a solar-flux-driven model, with fixed F10.7/Kp inputs.
   - Space-weather data ingestion is out of scope.
4. **Scenario schema extension:**
   - `force_models` entries and drag parameters;
   - v1/v2 scenarios unchanged;
   - new scenario files only.
5. **Events:**
   - the existing events carry the new physics;
   - possible additive fields, for example a drag acceleration sample (contract amendment, reviewed);
   - an explicit "orbit decay / re-entry" outcome, using the existing `impact` cause if sufficient (decided in the contract task).
6. **Validation and Proof (§5)**, a threshold DR after measurement, and the full Proof with independent review.

### Explicit non-goals (deferred)
- **Rust or any C implementation, or migration** (ADR-0008 TL-9). M3 is Python only.
- **AI Navigator, AI crew, LLM integration and agent tooling.** The **Mission Laboratory forks, maneuver comparison and safe recommendations belong to M5** and are not started here.
- Crew permissions and the authorization layer (Option B / later; ADR-0008 AT-2).
- Higher-order harmonics (beyond J2), third bodies, SRP, tides, relativity, Earth orientation (precession/nutation/polar motion), space weather.
- Attitude dynamics; lift; variable or attitude-dependent area; sensors; thermal.
- Changing M1 or M2 scenarios, thresholds, references, goldens or semantics.
- Δv-target and abort commands (Option B).
- 3D.

## 4. Proposed tasks, gates and review checkpoints
| # | Task | Depends on | Gate / output | Independent review |
|---|---|---|---|---|
| P0 | Planning Decision Requests: G1 (**DR-0024**), G2 (**DR-0025**), G3 (**DR-0026**). Drafted and reviewed 2026-10-15 (VAL-0018; `M3-planning-review-01.md`); **resolved by the Tech Lead 2026-10-15**; ADR-0009; DR-0027 OPEN. (Called "T0" in earlier drafts; renamed because the Tech Lead's T0 is the spike below.) | G0 (approved) | Resolved DRs; SCI-0013…0017 approved (not implemented) | Codex (`M3-planning-review-01.md`, `M3-planning-review-02.md`) |
| T0 | **Reference-configuration spike (authorized 2026-10-15, after the planning merge; since narrowed: it also needs the Tech Lead's explicit approval of the planning checkpoint):** also the DR-0027 A-4/A-5/A-6/A-s/B-4 proposals; labelled DR-0028 realization; executable reference configurations for the planned J2 and drag/atmosphere cases; GMAT configurations verified to represent the intended physics; planning measurements reproduced; every band boundary exercised and the discontinuities quantified; geodetic height and atmosphere-relative velocity verified; perturbations-off compatibility with M1/M2; any new DR identified. **Minimum isolated spike code only; no production architecture, no thresholds, no M1/M2 regeneration** | P0 | Spike evidence (VAL record); candidate reference missions, C_d/A, GMAT method; T1 READY / BLOCKED recommendation | Codex (T0 review); stop at checkpoint |
| T1 | J2 force model, pure; analytic unit tests (secular Ω̇, ω̇ rates, energy and polar angular-momentum conservation) | G1 | Unit-level VAL record | Codex |
| T2 | Drag force model and spacecraft Cd/A; force-context extension (mass); analytic tests (decay rate vs an approximate semi-analytic estimate; behaviour outside the table per the G1 domain policy; energy monotonicity) | G1, G3 | Unit-level VAL record; architecture scan; M1/M2 byte-identity | Codex |
| T3 | Scenario and runner integration, contract amendment, new reference scenarios (J2-only, drag-only, J2+drag, J2+drag+M2 burn) | T1, T2 | Mission tests; M1/M2 goldens unchanged | Codex |
| T4 | Validators and an M3 Proof script; **provisional** `m3.json`; independent DOP853 reference with the same force models | T3 | Measured metrics (VAL) | Codex |
| T5 | GMAT M3 references (J2 and the chosen atmosphere, exact configuration), digest-pinned; reference snapshot extension or a separate M3 snapshot (DR-0021 procedure) | G2, T4 | Committed references; O-gates | Codex |
| T6 | Three-platform measurement, then the **threshold DR** | T4, T5 | Approved `m3.json` | Codex |
| T7 | Full M3 Proof, Proof record, README, milestone review | T6 | Proof PASS | Codex (milestone) |

Every task follows the M2 workflow:
- small commits pushed to `milestone-3-…`;
- CI green on the DR-0008 matrix;
- every finding dispositioned (ACCEPTED, REJECTED_WITH_REASONING or ESCALATED_FOR_INVESTIGATION), with unresolved High findings blocking;
- a stop at each Tech Lead gate.

## 5. Numerical and physical validation requirements (proposed oracles; superseded in detail by DR-0025)
| # | Oracle | What it proves | Independence |
|---|---|---|---|
| Q1 | J2 secular rates: Ω̇ = −(3/2) n J2 (R_e/p)² cos i, and ω̇ | J2 implementation and frame | Analytic (first-order; a mean-vs-osculating caveat as in VAL-0007) |
| Q2 | J2 conservation: energy (with the J2 potential) and the polar angular-momentum component h_z | Conservative-force integration | Analytic invariants |
| Q3 | Independent DOP853 integration with identical force models | Full trajectory, J2 and drag | Independent integrator (SciPy, dev dependency) |
| Q4 | Drag decay vs analytic estimate for a near-circular orbit in an exponential atmosphere: Δa per revolution ≈ −2π ρ (Cd·A/m) a² | Drag magnitude and direction | Analytic, approximate (tolerance from theory, not tuned) |
| Q5 | Drag direction: anti-parallel to v_rel; energy strictly decreasing; behaviour outside the table per the approved G1 domain policy (DR-0024 recommends extrapolation, not a cutoff) | Sign and frame errors | Exact rules |
| Q6 | RK4 convergence order with J2 and drag, including with M2 burns | Integration correctness | Numerical self-consistency |
| Q7 | GMAT R2026a with matched J2 constant and atmosphere configuration (exact-configuration gate as in O9) | External trusted tool | External |
| Q8 | M1/M2 regression: golden hashes, M2 Proof 228/228, M2 snapshot unchanged | No regression | Existing gates |
| Q9 | Determinism and cross-platform: byte-identical same-platform replay; three-platform final-state bounds measured, never borrowed from M1/M2 | Reproducibility | Existing method (DR-0008/DR-0023) |

**Threshold method:** as in DR-0015/DR-0023.
- Candidates are measured on the implementation across the three platforms, then approved in a threshold DR.
- No tolerance is set below a measured noise floor without independent justification.
- **Drag amplifies along-track error growth**, so the M1/M2 bounds must not be assumed to transfer (VAL-0007 phase drift).

## 6. Dependencies
- **G0 (Tech Lead):** confirm M3's objective. Option A is recommended, unless an original objective exists outside the repository.
- **G1 (science DR):**
  - the J2 and constant set: WGS 84 J2 vs an EGM/JGM value, kept consistent with GMAT;
  - Earth rotation rate;
  - the atmosphere model and its parameters;
  - the spacecraft Cd and area, illustrative with a cited basis, as in DR-0010.
- **G2 (validation DR):** the oracle set, the GMAT configuration, and the reference-snapshot treatment (extend vs a new snapshot under DR-0021 condition 3).
- **G3 (architecture DR):** a force-context object (ADR-0003 trigger), the scenario schema extension, and event additions (contract amendment).
- **Tooling:** GMAT R2026a on the reference host (exists); SciPy (exists). No new runtime dependency is expected. An atmosphere library would need a DR (playbook dependency rule).

## 7. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Constant mismatch with GMAT (J2 value, R_e, ω_E, atmosphere constants) gives false discrepancies | Medium | False FAIL or masked error | Exact-configuration gate (O9 precedent); a single constants module |
| Atmosphere model not reproducible or not matchable in GMAT | Medium | Weak external validation | Start with an exponential/static model; flux-driven only with fixed inputs |
| Drag amplifies cross-platform drift beyond the M1/M2 bounds | Medium | Threshold surprises | Measure first (Q9); a separate M3 threshold DR |
| Extending the force signature with a mass context breaks M1/M2 byte identity | Low–Medium | Regression | M1/M2 goldens and the M2 Proof as gates in every task |
| Scope creep into M5 (forks, comparisons) or the crew layer | Medium | Violates this plan and the playbook | Non-goals above; reviewer prompt includes the scope check |
| Re-entry/decay outcome semantics ambiguous | Medium | Contract churn | Decide in G3 before the runner work |
| Reference-snapshot growth and baseline-change overhead | Medium | Effort | Decide snapshot structure in G2 |

## 8. Architectural boundaries worth preparing for a future Flight Core (documentation and design only; ADR-0008 TL-8)
These are recommendations for how M3 code is *shaped*, all within Python and without changing validated M1/M2 behaviour:
1. **Pure force models.** Each acceleration is a function of (t, r, v, context) with no I/O, global state or allocation-dependent semantics. Parameters live in immutable, fixed-size structures. This is the subset a Flight Core would port.
2. **An explicit force-context type** (mass, Cd·A, Earth rotation) instead of ad-hoc arguments. It becomes a natural FFI/`no_std` struct later.
3. **Constants in one module** with provenance (already the practice; extend it to J2, ω_E and atmosphere parameters).
4. **No new unbounded structures** in the propagation path. Any new per-step data has a stated bound.
5. **Simulation-only artefacts (events, JSONL, validation) stay outside force models**, keeping the Flight Core / Mission Laboratory split visible.

None of these needs the M2 code to change. Changes to existing M2 structures (for example bounding the burn queue) remain under ADR-0008 AT-6 and need separate approval.

## 9. Decision gates requested
| Gate | Decision | Blocks |
|---|---|---|
| **G0** | M3 objective. **APPROVED 2026-10-15: Option A** | Everything (now unblocked for planning only) |
| **G1** | Physical models and constants: **DR-0024, RESOLVED 2026-10-15** (Q4 axis flagged for confirmation); DR-0027 OPEN. *Update 2026-10-15: Q4 APPROVED with constraints; its realization OPEN (DR-0028). DR-0027 RESOLVED WITH CONDITIONS; T0 proposals pending. Update (third checkpoint): DR-0028 APPROVED J-ax-1* | T1/T2 (DR-0028; lifted by the J-ax-1 decision); T2 (DR-0027 T0 items) |
| **G2** | Validation strategy: **DR-0025, RESOLVED 2026-10-15** (principles; Q-G2-1, 5, 7 deferred to the T0 checkpoint, Q-G2-6 to T4) | T4–T6 |
| **G3** | Architecture and physics versioning: **DR-0026, RESOLVED 2026-10-15 (D3); ADR-0009**. *Update 2026-10-15: Q-G3-9 APPROVED with constraints (approximate diagnostic only); Q-G3-7 NOT AUTHORIZED* | — |
| G4 | M3 thresholds (after T6 measurement) | Proof |
| G5 | M3 acceptance and merge | — |

**Requested response (updated 2026-10-15, after the decision checkpoint):** G0–G3 are resolved. Open: DR-0027; the items deferred to the T0 checkpoint; confirmation of DR-0024 Q4 and DR-0026 Q-G3-9; and a separate authorization before T1 begins.

**Requested response (updated 2026-10-15, second checkpoint; supersedes the paragraph above):** Q4 and Q-G3-9 are decided; DR-0027 is resolved with conditions. Open: DR-0028; the DR-0027 items proposed at T0; the items deferred to the T0 checkpoint (DR-0025 Q-G2-1, Q-G2-5, Q-G2-7; DR-0024 Q9 values); Q-G2-6 (T4). Needed from the Tech Lead: explicit approval of the planning checkpoint before the planning merge and before T0; a separate authorization before T1. The full matrix is in `M3-decision-matrix.md`.

**Requested response (updated 2026-10-15, third checkpoint; supersedes the paragraph above where it differs):** DR-0028 is decided (J-ax-1). Still open:
- the DR-0027 items proposed at T0;
- the T0-checkpoint deferrals (DR-0025 Q-G2-1, Q-G2-5, Q-G2-7; DR-0024 Q9 values);
- Q-G2-6 (T4).

Needed from the Tech Lead: acceptance of the planning checkpoint; then, separately, authorization of the planning merge and of T0; later, a separate authorization before T1.
