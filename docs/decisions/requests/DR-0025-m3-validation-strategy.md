# Decision Request: M3 validation strategy for J2 and drag (gate G2)

**Status:** RESOLVED — principles APPROVED (Tech Lead, 2026-10-15); several items explicitly DEFERRED to T0 or later evidence, see "Resolution". No numerical threshold is approved. Where the request body differs from the Resolution, the Resolution governs.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A (G0 approved 2026-10-15).
- Planning baseline: `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f`.
- Depends on DR-0024 (G1, the physics) and DR-0026 (G3, the seams and versioning).
- Evidence: VAL-0018 (PLANNING) and `docs/science/experiments/m3-planning/`.

Source keys ([VAL], [CUR], [KH], [NGA], [IERS-1], [IERS-6], [GMAT-MS], [GMAT-UG]) are defined in DR-0024 §3.1.

This request designs the validation **before** implementation. **No numerical threshold is proposed for approval here.** Where research supports a value, it is shown as a *candidate* with its basis. Every gate value comes later, from measurement on the implementation and a threshold DR: the DR-0008/DR-0015/DR-0023 method.

## 1. Validation objectives
Each capability is validated separately before it is combined.
| ID | Capability | What must be shown |
|---|---|---|
| VO-1 | **J2 only** | Correct form, sign, axis and constants; conservative dynamics; correct secular behaviour |
| VO-2 | **Drag only** | Correct direction (anti-parallel to v_rel); magnitude ∝ ρ·(C_d A/m)·v_rel²; density per the pinned dataset; atmosphere rotation; current-mass coupling; height definition; dissipation |
| VO-3 | **J2 + drag** | Superposition with no hidden coupling; the combined trajectory agrees with an external exact-configuration reference |
| VO-4 | **With M2 burns** | Engine-event step splitting, mass bookkeeping and burn oracles still hold with perturbations active. Drag uses the decreasing mass |
| VO-5 | **Perturbations disabled (regression)** | M1/M2 behaviour and evidence unchanged: byte-identical v1/v2 outputs and goldens; M2 Proof 228/228; snapshot and GMAT M2 gates pass unchanged |
| VO-6 | **Integration adequacy** | Convergence order where the RHS is smooth; measured truncation error at the chosen dt; behaviour at density band edges |
| VO-7 | **Reproducibility** | Same-platform byte-identical replay; measured three-platform drift; M3 bounds never borrowed |
| VO-8 | **Gate sensitivity** | Deliberately wrong physics and corrupted references are detected (mutation and corruption tests) |
| VO-9 | **Long duration** | Behaviour over days, up to decay to the configured end condition (DR-0026), against the semi-analytic decay oracle and GMAT |

## 2. Proposed references, and how independent each one is
Classification:
- **I** — independent evidence: different theory or a different implementation of the physics.
- **P** — partially independent: separately coded by this project, or independent in one respect only.
- **C** — same-model consistency check.
- **R** — regression check.

Two codings of the same equations by the same team are **P, not I**. They catch transcription, plumbing and integration errors, but not a misunderstanding of the physics.

