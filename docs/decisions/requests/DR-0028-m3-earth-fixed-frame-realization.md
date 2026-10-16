# Decision Request: realization of the M3 Earth-fixed frame (follow-up to DR-0024 Q4)

**Status:** RESOLVED — APPROVED: J-ax-1, with requirements (Tech Lead, 2026-10-15, "M3 Planning — Resolve Review 03 and DR-0028", section 2). See "Resolution"; where the body below differs from the Resolution, the Resolution governs. No Earth-orientation implementation is authorized.  
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
- **No longitude, no ground position:** without an Earth rotation angle the model has no terrestrial longitude, so it cannot give sub-satellite points, ground tracks, site visibility or local solar time.
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
