# Scientific Validation Log

Record meaningful reference comparisons and discrepancies here or link to machine-readable validation artifacts.

Each record should identify:
- date and code revision;
- capability under test;
- project configuration;
- reference source/tool and its configuration/version;
- expected/reference result;
- project result;
- absolute/relative error where meaningful;
- discrepancy classification;
- accepted/rejected/unresolved status;
- linked scientific assumption/ADR/Proof record.

Initially GMAT is the primary orbital reference. Add independent authoritative validation sources as the project matures.

---

## VAL-0001 — Kepler oracle against textbook worked examples
- **Date / revision:** 2026-10-05 / `759fa23`
- **Capability:** `tars.astro.kepler.propagate`, `tars.astro.elements.rv_to_elements` (the M1 validation oracle)
- **References:**
  - Vallado (2013) Example 2-4: Kepler problem, 40 min.
  - Vallado (2013) Example 2-5: RV2COE.
  - SciPy `solve_ivp` DOP853 (rtol 1e-13) as an independent numerical reference.
- **Result:**
  - Example 2-4 matches every printed digit: 1e-4 km in position, 1e-6 km/s in velocity.
  - Example 2-5 matches at printed precision.
  - DOP853 agrees within 1 mm and 1 µm/s for circular, e = 0.15 and e = 0.72 cases.
- **Discrepancy:** A Curtis (2014) Example 3.7 velocity component recalled from memory differed in the 3rd significant figure, while position matched. The value was a transcription from memory and could not be verified, so it is **not used** as an oracle. Classification: reference transcription uncertainty. Status: unresolved and non-blocking. Verify against the physical book if desired.
- **Linked:** `tests/test_kepler.py`, `tests/test_elements.py`; ADR-0006

## VAL-0002 — M1 RK4 convergence and invariants against the exact two-body solution
- **Date / revision:** 2026-10-05 / `6800d8b`
- **Configuration:** `scenarios/m1_leo_250km.json` (dt varied 60…1 s), 53 700 s
- **Reference:** analytic Kepler propagation (VAL-0001)
- **Result:**
  - At dt = 10 s: 0.298 m position error, \|ΔE/E\| = 3.8e-10.
  - Fitted order 4.33; full table in DR-0008.
- **Discrepancy:** order 4.33 rather than 4. Classification: numerical, pre-asymptotic. Status: accepted pending DR-0008.
- **Linked:** DR-0004, DR-0008, `toolbox/validators/m1_proof.py`

## VAL-0003 — Cross-platform agreement (DR-0006)
- **Date / revision:** 2026-10-05 / CI run 37397754454
- **Platforms:**
  - macOS 26 x86_64 (local)
  - ubuntu-latest x86_64
  - macos-latest arm64

  All use Python 3.12 and NumPy 2.5.3 from `uv.lock`.
- **Result:**
  - Event-log sha256 differs between platforms.
  - Final-state difference ≤ 2.9e-6 m and ≤ 3.4e-9 m/s after 10 orbits.
  - Repeat runs on the same platform are byte-identical.
- **Classification:** numerical (floating-point, platform-dependent rounding). Status: expected; bound proposed in DR-0008.

## VAL-0004 — M1 against GMAT R2026a (two-body, matched constants)
- **Date / revision:** 2026-10-06 / reference generated at `336b3b1`
- **Configuration:**
  - Scenario `m1_leo_250km` (hash `603152ad…`), RK4 dt = 10 s.
  - GMAT script `toolbox/references/gmat/m1_two_body.script`: point-mass Earth, Mu = 398600.4418 km³/s², R = 6378.137 km, EarthMJ2000Eq, PrinceDormand78 at Accuracy 1e-13 with MaxStep 60 s.
  - 896 states, every 60 s over 0–53 700 s.
- **Reference:** GMAT R2026a, build Mar 26 2026. Provenance is in `toolbox/references/gmat/README.md` and `m1_two_body_metadata.json`.
- **Results:**

| Comparison | Max position diff | Max velocity diff |
|---|---|---|
| Ours vs GMAT | 0.29832 m | 3.490e-4 m/s |
| GMAT vs exact Kepler | 7.2e-6 m | 8.4e-9 m/s |
| Ours vs exact Kepler | 0.29833 m | 3.490e-4 m/s |

  - Initial SMA difference: 1.9e-9 m, confirming GMAT used the WGS 84 μ. GMAT's default μ would have given about 5 mm.
  - Period difference: 9e-13 s.
  - Initial states are identical.
