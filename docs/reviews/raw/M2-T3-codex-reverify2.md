| Item | Status | Evidence |
|---|---|---|
| N1: overridden dump / canonical copy | PARTIAL | Original subclass exploit rejects. Forged exact instances still bypass validation and retain aliases; see N5. |
| N2: exception containment | PARTIAL | Original exceptions are contained. Forged exact command IDs can raise `RuntimeError` outside containment; see N5. `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` propagate without mutation. |
| N3: invalid Unicode | RESOLVED | Lone surrogates reject in accepted/rejected issuer, detail, schema-error elements, and direction-law elements. `review_scratch/adversarial.out`. |
| N4: rejection precedence | RESOLVED | Combined invalid duration/past ignition without propulsion returns `no_propulsion_configured`, matching the revised contract. |
| Payload boundary | FAIL | Subclasses, hostile objects, huge integers, million-character strings, deep nesting, and hostile values reject safely; forged serializer bypass survives. Non-dict mappings reject. |
| Rejection atomicity | PASS | All ten approved rejection codes preserve physical state, schedule, counter, committed propellant, ID registry, and transitions. Additional adversarial rejections also preserve state. `review_scratch/deep.out`, `adversarial.out`. |
| Versioned machine-readable schemas | PASS | Command and seven M2 event schemas are versioned; regression tests cover strict versions, serialization, and parsing. |
| Exact approved rejection codes | PASS | Exactly ten approved codes; each independently exercised. |
| Stable correlation IDs | PARTIAL | Normal paths preserve deterministic numbering and shared T2 sequence. N5 bypasses command-ID validation. |
| Intent versus outcome | PASS | Modified cutoff transitions change execution duration, consumption, and sensed Δv while planned consumption remains fixed. Thrust telemetry matches simulator RHS in both directions. |
| Immutable deterministic records | PARTIAL | Normal records pass freezing and deterministic-stream checks; N5 retains caller-owned mutable command contents and produces an unwritable event. |
| T2/M1 compatibility | PASS | 555 tests and M1 proof pass. Golden hash remains `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. |
| No new AI permissions | PASS | Supplied fix diff adds no permissions, provider dependencies, or crew authority. |
| Contract accuracy | PARTIAL | Unicode and precedence claims now hold; canonical-copy, exception-containment, and mapping claims remain false. |
| Snapshot identity | UNVERIFIED | Git metadata is absent; supplied commit `79d9d9b` cannot be independently confirmed. |

### N5 — Instance-level serializer bypasses the exact-command boundary

**Severity:** High

**Claim:** Calling `BurnCommand.model_dump(instance)` still uses the caller-controlled instance’s `__pydantic_serializer__`. If that serializer returns the instance, `model_validate()` trusts it without revalidation.

**Evidence:** `review_scratch/followup.py.txt` and `followup.out` demonstrate:

- An exact command forged with `schema_version=2` and `issuer=[]` is **accepted**, schedules one burn, and satisfies `receipt.command is payload`.
- Changing the original command’s duration changes receipt intent to `1.0`, while its plan retains `77.3`.
- Event conversion raises `ValidationError` after scheduling.
- A forged command ID whose `__hash__` raises causes `RuntimeError` to escape `submit()`.

Boundary: `src/tars/sim/commands.py:135–143`; ID lookup occurs outside the parsing guard.

**Suggested fix:** Extract stored command fields without instance serialization hooks, require a plain dict, and validate into a fresh exact command. Add regression probes for forged serializers returning themselves and hostile command IDs.

### N6 — Valid non-dict mappings contradict the published input contract

**Severity:** Medium

**Claim:** The contract accepts mappings and promises copying into a plain dict, but implementation copies only dict instances.

**Evidence:** Valid `UserDict(_cmd())` and `MappingProxyType(_cmd())` both return `schema_invalid`; direct parsing reports `model_type`. See `review_scratch/followup.out`. Other mappings reach strict `BurnCommand.model_validate()` unchanged.

**Suggested fix:** Handle `collections.abc.Mapping` explicitly and copy within exception containment, or narrow the documented API to supported dict inputs.

**T3 verdict: FAIL** — Ran the requested pytest (**555 passed**), Ruff lint/format (**passed**), determinism (**passed**), M1 proof (**PASS**), prior probes, and expanded adversarial probes. Artifacts are under `review_scratch/`; `src/` and `tests/` were unchanged.