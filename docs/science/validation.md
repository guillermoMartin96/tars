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
  - **Epoch column.** It carries per-command re-rounding (M-a). It is used only for spacing verification, with a resolution of about 3e-7 s per value.
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
  - **Each O9 check disabled in turn makes a test fail.** As first written, this claim was false for the coast-vs-Kepler gate (review M2-T6 F7). It is now verified by a harness over all 15 gated metrics and the F1/F3/F5/F6 checks, each with its own targeted test.
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

