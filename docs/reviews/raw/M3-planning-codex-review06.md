### M3P6-F1 — Exact line-of-nodes result needs a domain restriction

**Severity:** MINOR  
**Category:** Mathematical consistency  
**Where:** `docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md`, amendment 2, exact-results table (line 247) and E2.

**Claim:** “Any finite δ” is incorrect for the stated inclination and node definitions.

**Evidence:** For φ = Ω, the transformed vector is
\[
h_B=(\sin(i-\delta)\sin\Omega,\;-\sin(i-\delta)\cos\Omega,\;\cos(i-\delta)).
\]
Thus Δi = −δ and ΔΩ = 0 hold when \(0<i-\delta<\pi\). Crossing an equatorial configuration folds the inclination and changes the node by 180°.

My independently constructed matrix gives:

```text
i=2°, Ω=φ=0°, δ=+5°:
Δi=+1°, |ΔΩ|=180°
```

This contradicts the claimed −5° and zero. The E2 grid avoids these crossings, so it cannot validate the unrestricted claim.

**Suggested resolution:** Qualify the exact relation with its nonsingular domain, document the endpoint/crossing behavior, and add corresponding finite-rotation checks while preserving history.

### M3P6-F2 — E5’s node-jump result is reported but never asserted

**Severity:** MINOR  
**Category:** Verification adequacy  
**Where:** `docs/science/experiments/m3-planning/dr0028_node_signed_verification.py`, `exact_properties()`, lines 288–293.

**Claim:** The script does not enforce the complete E5 property described in DR-0028.

**Evidence:** It computes and records the maximum node jump but never checks that it equals 180°, or that any defined samples were obtained.

I independently mutated `finite()` to return zero node change specifically at the E5 inclination, leaving the first-order grid unchanged:

```text
E5 jump mutation exit 0
verdict PASS
reported jump 0.0
```

The current recorded 180° result is correct; the verification does not require it.

**Suggested resolution:** Assert the expected jump using a documented tolerance, require defined sample coverage, and demonstrate that suppressing the jump causes exit 1.

### M3P6-F3 — Implemented wrapping interval contradicts the declared convention

**Severity:** MINOR  
**Category:** Mathematical consistency  
**Where:** `dr0028_node_signed_verification.py`, `wrap()` (lines 75–76), versus its module convention and DR-0028 amendment 2 (line 219).

**Claim:** The declared interval is \((-\pi,\pi]\), but the implementation returns \([-\pi,\pi)\).

**Evidence:**

```text
wrap(+pi) = -3.141592653589793
wrap(-pi) = -3.141592653589793
```

The committed oracle consequently returns −180° for the crossing example in M3P6-F1, although the declared interval requires +180°. E5 takes absolute values and hides this discrepancy.

**Suggested resolution:** Make `wrap()` match the declared convention and check both antipodal endpoints explicitly.

## Summary

**REQUEST_CHANGES** — three MINOR findings; no MAJOR or BLOCKER findings.

Reviewed HEAD: `2ec8f878d8dea29a220a8596c934974fb57eb45f`. Correction commit: `bcb7f9bff6b79ad22f01eaa6a2cac3e444f55ecf`. Their difference contains only the review prompt.

Verified independently:

- **Corrected signs and derivation:** Using my own matrix \(R_z(\phi)R_x(-\delta)R_z(-\phi)\), I obtain
  \[
  \Delta i=-\delta\cos(\Omega-\phi),\qquad
  \Delta\Omega=+\delta\cot i\sin(\Omega-\phi).
  \]
  These agree with DR-0024’s passive transformation. The perpendicular-axis closed form also agrees, with maximum discrepancy below \(8.7\times10^{-16}\) over 1,000 independent cases.
- **Preserved example:** Recomputed ΔΩ = **+0.259805543688°**, Δi = **+0.000340085438°**.
- **Signed script:** Ran it with output under `review_scratch/`; exit 0 and `cmp` confirmed byte-identical JSON. Reproduced 506 inclination-order samples, 532 node-order samples, and 1,064 sign checks. The documented grid orders and tolerance treatment are sound.
- **Live formula mutations:** Independently reversing Δi or ΔΩ produced exit 1 with **1,120** and **1,008** failing checks respectively. A zero-formula mutation was also rejected.
- **Research regression:** Reran `dr0028_node_sensitivity.py` and `q10_residual_consequences.py`; both JSON files were byte-identical. Independently recomputed all **27 atmosphere boundary jumps**, with zero discrepancy against the recorded values.
- **Local regression commands:**  
  `.venv/bin/python -m pytest -q -p no:cacheprovider` — **1,185 passed**, three overflow warnings from numerical-extreme tests.  
  `toolbox/validators/m1_proof.py` — **7/7 PASS**.  
  `toolbox/validators/m2_proof.py` — **228/228 PASS**.  
  `cross_platform.py` and both committed GMAT comparison commands passed; local M1 golden differences were zero.
- **History and scope:** Checked both requested git ranges. Only three index/status lines were removed since `cf0e24f`. Earlier review records retain their historical content; the complete 558-byte withdrawn Q4 row is preserved. Registers remain additions-only (**218/0**, **43/0**), with every baseline line retained.
- **Planning consistency:** J-ax-1, identity transformation, atmospheric co-rotation, FC-1…FC-10, constants, digests, local-solar-time correction, prior dispositions, and authorization boundaries remain intact. The branch diff is entirely under `docs/`; no production or frozen acceptance artifacts changed. Ruff lint/format passed; checked relative Markdown links had no broken targets.
- **CI limitation:** GitHub API access failed. I could not independently confirm the reported successful run or CI on exact HEAD.

Remaining gates:

- **T0:** planning acceptance, separately authorized merge, and explicit T0 authorization.
- **T1:** T0 evidence and independent review, resolution of applicable T0-checkpoint decisions, and separate authorization.
- **T2:** additionally requires owner decisions on DR-0027 A-4/A-5/A-6/A-s/B-4. Q-G2-6 remains deferred to T4; numerical acceptance thresholds remain for the later threshold DR.

**The package is not ready to be presented for planning acceptance as documentation evidence until these MINOR findings are resolved.**

No fixes, merge, or M3 implementation work were performed.