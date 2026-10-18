# Decision Request: M3 T0 proposals: termination and atmosphere domain, GMAT method, reference missions, geodetic test points, validation-scenario parameters

**Status:** OPEN. Nothing here is decided. Every item is a proposal for the Tech Lead; no OPEN, DEFERRED or T0 → owner item elsewhere changes status because of this request.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-18  
**Related milestone/issue:**
- M3 T0, authorized by "TARS — M3 T0 Reference-Configuration Spike Authorization" (I-15, 2026-10-18), §5.
- It answers the T0 obligations of:
  - DR-0027 (A-4, A-5, A-6, A-s, B-4);
  - DR-0025 (Q-G2-1, Q-G2-5, Q-G2-7);
  - DR-0024 (Q9 values).
- **Evidence:** VAL-0019 and `docs/science/experiments/m3-t0/` (result files cited as `atmosphere`, `decay`, `geodetic`, `frames`, `regression` and `gmat`, meaning `t0_<name>_results.json`).

Every number below was measured by the T0 spike unless it is marked **[derived]** or **[source]**. Values such as "80 km" in the evidence are **spike test values** used to exercise a mechanism. They are not proposed scenario values; DR-0027 A-3 prohibits a universal altitude.

## Summary of proposals
| # | Item | Recommendation | Needs |
|---|---|---|---|
| P1 | DR-0027 A-4: permitted termination altitudes | Rule-based admissibility, not a numerical range: h_f below the initial height, above a − b, and satisfying a stiffness bound ρ(h_f)·v·dt/B_min ≤ κ, with κ chosen by the owner | Owner: rule and κ |
| P2 | DR-0027 A-5: crossing behaviour | End at the first committed state with h ≤ h_f (as `impact` does); report a cubic-Hermite crossing time; outcome `reentry`; missed dips documented | Owner |
| P3 | DR-0027 A-6: domain edges and `impact` | `impact` unchanged and kept as a backstop; with P1, termination always precedes `impact`; same-tick precedence defined | Owner |
| P4 | DR-0027 A-s: density for RK4 stages below the lower edge | (ii) fail closed | Owner |
| P5 | DR-0027 B-4: unsupported altitudes | h < 0: fail closed (P4). 0–25 km: excluded by P1. 900–1000 km: accepted with documentation. Above 1000 km: top band extrapolated (GMAT-identical), labelled unverified; reference missions kept below 900 km | Owner |
| P6 | DR-0025 Q-G2-1: GMAT method | A decomposed exact configuration with a pinned setting list. Option (b) is feasible for J2 (0.076 mm), but adopting it in a validator needs a DR-0028 scope ruling. The geodetic-drag GMAT path is **escalated for investigation** | Owner, plus a DR-0028 scope ruling |
| P7 | DR-0025 Q-G2-5: reference missions | RM-0 … RM-8 (table in P7), all exercised except RM-3b | Owner |
| P8 | DR-0025 Q-G2-7: geodetic test points | Exact answers and forward-constructed points as the gate source; GeographicLib examples and GMAT as corroboration; the algorithm's domain stated | Owner |
| P9 | DR-0024 Q9: C_d, A, mass, initial states | C_d 2.2 (illustrative). Vehicle V1: 850 kg, 15 m² (B 25.8 kg/m²). Vehicle V2: the M2 vehicle with A 15 m². Initial states per P7 | Owner |
| P10 | New: J2 identity (decimal or C̄20) | Pin C̄20 as the source value, with J2 = −√5 C̄20 derived | Owner (before T1) |

**T1/T2 readiness (recommendation, not authorization):**
- **T1 (J2):** no T0 item blocks it, once P10 is decided.
- **T2 (drag):** BLOCKED until P1–P5, P8 and P9 are decided.
- **T4/T5:** need P6 and P7.

---

## P1 — DR-0027 A-4: permitted ranges of the per-scenario termination altitude h_f
**Problem.** A drag scenario must state h_f in metres, geodetic (A-1, A-2). Which values may it state?

