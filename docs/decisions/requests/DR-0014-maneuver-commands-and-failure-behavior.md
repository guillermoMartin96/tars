# Decision Request: Maneuver command interface, failure behavior, and event contract

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion ([plan](../../milestones/M2-propulsion.md))

## Problem
M2 introduces the project's first **command**: the interface a future AI crew will use to change physical reality. Its shape, validation rules, and failure behavior will be inherited by the crew layer. Several choices are material:
- how a burn ends (duration vs Δv target);
- when it starts;
- what happens with insufficient propellant;
- how commands and burns are recorded.

## Constraints
- The simulator validates and executes. A command can only request; it never mutates r, v, or mass (architecture invariant 1).
- Machine-readable from day one: every command outcome and engine transition is an event (invariant 5).
- Deterministic and LLM-free (invariant 3). Commands in M2 come from the scenario timeline; no AI crew.
- Crew roles and permissions are **not** defined here. Any permission model needs its own DR (invariant 2).
- M1 event bytes unchanged (DR-0013 4A).

## Proposed command schema (Pydantic, strict, `allow_inf_nan=False`)
```json
{
  "type": "BurnCommand",
  "command_id": "burn-001",
  "issuer": "scenario_timeline",
  "ignition_t_s": 600.0,
  "direction": "prograde",
  "duration_s": 77.3,
  "on_insufficient_propellant": "reject"
}
```
- `issuer` is an opaque, recorded provenance string. In M2 it is always `scenario_timeline`. It carries **no authority**; enforcement is future crew work.
- Scenario timeline: `commands: [BurnCommand, …]`. Each is submitted at its `submit_t_s` (default 0) through `Simulator.submit()`.

## Options
### 1. Burn termination
- **1A — Duration only (recommended for M2).** Exact, simplest to validate; GMAT's `Propagate {ElapsedSecs}` matches it directly.
- **1B — Δv target (ideal accelerometer cutoff).** Under DR-0011 the duration follows analytically at ignition: T = (m0/ṁ)·(1 − exp(−Δv/(Isp·g0))). Useful for crew commands, but it is a guidance function. Recommended as a *post-slice* addition if approved; the sensed-Δv telemetry is built in 1A anyway.
- **1C — Both.**

### 2. Ignition timing
- **2A — Any time ≥ submission time (recommended).** Split-step integration (DR-0013 3A) makes off-grid ignition exact.
- **2B — Tick-aligned ignition only.** Simpler validation, but it constrains the future crew artificially.

### 3. Insufficient propellant
Required propellant = ṁ·duration is known exactly at validation time.
- **3A — Reject at submission.** Safe, but then the depletion flame-out path is never exercised by a mission.
- **3B — Accept; burn until depletion.** Realistic engine behavior, but silently delivers less than commanded.
- **3C — Per-command policy `on_insufficient_propellant: "reject" | "burn_to_depletion"`, default `reject` (recommended).**
  - Default is safe. The partial-burn path is explicit, tested, and reported (`BurnEnded.cause = "propellant_depleted"`, delivered vs commanded duration).
  - Depletion is enforced physically, not just by validation: the engine stops at the exact depletion time whatever the validation said, and propellant never goes negative.

### 4. Validation and rejection (applies to all options)
Rejected commands produce `CommandRejected` with a stable reason code and **no state change**. Proposed codes:
- `schema_invalid` (unknown direction, non-finite, extra fields)
- `non_positive_duration`
- `ignition_in_past`
- `overlaps_scheduled_burn` (one engine; no overlapping burns)
- `engine_busy`
- `no_propellant`
- `insufficient_propellant` (policy `reject`)
- `duplicate_command_id`
- `no_propulsion_configured`
- `burn_unschedulable` *(added by amendment, 2026-10-10; see Resolution)*

**Out of M2 scope:** abort/cancel commands. Proposed as a follow-up once the interface is approved (a `CancelBurn` with its own validation), not in the slice.

