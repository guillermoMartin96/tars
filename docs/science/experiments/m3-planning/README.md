# M3 planning experiments (research only)

These scripts and outputs are **planning evidence** for the M3 Decision Requests DR-0024 (G1), DR-0025 (G2) and DR-0026 (G3). They are recorded as VAL-0018 (PLANNING).
- They are not project code, Toolbox assets, references or Proof gates.
- They do not import or exercise any production force model, because none exists for M3. They measure *candidate* physics, written independently in these scripts.
- Only the scenario loader and the M1 initial state are imported from `src/tars`.

**Provenance**
- Executed 2026-10-15 on branch `milestone-3-planning`. The production code is identical to the planning baseline `main` = `d92ab89`.
- Host: macOS 26.2 x86_64, Intel i9-9880H.
- Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1 (from `uv.lock`).
- GMAT R2026a, build Mar 26 2026; `GmatConsole` sha256 `1162803d…` (as in VAL-0004/VAL-0007).

## Candidate model under test
```
r' = v
v' = -mu r/|r|^3                                   (two-body; WGS 84 mu, DR-0003)
     - (3/2) J2 mu Re^2 / r^5 [x(1-5z^2/r^2), y(1-5z^2/r^2), z(3-5z^2/r^2)]   (J2 about the frame z axis)
     - (1/2) rho(h) / B |v_rel| v_rel                    B = m/(Cd A); v_rel = v - w x r, w = (0, 0, wE)
rho(h) = rho_i exp(-(h - h_i)/H_i)                 piecewise exponential, GMAT R2026a table (Vallado 8.6)
```
- The initial state is the M1 one: circular 250 km, i = 51.6°.
- The horizon is 53 700 s, the M1/M2 horizon.
- Ballistic coefficients are illustrative only, because no project drag parameters exist:
  - B = 25.8 kg/m², the GMAT defaults used in VAL-0007;
  - B = 100 kg/m².

## Files
| File | Purpose |
|---|---|
| `perturbation_experiment.py` → `perturbation_results.json` | Measures: acceleration magnitudes; RK4 (dt = 20/10/5/2.5 s) against SciPy DOP853 (rtol 1e-13); fitted J2 node rate against the first-order rate; drag decay against the first-order estimate; sensitivity of the final state to each constant and modelling choice; density continuity at the table's band edges. |
| `gmat_probe.py` → `gmat_probe_results.json` | GMAT feasibility probe. It asks which GM GMAT's gravity field applies, how far GMAT's J2 is from a J2 about the frame z axis at the 2026 and J2000 epochs, and how closely GMAT's `Exponential` drag matches the Python model with spherical and geodetic altitude. |
| `gmat_scripts/*.script` | The exact scripts the probe ran. `<tmp>` is the probe's temporary directory, which holds the generated `.cof` files and the reports. `<GMAT>` is the GMAT install root. |

## Reproduce
```sh
D=docs/science/experiments/m3-planning
uv run --no-sync python $D/perturbation_experiment.py $PWD/src scenarios/m1_leo_250km.json $D/perturbation_results.json
uv run --no-sync python $D/gmat_probe.py $PWD/src scenarios/m1_leo_250km.json "<GMAT>/bin/GmatConsole" $D/gmat_probe_results.json
```
The GMAT probe was run twice, and both runs gave identical numbers.

## Results (summary; full numbers in the JSON files)
| Quantity | Value |
|---|---|
| Point-mass gravity at 250 km | 9.073 m/s² |
| J2 acceleration at r0 (equator) / maximum (pole) | 1.36e-2 / 2.73e-2 m/s² (1.5e-3 / 3.0e-3 of point mass) |
| Drag acceleration at 250 km (B = 25.8 / 100 kg/m²) | 7.8e-5 / 2.0e-5 m/s² |
| Displacement from the point-mass orbit after 53 700 s: J2 / drag (B 25.8) / J2 + drag (B 25.8) | 741 km (GMAT measured 741 km in VAL-0007) / 363 km / 1 161 km |
| RK4 dt = 10 s vs DOP853, final position: point mass / J2 / drag (B 25.8) / J2 + drag (B 25.8) / J2 + drag (B 100) | 0.298 / 0.302 / 4.57 / 2.06 / 0.70 m |
| Error ratio when dt is halved (ideal 16): J2 | 22.4, 20.0, 18.3 |
| Error ratio when dt is halved: drag only, B 25.8 | **10.4, 9.0, 13.6**: order degraded (see below) |
| J2 node rate: fit / first-order analytic (osculating a0) | −5.4385 / −5.4099 °/day (+0.53%; cf. VAL-0007, GMAT −5.439) |
| Drag decay, fitted mean dā/dt vs first-order estimate at h0 with the King-Hele rotation factor | B 25.8: −12.8 km/day, +11.0% vs estimate; B 100: −3.05 km/day, +2.6% |
| Table density at band edges | **Finite jumps** from table rounding: 1.4e-3 relative at 25 km, 1.5e-5 at 250 km, ≤ 1e-4 elsewhere. **The scale height, and so dρ/dh, also changes at every edge**; for example 37.1 → 45.5 km at 250 km. |

