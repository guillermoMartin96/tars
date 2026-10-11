### F1 — O4 trusts an unverified initial state

**Severity:** High  
**Claim:** A simulator initializing the wrong orbit can pass every M2 check because O4 takes its initial position and velocity from `SimulationStarted`, rather than independently deriving them from the scenario.

**Evidence:** `src/tars/validation/m2.py:774–778` seeds DOP853 from the log. In `review_scratch/initial_probe.py`, monkeypatching `runner.initial_state` to rotate both vectors by 90° produced **PASS on all 76 full Proof checks**, including O8. See `review_scratch/initial_mutant_full.json`. This simulator-output dependency is absent from the documented independence exceptions.

**Suggested fix:** Independently calculate the scenario’s initial Cartesian state, verify the initial event against it, and seed O4 from that expectation. Add a wrong-orientation mutant.

### F2 — Successful termination is not checked against the requested horizon

**Severity:** High  
**Claim:** The Proof can accept a substantially shortened mission as successful and measure trajectory accuracy at the wrong time.

**Evidence:** `check_outcomes` uses `SimulationCompleted.t` as its horizon (`m2.py:433`); O4 and cadence checks also follow the reported endpoint. `review_scratch/stop_probe.py` substitutes a 3,000-second stop for each 53,700-second mission. **All 76 full Proof checks pass**, and every mission’s reported final time is 3,000 seconds. See `review_scratch/stop_mutant_full.json`.

**Suggested fix:** Verify successful duration stops against `scenario.stop.duration_s` and its exact tick. Calculate reference endpoints from the requested horizon. Add a premature-success mutant.

### F3 — Powered samples and boundary completion states escape validation

**Severity:** Medium  
**Claim:** Large errors in state telemetry can pass while cutoff and final reference comparisons remain correct.

**Evidence:** O4 checks `BurnEnded` and `SimulationCompleted`; O5 excludes powered intervals. In `review_scratch/probe.py`, doubling `StateSampled.r` at 630 seconds during burns passed all 76 full Proof checks, including control and replay checks. Separately, replacing the active-stop `SimulationCompleted.r/v` with billion-metre and million-metre-per-second vectors yielded `boundary_violations(...) == []`: that function compares samples but never reconciles the completion state with them. Results are in `review_scratch/probe.log` and `review_scratch/mutant_full.json`.

**Suggested fix:** Compare powered telemetry against the independent reference and check consistency among final samples, `SimulationCompleted`, and `RunResult.final`. Include equivalent consistency checks for `final_propulsion`.

### F4 — Missing depletion events are accepted

**Severity:** Medium  
**Claim:** The event checker enforces depletion pairing in only one direction, allowing a depletion termination without its required `PropellantDepleted`.

**Evidence:** `m2.py:258–264` requires an existing `PropellantDepleted` to precede its `BurnEnded`; it does not require every depleted `BurnEnded` to have that predecessor. The full probe removed every depletion event and still passed all 76 checks. The contract explicitly requires `PropellantDepleted`, then `BurnEnded`, at depletion cutoffs.

**Suggested fix:** Require exactly one matching, immediately preceding depletion event for every `BurnEnded(end_cause="propellant_depleted")`. Verify its correlation fields and exact event time; add deletion and mismatched-payload tests.

### Summary

**Verdict: FAIL** — two High and two Medium validator findings, demonstrated with executable mutations. No implementation fixes were made; review artifacts are under `review_scratch/`.

Verified:

- All seven requested commands passed: **762 tests**, lint/format, M2 and M1 Proof, determinism, cross-platform golden comparison, and GMAT M1 comparison.
- All four committed M2 scenarios passed additional cross-process replay checks.
- Fresh measurements match VAL-0013 at its published precision.
- The independent RHS, DOP853 segmentation, O5 cutoff-state method, O6 midpoint method, and O8 timestep choices are sound for the reference missions.
- Hand-declared receipts, rejection coverage, overlapping burns, control runs, and same-tick semantics are exercised.
- Thresholds remain provisional; M1 gates and platform-specific hash handling are preserved. The timing Δv budget remains separate from trajectory error, FU-1 remains recorded, and T6–T8 remain deferred.