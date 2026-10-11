# Decision Request: Burns in progress or pending when a scenario stops

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-11  
**Related milestone/issue:** M2 T4 (runner timeline, `stop.duration_s`); DR-0010 #4; DR-0014 §5; T3 contract

## Problem
A scenario can stop while an accepted burn is still burning, or before a scheduled burn ignites. Two cases cause this:
- a `duration_s` stop that falls inside the burn;
- an `orbits` stop, or a failure (impact, escape, non-finite), reached first.

The approved event contract (DR-0014 §5, T3) has `BurnEnded.end_cause ∈ {completed, propellant_depleted}` and no way to say "the simulation ended first". The Tech Lead asked T4 to handle burns that cross the stop time correctly, and **not to invent event types or semantics without a DR**. This DR asks how such burns should be represented.

## Current implementation (T4, within the approved contract)
The stop is an **observation horizon, not an engine command**.
- **Physics.** The engine is not cut off at the stop; the simulation simply ends. Physics up to the stop is identical to a longer run (tested).
- **Active burn.** It has `CommandAccepted` and `BurnStarted` but **no `BurnEnded`**. The final `PropulsionSampled` (always emitted at the final tick) shows `engine_state: "burning"` and `active_burn_id`. `RunResult.final_propulsion` and the CLI summary report `final_engine_state` and `active_burn_id_at_stop`.
- **Pending burn.** It has `CommandAccepted` only. The final sample lists it in `pending_burn_ids` (`engine_state: "scheduled"`), and the summary has `pending_burn_ids_at_stop`.
- **Status.** `SimulationCompleted.status` is `success` when the stop condition was reached without a failure. A burn in progress does not make the run fail.
- **Boundary cases (tested):**
  - a cutoff exactly at the stop time is emitted (`BurnEnded`);
  - an ignition exactly at the stop time is emitted (`BurnStarted`, zero propellant used).
- **Timeline entries never submitted.** If the run ends first (orbits stop, failure), they are not submitted, emit no event, and are listed in `RunResult.unsubmitted_command_ids` and the summary. For a `duration_s` stop, a submission at or after the stop time is a scenario validation error.

## Constraints
- No new event types, rejection codes or permission semantics without approval.
- Do not invent physics: the engine has no reason to stop at an arbitrary observation horizon.
- Deterministic; M1 bytes unchanged; T3 schemas are a contract (`schema_version: 1`).

## Options
### A — Keep the current representation (recommended for M2)
**Pros**
- No contract change.
- The truth at the stop is fully machine-readable from the final `PropulsionSampled`, `RunResult` and the summary.
- It never pretends the engine stopped.

**Cons**
- A consumer pairing `BurnStarted`/`BurnEnded` must also read the final sample to tell "still burning" from "missing event".

### B — Add `end_cause: "simulation_ended"` to `BurnEnded`, emitted at the stop for an active burn
**Pros**
- Every `BurnStarted` gets a matching `BurnEnded`.

**Cons**
- **Misleading:** the engine did not stop. A later replay or extension of the same scenario would contradict the event.
- Changes an approved enum, so a contract change for existing consumers.
- Pending burns still need separate handling.

### C — New event `BurnInterrupted` / `SimulationEndedWithActiveBurns`
**Pros**
- Explicit, and leaves `BurnEnded` meaning "the engine stopped".

**Cons**
- A new public event type, which needs a schema addition and tests.
- Information is equivalent to the final `PropulsionSampled` in option A.

### D — Forbid it: reject scenarios whose timeline burns could extend past `stop.duration_s`
**Pros**
- Simple logs.

**Cons**
- **Not decidable at load:** the scenario cannot know whether a command will be accepted, and the planned cutoff depends on propellant state and policy.
- Applies only to duration stops. Removes a legitimate case (observation window shorter than a burn).

## Recommendation
**A.** It represents the truth without inventing an engine event or a new schema. Revisit if a crew or analysis consumer needs explicit pairing; option C is the clean extension.

## Impact
- Architecture: none for A; B and C change the T3 event contract.
- Science/validation: none. T5 validators will read `BurnEnded` only for burns that ended.
- Dependencies: none.
- Development effort: A done. B or C: small (schema, runner, tests, contract).
- Token/compute impact: none.
- Reversibility: high. Nothing downstream depends on it yet.

## Blocked work
- None. T4 implements A, which uses only approved semantics. If B or C is chosen, the change is small and additive.

## Work continuing independently
- T4 review and Proof; T5 planning (not started without authorization).

## Requested response
`A` / `B` / `C` / `D` / discuss.

## Resolution
**Decision:** <pending>  
**Reasoning/notes:**  
**Follow-up:**