| # | Reference | Covers | Class | Why that class |
|---|---|---|---|---|
| Q1 | **First-order secular J2 theory** [VAL §9.6; CUR §10.7]: Ω̇ = −(3/2) n J2 (R/p)² cos i; ω̇ = (3/4) n J2 (R/p)² (5cos²i − 1) | VO-1 | **I** (theory) | Derived from perturbation theory, not from our acceleration. It is approximate: first order in J2, mean elements. |
| Q2 | **Exact J2 invariants:** E = v²/2 − μ/r + (μ J2 R²/2r³)(3z²/r² − 1) and h_z = (r × v)·ẑ | VO-1 | **P** | Exact consequences of a conservative axisymmetric potential. Independent only if the potential is coded separately from the acceleration. It detects a non-conservative or non-axisymmetric acceleration, but not a wrong J2 value. |
| Q3 | **Gradient check:** the acceleration equals the complex-step derivative of the separately coded potential at sampled points | VO-1 | **P** (unit) | The potential is a simpler formula, so this catches algebra and sign errors in the acceleration components. The complex step avoids finite-difference noise. |
| Q4 | **Drag unit identities:** a_d ∥ −v_rel (cross product zero to round-off); scaling in ρ, C_d A/m and \|v_rel\|²; ρ equals the table at band bases; ω_E = 0 gives v_rel = v | VO-2 | **C** (unit) | Restates the specified equation. It catches sign, unit and wiring errors. |
| Q5 | **Dissipation (power theorem):** ΔE (two-body + J2 energy) equals ∫ a_d·v dt, by quadrature of dense outputs; E strictly decreases while \|ω_E × r\| < \|v\| | VO-2, VO-3 | **P** | Couples the force to the integrator independently of how the density is computed. It does not validate the density itself. |
| Q6 | **Semi-analytic decay oracle:** integrate the orbit-averaged dā/dt = −ρ(ā) √(μā) F / B (F the atmosphere-rotation factor [KH]) as a scalar ODE; compare the mean SMA history | VO-2, VO-9 | **I** (theory), approximate | Averaging theory for near-circular orbits. **It is approximate in every configuration** (review M3P-F3): orbit averaging, near-circularity, and the rotation factor F, which neglects part of the relative-speed variation along an inclined orbit, all have errors that must be carried in its error budget. It runs on a one-band, spherical-height configuration to remove the avoidable model differences. The measured first-order estimate *at fixed density* is off by 2.6–11% because density rises as the orbit decays. Integrating removes that part, but not the others: with the full table, the scalar equation gives −7 974.5 m against −7 980.1 m for the Cartesian model over 10 orbits (reviewer diagnostic). |
| Q7 | **Validator-side reference model + SciPy DOP853** (rtol 1e-13), as M2 O4 | VO-1–VO-4, VO-6 | **P** | Separately coded equations, but the same equations and team, with an independent integrator. It catches integration, step-splitting and composition errors. |
| Q8 | **GMAT R2026a exact configuration:** generated `.cof` with the pinned GM, R and C̄20; `Exponential` with the pinned table; explicit `Earth.Flattening`; states exchanged in **TOEEq axes fixed at the scenario epoch**; PrinceDormand78 | VO-1–VO-4, VO-9 | **I** | A different implementation, team and integrator. Measured residuals over 10 orbits are 0.19 m (J2), 2 mm (drag, spherical height) and 0.38 m (drag, geodetic height). The J2 and geodetic residuals are attributed to Earth orientation (polar motion, pole motion during the run) that the fixed-pole model omits. **They must be bounded before use as a gate (§10).** |
| Q9 | **Configuration identity checks:** the GMAT script, `.cof` and atmosphere file are regenerated from the pinned configuration and compared byte for byte; constants are checked exactly (the SCI-0005 precedent) | VO-1–VO-3 | **C** (exact) | Trajectory gates cannot resolve every constant error. For example, JGM-3 vs EGM2008 J2 is 0.35 m, comparable to the Q8 J2 residual. Constants are therefore verified by identity, not by trajectory agreement. |
| Q10 | **Convergence order:** RK4 at dt, dt/2, dt/4 | VO-6 | **C** | Self-consistency. Applies only to configurations with a smooth RHS (§5). |
| Q11 | **Sign and limiting cases:** node regression negative for i < 90° and positive for i > 90°; apsidal sign change at 63.4°; no node motion at i = 90°; J2 = 0 or no drag model gives results bitwise identical to point mass | VO-1, VO-5 | **I** (theory) for signs; **R** for the identities | Qualitative theory and exact identities |
| Q12 | **Existing M1/M2 gates, unchanged** | VO-5 | **R** | M1 golden `7a4e1877…`; M2 Proof; snapshot; GMAT M1/M2 compare; three-platform M2 gate |
| Q13 | **Geodetic-height unit vectors** (only if DR-0024 Q6 = H-geod): conversions of published test points, and an independent algorithm (iterative vs closed form) agreeing to round-off | VO-2 | **P** / **I** for published points | A new numerical algorithm needs its own oracle. The source of published test points is to be chosen (Q-G2-7). |

