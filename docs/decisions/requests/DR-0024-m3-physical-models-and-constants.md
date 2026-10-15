# Decision Request: M3 physical models and constants: J2 and atmospheric drag (gate G1)

**Status:** OPEN (PROPOSED; not approved)  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A: J2 + atmospheric drag. G0 was approved by the Tech Lead on 2026-10-15.
- Planning baseline: `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f`.
- Companion requests: DR-0025 (G2, validation) and DR-0026 (G3, architecture).
- Impact analysis: `docs/milestones/M3-baseline-and-impact.md`.

Nothing here is implemented. Every value below is a *candidate* until this request is resolved. Statements are labelled **[fact]** (sourced or measured), **[derived]** (computed here from facts) or **[recommendation]**.

## 1. Problem statement
- M1 and M2 model Earth as a point mass (SCI-0001) with no perturbing forces (SCI-0004). VAL-0007 measured that this departs from realistic low-Earth-orbit (LEO) physics by 0.7–1.3 thousand km in 15 hours at the reference orbit. **[fact]**
- M3 adds the two dominant LEO perturbations, Earth's oblateness (J2) and atmospheric drag. That requires choosing:
  - the mathematical form of each force;
  - the frame and axis it is evaluated in;
  - the constants and their provenance;
  - the atmosphere model;
  - which quantities are pinned physics and which are per-scenario inputs;
  - the behaviour outside each model's domain.
- These choices must be made before implementation (T1/T2), because:
  - the validation strategy (DR-0025) depends on them;
  - exact-configuration references can only be built against a fixed definition;
  - the planning experiment shows that several "small" choices move the 10-orbit trajectory by metres to tens of kilometres (§3.3).

## 2. Requirements
- **R1. Authoritative sources.** Equations and constants come from authoritative sources (CLAUDE.md, playbook). They are not chosen because a library uses them.
- **R2. No reinterpretation of M1/M2.** v1/v2 scenarios, goldens, thresholds and references keep exactly their accepted meaning (two-body; WGS 84 GM and a; spherical altitude).
- **R3. Pinned constants are separate from scenario parameters.** Universal constants and environment datasets are pinned and versioned. Spacecraft and mission inputs are per-scenario.
- **R4. Deterministic, provider-independent, runnable without an LLM.** No network or space-weather data at run time.
- **R5. Validatable.** There must be at least one independent or partially independent reference for each capability (DR-0025), including an exact-configuration external reference where feasible.
- **R6. Explicit domain of validity.** Behaviour outside it is defined, never silent.
- **R7. Proportionate.** The fidelity should suit a simulator whose purpose is a realistic environment for later maneuvering and navigation work. It is not operational orbit determination.

