**F1: RESOLVED —** Injected first-step failure now leaves the final sample `scheduled`, with pending `burn#000001`, matching `final_propulsion`. Both new failure-after-submission tests (0 s and 60 s) fail against reconstructed old code. The timeout-boundary test also fails against old code and passes now. Submission order and suppression at terminating ticks match the revised contract; M1 ordering remains unchanged.

**F2: RESOLVED —** Original tuple/NaN, bytes, set and numeric-subclass probes now raise `ValidationError`. Direct submission and timeline execution produce identical receipts for valid JSON payloads, including deliberately invalid commands. Eight newly covered invalid payload cases and the private-copy test fail against old code. Inspection confirms the runner uses a type-preserving deep copy.

**F3: RESOLVED —** Injecting failure on the summary rename leaves new events **without a summary**, correctly marking publication incomplete. Staging failure preserves the previous complete pair. Removing commit-marker retraction in a scratch mutation makes both interruption tests fail. This satisfies the documented single-publication interruption protocol; it does not preserve the previous complete generation after publication begins.

**F4: RESOLVED —** Duration scenarios round-trip through canonical JSON and Python dumps; compatible `with_dt(5.0)` succeeds. Implicit, explicit and null orbits-stop defaults produce identical hashes. Duration round-trip, `with_dt`, and default-canonicalization tests fail against old code.

**F5: RESOLVED —** The original overflow scenario now exits **2**, without a traceback. Duration, submission and telemetry ratio regression tests fail against old code. A separate orbits-timeout arithmetic issue remains below.

Evidence: `review_scratch/probes.txt`, `old-regression-tests.txt`, `publication-mutation.txt`, and `remaining-regression-checks.txt`.

### N1 — Orbits-stop timeout arithmetic can still overflow

**Severity:** Low  
**Claim:** Schema-valid finite version-2 inputs can crash the orbits-stop runner instead of receiving an invalid-input diagnostic. This is a remaining arithmetic edge case, not introduced by the fixes.

**Evidence:** `src/tars/sim/runner.py:164` applies `math.ceil()` to an unchecked product and quotient. Two independent configurations validate successfully but exit **1** with `OverflowError: cannot convert float infinity to integer`:

- `stop={"orbits":2,"max_duration_periods":1e308}`.
- `stop={"orbits":2}`, `dt_s=1e-308`, matching telemetry interval, and no commands.

Inputs and CLI traces are preserved in `review_scratch/guard_product.json`, `orbit_tick_ratio.json`, and `timeout-overflow.txt`.

**Suggested fix:** Validate representability of the complete orbits-timeout calculation before execution and report unsupported configurations as invalid input. Add regression tests for product and quotient overflow.

**Note:** Not every new test distinguishes old behavior. The integer-payload runner test, infinity rejection, and two orbits serialization cases pass against old code; they provide positive coverage. Defect-specific tests do catch each original finding.

### Summary

**Verdict: CONDITIONAL PASS — F1–F5 resolved; N1 remains.**

- **687 tests passed**; Ruff lint and format checks passed.
- Determinism reproduced exact M1 hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- M1 Proof passed all approved gates.
- M2 slice succeeded at tick **5370**, with **nine orbits**; repeated JSONL output was byte-identical.
- No new event types, rejection codes, permission semantics, or scope expansion found. DR-0017’s Δv bound remains distinct from trajectory error.

No source or test files were edited; review artifacts are under `review_scratch/`.