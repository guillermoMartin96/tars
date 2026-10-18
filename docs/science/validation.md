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
- **Historical correction note (2026-10-15; DR-0025 Q-G2-8, approved by the Tech Lead).** The entry above is left as written; this note corrects its implied constants.
  - **Historical result (unchanged):** the measured divergences, node drifts, SMA changes and altitude ranges in the table, from the committed scripts and reports in `toolbox/references/gmat/informational/`.
  - **Incorrect historical description:** the generated scripts set `Earth.Mu = 398600.4418` and `Earth.EquatorialRadius = 6378.137` (WGS 84), which presents the runs as using the project's constants. Nothing in the record says otherwise.
  - **Corrected interpretation:** these runs use a gravity field (`GravityField.Earth.PotentialFile = 'JGM3.cof'`), and GMAT's gravity field applies the GM and reference radius from the `.cof` file header, not `Earth.Mu`. The JGM-3 file header gives GM = 3.98600441500000e+14 m³/s² and R = 6.37813630000000e+06 m, and its C̄2,0 = −4.84165374886470e-04 (so J2 ≈ 1.0826267e-3). Established by the M3 planning GMAT probe (VAL-0018: a GMAT run with a generated `.cof` matches the Kepler solution with GM 3.986004415e14 to 1.4e-5 m and differs from WGS 84 by 0.627 m). So the J2-only, 4×4 and drag cases used the JGM-3 GM, R and J2.
  - **Effect on prior acceptance decisions: none.** VAL-0007 is informational and gates nothing (DR-0005). The GM difference is about 0.6 m over 10 orbits, negligible against the 741–1 325 km results and the conclusions drawn from them. The gating M1/M2 GMAT references use a point-mass force with `Earth.Mu` and are unaffected (SCI-0005 correction note).

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
- **Classification:** finding 1: reference-documentation discrepancy, resolved by measurement. Finding 2: reference configuration trap. Finding 3: reference-tool numerical resolution (hypothesis).
- **Addendum (2026-10-09, VAL-0010):** the finding 3 hypothesis is **refuted**. The 1.85e-7 s shortfall is GMAT rounding the final step to a time stop condition to whole microseconds (`TIME_ROUNDOFF = 1e-6`). It is not epoch-ulp quantization; the 3.1e-7 s ulp was a coincidence. Findings 1, 2 and 4 stand. **Status:** informational. Feeds DR-0011 and DR-0015. GMAT evidence for M2 gates must come from a committed, provenance-tracked reference generated from the approved scenario, not from this probe.

## VAL-0010 — REV-012: GMAT epoch bookkeeping and stop-time quantization (root cause)
- **Date / revision:** 2026-10-09 / harness `e47ce31`; results committed on branch `investigation/rev-012-gmat-epoch`
- **Who:** investigation by a separate agent in an isolated worktree, as authorized by the Tech Lead. The agent is the same model family as the implementer, not a different provider. It was interrupted before writing this record. The implementing engineer completed the record after independently verifying:
  - `rev012.py analyze` reproduces `results.json` byte-for-byte from the committed reports;
  - `rev012.py reproduce` re-runs GMAT and reproduces the committed M1 reference report and the VAL-0009 probe report byte-for-byte;
  - the cited GMAT R2026a source lines exist as described: `PropagationEnabledCommand.hpp` defines `TIME_ROUNDOFF 1.0e-6`; `Propagate.cpp` l. 5501/5640 round `secsToStep`; l. 4610/4617 set `currEpoch = baseEpoch + elapsedTime/86400`.
- **Questions:** REV-012 (M1 epoch-column drift) and VAL-0009 finding 3 (M2 probe burn shortfall). Root cause, origin, impact, comparison method, and M1 compatibility.
- **Artifacts:** `docs/science/experiments/rev-012/`: README, `rev012.py`, 61 generated scripts, reports, `results.json`, `run_provenance.json`, `reproduce.json`.
- **Root cause: verified (GMAT source + bit-exact reproduction).** Both effects are **GMAT behavior**. Our timestamp handling is not involved. There are two distinct mechanisms:
  - **M-a, epoch drift (REV-012).**
    - GMAT stores the spacecraft epoch as a double A.1 MJD.
    - Each `Propagate` command re-rounds it once (`currEpoch = baseEpoch + elapsedTime/86400`; the two-part `GmatTime` path is off by default).
    - The rounding error per command is constant for a given epoch and segment, so drift grows linearly with the number of commands. M1 (895 × 60 s at the M1 epoch): −1.063e-4 s, reproduced bit-exactly on all 896 rows.
    - `Sat.ElapsedSecs` is derived from the same double, so it drifts too.
    - **The integrated states are at the labelled elapsed times** (vs Kepler: 7.2 µm, 9e-10 s). M1's comparison used the labels, so it was never affected.
  - **M-b, stop-time rounding (VAL-0009 shortfall).**
    - When a time stop condition triggers, GMAT rounds the remaining step to a whole microsecond.
    - After adaptive steps, each time-stopped `Propagate` (ignition, burn end, coast end) therefore ends up to about 0.5 µs (+ |q| ≤ 0.31 µs epoch term) off the requested time.
    - The model predicts all 35 measured burn durations (5 epochs × 7 durations) to the mass resolution, ≤ 2.3e-12 s. The 77.3 s case reproduces −1.847e-7 s.
- **Impact (measured, reference burn, at 53 700 s):**
  - Sensitivity per µs: burn duration 6.2 cm; final stop time 7.7 mm; ignition shift 0.1 mm.
  - Re-running the DOP853 reference with GMAT's three measured offsets reduces GMAT − reference from **1.17 cm → 6.8 µm**. The VAL-0009 residual is fully explained.
  - Time-dependent forces (Earth rotation, ephemerides, drag) would see the M-a epoch error as a time offset. That impact is an order-of-magnitude estimate only, not measured.
- **Methods tested:**
  - *Aligned stepping:* coast `InitialStepSize = MaxStep = 60 s`; burn `InitialStepSize = MaxStep = 1 s`, so every stop lands on the step grid and no rounding is applied. Result: burn duration ≤ 6e-10 s, ignition 2e-13 s, final stop ≤ 1e-9 s. GMAT vs independent DOP853 **without correction: 12 µm, 1.4e-8 m/s**, identical at three epochs.
  - *Single-step burn:* unreliable; the integrator still cut the step for 77.3 s.
  - *Streaming output:* one `Propagate` with a row per step gives single rounding per row. It matches the committed M1 reference to 1.3e-9 m.
- **M1 compatibility:** no change to M1 is needed or proposed. M1's approved comparison aligns on `ElapsedS` labels at states verified to 9e-10 s. The committed M1 reference reproduces byte-for-byte. No threshold, reference, scenario, or M1 code was modified.
- **Consequences for DR-0015 candidates:**
  - The O9 basis "1 MJD ulp per burn boundary", including the 1e-7 kg mass candidate, rests on the refuted hypothesis.
  - The 2.5e-2 m GMAT-vs-reference candidate reflects the unaligned method.
  - Both need re-derivation under the method chosen in **DR-0016**. Nothing has been changed.
- **Limits:** point-mass Earth, one host, GMAT R2026a only. Aligned stepping depends on steps being MaxStep-limited, so each generated reference must verify this (per-step rows, mass, Kepler timing).
- **Classification:** reference-tool numerical behavior (verified), not an implementation error. **Status:** REV-012 root cause resolved for evidence purposes. The comparison method for gated M2 GMAT validation awaits DR-0016.
- **Addendum (2026-10-10): the DOP853 reference has a cross-platform precision floor of several micrometres.**
  - Recomputing the attribution in CI gave the following GMAT − DOP853 values at 53 700 s:

    | Stepping | Ubuntu x86_64 | Reference host | macOS arm64 |
    |---|---|---|---|
    | Natural | 1.17245 cm | 1.17260 cm | 1.17288 cm |
    | Aligned | ~11 µm | 12.3 µm | ~15 µm |

  - The GMAT reports are committed and identical everywhere. The spread is in the SciPy DOP853 reference: its adaptive step-size decisions amplify last-bit platform differences.
  - **Interpretation:**
    - The ≈ 1.2 cm → ≈ 10 µm improvement from aligned stepping (DR-0016) holds on every platform.
    - The aligned residual is at the reference's own precision floor, so it bounds GMAT's disagreement from above rather than measuring it.
  - **Consequence for T6/T7:** any GMAT-vs-DOP853 gate must not be set below the reference's demonstrated cross-platform spread (tens of µm at this horizon), unless the reference is made platform-robust.
  - `tests/test_rev012_evidence.py` now uses bounds derived from this measured spread. Its first version assumed last-bit agreement and failed in CI from `f8e62c4`.

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
- **Correction (2026-10-10, external review M2-T1-review-01):**
  - **The "independent" orbit row is overstated.** The DOP853 reference above used the same production right-hand side, including the production pointing law, as the RK4 run. It therefore checked the integrator, not the velocity-tracking model. A frozen-pointing mutant passed every test (REV-T1-05).
  - Since `af4de18` the reference uses an independently written right-hand side, and the mutant fails.
  - **A mutation was missing.** The mutation list above omitted stateful pointing mutants, and its "1 % slack" boundary test only probed a favourable value. The exact-boundary rule is now time-domain and tested in both directions (REV-T1-03).
  - **Some assertions were weaker than stated.** `pytest.approx`'s default absolute floor (1e-12) made several small-quantity relative checks looser than written. All checks now use `abs=0`.
  - The measured values in the table are unaffected.

