# Decision Request: M3 atmosphere validity boundary, decay termination, and the Q10 table residuals

**Status:** OPEN (BLOCKED ON OWNER)  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A. Raised by the resolutions of DR-0024 (Q8, Q10) and DR-0026 (Q-G3-6), as those resolutions require.
- Source keys are defined in DR-0024 §3.1.

Nothing here is implemented. No value below is a default.

## Problem
Two numerical questions were deliberately left open when G1–G3 were resolved:
- **A. Where a decaying M3 run ends.** The owner approved the principle: no indefinite extrapolation below the modelled domain; an explicit validity boundary and a re-entry/termination event; no invented universal altitude. The number, and how it is set, are undecided.
- **B. Three cells of the atmosphere table** that the Q10 check could not confirm against an author-published source (DR-0024 §3.4).

Neither blocks T0, which uses them only as explicit, labelled spike inputs. A blocks T2/T3 (drag integration, end conditions). B blocks pinning the M3 dataset identity (T2).

## Constraints
- Preserve the source model faithfully (DR-0024 Q5a). No value is altered to force continuity.
- Do not invent a numerical altitude to close a decision.
- Scenario parameters are explicit inputs; constants and datasets are pinned (DR-0024, DR-0026).
- M1/M2 behaviour, including the `impact` end at spherical altitude ≤ 0 (SCI-0006), is unchanged.

## A. Validity boundary and termination
### Facts
- **The table's modelled domain** starts at the 0 km band (0.010 km in the author's file) and has no upper limit: the top band applies above its base [GMAT-UG; DR-0024 §3.4]. Geodetic height is never below spherical altitude for a point outside the ellipsoid, because the ellipsoid lies inside the sphere of radius a. So for committed states the v1/v2 `impact` rule (spherical altitude ≤ 0) is reached no later than geodetic height 0.
- **RK4 intermediate stages** can evaluate states slightly below a committed state's height. A density function that raises an exception there would turn a legitimate final step into a failure. The behaviour below the lower edge must therefore be defined explicitly.
- **The drag model's physical assumptions** (free-molecular flow, constant C_d, rigid body) fail well above the ground. The project holds **no cited source** for a specific altitude at which they fail. Altitudes commonly used as conventions exist (for example a re-entry "entry interface" and the 100 km Kármán line), but none has been read and verified for this request, so none is proposed.

### Options
- **A1 — A mandatory per-scenario v3 field** (for example `altitude_floor_m`, geodetic) with no default. Reaching it ends the run with a defined outcome (`reentry`, per DR-0026). Each scenario's value cites its basis.
  - Pros: no universal number; validation scenarios state what they assume.
  - Cons: every drag scenario must justify a value.
- **A2 — One pinned project-wide floor** in the physics configuration (part of `physics_id`), with a cited basis chosen by the owner.
  - Pros: one identity, consistent across scenarios.
  - Cons: needs a defensible source now.
- **A3 — The table's lower edge only (0 km geodetic) plus the existing `impact`.**
  - Pros: uses only the source's own domain.
  - Cons: integrates drag through altitudes where its assumptions fail, which the owner's principle discourages.
- **Sub-question A-s (any option):** density for an intermediate RK4 stage below the lower edge: (i) evaluate the lowest band (the source's own formula) only for intermediate stages, with the committed-state boundary check ending the run; or (ii) fail closed as a run error.

### Recommendation
- **A1, with A-s (i).** A1 avoids inventing a universal number and keeps the decision visible in each scenario.
- The value used by M3 reference scenarios is to be proposed at the T0 checkpoint **only if** a source is found, and otherwise left to owner judgment, explicitly labelled as such.

## B. Q10 residual table cells
### Facts (DR-0024 §3.4; `q10_table_check_results.json`)
| Cell | GMAT R2026a file | Author's `ATMOSEXP.DAT` | Effect |
|---|---|---|---|
| Lowest base altitude | 0.0 km | 0.010 km | Heights below 10 m only |
| 900 km scale height | 181.05 km | 181.045 km | Above 900 km only; 2.8e-5 relative in H |
| 1000 km row | 3.019e-15 kg/m³, 268.00 km | absent | Above 1000 km only |

The printed table was not available to the project.

### Options
- **B1 — Pin the GMAT R2026a file unchanged** as the dataset of record, with provenance "GMAT R2026a, citing Vallado 5th ed. §8.6; 25/28 rows confirmed against the author's data file". Keeps the exact GMAT configuration.
- **B2 — Pin the author's file values** (27 rows; top band 900 km). Loses the exact GMAT match above 900 km; GMAT would need a generated table.
- **B3 — Defer pinning** until a printed copy is checked; restrict M3 reference missions to below 900 km meanwhile.

### Recommendation
- **B1**, together with a request to check the printed table when a copy is available. Any difference found later creates a new dataset identity; it never edits the pinned one.

## Impact
- **Architecture:** A decides one v3 field and one outcome; B decides one dataset digest.
- **Science/validation:** SCI-0015 and SCI-0016 limitations; boundary tests (DR-0025).
- **Dependencies:** none.
- **Development effort:** small.
- **Token/compute impact:** negligible.
- **Reversibility:** high before T2. After T2, a change creates a new `physics_id`.

## Blocked work
- A: T2/T3 end-condition and drag-integration design.
- B: pinning the M3 atmosphere dataset identity (T2).

## Work continuing independently
- T0 spike (authorized), with explicit labelled inputs.

## Requested response
`A1`/`A2 <value + basis>`/`A3`, `A-s (i)`/`(ii)`, and `B1`/`B2`/`B3`, or `discuss`.

## Resolution
**Decision:** _pending_  
**Reasoning/notes:**  
**Follow-up:**
