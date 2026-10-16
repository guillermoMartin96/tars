### M3P3-F1 — Velocity transformation needs a fixed-pole qualification
**Severity:** MINOR  
**Category:** Coordinate-frame and physics consistency  
**Where:** `docs/decisions/requests/DR-0024-m3-physical-models-and-constants.md`, “Q4 coordinate conventions,” Relation and FC-9  
**Claim:** The velocity transformation is stated generally but assumes a frame rotating solely at the pinned spin rate about its pole. That qualification matters because DR-0028 leaves time-varying pole options open.  
**Evidence:** The record states:

> “v_EF = R(t)(v_I − ω × r_I), with ω = ω_E Ẑ”

For a general time-dependent rotation, differentiating `r_EF = R(t)r_I` gives:

```text
v_EF = R(t)v_I + Ṙ(t)r_I
```

The recorded expression therefore requires `Ṙ = −R[ω×]`. A moving pole introduces additional angular-velocity components; the pinned `ω_E Ẑ` alone does not describe that coordinate transformation. FC-9 replaces only FC-3/FC-4, leaving the velocity tests unqualified.

The expression is correct for recommended option A1. Its axisymmetry identities and FC-5 signs are also correct for the planned LEO cases.  
**Suggested resolution:** Explicitly scope the simplified velocity transformation to A1. For A2/A3, require the general transformation and distinguish the frame’s full angular velocity from the assumed atmospheric spin, with corresponding velocity tests. Leave the choice OPEN.

### M3P3-F2 — Q4 amendment log abbreviates the withdrawn attribution
**Severity:** MINOR  
**Category:** Decision authorization and traceability  
**Where:** `docs/decisions/requests/DR-0024-m3-physical-models-and-constants.md`, amendment log  
**Claim:** The amendment preserves the withdrawal’s meaning but does not preserve the previous attribution verbatim as requested.  
**Evidence:** The log says the Q4 row formerly read:

> “the approval comes from the D3 approval in DR-0026 … flagged for owner confirmation in the checkpoint report”

The previous row, recoverable with:

```sh
git show 23bafd2:docs/decisions/requests/DR-0024-m3-physical-models-and-constants.md
```

includes the omitted attribution:

> “whose §5.7 states ‘In M3 the body axis is the frame z axis (DR-0024 J-ax-1)’”

It also attributes approval to the proposed pinned rotation rate and D-rot-1. Those clauses are absent from the amendment quotation.  
**Suggested resolution:** Append the complete previous Q4 row, including its status, verbatim to the amendment log. Preserve the current withdrawal and corrected decision.

## Summary

**REQUEST_CHANGES**

Verified at branch `m3-planning-checkpoint-037cfd34`, commit `007f38cfaef337628b82896f37fb3e0cdd3a9def`:

- The whole-branch diff contains **39 files, all under `docs/`**. Baseline science-register lines remain unchanged: assumptions **193 additions / 0 deletions**; validation **43 / 0**. SCI-0005 and VAL-0007 correction notes are unchanged since review 02.
- Owner approvals, deferred questions, NOT AUTHORIZED telemetry, model-version retention, AC-1 and AT-1…AT-7 remain represented. Creating DR-0028 is justified: approving the common Earth-fixed axis does not select its inertial realization.
- Termination altitude remains explicit per scenario, metres, geodetic, without a default or universal number. Ranges, crossing semantics and domain interactions remain assigned to T0. The governing records withdraw automatic top-band extrapolation.
- T0 has not started and requires explicit checkpoint approval plus the planning merge. No production implementation, frozen-artifact change, merge, or language/runtime decision appears in the diff.
- Independently recomputed:
  - `exp(0.010/7.249) = 1.0013804525694443`; GMAT density is **0.1378549547% lower** throughout the shared lowest band.
  - Author-base 25 km jump: **−1.8868488886e−5**; GMAT jump: **+0.0013615580335**.
  - GMAT/author density difference: **+7.62705e−6 at 950 km**, **+1.52540e−5 at 999.999 km**, **−7.27581e−7 at 1000 km**, **+19.62765% at 1100 km**, **+144.99606% at 1500 km**, **+500.23114% at 2000 km**.
  - All 27 boundary jumps agree with independent recomputation within **1.11e−16**. The residual script rerun is byte-identical.
- Recorded rows support **25 identical, 2 differing, 1 absent**. Printed-edition uncertainty is explicit. Network retrieval failed, so source bytes, digests and errata were **not independently reverified**.
- Local checks passed: **M1 Proof 7/7**, **M2 Proof 228/228**, M1 golden comparison with zero differences, both committed GMAT comparisons, M1 cross-process determinism, Ruff lint and formatting. Full pytest remains running at reporting; remote CI status was not verified.

**The planning branch is not yet ready to be presented to the Tech Lead for checkpoint approval as planning/documentation evidence; resolve the two MINOR findings first.**