**Evidence**
- **No source-backed physical limit exists** (DR-0027 A). T0 found none either; none is proposed.
- **Numerical stiffness.** The linearised drag decay rate is λ = ρ v / B [derived; B = m/(C_d A)]. Classical RK4 is stable on the real axis only for |λ dt| ≤ 2.785, and its local relative error is about (λ dt)⁵/120. Heights at which dt = 10 s reaches a given |λ dt| (`atmosphere` → `stiffness_dt10`, circular speed, 5 km grid):

  | B | λdt ≥ 2.785 (unstable) | ≥ 1 | ≥ 0.1 | ≥ 0.01 |
  |---|---|---|---|---|
  | 25.8 kg/m² | 50 km | 55 km | 75 km | 90 km |
  | 100 kg/m² | 40 km | 45 km | 65 km | 80 km |

- **Decay from 180 km to the ground** (B 25.8, J2 + drag, RK4 at dt = 10 s against DOP853; `decay` → `rk4_divergence`):
  - the RK4 height error passes 1 m at 148 km;
  - it passes 100 m at 71.8 km (t = 20 680 s);
  - RK4 diverges at about 11–12 km (t = 21 070 s; the speed is no longer bounded);
  - DOP853 reaches geodetic 0 at 21 444 s (5.96 h).

  The circular-speed estimate in the table is conservative during the final plunge, because the speed falls.
- **Impact interaction [derived, exact].** For a point outside the ellipsoid, geodetic height h ≥ |r| − a (the ellipsoid lies inside the sphere of radius a), and h ≤ |r| − b. The v1/v2 `impact` condition |r| − a ≤ 0 therefore implies h ≤ a − b = **21 384.69 m**. If h_f > a − b, the termination height is reached no later than `impact` could fire.
- **The table domain starts at 0 km.** The 0–25 km band carries the disputed 0.13785 % base-altitude cell (DR-0027 B-2).

**Options**
- **A4-a: domain-only rule.** Require 0 < h_f < h_initial. Simple, but it admits h_f where RK4 at the scenario's dt is unstable or inaccurate (for example 25 km: λdt = 119 at B 25.8).
- **A4-b: rule-based admissibility.** Scenario validation rejects a drag scenario unless:
  1. a − b < h_f < h_geod(initial state);
  2. ρ(h_f) · v_c(h_f) · dt / B_min ≤ κ, where B_min uses the smallest mass the scenario can reach (dry mass) and κ is a pinned project constant chosen by the owner.

  Example consequences at dt = 10 s: κ = 0.01 admits h_f ≥ 90 km at B 25.8 and ≥ 80 km at B 100; κ = 0.1 admits ≥ 75 km and ≥ 65 km.
  - *Pros:* no universal altitude. The bound follows each scenario's own B and dt, and it excludes the region where the measured RK4 error grows by orders of magnitude.
  - *Cons:* a new pinned constant κ; validation must evaluate the table at h_f.
- **A4-c: a fixed numerical range** (for example 80–200 km). Contrary to the spirit of A-3 (a universal number), and wrong for other B or dt.

**Numerical implications.** With κ = 0.01, every admissible floor in the decay run is entered with RK4 stages ≥ h_f − 600 m (`decay` → floors 90–150 km: −122 … −599 m), far above the lower edge (P4).

**Risks**
- The stiffness formula uses circular speed, which is conservative in the plunge.
- κ is engineering judgment, labelled as such.
- A burn lowers B; the rule uses dry mass to cover that.

**Recommendation.** A4-b. The owner chooses κ. The implementer's suggestion is κ = 0.01, because it keeps RK4's local relative error from drag stiffness near 1e-12; that figure is a derived estimate, not a measurement. Clause 1 is kept explicitly even though κ = 0.01 already implies it at these B values.

## P2 — DR-0027 A-5: event-crossing behaviour
**Problem.** How is a crossing of h_f detected and located between committed states, and what does the run report?

**Evidence** (`decay` → `floors`, ten spike floors, B 25.8, dt = 10 s; truth = DOP853 events on the same model)

| Method | Crossing-time difference from DOP853 | Notes |
|---|---|---|
| First committed state with h ≤ h_f | −0.29 … +9.26 s | The final state is up to 3.06 km below h_f (50 km floor), 1.72 km at 80 km, 39 m at 150 km |
| + scalar cubic Hermite on h, with dh/dt = n̂·v at both ends | −0.07 … −0.41 s | No extra force evaluation. Same technique as the existing ascending-node detector |
| + vector cubic Hermite of r, then h of the interpolant | equal to the scalar method within 1.9e-4 s | — |