## 3. Validation matrix
| Configuration | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J2 only (unit + mission) | ● | ● | ● | | | | ● | ● | ● | ● | ● | | |
| Drag only, one-band table, spherical height | | | | ● | ● | ● | ● | ● | ● | ● | ● | | |
| Drag only, full table, chosen height | | | | ● | ● | | ● | ● | ● | ○ (report) | | | ● |
| J2 + drag (reference missions) | | | | | ● | | ● | ● | ● | ○ | | | |
| J2 + drag + M2 burn | | | | | | | ● | ● | ● | ○ | | | |
| Perturbations disabled (v1/v2 and a v3 point-mass case) | | | | | | | | | | | ● | ● | |
| Long duration (days; decay) | | | | | ● | ● | ● | ● | ● | | | | |

● = gate candidate; ○ = measured and reported, not gated.

## 4. Expected physical behaviours (what correct output looks like)
- **J2.**
  - Node regression at −5.44 °/day for the reference orbit (measured; VAL-0007 GMAT −5.439 °/day).
  - Apsidal motion is ill-defined for near-circular orbits; check it on an eccentric case.
  - Short-period oscillation of osculating SMA of order J2 R²/a ≈ 7 km amplitude (to be measured).
  - The mean SMA has no secular change.
  - E and h_z are conserved.
- **Drag.**
  - The mean SMA decreases monotonically: −12.8 km/day at B = 25.8 kg/m² and −3.05 km/day at B = 100 kg/m² with the static table at 250 km (measured).
  - Energy decreases; inclination decreases slightly, because co-rotation gives a small cross-track component.
  - Eccentricity of a near-circular orbit stays small.
  - Drag decelerates the spacecraft instantaneously, but the lower orbit has a higher mean motion. The accumulated effect is a phase **advance**: after 10 orbits at B 25.8 the spacecraft is 363 km from the point-mass position, ahead along-track (+362 km projected on the point-mass velocity; corrected after review M3P-F2).
- **J2 + drag:** the effects superpose with no hidden coupling; the combined displacement was 1 161 km (measured).
- **With a burn:** the M2 burn oracles hold with perturbations folded into the coast. Drag uses the decreasing total mass.

## 5. Convergence strategy
- **Smooth configurations** (J2 only; one-band drag; J2 + one-band drag) get an order check, under a policy to be set by measurement.
  - **The approved DR-0008 policy |p − 4| ≤ 0.5 is not borrowed.**
  - Its basis (pre-asymptotic orders 4.14–4.33 on point mass) is specific to M1/M2.
  - The J2 ratios measured here are 22.4, 20.0 and 18.3, i.e. orders 4.5, 4.3 and 4.2.
- **The literal multi-band table is discontinuous at band edges** (finite density jumps from table rounding, up to 1.4e-3 relative, plus scale-height changes; review M3P-F1). Measured drag-only error ratios of 10.4, 9.0 and 13.6 (apparent orders 3.4, 3.2, 3.8) **would fail the M1/M2 order policy**. They are not an asymptotic order, and the value and slope contributions are not separated. Options (Q-G2-3):
  - (a) gate order on smooth configurations only; for multi-band configurations, gate the DOP853 and GMAT agreement and report the order;
  - (b) split integration steps at band-edge crossings, which needs root-finding: a new numerical component and a G3 change;
  - (c) use a smooth (C1) interpolation of log ρ, which is no longer the GMAT/Vallado model;
  - (d) enforce value continuity only (DR-0024 Q5a), which removes the jumps but not the slope changes.
  - Recommended: **(a)**.
- **dt sensitivity.**
  - RK4 at dt = 10 s vs DOP853: J2 0.30 m; drag only (B 25.8) 4.6 m; J2 + drag 2.1 m (B 25.8) and 0.70 m (B 100).
  - Drag configurations at dt = 10 s are an order of magnitude less accurate than M1's 0.3 m.
  - **Whether M3 scenarios keep dt = 10 s is an owner decision (Q-G2-4).** dt is per scenario; M1/M2 are unaffected.

