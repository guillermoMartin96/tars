### F23 — Infinite Simpson allowances turn failing errors into zero

**Severity:** Medium  
**Claim:** The root fix misses non-finite allowances before clamping. At `m2.py:718` and `:1633`, `max(err - inf, 0.0)` becomes zero, so `worst` and `Check` receive a finite passing metric. Both AST allowlist justifications overlook this case.

**Evidence:** `review_scratch/simpson_full.py` increases sensed delta-v by `1e-6 m/s`, keeping bookkeeping consistent. With the normal allowance, standalone evaluation and full-mission checks reject it. With `simpson_bound` returning `+inf`, standalone O9 passes and **all 42 full-mission checks pass**, without missing gates. See `simpson_full.log`. The excess metric changes from approximately `3.41579e-8`—above its `1e-12` limit—to zero.

**Suggested fix:** Validate each allowance before subtraction or clamping. Convert non-finite allowances into an explicit failure. Correct both allowlist justifications and add standalone and integrated regression tests.

### F24 — AST guard misses NumPy ufunc reductions

**Severity:** Low  
**Claim:** F21’s original examples are detected, but relevant max/min forms remain unguarded. The visitor examines the final callable name, so `.reduce()` hides the reducer.

**Evidence:** `review_scratch/guard_mutation.py` runs the actual guard against mutations using `np.maximum.reduce`, `np.minimum.reduce`, `np.fmax.reduce`, `np.fmin.reduce`, and `np.maximum(a, b)`. All pass unnoticed.

More directly, replacing the auxiliary merge with `np.fmax.reduce([dst.get(k, -math.inf), x])` passes the guard and hides a poisoned NaN: the merged metric remains `0.1`. See `guard_mutation.log`.

**Suggested fix:** Recognize the underlying ufunc in reduction calls and include `maximum`/`minimum`. Mutation-test these forms through the actual allowlist test.

### F25 — Integrated node regression test survives disabling its fix

**Severity:** Low  
**Claim:** The integrated node test does not reliably establish that the new finiteness checks caused rejection.

**Evidence:** `review_scratch/disable_tests.py` disables both node finiteness checks in memory. `test_poisoned_node_oracle_fails_the_integrated_mission` **still passes**. Its global every-80th-call poisoning and broad failure assertion are insufficiently targeted. The standalone tests correctly fail when either mechanism is disabled independently. See `disable_tests.log`.

**Suggested fix:** Target a known bisection iteration in each validator and assert the corresponding non-finite timing metric. Require the integrated test to fail when those checks are disabled.

### Summary

**Verdict: FAIL**, because F23 demonstrates a remaining acceptance false pass.

- **F20 resolved:** NaN and ±infinity reject through Check, auxiliary merging, and standalone O9. Disabling the relevant mechanisms breaks their targeted tests.
- **F21 partially resolved:** the original F19 expression and five tested forms are detected; F24 remains.
- **F22 resolved for the consumed node coordinate:** NaN and ±infinity reject in standalone and full-mission probes. F25 weakens integrated regression protection.
- All eight required commands pass: **947 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism, and cross-platform validation.
- Previous M2 results, thresholds, and **773 metric bits across 212 checks** are identical. The complete report differs in top-level `platform` metadata.
- All 21 reference-component mutations, 18 row mutations, and 47 mandatory threshold deletions reject.
- T5 baseline, M1 gates/results, golden hashes, and loaded limits remain unchanged. New O9 trajectory-position tolerances respect the 15 µm floor. DR-0017/DR-0018 remain separate; thresholds remain provisional; no T7 implementation scope appears.
- All three GMAT reports are byte-identical to `1de827e`; all **132 protected tracked files** remain unchanged.
- Report-only metrics can still contain non-finite values without failing a check. Node bisection validates the consumed `z` coordinate, rather than every returned vector component.

Executable probes and logs are under `review_scratch/`.