- **The Hermite residual is the RK4 trajectory's own timing error**, not interpolation error. The two Hermite variants agree to 1.9e-4 s while both differ from DOP853 by up to 0.41 s, the RK4 truncation error at dt = 10 s.
- **GMAT, independently:** GMAT's own stop at geodetic 80 km happens at 20 640.941 s, against the spike's 20 640.965 s (`gmat` → `decay`, Δ = −0.023 s).
- **Missed crossings.** A trajectory can dip below h_f between two committed states and come back. On a 250 × 800 km orbit the largest dip below the lower committed height of a 10 s step was **1.56 m**, against the analytic bound a e n² dt²/8 = 4.17 m [derived] (`decay` → `missed_crossing`).

**Options**
- **A5-a:** committed-state detection only (the v1/v2 `impact` semantics); report the committed state.
- **A5-b:** A5-a, plus a refined crossing time by scalar cubic Hermite on h, reported in the event. The run still ends at the committed state.
- **A5-c:** split the last step to land on h_f (root finding inside the step loop).
  - A new numerical component, akin to DR-0025 Q-G2-3 (b), which was not approved.
  - It changes the final state's definition.

**Proposed outcome and fields** (names remain proposals until the v3 contract is designed at T3, DR-0027 A):
- outcome `reentry` (DR-0026 §5.6);
- `termination_altitude_m` (the configured h_f);
- `crossing_t_s` (Hermite);
- the committed final tick and t;
- the geodetic height of the committed final state;
- a method identifier (for example `hermite_h_v1`) so the definition is versioned with the physics identity.

**Risks**
- Missed dips are not detected; the bound is about 4 m for e = 0.04 at dt = 10 s and grows with e and dt².
- A5-b reports a time that does not belong to a committed state, so consumers must not read it as a state.

**Recommendation.** A5-b, with missed dips documented as a known limitation and not detected. In a decaying orbit the next pass crosses lower.

## P3 — DR-0027 A-6: interaction with domain edges and `impact`
**Evidence**
- a − b = 21 384.69 m [derived]. At the 25 km spike floor, the spherical altitude at the crossing was 22.3 km at latitude −15.8° (`decay`), consistent with the inequality in P1.
- **The 250 km band base coincides with the M1 reference orbit's altitude.**
  - GMAT computed 249.9999999999982 km for that state and selected the 200 km band; the spike computed exactly 250 000.0 m and selected the 250 km band (`gmat` → `trajectories`).
  - With geodetic height the orbit changes band 29–39 times in 10 orbits (P7).
  - At an exact base, the selected band is decided by round-off in any implementation.
- **GMAT's band rule** (h ≥ base[k] selects band k) is confirmed at ±1 km around all 27 boundaries to the probe bias of 1.43e-7 (`gmat` → `density_probes`). Probes exactly on a base mix both bands inside GMAT's integrator stages.

**Proposal**
1. `impact` (spherical ≤ 0, SCI-0006) is unchanged and stays active in v3 as a backstop. Under P1 it can never fire first for a committed state.
2. Same-tick precedence, deterministic: `non_finite` → `reentry` → `impact` → `escape`. Under P1 and dt = 10 s, `reentry` and `impact` cannot both hold at one tick; the order is defined anyway.
3. Termination uses height only. It never depends on which band a base height selects.
4. The round-off ambiguity at an exact base is a property of the published model (DR-0024 Q5a), not a defect. Reference-mission design should treat it explicitly (P7).

## P4 — DR-0027 A-s: density for an RK4 stage below the lower edge
**Evidence**
- **RK4's second stage sits below the committed path in LEO** [derived from the stage formula]. It evaluates r + (dt/2) v₂ with v₂ = v + (dt/2) a, which lies about g (dt/2)² − v² (dt/2)²/(2r) ≈ 117 m inside the arc at dt = 10 s.
  - Measured: 115.7–117.7 m below the lower committed height in every 10 km band from 120 to 180 km (`decay` → `stages`).
  - During the plunge (50–110 km) the stages stay above the lower committed height.
- **In the crossing step,** stages went at most 599 m below h_f for spike floors 90–150 km, and 3.05 km below at 50 km.
- **GMAT R2026a fails closed:** a probe 1 m below the ellipsoid stops the run with "Exponential atmosphere: Position vector is inside central body" (`gmat` → `density_probes` → `below_zero_probe`).

**Options**
- **(i)** Evaluate the lowest band's formula for stages below the lower edge; the committed-state check ends the run.
- **(ii)** Fail closed: a run error with a defined cause.