## 6. Reproducibility strategy
- **Same platform:** byte-identical `events.jsonl` across processes (DR-0006 definition, unchanged), for every M3 scenario.
- **Every M3 output records the physics configuration identity** (DR-0026): the constants-set digest, dataset digests and force-model versions. A reference is valid only for the identity it was produced with, and comparing against a different identity is refused. This is the DR-0006 scenario-hash precedent, extended to physics.
- **New M3 goldens and an M3 reference snapshot** (if adopted) follow DR-0021 conditions 2–5 in substance:
  - independent baseline approval;
  - immutable by digest;
  - no circular validation.
- **Long-duration and decay runs:** the end time (decay or re-entry, DR-0026) is a gated quantity of its own. It is extremely sensitive to everything (§3.3 of DR-0024), so its tolerance must come from measurement.

## 7. Cross-platform strategy
- **Measure** final-state spreads across the DR-0008 matrix (macOS x86_64 reference host, Linux x86_64, macOS arm64) for every M3 reference mission, then propose bounds in a threshold DR.
  - **M2's 1e-4 m / 1e-7 m/s is not borrowed:**
    - drag amplifies differences strongly: a 0.7 m altitude datum shift becomes 9 m, and a +1% ballistic coefficient becomes 4.8 km;
    - `exp()` is evaluated by the platform maths library and may differ by an ulp across platforms (to be measured, not assumed).
- If drag amplification makes final-state spreads large, gate **a bounded-horizon** quantity, with the long-duration quantities reported. That is a measurement-driven owner decision.

## 8. Negative and corruption testing (gate sensitivity)
The M2 practice continues: adversarial tests and reviewer mutation rounds under the DR-0019 B / DR-0020 A / DR-0022 B threat model.
- **Physics mutations.** Each must fail at least one gate, and the evidence is a committed detection matrix:
  - J2 sign flipped; z-component coefficient 3 → 1; J2 from a different constant set; the J2 axis tilted by 0.15°;
  - drag sign; v instead of v_rel; ω_E sign flipped or zero;
  - spherical/geodetic height swapped; a km/m error in scale height; the density table shifted by one row;
  - dry mass used instead of total mass; C_d·A/m inverted;
  - altitude datum offset.
- **Measured detectability.**
  - Several mutations change the 10-orbit final state by metres to km: ω_E = 0 gives 40 km, the height swap 74 km, B +1% 4.8 km. These are easily detected.
  - **Some do not.** JGM-3 vs EGM2008 J2 is 0.35 m. Those must be caught by Q9 identity checks, and the matrix must show which gate catches each.
- **Reference corruption:**
  - GMAT reports, `.cof` and atmosphere files, manifest, snapshot, thresholds, goldens and dataset digests;
  - the coordinated-corruption lesson of DR-0021 applies, with reference values pinned by digest.
- **Datasets:** a tampered atmosphere table must be rejected by its pinned digest before any physics runs.

## 9. Proposed evidence artifacts (M3; new, never replacing M1/M2)
- `proof/thresholds/m3.json`: provisional, then approved by a threshold DR, with its digest pinned the same way as m1/m2.
- `proof/references/m3_final_states.json`: an M3 golden per reference mission and physics identity.
- `toolbox/references/gmat/m3/`: generated scripts, `.cof`, atmosphere file copy, reports, metadata and a digest manifest.
- `toolbox/references/snapshot/m3/`: only if DR-0021 is extended to M3 (Q-G2-6).
- `toolbox/validators/m3_proof.py` and `toolbox/scripts/run_m3_proof.sh`.
- `proof/records/M3-*.md`, `proof/records/evidence/M3/`.
- A VAL record per measurement; the mutation detection matrix.