## VAL-0012 — T2: production simulator on the reference burn (M2; measurement, not a Proof gate)
- **Date / revision:** 2026-10-10 / `f4b9774` (simulator); script `docs/science/experiments/m2-t2/measure_t2.py`, output `results.json`. A rerun is byte-identical on the reference host.
- **Configuration:** DR-0010 reference case from the M1 initial state, run through the production `Simulator`:
  - spacecraft 1000 kg dry + 300 kg propellant;
  - 490 N / 312 s engine;
  - prograde burn scheduled at 600 s for 77.3 s; coast to 53 700 s.
- **References:**
  - the VAL-0008 SciPy DOP853 final state (rtol 1e-13), whose right-hand side shares no production code;
  - the exact Kepler propagation of the simulator's own cutoff state;
  - analytic mass law and rocket equation.
- **Results:**

| dt [s] | vs DOP853 at 53 700 s | Coast vs Kepler from cutoff | Propellant − ṁT | Sensed Δv − rocket eq. (rel) |
|---|---|---|---|---|
| 20 | 6.43 m, 7.4e-3 m/s | 6.27 m | 5e-14 kg | 2.9e-13 |
| **10** | **0.2904 m, 3.35e-4 m/s** | 0.283 m | −1.2e-13 kg | 2.3e-14 |
| 5 | 1.47e-2 m, 1.69e-5 m/s | 1.43e-2 m | 2.8e-13 kg | 5.8e-15 |
| 2.5 | 8.17e-4 m, 9.4e-7 m/s | 7.9e-4 m | 2.8e-13 kg | 4.6e-15 |

- **Observed order** vs DOP853: 4.47, 4.31, 4.17 (20 → 2.5 s). The 20 → 10 pair is pre-asymptotic, as in M1 (DR-0008).
- **Cross-check against the independent planning implementation (VAL-0008):** at dt = 10 s the planning script's error was 0.290353 m; the production simulator's is 0.290351 m (Δ ≈ 1.6 µm). SMA after the burn: production 6 678 658.0324 m, planning reference 6 678 658.0325 m.
- **Interpretation:**
  - With exact step splitting the burn contributes negligibly. The end-of-run error is the same RK4 coast error as M1 (0.298 m on the circular orbit; 0.283 m here from the cutoff state).
  - Mass and sensed Δv are exact to round-off.
- **Classification:** no discrepancy. **Status:** informational evidence for the M2 threshold DR (DR-0015 method). It does not approve any tolerance.
- **Re-run at `03f6e4b` (after REV-T2-03):**
  - Plans now describe the represented interval `cutoff − ignition` (77.29999999999995 s here) and its consumption.
  - Every trajectory quantity is bit-identical. Only "Propellant − ṁT" changed, by ≤ 7e-15 kg: 5.9e-14 / −1.1e-13 / 2.9e-13 / 2.9e-13 kg. `results.json` is regenerated.

## VAL-0013 — T5: M2 Proof oracles O1–O8 on the reference missions (provisional thresholds; reference host)
- **Date / revision:** 2026-10-11 / `b9bd22c` (validators); validator `toolbox/validators/m2_proof.py`, logic `src/tars/validation/m2.py`, missions `src/tars/validation/m2_missions.py`. The report from the Proof run is committed under `proof/records/evidence/M2-T5/`. CI reports for ubuntu and macOS are uploaded as artifacts (`proof-<os>`). They are evidence for T7; they are not compared here.
- **Host:** Darwin x86_64, i9-9880H, Python 3.12.15, NumPy 2.5.3 (the M1 reference host).
- **Missions** (all from the M1 circular 250 km orbit, dt = 10 s, stop at 53 700 s, 490 N / 312 s engine):

| Mission | Burns | Outcome |
|---|---|---|
| `m2_prograde_burn` (slice) | 77.3 s prograde at 600 s | apoapsis 351.03 km, periapsis 250.02 km |
| `m2_retrograde_burn` | 77.3 s retrograde at 600 s | apoapsis 249.98 km, periapsis 150.86 km |
| `m2_burn_to_depletion` | 20 kg tank; 200 s burn_to_depletion; submitted and ignited at 600 s | flames out at 724.8847 s after 124.8847 s; residual 1.1e-14 kg; apoapsis 461.17 km |
| `m2_invalid_commands` | 12 entries: 3 accepted (one corrected retry, one adjacent to the previous cutoff), 9 rejected | 8 distinct rejection codes |
| `…_empty_tank` / `…_no_propulsion` (derived) | same timeline, 0 kg propellant / no spacecraft | `no_propellant` / `no_propulsion_configured`, plus precedence |

All 10 approved rejection codes are exercised.

- **Independence.** Expected values come from the scenario's raw inputs only: F, Isp, masses, commanded times, and the hand-declared receipts in `m2_missions.py`. The relations are textbook: ṁ = F/(Isp·g0), the rocket equation, and a closed form; the trajectory reference is SciPy DOP853 on an independently written right-hand side. Simulator outputs are only the quantities under test. Two documented exceptions:
  - O5 propagates the simulator's own cutoff state. It tests the coast, not the burn.
  - O6 starts the impulsive reference from the simulator's ignition state, so the pre-burn coast error cancels.
- **Methods and units:**
  - **O1:** |integrated propellant used − ṁ·T| / initial mass, where T is the commanded duration or the analytic depletion time P/ṁ. For a depletion burn, the residual is compared with the DR-0017 D1a bound ṁ·2·ulp(cutoff).
  - **O2:** |sensed Δv − c·ln(m0/mf)| / Δv, with m0 and mf chained burn by burn from the scenario.
  - **O3:** production `Simulator`, zero force, velocity tracking along v0 (prograde and retrograde). Velocity and propellant are compared with the 40-digit closed form at cutoff. Position is checked by its convergence order between dt = 10 and 5 s, because its error is genuine RK4 truncation (VAL-0011).
  - **O4:** state at each cutoff (`BurnEnded`) and at 53 700 s, against DOP853 (rtol 1e-13, atol 1e-9, segments split at the predicted ignition and cutoff times).
  - **O5:** every telemetry sample in each coast arc, against exact Kepler propagation of the arc's start state.
  - **O6:** five runs at fixed Δv (thrust × 2^k, duration / 2^k, same midpoint), comparing the finite-burn SMA with the impulsive vis-viva SMA. Reported as the order per halving and as the slice ratio |ΔSMA_finite/ΔSMA_impulsive − 1|.
  - **O7:** signs of ΔE and ΔSMA across each burn, and the rotation of the angular-momentum direction.
  - **O8:** final position error against DOP853 at dt = 10, 5 and 2.5 s.
- **Results (reference host):**

| Oracle | Metric | Prograde | Retrograde | Depletion | Invalid cmds | Provisional limit |
|---|---|---|---|---|---|---|
| O1 | propellant used, rel. to initial mass | 9.2e-17 | 9.2e-17 | 1.0e-17 | 4.2e-17 | 1e-12 |
| O1 | depletion residual / D1a bound | — | — | 0.305 | — | 1 (analytic) |
| O2 | sensed Δv, rel. | 1.1e-14 | 1.1e-14 | 4.9e-14 | 5.6e-14 | 1e-12 |
| O4 | at cutoff [m; m/s] | 7.65e-4; 1.21e-6 | 7.80e-4; 1.24e-6 | 8.14e-4; 1.33e-6 | 8.01e-3; 1.00e-5 | 2e-3; 3e-6 (invalid cmds: 1.6e-2; 2e-5) |
| O4 | at 53 700 s [m; m/s] | 0.2904; 3.35e-4 | 0.3127; 3.64e-4 | 0.2891; 3.20e-4 | 0.2973; 3.50e-4 | 0.6; 7e-4 |
| O5 | coast max [m; m/s] | 0.283; 3.26e-4 | 0.314; 3.64e-4 | 0.275; 3.04e-4 | 0.279; 3.27e-4 | 0.6; 7e-4 |
| O6 | max \|p − 2\| over 4 pairs | 0.0041 | 0.0039 | — | — | 0.05 |
| O6 | slice ratio deviation | 2.59e-6 | 2.56e-6 | — | — | 1e-5 |
| O6 | finite − impulsive SMA (77.3 s) | −0.131 m | −0.127 m | — | — | reported |
| O7 | sign violations; plane rotation [rad] | 0; 1.4e-19 | 0; 7.5e-17 | 0; 1.5e-16 | 0; 1.0e-16 | 0; 1e-12 |
| O8 | orders 10→5, 5→2.5 | 4.31, 4.17 | 4.33, 4.19 | 4.28, 4.14 | 4.32, 4.21 | \|p − 4\| ≤ 0.5 |
| Accounting | propellant, Δv bookkeeping (rel.) | 0, 0 | 0, 0 | 0, 0 | 0, 0 | 1e-12 |
| Accounting | \|thrust accel\| vs F/m; direction vs ±v̂ | 1.5e-16; 1.7e-16 | 1.5e-16; 1.7e-16 | 1.2e-16; 1.1e-16 | 1.5e-16; 1.2e-16 | 1e-12 |

  - **O3 (free space, slice burn):** velocity rel. error 1.8e-14; propellant 2.1e-16 of the initial mass; position error at dt = 10 s 4.26e-9 m (prograde) and 4.25e-9 m (retrograde); orders 3.80 and 3.88 (limits 1e-12, 1e-12, |p − 4| ≤ 0.5).
  - **Contract checks** (exact; no tolerance) all hold on every mission:
    - event order and cadence;
    - traceability, including commanded against executed values;
    - declared receipts and the predicted burn lifecycle;
    - mass bookkeeping identities;
    - rejected commands change nothing: each run is bit-identical to a control run with only the accepted entries;
    - in-process and cross-process determinism;
    - the DR-0018 boundary at four stop times (inside a burn, before ignition, at ignition, at cutoff).
