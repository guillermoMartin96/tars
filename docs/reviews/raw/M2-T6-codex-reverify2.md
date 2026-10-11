### F14 — Historical manifest records remain unchecked
**Severity:** Medium  
**Claim:** F8 fixes metadata binding and latest-record consistency, but older replacement history can still be corrupted or erased without rejection.

**Evidence:** `review_scratch/extra.py` independently:

- changed an older record to a 1900 timestamp, zero revision, null reason and invalid digest;
- appended an unknown mission with null history values;
- deleted all superseded records.

Each `_evaluate` returned `rejected=[]`, `passed=true`. Results: `review_scratch/extra2.log`. `history_problems` validates record keys, then compares only the latest mission record.

VAL-0014 therefore overstates detection of history substitution. The README also still records two replacements, whereas the review record documents a third.

**Suggested fix:** Validate every history record’s values, mission and chronology. Define and enforce history-preservation semantics, with an independent reviewed anchor if deletion must be detectable. Correct the documentation.

### F15 — Non-finite thresholds silently disable numerical gates
**Severity:** Medium  
**Claim:** The shared threshold loader accepts an overflowing JSON number as infinity, allowing a present but ineffective O9 gate.

**Evidence:** `review_scratch/infinite_limit.py` introduced a 1 m position error into a burn row and consistently updated its metadata and manifest digests.

- With the committed limit: rejected numerically, `1 > 3e-05`.
- With only `gmat_vs_dop853_position_error_max_m` changed to valid JSON number `1e999`: `_evaluate` returned no rejection and a passing check.

Results: `review_scratch/infinite_limit.log`. `load_scoped_thresholds` checks names, scopes and status, but not numerical limit validity. This is an existing shared-loader weakness exposed by the T6 acceptance path.

**Suggested fix:** Require every non-null threshold to be a finite, nonnegative number. Add an overflow-value mutation test.

### Summary

**Verdict: FAIL.** The committed numerical evidence passes; two demonstrated acceptance gaps remain.

F8–F13 status:

- **F8:** Partially resolved. Metadata binding and latest-history consistency work; historical-record validation remains incomplete under F14.
- **F9:** Resolved. Publication interruption probes reject partial replacements.
- **F10:** Resolved. Substituted reproduction executables are rejected; three authenticated GMAT reproductions pass.
- **F11:** Resolved. Symlinked previews are rejected without changing their targets.
- **F12:** Resolved. Both corrupted audit metrics and every mandatory audit-threshold deletion are rejected.
- **F13:** Resolved. Same-tick boundary coverage follows the reporting rule.

Disabling each fix causes its targeted tests to fail, including separate F8 digest and history controls.

Verified:

- Full suite: **905 passed**, two expected overflow warnings.
- T6 suite: **76 passed**.
- Ruff lint and formatting pass.
- M2 Proof: **212/212 passed**; M1 Proof passes.
- Both GMAT comparisons, determinism and golden comparison pass.
- All **18 row mutations** and **15 missing O9 threshold probes** are rejected.
- All three reports are directly confirmed **byte-identical to `1de827e`** through the original worktree’s Git history.
- T5 behavior is preserved; the report-only rule moved unchanged into `tars.validation.m2`.
- M1 thresholds and golden artifacts remain unchanged.
- DOP853 position limits remain **30 µm**, above the **11–15 µm** floor.
- DR-0017 and DR-0018 remain separate; thresholds remain provisional; no T7 implementation scope was introduced.
- Reproduction wording correctly distinguishes reproducibility from proof of historical origin, subject to F14’s history-documentation corrections.
- Snapshot integrity check reports **no tracked-file changes**. Review artifacts are under `review_scratch/`.