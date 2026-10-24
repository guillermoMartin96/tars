# External Review: M3 T2 decision-readiness package (I-23), Review 01

**Reviewer/model:** Codex (codex-cli 0.162.0), session `01a16fe1-12e7-7730-a566-6c1b61318b7e`; a separate provider from the implementer  
**Date:** 2026-10-24  
**Reviewed revision:** `5ee6a6a2d78ef425687ba164bb32033947ee7c01` (branch `milestone-3-t2-decision-readiness`; parent `main` = `fc50aed`)  
**Scope:** documentation only, under I-23 §10. The reviewer assessed technical correctness, decision completeness, evidence quality and scope compliance of the five I-23 deliverables and the append-only edits.  
**Raw records:**
- `docs/reviews/raw/M3-T2-readiness-codex-review01-prompt.md`, which includes I-23 verbatim;
- `docs/reviews/raw/M3-T2-readiness-codex-review01.md`;
- evidence in `docs/reviews/raw/M3-T2-readiness-codex-review01-evidence/`, with SHA256SUMS. It holds the reviewer's script and output, and the implementer's I-23 corroboration script. Python is stored as `.py.txt`.

**How it was run:**
- a fresh clone pinned at the full SHA, with `uv sync --locked` and `review_scratch/` excluded from git;
- `codex exec -s workspace-write`, no network;
- the tracked tree was clean after the review.

## Summary
**`VERDICT: REQUEST_CHANGES`.**

The reviewer confirmed the following:
- the documentation-only scope (10 files, all under `docs/`);
- the governing P1–P10 gate, quoted correctly and not narrowed;
- the P1–P9 readiness classifications, as defensible;
- N-1, N-2, N-3, N-5 and N-7;
- the arithmetic of C-1 … C-5, and the honesty of the C-5 … C-7 limits;
- the draft packet's structure and its "DRAFT — NOT AUTHORIZED" marking;
- the register's completeness;
- the append-only edits (24 commits, 0 merge commits).

It raised 2 MAJOR, 3 MINOR and 1 NOTE findings. **No classification in the P1–P9 matrix changes because of them**; they concern proposed acceptance criteria and wording.

**I-23 §10 stop rule:** the findings are recorded, reproduced and given proposed dispositions here. **No correction is applied and no Review 02 is started** without authorization.

## Findings

### M3T2R-R1-F1 — "Continuity through 1000 km" contradicts the pinned table
**Severity:** MAJOR (Codex scale) ≈ High (template scale)  
**Reviewer claim:** strategy U-15 and §3.5, and packet P5 item 8, require continuity at 1000 km. The pinned table jumps there, and DR-0024 Q5a forbids altering values to force continuity.  
**Evidence (reproduced by the implementer):** the 900 km band's left limit at 1000 km is `3.0190482489066533e-15`, against the 1000 km row's `3.019e-15`. The relative jump is −1.598149571502283e-5. DR-0029 P1 (line 86) already lists 1000 km among the 12 downward jumps.  
**Affected:** `M3-T2-validation-strategy.md` U-15 and §3.5; packet P5 items 7–8 and 14. The wording is inherited from DR-0029 P5's table cell "(continuous, GMAT-identical)", which means continuous *within* the top band above its base.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** the claim is correct. Requiring continuity at the base would contradict DR-0024 Q5a.  
**Proposed resolution (not applied):**
- U-15 and the packet P5 rows test the documented −1.598e-5 jump and the band selection at 1000 km ±1 ulp, like every other base.
- They separately test the smoothness of the top band's formula above 1000 km.
- A note is appended to DR-0029 saying that P5's "continuous" means within the top band. The accepted text is not rewritten.

### M3T2R-R1-F2 — E1 is reused beyond its proven domain
**Severity:** MAJOR ≈ High  
**Reviewer claim:** the packet's P8 acceptance criterion (item 14) and strategy U-17/U-18 apply E1's ε_h to forward-constructed points over −10 km … 2000 km. E1 is derived for exterior points (true height ≥ 0) and for the inverse's evaluation error only. It does not include the rounding of the forward construction, or the error of the reference.  
**Evidence (reproduced):** the committed `t0_termination_results.json`, `floating_point_enclosure/assumptions/domain`, reads "true geodetic height >= 0 (outside the ellipsoid), no overflow".  
**Affected:** packet P8 item 14; strategy U-17, U-18, PM-5.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** the criterion overstated E1's coverage. It is the same error class as the T0 lessons "state the domain of every guarantee" and "a bound for exact arguments does not bound computed ones".  
**Proposed resolution (not applied):**
- E1 is used only for h ≥ 0, and only for the inverse's error.
- The forward-construction error and the reference-evaluation error are derived as separate terms, which becomes a T2 deliverable.
- Negative heights (−10 km … 0) are reported, not gated, until a bound is derived for them.

