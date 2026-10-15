# Decision Request: M3 force, scenario and event architecture; physics versioning (gate G3)

**Status:** RESOLVED — D3 APPROVED with constraints (Tech Lead, 2026-10-15); the decay-termination value stays OPEN (DR-0027). Recorded as ADR-0009. Where the request body differs from the Resolution, the Resolution governs. Implementation not authorized by this resolution.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A (G0 approved 2026-10-15).
- Planning baseline: `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f`.
- Companions: DR-0024 (G1 physics), DR-0025 (G2 validation).
- Impact analysis: `docs/milestones/M3-baseline-and-impact.md`.
- Accepted constraints: ADR-0002 (state ownership, units, time), ADR-0003 (force boundary; reconsider trigger "a force needs state beyond (t, r, v)"), ADR-0004 (RK4), ADR-0005 (events, scenarios), ADR-0007 (propulsion; reconsider trigger "mass-dependent non-thrust forces (drag)").
- ADR-0008 is proposed, on the research branch: TL-1 to TL-9 accepted, AT-1 to AT-7 open.

Design only. No code is changed by this request, and no FFI, Rust crate, C ABI, JSONL adapter or language migration is proposed or authorized (ADR-0008 TL-9).

## 1. Current architecture (as built at `d92ab89`)
| Concern | Where | Shape |
|---|---|---|
| State | `tars.sim.simulator.Simulator` | y = [r, v] (M1 path), or y = [r, v, m_prop, Δv_sensed] with a spacecraft (ADR-0007). It is private and committed atomically per tick, and exposed only as read-only snapshots (ADR-0002). |
| Forces | `tars.sim.forces` | `ForceModel` protocol `acceleration(t, r, v) -> ndarray[3]`; `PointMassGravity(mu)`; `CompositeForceModel` sums the components in list order, starting from `np.zeros(3)`. |
| Thrust | `tars.sim.propulsion` + `Simulator._powered_derivative` | A separate subsystem, not a `ForceModel`. The powered RHS computes `force_model.acceleration(t, r, v) + thrust` and uses mass from y (ADR-0007). |
| Integrator | `tars.sim.integrators.RK4` | Sees only f(t, y). Ticks are split at engine events (DR-0013 3A). |
| Constants | `tars.sim.constants` | `EarthConstants(name, mu, equatorial_radius)` with the instance `WGS84`; `STANDARD_GRAVITY`; `EARTH_J2_APPROX` (informational). |
| Scenario | `tars.sim.scenario` | v1 `Scenario`: `force_models: tuple[Literal["point_mass_gravity"], ...]`, `earth_constants: Literal["WGS84"]`. v2 `ScenarioV2` adds the spacecraft (with a required engine), commands and a duration stop. `config_hash()` is the sha256 of the canonical scenario JSON. |
| Building | `tars.sim.runner.build_force_model` | A name → constructor registry over `scenario.force_models`. |
| Events | `tars.events.schema` | `SimulationStarted` records the scenario hash, `software_version` (a static `0.1.0`), constants (name, mu, radius), force-model *names*, integrator and dt. Additive M2 types (strict). `SimulationCompleted.failure_cause ∈ {impact, escape, timeout, non_finite}`. |
| Termination | `runner` | `impact` at spherical altitude ≤ 0 (SCI-0006); `escape` at two-body specific energy ≥ 0. |
| Evidence binding | validators, GMAT, goldens | References are bound to `scenario_hash`, plus pinned digests (thresholds, GMAT manifest, snapshot, M2 golden). |
| Static guards | `tars.validation.architecture` | The physics core must not import randomness, time, OS, `importlib` or `tars.validation`; no LLM or 3D SDKs. |
| Consumers of the old protocol | `tars.validation.m2.FreeSpace` and test doubles | Implement `acceleration(t, r, v)`. **Frozen M2 validator code.** |

## 2. Problems M3 introduces
1. **Drag needs the current mass.** This is the ADR-0003 and ADR-0007 reconsider trigger. Mass lives in y[6] only when a spacecraft is configured, and inside RK4 stages it differs from the committed value.
2. **Drag needs spacecraft properties (C_d, A),** which belong to the spacecraft, not the environment. The v2 `SpacecraftConfig` requires an engine, but a drag-only spacecraft has none.
3. **New pinned physics** (J2, its reference radius, flattening, ω_E) and a **pinned dataset** (the atmosphere table) need ownership, provenance and identity.
4. **"Same scenario, different physics."**
   - `scenario_hash` covers the scenario text only. Constants are referenced by name (`"WGS84"`), and force models by unversioned names.
   - If a model's equations or constants changed in code, an unchanged scenario would silently mean different physics.
   - Today only the goldens would notice, by failing, not by explaining.