- **Discrepancy classification:** numerical error (our RK4 truncation, along-track phase lag).
  - Ours-vs-GMAT equals ours-vs-Kepler to 7 µm, and GMAT agrees with the exact solution to 7 µm.
  - There is no modelling or configuration disagreement.
- **Status:** accepted; within the approved 0.6 m (DR-0008).
- **Linked:** ADR-0006, DR-0005, DR-0008, SCI-0001, SCI-0004, SCI-0005

## VAL-0005 — Cross-platform validator under approved bounds; CI hardware variability
- **Date / revision:** 2026-10-06 / CI runs 37397754454 and 37399273081
- **Golden:** `proof/references/m1_final_state.json`. Reference platform: macOS x86_64, Intel i9-9880H.
- **Results:**

| Platform | \|Δr\| | \|Δv\| |
|---|---|---|
| ubuntu-latest, run 37397754454 | 2.89e-6 m | 3.4e-9 m/s |
| ubuntu-latest, run 37399273081 | 8.76e-7 m | 1.0e-9 m/s |
| macos-latest arm64, both runs | 8.76e-7 m | 1.0e-9 m/s |

- **Finding:** the same CI label (`ubuntu-latest`, same `uv.lock`) produced different last bits on different runs. GitHub-hosted runners vary in CPU model, and NumPy dispatches SIMD kernels by CPU at runtime.
  - "Same platform" in DR-0006 must therefore be read as the same machine type (CPU and instruction set), not the same OS label.
  - Reports now record the CPU model (`platform_info`).
- **Classification:** numerical (floating-point, hardware-dependent). Status: accepted. All runs are within the approved 1e-4 m / 1e-7 m/s bounds, by a margin of more than 30×.
- **Addendum (CI run 37400894038):** on both CI platforms the M1 initial velocity differs from the reference platform's by 1.29e-12 m/s, about 1.5 ulp. This comes from the last bits of `sin`/`cos(51.6°)` in the platform math library.
  - The initial position is identical.
  - Growth of this 1-ulp initial difference, mostly along-track, plausibly accounts for the ~1e-6 m final-state differences.
  - Consequence: the GMAT-script provenance check compares the six state literals within the approved cross-platform bound. All other lines must match exactly.

## VAL-0006 — GMAT reference gates (DR-0009)
- **Date:** 2026-10-05
- **Result:** the committed GMAT R2026a reference passes all nine approved `gmat_reference` gates.

| Gate | Measured | Limit | Margin |
|---|---|---|---|
| Ours vs GMAT, position | 0.298 m | 0.6 m | 2.0× |
| Ours vs GMAT, velocity | 3.49e-4 m/s | 7e-4 m/s | 2.0× |
| GMAT vs Kepler, position | 7.2e-6 m | 1e-4 m | 14× |
| GMAT vs Kepler, velocity | 8.4e-9 m/s | 1e-7 m/s | 12× |
| Initial SMA difference | 1.9e-9 m | 1e-6 m | 537× |
| Initial-state difference | 0 m | 1e-6 m | — |
| Period difference | 9e-13 s | 1e-8 s | 1.1e4× |
| Script initial position | 0 m | 1e-6 m | — |
| Script initial velocity | 0 m/s (CI: 1.3e-12 m/s) | 1e-9 m/s | ≥ 770× |

- **Sensitivity:** synthetic references with μ = 3.986004415e14, 3.986004421e14 and μ·(1+1e-12) all fail, regardless of sign (test and reviewer `/tmp/rerev_a.py`).

## VAL-0007 — INFORMATIONAL: M1 model vs realistic GMAT models (DR-0005; not an M1 gate)
- **Date:** 2026-10-05
- **Purpose:** measure how far the approved M1 model (point-mass Earth, no drag) departs from higher-fidelity physics over the same 10 orbits (53 700 s), starting from the same Cartesian state.
- **Reference:**
  - GMAT R2026a with the JGM-3 gravity field (GMAT-bundled `JGM3.cof`).
  - Jacchia-Roberts atmosphere with constant F10.7 = F10.7A and Kp = 3.
  - Illustrative spacecraft: GMAT defaults (850 kg, 15 m², Cd 2.2; m/(Cd·A) = 25.8 kg/m²). There is no project spacecraft yet.
  - Artifacts: `toolbox/references/gmat/informational/` (scripts, reports, metadata, `summary.json`). Reproduce with `gmat_m1.py realistic-summary`.

