Evidence files below are under `review_scratch/`.

| Item | Status | Evidence |
|---|---|---|
| REV-T3-01 | RESOLVED | `deep.out`: all ten rejection codes preserve state, schedule, counter, committed propellant, ID registry and transitions; rejected IDs remain reusable. |
| REV-T3-02 | RESOLVED | `boundary.out`, `probe.out`: forged instances revalidate; subclasses reject; receipt commands are fresh canonical copies unaffected by caller mutation. |
| REV-T3-03 | RESOLVED | `probe.out`, `deep.out`: rejected intent retained; thrust telemetry matches simulator RHS in both directions. |
| REV-T3-04 | RESOLVED | `probe_unicode.out`, `adversarial.out`: malformed Unicode rejects; resulting rejection events serialize. |
| REV-T3-05 | RESOLVED | Regression suite and `probe.out`: exact T2 scheduling signature; engine-level command IDs null; shared burn sequence. |
| REV-T3-06 | RESOLVED | `event_checks.out`, `probe.out`: boolean/float versions and malformed correlation IDs reject. |
| REV-T3-07 | RESOLVED | Reviewed tests use valid controls, change one property and assert the precise validation error; tests pass. |
| N1 | RESOLVED | `edge.out`: overridden dumping cannot restore validation or aliasing bypass. |
| N2 | RESOLVED | `boundary.out`: every built-in ordinary exception class exercised through mapping hooks is contained; exercised process-control exceptions propagate atomically. |
| N3 | RESOLVED | `adversarial.out`: invalid Unicode rejects in issuer, detail, schema-error elements and direction-law elements. |
| N4 | RESOLVED | `adversarial.out`: configuration check precedes duration/time checks, matching revised contract. |
| N5 | RESOLVED | `followup.out`: self-returning serializer and hostile command-ID hash reject before scheduling; no retained alias. |
| N6 | RESOLVED | `followup.out`: `UserDict` and `MappingProxyType` validate successfully into fresh commands. |
| Expanded boundary attack | PASS | `boundary.out`, `event_checks.out`: 242 cases cover field/dictionary tampering, Pydantic internals, class reassignment, hostile mappings, subclass keys/values, bool, huge integers and NaN. |
| Rejection atomicity and serialization | PASS | Every approved rejection code preserves the full simulator fingerprint and produces a serializable event; expanded rejections also checked. |
| Versioned machine-readable schemas | PASS | `schemas.json`: command plus all seven M2 schemas; strict version checks and JSONL round-trips pass. |
| Exact approved rejection codes | PASS | `deep.out`: exactly ten approved codes, independently exercised. |
| Stable correlation IDs | PASS | Regression suite and adapted probes confirm accepted-only registration, deterministic numbering and shared T2 sequence. |
| Intent versus outcome | PASS | `probe.out`: modified cutoff outcomes change executed duration, consumption and sensed Δv while planned consumption stays fixed. |
| Immutable deterministic records | PASS | All seven M2 events reject ordinary mutation; canonical copies survive caller tampering; separate-process mixed-event outputs match exactly. |
| T2/M1 compatibility | PASS | 564 tests; M1 proof PASS; golden hash remains `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. |
| No new AI permissions | PASS | Fix diff introduces no permissions, provider dependencies or crew authority. |
| Contract accuracy | PASS | Revised copying, builtin-type restrictions, exception containment, precedence and correlation claims match observed behavior. “Never raises” has the explicitly documented process-control exception qualification. |
| Prior mutant qualification | CONFIRMED | `mutants.out`: issuer validator remains redundant under current Pydantic; removing `safe_text` sanitization still fails its direct Unicode contract. |
| Snapshot identity | UNVERIFIED | Git metadata is absent; supplied commit `7f8597e` cannot be independently confirmed. |

**NEW findings:** None.

**T3 verdict: PASS** — Ran the requested pytest (**564 passed**), Ruff lint/format (**passed**), determinism (**passed**), M1 proof (**PASS**, `review_scratch/m1.json`), adapted prior probes, isolated in-memory mutant probes and expanded boundary/event checks. All new files are under `review_scratch/`; `src/` and `tests/` were unchanged.