## 3. Sources and evidence
### 3.1 Primary sources consulted (versions and dates)
| Key | Source | Used for |
|---|---|---|
| [NGA] | NGA.STND.0036_1.0.0_WGS84, *World Geodetic System 1984*, version 1.0.0, 2014-07-08 (downloaded from earth-info.nga.mil, 2026-10-15) | Table 3.1 defining parameters: a = 6378137.0 m; 1/f = 298.257223563; GM = 3.986004418e14 m³/s²; ω = 7.292115e-5 rad/s. §3.5.1 and Table 5.1: EGM2008 dynamic C̄2,0 = −0.484165143790815e-3. Table 6.1: WGS 84 *normal-field* C̄2,0 = −0.484166774985001e-3 (geometric, implied by the ellipsoid; not a dynamic value). §3.2: "distinct values for the C̄2,0 term, one dynamically derived … the other geometric" |
| [IERS-1] | IERS Conventions (2010), TN36, ch. 1, working version dated 16 November 2017 (obspm.fr Conventions Centre) | Table 1.1: GM⊕ = 3.986004418e14 m³/s², **TCG-compatible**; a_E = 6378136.6 m; J2⊕ = 1.0826359e-3 (zero-tide); 1/f = 298.25642; LG = 6.969290134e-10; ERA rate 1.00273781191135448 rev/UT1-day. §1.2: **"the TT-compatible geocentric gravitational constant is 3.986004415e14 m³/s² … It shall be used to compute orbits in a TT-compatible reference frame."** Table 1.2 (GRS80): ω = 7.292115e-5 rad/s |
| [IERS-6] | IERS Conventions (2010), TN36, ch. 6, working version dated 1 February 2018 | §6.1: EGM2008 GM and a_e (398600.4415 km³/s², 6378136.3 m) are its TT-compatible scaling parameters. Table 6.2: conventional C̄20 (zero-tide) = −0.48416948e-3 at 2000.0, rate +11.6e-12/yr (SLR, Cheng et al. 2010). §6.2.2: EGM2008 zero-tide minus tide-free ΔC̄20 = −4.1736e-9; conventional tide-free C̄20 = −0.48416531e-3 |
| [GMAT-MS] | GMAT R2026a *Mathematical Specification* (draft, bundled `docs/GMATMathSpec.pdf`) | §4.2.3 Eq. 4.73–4.74: a_d = −½ ρ v_rel² (C_d A/m) v̂_rel, v_rel = v − ω × r (+ wind). Eq. 2.98: ω_e = 7.29211514670698e-5 (1 − LOD/86400). Earth orientation is IAU-1976/FK5 |
| [GMAT-UG] | GMAT R2026a *User Guide / Reference* (bundled `docs/help/help-letter.pdf`), "Force Model", "CelestialBody" | Atmosphere models offered: JacchiaRoberts, MSISE86, MSISE90, NRLMSISE00, Exponential. The Exponential model reads a table file (altitude band base, base density, scale height) and cites Vallado, 5th ed. (2022), §8.6. Altitude limits per model. Earth's `RotationDataSource` cannot be changed |
| [GMAT-data] | GMAT R2026a `data/atmosphere/earth/EarthExponentialAtmosphereData.txt`; `data/gravity/earth/{JGM3,EGM96}.cof` | The 28-band exponential table (0–1000 km). JGM-3 / EGM96 C̄20 with the file GM 3.986004415e14 and R 6378136.3 m |
| [VAL5] | D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 5th ed. (2022), §8.6; 4th ed. (2013), §8.6 and §9.6 | Exponential atmosphere and drag; secular J2 rates. **Not re-read for this request.** The table values are taken from the GMAT-distributed file that cites it (open question Q10) |
| [MG] | O. Montenbruck, E. Gill, *Satellite Orbits*, Springer 2000, §3.2 and §3.5 | Geopotential and drag formulation; typical C_d 2.0–2.3 (secondary for this request; not re-read) |
| [CUR] | H. D. Curtis, *Orbital Mechanics for Engineering Students*, 3rd ed., 2014, §10.7 (J2 perturbation) | J2 acceleration components (already cited for SCI-0001) |
| [US76] | *U.S. Standard Atmosphere, 1976*, NOAA/NASA/USAF, NASA-TM-X-74335 | Steady-state reference atmosphere to 1000 km (candidate A3) |
| [MSIS00] | J. M. Picone et al., "NRLMSISE-00 empirical model of the atmosphere", JGR 107(A12), 1468 (2002), doi:10.1029/2002JA009430 | Candidate A4 |
| [MSIS2] | J. T. Emmert et al., "NRLMSIS 2.0: A whole-atmosphere empirical model of temperature and neutral species densities", Earth and Space Science 8(3), 2021, doi:10.1029/2020EA001321 | Candidate A4 (successor to NRLMSISE-00) |
| [CIRA] | COSPAR International Reference Atmosphere CIRA-2012, as summarized by S. Bruinsma et al., *J. Space Weather Space Clim.* 7, A4 (2017), doi:10.1051/swsc/2017003 (**secondary**) | CIRA-2012 selected NRLMSISE-00, JB2008 and DTM2009 (later DTM2013/DTM2020) as the thermosphere reference models |
| [KH] | D. King-Hele, *Satellite Orbits in an Atmosphere*, Blackie 1987 (**secondary**: cited through standard textbook usage, not re-read) | Atmosphere-rotation factor F = (1 − r ω_E cos i / v)² for decay estimates |

**Source disagreements recorded, not resolved here:**
- **The value of J2.** Each candidate is labelled with its tide system:
  - EGM2008 tide-free 1.0826261739e-3 [NGA] [derived];
  - IERS 2010 zero-tide 1.0826359e-3 [IERS-1];
  - IERS conventional zero-tide at 2000.0, 1.0826359e-3 [IERS-6] [derived];
  - IERS conventional tide-free 1.0826265e-3 [IERS-6] [derived];
  - JGM-3 1.0826267e-3 and EGM96 1.0826267e-3 [GMAT-data] [derived];
  - WGS 84 normal field 1.0826298e-3 [NGA]. This is a geometric value and must not be used as a dynamic J2.