| Case | Max divergence from M1 | Final radial / in-track / cross-track | Node drift (fit) | Mean SMA change over the run | Geodetic altitude range |
|---|---|---|---|---|---|
| J2 only | 741 km | −41 / +674 / +303 km | −5.439°/day | −2 m | 238.2–256.3 km |
| JGM-3 4×4 | 741 km | −42 / +675 / +303 km | −5.427°/day | −3 m | 238.1–256.2 km |
| 4×4 + drag, F10.7 = 70 | 909 km | −67 / +855 / +302 km | −5.433°/day | −3.6 km | 235.0–256.0 km |
| 4×4 + drag, F10.7 = 150 | 1 092 km | −99 / +1 045 / +300 km | −5.439°/day | −7.4 km | 231.0–256.0 km |
| 4×4 + drag, F10.7 = 250 | 1 325 km | −147 / +1 282 / +298 km | −5.446°/day | −12.4 km | 226.0–256.0 km |

**Interpretation and checks:**
- **J2 dominates the geometry.** The measured node drift (−5.44°/day) matches the first-order analytic J2 rate quoted in SCI-0001 (−5.41°/day) within 0.5%; the remainder is consistent with first-order theory using osculating rather than mean elements.
  - The cross-track divergence of about 303 km matches r·ΔΩ·sin i = 305 km for the measured ΔΩ = −3.37°.
  - The larger in-track divergence of about 674 km is a phase drift. The point-mass circular velocity is not a J2-circular state, and J2 changes the mean motion. This interpretation is standard, not separately verified here.
- **Higher harmonics (4×4) change little** over 10 orbits compared with J2 alone.
- **Drag adds orbital decay that M1 cannot represent.**
  - The mean SMA falls 3.6 / 7.4 / 12.4 km over the run (about 6 / 13 / 22 km/day) for F10.7 = 70 / 150 / 250. Solar activity changes the decay by about 3.5× across this range.
  - Implied mean densities are 3.7e-11 / 7.7e-11 / 1.3e-10 kg/m³, consistent in order of magnitude with tabulated thermospheric densities near 250 km.
  - The decay figures scale inversely with the assumed m/(Cd·A), so they are illustrative for this ballistic coefficient only.
- **Geodetic altitude** (above the WGS 84 ellipsoid) spans about 238–256 km even without drag. This differs from M1's spherical 250 km definition (SCI-0006) because of the ellipsoid and the J2-induced radius oscillation.

**Conclusion:**
- The M1 model reproduces the chosen idealized physics to 0.3 m (VAL-0002, VAL-0004).
- It departs from realistic LEO physics by about 0.7–1.3 **thousand km** within 15 hours.
- This confirms SCI-0001 and SCI-0004 as stated and quantifies them. J2 and drag must precede any mission that depends on real ground tracks, node timing, or orbit lifetime.

- **Status:** informational; no gate. GMAT epoch-column drift REV-012 is deferred (see the GMAT README).

## VAL-0008 — PLANNING: finite-burn numerics with RK4 (M2; not a gate)
- **Date / revision:** 2026-10-09 / `63bec8d` (research scripts; no project propulsion code exists)
- **Purpose:** measure whether fixed-step RK4 at the approved dt = 10 s can model a finite burn with changing mass, and what step handling is required, before choosing the M2 architecture (DR-0013) and candidate tolerances (DR-0015).
- **Configuration:** M1 initial state. Illustrative spacecraft: 1000 kg dry, 300 kg propellant, 490 N, Isp 312 s, g0 = 9.80665 m/s². Velocity-tracking prograde burn at t = 600 s for 77.3 s. Propagated to 53 700 s. Artifacts: `docs/science/experiments/m2-planning/`.
- **Reference:** SciPy DOP853 (rtol 1e-13), integrated segment by segment across the burn boundaries. The post-burn coast agrees with the exact Kepler oracle (VAL-0001) to 5.7e-6 m, and propellant use agrees with ṁ·T exactly.
- **Results:**

