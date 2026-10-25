# External Review: M3 T2 decision-readiness package, Review 02 (after I-24 corrections)

**Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17058-9d91-7fb2-b7f1-cf4be0ce15d4`. The reviewer is from a separate provider from the implementer and ran in a new session, separate from Review 01.  
**Date:** 2026-10-24  
**Reviewed revision:** `f44a94fb09101f99dc380eaf1cff701a217b79d0` (correction scope `d8270c2..f44a94f`; branch `milestone-3-t2-decision-readiness`; `main` = `fc50aed`)  
**Authorization:** I-24 §6 (Tech Lead, 2026-10-24).  
**Raw records:**
- `docs/reviews/raw/M3-T2-readiness-codex-review02-prompt.md`, which includes I-24 verbatim;
- `docs/reviews/raw/M3-T2-readiness-codex-review02.md`, verbatim. Its links to `review_scratch/` refer to the reviewer's clone; those files are copied into the evidence directory;
- `docs/reviews/raw/M3-T2-readiness-codex-review02-evidence/`, with `SHA256SUMS`. It holds the reviewer's scripts and outputs (`review02`, `thresholds02`, `symmetry02`) and the implementer's reproduction `implementer_r2_reproduction`. Python is stored as `.py.txt`.

**How it was run:** a fresh clone pinned at the full SHA, `uv sync --locked`, `review_scratch/` excluded from git, `codex exec -s workspace-write`, no network. The tracked tree was clean afterwards.

## Summary
**`VERDICT: REQUEST_CHANGES`**, with 2 MAJOR findings and 1 MINOR.

**Review 01 resolution, as the reviewer assessed it:**

| Finding | Status |
|---|---|
| F1 | RESOLVED |
| F2 | RESOLVED |
| F3 | PARTIALLY RESOLVED (see R2-F2) |
| F4 | RESOLVED (R2-F3 is wording only) |
| F5 | RESOLVED |
| F6 | PARTIALLY RESOLVED (B-9 and B-11; see R2-F1 and R2-F2) |

**The reviewer confirmed:**
- **Scope:** 11 files, all under `docs/`; the append-only prefixes are intact; the Review 01 records are unchanged; no protected path or T0 file is touched; the evidence checksums match.
- **Decisions still open:** P1–P9 are OPEN with unchanged classification. Q-GATE, DQ-1 … DQ-6, P6/X-1 and DR-0028 P6(b) are open. The draft packet is still "DRAFT — NOT AUTHORIZED", and the P5 amendment is only proposed.
- **The owner briefing:** complete against I-24 §3 items 1–7, and its threshold table was reproduced independently with Brent's method.
- **The new derivations:** B-1, B-2, B-10 and B-12 … B-15 are sound, and so are the related corrections to U-21, U-23, U-6 and U-16.

**Readiness:** the decision alternatives and classifications are usable. The package is not yet a fully validated planning package, because two conditional gates in the validation strategy lack a sufficient derivation.

**I-24 §6 stop rule:** the findings are reproduced and recorded here, each with a proposed disposition. **No correction is applied and Review 03 is not started** without authorization.

## Findings

### M3T2R-R2-F1 — z-reflection exactness also needs cos to be even
**Severity:** MAJOR  
**Location:** validation strategy U-19, assumption A-LM-1, §3.9 B-11; briefing, last paragraph (conditional assumptions).

**Reviewer claim:** the spike's final height p·cos(lat) + z·sin(lat) − a√(1 − e2 sin² lat) uses cos. Under z → −z, lat → −lat. A-LM-1 assumes hypot symmetry and the oddness of sin and atan2, but not cos(−x) = cos(x). B-11's claim that the operands are "identical up to sign" therefore does not follow from its stated assumptions.

**Evidence (reproduced by the implementer, `implementer_r2_reproduction.out`):**
- The `math.cos` call is at `t0_model.py:161`.
- Changing only cos(lat) by 2 ulp at φ = 0.6, h = 120 km, an error that A-FP-2 permits, changes the height by 9.313225746154785e-10 m.
- On this host the reflected height is equal at one test point. That is an observation, not a proof.

**Disposition:** `ACCEPTED`. The derivation omitted an operation.

**Proposed resolution (not applied):** extend A-LM-1 to include the evenness of cos, which IEEE 754 does not require. B-11, U-19 and the briefing's note on conditional rows then name it. The alternative is to report z-reflection until a bound is derived. Quarter turns are unaffected: they involve only hypot.

### M3T2R-R2-F2 — PM-4 (b)'s strict decrease cites a two-sided allowance that E3 does not provide
**Severity:** MAJOR  
**Location:** validation strategy PM-4 (b), §3.9 B-9, G-T2-2.

**Reviewer claim:** E3 is a **one-sided** enclosure, ρ̂ ≤ F_ρ e^η₀ ρ(h_s) exp(θ_x X) + N_ρ, at the rounded selection height h_s. PM-4 (b) needs a lower bound as well as an upper bound, relative to the exact formula at the input heights. It also needs the km-conversion error and the additive term, and E3 supplies neither as stated. Calling the criterion derived is unsupported.

**Evidence (reproduced):** the `rounding_allowances` docstring contains only "rho^ <= …" (`implementer_r2_reproduction.out`; `t0_termination.py` around lines 593–598). There is no lower enclosure.

**Disposition:** `ACCEPTED`. The I-24 text called "ε the E3 relative allowance" two-sided without checking that E3 is one-sided.

**Proposed resolution (not applied):** reclassify PM-4 (b) and B-9's strict-decrease part as **Deliverable**, reported until a two-sided, input-height-referenced bound is derived and reviewed. U-13's use of E3 as an upper enclosure stays Conditional (A-FP-2), and its wording should name the enclosure as upper-only. PM-4 (a), non-increase under A-LM-2, is retained.

### M3T2R-R2-F3 — wrong extremum wording for the first raising input
**Severity:** MINOR  
**Location:** decision packet P4 item 8, recorded T0 behaviour.

**Reviewer claim:** −2.475e-321 is the **smallest-magnitude** negative input whose quotient by 1000 is nonzero. It is not the "largest-magnitude negative h whose quotient is the smallest subnormal". Larger-magnitude inputs, such as −4.94e-321, also give a quotient of −5e-324.

**Evidence (reproduced):** −2.475e-321/1000 and −4.94e-321/1000 both give −5e-324, while −7.41e-321/1000 gives −1e-323.

**Disposition:** `ACCEPTED`.

**Proposed resolution (not applied):** correct the wording. The trap interval (−2.475e-321, 0), the proposed guard and the tests are unchanged.

### Reviewer note (not a finding)
B-15 (the bracket-width argument) needs the root brackets themselves. The committed T0 threshold JSON holds the estimates and residuals, not the final brackets. A T2 or T3 recomputation should retain its brackets. **Disposition:** ACCEPTED as a note for the T2/T3 deliverable; no change proposed now.

## Effect on the package
- **Unchanged:** the P1–P9 classifications and recommendations; the governing gate; Q-GATE; DQ-1 … DQ-6; the briefing's decision content.
- **Affected (corrections proposed, not applied):**
  - in the strategy: U-19, A-LM-1, B-11, PM-4 (b), B-9, U-13 wording, G-T2-2;
  - in the packet: P4 item 8 wording;
  - in the briefing: the closing note on conditional rows.
- None of the three findings changes a gate that would apply **unconditionally**. R2-F1 and R2-F2 concern Conditional rows, which gate only if the T2 authorization accepts their assumptions.

## Proof gate
- [ ] All Critical findings resolved: none raised
- [ ] All High findings resolved: **R2-F1 and R2-F2 (MAJOR) ACCEPTED, not applied**
- [x] Every substantive finding has an explicit disposition
- [ ] Accepted fixes have been re-tested: no fix applied
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none escalated

**Review gate result: BLOCKED**, pending the owner's authorization of the corrections. This is a planning package, not a Proof. Under I-24 §6 the pass stops here, and Review 03 needs separate authorization.
