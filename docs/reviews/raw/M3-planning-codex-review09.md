| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P8-F1 | **RESOLVED** | The current finite-value guard rejects invalid oracle and formula values, discards their series from coverage, and enforces four separate minima. My 60 independent formula/oracle injection cases—including partial injections—each exited 1 through the entrypoint and returned failures from `check_formulas()`. Regression-protection gaps are reported separately below. |

### M3P9-F1 — Oracle infinity rejection lacks regression protection

**Severity:** MINOR  
**Class:** Verification defect  
**Where:** `docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`, `nonfinite_reason()` and `FORMULA_DEFECT_MUTANTS`.

**Claim:** The regression suite permits weakening oracle validation so infinities can again satisfy coverage and escape the comparisons.

**Evidence:** In an independent scratch copy, I changed only:

```python
if num is None or not math.isfinite(num):
```

to:

```python
if num is None or math.isnan(num):
```

The script exited **0**, verdict **PASS**. Oracle defect mutants exercise NaN, but neither infinity.

I then injected signed infinity into the inclination oracle for only `i=30°`, `Ω=φ=0°`, preserving the numerical result’s sign:

```python
if inc == math.radians(30) and node == 0 and phi == 0:
    a = math.copysign(math.inf, a)
```

Results:

```text
Current guard + partial infinity:  exit 1, FAIL
Weakened guard alone:             exit 0, PASS
Weakened guard + partial infinity: exit 0, PASS
Inclination order samples:        508
Inclination observed-order range: [NaN, NaN]
Formula failures:                 []
```

Thus invalid samples can count towards coverage after a weakening that the new regression protection does not detect.

Reproducer: `.venv/bin/python review_scratch/oracle_inf_gap.py`.

**Suggested resolution:** Add oracle ±∞ mutants for both components, requiring designated non-finite failures and exclusion from coverage. Include an entrypoint mutation weakening the oracle check to `isnan()`.

### M3P9-F2 — Order and sign assertions can independently disappear without rejection

**Severity:** MINOR  
**Class:** Verification defect  
**Where:** `dr0028_node_signed_verification.py`, `check_formulas()` lines 301–316 and the formula-mutant acceptance checks; `dr0028_node_signed_mutation_check.py`.

**Claim:** Coverage remains satisfied when the corresponding assertion is disabled, and existing mutants do not require rejection by that specific assertion.

**Evidence:** Independently replacing either condition with `if False:` produced exit **0**, verdict **PASS**:

```python
if p < P_MIN:
if (n > 0.0) != (lin_v > 0.0):
```

Disabling each assertion separately for only `delta_i` or only `delta_node` also passed—all four component-specific mutations.

With the order assertion disabled, I doubled both analytical coefficients:

```python
return (
    -2 * delta * math.cos(node - phi),
    2 * delta / math.tan(inc) * math.sin(node - phi),
)
```

The entrypoint still reported:

```text
exit:                     0
verdict:                  PASS
order samples:            596 inclination, 556 node
minimum observed orders:  0.994842916318, 0.973647187295
sign checks:              560 inclination, 504 node
formula failures:         []
```

These incorrect coefficients leave first-order errors, but the disabled assertion is not detected. Sign-reversed mutants remain rejected by sign checks; conversely, order checks conceal a missing sign assertion.

Reproducers:

```text
.venv/bin/python review_scratch/review09.py
.venv/bin/python review_scratch/extra_probes.py
```

**Suggested resolution:** Require designated order failures from same-sign coefficient-error mutants and designated sign failures from sign-reversal mutants, separately for each component. Add independent assertion-removal mutations.

### M3P9-F3 — Additional limits of the finite verification

**Severity:** NOTE  
**Class:** Optional improvement  
**Where:** `dr0028_node_signed_verification.py`, first-order checks and E3/E4 mutation protection.

**Claim:** The current evidence establishes narrower properties than arbitrary finite-output correctness or protection against removal of every assertion.

**Evidence:** Additional independent mutations produced exit **0**, verdict **PASS**:

- Returning `(100.0, 100.0)` at the first three halving steps while retaining the formulas at the final two. Only the final two errors determine order; only the final step determines sign.
- Disabling E3’s finite-deviation assertion.
- Disabling E4’s inclination-bound assertion.

These are distinct from non-finite rejection. The coarse-step mutation leaves the tested asymptotic behavior intact; the E3/E4 mutations expose optional additional mutation coverage.

