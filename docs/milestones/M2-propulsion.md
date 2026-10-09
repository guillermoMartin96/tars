# Milestone 2 — Propulsion & Orbital Maneuvers: plan and draft Proof

**Status:** PLANNING CHECKPOINT. Awaiting Tech Lead approval of DR-0010…DR-0015. No propulsion code has been written.  
**Branch:** `milestone-2-propulsion-f90f9ba4`, from `main` at `63bec8d`  
**Date:** 2026-10-09  
**Definition of done:** prototype phase (proof/definition-of-done.md), unless the Tech Lead sets a stricter bar.

**Objective:** implement physically modelled spacecraft propulsion so that commanded burns produce predictable, validated orbital changes.

---

## 1. Repository and Milestone 1 readiness

### 1.1 Verified state (2026-10-09)
| Item | Result |
|---|---|
| `main` | `63bec8d`: M1 (PR #1, `6cf072a`) and M1 independent-audit remediation (PR #2) merged |
| Working branch | `milestone-2-propulsion-f90f9ba4` from `63bec8d`; clean before planning work |
| Tests | 212 passed (`uv run --no-sync pytest`) |
| Lint / format | ruff check and format: clean |
| M1 Proof (non-GMAT) | PASS against approved `proof/thresholds/m1.json`; dt = 10 s position error 0.298 m |
| GMAT compare (committed reference) | PASS (9 DR-0009 gates) |
| Determinism | byte-identical across processes; sha256 `7a4e1877…` = golden |
| Cross-platform validator | bit-identical to golden on the reference host |

**Assessment:** M1 is complete, merged, and reproducible on this branch. There are no open Critical or High findings. M2 can start once the decisions below are approved.

### 1.2 Items that affect propulsion
| Item | Source | Effect on M2 | Handling |
|---|---|---|---|
| **No roadmap document exists** | repo | M2 scope cannot be checked against a roadmap | DR-0010 #1; scope fixed in this plan |
| ADR-0003 reconsider trigger: "a force needs state beyond (t, r, v), e.g. mass" | ADR-0003 | thrust needs mass | DR-0013 option 2A: separate propulsion subsystem, ForceModel unchanged |
| ADR-0004 fixed step; DR-0008 "revisit dt when finite burns arrive" | ADR-0004, DR-0008 | thrust on/off is discontinuous | DR-0013 option 3A: split steps at engine events; dt = 10 s keeps 4th order (VAL-0008) |
| **REV-012 deferred: GMAT epoch-column drift; investigate before the first time-dependent force model** | M1 review, GMAT README | GMAT burn residual traced to the same epoch arithmetic (VAL-0009) | DR-0015 option A: investigate before gated GMAT burn comparison |
| Stop condition counts ascending-node passages; timeout guard uses the initial period | DR-0007, F3 | the burn changes the period | DR-0010 #4: add `stop.duration_s`; M1 semantics unchanged |
| M1 thresholds apply to the M1 scenario only | README, `m1.json` basis | M2 needs its own thresholds | DR-0015 method; threshold DR after measurement |
| Golden M1 event-log hash | `proof/references/m1_final_state.json` | M2 must not change M1 bytes | DR-0013 4A; regression gate |
| SCI-0002 "spacecraft is a massless point" | assumptions | mass now matters for thrust | revision drafted with DR-0011 |
| GMAT `GravitationalAccel` default 9.81 m/s² | VAL-0009 | silent 7.85 m mismatch | exact configuration gate (DR-0015) |
| GMAT Math Spec shows a d(mv)/dt equation of motion | VAL-0009 | ambiguity about the reference model | measured: GMAT integrates a = F/m |
| Scenario/event `schema_version` is `Literal[1]` | `scenario.py`, `schema.py` | new blocks and events | DR-0014 §5: scenario v2; additive events |
| Architecture scan covers `sim`/`astro` | `architecture.py` | new `tars.sim.propulsion` is automatically in scope | extend tests for no mass/propellant setters |

---

## 2. Scope (proposed, DR-0010)

### In scope
1. Spacecraft dry mass and propellant mass, owned by the simulator.
2. One engine: constant thrust F and specific impulse Isp; mass flow ṁ = F/(Isp·g0) (DR-0011).
3. Variable spacecraft mass integrated with the trajectory.
4. Finite-duration burns with exact ignition and cutoff times (step splitting, DR-0013).
5. Prograde and retrograde directions with velocity-tracking (VNB) pointing (DR-0012).
6. A structured `BurnCommand`, submitted from a scenario timeline, with validation, rejection reasons, and an explicit insufficient-propellant policy (DR-0014).
7. Propellant depletion: exact flame-out, never negative.
8. Burn and propulsion events and telemetry (DR-0014 §5).
9. Deterministic replay; M1 byte-identical.
10. Validation against analytic oracles, an independent integrator, and GMAT (DR-0015).
11. Scenario `stop.duration_s`.

**First vertical slice:** one manual prograde burn from the M1 circular 250 km orbit. Proposed burn: 490 N / 312 s engine, 1000 + 300 kg spacecraft, ignition at 600 s, duration 77.3 s, Δv ≈ 29.3 m/s, apoapsis 250 → ≈ 351 km.

### Explicit non-goals
- AI crew, agents, tool adapters, crew permissions. The interface is only *designed* for future use (DR-0014 §6).
- 3D or visualization of any kind.
- J2, drag, SRP, third bodies (DR-0002 model retained).
- Attitude dynamics, torques, thrust misalignment, centre-of-mass shift.
- Engine transients, minimum impulse bit, throttling, pressure/temperature models, multiple engines/tanks, ullage, residual propellant.
- Thermal effects (in the conceptual playbook chain; no researched basis).
- Sensor models: telemetry is truth state.
- Δv-target cutoff and abort/cancel commands: candidate follow-ups needing approval (DR-0014).
- Targeting/optimization (e.g. solving for a Hohmann transfer), rendezvous, plane changes.
- Milestone 3 or later work.

---

## 3. Physics model (proposed, DR-0011/DR-0012)

**Equations of motion** (ECI, SI units). With the engine on:

```
r' = v
v' = −μ r/|r|³ + (F / (m_dry + m_prop)) · û(r, v)        û = ±v/|v|  (prograde / retrograde)
m_prop' = −F / (Isp · g0)                                  g0 = 9.80665 m/s² (exact)
```

With the engine off, the thrust and mass terms are zero, and the M1 two-body model applies.

### Key concepts behind the model
- **Isp and g0.** Specific impulse is a ratio between thrust and propellant weight flow. Its "seconds" assume standard gravity. g0 is a units convention, **not** the local gravity at 250 km (≈ 9.07 m/s²). GMAT's default 9.81 is a different convention and must be overridden (VAL-0009).
- **Why a = F/m and not d(mv)/dt = F.** The exhaust carries away momentum. Applying Newton's law to the vehicle alone gives m·dv/dt = F. Writing d(mv)/dt adds a fictitious −ṁv "force" that depends on the observer's frame (Plastino & Muzzio 1992). The GMAT Math Spec writes the latter form, but GMAT's code does the former (VAL-0009).
- **The rocket equation comes out of the model; it is not an input.** Integrating F/m with m linear in time gives Δv = Isp·g0·ln(m0/mf), for any pointing history and any gravity. That makes "sensed Δv" an exact oracle.
- **Finite vs impulsive.** Textbook maneuvers assume an instantaneous Δv. A finite burn spreads it along an arc. For a burn centred on the impulsive point, the difference in SMA scales with burn duration² (VAL-0008 measures ratio → 4.000 when the duration halves). The 77 s slice differs from impulsive by only 0.13 m of SMA (2.6e-6 of the change).
- **Pointing changes the physics.** Holding the ignition direction fixed instead of tracking velocity changes SMA by 69 m for the slice (VAL-0008), so "prograde" must be defined precisely (DR-0012).

**Free-space closed form (oracle O3).** With no gravity, fixed û, and m(t) = m0 − ṁt, c = Isp·g0:
- v(t) = v0 + c·ln(m0/m)·û
- x(t) = x0 + v0·t + c·[t − (m/ṁ)·ln(m0/m)]·û

The second line follows from ∫₀ᵗ ln(m0/(m0 − ṁs)) ds = t − (m(t)/ṁ)·ln(m0/m(t)).

Assumptions: SCI-0008…0012 (status Proposed) in `docs/science/assumptions.md`.

---

## 4. Architecture and interfaces (proposed, DR-0013/DR-0014)

```
scenario timeline ──BurnCommand──► Simulator.submit() ──► validation ──► CommandAccepted | CommandRejected(reason)
                                         │ (no state change on reject)
                                         ▼
                              Engine state machine (simulator-owned)
                              IDLE → SCHEDULED → BURNING → IDLE        (exact event times known in advance)
                                         │
                       thrust accel û·F/m, ṁ    + Σ ForceModel accel (gravity, unchanged)
                                         ▼
               RK4 on y = [r, v, m_prop, Δv_sensed], tick split at ignition/cutoff/depletion
                                         ▼
                 new state ──► read-only StateSnapshot + PropulsionSnapshot ──► events / telemetry
```

| Component | Responsibility | Notes |
|---|---|---|
| `tars.sim.constants` | `STANDARD_GRAVITY` | single source; grep test extended |
| `tars.sim.propulsion` (new) | `EngineSpec` (F, Isp), `TankSpec`, mass flow, pointing (`prograde`/`retrograde` → û from r, v), engine state machine, event-time computation | pure, deterministic; inside the architecture scan |
| `tars.sim.simulator` | owns y, engine, propellant; `submit()`; sub-step scheduling inside a tick; snapshots | 6-state M1 path unchanged when no propulsion (DR-0013 4A) |
| `tars.sim.commands` (new) | `BurnCommand`, `CommandReceipt`, reason codes | strict Pydantic; `issuer` recorded, no authority |
| `tars.sim.scenario` | `schema_version: 2` with `spacecraft`, `commands`, `stop.duration_s` | v1 files unchanged |
| `tars.sim.runner` | submits timeline commands, emits new events, duration stop | M1 path byte-identical |
| `tars.events.schema` | new additive event types (DR-0014 §5) | existing types untouched |
| `tars.validation` / `toolbox/validators/m2_proof.py` | oracles O1–O9, thresholds `proof/thresholds/m2.json` | `KNOWN_VALIDATORS` extended |
| GMAT workflow | M2 script generator from scenario, committed reference, provenance, replacement guard | after REV-012 (DR-0015) |

**Ownership rules (hard invariants, tested):**
- No public setter for r, v, mass or propellant.
- `submit()` can only schedule engine activity.
- Rejected commands leave state bit-identical.
- Force models and pointing receive read-only arrays (REV-004 pattern).

---

## 5. Numerical accuracy requirements
- Integrator: classical RK4, dt = 10 s, unchanged (ADR-0004, DR-0008).
- **Every engine event strictly inside a tick splits that tick** into RK4 sub-steps at the exact event time. Events exactly on a tick boundary need no split. Several events in one tick are handled in order.
- Simulation time stays `tick·dt`. Event times are stored as exact floats (`tick·dt + offset`).
- Expected accuracy (VAL-0008): burn contributes ≈ 1 mm / 1 µm/s; end-of-run error ≈ M1 coast error; mass exact to round-off; observed order ≈ 4.
- Node-crossing detection inside a tick with a thrust discontinuity uses the existing cubic Hermite. Its accuracy is reduced only for crossings inside a burn tick. M2 gates do not use node timing during burns, and this is documented.

---

## 6. Telemetry and event contracts
Defined in DR-0014 §5: `SpacecraftConfigured`, `CommandAccepted`, `CommandRejected`, `BurnStarted`, `BurnEnded`, `PropulsionSampled`, `PropellantDepleted`.
- All are strict Pydantic models with finite numbers only (F2 lesson).
- All are serialized as JSONL and round-trip tested.
- Existing M1 event types and bytes are unchanged.
- Mission success/failure stays in `SimulationCompleted`. A burn ending by depletion is reported in `BurnEnded`, not as a simulation failure.

## 7. Deterministic replay
- Same platform, pinned `uv.lock`: two runs of each M2 scenario give byte-identical `events.jsonl` (sha256), in-process and cross-process (DR-0006).
- Commands are part of the scenario, so they are covered by `scenario_hash`. There is no hidden input.
- Cross-platform: a committed M2 golden final state (r, v, mass), with bounds measured in CI on ubuntu x86_64 and macOS arm64 before approval.
- The M1 scenario remains bit-identical to its golden on the reference host.
- No stochastic behavior in M2. The seed is recorded as in M1.

---

## 8. Test plan
| Layer | Tests (planned) |
|---|---|
| **Unit** | mass flow and g0; pointing unit vectors (prograde ⟂ N̂, retrograde = −prograde, `\|û\| = 1`); engine state machine transitions; event-time computation (cutoff, depletion, cutoff = depletion); command schema (finite, extra fields, enums); every rejection reason; free-space closed form (O3); rocket equation (O2); sub-step scheduler (event on boundary, inside, two in one tick, ignition and depletion in same tick) |
| **Integration** | simulator + propulsion: propellant never negative; rejected command leaves state bit-identical; no setters (architecture scan + reflection test); snapshot immutability; force/pointing cannot mutate state; M1 path byte-identical (golden hash); runner emits the full event sequence |
| **Physics validation** | O1–O9 (DR-0015): mass law, rocket equation, DOP853 reference at cutoff and end, post-burn Kepler, impulsive-limit order, direction signs and in-plane invariants, RK4 convergence through the burn, GMAT gates |
| **Mission** | (1) `m2_prograde_burn` slice; (2) retrograde burn; (3) `burn_to_depletion` partial burn; (4) invalid-command set: each rejection, mission continues safely; (5) M1 scenario unchanged |
| **Replay** | same-platform byte identity for M2 scenarios; cross-platform golden; M1 golden |

---

## 9. Implementation sequence (after approvals)
| # | Task | Depends on | Output |
|---|---|---|---|
| T0 | **REV-012 investigation:** GMAT epoch arithmetic vs ElapsedSecs; how burn boundaries quantize | none (can start now) | VAL record; comparison-alignment rule |
| **T1** | **Propulsion pure model:** `STANDARD_GRAVITY`, `EngineSpec`/`TankSpec`, mass flow, pointing, event-time computation; O1–O3 unit tests incl. the free-space closed form | DR-0011, DR-0012 | `tars.sim.propulsion`, unit tests |
| T2 | Simulator: augmented state, engine state machine, sub-step scheduling, `PropulsionSnapshot`, M1 byte-identity gate | DR-0013 | integration tests |
| T3 | Commands and events: `BurnCommand`, receipts, rejection matrix, new event types | DR-0014 | schema tests |
| T4 | Scenario v2 + runner timeline + `stop.duration_s`; slice scenario file; CLI | DR-0010, DR-0014 | mission test (slice) |
| T5 | Validators O1–O8, `m2_proof.py`, provisional `m2.json`; retrograde, depletion and invalid-command missions | T1–T4 | measured metrics |
| T6 | GMAT M2 reference: generator, run, commit with provenance; O9 gates | DR-0015, T0, T4 | committed reference, VAL record |
| T7 | Three-platform measurement (local + CI) → **threshold DR** → approval | T5, T6 | approved `m2.json` |
| T8 | Full Proof run, Proof record, README update, external review, dispositions | T7 | `proof/records/M2-propulsion.md` |

Commits and pushes happen at each coherent step. No merge to `main` without Tech Lead approval.

---

## 10. Draft Proof requirements (M2)
Applies on top of the standard gate (proof/PROOF.md) and architecture/physics/mission/review Proof. Numeric limits come from the approved threshold DR; candidates are in DR-0015.

| # | Requirement | Evidence |
|---|---|---|
| P1 | A commanded prograde burn is accepted, ignites at the commanded time and ends at ignition + duration | `CommandAccepted`, `BurnStarted`, `BurnEnded(cause=completed)` with exact times |
| P2 | Propellant decreases per ṁ = F/(Isp·g0); used = ṁ·T (O1); sensed Δv matches the rocket equation (O2) | validator metrics within approved limits |
| P3 | Orbit changes in the expected direction: prograde raises SMA/energy/apoapsis; retrograde lowers them; plane unchanged (O7) | element deltas from events |
| P4 | Numerical results agree with analytic expectations and the independent reference within approved limits (O3–O6, O8) | `m2_proof.py` report |
| P5 | GMAT finite-burn reference agrees within approved limits; configuration exact (O9); REV-012 investigated | `gmat … compare`, VAL records |
| P6 | Identical scenario and commands give byte-identical events on the same platform; cross-platform within approved bounds | determinism and cross-platform validators |
| P7 | Invalid commands are rejected with the correct reason and **no state change**; insufficient propellant is rejected (default) or flames out exactly at depletion (`burn_to_depletion`), propellant never negative | mission + integration tests |
| P8 | Architecture: no setters for r/v/mass/propellant; commands only via `submit()`; physics core scan clean; no LLM/3D deps | architecture validator + tests |
| P9 | All important transitions emit schema-valid events; JSONL round-trips | event tests |
| P10 | **M1 unchanged:** golden event-log hash on the reference host; all approved M1 gates pass unchanged; M1 thresholds untouched | `m1_proof.py`, GMAT M1 compare, cross-platform |
| P11 | Assumptions SCI-0008…0012 Active; ADR for propulsion architecture; DRs resolved | docs |
| P12 | External review completed; every finding dispositioned; no open Critical/High | `docs/reviews/M2-*.md` |

The Proof record is written only after the work it describes is committed (playbook/delegation.md, REV-013 lesson).

---

## 11. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Step-splitting bugs at tick boundaries (off-by-one, double events) | medium | silent Δv error | dedicated scheduler unit tests; O1 exactness detects cutoff-timing errors to ~1e-12 relative |
| M1 bytes change accidentally | low | breaks the golden hash and M1 Proof | separate code path; golden hash test in CI on the reference host and cross-platform validator |
| REV-012 cause not identifiable from outside GMAT | medium | GMAT gate rests on a hypothesis | bound the effect analytically (ulp-based), escalate per DR-0015 |
| GMAT configuration traps beyond `GravitationalAccel` (e.g. tank pressure terms, duty cycle) | low | false discrepancy | exact regenerated-script check; only C1/K1 non-zero; probe already matched to 0.12 mm SMA |
| Cross-platform amplification during burns | low–medium | M1 bounds don't transfer | measure first; no bound assumed |
| Scope creep into crew/permissions | medium | violates invariant 2 | DR-0014 §6 is design intent only |
| Illustrative spacecraft taken as a real vehicle | low | misleading conclusions | labelled illustrative everywhere; engine class cited |

---

## 12. Decision Requests (all OPEN)
| DR | Topic | Recommendation |
|---|---|---|
| [DR-0010](../decisions/requests/DR-0010-m2-scope-and-reference-scenario.md) | Scope, roadmap gap, reference spacecraft/scenario | A: R-4D-11-class 490 N/312 s, 1000+300 kg, 77.3 s prograde from the M1 orbit |
| [DR-0011](../decisions/requests/DR-0011-propulsion-physical-model.md) | Physical model | A: ideal constant F/Isp, g0 = 9.80665, a = F/m, integrated propellant |
| [DR-0012](../decisions/requests/DR-0012-burn-direction-and-frames.md) | Burn direction | A: velocity-tracking VNB prograde/retrograde |
| [DR-0013](../decisions/requests/DR-0013-propulsion-architecture-and-integration.md) | Architecture and integration | 1A+2A+3A+4A+5: augmented state, separate subsystem, split steps, M1 path untouched |
| [DR-0014](../decisions/requests/DR-0014-maneuver-commands-and-failure-behavior.md) | Commands, failure behavior, events | 1A duration, 2A any time, 3C policy default reject |
| [DR-0015](../decisions/requests/DR-0015-m2-validation-strategy-and-tolerances.md) | Validation, GMAT, REV-012, tolerances | A: GMAT gated after REV-012; oracles O1–O9; threshold DR after measurement |

## 13. Proposed first implementation task
**T1: propulsion pure model.** Needs DR-0011 and DR-0012; independent of DR-0013/0014.
- `STANDARD_GRAVITY` in `tars/sim/constants.py`.
- `tars/sim/propulsion.py` with:
  - `EngineSpec(thrust_n, isp_s)`, with mass flow computed from g0;
  - `TankSpec(dry_mass_kg, propellant_kg)`;
  - `pointing(direction, r, v) -> û`;
  - `burn_schedule(ignition_t, duration, propellant, mdot) -> (cutoff_t, cause)`.
- Unit tests: analytic O1 (mass law) and O2 (rocket equation), the O3 free-space closed form integrated with the project RK4, pointing properties, and the architecture scan.
- No simulator, scenario, or event changes, so M1 is untouched by construction.

REV-012 (T0) can run in parallel now; it needs no decision. It will not start without your go-ahead.
