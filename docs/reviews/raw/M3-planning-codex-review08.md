| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P7-F1 | **RESOLVED** | The `wrap()` docstring and DR-0028 amendment 4 explicitly restrict the contract to finite floats. Both NaN signs and ±∞ raise the guard’s `ValueError`. Independently checked 249,901 finite inputs against `f999626` bit-for-bit and against exact rational reduction: zero differences. Both ±π map to +π. |

### M3P8-F1 — Non-finite inclination predictions can pass the signed verification

**Severity:** MINOR  
**Category:** Verification adequacy  
**Where:** `docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`, `check_formulas()` lines 208–244; overall verdict lines 651–655.

**Claim:** The script can return PASS when the inclination formula produces NaN for every valid input.

**Evidence:** Order checks run only when both errors satisfy `>= tol`; sign checks similarly require `abs(lin) >= tol`. Comparisons with NaN are false, so these checks silently skip the defective component. The verdict requires no failures but does not require nonzero per-component coverage.

In a scratch copy, I replaced only the formula under test with:

```python
def formulas_amendment2(inc, node, phi, delta):
    return math.nan, delta / math.tan(inc) * math.sin(node - phi)
```

Running `.venv/bin/python review_scratch/nan_probe.py` produced:

```text
exit 0
verdict PASS
order_samples_delta_i: 0
order_samples_delta_node: 532
observed_order_delta_i_min_max: None
sign_checks: 504
failures: []
mutants rejected True
```

The report also contains NaN for the review-04 first-order inclination prediction. Thus an entirely invalid inclination formula passes despite all built-in mutants remaining rejected.

**Suggested resolution:** Reject non-finite oracle results, formula results and errors before conditional comparisons. Require justified minimum coverage for each formula component. Add a mutant returning NaN for inclination and require exit 1. Preserve the current numerical tolerances and historical evidence.

## Summary

**REQUEST_CHANGES** — one new MINOR finding. M3P7-F1 is resolved.

Reviewed detached HEAD: `491ef7740643ab2c0008db593fd00c20ee2cc906`. Correction commit: `cf9f3d6252998c10e2e6c03d0cffe4e045360a48`; HEAD adds only the review prompt.

Verified independently:

- **Wrapping:** `.venv/bin/python review_scratch/review.py` checked random binary64 patterns, ±π, signed zeros, normal/subnormal extremes and ±maximum finite values. All 249,901 finite inputs matched the previous implementation and rational reduction. The fmod/Sterbenz argument is sound for this finite domain.
- **Determinism and regression:** Two signed-script runs produced byte-identical JSON and stdout; output matches the committed result. Every previously existing JSON value and earlier mutant failure count remains unchanged.
- **Requested mutations:** Removing the guard, weakening its test to type-only, disabling non-finite tests, restoring either historical defect, deleting E5a/E5b/E5c separately, and reversing either formula sign each exited 1.
- **Mathematics:** Independently derived the signed formulas, five line-of-nodes regimes, endpoint singularities, node reversal, perpendicular-axis closed form and inclination bound. An independent conjugated-Cartesian-rotation implementation checked 20,000 cases: maximum matrix discrepancy `4.44e−16`, closed-form discrepancy `1.14e−15`, and no inclination-bound excess. Reproduced the `i=2°, δ=5°` counterexample as `Δi=+1°, ΔΩ=180°`. Reviewed the tolerance derivations; the new finding concerns skipped checks, not tolerance size.
- **Research evidence:** Reran the sensitivity and Q10 residual scripts; both outputs were byte-identical. Recomputed all 27 atmosphere jumps within `1.11e−16`.
- **History and scope:** Review records/raw outputs 01–07 remain unchanged or append-only against `0dac6d3`. The withdrawn Q4 quotation retains its exact 558 bytes. Baseline register lines remain unchanged and ordered: **218/0** and **43/0** additions/deletions. DR-0024…0027, ADR-0009, constants, digests and protected M1/M2 paths are unchanged by this correction. The whole-branch diff remains under `docs/`.
- **Preservation gates:** `m1_proof.py --out review_scratch/m1.json` passed **7/7**; `m2_proof.py --out review_scratch/m2.json`, without `--quick`, passed **228/228**. Both GMAT `compare` commands, snapshot `verify-baseline`, local cross-platform golden check, and M1 plus all four M2 determinism checks passed. Golden position/velocity differences were zero.
- **Other checks:** Ruff lint/format passed. Checked relative Markdown targets had no broken paths. `git diff --check` reported two Markdown hard-break lines; disabling end-of-line whitespace checking passed.
- **Partial/unavailable:** Full pytest was interrupted after **256 passed**; this is not a completed full-suite run. Complete Proof wrapper scripts and three-platform execution were not rerun. GitHub API access failed, so reported CI success remains independently unverified. External source bytes and source digests were not freshly retrieved.

Remaining gates retain their status:

- **T0:** Planning acceptance, separate merge/T0 authorization, and the planning merge.
- **T1:** T0 evidence and independent review, applicable checkpoint decisions, and separate authorization.
- **T2:** Additionally, owner decisions on DR-0027 A-4/A-5/A-6/A-s/B-4 and applicable T0 deferrals.
- Q-G2-1/5/7 and Q9 values remain deferred to the T0 checkpoint; Q-G2-6 to T4; numerical thresholds to a later measured-evidence DR. Q-G3-7 and the stated implementation exclusions remain NOT AUTHORIZED.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence until M3P8-F1 is resolved.**

No fixes, merge, or M3 implementation occurred. Tracked working-tree status remains clean.