**Suggested resolution:** No additional acceptance requirement is proposed here. Keep these limitations explicit; add protection if broader claims are intended.

## Summary

**REQUEST_CHANGES** — two MINOR verification findings and one NOTE. The committed formulas and current finite-value guard are correct; regression protection remains incomplete.

Reviewed detached HEAD: `5515a7a25431f01ccfb7be00b62bcaa91e83859a`. Correction commits: `1208090` and `ff08ef9`.

Verified independently:

- **Injection tests:** 42 formula-path and 18 oracle-path cases covered NaN and both infinities, through the entrypoint and `check_formulas()`. Partial cases included selected steps, individual series, one tilt sign, near-equatorial and near-polar subsets. All 60 entrypoint cases exited 1; all direct calls returned failures.
- **Determinism and preservation:** Two baseline runs were byte-identical. Recursive comparison against independently executed `0ac630b` found exactly one changed pre-existing value: `cos_sin_swapped/failing_checks`, **1576→1578**. Other differences were added keys. AST comparisons confirmed unchanged oracle, formulas, wrapping, noise calculation and step scale; grid and tolerance output remained identical.
- **Coverage:** Independently recomputed **506/532 order samples** and **560/504 sign checks**. Exact sign zero sets exclude **40/96** of the 600 series. The four minima are enforced separately. Independently calculated nearest order-gate ratios were approximately **1.012333/0.993963** and **1.549770/0.495320**. Their margins exceed the documented `0.001` rounding allowance; no existing coverage was reduced.
- **Committed mutation harness:** Ran twice; outputs were byte-identical and matched the committed result: **33/33 detected**. The E2/E5b `ValueError` outcomes are acceptable: they terminate nonzero, are accurately identified as exceptions, and are never reported as a passing verification verdict.
- **Mathematics:** Independently derived the signed formulas from `h_B=h_A−δ(e×h_A)`, the five line-of-nodes regimes, endpoint singularities, node reversal, perpendicular-axis closed form and spherical inclination bound. A separate conjugated-Cartesian rotation implementation checked **20,000 cases**: maximum matrix discrepancy **3.33×10⁻¹⁶**, identity discrepancy **6.66×10⁻¹⁶**, closed-form discrepancy **3.18×10⁻¹⁵**, and no inclination-bound excess. **99,955 finite binary64 inputs** matched independent exact rational wrapping.
- **Research reruns:** Sensitivity and Q10 residual-consequence outputs reproduced byte-for-byte.
- **History and documents:** Inspected the amendment chain, earlier findings/dispositions, frame conventions and authorization records. Reviews 01–07 remain byte-identical to `0ac630b`; review 08 retains its previous bytes as a prefix. Baseline registers retain every original line: assumptions **218 additions/0 deletions**, validation **43/0**. Targeted removals are limited to three status/index lines. Checked relative link paths: **0 broken**. Ruff lint/format and `git diff --check` passed.
- **Preservation gates:** Using `PYTHONPATH=src` with the supplied virtual environment, completed `m1_proof.py` **7/7**, full `m2_proof.py` **228/228**, both GMAT `compare` commands, snapshot `verify-baseline`, local cross-platform validation, M1 determinism and all four M2 determinism commands. All passed.
- **Partial/unavailable:** Full pytest was deliberately interrupted after **267 passed in 168.71 s**; it was not completed. Complete Proof wrapper scripts and three-platform execution were not rerun. GitHub API access failed, so CI run `39003804587` and its individual job conclusions remain independently unverified. External source bytes/digests were not freshly retrieved.
- **Scope:** All **63 whole-branch changed files** are under `docs/`. Protected implementation/evidence paths, DR-0024…0027, ADR-0009 and registers are unchanged by this correction. Tracked worktree status is clean.

Outstanding gates remain:

- **T0:** planning acceptance, explicit merge/T0 authorization and successful planning merge.
- **T1:** T0 evidence and independent review, applicable checkpoint decisions and separate authorization.
- **T2:** additionally, owner decisions on DR-0027 A-4/A-5/A-6/A-s/B-4.
- Q-G2-1/5/7 and Q9 values remain deferred to the T0 checkpoint; Q-G2-6 to T4; numerical thresholds require a later measured-evidence DR. Q-G3-7 and the stated implementation exclusions remain NOT AUTHORIZED.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence until M3P9-F1 and M3P9-F2 are resolved.**

No fixes, merge, T0/T1/T2 work or M3 implementation were performed.
