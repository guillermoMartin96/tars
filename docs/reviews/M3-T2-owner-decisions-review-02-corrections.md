# M3 owner-decision recording: Review 02 corrections (I-28)

- **Authority:** "TARS — Authorization I-28: M3 Owner Decisions: Review 02 MINOR Corrections and Final Closure Review" (owner/Tech Lead, 2026-10-25).
- **Base:** `45f80f8523d1ed0033cf9f773d5072e719d4d442` (branch `milestone-3-t2-owner-decisions`). Review 02 reviewed `f3ae387`.
- **Findings record:** `docs/reviews/M3-T2-owner-decisions-review-02.md` (unchanged).
- **Scope:** documentation only, append-only. **No owner decision is added or changed.**
- **Outcome:** both authorized corrections are applied. The full search required by I-28 §2 found **one further contradiction outside the two authorized cells (M3T2OD-I28-C1, below)**. Following I-28 §2, it is documented, **not corrected**, and work **STOPS here**: the independent closure review (I-28 §5) has **not** been requested.

## Baseline (I-28 §1)
| Check | Result |
|---|---|
| HEAD = remote = `45f80f85…d442`; local branch `m3-t2-owner-decisions-972e4c7c`, upstream `origin/milestone-3-t2-owner-decisions` | Yes |
| `origin/main` = `fc50aed5…4942`, an ancestor of HEAD (fast-forward possible) | Yes |
| Worktree clean | Yes (0 entries) |
| Review 02 verdict and findings | `VERDICT: PASS` (raw output, line 1); M3T2OD-R2-F1 and M3T2OD-R2-F2, both MINOR |
| Evidence checksums: I-26 probe, Review 01, I-27 self-validation, Review 02 | OK (all `shasum -a 256 -c`) |
| CI | Green on `a57de3f` (40209939903), `2cd1e6e` (40211118324), `a22297d` (40211666223), `f3ae387` (40220372068) and `45f80f8` (40220636738) |
| Protected paths changed since `fc50aed` (accepted T1 baseline on `main`) | None; 0 files outside `docs/` |

## Correction matrix
| Finding | Location | Correction (append-only) |
|---|---|---|
| **M3T2OD-R2-F1** (MINOR) | `docs/milestones/M3-T0-decision-matrix.md` line 14 (P2 row, "Assumptions, limitations, risks" cell) | In-cell marker "Superseded in part by I-28 (M3T2OD-R2-F1)": the quoted sentence is kept as written; the outcome name `reentry` and the precedence `non_finite` → `reentry` → `impact` → `escape` are **DECIDED** (I-26 P3); T3 implements these contracts and does not decide them again; event field names remain T3 design, within the approved contract only. Points to DR-0029 P3, "I-27 correction" |
| | Same file, line 27 (reconciliation row "DR-0027 A-4, A-5, A-6") | The same marker, with "field names, including `altitude_floor_m`, remain T3 design" |
| **M3T2OD-R2-F2** (MINOR) | `docs/reviews/M3-T2-owner-decisions-review-01-corrections.md`, after the Review 02 entry | Appended "I-28 correction (M3T2OD-R2-F2)" note, detailed below. The raw evidence is preserved unchanged |

Both markers are pure insertions before the cell's closing `|`. Removing them restores the original lines byte for byte (self-validation check [1]). The outcome name, the precedence and every other P3 decision are unchanged.

### M3T2OD-R2-F2 in detail
- **Exact additional finding.** `git diff --check a22297d f3ae387` exits with status 2 and reports four lines. Three are lines 3–5 of the I-27 correction record, which are intended Markdown hard breaks. The fourth is `docs/reviews/raw/M3-T2-owner-decisions-I27-evidence/self_validation.out` line 31, which ends in a single space character (byte `0x20` before the newline).
- **Cause, verified independently.** The I-27 self-validation script prints each compared block's label truncated to 45 characters (`a[:45]`, line 46 of `self_validation.py.txt`). The DR-0025 label "**Owner policy on conditional floating-point gates" is cut directly after a space. No other line of that output file has trailing whitespace.
- **Effect on interpretation: none.** The result is computed on the full blocks (`same = old == new`, line 45) before printing. The truncated label only shortens what is displayed, so the "[3] identical" result stands.
- **Evidence preservation.** `self_validation.out` is not rewritten. Its checksum is pinned in `SHA256SUMS` and still verifies. No corrected copy is needed, because the content is accurate and only the description of the check was wrong.
- **Fresh whitespace check.** The output is in the I-28 evidence (check [7]):
  - `git diff --cached --check 45f80f8` covers the I-28 changes, before commit. Its exit status is recorded exactly as returned.
  - Over the whole range `a22297d..45f80f8`, the check still reports the historical lines. These are the hard breaks in the I-27 and Review 02 records, the hard breaks in the verbatim Codex output, and `self_validation.out:31`. They are preserved on purpose, so **that range is not clean** and is not claimed to be.
  - The I-28 self-validation prints right-stripped labels so that it cannot repeat the defect.

