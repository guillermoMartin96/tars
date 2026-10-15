### F1 — Final propulsion telemetry can omit an accepted pending burn
**Severity:** High  
**Claim:** If a step fails immediately after a submission, the final `PropulsionSampled` can describe the state before that submission, contradicting `final_propulsion`, the CLI summary, and DR-0018.

**Evidence:** `runner.py:220` suppresses any second propulsion sample at the same tick. Samples precede submissions (`runner.py:234–236`), and a non-finite step leaves the tick unchanged (`runner.py:254–256`). Final sampling therefore skips the updated schedule (`runner.py:291`).

The injected first-step failure in `review_scratch/probes.py` produced:

- Completion: tick 0, `non_finite`.
- Final JSONL propulsion sample: `idle`, no pending burns.
- `final_propulsion`: `scheduled`, pending `burn#000001`.

The same issue applies after a submission at a later sampled tick. The existing non-finite test (`tests/test_mission_m2.py:491`) fails during an established burn and misses this case. The final-sample claim in `docs/contracts/m2-commands-and-events.md:120` and DR-0018 §“Current implementation” is consequently inaccurate.

**Suggested fix:** Define a contract-consistent way to emit authoritative final schedule state after submissions without accidental duplicate telemetry. Add first-step and later-submission failure tests comparing final JSONL telemetry with `final_propulsion`.

### F2 — Python payload validation permits hash ambiguity and changes command semantics
**Severity:** Medium  
**Claim:** Python-created timeline entries can contain non-JSON values, and the runner’s JSON copy can turn a command rejected by `submit()` into an accepted command.

**Evidence:** `_require_finite_json` (`scenario.py:142–152`) checks floats and recurses through dictionaries/lists, but does not reject other types. `command: dict[str, Any]` accepts their values. The runner then serializes and deserializes payloads (`runner.py:170`).

Probes demonstrated:

- A tuple containing NaN passes `ScenarioV2.model_validate`.
- Bytes and sets pass scenario validation, then cause runner `TypeError`.
- `{"x": b"abc"}` and `{"x": "abc"}` have identical scenario hashes despite different runtime behavior.
- A valid burn with an `int` subclass as its duration is rejected by direct `Simulator.submit()`, but accepted through `run_scenario()` because the JSON copy converts it to a plain integer.

See `review_scratch/probes.txt` and `review_scratch/more_probes.txt`. These contradict the documented standard-JSON and verbatim-passthrough guarantees and DR-0014’s confirmed strict-input semantics. Existing payload tests primarily exercise JSON input.

**Suggested fix:** Recursively require exact standard JSON types and string keys for Python input, while retaining deliberately invalid commands composed of valid JSON values. Copy payloads without changing their accepted types. Test Python input, hash collisions, and direct-versus-runner rejection equivalence.

### F3 — CLI failure can leave outputs from different runs
**Severity:** Medium  
**Claim:** Individual file replacement is atomic, but publication of the mission output pair is not.

**Evidence:** `run_mission.py:88` replaces `events.jsonl` before summary construction and replacement at line 111. Injecting failure only on the summary rename left new events alongside the previous summary (`review_scratch/probes.txt`: `events_changed True`, `summary old summary`).

Thus the surviving summary can contain the wrong scenario, final state, and event hash. `tests/test_cli.py:143` covers runner failure before writes; line 166 covers a single failed replacement. Neither tests failure after the first successful replacement.

**Suggested fix:** Prepare both artifacts before publication and use a generation directory with an atomic manifest/pointer switch, or another explicit transactional publication scheme. Test second-publication failure against an existing complete output pair. Document the pair-level guarantee.

### F4 — Duration scenarios cannot round-trip their own serialized configuration
**Severity:** Medium  
**Claim:** A valid duration scenario’s canonical JSON fails validation, and its inherited `with_dt()` helper fails even for a compatible timestep.

**Evidence:** `StopConditionV2` always serializes default `max_duration_periods=1.1` (`scenario.py:178`), but rejects that field whenever explicitly present with `duration_s` (`scenario.py:185–186`). Both `canonical_json()` and `with_dt()` dump it (`scenario.py:83`, `90–91`).

Probes showed:

- `parse_scenario(slice_scenario.canonical_json())` raises `ValidationError`.
- A 30-second scenario’s `with_dt(5.0)` raises the same error.

Both configurations otherwise satisfy the tick grid. Current tests check hash stability but not serialization round-tripping or the v2 helper.

**Suggested fix:** Make duration-stop serialization compatible with its validator, preserving M1 serialization. Add canonical JSON and Python dump round-trip tests, plus compatible/incompatible `with_dt()` cases.

### F5 — Finite timing inputs can escape validation as an uncaught overflow
**Severity:** Low  
**Claim:** Tick-grid validation can crash the CLI instead of reporting invalid input.

**Evidence:** `_tick_count` calls `round(value / dt_s)` without checking quotient representability (`scenario.py:106`). With finite `duration_s=1e308`, `dt_s=1e-10`, and matching telemetry interval, the quotient becomes infinity.

Running the CLI against `review_scratch/overflow.json` exited 1 with an `OverflowError` traceback. Its documented invalid-input exit is 2; its handler catches only `OSError` and `ValidationError` (`run_mission.py:78–82`).

**Suggested fix:** Detect unrepresentable tick arithmetic and raise a validation error. Cover both duration and submission ratios, including the CLI exit behavior.

## Summary

**Verdict: FAIL.** The normal mission path is well covered and passes, but final failure telemetry, strict Python payload handling, and output publication need correction.

All requested checks completed:

- Pytest: **660 passed**.
- Ruff check and format check: **passed**.
- Determinism: **passed**, exact M1 reference hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- M1 Proof: **all approved gates passed**; artifact: `review_scratch/m1.json`.
- M2 slice: **success**, tick 5370, time 53,700 s, nine completed orbits; artifacts: `review_scratch/slice/`.

Verified through tests, code inspection, and independent probes:

- Deterministic ordering, repeated-run JSONL equality, command/burn correlation, rejection precedence, corrected-ID retries, and commanded-versus-executed values.
- End-tick envelopes, ignition at the submission tick, multiple transitions within one tick, cutoff-before-ignition ties, depletion ordering, and propulsion cadence.
- Exact duration boundaries, ignition/cutoff at the stop, active and pending burns, orbit stopping, and unsubmitted commands after impact/escape.
- Non-finite integration rollback and unexpected-exception propagation without a returned result.
- V1’s unchanged M1 path and golden output.
- No new public event types, rejection codes, permission semantics, thermal behavior, or autonomous planning.
- DR-0017 remains explicitly a timing-induced Δv bound, not a trajectory-error guarantee.

DR-0018’s observation-horizon behavior stays within the approved event vocabulary: an unfinished burn does not receive a fabricated `BurnEnded`. Its final-telemetry guarantee fails in F1. The passing suite misses all five demonstrated cases.

Source and tests were left unchanged; review artifacts are under `review_scratch/`.