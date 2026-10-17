# Decision Request: realization of the M3 Earth-fixed frame (follow-up to DR-0024 Q4)

**Status:** RESOLVED — APPROVED: J-ax-1, with requirements (Tech Lead, 2026-10-15, "M3 Planning — Resolve Review 03 and DR-0028", section 2). See "Resolution"; where the body below differs from the Resolution, the Resolution governs. No Earth-orientation implementation is authorized.  
**Resolution amendment 1 (2026-10-16, append-only):** two limitation statements in the Resolution are corrected under reviews M3P4-F1 (node error bound) and M3P4-F2 (local solar time). The decision itself (A, B, R-1…R-4) is unchanged. See "Resolution amendment 1" at the end.  
**Resolution amendment 2 (2026-10-16, append-only):** the signs of two first-order formulas in amendment 1, item 1, are corrected under review M3P5-F1. Magnitudes, bounds and the decision are unchanged. See "Resolution amendment 2" at the end.  
**Resolution amendment 3 (2026-10-16, append-only):** under review 06 (M3P6-F1, F2, F3), the line-of-nodes exact result is given its domain and the full identity, the 180° node discontinuity is asserted, and the verification script's angle wrapping is made to match the documented (−π, π]. The signed formulas, the convention and the decision are unchanged. See "Resolution amendment 3" at the end.  
**Resolution amendment 4 (2026-10-16, append-only):** under review 07 (M3P7-F1), the wrapping guarantee is restricted to finite angles, and non-finite inputs raise ValueError. Finite-input behaviour, the signed formulas, the convention and the decision are unchanged. See "Resolution amendment 4" at the end.  
**Resolution amendment 5 (2026-10-16, append-only):** under review 08 (M3P8-F1), the verification script rejects non-finite values before every comparison and requires a minimum number of valid samples for each formula's order and sign checks; a bounded audit applies the same rule to the exact properties. All finite results, the signed formulas, the convention and the decision are unchanged. See "Resolution amendment 5" at the end.  
**Resolution amendment 6 (2026-10-17, append-only):** under review 09 (M3P9-F1, F2, F3), new mutants make the oracle ±∞ rejection and each formula's order and sign assertions load-bearing for their own reason, and E3 and E4 each gain a mutant; the file-level mutation check now accepts a detection only for its declared reason. No check, formula, tolerance, finite result or decision is changed. See "Resolution amendment 6" at the end.  
**Resolution amendment 7 (2026-10-17, append-only):** under review 10 (M3P10-F1, F2), the mutation check no longer accepts an exception raised inside a built-in mutant as evidence of a removed assertion, except where an explicit allowance names the mutant, type, message and call stack; the 18 assertions that were not individually load-bearing are classified, and the six of category A gain mutants. No check, formula, tolerance, finite result or decision is changed. See "Resolution amendment 7" at the end.  
**Resolution amendment 8 (2026-10-17, append-only):** under review 11 (M3P11-F1, F2), a built-in mutant's defect counts as exercised only when exactly its declared intended defect occurs (not any difference), and the mutation check establishes that by an independent probe before accepting a detection; five assertions wrongly classified as redundant in amendment 7 are reclassified as independently important and gain mutants (11 A, 4 B, 3 C). No check, formula, tolerance, finite result or decision is changed. See "Resolution amendment 8" at the end.  
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

- **Signs superseded by Resolution amendment 2 (review M3P5-F1).** The two signed estimates in this table (Δi and ΔΩ) have reversed signs for the stated convention. They are kept as originally written. The corrected forms are Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ). The "Largest value over φ" column and the node-point row are unaffected.

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

## Resolution amendment 2 (2026-10-16; review M3P5-F1)
**Authority:** Tech Lead, instruction "M3 Planning — M3P5-F1 Correction and Review 06" (I-5), sections 1–2.
- **The decision is unchanged.** J-ax-1, the constant identity transformation of M3, atmospheric co-rotation as air motion, the constants and the scope are as resolved.
- **History is preserved.** Amendment 1's table keeps its original signed formulas, followed by a pointer to this section.
- **Not affected:** amendment 1's magnitudes, bounds, envelopes and example values, and its item 2 (local solar time).

### Convention, stated in full
- **Rotation sense.** Rot(u, a) is the active right-hand rotation by angle a about the unit axis u. The tilt axis is e = (cos φ, sin φ, 0), in A's equator at azimuth φ.
- **What a positive tilt means.** δ > 0 means frame B's axes are frame A's axes rotated by +δ about e, so B's pole is A's pole tilted by +δ. δ < 0 tilts it the other way.
- **How components transform.** Components transform passively, v_B = R v_A with R = Rot(e, −δ). For φ = 0 this is Rx(−δ), the review-04 convention.
- **Consistency with DR-0024.** This is the form r_B = R r_A of DR-0024 "Q4 coordinate conventions, revision 2", for a constant R, so Ṙ = 0.
  - The tilt R is an analysis device, used only to quantify the J-ax-1 approximation.
  - It is not an M3 transformation: in M3, R_EA←I is the identity.
- **Elements, in each frame,** from the unit angular-momentum vector ĥ:
  - i = atan2(√(h_x² + h_y²), h_z);
  - Ω = atan2(h_x, −h_y), which is undefined when h_x = h_y = 0.
- **Differences** are B minus A, with ΔΩ wrapped to (−π, π].

### Corrected first-order formulas (approximations, valid for |δ| ≪ sin i)
Δi ≈ −δ cos(Ω − φ)

ΔΩ ≈ +δ cot i sin(Ω − φ)

**Derivation.**
1. To first order, R = Rot(e, −δ) ≈ I − δ[e×], so ĥ_B ≈ ĥ_A − δ e × ĥ_A.
2. With ĥ_A = (sin i sin Ω, −sin i cos Ω, cos i):

   e × ĥ_A = (sin φ cos i, −cos φ cos i, −sin i cos(Ω − φ)).

3. **Inclination.** Δh_z = +δ sin i cos(Ω − φ). Since cos i = h_z, −sin i Δi = Δh_z, which gives Δi ≈ −δ cos(Ω − φ).
4. **Node.** With X = h_x and Y = −h_y:
   - ΔX = −δ sin φ cos i and ΔY = −δ cos φ cos i;
   - ΔΩ = (Y ΔX − X ΔY)/(X² + Y²) = δ cot i sin(Ω − φ).
5. **Dimensions.** Every term is an angle times a dimensionless trigonometric factor.

**Cause of the error.** Amendment 1 used ĥ_B ≈ ĥ_A + δ e × ĥ_A, the active sense, while stating the passive convention.

### Agreement with exact (finite-rotation) results
These checks use the matrix R and the element definitions only, never the formulas under test.

| Case | Exact result | First-order formula | Agreement |
|---|---|---|---|
| **Review-04 example:** i = 30°, Ω = 90°, φ = 0, δ = +0.15° | Ω_B = 90.2598055437°, so ΔΩ = +0.2598055° | +δ cot 30° = +0.2598076° | Signs agree. The difference, 2.1e-6°, is third order |
| Same example, inclination | Δi = +3.4e-4° | 0, since cos 90° = 0 | Second order, as expected |
| **Tilt about the line of nodes** (φ = Ω), any finite δ | Δi = −δ exactly; ΔΩ = 0 exactly | −δ and 0 | Exact for both signs of δ |
| **Tilt axis 90° behind the node** (φ = Ω − 90°) | ĥ_B = (sin i, sin δ cos i, cos δ cos i) for Ω = 90°, φ = 0, extended by symmetry about z. So ΔΩ = atan(sin δ cot i) and cos i_B = cos δ cos i | +δ cot i | ΔΩ has the sign of δ cot i |

- **Line-of-nodes row qualified by Resolution amendment 3, item 1 (review M3P6-F1).** "Any finite δ" is wrong as written. Δi = −δ and ΔΩ = 0 hold exactly only for i − π < δ < i, that is, 0 < i − δ < π. Outside that domain, the inclination folds and the node jumps by 180°; at its endpoints, the node is undefined. The row is kept as originally written.

### Verification script
`docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`, output `dr0028_node_signed_verification_results.json`. A rerun is byte-identical. The script exits 0 only if every check below passes and every mutant is rejected.
- **Revised by Resolution amendment 3 (review 06).** This section describes the script as committed at `bcb7f9b`. Amendment 3 records the revision, which corrects the wrapping, extends E2 and asserts E5. The first-order checks and their results are unchanged.
- **Hardened by Resolution amendment 5 (review M3P8-F1).** As committed up to `cf9f3d6`, a non-finite first-order value was skipped silently by the order and sign checks, and no per-formula sample minimum was enforced. Amendment 5 adds both. The results are unchanged.

**Oracle (independent of the formulas under test):**
- R is built from Rodrigues' formula. The script checks that R is a proper rotation, equals Rx(−δ) for φ = 0, and that Rᵀẑ equals Rot(e, +δ)ẑ.
- i and Ω are derived from the transformed ĥ.
- The formulas under test are evaluated only in the comparison step.

**Exact properties (any finite δ):**

| ID | Property |
|---|---|
| E1 | The rotation convention above |
| E2 | Tilt about the line of nodes gives Δi = −δ and ΔΩ = 0 exactly |
| E3 | The φ = Ω − 90° closed form |
| E4 | \|Δi\| ≤ \|δ\| for tilts up to ±30°, at every inclination from 0° to 180° in 5° steps |
| E5 | An equatorial orbit has no node, and at i = 0.1° with δ = 0.15° the node jumps by 180° |
| E6 | The review-04 example |

