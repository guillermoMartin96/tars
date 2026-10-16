# Decision Request: realization of the M3 Earth-fixed frame (follow-up to DR-0024 Q4)

**Status:** RESOLVED — APPROVED: J-ax-1, with requirements (Tech Lead, 2026-10-15, "M3 Planning — Resolve Review 03 and DR-0028", section 2). See "Resolution"; where the body below differs from the Resolution, the Resolution governs. No Earth-orientation implementation is authorized.  
**Resolution amendment 1 (2026-10-16, append-only):** two limitation statements in the Resolution are corrected under reviews M3P4-F1 (node error bound) and M3P4-F2 (local solar time). The decision itself (A, B, R-1…R-4) is unchanged. See "Resolution amendment 1" at the end.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A. Raised by the Tech Lead's approval of DR-0024 Q4 (2026-10-15, "M3 planning checkpoint continuation", section 1). That approval names a physical axis (the Earth-fixed +Z axis) but no option from DR-0024 §4.1 (J-ax-1, J-ax-2, J-ax-3).
- Source keys are defined in DR-0024 §3.1. Coordinate conventions: DR-0024 Resolution, "Q4 coordinate conventions".

Nothing here is implemented. No value below is a default.

## Problem
The owner approved: "Use the Earth-fixed +Z axis as the common physical symmetry/rotation axis for J2, the reference ellipsoid, and atmospheric rotation", and required the Earth-fixed and inertial representations to be kept distinct, with correct transformations between them.

Two things that approval does not fix are needed before T1:
- **A. How the Earth-fixed +Z axis is placed in the inertial frame** (SCI-0003, EarthMJ2000Eq-aligned). In the real Earth, the Earth-fixed (ITRF) +Z axis is not the inertial z axis: precession, nutation and polar motion put it about 0.15° away in 2026 (DR-0024 §3.3, §4.1). DR-0024 J-ax-1 *defines* a model Earth-fixed frame whose +Z coincides with the inertial z axis. J-ax-2 and J-ax-3 tie it to the real pole of date. The approval text fits J-ax-1 (with a model-defined Earth-fixed frame) and J-ax-3 (the real ITRF frame) equally.
- **B. The Earth rotation angle θ(t)** that relates the two representations about +Z, if any M3 output is expressed in Earth-fixed coordinates.