## 10. Candidate threshold methodology
Each threshold needs one of: an analytical derivation, documented measurement, an authoritative external reference, or explicit owner-approved engineering judgment. Candidates by class:
| Class | Method | Status now |
|---|---|---|
| Round-off identities (Q3, Q4, the bitwise identities in Q11) | Analytic: relative 1e-12-class or exact, as M2's ROUND class | Method proposed; values set at implementation |
| Exact configuration identity (Q9) | Exact equality | Method proposed |
| Invariant drift (Q2) | Measured RK4 drift at dt, about 2× measured (DR-0008 convention), approved in a threshold DR | **No value** |
| Secular J2 rate (Q1) | **Derived**: the first-order theory's own error (O(J2) mean-vs-osculating difference plus O(J2²)) bounds the comparison, cross-checked by measurement. A tighter check uses mean elements from a first-order short-period correction (Brouwer/Kozai) or a long-arc fit | **No value.** The measured +0.53% with osculating a₀ shows a naïve tolerance would be either loose or wrong |
| Decay oracle (Q6) | Derived from averaging-theory error for near-circular orbits plus measurement on the smooth configuration | **No value** |
| DOP853 agreement (Q7) | Measured RK4 truncation error, about 2×; the DOP853 floor measured as in DR-0023 FU-1 | **No value** (measured RK4 error 0.30 m J2, 4.6 m drag at dt = 10 s; illustrative B) |
| GMAT exact configuration (Q8) | **Bound the Earth-orientation residual before gating** (Q-G2-1). Either derive it (omitted pole motion and polar motion during the run) or remove it (have GMAT report its Earth-fixed z axis in TOEEq axes, for example through a GroundStation at the pole, and drive the validator-side reference with that axis so the comparison becomes exact). Then gate on measured agreement plus the RK4 error, by the DR-0023 FU-1 method | **No value.** Measured 0.19 m / 2 mm / 0.38 m are planning numbers only |
| Cross-platform (VO-7) | Measured three-platform spread, threshold DR | **No value; M2 bounds not borrowed** |

## 11. Independence analysis (summary)
- **I** for every capability:
  - J2: secular theory (Q1) and GMAT (Q8).
  - Drag: the decay theory on the smooth configuration (Q6) and GMAT (Q8).
  - Combined and burn: GMAT (Q8) only.
- **The combined and burn configurations rest on a single independent reference (GMAT).** Their other references are partially independent (Q5, Q7). That is a stated gap (§12).
- **No density model is independently validated against the real atmosphere.** The table *is* the model, and GMAT agreement shows only that two codes evaluate the same table the same way. That is appropriate for a static model, and it must be stated as such in every record.

## 12. Known validation gaps
1. **The real-atmosphere density is not validated.** The pinned static table is the definition. Realism is informational only, for example comparison with GMAT NRLMSISE-00 or JR runs, as in VAL-0007.
2. **The GMAT J2 and geodetic residuals** (0.19 m, 0.38 m) are not yet bounded or explained term by term (Q-G2-1).
3. **Only one fully independent reference** exists for J2 + drag + burn.
4. **Geodetic-height test points:** an authoritative published set is not yet identified (Q-G2-7).
5. **The first-order theories are approximate.** Their own error must be derived before they gate.
6. **Order checks do not apply to the multi-band table** (§5).
7. **Long-duration decay times** are hypersensitive. Their tolerance may be wide by necessity, which must be stated rather than hidden.

## 13. Effect on the interpretation of existing M1/M2 results (explicit)
- **No M1/M2 result changes meaning.**
  - Every M1/M2 claim is agreement with a *point-mass* (plus thrust) model, against references configured with the same exclusions. SCI-0001 and SCI-0004 state the omission and VAL-0007 quantifies it.
  - Adding J2 and drag in new, separately identified configurations does not touch those claims (DR-0026 versioning).
- **What does not transfer to M3** and must be measured afresh:
  - **DR-0008 dt = 10 s adequacy.** Measured 0.30 m for J2 (similar to M1) but 4.6 m for drag only. The M1 evidence says nothing about drag.
  - **O8 order policy |p − 4| ≤ 0.5.** Approved at a 1.5× margin with point-mass orders 4.14–4.33. Multi-band drag orders of 3.2–3.8 would fail it, so it must not be applied to them.
  - **O6 impulsive-limit order** (bound 0.0405 against a 0.05 limit). Its finite-minus-impulsive SMA comparison assumes a two-body coast. Under drag the post-burn SMA decays, so an M3 analogue would need its own theory and measurement.
  - **DR-0023 cross-platform 1e-4 m / 1e-7 m/s.** Measured on point-mass + burn. Drag's sensitivity makes transfer unjustified (TL-7 spirit).
  - **DR-0021 reproducibility tolerances** (snapshot classes). Specific to M2 values.