- **E2 and E5 superseded by Resolution amendment 3, items 1 and 2 (reviews M3P6-F1, M3P6-F2).** As committed at `bcb7f9b`, E2 tested only the interior of the domain, and E5's 180° jump was reported but not asserted. The rows above are kept as originally written.

**Signed first-order checks.**
- **Grid:**
  - inclined orbits: i = 30°, 51.6°, 120°;
  - near-polar orbits: 89°, 90°, 91°;
  - near-equatorial orbits: 2°, 5°, 175°, 178°;
  - six node longitudes, five tilt azimuths, and both tilt signs.
- **Steps:** δ_k = ±10⁻² sin i · 2⁻ᵏ rad, for k = 0…4.
  - The node's expansion parameter is δ/sin i, because the node is singular when |δ| ~ sin i.
  - The steps keep |δ|/sin i ≤ 10⁻², which is the singularity handling for near-equatorial cases.
- **Order check.**
  - The observed order is p = log₂(E(δ₃)/E(δ₄)), where E = |exact − formula|.
  - A correct first-order term leaves an error of order 2 or higher, while a wrong one leaves an O(δ) error, which gives p → 1. The script requires p ≥ 1.5, the midpoint between the two.
  - **Measured:** p is between 1.98 and 3.00 for both formulas, over 506 (Δi) and 532 (ΔΩ) samples. The order is 3 where the second-order coefficient vanishes.
- **Sign check.** The sign of the exact result must equal the sign of the formula at the smallest step: 1064 checks.
- **Rounding tolerance.**
  - The noise bound is 64 ε / sin i, with ε = 2.2e-16.
  - It allows about 16 ε of component error, which is amplified by 1/sin i through atan2 for Ω and doubled for a difference of two angles; that gives 32 ε / sin i, and a factor-2 margin brings it to 64 ε / sin i.
  - Samples are used for the order and sign checks only when they exceed 1000 × noise. This keeps the noise shift in p below 0.003.
  - The exact-property checks use the same noise bound. The largest deviation found was 0.03 noise units.

**Mutation sensitivity (each must be rejected):**

| Mutant | Failing checks |
|---|---|
| Amendment 1's original formulas (both signs reversed) | 2128 |
| Δi sign reversed | 1120 |
| ΔΩ sign reversed | 1008 |
| cos and sin swapped | 1576 |

Editing the formula under test in place, reversing either sign or both, makes the script exit 1.

## Resolution amendment 3 (2026-10-16; reviews M3P6-F1, M3P6-F2, M3P6-F3)
**Authority:** Tech Lead, instruction "Continue M3 planning on `milestone-3-planning` from commit `dcabcb2`" (I-6), section 1.
- **The decision is unchanged.** J-ax-1, the identity transformation of M3, atmospheric co-rotation as air motion, the constants and the scope are as resolved.
- **The signed first-order formulas are unchanged:** Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ).
- **The convention is unchanged.** It is the one stated in amendment 2:
  - δ > 0 means B's pole is A's pole rotated by +δ about e = (cos φ, sin φ, 0), in the active right-hand sense;
  - components transform passively, v_B = R v_A with R = Rot(e, −δ);
  - i ∈ [0, π] is computed as atan2(√(h_x² + h_y²), h_z), and Ω as atan2(h_x, −h_y);
  - differences are B minus A, and ΔΩ lies in (−π, π].
- **History is preserved.** Amendment 2 is kept, with pointers at its line-of-nodes row, its verification section and its E2/E5 rows.

### Item 1 (M3P6-F1): the line-of-nodes identity and its domain
This item is an **exact geometric identity** for finite δ, not an approximation.

**Setup.** Tilt about the line of nodes means φ = Ω, so e = (cos Ω, sin Ω, 0) is A's node direction. A's node is defined, so 0 < i < π.

**Derivation.**
1. Let u = (sin Ω, −cos Ω, 0). Then ĥ_A = sin i · u + cos i · ẑ, and e × u = −ẑ, e × ẑ = u.
2. Rot(e, a) therefore maps u to cos a · u − sin a · ẑ, and ẑ to cos a · ẑ + sin a · u.
3. With a = −δ and j = i − δ:

   ĥ_B = sin j · u + cos j · ẑ = (sin j sin Ω, −sin j cos Ω, cos j).

**Result (any finite δ, with −π < j < 2π):**

| j = i − δ | Tilt range for given i | i_B | Δi | ΔΩ |
|---|---|---|---|---|
| 0 < j < π (interior) | i − π < δ < i | j | −δ | 0 |
| j = 0 (endpoint) | δ = i | 0 | −i | undefined: B is equatorial |
| j = π (endpoint) | δ = i − π | π | π − i | undefined: B is equatorial |
| −π < j < 0 (crossing, positive tilt) | i < δ < i + π | −j | δ − 2i | +π |
| π < j < 2π (crossing, negative tilt) | i − 2π < δ < i − π | 2π − j | 2π − 2i + δ | +π |

**What happens at a crossing.** Beyond an endpoint, sin j < 0, so ĥ_B = |sin j|(−u) + cos j ẑ.
- **Inclination:** it folds back into [0, π].
- **Node:** ẑ × ĥ_B reverses, so the ascending node of B is the other intersection of the two planes, Ω_B = Ω + π.
- **At the endpoints themselves:** the orbit lies in B's equator and has no node.

**Consequences.**
- **Domain of the amendment-2 claim.** "Δi = −δ and ΔΩ = 0 for any finite δ" holds exactly on the interior row only, i − π < δ < i.
- **Counterexample (review 06):** i = 2°, Ω = φ = 0, δ = +5° gives j = −3°, so i_B = 3°, Δi = +1° (= δ − 2i) and ΔΩ = +180°. The oracle reproduces this exactly.
- **Exact versus first order.** At φ = Ω, the first-order formula gives Δi ≈ −δ cos 0 = −δ, which coincides with the interior row. But the first-order formulas need |δ| ≪ sin i, a stronger condition than the exact domain. Near an endpoint, the first-order ΔΩ (zero here) misses the discontinuity entirely.

**Tests (E2).** Each case is evaluated at all six node longitudes.

| Case | Count | Configurations |
|---|---|---|
| Interior | 168 | The earlier grid, plus near-equatorial interior cases (2°, −5°), (2°, +1.5°), (178°, +5°), (178°, −1.5°) |
| Crossing, positive tilt | 72 | i = 0.1°, 2°, 10°, 30°, crossing by 0.05°, 3° or 25°; includes the counterexample |
| Crossing, negative tilt | 72 | i = 179.9°, 178°, 170°, 150°, crossing by 0.05°, 3° or 25° |
| Endpoints | 48 | δ = i and δ = i − π, for i = 2°, 30°, 90°, 178° |

The top endpoint uses the float δ for which i − δ = π exactly.

**Tolerances.**
- **Interior and crossing cases.** The tolerance is 64 ε / min(sin i_A, sin i_B). This is the amendment-2 noise bound, using the larger 1/sin amplification of the two frames. The node is compared by circular distance. The largest deviation measured was 0.03 tolerance units.
- **Endpoints.** The computed √(h_x² + h_y²) of ĥ_B must be ≤ 32 ε. Each component carries at most 16 ε, plus at most 2 ε from rounding δ = i − π, and 16√2 ε + 2 ε < 32 ε. The largest value measured was 0.81 ε.
- **Classification.** The expected-value function must report the node as undefined at both endpoints.

### Item 2 (M3P6-F2): the node discontinuity is asserted
All E5 checks use the E2 tolerance, and they are now assertions, not observations.

| Check | What it asserts |
|---|---|
| **E5a** | For every crossing case (72 per tilt sign), the circular distance between ΔΩ and +π is within tolerance |
| **E5b** | For an azimuth sweep at i = 0.1°, \|δ\| = 0.15°, Ω = 0, φ = 0…359°, for both tilt signs, the node jumps by π at the line-of-nodes azimuth, and at least 359 of 360 samples are defined (measured 360 of 360) |
| **E5c** | A coverage guard: each tilt sign must have executed at least 73 jump assertions (72 crossings plus 1 sweep). Measured: 73 and 73 |
| **E5d** | An equatorial orbit has no node, unchanged |

- **Why E5a uses circular distance.** Under exact arithmetic the jump is +π, by the (−π, π] convention. A computed difference within rounding of ±π can reduce to either representative.
- **Line-of-nodes azimuth in E5b.** It is φ = Ω for δ > 0 and φ = Ω + 180° for δ < 0, which is the same rotation.

**Mutants, each rejected by its designated tests.**

