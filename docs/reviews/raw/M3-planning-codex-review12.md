| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P11-F1 | **NOT RESOLVED** | The reassociated fallback is correctly rejected now, but a first-step-only oracle defect is certified as an all-steps defect. See M3P12-F1. |
| M3P11-F2 | **NOT RESOLVED** | All five requested reclassifications have meaningful protection. However, the remaining E6-sign redundancy argument has a counterexample. See M3P12-F2. |
| M3P10-F1 | **NOT RESOLVED** | Historical exception counterexamples are handled correctly, but the broader intended-reason detection guarantee remains unsound through M3P12-F1. |
| M3P10-F2 | **NOT RESOLVED** | The inventory is correct, but its classification still incorrectly treats E6-sign as redundant. |

### M3P12-F1 — Oracle observation misses absent defects after the first invalid step

**Severity:** MINOR  
**Class:** Unsound verification claim  
**Where:** `dr0028_node_signed_mutation_check.py`, `observe_oracle_values()`; verification script, `check_formulas()`; DR-0028 amendment 8, exercise criterion.

**Claim:** The oracle-value probe can establish an all-steps defect when the injected value is wrong only at the first step.

**Evidence:** Amendment 8 requires the intended defect to be “never missing.” However, the probe observes values only when `nonfinite_reason()` runs. After the first invalid value, this condition skips subsequent validation for that component:

```python
if errs[name] is None:
    continue
```

I supplied the existing `review09_oracle_delta_i_nan_first_step` edit while claiming the exercise predicate and expected rejection of `review09_oracle_delta_i_nan_all`. I repeated this for ΔΩ.

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  review_scratch/oracle_partial_counterexample.py
```

Results for **each** component:

```text
classification: expected rejection
probe: intended=600, missing=0, unintended=0
actual oracle component values:
    nonfinite=600
    finite=2400
```

Independent tracing observed every constructed oracle-value dictionary. Thus 2,400 subsequent values lack the claimed defect, but none is recorded as missing.

I also ran the full harness entrypoint with this single falsely described mutation, retaining all 23 controls:

```text
TMPDIR="$PWD/review_scratch" PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python review_scratch/oracle_partial_entrypoint.py
```

Output:

```text
main_return 0
verdict: PASS
mutations_attempted: 1
validly_exercised: 1
detected_for_intended_reason: 1
controls_with_declared_outcome: 23 / 23
```

No recorder, result flag, exception record or output JSON was forged.

**Concrete risk:** The harness cannot distinguish these partial and all-steps oracle injections. Its `missing=0` evidence depends on the tested validation path discarding samples, so it can certify a stronger defect-exercise claim than it observed. The committed mathematical results are unaffected.

**Suggested resolution:** Observe every oracle value before discarded-series logic can hide it, and independently enforce the expected input schedule and observation coverage. Add first-step-only injections claimed as all-steps injections as negative controls for both components.

### M3P12-F2 — E6-sign independently protects the formula at the preserved example

**Severity:** MINOR  
**Class:** Unsound verification claim  
**Where:** `dr0028_node_signed_assertion_classification.py`, `premises_e6_sign()` and E6-sign entry; DR-0028 amendment 8, category B argument.

**Claim:** E3 protects the oracle’s sign at the review-04 example, but does not protect the analytical formula’s sign there. The first-order grid checks a different set of tilt values.

**Evidence:** E6-sign asserts both:

```python
d_node > 0.0 and lin_node > 0.0
```

The redundancy premise establishes protection for `d_node`. Its argument for `lin_node` overlooks the different tilt samples.

In a scratch copy, I replaced the node formula with:

```python
(1.0 if not (0.0026 < abs(delta) < 0.0027) else -1.0) \
    * delta / math.tan(inc) * math.sin(node - phi)
```

This reverses its sign throughout a finite tilt interval, for all inclinations, nodes, azimuths and both tilt signs. The interval contains the preserved example’s `0.15° = 0.00261799… rad`, but contains no first-order grid step.

Commands:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  review_scratch/e6_counterexample.py

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  review_scratch/e6_entrypoints.py
```

Actual verification entrypoint results:

```text
E6-sign present:
    exit 1, verdict FAIL
    exact failures: ["E6 review-04 example sign disagreement"]
    formula failures: []

Only E6-sign removed:
    exit 0, verdict PASS
    exact failures: []
    formula failures: []
```

Both runs preserve order coverage **506/532**, sign coverage **560/504**, and successful built-in defect exercise. The oracle remains correct; E3 reports nothing.

**Concrete risk:** Removing E6-sign permits a wrong formula sign at an explicitly protected example to pass the complete verification script. Its category B classification and claimed equivalent protection are therefore false.

This does not require broadening the intentionally asymptotic order test. E6-sign already protects this additional sample.

**Suggested resolution:** Treat E6-sign as independently important and add targeted formula-defect protection, or establish genuinely equivalent protection at the same example. Correct the classification totals and dependency claims through the authorized amendment process.

## Summary

**REQUEST_CHANGES** — two MINOR unsound verification claims. No current mathematical-result defect, production change or M1/M2 baseline change was found.

Reviewed detached HEAD **`5b12eece4d952450fc47a13c75059ef748fc007e`**, parent `bd6c8b4`.

