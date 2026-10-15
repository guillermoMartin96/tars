### M3P2-F1 — Unaddressed physical and event choices are recorded as approved
**Severity:** BLOCKER  
**Where:** DR-0024 Resolution Q4; DR-0026 Resolution Q-G3-9; SCI-0013/0014/0017; M3-proposal §9.  
**Claim:** The records extend the owner’s D3 architecture approval to decisions the owner did not explicitly resolve.  
**Evidence:** Q4 acknowledges that the owner did not select an axis, but labels frame-z alignment “APPROVED via DR-0026 D3.” Q-G3-9 likewise acknowledges that the two-body escape criterion was not separately addressed, then records it as approved. These are additional physical/event semantics beyond D3’s context, density, configuration-identity and schema architecture. Requesting subsequent confirmation does not make the approval attribution accurate. In contrast, Q-G3-10’s optional engine is expressly included in the D3 definition, so its treatment is supported.  
**Suggested resolution:** Keep Q4 and Q-G3-9 OPEN pending explicit owner decisions. Propagate that status to the SCI entries and milestone documents; retain the proposed choices as recommendations.

### M3P2-F2 — Documents introduce an unsupported T0 authorization
**Severity:** BLOCKER  
**Where:** M3-proposal status and §4 T0; milestones/README; DR-0024 follow-up; DR-0027 “Work continuing independently.”  
**Claim:** The records attribute authorization for executable follow-on work to the owner without support in the supplied instruction.  
**Evidence:** The proposal calls T0 “authorized 2026-10-15, after the planning merge” and permits “minimum isolated spike code.” DR-0027 also calls that spike authorized. The supplied owner decisions resolve planning principles and require later measurements; they do not authorize T0 execution or make merging planning documents an execution authorization. The checkpoint explicitly states that no M3 implementation is authorized.  
**Suggested resolution:** Record T0 as proposed and awaiting separate authorization, or cite an explicit owner instruction that authorizes this precise research scope. A planning merge must not itself grant that authority.

### M3P2-F3 — Lowest-band source discrepancy affects the entire band
**Severity:** MINOR  
**Where:** DR-0024 §3.4 “Consequences”; DR-0027 §B “Effect.”  
**Claim:** The statement that the 0.010-versus-0.0 km base discrepancy affects “heights below 10 m only” is mathematically incorrect.  
**Evidence:** For every height where both sources select their lowest band,
\[
\frac{\rho_{\text{author}}(h)}{\rho_{\text{GMAT}}(h)}
=\exp(0.010/7.249)=1.00138045256944.
\]
The difference is therefore approximately **0.138045% throughout the lowest band up to 25 km**, not merely below 10 m. The row comparison correctly identifies the differing cell, but its documented consequence understates its reach.  
**Suggested resolution:** Correct both descriptions and qualify the claim that all relevant low-altitude bands are confirmed. Keep the dataset choice OPEN in DR-0027.

## Summary

**REQUEST_CHANGES**

Verified:

- Whole-branch scope: **32 files, all under `docs/`**; no production implementation or changes outside documentation.
- Historical registry lines remain unchanged and in order: assumptions **185 additions, zero deletions**; validation **43 additions, zero deletions**.
- Correction notes distinguish historical results, incorrect descriptions, corrected interpretations and unchanged acceptance. Gating GMAT scripts set `Earth.Mu = 398600.4418` and use point masses; informational scripts use `JGM3.cof`. Recorded probe evidence supports the stated file-GM behavior and JGM-3 constants.
- Q10 JSON independently yields **25 identical rows, two differing rows, one absent row**. All **27 boundary jumps** recompute consistently, including **+0.00136155803350 at 25 km**, **+0.00009588628442 at 80 km**, and **−0.00001534535341 at 250 km**.
- DR-0024 §3.5’s relative magnitudes are correct: radius contribution **2.19499868×10⁻⁷**, GM contribution **7.52633289×10⁻¹⁰**, tide-value difference **8.98380275×10⁻⁶**, approximately **41 times** the radius contribution. Its mathematical-consistency conclusion is supported.
- Thresholds, final timestep, reference missions, geodetic test source, snapshot treatment, termination altitude and residual dataset choices remain deferred/open. AC-1 remains accepted; AT-1–AT-7 remain open; no language/runtime or hardware decision was made.
- Network retrieval failed; Q10 arithmetic was checked against the supplied per-row JSON. Original-file digests, author routines and errata inspection were not independently reverified.

The planning branch is **not ready to merge as planning/documentation evidence** until the unsupported approval and authorization records are corrected.