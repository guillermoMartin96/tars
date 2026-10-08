# External Review Follow-up: Milestone 1 independent audit

**Reviewer/model:** OpenAI Codex; independent read-only audit, followed by remediation
authorized by the Tech Lead. The same agent implemented these fixes; this follow-up
does not claim a separate independent reviewer verified the remediation.

**Date:** 2026-10-08

**Reviewed revision:** `6cf072ad32c26f8be6ac177ed4fcd39c3eba1946`, M1 merge commit.
The audit ran in an isolated worktree initially on `incandescent-flute-e5ed26d8`.
Remediation uses the existing `review/m1-independent-audit` branch in that worktree.

**Scope:** Milestone 1 science, numerical methods, GMAT methodology, reproducibility,
architecture, error handling, tests, approved decisions, Proof, and prior review history.

## Summary

Original assessment: **CONDITIONAL PASS**. No Critical or High findings were raised.
The approved two-body scenario reproduced all recorded metrics: 118 tests passed,
all seven non-GMAT checks and nine GMAT gates passed, and an independent closed-form
circular reference agreed with the reported error at every tick. The committed GMAT
report contained 896 finite rows with matching hashes. The original audit did not
execute fresh GMAT runs or independently fetch the historical Linux/arm64 CI runs.

Two Medium findings were confirmed validation defects. Two Low findings concerned
the documented scope and semantics. No force, integrator, scenario, acceptance
threshold, architecture boundary, or permission change was needed. Optional changes
to generic orbit counting and scenario constant overrides remain outside M1 remediation.

The final executable revision is `e5f5e536a37240d379c6370130f4c03d40ff48f7`.
Remediation validation: **212 tests pass**, approved M1 Proof passes, the original
event-log hash is unchanged on the reference host, and new Linux/arm64 CI runs pass.
See the [follow-up Proof record](../../proof/records/M1-independent-audit.md).

## Findings

### F1 — Interior NaNs can be omitted from GMAT error maxima

**Severity:** Medium

**Reviewer claim:** `parse_report` accepts non-finite numbers; Python `max()` can
ignore an interior NaN, so invalid reference states can produce passing finite metrics.

**Evidence/reproduction at the reviewed revision:** Load the committed report into
memory, use `dataclasses.replace` to set row 100's position and velocity to
`np.full(3, np.nan)`, call `gmat.compare`, and evaluate the seven report-derived gates.
They pass despite the invalid row. No committed reference data was modified.

**Affected code/Proof:** `src/tars/validation/gmat.py`, `tests/test_gmat.py`; integrity
of GMAT reference validation under DR-0009 and Physics Proof.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Confirmed fail-open validation defect. Existing finite
evidence remains valid, but every reference row must be valid before aggregation.
This is input integrity, not a new numerical tolerance.

**Resolution/evidence:** Commit `e1e039382e8f73b094963b0e7df17314d246381e` rejects empty
reports, incorrect column counts, and non-finite fields, including the epoch column.
`compare` also rejects invalid scalar fields and vector shape/values for in-memory
rows. Added 59 cases; before the fix, 57 failed and two shape cases already passed
through NumPy's incidental errors. Afterwards, the GMAT/CLI suite passed all 79 cases.
The full suite and all nine committed GMAT gates pass at the final executable revision.

### F2 — Scenario and event schemas accept non-finite numerical values

**Severity:** Medium

**Reviewer claim:** Infinite altitude passes scenario validation and fails during
execution. Non-finite telemetry is accepted, serializes as `null`, and then fails
the event parser, breaking the expected JSONL round trip.

**Evidence/reproduction at the reviewed revision:** Set
`initial_orbit.altitude_m = float("inf")` in a copy of the scenario, validate, and run;
execution emits warnings and raises `ValueError`. Construct `StateSampled` with
`r=[float("nan"), 0, 0]`, serialize it, and parse it; parsing raises `ValidationError`.

**Affected code/Proof:** `src/tars/sim/scenario.py`, `src/tars/events/schema.py`,
`tests/test_scenario.py`, `tests/test_events.py`, `tests/test_cli.py`; machine-readable
inputs/events and invalid-input handling.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Confirmed schema-boundary defect; invalid numbers should
be rejected before physics or serialization. Valid schema-version-1 payloads retain
their fields and representation. The change concerns typed numerical fields;
arbitrary metadata in `earth_constants: dict[str, Any]` is not recursively constrained.

