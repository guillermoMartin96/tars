### M3P-F1 — The pinned density table is discontinuous, not C0
**Severity:** MAJOR  
**Where:** DR-0024 §§4.3, 5, 11; DR-0025 §5 and Q-G2-3; experiment README; VAL-0018  
**Claim:** The table is C0, with discontinuities only in its derivative.  
**Evidence:** The implemented band selection uses independently rounded base densities. At 250 km, the relative density jump is −1.53453534e-5; at 25 km it is +1.36155803e-3. These finite jumps are recorded in `band_boundary_jumps` and reproduced by the rerun. Consequently, the RHS has value discontinuities, and the observed convergence degradation cannot be attributed solely to derivative jumps. The measured ratios do not establish an asymptotic convergence order.  
**Suggested resolution:** Documentation correction: describe the literal table as discontinuous and distinguish density jumps from scale-height changes. Retaining the literal table requires no new policy choice; enforcing continuity would change the model and requires an explicit engineering-policy decision, with corresponding reference and identity treatment.

### M3P-F2 — Drag-induced along-track displacement has the wrong sign
**Severity:** MINOR  
**Where:** DR-0025 §4, “Drag”  
**Claim:** The spacecraft falls progressively further behind the point-mass orbit.  
**Evidence:** Drag lowers semimajor axis and increases mean motion. Using the committed candidate equations at 53,700 s, the drag-only displacement projected onto the point-mass final velocity direction is **+362,217.6 m**: ahead. Its displacement magnitude is **362,659.2 m**, consistent with the quoted 363 km.  
**Suggested resolution:** Mechanical/documentation correction: describe the accumulated phase advance for this case. Distinguish instantaneous deceleration from the subsequent increase in orbital angular rate.

### M3P-F3 — The decay oracle retains approximations beyond density evolution
**Severity:** MINOR  
**Where:** DR-0025 §2 Q6; DR-0024 [KH] source description; experiment README finding 5  
**Claim:** Integrating the scalar decay equation addresses the fixed-density estimate’s discrepancy; Q6 says it is “exact only” for spherical height and a smooth atmosphere.  
**Evidence:** Spherical height and smooth density do not make orbit averaging exact. The stated rotation factor also neglects part of the inclined-orbit relative-speed variation. For a circular orbit, with \(q=\omega a/v\) and argument of latitude \(u\), the instantaneous power factor is
\[
(1-q\cos i)\sqrt{1-2q\cos i+q^2(1-\sin^2 i\sin^2u)},
\]
rather than simply \((1-q\cos i)^2\). As a diagnostic, integrating the proposed scalar equation with the full table gives **−7,974.464 m**, versus **−7,980.056 m** from the Cartesian candidate model. This is not the proposed smooth validation case, but demonstrates that updating density alone does not eliminate model discrepancy.  
**Suggested resolution:** Documentation correction: label the equation and rotation factor approximate throughout, enumerate their assumptions, and retain their approximation errors in the future oracle budget. Choosing a more complete averaged model would be an engineering-policy choice.

### M3P-F4 — The task plan still specifies a rejected atmosphere cutoff
**Severity:** MINOR  
**Where:** `docs/milestones/M3-proposal.md` §4 T2 and §5 Q5  
**Claim:** Validation should check “zero drag above the cutoff” and “no drag above the model’s top altitude.”  
**Evidence:** DR-0024 §§4.6, 6 and 12 instead recommend extrapolating the highest band and reject a zero-density cutoff. The proposal gives the DRs precedence, so this is not an approved conflicting decision, but its task instructions remain inconsistent with the current recommendation.  
**Suggested resolution:** Mechanical/documentation correction: replace the cutoff assertions with checks of whichever extrapolation/domain policy G1 approves.

### M3P-F5 — Rotation-rate relative difference is understated tenfold
**Severity:** MINOR  
**Where:** DR-0024 §3.1, “Source disagreements recorded”  
**Claim:** The relative difference between the two quoted rotation rates is \(2\times10^{-9}\).  
**Evidence:** Using those values,
\[
7.29211514670698\times10^{-5}/(7.292115\times10^{-5})-1
=2.01185775\times10^{-8}.
\]
The qualitative conclusion that this difference is small remains reasonable.  
**Suggested resolution:** Mechanical/documentation correction to \(2\times10^{-8}\).

## Summary

**Verdict: REQUEST_CHANGES**

Verified:

- The baseline-to-HEAD diff contains **24 changed files, all under `docs/`**. Existing validation-register bytes are preserved as an exact prefix; only VAL-0018 was appended. No reviewed files were modified.
- The supplied baseline `d92ab89` has the same tree as accepted candidate `f05bc1e`. The snapshot’s `origin/main` points to `63bec8d`; I used the explicitly supplied baseline hash.
- The Python experiment reproduced **every committed numeric value exactly**, excluding runtime. At dt = 10 s, position errors were **0.298336 m** point mass, **0.301742 m** J2, **4.570308 m** drag, and **2.055566 / 0.698463 m** combined.
- Reproduced displacements: **740.680 km** J2, **362.659 km** drag, **1,161.034 km** combined; node rates **−5.438454 / −5.409878°/day**; height-choice sensitivity **74.013 km**, non-rotation **40.033 km**, and B +1% **4.833 km**.
- Checked J2 acceleration signs, potential/energy consistency, normalization, secular-rate expressions, mass coupling, and dissipation preconditions. NGA defining constants and IERS normalization/scaling values agree with the cited primary material. [NGA](https://earth-info.nga.mil/?action=wgs84&dir=wgs84), [IERS chapter 6](https://iers-conventions.obspm.fr/content/chapter6/icc6.pdf)
- GMAT figures **0.189401 m**, **0.002009 m**, and **0.383221 m** match the committed results and probe configurations; GMAT was not rerun. TOEEq exchange aligns the initial pole but does not freeze GMAT’s physical Earth orientation; the drafts appropriately leave residual bounding unresolved.
- G1–G3 remain open; M1/M2 evidence remains unchanged; no approved M3 thresholds, Rust/C/FFI commitment, or owner decision taken by the drafts was found. The architecture additions have concrete M3 uses and leave foreseeable force extensions possible.

The planning checkpoint is **not ready to go to the Tech Lead as written**, principally because the density-model smoothness claim misstates the basis of the G2 convergence decision.