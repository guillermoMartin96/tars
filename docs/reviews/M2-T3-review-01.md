# External Review: M2 Task T3 — command and event schema

**Reviewer/model:** OpenAI Codex CLI, model `gpt-6.1-sol` (separate provider), session `01a12895-612e-7342-9b3d-f9d654b050e1`.  
**Date:** 2026-10-10  
**Reviewed revision:** `d413edd` (diff `72b3f0d..d413edd`).  
**Scope:** T3 requirements:
- versioned schemas;
- exact approved rejection codes;
- stable correlation IDs;
- intent separate from outcome;
- immutable, deterministic events;
- T2 and M1 compatibility;
- no new AI permissions.

The review also covered DR-0014, DR-0017, ADR-0007 and the contract document.  
**Raw:** `raw/M2-T3-codex.md`; prompt and probes alongside.

## Summary
**Verdict: FAIL.**

Confirmed by the reviewer:
- 512 tests pass;
- exactly the ten approved codes, all exercised;
- T2 interfaces callable; M1 golden hash and Proof intact;
- outcome fields respond to execution, not to the plan;
- all event types round-trip with M1 events;
- a deterministic stream across processes;
- no new AI permissions or provider dependencies.

The defects concern rejection atomicity, the command-instance trust boundary, missing approved payload fields, Unicode safety, a correlation bypass, schema strictness, and test precision.

## Findings
All seven are **`ACCEPTED`**. Resolutions are pending the fix commit.

### REV-T3-01 — Rejection changes the seen-ID registry (F1)
**Severity:** High  
**Implementer reasoning:** Correct.
- The "single use once seen" design contradicted the requirement that a rejected command changes nothing, and a test enshrined it.
- A command ID is now consumed only on acceptance: `duplicate_command_id` means an accepted command already used the ID. A rejected command can be corrected and resubmitted under the same ID.

### REV-T3-02 — Prebuilt commands bypass validation; mutable receipt contents (F2)
**Severity:** High  
**Implementer reasoning:** Correct. `model_copy(update=…)` and subclasses bypass validation. Every submission, including `BurnCommand` instances, will be re-validated against the exact schema into a fresh canonical command owned by the receipt. Any failure becomes `schema_invalid` without raising.

### REV-T3-03 — Event payloads omit approved command intent and thrust telemetry (F3)
**Severity:** Medium  
**Implementer reasoning:** Correct against DR-0014 §5.
- `CommandRejected` will carry the commanded intent when the command is schema-valid, plus a bounded structured list of schema errors.
- `PropulsionSampled` will carry the truth-state thrust-acceleration vector.

### REV-T3-04 — Invalid Unicode echoed into an unserializable rejection event (F4)
**Severity:** Medium  
**Implementer reasoning:** Correct. Every echoed string will be made safe for serialization, and invalid Unicode in a command's `issuer` becomes a schema error.

### REV-T3-05 — Public scheduling bypasses command-ID uniqueness (F5)
**Severity:** Medium  
**Implementer reasoning:**
- Correct, and it also contradicted the contract.
- `schedule_burn` returns to its exact T2 signature. Correlation by command ID is internal to `submit()`, and engine-level burns have `command_id = null`.

### REV-T3-06 — Strict schemas accept bool/float versions; unconstrained correlation IDs (F6)
**Severity:** Low  
**Implementer reasoning:**
- Correct: `Literal[1]` matches `True` and `1.0` by equality.
- M2 schemas (the command and M2 events) will require an actual integer version and constrained ID types. The M1 event base is unchanged.

### REV-T3-07 — Some negative tests can pass for unrelated failures (F7)
**Severity:** Low  
**Implementer reasoning:** Correct; this is the same lesson as REV-T1-05. Each negative test will change one property, use the input mode it claims (Python vs JSON), and assert the failing field.

## Resolutions (fixed in `defd23f`)
| Finding | Resolution | Tests (mutation check) |
|---|---|---|
| REV-T3-01 (High) | IDs registered only after acceptance; a rejection leaves registry, counter, schedule and state unchanged | `test_rejected_commands_do_not_consume_their_id`, `test_rejected_submissions_change_nothing`, `test_rejected_submissions_do_not_consume_burn_ids` (registering before scheduling fails 34 tests) |
| REV-T3-02 (High) | `parse_command` dumps any model instance and re-validates against the exact schema into a fresh `BurnCommand`; other payload errors become `schema_invalid` | `test_prebuilt_commands_are_revalidated` (4 forged `model_copy` cases), `test_subclassed_commands_with_extra_mutable_fields_are_rejected`, `test_receipt_owns_a_canonical_copy_of_the_command` (trusting instances fails 5) |
| REV-T3-03 (Medium) | `CommandRejected` gains intent fields and `schema_errors`; `PropulsionSampled` gains `thrust_acceleration_mps2` | `test_rejected_event_keeps_commanded_intent_or_structured_schema_errors`, `test_propulsion_sample_carries_the_truth_thrust_acceleration` (dropping either fails) |
| REV-T3-04 (Medium) | Echoed fields must be a valid ID or valid Unicode; `safe_text` sanitizes record strings; issuer validator | `test_rejection_events_from_malformed_unicode_serialize` (4 payloads), `test_command_with_invalid_unicode_issuer_is_schema_invalid`, `test_safe_text_escapes_invalid_unicode_and_bounds_length` |
| REV-T3-05 (Medium) | `schedule_burn` signature restored exactly; correlation internal to `submit` | `test_schedule_burn_keeps_its_t2_signature_and_null_command_ids` |
| REV-T3-06 (Low) | `StrictVersion1` (integer only) for the command and M2 events; `CommandId`/`BurnId` constrained types; M1 event base unchanged | `test_command_schema_version_must_be_the_integer_one`, `test_m2_event_schema_version_must_be_the_integer_one`, `test_m2_event_correlation_ids_are_constrained` (each relaxation fails) |
| REV-T3-07 (Low) | Separate extra-field (Python input, tuples kept) and non-finite (JSON input) tests, each asserting the exact error | `test_new_events_reject_extra_fields`, `test_new_events_reject_non_finite_numbers_from_json` |

**Equivalent mutants (documented):** current pydantic already rejects invalid Unicode in length-constrained strings and in mapping keys (`string_unicode`, never echoing the key). The explicit issuer validator and the `safe_text` sanitizer are defence in depth. `safe_text` is pinned by a direct contract test.

**Re-test at `defd23f`:**
- 542 tests pass; ruff clean;
- M1 Proof PASS; GMAT compare PASS;
- determinism and cross-platform bit-identical to `7a4e1877…`.

## Proof gate
- [x] Every finding dispositioned
- [x] High findings resolved (`defd23f`)
- [x] Fixes re-tested by the implementer
- [ ] Reviewer re-verification (requested)

**Review gate result:** BLOCKED.