**Sensitivity of the final position after 53 700 s** (DOP853; J2 + drag with B 25.8 unless marked "J2 only"):
| Change | Δ final position |
|---|---|
| J2 value: EGM2008 tide-free (baseline) → IERS 2010 zero-tide J2 (J2 only / with drag) | 6.65 / 7.44 m |
| → IERS conventional C̄20 tide-free at 2000.0 | 0.25 / 0.28 m |
| → JGM-3 / EGM96 (GMAT-bundled files) | 0.35 / 0.39 m |
| → WGS 84 *normal-field* C̄20 (geometric; not a dynamic value) | 2.50 / 2.79 m |
| J2 reference radius 6378137 → 6378136.3 m (J2 only / with drag) | 0.16 / 0.18 m |
| GM 3.986004418e14 → TT-compatible 3.986004415e14 (J2 only / with drag) | 0.63 / 0.70 m |
| Altitude datum for density lowered by 0.7 m | 9.2 m |
| J2 axis tilted by the 2026 precession angle θ_A = 521″ (J2 only) | 117 m |
| J2 and atmosphere axis tilted 0.145° about x (with drag) / 10″ | 2 400 / 46 m |
| Geodetic (WGS 84 ellipsoid) instead of spherical altitude for density | **74 km** |
| Non-rotating instead of co-rotating atmosphere | **40 km** |
| Ballistic coefficient +1% | 4.8 km |