- **GM.** 3.986004418e14 is the WGS 84 value [NGA] and the IERS *TCG-compatible* value [IERS-1]. The IERS TT-compatible value is 3.986004415e14 [IERS-1 §1.2], which is also the EGM2008 scaling GM [IERS-6] and GMAT's default.
  - **The accepted M1 record SCI-0005 states that 3.986004418e14 is "TT-compatible".** [IERS-1] labels it TCG-compatible. That is a documentation inaccuracy in an accepted M1 record. It does not change any M1 result, because GMAT was configured with the same value. This request does not edit SCI-0005; see Q3.
- **Earth rotation rate.** 7.292115e-5 rad/s is the WGS 84 / GRS80 nominal value [NGA][IERS-1 T1.2]. 7.29211514670698e-5 rad/s is the IERS ERA rate [IERS-1], which GMAT uses [GMAT-MS] [derived: 2π × 1.00273781191135448 / 86400]. The relative difference is 2e-9, which is negligible here.

### 3.2 Measurements (planning experiment; VAL-0018; `docs/science/experiments/m3-planning/`)
All measurements are from the M1 initial state over the 53 700 s M1/M2 horizon. **[fact, measured]**
- **Acceleration at 250 km:**
  - point mass 9.073 m/s²;
  - J2 1.36e-2 m/s² at the equator, 2.73e-2 m/s² at the pole;
  - drag 7.8e-5 m/s² (B = m/(C_d A) = 25.8 kg/m²) or 2.0e-5 m/s² (B = 100 kg/m²).
- **Displacement from the point-mass orbit after 53 700 s:**
  - J2 741 km (GMAT measured 741 km in VAL-0007);
  - drag (B 25.8) 363 km;
  - J2 + drag 1 161 km.
- **RK4 at dt = 10 s vs DOP853:**
  - J2 0.30 m (order ≈ 4: ratios 22, 20, 18);
  - drag 4.6 m (ratios 10.4, 9.0, 13.6: order degraded);
  - J2 + drag 2.1 m (B 25.8) / 0.70 m (B 100).
- **J2 node rate:** fitted −5.4385 °/day against the first-order analytic −5.4099 °/day (osculating a₀): +0.53%.
- **GMAT R2026a probe (exact constants via a generated `.cof`):**
  - GMAT's gravity field applies the `.cof` file's GM, not `Earth.Mu`.
  - GMAT's default Earth flattening is not WGS 84.
  - With states exchanged in GMAT's **true-of-epoch axes (TOEEq) fixed at the scenario epoch**, GMAT reproduces the fixed-pole candidate models to **0.19 m (J2)**, **2 mm (drag, spherical height)** and **0.38 m (drag, geodetic height, flattening set to WGS 84)** over 53 700 s.
  - In EarthMJ2000Eq axes the differences are 123.5 m, 1.38 m and 4.3 m, dominated by GMAT's pole of date.

### 3.3 What the choices change (Δ final position after 53 700 s; J2 + drag, B 25.8) **[fact, measured]**
| Choice | Δ |
|---|---|
| J2 value: tide-free (EGM2008) vs zero-tide (IERS 2010) | 6.7 m (J2 only) / 7.4 m |
| J2 value: EGM2008 tide-free vs JGM-3 / EGM96 | 0.35–0.39 m |
| J2 value: dynamic vs the WGS 84 normal-field (geometric) C̄20 | 2.5–2.8 m |
| J2 reference radius 6378137 vs 6378136.3 m | 0.16–0.18 m |
| GM 3.986004418e14 vs 3.986004415e14 | 0.63–0.70 m |
| J2 axis = frame z vs the 2026 mean pole (θ_A = 521″) | 117 m (J2 only). GMAT in EarthMJ2000Eq axes: 123.5 m. **GMAT in true-of-epoch axes: 0.19 m** |
| Density altitude: spherical vs geodetic | **74 km** |
| Atmosphere co-rotating vs not rotating | **40 km** |
| Ballistic coefficient +1% | 4.8 km |
| Altitude datum −0.7 m (for density) | 9.2 m |

