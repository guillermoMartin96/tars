# Decision Request: Milestone 2 scope, roadmap gap, and reference scenario

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion & Orbital Maneuvers ([plan](../../milestones/M2-propulsion.md))

## Problem
The kickoff asks to compare the proposed M2 scope with "the existing roadmap". **The repository has no roadmap document.** The only forward-looking material is:
- the command chain in `playbook/architecture.md`: `execute_burn(command) -> propulsion model -> propellant/thermal effects -> force/acceleration -> numerical integration -> new physical state -> sensors/telemetry`;
- "reconsider" triggers in ADR-0002/0003/0004 and DR-0008 that anticipate thrust;
- deferred finding REV-012.

The scope must therefore be fixed from the kickoff proposal plus these documents. Several discrepancies need a decision, along with the reference spacecraft and scenario that every M2 gate will be measured on.

## Discrepancies between the proposal and the repository
| # | Item | Repository says | Proposal says | Recommendation |
|---|---|---|---|---|
| 1 | Roadmap | none exists | "compare against roadmap" | Record M2 scope in `docs/milestones/M2-propulsion.md`. A multi-milestone roadmap is the Tech Lead's to define; not created here. |
| 2 | Thermal effects | in the architecture command chain | absent | **Non-goal for M2.** No scientific basis has been researched; the chain is conceptual. |
| 3 | Sensors | chain ends in "sensors/telemetry" | telemetry only | M2 telemetry is **truth state**. Sensor models (noise, bias) are a non-goal. |
| 4 | Stop condition | M1 stops after N ascending-node passages; timeout guard uses the *initial* period | burn changes the period | Add a **duration** stop condition (`stop.duration_s`) for M2 scenarios. M1 semantics unchanged. |
| 5 | Force model | point mass only (DR-0002) | not stated | **Keep point-mass gravity only.** Adding J2/drag would make "orbital change from the burn" inseparable from perturbations and lose the exact Kepler oracle for the coast arcs. |
| 6 | REV-012 deferral | "investigate before the first time-dependent force model" | — | Thrust is scheduled in time, so the trigger applies conservatively. VAL-0009 links the GMAT burn residual to the same epoch arithmetic. Investigate before gated GMAT burn comparison (DR-0015). |
| 7 | "Structured maneuver commands" vs AI crew | crew/permissions not implemented; changes need a DR | no AI crew in M2 | Commands come from a **scenario timeline**. The interface is designed so a future Pilot role can use it. No permission model in M2 (DR-0014). |

## Constraints
- M1 approvals, thresholds, scenario and references are unchanged. The M1 scenario must produce a byte-identical event log (golden `events_sha256 = 7a4e1877…`).
- Never invent scientific behavior; spacecraft parameters need a cited basis.
- The first vertical slice is a single manual prograde burn from stable LEO.

## Options — reference spacecraft and scenario
All options start from the approved M1 initial state (circular 250 km, i = 51.6°, ascending node, WGS 84, RK4 dt = 10 s). This reuses the validated M1 configuration and the GMAT setup.

### A — Apogee-class biprop engine, about +100 km apoapsis raise (recommended)
- Engine: **490 N, Isp 312 s**, nominal values for the Aerojet Rocketdyne / L3Harris **R-4D-11** class. The vendor sheet gives 311 s (164:1 nozzle) and 315.5 s (300:1 nozzle); 490 N is the nominal thrust.
- Spacecraft: **1000 kg dry + 300 kg propellant** (illustrative; there is no project vehicle yet).
- Slice burn: prograde at t = 600 s for **77.3 s** (≈ 29.3 m/s, 12.38 kg). Apoapsis goes from 250 to ≈ 351 km, periapsis stays 250 km. Duration is deliberately not a multiple of dt, so step splitting is exercised.
- Coast to 53 700 s, the same horizon as the M1 GMAT comparison.

**Pros**
- Burn duration (≈ 1.4% of the period) is long enough for finite-burn effects to be real but measurable. Acceleration 0.38 m/s².
- Already measured in VAL-0008/0009: RK4 error 0.29 m; GMAT agreement 1.2 cm.
- Cited, real engine class.

**Cons**
- Spacecraft masses are illustrative, not a real vehicle.

### B — Small monopropellant thruster (≈ 22 N, Isp ≈ 220 s)
**Pros**
- Typical small-satellite propulsion.

**Cons**
- A 29 m/s burn would take about 30 min (a third of an orbit): a long-arc steering problem, not the "single burn" slice.
- Larger finite-burn losses complicate the first analytic comparison.
- Cited source not yet researched.

### C — Large engine, near-impulsive burn (≈ 10 kN)
**Pros**
- Very close to impulsive theory.

**Cons**
- Burn lasts only a few seconds, shorter than dt. Finite-burn effects stay below meaningful measurement, so it does not exercise the capability.

## Recommendation
Option **A**, with the scope and non-goals in the M2 plan (§2), and resolutions 1–7 above.

## Impact
- Architecture: adds a duration stop condition and a scenario schema version (DR-0013/0014).
- Science/validation: all M2 thresholds are measured on this scenario. Changing it means re-measurement, as with M1.
- Dependencies: none.
- Development effort: low; reuses the M1 configuration.
- Token/compute impact: negligible. The scenario runs in seconds.
- Reversibility: high before thresholds are approved; afterwards, re-measurement is required.

## Blocked work
- Scenario file, GMAT M2 reference, threshold measurement.

## Work continuing independently
- Propulsion pure-model unit tests (after DR-0011), architecture work (after DR-0013), REV-012 investigation.

## Requested response
`A` / `B` / `C` / `A with changes: …`; plus confirm or amend resolutions 1–7.

## Resolution
**Decision:** APPROVED — A, with resolutions 1–7 (Tech Lead, 2026-10-09).  
**Reasoning/notes:**
- The R-4D-11-class engine (490 N, 312 s), 1000 kg dry + 300 kg propellant, and the 77.3 s prograde burn from the M1 orbit are approved as the **reference case**.
- They are **configurable reference-case parameters, not universal assumptions.** Engine, tank and burn values are inputs to the propulsion model (EngineSpec/TankSpec), never constants in physics code. Scenario files supply them.
- Thresholds measured on this case apply to this case only, as with M1.

**Follow-up:**
- T1 implements configurable specs.
- The scenario file is created in T4 (needs separate authorization).

## Sources
- L3Harris (Aerojet Rocketdyne), *Bipropellant Rocket Engines* spec sheet (2024/2025), R-4D-11: Isp 311 s (164:1) / 315.5 s (300:1); thrust range 378–511 N. https://www.l3harris.com/sites/default/files/2025-05/l3harris-ar-bipropellant-rocket-engines.pdf
- "Aerojet High-Performance Bipropellant Apogee Engines", IAC-10.C4.1.8 (2010): R-4D-11 nominal thrust 490 N. https://iafastro.directory/iac/archive/browse/IAC-10/C4/1/8239/