**Analysis**
- Under P1, no stage of a valid run reaches h < 0: the margin is of order h_f − 600 m ≥ 79 km for κ = 0.01. Either option therefore leaves every valid run unchanged.
- Option (i) would silently extend the model below its domain, against DR-0024 Q8, "no indefinite extrapolation below the modelled domain", and against GMAT's behaviour.
- Option (ii) makes a misconfiguration (or a defect that produces such a state) visible.

**Recommendation.** (ii) fail closed. The cause name is designed at T3; a candidate is a new additive `failure_cause` value such as `outside_atmosphere_domain`.

## P5 — DR-0027 B-4: domain behaviour at unsupported altitudes
| Region | Evidence | Proposal |
|---|---|---|
| h < 0 (below the lower edge) | GMAT fails closed (P4) | Fail closed (P4) |
| 0 ≤ h < 25 km (disputed base cell, −0.13785 %; largest jump, +1.36e-3 at 25 km) | `atmosphere` → `boundaries` | Unreachable for admissible h_f (P1). Evaluated as published if ever reached, with no repair (B-3) |
| 25–900 km | 25 rows identical to the author's file (DR-0024 §3.4); GMAT density matches the spike in every band (`gmat` → `density_probes`) | Normal domain |
| 900–1000 km (scale height 181.05 vs 181.045 km) | Density consequence ≤ 1.5e-5 (DR-0027 B-2) | Accept; document |
| ≥ 1000 km (top band, unverifiable row) | GMAT extrapolates the top band; the spike matches it at 1001, 1100, 1500 and 2000 km to the probe bias. Against the author's file: +19.6 % / +145 % / +500 % at 1100/1500/2000 km (DR-0027 B-2) | Extrapolate the top band (continuous, GMAT-identical). Every record says that density above 1000 km is unverified. No M3 reference mission goes above 900 km (P7) |

**Alternatives for ≥ 1000 km**
- **Fail closed** above 1000 km: strict, but it ends real trajectories that briefly cross the top.
- **ρ = 0 above a cutoff:** rejected already (DR-0024 §12) because it introduces a discontinuity.

**Numerical implication [derived].** At 1000 km and B 25.8 the drag acceleration is about 3e-9 m/s². A ±500 % density error there changes a 10-orbit trajectory by metres only if the spacecraft stays above 1000 km for the whole run.

## P6 — DR-0025 Q-G2-1: GMAT exact-configuration method
**Evidence** (`gmat`; 53 700 s from the M1 state unless noted; spike = DOP853 rtol 1e-13, converged to µm; GMAT = PrinceDormand78, accuracy 1e-13, maximum step 60 s)

| Configuration | GMAT vs spike (J-ax-1): final / maximum | GMAT vs spike driven by GMAT's axis (diagnostic) | Attribution |
|---|---|---|---|
| J2 only, `Earth.NutationUpdateInterval` = 60 s (GMAT default) | 0.273 / 1.05 m | 0.083 m, along-track only | The default holds GMAT's Earth-orientation matrix for 60 s |
| **J2 only, `NutationUpdateInterval` = 0** | **0.192 / 1.03 m** | **0.076 mm** | **Fully attributed:** GMAT's Earth-fixed +Z (polar motion: a 0.349″ circle per sidereal day around the celestial pole, measured) |
| Drag, one-band table, spherical height | 2.05 mm | 2.05 mm | Axis-independent floor; not further attributed |
| Drag, full table, spherical height | 1.98 mm | 2.01 mm | Same floor |
| Drag, full table, geodetic, interval 60 s | 0.186 m | 0.040 m; **4.2 mm** with GMAT's 1e-7 rad height rule | Attributed: polar-motion tilt of GMAT's ellipsoid, plus GMAT's height stopping rule (≤ 1.4 mm in height, `geodetic`) |
| Drag, full table, geodetic, interval 0 | 0.327 m | 0.175 m; 0.137 m with the height rule | **NOT attributed.** GMAT's Earth-fixed frame at report epochs is identical under both settings (height from the fitted axis = height from GMAT's Earth-fixed coordinates to 0.6 µm). The difference arises inside GMAT's steps |
| J2 + drag, geodetic (i 51.6°; 97°; 250 × 800 km) | 0.20 / 1.08; 0.58 / 0.70; 0.24 / 0.86 m | 0.18; 0.23; 0.095 m | Not attributed (contains the geodetic path) |
| J2 + drag + M2 burn | 0.24 / 0.94 m; mass 2.9e-9 kg | — | J-ax-1 residual only |
| Perturbations off, exact-configuration form | Every approved M1 GMAT gate passes unchanged (GMAT vs Kepler 4.86e-6 m against the 1e-4 m limit) | — | — |