### 5. Event contract (all frozen Pydantic models, JSONL, existing envelope `schema_version`, `type`, `tick`, `t`)
| Event | When | Key payload |
|---|---|---|
| `SpacecraftConfigured` | after `SimulationStarted`, only if propulsion is configured | dry mass, propellant mass, engine F, Isp, g0, ṁ, pointing model |
| `CommandAccepted` | on valid submission | full command echo, predicted propellant, predicted cutoff time |
| `CommandRejected` | on invalid submission | command echo (or raw input), reason code, detail |
| `BurnStarted` | at ignition (exact `event_t`, which may be inside a tick) | command_id, mass, propellant, direction unit vector (ECI), r, v |
| `BurnEnded` | at cutoff/depletion | command_id, `cause` ∈ {`completed`, `propellant_depleted`}, commanded vs actual duration, propellant used, sensed Δv, rocket-equation Δv, r, v, mass |
| `PropulsionSampled` | each telemetry sample when propulsion is configured, plus each tick while burning | propellant mass, total mass, engine state, thrust acceleration vector |
| `PropellantDepleted` | when propellant reaches zero | t, command_id |

**Schema versioning:** existing types and `SimulationStarted` are unchanged, so M1 bytes do not change. New types are additive under `schema_version` 1. The scenario schema gets `schema_version: 2` for files with `spacecraft` / `commands` / `stop.duration_s`; version-1 scenarios load and behave exactly as before.
- The alternative, bumping the event schema to 2 everywhere, would change M1 bytes and the golden hash, so it is not recommended.

### 6. Future crew interface (design intent only; no implementation)
The same `submit(BurnCommand) -> CommandReceipt` is the single entry point a Pilot tool would call through a provider-independent tool adapter. The receipt is structured (accepted / rejected + reason), so an agent can reason about failures without parsing text. Permission checks would sit *in front of* `submit()` in the crew layer, never inside physics.

## Recommendation
**1A, 2A, 3C, plus §4–§6 as written.** 1B (Δv target) and cancel/abort are candidate follow-ups after the vertical slice, each needing explicit approval.

## Impact
- Architecture: defines the first command boundary and its events; no permission model.
- Science/validation: the depletion path is validated analytically (GMAT throws at depletion; VAL-0009).
- Dependencies: none.
- Development effort: moderate (validation matrix and event tests).
- Token/compute impact: none.
- Reversibility: medium. Event and command schemas become a contract for later milestones.

## Blocked work
- Command/event schema code, runner timeline, invalid-command and depletion mission tests.

## Work continuing independently
- Propulsion model, simulator step splitting, REV-012.

## Requested response
Per item: `1A|1B|1C`, `2A|2B`, `3A|3B|3C`; accept or amend §4–§6.

## Resolution
**Decision:** APPROVED — 1A, 2A, 3C (Tech Lead, 2026-10-09):
- duration-based burns;
- arbitrary valid start times;
- insufficient propellant rejected by default;
- explicit `burn_to_depletion` opt-in.

**Reasoning/notes:**
- §4–§6 accepted as the design basis.
- Δv-target cutoff (1B) and cancel/abort remain unapproved follow-ups.
- No permission model is introduced.

**Follow-up:** T1 provides the propellant-sufficiency check and burn-schedule representation. Command/event schemas are T3.

**Amendment — rejection vocabulary (Tech Lead, 2026-10-10; escalated from M2-T1-review-01):**
- `schema_invalid` is retained as defined in §4. It covers non-real or non-finite numbers, unknown enums (direction, policy), and extra or malformed fields.
- `invalid_input` is **not** introduced. The T1 code that used it is migrated.
- New code **`burn_unschedulable`**: a structurally valid burn command that cannot be scheduled with an exact, representable plan. Examples:
  - the cutoff is not finite, or not strictly after ignition;
  - the depletion time underflows the clock;
  - the planned propellant consumption underflows to zero.
- The approved vocabulary is §4 plus `burn_unschedulable`. T3 must use exactly these stable, machine-readable codes.