5. **Event content.** The physics actually applied must be machine-readable at run start. Decay needs a defined end semantics (DR-0024 Q8).
6. **Floating-point determinism of composition.** The bits depend on summation order, so the order must be canonical, not incidental.
7. **Domain and error behaviour** of new components (density extrapolation, height conversion) must be total and deterministic.
8. **M1/M2 must stay byte-identical,** including the frozen M2 validator code that implements the old protocol.
9. **Validation seams:** components must be evaluable alone for unit oracles and mutation tests (DR-0025 §8).
10. **Foreseeable forces.** None is implemented now, but the design must not block them:
    - higher-order gravity (needs Earth rotation angle and time);
    - third body (ephemerides, time);
    - SRP (Sun position, shadow, area, C_R, mass);
    - attitude-dependent aerodynamics (attitude state).

## 3. Architectural requirements
- **AR-1 Integrator decoupled.** The integrator sees only f(t, y). Force models never see the integrator or y's layout. This is already true, and it stays true.
- **AR-2 Pure force evaluation.** Each force is a deterministic function of (t, r, v, context) and immutable parameters. No I/O, globals, caches with mutable state, randomness or clock. The existing static guard extends to new modules.
- **AR-3 Minimal context.** Per-evaluation, read-only spacecraft quantities that a force needs and the state owns, which in M3 is total mass only. Built by the simulator from the stage state y.
- **AR-4 Canonical order.** Components are summed in a fixed, documented order, independent of scenario list order.
- **AR-5 Explicit physics identity.** A canonical, hashable description of the applied physics: model identifiers and versions, constant values, dataset digests. It is recorded in run events and in every M3 reference, and comparing against a different identity is refused.
- **AR-6 v1/v2 frozen.** Schemas, code paths and bytes are unchanged. The M1 golden `7a4e1877…`, the M2 Proof, the snapshot and the M2 golden all pass unchanged.
- **AR-7 Ownership:**
  - universal constants: a pinned module;
  - datasets: pinned files plus digests in reviewed source;
  - spacecraft properties: the scenario;
  - environment selection: the scenario, by identifier only.
- **AR-8 Errors:**
  - configuration errors at scenario validation: unknown identifier, missing drag properties, drag without mass, non-positive C_d or A, dataset digest mismatch;
  - runtime functions are total;
  - non-finite results use the existing `FloatingPointError` → `non_finite` path.
- **AR-9 Seams.** Each component is constructible and evaluable alone. The composite exposes its components. The validator-side reference models live in `tars.validation`, never imported by the physics core.
- **AR-10 Language-neutral data.** The physics identity serializes to canonical JSON. Force parameters are plain fixed-size data. This is preparation only (TL-8).

## 4. Candidate designs
### D1 — Inject mass through mutable state on the force object
`drag.mass = …` is set before each evaluation.
- **Pros:** no signature change.
- **Cons:**
  - hidden mutable state shared across RK4 stages;
  - breaks AR-2;
  - unsafe for any future forked or isolated run (Mission Laboratory);
  - order-dependent bugs.

### D2 — Context-object signature (the ADR-0003 plan)
A new protocol `acceleration(t, r, v, ctx: ForceContext) -> Vector`, where `ForceContext` is a frozen record (`total_mass_kg`, absent for a massless M1 state).
- Gravity components ignore it.
- Old-protocol models are wrapped by an adapter that calls them unchanged, so the frozen M2 validator code and test doubles keep working.
- The point-mass-only path keeps identical arithmetic: start from `np.zeros(3)`, left-fold in order.
- **Pros:**
  - smallest change that answers both reconsider triggers;
  - pure;
  - extensible by adding context fields when a real force needs them (attitude).
- **Cons:**
  - one signature change in the simulator's derivative functions;
  - an adapter to maintain.

### D3 — D2 plus explicit environment components and a physics identity
D2, plus:
- **a density-model component** `density(r) -> ρ`, built from a height function (spherical or geodetic) and a profile (the pinned table), injected into the drag force;
- **a `PhysicsConfiguration`** (immutable): the constants set, an ordered list of (model id, version, parameters), dataset digests, a canonical JSON and `physics_id = sha256(canonical JSON)`;
- **scenario schema v3** with an `environment` block and a spacecraft with mass properties, optional engine and optional drag properties;
- **one additive event** recording the identity.

