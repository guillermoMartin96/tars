# Scientific Assumptions Registry

This registry distinguishes deliberate model simplifications from bugs and unknowns. Use stable IDs such as `SCI-0001` and the structure in `toolbox/templates/science-assumption.md`.

## Index
| ID | Title | Status | Applies to |
|---|---|---|---|
| SCI-0001 | Earth gravity is a Newtonian point mass | Active | M1 force model |
| SCI-0002 | Restricted two-body: spacecraft mass negligible relative to Earth | Revised (2026-10-09, DR-0011) | M1/M2 dynamics |
| SCI-0003 | Earth-centred J2000-aligned frame treated as inertial | Active | M1 state/frame |
| SCI-0004 | No perturbing forces (drag, SRP, third body, tides, relativity) | Active | M1 force model |
| SCI-0005 | Earth constants from WGS 84 | Active | All physics |
| SCI-0006 | Altitude measured above a spherical Earth | Active | Reporting/initial conditions |
| SCI-0007 | Uniform simulation time from a labelled epoch | Active | Time propagation |
| SCI-0008 | Ideal constant-thrust, constant-Isp engine; instantaneous on/off | Active (DR-0011) | M2 propulsion |
| SCI-0009 | Standard gravity g0 = 9.80665 m/s² converts Isp to exhaust velocity | Active (DR-0011) | M2 propulsion |
| SCI-0010 | Variable-mass equation of motion a = F/m (no ṁ·v term) | Active (DR-0011) | M2 dynamics |
| SCI-0011 | Instantaneous ideal pointing through the centre of mass; no attitude dynamics | Active (DR-0011, DR-0012) | M2 thrust direction |
| SCI-0012 | Single tank, all propellant usable, instantaneous flame-out at depletion | Active (DR-0011, DR-0014) | M2 propellant |
| SCI-0013 | Earth J2 zonal field about the frame z axis (fixed pole), EGM2008 tide-free J2 with WGS 84 GM and a | Approved (DR-0024); not implemented. Axis: Earth-fixed +Z (DR-0024 Q4); realization OPEN (DR-0028); APPROVED J-ax-1 2026-10-15 (DR-0028) | M3 configurations |
| SCI-0014 | Atmosphere rigidly co-rotating with Earth about the frame z axis; no winds | Approved (DR-0024); not implemented. Axis: Earth-fixed +Z (DR-0024 Q4); realization OPEN (DR-0028); APPROVED J-ax-1 2026-10-15 (DR-0028) | M3 configurations |
| SCI-0015 | Static piecewise-exponential atmosphere (Vallado/GMAT table), preserved as published | Approved (DR-0024); not implemented; table conditionally approved and termination input approved with conditions (DR-0027); domain behaviour OPEN | M3 configurations |
| SCI-0016 | Cannonball drag: constant C_d and A from the scenario, current total mass, no lift | Approved (DR-0024); not implemented | M3 configurations |
| SCI-0017 | Density height = geodetic height above the WGS 84 ellipsoid | Approved (DR-0024); not implemented. Ellipsoid axis: Earth-fixed +Z (DR-0024 Q4); realization OPEN (DR-0028); APPROVED J-ax-1 2026-10-15 (DR-0028) | M3 configurations (density only; also the termination-altitude convention, DR-0027 A-2) |