- **Cross-checks with earlier records.**
  - The slice values reproduce VAL-0012 at dt = 10 s: 0.2904 m against DOP853; coast 0.283 m; orders 4.31 and 4.17.
  - O6 reproduces the VAL-0008 planning values: −0.131 m; ratio 2.6e-6.
  - The slice events sha256 is unchanged from T4 (`42316356…`).
- **Observations:**
  - **O4 at cutoff is dominated by the coast before the burn.** The invalid-command mission's last cutoff is at 2420 s, and its error (8.0e-3 m) is ten times the slice's at 677 s. A single horizon-independent cutoff limit would be meaningless, so the provisional limit for that mission is scoped (≈ 2× measured).
  - **Sensed Δv cannot see a thrust-vector error.** It integrates the scalar F/m separately from the trajectory. A 1e-5 thrust-vector mutant passes O2 and is caught only by O4, which the test suite pins.
  - **Depletion leaves the DR-0017 D1a residual,** so the tank is not empty. A later reject-policy burn is `insufficient_propellant`. A later `burn_to_depletion` burn is `burn_unschedulable`: the depletion time of the residual (~7e-14 s) is below the clock resolution at 1800 s. `no_propellant` therefore needs a tank loaded empty.
  - **The DR-0017 timing bound is separate from trajectory error.** The validators report each burn's `timing_delta_v_error_mps` from `CommandAccepted` as a per-burn timing quantity. They never use it as a trajectory-error bound. The trajectory error is O4/O5/O8.
- **Thresholds.** `proof/thresholds/m2.json` is **provisional**: the DR-0015 candidates, or the DR-0015 method applied to these measurements (basis per group in the file). No threshold was set or changed to make a check pass. Final values come from T7 (three platforms, threshold DR). FU-1 (GMAT gates; 11–15 µm DOP853 floor) is untouched. O8 excludes dt = 1 s, whose error (~2e-5 m) approaches that floor.
- **Classification:** no discrepancy. **Status:** provisional Proof evidence (T5); not an approval of any tolerance.
- **Revision after review M2-T5-review-01 (2026-10-11):**
  - O4 is now seeded from an independently derived initial state, which is bit-identical to the simulator's (initial error 0). It compares every `StateSampled`, coast and powered, with the reference.
    - Largest sample errors: 0.2906 / 0.3127 / 0.2891 / 0.2973 m (prograde, retrograde, depletion, invalid commands), near the end of the horizon. The prograde maximum is at 53 400 s (0.290574 m); its final error at 53 700 s is 0.290344 m (correction from re-verification).
  - The reference now restarts at each sample time. Final errors move by at most about 7 µm (slice 0.290351 → 0.290344 m), within the DOP853 cross-platform floor. Cutoff errors move by below 1e-7 m.
  - The final state is judged at the scenario's requested horizon, and the final-state consistency and depletion pairing are checked both ways.
- **Revision after re-verification (review M2-T5-review-01, findings F5–F15, 2026-10-11).** The validators now check every simulator output against an independent expectation or an exact rule, for every run: reference missions, derived variants, DR-0018 stop-time variants and the O6/O8 auxiliary runs. New measured quantities (reference host):

| Quantity | Measured | Provisional limit (basis) |
|---|---|---|
| Ignition state vs DOP853 | 6.9e-4 m, 1.03e-6 m/s; invalid cmds 7.9e-3 m, 9.9e-6 m/s | cutoff limits (ignition precedes cutoff) |
| Thrust direction vs reference velocity, every burning sample | 1.3–1.5e-10; invalid cmds 1.15e-9 | O4 cutoff velocity limit / orbital speed: 4e-10; 2.6e-9 |
| Node-crossing time vs independently located crossings (DOP853 + Kepler bisection) | ≤ 4.0e-5 s | 8e-5 s (≈ 2× measured; the approved M1 node-crossing limit) |
| Completion altitude extrema vs reference extrema over every tick (both directions) | ≤ 6.3e-3 m (sample-only extrema would err by about 2 m) | 0.013 m (≈ 2× measured) |
| Per-sample propellant / sensed Δv vs prediction | ≤ 8.8e-17 / ≤ 5e-14 (relative) | 1e-12 |
| Coast-only missions vs DOP853 (empty tank, no propulsion) | 0.298 m, 3.49e-4 m/s | 0.6 m, 7e-4 m/s |

  - **Finding: high-thrust sensed-Δv error is RK4 (Simpson) truncation, not round-off.**
    - Sensed Δv obeys dv/dt = F/m(t), a function of time only, so RK4 reduces to Simpson's rule. Its error is h⁵/2880·f⁗ with f⁗ = 24·F·ṁ⁴/m⁵.
    - For the reference vehicle, the bound is 5e-13 m/s, far below the 1e-12 relative gate.
    - The O6 variants raise thrust up to 16×, so ṁ⁴ grows by 65 536×. Measured errors per level (×1 … ×16): 1.1e-14, 2.6e-13, 3.6e-12, 7.9e-12, 2.0e-11 relative. Against the analytic bound summed over the actual sub-steps, the ratios are 0.62, 0.97, 0.99, 0.98, 0.98.
    - The O2 and per-sample gates therefore apply the unchanged 1e-12 round-off allowance to the error in excess of this computed bound. The raw relative error is still reported.
    - This explains a mechanism; it does not loosen a tolerance. The reference missions' gate is unchanged in effect.
  - **O8 auxiliary runs** keep the mission's 60 s telemetry grid (only dt changes), so their samples are compared with the same reference. The final errors are unchanged: dt = 10 / 5 / 2.5 s gives 0.29034 / 0.014658 / 0.000809 m (orders 4.31, 4.18).

## VAL-0014 — T6: GMAT R2026a finite-burn references and O9 (provisional thresholds; reference host)
- **Date / revision:** 2026-10-11. References generated and verified on the reference host (macOS x86_64, GMAT R2026a, build Mar 26 2026). Code: `src/tars/validation/gmat_m2.py`, `toolbox/scripts/gmat_m2.py`. References: `toolbox/references/gmat/m2/`.
- **Purpose.** O9 (DR-0015): use an external, trusted tool as an independent physics reference for finite burns, generated with DR-0016 aligned stepping.
- **Configuration.** See the GMAT README M2 section.
  - The engine coefficients and g0 are pinned explicitly.
  - The arcs come from the commanded times (scenario inputs).
  - Steps are aligned: 60 s on coasts, 1 s during burns, one step on realignment arcs.
  - Missions: prograde, retrograde, invalid commands (three burns, two of them adjacent with opposite directions). Depletion is excluded (below).