**Configuration findings (each one changes the reference by more than its own residual)**
1. **`Earth.NutationUpdateInterval`:** the default of 60 s moves the J2 reference by 8 cm (along-track) against 0.076 mm at 0. It must be pinned explicitly.
2. **GMAT's default C_d is 2.2000000000000002** (measured). Any scenario value must be set explicitly.
3. **GMAT's gravity field applies the `.cof` GM, not `Earth.Mu`** (VAL-0018, confirmed by the regression in `gmat` → `regression_m3_form`). The `.cof` must be generated from the pinned constants.
4. **GMAT's geodetic height** uses a 1e-7 rad stopping rule (≤ 1.4 mm error) and fails exactly on the axis. It belongs in the error budget of every geodetic comparison.
5. **GMAT's Earth orientation depends on its EOP file** (sha256 `52c95d68…`, data to 2026-09-14). The file must be recorded, because the axis it implies changes with it.
6. **States are exchanged in TOEEq fixed at the scenario epoch.** The echo of the initial state is 1.9e-9 m.
7. **GMAT's geodetic-drag result also depends on how the run is segmented into `Propagate` commands.** The planning probe was rerun unmodified on 2026-10-18 and reproduced byte for byte. Same physics, three GMAT configurations:

   | GMAT configuration | Geodetic-drag residual vs the spike |
   |---|---|
   | One 53 700 s `Propagate`, default interval (planning probe) | 0.383 m |
   | 895 × 60 s `Propagate`s, default interval (T0) | 0.186 m |
   | 895 × 60 s `Propagate`s, interval 0 (T0) | 0.327 m |

   - **J2 also varies:** 0.189 / 0.273 / 0.192 m. Its variation is fully explained: at interval 0 GMAT matches the spike driven by GMAT's axis to 0.076 mm.
   - **Spherical drag does not vary:** 2.0 mm in all three.
   - **Only the geodetic-drag variation is unexplained.** It is part of the escalated item below.

**Options**
- **(a) TOEEq exchange plus a derived bound on the Earth-orientation residual.**
  - Measured J-ax-1 residuals: 0.19–0.58 m final, up to 1.08 m maximum.
  - The polar-motion part is derived from GMAT's own EOP data.
  - The interval-0 geodetic part is not yet bounded.
- **(b) Drive the validator reference with GMAT's reported Earth-fixed axis.**
  - Feasible and exact for J2: 0.076 mm.
  - Recovering the axis needs two non-coplanar orbits, because one orbit plane leaves the out-of-plane component undetermined.
  - It also needs the diurnal polar-motion term (a quadratic-only fit leaves a 0.99 m residual).
  - **Scope question:** the validator would contain a J2 and an ellipsoid evaluated about a time-dependent, data-derived pole. DR-0028 says "No additional Earth-orientation implementation is authorized". The axis is GMAT output consumed as data, not an Earth-orientation model, but whether that falls inside the prohibition is the owner's ruling, not the implementer's. **Dependent work (choosing (b) for T5) is blocked on that ruling; nothing else is.**
- **(c) GMAT informational only** for configurations that cannot be matched exactly.
- **(d) [new] Decomposed exact configuration.** Each link is checked where GMAT can be exact; the geodetic trajectory comparison stays informational until the escalated item is resolved.
  - GMAT J2 against the validator reference, under (b) or under the (a) bound.
  - GMAT spherical-height drag against the validator reference: 2 mm and axis-independent. This checks density, rotation, ballistic coefficient and mass with no Earth-orientation effect.
  - Geodetic height checked separately, by P8 points and by GMAT's own altitude (≤ 1.3 mm at mid-latitudes).

**ESCALATED_FOR_INVESTIGATION.** The 0.137 m geodetic-drag difference at `NutationUpdateInterval` = 0 and the 0.18–0.23 m combined residuals are not explained.
- Candidate next steps (T5): read the R2026a sources for `CalculateGeodetics` and the atmosphere's rotation-matrix caching; repeat with intermediate intervals; isolate per step.
- Until then, no geodetic trajectory comparison can be called exact.