| Mutant | Designated tests | Failing checks |
|---|---|---|
| Oracle with the jump suppressed everywhere | E5a and E5b | 144 and 2 |
| Oracle with the jump suppressed only at i = 0.1° (review 06's mutation) | E5a and E5b | 18 and 2 |
| Jump assertions disabled | E5c | 2 |

Removing any single one of E5a, E5b or E5c therefore makes the script fail, as the file-level mutations below confirm.

### Item 3 (M3P6-F3): angle wrapping
**Implementation.**
- `wrap(a)` computes r = fmod(a, 2π), which is exact in IEEE arithmetic.
- It then applies r − 2π if r > π, or r + 2π if r ≤ −π. These steps are exact by Sterbenz's lemma.
- The result is the unique float in (−π, π] that differs from a by an exact integer multiple of 2π, where π and 2π are the float constants. In particular wrap(+π) = wrap(−π) = +π.
- **Deterministic:** its only branches are exact comparisons.
  - **Domain restricted by Resolution amendment 4 (review M3P7-F1).** The guarantee above holds for **finite** float inputs only. As committed at `f999626`, wrap(±∞) raised math.fmod's ValueError and wrap(NaN) returned NaN. Non-finite inputs now raise the guard's ValueError. The text above is kept as originally written.

**Tests.**
- **Exact reduction:** 22 inputs, compared exactly with an independent rational (Fraction) reduction. The inputs are ±π, ±0, the float neighbours of ±π, ±2π, ±10⁶, and π + 2πk and −π − 2πk for k = 1…5.
- **Endpoints:** ±π, checked explicitly.
- **Equivalent angles:** 30 exactly representable pairs (a, a + 2πk) give identical results.
- **Determinism:** each input gives the same result on repeated calls.
- **Why the exact reduction is the reference.** A float such as π + 2π is generally not exactly congruent to π modulo the float 2π. Each float input is therefore compared with its own exact reduction, and only exactly representable equivalents are used for the equality test.

**Mutant.** The previous implementation, which returns [−π, π), is rejected with 28 failing wrap checks.

**Earlier script.** `dr0028_node_sensitivity.py` (amendment 1 evidence) uses a [−π, π) reduction internally. It reports only absolute values and declares no interval, so its outputs are unaffected; it is unchanged.

### Script revision and results
`dr0028_node_signed_verification.py` is revised in place; the amendment-2 version remains at commit `bcb7f9b`. Verdict: PASS, exit 0, and a rerun is byte-identical.

**First-order checks:** unchanged, and they reproduce identically.
- 506 and 532 order samples, with observed order 1.98–3.00;
- 1064 sign checks;
- the four first-order mutants rejected (2128, 1120, 1008 and 1576 failing checks).

**Exact and wrapping mutants:** all five rejected by their designated tests.

| Mutant | Rejected by | Failing checks |
|---|---|---|
| Unrestricted line-of-nodes claim | E2 | 192 |
| Jump suppressed everywhere | E5a and E5b | 144 and 2 |
| Jump suppressed only at i = 0.1° | E5a and E5b | 18 and 2 |
| Jump assertions disabled | E5c | 2 |
| Previous wrap | wrap tests | 28 |

**File-level mutation (the script edited in place; each must exit 1):**

| Edit | Result |
|---|---|
| Restore the previous wrap | exit 1 |
| Restore the unrestricted line-of-nodes claim | exit 1 |
| Remove the E5a assertion | exit 1 |
| Remove the E5b assertion | exit 1 |
| Remove the E5c coverage guard | exit 1 |
| Reverse the Δi sign | exit 1 |
| Reverse the ΔΩ sign | exit 1 |

## Resolution amendment 4 (2026-10-16; review M3P7-F1)
**Authority:** Tech Lead, instruction "Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`" (I-7), section 2.
- **Unchanged:**
  - the decision (J-ax-1), the identity transformation of M3, atmospheric co-rotation as air motion, the constants, the thresholds and the scope;
  - the signed first-order formulas Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ);
  - the passive convention R = Rot(e, −δ) and the interval (−π, π], including wrap(±π) = +π.
- **History is preserved.** Amendment 3 is kept, with a pointer under its item 3.

### The wrapping contract
- **Domain:** `wrap(a)` accepts **finite** float angles only.
- **Finite inputs (unchanged):** the result is the unique float in (−π, π] that differs from a by an exact integer multiple of 2π, where π and 2π are the float constants. The result is exact, by fmod exactness and Sterbenz's lemma, and wrap(+π) = wrap(−π) = +π.
- **Non-finite inputs:** NaN (of either sign), +∞ and −∞ raise `ValueError("wrap: non-finite angle: …")`. No guarantee of the finite contract applies to them.
- **Why the guard is needed.** Without it, the function silently returned NaN for NaN, and for ±∞ raised math.fmod's own ValueError ("math domain error"). That error was not part of the documented contract.
- **Where wrap is used in the script:** only to take differences of two finite atan2 results, which are always finite. No computed result depends on the non-finite behaviour.

### Tests
| Test | What it checks |
|---|---|
| `wrap_nonfinite_tests` | NaN, −NaN, +∞ and −∞ must each raise ValueError **with the guard's message**. Any other exception, a different ValueError, or a return value is a failure |

- **Why the message is checked as well as the type.** math.fmod already raises ValueError for ±∞, so a type-only check would not detect a removed guard for those two inputs.
- **Finite behaviour unchanged.** The finite-input wrap tests are unchanged: 22 inputs against the exact rational reference, both endpoints, 30 exactly equivalent pairs, and determinism. Their outputs are identical.

### Mutants
- **New built-in mutant** `M3P7-F1_nonfinite_guard_removed`. It is the `f999626` implementation, without the guard.
  - It must fail the non-finite tests in all four categories, and it does: 4 of 4.
  - Requiring all four, not just one, makes the ±∞ message check load-bearing, not only the NaN cases.
  - It produces no finite-wrap failures, so the new test is specific to the defect.
- **Existing mutants.** Their earlier failure counts are unchanged. The previous [−π, π) wrap mutant now also fails the four non-finite checks, which it never guarded against.

### Results
- **Verdict PASS.** Two consecutive runs produce byte-identical output.
- **Every pre-existing section of the output is identical to `f999626`:** grid, tolerances, exact properties, wrapping, first-order checks and their mutants.
- **New output section:** `wrap_nonfinite`.
- **Finite-input equivalence.** Bitwise comparison of the guarded wrap against the `f999626` implementation on 200 001 finite floats found 0 differences. The floats were random bit patterns and uniform angles in ±50, plus ±π, ±0, the subnormal extremes and ±max.

**File-level mutation (the script edited in place; each must exit 1):**

| Edit | Result |
|---|---|
| Remove the non-finite guard | exit 1 |
| Weaken the guard test to a type-only check | exit 1 |
| Disable the non-finite tests | exit 1 |
| Restore the previous wrap | exit 1 |
| Restore the unrestricted line-of-nodes claim | exit 1 |
| Remove E5a | exit 1 |
| Remove E5b | exit 1 |
| Remove E5c | exit 1 |
| Reverse the Δi sign | exit 1 |
| Reverse the ΔΩ sign | exit 1 |

## Resolution amendment 5 (2026-10-16; review M3P8-F1)
**Authority:** Tech Lead, instruction "Continue TARS M3 planning from `milestone-3-planning` at `0ac630b`" (I-8), sections 2–5.
- **Unchanged:**
  - the decision (J-ax-1), the identity transformation of M3, atmospheric co-rotation as air motion, the constants, the thresholds and the scope;
  - the signed first-order formulas Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ), the passive convention R = Rot(e, −δ), the interval (−π, π] and the finite-only `wrap()` contract of amendment 4;
  - the oracle, the grid, the noise bound, the significance factor (10³) and the order threshold (1.5).
- **History is preserved.** Earlier amendments are kept, with a pointer under amendment 2's "Verification script".
- **Nature of the finding.** It was a verification-harness defect, not a mathematical one. The committed formulas were always finite, and their PASS was genuine.

### The defect (as committed up to `cf9f3d6`)
- Every comparison with NaN is false. A NaN first-order value therefore failed the significance gates (`err >= tol`, `|lin| >= tol`) and the series was skipped, with no failure recorded.
- ±∞ passes every `>= tol` gate. The order estimate then became log2(∞/∞) = NaN, and `NaN < 1.5` is false, so no order failure was recorded; a sign check could even be counted as valid.
- Nothing required each formula to reach a minimum number of samples. Review 08's counterexample (Δi returned as NaN) exited 0 with verdict PASS, 0 Δi order samples and 504 sign checks.

### The correction
- **Finite validation before any comparison.** `nonfinite_reason` checks the oracle value and the first-order value of each component at every step with `math.isfinite`.
  - A non-finite value is recorded as a `nonfinite <component>` failure, so the process exits 1.
  - That component's series is then discarded for both the order and sign checks, so it can never count towards coverage.
  - Nothing is filtered silently, and no fallback value is substituted.
  - With both values finite, |oracle| ≤ π, so their difference cannot overflow; no third check is needed.
  - A non-numeric value makes `math.isfinite` raise TypeError. The process ends nonzero; it is never reported as PASS.
- **Per-formula coverage minima, each enforced separately.** Only samples that are finite and pass the existing significance gate count.

| Formula | Check | Minimum | Observed | Derivation |
|---|---|---|---|---|
| Δi | order | 506 | 506 | committed count, unchanged since `bcb7f9b` (see below) |
| ΔΩ | order | 532 | 532 | committed count, unchanged since `bcb7f9b` (see below) |
| Δi | sign | 560 | 560 | 600 series minus the 40 where cos(Ω − φ) = 0 exactly |
| ΔΩ | sign | 504 | 504 | 600 series minus the 40 where sin(Ω − φ) = 0 and the 56 more at i = 90° (cot i = 0) |

