### F47 — Corrupted reference radii can change reported metrics and reverse O9 acceptance

**Severity:** Medium

**Claim:** Solver-node reconciliation and local position/velocity consistency do not anchor consumed dense-output radii to the physical trajectory. Correlated interior position corruption passes while changing the T5 altitude oracle. This is blocking under **DR-0019 B** (corrupted independent-reference data and simulator output through unchanged validators) and **DR-0020 A** (affected `orbit_events.max_altitude_error_m`, reported values and O9 acceptance).

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/translation_probe.py`. It adds 5 mm in x to interior solver positions and corresponding dense positions, preserving endpoints, velocities and propellant. Standalone O9 passes; full Proof exits 0 with all 213 checks passing, but **16 check records change**. For `orbit_events[m2_prograde_burn]`, `max_altitude_error_m` changes from **0.004306526854634285** to **0.0006386237218976021**. See `review_scratch/translation.log`.

Run `PYTHONPATH=src .venv/bin/python review_scratch/extrema_acceptance_probe.py` for an acceptance reversal: a simulator completion maximum overstated by **0.1 m** is rejected against the clean reference (`max_altitude_error_m=0.0956935 > 0.013`). Scaling interior reference r/v together by `1 + 0.1/6628137`, while preserving endpoints and propellant, makes unchanged standalone O9 return **no rejections and PASS**. See `review_scratch/extrema_acceptance.log`. Only returned reference data and simulator output are corrupted; validator implementations, thresholds and GMAT artifacts remain unchanged.

This differs from accepted F43: negation preserves radii; these mutations change a consumed quantity and can conceal a failing simulator report.

**Suggested fix:** Independently anchor the dense radii used for extrema to the validated segment state and physical evolution, with justified numerical bounds. Add both the reference-only metric-corruption regression and the simulator/reference acceptance-reversal regression; preserve existing gates and the reference floor.

### F48 — Finite reference velocities bypass derivative consistency through norm overflow

**Severity:** Medium

**Claim:** Finite but enormous reference velocities produce infinite speed and error norms. `_check_dense_consistency` accepts `inf <= tolerance * inf`, allowing a velocity that violates `r′ = v`. This is blocking under **DR-0019 B** because invalid reference data traverses unchanged helpers, and under **DR-0020 A** because it defeats the existing position-derivative consistency check and its explicitly required physical relation. Condition 3 preserves that check even when its intermediate velocity is otherwise unreported.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/overflow_velocity_probe.py`. It sets interior solver and corresponding dense velocities to **1e200**, preserving positions, propellant and endpoints. Every returned component remains finite; node reconciliation succeeds. NumPy norms overflow, and the derivative check accepts the resulting infinite comparisons. Standalone O9 passes. Full Proof exits 0 after **34,152 corrupted solver nodes and 719,908 corrupted dense returns**, with all **213 check records identical** to the clean run. See `review_scratch/overflow_velocity.log`.

Unlike F43, this corruption does not preserve derivative consistency: the dense positions still have ordinary orbital derivatives while their velocities are enormous.

**Suggested fix:** Use overflow-safe norms and reject non-finite derived speeds, differences and comparison bounds before applying tolerances. Add a regression with correlated, finite `1e200` velocities; terminal metric finiteness alone cannot detect this bypass.

### Summary

**Verdict: FAIL.** F47 and F48 are blocking under the approved review scope.

- **F42–F43:** accurately recorded as **accepted residual risk**, not fixed. Their exact original mutations again produce identical 213-check results. The stated relevance analysis is correct for those mechanisms; it does not cover F47 or F48.
- **F44–F46:** resolved. Five targeted cases pass. Disabling stencil velocity validation, stencil mass-law validation, unconditional node reconciliation and the epoch anchor causes **one targeted failure each**.
- All eight required commands pass: **1,010 tests**, Ruff lint/format, M2/M1 Proof, both GMAT comparisons, determinism and cross-platform validation. Workflow, interruption, artifact, row, threshold and simulator-output sweeps reject their other tested corruptions.
- Fresh M2 Proof has **213 checks and 777 metrics**. Names, metrics, thresholds and results match `previous-m2-report.json` exactly; only CPU platform metadata differs.
- T5 baseline limits, M1 gates, golden assets and loaded thresholds are unchanged. Threshold and manifest pins match; pinned files are unchanged from `1a11ff7`. Applicable O9 position gates respect the **15 µm floor**. M2 thresholds remain provisional; DR-0017/DR-0018 separation is preserved; no T7 implementation appears. All three GMAT reports are byte-identical to **1de827e**.
- README and the decision/disposition records reflect the approved scope and F42–F46 status. Broad claims of complete reference validation remain contradicted by F47–F48 and need correction with their remediation. All **133 protected snapshot files** remain unchanged. Evidence is under `review_scratch/`.