Independently verified:

- **Historical counterexample:** `review_scratch/fallback_repro.py` reconstructs the suppressed-import/reassociated fallback using files read from git. With the order assertion intact, `c16b3b5` classifies it as `expected rejection`; HEAD classifies it as `invalid mutation setup`.
- **Regression demonstration:** `dr0028_node_signed_harness_regression.py` reproduces all five M3P10-F1 and four M3P11-F1 historical failures. All 23 corrected controls receive their declared category and exercise result.
- **Mutation suite:** `dr0028_node_signed_mutation_check.py` completes with the committed output reproduced byte-for-byte: **109 attempted, 109 reported exercised, 109 reported detected**, 23/23 controls; all other classification counts zero; **0/77** direct predicates met at baseline. M3P12-F1 demonstrates a limitation beyond those controls.
- **Exception handling:** Rechecked the named wrap-guard and order-estimate allowances and their type/message/stack matching. Wrong-location and wrong-type controls are rejected. An additional probe-only import failure is classified as invalid mutation setup, not detection.
- **Assertion inventory:** Classification reproduces **35 assertion sites**, the same **18 historical survivors**, and reported totals **11 A / 4 B / 3 C**. Sweep reproduces **28 detected / 7 surviving / 0 exceptions**.
- **All 11 existing A demonstrations:** Each genuinely exercises its declared defect without exception, fails with its assertion present, and leaves zero exact/wrapping failures after that assertion alone is removed. This includes all five new protections.
- **Remaining classifications:** W1, W4 and E6-value have adequate redundancy arguments within the documented deterministic scope. W3, W6 and E2a have reasonable diagnostic rationales. E6-sign is disputed above.
- **Numerical preservation:** Ran `dr0028_node_signed_verification.py` twice: byte-identical outputs matching committed evidence. Independently executed `cadccd8`: **zero changed or removed pre-existing values; 315 added keys**. AST comparisons confirm unchanged oracle, formulas, wrapping, grid, checks, tolerances and minima.
- **Coverage and regressions:** Order **506/532** and sign **560/504** remain separately enforced. The 1% Δi oracle mutant still produces **one E3 and one E4 failure**. The mutation suite exercises component-specific sign/order removals and nonfinite rejection.
- **Independent mathematics:** Separate conjugated Cartesian rotations checked **10,000 cases**, with maximum oracle disagreement **1.78×10⁻¹⁵ rad** and no inclination-bound excess. Central differences confirm both signed derivatives. Reproduced ΔΩ **+0.259805543688°** and the crossing result **Δi≈+1°, ΔΩ=180°**. **9,997 finite random binary64 inputs** matched independent rational wrapping.
- **Research evidence:** Sensitivity and atmosphere-residual outputs reproduce byte-for-byte. Independently recomputed all **27 density jumps**, maximum disagreement **1.11×10⁻¹⁶**; lowest-band ratio **1.0013804525694443**.
- **History and scope:** Read reviews 01–11 and the full DR-0028 amendment chain. All prior record/raw-output contents remain preserved against `cadccd8`. I-1 through I-10 remain identical in the new prompt. All **78 whole-branch changed files**, including this prompt, are under `docs/`. Protected implementation/evidence paths are unchanged. Registers retain every baseline line, with **218/0** and **43/0** additions/deletions. Scoped Ruff and relative-path checks pass.

Completed preservation commands, using the supplied environment and `PYTHONPATH=src`:

```text
toolbox/validators/m1_proof.py --out review_scratch/m1.json
toolbox/validators/m2_proof.py --out review_scratch/m2.json
toolbox/scripts/gmat_m1.py compare
toolbox/scripts/gmat_m2.py compare
toolbox/scripts/reference_snapshot.py verify-baseline \
  toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz
toolbox/validators/cross_platform.py
toolbox/validators/m2_cross_platform.py collect --out review_scratch/m2_platform.json
toolbox/validators/determinism.py
toolbox/validators/determinism.py --scenario <each of four M2 scenarios>
```

All completed successfully: standalone M1 validator **7/7**, full standalone M2 validator **228/228** without `--quick`, both committed-reference GMAT comparisons, snapshot verification, local cross-platform checks and five determinism runs. Focused pytest completed **21 passed**.

**Validation limits:** These are complete standalone validator executions, not complete Proof-wrapper executions. The full Proof wrappers and full pytest suite were not rerun. Fresh GMAT executable runs, external-source retrieval and three-platform execution were not performed. GitHub API access failed for run `39075007905`; its reported individual CI conclusions remain independently unverified.

Remaining gates are unchanged:

- **T0:** explicit planning acceptance, separate merge/T0 authorization and successful planning merge.
- **T1:** T0 evidence, independent review, applicable checkpoint decisions and separate authorization.
- **T2:** additionally, owner resolution of DR-0027 **A-4/A-5/A-6/A-s/B-4**.
- **Q-G2-1/5/7 and Q9 values** remain deferred to the T0 checkpoint; **Q-G2-6** to T4; numerical thresholds require a later measured-evidence DR. **Q-G3-7** remains NOT AUTHORIZED.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence.**

No reviewed files were fixed, nothing was merged, and no M3 implementation or T0/T1/T2 work began.