## Sources used throughout
- **[NGA]** NGA.STND.0036_1.0.0_WGS84, *Department of Defense World Geodetic System 1984*, National Geospatial-Intelligence Agency, 2014. https://earth-info.nga.mil/GandG/wgs84/index.html
- **[VAL]** D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed., Microcosm Press, 2013. Ch. 1–2 (two-body problem, Kepler's equation), Ch. 8–9 (perturbations).
- **[CUR]** H. D. Curtis, *Orbital Mechanics for Engineering Students*, 3rd ed., Butterworth-Heinemann, 2014. Ch. 2–4 (two-body motion, orbital elements), Ch. 6 (orbital maneuvers, including non-impulsive), Ch. 10 (perturbations), Ch. 11 (rocket vehicle dynamics).
- **[IERS]** G. Petit, B. Luzum (eds.), *IERS Conventions (2010)*, IERS Technical Note 36. Table 1.1 numerical standards; Ch. 2 reference frames.
- **[SUT]** G. P. Sutton, O. Biblarz, *Rocket Propulsion Elements*, 9th ed., Wiley, 2017. Ch. 2 (specific impulse), ch. 4 (flight performance).
- **[PM92]** A. R. Plastino, J. C. Muzzio, "On the use and abuse of Newton's second law for variable mass problems", *Celestial Mechanics and Dynamical Astronomy* 53, 227–232 (1992). doi:10.1007/BF00052611
- **[NIST-gn]** NIST CODATA, standard acceleration of gravity g_n = 9.806 65 m s⁻² (exact). https://physics.nist.gov/cgi-bin/cuu/Value?gn
- **[GMATMS]** GMAT R2026a Mathematical Specification (draft) §4.2.7; GMAT R2026a help pages `ChemicalThruster`, `ChemicalTank`.
- **[GMATVV]** S. P. Hughes et al., *Verification and Validation of the General Mission Analysis Tool (GMAT)*, AIAA/AAS 2014. https://ntrs.nasa.gov/citations/20140017798. Documents GMAT Earth μ = 398600.4415 km³/s².

---

# SCI-0001: Earth gravity is a Newtonian point mass

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** Milestone 1 force model (`PointMassGravity`)

## Assumption
- Earth's gravitational field is that of a point mass (equivalently, a spherically symmetric body): **a = −μ r / |r|³**.
- No zonal or tesseral harmonics are modelled (J2 and higher).

## Why we are making it
- DR-0002 (option A). It is the foundation model.
- It has an exact analytic solution (Kepler), so integrator correctness can be proven against truth.

## Sources
- [VAL] §1.3–1.4, §2.2
- [CUR] §2.2–2.4

## Known limitations / expected error
- Earth's oblateness (J2 ≈ 1.0826×10⁻³) is the largest neglected effect.
- For the M1 orbit (circular, 250 km, i = 51.6°), the secular J2 rates are standard first-order results ([VAL] §9.6; [CUR] §4.7). Evaluated with WGS 84 constants:
  - Node regression dΩ/dt = −(3/2) n J2 (R/a)² cos i ≈ **−5.41°/day**, or −3.36° over 10 orbits.
  - Apsidal rotation dω/dt ≈ +4.05°/day. This is not meaningful for a near-circular orbit.
- Over 10 orbits, the real orbit plane rotates by more than 3°. This corresponds to position differences of hundreds of km versus the point-mass model.
- **M1 orbits are therefore not realistic predictions of a real 250 km spacecraft.**

## Validation approach
- Analytic Kepler oracle and invariant conservation.
- GMAT configured with point-mass Earth gravity (degree/order 0) and matched μ.
- Informational GMAT runs (VAL-0007) **measured** the omission:
  - J2 node drift −5.44°/day, matching the analytic −5.41°/day;
  - divergence from M1 of about 741 km after 10 orbits (J2 only).

## Accepted discrepancy / tolerance
- Versus a realistic model: not applicable in M1; the omission is deliberate.
- Versus a point-mass reference: numerical tolerances only (DR-0004 follow-up).

## Revisit when
- Any mission depends on ground track, node, RAAN, or orbit fidelity over more than about one orbit.
- J2 is planned for a later milestone.

## Related
- ADR: ADR-0003
- DR: DR-0002
- Proof: proof/physics.md

---

# SCI-0002: Restricted two-body — spacecraft mass negligible relative to Earth (originally "spacecraft is a massless point")

**Status:** Revised (2026-10-09, DR-0011; originally Active 2026-10-05)  
**Introduced:** 2026-10-05  
**Applies to:** M1 dynamics

## Assumption
- The spacecraft's mass is negligible compared with Earth's. Earth's acceleration toward the spacecraft is ignored.
- The equation of motion uses μ = G·M_Earth, not G(M_Earth + m).
- The spacecraft is a point (no attitude, no extent).
- **Revision (M2, DR-0011):** the spacecraft now has a finite, time-varying mass m = m_dry + m_prop. It is used only to compute thrust acceleration F/m (SCI-0010). The restricted two-body approximation for gravity is unchanged: μ = G·M_Earth, and Earth's reaction is neglected.

## Why we are making it
For any spacecraft, m/M_Earth is of order 10⁻²¹, so the correction is far below numerical precision.

## Sources
- [VAL] §1.3 (relative two-body equation)
- [CUR] §2.2–2.3

## Known limitations / expected error
- Negligible for translational motion.
- Attitude dynamics are not modelled. This is irrelevant for M1, which has no torques.

## Validation approach
None needed beyond the overall two-body validation.

## Accepted discrepancy / tolerance
Not applicable.

## Revisit when
- Attitude, extended bodies, or spacecraft mass properties affect forces (drag area, thrust).

## Related
- ADR: ADR-0002

---

# SCI-0003: Earth-centred, J2000-aligned frame treated as inertial

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** M1 state representation

## Assumption
- State vectors are Cartesian in an Earth-centred frame whose axes are aligned with the mean equator and equinox of J2000.0. This is the same frame as GMAT's `EarthMJ2000Eq`.
- The frame is treated as inertial: Earth's own heliocentric acceleration and the precession/nutation of the axes are ignored.

## Why we are making it
- With no third-body forces (SCI-0004), the Earth-centred frame is the natural frame for the relative two-body equation.
- Matching GMAT's frame makes comparison direct.

## Sources
- [IERS] Ch. 2
- [VAL] §3.7 (coordinate frames)
- GMAT user guide, coordinate system `EarthMJ2000Eq`

## Known limitations / expected error
- In reality the geocentric frame is accelerated by the Sun and Moon. That effect is the third-body perturbation, deliberately excluded under SCI-0004.
- No Earth rotation, so there are no Earth-fixed coordinates, latitude/longitude, or ground track in M1.

## Validation approach
Same initial state and frame used in GMAT.

## Accepted discrepancy / tolerance
Not applicable while third-body effects are excluded.

## Revisit when
- Third-body perturbations, ground tracks, or Earth-fixed sites are introduced.

## Related
- ADR: ADR-0002
- SCI: SCI-0004

---

# SCI-0004: No perturbing forces

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** M1 force model

## Assumption
The following are not modelled:
- atmospheric drag
- solar radiation pressure
- Sun/Moon third-body gravity
- solid-Earth and ocean tides
- relativistic corrections

## Why we are making it
DR-0002 (option A). Each requires its own researched model. The force-model boundary (ADR-0003) allows them to be added later.

## Sources
- [VAL] Ch. 8–9 (perturbation models and relative magnitudes)
- [CUR] §10

## Known limitations / expected error
- **Atmospheric drag is significant at 250 km.** Real objects at this altitude decay measurably within days and re-enter within weeks to months without reboost.
- The drag rate depends strongly on solar/geomagnetic activity and on the spacecraft's ballistic coefficient. It is **not** estimated here. It is to be quantified later with a researched atmosphere model and/or GMAT.
- The other listed effects are smaller than J2 and drag at this altitude ([VAL] Ch. 8 magnitude comparisons).
- **Consequence:** the M1 orbit never decays. That is a property of the model, not of reality.

## Validation approach
- M1 compares only against references configured with the same exclusions.
- Informational GMAT runs (VAL-0007) **measured** the drag omission for an illustrative spacecraft (m/(Cd·A) = 25.8 kg/m²):
  - mean SMA decay of 3.6–12.4 km over 10 orbits for F10.7 = 70–250;
  - divergence from M1 of 0.9–1.3 thousand km including J2.

## Accepted discrepancy / tolerance
Not applicable in M1.

## Revisit when
- Mission duration exceeds hours at LEO altitude.
- Any lifetime, decay, or reentry question arises.
- Drag is planned for a later milestone.

## Related
- DR: DR-0002
- ADR: ADR-0003

---

# SCI-0005: Earth constants from WGS 84

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** All physics using Earth constants

## Assumption
- Geocentric gravitational constant **GM = 3.986004418×10¹⁴ m³/s²**.
- Reference (equatorial) radius **a = 6 378 137.0 m**.
- Both are WGS 84 defining parameters [NGA].
- Defined once in `tars/sim/constants.py` (`WGS84`) and recorded in every `SimulationStarted` event.

## Why we are making it
- DR-0003.
- An authoritative published standard. Its GM equals the IERS Conventions (2010) value 3.986004418×10¹⁴ m³/s² (TT-compatible) [IERS Table 1.1].

## Sources
- [NGA] (defining parameters table)
- [IERS] Table 1.1

## Known limitations / expected error
- GMAT's default Earth μ is 398600.4415 km³/s² [GMATVV]. That differs by 3×10⁻⁴ km³/s² (relative 7.5×10⁻¹⁰).
- The size of the period difference depends on how the orbit is defined. Both cases below are computed, not estimated, and corrected per external review REV-001.
  - Both tools place the orbit at the same radius, each with its own μ: about 2.0×10⁻⁶ s per orbit.
  - Both tools start from **the same Cartesian state**, as in our GMAT comparison: GMAT's SMA shifts by about 5 mm, ΔT/T ≈ 2·Δμ/μ, and the period shifts by about 8.1×10⁻⁶ s per orbit. That is **about 0.63 m along-track after 10 orbits**, comparable to the RK4 error at dt = 10 s.
- **GMAT validation cases must override Earth μ (and radius) to WGS 84.** Otherwise the comparison measures a configuration mismatch.

## Validation approach
- The GMAT script sets the constants explicitly.
- `gmat_m1.py compare` rejects any reference whose committed script differs from the script regenerated for the current scenario, or whose metadata constants differ from the scenario's. These are exact checks.
- GMAT's applied μ is evidenced by the initial-SMA and period differences. They are gated numerically: initial SMA difference ≤ 1e-6 m and GMAT vs Kepler ≤ 1e-4 m (**DR-0009**).

## Accepted discrepancy / tolerance
Zero: constants must match exactly in reference comparisons.

## Revisit when
- Adopting a gravity-field model with its own GM and reference radius (for example, EGM2008: a = 6 378 136.3 m). Those constants must then travel with the field model.

## Related
- DR: DR-0003
- ADR: ADR-0003

## Historical correction note (2026-10-15; DR-0024 Q3, approved by the Tech Lead)
The text above is the accepted M1 record and is left as written. This note corrects one statement in it.
- **Historical result (unchanged):** M1 and M2 use GM = 3.986004418×10¹⁴ m³/s² in the simulator and in every gating GMAT reference. The gate scripts set `Earth.Mu = 398600.4418` and use a point-mass force (`PointMasses = {Earth}`, no gravity file), so GMAT applies `Earth.Mu` (`toolbox/references/gmat/m1_two_body.script`, lines 6–9 and 25–26; the M2 scripts likewise).
- **Incorrect historical description:** "Its GM equals the IERS Conventions (2010) value 3.986004418×10¹⁴ m³/s² (**TT-compatible**) [IERS Table 1.1]".
- **Corrected interpretation:** IERS Conventions (2010) Table 1.1 labels 3.986004418×10¹⁴ m³/s² as **TCG-compatible**. §1.2 gives the **TT-compatible** value as 3.986004415×10¹⁴ m³/s² and says it "shall be used to compute orbits in a TT-compatible reference frame" (verified against TN36 ch. 1, working version 2017-11-16; DR-0024 §3.1). The numerical equality with the WGS 84 defining value is correct; only the time-scale label was wrong. Using the TCG-compatible value with TT-labelled time (SCI-0007) is a relative GM difference of 7.5×10⁻¹⁰, about 0.63–0.70 m along-track over 10 orbits at the reference orbit (VAL-0018).
- **Effect on prior acceptance decisions: none.** Every M1/M2 acceptance check compares the simulator against references using the identical GM. The label enters no computation, no threshold and no reference. The "Known limitations" paragraph above (GMAT default μ = 398600.4415) remains correct.
- **"Revisit when" above** ("adopting a gravity-field model with its own GM and reference radius"): evaluated for M3 in DR-0024 §3.5. M3 adopts one coefficient (EGM2008 C̄2,0), not a gravity-field model, and the Tech Lead decided to keep the WGS 84 GM and a (DR-0024 Q2, Q3). See SCI-0013.

---

# SCI-0006: Altitude measured above a spherical Earth

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** Initial conditions, telemetry, and termination checks

## Assumption
- Altitude h = |r| − a, where a = 6 378 137 m (SCI-0005).
- This is geocentric altitude above a sphere of equatorial radius. It is **not** geodetic height above the WGS 84 ellipsoid.
- "250 km orbit" means |r| = a + 250 km = 6 628 137 m.

## Why we are making it
- It is consistent with a point-mass Earth (SCI-0001) and needs no Earth-fixed frame (SCI-0003).

## Sources
- [NGA] (ellipsoid parameters a, 1/f = 298.257223563)

## Known limitations / expected error
- The WGS 84 polar radius is a(1 − f) ≈ 6 356 752 m.
- At high latitude, geodetic height above the ellipsoid therefore exceeds this spherical altitude by up to about 21 km.
- For the M1 orbit at i = 51.6°, reported altitude will differ from geodetic altitude by up to about 13 km near the latitude extremes. That is relevant when atmosphere models are introduced.

## Validation approach
Unit test: h(initial) = 250 000 m exactly.

## Accepted discrepancy / tolerance
Not applicable (definition).

## Revisit when
- An atmosphere model (density depends on geodetic height), ground track, or visibility calculation is introduced.

## Related
- SCI: SCI-0001, SCI-0005

---

# SCI-0007: Uniform simulation time from a labelled epoch

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** Time propagation

## Assumption
- Simulation time is a uniform count of SI seconds from a labelled epoch: 2026-01-01T00:00:00 TT (DR-0007). It behaves like Terrestrial Time.
- There are no leap seconds and no UTC/UT1 conversions.
- No physics in M1 depends on absolute epoch.

## Why we are making it
- Two-body point-mass dynamics are time-invariant, so the epoch affects nothing physical in M1.
- Using a uniform scale (TT) avoids leap-second discontinuities.

## Sources
- [IERS] Ch. 10 (time scales)
- [VAL] §3.5 (time systems)

## Known limitations / expected error
None in M1. Absolute time becomes physically meaningful with:
- Earth rotation (needs UT1)
- Sun/Moon ephemerides
- solar activity for drag

## Validation approach
- GMAT uses the same epoch, expressed in its TT format.
- The comparison is made on elapsed seconds.

## Accepted discrepancy / tolerance
Not applicable.

## Revisit when
- Earth rotation, ephemerides, or atmosphere models are introduced.

## Related
- DR: DR-0007
- ADR: ADR-0002

---

# M2 propulsion assumptions

Drafted at the M2 planning checkpoint and approved by the Tech Lead on 2026-10-09 (DR-0011, DR-0012, DR-0014).
- Engine, tank and burn **values** are configurable reference-case parameters (DR-0010), not assumptions. The assumptions below concern the *model form*.
- Numerical tolerances referenced as "per the approved M2 threshold DR" are **not yet set**: DR-0015 is conditionally approved, and REV-012 plus implementation measurements come first.

# SCI-0008: Ideal constant-thrust, constant-Isp engine; instantaneous on/off

**Status:** Active (approved via DR-0011, 2026-10-09)  
**Introduced:** 2026-10-09  
**Applies to:** M2 propulsion model

## Assumption
- While on, one engine delivers constant thrust F [N] at constant specific impulse Isp [s].
- Thrust rises from zero to F and falls back instantaneously at ignition and cutoff.
- There is no throttling, blow-down decay, minimum impulse bit, or pressure/temperature dependence.

## Why we are making it
- It gives exact analytic oracles: linear mass law and the rocket equation.
- It matches GMAT `ChemicalThruster` with only C1 and K1 non-zero.

## Sources
- [SUT] ch. 2–4
- [GMATMS] Eq. 4.112–4.115

## Known limitations / expected error
- Real start/stop transients last tens to hundreds of milliseconds. Pressure-fed systems lose thrust as the tank blows down.
- For a 77 s burn, transients shift total impulse by an amount of order the transient time over the burn time. That is a sub-percent effect, not modelled.

## Validation approach
- O1 (mass law) and O2 (rocket equation), exact to round-off.
- GMAT finite burn (VAL-0009).

## Accepted discrepancy / tolerance
Per the approved M2 threshold DR.

## Revisit when
- Throttling, pulse-mode attitude thrusters, or blow-down tanks are needed.

## Related
- DR-0011; VAL-0008, VAL-0009

---

# SCI-0009: Standard gravity converts Isp to exhaust velocity

**Status:** Active (approved via DR-0011, 2026-10-09)  
**Introduced:** 2026-10-09  
**Applies to:** M2 propulsion model

## Assumption
- Effective exhaust velocity is c = Isp·g0 with **g0 = 9.80665 m/s²**, the exact standard acceleration of gravity.
- Mass flow is ṁ = F/c.
- g0 is a unit-conversion convention, not the local gravity (≈ 9.07 m/s² at 250 km).

## Why we are making it
- It is the definition used with published Isp values.

## Sources
- [NIST-gn]
- [SUT] ch. 2

## Known limitations / expected error
- None for the definition itself.
- **GMAT's `ChemicalThruster.GravitationalAccel` defaults to 9.81 m/s².** If not overridden, propellant use differs by 0.034% and the trajectory diverges by 7.85 m in the M2 probe (VAL-0009).

## Validation approach
- Single named constant `STANDARD_GRAVITY`, with a grep test like the WGS 84 constants test.
- GMAT script configuration is checked exactly.

## Accepted discrepancy / tolerance
Zero: the constant must match exactly in reference comparisons.

## Revisit when
- Never for the definition. Revisit only if an engine data source quotes Isp in other units.

## Related
- DR-0011; VAL-0009

---

# SCI-0010: Variable-mass equation of motion a = F/m

**Status:** Active (approved via DR-0011, 2026-10-09)  
**Introduced:** 2026-10-09  
**Applies to:** M2 dynamics

## Assumption
- The spacecraft's acceleration is the thrust force divided by the current total mass, plus gravity: v' = −μr/|r|³ + (F/m)û.
- There is no ṁ·v term.

## Why we are making it
- This is the correct application of Newton's second law to a body that ejects mass. The exhaust momentum is already accounted for in the thrust F.
- The form d(mv)/dt = F introduces a fictitious, frame-dependent force [PM92].

## Sources
- [PM92]
- [CUR] ch. 11
- [SUT] ch. 4

## Known limitations / expected error
- None within the point-mass model.
- The GMAT Mathematical Specification (Eq. 4.2–4.3) is written in the d(mv)/dt form. GMAT's implementation was **measured** to integrate a = F/m (VAL-0009: SMA agreement 0.12 mm; the extra term would be about 0.95 m/s²).

## Validation approach
- O2 (rocket equation)
- O3 (free-space closed form)
- O9 (GMAT)

## Accepted discrepancy / tolerance
Per the approved M2 threshold DR.

## Revisit when
- Never for point-mass translational dynamics.

## Related
- DR-0011; VAL-0009

---

# SCI-0011: Instantaneous ideal pointing through the centre of mass

**Status:** Active (approved via DR-0011, DR-0012, 2026-10-09)  
**Introduced:** 2026-10-09  
**Applies to:** M2 thrust direction

## Assumption
- Thrust acts exactly along the commanded direction, evaluated from the current state at every derivative evaluation: prograde = +v/|v|, retrograde = −v/|v|, using ECI velocity.
- The line of action passes through the centre of mass.
- There are no attitude dynamics, pointing errors, or torques.

## Why we are making it
- It defines "prograde" operationally, for an ideal attitude controller tracking the velocity vector.
- It matches GMAT `Axes = VNB`.

## Sources
- [GMATMS] §4.2.7 (VNB)
- [VAL] ch. 3

## Known limitations / expected error
- Real vehicles have pointing error and slew limits.
- Holding the ignition direction instead changes SMA by 69 m for the M2 slice (VAL-0008), so the pointing model is material.

## Validation approach
- O7 sign/plane checks
- O9 GMAT VNB comparison

## Accepted discrepancy / tolerance
Per the approved M2 threshold DR.

## Revisit when
- Attitude dynamics, inertial-hold burns, or out-of-plane maneuvers are introduced.

## Related
- DR-0012; VAL-0008

---

# SCI-0012: Single tank, all propellant usable, instantaneous flame-out

**Status:** Active (approved via DR-0011, DR-0014, 2026-10-09)  
**Introduced:** 2026-10-09  
**Applies to:** M2 propellant accounting

## Assumption
- All loaded propellant is usable: no residuals, no ullage requirement, no mixture-ratio bookkeeping (one effective propellant mass).
- When it reaches zero, thrust stops instantaneously at the exact depletion time t_ign + m_prop/ṁ. Propellant never goes negative.

## Why we are making it
- It is the simplest physically consistent depletion behavior.
- It is exactly computable in advance, so integration steps can be split there.

## Sources
- [SUT] ch. 4 (propellant budget concepts)
- GMAT `ChemicalTank` documentation: GMAT raises an exception at depletion by default rather than modelling flame-out.

## Known limitations / expected error
- Real systems keep unusable residuals (typically a few percent) and sputter near depletion.
- Not GMAT-validatable (VAL-0009 finding 4); validated analytically only.

## Validation approach
- O1 at depletion
- Mission test `burn_to_depletion`

## Accepted discrepancy / tolerance
- Exact to round-off for the depletion time and propellant floor.
- **DR-0017 D1a (2026-10-10):** event times are float64. A depletion cutoff is the latest representable time not after depletion, so a burn-to-depletion can leave a residual of at most ṁ·2·ulp(cutoff). The residual is retained, not discarded, and its Δv effect is bounded by the DR-0017 timing budget (1e-7 m/s per burn). At mission times the residual is ~1e-14 kg.

## Revisit when
- Residual budgets, multiple tanks, or bipropellant mixture ratios matter.

## Related
- DR-0011, DR-0014

---

# SCI-0013: Earth J2 zonal field about the frame z axis (fixed pole)

**Status:** Approved (DR-0024, Tech Lead 2026-10-15); not implemented. Axis choice approved via DR-0026 D3, flagged for confirmation (DR-0024 Q4)  
**Status update (2026-10-15, append-only):** the "approved via DR-0026 D3" attribution above is withdrawn (review M3P2-F1). The owner decided DR-0024 Q4 explicitly: **the Earth-fixed +Z axis** is the common symmetry axis, with Earth-fixed and inertial representations kept distinct (DR-0024 Resolution, "Q4 coordinate conventions"). Whether that axis coincides with the frame z axis, as written below (DR-0028 A1, recommended), or follows the pole of date is **OPEN in DR-0028**.  
**Status update 2 (2026-10-15, append-only):** **DR-0028 APPROVED J-ax-1.** M3 uses a **non-rotating Earth-axis-aligned reference model**:
- its +Z axis coincides with Earth's symmetry/spin axis by assumption and is fixed in the inertial frame, so the "frame z axis" wording below holds;
- there is no Earth rotation angle, precession, nutation, polar motion or time-dependent orientation;
- it is **not** a physically accurate rotating terrestrial frame.

Limitations (DR-0028 Resolution):
- 117–123 m over 10 orbits against a pole-of-date Earth in 2026 (25 m at J2000), growing with time and epoch distance from J2000;
- no longitude, ground track, site visibility or local solar time;
- Earth-fixed navigation measurements, tesserals and MSIS-class atmospheres each need a separately authorized Earth-orientation model.

Conventions and tests: DR-0024 "Q4 coordinate conventions, revision 2" (FC-1…FC-10). Extension point: ADR-0009 item 17 (not implemented).  
**Status update 3 (2026-10-16, append-only; reviews M3P4-F1, M3P4-F2; DR-0028 Resolution amendment 1).** Two limitation statements in status update 2 are corrected. The approval and the model are unchanged.
- **Pole tilt (M3P4-F1).** With δ ≈ 0.15° the angle between the model axis and the real pole:
  - the inclination difference is bounded geometrically by δ;
  - the ascending-node difference is not. To first order (δ ≪ i), the node point moves along the orbit by up to δ/sin i, and the node longitude by up to δ|cot i|;
  - near-equatorial nodes are poorly conditioned or undefined;
  - the 117–123 m and 25 m figures are measurements for the VAL-0018 configuration only. No general growth law is claimed (the phrase "growing with time and epoch distance from J2000" in status update 2 is withdrawn).
- **Local solar time (M3P4-F2).** Local solar time does not need an Earth rotation angle: the angle cancels in the solar hour angle α_sc − α_Sun.
  - M3 lacks a solar ephemeris and a time convention for it, so it stays outside M3 scope.
  - Longitude, ground tracks and site visibility still need an Earth rotation angle, as stated.
  - No solar ephemeris, Earth-orientation provider or local-solar-time implementation is authorized.
**Introduced:** 2026-10-15  
**Applies to:** M3 physics configurations only. SCI-0001 and SCI-0004 remain Active for M1/M2 configurations.

## Assumption
- Gravity = point mass + the degree-2 zonal term: U = (μ/r)[1 − J2 (a/r)² P₂(z/r)], with the symmetry axis = the frame z axis (SCI-0003).
- μ = 3.986004418×10¹⁴ m³/s² and a = 6 378 137.0 m (WGS 84, SCI-0005, unchanged); **J2 = 1.0826261739×10⁻³** = −√5 C̄2,0 with the EGM2008 tide-free C̄2,0 = −0.484165143790815×10⁻³ [NGA Table 5.1].
- J2 is constant in time. No J3+, tesserals, tides, precession, nutation or polar motion.

## Why we are making it
- J2 is the dominant LEO perturbation (VAL-0007, VAL-0018: 741 km over 10 orbits).
- A fixed axis keeps the system autonomous (exact energy and h_z invariants) and the epoch metadata-only (SCI-0007).

## Sources
- [NGA] Table 3.1, Table 5.1; [IERS] TN36 ch. 1 and ch. 6 (tide systems); [CUR] §10.7; DR-0024 §3–§4.

## Known limitations / expected error
- The pole of date differs from frame z by about 0.15° in 2026: 117–123 m over 10 orbits against a pole-of-date model (25 m at J2000) [VAL-0018].
- Tide-free J2 omits the permanent tidal deformation (ΔJ2 ≈ 9.3×10⁻⁹; 6.7 m over 10 orbits against the zero-tide value).
- Mixing the EGM2008 C̄2,0 with the WGS 84 a and GM changes the J2 coefficient by 2.2×10⁻⁷ relative (DR-0024 §3.5; 0.16–0.18 m over 10 orbits).

## Validation approach
- DR-0025: invariants, secular rates, DOP853 (partially independent), GMAT exact configuration with a generated `.cof` carrying these constants (method decided after T0).

## Accepted discrepancy / tolerance
Not set. Thresholds come from a later threshold DR.

## Revisit when
- Ground tracks, node timing or navigation accuracy need the pole of date; higher harmonics are added.

## Related
- DR-0024, DR-0025, DR-0026; ADR-0009; VAL-0018.

---

# SCI-0014: Atmosphere rigidly co-rotating with Earth; no winds

**Status:** Approved (DR-0024 Q7, Tech Lead 2026-10-15); not implemented  
**Status update (2026-10-15, append-only):** the rotation axis is **the Earth-fixed +Z axis**, shared with J2 and the ellipsoid (DR-0024 Q4, owner decision). v_rel is evaluated with the frame transformations in DR-0024 "Q4 coordinate conventions" (FC-1…FC-9). Whether +Z coincides with the frame z axis, as written below, is **OPEN in DR-0028**.  
**Status update 2 (2026-10-15, append-only):** DR-0028 APPROVED J-ax-1, so +Z is the frame z axis, as written below.
- The co-rotation is a velocity field of the air in the inertial frame, v_air = ω_E Ẑ × r. It is not a rotating frame and needs no Earth rotation angle.
- The identity transformation between the inertial frame and the Earth-axis-aligned model has zero derivative. That never removes the ω_E Ẑ × r term (DR-0024 revision 2, FC-2(b)).  
**Introduced:** 2026-10-15  
**Applies to:** M3 drag

## Assumption
- v_rel = v − ω_E × r, with ω_E = 7.292115×10⁻⁵ rad/s about the frame z axis [NGA Table 3.1]. No winds.

## Why we are making it
- Ignoring rotation changes the 10-orbit trajectory by 40 km and is physically wrong (VAL-0018).

## Sources
- [NGA] Table 3.1; GMAT Mathematical Specification Eq. 4.73–4.74 (same form).

## Known limitations / expected error
- Real thermospheric winds are not modelled. The IERS ERA rate differs from the nominal ω_E by 2×10⁻⁸ relative (negligible).

## Validation approach
- Unit checks of v_rel; GMAT exact configuration (DR-0025).

## Accepted discrepancy / tolerance
Not set.

## Revisit when
- Winds or a pole-of-date Earth are modelled.

## Related
- DR-0024, SCI-0013, SCI-0016.

---

# SCI-0015: Static piecewise-exponential atmosphere, preserved as published

**Status:** Approved (DR-0024 Q5, Q5a, Q8, Q10, Tech Lead 2026-10-15); not implemented. Termination value and Q10 residual cells OPEN (DR-0027)  
**Status update (2026-10-15, append-only; DR-0027 resolved with conditions):**
- The GMAT R2026a table (sha256 `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`) is **pinned verbatim as the initial reference**, with the three disputed cells and the printed-edition uncertainty documented (DR-0027 B-1, B-2). No value is repaired or substituted (B-3). It is not claimed to agree with the printed textbook (B-5).
- The termination altitude is an **explicit per-scenario input, metres, geodetic, with no default**; no universal value (DR-0027 A-1…A-3). Ranges, crossing behaviour and boundary interactions are proposed at T0.
- **Domain behaviour is OPEN** (DR-0027 B-4). The sentence below, "Above the top band, the top band applies as the source defines", was an implementer statement, not an owner decision, and is withdrawn.
- **Correction (M3P2-F3):** the 0 km base-altitude discrepancy changes density by 0.13785 % throughout 0.010–25 km, not only below 10 m. The 25–800 km rows are the ones confirmed in all fields.  
**Introduced:** 2026-10-15  
**Applies to:** M3 drag

## Assumption
- ρ(h) = ρ₀,i exp(−(h − h₀,i)/H_i) in band i, with the tabulated values of the Vallado/GMAT exponential table (28 bands, 0–1000 km) **exactly as published**. Values are never altered to force continuity.
- Static: no diurnal, seasonal, solar-cycle or geomagnetic variation.
- A one-band subset (one row of the same table) is retained for analytic and unit tests.
- **No indefinite extrapolation below the modelled domain.** A run ends at an explicit validity boundary or termination event; its numerical value is OPEN (DR-0027 item A). Above the top band, the top band applies as the source defines.

## Why we are making it
- Deterministic, matchable exactly in GMAT, realistic profile shape (DR-0024 §4.3).

## Sources
- GMAT R2026a `EarthExponentialAtmosphereData.txt` (sha256 `75762f67…a85e`), citing Vallado 5th ed. §8.6.
- Verified against the author's published data file `ATMOSEXP.DAT` (CelesTrak/fundamentals-of-astrodynamics @ `49df047`) and the author's errata (DR-0024 §3.4): 25 of 28 rows identical; the 0 km base altitude, the 900 km scale height and the 1000 km row are residuals (DR-0027 item B).

## Known limitations / expected error
- **Discontinuous as published:** value jumps at every band boundary (largest +1.36×10⁻³ relative at 25 km; ≤ 9.6×10⁻⁵ from 30 km up) and a slope change at every boundary (DR-0024 §3.4).
- Real density at 250 km varies by a factor of about 3.5 with solar activity (VAL-0007). Lifetime predictions are indicative only.

## Validation approach
- Tests at and immediately around every band boundary; GMAT with the identical table file; boundary-appropriate convergence evidence (DR-0025 principles 4–5).

## Accepted discrepancy / tolerance
Not set.

## Revisit when
- Solar-activity dependence is needed (A4, NRLMSIS-class), or the printed table shows a difference.

## Related
- DR-0024, DR-0025, DR-0027.

---

# SCI-0016: Cannonball drag with current total mass

**Status:** Approved (DR-0024 Q9 principle, Tech Lead 2026-10-15); not implemented. Reference-scenario values DEFERRED to the T0 checkpoint  
**Introduced:** 2026-10-15  
**Applies to:** M3 drag

## Assumption
- a_d = −½ ρ (C_d A / m) |v_rel| v_rel. C_d and the reference area A are constant, attitude-independent **scenario inputs**. No lift.
- m is the spacecraft's current total mass (dry + propellant, the M2 rule) at every derivative evaluation.

## Why we are making it
- The simplest free-molecular drag model; matches GMAT `DragModel = Spherical`.

## Sources
- GMAT Mathematical Specification Eq. 4.73–4.74; [MG] §3.5 (secondary).

## Known limitations / expected error
- Real C_d and area depend on attitude, composition and altitude. B ± 1 % moves the 10-orbit trajectory by 4.8 km (VAL-0018).
- The free-molecular assumption fails at low altitude; the validity floor is OPEN (DR-0027 item A).

## Validation approach
- Direction and energy-decrease checks; decay-rate estimates; DOP853; GMAT (DR-0025).

## Accepted discrepancy / tolerance
Not set.

## Revisit when
- Attitude-dependent area, lift, or a body model is needed.

## Related
- DR-0024, DR-0026, SCI-0010, SCI-0014, SCI-0015.

---

# SCI-0017: Density height is geodetic height above the WGS 84 ellipsoid

**Status:** Approved (DR-0024 Q6, Tech Lead 2026-10-15); not implemented  
**Status update (2026-10-15, append-only):** the ellipsoid axis is **the Earth-fixed +Z axis** (DR-0024 Q4, owner decision); geodetic height is evaluated from the Earth-fixed position (DR-0024 "Q4 coordinate conventions", FC-4). Whether +Z coincides with the frame z axis, as written below, is **OPEN in DR-0028**. Geodetic height is also the convention of the per-scenario termination altitude (DR-0027 A-2).  
**Status update 2 (2026-10-15, append-only):** DR-0028 APPROVED J-ax-1. The ellipsoid is evaluated about the frame z axis of the non-rotating Earth-axis-aligned model, as written below. The transformation is the identity, so the "Earth-fixed position" of the previous update is the inertial position itself. Geodetic height is axisymmetric about +Z (FC-4), and no longitude or rotation angle is involved.  
**Introduced:** 2026-10-15  
**Applies to:** M3 atmosphere density only. SCI-0006 (reported altitude, impact) is unchanged for v1/v2.

## Assumption
- The density model is evaluated at the geodetic height above the WGS 84 ellipsoid (a = 6 378 137.0 m, 1/f = 298.257223563 [NGA]), with the ellipsoid axis = the frame z axis.

## Why we are making it
- Physically meaningful input; the author's own reference code uses geodetic height for this table (DR-0024 §3.4). Spherical height would move the 10-orbit trajectory by 74 km (VAL-0018).

## Sources
- [NGA] Table 3.1; DR-0024 §4.5.

## Known limitations / expected error
- The cartesian-to-geodetic conversion is a numerical algorithm with its own error; its verification source is chosen at T0 (DR-0025 Q-G2-7).

## Validation approach
- Published geodetic test points (source at T0); GMAT with WGS 84 flattening (DR-0025).

## Accepted discrepancy / tolerance
Not set.

## Revisit when
- A pole-of-date Earth is modelled.

## Related
- DR-0024, SCI-0006, SCI-0013.