| Quantity | Measured |
|---|---|
| Propellant used (analytic ṁ·T) | 12.3794 kg; Δv (rocket equation) 29.2758 m/s |
| Orbit change | SMA +50 521 m; apoapsis altitude 351.03 km, periapsis 250.02 km, e = 0.00756 |
| RK4 dt = 10 s, step **split** at cutoff: error at the first tick after cutoff | 7.7e-4 m, 1.2e-6 m/s |
| Same, at 53 700 s | 0.290 m, 3.35e-4 m/s (M1 coast-only RK4 error: 0.298 m) |
| RK4 dt = 10 s, step **not** split (thrust switched off inside the RK4 stages) | **168 km**, 193 m/s; propellant error 0.43 kg |
| Convergence, split, dt 20 → 10 → 5 → 2.5 s | Observed order 4.47, 4.31, 4.18 |
| RK4 propellant mass error | ≤ 5e-12 kg (RK4 integrates the linear mass law exactly; round-off only) |
| Integrated sensed Δv vs rocket equation (RK4 dt = 10 s) | 3.5e-13 m/s |
| Finite − impulsive SMA (impulsive Δv from the rocket equation, applied at burn midpoint) | −0.131 m (2.6e-6 of ΔSMA) |
| Impulsive limit: finite − impulsive SMA ratio when burn duration halves (fixed Δv) | 3.987, 3.997, 3.9992, 3.9998, 3.99995 → **second order in burn duration** |
| Fixed inertial direction (velocity at ignition) − velocity-tracking | SMA −69.3 m; 4.63 km apart at 53 700 s |

- **Conclusions:**
  - RK4 at dt = 10 s keeps 4th-order accuracy through a finite burn **only if steps are split at engine on/off times**. Straddling the discontinuity is not acceptable (DR-0013).
  - The burn itself adds about 1 mm; end-of-run error is dominated by the same coast error as M1.
  - The pointing model (tracking vs fixed inertial) is a material physical choice (DR-0012).
  - Finite burns converge to the impulsive textbook result as burn duration² (DR-0015 analytic gate).
- **Classification:** planning measurement; no discrepancy. **Status:** informational; to be re-measured on the implemented code and approved scenario before any threshold is approved.

## VAL-0009 — PLANNING: GMAT R2026a finite-burn probe (M2; not a gate)
- **Date / revision:** 2026-10-09 / `63bec8d`
- **Purpose:**
  - Determine which equation of motion GMAT actually integrates for a finite burn. The GMAT Mathematical Specification (R2026a draft, Eq. 4.2–4.3) writes d(mv)/dt = ΣF, which implies an extra ṁ/m·ṙ term; the correct variable-mass form gives a = F/m (Plastino & Muzzio 1992).
  - Identify configuration traps and the agreement level achievable with GMAT as a gated M2 reference.
- **Configuration:** same case as VAL-0008. GMAT `ChemicalThruster` C1 = 490 N, K1 = 312 s, `DecrementMass = true`, `CoordinateSystem = Local`, `Origin = Earth`, `Axes = VNB`, direction (1, 0, 0). `ChemicalTank` 300 kg, `DryMass` 1000 kg. Point-mass Earth with WGS 84 μ and radius. PrinceDormand78, Accuracy 1e-13. `BeginFiniteBurn` / `Propagate {ElapsedSecs = 77.3}` / `EndFiniteBurn`.
- **Results (vs the DOP853 reference of VAL-0008):**

| GMAT `GravitationalAccel` | Mass after burn − analytic | SMA after burn | Final position / velocity at 53 700 s |
|---|---|---|---|
| **9.80665** (override) | +3.0e-8 kg | −0.12 mm | 1.17 cm, 1.3e-5 m/s |
| 9.81 (GMAT default) | +4.2e-3 kg | −83 mm | 7.85 m, 9.0e-3 m/s |