- **Method.**
  - **Labels.** Rows are labelled from the step schedule, never from GMAT's epoch or `ElapsedSecs` columns (VAL-0010 M-a).
  - **Alignment verification.** Each reference is checked before storing and on every compare: row counts, step spacing, burn duration from mass, and coasts vs exact Kepler.
  - **GMAT vs independent references.** GMAT is compared with the independent-RHS DOP853 at every row, and its mass with the analytic mass law.
  - **The simulator vs GMAT.** Compared at every telemetry sample, at every ignition and cutoff (exact GMAT arc boundaries), in mass at every propulsion sample on a GMAT row (902 per mission), at node crossings (GMAT's located by Kepler bisection), and at 53 700 s.
- **Results (reference host):**

| Quantity | Prograde | Retrograde | Invalid cmds | Provisional limit (basis in `m2.json`) |
|---|---|---|---|---|
| Rows (aligned, counts exact) | 973 | 973 | 956 | exact |
| Step spacing from GMAT epoch | 2.3e-7 s | 2.3e-7 s | 2.3e-7 s | 1e-6 s (epoch resolution) |
| Burn duration from GMAT mass | 1.4e-10 s | 1.4e-10 s | 5.5e-11 s | 1e-9 s (≈ 2× VAL-0010) |
| GMAT coasts vs Kepler | 4.0e-6 m | 1.6e-6 m | 3.8e-6 m | 1e-4 m (approved M1) |
| GMAT vs DOP853, max over rows | 4.7e-6 m, 5.4e-9 m/s | 3.6e-6 m, 4.3e-9 m/s | 6.2e-7 m, 6.9e-10 m/s | 3e-5 m, 3.5e-8 m/s (2× the 15 µm DOP853 floor, FU-1) |
| GMAT mass vs mass law | 2.3e-11 kg | 2.3e-11 kg | 1.8e-11 kg | 1.3e-9 kg (O1 round-off class) |
| Ours vs GMAT, samples (max) | 0.291 m, 3.35e-4 m/s | 0.313 m, 3.64e-4 m/s | 0.297 m, 3.50e-4 m/s | 0.6 m, 7e-4 m/s |
| Ours vs GMAT, ignition/cutoff states | 7.7e-4 m, 1.2e-6 m/s | 7.8e-4 m, 1.2e-6 m/s | 8.0e-3 m, 1.0e-5 m/s | O4 cutoff limits (invalid cmds scoped) |
| Ours vs GMAT at 53 700 s | 0.290 m | 0.313 m | 0.297 m | 0.6 m |
| Ours vs GMAT, mass | 2.3e-11 kg | 2.3e-11 kg | 1.7e-11 kg | 1.3e-9 kg |
| Ours vs GMAT, node crossings | 3.2e-5 s | 4.0e-5 s | 3.3e-5 s | 8e-5 s |

- **Classification (as M1).**
  - Ours vs GMAT equals ours vs DOP853 (O4) to within micrometres. At 53 700 s: 0.2903419 m vs 0.2903434 m (slice), 0.3127435 m vs 0.3127443 m (retrograde), 0.2972918 m vs 0.2972946 m (invalid commands). The 0.7–2.8 µm differences match GMAT vs DOP853.
  - GMAT vs DOP853 is 5 orders of magnitude smaller.
  - So the simulator's difference from GMAT is its own RK4 truncation error (VAL-0012), not a modelling disagreement. The burn itself (ignition and cutoff states) contributes about 1 mm.
- **Discrepancies and uncertainty.**
  - **Aligned stepping is better here than in REV-012.** GMAT vs DOP853 is 0.6–4.7 µm, against 12 µm measured on the REV-012 aligned case. The T6 schedule realigns to the 60 s grid after each cutoff (REV-012 coasted 53 022.7 s from the cutoff), so the comparison points differ. Either way, the value is at or below the DOP853 reference's own cross-platform floor (11–15 µm, VAL-0010 addendum). It bounds GMAT's disagreement rather than measuring it, and the gate is set from the floor, not from these values (FU-1).
  - **Epoch column.** It carries per-command re-rounding (M-a). It is used for spacing verification (resolution about 3e-7 s per value) and for the epoch anchor: the first row's A.1 MJD must equal the configured TT epoch converted to A.1 (TT − A.1 = 32.184 − 0.0343817 s) within 1 µs (review M2-T6 F46). It never labels rows.
  - **Mass.** GMAT and our mass agree to 2e-11 kg, the round-off level of 1300 kg. GMAT's burn duration inferred from mass agrees to 1.4e-10 s; DR-0016's aligned stepping removed the 1.85e-7 s VAL-0009 shortfall.
  - **The DR-0017 timing bound is not involved.** O9 measures trajectory, mass and timing differences against GMAT. It does not use, and is not bounded by, the DR-0017 per-burn timing Δv quantity.
  - **DR-0018 is not exercised.** The GMAT missions all stop after their burns, so no burn crosses the observation stop.
- **Depletion.**
  - GMAT cannot propagate a burn to exact depletion with `AllowNegativeFuelMass = false`. Its stop-condition step overshoots and the tank reaches −0.0064 kg, so GMAT throws.
  - This is the known VAL-0009 finding 4. Depletion is validated analytically (O1, O2, D1a).
- **Reproducibility.**
  - GMAT re-runs reproduce every report byte for byte.
  - A replacement before review (header comment reworded) left the reports byte-identical.
- **Negative and mutation tests** (`tests/test_gmat_m2.py`).
  - **Rejected references:** a tampered report, g0 = 9.81, a C1 change, K3 ≠ 0, a changed Accuracy, wrong metadata constants, a missing row, an unaligned step, and a 1 mm GMAT state or 1 mg GMAT mass error (caught by the independent references).
  - **Simulator mutants that fail O9:** thrust × (1 + 1e-5), g0 = 9.81, frozen pointing, swapped retrograde direction, cutoff timing × (1 + 1e-9).
  - **Each O9 check disabled in turn makes a test fail.** As first written, this claim was false for the coast-vs-Kepler gate (review M2-T6 F7). It is now verified by a harness over all gated O9 metrics (15 at the time; 16 since review F36 added the coast velocity gate) and the F1/F3/F5/F6 checks, each with its own targeted test.
- **Cross-platform (CI, `805d789`).** The committed GMAT reports are identical everywhere; only our simulator and the DOP853 reference vary by platform.

  | Platform | GMAT vs DOP853 (max, prograde / retrograde / invalid cmds) | Ours vs GMAT at 53 700 s, prograde |
  |---|---|---|
  | Reference host (macOS x86_64) | 4.7 / 3.6 / 0.6 µm | 0.2903419 m |
  | ubuntu-latest x86_64 | 3.0 / 2.2 / 3.4 µm | 0.290346 m |
  | macos-latest arm64 | 5.7 / 2.0 / 5.5 µm | 0.290349 m |

  All values are within the 30 µm provisional limit, which is set from the DOP853 floor, not from these values (FU-1). The T7 measurement will formalize this.
- **Provenance (review M2-T6 F3).** Each reference must have:
  - the approved GMAT binary digest;
  - a successful console log bound by its hash;
  - complete metadata;
  - an entry in the approved-digest manifest.

  These controls detect silent or accidental substitution, including of metadata.
  - **Manifest history.** It is a validated hash chain covering all four generations, and the manifest digest is pinned in reviewed source. Edits, insertions, reordering, deletions and wholesale rewrites are all rejected (reviews M2-T6 F14, F32).
  - **Thresholds.** The threshold files are authenticated by pinned digests (F33).
  - **References.** Every independent-reference state (DOP853 terminal and dense output, Kepler) is validated in full, including the reference propellant against the mass law (F29–F31).
  - **Origin.** None of these controls proves GMAT origin against deliberate fabrication.
- **Reproduction.** The reproduction test authenticates the executable (approved sha256) and its success marker, and requires byte-identical reports. That is authenticated, independent reproducibility evidence. It does not by itself prove the historical origin of stored bytes (review M2-T6 F10).
- **Classification:** no discrepancy. **Status:** provisional Proof evidence (T6); thresholds remain provisional until the T7 three-platform measurement and threshold DR.
- **T5 corrections made during T6 review (documented, tested, independently reviewed in M2-T6-review-01).**
  - NaN-safe reductions (`worst`) in O4 and O5, plus rejection of non-finite reference states (F16).
  - Exact threshold-file structure and finite, nonnegative limits in both loaders (F15, F17).
  - A distinct name for the orbit-event contract check.
  - No gate, limit or measured value changed: the 212 Proof metric values are bit-identical before and after.
- **Scope of the false-pass review (DR-0019 B, approved 2026-10-11).**
  - **Covered:** wrong simulator output or physics; tampered references or thresholds; workflow failures; invalid reference outputs; missing observations or thresholds; non-finite metrics.
  - **Not covered at runtime:** replacing the validator's own helper code, which code review, mutation tests and the AST guard cover instead.
  - Bad data passing through unmodified helpers stays in scope.
- **DR-0020 (approved A with conditions, 2026-10-11).**
  - A reference-output corruption is blocking when it could affect a check, a reported value, an acceptance decision or a required physical invariant.
  - F42 and F43 are accepted residual risk: corruptions of unused or invariant-preserving reference internals.
  - Currently unused intermediates (listed in the review record) must be validated before anything relies on them.
- **Reference anchoring (review M2-T6 F47, F48).**
  - The altitude extrema now use tick radii from independent anchors: exact Kepler from each coast segment's start, and an in-validator fixed-step RK4 during burns. They no longer use the DOP853 dense output.
  - Every DOP853 segment end must agree with its anchor:
    - coasts: ≤ 1e-7 m and 1e-10 m/s (measured 2.9e-9 m and 2.9e-12 m/s);
    - burns: ≤ 1e-6 m, 1e-9 m/s and 1e-9 kg (measured 3.8e-8 m, 1.1e-10 m/s and 1.5e-10 kg).
  - Every tolerance comparison requires finite operands.
  - The extrema metrics moved by at most 2e-8 m.
  - Every consumed anchor tick must also agree with the validated DOP853 dense output at that tick, with the same limits (review F49; measured ≤ 2.8e-8 m). An extremum moves only if both independent references are corrupted consistently.


## VAL-0015 — DR-0021: approved reference snapshot, coverage and reproducibility tolerances (M2; T6)
- **Date / revision:** 2026-10-12.
  - Baseline 1: generated at `ad1c33b` (clean tree), pinned at `c753372`.
  - Baseline 2: generated at `ad74f91`, pinned at `f5a7e40`. It adds the inputs of the sim-seeded and closed-form values (review F53).
  - **Baseline 3 (current):** generated at `58be803` (clean tree), pinned at `9d49b60`. It adds the reference marks, so that node crossings can be enumerated independently (review F55).
  - Tolerances were set after the measurement below.
- **Purpose:** DR-0021 option A. Every reference-derived value of the M2 Proof is verified against an approved, digest-pinned snapshot, so coordinated corruption of several independent references (review F50, F51) is detected.
- **Mechanism (`tars.validation.reference_snapshot`).**
  - Each reference oracle passes its outputs through `pin(label, seed, **parts)`. Keys are scope (scenario, consumer), label and call counter; part names carry their unit.
  - Verify sessions are opened by the M2 Proof (`m2_proof`) and by each GMAT M2 evaluation (`gmat_m2:<mission>`, used by `compare` and `run`). The artifact is authenticated by its pinned sha256 before use.
  - A value that is missing, unexpected, non-finite, changed in kind or shape, or outside its tolerance is a problem, and the exact check `reference_snapshot` fails, or the GMAT evaluation is rejected. Coverage is complete: every approved value of the entrypoint must be reproduced.
  - **Consumption.**
    - Seeds `ref` (scenario inputs only) and `gmat` (committed GMAT rows): once a value agrees, the check consumes the *approved* value. A within-tolerance deviation therefore changes no metric and cannot alter an acceptance decision.
    - Seed `sim` (Kepler states seeded by simulator output: O5, O6): verified but not substituted. The exact check `reference_snapshot_margins` requires every gated metric built on them to pass by more than the worst shift a within-tolerance deviation could cause (O5: √3 × the per-component tolerance, because its metrics are Euclidean norms, review F52; O6: corner bounds on the scalar impulsive SMA in `m2.o6_snapshot_shifts`).
  - `exact` values (evaluation-time grids, the decimal O3 closed form, the GMAT epoch anchor) must match bit for bit.
- **Coverage inventory (pinned).**

| Label | Seed | Values | Consumed by |
|---|---|---|---|
| `initial_state` | ref | r, v from the elements | O4 initial state, DOP853 seed, GMAT script |
| `predicted_burns` | ref | ignition, commanded, intended, cutoff, executed times; propellant before/used/after; mass before/after; Δv | O1, O2, accounting and receipts, lifecycle, segment bounds, GMAT arcs |
| `simpson_bound`, `timing_bound` | ref | RK4 truncation bound with its window; DR-0017 timing bound with its durations and propellant | O2 and sample excess metrics; receipt check |
| `dop853.marks`, `dop853.bounds`, `dop853.ticks` | ref, exact | the reference's mark times; segment bounds; tick index range and dt (the grid is checked to be k·dt bit for bit) | every evaluation time |
| `dop853.start`, `dop853.segment` | ref | start state; each segment end (r, v, propellant); anchor (Kepler or RK4) positions at every tick; anchor end state | marks for O4, O8 and O9; node bisection seeds; altitude extrema |
| `dop853.extrema` | ref | min and max reference altitude | orbit_events extrema metrics |
| `orbit.node_crossings` | ref | timed crossings; powered-interval count | node crossing error, crossing count |
| `o5.kepler` | sim | arc seed state and flight times; Kepler r, v at every coast sample | O5 |
| `o6.delta_v`, `o6.midpoint` | ref, sim | impulsive Δv; ignition seed state, flight time, midpoint r, v and impulsive SMA | O6 |
| `o3.closed_form`, `o3.expected_cutoff` | ref, exact | decimal Δv and displacement; expected cutoff v, r, propellant with the start state and duration | O3 |
| `o9.arcs`, `o9.label_times`, `o9.epoch_anchor` | ref, exact | arc schedule; row labels; configured A.1 epoch | O9 alignment, labelling, epoch anchor |
| `o9.expected_mass` | ref | analytic mass at every GMAT row | `gmat_mass_vs_analytic_error_max_kg` |
| `o9.alignment_kepler`, `o9.gmat_node_crossings` | gmat | Kepler states from GMAT arc starts; GMAT node crossings | O9 alignment; ours-vs-GMAT node error |

  Baseline 3: 48,310 records, 982,324 values (gzip JSON). Every value common to baselines 1, 2 and 3 is bit-identical.
- **Excluded (explicitly), with reason.**
  1. *DOP853 dense output at the ticks.* The positions are consumed only by the F49 check, which requires them to agree with the pinned anchor tick positions (≤ 1e-7 m on coasts, 1e-6 m in burns), so they are pinned transitively. Velocity and propellant feed only self-consistency checks. Storing them would add 534k values.
  2. *DOP853 interior solver nodes, stencil and midpoint samples.* Their number follows the adaptive step selection, which can differ by platform. They feed only the self-consistency checks (node reconciliation, derivative stencil, mass law), which remain.
  3. *Internal states of `kepler_state`* (round trip, invariants): validation of an output that is itself pinned.
  4. *Per-iteration bisection states*: only their sign steers the bisection; the resulting crossing times are pinned.
  5. *Bookkeeping identities on simulator output* (total = dry + propellant, F/m with the reported mass, the rocket equation on reported masses, unit vectors): the expected side is a function of the same run's reported values and scenario constants, not a reference oracle output.
  6. *Simulator output* (never truth) and *GMAT rows* (pinned by the GMAT manifest digest).
  7. *M1 references*: M1 is approved and closed; DR-0021 concerns M2.
- **Tolerance measurement (condition 4).**
  - **Method.** `reference_snapshot.py measure-deviation` runs the Proof and the three GMAT evaluations in *verify* mode against baseline 1 with unlimited tolerances, so substitution happens exactly as in a real run. It reports the largest |runtime − approved| per class.
  - This is the right quantity. Without substitution, record-mode drift accumulates along the DOP853 chain: up to 6.8 µm between platforms, consistent with the 11–15 µm cross-platform floor of VAL-0010. With substitution, each segment starts from its approved state.
  - **Environments (24 measurements):**
    - the reference host (macOS x86_64, i9-9880H): every class 0;
    - GitHub `ubuntu-latest` on eight hosts: EPYC 7763 twice, Xeon Platinum twice, EPYC 9V74 twice, EPYC 9V45, and one more EPYC 9V74;
    - GitHub `macos-latest` on eight hosts (Apple M1).

    Workflow `reference-snapshot-measure`: tags `refsnap-measure-2` to `-5` against baseline 1, `-6` to `-9` against baseline 2, and `-10` to `-13` against baseline 3 (7 more hosts). The maxima are identical by class in every set; the flight-time and mark parts are exact everywhere. Same `uv.lock`: NumPy 2.5.3, SciPy 1.18.1.
  - **Rule (review F59).** The smallest 1-2-5 value ≥ max(10 × the largest measured deviation, 10 ulp of the class's largest value in the approved snapshot). Counts are exact. Unused classes are exact, so they fail closed. The measured maxima are recorded in `reference_snapshot.MEASURED`; a test recomputes the rule from the artifact.
  - The factor 10 covers runner hardware not sampled: the AVX-512 hosts alone raised the GMAT-seeded Kepler class 36×. The tolerance size only trades false alarms against sensitivity, because the acceptance guarantee comes from substitution and from the margin check, not from the size of the tolerance. The GMAT comparison tolerance is not used.

| Class | Measured max | Tolerance |
|---|---|---|
| ref m | 2.79e-9 | 5e-8 |
| ref m/s | 4.09e-12 | 5e-11 |
| ref kg | 1.14e-13 | 5e-12 (10 ulp of 1,300 kg) |
| ref s | 0 | 1e-10 (10 ulp of 53,100 s) |
| ref count | 0 | 0 (exact) |
| gmat m | 2.02e-7 (AVX-512 hosts) | 5e-6 |
| gmat m/s | 2.52e-10 | 5e-9 |
| gmat s | 0 | 1e-10 |
| sim m | 5.37e-7 | 1e-5 |
| sim m/s | 6.59e-10 | 1e-8 |
| sim s (O5/O6 flight times) | 0 | 1e-10 (10 ulp of 53,700 s) |
| exact values | bit-identical on every host | 0 |

- **Margins for the sim-seeded gates (baseline report).**
  - **O5:** 0.314 m against a 0.6 m limit (shift bound √3 × 1e-5 = 1.7e-5 m); 3.6e-4 m/s against 7e-4 m/s (shift bound 1.7e-8 m/s).
  - **O6 order deviation**, per mission: prograde 0.0041 + 0.0356 = 0.0397, retrograde 0.0039 + 0.0366 = 0.0405, against 0.05. Corrected in T7 (review T7-F4); the T7 worst over 11 bundles is 0.039703 and 0.040493.
  - **O6 slice ratio:** 2.6e-6 + 2.0e-10 against 1e-5.
  - The O6 order bound is conservative, because the sim length tolerance is set by O5's long Kepler arcs. If T7 tightens that O6 limit below about 0.041, the impulsive SMA needs its own measured class.
- **Detection (regression tests, `tests/test_reference_snapshot.py`).**
  - **F50:** Kepler anchor ticks and DOP853 dense positions are corrupted consistently at 1.001 × the flight time. Every runtime check passes and the extremum moves; `_evaluate` rejects it through the snapshot, while the same simulator data is rejected on its limit with clean references.
  - **F51:** O6 Kepler at 10 × the flight time, forward and in the round trip, is rejected.
  - **Coordinated shift:** both references raised by 1 cm at every interior tick pass every runtime check and are rejected.
  - **Tampering:** a tampered, missing or malformed artifact; out-of-tolerance, non-finite, unexpected, missing or changed-kind values; incomplete coverage.
- **Baseline approval evidence (condition 2; review F53).**
  - The recording run passed the M2 Proof (213 checks and the 2 snapshot checks) and the three GMAT evaluations. That alone is not enough: a corruption present while recording can pass the recording Proof (F53).
  - `verify-baseline` checks the candidate as follows (F54–F56):
    - **Inventory.** It compares the candidate with a **fresh recording** of the reviewed code. Records, counters, entrypoints, part names and shapes must match exactly.
    - **Inputs.** The input parts (marks, O5 and O6 seeds and flight times, Simpson windows, DR-0017 inputs, O3 start and duration) come from the simulator and the scenario, never from a reference. They must agree with the fresh recording's within their class's reproducibility tolerance: bit-identical on the generating host, and exact for exact records (the marks and the O3 inputs). O5 and O6 flight times use the continuous `sim s` tolerance (1e-10 s); they were bit-identical in every measurement.
    - **Outputs.** Every output part is recomputed from its inputs and the scenario, with implementations independent of the runtime references.
    - **Coverage.** It is tracked per part. An unverified part, or a record that cannot be evaluated, is a failure.

| Values | Independent recomputation | Limit | Measured agreement |
|---|---|---|---|
| Coast segment ends, anchor ticks and ends | universal-variable Kepler (Curtis Alg. 3.3–3.4, written in the tool) | 1e-6 m, 2e-9 m/s | 2.8e-9 m, 3.3e-12 m/s |
| O5 and O6 Kepler states; GMAT alignment states | the same, from the pinned seed (GMAT arc-start row) | 1e-6 m, 2e-9 m/s | 2.9e-7 m, 4.1e-10 m/s (longest arcs) |
| Burn segments | ODEPACK LSODA (`odeint`) with its own equations of motion; propellant on the mass law | 1e-5 m, 1e-8 m/s, 1e-9 kg | 6.5e-7 m, 1.1e-9 m/s |
| Node crossings (reference, GMAT) | independently **enumerated** over the marks (GMAT rows): count, order, powered intervals, times by bisection on the independent Kepler | 1e-6 s | exact |
| Initial state | `tars.astro.elements` (not the validator's formula) | 1e-12 relative | exact |
| Predicted burns, Simpson and DR-0017 bounds, O6 Δv and SMA, O9 expected mass, epoch, arcs with steps, row labels, tick grids, and segment bounds from the marks | re-derived from the scenario | exact or 1e-12 relative | exact |
| O3 closed form | 40-digit decimal in a separate form | 1e-12 relative | ≤ 1e-15 |

  - DOP853 against the committed GMAT rows: at most 4.66e-6 m and 5.39e-9 m/s (O9 gates 3e-5 m, 3.5e-8 m/s). Coast energy is conserved to 1e-11, and the extrema equal the pinned ticks' extrema.
  - **Regression tests:**
    - a recording made under F51's 10× flight time, self-consistent in state and SMA, is rejected;
    - zeroed O6 values with an SMA of −1e30 m are rejected;
    - a recording made under F50's coordinated corruption is rejected;
    - each of 11 single corrupted value kinds is rejected;
    - an uncovered record is rejected;
    - unreadable records fail closed.

    Disabling each verifier check fails its tests.
  - Agreement with the snapshot is not evidence of physical correctness: that rests on these checks.
- **Run safeguards (DR-0022 B).**
  - At the end of every verification run, the in-memory ledger is re-hashed against its load-time hash. The artifact file is re-hashed against the bytes loaded and against the pinned digest.
  - The M2 Proof and every GMAT comparison must have run a verification session, in verify mode, that compared values.
  - Any failure fails closed.
  - These catch accidental corruption and wrong execution state, not deliberate in-memory tampering, which is outside the threat model (DR-0019 B, DR-0022; review F58).
- **Status:** M2 thresholds remain provisional (T7). The tolerances are reproducibility limits, not Proof thresholds.

## VAL-0016 — T7: three-platform measurement for the M2 threshold decision (DR-0015 method; DR-0008 precedent)
- **Date / revision:** 2026-10-13, `2870392`. Every bundle comes from a clean tree with identical input digests (scenarios, `m1.json`, `m2.json`, reference snapshot baseline 3, GMAT manifest, `uv.lock`).
- **Method.** `toolbox/scripts/m2_t7_measure.py collect` runs on each platform and records:
  - the environment, with digests of every input and output and the exact commands;
  - the full M2 Proof, verified against the reference snapshot;
  - cross-process determinism of the four M2 scenario files and of M1 (the Proof also replays all six missions in process);
  - every mission's final state;
  - M1 cross-platform agreement;
  - reference variation, measured two ways: verify mode (`measure-deviation`) and record mode (raw values, no substitution).

  `analyze` aggregates the bundles. Evidence: `proof/records/evidence/M2-T7/`.
- **Platforms (the DR-0008 matrix), 11 bundles:**
  - macOS x86_64 reference host (i9-9880H; NumPy SIMD X86_V3; Accelerate);
  - Linux x86_64, GitHub `ubuntu-latest`, five runs on four CPU types: EPYC 7763 (X86_V3, no AVX-512), Xeon Platinum 8573, EPYC 9V74 twice and EPYC 9V45 (AVX-512);
  - macOS arm64, GitHub `macos-latest`, five runs on Apple M1.

  All use Python 3.12, NumPy 2.5.3 and SciPy 1.18.1 from the same `uv.lock`.
- **Results:**
  - **Proof:** the M2 Proof passes 215/215 on all 11.
  - **Determinism:** byte-identical on all 11: cross-process for the four M2 scenario files and M1, and in process for all six missions, including the two generated variants (review T7-F6).
  - **M1:** cross-platform |Δr| is at most 2.9e-6 m (unchanged, within the approved 1e-4 m).
  - **Simulator, cross-platform:** M2 final states drift by at most 7.2e-6 m and 8.4e-9 m/s (prograde slice). Coast-only missions drift 2.9e-6 m, so the burn amplifies the drift about 2.5×. Event logs are not bit-identical across platforms, as DR-0006 expects.
  - **Gated metrics** (review T7-F5):
    - largest cross-platform spread of any check: 1.1e-5 m (O4 and O5 at 53,700 s); simulator vs GMAT 7.2e-6 m;
    - O8 order spread: 1e-3;
    - every O9 GMAT-vs-reference metric and every scenario-only metric: zero spread;
    - round-off-class metrics: at most 3.3e-16.
  - **Reference variation, record mode** (raw DOP853, no substitution): up to 8.62e-6 m and 1.01e-8 m/s as vector norms (largest components 8.10e-6 m and 9.9e-9 m/s), which is the FU-1 floor re-measured. Kepler from GMAT rows: 2.1e-7 m. Node crossings: 8.5e-10 s.
  - **Reference variation, verify mode** (with substitution, as the Proof runs): reference values 2.8e-9 m and 4.1e-12 m/s; GMAT-seeded 2.0e-7 m; simulator-seeded 5.4e-7 m. All within the DR-0021 tolerances.
  - **O6 impulsive SMA:** cross-platform variation 1.9e-9 m.
- **Error attribution:**
  - **Simulator integration error** (RK4, dt = 10 s): 0.29–0.31 m at 53,700 s; ≤ 8e-3 m at burn boundaries; O8 orders 4.14–4.33.
  - **Reference disagreement:** the committed GMAT rows and the approved DOP853 baseline differ by 4.66e-6 m. That shows two independent methods are consistent; it does not bound either one's absolute error (review T7-F1). The reference's platform drift (8.62e-6 m) is removed from the verdict by the snapshot (≤ 5e-8 m in verify mode).
  - **Simulator platform drift:** ≤ 1.1e-5 m in any metric.
  - **Round-off-class metrics:** ≤ 7.5e-14 relative.

  Platform variation of compared quantities (≤ 1.1e-5 m) and the reference disagreement (4.66e-6 m) are more than four orders of magnitude below the simulator error (0.31 m) and below every margin. They describe reproducibility and consistency, not the references' absolute accuracy.
- **Status:** a measurement, not approval. The threshold matrix and the recommendations are in DR-0023. No threshold, reference value or tolerance was changed.

## VAL-0017 — DR-0023 decision 4: M2 cross-platform final-state gate (three platforms, one revision)
- **Date / revision:** 2026-10-14. Evidence revision `27e5b8b`, the implementation commit, from a clean tree on every platform.
- **Method.** `toolbox/validators/m2_cross_platform.py collect` runs every canonical M2 mission (the six in `tars.validation.m2_missions`) and writes one evidence record. Each record carries:
  - the revision and whether the tree was clean;
  - the platform identity: OS, architecture, CPU, and Rosetta translation, which is rejected;
  - the environment, including the `uv.lock` digest;
  - CI provenance: run id, commit and runner architecture, cross-checked against the machine;
  - the canonical input digest (scenario config hash) of every mission;
  - every final state, status, tick, time and event-log digest;
  - a record digest.

  `gate` validates every record and requires all three DR-0008 platforms. It compares every pair of records for every mission as Euclidean |Δr| and |Δv|; status, final tick and final time must agree exactly. It fails closed: a missing, unreadable, corrupted, inconsistent or stale record gives +inf and a violation.
- **Platforms:**
  - macOS x86_64 reference host (i9-9880H, local);
  - GitHub push run 38629384726: `ubuntu-latest` (AMD EPYC 9V74), `macos-latest` (Apple M1) and `macos-15-intel` (i7-8700B).
- **Results (four records, six missions, all pairs):** at most **7.23e-6 m and 8.43e-9 m/s** (prograde slice), against limits of 1e-4 m and 1e-7 m/s. Margins are 13.8× and 11.9×.

  | Mission | Worst \|Δr\| (m) | Worst \|Δv\| (m/s) |
  |---|---|---|
  | prograde | 7.23e-6 | 8.43e-9 |
  | retrograde | 5.55e-6 | 6.44e-9 |
  | burn to depletion | 3.53e-6 | 3.97e-9 |
  | invalid commands | 4.75e-6 | 5.49e-9 |
  | invalid commands, empty tank | 3.76e-6 | 4.42e-9 |
  | invalid commands, no propulsion | 3.76e-6 | 4.42e-9 |

  - By platform pair, the arm64-vs-x86_64 pairs are the largest (7.23e-6 m), then Linux vs macOS x86_64 (5.55e-6 m), then Linux vs arm64 (3.76e-6 m).
  - The reference host and the GitHub Intel runner are **bit-identical** (Δ = 0) on every mission.
  - The reference-host record is also bit-identical to the T7 reference-host bundle at `2870392`: the same final states and the same event-log digests.
  - These match VAL-0016: 7.2e-6 m and 8.4e-9 m/s over 11 bundles.
- **Golden record.** `proof/references/m2_final_states.json` is the reference-host record. It is sha256-pinned in `approved_digests.APPROVED_M2_GOLDEN_SHA256` and identical, byte for byte, to the archived `reference-host.json`. The M2 Proof validates it and compares every mission on the running platform with it (13 checks; 228 in total).
- **Retention.** The records, the gate report and a manifest with their digests are committed in `proof/records/evidence/M2-T7/cross-platform/`. They no longer depend on the 90-day CI artifact expiry. `tests/test_m2_cross_platform.py` re-runs the gate on them, at their revision and against the current canonical inputs, so a scenario change makes the archive visibly stale.
- **CI.** Every `check` job collects its record from the clean checkout before anything else. The `m2-cross-platform` job gates the three records of the same workflow run, using `--revision ${{ github.sha }}` and `--run-id ${{ github.run_id }}`.
- **What it does not detect.** The record digest detects corruption and accidental edits. It does not authenticate a deliberately forged record (DR-0019 B; DR-0022 B condition 1). CI records are produced and consumed within one run, and the golden is pinned by a reviewed digest.
- **Status:** gate implemented under DR-0023 decision 4. No existing threshold, reference, tolerance or check was changed.


## VAL-0018 — PLANNING: candidate J2 and drag physics; GMAT feasibility (M3; not a gate)
- **Date:** 2026-10-15
- **Revision:** branch `milestone-3-planning`. The production code is identical to the M3 planning baseline `main` = `d92ab89`.
- **Purpose:** measure what the M3 Decision Requests (DR-0024 G1, DR-0025 G2, DR-0026 G3) need before any model, threshold or design is chosen.
- **Code:** candidate physics written independently in `docs/science/experiments/m3-planning/`. It is not project code, and no production force model exists for M3.
- **Configuration:**
  - M1 initial state, 53 700 s;
  - WGS 84 GM and a;
  - J2 = 1.0826261739e-3 (EGM2008 tide-free C̄2,0 from NGA.STND.0036 Table 5.1), about the frame z axis;
  - GMAT R2026a's piecewise-exponential atmosphere table, spherical or geodetic height;
  - atmosphere co-rotating at ω_E = 7.292115e-5 rad/s;
  - illustrative B = m/(C_d A) = 25.8 and 100 kg/m².
- **References:**
  - SciPy DOP853 (rtol 1e-13);
  - first-order J2 secular theory;
  - first-order drag decay estimate;
  - GMAT R2026a (build Mar 26 2026), with a generated `.cof`, the `Exponential` atmosphere, and states in EarthMJ2000Eq or in true-of-epoch (TOEEq) axes fixed at the epoch.
- **Results (full tables in the experiment README and JSON):**
  - **RK4 dt = 10 s vs DOP853:** J2 0.30 m; drag (B 25.8) 4.6 m; J2 + drag 2.1 m (B 25.8) / 0.70 m (B 100).
  - **Convergence:** J2 error ratios 22.4 / 20.0 / 18.3. Drag-only ratios 10.4 / 9.0 / 13.6: the literal density table has finite value jumps (≤ 1.4e-3 relative, from rounding) and scale-height changes at band edges.
  - **Displacement from point mass after 10 orbits:** J2 741 km (matching GMAT's 741 km in VAL-0007); drag 363 km; both 1 161 km.
  - **J2 node rate:** fitted −5.4385 °/day against first-order −5.4099 °/day (+0.53%, osculating a₀).
  - **Drag decay:** −12.8 km/day (B 25.8), −3.05 km/day (B 100). The first-order fixed-density estimate is off by 11% / 2.6%.
  - **GMAT:**
    - its gravity field uses the `.cof` GM, not `Earth.Mu`, and its default flattening is not WGS 84;
    - fixed-pole models against GMAT in EarthMJ2000Eq axes: 123.5 m (J2), 1.38 m (drag, spherical), 4.33 m (drag, geodetic);
    - **in TOEEq axes: 0.19 m (J2), 0.0020 m (drag, spherical), 0.38 m (drag, geodetic, WGS 84 flattening).**
  - **Sensitivities (Δ final position):**
    - J2 tide-free vs zero-tide 6.7 m;
    - GM TT vs TCG value 0.63 m;
    - J2 axis tilted by the 2026 precession angle 117 m;
    - geodetic vs spherical height 74 km;
    - non-rotating atmosphere 40 km;
    - B +1% 4.8 km.
- **Classification:** planning measurements of candidate physics. They show which choices are physically material and that GMAT can serve as an exact-configuration reference for a fixed-pole model in TOEEq axes. They do not validate any implementation.
- **Status:** informational; no gate; no threshold derived.
- **Observation on earlier records (not edited):** the VAL-0007 informational GMAT runs used the JGM-3 coefficient-file GM (3.986004415e14) and R (6378136.3 m), not their `Earth.Mu` override. The effect (~0.6 m) is negligible against those runs' 741–1 325 km results (DR-0025 §13).

## VAL-0019 — M3 T0: reference-configuration spike (J2, drag, atmosphere boundaries, geodetic height, frames; not a gate)
- **Date:** 2026-10-18. **Corrected after Review 01** (M3T0-F1 … F4; log at the end of this record).
- **Authority:** "TARS — M3 T0 Reference-Configuration Spike Authorization" (Tech Lead, I-15), T0 only.
- **Revision:** branch `milestone-3-t0-reference-spike`, from `main` = `86df2c3` (PR #4 merge commit). No production file is changed: `src/`, `proof/`, `toolbox/`, `scenarios/` and `.github/` are identical to `86df2c3`.
- **Code:** `docs/science/experiments/m3-t0/` (README there lists commands, versions and digests).
  - An independent spike model of the approved M3 physics (DR-0024 Resolution; DR-0027 B-1 table by digest; DR-0028 J-ax-1).
  - GMAT R2026a exact configurations generated by an additive splice of the committed M1/M2 generators.
- **References:**
  - SciPy DOP853 (rtol 1e-13; converged to µm);
  - GMAT R2026a (build Mar 26 2026; console sha256 `1162803d…`; EOP file `52c95d68…`), PrinceDormand78 at accuracy 1e-13, states exchanged in TOEEq fixed at the epoch;
  - analytic known answers (geodetic height, stiffness, crossing bounds);
  - GeographicLib CartConvert(1) published examples.
- **Results (spike inputs: C_d 2.2, A 15 m², m 850 kg unless noted; 53 700 s):**
  - **Regression, perturbations off:**
    - the T0 splice reproduces the committed M1 and all three M2 GMAT scripts byte for byte, and GMAT re-running them reproduces the committed reports byte for byte;
    - the M3 exact-configuration form passes every approved M1 GMAT gate (GMAT vs Kepler 6.95e-6 m, limit 1e-4 m);
    - the spike's RK4 equals the M1 golden final state bitwise on the reference host.
  - **GMAT exact configurations against the J-ax-1 spike (final / maximum position difference):**

    | Configuration | Final / maximum |
    |---|---|
    | J2 | 0.192 / 1.03 m |
    | One-band spherical drag | 2.05 mm |
    | Full-table spherical drag | 1.98 mm |
    | Full-table geodetic drag | 0.327 m |
    | J2 + drag, i 51.6° | 0.199 / 1.08 m |
    | J2 + drag, i 97° | 0.583 / 0.70 m |
    | J2 + drag, 250 × 800 km | 0.237 / 0.86 m |
    | J2 + drag + M2 burn | 0.240 / 0.94 m (mass 2.9e-9 kg) |
    | Decay stop at geodetic 80 km (spike test value) | GMAT 0.023 s earlier than the spike |

  - **J-ax-1 residual attributed:**
    - GMAT's Earth-fixed +Z, recovered in TOE axes from two non-coplanar orbits, circles the celestial pole once per sidereal day with radius 0.349″ (polar motion from GMAT's EOP data; fit residual 0.08 mm).
    - Driving the spike with that axis (a diagnostic, not the M3 model) reduces the J2 difference to **0.076 mm**, provided `Earth.NutationUpdateInterval` = 0. GMAT's default of 60 s leaves 8 cm along-track.
  - **Geodetic drag, not attributed:**
    - With the default interval, the axis and GMAT's 1e-7 rad height rule explain the difference to 4.2 mm.
    - With interval 0, 0.137 m remains.
    - The GMAT result also depends on how the run is segmented into `Propagate` commands: 0.383 m for one command (the planning probe, rerun and reproduced byte for byte), 0.186 m for 895 × 60 s commands. ESCALATED_FOR_INVESTIGATION (DR-0029 P6).
  - **Planning measurements (VAL-0018) reproduced:**
    - the planning GMAT probe reruns byte-identically, and `perturbation_experiment.py` reruns identically in every value except its `runtime_s` field (both rerun in a scratch copy on 2026-10-18; no planning file changed);
    - T0's own configuration gives J2 0.192 m (planning 0.189 m) and spherical drag 2.0 mm (planning 2.0 mm);
    - geodetic drag differs (above).
  - **Atmosphere table:**
    - 27 boundaries; largest value jump +1.36e-3 at 25 km, all others ≤ 9.6e-5; log-slope changes up to −32 %;
    - GMAT's band rule (h ≥ base selects that band) and density agree with the spike at ±1 km of every boundary to the probe bias (1.43e-7);
    - GMAT extrapolates the top band above 1000 km;
    - **GMAT fails closed below geodetic 0** ("Position vector is inside central body");
    - converting km ↔ m never moves a boundary;
    - the M1 orbit's 250 km altitude is exactly a band base (GMAT computes 249.9999999999982 km), so geodetic-height missions on it change band 29–39 times in 10 orbits.
  - **RK4 (dt = 10 s):**
    - linearised drag stiffness (circular-speed proxy) reaches RK4's stability limit below 51 244.55 m (B 25.8) and 40 881.39 m (B 100); exact thresholds for κ = 2.785, 1, 0.1 and 0.01, with the proxy and with a bound on |v_rel| valid for every bound state, are in `t0_termination_results.json` → `stiffness_thresholds` (the 5 km grid in `t0_atmosphere_results.json` understates them by up to 5 km);
    - in a 180 km decay the height error exceeds 100 m below 72 km, and RK4 diverges near 12 km;
    - one boundary crossing contributes an error visible only for dt ≤ 2.5 s (apparent order 4.0 from dt 20 to 5 s; 2.8 from 2.5 to 1.25 s; smooth control 3.9–4.0 throughout);
    - the third RK4 stage (the input of k3) sits about 117 m below the committed path in LEO; at the 180 km state the k2, k3 and k4 inputs sit at +116.31, −115.73 and +1.16 m from the initial height.
  - **Termination crossings:**
    - a cubic Hermite on h with dh/dt = n̂·v locates crossings to within the RK4 trajectory's own timing error (−0.07 … −0.41 s against DOP853); scalar and vector Hermite agree to 1.9e-4 s;
    - stopping at the first committed state is up to 9.3 s late and up to 3 km low;
    - missed dips (a trajectory dipping below the lower committed height inside a step):
      - 1.56 m at one fixed sampling phase (250 × 800 km), a measurement, not a bound;
      - with the lowest point at mid-step, 4.99 m (Kepler) and 4.82 m (J2 + drag) for 250 × 800 km, and 0.45 m for a circular 250 km, 51.6° orbit;
      - derived bound: dip ≤ (dt²/8) sup max(ḧ, 0), with ḧ ≤ n̂·a + |v_t|²/(h + b²/a). This gives 5.28 m, 5.11 m and 0.74 m in those three cases. Across 9 orbits, two-body and J2 + drag, and 40 sampling phases, it is never exceeded (smallest margin 0.025 m);
      - two-body bound at dt = 10 s: 0.74–0.80 m for circular orbits (perigee 80–250 km), 5.30–5.61 m for e = 0.04 (`t0_termination_results.json` → `missed_crossing`).
    - DR-0029 P1 (A4-b) admissibility is necessary, not sufficient:
      - a P1-admissible stress input puts an RK4 stage at −28 km, and its committed state satisfies `reentry` and `impact` on the same tick;
      - the circular-speed proxy underestimates λ for an e = 0.9 retrograde perigee (λ dt 0.0144 at κ 0.01);
      - a derived sufficient condition for every stage to stay above 0 km at dt = 10 s is h_f ≥ 111.5 km drag-free, 118.6 km at B 100 and 124.5 km at B 25.8, for unrestricted bound states (`t0_termination_results.json`).
  - **Geodetic height:**
    - iterative and Vermeille (2002) inverses reproduce 640 forward-constructed points to ≤ 3e-9 m;
    - the GeographicLib examples agree within their 1 cm print rounding;
    - GMAT's conversion is within 1.3 mm at mid-latitudes and fails exactly on the axis;
    - points inside the evolute (deep inside the Earth) are outside both algorithms' domain.
  - **Frames (spike level):**
    - FC-2, FC-3 (J2 axisymmetry to 9.4e-16 relative), FC-5 and FC-6 hold;
    - FC-8: v_rel departs from v by up to 2.9° at 51.6° and is parallel to v at the highest-latitude point, so a FC-8 test must not sample only there.
- **Spike digests (sha256, as committed with this record):**
  - `t0_atmosphere.py` `cccb0efe7f74810004cc2ca6ee80815c979698fa4cee2e107318e6dac0e53cad`
  - `t0_decay.py` `0b0512f9b349e35bf20d3352c36d083f642fc073033278f3993321d9e2a43415` (corrected after Review 01; was `9d206145…7260`)
  - `t0_frames.py` `aa6a0997da255b7fb24a192c1d35be52fed48b483b49be3ca19981815633b2ec`
  - `t0_geodetic.py` `0e7a4044027ee3bf07f10c9176543959022ad2cfb2c7b157d880e3f40ee18d30`
  - `t0_gmat.py` `204d47c12fd4b7311fc056f894001f6c84bc827818456c23c461664d1a533e23`
  - `t0_model.py` `1d70e86c25546a91365a5ed101ad0d390bc9e507862ca4eacbfa78fe2160b09d`
  - `t0_regression.py` `06ac4c0bdf82aa442a111fc380cf94457322e37a2aae72384afda3cfe93f413c`
  - `t0_termination.py` `2cb1a0383e917c1a0fd341f7f55dcf0331d02c61a658572c4a2ba29dbc47aa0a` (added after Review 01)
  - `check_review01.py` `6e40cd618d915be4f33c661b88af22dda880d23d1753e35998c996e54d323b1b` (Review 01 regression checks; added after Review 01)
  - `data/EarthExponentialAtmosphereData.txt` `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`
- **Classification:** spike evidence for the T0 proposals (DR-0029). Model and frame agreement are exact where attributed. One configuration sensitivity is unresolved and escalated.
- **J-ax-1 limitation, quantified against GMAT's real Earth over 53 700 s:**
  - 0.19–0.58 m final and up to 1.08 m maximum, from polar motion (0.35″) at the 2026 epoch;
  - the geodetic height difference between J-ax-1 and GMAT's ellipsoid is up to 4.0 cm.

  These add to the precession/nutation limitation already recorded in DR-0028 (117 m against a 2026 mean-pole model; 123.5 m against GMAT in EarthMJ2000Eq axes).
- **Status:** informational. No gate, no threshold, no reference created. Nothing in `toolbox/references` was regenerated.
<!-- review01-correction-log -->
- **Correction log (Review 01, 2026-10-18; "TARS M3 T0 — Review 01 Correction Authorization").** The superseded wording is preserved at `bdcaacf`.
  - F4: the M3-form residual, quoted from a superseded run, is replaced by the committed 6.95e-6 m.
  - F2: the grid stiffness heights are replaced by exact thresholds, and the P1 properties are added.
  - F3: the inward stage is the third, not the second.
  - F1: the fixed-phase formula, which had been presented as a bound, is replaced by the derived bound and its sweeps.
  - `t0_decay.py` now labels its missed-crossing output as a single-phase measurement. Its other outputs are unchanged.
<!-- /review01-correction-log -->
