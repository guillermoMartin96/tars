# M2 command and event contract (T3)

**Status:** implemented in `12d8818`; revised after review M2-T3-review-01 in `defd23f`. Scenario timeline and emission added in T4 (`59f2869`, `c78ecf3`). Authority: DR-0014 (approved; vocabulary amended 2026-10-10), DR-0017, ADR-0007.  
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

- **Event times:** the envelope's `tick` and `t` identify the step in which the event occurred, and `event_t_s` is the exact engine-event time (the same convention as `OrbitCompleted.crossing_t`).
  - **Precisely:** the envelope is the **end tick of the step that executed the transition**, so `t − dt ≤ event_t_s ≤ t`.
  - An event exactly on a tick boundary is executed at the end of the step reaching it: ignition at 600 s gives tick 60.
  - The one exception is an event at the very start of a step that no earlier step reached: a burn submitted at tick k with ignition at k·dt, including t = 0. It is executed at the start of the next step, so it is reported at tick k + 1 with `event_t_s = k·dt`.
- Converters are pure and deterministic, so identical scenarios and commands give byte-identical JSONL on the same platform (tested).

## Scenario timeline and emission (T4)
**Code:** `src/tars/sim/scenario.py` (`ScenarioV2`), `src/tars/sim/runner.py`. **Tests:** `tests/test_scenario_v2.py`, `tests/test_mission_m2.py`, `tests/test_cli.py`.

### Scenario schema version 2
- `"schema_version": 2` (the integer) selects version 2. Version-1 files load into the unchanged M1 `Scenario`, so their hash and event bytes are unchanged.
- New blocks are strict (no bool or string coercion; finite numbers only):
  - `spacecraft`: `{dry_mass_kg, propellant_kg, engine: {thrust_n, isp_s}}`, optional. It is converted to `SpacecraftSpec`, and derived quantities must be representable.
  - `commands`: a timeline of `{submit_t_s, command}` entries.
    - `command` is passed **verbatim** to `Simulator.submit()`. The scenario does not validate it, so the simulator stays the only validator and a scenario can contain a deliberately invalid command.
    - It must be a JSON object of standard JSON values (no NaN or infinity anywhere), so the canonical form, and therefore `scenario_hash`, is unambiguous.
  - `stop`: exactly one of `orbits` (M1 semantics, including the `max_duration_periods` timeout) or `duration_s`.
- **Tick grid.** `submit_t_s` and `stop.duration_s` must be exactly `n · dt_s` for an integer n, because time is `tick · dt` (ADR-0002). For example, 0.3 with dt = 0.1 is rejected, because 3 · 0.1 ≠ 0.3.
- **Timeline order.**
  - `submit_t_s` is non-decreasing; entries at the same time are submitted in file order.
  - With a duration stop, every `submit_t_s` must be earlier than the stop.

### Emission order (deterministic)
1. **Tick 0:**
   1. `SimulationStarted`;
   2. `SpacecraftConfigured` (if configured);
   3. `StateSampled`;
   4. `PropulsionSampled`;
   5. command events for the submissions due at tick 0.
2. **After each committed step, at its end tick k:**
   1. engine events of the step in exact-time order. At equal times a cutoff precedes an ignition. A depletion cutoff emits `PropellantDepleted`, then `BurnEnded`.
   2. `StateSampled`, then `PropulsionSampled`.
   3. `OrbitCompleted`.
   4. Command events for the submissions due at tick k, in file order. Submissions happen after the tick-k samples, so a tick-k sample does not yet list a burn submitted at tick k.
3. **End:** `StateSampled` and `PropulsionSampled` at the final tick if not already emitted, then `SimulationCompleted`.

### Cadence
- `StateSampled` is emitted on the telemetry grid and at the final tick, as in M1.
- `PropulsionSampled` is emitted on the telemetry grid, at the final tick, and **at every tick whose step involved the engine**: burning at the start or end of the step, or any transition during it (DR-0014 §5). At most one per tick.

### Stop and failure semantics
- **Duration stop.** The run ends at tick `duration_s / dt_s` with `status: success` unless impact, escape or a non-finite state occurs first. Orbits are still counted.
- **Stop inside a burn.**
  - No `BurnEnded` is emitted; the engine is not cut off by an observation horizon.
  - The final `PropulsionSampled` shows the active or pending burns.
  - Cutoffs and ignitions exactly at the stop time are emitted.
  - The representation is pending decision **DR-0018** (recommended: keep as is).
- **Failures.** On a non-finite step, nothing from that step is emitted, because the simulator commits nothing. Engine transitions are read only after a committed step, so no event is ever duplicated. The run ends with `failure_cause: non_finite`.
- **Unsubmitted entries.** Entries not yet submitted when the run ends are listed in `RunResult.unsubmitted_command_ids` and the CLI summary.
- **No partial results.**
  - `run_scenario` returns only after the whole run, and any unexpected exception propagates with no result.
  - The CLI writes `events.jsonl`, then `summary.json`, each atomically (temporary file plus rename).
  - Re-running a scenario builds a fresh simulator, and logs are byte-identical.

## Explicitly out of scope
- Abort/cancel and Δv-target commands (DR-0014: unapproved follow-ups).
- Crew permissions and authority checks.
- An explicit event for burns still active when a scenario stops (DR-0018, open).
