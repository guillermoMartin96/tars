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

## Addendum: reviewer re-verification (`1b2e8ed`)
**Reviewer:** Codex `gpt-6.1-sol`, session `01a1289e-3220-7180-9781-b42ae622670f`.  
**Raw:** `raw/M2-T3-codex-reverify.md`; probes alongside.  
**Verdict:** FAIL.
- REV-T3-01, 03, 04, 05, 06 and 07 RESOLVED; REV-T3-02 PARTIAL.
- The reviewer qualified the implementer's equivalence claim for `safe_text`: it is equivalent only on the tested rejection paths, not globally. That is why its direct contract test exists.

### N1 — Overridden `model_dump()` restores the validation and aliasing bypass
**Severity:** High  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `ef0c626`.
- Only an exact `BurnCommand` is accepted. It is read via `BurnCommand.model_dump(instance)`, which a subclass cannot override. Any other model is `schema_invalid`, and none of its methods is called.
- Tests: `test_overridden_model_dump_cannot_bypass_validation`, `test_only_exact_burn_commands_or_plain_mappings_are_accepted`. Trusting `model_dump` fails 2 tests.

### N2 — Payload failures could escape `submit()`
**Severity:** Medium  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `ef0c626`.
- Ordinary exceptions from payload handling and from diagnostic echo are contained into `schema_invalid`; process-control exceptions propagate.
- Echo reads only from plain dicts.
- A dict subclass is copied from its storage without calling its overridden methods, so its valid content is accepted safely.
- Tests: `test_hostile_payloads_never_escape_submit` (4 payload kinds), and `test_unforeseen_payload_failures_are_contained_but_interrupts_propagate`, which injects a failure. Mutants that remove the containment or swallow `BaseException` fail.

### N3 — M2 event strings could validate but fail serialization
**Severity:** Medium  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `ef0c626`.
- `SafeStr` (valid Unicode) applies to `issuer`, `detail`, `schema_errors` elements and `direction_laws` elements. M1 schemas are unchanged.
- Tests: `test_m2_event_strings_must_be_valid_unicode` (4 cases), `test_spacecraft_event_direction_laws_must_be_valid_unicode`. Removing `SafeStr` fails 5 tests.

### N4 — Documented precedence omitted the configuration check
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** The contract now lists `no_propulsion_configured` third, matching T2 behavior. Test `test_no_propulsion_configured_precedes_command_checks`.

**Re-test at `ef0c626`:**
- 555 tests pass; ruff clean;
- M1 Proof PASS;
- determinism `7a4e1877…`.

## Addendum 2: second reviewer re-verification (`79d9d9b`)
**Reviewer:** Codex `gpt-6.1-sol`, session `01a128a4-7f1a-7222-8571-8df963273497`.  
**Raw:** `raw/M2-T3-codex-reverify2.md`; probes alongside.  
**Verdict:** FAIL.
- N3 and N4 RESOLVED; N1 and N2 PARTIAL (see N5).
- The reviewer confirmed:
  - every rejection path is atomic;
  - all ten codes are exercised;
  - intent and outcome are correct;
  - thrust telemetry matches the RHS;
  - M1 and T2 compatibility; no new permissions.

### N5 — Instance-level serializer bypasses the exact-command boundary
**Severity:** High  
**Reviewer claim:**
- `BurnCommand.model_dump(instance)` still uses the instance's own `__pydantic_serializer__`. A forged exact instance whose serializer returns itself was accepted, unvalidated and aliased.
- A forged command ID with a hostile `__hash__` raised outside the containment.

**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `ffa4c3c`.
- No Pydantic serialization of untrusted instances at all. Stored fields are read from the instance `__dict__`, and extra attributes are rejected as tampering.
- Keys must be exact `str` and values exact `str`/`int`/`float`. Echoed IDs and issuers must be exact `str`.
- Tests:
  - `test_instance_serializer_hooks_cannot_bypass_validation` (self-returning and throwing serializers);
  - `test_receipt_intent_cannot_be_changed_through_the_submitted_instance`;
  - `test_non_builtin_values_and_keys_are_rejected_without_escaping` (hash-bomb `str` subclass in instance and mapping, hostile key, `float` subclass);
  - `test_non_string_keys_are_rejected_explicitly`.
- The reviewer's `followup` probe no longer reaches acceptance: the forged command is rejected.
- Mutation:
  - removing the builtin-type check, the key check, the tamper check or the exact-`str` echo fails tests;
  - reverting to `BurnCommand.model_dump` is equivalent once the tamper check exists, because the class is exact and per-instance hooks are rejected first.

### N6 — Valid non-dict mappings contradicted the contract
**Severity:** Medium  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `ffa4c3c`. Any `Mapping` is copied into a plain dict. Test `test_any_mapping_type_is_accepted` (`UserDict`, `MappingProxyType`); a dict-only mutant fails it.

**Re-test at `ffa4c3c`:**
- 564 tests pass; ruff clean;
- M1 Proof PASS; GMAT compare PASS;
- determinism and cross-platform bit-identical to `7a4e1877…`.

## Proof gate
- [x] Every finding dispositioned (REV-T3-01…07, N1–N6)
- [x] High findings resolved (REV-T3-01, REV-T3-02, N1, N5)
- [x] Fixes re-tested by the implementer
- [ ] Reviewer re-verification of N5–N6 (requested)

**Review gate result:** BLOCKED, pending re-verification.
