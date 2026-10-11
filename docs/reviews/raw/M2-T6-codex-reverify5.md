### F20 — Negative-infinity metrics silently pass

**Severity:** Medium  
**Claim:** `worst`/`worst_of` discard `-inf` beside finite values, and `Check` accepts an unreduced `-inf` metric because it satisfies the upper limit.

**Evidence:** `review_scratch/probes.txt` demonstrates:
- Auxiliary O4/O5 metrics poisoned with `-inf` disappear during merging; all 28 integrated checks pass.
- An O9 sample-position metric poisoned with `-inf` passes standalone evaluation.
- NaN and `+inf` mutations fail correctly.

The affected mechanisms are `m2.py:210–225`, `_merge_audits`, and `thresholds.py:145`.

**Suggested fix:** Reject all non-finite gated metrics before comparison or aggregation. Handle the merge’s initialization sentinel separately. Add standalone and integrated `-inf` regression tests.

### F21 — Static guard misses the original merge vulnerability

**Severity:** Low  
**Claim:** The guard does not reliably detect unsafe metric accumulators.

**Evidence:** `review_scratch/guard_mutation.txt` restores the original F19 expression through an in-memory source mutation:

```python
dst[k] = max(dst.get(k, -math.inf), x)
```

The actual guard test still passes. Its regex also misses dictionary accumulators, reversed arguments, generator reductions and `np.nanmax`. It omits the CLI and thresholds module. Details are in `review_scratch/guard_mutation.log` and `review_scratch/probes.log`.

**Suggested fix:** Use an AST-based guard with explicit reviewed exceptions, and mutation-test detection of these common forms.

### F22 — Node refinement consumes non-finite oracle output without rejection

**Severity:** Medium  
**Claim:** T5 and O9 node-crossing bisection compare unchecked Kepler output with zero. NaN follows the `else` branch; infinities also update the bracket without marking the oracle invalid.

**Evidence:** `review_scratch/node_poison.txt` poisons Kepler results on the final bisection iteration in `m2.orbit_checks` and `gmat_m2._node_crossings`. NaN and ±infinity all pass standalone evaluation and integrated quick checks.

`review_scratch/node_poison_full.txt` repeats the NaN mutation through the full mission path: **all 42 checks pass**, with no missing gates. See `review_scratch/node_poison_full.log`. Vulnerable comparisons are at `m2.py:1881` and `gmat_m2.py:402`.

**Suggested fix:** Validate propagated reference values before each comparison and fail closed on non-finite output. Add standalone and full integrated mutation tests.

### Summary

**Verdict: FAIL**, due to F20 and F22; F21 weakens regression protection.

- **F18 resolved:** original dense-output NaN/±infinity probes fail closed.
- **F19 resolved for NaN:** standalone merging and integrated auxiliary poisoning fail correctly. Disabling either fix makes its targeted regression tests fail.
- All eight required commands pass: **933 tests**, Ruff, both Proof validators, both GMAT comparisons, determinism and golden comparison.
- Previous Proof validator names, results, thresholds and **773 scalar metric bits across 212 checks** are identical. Only top-level `platform` metadata differs.
- All 21 reference-component mutations, 18 row mutations and 47 mandatory threshold deletions reject correctly.
- The reduction/comparison sweep found the issues above; remaining sums and sample-extrema reductions have downstream rejection checks.
- T5 baseline, M1 gates, golden references and loaded limits remain unchanged. O9 position gates respect the 15 µm floor; DR-0017/DR-0018 remain separate, thresholds remain provisional, and no T7 implementation scope appears.
- All three GMAT reports are byte-identical to `1de827e`. All **132 protected tracked files** remain unchanged.

Executable probes and logs are under `review_scratch/`.