## 4. Candidate approaches
### 4.1 J2 formulation
- **Potential** [CUR §10.7][MG §3.2]: U = (μ/r)[1 − J2 (R/r)² P₂(sin φ)], with P₂(x) = (3x² − 1)/2 and sin φ = z/r in the body frame. a = ∇U. The two-body term is unchanged.
- **Acceleration** (body frame, z along the symmetry axis) **[fact]**:
  a_J2 = −(3/2) J2 μ R² / r⁵ · [x(1 − 5z²/r²), y(1 − 5z²/r²), z(3 − 5z²/r²)].
  - **Sign check [derived]:**
    - At the equator (z = 0): a_J2 = −(3/2)J2 μR²/r⁴ r̂, an extra inward pull from the equatorial bulge.
    - At the pole: +3 J2 μR²/r⁴ ẑ, outward, so weaker gravity over the poles. Both are physically correct.
  - **Units:** SI; J2 dimensionless; R in m.
  - **Exact relation:** J2 = −√5 C̄2,0 for fully normalized coefficients [NGA eq. 3-1].
- **Domain [fact]:** the series is valid outside the reference sphere (r > R), which every non-impacting state satisfies. Truncation at degree 2 omits J3 and higher (~1e-3 of J2 at LEO) and every tesseral term.
- **Time dependence [fact]:** C̄20 drifts at +11.6e-12/yr [IERS-6]. Over 26 years ΔJ2 ≈ 6.7e-10 (relative 6e-7) [derived], which is negligible against the source spread. **A constant J2 is proposed.**
- **Numerical behaviour [measured]:**
  - The J2 force is smooth, and RK4 keeps order 4.
  - At dt = 10 s the truncation error is the same as two-body (0.30 m vs 0.298 m).
- **Interaction with the two-body model:** purely additive. The same μ is used in both terms. With J2 about a fixed axis the system is autonomous and conservative, so energy (including the J2 potential) and the axial angular momentum h_z are exact invariants (oracles for DR-0025).

**Axis options:**
- **J-ax-1 — J2 about the frame z axis (fixed pole).** The ECI frame (SCI-0003, EarthMJ2000Eq-aligned) defines the pole. No time, precession, nutation or Earth Orientation Parameters (EOP) are needed, and the epoch stays metadata (SCI-0007). GMAT reproduces it to 0.19 m over 10 orbits when states are exchanged in GMAT's true-of-epoch axes at the scenario epoch [measured]; the residual is the Earth-orientation motion this model deliberately omits.
- **J-ax-2 — J2 about the IAU 2006 (or IAU 1976) mean pole of date (precession only).** Analytic polynomials and no data files; the epoch becomes physical. It removes most of the GMAT mismatch, but nutation remains (about 25 m at J2000) and GMAT uses IAU-1976/FK5.
- **J-ax-3 — full pole of date (precession–nutation, polar motion; EOP data).** This would match GMAT, but it needs data files, time-scale conversions (UT1 for the Earth Rotation Angle only if longitude-dependent terms are added) and a large validated implementation.

### 4.2 Constant sets for J2
- **K-A — WGS 84 family + EGM2008 tide-free C̄2,0, all from [NGA]:** GM 3.986004418e14 (unchanged, DR-0003); R = a = 6378137.0 m (unchanged); J2 = −√5 × (−0.484165143790815e-3) = 1.0826261739e-3.
- **K-B — EGM2008-consistent scaling for the J2 term only:** J2 from C̄2,0 with R = 6378136.3 m and GM_TT = 3.986004415e14 inside the J2 term, while the two-body term keeps WGS 84 GM. That is internally consistent per [IERS-6] but means two GMs in one force field.
- **K-C — IERS 2010 numerical standards:** GM 3.986004418e14 (TCG) or 3.986004415e14 (TT), a_E 6378136.6 m, J2 1.0826359e-3 (zero-tide). It would be a new named constant set beside `WGS84`, with a different altitude datum.
- **K-D — IERS conventional geopotential:** C̄20(t) zero-tide with its secular rate. Disproportionate for M3.
- **Tide system (applies to K-A to K-D):**
  - **Tide-free** C̄20 removes the permanent tidal deformation of the Earth. GMAT's bundled JGM-3 and EGM96 fields are tide-free.
  - **Zero-tide** keeps it, so it is arguably the better single value when *no* tide model is applied, because the deformation is real [IERS-1 §1.1, IERS-6 §6.2.2].
  - The difference is ΔJ2 ≈ 9.3e-9, which is 6.7 m over 10 orbits [measured].

