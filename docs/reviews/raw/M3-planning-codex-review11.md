| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P10-F1 | **NOT RESOLVED** | The original uncaught-import counterexample is rejected correctly now. However, a suppressed import failure followed by an algebraically equivalent fallback still counts as detection of an assertion removal that never occurred. See M3P11-F1. |
| M3P10-F2 | **NOT RESOLVED** | The six added protections work, but five category B assertions have independently important counterexamples. The reported 6 A / 9 B / 3 C classification is therefore unsound. See M3P11-F2. |

### M3P11-F1 — Rounding differences can masquerade as the intended exercised defect

**Severity:** MINOR  
**Class:** Verification defect  
**Where:** `dr0028_node_signed_verification.py`, `instrumented()` and `exercised()`; `dr0028_node_signed_mutation_check.py`, `not_rejected` predicate.

**Claim:** Any unequal floating-point result establishes `defect_exercised`, even when the intended defect has disappeared and the difference is harmless rounding—or occurs in the wrong component. This still permits a suppressed infrastructure failure to count as evidence of assertion removal.

**Evidence:** In a scratch copy, immediately before `out[component] *= factor` inside `formula_scaled()`, I inserted:

```python
if factor == 2.0:
    try:
        import nonexistent_review11_dependency
    except ImportError:
        return (
            -delta * math.cos(node - phi),
            delta * (math.sin(node - phi) / math.tan(inc)),
        )
```

The fallback returns the correct analytical formulas. Its node expression merely reassociates multiplication and division. **The order assertion remains intact.**

Command:

```text
TMPDIR="$PWD/review_scratch" \
  .venv/bin/python review_scratch/exception_counterexample.py
```

Observed:

```text
order assertion intact: True
('expected rejection', 'exit 1, FAIL verdict; expected rejection shown')
```

Both doubled-coefficient mutants report:

```text
formula calls:                       3000
differing calls:                       940
defect_exercised:                     true
order failures:                         0
sign failures:                          0
rejected_by_designated_checks:       false
```

For the supposed doubled-Δi mutant, even Δi is unchanged: differences occur only in ΔΩ.

I then ran the complete harness entrypoint with this construction as its mutation, retaining the original baseline check and all 13 controls:

```text
{"verdict": "PASS", "mutations": 1, "detected": 1, ...}
[all 13 controls: PASS]
main_return 0
```

The assertion-removal expectation is therefore accepted without removing an assertion or exercising either intended doubled coefficient. This does not invalidate the committed mathematical results; it invalidates the claimed reason-specific detection guarantee.

**Suggested resolution:** Establish that the **named target defect**, in its intended component and domain, was exercised. Arbitrary bitwise inequality is insufficient. Add this fallback as a negative control. A paired intact-assertion run using the same mutant construction would also expose this case.

### M3P11-F2 — Five “redundant” assertions protect failures their proposed substitutes miss

**Severity:** MINOR  
**Class:** Verification defect  
**Where:** `dr0028_node_signed_assertion_classification.py`, category B entries W5, E1, E2e, E5b-nonfinite and E5b-defined; DR-0028 amendment 7, assertion classification and dependency claims.

**Claim:** Demonstrating overlap for one defect does not establish redundancy across the assertion’s protected property. Five category B assertions admit counterexamples that escape every other exact-property check when that assertion alone is removed.

**Evidence:** Reproducer:

```text
PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python review_scratch/classification_counterexamples.py
```

Using the same injected-component interfaces as the classification tool:

- **E1:** Supply `tilt_fn = Rz(0.01) · tilt_matrix(phi, delta)`. This proper rotation preserves endpoint equatoriality but changes the coordinate origin. Intact output: `E1 rotation convention deviation 1.000e-02`. Removing E1’s deviation assertion leaves **no failures**.
- **E2e:** Return the identity rotation only at `phi=37°`, `delta=2°`; otherwise use `tilt_matrix`. These endpoint inputs are outside E1’s sampled tilts. Intact output: `E2 endpoint not equatorial: i=2.0 rho=3.490e-02`. Removing E2e leaves **no failures**.
- **E5b-nonfinite:** Return a NaN node difference only at `i=0.1°`, `Ω=0°`, `φ=1°`. Each sweep still has 359 valid samples, and both crossing assertions execute. Intact output contains two `E5b sweep: non-finite node difference at phi = 1 deg` failures. Removing this assertion leaves **no failures**.
- **E5b-defined:** Return an undefined node only at the non-crossing azimuths `φ=1°` and `2°` for that sweep. Both crossing assertions still execute. Intact output contains `only 358 defined samples` for each tilt sign. Removing the sample-count assertion leaves **no failures**.
- **W5:** Return `1.01` for input `1.0`, otherwise use the reference wrap. W2’s exact-reduction input list does not include this input. Intact output has six exact-equivalence failures. Removing W5 leaves **no failures**.

I additionally reproduced both E5b cases through the complete script entrypoint:

```text
.venv/bin/python review_scratch/classification_entrypoint.py

E5b-defined   removed False exit 1 verdict FAIL
E5b-defined   removed True  exit 0 verdict PASS
E5b-nonfinite removed False exit 1 verdict FAIL
E5b-nonfinite removed True  exit 0 verdict PASS
```

Thus E5c does not replace general sweep coverage, and allowing one undefined sample does not replace explicit non-finite rejection.

The six existing A demonstrations are sound. W1/W4 and E6-value/E6-sign have adequate redundancy evidence within their stated deterministic scope. The three C rationales are reasonable for the current stateless implementation and fixed test configurations. The five counterexamples above instead meet category A’s definition.

**Suggested resolution:** Reclassify these five assertions and add narrowly targeted protection under I-10 §4, or strengthen the independent checks until the redundancy claims hold. Correct amendment 7’s classification totals and dependency statements.

## Summary

**REQUEST_CHANGES** — two MINOR verification findings; no BLOCKER, MAJOR or current mathematical-result defect found.

Reviewed branch `m3-planning-checkpoint-037cfd34`, HEAD **`c16b3b50fe2814e6b05423bfb2de31b5f4c7f097`**, parent `0972e1a`, correction commit `8f3f22a`.

Verified independently:

- Ran `dr0028_node_signed_verification.py` twice: byte-identical output, matching committed evidence. Order coverage **506/532** and sign coverage **560/504**, independently enforced.
- Ran `dr0028_node_signed_mutation_check.py` twice: byte-identical output, **109/109** detections and **13/13** declared control classifications.
- Ran `dr0028_node_signed_harness_regression.py`: all five regression controls fail against `896d52d` and pass now. My separate `original_repro.py` independently reproduces the original caught-import false detection.
- Ran classification and sweep tools: reported **18/18**, and **35 assertions / 23 detected / 12 surviving / 0 exceptions**. Their committed outputs reproduce exactly; F2 identifies limitations beyond their demonstrations.
- Executed `896d52d` independently and recursively compared outputs: **zero changed pre-existing values; 79 added keys**. AST comparison confirms unchanged mathematical definitions and checks, apart from E5d’s parameterization. The 1% Δi oracle mutant still produces **one E3 and one E4 failure**.
- Independently derived both signed first-order formulas, the line-of-nodes regimes, endpoint singularities, node reversal, perpendicular-axis closed form and inclination bound. My conjugated-Cartesian rotation calculation checked **10,000 cases**; rotation disagreement was at most `4.44e-16`, closed-form node disagreement `1.33e-15`. Reproduced:
  - review-04 `ΔΩ = +0.259805543688°`;
  - crossing `Δi≈+1°`, `ΔΩ=180°`.
- Checked **10,000 finite angles** against rational wrapping, both endpoints and non-finite rejection.
- Reran sensitivity and atmosphere-residual scripts byte-for-byte. Independently recomputed all **27 density jumps**, maximum discrepancy `1.11e-16`; lowest-band ratio **1.0013804525694443**.
- Confirmed all **75 whole-branch changed files are under `docs/`**. Protected production, test, scenario, toolbox and Proof paths are unchanged from `d92ab89`. Baseline register lines remain intact: **218/0** and **43/0** additions/deletions. Records/raw outputs 01–10 retain their previous contents; I-1–I-9 instruction blocks are preserved verbatim in the new prompt.
- Completed standalone `m1_proof.py`: **7/7**; full `m2_proof.py`, without `--quick`: **228/228**. Both GMAT `compare` commands, snapshot `verify-baseline`, local golden comparison and all five determinism runs succeeded. Ruff lint and formatting succeeded.
- **Partial:** attempted both complete Proof wrappers in an isolated scratch clone. Pytest was interrupted in both; the M2 wrapper’s duplicate snapshot and validator runs were also interrupted. Both wrappers consequently report failure/incomplete evidence, **not complete Proof passes**. The M2 wrapper also inherited M1-generated evidence changes, so its checkout provenance was not clean.
- **Unavailable:** GitHub API connection failed for run `39056505376`; its individual CI job conclusions remain independently unverified. Fresh external source bytes, source digests, GMAT executable runs and three-platform execution were not revalidated.

J-ax-1, atmospheric co-rotation, constants and authorization boundaries remain preserved. T0 still requires planning acceptance, merge authorization/success and explicit T0 authorization. T1 requires the T0 checkpoint, applicable owner decisions and separate authorization. T2 additionally depends on DR-0027 A-4/A-5/A-6/A-s/B-4 and applicable T0 deferrals. Q-G2-1/5/7 and Q9 values remain deferred; Q-G2-6 remains deferred to T4; numerical thresholds require later measured evidence. Q-G3-7 remains NOT AUTHORIZED.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence.**

No reviewed files were fixed, nothing was merged, and no T0/T1/T2 or production implementation was performed.