Each piece answers a listed problem (P2–P5, P9). Nothing is added for an unlisted force.

### D4 — General plugin framework
Forces declare their state requirements, dynamic state augmentation, a generic environment service bus, and runtime registration of models.
- **Pros:** maximal flexibility.
- **Cons:**
  - speculative;
  - large untested surface;
  - dynamic registration conflicts with the static determinism guard (no `importlib`) and with the identity requirement;
  - over-engineered for one mass-dependent force.

## 5. Recommended design: D3 **[recommendation; not approved]**
### 5.1 Dependency direction
```
scenario (v3, data)  ──►  PhysicsConfiguration (immutable; physics_id)
                                │ builds
                                ▼
constants / datasets  ──►  force components (pure)  ──►  ForceSet (canonical order)
                                                              │ acceleration(t, r, v, ctx)
Simulator (owns y; builds ctx from stage y) ──► derivative f(t, y) ──► Integrator (RK4)
                                ▲
                    propulsion subsystem (thrust added last; ADR-0007 unchanged)
validators / references ──► PhysicsConfiguration.physics_id (refuse mismatch)   [tars.validation only]
```
- Arrows point from dependent to dependency. The physics core depends on nothing in `tars.validation` (existing guard).
- The runner builds the configuration from the scenario. The simulator receives already-built, immutable objects.