- **M2's maneuver results** (Δv → SMA change) remain correct for the idealized environment. They are not predictions of the same maneuver in an atmosphere, and no M2 record claims that.
- **VAL-0007 metadata caveat (new finding).**
  - The informational GMAT J2 and realistic runs set `Earth.Mu` = WGS 84, but GMAT's gravity field applies the JGM-3 file GM (3.986004415e14). Those runs therefore used the JGM-3 GM and R, not WGS 84.
  - The effect (~0.6 m) is negligible against their 741–1 325 km results, and they gate nothing. The record is not edited; this is noted for the owner (Q-G2-8).

## 14. Owner decisions required (BLOCKED ON OWNER)
| # | Decision | Recommendation |
|---|---|---|
| Q-G2-1 | GMAT exact-configuration method: (a) TOEEq exchange plus a *derived* bound on the Earth-orientation residual; (b) TOEEq exchange plus driving the validator reference with GMAT's reported Earth-fixed axis, making the comparison exact; (c) GMAT informational only for J2 | (b) if a T0 spike shows it is feasible, else (a) |
| Q-G2-2 | Accept the independence classification and the rule that constants are verified by identity (Q9), not by trajectory gates | Accept |
| Q-G2-3 | Convergence for the discontinuous table: (a) order gates on smooth configurations only; (b) step splitting at band crossings; (c) a C1 density interpolation; (d) value continuity enforced (with DR-0024 Q5a) | (a) |
| Q-G2-4 | dt for M3 scenarios: keep 10 s (drag error 4.6 m at B 25.8), or choose from measurement on the implementation (for example 5 s: 0.51 m) | Decide after T4 measurement. No pre-commitment |
| Q-G2-5 | Reference missions: horizon (10 orbits, as M1/M2) plus one long-duration decay mission; inclinations including > 90° for the sign check; one eccentric orbit for ω̇ | As stated; final list at T0 |
| Q-G2-6 | Extend the DR-0021 reference-snapshot mechanism to M3 (new snapshot `snapshot/m3`), or rely on goldens plus GMAT plus the validator reference | Decide with G3. Recommended: a separate M3 snapshot if the same consumed-reference threat applies |
| Q-G2-7 | Source for geodetic-height test points (if H-geod) | Identify a published geodesy reference before T2; no dependency without a DR |
| Q-G2-8 | Record a non-editing erratum note about the VAL-0007 GMAT GM, beside the SCI-0005 wording question (DR-0024 Q3)? | Yes, as an appended note approved by the Tech Lead; no M1/M2 evidence changes |

## Impact
- **Architecture:** validator-side reference models, a configuration identity (DR-0026), GMAT M3 generation.
- **Science/validation:** VAL-0018 onward; new SCI entries (DR-0024).
- **Dependencies:** none new (SciPy and GMAT already used).
- **Development effort:** moderate to high. The validation is larger than the physics, as in M2.
- **Token/compute impact:** long-duration RK4 runs, and DOP853 and GMAT reference generation offline.
- **Reversibility:** high until thresholds are approved.

## Blocked work
- M3 T4–T7 (validators, references, thresholds, Proof).
- T0 reference-mission definition, until Q-G2-5 is answered.

## Work continuing independently
- None of the implementation.

## Requested response
Answers to Q-G2-1 to Q-G2-8, or `discuss`.

## Resolution
**Decision:** principles APPROVED (Tech Lead, 2026-10-15, "M3 planning decision checkpoint", section 2). Each owner question is closed below, either by an owner decision or by an explicit deferral, so that nothing is decided by implication.

