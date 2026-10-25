# External Review: M3 owner-decision recording and reconciliation (I-26), Review 01

**Reviewer/model:** Codex (codex-cli 0.162.0), session `01a173dc-f9a3-7711-8b1a-d68f9f643f9f`. The reviewer is from a separate provider from the implementer, in a new session.  
**Date:** 2026-10-25  
**Reviewed revision:** `2cd1e6ec1bc2df13827c36d03fda5bf4b4150c09`. The focus was `a57de3f..2cd1e6e` on branch `milestone-3-t2-owner-decisions`; `main` = `fc50aed`.  
**Authorization:** I-26 §7 (owner/Tech Lead, 2026-10-25).  
**Raw records:**
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review01-prompt.md`, which includes I-26 verbatim;
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review01.md`, the final message, verbatim;
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review01-evidence/`, holding the full review `Review-01.md`, `check_review.py.txt`, `check_review.out` and `SHA256SUMS`.

**How it was run:** a fresh clone pinned at the full SHA, `uv sync --locked`, `review_scratch/` excluded from git, `codex exec -s workspace-write`, no network. The tracked tree was clean afterwards (0 entries in `git status --porcelain`).

## Summary
**`VERDICT: REQUEST_CHANGES`.** One MAJOR finding and one MINOR finding. Both are reproduced and **ACCEPTED, not applied** (I-26 §7: "record and reproduce the findings, then STOP. Do not begin an unapproved correction loop").

The reviewer found everything else in order:
- the verbatim fidelity of P1–P9, Q-GATE, DQ-1 … DQ-6 and the floating-point policy;
- P6 recorded as provisional only;
- the scope of the Q-GATE supersession;
- the path (α) and km-route operation specification, bitwise against T0 on 1003 geodetic and 89 density samples;
- the conditional-row register, including the U-23 reclassification;
- preserved contracts, no execution approval, and documentation-only append-only changes.

## Findings and dispositions
| ID | Severity | Finding (reviewer) | Reproduction (implementer) | Disposition | Proposed correction (not applied) |
|---|---|---|---|---|---|
| M3T2OD-R1-F1 | MAJOR | The reconciliation leaves the outcome identifier `reentry` open for T3 confirmation, although I-26 names it in the decided precedence. This narrows P3 | I-26 §2 P3 lists "2. `reentry`" in the decided precedence. The records that defer it are DR-0029 P3 implementer note (line 292), DR-0027 "I-26 note" row "Names" (line 146), DR-0026 "I-26 note" row "§5.6 outcome name `reentry`" (line 329), and the open-issues register OI-23 (line 55, "Open"). **Reproduced** | **ACCEPTED.** Deferring the *implementation* to T3 does not defer the owner's *choice* of the outcome in the precedence. The implementer's note added a qualification the owner's text does not contain | Append a reconciliation: `reentry` is the decided outcome identifier (I-26 P3) and supersedes DR-0027 A's "outcome name remains a proposal" for the outcome only. Field names (`altitude_floor_m`, `termination_altitude_m`, `crossing_t_s`, the method id) and schema details remain T3 design. Mark OI-23 RESOLVED |
| M3T2OD-R1-F2 | MINOR | "RM-3b is a measured candidate only" implies a completed measurement | DR-0029 P7 implementer note (line 526) says "measured candidate". The same section's table row (line 499) says "**Not run** (candidate only)", and I-26 says "a candidate to be measured during T4". **Reproduced** | **ACCEPTED.** Wording error; no decision changes | Append a clarification: RM-3b is an unmeasured candidate, to be measured in T4, and not a mandatory gate without later approval |

**Severity check:** F1 is MAJOR under the review's own guide ("a recorded decision that differs from the owner's text"). It does not affect T2's code: T2 implements no outcome or precedence (P3 is T3 behaviour). It does affect the T2 *authorization* precondition PC-3, "contracts recorded and reconciled", until it is corrected.

## Proof gate
- [x] All Critical findings resolved: none raised
- [ ] All High findings resolved: **M3T2OD-R1-F1 (MAJOR) is accepted but not corrected**
- [x] Every substantive finding has an explicit disposition: F1 and F2 are ACCEPTED
- [ ] Accepted fixes re-tested: corrections not authorized yet
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: P6's geodetic-drag item stays ESCALATED_FOR_INVESTIGATION

**Review gate result: REQUEST_CHANGES (open).** The I-26 reconciliation is not ready for the owner's checkpoint acceptance until F1 is corrected and re-reviewed, which needs separate authorization. **Nothing is approved by this review, and T2 is NOT AUTHORIZED.**