- **Findings:**
  1. **GMAT integrates a = F/m, not the Math Spec's d(mv)/dt form.** The extra term would be about ṁ·v/m ≈ 0.95 m/s² here, larger than the thrust acceleration itself (0.38 m/s²). The measured 0.12 mm SMA agreement excludes it.
  2. **GMAT's default `GravitationalAccel` is 9.81 m/s²** (GMAT help, `ChemicalThruster`), not standard gravity g0 = 9.80665 m/s². Like the Earth μ in M1 (SCI-0005), it must be overridden and gated, or the comparison measures a configuration mismatch (7.85 m here).
  3. **The residual 1.2 cm is explained by burn timing.** The mass difference implies GMAT burned 1.85e-7 s less. One ulp of GMAT's Modified Julian epoch near MJD 31 041 is 3.14e-7 s. A 1.85e-7 s shorter burn changes Δv by about 7e-8 m/s, giving ΔSMA ≈ 0.12 mm and an along-track drift of about 1.1 cm over 9.9 orbits, as measured. Working hypothesis: epoch quantization in GMAT's stopping logic. This is the same family as the deferred REV-012 epoch-column drift, and it is **not verified against GMAT internals**.
  4. GMAT throws an exception at tank depletion by default (`AllowNegativeFuelMass = false`). Our propellant-exhaustion behavior therefore cannot be validated against GMAT; only analytically.
- **Classification:** finding 1: reference-documentation discrepancy, resolved by measurement. Finding 2: reference configuration trap. Finding 3: reference-tool numerical resolution (hypothesis). **Status:** informational. Feeds DR-0011 and DR-0015. GMAT evidence for M2 gates must come from a committed, provenance-tracked reference generated from the approved scenario, not from this probe.

## VAL-0011 — T1 standalone propulsion model vs analytic and independent references (M2; unit level, not a Proof gate)
- **Date / revision:** 2026-10-09 / `de23600` (`src/tars/sim/propulsion.py`, `tests/test_propulsion.py`)
- **Configuration:** DR-0010 reference case (490 N, 312 s, 1000 kg dry + 300 kg propellant, 77.3 s burn). The project RK4 is composed with the model functions in tests; the simulator is not involved (T2 not authorized). VAL-0010 is reserved for the REV-012 investigation.
- **Results:**

| Check | Reference | Measured |
|---|---|---|
| Mass flow, propellant used | F/(Isp·g0) by hand | ṁ = 0.1601477385766618 kg/s; 12.379420191975958 kg (= VAL-0008) |
| O2 rocket equation vs adaptive quadrature of F/m(t) (SciPy `quad`, epsrel 1e-13) | Tsiolkovsky | 29.275767297714708 m/s; relative difference −6.3e-15 |
| O3 free-space velocity, RK4 dt = 10 / 5 / 2.5 s | closed form, 40-digit decimal | 5.3e-13 / 4.2e-14 / 1.3e-14 m/s (≤ 1.8e-14 relative: round-off) |
| O3 free-space displacement, RK4 dt = 10 / 5 / 2.5 s | closed form, 40-digit decimal | 4.29e-9 / 2.79e-10 / 1.72e-11 m on 1130 m; order 3.94, 4.02 |
| Mass conservation (RK4) | linear law | ≤ 2.8e-13 kg |
| Powered arc in orbit, RK4 dt = 20 / 10 / 5 s at cutoff | SciPy DOP853 rtol 1e-13 | 1.37e-3 / 8.89e-5 / 5.80e-6 m; order 3.95, 3.94 |

- **Finding (test design, corrected before commit):**
  - The first version of the free-space test assumed position agreement at round-off. The measured 4.3e-9 m is real 4th-order RK4 truncation, because for x″ = a(t) the position's local error depends on a‴, not a⁗. The a-priori estimate was wrong by about 10³.
  - The float64 closed form also loses about 1.5e-9 m to cancellation.
  - The test now uses a 40-digit decimal reference, a round-off bound for velocity, and the approved convergence-order policy (|p − 4| ≤ 0.5, DR-0008) for position. No new numerical tolerance was introduced.
- **Mutation check:** six deliberate physics mutants were each detected by the suite: g0 = 9.81, wrong mass in F/m, negative residual propellant, a 1 % slack in the sufficiency check (needed a new boundary test), retrograde = prograde, and a cutoff shifted 5 s.
- **Classification:** no discrepancy. **Status:** informational; Proof-level gates come from DR-0015 after T5/T6 and REV-012.