**GMAT probe** (each GMAT final state vs the matching Python DOP853 model):
| Case | Δ position / Δ velocity | Reading |
|---|---|---|
| `c20zero_fileGM415`: a `.cof` with C20 = 0 and GM 3.986004415e14, while `Earth.Mu` = 3.986004418e14 | 1.4e-5 m vs a Kepler orbit with GM 4415; 0.627 m vs WGS 84 | **GMAT's gravity field applies the coefficient file's GM, not `Earth.Mu`.** |
| `j2_custom_2026`: custom `.cof` with the WGS 84 GM and radius and the EGM2008 tide-free C20; state in EarthMJ2000Eq | 123.5 m / 1.153 m/s | GMAT evaluates J2 in its Earth-fixed frame (IAU-1976/FK5 pole of date). The 521″ precession tilt alone reproduces 117 m / 1.149 m/s. |
| `j2_custom_2000`: the same at epoch 2000-01-01 12:00 TT | 25.4 m / 0.031 m/s | Residual from nutation and polar motion at J2000. |
| `j2_jgm3_2026`: GMAT's own JGM3.cof vs Python with JGM-3 GM and R | 123.5 m | Same pole effect; the constants matched. |
| **`j2_custom_2026_TOE`**: initial and final states in GMAT **true-of-epoch axes (TOEEq) fixed at the scenario epoch** | **0.19 m / 4.5e-4 m/s** | Expressing the state in the axes whose z is GMAT's pole at the epoch removes the pole offset. The residual is consistent with polar motion and pole motion during the run (not separated). |
| `drag_sph_2026` / `drag_sph_2000`: `Exponential` atmosphere, `Earth.Flattening = 0`, EarthMJ2000Eq | 1.38 / 1.12 m | The atmosphere rotates about GMAT's pole of date. |
| **`drag_sph_2026_TOE`**: the same in TOEEq axes | **0.0020 m / 2.4e-6 m/s** | **Exact-configuration match.** The 1.38 m above was the rotation axis. |
| `drag_geod_2026`: GMAT's default flattening, EarthMJ2000Eq | 4.33 m | Pole of date and GMAT's default flattening. |
| `drag_geod_2026_TOE_defaultf`: TOEEq, GMAT's default flattening | 1.85 m | **GMAT's default Earth flattening is not the WGS 84 value.** |
| **`drag_geod_2026_TOE_wgs84f`**: TOEEq, `Earth.Flattening` = 1/298.257223563 | **0.38 m / 4.4e-4 m/s** | Remaining residual: polar motion (GMAT's ellipsoid is ITRF-fixed) and/or a different geodetic-height algorithm (not separated). |

## Findings that drive the Decision Requests
1. **The J2 axis is a definition, not a detail.**
   - A J2 about the frame z axis (SCI-0003 frame) and GMAT's J2 about the pole of date differ by 123 m after 10 orbits at a 2026 epoch (25 m at J2000). That is 80–400× the RK4 truncation error.
   - **GMAT can nevertheless be an exact-configuration reference for a fixed-pole model** if states are exchanged in its true-of-epoch axes fixed at the scenario epoch. The residuals are then 0.19 m (J2), 2 mm (spherical-height drag) and 0.38 m (geodetic-height drag). Those residuals are attributed to Earth-orientation terms that the fixed-pole model deliberately omits, and must be bounded in DR-0025 before any gate uses them.
2. **GMAT's gravity GM comes from the `.cof` file, and its default Earth flattening is not WGS 84.** An exact-configuration GMAT gate needs a generated coefficient file with the project's GM, radius and C20, and an explicit `Earth.Flattening`. The informational VAL-0007 J2 runs therefore used the JGM-3 GM (3.986004415e14), not the `Earth.Mu` override in their scripts. That run is informational, and the 0.6 m effect is negligible against its 741 km result, but its metadata does not say so.
3. **Drag is far more sensitive to modelling choices than to integration error.**
   - 0.7 m of altitude datum moves the final state by 9 m, and 1% in B moves it by 4.8 km.
   - The altitude definition and atmosphere rotation are tens of km.
   - Any drag reference must match the configuration *exactly*; "realistic" references can only be informational.
4. **The literal piecewise-exponential table is discontinuous at band edges.** Table rounding gives finite density jumps (1.4e-3 relative at 25 km, 1.5e-5 at 250 km, ≤ 1e-4 elsewhere), and the scale height also changes. RK4's error ratios degrade when an orbit crosses a band edge: 9.0–13.6 instead of 16 for drag only. These are not an asymptotic order. An order-4 convergence oracle needs a smooth configuration, such as one band, or must account for edge crossings. (Corrected after review M3P-F1, which pointed out that an earlier wording called the table C0.)
5. **The first-order decay estimate is not a tight oracle** at these decay rates. The density grows as the orbit decays (+11% at B 25.8). A semi-analytic oracle must integrate the decay with density evaluated along the decaying orbit, and even then it stays approximate: orbit averaging and the rotation factor carry their own errors (review M3P-F3).
6. **The J2 constant choice matters at the metre level**, which is above the 0.3 m RK4 error. Tide system (zero-tide vs tide-free), source and GM labelling (TT vs TCG) must be decided explicitly and matched exactly in references.

## Q10 table check (added 2026-10-15, after the owner's G1 decision)
`q10_table_check.py` compares the GMAT R2026a exponential-atmosphere table with the data file published in the author's code repository (`CelesTrak/fundamentals-of-astrodynamics` @ `49df0479c950917c0a2c5ac31f2db6477bba57f6`, `software/misc/pascal/ATMOSEXP.DAT`), field by field as decimals, and quantifies the density jump at every band boundary. Output: `q10_table_check_results.json`; a rerun is byte-identical.

```
python -I q10_table_check.py "<GMAT>/data/atmosphere/earth/EarthExponentialAtmosphereData.txt" <checkout>/software/misc/pascal/ATMOSEXP.DAT q10_table_check_results.json
```

Result: 25 of 28 rows identical; the 0 km base altitude (0.0 vs 0.010 km) and the 900 km scale height (181.05 vs 181.045 km) differ; the 1000 km row is absent from the author's file. Largest boundary jump +1.36e-3 (25 km). Interpretation: DR-0024 §3.4; open residuals: DR-0027 item B.

## Q10 residual consequences (added 2026-10-15, review M3P2-F3)
`q10_residual_consequences.py` evaluates both sources as piecewise-exponential tables, using only the per-row values recorded in `q10_table_check_results.json`, and reports the density ratio at sample heights. Output: `q10_residual_consequences_results.json`; a rerun is byte-identical.

```
python -I q10_residual_consequences.py q10_table_check_results.json q10_residual_consequences_results.json
```

Result: in the lowest band (0.010–25 km) the GMAT density is 0.13785 % below the author's file at every height (ratio exp(0.010/7.249)). With the author's base altitude the 25 km jump would be −1.89e-5 instead of +1.36e-3. The 900 km scale-height rounding gives up to +1.5e-5 below 1000 km. Above 1000 km, where the author's file has no row, the sources diverge: +19.6 % at 1100 km, +145 % at 1500 km. Interpretation: DR-0024 §3.4 (correction), DR-0027 Resolution "Disputed cells".

## DR-0028 node sensitivity (added 2026-10-16, review M3P4-F1)
`dr0028_node_sensitivity.py` is standard-library geometry. It compares the inclination, ascending-node longitude and node point of one orbit seen from two frames whose poles differ by a small tilt δ. It reproduces the review-04 example and sweeps the tilt direction for several inclinations. Output: `dr0028_node_sensitivity_results.json`; a rerun is byte-identical.

```
python -I dr0028_node_sensitivity.py dr0028_node_sensitivity_results.json
```

Result, δ = 0.15°:
- |Δi| ≤ δ in every case.
- The node point moves by up to δ/sin i, and the node longitude by up to δ|cot i|; both agree with the first-order estimates to within 0.4 %.
- Review-04 example: the node moves to 90.2598055437°.
- At i = 0.1°, the node longitude can jump by 180°.

Interpretation: DR-0028 "Resolution amendment 1", item 1.

## DR-0028 signed node verification (added 2026-10-16, review M3P5-F1)
`dr0028_node_signed_verification.py` is a self-checking, standard-library script. It exits 0 only if both conditions hold:
- every exact property and every signed first-order check passes;
- every mutated formula is rejected.

What it does:
- Its oracle uses only an explicit Rodrigues rotation matrix and the element definitions; it never evaluates the formulas under test.
- It covers inclined, near-polar and near-equatorial orbits, several node longitudes and tilt azimuths, and both tilt signs.
- It checks signs and the convergence order of the linearization error.

Output: `dr0028_node_signed_verification_results.json`; a rerun is byte-identical.

```
python -I dr0028_node_signed_verification.py dr0028_node_signed_verification_results.json
```

Results:
- **Verdict:** PASS.
- **Observed error order:** 1.98–3.00, over 1038 samples.
- **Sign checks:** 1064, all agreeing.
- **Mutants:** all four rejected (both signs reversed as in amendment 1, each sign reversed alone, cos/sin swapped).

Interpretation: DR-0028 "Resolution amendment 2". The earlier `dr0028_node_sensitivity.py` compares absolute values only and is kept unchanged as amendment 1 evidence.

## Signed verification, revised (2026-10-16, reviews M3P6-F1, F2, F3)
`dr0028_node_signed_verification.py` was revised in place; the earlier version remains at commit `bcb7f9b`. The first-order checks and their results are unchanged.

What changed:
- **`wrap()`** now returns values in (−π, π] exactly. It is tested against an exact rational reduction, at both endpoints, and on exactly equivalent pairs.
- **E2** tests the full exact line-of-nodes identity: 168 interior, 144 equator-crossing (both tilt signs) and 48 endpoint cases, including the counterexample i = 2°, δ = 5°.
- **E5** now asserts the node discontinuity: E5a for the crossings, E5b for the azimuth sweep, and E5c, a coverage guard.
- **Five new mutants** must each be rejected by their designated tests: the unrestricted claim, the jump suppressed (two variants), the assertions disabled, and the previous wrap.

Result: PASS; a rerun is byte-identical. Interpretation: DR-0028 "Resolution amendment 3".

## Signed verification, wrap domain (2026-10-16, review M3P7-F1)
`wrap()` now accepts finite angles only. NaN, −NaN, +∞ and −∞ raise `ValueError("wrap: non-finite angle: …")`, and `wrap_nonfinite_tests` checks that.

Results:
- A new mutant, the unguarded `f999626` implementation, must fail in all four categories, and does.
- Finite-input behaviour and every pre-existing output section are unchanged. Two runs are byte-identical.

Interpretation: DR-0028 "Resolution amendment 4".

## Signed verification, finite validation and coverage (2026-10-16, review M3P8-F1)
Before this revision, a first-order formula returning NaN or ±∞ skipped the order and sign checks without a failure, and the script could still pass.

What changed:
- **Finite validation.** Every oracle and first-order value is checked with `math.isfinite` before any tolerance, order or sign comparison. A non-finite value is a failure, and that series counts towards no coverage minimum.
- **Per-formula coverage.** Each formula must reach a minimum number of valid samples, separately for the order and sign checks: Δi 506 and 560, ΔΩ 532 and 504. The sign minima are derived from the grid; the order minima are the existing counts. The derivations are in DR-0028 amendment 5.
- **Audit.** The exact properties E1–E4 and E6 now reject non-finite values instead of letting `max()` or a comparison drop them.
- **Mutants.** Ten new first-order mutants (NaN, ±∞ and zero predictions; NaN oracle values) and three audit mutants are each rejected by their designated checks.

`dr0028_node_signed_mutation_check.py` runs 33 file-level mutations of the verification script, each through its real entrypoint in a separate process, and requires each to exit nonzero. Output: `dr0028_node_signed_mutation_check_results.json`; a rerun is byte-identical.

```
python -I dr0028_node_signed_mutation_check.py dr0028_node_signed_mutation_check_results.json
```

Results: both scripts PASS; 33 of 33 mutations detected. Every finite result is unchanged; only new keys were added. Interpretation: DR-0028 "Resolution amendment 5".

## Assertion-specific mutants and reason-checked mutation (2026-10-17, reviews M3P9-F1..F3)
Review 09 showed that two assertions could be weakened or removed without any failure: the oracle's ±∞ rejection, and the order and sign checks of each formula. For E3 and E4 it noted the same gap.

What changed:
- **New built-in mutants** in `dr0028_node_signed_verification.py`, each rejected by its own designated check:
  - oracle ±∞ for each formula, over the whole grid and at a single sample;
  - per formula, a doubled first-order coefficient (order check) and a reversed sign (sign check);
  - a 1 % oracle inclination error (E3 and E4).
- **A built-in mutant that raises** is recorded as not rejected, so a crash never counts as a rejection.
- **`dr0028_node_signed_mutation_check.py`** now accepts a detection only for each mutation's declared reason, checked against the script's output. Five negative controls must be classified as not detected. It runs 109 mutations: the 33 earlier ones, 16 new ones, and review 09's 60 injection cases.
- **`dr0028_node_signed_assertion_sweep.py`** (new, measurement only) removes each of the 35 assertions in turn. 17 are detected individually, including every assertion named by the review 09 findings. The 18 that survive alone are recorded for a decision and not corrected.

```
python -I dr0028_node_signed_verification.py dr0028_node_signed_verification_results.json
python -I dr0028_node_signed_mutation_check.py dr0028_node_signed_mutation_check_results.json
python -I dr0028_node_signed_assertion_sweep.py dr0028_node_signed_assertion_sweep_results.json
```

Results:
- Both checks PASS: 109 of 109 mutations detected for their declared reason, and all 5 controls classified as not detected.
- The sweep reports 17 assertions detected and 18 surviving.
- Each output is byte-identical on a rerun.
- Every finite result is unchanged; only keys were added.

Interpretation: DR-0028 "Resolution amendment 6".

## Exception classification and assertion classification (2026-10-17, reviews M3P10-F1, F2)
Review 10 showed that the mutation check counted an unrelated exception inside a built-in mutant (for example, an import failure) as evidence that an assertion had been removed.

What changed:
- **Defect record.** `dr0028_node_signed_verification.py` records each built-in mutant's injected function against its reference implementation, so the output shows whether the defect was exercised. An unexercised mutant fails the run. An exception is recorded with its type, message and in-script call stack.
- **Six classification categories.** `dr0028_node_signed_mutation_check.py` classifies every run as one of: invalid mutation setup, process failure, normal execution, unexpected exception, rejected for another reason, or expected rejection. Only the last is a detection.
  - "Not rejected" requires a completed, exercised mutant.
  - An exception counts only under an explicit allowance (mutant, type, message, stack), for the E2/E5b wrap guard and the order-estimate math domain error.
  - There are 13 controls, each with its declared category.
- **`dr0028_node_signed_harness_regression.py`** (new) runs the controls against the reviewed harness (`896d52d`, read from git) and against the corrected one. The five M3P10-F1 regression controls fail there and pass now.
- **`dr0028_node_signed_assertion_classification.py`** (new) classifies the 18 assertions the sweep found not individually load-bearing, each with executed evidence: 6 A, which gain built-in mutants; 9 B; 3 C; 0 D.

```
python -I dr0028_node_signed_assertion_classification.py dr0028_node_signed_assertion_classification_results.json
python -I dr0028_node_signed_harness_regression.py dr0028_node_signed_harness_regression_results.json
```

The regression demonstration needs git, to read `896d52d`.

Results:
- All four checks PASS. 109 of 109 mutations are detected for their declared reason, and 13 of 13 controls receive their declared category.
- The sweep reports 23 assertions detected and 12 surviving: the 9 of category B and the 3 of category C.
- Each output is byte-identical on a rerun.
- Every finite result is unchanged; only keys were added.

Interpretation: DR-0028 "Resolution amendment 7".
