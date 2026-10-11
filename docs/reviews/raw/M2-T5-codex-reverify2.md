### F16 — Returned receipts and plans remain incompletely reconciled

**Severity:** Medium  
**Claim:** F8 remains partially unresolved. Validated events can accompany contradictory returned command intent, diagnostics and burn plans.

**Evidence:** [new_probes.py](review_scratch/new_probes.py) passes **206/206 checks** after independently deleting receipt commands, fabricating receipt schema errors/detail, or setting accepted-plan ignition, commanded duration, mass flow or timing bound to **999**. Changing the returned scenario also passes. [more.py](review_scratch/more.py) passes **206/206** with corrupted active/pending-plan duration, ignition, mass flow, cause, policy and timing bound. `check_result_consistency()` compares only selected plan fields.

**Suggested fix:** Reconcile complete receipts and plans with scenario inputs and validated events, including command intent, diagnostics, rejected-plan absence and every final snapshot plan field.

### F17 — Altitude extrema can omit extrema between telemetry samples

**Severity:** Medium  
**Claim:** F14 remains partially unresolved. The new limits constrain outward errors but permit reported extrema to understate the actual tick-history range.

**Evidence:** Mutation `completion.sample_extrema_instead_of_tick_extrema` replaces completion extrema with extrema from `StateSampled` alone and passes **206/206 checks**. It understates the depletion mission’s maximum altitude by **2.1275 m** and overstates the invalid-command mission’s minimum by **1.9372 m**. Both exceed the stated **0.6 m** allowance. See [extrema.json](review_scratch/extrema.json) and [more-results.json](review_scratch/more-results.json).

**Suggested fix:** Independently predict extrema over the executed tick grid and requested horizon, then gate errors in both directions. Sample bracketing and global apsides are insufficient.

### F18 — Invalid event schema versions pass the Proof

**Severity:** Low  
**Claim:** The audit checks event semantics without verifying the schema-version contract.

**Evidence:** Mutation `event.schema_version` changes every event’s version to **999** and passes **206/206 checks**, although the event schema requires version **1**. See [new-results.json](review_scratch/new-results.json).

**Suggested fix:** Validate serialized event envelopes against the event schema, or explicitly require the supported schema version before auditing their contents.

### Summary

**Verdict: FAIL.**

- **F5:** Resolved; doubled O3 duration rejected.
- **F6:** Resolved; auxiliary telemetry audited. The old 630 s probe is now a no-op because that sample is no longer emitted; the adapted auxiliary corruption is rejected.
- **F7:** Resolved; coast-only missions have independent trajectory gates.
- **F8:** Partially resolved; remaining gaps are F16.
- **F9:** Resolved; intermediate schedule, mass and sensed-Δv mutants rejected.
- **F10:** Resolved; reversed thrust between state samples rejected.
- **F11:** Resolved; transition payload mutants rejected.
- **F12:** Resolved for event plans, timing claims and represented D1a cutoff; returned-plan gaps fall under F16.
- **F13:** Configuration, issuer, schema-error and invalid-intent checks resolved; diagnostic reconciliation remains incomplete under F16.
- **F14:** Partially resolved; orbit and sampled-altitude checks work, but extrema retain F17.
- **F15:** Resolved; missing thresholds fail metric coverage.

All seven requested commands passed: **818 tests**, lint/format, **206-check M2 Proof**, M1 Proof, determinism, platform-specific golden comparison and GMAT M1 comparison. Lint/format ran before adding review scripts.

Selective in-memory removal of the new checks produced failing regressions for every F5–F15 family: **38 failures**, with five selected cases still caught by overlapping gates. These were check removals, not historical source checkouts.

The Simpson bound is correctly derived and independently computed from predicted burns and the tick grid. It is tight: normal O6 error/bound ratios are approximately **0.62–0.99**. Both **1 ppm mass-flow** and **1 ppm sensed-integrand** mutants are rejected. The changed gate expands acceptance relative to the raw-error gate for high-thrust variants, but uses a justified analytic truncation allowance; the numerical discovery and changed gate are disclosed.

Fresh measurements support the ignition, direction, node-time and per-sample limits. The extrema limits gate outward errors but leave F17. Thresholds remain provisional; M1 gates, DR-0017 separation, FU-1 and same-tick behavior are preserved. No T6–T8 implementation or approval scope was introduced.

The complete field inventory, numerical assessment and verification details are in [review_scratch/audit.md](review_scratch/audit.md). No implementation fixes were made.