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