## Full search (I-28 §2) and the STOP finding
Every line of the 24 M3 decision documents was searched, including pre-existing lines. The documents are DR-0024 … DR-0029 with their packets and briefing, ADR-0009, the `docs/milestones/M3-*` documents and `README.md`. The search used two patterns: single-line matches, and a window of ±4 lines around each `reentry` mention. The window is there because a heading can carry the status while its list items carry the name, which a single-line search misses. Each unmarked hit is classified in the self-validation (check [2]).

**M3T2OD-I28-C1 (new; MINOR by the implementer's assessment, the same class as R2-F1; NOT corrected).**
- **Location:** `docs/decisions/requests/DR-0029-m3-t0-proposals.md` lines 221–222, P2 section, T0 text from commit `294e1f5` (2026-10-18).
- **Text:** "**Proposed outcome and fields** (names remain proposals until the v3 contract is designed at T3, DR-0027 A):", followed by "- outcome `reentry` (DR-0026 §5.6);".
- **Why it is a contradiction:** it lists the outcome name `reentry` among names that remain proposals until T3, and it has no in-place supersession marker.
- **Mitigation already in the record:**
  - The I-26 implementer note in the same section (line 252) narrows the "remain T3 contract proposals" statement to the field names.
  - The I-27 correction in P3 (lines 296–302) states that `reentry` is DECIDED, and supersedes DR-0027 A's "Names" row, which line 221 cites as its basis.
  - So the governing record is unambiguous, as Review 02 judged for R2-F1.
- **Why it was missed before:** Review 02 did not report it. The I-27 self-validation scanned only added lines, and a single-line search does not find it, because `reentry` is on the next line.
- **Proposed correction (not applied):** an in-cell or in-line marker after line 221 in the I-28 form ("Superseded in part …: the outcome name `reentry` is DECIDED …; field names remain T3 design within the approved contract").
- **Not a decision change:** it changes no decision, status or gate.
- **Why work stops:** I-28 §2 says "If another material contradiction is found, document it and STOP rather than expanding this authorization." It is in the authoritative decision record and is of the same kind as R2-F1, so the implementer treats it as material for that rule.

Examined and **not** treated as contradictions:
- **DR-0027 line 96** ("Names … remain proposals … | Proposals only"). It is superseded under the repository's transition convention. The I-26 note's "Names" row (line 146) names it, and carries the I-27 marker "superseding the 'Names' row of the A table above for the outcome name only".
- **`M3-T0-decision-matrix.md` line 41** ("DR-0026 contract (failure cause names) | Design at T3 | P2, P4 name candidates"). It does not name `reentry`. It stays accurate for names that are still T3 design, such as P4's domain-error cause name and the event field names.
- **`M3-T0-decision-matrix.md` line 15.** It holds the P3 options and recommendation columns ("single proposal", "As proposed"). It makes no claim about status, and the I-26 and I-27 notes in the same file transition P3.
- **The other hits:** historical question text (DR-0024 Q8; DR-0027 A-5; briefing P3 question, answered "Proposal accepted"), the pre-decision packet's preserved assessments, review-history log entries and false positives.

## Consistency audit (I-28 §4)
All 23 decision documents other than the T0 decision matrix are byte-identical to `45f80f8`. The T0 matrix change consists only of the two insertions (checks [1] and [3]). Therefore:

| # | Item | Result |
|---|---|---|
| 1 | P1–P5, P7–P9 | DECIDED (DR-0029 Resolution rows unchanged) |
| 2 | P6 | NOT FULLY DECIDED: (d) PROVISIONALLY SELECTED; geodetic drag ESCALATED_FOR_INVESTIGATION |
| 3 | DR-0028 P6(b) | OPEN: the ruling packet's status "Nothing here is decided" is unchanged |
| 4 | Q-GATE | Approved and unchanged |
| 5 | DQ-1 … DQ-6 | DECIDED and unchanged (packet r1 byte-identical) |
| 6 | Floating-point policy | Unchanged (DR-0025 and packet r1 byte-identical) |
| 7 | RM-3b | Unmeasured T4 candidate (the I-27 correction is present and unchanged) |
| 8 | P8 accuracy tests | Report-only where A-FP-2 is unjustified (packet r1 §6.2 unchanged) |
| 9 | Historical review evidence | Not rewritten: every file under `docs/reviews/` at `45f80f8` is byte-identical, except one append-only note in the I-27 correction record (check [4]) |
| 10 | New scientific or numerical decision | None |

**Self-validation:**
- **Evidence directory:** `docs/reviews/raw/M3-T2-owner-decisions-I28-evidence/`.
- **Contents:** `self_validation.py.txt`, `self_validation.out` and `SHA256SUMS`.
- **Coverage:** checks [1]–[7] cover the R2-F1 cells, the full search, the §4 audit, the immutability of historical evidence, the docs-only scope with no protected path, link resolution and the fresh whitespace check.

## Not done (I-28 §2 STOP)
- No independent closure review was requested, because the record is known to contain M3T2OD-I28-C1.
- M3T2OD-I28-C1 is not corrected.
- Nothing is accepted or merged. No T2 branch was created.
