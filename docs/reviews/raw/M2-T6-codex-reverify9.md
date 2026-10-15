### F34 — NaN solver times bypass reference mass-law validation

**Severity:** Medium  
**Claim:** `m2.py:903–905` validates state finiteness but not solver times. A NaN time makes the mass-law error NaN; `NaN > tolerance` is false, so off-law propellant passes.

**Evidence:** `review_scratch/reference_time_probe.py` changes raw SciPy terminal data to `t=NaN`, propellant **299 kg**; the prograde expectation is **287.62057980802405 kg**. Standalone O9 accepts it. Full Proof exits 0 with all **213 check records identical**. See `review_scratch/reference_time_probe.log`.

This is in scope under DR-0019 B: only independent-reference output data changes; validator helpers remain unmodified.

**Suggested fix:** Validate solver times for finiteness, ordering and segment endpoints. Require the mass-law expectation and computed error to be finite before accepting the comparison.

### F35 — Physically invalid finite dense velocities pass

**Severity:** Medium  
**Claim:** DOP853 dense velocities are checked for finiteness, then discarded (`m2.py:978–981`). They can contradict the trajectory and terminal states without rejection.

**Evidence:** `review_scratch/dense_velocity_probe.py` replaces every raw dense-output velocity with **zero**, preserving position and propellant. Standalone O9 passes. Full Proof accepts **17,463 corrupted dense outputs**, exits 0, and produces identical check records.

This is in scope under DR-0019 B: it corrupts independent-reference dense-output data without changing validator implementation.

**Suggested fix:** Check dense-state consistency against terminal states at shared times and validate the velocity against the position evolution. Add finite-corruption rejection tests.

### F36 — Physically invalid finite Kepler coast velocities pass

**Severity:** Medium  
**Claim:** GMAT coast alignment checks Kepler velocity only for finiteness, then discards it (`gmat_m2.py:372`). A zero velocity paired with the propagated orbital position passes.

**Evidence:** `review_scratch/kepler_velocity_probe.py` changes raw Kepler velocities to zero only for coast alignment. Standalone O9 accepts **894 corrupted outputs**. Full Proof accepts **3,577**, exits 0, and produces identical check records.

This is in scope under DR-0019 B: the probe changes independent-reference output data; `kepler_state` and alignment helpers remain unmodified.

**Suggested fix:** Compare Kepler coast velocity with the corresponding GMAT velocity using an appropriate documented gate. Test finite velocity corruption alongside non-finite values.

### F37 — CLI summary ignores unsubmitted command IDs

**Severity:** Medium  
**Claim:** `cli_summary_violations` never validates `unsubmitted_command_ids`, although the CLI summary builder emits it.

**Evidence:** `review_scratch/cli_summary_probe.py` changes the expected empty list to accepted-command IDs, invented IDs or null; each passes. `review_scratch/cli_summary_proof.py` mutates six actual returned summary dictionaries in place using a return-event profiler—replacing no implementation. Full Proof exits 0 with identical check records.

This is in scope under DR-0019 B: incorrect CLI summary data passes the T5 validation dependency.

**Suggested fix:** Reconcile unsubmitted IDs with the scenario timeline and submission boundary, including exact ordering and field presence.

### Summary

**Verdict: FAIL.**

- **F29–F33’s original reproductions are resolved.** Disabling their mechanisms causes respectively **12, 3, 2, 1 and 2** regression failures. F34–F36 expose additional reference-data gaps.
- All eight required commands pass: **989 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism and cross-platform validation.
- All **212 prior check records**, including **773 metric values**, are bit-identical; the current report contains **213 checks**.
- T5 baseline limits, M1 gates, golden assets and loaded baseline thresholds are preserved. O9 position limits respect the **15 µm floor**.
- DR-0017/DR-0018 remain separate; thresholds remain provisional; no T7 implementation scope appears.
- All three GMAT reports are byte-identical to `1de827e`.
- Artifact, history, threshold and row-corruption sweeps reject their tested mutations. Documentation records the scope and pins accurately, but its complete-reference-validation and closed-boundary claims are contradicted above.
- All **133 protected tracked files** match `1270b09`. Review artifacts are confined to `review_scratch/`.

Run each finding’s probe with `PYTHONPATH=src .venv/bin/python review_scratch/<script>.py`.