## Facts
- **[derived] Under J-ax-1 none of the approved M3 physics depends on θ(t).** J2, the WGS 84 ellipsoid and a rigidly co-rotating atmosphere are all axisymmetric about +Z. The J2 acceleration, the geodetic height and v_rel = v − ω_E × r are therefore the same whether they are computed directly in the inertial frame or through an Earth-fixed frame rotated about +Z by any angle. This is a testable identity (FC-3, FC-4 and FC-2 in DR-0024's coordinate conventions).
- **[derived] Under J-ax-2 or J-ax-3 that is no longer true.** The epoch becomes physical (SCI-0007 changes), and J-ax-3 needs time-scale conversions and Earth Orientation Parameter data. DR-0024 §4.1 and §5 give the costs; J-ax-3 is the option DR-0024 did not recommend.
- **[measured, VAL-0018] Effect of the choice:** 117 m (J2 only, 10 orbits) between frame z and the 2026 mean pole. GMAT in true-of-epoch axes fixed at the epoch reproduces the J-ax-1 model to 0.19 m.
- **[fact] No M3 force or approved output needs θ(t) under J-ax-1.** It is needed only if an Earth-fixed position (for example longitude or a ground track) is reported or tested. No such output is approved; per-sample telemetry (DR-0026 Q-G3-7) is NOT AUTHORIZED.

## Options
- **A1 — Model-defined Earth-fixed frame (J-ax-1).** +Z_EF ≡ +z of the inertial frame, by definition. Pole motion is a documented limitation (SCI-0013).
- **A2 — Mean pole of date (J-ax-2).**
- **A3 — Real ITRF +Z (J-ax-3)**, with EOP data.
- **B1 — No θ(t) in M3.** Earth-fixed coordinates appear only inside the frame-consistency tests, which use arbitrary test angles. Any reported Earth-fixed quantity needs a later decision.
- **B2 — A pinned convention now**, for example θ(t₀) = 0 at the scenario epoch with ω_E from DR-0024 Q7. This is a model convention, not the real Earth rotation angle, and would be labelled as such.

## Recommendation
- **A1 and B1.** These are the options DR-0024 put forward and review 02 asked the owner to confirm. They keep the approved physics autonomous and time-invariant. The implementer does not treat them as approved: the approval text does not name them.

## Impact
- **Architecture:** A1/B1 add one pinned axis definition and test-only rotations. A2/A3 make the epoch physical and add an Earth-orientation component (DR-0026 §6).
- **Science/validation:** SCI-0013, SCI-0014, SCI-0017; the DR-0025 GMAT method (Q-G2-1, deferred to T0).
- **Dependencies:** none for A1; EOP data for A3.
- **Reversibility:** high before T1.

## Blocked work
- T1 (J2 force) and T2 (drag, geodetic height): the axis realization fixes their equations.

## Work continuing independently
- Planning documentation. T0 has not started and needs the Tech Lead's explicit approval of this checkpoint. If T0 is approved before this DR is answered, its spike configurations must label the realization they assume.

## Requested response
`A1`/`A2`/`A3` and `B1`/`B2 <convention>`, or `discuss`.

## Resolution
**Decision:** **APPROVED: J-ax-1** (Tech Lead, 2026-10-15, instruction "M3 Planning — Resolve Review 03 and DR-0028", section 2). "For M3, use a simplified nonrotating Earth-axis-aligned reference model." Recorded by the implementer; no item below was decided by the implementer.

| # | Item | Status |
|---|---|---|
| A | **J-ax-1.** The model's +Z axis is defined, **by assumption**, to coincide with the selected Earth symmetry/spin axis, and that axis is **fixed in the M3 inertial frame** (SCI-0003). A2 (mean pole of date) and A3 (ITRF / full Earth orientation) are not adopted for M3 | APPROVED |
| B | **No Earth rotation angle is required for M3** (option B1). Option B2 (a pinned θ(t) convention) is not adopted | APPROVED |
| R-1 | No time-dependent Earth orientation, precession, nutation or polar motion | APPROVED (requirement) |
| R-2 | The simplified frame is **not identified as a physically accurate rotating Earth-fixed terrestrial frame**. Records call it the "non-rotating Earth-axis-aligned reference model" (EA), not ITRF, ECEF or "Earth-fixed" without qualification | APPROVED (requirement) |
| R-3 | Its approximation, limitations and implications for future mission capabilities are documented (below; SCI-0013) | APPROVED (requirement); done |
| R-4 | A clear architectural extension point for future Earth-fixed frame transformations is preserved (below; ADR-0009 item 17) | APPROVED (requirement); recorded, not implemented |
| — | **No additional Earth-orientation implementation is authorized** | NOT AUTHORIZED |

**What the model is.**
- **Frames and transformation:** EA and the inertial frame I share their axes; R_EA←I is the constant identity, so its derivative is zero (DR-0024 "Q4 coordinate conventions, revision 2").
- **Physics on that axis:**
  - J2, the WGS 84 ellipsoid (geodetic height) and the atmosphere's rigid rotation (v_air = ω_E Ẑ × r) all use this +Z.
  - Atmospheric co-rotation (DR-0024 Q7) is a velocity field of the air in I, not a rotating frame, so it needs no rotation angle.
- **Unchanged:** the approved constants (GM, a, J2, 1/f, ω_E) and every DR-0024/DR-0027 atmosphere constraint.

**Approximation and limitations.**
- **The real spin axis is not fixed in I.**
  - Precession and nutation move the pole of date about 0.15° (θ_A = 521″, DR-0024 §3.3) from the EarthMJ2000Eq z axis in 2026. Polar motion adds a further, smaller wander, not quantified by the project.
  - Measured effect (VAL-0018, J2 only, 53 700 s): **117 m** against a 2026 mean-pole model, **25 m** at J2000, and **123.5 m** against GMAT in EarthMJ2000Eq axes. GMAT reproduces the M3 model to 0.19 m when states are exchanged in its true-of-epoch axes fixed at the epoch.
- **Accumulation:** node and inclination geometry relative to the true equator are offset by up to the pole offset, and the error grows with propagation time and with distance of the epoch from J2000.
  - **Superseded by Resolution amendment 1, item 1 (review M3P4-F1).** Only the inclination difference is bounded by the pole offset. The ascending-node difference is not, and the growth statement was not measured. The sentence above is kept as originally written.
- **No longitude, no ground position:** without an Earth rotation angle the model has no terrestrial longitude, so it cannot give sub-satellite points, ground tracks, site visibility or local solar time.
  - **Partly superseded by Resolution amendment 1, item 2 (review M3P4-F2).** The restriction on longitude, sub-satellite points, ground tracks and site visibility stands. Local solar time does not need an Earth rotation angle; M3 lacks it for other reasons. The sentence above is kept as originally written.
- **Not a terrestrial frame:** the model must not be used where an ITRF/ECEF frame is meant.

**Implications for future mission capabilities.** Each of the following needs a separately authorized Earth-orientation model; none is enabled by M3:
- ground tracks, ground-station or site visibility windows, and landing or re-entry footprints;
- navigation using Earth-fixed measurements (GNSS in ITRF, ground-station range/Doppler);
- node-timing or orbit-determination comparisons with real-world data beyond the stated error;
- longitude-dependent gravity (tesserals) or a time- and location-dependent atmosphere (MSIS-class).

The M5 Mission Laboratory can compare candidate maneuvers within the model. Absolute geographic statements are out of scope.

**Extension point (R-4; design record only).**
- The axis is part of the pinned physics configuration under a versioned model identifier. Its name is chosen at T1 design, under DR-0026's versioning rule.
- Forces and the density component read the axis, and any future orientation, only through the immutable force-evaluation context and physics configuration (ADR-0009). They never construct it themselves.
- A future Earth-orientation model would be added as a **new versioned component** (an injected, immutable orientation provider, as DR-0026 §5.7 anticipated). It would come with:
  - its own Decision Request;
  - the general velocity relation v_B = R v_A + Ṙ r_A;
  - frame-consistency checks FC-9 and FC-10.
- Existing M3 model versions are retained under the D3 retention rule.
- **Nothing in this extension point is implemented or authorized now.**

**Reasoning/notes:** the decision matches the recommendation in this request (A1, B1) and the realization the M3 planning experiments measured against GMAT.

**Follow-up:**
- DR-0024 "Q4 coordinate conventions, revision 2" and FC-1…FC-10.
- SCI-0013, SCI-0014 and SCI-0017 status updates; ADR-0009 item 17.
- T1/T2 are no longer blocked by this DR; they remain NOT AUTHORIZED.

## Resolution amendment 1 (2026-10-16; reviews M3P4-F1 and M3P4-F2)
**Authority:** Tech Lead, instruction "M3 Planning — Review 04 Corrections and Final Verification" (I-4), section 1. That instruction authorizes these two corrections only.
- **The decision is unchanged.** J-ax-1 stands: R_EA←I is the constant identity, atmospheric co-rotation is a velocity field of the air, there is no Earth rotation angle, and A, B and R-1…R-4 are as resolved.
- **History is preserved.** The two corrected bullets stay in "Approximation and limitations" exactly as first written, each followed by a pointer to this section.
- **Sources:**
  - [McK] D. P. McKinley, "Long Term Mean Local Time of the Ascending Node Prediction", a.i. solutions / NASA GSFC, NTRS 20080012667, §II. PDF sha256 `542421d3…f475c`, read 2026-10-16.
  - Everything else is derived geometry, checked numerically by `docs/science/experiments/m3-planning/dr0028_node_sensitivity.py` (output `dr0028_node_sensitivity_results.json`; a rerun is byte-identical).

### Item 1 (M3P4-F1): pole tilt, inclination and ascending node
Replaces the "Accumulation" bullet.

**Notation.**
- δ is the angle between the model's +Z axis and the real spin axis. It is about 0.15° in 2026 (θ_A = 521″, DR-0024 §3.3) and depends on the epoch.
- ĥ is the orbit's unit angular-momentum vector.
- i is the inclination and Ω the ascending-node longitude. Each is measured in the frame named.
- All angles are in radians in the formulas below. Every estimate is linear in δ, so degrees may be used consistently.

**Geometric bound: exact, for any δ and any orbit.**
- The inclination is the angle between ĥ and the pole: i = ∠(ĥ, pole).
- Two poles δ apart therefore give |i_EA − i_true| ≤ δ, by the triangle inequality on the unit sphere. The bound is attained for a suitable tilt direction.
- Numerical check: the largest |Δi|/δ found was 1.0, both for δ = 0.15° over 8 inclinations × 360 tilt azimuths and for δ = 5° over a 37 × 36 grid. It never exceeded 1.

**First-order estimates: approximations, not bounds.**
These hold for δ ≪ i and δ ≪ 180° − i, that is, away from the near-equatorial singular configurations. They assume a tilt by δ about an equatorial axis at azimuth φ.

| Quantity | Estimate | Largest value over φ |
|---|---|---|
| Inclination change Δi | δ cos(Ω − φ) | δ (consistent with the exact bound) |
| Node-point displacement along the orbit | δ \|sin(Ω − φ)\| / sin i | **δ / sin i** |
| Node-longitude change ΔΩ, each frame measuring from its own x axis | −δ cot i sin(Ω − φ) | δ \|cot i\|, which is ≤ δ / sin i |

- **The node error is amplified by up to about 1/sin i.** It exceeds δ at every inclination below 90° (or above 90° for retrograde orbits).
- **Two node measures.** δ/sin i is the envelope: it is how far the node point moves along the orbit. The node *longitude* moves by at most δ|cot i|.
- **Node longitude depends on convention.** It also depends on where each frame puts its longitude origin, its x axis or equinox. The estimate above assumes the origin is carried by the same rotation, as in review 04's example. Another origin, such as an equinox of date, adds a convention-dependent term.
- **Numerical agreement (δ = 0.15°):**
  - the swept maxima of ΔΩ/δ and of the node-point shift/δ agree with |cot i| and 1/sin i to better than 0.4 % at every swept inclination (1°, 5°, 10°, 30°, 51.6°, 120°, 170°);
  - at i = 90°, ΔΩ is second order (6.5e-4 δ) and the node point moves by δ.

**Review 04 counterexample: preserved, assumptions verified.**
- **Assumptions:**
  - ĥ = (sin 30°, 0, cos 30°), so i = 30° and the node is at 90°;
  - the tilted components are R ĥ with R = Rx(−0.15°), a passive rotation about the common x axis, so φ = 0 and x_B = x_A;
  - Ω = atan2(h_x, −h_y), measured from each frame's own x axis.
- **Results (independent recomputation):**
  - the node moves to **90.2598055437°**, so ΔΩ = 0.2598055°, larger than δ = 0.15°;
  - the first-order δ cot i is 0.2598076°;
  - the node point moves 0.2999979° along the orbit, against δ/sin i = 0.30°;
  - Δi = 3.4e-4°. This is second order, because this tilt axis is perpendicular to the line of nodes.
- **Conclusion:** the review's value is the node-longitude measure, and it is confirmed exactly.

**Near-equatorial orbits.**
- As i → 0° (or 180°), 1/sin i → ∞. The node is poorly conditioned, and it is undefined for an exactly equatorial orbit.
- When i ≤ δ, the orbit can be equatorial in one frame, or its node can jump by up to 180°.
- Measured, δ = 0.15°, largest |ΔΩ| over tilt azimuths:

| Inclination | Largest \|ΔΩ\| | Note |
|---|---|---|
| 0.3° | 30.0° | |
| 0.15° | 89.5° | node undefined at one sampled azimuth |
| 0.1° | 180° | |

- **No node statement is made for such orbits.**

**Trajectory difference.**
- The accumulated position difference depends on the orbit, the propagation duration and the epoch.
- The project has measured it only for the VAL-0018 configuration (250 km circular, i = 51.6°, J2 only, 53 700 s):
  - 117 m against a 2026 mean-pole model;
  - 25 m at J2000;
  - 123.5 m against GMAT in EarthMJ2000Eq axes.
- No general bound or growth law is claimed.

### Item 2 (M3P4-F2): local solar time
Replaces the words "or local solar time" in the "No longitude, no ground position" bullet.

**What still needs an Earth rotation angle (unchanged).** Terrestrial longitude, sub-satellite points, geographic ground tracks and site or ground-station visibility.

**Local solar time does not inherently need one.**
- θ is the Earth rotation (sidereal) angle, and α is right ascension in one consistent equatorial frame.
- The spacecraft's sub-point has east longitude λ = α_sc − θ, and the sub-solar point has λ_Sun = α_Sun − θ.
- The Sun's hour angle at the spacecraft's meridian is therefore H = λ − λ_Sun = α_sc − α_Sun, and **θ cancels**.
- The local apparent solar time is (12 h + H / (15°/h)) mod 24 h.
- At the ascending node, α_sc = Ω. With the mean Sun in place of the true Sun this gives the mean local time of the ascending node, which [McK] §II defines as "the angle between the orbit's ascending node and the mean Sun". Neither the equation nor the definition contains θ.

**What M3 lacks.**
- **A solar ephemeris:** α_Sun at each simulation time, in the same equatorial frame as α_sc (the M3 inertial frame I).
- **A time convention connecting simulation time to that ephemeris.** SCI-0007 labels the epoch (2026-01-01T00:00:00 TT), but no M3 model consumes it. Making the epoch an ephemeris argument would be a model change.
- **For mean local time:** a mean-Sun (equation-of-time) convention.
- **No M3 force needs local solar time.** The approved atmosphere is static, with no diurnal variation (DR-0024 §10).

**Scope.**
- Local solar time and other Sun-relative geometry remain **outside M3 scope**.
- They would need a separately authorized solar ephemeris and time convention. They would not need an Earth-orientation model.
- **No solar ephemeris, Earth-orientation provider or local-solar-time implementation is authorized.**