- **Sign minima are derived from the grid.**
  - The grid has 10 inclinations × 6 nodes × 5 tilt azimuths × 2 signs = 600 series per formula.
  - A sign check is meaningful only where the first-order term is nonzero. Node and azimuth are integer degrees, so the zero set is exact: Ω − φ ∈ {90°, 270°} for Δi (the pairs (90°, 0°) and (300°, 210°)); Ω − φ ∈ {0°, 180°} (the pairs (0°, 0°) and (300°, 300°)) or i = 90° for ΔΩ.
  - `sign_check_minimum` computes these counts from the grid. At the committed formulas, every applicable series sits at least 4.6 × 10³ times above the gate, and every excluded one at most 3 × 10⁻⁹ times it.
- **Order minima are the existing coverage.**
  - Which series pass the order gate depends on the size of the O(δ²) error relative to 10³ × noise, so the count has no closed form.
  - It is nevertheless fixed. Rounding moves an error by at most the noise bound, which is 10⁻³ of the gate. The nearest samples sit at 1.0123 and 0.9940 of the gate for Δi, and at 1.55 and 0.495 for ΔΩ. Both margins exceed 10⁻³.
  - The script reports these nearest ratios under `gate_ratio_nearest`. The minima therefore keep every existing order sample; none is reduced.
- **New output keys:** `sign_checks_delta_i`, `sign_checks_delta_node`, `minimum_valid_samples`, `gate_ratio_nearest` and `formula_defect_mutants`.

### Bounded audit of the same failure class (I-8 section 4)
| Location | Finding | Action |
|---|---|---|
| First-order checks | Non-finite values skipped silently; no per-formula minimum; ±∞ could increment the sign counter | Corrected (above) |
| E1 rotation convention | `max()` drops a NaN that is not its first argument, so a NaN matrix entry would pass | Corrected: non-finite deviation or matrix entry is a failure |
| E2 identity and endpoints | `dev = max(NaN, …)` is NaN and `NaN > 1` is false; a NaN `hypot` passes `rho > 32 eps` | Corrected: non-finite values are failures; the endpoint check now uses the `tilt_fn` parameter (default `tilt_matrix`, results identical) so a mutant can reach it |
| E3 closed form, E4 bound | `max()` drops NaN | Corrected; E3 and E4 now call the `oracle` parameter (default `finite`, results identical) so mutants can reach them |
| E5b sweep | A NaN node would reach `circ`, where the wrap guard raises | Corrected: an explicit failure is recorded first |
| E6 review-04 example | `abs(NaN − 90.2598…) > 5e-11` is false | Corrected: non-finite values are failures |
| Empty sample sets | Only the first-order checks and the E5b sweep filter samples at run time; E5b already has a guard (≥ 359 defined samples per sign), and E2 skips a case only after recording a failure | No other change |
| Swallowed exceptions | `wrap_nonfinite_tests` catches every exception but records each as a failure; nothing else catches | No change |
| Missing assertions | E6 reports its Δi but asserts only the node. This is by design: E6 reproduces the review-04 node example, and Δi is checked over the whole grid by the first-order checks | No change (documented) |

No separate mathematical issue, contract change or out-of-scope work was found.

### Mutants
**First-order defect mutants** (new section `formula_defect_mutants`). Each must be rejected by every designated check, with at least the given number of failures.

| Mutant | Designated checks (minimum failures) | Observed |
|---|---|---|
| Δi = NaN, +∞, −∞ (three mutants) | nonfinite Δi (600), coverage Δi (2) | 600, 2 each |
| ΔΩ = NaN, +∞, −∞ (three mutants) | nonfinite ΔΩ (600), coverage ΔΩ (2) | 600, 2 each |
| Δi = 0 | coverage Δi (1) | 1 (plus 560 order failures) |
| ΔΩ = 0 | coverage ΔΩ (1) | 1 (plus 504 order failures) |
| Oracle Δi = NaN | nonfinite Δi (600), coverage Δi (2) | 600, 2 |
| Oracle ΔΩ = NaN | nonfinite ΔΩ (600), coverage ΔΩ (2) | 600, 2 |

- Requiring 600 non-finite failures, one per series, means a check weakened to catch only some values or some series is detected.
- Requiring 2 coverage failures means both the order and the sign minimum of that formula are load-bearing.
- The zero mutants are finite but skip every sign check. They show that skipped samples cannot satisfy coverage.

**Audit mutants** (in `exact_and_wrap_mutants`):

| Mutant | Designated tests | Failures |
|---|---|---|
| NaN rotation-matrix entry | E1, E2 (endpoints) | 20, 48 |
| Oracle Δi = NaN | E2, E3, E4, E6 | 312, 144, 6660, 1 |
| Oracle ΔΩ = NaN | E2, E3, E5b, E6 | 312, 144, 722, 1 |

**Existing mutants.** All are still rejected, with unchanged failure counts, with one exception. `cos_sin_swapped` has 1578 failing checks instead of 1576, because it also skips 4 Δi and 36 ΔΩ sign checks and so fails both sign minima.

### File-level mutation through the entrypoint
`dr0028_node_signed_mutation_check.py` (output `dr0028_node_signed_mutation_check_results.json`) applies each edit to a copy of the script. It runs the copy as a separate `python -I` process and requires a nonzero exit. The unmutated script must exit 0 with verdict PASS. Verdict PASS: 33 of 33 detected, and a rerun is byte-identical.

| Group | Edits | Detected |
|---|---|---|
| Injection | Δi formula returns NaN, +∞, −∞; ΔΩ formula returns NaN, +∞, −∞ | 6/6 (FAIL verdict) |
| Coverage | Δi coverage disabled; ΔΩ coverage disabled; sign minimum removed; order minimum removed; comparison disabled; sign counter moved outside its gate | 6/6 (FAIL verdict) |
| Validation | finite validation removed; formula check weakened to `isnan`; oracle check removed; invalid sample not discarded | 4/4 (FAIL verdict) |
| Audit | finite check removed from E1, E2, E2 endpoints, E3, E4, E5b, E6 | 7/7: 5 by FAIL verdict; E2 and E5b by the ValueError of the amendment-4 wrap guard |
| Earlier findings | Δi sign reversed; ΔΩ sign reversed; unrestricted line-of-nodes claim; E5a, E5b, E5c removed; previous wrap; wrap guard removed; guard test weakened to type-only; non-finite wrap tests disabled | 10/10 (FAIL verdict) |

- **E2 and E5b detection.** With those checks removed, the oracle-ΔΩ-NaN mutant passes a NaN to `circ`, and the wrap guard ends the process with ValueError before a verdict is written. The harness records this as "exception: ValueError", not as a FAIL verdict.
- **Superseded by Resolution amendment 6 (review M3P9-F1..F3).** A built-in mutant that raises is now recorded as not rejected, so these two mutations end with a FAIL verdict whose designated mutant is shown as unrejected; the mutation check now requires each mutation's declared reason and covers 109 mutations.

### Results
- **Verdict PASS, exit 0.** Two consecutive runs produce byte-identical output.
- **Finite results unchanged.** Comparing the output with `0ac630b`, every pre-existing value is identical (grid, tolerances, exact properties, wrapping, first-order statistics, every existing mutant count), except `cos_sin_swapped` as explained above. Only new keys were added, including zero entries for E1, E3, E4 and E6 in the failure counts of each existing exact mutant.

## Resolution amendment 6 (2026-10-17; reviews M3P9-F1, M3P9-F2, M3P9-F3)
**Authority:** Tech Lead, instruction "I-9 — M3 Planning Verification Hardening and Codex Review 10" (I-9), sections 3–7.
- **Unchanged:**
  - the decision (J-ax-1), the identity transformation of M3, atmospheric co-rotation as air motion, the constants, the thresholds and the scope;
  - the signed first-order formulas Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ), the passive convention R = Rot(e, −δ), the interval (−π, π] and the finite-only `wrap()` contract;
  - the oracle, the grid, the step sizes, the noise bound, the significance factor (10³), the order threshold (1.5), the four coverage minima (506, 532, 560, 504), and every check and assertion, including the definitions of E3 and E4.
- **History is preserved.** Amendment 5 is kept, with a pointer under its "File-level mutation through the entrypoint".
- **Nature of the findings.** Both MINOR findings were regression-protection gaps in the verification harness, not mathematical defects. The committed guard rejected oracle ±∞, and the committed formulas passed both assertions genuinely; what was missing was a mutant that only the guarded assertion could reject.

### M3P9-F1: oracle ±∞
New built-in mutants in `formula_defect_mutants`. Each must be rejected by every designated check, with at least the given number of failures.

| Mutant | Designated checks (minimum failures) | Observed |
|---|---|---|
| Oracle Δi = +∞, −∞ (two mutants) | nonfinite Δi (600), coverage Δi (2) | 600, 2 each |
| Oracle ΔΩ = +∞, −∞ (two mutants) | nonfinite ΔΩ (600), coverage ΔΩ (2) | 600, 2 each |
| Oracle Δi = +∞, −∞ at a single sample (two mutants) | nonfinite Δi (1), coverage Δi (2) | 1, 2 each |
| Oracle ΔΩ = +∞, −∞ at a single sample (two mutants) | nonfinite ΔΩ (1), coverage ΔΩ (2) | 1, 2 each |

- **The single sample** is the smallest step of the series i = 30°, Ω = 37°, φ = 0°, positive tilt. Only one oracle value of one formula is non-finite; every other value is exact.
- **Why 2 coverage failures for one sample.** At the committed formulas that series is a valid order sample and a valid sign sample of both formulas. The minima equal the observed counts, so losing it must fail both minima of the corrupted formula. This shows directly that one invalid sample cannot be counted towards coverage.
- **Weakened checks.** With the oracle check weakened to `math.isnan`, all eight ±∞ mutants are no longer rejected. With it weakened to `math.isinf`, the two NaN oracle mutants of amendment 5 are no longer rejected. Both weakenings are file-level mutations (below).

