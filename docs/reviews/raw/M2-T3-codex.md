### F1 — Rejection changes the seen-ID registry
**Severity:** High  
**Claim:** Schema-valid rejected commands mutate simulator state, violating DR-0014 and the explicit rejection-atomicity requirement.

**Evidence:** `src/tars/sim/simulator.py:392` adds the ID before scheduling validation. In `review_scratch/probe.py`, submitting duration `0.0` changes `_seen_command_ids` from `set()` to `{'burn-001'}`; correcting and resubmitting returns `duplicate_command_id`. The burn counter remains zero. `tests/test_commands.py:201` checks physical snapshots but omits the registry; line 210 explicitly enshrines this conflicting behavior. The new contract simultaneously says “changes nothing” and reserves rejected IDs.

**Suggested fix:** Commit the seen ID only after acceptance. If rejected IDs must be consumed, obtain an explicit amendment to the approved atomicity requirement and reconcile the documentation and tests.

### F2 — Prebuilt commands bypass validation and introduce mutable receipt contents
**Severity:** High  
**Claim:** `submit()` trusts any `BurnCommand` instance, allowing malformed commands, exceptions, and mutable objects inside frozen receipts.

**Evidence:** `src/tars/sim/commands.py:88` returns instances without validation. Probes using the supported `model_copy(update=...)` API demonstrate:

- `schema_version=2` is accepted and schedules a burn.
- `command_id=[]` raises `TypeError`, contradicting “never raises for a bad command.”
- `issuer=[]` is accepted; appending through `receipt.issuer` changes both receipt provenance and `receipt.command.issuer`.

A normally validated subclass with a mutable `annotations` field is also accepted and retained by reference. An in-memory mutation of the original command changes a subsequently generated `CommandAccepted` duration while its receipt plan retains the original duration. See `review_scratch/probe.py` and `probe_more.py`.

**Suggested fix:** Validate every submission against the exact command schema, including model instances, and retain an independent canonical command snapshot. Reject subclass extras and invalid copied values before any registry or schedule mutation.

### F3 — Event payloads omit approved command intent and thrust telemetry
**Severity:** Medium  
**Claim:** The event schema does not fully implement the approved DR-0014 §5 payload contract.

**Evidence:** `CommandRejected` at `src/tars/events/schema.py:137` contains only ID, issuer, reason, and detail. Its converter at `src/tars/sim/burn_events.py:41` discards `receipt.command`, even for schema-valid rejected commands. Thus, rejecting a requested duration loses that duration from the event record.

`PropulsionSampled` at `src/tars/events/schema.py:198` and its converter at `src/tars/sim/burn_events.py:173` omit the approved thrust acceleration vector. The probe confirms its absence from serialized keys. These are schema omissions; T4 emission timing does not resolve them.

**Suggested fix:** Include validated rejected-command intent, with a bounded structured representation for malformed input, and add truth-state thrust acceleration telemetry. Update converter inputs as needed and test the approved payload fields explicitly.

### F4 — Malformed Unicode is echoed into an unserializable rejection event
**Severity:** Medium  
**Claim:** Schema-invalid input can produce a rejection receipt whose event cannot be written as JSONL.

**Evidence:** `readable_field()` at `src/tars/sim/commands.py:102` validates issuer length only. In `review_scratch/probe_unicode.py`, a mapping with `issuer='\ud800'` correctly receives `schema_invalid`, but the receipt echoes that surrogate. `command_event(receipt).model_dump_json()` then raises `PydanticSerializationError` with a Unicode encoding error.

Ordinary Unicode and escaped control characters round-trip successfully; the defect concerns invalid Unicode.

**Suggested fix:** Validate echoed issuer strings for Unicode validity, returning `None` when invalid. Test serialization of rejection events from malformed Python mappings.

### F5 — Public scheduling bypasses command-ID uniqueness
**Severity:** Medium  
**Claim:** The new `schedule_burn(command_id=...)` argument permits ambiguous command correlation outside the duplicate-ID checks.

**Evidence:** `src/tars/sim/simulator.py:263` exposes the correlation argument, but only `submit()` checks `_seen_command_ids`. The probe schedules a burn with `command_id='same'`, then submits another command with that ID. Both are accepted:

```text
[('burn#000001', 'same'), ('burn#000002', 'same')]
```

This also contradicts `docs/contracts/m2-commands-and-events.md:50`, which states that engine-level scheduled burns have null command IDs.

**Suggested fix:** Keep correlation assignment internal to submission, preserving the T2 public scheduling interface, or enforce one documented validation and uniqueness policy across both entry points.

### F6 — “Strict” schemas accept invalid version types and correlation strings
**Severity:** Low  
**Claim:** Runtime validation is weaker than the advertised machine-readable schema.

**Evidence:** `schema_version: Literal[1]` at `src/tars/sim/commands.py:38` accepts both Python `True` and `1.0`, normalizing them to `1`. JSON event parsing likewise accepts `schema_version: true` and `1.0`; the inherited field is at `src/tars/events/schema.py:18`.

Event correlation fields are unconstrained strings. The probe parses a `BurnEnded` with `command_id='bad\n#'` or `burn_id=''`, although those values violate the documented ID contract.

**Suggested fix:** Require an actual integer version in M2 schemas and reuse constrained correlation-ID types across commands and events. Preserve M1 behavior separately.

### F7 — Non-finite rejection tests can pass for unrelated validation failures
**Severity:** Low  
**Claim:** Some schema tests would pass plausible incorrect implementations.

**Evidence:** `tests/test_commands.py:361` tests non-finiteness by inserting both infinite `t` and an extra `x` field. The probe replaces the infinite value with a finite value and still obtains `extra_forbidden`; therefore the test does not establish finite-number enforcement.

At line 358, JSON-decoded lists are passed into strict Python models requiring tuples. For vector-bearing events, that can also mask whether extra fields are rejected. Receipt tests check only outer freezing and miss F2.

**Suggested fix:** Change one property per negative test. Use `model_dump()` for Python validation, JSON validation for JSON inputs, and assert the failing field/error type. Add nested-mutation and model-instance boundary cases.

## Summary

**Verdict: FAIL.** Rejection atomicity and command-boundary validation require correction before T3 approval.

Verified:

- **Tests:** requested pytest command — **512 passed**.
- **Lint/format:** requested Ruff checks — **passed**, 122 files formatted.
- **M1 determinism:** both processes produced `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- **M1 proof:** all gates passed; report at `review_scratch/m1.json`.
- **Vocabulary:** exactly the ten approved rejection codes; all are exercised.
- **Compatibility:** existing T2 interfaces remain callable; the full regression suite and M1 golden checks pass.
- **Intent versus outcome:** mutation probes show executed duration, consumed propellant, sensed Δv, and rocket-equation Δv respond to transition outcomes while planned consumption remains unchanged.
- **Events:** all seven M2 types plus an M1 event round-trip through the discriminated JSONL parser. Unknown types, unsupported versions, infinite times, and boolean ticks are rejected.
- **Replay:** the probe’s mixed event stream has identical hashes across separate processes.
- **Architecture/scope:** no new AI permissions, provider dependencies, or runner emission wiring found.

Documentation accurately describes much of the implementation, but its atomicity, correlation, and strictness claims conflict with the findings above. All review artifacts are under `review_scratch/`; implementation and tests were left untouched.