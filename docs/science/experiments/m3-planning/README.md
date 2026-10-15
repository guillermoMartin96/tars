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