### M3P9-F2: order and sign assertions, each formula separately
`by_formula_test` now also counts order and sign failures per formula (the totals are kept). New built-in mutants; the other formula is exact in each:

| Mutant | Designated check (minimum failures) | Observed |
|---|---|---|
| Δi first-order coefficient doubled | order Δi (560) | order Δi 560; no sign failure |
| ΔΩ first-order coefficient doubled | order ΔΩ (504) | order ΔΩ 504; no sign failure |
| Δi sign reversed | sign Δi (560) | sign Δi 560 (and order Δi 560) |
| ΔΩ sign reversed | sign ΔΩ (504) | sign ΔΩ 504 (and order ΔΩ 504) |

- **Derivation of the minima.** Doubling a coefficient keeps every sign but leaves an error equal to the whole first-order term, so the observed order drops to about 1 in every series where that term is nonzero. Reversing the sign makes the first-order term disagree in sign with the finite result in the same series. Those series are counted by `sign_check_minimum`: 560 for Δi and 504 for ΔΩ. The observed counts equal the minima exactly.
- **Why each mutant is specific.** The doubled coefficient produces no sign failure, so only the order assertion of its formula can reject it. The reversed sign is rejected by the sign assertion of its formula; requiring 560 or 504 sign failures means a disabled sign assertion is detected even though the order check would still fail.
- **Review 09's counterexample.** With the order assertion disabled, doubled coefficients previously passed. Each per-formula and whole-check removal of the order or the sign assertion is now a file-level mutation that must be detected (below).

### M3P9-F3: E3 and E4 assertions
- **New built-in mutant** `M3P9-F3_oracle_delta_i_scaled_1pct` (in `exact_and_wrap_mutants`): the oracle's Δi multiplied by 1.01, ΔΩ exact. Designated tests: E3 and E4. Observed: E3 1, E4 1 (and E2 288).
- A finite oracle records no non-finite failure in E3 or E4, so each designated count comes only from the closed-form deviation assertion (E3) or the inclination-bound assertion (E4). Removing either assertion leaves the mutant unrejected by that test.
- E3 and E4 themselves are unchanged.
- **Step-size limitation, kept by design (I-9 §5).** The order check uses only the errors at the two smallest steps, and the sign check only the smallest step. A formula that is wrong only at the three larger steps therefore passes, as review 09 showed with (100, 100) returned at those steps. This is an intentional property of an asymptotic order test: the claim verified is the behaviour as δ → 0 on the fixed grid of five halvings, which is what the first-order formulas assert. No approved requirement concerns the larger steps, so the step selection is not changed.

### Built-in mutants that raise
- `main` now evaluates each built-in defect mutant through `mutant_failures`. An exception raised while a mutant is evaluated is recorded under `exception`, and the mutant counts as **not rejected**, so the verdict is FAIL and the exit status 1. A crash is never counted as a designated rejection. The formulas under test and the exact properties are not wrapped: an exception there still ends the process.
- **Why this was needed.** With the oracle check weakened, the new single-sample ±∞ mutants make the order estimate evaluate log2(finite/∞) = log2(0), which raises "math domain error". Before this change, that crash would have ended the process before any verdict, so the file-level mutation would have been "detected" only by a crash.
- **At the committed script no mutant raises**, so no `exception` key appears in the output.
- **Superseded by Resolution amendment 7 (review M3P10-F1).** Recording a raising mutant as not rejected is kept, but the mutation check no longer accepts "not rejected" from a mutant that raised, or whose defect was not exercised; an exception counts only under an explicit allowance.

### File-level mutation check (I-9 §6)
`dr0028_node_signed_mutation_check.py` (output `dr0028_node_signed_mutation_check_results.json`) is revised so that each mutation is detected only for its intended reason.
- **Declared expected rejection.** Each mutation names its target property and its expected rejection as predicates on the script's output. Examples: "built-in mutant M3P9-F2_delta_i_coefficient_doubled not rejected" (an assertion was removed), or "exactly 600 failures starting `nonfinite delta_i formula=nan`" (a defect was injected).
- **Detection rule.** A mutation is detected only when the copy exits 1 with nothing on stderr, writes a FAIL verdict, and every predicate holds. Exit 0, a FAIL verdict for another reason, any exception that ends the process, or a fragment that does not occur exactly once is NOT detected, and the check fails.
- **No vacuous expectation.** No expectation may already be met by the unmutated script's output; none is.
- **Negative controls.** Five deliberately invalid runs must each be classified as not detected: a syntax error, an import failure, a missing script, a neutral edit (exit 0), and a real defect (Δi sign reversed) declared with the wrong reason (a ΔΩ sign failure). All five are classified as not detected.
- **Report.** For each mutation: group, target property, expected rejection, observed outcome and PASS/FAIL. Machine-specific paths are replaced, so reruns are byte-identical.

| Group | Mutations | Detected for the declared reason |
|---|---|---|
| M3P8-F1 injection (formula NaN, ±∞; each formula) | 6 | 6 |
| M3P8-F1 coverage | 6 | 6 |
| M3P8-F1 validation | 4 | 4 |
| M3P8-F1 audit (finite checks of E1, E2, E2 endpoints, E3, E4, E5b, E6) | 7 | 7 |
| M3P9-F1 oracle (±∞ at one sample, each formula; check weakened to `isnan` and to `isinf`) | 6 | 6 |
| M3P9-F2 order and sign (each coefficient doubled; order or sign assertion disabled for Δi, for ΔΩ and for both) | 8 | 8 |
| M3P9-F3 exact properties (E3, E4 assertion removed) | 2 | 2 |
| Earlier findings (reviews 05–07) | 10 | 10 |
| Review-09 injection matrix | 60 | 60 |
| **Total** | **109** | **109** |

- **The 33 mutations of amendment 5 are kept.** Each now has a declared reason. The E2 and E5b finite-check removals are detected by a FAIL verdict in which `M3P8-F1_audit_oracle_delta_node_nan` is unrejected and recorded as raising the wrap guard's ValueError.
- **Review-09 injection matrix.** Review 09 ran 60 independent NaN/±∞ injection cases. They are preserved as file-level mutations with the same structure:
  - formula path: each formula × NaN, +∞, −∞ × {all, first step, last step, one series, positive tilt, near-equatorial, near-polar} = 42;
  - oracle path: each formula × NaN, +∞, −∞ × {all, first step, negative tilt near-polar} = 18.

  Each requires the exact number of `nonfinite` failures: one per affected series (600, 600, 600, 1, 300, 240 and 180 for the formula subsets; 600, 600 and 90 for the oracle subsets).

### Assertion-removal sweep (measurement; not corrected)
`dr0028_node_signed_assertion_sweep.py` (output `dr0028_node_signed_assertion_sweep_results.json`) removes each of the 35 `failures.append(...)` statements of the verification script in turn and runs the copy. It is a measurement with no verdict.

| Test | Assertions | Detected individually | Survive individually |
|---|---|---|---|
| First-order checks (nonfinite, order, sign, coverage) | 4 | 4 | 0 |
| E3, E4 | 4 | 4 | 0 |
| E5a, E5c | 2 | 2 | 0 |
| E1 | 2 | 1 | 1 (the deviation bound) |
| E2 | 7 | 2 | 5 |
| E5b, E5d | 4 | 1 | 3 |
| E6 | 3 | 1 | 2 |
| Finite wrap tests | 6 | 0 | 6 |
| Non-finite wrap tests | 3 | 2 | 1 |
| **Total** | **35** | **17** | **18** |

- **What a survivor means.** No built-in mutant depends on that assertion alone. Either another assertion of the same test rejects every designated mutant, as for the previous-wrap mutant, which fails several finite wrap assertions at once; or no mutant exercises it.
- **Every assertion named by M3P9-F1, F2 and F3 is detected individually:** the non-finite, order and sign assertions of the first-order checks, and the E3 and E4 assertions. The oracle finite check is a condition inside `nonfinite_reason`, not a separate statement; its removal and both weakenings are file-level mutations above.
- **The 18 survivors are not corrected.** Protecting them needs new defect mutants for assertions that no review finding named, which is outside I-9 §3–§5. They are recorded for the Tech Lead's decision. None of them is a defect in a check: each assertion is present, and the sweep shows only that no mutant makes it individually load-bearing.
- **Followed up by Resolution amendment 7 (review M3P10-F2, I-10 §4).** The 18 are classified (6 A, 9 B, 3 C, 0 D); the six of category A gain built-in mutants. The sweep now reports 23 detected and 12 surviving.

### Results
- **Verdict PASS, exit 0.** Two consecutive runs of the verification script, of the mutation check and of the sweep each produce byte-identical output.
- **Finite results unchanged.** Comparing the output with `faba9d6`, every pre-existing value is identical. The 53 differences are all added keys: the per-formula order and sign counts of the existing first-order mutants, and the 13 new mutants.
- **Coverage unchanged:** order 506 (Δi) and 532 (ΔΩ), sign 560 (Δi) and 504 (ΔΩ), each equal to its minimum.
- **Unchanged definitions.** An AST comparison with `faba9d6` shows that only `EXACT_MUTANTS`, `by_formula_test` and `main` changed among the existing top-level definitions, plus the new mutant helpers. The oracle, formulas, wrap, tolerances, grid, checks and minima are unchanged.

