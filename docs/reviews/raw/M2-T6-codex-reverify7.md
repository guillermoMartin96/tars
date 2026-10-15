### F26 — Infinite depletion bounds turn failing residuals into zero

**Severity:** Medium  
**Claim:** `m2.py:715` divides the depletion residual by an unchecked bound. A ±infinite bound produces finite zero, which passes `worst` and `Check`.

**Evidence:** `review_scratch/residual_full.py` introduces a bookkeeping-consistent `1e-10 kg` residual. With the normal bound, the main and auxiliary O1 checks fail with a ratio of approximately **2746.24**, above the limit of 1. Patching `_ulp` to ±infinity makes **all 28 full-mission checks pass**, with no missing gates or non-finite report metrics. NaN correctly rejects. See `residual_full.log`.

**Suggested fix:** Require the computed bound to be finite and positive before division. Add standalone and integrated regression tests that fail when this validation is disabled.

### F27 — Aliased reducers bypass the actual AST allowlist

**Severity:** Low  
**Claim:** The AST guard recognizes reducer names syntactically but does not resolve aliases.

**Evidence:** `review_scratch/alias_guard.py` replaces the auxiliary merge with `reducer.reduce(...)`, importing `numpy.fmax as reducer`. The **actual allowlist test passes**. The mutated merge turns a good metric followed by NaN into **0.1**; the original merge returns infinity. See `alias_guard.log`.

**Suggested fix:** Resolve imported reducer aliases and simple reducer bindings, or explicitly reject unsupported alias forms in guarded files. Test the aliased merge through the actual allowlist test.

### F28 — Standalone O9 accepts non-finite T5 report-only metrics

**Severity:** Low  
**Claim:** `_evaluate` checks finiteness of O9 metrics, but its T5 audit loop checks only gated metrics. Non-finite report-only audit metrics still permit standalone acceptance.

**Evidence:** `review_scratch/report_only.py` injects NaN and ±infinity into `sensed_delta_v_rel_error_max`, `sample_delta_v_rel_error_max`, and `final_propellant_kg`. **All nine mutations pass standalone O9**, with no rejection reasons. Proof’s `Gates` records each for rejection.

The new report-only test also **survives removing the terminal Proof check**, demonstrated in `report_gate_disable.log`.

**Suggested fix:** Validate every T5 audit metric for finiteness in standalone evaluation. Add tests covering standalone rejection and the terminal Proof result; require both to fail when their mechanisms are disabled.

### Summary

**Verdict: FAIL**, because F26 demonstrates a remaining full-mission acceptance false pass.

- **F23 resolved:** normal, NaN, and ±infinite Simpson allowances reject the sensed-Δv error through standalone and full-mission paths. Disabling `excess_over` breaks the new tests.
- **F24 resolved for the reported forms:** direct ufunc reductions and the additional supported methods fail the actual allowlist test. Disabling ufunc resolution breaks the regression tests. Alias coverage remains incomplete under F27.
- **F25 resolved:** the integrated node test fails when either validator’s finiteness check is disabled independently.
- **All eight required commands pass:** **957 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism, and cross-platform validation.
- **Report identity confirmed:** all 212 previous checks and **773 metric values, bit-for-bit**, are identical. The added `report_only_metrics_finite` check passes. Complete JSON differs in `platform` and the added result.
- All **21 reference-component mutations, 18 row mutations, and 47 threshold deletions** reject.
- T5 baseline, M1 results, golden assets, and loaded limits remain unchanged. New O9 position gates respect the 15 µm floor. DR-0017/DR-0018 remain separate; thresholds remain provisional; no T7 implementation scope appears.
- All three GMAT reports are byte-identical to `1de827e`. All **132 protected tracked files** match `d7d77ae`.

Executable probes and logs are under `review_scratch/`. No implementation files were edited.