### 4.3 Atmosphere density models
| | A1 single exponential | A2 piecewise-exponential table | A3 U.S. Standard Atmosphere 1976 | A4 empirical thermosphere (NRLMSISE-00 / NRLMSIS 2.0 / JB2008 / DTM / Jacchia-Roberts) |
|---|---|---|---|---|
| Form | ρ = ρ₀ exp(−(h − h₀)/H) | A1 per band, 28 bands 0–1000 km [GMAT-data; VAL5 §8.6] | Layered hydrostatic and diffusion model [US76] | Empirical; species, temperature [MSIS00][MSIS2][CIRA] |
| Inputs | h | h | h | h, geodetic lat/lon, local solar time, day of year, F10.7, F10.7A, Ap/Kp (JB2008: more indices) |
| Time / epoch dependence | None | None | None | Yes: UT1/UTC, Sun position, space-weather history |
| Smoothness | C∞ | **C0 only: dρ/dh jumps at band edges** [measured]; RK4 order degrades on crossings | Piecewise (layer formulas) | Smooth in h; driven by stepwise daily/3-hour inputs |
| Realism at 250 km | Only near h₀ | A static mean profile; no solar-cycle variation | Moderate-activity mean only | Best available; still ~10–30% density error ([CIRA] secondary) |
| External exact-configuration reference | GMAT `Exponential` with a one-row file | **GMAT `Exponential` with the identical file: 2 mm from the Python model at 10 orbits (true-of-epoch axes, spherical height)** [measured] | Not in GMAT | GMAT has JR, MSISE90 and NRLMSISE00 (single-precision Fortran, a stated GMAT caution) |
| Implementation and verification cost | Very low | Low (table lookup) | Moderate | High: large empirical code or a new dependency (DR), space-weather data management, time scales |

**Not justified at M3 [recommendation]:** A4. M3's purpose is a validated, deterministic environment, not operational accuracy. A4 would make the epoch physical (SCI-0007), add space-weather data and possibly a dependency, and its density uncertainty (tens of percent) exceeds every integration error by orders of magnitude, so it cannot be gated tightly against anything except an exact copy of itself. It belongs to a later fidelity milestone if one is ever needed.

### 4.4 Drag force
- **Equation [GMAT-MS 4.73–4.74][MG §3.5][VAL5 §8.6]:**
  a_d = −½ ρ(h) (C_d A / m) |v_rel| v_rel, with v_rel = v − ω_E × r.
  - Units: kg/m³, m², kg, m/s.
  - "Cannonball" model: constant C_d and a constant reference area normal to v_rel, attitude-independent. GMAT `Drag.DragModel = Spherical` is the same thing [GMAT-UG].
- **Atmosphere rotation options:**
  - **D-rot-1 — rigid co-rotation about the frame z axis** with ω_E (no winds).
  - **D-rot-2 — no rotation.** A 40 km effect [measured], physically wrong.
  - **D-rot-3 — co-rotation about the pole of date.** Goes with J-ax-2/3.
- **Mass:** m = m_dry + m_prop from simulator-owned state (M2). It changes during burns. Drag must use the current mass at every derivative evaluation, consistent with SCI-0010. A drag-capable spacecraft therefore needs mass properties even without an engine (DR-0026).
- **C_d and A are scenario parameters**, not constants (R3).
  - **C_d:** typical free-molecular values are 2.0–2.4, and 2.2 is the conventional default ([MG], [VAL5], GMAT default; secondary).
  - **A:** depends on the vehicle.
  - **Neither has a project value yet** (Q9).

### 4.5 Altitude used for density
- **H-sph — spherical altitude h = |r| − a** (SCI-0006, as reported today):
  - simple and exact;
  - matches GMAT with `Earth.Flattening = 0` to 2 mm in true-of-epoch axes;
  - but overestimates density at high latitude, because the ellipsoid surface lies up to ≈21 km below the sphere at the poles (SCI-0006).