## Resolution amendment 7 (2026-10-17; reviews M3P10-F1, M3P10-F2)
**Authority:** Tech Lead, instruction "I-10 — Resolve M3P10-F1 and authorize Review 11" (I-10), sections 2–6.
- **Unchanged:**
  - the decision (J-ax-1), the identity transformation of M3, atmospheric co-rotation as air motion, the constants, the thresholds and the scope;
  - the signed first-order formulas, the passive convention R = Rot(e, −δ), the interval (−π, π] and the finite-only `wrap()` contract;
  - the oracle, the grid, the step sizes, the noise bound, the significance factor (10³), the order threshold (1.5), the four coverage minima (506, 532, 560, 504), and every check and assertion.
- **The one change inside a test:** E5d now calls the `elements_fn` parameter (default `elements`, results identical), so a built-in mutant can reach it. The same was done for `tilt_fn` in amendment 5.
- **History is preserved.** Amendment 6 is kept, with pointers under "Built-in mutants that raise" and "Assertion-removal sweep".
- **Nature of the finding.** M3P10-F1 was a verification-harness defect, introduced by amendment 6, and not a mathematical one. It never produced a false PASS of the verification script.

### M3P10-F1: the defect and its root cause
- Amendment 6 recorded a built-in mutant that raises as **not rejected**, so that a crash would never count as a rejection. That is correct for the script's verdict.
- The mutation check, however, used "not rejected" as the evidence that an assertion had been removed. It could not tell a mutant whose designated check stayed silent from a mutant that raised for an unrelated reason.
- **Review 10's counterexample:** an unrelated import inside `formula_scaled()` (factor 2), with the order assertion intact, was classified as "order assertion disabled". The implementer reproduced it before the fix. The committed regression demonstration reproduces it against the reviewed harness (`896d52d`).
- **A second gap of the same kind:** a mutant that catches an exception and returns the reference result is also "not rejected", although it tests nothing.

### The correction (verification script)
- **Defect record.** Each built-in mutant's injected function (`formula`, `oracle`, `wrap_fn`, `line_of_nodes`, `tilt_fn`, `elements_fn`) is wrapped in a recorder. On every call, the recorder compares the mutant's outcome with the reference implementation, results or exceptions, and counts the calls that differ. A setting (`assert_jump`) is compared with its default. The mutant's own result or exception passes through unchanged.
- **`defect_exercised`** is true when some call differed. A built-in mutant whose defect is never exercised is invalid setup: it is listed in `mutants_with_defect_not_exercised`, and the verdict is FAIL. At the committed script, all 42 built-in mutants are exercised.
- **Superseded by Resolution amendment 8 (review M3P11-F1).** "Some call differed" is not evidence of the intended defect: a rounding-level difference, or a difference in another component, passed as exercised. Amendment 8 requires exactly the declared intended defect, established by an independent probe.
- **Exception record.** A mutant's exception is recorded with its type, message and call stack. The stack lists the frames of the script only, as "function: source line", with no paths or line numbers.

### The correction (mutation check)
Every run receives exactly one category; only "expected rejection" is a detection.

| Category | Meaning |
|---|---|
| invalid mutation setup | the fragment does not occur exactly once (not run), or a built-in mutant named by the expectation never exercised its defect |
| process failure | no output (syntax error, import failure, missing file, any crash), or exit status and verdict inconsistent |
| normal execution | exit 0, verdict PASS |
| unexpected exception | a built-in mutant raised an exception that no allowance of this mutation matches |
| rejected for another reason | exit 1 and FAIL, but the declared rejection is not shown |
| expected rejection | exit 1 and FAIL, no unexpected exception, every predicate holds |

- **"Not rejected" now requires** that the mutant completed without an exception, exercised its defect, and was not rejected by its designated checks.
- **Allowed exceptions.** Each is named by mutant, exception type, message prefix and the exact call stack. Measured over all 109 mutations, exactly six make a built-in mutant raise, through two mechanisms. All other exceptions are unexpected.

| Mutations | Mutant(s) | Exception | Stack |
|---|---|---|---|
| E2 finite check removed | oracle ΔΩ = NaN | ValueError "wrap: non-finite angle" (the amendment-4 guard) | run_exact > E2 identity line > circ > wrap guard |
| E5b finite check removed | oracle ΔΩ = NaN | the same | run_exact > E5b jump line > circ > wrap guard |
| oracle check weakened to `isnan`; oracle check removed; finite validation removed; invalid sample not discarded | the four single-sample oracle ±∞ mutants | ValueError "math domain error" | `check_formulas: p = math.log2(e[-2] / e[-1])` |

- **The second row of allowances** is the documented `isnan` case. It occurs in four mutations, not one: each lets a single oracle ±∞ through the finite validation, so e[−1] = ∞, and log2(finite/∞) = log2(0) raises at the order estimate. The other three were never documented, because the earlier check did not inspect exceptions outside its predicates. They are allowed under the same narrow terms and are listed here.
- **`M3P7-F1_nonfinite_tests_disabled`** now declares its reason precisely. The guard-removed mutant completes without rejection because nothing exercises it, and the `wrap_nonfinite` report has no per-case entries.
- **`M3P7-F1_guard_removed`** now matches the guard together with the line after it, because the new inexact-wrap mutant contains the same guard text.

### Controls (I-10 §3)
Each control declares the category it must receive.

| Control | Declared category | Original harness (`896d52d`) | Corrected |
|---|---|---|---|
| syntax error | process failure | met | met |
| import failure (process) | process failure | met | met |
| missing script | process failure | met | met |
| neutral edit | normal execution | met | met |
| fragment absent | invalid mutation setup | met | met |
| Δi sign reversed, claimed as the ΔΩ sign removal | rejected for another reason | met | met |
| **import failure inside a built-in mutant** | unexpected exception | **not met (counted as detection)** | met |
| **ZeroDivisionError inside a built-in mutant** | unexpected exception | **not met** | met |
| **exception suppressed inside a mutant, which returns the reference result** | invalid mutation setup | **not met** | met |
| **allowed wrap-guard exception at E5b, claimed for the E2 removal** | unexpected exception | **not met** | met |
| **allowed exception at E2 but of type TypeError** | unexpected exception | **not met** | met |
| injected doubled Δi coefficient | expected rejection | met | met |
| Δi order assertion removed (the built-in mutant completes without rejection) | expected rejection | met | met |

`dr0028_node_signed_harness_regression.py` produces this table. It reads the reviewed harness and script from git at `896d52d`, runs every control against both versions, and requires the five M3P10-F1 regression controls (in bold) to fail against the original and pass against the corrected harness.

### M3P10-F2: classification of the 18 assertions (I-10 §4)
`dr0028_node_signed_assertion_classification.py` records each classification with executed evidence. For A, a built-in mutant is rejected by the designated test with the assertion present, and not without it. For B, with only that assertion removed, a defect of the kind it guards is still rejected by the named independent check.

| Assertion | Category | Evidence |
|---|---|---|
| W2 finite wrap equals the exact rational reduction | A | new mutant: inexact reduction a − 2π round(a/2π) (2 failures; 0 without the assertion) |
| N1 non-finite wrap raises ValueError, not another type | A | new mutant: the guard raises TypeError (4; 0) |
| E2b no E2 case skipped as "undefined node" | A | new mutant: interior regime undefined (168; 0) |
| E2c line-of-nodes identity in every regime | A | new mutant: ΔΩ = 0 in the crossing regimes (144; 0) |
| E2d node undefined at the endpoints | A | new mutant: closed interval 0 ≤ j ≤ π (48; 0) |
| E5d equatorial orbit has no node | A | new mutant: `elements` reports a node at the equator (1; 0) |
| W1 result in (−π, π] | B | previous [−π, π) wrap still rejected by W2 (14) |
| W4 wrap(±π) = +π | B | the same (14) |
| W5 exact equivalents agree | B | fmod without the correction step still rejected by W2 (9) |
| E1 rotation convention | B | active transform Rot(e, +δ) still rejected by E2 endpoints (36) |
| E2e endpoints equatorial | B | the same defect still rejected by E1 (1) |
| E5b non-finite sweep value | B | oracle ΔΩ = NaN still rejected by the E5b defined-sample guard (2) |
| E5b defined-sample guard | B | no node at the sweep's crossing azimuths still rejected by E5c (2) |
| E6 review-04 value | B | ΔΩ 0.01 % too large still rejected by E3 (the example is an E3 case: φ = Ω − 90°) |
| E6 sign agreement | B | ΔΩ negated still rejected by E3 |
| W3 determinism of wrap | C | wrap is stateless; a defect only W3 sees would need state and be wrong only on a second call |
| W6 at least 5 equivalent pairs | C | guards W5's fixed input list against becoming vacuous; fails only if that code is edited |
| E2a review-06 counterexample among the E2 cases | C | guards the fixed case list; the case is checked by E2c like every other |

