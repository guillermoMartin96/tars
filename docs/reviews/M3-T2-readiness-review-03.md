# External Review: M3 T2 decision-readiness package, Review 03 (after I-25 corrections)

**Reviewer/model:** Codex (codex-cli 0.162.0), session `01a170c1-0083-7c72-baf3-5acf8f57bfc3`. The reviewer is from a separate provider from the implementer, in a session separate from Reviews 01 and 02.  
**Date:** 2026-10-24  
**Reviewed revision:** `628623bdb5fdaee5da4167167be914a68a1734a9` (focus `e769f9e..628623b`; branch `milestone-3-t2-decision-readiness`; `main` = `fc50aed`)  
**Authorization:** I-25 §5 (Tech Lead, 2026-10-24).  
**Raw records:**
- `docs/reviews/raw/M3-T2-readiness-codex-review03-prompt.md`, which includes I-25 verbatim;
- `docs/reviews/raw/M3-T2-readiness-codex-review03.md`, verbatim;
- `docs/reviews/raw/M3-T2-readiness-codex-review03-evidence/`, holding `review03.py.txt`, `review03.out` and `SHA256SUMS`.

**How it was run:** a fresh clone pinned at the full SHA, `uv sync --locked`, `review_scratch/` excluded from git, `codex exec -s workspace-write`, no network. The tracked tree was clean afterwards.

## Summary
**`VERDICT: PASS`. No findings (no BLOCKER, MAJOR, MINOR or NOTE).**

| Item (I-25 §5) | Reviewer's result |
|---|---|
| 1. R2-F1 | **RESOLVED.** The narrowed A-LM-1 (hypot symmetry and evenness) suffices for exact quarter-turn equality, because path (α) sees x and y only through `hypot`. Exact z-reflection is diagnostic, and A-FP-2 is not strengthened. B-11 (c) is valid: σ is exact (signed permutations, at subnormal magnitudes too), h_true(σr) = h_true(r), exteriority is preserved, and the substitution h ≤ (ĥ + β)/(1 − α) is conservative, since 0 < α < 1, β > 0 and ε_h is increasing |
| 2. R2-F2 | **RESOLVED.** E3 is used as an upper enclosure only, and no lower bound is inferred. Strict decrease is reported pending a reviewed two-sided derivation and authorization. Non-increase remains justified under A-LM-2 |
| 3. R2-F3 | **RESOLVED.** The change is to wording only. Independently: 500 negative binary64 values next to zero give a zero quotient, and the 501st, −2.475e-321, gives −5e-324 and raises. Interval, guard, signed zeros, tests and evidence are unchanged |
| 4. New errors | None found |
| 5. Gates justified | B-1, B-2, B-13, B-14 and B-15 rechecked. The B-15 premise still needs the retained brackets, as Review 02's note says. B-9 … B-12 now have derivations, named assumptions and domains, and B-3 … B-8 remain reported deliverables. No contradictory unconditional gate was found |
| 6. Earlier findings | Review 01 F1, F2, F4 and F5 stay closed. The remaining gaps in F3 and F6 are closed by these corrections |
| 7. Boundaries | 6 files, all under `docs/`. Historical records unchanged; append-only prefixes intact; no protected path or T0 file touched. P1–P9 classifications unchanged. Q-GATE, DQ-1 … DQ-6 and P6/X-1 open. The draft packet is still DRAFT — NOT AUTHORIZED |

**Reviewer's own computations** (`review03.out`):
- 2 000 sampled exterior points: 0 failures of quarter-turn equality and 0 of the bounded comparison. The largest reflected-height difference was 0 against 2ε_h(120 km) = 1.805e-8 m.
- The F1 and F4 figures reproduced.

The samples are corroboration only. The verdict rests on the derivations.

**Reviewer's limitations:**
- No network, so no authentication of CI or remote state, and no M1/M2 proof run.
- A-FP-2 and A-LM-0 … A-LM-2 remain **unproved and unapproved**, and cross-platform library behaviour is not established.

## Proof gate
- [x] All Critical findings resolved: none raised
- [x] All High findings resolved: none raised. Review 02 R2-F1 and R2-F2 are corrected, and this review confirmed them resolved
- [x] Every substantive finding has an explicit disposition: none raised in this review; Review 01 and Review 02 findings all corrected and confirmed
- [x] Accepted fixes re-tested: by an independent review with its own computations
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: P6's geodetic-drag item stays ESCALATED and is outside this package's gates

**Review gate result: PASS.** This is a planning package, not a Proof. **The PASS approves no DR-0029 decision, no assumption (A-FP-2, A-LM-0 … A-LM-2), no proposed amendment, and no T2 implementation.**
