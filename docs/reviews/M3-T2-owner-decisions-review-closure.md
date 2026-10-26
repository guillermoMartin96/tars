# External Review: M3 owner-decision recording, closure review (after I-28 and I-29)

- **Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17689-a302-76d1-bfe4-3feff72ad0de`. The reviewer is from a separate provider from the implementer, in a session separate from Reviews 01 and 02.
- **Date:** 2026-10-25
- **Reviewed revision:** `69aa2e69415aa10b97bfc9b609b6a4112278bfa1`, focused on `45f80f8..69aa2e6` (I-28 `1f2ce7e` and I-29 `69aa2e6`), on branch `milestone-3-t2-owner-decisions`. `main` = `fc50aed`.
- **Authorization:** I-29 §5 (owner/Tech Lead, 2026-10-25).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-owner-decisions-codex-closure-prompt.md`, which contains the Review 02 findings and I-29, I-28, I-27 and I-26, all verbatim;
  - `docs/reviews/raw/M3-T2-owner-decisions-codex-closure.md`, the verbatim output;
  - `docs/reviews/raw/M3-T2-owner-decisions-codex-closure-evidence/`, containing `audit.py.txt` (the reviewer's script), `audit.out` (the implementer's rerun of that script in the same pinned clone, byte-identical to the reviewer's own `audit.out`) and `SHA256SUMS`.
  - Two context dumps the reviewer wrote to its scratch directory (`contexts.txt`, `full-context.txt`, about 1 550 lines in total) are not committed.
- **How it was run:**
  - a fresh clone pinned at the full SHA;
  - `uv sync --locked`;
  - `review_scratch/` excluded from git;
  - `codex exec -s workspace-write`;
  - no network.

  The tracked tree was clean afterwards (0 entries in `git status --porcelain`).

## Summary
**`VERDICT: PASS`.** **No finding at any severity**: no BLOCKER, MAJOR, MINOR or NOTE.

| Item (I-29 §5) | Reviewer's result |
|---|---|
| 1. R2-F1 | **RESOLVED.** Both T0-matrix markers are present. Removing them restores the original lines byte for byte |
| 2. R2-F2 | **RESOLVED.** The I-28 note's description (exit 2, four lines, `a[:45]` cause, display only) is accurate. The fresh committed-range checks exit 0. The historical range still exits 2 and is not claimed clean |
| 3. I-28-C1 | **RESOLVED.** The block (DR-0029 lines 229–235) immediately follows the preserved P2 list (lines 221–227). It states all six I-29 §2 items. The DR changes are one 8-line insertion and one log line. A5-b and the P3 precedence are unchanged |
| 4. Further contradictions | None. The reviewer's own full-context search of the 24 documents agrees with the implementer's classifications. That includes DR-0027 line 96 and T0-matrix lines 15 and 41 |
| 5. Owner decisions | Preserved, as follows: P1–P5 and P7–P9 DECIDED; P6 NOT FULLY DECIDED; DR-0028 P6(b) OPEN; X-1 unauthorized; Q-GATE, DQ-1 … DQ-6 and the floating-point policy unchanged; RM-3b an unmeasured T4 candidate; conditional accuracy rows report-only |
| 6. Historical evidence | Preserved. The only changed review file is the append-only I-27 correction record; all 2 711 files present at `1f2ce7e` are unchanged; all six checksum manifests verify. The stated 8-line shift (old line 252 → 260) is correct |
| 7. Scope | 11 files, all under `docs/`; append-only; no protected path changed |
| 8. Readiness | "Ready for owner acceptance of the reconciliation" from the standpoint of documentation accuracy and consistency. Acceptance remains the owner's decision |

## Findings and dispositions
None were raised, so no disposition is required.

## Evidence notes
- **Reviewer's independent `git diff --check` results:**

  | Range | Exit | Output |
  |---|---|---|
  | `a22297d..f3ae387` | 2 | four lines |
  | `45f80f8..1f2ce7e` | 0 | none |
  | `1f2ce7e..69aa2e6` | 0 | none |
  | `45f80f8..69aa2e6` | 0 | none |
  | `a22297d..69aa2e6` | 2 | preserved historical whitespace |

- **Whitespace in this commit:** `audit.out` reproduces those diagnostics verbatim, including the quoted historical lines that end in Markdown hard-break spaces, and the verbatim raw output is kept as received. **`git diff --check` on this review commit therefore reports those quoted lines; its exit status is recorded in the I-29 checkpoint as returned.** The evidence is not altered to make the check pass.

## Proof gate
- [x] All Critical findings resolved: none raised
- [x] All High findings resolved: none raised
- [x] Every substantive finding has an explicit disposition: none raised; R2-F1, R2-F2 and I-28-C1 confirmed RESOLVED
- [x] Accepted fixes re-tested: the I-28 and I-29 corrections were re-tested by this independent review, with its own computations
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: P6's geodetic-drag item remains ESCALATED_FOR_INVESTIGATION

**Review gate result: PASS.** **The PASS accepts no decision package, approves no assumption, and authorizes no implementation, merge or investigation.**
