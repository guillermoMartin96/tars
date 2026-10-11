# M2 command and event contract (T3)

**Status:** implemented in `12d8818`; revised after review M2-T3-review-01 in `defd23f`. Authority: DR-0014 (approved; vocabulary amended 2026-10-10), DR-0017, ADR-0007.  
**Code:** `src/tars/sim/commands.py`, `Simulator.submit()`, `src/tars/events/schema.py`, `src/tars/sim/burn_events.py`.  
**Tests:** `tests/test_commands.py`.

## Versioning
- `BurnCommand` and every M2 event carry `schema_version: 1`. It must be the **integer** 1; `true` and `1.0` are rejected.
- M2 event types are **additive** under version 1, and the M1 event types are unchanged. The M1 golden event-log hash `7a4e1877…` is preserved.
- A breaking change to any field requires a new schema version and a decision.

## BurnCommand (input)
| Field | Type | Notes |
|---|---|---|
| `schema_version` | `1` | |
| `type` | `"BurnCommand"` | |
| `command_id` | string `^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$` | Issuer-chosen; consumed once accepted. `#` is reserved for burn IDs. |
| `issuer` | valid-Unicode string, 1–64 characters | Recorded provenance, **no authority**. Permission checks belong in front of `submit()` (future crew layer). |
| `ignition_t_s` | finite real | Any time ≥ now (DR-0014 2A). |
| `direction` | `"prograde"` \| `"retrograde"` | |
| `duration_s` | finite real | Its sign is checked as `non_positive_duration`, not as a schema error. |
| `on_insufficient_propellant` | `"reject"` (default) \| `"burn_to_depletion"` | DR-0014 3C. |

The schema is strict: no bool, string or None coercion into numbers, no NaN or inf, no extra fields.

## Submission → receipt
`Simulator.submit(command | mapping) -> CommandReceipt` (frozen).
- It never raises for a bad command.
- A rejected command changes **nothing**: physical state, engine schedule, burn counter, and the command-ID registry.
- Accepted payloads are an **exact** `BurnCommand` or any `collections.abc.Mapping` (`ffa4c3c`).
  - **Instances.** Stored field values are read directly from the instance, with no Pydantic serialization hook. Attributes beyond the declared fields mean tampering, which is `schema_invalid`.
  - **Mappings** are copied into a plain dict.
  - **Subclass instances** are `schema_invalid`, and none of their methods is called.
  - **Keys and values.** Every key must be an exact `str`, and every value an exact `str`, `int` or `float` (bool and subclasses rejected). The canonical command therefore never holds or aliases caller-defined objects.
- Any ordinary exception while handling a payload becomes `schema_invalid` (`<payload>: unprocessable`); process-control exceptions propagate (`ef0c626`).
- **Accepted:** `status`, `command_id`, `issuer`, `command` (verbatim intent), `burn_id`, `plan` (exact executed plan), `tick`, `t`.
- **Rejected:** `reason`, one of the approved codes below, plus `detail`.
  - For a schema-valid command: `command` (verbatim intent).
  - For a malformed payload: `schema_errors` ("field: error_type", bounded; input values are never echoed). `command_id` and `issuer` are echoed only if they are a valid ID or valid Unicode.

**Approved rejection codes** (exact, machine-readable):
`schema_invalid`, `non_positive_duration`, `ignition_in_past`, `overlaps_scheduled_burn`, `engine_busy`, `no_propellant`, `insufficient_propellant`, `duplicate_command_id`, `no_propulsion_configured`, `burn_unschedulable`.

**Precedence** (a command failing several rules reports the first):
1. schema;
2. duplicate command ID (already used by an **accepted** command);
3. no propulsion configured (`no_propulsion_configured`; checked first by the T2 engine path);
4. non-positive duration;
5. ignition in the past;
6. engine conflicts (`engine_busy`, `overlaps_scheduled_burn`);
7. propellant and schedulability (`no_propellant`, `insufficient_propellant`, `burn_unschedulable`).

Engine-level `schedule_burn` (the T2 interface, unchanged) follows the same order from step 3.

Command-ID consumption, strict input and this precedence were confirmed as contract by the Tech Lead on 2026-10-11 (DR-0014, amendment "T3 semantics confirmed").

## Correlation IDs
| ID | Assigned by | Stability |
|---|---|---|
| `command_id` | Issuer | Consumed only on acceptance. A rejected command can be corrected and resubmitted under the same ID. |
| `burn_id` | Simulator: `burn#000001`, `burn#000002`, … | Deterministic. Only accepted burns are numbered; `submit` and `schedule_burn` share one sequence. |

Every burn event carries `burn_id` (pattern `^burn#[0-9]{6,}$`). It also carries `command_id` (command-ID pattern) when the burn came from `submit()`. Burns from engine-level `schedule_burn` (the exact T2 signature, which takes no command ID) have `command_id: null`. Both ID formats are enforced in the event schemas.

## Events (all `schema_version: 1`, strict, frozen, finite; vectors are 3-tuples; free-form strings valid Unicode)
| Event | Built from | Commanded intent | Executed outcome |
|---|---|---|---|
| `SpacecraftConfigured` | `SpacecraftSpec` | — | configuration, mass flow, DR-0017 budget |
| `CommandAccepted` | receipt | `commanded_ignition_t_s`, `commanded_duration_s`, direction, policy | `planned_*` (exact plan), `timing_delta_v_error_mps` |
| `CommandRejected` | receipt | `command_id`, `issuer` (if readable); `direction`, `on_insufficient_propellant`, `commanded_ignition_t_s`, `commanded_duration_s` (null if schema-invalid) | `reason`, `detail`, `schema_errors` |
| `BurnStarted` | ignition transition | `commanded_ignition_t_s`, `commanded_duration_s`, `planned_cutoff_t_s`, `planned_end_cause` | `event_t_s` (exact, may lie inside a tick), r, v, thrust unit vector, propellant, mass |
| `BurnEnded` | ignition + cutoff transitions | `commanded_duration_s`, `planned_propellant_used_kg` | `end_cause` (`completed` \| `propellant_depleted`), `executed_duration_s`, integrated `propellant_used_kg`, `sensed_delta_v_mps`, `rocket_equation_delta_v_mps`, r, v, mass |
| `PropellantDepleted` | depletion cutoff only | — | `residual_propellant_kg` (DR-0017 D1a) |
| `PropulsionSampled` | `PropulsionSnapshot` + `StateSnapshot` (same tick) + `SpacecraftSpec` | — | propellant, mass, sensed Δv, engine state, active and pending burn IDs, truth `thrust_acceleration_mps2` (zero unless burning) |

- **Event times:** the envelope's `tick` and `t` are the step in which the event occurred, and `event_t_s` is the exact engine-event time (the same convention as `OrbitCompleted.crossing_t`).
- **Emission order and cadence** belong to the runner (T4, not authorized yet). Converters are pure and deterministic, so identical scenarios and commands give byte-identical JSONL on the same platform (tested).

## Explicitly out of scope
- Abort/cancel and Δv-target commands (DR-0014: unapproved follow-ups).
- Crew permissions and authority checks.
- Scenario timeline wiring (`submit_t_s`) and event emission (T4).
