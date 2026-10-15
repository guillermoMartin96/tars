### F16 — Non-finite intermediate oracle states silently pass O9

**Severity:** Medium  
**Claim:** O9 accepts an invalid intermediate DOP853 reference state. Reductions such as `max(existing_error, NaN)` discard the invalid error before threshold checking.

**Evidence:** Executable mutations `review_scratch/nonfinite_oracle.py` and `review_scratch/nonfinite_integrated.py` replace the reference position and velocity at **650 s** with NaNs:

- Standalone `_evaluate`: `rejected=[]`, `passed=true`.
- Integrated mission Proof: **16 checks passed**, no missing gates.
- An infinity control fails numerically.

Logs: `review_scratch/nonfinite_oracle.log`, `review_scratch/nonfinite_integrated.log`. Committed artifacts remain unchanged.

**Suggested fix:** Validate every independent reference state and computed error for finiteness before reduction. Reject invalid values explicitly. Add intermediate-NaN mutation tests for both acceptance paths.

### F17 — Both loaders accept object-valued limits

**Severity:** Low  
**Claim:** F15’s recursive validation treats dictionaries at metric leaves as containers, allowing non-numeric limits through both loaders.

**Evidence:** `review_scratch/object_limit.py` replaces an M1 position limit and an M2 O9 position limit with `{}`. Both loaders accept them; downstream `Check` and standalone O9 raise an uncaught `TypeError`. This causes a crash, **not a false pass**. Results: `review_scratch/object_limit.log`.

**Suggested fix:** Validate each loader’s nesting structure, then require every metric leaf to be null or a finite, nonnegative number. Add object-valued limit tests.

### Summary

**Verdict: FAIL**, because F16 demonstrates a remaining numerical false pass.

- **F14 resolved:** value edits, unknown missions, deletion, reordering and chain edits are rejected. Each targeted test fails when its rule is disabled.
- **F15’s original exploit resolved:** both loaders reject non-finite, negative and scalar non-numeric limits. Disabling each rule, or either loader’s validation call, fails tests. Object-valued validation remains incomplete under F17.
- All **12 historical records** match committed metadata across the four generations. The consistent re-chain limitation is honestly and consistently documented and reproduced.
- **919 tests passed**, with two expected overflow warnings; Ruff passes.
- M2 Proof **212/212**, M1 Proof, both GMAT comparisons, determinism and golden comparison pass.
- All **18 row mutations** and **47 mandatory audit/O9 threshold deletions** are rejected.
- T5 behavior, loaded baseline thresholds, M1 gates and golden hashes remain unchanged. O9 position limits respect the **11–15 µm floor**; DR-0017/DR-0018 remain separate, thresholds provisional, and no T7 implementation scope was introduced.
- All three reports remain **byte-identical to `1de827e`**. Final snapshot verification found no committed-file changes. Review artifacts are under `review_scratch/`.