### F18 — Non-finite DOP853 dense output silently passes

**Severity:** Medium  
**Claim:** `dop853_reference` validates `sol.y`, but not `sol.sol(ticks)`. NaN dense-output positions produce NaN altitude extrema, which the remaining `min`/`max` reductions silently discard.

**Evidence:** `review_scratch/hazards.py` poisons dense-output positions on the initial `[0, 60]` coast segment while retaining finite integration states. Standalone O9 returns `rejected=[]`, `passed=True`; integrated mission Proof reports no failed checks or missing gates. See `review_scratch/hazards.log`. The vulnerable reductions are at `src/tars/validation/m2.py:919–921`.

**Suggested fix:** Validate every dense-output component and derived altitude before reduction. Add standalone and integrated mutation tests for non-finite dense output.

### F19 — Auxiliary-audit merging discards failing O4/O5 metrics

**Severity:** Medium  
**Claim:** `_merge_audits` still uses builtin `max`, allowing an auxiliary run’s NaN metric to disappear before threshold evaluation.

**Evidence:** `review_scratch/hazards.py` demonstrates that a NaN O4 metric fails individually but passes after merging. `review_scratch/merge_integrated.py` injects NaN O4 sample-position and O5 coast-position errors into the actual `dt=2.5` auxiliary audit. All **42 integrated mission checks pass**, with no missing gates. See `review_scratch/merge_integrated.log`. The vulnerable reduction is `toolbox/validators/m2_proof.py:118`.

**Suggested fix:** Use the NaN-safe reduction when merging, or gate each auxiliary audit before aggregation. Add integrated O4/O5 merge mutation tests.

### Summary

**Verdict: FAIL**, due to F18–F19.

- **F16:** Original standalone and integrated intermediate-state probes now fail closed. Dense-output coverage remains incomplete under F18.
- **F17:** Object-valued leaves and structurally wrong limits are rejected.
- Disabling each of eight fix mechanisms makes its targeted test fail.
- T5 corrections preserve finite behavior and do not loosen gates. Across **212 checks, all 773 scalar metric values are bit-identical** to the supplied previous report; thresholds, statuses and pass results are unchanged. The renamed contract check is consumed consistently, and check names are unique.
- O9 rejects all 21 reference-component NaN/±infinity mutations. O5 rejects NaN Kepler outputs. All 18 row mutations and 47 mandatory threshold deletions are rejected.
- **All eight required commands pass:** 928 tests, Ruff, both Proof validators, both GMAT comparisons, determinism and golden comparison.
- T5 baseline, M1 gates, golden bytes and loaded limits remain unchanged. O9 position tolerances respect the 11–15 µm floor; DR-0017/DR-0018 remain separate, thresholds remain provisional, and no T7 implementation scope was introduced.
- All three GMAT reports are byte-identical to `1de827e`. All 132 protected tracked files remain unchanged. Evidence is under `review_scratch/`.