**Recommendation.** (d), with the pinned setting list above. Option (b) for the J2 link only if the owner rules that it is inside DR-0028; otherwise the (a) bound for J2. The escalated item is resolved before T5 proposes any geodetic GMAT gate.

## P7 — DR-0025 Q-G2-5: reference missions
All are exercised in `gmat` (GMAT vs spike) unless noted. Horizon 53 700 s (the M1/M2 horizon) unless noted.

| Id | Configuration | Purpose (DR-0025 oracles) | T0 evidence |
|---|---|---|---|
| RM-0 | v3 point mass (perturbations off), M1 state | VO-5 regression | M3-form GMAT passes every M1 gate; spike RK4 bitwise equal to the M1 golden |
| RM-1 | J2 only, M1 orbit | Q1, Q2, Q3, Q10, Q8 | 0.192 m (J-ax-1); 0.076 mm (GMAT axis) |
| RM-2 | Drag, one-band 250 km table, spherical height | Q4, Q5, Q6 decay oracle, Q10 (smooth) | 2.05 mm |
| RM-3 | Drag, full table, geodetic, M1 orbit | Q5, Q7, Q8, band crossings | 0.327 m; 39 band changes in 10 orbits |
| RM-3b | Drag, full table, geodetic, circular 275 km (mid-band) | Full table without band crossings over the horizon | **Not run** (candidate only) |
| RM-4 | J2 + drag, geodetic, M1 orbit (**primary**) | VO-3 | 0.199 m final / 1.08 m maximum; 29 band changes |
| RM-5 | J2 + drag, geodetic, circular 250 km, i = 97° | Node advance (i > 90°, Q11 sign) | 0.583 m |
| RM-6 | J2 + drag, geodetic, 250 × 800 km, i = 51.6° | ω̇ (eccentric), 9 bases spanned, 151 band changes | 0.237 m final / 0.858 m maximum |
| RM-7 | J2 + drag + M2 prograde burn (M2 vehicle, A 15 m²) | VO-4 | 0.240 m; mass 2.9e-9 kg |
| RM-8 | J2 + drag, geodetic, circular 180 km → h_f (P1) | VO-9 decay, A-5 crossing | GMAT stop at 80 km (spike test value) within 0.023 s; 5.96 h to the ground |

**Note on the 250 km base.**
- The M1 initial altitude is exactly the 250 km band base, so RM-3, RM-4, RM-5 and RM-7 start on a boundary and cross it repeatedly.
- That makes them good boundary cases (DR-0025 principle 5), but they cannot serve as no-crossing cases; RM-3b is proposed for that role.
- RM-2 is unaffected, because the one-band table has no boundary.

**Recommendation.** RM-0 … RM-8, with the RM-8 floor set by each scenario under P1 and RM-3b to be measured in T4. All apogees are below 900 km (P5).

## P8 — DR-0025 Q-G2-7: source of geodetic-height test points
**Evidence** (`geodetic`; `gmat` → `geodetic_points`)

| Candidate | Independence | Result |
|---|---|---|
| (a) Exact answers: equator h = √(x² + y²) − a; axis h = \|z\| − b | Analytic | Iterative: 0 error; Vermeille: ≤ 5.5e-10 m |
| (a′) 640 points from the closed-form forward transformation (latitudes −90…90°, heights −10 km … 2000 km) | Different formula (forward), shares no code with the inverse | Iterative ≤ 1.9e-9 m; Vermeille ≤ 2.9e-9 m |
| (b) GeographicLib CartConvert(1) manual examples (WGS 84; printed to 0.01 m) | Published, external | Forward within 4.5 mm; inverse within 4.2 mm (inside the 5 mm rounding) |
| (c) GMAT R2026a `Earth.Altitude` / `Latitude` | Independent implementation | ≤ 1.3 mm at mid-latitudes; 15 mm at 89.999999°; **fails exactly on the axis** (h ≈ −N) |
| (d) A geodesy text or standard with printed test points | — | Not available to the project; would need acquisition |

