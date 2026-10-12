### F38 — Kepler invariants do not validate orbital phase
**Severity:** Medium
**Claim:** `m2.kepler_state` accepts a state on the opposite side of the orbit. Conservation of energy and angular momentum does not establish propagation to the requested time; O6 then reduces the unchecked state to SMA and passes.
**Evidence:** `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py kepler` negates the actual returned position and velocity arrays only for O6 midpoint propagation. All validator helpers remain unchanged. Ten corrupted reference outputs pass the full Proof (exit 0), with all 213 check records identical. See `review_scratch/kepler_phase.log`. This is in scope under DR-0019 B: invalid independent-reference output DATA passes through unmodified helpers.
**Suggested fix:** Validate Kepler phase/time of flight against an independent expectation, including O6 midpoint states; add an invariant-preserving wrong-phase regression.

### F39 — Dense consistency accepts wrong trajectories and unchecked stencil components
**Severity:** Medium
**Claim:** The dense-output guard checks local position derivatives at tick times and one endpoint, but does not reconcile the trajectory with solver nodes or validate every newly requested dense state.
**Evidence:** `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py dense` negates raw dense positions and velocities at interior ticks, preserving endpoint values, mass and position norms. Standalone O9 passes; the full Proof accepts 514,245 corrupted returned states and produces identical check records. The `stencil` mode puts NaN into velocity and propellant returned at the guard's t±0.001 s requests; 377,796 corrupted states likewise pass with identical records. See `review_scratch/dense_phase.log` and `review_scratch/stencil_phase.log`. This is in scope under DR-0019 B: finite and non-finite independent-reference DATA is corrupted; the dense-consistency and reduction helpers are unchanged.
**Suggested fix:** Validate all components at every dense evaluation, including derivative stencils. Reconcile dense states with solver nodes and both segment boundaries, and check dynamical consistency rather than only sampled kinematics.

### F40 — Finite DOP853 interior solver states remain unchecked physically
**Severity:** Medium
**Claim:** `_check_reference_states` checks solver-state finiteness and propellant, but never checks interior position/velocity against the integrated trajectory. Invalid finite solver states pass if the terminal and dense outputs remain valid.
**Evidence:** `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py solver` negates `sol.y[:6, 1:-1]` in the real SciPy result, preserving its initial/terminal states, times, dense output and propellant. Standalone O9 accepts 7,424 corrupted states. The full Proof accepts 70,924 and exits 0 with all 213 records identical. See `review_scratch/solver_phase.log`. This is in scope under DR-0019 B: raw DOP853 output DATA is changed without changing validator implementation.
**Suggested fix:** Reconcile every solver node with dense output and validate its trajectory/time consistency. Add a finite interior-state corruption test.

### F41 — No-propulsion CLI summary fields escape reconciliation
**Severity:** Medium
**Claim:** `cli_summary_violations` skips final propulsion fields when there are no `PropulsionSampled` events, letting the no-propulsion mission claim fuel and an active engine.
**Evidence:** `PYTHONPATH=src .venv/bin/python review_scratch/no_propulsion_summary_probe.py` independently changes each skipped field, then mutates the actual producer's returned dictionary using a return-event profiler: propellant and total mass = 1e9 kg, engine = burning, and invented active/pending burn IDs. All are accepted. Full Proof exits 0 with identical 213 check records. See `review_scratch/no_propulsion_summary.log`. This is in scope under DR-0019 B: incorrect simulator CLI summary DATA passes the T5 dependency; no validator helper is replaced.
**Suggested fix:** Require the no-propulsion null/empty values and field presence explicitly; exercise absent, finite incorrect and non-finite values.

### Summary
**Verdict: FAIL.**

- F34–F37's original reproductions are resolved. Seven targeted tests pass. Disabling F34, F35, F36 invariants, F36 coast velocity and F37 produces 2, 2, 1, 1 and 1 failures. F38–F41 expose remaining in-scope gaps.
- All eight required commands pass: 996 tests (two expected overflow warnings), Ruff, M2 Proof (213 checks), M1 Proof, both GMAT comparisons, determinism and cross-platform validation.
- The fresh M2 report matches the implementer's 213-check report (all contents except platform). The supplied older report actually has 212 checks: all its records and 773 previous metrics are unchanged apart from the new O9 velocity metric/threshold in three checks; `report_only_metrics_finite` is also present in the fresh report. New velocity metrics are 4.629e-9, 1.818e-9 and 4.486e-9 m/s, all below 1e-7 m/s.
- T5 baseline gates, M1 gates, golden assets and loaded baseline thresholds are preserved. O9 position gates respect the 15 µm floor. The new m2.json pin matches the file and was updated with it in fix10.
- DR-0017/DR-0018 remain separate, thresholds remain provisional, and no T7 implementation scope appears. All three GMAT reports are byte-identical to 1de827e.
- Artifact/history/threshold and GMAT-row sweeps reject the tested mutations; workflow generation, publication/interruption and simulator physics-mutant regressions pass.
- Documentation's scope and numerical evidence are consistent, but the review record's general-closure claim and VAL-0014's complete-reference-validation claim are contradicted by F38–F40.
- All 133 protected tracked files remain byte-identical to b3a76eb. Review scripts and evidence are under review_scratch/.

**Note:** VAL-0014 still says 15 gated O9 metrics; there are now 16, and its results table omits the new coast-velocity gate. The supplied previous-report filename/count mismatch limits the exact historical comparison to its actual 212 records.
