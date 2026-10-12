### F29 — DOP853 dense-output validation discards invalid components

**Severity:** Medium  
**Claim:** `m2.py:938` checks only position-derived altitude. Non-finite dense-output velocity and propellant escape validation. This is in scope under DR-0019 B: independent-reference data is corrupted while validator helpers remain unchanged.

**Evidence:** `review_scratch/oracle_matrix.py` demonstrates acceptance for NaN and ±infinity in each velocity component and propellant. `oracle_proof.py dense` exits 0 with all **213 results identical** to the clean Proof.

**Suggested fix:** Validate the complete dense-output state before slicing it. Add component-by-component and integrated rejection tests.

### F30 — GMAT coast alignment accepts invalid Kepler velocity

**Severity:** Medium  
**Claim:** `gmat_m2.py:366` discards Kepler’s returned velocity without validating it. Invalid independent-reference outputs are explicitly in scope under DR-0019 B.

**Evidence:** `review_scratch/oracle_matrix.py` corrupts only the velocity returned to `alignment_metrics`; NaN and ±infinity all pass standalone O9. `oracle_proof.py kepler` passes all **213 checks**, with results identical to the clean run. Validator helpers are unchanged.

**Suggested fix:** Validate both returned vectors before computing the coast metric. Test this consumer independently of O5 and node bisection.

### F31 — Negative DOP853 terminal propellant passes

**Severity:** Medium  
**Claim:** DOP853 state validation requires finiteness but does not reject physically invalid propellant. The seventh state component is ignored by downstream comparisons. This is in scope as invalid independent-reference data.

**Evidence:** `review_scratch/reference_mass_solver.py` changes raw SciPy terminal output to **−1 kg propellant**, leaving every validator helper unchanged. Standalone O9 accepts it. Full Proof exits 0 with **213 results identical** to the clean run.

**Suggested fix:** Validate reference propellant against the independent mass law and depletion semantics at production and consumption boundaries.

### F32 — Rebuilding the manifest chain hides deleted history

**Severity:** Medium  
**Claim:** Manifest history lacks an independent approval anchor. Although documented as F14’s limitation, the supplied DR-0019 B scope explicitly includes history tampering and provides no wholesale-rewrite exemption.

**Evidence:** `review_scratch/history_rewrite.py` deletes nine records, reducing history from **12 to 3**, and recomputes the remaining chain. All three missions return `rejected=[]` and pass. Only copied manifest data changes.

**Suggested fix:** Verify history against an independently approved digest or trusted historical record. A chain stored entirely inside the mutable manifest cannot authenticate its own history.

### F33 — Finite threshold tampering permits wrong physics to pass

**Severity:** High  
**Claim:** Threshold loaders check structure and numerical validity but do not authenticate approved values. Tampered finite limits can disable numerical validation. Threshold corruption and incorrect simulator physics are both in scope under DR-0019 B.

**Evidence:** `review_scratch/finite_threshold_tamper.py` applies the existing thrust × `(1 + 1e-5)` mutant. Approved thresholds reject its approximately **47.7 m** final-position error. Redirecting threshold-file reads to a scratch copy containing finite `1e100` limits makes standalone O9 pass and full Proof exit 0 with **all 213 checks passing**. Validator implementations remain unchanged.

**Suggested fix:** Bind loaded thresholds to independently approved values or digests, including provisional thresholds. Test finite inflation alongside non-finite and missing limits.

### Summary

**Verdict: FAIL.**

- **F26–F28 resolved.** Disabling their mechanisms produces the expected regression failures: F26 four; F27 three; F28 standalone three and terminal Proof one.
- **All eight required commands pass:** 969 tests, Ruff, both Proof validators, both GMAT comparisons, determinism and cross-platform validation.
- **Report identity confirmed:** all 212 previous check records and 773 metric values are bit-identical. There are now 213 checks.
- T5 baseline, M1 gates, golden assets and loaded baseline limits are preserved. O9 position limits respect the 15 µm floor. Thresholds remain provisional; DR-0017/DR-0018 remain separate; no T7 implementation scope appears.
- All three GMAT reports are byte-identical to `1de827e`.
- Documentation accurately records the history-rewrite limitation, but its closed-boundary claims are contradicted by the findings above.
- All 132 protected tracked files remain byte-identical to `6a03e1b`.

Executable probes and logs are under `review_scratch/`. Run probes with `PYTHONPATH=src .venv/bin/python review_scratch/<script>.py`.