**Approved principles:**
1. **Evidence classes.** All M3 validation evidence is classified as one of: independent external reference; partially independent numerical reference; same-model / invariant check; regression check (§2, §11).
2. **GMAT.** GMAT counts as an independent external oracle **only** when its setup is independently specified and documented while representing the same intended physical problem. Every GMAT comparison records the force model (gravity degree/order, the `.cof` file and its GM/R/C̄20, tide model), frame and axes of the state exchange, constants (Earth.Mu, EquatorialRadius, Flattening, rotation), atmosphere model and its table file (with digest), drag model (Cd, area, mass, `DragModel`), propagator, step-size and error-control settings, and any other solver setting needed to reproduce the comparison.
3. **DOP853** with the same force equations or constants is **partially independent**, never fully independent.
4. **No blind reuse of the M2 measured-order rule** (DR-0008 |p − 4| ≤ 0.5). Numerical-order and convergence tests are applied only where their mathematical assumptions hold, in particular on smooth configurations (point mass, J2, the one-band atmosphere).
5. **Discontinuous atmosphere.** For the piecewise table, convergence, error and stability evidence appropriate to a discontinuous right-hand side is used instead of an artificial fourth-order measurement across band boundaries. Together with DR-0024 Q5a: **tests at and immediately around every band boundary** are required.
6. **dt = 10 s is PROVISIONAL.** Candidate timesteps are measured in the designated measurement task, after the physical models and the reference setup exist.
7. **No M3 numerical acceptance threshold is approved during planning.** Thresholds are proposed in a later Decision Request, from measured evidence, with margin and rationale.
8. **Frozen M1/M2 evidence is preserved.** Perturbations-off regression must reproduce it exactly wherever the existing contracts require exact reproduction (M1 golden hash, M2 Proof, M2 cross-platform goldens, M2 reference snapshot).
9. **VAL-0007 correction note** explaining the actual GM used by that GMAT run; the historical measurement is not rewritten.

| # | Closure | Status |
|---|---|---|
| Q-G2-1 | GMAT exact-configuration **method** (a) derived Earth-orientation bound, (b) driving the reference with GMAT's reported axis, or (c) informational only: the owner approved the documentation and independence conditions (principle 2) but **did not choose a method**. T0 must establish which configurations actually represent the intended physics; the method is chosen after T0 | DEFERRED to the T0 checkpoint |
| Q-G2-2 | The four-class independence classification is APPROVED (principle 1). The sub-rule "constants are verified by identity checks, not trajectory gates" was not separately addressed; it stays a PROPOSED method, classed as a same-model check | Classification APPROVED; identity-check rule PROPOSED |
| Q-G2-3 | Option (a) APPROVED in substance: order gates only on smooth configurations (principle 4), with discontinuity-appropriate evidence and boundary tests for the table (principle 5). Option (d) (continuity-enforced values) is **excluded** by DR-0024 Q5a. Options (b) (step splitting at band crossings) and (c) (C1 interpolation) are **not approved**; (c) would alter the source model | APPROVED (a); (c), (d) excluded; (b) not approved |
| Q-G2-4 | dt = 10 s PROVISIONAL; measurement in the designated task (principle 6) | APPROVED |
| Q-G2-5 | Reference missions: **not decided.** T0 builds and exercises candidate configurations (J2, drag/atmosphere, boundary cases) and proposes the list | DEFERRED to the T0 checkpoint |
| Q-G2-6 | M3 reference-snapshot treatment: **not decided**; decided when the M3 validators are designed (T4), with evidence | DEFERRED (T4) |
| Q-G2-7 | Source for geodetic-height test points: **not decided.** T0 must verify geodetic-height behaviour and identify the source it used | DEFERRED to the T0 checkpoint |
| Q-G2-8 | VAL-0007 correction note: APPROVED and added (`docs/science/validation.md`, VAL-0007 "Historical correction note") | APPROVED; done |
| — | Numerical thresholds for M3 | Not approved; later threshold DR (G4) |

**Reasoning/notes:**
- Deferred items carry no default. Code and documents must not treat a recommendation in §14 as the decision.
- §13's statements about what does not transfer from M1/M2 stand unchanged.

**Follow-up:**
- T0 checkpoint: Q-G2-1 method, Q-G2-5 reference missions, Q-G2-7 geodetic source, and candidate C_d/A (DR-0024 Q9).
- T4: Q-G2-6. Later: the threshold DR (G4).
