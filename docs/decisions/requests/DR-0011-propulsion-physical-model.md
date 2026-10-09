# Decision Request: Propulsion physical model

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion ([plan](../../milestones/M2-propulsion.md))

## Problem
M2 needs a defined engine and mass model before any propulsion code is written (playbook/science.md: "never invent scientific behavior"). The fidelity choices are material: they decide which analytic oracles exist and what GMAT can confirm.

## Background (what the physics says)
- **Specific impulse** relates thrust to propellant mass flow: F = ṁ·Isp·g0. Isp is quoted in seconds by convention, so g0 is a fixed conversion constant, the standard acceleration of gravity **g0 = 9.80665 m/s²** (exact by definition). It is not the local gravity. [SUT] ch. 2; [NIST].
- **Mass flow**: ṁ = F / (Isp·g0). With constant F and Isp, mass falls linearly in time.
- **Equation of motion with changing mass.** For a rocket, Newton's second law in the form d(mv)/dt = F is a well-known misuse: it adds a spurious −ṁ·v term that depends on the observer's frame. The correct form for the vehicle is m·dv/dt = F_thrust + F_ext, so **a = F/m + gravity**. [PM92]; [CUR] ch. 11.
  - GMAT's Math Spec (Eq. 4.2–4.3) is written in the d(mv)/dt form. VAL-0009 measured that GMAT's code integrates a = F/m.
- **Rocket equation** (consequence, not an input): Δv_ideal = Isp·g0·ln(m0/mf) for the thrust-only velocity change, independent of direction history and gravity. It gives an exact oracle for the integrated thrust acceleration. [SUT] ch. 4; [CUR] ch. 11.

## Constraints
- Must have analytic oracles and a GMAT-supported configuration (DR-0015).
- Deterministic and provider-independent; no new dependency.
- Prototype bar: simplifications are allowed if they are explicit and registered.

## Options
### A — Ideal constant-thrust, constant-Isp engine; propellant mass integrated; instantaneous on/off (recommended)
- One engine. Constant F and Isp while on. No startup/shutdown transients, minimum impulse bit, throttling, or pressure blow-down.
- Thrust acts through the centre of mass (no torque).
- Spacecraft mass m = m_dry + m_prop. m_prop is a simulator-owned state with dm_prop/dt = −F/(Isp·g0) while the engine is on.
- Propellant cannot go below zero: depletion is an exact flame-out time (DR-0014).
- a = F/m along the commanded direction (DR-0012).

**Pros**
- Exact oracles: propellant used = ṁ·T exactly; Tsiolkovsky for sensed Δv; free-space closed-form motion.
- Matches GMAT's `ChemicalThruster` with only C1/K1 non-zero (VAL-0009: 3e-8 kg, 0.12 mm SMA).
- RK4 integrates the linear mass law exactly (VAL-0008: ≤ 5e-12 kg).

**Cons**
- Real engines have transients (tens to hundreds of ms) and blow-down thrust decay. These are sub-percent impulse effects for a 77 s burn, but not zero.

### B — A plus throttle (0 < k ≤ 1, scaling F and ṁ together)
**Pros**
- Useful later for fine control.

**Cons**
- Not needed for the slice. Adds a command parameter and a validation dimension with no new physics proof.

### C — Pressure/temperature-dependent thrust and Isp (GMAT C1–C16/K1–K16 polynomials, blow-down tank)
**Pros**
- Higher fidelity; GMAT supports it.

**Cons**
- Needs real engine coefficient data we do not have.
- Removes the exact oracles. Out of proportion for the first propulsion milestone.

## Recommendation
**Option A.** Throttling (B) and pressure models (C) are recorded as reconsider triggers. g0 is added to `tars/sim/constants.py` as a named constant (`STANDARD_GRAVITY = 9.80665`), never as a literal elsewhere.

## Proposed scientific assumptions (registry entries drafted, status Proposed)
- SCI-0008 Constant-thrust, constant-Isp ideal engine; instantaneous on/off.
- SCI-0009 Standard gravity g0 = 9.80665 m/s² converts Isp to exhaust velocity.
- SCI-0010 Variable-mass equation of motion a = F/m (no ṁ·v term).
- SCI-0011 Instantaneous pointing, thrust through the centre of mass, no attitude dynamics (also DR-0012).
- SCI-0012 Single tank; all loaded propellant usable; instantaneous flame-out at depletion.
- SCI-0002 needs a wording revision on approval: the spacecraft is still negligible relative to Earth (μ, not G(M+m)), but it now has a mass that matters for thrust acceleration.

## Impact
- Architecture: the integrated state gains mass (DR-0013).
- Science/validation: enables the rocket-equation, mass-law and free-space oracles; GMAT comparable with `GravitationalAccel = 9.80665`.
- Dependencies: none.
- Development effort: low.
- Token/compute impact: negligible.
- Reversibility: high. Engine parameters sit behind a model object; B and C would extend it.

## Blocked work
- `tars.sim.propulsion` implementation and its unit tests.

## Work continuing independently
- Simulator step-splitting refactor with an M1 byte-identity guard (after DR-0013).
- REV-012 investigation.

## Requested response
`A` / `A+B` / `C` / `discuss`.

## Resolution
**Decision:** <fill after response>  
**Reasoning/notes:** ...  
**Follow-up:** ...

## Sources
- **[SUT]** G. P. Sutton, O. Biblarz, *Rocket Propulsion Elements*, 9th ed., Wiley, 2017. Ch. 2 (Isp, F = ṁ·Isp·g0), ch. 4 (flight performance, rocket equation).
- **[CUR]** H. D. Curtis, *Orbital Mechanics for Engineering Students*, 3rd ed., 2014. Ch. 6 (impulsive and non-impulsive orbital maneuvers), ch. 11 (rocket vehicle dynamics).
- **[PM92]** A. R. Plastino, J. C. Muzzio, "On the use and abuse of Newton's second law for variable mass problems", *Celestial Mechanics and Dynamical Astronomy* 53, 227–232 (1992). doi:10.1007/BF00052611
- **[NIST]** NIST CODATA: standard acceleration of gravity g_n = 9.806 65 m s⁻² (exact; adopted by the 3rd CGPM, 1901). https://physics.nist.gov/cgi-bin/cuu/Value?gn
- **[GMATMS]** GMAT R2026a Mathematical Specification (draft), §4.1.1 and §4.2.7 (Eq. 4.112–4.115); GMAT R2026a help, `ChemicalThruster` (`GravitationalAccel` default 9.81 m/s²) and `ChemicalTank` (`AllowNegativeFuelMass`). Bundled with the local install.
- VAL-0008, VAL-0009 (`docs/science/validation.md`).