- **No category D.** No assertion's verification value is uncertain, and none conceals a correctness risk that would require a decision.
- **Corrected by Resolution amendment 8 (review M3P11-F2).** The B classifications of W5, E1, E2e, the E5b non-finite sweep value and the E5b defined-sample guard above are invalid: each protects a defect that only it rejects. They are category A (11 A, 4 B, 3 C), and the dependency statements below for E1/E2e, W5 and the E5b guard are corrected there.
- **Dependencies within B.**
  - E1 and E2e protect each other against a sign error in `tilt_fn`. Removing both at once would lose that protection for the `tilt_fn` parameter. The oracle's own `tilt_matrix` stays protected by E2c, E3, E4 and the first-order checks.
  - W1, W4 and W5 rest on W2 (A), E6 on E3 (protected since amendment 6), and E5b's defined-sample guard on E5c.
- **Sweep, before and after:** 17 detected and 18 surviving (amendment 6), now 23 and 12. The difference is exactly the six assertions of category A. The 12 survivors are the 9 of B and the 3 of C.

### Results
- **Verdict PASS, exit 0** for the verification script, the mutation check (109/109 detected for the declared reason; 13/13 controls receive their declared category), the classification (18/18) and the regression demonstration. The sweep is a measurement. Each of the five outputs is byte-identical on a rerun.
- **Finite results unchanged.** Comparing the output with `896d52d`, no pre-existing value changed. The 79 differences are added keys: `defect_calls` and `defect_exercised` for each of the 36 existing mutants, the six new mutants, and `mutants_with_defect_not_exercised` (empty).
- **Coverage unchanged:** order 506 (Δi) and 532 (ΔΩ), sign 560 (Δi) and 504 (ΔΩ), each enforced separately. The 1 % Δi oracle error is still rejected by E3 and by E4.
- **Before and after:**

| Count | Amendment 6 | Amendment 7 |
|---|---|---|
| Built-in mutants | 36 | 42 |
| File-level mutations detected | 109/109 (old classification) | 109/109 (category "expected rejection") |
| Controls | 5 | 13 |
| Sweep: detected / surviving | 17 / 18 | 23 / 12 |
| Verification script run time | about 0.7 s | about 1.9 s (the recorder calls each reference too) |

