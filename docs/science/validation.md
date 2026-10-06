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
