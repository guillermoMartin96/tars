### F47 — Corrupted reference radii can reverse O9 acceptance

**Severity:** Medium

**Claim:** Correlated interior solver/dense position corruption passes reconciliation while changing the consumed altitude oracle. Blocking under **DR-0019 B** because corrupted reference data traverses unchanged validators, and **DR-0020 A** because it affects reported `orbit_events` metrics and O9 acceptance.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/translation_probe.py`. Adding 5 mm to interior solver and dense x positions preserves endpoints, velocities and propellant. Standalone O9 and all 213 Proof checks pass, but **16 check records change**. Prograde `max_altitude_error_m` changes from **0.0043065269** to **0.0006386237**.

Run `PYTHONPATH=src .venv/bin/python review_scratch/extrema_acceptance_probe.py`. A simulator maximum altitude overstated by **0.1 m** is rejected against the clean reference: **0.0956935 m > 0.013 m**. Scaling interior reference r/v together, preserving endpoints and propellant, makes unchanged O9 return **no rejections and PASS**.

See `review_scratch/translation.log` and `review_scratch/extrema_acceptance.log`. Unlike accepted F43’s negation, these mutations change consumed radii.

**Suggested fix:** Independently anchor consumed dense radii to the validated segment state and physical evolution. Add regressions for both changed reported metrics and reversed acceptance, preserving existing gates and the reference floor.

### F48 — Finite reference velocities bypass derivative consistency through overflow

**Severity:** Medium

**Claim:** Enormous finite velocities produce infinite speed and error norms. `_check_dense_consistency` accepts `inf <= tolerance * inf`, despite violating `r′ = v`. Blocking under **DR-0019 B** because only reference data is corrupted, and **DR-0020 A** because the existing derivative-consistency check and required physical relation are defeated. Condition 3 requires that check to remain enforced.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/overflow_velocity_probe.py`. It sets interior solver and corresponding dense velocities to **1e200**, preserving positions, propellant and endpoints. All returned components remain finite; node reconciliation succeeds, but NumPy norms overflow.

Standalone O9 passes. Full Proof exits 0 after **34,152 corrupted solver nodes and 719,908 corrupted dense returns**, with all **213 check records identical** to the clean run. See `review_scratch/overflow_velocity.log`.

Unlike F43, this mutation does not preserve position-derivative consistency.

**Suggested fix:** Use overflow-safe norms and reject non-finite derived speeds, errors and bounds before tolerance comparisons. Add the correlated finite-velocity regression.

### Summary

**Verdict: FAIL.** F47 and F48 are blocking under the approved scope.

- **F42–F43:** accurately recorded as **accepted residual risk**, not fixed. Their original mutations again leave all 213 check records identical. Their relevance analysis is correct for those exact mechanisms.
- **F44–F46:** resolved. Five targeted cases pass. Disabling velocity validation, stencil mass-law validation, unconditional node reconciliation and epoch anchoring causes **one targeted failure each**.
- All eight required commands pass: **1,010 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism and cross-platform validation. Other tested artifact, threshold, row, simulator and workflow corruptions are rejected.
- Fresh M2 Proof matches the previous **213 checks and 777 metrics** exactly, including names, thresholds and results. Only CPU platform metadata differs.
- T5 baseline limits, M1 gates, golden assets and loaded thresholds remain unchanged. Threshold/manifest pins match. Applicable O9 position gates respect the **15 µm floor**; M2 thresholds remain provisional. DR-0017/DR-0018 separation is preserved; no T7 implementation appears. All three GMAT reports match **1de827e** byte-for-byte.
- README and decision/disposition records reflect the approved scope and F42–F46 status. Broad reference-validation claims remain contradicted by F47–F48. All **133 protected snapshot files** are unchanged; evidence is under `review_scratch/`.