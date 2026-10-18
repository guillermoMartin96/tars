| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P9-F1 | **RESOLVED** | Oracle ±∞ injections into either component produce 600 non-finite failures over the grid, or 1 at the designated single sample, plus both coverage failures. Independent `isnan` and `isinf` weakenings exit 1. Review 09’s partial-infinity counterexample also exits 1. |
| M3P9-F2 | **RESOLVED** | Doubled coefficients produce 560 Δi or 504 ΔΩ order failures; reversed signs produce the corresponding sign failures. Independent removal of each component’s order/sign assertion, either whole assertion, and both together exits 1. |
| M3P9-F3 | **RESOLVED — E3/E4 coverage** | Removing E3 or E4 individually exits 1 because the designated finite oracle-error mutant loses that rejection. Their mathematical checks are unchanged. The smallest-step limitation is accurately documented and remains intentional. |

### M3P10-F1 — Caught infrastructure exceptions can count as detection for the intended reason

**Severity:** MINOR  
**Class:** Verification defect  
**Where:** `docs/science/experiments/m3-planning/dr0028_node_signed_mutation_check.py`, `holds()` lines 104–107 and `classify()` lines 642–657.

**Claim:** The classifier does not fully enforce the requirement that infrastructure failures must not count as successful mutation detection.

**Evidence:** A `not_rejected` predicate checks only whether the rejection flag is false:

```python
return out[a][b][FLAGS[a]] is False
```

`mutant_failures()` also sets that flag false when evaluation raises. `classify()` reports the exception but still returns `True`.

I constructed an additional negative control using the committed runner, classifier, baseline check and five existing controls. It retains the order assertion unchanged and inserts an unrelated import failure inside `formula_scaled()`:

```python
if factor == 2.0:
    import review10_missing_dependency
```

The control uses the **same expected predicates as the committed `order_assertion_disabled` mutation**: the two doubled-coefficient mutants must be unrejected. No order assertion is removed.

Reproducer:

```text
TMPDIR="$PWD/review_scratch/tmp" \
  .venv/bin/python review_scratch/infrastructure_control.py
```

Output:

```text
{"verdict": "PASS", "mutations": 1, "detected": 1, ...}
main_return 0
```

Its recorded outcome is:

```text
exit 1, FAIL verdict; expected rejection shown;
M3P9-F2_delta_i_coefficient_doubled raised ModuleNotFoundError:
No module named 'review10_missing_dependency';
M3P9-F2_delta_node_coefficient_doubled raised ModuleNotFoundError:
No module named 'review10_missing_dependency'
```

All five supplied negative controls still report PASS. Thus an unrelated import failure inside a caught built-in-mutant evaluation is accepted as evidence of order-assertion removal. The existing import-failure control covers only an uncaught process-level failure.

I also reproduced this classification with `ZeroDivisionError` inside the order and sign conditions.

Recording a raising built-in mutant as **unrejected**, and making verification fail, is sound. The defect is the subsequent interpretation of that flag as sufficient evidence of the mutation’s intended reason. This does **not** demonstrate a false passing verdict from the committed verification script or invalidate its current mathematical results.

**Suggested resolution:** Distinguish assertion survival from exceptional evaluation in expected-rejection predicates. Reject unrelated caught infrastructure exceptions. Where a mutation intentionally produces a downstream exception, specify and validate that expected outcome narrowly. Add the caught-import-failure negative control.

### M3P10-F2 — The 18 surviving assertion removals remain a documented coverage limitation

**Severity:** NOTE  
**Class:** Optional improvement  
**Where:** `dr0028_node_signed_assertion_sweep.py`; DR-0028 amendment 6, “Assertion-removal sweep”.

**Claim:** The sweep measures individual mutation protection, not the correctness of every active assertion.

**Evidence:** My rerun matches the committed report byte-for-byte:

```text
assertion_sites: 35
detected: 17
survives: 18
exception: 0
```

I inspected every survivor:

- **E1:** finite rotation-deviation bound.
- **E2:** required counterexample presence, unexpected undefined node, finite identity deviation, endpoint classification, endpoint equatorial residual.
- **E5:** equatorial-node classification, sweep non-finite rejection, sweep defined-sample minimum.
- **E6:** numerical-example reproduction and sign agreement.
- **Finite wrapping:** interval, rational reduction, determinism, endpoints, exact equivalents and equivalent-pair coverage.
- **Non-finite wrapping:** rejection of exceptions other than `ValueError`.

These assertions remain present. Some share rejection responsibility with other assertions; others lack a targeted mutant. My independent geometry and wrapping checks found no corresponding current correctness defect.

The documentation accurately records this limitation. I find no basis for turning all 18 survivors into mandatory corrections merely because their individual removals survive. Their scope disposition remains the Tech Lead’s decision.

**Suggested resolution:** No change required by this finding. If broader mutation protection is later authorized, add focused mutants for these properties.

## Summary

**REQUEST_CHANGES** — one MINOR verification defect and one NOTE. The specific review-09 corrections work, but the intended-reason classifier still accepts an unrelated caught infrastructure failure.

Reviewed **detached HEAD `1f1383b0c8e71f532074c0353b62fb099d5852c5`**. The snapshot contains correction commits `03707a8` and `6396141`, followed by the prompt/erratum commits. Tracked worktree status remained clean.

Verified independently:

- **Verification and preservation:** Executed current scratch copies twice through the real entrypoint; both exit 0, with byte-identical JSON. Independently executed `faba9d6` and recursively compared every pre-existing output value: **none changed**. AST comparison identifies only `EXACT_MUTANTS`, `by_formula_test` and `main` as changed existing top-level definitions. Oracle, formulas, wrapping, grid, tolerances, checks and minima are unchanged.
- **Coverage:** Recomputed **506/532 order samples** and **560/504 sign checks**, each equal to its separately enforced minimum. Independent enumeration confirms the sign zero sets exclude 40 and 96 of 600 series. Order minima preserve existing coverage; measured nearest gate ratios remain safely separated from the documented rounding allowance.
- **Mutation suite:** Ran `dr0028_node_signed_mutation_check.py` twice with scratch output paths. Both report **109/109 detected**, no vacuous expectation and **5/5 controls correctly classified**; outputs are byte-identical and match the committed report. Finding F1 identifies a limitation beyond those supplied controls.
- **Injection coverage:** Checked both oracle components, both infinities, whole-grid and single-sample corruption. Independently weakened the oracle guard to `isnan` and `isinf`. All required cases exit nonzero. The reconstructed 60-case matrix matches the structure described in review 09; exact historical scratch-file equivalence cannot be established because those files were not retained.
- **Order/sign protection:** Independently disabled all four component-specific assertions, both whole assertions, and order/sign together. All exit 1. Doubled and halved coefficients produce **560/504 order failures with zero sign failures**; reversed signs produce **560/504 sign failures**. Review 09’s disabled-order/doubled-coefficient counterexample now exits 1.
- **Exact-property protection:** E3 and E4 removals are detected independently. The assertion sweep reproduces **35/17/18**, with no exceptions.
- **Mathematics:** Independently derived
  \[
  h_B=h_A-\delta(e\times h_A)+O(\delta^2),
  \quad
  \Delta i=-\delta\cos(\Omega-\phi),
  \quad
  \Delta\Omega=\delta\cot i\sin(\Omega-\phi).
  \]
  For the line-of-nodes case, \(h_B=\sin(i-\delta)u+\cos(i-\delta)\hat z\), yielding the three open regimes, two singular endpoints and node reversal. The perpendicular-axis closed form and spherical inclination bound also agree.
- **Independent numerical checks:** A separate conjugated-Cartesian rotation implementation checked **20,000 cases**. Maximum discrepancies were **4.44×10⁻¹⁶** for rotation, **8.88×10⁻¹⁶** for line-of-nodes inclination and **1.33×10⁻¹⁵** for the closed-form node change; no inclination-bound excess occurred. Central finite differences independently confirmed both signed derivatives. **99,938 finite binary64 inputs** matched exact rational wrapping, including the canonical interval.
- **Preserved examples:** Recomputed \(i=2^\circ,\delta=5^\circ\) as **Δi≈+1°, ΔΩ=180°**. Review 04’s example gives **ΔΩ=+0.259805543688°**, **Δi=+0.000340085438°**.
- **Research reruns:** Sensitivity and Q10 residual-consequence outputs reproduce byte-for-byte.
- **History and authorization:** Read the review records/raw findings and DR-0028 amendment chain. All 18 earlier record/raw-output files remain unchanged or append-only against `faba9d6`. Earlier corrections and their dispositions remain recorded. Superseded mathematical statements retain correction pointers. J-ax-1, the identity transformation, atmospheric co-rotation, historical SCI-0005/VAL-0007 corrections and scope restrictions remain intact.
- **Diff integrity:** Whole-branch changes are exclusively under `docs/`. `src/`, `tests/`, `toolbox/`, `scenarios/` and `proof/` are unchanged from `d92ab89`. DR-0024…0027 and ADR-0009 are unchanged since `faba9d6`. Registers retain every baseline line, with **218/0** and **43/0** additions/deletions. Targeted document removals are status/index rows only. Scoped Ruff lint/format, relative-link checks and `git diff --check` pass.

Preservation commands completed using `PYTHONPATH=src` and the supplied environment:

```text
toolbox/validators/m1_proof.py --out review_scratch/m1.json
toolbox/validators/m2_proof.py --out review_scratch/m2_proof.json
toolbox/scripts/gmat_m1.py compare
toolbox/scripts/gmat_m2.py compare
toolbox/scripts/reference_snapshot.py verify-baseline \
  toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz
toolbox/validators/cross_platform.py
toolbox/validators/determinism.py
toolbox/validators/determinism.py --scenario <each of four m2_*.json scenarios>
```

All exited 0: **M1 Proof 7/7; full M2 validator 228/228**, both committed-reference GMAT comparisons, snapshot baseline verification, local cross-platform validation and all five determinism runs.

**Partial/unavailable validation:** Full pytest was deliberately interrupted after **290 passed in 288.15 seconds**, exit 2; it is not a completed suite. Complete Proof wrappers, fresh GMAT executable runs and three-platform execution were not rerun. GitHub API access failed, so the reported CI run and individual job conclusions remain independently unverified. External source bytes/digests were not freshly retrieved.

Remaining gates are unchanged:

- **T0:** explicit planning acceptance, merge/T0 authorization and successful planning merge.
- **T1:** T0 evidence and independent review, applicable checkpoint decisions and separate authorization.
- **T2:** additionally, owner decisions on DR-0027 **A-4/A-5/A-6/A-s/B-4**.
- **Q-G2-1/5/7 and Q9 values** remain deferred to the T0 checkpoint; **Q-G2-6** to T4. Numerical thresholds require a later measured-evidence DR. **Q-G3-7** remains NOT AUTHORIZED.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence until M3P10-F1 is resolved.**

No planning files or production code were corrected, nothing was merged, and T0/T1/T2 remain unstarted.