**Resolution/evidence:** Commit `f264d0c0281a161bfc0e2d84aaaa6917501edb49` adds
`allow_inf_nan=False` to both base models. Added 32 regression cases cover Python/JSON
scenario input, telemetry scalars/vectors, validation metrics/thresholds, and the CLI.
Before the fix, 23 cases failed and nine invalid inputs were already rejected through
other constraints. Afterwards, all 70 focused schema/CLI/validator tests passed.
The CLI now returns invalid-input exit code 2 without a traceback or mission artifacts
for infinite altitude and timeout multipliers. No finite numerical result changes.

### F3 — Orbit count represents node passages for arbitrary initial phase

**Severity:** Low

**Reviewer claim:** The generic scenario permits nonzero initial argument of latitude;
ten `OrbitCompleted` events can represent less than ten full revolutions.

**Evidence/reproduction at the reviewed revision:** Change only the start phase to
90°, 180°, or 270° and run. Success occurs at 52 370, 51 020, or 49 680 s, respectively,
each before ten full periods. The approved ascending-node M1 scenario is unaffected.

**Affected code/Proof:** `StopCondition`, `OrbitCompleted`, `tests/test_mission_m1.py`,
README; interpretation of mission output, not the approved DR-0007 experiment.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Confirmed documentation/semantic gap, not a defect in the
approved ascending-node experiment. Changing the stop condition or rejecting phases
would change existing behavior without a demonstrated M1 need.

**Resolution/evidence:** Commit `e5f5e536a37240d379c6370130f4c03d40ff48f7` documents
the existing node-passage semantics in the schema, event docstring, README, and
clarification record. Three regression cases verify nonzero-phase success, the passage
count, and duration between nine and ten periods. These broad behavioral bounds are
not new scientific acceptance tolerances. Runtime counting remains unchanged.

**Remaining limitation:** Full-revolution semantics for arbitrary starting phase
are an optional future change requiring a proposal/approval before implementation.

### F4 — Entry-point documentation and historical ADR wording are stale

**Severity:** Low

**Reviewer claim:** README calls the project scaffolding-only; ADR-0003 claims
scenario constant overrides; ADR-0004 still calls timestep/tolerances pending.

**Evidence/reproduction:** Compare README and ADR-0003/0004 with the implemented
scenario schema and later DR-0008/0009 approvals. ADR-0004's conceptual protocol
argument order and ADR-0006's "CSV" description also differ from implementation.

**Affected code/Proof:** README and documentation traceability. No physics defect.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Current usage guidance must match actual behavior while
approved decisions retain their historical content and authority.

**Resolution/evidence:** Commit `e5f5e536a37240d379c6370130f4c03d40ff48f7` replaces the
stale README with M1 usage, validation procedures, and limitations. A separate
`docs/decisions/M1-implementation-clarifications.md` explains the narrower WGS84-only
schema, final approvals, protocol signature, report format, and final-state coverage.
Original ADRs and Decision Requests are unchanged. Documentation was checked against
implementation and the passing CLI/Proof results.

## Prior review history and governance

REV-001–015 retain their original dispositions in `M1-orbit-review-01.md`. Regression
coverage for mismatched constants, truncated references, force mutation, architecture
scan bypasses, oracle convergence, final sampling, and threshold-group typos passes.
The Tech Lead's REV-012 epoch-drift deferral remains in effect before the first gated
time-dependent force model. No new scientific investigation is needed for these
input-validation fixes. No Decision Request is open or necessary for this scope.

No existing tests or Proof gates were weakened or removed. Original thresholds,
scientific assumptions, approvals, scenario, GMAT/golden references, and historical
Proof evidence are unchanged. M1 remains an idealized two-body prototype.

## Proof gate

- [x] All Critical findings resolved (none raised)
- [x] All High findings resolved (none raised in this audit)
- [x] Every substantive finding has an explicit disposition
- [x] Accepted fixes have been re-tested at the cited executable revision
- [x] No escalated scientific claims remain unresolved

**Review gate result:** PASS for M1 remediation. F1/F2 defects are fixed, F3's existing
limitation is explicit and tested, and F4 is clarified without rewriting decisions.
Recommendation: READY TO MERGE once the PR's final checks remain green and the Tech
Lead approves. This does not authorize Milestone 2.
