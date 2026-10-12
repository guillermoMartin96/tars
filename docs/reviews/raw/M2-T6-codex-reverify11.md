### F42 — Kepler round trip still accepts the original wrong-phase corruption

**Severity:** Medium  
**Claim:** F38 remains unresolved. Corrupting both propagation outputs makes the errors cancel in the round trip.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/reference_phase_probe.py kepler`. It negates the actual returned position and velocity arrays during O6 propagation, including the backward call. Full Proof accepts **20 corrupted returns**, exits 0, and produces identical 213 check records. See `review_scratch/kepler_phase.log`.

**Scope:** Invalid independent-reference output data passes through unmodified validator helpers, explicitly in scope under DR-0019 B.

**Suggested fix:** Validate phase/time of flight independently of the same propagator’s inverse. Add the original two-sided corruption regression; the new test corrupts only forward propagation.

### F43 — Correlated solver and dense corruption defeats reconciliation

**Severity:** Medium  
**Claim:** Agreement between solver nodes and dense output does not establish a valid trajectory when both are corrupted consistently.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/correlated_probe.py correlated`. It negates interior solver and dense positions and velocities while preserving segment endpoints and propellant. Node reconciliation and the sampled derivative check pass. Standalone O9 and full Proof pass; **548,457 corrupted returned states** produce identical check records. See `review_scratch/correlated.log`.

**Scope:** The probe changes DOP853 result data and dense-output states, without modifying validator implementation. DR-0019 B includes invalid independent-reference outputs.

**Suggested fix:** Validate propagation continuity and node-to-node evolution against independently anchored dynamics, rather than relying solely on agreement between two outputs from the same reference.

### F44 — Finite but invalid stencil components remain unchecked

**Severity:** Medium  
**Claim:** The stencil fix checks finiteness, but still accepts physically invalid velocity and propellant components.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/correlated_probe.py stencil`. It sets velocity and propellant to **1e9** only at derivative-stencil evaluations, leaving positions unchanged. Standalone O9 and full Proof pass; **377,796 corrupted states** yield identical check records. See `review_scratch/finite_stencil.log`.

**Scope:** These are corrupted dense-reference outputs flowing through unchanged helpers, explicitly covered by DR-0019 B.

**Suggested fix:** Validate stencil propellant against the mass law and velocity against trajectory dynamics. Use stencils within each segment’s domain so boundary extrapolation does not undermine these checks.

### F45 — Segments without telemetry ticks skip solver-node reconciliation

**Severity:** Medium  
**Claim:** F40’s fix does not reconcile every solver node. `_check_dense_consistency` runs only when `ticks.size` is nonzero.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/tickless_probe.py tickless`. It negates only interior solver states in segments containing no telemetry ticks; dense output and endpoints remain unchanged. Standalone O9 accepts **145 corrupted nodes**. Full Proof accepts **587**, exits 0, and produces identical check records. See `review_scratch/tickless.log`.

**Scope:** Only raw DOP853 state data changes. Invalid independent-reference outputs are in scope under DR-0019 B.

**Suggested fix:** Perform solver-node reconciliation unconditionally for every segment, separately from telemetry-grid checks. Add a short-segment regression.

### F46 — Staged GMAT validation accepts a one-day epoch corruption

**Severity:** Medium  
**Claim:** GMAT epoch validation checks differences between rows but never anchors the first epoch to the script’s configured epoch.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/epoch_probe.py`. It shifts every report epoch by **86,400 s** and recomputes staged metadata, manifest and history digests using their normal rules. The unchanged pre-publication `_evaluate(..., base=stage)` returns no rejection and a passing check. Spacing remains **2.3376e-7 s**. See `review_scratch/epoch.log`.

This demonstrates a staged workflow false pass; committed-file tampering remains protected by the manifest pin.

**Scope:** Corrupted GMAT report artifacts accepted by the run workflow are explicitly in scope under DR-0019 B. No validator helper is replaced.

**Suggested fix:** Anchor the initial A1MJD to the configured script epoch with the appropriate time-scale conversion and resolution allowance. Preserve DR-0016’s schedule-derived elapsed-time labels.

### Summary

**Verdict: FAIL.**

- **F38:** unresolved; its original reproduction still passes.
- **F39:** partially resolved; individual dense corruption and non-finite stencils are rejected, but F43–F44 remain.
- **F40:** partially resolved; individual corruption is rejected on tick-bearing segments, but F43 and F45 remain.
- **F41:** resolved, including missing/wrong fields and 15 non-finite summary mutations.
- All **nine targeted tests pass**. Disabling round-trip, node, stencil and CLI mechanisms causes **1, 2, 1 and 5 failures**, respectively.
- All eight required commands pass: **1,005 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism and cross-platform validation.
- Fresh M2 Proof contains **213 checks and 777 metrics**, with names, metrics, thresholds and results identical to `previous-m2-report.json`.
- T5 baseline limits, M1 gates, golden assets and loaded thresholds are preserved. O9 position gates respect the 15 µm floor; threshold pins match.
- DR-0017/DR-0018 separation and provisional thresholds are preserved; no T7 implementation appears. All three GMAT reports are byte-identical to `1de827e`.
- Artifact, threshold, GMAT-row and simulator-data sweeps rejected their other tested corruptions. Workflow and interruption regressions pass.
- README and VAL-0014’s metric-count correction are consistent. General reference-validation and closure claims in VAL-0014, the review record and DR-0019 are contradicted by F42–F46.
- All **133 protected snapshot files** remain byte-identical to `1a11ff7`. Review evidence is under `review_scratch/`.