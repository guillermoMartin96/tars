# External Review: M3 owner-decision recording, Review 02 (after the I-27 corrections)

**Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17447-233f-7e41-9a36-22902a0964d2`. The reviewer is from a separate provider from the implementer, in a session separate from Review 01.  
**Date:** 2026-10-25  
**Reviewed revision:** `f3ae3876825b2966faaced3281f638b6271572ad`, focused on `a22297d..f3ae387`, on branch `milestone-3-t2-owner-decisions`. `main` = `fc50aed`.  
**Authorization:** I-27 §8 (owner/Tech Lead, 2026-10-25).  
**Raw records:**
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review02-prompt.md`, which contains I-27, I-26 and the Review 01 findings, all verbatim;
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review02.md`, verbatim;
- `docs/reviews/raw/M3-T2-owner-decisions-codex-review02-evidence/`: `review02.py.txt` (the reviewer's script), `review02.out` (a rerun of that script by the implementer in the same pinned clone) and `SHA256SUMS`.

**How it was run:** a fresh clone pinned at the full SHA; `uv sync --locked`; `review_scratch/` excluded from git; `codex exec -s workspace-write`; no network. The tracked tree was clean afterwards.

## Summary
**`VERDICT: PASS`.** There is no BLOCKER or MAJOR finding. Two MINOR findings are reproduced and **ACCEPTED, but not applied**: I-27 authorizes no further correction pass (§8, §11).

| Item (I-27 §8) | Reviewer's result |
|---|---|
| 1. R1-F1 | **Substantively resolved.** The five clarifications are established (DR-0029 P3), DR-0026 and DR-0027 are superseded in place (DR-0027 for the outcome name only), and OI-23's resolution is justified. The local marking is incomplete in two historical cells (R2-F1), so the reviewer labels it PARTIALLY RESOLVED, MINOR |
| 2. R1-F2 | **RESOLVED.** RM-3b is an unmeasured T4 candidate: not a result and not a gate. Leaving the pre-I-26 recommendation text unchanged is appropriate |
| 3. New inconsistencies | R2-F1 and R2-F2 only (MINOR) |
| 4. I-26 decisions | Faithful. P1–P5 and P7–P9 are DECIDED; the owner blockquotes and Resolution rows are byte-identical to `a22297d` |
| 5. P6 | Unresolved: (d) PROVISIONALLY SELECTED; ESCALATED; P6(b) OPEN; X-1 and the geodetic GMAT gate NOT AUTHORIZED |
| 6. Q-GATE, DQ, floating-point policy | Unchanged. Packet r1 and the validation strategy are byte-identical to the parent |
| 7. P8 limitation | "No change" was correct. U-17, U-19 (c), PM-5, PM-6 and U-18 are report-only; U-20 and the structural gates are unconditional; no tolerance is introduced; T0 agreement is not independent validation |
| 8. Scope | 12 files, all under `docs/`; append-only; no historical record or protected path changed |

## Findings and dispositions
| ID | Severity | Finding (reviewer) | Reproduction (implementer) | Disposition | Proposed correction (not applied) |
|---|---|---|---|---|---|
| M3T2OD-R2-F1 | MINOR | Two historical cells in `docs/milestones/M3-T0-decision-matrix.md` still describe `reentry` as a T3 proposal, with no in-place supersession marker | **Reproduced.** Line 14 (P2 row): "Event names (`reentry`, fields) remain T3 contract proposals". Line 27 (reconciliation table): "The names `altitude_floor_m` and `reentry` remain proposals until the v3 schema (T3)". Both are pre-I-26 text, from T0 commit `bdcaacf`. The same file's I-27 note states that `reentry` is DECIDED, so the governing record is unambiguous. **Root cause:** the I-27 self-validation scanned only lines added in I-26 and I-27, so it missed pre-existing statements that the decision superseded | **ACCEPTED** | Append in-cell markers to both cells: "`reentry` DECIDED (I-26 P3; DR-0029 P3, I-27 correction); field names remain T3 design within the approved contract". Extend any future supersession check to pre-existing lines |
| M3T2OD-R2-F2 | MINOR | The correction record says `git diff --check` reports only Markdown hard breaks, but `self_validation.out:31` also has a trailing space | **Reproduced.** `git diff --check a22297d f3ae387` flags lines 3–5 of the correction record (Markdown hard breaks, intended) and line 31 of `self_validation.out`. The space comes from the script truncating a label to 45 characters (`a[:45]`), which ended on a space. That is not a Markdown hard break, so the record's statement is inaccurate | **ACCEPTED** | Append a note to the correction record that states the diagnostic accurately. The evidence file is kept unchanged, because its checksum is pinned |

Neither finding changes a decision, a status, a gate or a classification.

## Proof gate
- [x] All Critical findings resolved: none raised
- [x] All High findings resolved: none raised. Review 01's MAJOR finding (R1-F1) is resolved in substance, and the reviewer confirmed it
- [x] Every substantive finding has an explicit disposition: R2-F1 and R2-F2 are ACCEPTED (MINOR, not applied)
- [x] Accepted fixes re-tested: the I-27 corrections were re-tested by this independent review, with its own computations
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: P6's geodetic-drag item remains ESCALATED_FOR_INVESTIGATION

**Review gate result: PASS.** The two MINOR findings remain open as documented traceability defects for the owner to disposition. **The PASS accepts no decision package, approves no assumption, and authorizes no implementation, merge or investigation.**