**Domain.**
- Both inverse algorithms are valid outside the evolute region near the centre.
- The published reverse example (30 km, 30 km, 0) lies inside it: the iterative algorithm returns a non-nearest solution (0.86 m from GeographicLib's), and Vermeille divides by zero.
- Every M3 state is far outside this region, but the production function must state its domain and reject points outside it.

**Recommendation.** (a) and (a′) as the gate source (exact to round-off), with (b) and (c) recorded as external corroboration. The production height function's domain is stated, and on-axis points are tested explicitly.

## P9 — DR-0024 Q9: validation-scenario parameters
**Evidence and basis**
- **C_d 2.2** is GMAT R2026a's default (measured, `gmat`; VAL-0007 used it).
  - It is commonly described as the conventional value for compact satellites in free-molecular flow. **[secondary]** Search results attribute the value to Cook and to Izakov via an abstract by K. Moe; that abstract and the primary sources were **not read**, so no primary citation is claimed.
  - In the cannonball model C_d enters only through B = m/(C_d A). The validation oracles test the model's correctness for a given B, not the realism of C_d.
- **B 25.8 kg/m²** (850 kg, 15 m², C_d 2.2; the GMAT defaults):
  - it gives measurable decay (−12.8 km/day at 250 km, VAL-0018);
  - it continues VAL-0007/VAL-0018;
  - drag-only RK4 error at dt = 10 s: 4.6 m (VAL-0018).
- **B 100 kg/m²:** a low-drag variant (0.70 m RK4 error in J2 + drag, VAL-0018).
- **M2 vehicle** (1000 kg dry + 300 kg propellant, DR-0010): with A 15 m² and C_d 2.2, B = 39.4 kg/m² before the RM-7 burn and 39.0 kg/m² after it (final mass 1287.62 kg, measured in GMAT).
- **Sensitivity:** B + 1 % moves the 10-orbit trajectory by 4.8 km (VAL-0018). B is therefore a pinned scenario input with an exact value, never tuned.

**Options**
- **(i)** V1 = 850 kg, 15 m², C_d 2.2 (B 25.8), plus V2 = the M2 vehicle with A 15 m², for RM-7.
- **(ii)** As (i), plus a B 100 variant of RM-4.
- **(iii)** A cited real vehicle class: no source was read in T0.

**Initial states**
- Circular states use the M1 construction (altitude, inclination, RAAN 0, argument of latitude 0, epoch 2026-01-01 TT as metadata).
- RM-6 needs an elliptic state (perigee/apogee construction, `t0_model.perigee_state`) or a Cartesian state. Which v3 orbit kinds exist is a T3 schema decision.

**Recommendation.** (i), with every value labelled "illustrative, validation only" in the scenarios and records, as DR-0010 did for the engine. Option (ii) only if the owner wants a low-drag case gated.

## P10 — New: identity of the pinned J2 value
**Evidence.** DR-0024 Q1 records "J2 = 1.0826261739e-3 (= −√5 × −0.484165143790815e-3)". The two are not the same double: −√5 C̄20 = 1.0826261738522227e-3, a relative difference of −4.4e-11 (`t0_model.J2_FROM_C20`). A generated `.cof` carries C̄20.

**Options**
- **(a)** Pin C̄20 (the NGA source value) and derive J2.
- **(b)** Pin the decimal J2 and write C̄20 = −J2/√5 into the `.cof`.

**Trajectory effect.** Negligible: about 6.7 m × (4.4e-11 / 8.6e-6) ≈ 3e-5 m [derived from the VAL-0018 tide-system sensitivity]. The physics identity (DR-0026) must still contain exactly one of them.

**Recommendation.** (a), because the source publishes C̄20.

## Impact
- **Architecture:** P2–P5 decide one v3 end condition, one failure cause, one domain rule and one pinned constant (κ). P6 decides the GMAT generator's settings. No production change is made here.
- **Science/validation:** VAL-0019; SCI-0015/0016/0017 limitations (unsupported altitudes, termination); DR-0025 oracle design.
- **Dependencies:** none.
- **Reversibility:** high until T2/T3 implement them. After that, a change creates a new physics identity.

## Blocked work
- **T2/T3** (drag, end conditions, contract): P1–P5, P8, P9.
- **T1:** P10.
- **T4/T5:** P6 and P7. Choosing P6 (b) additionally needs the DR-0028 scope ruling. The escalated geodetic-drag investigation blocks only geodetic GMAT gates.

## Work continuing independently
- None of the implementation. T1 and later are not authorized.
- The Codex review of T0 waits for the Tech Lead's §8 instructions.

## Requested response
For each of P1–P10: accept, choose an option, or `discuss`. P1 needs κ. P6 needs a ruling on whether option (b) falls inside DR-0028's prohibition on additional Earth-orientation implementation.

## Resolution
**Decision:** (pending)
