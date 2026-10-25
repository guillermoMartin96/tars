# M3 T2 decision-readiness package: corrections of Review 02 (I-25)

**Authorization:** "Authorization I-25 — M3 T2 Decision Readiness: Review 02 Corrections and Independent Review 03" (Tech Lead, 2026-10-24). Scope: documentation only; no new numerical experiment.  
**Base:** `e769f9e24dcf619119c9c5d27ca70423e279bfc0` (branch `milestone-3-t2-decision-readiness`; `main` = `fc50aed`).  
**Findings corrected:** `docs/reviews/M3-T2-readiness-review-02.md`. That record and its raw files are **unchanged**. The wording it reviewed is preserved at `f44a94f`.

## Baseline verification (I-25 §1)
| Check | Result |
|---|---|
| `git fetch origin`; branch | local `tars-m3-t2-readiness-853e0447`, tracking and equal to `origin/milestone-3-t2-decision-readiness` |
| HEAD = remote | `e769f9e` = `e769f9e` |
| `origin/main` | `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942` |
| Worktree | clean |
| Review 02 record and evidence | read in full; `SHA256SUMS` verifies |
| Findings against their reproductions | the recorded `implementer_r2_reproduction.py.txt` was re-run read-only (`python -I`). Its output is **identical** to the committed `.out` |
| Protected paths | `git diff --name-only fc50aed..e769f9e` touches `docs/` only |

No precondition failed.

## Correction matrix
| Finding | Severity | Correction | Where | Evidence and derivation | What is preserved |
|---|---|---|---|---|---|
| M3T2R-R2-F1 | MAJOR | The I-24 text gated exact z-reflection equality on A-LM-1. That needed cos evenness as well, which no assumption covered. It is now split into three parts. (a) **Exact quarter-turn equality:** conditional on A-LM-1, narrowed to hypot symmetry and evenness, which is all it uses. (b) **Exact z-reflection equality: diagnostic, reported, never gated.** (c) **Bounded comparison** \|ĥ(r) − ĥ(σr)\| ≤ 2ε_h(h): conditional on A-FP-2, exterior points, path (α). The withdrawn oddness of sin and atan2 and the evenness of cos are listed as **not assumed**. A-FP-2 is not strengthened | Strategy U-19, A-LM-1, B-11; briefing closing note | (c) is derived from E1: σ is exact in binary64 and a symmetry of the ellipsoid, so h_true(σr) = h_true(r), and the triangle inequality applies with E1 at each point. The R2-F1 perturbation (9.3e-10 m) lies inside 2ε_h (≈ 1.8e-8 m at 120 km), consistent with the bound | Mathematical symmetry is stated separately from computed behaviour. No tolerance invented. General rotations are still a Deliverable (B-5) |
| M3T2R-R2-F2 | MAJOR | PM-4 (b), strict decrease, is now **reported only**. B-9 is split: (i) E3 as an **upper** enclosure (U-13, conditional on A-FP-2); (ii) strict decrease, a **Deliverable** that gates only after a reviewed two-sided derivation and explicit authorization. U-13 is stated as one-sided. G-T2-2 lists PM-4 (b) as reported | Strategy PM-4, U-13, B-9, G-T2-2 | E3 (`t0_termination.rounding_allowances`) contains only "rho^ <= …" (Review 02 evidence). No lower bound is inferred from E3 or from samples | PM-4 (a), non-increase under A-LM-2. The mathematical strict monotonicity of the exact formula, stated as mathematics |
| M3T2R-R2-F3 | MINOR | −2.475e-321 is described as the **smallest-magnitude** negative input whose quotient by 1000 is nonzero, the quotient rounding to −5e-324 | Packet P4 item 8 | Review 02 evidence: −2.475e-321/1000 and −4.94e-321/1000 both give −5e-324; −7.41e-321/1000 gives −1e-323. A word diff shows a wording-only change | Trap interval (−2.475e-321, 0); metres-first guard; −0.0 in the domain; U-14 and P4 item 14 tests; I-24 evidence |

## Consistency audit (I-25 §3)
1. **References searched** across the packet, briefing, strategy, draft packet, readiness report and register: U-19, PM-4, B-9, B-11, A-LM-1, A-LM-2, E3, −2.475e-321, "strict", "reflection", "odd", "even".
   - Remaining hits on the old wording are in historical correction logs and Review status notes, which describe earlier states.
   - The I-24 F3 log entry is marked as superseded for PM-4 (b).
2. **No contradictory unconditional gate remains.**
   - The Gate rows are U-4/PM-1 (B-1), U-5/PM-3 (B-2), U-12 (B-13), the "no exception" part of U-16 (B-14) and B-15 on its domain, together with the exact (E) rows of §3.9.
   - Neither exact z-reflection nor strict decrease gates in any form.
3. **Draft authorization packet vs strategy:**
   - §6's conditional assumptions (A-FP-2, A-LM-1, A-LM-2) are still accurate;
   - G-T2-1 … G-T2-3a are referenced unchanged;
   - an append-only note was added; no substantive change was needed.
4. **The decision packet approves no numerical assumption.** It contains no A-LM reference outside the Review 02 status note. P8 item 14 states that E1 rests on A-FP-2. Every conditional row defers to the T2 authorization.
5. **Review 01 findings stay resolved.**
   - F1, F2, F4 and F5 text is untouched.
   - F3 (non-increase) is untouched; only its strict part is now reported.
   - F6's classification scheme is unchanged, with B-9 and B-11 reclassified within it.
6. **P1–P9 classifications are unchanged:**
   - READY FOR OWNER DECISION: P1 (κ, v̂), P2, P4, P8, P9;
   - BLOCKED BY ANOTHER DECISION: P3 (P1), P5 (P4, P1), P7 (P1, P9);
   - NEEDS ADDITIONAL EVIDENCE: P6.
   - Q-GATE, DQ-1 … DQ-6 and the P6 investigation (X-1) stay open.

## Proof gate (this record)
- [x] Every Review 02 finding has a correction and a location
- [x] Documentation-only; no protected path; no new experiment; the existing reproduction was re-run read-only, writing nothing
- [x] No invented tolerance: the one new bound (B-11 (c)) is derived from the reviewed E1
- [ ] Independent Review 03: see `docs/reviews/M3-T2-readiness-review-03.md`
