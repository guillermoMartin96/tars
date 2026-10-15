# Decision Request: Burn direction, pointing model, and frames

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion ([plan](../../milestones/M2-propulsion.md))

## Problem
"Prograde" and "retrograde" need a precise definition. There is no attitude model, so the simulator must decide how thrust direction behaves *during* a finite burn. VAL-0008 measured this as a material choice for the reference burn (77 s, 0.38 m/s²):
- tracking the instantaneous velocity vs holding the ignition-time velocity direction fixed changes SMA by **69 m**;
- the two trajectories end **4.6 km** apart after about 10 orbits.

## Definitions (proposed)
- **Frame:** all vectors in the M1 Earth-centred J2000-aligned inertial frame (SCI-0003, GMAT `EarthMJ2000Eq`).
- **VNB** (Velocity–Normal–Binormal), Earth origin, the same definition as GMAT `Axes = VNB` [GMATMS §4.2.7]:
  - V̂ = v/|v|;
  - N̂ = (r × v)/|r × v| (orbit normal);
  - B̂ = V̂ × N̂.
- **Prograde** = +V̂; **retrograde** = −V̂. Velocity is inertial, relative to Earth's centre. Earth rotation is not modelled (SCI-0003).

## Constraints
- Must be validatable against GMAT (DR-0015) and analytically.
- Must not imply attitude dynamics we have not researched.
- Must be expressible as a structured command a future Pilot role can issue.

## Options
### A — Velocity-tracking VNB pointing (recommended)
The thrust direction is re-evaluated from the current (r, v) at every derivative evaluation. This models an ideal attitude controller holding the vehicle on the velocity vector. GMAT: `ChemicalThruster.CoordinateSystem = Local`, `Origin = Earth`, `Axes = VNB`, direction (±1, 0, 0).

**Pros**
- Matches the operational meaning of a "prograde burn"; standard in mission design.
- GMAT supports it natively; VAL-0009 measured 0.12 mm SMA agreement with this exact setup.
- The direction is a smooth function of state, so RK4 keeps its order inside the burn (VAL-0008: order ≈ 4.2–4.5).
- Energy gain is maximal for a given propellant, since v·a is maximized.

**Cons**
- Assumes perfect, instantaneous attitude tracking (SCI-0011).

### B — Inertially fixed direction, captured at ignition
The direction is +v̂ (or −v̂) at the ignition instant, held constant in inertial space. GMAT: thruster in `EarthMJ2000Eq` with the captured vector, or `Local` with `Axes = MJ2000Eq`.

**Pros**
- Models an attitude-hold burn, also common in practice.
- Simplest force law.

**Cons**
- For a finite burn it is not exactly "prograde" after ignition.
- Requires capturing a vector into the command or engine state at ignition. That is one more piece of simulator-owned state.

### C — Both, as a command field (`pointing: "track" | "inertial_hold"`)
**Pros**
- Teaches the difference explicitly; useful for later maneuvers (plane changes, rendezvous).

**Cons**
- Doubles the validation matrix (GMAT reference and gates per mode) in the first propulsion milestone.

## Recommendation
**Option A** for M2. The command schema carries a `direction` enum (`prograde` | `retrograde`). The thrust law sits behind a pointing function, so B/C can be added without changing the command path. Arbitrary VNB vectors are deferred until a mission needs them.

## Impact
- Architecture: the thrust force depends on (r, v, m) and engine state (DR-0013).
- Science/validation: gated GMAT VNB comparison; sign checks (prograde raises SMA, retrograde lowers it).
- Dependencies: none.
- Development effort: low.
- Token/compute impact: none.
- Reversibility: high.

## Blocked work
- Thrust direction implementation and GMAT reference script.

## Work continuing independently
- Mass/flow model and step splitting.

## Requested response
`A` / `B` / `C` / `discuss`.

## Resolution
**Decision:** APPROVED — A (Tech Lead, 2026-10-09): velocity-tracking prograde thrust for the reference scenario.  
**Reasoning/notes:**
- **Preserve an extensible direction interface for future guidance modes.**
- Direction laws are implemented behind a `DirectionLaw` protocol: a function of the read-only (t, r, v) returning a unit vector. Prograde and retrograde are two implementations.
- Inertial hold or guidance-commanded vectors can be added later without changing the propulsion model or the command path.

**Follow-up:** T1.

## Sources
- **[GMATMS]** GMAT R2026a Mathematical Specification (draft) §4.2.7, "VNB Thruster System"; GMAT help `ChemicalThruster` (Axes = VNB).
- **[VAL]** Vallado (2013) ch. 3 (coordinate systems, including satellite-based frames).
- VAL-0008, VAL-0009.
