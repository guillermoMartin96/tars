| ID | Disposition | Evidence |
|---|---|---|
| M3P6-F1 | **RESOLVED** | Independently derived the identity and all five table rows. Recomputed i = 2°, δ = 5°: Δi = +1°, ΔΩ = +180°. Restoring the unrestricted claim exits 1. |
| M3P6-F2 | **RESOLVED** | Both tilt signs have 73 executed jump assertions. Suppressing the jump, and separately deleting E5a, E5b or E5c, each exits 1. |
| M3P6-F3 | **RESOLVED** | Both ±π map to +π. Exact rational comparisons confirm finite-input reduction. Restoring the previous wrapping implementation exits 1, with 28 designated failures. The broader input-domain claim has the separate issue below. |

### M3P7-F1 — Exact wrapping guarantee needs a finite-input restriction

**Severity:** MINOR  
**Category:** Mathematical consistency  
**Where:** `docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`, `wrap()` docstring, lines 85–91; DR-0028, Resolution amendment 3, item 3, lines 389–392.

**Claim:** The wrapping guarantee omits its necessary finite-input precondition.

**Evidence:** The docstring states:

> “The result is therefore the unique float in (-PI, PI] that differs from a by an exact integer multiple of TAU”

Amendment 3 repeats this guarantee without restricting `a` to finite values. Independently evaluating the function using `runpy.run_path()` gives:

```text
wrap(inf) raises ValueError: math domain error
wrap(-inf) raises ValueError: math domain error
wrap(nan) = nan; in interval = False
```

Thus the guarantee does not hold for every float input. The fmod/Sterbenz argument is correct for **finite** binary64 inputs; this is a documentation-domain defect, not a finite-angle numerical defect.

**Suggested resolution:** Explicitly restrict the exactness and interval guarantees to finite float angles. Document nonfinite inputs as outside the supported domain, or define and test their rejection behavior. Preserve the existing endpoint correction.

## Summary

**REQUEST_CHANGES** — one new MINOR finding. All three original review-06 findings are resolved.

Reviewed HEAD: `cf5fc712affd198bdadaf4b6faadd9ffedc8b38f`.  
Correction commit: `f999626b7277da2c3f24d75eb9de19bac10297d9`.

Verified independently:

- **Exact geometry:** With \(u=(\sin\Omega,-\cos\Omega,0)\), the passive rotation gives
  \[
  \hat h_B=\sin(i-\delta)u+\cos(i-\delta)\hat z.
  \]
  Consequently, for \(j=i-\delta\), the inclination is \(j\), \(-j\), or \(2\pi-j\) in the three documented open regimes. These yield exactly the table’s Δi expressions. At \(j=0,\pi\), B’s node is undefined. In both crossing regimes, the node direction reverses; wrapping gives +π.
- **Independent numerical checks:** My vector-rotation code checked 10,000 identity cases, with maximum component discrepancy \(6.11\times10^{-16}\). A separate implementation using conjugated Cartesian rotations checked all 48 endpoints; maximum transverse residual was **0.8125 ε**.
- **Signed formulas:** Independently differentiated the transformed angular-momentum vector and recovered
  \[
  \Delta i\approx-\delta\cos(\Omega-\phi),\qquad
  \Delta\Omega\approx+\delta\cot i\sin(\Omega-\phi).
  \]
  The passive convention agrees with DR-0024 revision 2.
- **Tolerances and coverage:** The two-frame \(64\epsilon/\min(\sin i_A,\sin i_B)\) treatment correctly accounts for node conditioning. Circular distance handles floating results near either antipodal representative. The endpoint 32 ε allowance is consistent with the documented component-error budget. Observed coverage is nonvacuous: 168 interior, 144 crossing and 48 endpoint cases; 73 jump assertions per tilt sign.
- **Wrapping:** Independently compared **99,962 finite floats**, plus explicit maximum-magnitude, minimum-normal and subnormal inputs, against exact rational reduction. No mismatch occurred. The rational reference, endpoint tests and exact-equivalence filtering are correct.
- **Mutation testing:** `.venv/bin/python review_scratch/review.py` confirmed exit 1 for all eight file-level mutations: old wrapping, unrestricted identity, suppressed oracle jump, separate deletion of E5a/E5b/E5c, and either reversed formula sign. All five built-in exact mutants and four formula mutants were rejected by their required checks.
- **Research regression:** Reran the signed verification, sensitivity and Q10 residual scripts. Their JSON outputs were byte-identical to the committed results. The signed script’s `grid`, `tolerances`, `formulas_under_test` and `mutants` sections equal those at `bcb7f9b`: 506/532 order samples and 1,064 sign checks. The sensitivity script’s internal opposite endpoint convention causes no reported-value contradiction.
- **Baseline validation:** Ran `m1_proof.py` (**7/7**), full `m2_proof.py` without `--quick` (**228/228**), both GMAT comparison commands, `reference_snapshot.py verify-baseline`, `cross_platform.py` and `determinism.py`; all passed. The optional `.venv/bin/pytest -q` run was interrupted during expensive snapshot mutations after **856 passed, 2 warnings**; I do not claim a completed full-suite rerun.
- **History and scope:** Checked both requested diff ranges. The branch changes only `docs/`. Baseline registers retain every original line in order, with **218/0** and **43/0** additions/deletions. Targeted removals are status/index cells only. Earlier findings and amendments remain preserved. Approved constants, FC-1…FC-10, frozen artifacts, validation semantics and outstanding decision statuses remain unchanged. Ruff lint/format, scoped relative links and `git diff --check` passed.
- **CI limitation:** GitHub API access failed. The reported four-job CI success was not independently confirmed.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence until M3P7-F1 is resolved.**

No fixes, merge, or M3 implementation work were performed; tracked working-tree status remains clean.