- **H-geod — geodetic height above the WGS 84 ellipsoid** (a, f from [NGA]; ellipsoid axis = frame z under J-ax-1):
  - this is the physically meaningful input for any atmosphere model, and SCI-0006's own revisit trigger names it;
  - it needs a cartesian→geodetic conversion: an iterative or closed-form algorithm that must be validated itself;
  - GMAT matches it to 0.38 m in true-of-epoch axes once `Earth.Flattening` is set to WGS 84 (GMAT's default is not WGS 84) [measured]. The residual is not separated: polar motion of GMAT's ITRF-fixed ellipsoid, or a different height algorithm;
  - its effect on the trajectory is 74 km over 10 orbits.

### 4.6 Out-of-domain behaviour
- **Density below 0 km.** The run ends at impact (spherical altitude ≤ 0, unchanged). Intermediate RK4 stages may still evaluate slightly negative h, so the model must be total.
  - Candidate: extrapolate the lowest band, which is GMAT's documented behaviour when a table starts above 0.
- **Density above the table top (1000 km).** The candidates are:
  - extrapolate the top band, which keeps the profile continuous and is what GMAT's Exponential applies [GMAT-UG: "No lower or upper altitude limit"];
  - ρ = 0 above a cutoff, which introduces a discontinuity (rejected).
- **Physical validity of the drag model itself.** The free-molecular, constant-C_d drag model and the static atmosphere lose validity at low altitude: continuum flow, heating and break-up. **No numerical lower limit is proposed here.** That is Q8, an owner or engineering-judgment decision, coupled with a possible `reentry` outcome in DR-0026.

## 5. Tradeoffs (summary)
- **Physical fidelity of the axis vs simplicity.**
  - J-ax-1 is simplest and keeps time-invariance.
  - Its loss of realism is ~0.15° of pole offset in 2026.
  - The measured true-of-epoch technique keeps GMAT usable as an external reference, so exact matching no longer requires J-ax-3.
  - J-ax-3 would add Earth-orientation modelling and data that M3 does not otherwise need. DR-0025 §2 discusses the residual bound.
- **Smoothness vs realism of the density profile.**
  - A1 is smooth and analytically tractable, but realistic only near h₀.
  - A2 is realistic in shape over 0–1000 km and GMAT-matchable, but C0 only.
  - **A2 contains A1 as the one-band case** [derived], so one implementation serves both, with a smooth configuration available for order checks.
- **Spherical vs geodetic height.** Both are simple and defensible. Geodetic is the physically meaningful one, and the effect is tens of km.
- **One standard vs physically preferred tide convention.** K-A is the same standard document as DR-0003, but tide-free. A zero-tide value (K-C) is arguably more physical when no tides are modelled. The trajectory difference is metres.

## 6. Recommended approach **[recommendation; not approved]**
1. **J2 axis: J-ax-1** (frame z axis, fixed pole). Record it as a new assumption (SCI-0013 below), with the measured 117–123 m (2026) and 25 m (J2000) model limitation against a pole-of-date Earth. This keeps:
   - SCI-0003 (the frame);
   - SCI-0007 (the epoch is metadata);
   - autonomy, so exact invariants are available as oracles.
2. **J2 constants: K-A.**
   - GM and a unchanged from DR-0003.
   - **J2 = 1.0826261739e-3 from the EGM2008 C̄2,0 published in NGA.STND.0036 Table 5.1**: same standard document, dynamic value, tide-free like GMAT's bundled fields.
   - Record that the permanent-tide deformation is not represented (ΔJ2 ≈ 9.3e-9), along with all tides (SCI-0004 continues).
   - **The tide-system choice is flagged for the owner (Q1)**; the zero-tide alternative is defensible.
3. **Atmosphere: A2.**
   - Vallado's piecewise-exponential table, pinned as a versioned dataset by digest. Its provenance is the GMAT-distributed file that cites Vallado §8.6 (Q10).
   - A one-band table derived from one row is also pinned, for smooth analytic and convergence cases.
4. **Density height: H-geod** (WGS 84 ellipsoid about frame z). This is physically meaningful, as SCI-0006's revisit trigger anticipated. **This is the most consequential owner choice in this request (Q6)**: H-sph is simpler and matches GMAT more closely today (2 mm vs 0.38 m).
5. **Atmosphere rotation: D-rot-1** (rigid co-rotation about frame z, ω_E = 7.292115e-5 rad/s [NGA]; no winds).
6. **Drag: cannonball, constant C_d and A per scenario, current total mass** from simulator state.
7. **Domain: extrapolate the lowest and highest bands.** The physical lower limit and re-entry semantics are left to Q8 and DR-0026.
8. **Not in M3:** J3+, tesserals, third body, SRP, tides, relativity, Earth orientation, space weather, A3 and A4, winds, lift, attitude-dependent area.

## 7. Constants proposed for pinning (candidate set "WGS84-EGM2008-J2" or similar; name decided in DR-0026)
| Constant | Value | Source | Status |
|---|---|---|---|
| GM (μ) | 3.986004418e14 m³/s² | [NGA] T3.1 (DR-0003) | APPROVED previously (DR-0003); unchanged |
| a (equatorial radius; J2 reference radius; spherical datum) | 6378137.0 m | [NGA] T3.1 (DR-0003) | APPROVED previously as GM/a; **its use as the J2 reference radius is PROPOSED** |
| J2 | 1.0826261739e-3 (= −√5 · −0.484165143790815e-3) | [NGA] Table 5.1 (EGM2008, tide-free) | PROPOSED (Q1, Q2) |
| 1/f (ellipsoid, geodetic height) | 298.257223563 | [NGA] T3.1 | PROPOSED (only if H-geod) |
| ω_E | 7.292115e-5 rad/s | [NGA] T3.1 | PROPOSED |
| Exponential density table | 28 rows (base altitude km, ρ kg/m³, H km), pinned by sha256 | [GMAT-data], citing [VAL5] §8.6 | PROPOSED (Q5, Q10) |
| One-band validation table | The 250 km row of the same table | derived | PROPOSED |
| g₀ | 9.80665 m/s² | SCI-0009 | APPROVED previously; unchanged |

`EARTH_J2_APPROX = 1.0826e-3` in `constants.py` stays as it is (informational, used by M1 validation). It is **not** proposed as the M3 value.

## 8. Scenario parameters (per scenario, never universal)
- **Spacecraft mass properties:** dry mass and propellant (M2 semantics).
- **Drag properties:** C_d (dimensionless) and reference area A (m²). Positive and finite. Illustrative reference values need a cited basis, as DR-0010 did for the engine (Q9).
- **Selection of the environment:** which force models are active, and which pinned atmosphere dataset (by identifier) is used. Scenarios cannot redefine dataset contents or constants inline (DR-0026).
- **Initial orbit, epoch (metadata), integrator, dt, stop, commands:** as in M1/M2.

## 9. Units and frame conventions
- **Units:** SI throughout (m, s, kg, rad).
  - Table altitudes and scale heights in km are converted once, at dataset load. The dataset digest covers the original file.
  - Density is in kg/m³.
- **Frame:** the ECI frame of SCI-0003 (EarthMJ2000Eq-aligned, treated as inertial).
  - The J2 symmetry axis, the ellipsoid axis and the atmosphere rotation axis are all **the frame z axis** (J-ax-1, D-rot-1).
- **Time:** elapsed TT seconds from the epoch label (SCI-0007). The recommended models have no epoch dependence.

## 10. Domain-of-validity assumptions
- J2 truncated field: r > R. Higher harmonics, the pole of date and tides are neglected (quantified in §3.3).
- Exponential table: tabulated 0–1000 km; extrapolated outside it (§4.6).
  - It represents a static mean atmosphere: no diurnal, seasonal, solar-cycle or geomagnetic variation.
  - Real density at 250 km varies by a factor of order 3.5 with solar activity (VAL-0007: implied densities 3.7e-11 to 1.3e-10 kg/m³ for F10.7 = 70–250).
- Drag: free-molecular regime; constant C_d and A; no lift. The lower physical limit is unresolved (Q8).
- |ω_E × r| < |v| (≈ 0.48 km/s vs 7.7 km/s at 250 km), so drag power is negative and orbital energy strictly decreases. This is an oracle precondition, checked in DR-0025.

## 11. Known limitations
- Absolute realism is limited by the static atmosphere. Drag-driven predictions such as lifetime are indicative only, and must never be presented as forecasts.
- The fixed pole means the J2 node and ground-track geometry differ from the real Earth by about 0.15° of pole offset in 2026.
- The geodetic conversion (if adopted) is a new numerical algorithm with its own error budget (DR-0025).
- C0 density continuity at band edges degrades RK4's convergence order on crossings.
- The GMAT geodetic-height drag residual (0.38 m in true-of-epoch axes) is not yet separated into polar motion and algorithm difference. The spherical-height residual is 2 mm.

## 12. Rejected alternatives and why
- **WGS 84 normal-field C̄2,0 as J2.** It is a geometric, ellipsoid-implied quantity [NGA §3.2, Table 6.1], not the dynamic J2.
- **GMAT's JGM-3 or EGM96 values because GMAT ships them.** That would choose a constant because a tool uses it, against R1. They remain usable *as references* when configured explicitly.
- **K-D (time-varying conventional C̄20).** Its effect (relative 6e-7 over 26 years) is far below the other uncertainties, while adding a time dependence.
- **A4 at M3.** See §4.3.
- **A3 (US76).** No exact external reference in GMAT. More implementation than A2, for a similarly static profile.
- **Non-rotating atmosphere.** A 40 km effect, physically wrong.
- **ρ = 0 above a cutoff.** Introduces a discontinuity for no physical gain.

## 13. Questions requiring owner decision (BLOCKED ON OWNER)
| # | Question | Recommendation |
|---|---|---|
| Q1 | J2 value and tide system: EGM2008 tide-free (K-A, 1.0826261739e-3), or a zero-tide value (IERS 2010 1.0826359e-3)? | K-A, tide-free |
| Q2 | J2 reference radius: a = 6378137 m (K-A), or EGM2008's 6378136.3 m with its scaling GM (K-B)? Effect 0.16 m | 6378137 m |
| Q3 | GM for M3: keep WGS 84 3.986004418e14 (DR-0003)? Also, should SCI-0005's "TT-compatible" wording get an erratum note (IERS labels it TCG-compatible; TT = 3.986004415e14)? An erratum note does not change any M1/M2 result | Keep 3.986004418e14 for M3. Add an erratum note to SCI-0005, with Tech Lead approval, as M1 records are accepted evidence |
| Q4 | J2 and atmosphere axis: fixed frame z (J-ax-1), mean pole of date (J-ax-2), or full pole of date (J-ax-3)? | J-ax-1 |
| Q5 | Atmosphere model: A2 (table, plus the one-band subset), A1 only, or A3? A4 deferred? | A2; A4 deferred |
| Q6 | Height for density: geodetic (H-geod) or spherical (H-sph)? | H-geod (most consequential choice) |
| Q7 | Atmosphere rotation: rigid co-rotation about z with ω_E (WGS 84 nominal)? | Yes |
| Q8 | Lower validity limit of the drag model and re-entry semantics: no limit (run to impact at h ≤ 0), or an owner-set altitude ending the run as `reentry` (DR-0026)? No value is proposed without a source or explicit owner judgment | Owner judgment needed; DR-0026 offers the mechanism |
| Q9 | Reference-scenario drag parameters (C_d, A) and the basis for illustrative values (DR-0010 precedent) | C_d = 2.2 (cited convention); A from a cited vehicle class, chosen with the reference scenarios (T0) |
| Q10 | Table provenance: accept the GMAT-distributed table (citing Vallado §8.6) as the dataset of record, or require a check against the printed source first? | Check against the printed Vallado table before pinning; record any difference |

## Impact
- **Architecture:** a force-context with mass, and pinned datasets (DR-0026).
- **Science/validation:** proposed SCI entries below; DR-0025.
- **Dependencies:** none. NumPy and SciPy are already present; no atmosphere library.
- **Development effort:** low to moderate (A2, H-geod).
- **Token/compute impact:** low.
- **Reversibility:** high before implementation. After implementation, changing a constant means a new physics-configuration version (DR-0026), never an edit of existing evidence.

## Proposed new scientific assumptions (drafts; added to the register only on approval)
- **SCI-0013 — Earth's J2 field about the frame z axis (fixed pole).** Zonal degree 2 only, constants per §7. Neglects precession, nutation and polar motion. Measured effect against the pole of date: 117–123 m (2026) / 25 m (J2000) over 10 orbits.
- **SCI-0014 — Rigidly co-rotating atmosphere about the frame z axis with ω_E; no winds.**
- **SCI-0015 — Static piecewise-exponential density** (pinned table); no solar or geomagnetic variation; extrapolated outside 0–1000 km.
- **SCI-0016 — Cannonball drag:** constant C_d and A, free-molecular, current total mass, no lift.
- **SCI-0017 — Density height = geodetic height above the WGS 84 ellipsoid** (if Q6 = H-geod). It applies to density only. SCI-0006 remains the definition of reported altitude and impact for v1/v2 and is unchanged.
- **SCI-0001 and SCI-0004** stay Active for M1/M2 configurations. For M3 configurations they are superseded in part by SCI-0013 to SCI-0016, recorded per configuration, not by editing the M1 entries.

## Blocked work
- M3 T1 (J2 model) and T2 (drag model) are blocked on this request.
- So are the reference scenarios and the GMAT configuration in DR-0025.

## Work continuing independently
- None of the M3 implementation. Planning documents only.

## Requested response
Answers to Q1–Q10. For example: "Q1 K-A, Q2 a, Q3 keep + erratum, Q4 J-ax-1, Q5 A2, Q6 H-geod, Q7 yes, Q8 <decision>, Q9 <basis>, Q10 verify first", or `discuss`.

## Resolution
**Decision:** _pending_  
**Reasoning/notes:**  
**Follow-up:**