### M3T2R-R1-F3 — "Strictly decreasing" density is false in binary64
**Severity:** MINOR ≈ Medium  
**Reviewer claim:** PM-4's strict decrease fails for adjacent binary64 inputs and in the zero tail.  
**Evidence (reproduced):** `density(1.0) == density(nextafter(1.0, +inf))` is `True`, and `density(192000000) = density(192000001) = 0.0`.  
**Implementer disposition:** `ACCEPTED`  
**Proposed resolution (not applied):** test non-increase for general inputs inside a band. Require strict decrease only for inputs whose exact difference exceeds a derived rounding allowance.

### M3T2R-R1-F4 — Lower-edge specification: a typo and a portability trap
**Severity:** MINOR ≈ Medium  
**Reviewer claim:**
1. Packet P4 item 8 lists "0 m" among the raising cases and then says 0 m evaluates band 0.
2. Copying the spike's km-route guard verbatim fails at the smallest negative input.

**Evidence (reproduced):** `density(-5e-324)` returns `1.225`, because −5e-324/1000 rounds to −0.0 before the negativity check.  
**Affected:** packet P4 items 8 and 14; N-1 path (α); draft packet DQ-2; strategy U-14.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** both points are correct. The second is a real defect in the T0 *spike's* domain guard, which is test code. It is outside every derived floor, which assumes h ≥ 0, so no T0 result changes. It does mean path (α) must not copy the guard.  
**Proposed resolution (not applied):**
- Remove "0 m" from the raising list.
- Specify the guard as finite h_m < 0 in metres, applied before the km conversion.
- DQ-1/DQ-2 state that this guard correction leaves the exterior arithmetic covered by the floors unchanged.
- The T0 records are not edited. A note is appended to VAL-0019, if the owner wants the spike's behaviour recorded.

### M3T2R-R1-F5 — "h(t) is C² outside the ellipsoid" is false across band edges
**Severity:** MINOR ≈ Medium  
**Reviewer claim:** packet P2 item 5. The discontinuous density makes ḧ jump at band crossings, so h is only piecewise C².  
**Evidence:** DR-0025 Resolution principle 5; DR-0029 P1 (the 12 downward jumps).  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** correct, as an assumption statement. The *certified* bound in DR-0029 P2 is two-body only, where h is smooth, so no certified number changes. The packet's general wording was wrong.  
**Proposed resolution (not applied):** state piecewise smoothness. The chord bound then holds with sup ḧ⁺ taken almost everywhere, since h is C¹ with a bounded, piecewise-continuous ḧ. Keep the statement that no perturbed-motion bound exists.

### M3T2R-R1-F6 — Bounds named but not yet derived; zero cases unstated
**Severity:** NOTE ≈ Low  
**Reviewer claim:** some strategy rows name a "γ-bound" or "truncation bound stated" without an operation count (for example U-4, U-7, U-21, PM-2). Some exact-sign rows need nonzero-force sample domains; for example, U-4's strict a_d·v_rel < 0 fails at zero relative velocity or zero density.  
**Implementer disposition:** `ACCEPTED`  
**Proposed resolution (not applied):** mark those derivations as T2 deliverables to be reviewed before acceptance, and state each row's admissible sample domain and zero cases.

## Effect on the I-23 deliverables
- **Unchanged:**
  - the P1–P9 classifications;
  - the governing-gate statement;
  - N-1 … N-7;
  - the recommendations;
  - the draft packet's preconditions, scope, protected paths and stop conditions.
- **Affected (corrections proposed, not applied):**
  - `M3-T2-validation-strategy.md`: U-4, U-7, U-14, U-15, U-17, U-18, U-21, PM-2, PM-4, PM-5, §3.5;
  - packet P2 item 5; P4 items 8 and 14; P5 items 7, 8 and 14; P8 item 14;
  - draft packet DQ-1/DQ-2 wording.
- **Records the owner may want appended:** a DR-0029 P5 clarification (F1), and optionally a VAL-0019 note on the spike's −5e-324 guard (F4).

## Proof gate
- [ ] All Critical findings resolved: none raised
- [ ] All High findings resolved: **F1 and F2 (MAJOR) ACCEPTED, not applied**
- [x] Every substantive finding has an explicit disposition
- [ ] Accepted fixes have been re-tested: no fix applied
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none escalated

**Review gate result: BLOCKED**, pending owner authorization of the corrections. This is a planning package, not a Proof. It means the package should not be used as the basis of a T2 authorization until F1 and F2 are corrected.