- **Unchanged definitions.** An AST comparison with `896d52d` shows that among the existing top-level definitions only `exact_properties` changed (the `elements_fn` parameter and E5d's call), together with `EXACT_MUTANTS`, `MIN_DESIGNATED_FAILURES`, `mutant_failures` and `main`.

## Resolution amendment 8 (2026-10-17; reviews M3P11-F1, M3P11-F2)
**Authority:** Tech Lead, instruction "I-11 — Resolve Review 11 Findings and Authorize Review 12" (I-11), sections 2–5.
- **Unchanged:**
  - the decision (J-ax-1), the identity transformation of M3, atmospheric co-rotation as air motion, the constants, the thresholds and the scope;
  - the signed first-order formulas, the passive convention R = Rot(e, −δ), the interval (−π, π] and the finite-only `wrap()` contract;
  - the oracle, the grid, the step sizes, the noise bound, the significance factor (10³), the order threshold (1.5), the four coverage minima (506, 532, 560, 504), and every check and assertion, including E5d's `elements_fn` parameter from amendment 7.
- **History is preserved.** Amendment 7 is kept unchanged, with pointers under its "defect record", its classification table and its dependency statements. Its results were produced by the amendment-7 harness, and are not relabelled as valid under the criterion below. The amendment-7 counts (`differing`) are still reported, for comparison only.
- **Nature of the findings.** Both are verification-harness defects, and not mathematical ones. Neither produced a false PASS of the verification script, and no mathematical result changes.

### M3P11-F1: the defect and its root cause
- Amendment 7 counted a built-in mutant's defect as exercised when any call's outcome differed from the reference implementation in any way (`differing > 0`).
- A difference is not the intended defect. **Review 11's counterexample:** in `formula_scaled()`, for factor 2, a suppressed import failure followed by the correct formulas, with the ΔΩ product reassociated. The result differs from the reference by rounding in 940 of 3000 calls. The doubled-coefficient mutants were therefore "exercised", although neither doubled anything, and the run was classified "expected rejection" for `order_assertion_disabled` with the order assertion intact.
- **Reproduced before the fix.** The implementer reproduced it with the committed `run()` and `classify()` at `cadccd8`. The regression demonstration reproduces it against the reviewed harness at `c16b3b5`.
- **Root cause.** "Exercised" was a property of the output (any difference), not of the intended defect. Amendment 7 closed the case of a mutant suppressed to the exact reference result, but a difference that is only rounding, only in another component, or present in only one series still passed.

### The correction (verification script)
- **Intended defect per mutant (`DEFECTS`).** Each built-in mutant declares, for each injected function or setting, its intended defect: a description, and where it applies with the outcome it must produce there. Examples:
  - a doubled coefficient: that component exactly twice the reference, the other exactly unchanged, wherever the reference component is nonzero;
  - a non-finite oracle value: that component NaN or ±∞, at every call or at the one sample declared;
  - a historical `wrap()`: the documented formula's outcome, including its exceptions;
  - a jump suppression: ΔΩ = 0 wherever the reference |ΔΩ| > π/2.
  All 47 built-in mutants declare one; a mutant without one fails the run (`mutants_without_declared_defect`).
- **Each call is classified** against the reference implementation:

| Kind | Meaning |
|---|---|
| intended | the defect applies, and the mutant shows it |
| unchanged | the defect does not apply, and the mutant equals the reference |
| missing | the defect applies, but the mutant equals the reference |
| unintended | any other outcome: another difference, or a difference where none is intended |

- **`defect_exercised`** now means: the defect is shown at least once, it is never missing, and nothing else differs. A mutant that is not exercised fails the run, as before. A difference alone (rounding, a reassociated fallback, another component, a partial defect) is never evidence.
- **`observe()`** makes the same observation for a given test and set of injected functions, discarding the test's failures. The mutation check uses it on the unmutated script, with the mutant taken from a mutated copy (below).
- **What the observation reads.** It reads only the injected function's arguments and outcomes, never the result of a check. Exercise is therefore not defined by the assertion that is supposed to detect the defect.
- **`differing`** (amendment 7) is still counted and reported, for comparison only. It decides nothing.

### The correction (mutation check)
- **Every mutation declares an exercise predicate.** There are four families:

| Family | Mutations | Intended defect observed |
|---|---|---|
| built-in | 32 (they weaken a check; the evidence is a built-in mutant) | each designated built-in mutant, observed in its designated test of the unmutated script with the mutant taken from the copy; the copy's own record must agree (exercised, or not exercised for the "tests disabled" mutation) |
| formula | 52 (the formula under test is edited) | the copy's `formulas_amendment2` against the unmutated one, over the first-order grid: a component replaced by its value where its condition holds, or scaled by its factor |
| oracle values | 22 (an oracle value replaced inside `check_formulas`) | every value handed to the finite validation, against the unmutated oracle at the same sample |
| injected | 3 (`line_of_nodes_exact` or `wrap` edited) | the copy's function in the exact properties, against the declared defect |

- **The observation is independent.** A separate process (`dr0028_node_signed_mutation_check.py --probe`) loads the unmutated script and the mutated copy. It uses the unmutated script's references, declared defects and tests, and takes only the injected function from the copy. Neither the copy's own recorder nor any check decides whether the defect occurred.
- **A detection requires both** the defect established as exercised and the expected rejection shown. Classification order:
  - process failure, normal execution, inconsistent exit;
  - unexpected exception;
  - **invalid mutation setup** if the intended defect is not established;
  - rejected for another reason;
  - expected rejection.
- **No direct predicate is met by the unmutated script.** All 77 direct predicates (formula, oracle values, injected) are checked against an unmodified copy, and none is exercised there.
- **Allowances (I-11 §2.8), revalidated.** They are unchanged: the E2/E5b wrap guard (oracle ΔΩ = NaN mutant; ValueError "wrap: non-finite angle"; exact stack through E2's identity line or E5b's jump line), and the order-estimate math domain error (the four single-sample oracle ±∞ mutants; ValueError "math domain error"; `check_formulas: p = math.log2(e[-2] / e[-1])`) for the same four mutations.
  - Each raising mutant is now also established as exercised: the probe observes its intended defect in the unmutated test, where it completes.
  - Two new controls keep both allowances classified as expected rejection.
  - The wrong-location and wrong-type controls of amendment 7 still give "unexpected exception".
- **One expectation is tightened.** `M3P6-F3_previous_wrap_implementation` declared `wrap(`, which also matches W2's exactness messages. It now also requires W4's endpoint message, the check of the convention the mutation targets. The earlier predicate is kept, so this is strictly stronger.

### Controls (I-11 §2)
Each control declares the category it must receive, and whether the claimed defect must be established as exercised. There are 23 controls: the 13 of amendment 7 and 10 new ones. `dr0028_node_signed_harness_regression.py` runs every control against `896d52d`, against `c16b3b5` and against the corrected harness.

| Control | Declared category | Exercised | `c16b3b5` (detection) | Corrected |
|---|---|---|---|---|
| **review 11's suppressed import with reassociated fallback** | invalid mutation setup | no | **not met (counted as detection)** | met |
| **the mutant changes only the other formula** | invalid mutation setup | no | **not met** | met |
| **the mutant changes its component by one ulp only** | invalid mutation setup | no | **not met** | met |
| **the mutant shows its defect in one series only** | invalid mutation setup | no | **not met** | met |
| exercised ΔΩ doubling, run failing only because the ΔΩ order assertion is gone | rejected for another reason | yes | met | met |
| copy's own record edited to claim exercise, mutant returning the reference | invalid mutation setup | no | met (fragment absent there) | met |
| allowed wrap-guard exception (E2 finite check removed) | expected rejection | yes | met | met |
| allowed order-estimate exception (`isnan` weakening) | expected rejection | yes | met | met |
| genuine formula injection (one series) | expected rejection | yes | met | met |
| ΔΩ NaN injection claimed as the Δi injection | invalid mutation setup | no | met | met |

- **The four M3P11-F1 regression controls** (in bold) fail against `c16b3b5` and pass against the corrected harness. The five M3P10-F1 regression controls still fail against `896d52d` and pass.
- **One amendment-7 control changes category.** `wrong_reason` (a Δi sign reversal claimed as the ΔΩ sign reversal) was "rejected for another reason"; it is now "invalid mutation setup", because the claimed ΔΩ reversal is not exercised: it is missing everywhere, and Δi differs instead. It is still not a detection. The new control "exercised ΔΩ doubling…" takes over the role of an exercised defect rejected for the wrong reason.
- **Exercise expectations.** The other amendment-7 controls keep their categories, and each now also declares its exercise result. The neutral edit and the four exception controls inside mutants are not exercised. The allowed-exception controls are.

### M3P11-F2: classification of the 18 assertions, corrected (I-11 §3)
- **Amendment 7 classified W5, E1, E2e, E5b-nonfinite and E5b-defined as category B.** That classification was invalid. For each, it demonstrated overlap with another check for one chosen defect, not for the whole property the assertion protects. Review 11 gave a defect for each that only that assertion rejects. All five are category A.
- **Totals:**

| Category | Amendment 7 (invalid) | Amendment 8 |
|---|---|---|
| A, independently important | 6 | **11** |
| B, redundant | 9 | **4** |
| C, diagnostic | 3 | 3 |
| D, uncertain | 0 | 0 |

- **Identities checked against the inventory.** `dr0028_node_signed_assertion_classification.py` locates each of the 18 by its source text. Each selects exactly one of the 35 `failures.append` statements, the 18 are distinct, and they are exactly the 18 statements that the sweep committed at `896d52d` (review 10) found surviving.

**The five reclassified assertions.** Each has a new built-in mutant, designated to its test. Its evidence is executed:
- the mutant's declared defect is exercised: shown, never missing, nothing else different;
- it raises no exception;
- with the assertion present, the designated test rejects it, and every failure it causes comes from that assertion;
- with only that assertion removed, no exact-property or wrapping check reports anything.

| Assertion | Property protected | Mutant (defect) | Intended calls | Failures with / without |
|---|---|---|---|---|
| W5 | periodicity: exactly equivalent angles wrap to the same value, including inputs W2's fixed list lacks | `wrap_not_periodic`: an input one or more turns from 1.0 rad is reduced to 1.01 | 6 | 6 / 0 |
| E1 | the tilt transform is exactly the passive Rot(e, −δ), not merely a proper rotation that keeps B's pole and the endpoints | `tilt_node_origin_offset`: an extra 0.01 rad rotation about the pole (a node-longitude origin offset) | 68 | 1 / 0 |
| E2e | B is equatorial at both endpoints for every tested node, including azimuths E1 does not sample | `tilt_axis_quantized`: tilt-axis azimuth rounded to a 15° table (exact at E1's azimuths; wrong at nodes 37°, 145°, 200°) | 24 | 24 / 0 |
| E5b-nonfinite | every node difference in the azimuth sweep is finite (a non-finite value fails, not merely uncounted) | `oracle_node_nan_at_sweep_azimuth`: NaN at φ = 1° (both tilt signs; 359 defined samples remain) | 2 | 2 / 0 |
| E5b-defined | the node is defined at every sweep azimuth but at most one exact endpoint, not only at the crossings | `oracle_node_undefined_at_sweep_azimuths`: no node at φ = 1° and 2° (both crossings still asserted) | 4 | 2 / 0 |

- **The six A protections of amendment 7** (W2, N1, E2b, E2c, E2d, E5d) are kept. They now also show the same evidence: each defect is exercised under its declared defect, raises no exception, and escapes every check without its assertion.
- **The four category B assertions.** Each has a property-wide argument, whose premises are executed, plus the amendment-7 demonstration:
  - **W1** (result in (−π, π]): W2 compares the same result, at the same input in the same loop, with the exact reduction. Every one of the 108 inputs has its exact reduction in (−π, π], so wherever W1 fails, W2 fails.
  - **W4** (wrap(±π) = +π): ±π are among W2's inputs, and both reduce exactly to +π. So W4 failing implies W2 failing, given that `wrap` returns the same result for the same input. W3 is the diagnostic for that; scope as for W3.
  - **E6-value** (90.2598055437°): E3 makes the identical oracle call (φ = Ω − 90° = 0.0 exactly) and compares ΔΩ with the closed form within noise(30°) = 1.63e-12°. The closed form is 3.79e-11° inside E6's 5e-11° tolerance, so any ΔΩ that E6 rejects deviates from it by more than E3's tolerance.
  - **E6-sign:** at the same call the closed form is +4.53e-3 rad, far above E3's 2.84e-14 rad. So a ΔΩ ≤ 0 is rejected by E3. The committed formula's sign at this (i, Ω − φ) is covered on the first-order grid by the sign check (amendment 6).
- **The three category C assertions** keep their rationale: W3 (determinism of a stateless `wrap`), W6 (guards W5's fixed input list), and E2a (guards the E2 case list).
- **Amendment 7's dependency statements are corrected.**
  - "E1 and E2e protect each other": wrong. Each protects a different part of the transform: E1 its exact convention, E2e equatorial endpoints at azimuths E1 does not sample.
  - "W5 rests on W2": wrong. W2 covers only its fixed inputs.
  - "E5b's defined-sample guard rests on E5c": wrong. E5c counts only the crossing azimuths.
  - The remaining dependencies hold: W1 and W4 rest on W2, and E6 on E3.
- **Sweep, before and after:** amendment 6, 17 detected and 18 surviving; amendment 7, 23 and 12; amendment 8, **28 and 7**. The 7 survivors are exactly the 4 of B and the 3 of C.

### Results
- **Verdict PASS, exit 0**, for:
  - the verification script;
  - the mutation check;
  - the classification (18/18: 11 A, 4 B, 3 C, 0 D);
  - the regression demonstration.
  The sweep is a measurement. Each of the five outputs is byte-identical on a rerun.
- **Mutation check, reported separately (I-11 §5).** These results come from the corrected harness. Amendment 7's 109/109 was measured under its any-difference criterion and is not relabelled.

| Count | Value |
|---|---|
| Mutations attempted | 109 |
| Intended defect established as exercised | 109 |
| Detected for the intended reason (expected rejection) | 109 |
| Not exercised | 0 |
| Rejected for another reason | 0 |
| Unexpected exception | 0 |
| Process failure | 0 |
| Invalid mutation setup | 0 |
| Normal execution (survived) | 0 |
| Controls with their declared category and exercise result | 23 of 23 |
| Direct exercise predicates met by the unmutated script | 0 of 77 |

- **Built-in mutants:** 47 (42 + 5). Each declares its defect, each is exercised (0 missing, 0 unintended calls), and each is rejected by its designated checks.
- **Assertions:**
  - individually protected (category A): 11 of the 18, plus the 17 that the sweep already detected at `896d52d`;
  - intentionally redundant (B): 4;
  - diagnostic (C): 3.
  - The sweep: 35 assertion sites, 28 detected, 7 surviving, 0 exceptions.
- **Finite results unchanged.** Compared with `cadccd8`, no pre-existing output value changed and none was removed. That includes every amendment-7 `calls`, `differing` and `defect_exercised` value. The 315 differences are added keys:
  - per mutant, the defect description and call kinds;
  - the five new mutants;
  - `exercise_criterion`;
  - `mutants_without_declared_defect` (empty).
- **Coverage unchanged:** order 506 (Δi) and 532 (ΔΩ), sign 560 (Δi) and 504 (ΔΩ), each enforced separately.
  - The 1 % Δi oracle error is still rejected by E3 and by E4.
  - The doubled coefficients and reversed signs are still rejected by the order and sign checks of their own formula.
  - Non-finite values are still rejected in every series.
- **Before and after:**

| Count | Amendment 7 | Amendment 8 |
|---|---|---|
| Built-in mutants | 42 | 47 |
| "Exercised" means | any call differs | exactly the declared defect (shown, never missing, nothing else) |
| Exercise decided by | the copy's own record | an independent probe, and the copy's record must agree |
| File-level mutations detected | 109/109 (amendment-7 criterion) | 109/109 (exercise established and expected rejection) |
| Controls | 13 | 23 |
| Classification A / B / C / D | 6 / 9 / 3 / 0 (invalid for 5) | 11 / 4 / 3 / 0 |
| Sweep: detected / surviving | 23 / 12 | 28 / 7 |
| Mutation check run time | about 6 min | about 8 min (one probe process per run) |

- **Unchanged definitions.** An AST comparison with `c16b3b5` shows that only these existing top-level definitions changed: `instrumented`, `exercised`, `mutant_failures`, `EXACT_MUTANTS` and `main`, plus the docstring and one added module-level loop (building `DEFECTS`). `exact_properties`, `check_formulas`, `wrap`, `finite`, the formulas, the grid, the tolerances and the minima are unchanged.
