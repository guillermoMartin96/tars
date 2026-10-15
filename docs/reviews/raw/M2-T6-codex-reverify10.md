### F38 — Kepler invariants do not validate orbital phase

**Severity:** Medium  
**Claim:** `kepler_state` accepts a state on the opposite side of the orbit. Energy and angular momentum conservation do not establish propagation to the requested time; O6 reduces the unchecked state to SMA and passes.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py kepler`. The probe negates the actual returned position and velocity arrays for O6 midpoint propagation. Ten corrupted outputs pass the full Proof, with exit 0 and all 213 check records identical. See `review_scratch/kepler_phase.log`.

This is in scope under DR-0019 B: invalid independent-reference output data passes through unchanged validator helpers.

**Suggested fix:** Independently validate orbital phase/time of flight, including O6 midpoint states. Add an invariant-preserving wrong-phase regression.

### F39 — Dense consistency accepts invalid trajectories and unchecked stencil components

**Severity:** Medium  
**Claim:** The dense-output guard checks sampled position derivatives and an endpoint, but does not reconcile the trajectory with solver nodes or validate every newly requested dense state.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py dense`. It negates interior dense positions and velocities while preserving endpoints, propellant and position norms. Standalone O9 passes; full Proof accepts **514,245 corrupted returned states** with identical check records.

The same script’s `stencil` mode inserts NaN into velocity and propellant at the guard’s `t±0.001 s` requests. **377,796 corrupted states** also pass with identical records. See `review_scratch/dense_phase.log` and `review_scratch/stencil_phase.log`.

This is in scope under DR-0019 B: only independent-reference output data changes; the validation helpers remain unchanged.

**Suggested fix:** Validate every component at every dense evaluation, including derivative stencils. Reconcile dense states with solver nodes and both segment boundaries, and check dynamical consistency.

### F40 — Finite DOP853 interior solver states remain physically unchecked

**Severity:** Medium  
**Claim:** `_check_reference_states` checks finiteness and propellant, but does not validate interior solver positions and velocities against the trajectory.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py solver`. It negates `sol.y[:6, 1:-1]`, preserving initial/terminal states, times, dense output and propellant. Standalone O9 accepts **7,424 corrupted states**. Full Proof accepts **70,924**, exits 0, and produces identical 213 check records. See `review_scratch/solver_phase.log`.

This is in scope under DR-0019 B: raw DOP853 output data is corrupted without changing validator implementation.

**Suggested fix:** Reconcile every solver node with dense output and validate trajectory/time consistency. Add finite interior-state corruption tests.

### F41 — No-propulsion CLI summary fields escape reconciliation

**Severity:** Medium  
**Claim:** `cli_summary_violations` skips final propulsion fields when there are no `PropulsionSampled` events, allowing the no-propulsion mission to claim fuel and an active engine.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/no_propulsion_summary_probe.py`. Each skipped field accepts an incorrect value. A return-event profiler then mutates the actual producer’s dictionary to report **1e9 kg** propellant and total mass, a burning engine, and invented active/pending burn IDs. Full Proof exits 0 with identical 213 check records. See `review_scratch/no_propulsion_summary.log`.

This is in scope under DR-0019 B: incorrect CLI summary data passes the T5 dependency; no validator helper is replaced.

**Suggested fix:** Require explicit null/empty values and field presence for missions without propulsion. Test missing, incorrect finite and non-finite values.

### Summary

**Verdict: FAIL.**

- **F34–F37’s original reproductions are resolved.** Seven targeted tests pass. Disabling F34, F35, F36 invariants, F36 coast velocity and F37 produces **2, 2, 1, 1 and 1 failures**, respectively.
- All eight required commands pass: **996 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism and cross-platform validation.
- Fresh M2 results match the implementer’s **213-check** report exactly. The three new coast-velocity metrics pass: **4.629e-9, 1.818e-9 and 4.486e-9 m/s**, against **1e-7 m/s**.
- T5 baseline limits, M1 limits, golden assets and loaded baseline thresholds are preserved. O9 position gates respect the 15 µm floor. The updated threshold pin matches the file and accompanies its change.
- DR-0017/DR-0018 remain separate; thresholds remain provisional; no T7 implementation scope appears. All three GMAT reports are byte-identical to `1de827e`.
- Tested artifact, history, threshold and GMAT-row corruptions are rejected. Workflow, interruption and physics-mutant regressions pass.
- Documentation’s general-closure and complete-reference-validation claims are contradicted by F38–F40.
- All **133 protected tracked files** remain byte-identical to `b3a76eb`; review evidence is under `review_scratch/`.

**Note:** The supplied `previous-m2-report-1270b09.json` contains **212 checks**, not 213. Its records and **773 prior metrics** match, except for the requested O9 metric/threshold additions; the fresh report additionally contains `report_only_metrics_finite`. VAL-0014 also still says 15 gated O9 metrics; there are now **16**.