### 5.2 Force-composition model
- **Superposition** (Newton's second law): a_total = Σ a_i + a_thrust.
- **Canonical order:**
  1. conservative gravity (point mass, then J2);
  2. non-conservative environment forces (drag);
  3. thrust, added last by the powered derivative exactly as today.
- The order is fixed by the configuration builder, not the scenario's list order.
  - For a point-mass-only configuration the arithmetic is bit-identical to today's `CompositeForceModel`.
  - The regression gates enforce this.
- **Context:** `ForceContext(total_mass_kg)`. The simulator computes the mass inside the derivative from the stage state as `m_dry + max(m_prop, 0)`, the existing M2 rule (review N4). It is not taken from the committed state, so drag sees the same mass the thrust term sees in every RK4 stage.
- **Drag without a spacecraft:** rejected at scenario validation, because there is no mass. **Drag-only spacecraft:** v3 allows mass properties without an engine (P2).

### 5.3 State and configuration ownership
| Item | Owner | Mutability | Identity |
|---|---|---|---|
| r, v, m_prop, Δv_sensed | Simulator | Changed only by `step()` (ADR-0002) | — |
| Universal constants (GM, a, J2, f, ω_E) | `tars.sim.constants`, a named pinned set | Immutable; a change creates a new named set | Values included in `physics_id` |
| Atmosphere table | A pinned data file plus its sha256 in reviewed source (the `approved_digests` pattern) | Immutable; a change creates a new dataset id | Digest included in `physics_id` |
| Spacecraft mass and drag properties | Scenario | Immutable after validation | Included in `scenario_hash` (and `physics_id` for drag parameters) |
| Environment selection (model ids, height definition, dataset id) | Scenario, by identifier only; **no inline constant overrides** | Immutable | Included in `physics_id` |
| Integrator, dt | Scenario (unchanged) | Immutable | `scenario_hash` |

### 5.4 Scenario and versioning strategy
- **v1 and v2 are frozen.** Their schemas keep `Literal["point_mass_gravity"]` and `Literal["WGS84"]`. Their implicit physics identity is "point-mass gravity with WGS 84, plus M2 propulsion", defined by schema version.
  - It is **not** added to their events, which would change M1/M2 bytes. It is documented instead.
  - An old file can never acquire J2 or drag.
- **v3 (new, M3).** Its fields are:
  - `schema_version: 3`;
  - `environment`: a constants set id, plus gravity, atmosphere, height definition and atmosphere-rotation model ids with versions and a dataset id;
  - `spacecraft`: `dry_mass_kg`, `propellant_kg`, an optional `engine`, and optional `drag: {cd, area_m2}`;
  - the existing initial orbit, integrator, dt, commands, stop and telemetry semantics;
  - an optional end condition (§5.6).
- **Model identifiers are versioned:** for example `zonal_j2@1`, `drag_cannonball@1`, `exp_table_density@1`, `height_geodetic_wgs84@1`.
  - Changing a model's equations, constants or algorithm creates a new version, and so a new `physics_id`.
  - Reusing an identifier for different physics is the defect this mechanism prevents.
- **`physics_id`** = sha256 of the canonical JSON of the full `PhysicsConfiguration`, including numeric values and dataset digests. It is recorded:
  - in a new additive event `PhysicsConfigured`, emitted after `SimulationStarted` for v3 runs only;
  - in every M3 golden, GMAT M3 metadata, snapshot record, threshold-file basis and Proof record.
- **Validators refuse** to compare a run with a reference of a different `physics_id`, in the same way they already refuse a different `scenario_hash`.
- **Retention policy (owner choice, Q-G3-5):**
  - (a) only the current version of each model is executable; historical evidence stays reproducible at its recorded git revision, and stale references fail visibly by identity mismatch;
  - (b) every released model version stays executable side by side.
  - **Recommended: (a).** (b) multiplies maintained code without a present need. M1/M2 stay executable because their v1/v2 path is frozen code.

### 5.5 Events (additive only)
- **`PhysicsConfigured`** (v3 only; strict, frozen, the M2 sub-base style). Fields: `physics_id`, constants set (name and values), ordered models (id, version, parameters), dataset ids and digests, height definition.
- **No per-sample drag telemetry event in M3 (recommended).**
  - Validators recompute density and drag from state plus `physics_id`, which avoids a second source of truth.
  - An additive `EnvironmentSampled` event can be proposed later if a consumer needs it. The Mission Laboratory or the Navigator are possible consumers, but not M3.
- **End semantics for decay** (with DR-0024 Q8). The options are in §5.6.
- `software_version` remains as it is (M1 bytes). M3 identity rests on `physics_id`, and the code revision is recorded in evidence records.

### 5.6 End conditions under decay (owner choice, Q-G3-6)
- **(a)** Keep only `impact` (spherical altitude ≤ 0). Simple, but it integrates a drag model through altitudes where its assumptions fail.
- **(b)** Add a v3 end condition `altitude_floor_m` (value set per scenario, justified by the owner per DR-0024 Q8). Reaching it ends the run as a defined outcome, `reentry`. This is an **additive** value of `failure_cause`, or a stop reason, whichever the owner prefers semantically.
  - Mission success or failure is then scenario-defined: a lifetime mission expects it.
- **Recommended: (b)**, with no default altitude in code.
- The `escape` check keeps using two-body energy. With J2 the osculating energy differs by ~1e-3 relative, which is irrelevant at LEO. Recorded as a known simplification.

### 5.7 Units, frames and time
- **SI internally.** Datasets are converted at load and their digest covers the source bytes.
- **Every force returns an ECI acceleration.** Body-frame work (the J2 axis, the ellipsoid) is internal to the component.
  - In M3 the body axis is the frame z axis (DR-0024 J-ax-1), so no Earth-orientation provider exists.
  - A future time-dependent orientation would be an injected, immutable provider. It is not built now.
- **Time stays t = tick · dt** in elapsed TT seconds (ADR-0002, SCI-0007). M3 forces do not depend on absolute time.
  - The signature already carries t, so third body, SRP and tesserals can later obtain absolute time from a typed epoch in the configuration, which they would require.

### 5.8 Error handling and unsupported domains
- **Configuration:** Pydantic validation (strict, as v2) rejects unknown ids, version mismatches, missing or invalid drag properties, drag without mass, and dataset digest mismatch. It runs before any physics.
- **Runtime:**
  - density is total (extrapolated bands, DR-0024 §4.6);
  - the height conversion is deterministic, with a fixed iteration count or a closed form, and is total;
  - J2's singularity at r = 0 is unreachable before impact, with the existing guard kept.
- **Non-finite:** the existing `FloatingPointError` path reports `non_finite`. Atomic ticks are unchanged.

### 5.9 Serialization and reproducibility
- `PhysicsConfiguration.canonical_json()` uses the same convention as `Scenario.canonical_json()`: sorted keys, compact separators, JSON floats.
- Same-platform byte-identical replay (DR-0006) applies to v3.
- Cross-platform bounds come from measurement (DR-0025 §7).

### 5.10 Validation and test seams
- Each component is constructible from plain parameters and callable alone. These seams serve the DR-0025 unit oracles Q2–Q4 and Q13.
- `ForceSet.components` is exposed read-only, so tests can evaluate and mutate components individually (DR-0025 §8).
- The `PhysicsConfiguration` builder is a pure function of (scenario, pinned registries), testable without running a simulation.
- Validator-side reference models (DR-0025 Q7) live in `tars.validation`, coded separately.
- Regression seams are the M1/M2 gates.

## 6. Future extensibility analysis (no future force is implemented or designed in detail)
| Force | Needs | Blocked by D3? |
|---|---|---|
| Higher-order gravity (n×m) | Earth rotation angle (UT1) and EOP. Absolute time from a typed epoch; an orientation provider | No: a new component and version; absolute time added to the configuration when justified |
| Third body (Sun, Moon) | Ephemerides(t), dataset digest, epoch | No: a new component plus a pinned ephemeris dataset in `physics_id` |
| SRP | Sun position, Earth shadow, area, C_R, mass | No: ctx has mass; spacecraft properties gain an SRP block; the ephemeris is shared with third body |
| Thrust | — | Stays in the propulsion subsystem (ADR-0007). Folding it into the `ForceSet` is possible later but not proposed |
| Attitude-dependent aerodynamics | Attitude state, an area model | No: ctx gains a field. Attitude **dynamics** would be a state-container change (ADR-0002 reconsider), outside this design |

## 7. Language-boundary implications (no migration authorized)
- **Pure force functions over plain, fixed-size parameters** are the subset a future Flight Core would port first (ADR-0008, layer 1). Nothing here selects Rust or C (TL-6, TL-9).
- **The canonical `PhysicsConfiguration`** is a language-neutral specification of "which physics". If a second implementation is ever authorized, cross-language comparison can be defined against the same `physics_id`, with its own measured thresholds (TL-7, AT-3). No JSONL adapter or FFI is proposed.
- **The canonical summation order and the explicit constants** remove two common sources of cross-implementation bit differences.
- **No unbounded allocation in force evaluation** (the table is fixed-size). This is recorded, not enforced, as preparation only (AT-6).

## 8. Mission Laboratory awareness (not designed or implemented)
The future isolated-fork capability (M5) needs runs that cannot affect each other or the live state. D3 helps without building anything:
- immutable configurations shareable across forks;
- pure forces with no global caches;
- state owned by one `Simulator` instance;
- `physics_id` lets compared runs prove they used the same physics.

D1 would have made this harder (shared mutable force state). Nothing else is added for M5.

## 9. Rejected alternatives
- **D1** (mutable mass injection): violates AR-2 and is fork-unsafe.
- **D4** (plugin framework): speculative; conflicts with static determinism guards.
- **Editing v2 or v1 in place** (adding optional `environment` fields): changes `model_dump`, hence `scenario_hash` and M1/M2 bytes. This is the T4 lesson recorded in ADR-0007.
- **Inline constant overrides in scenarios** (ADR-0003 permitted them in principle, but the M1 schema never implemented them): they multiply physics identities and make provenance per-file. New sets are added as reviewed, named, pinned sets instead.
- **Drag inside the propulsion subsystem:** wrong ownership. Drag is environment physics that uses mass, not engine activity.
- **Recording physics identity in v1/v2 events:** changes M1/M2 bytes (AR-6).

## 10. Impact on artifacts
See `docs/milestones/M3-baseline-and-impact.md` for the full A/B/C classification. In short:
- M1/M2 artifacts are frozen.
- M3 adds new scenarios (v3), goldens keyed by `physics_id`, GMAT M3 references with `physics_id` in their metadata, `m3.json`, the Proof record, and possibly an M3 snapshot.
- Shared infrastructure (scenario loader, event schema, runner, simulator, constants, digests) gains additive paths only, with the v1/v2 paths unchanged and regression-gated.

## 11. Owner decisions required (BLOCKED ON OWNER)
| # | Decision | Recommendation |
|---|---|---|
| Q-G3-1 | Force signature: D2 context object (with a legacy adapter) | Approve D2 |
| Q-G3-2 | Adopt D3's additions: density component, `PhysicsConfiguration` / `physics_id`, scenario v3, `PhysicsConfigured` event | Approve |
| Q-G3-3 | Validators refuse comparisons across different `physics_id` | Approve |
| Q-G3-4 | No inline constant overrides; named pinned sets only | Approve |
| Q-G3-5 | Model-version retention: (a) current only, historical reproducible at its revision; or (b) all versions executable | (a) |
| Q-G3-6 | Decay end semantics: (a) impact only; (b) `altitude_floor_m` with outcome `reentry` (value per scenario, owner-justified) | (b), no default value |
| Q-G3-7 | Per-sample environment telemetry: none in M3 (validators recompute), or an additive event now | None in M3 |
| Q-G3-8 | Canonical summation order: gravity (point mass, J2) → drag → thrust | Approve |
| Q-G3-9 | `escape` check stays two-body energy | Approve, recorded as a simplification |
| Q-G3-10 | v3 spacecraft may have mass and drag properties without an engine | Approve |
| Q-G3-11 | Record the lasting design as ADR-0009 (PROPOSED until implemented and proven) | Yes, after this request resolves |

## Impact
- **Architecture:** one signature change behind an adapter; new additive modules; scenario v3; one additive event.
- **Science/validation:** enables DR-0025 seams and identity checks.
- **Dependencies:** none.
- **Development effort:** moderate.
- **Token/compute impact:** negligible.
- **Reversibility:** high before implementation. After it, identities make every change visible.

## Blocked work
- M3 T2 (drag integration) and T3 (scenario, runner, events) are blocked on this request.
- T1 (pure J2 component) can only start under the D2 signature, once that is approved.

## Work continuing independently
- None of the implementation.

## Requested response
Answers to Q-G3-1 to Q-G3-11, or `discuss`.

## Resolution
**Decision:** **D3 APPROVED with constraints** (Tech Lead, 2026-10-15, "M3 planning decision checkpoint", section 3). Nothing in this resolution authorizes Rust, C, FFI, firmware, RTOS, real-time execution or embedded deployment work, or any M3 implementation.

| # | Closure | Status |
|---|---|---|
| Q-G3-1 | A small **immutable** force-evaluation context with the minimum shared runtime state forces need, including current total mass; the old force signature preserved through an adapter so frozen M1/M2 behaviour stays reproducible. **Mutable mass is never injected into force implementations** (D1 rejected) | APPROVED |
| Q-G3-2 | Density is a separate component consumed by drag. `PhysicsConfiguration` with deterministic canonical serialization and a SHA-256 identity (`physics_id`). Scenario v3 is **additive** and never mutates historical v1/v2 artifacts. `PhysicsConfigured` event as proposed (§5.5) | APPROVED |
| Q-G3-3 | Validation **fails closed** when the expected physics identity does not match the active physics configuration | APPROVED |
| Q-G3-4 | Earth/model constants are pinned physics configuration; no inline constant overrides in scenarios (with DR-0024) | APPROVED |
| Q-G3-5 | **Owner decision differs from the recommendation (a).** Every historical physics/model version is **retained for as long as a frozen validation artifact or a supported historical scenario depends on it.** No time-based deletion period | APPROVED (owner's rule) |
| Q-G3-6 | A decay run ends at an **explicitly defined event or model-validity boundary**. No universal re-entry altitude is invented to close this request; the numerical definition stays OPEN (DR-0027 item A). No default value in code or scenarios | APPROVED (principle); value OPEN |
| Q-G3-7 | Per-sample environment telemetry: **not addressed by the owner.** No telemetry event is authorized by this resolution; adding one later needs its own decision | Not authorized; no decision |
| Q-G3-8 | Force composition and order are deterministic and documented: point mass, J2, drag, then thrust (§5.2) | APPROVED |
| Q-G3-9 | `escape` keeps the two-body energy check: part of the approved D3 text (§5.6), recorded as a known simplification. Not separately addressed by the owner; flagged in the checkpoint report | APPROVED via D3 (flagged) |
| Q-G3-10 | v3 spacecraft may carry mass and drag properties without an engine (§5.2, §5.4): part of the approved D3 text; consistent with DR-0024 Q9 (initial mass is a scenario input) | APPROVED via D3 |
| Q-G3-11 | ADR-0009 written after this resolution: `docs/decisions/0009-m3-force-context-and-physics-identity.md` (Accepted as a design decision; not implemented) | APPROVED; done |
| — | No general plugin framework in M3 (D4 rejected) | APPROVED |

**Reasoning/notes:**
- Q-G3-5 replaces recommendation (a). Consequence for the design: the code that evaluates a model version (for example `zonal_j2@1`) must stay executable while any frozen artifact or supported scenario records that version. A new version is added beside it, never in place of it. M1/M2's v1/v2 paths are already retained on the same principle.
- Q-G3-7 and Q-G3-9 are flagged so they cannot become implied decisions.

**Follow-up:**
- DR-0027 item A (termination value).
- ADR-0009 status moves to "Accepted — implemented" only after the M3 implementation and Proof.
