# Scientific Assumptions Registry

This registry distinguishes deliberate model simplifications from bugs and unknowns. Use stable IDs such as `SCI-0001` and the structure in `toolbox/templates/science-assumption.md`.

## Index
| ID | Title | Status | Applies to |
|---|---|---|---|
| SCI-0001 | Earth gravity is a Newtonian point mass | Active | M1 force model |
| SCI-0002 | Restricted two-body: spacecraft is a massless point | Active | M1 dynamics |
| SCI-0003 | Earth-centred J2000-aligned frame treated as inertial | Active | M1 state/frame |
| SCI-0004 | No perturbing forces (drag, SRP, third body, tides, relativity) | Active | M1 force model |
| SCI-0005 | Earth constants from WGS 84 | Active | All physics |
| SCI-0006 | Altitude measured above a spherical Earth | Active | Reporting/initial conditions |
| SCI-0007 | Uniform simulation time from a labelled epoch | Active | Time propagation |
| SCI-0008 | Ideal constant-thrust, constant-Isp engine; instantaneous on/off | Proposed (DR-0011) | M2 propulsion |
| SCI-0009 | Standard gravity g0 = 9.80665 m/s² converts Isp to exhaust velocity | Proposed (DR-0011) | M2 propulsion |
| SCI-0010 | Variable-mass equation of motion a = F/m (no ṁ·v term) | Proposed (DR-0011) | M2 dynamics |
| SCI-0011 | Instantaneous ideal pointing through the centre of mass; no attitude dynamics | Proposed (DR-0011, DR-0012) | M2 thrust direction |
| SCI-0012 | Single tank, all propellant usable, instantaneous flame-out at depletion | Proposed (DR-0011, DR-0014) | M2 propellant |

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

# SCI-0002: Restricted two-body — spacecraft is a massless point

**Status:** Active  
**Introduced:** 2026-10-05  
**Applies to:** M1 dynamics

## Assumption
- The spacecraft's mass is negligible compared with Earth's. Earth's acceleration toward the spacecraft is ignored.
- The equation of motion uses μ = G·M_Earth, not G(M_Earth + m).
- The spacecraft is a point (no attitude, no extent).

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

# Proposed M2 assumptions (pending DR-0011, DR-0012, DR-0014)

These entries are drafts written at the M2 planning checkpoint (2026-10-09). They become **Active** only when the referenced Decision Requests are approved. Until then, no code depends on them. On approval, SCI-0002 is revised: the spacecraft remains negligible relative to Earth (μ, not G(M+m)), but its mass now determines thrust acceleration.

# SCI-0008: Ideal constant-thrust, constant-Isp engine; instantaneous on/off

**Status:** Proposed (DR-0011)  
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

**Status:** Proposed (DR-0011)  
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

**Status:** Proposed (DR-0011)  
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

**Status:** Proposed (DR-0011, DR-0012)  
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

**Status:** Proposed (DR-0011, DR-0014)  
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
Exact to round-off for the depletion time and propellant floor.

## Revisit when
- Residual budgets, multiple tanks, or bipropellant mixture ratios matter.

## Related
- DR-0011, DR-0014
