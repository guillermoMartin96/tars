# M3 owner-decision recording: I-28-C1 correction (I-29)

- **Authority:** "TARS — Authorization I-29: M3 Owner Decisions: I-28-C1 Correction and Independent Closure Review" (owner/Tech Lead, 2026-10-25).
- **Base:** `1f2ce7e9b7a3d2fe243b79cf4eb099e792cad15e` (branch `milestone-3-t2-owner-decisions`).
- **Finding record:** `docs/reviews/M3-T2-owner-decisions-review-02-corrections.md`, section "Full search (I-28 §2) and the STOP finding" (unchanged).
- **Scope:** documentation only, append-only. **No owner decision is added or changed.**

## Baseline (I-29 §1)
| Check | Result |
|---|---|
| HEAD = remote = `1f2ce7e9…d15e`; local branch `m3-t2-owner-decisions-972e4c7c`, upstream `origin/milestone-3-t2-owner-decisions` | Yes |
| `origin/main` = `fc50aed5…4942`, an ancestor of HEAD | Yes |
| Worktree clean | Yes (0 entries) |
| Review 02 verdict | `VERDICT: PASS`, two MINOR findings (R2-F1, R2-F2) |
| Evidence checksums: I-26 probe, Review 01, I-27, Review 02, I-28 | OK (all `shasum -a 256 -c`) |
| Correction commits and CI | `f3ae387` (I-27), `1f2ce7e` (I-28). CI green on `f3ae387` (40220372068), `45f80f8` (40220636738) and `1f2ce7e` (40261200936), all four jobs |
| Files outside `docs/` changed since `fc50aed` | 0 |

## Correction
| Finding | Location | Correction (append-only) |
|---|---|---|
| **M3T2OD-I28-C1** (MINOR) | `docs/decisions/requests/DR-0029-m3-t0-proposals.md`, P2. The heading "**Proposed outcome and fields** (names remain proposals until the v3 contract is designed at T3, DR-0027 A):" and its list, which starts "- outcome `reentry` (DR-0026 §5.6);" (lines 221–227, unchanged) | A new block "**I-29 correction (2026-10-25, append-only; M3T2OD-I28-C1).**" inserted immediately after the list (line 229, after one blank line) and before "**Risks**". It states items 1–6 below. One entry is appended to the DR-0029 Resolution log |

The block states:
1. The outcome name `reentry` is DECIDED under I-26.
2. The precedence `non_finite` → `reentry` → `impact` → `escape` is DECIDED.
3. T3 implements these decisions; it does not reopen them.
4. The other event field names (`termination_altitude_m`, `crossing_t_s`, the method identifier), the event payload details and serialization remain T3 design responsibilities, within the approved contract.
5. Any change to the decided outcome name or precedence requires a new owner decision.
6. The heading's wording is superseded only insofar as it describes `reentry` as provisional. P2's decided A5-b crossing behaviour is unchanged.

**Preserved:**
- The heading and list are byte-identical to `1f2ce7e`.
- With the inserted lines removed, DR-0029 equals `1f2ce7e` exactly. P1–P9, the Q-GATE block and the DQ blocks are untouched.
- No other decision document changed.

**Line references:** line numbers cited in the I-27 and I-28 records refer to their own commits. In DR-0029, everything after line 227 now sits 8 lines lower; for example, the I-28 record's "line 252" is now line 260. Those records are not rewritten.

## Findings status (pending the closure review)
| Finding | Corrected in | Verified here |
|---|---|---|
| M3T2OD-R2-F1 | I-28, `1f2ce7e` | Both T0-matrix markers present; the T0 matrix is unchanged since `1f2ce7e` |
| M3T2OD-R2-F2 | I-28, `1f2ce7e` | Re-derived. `git diff --check a22297d f3ae387` exits 2 and flags exactly the four lines the I-28 note lists. `self_validation.out:31` is the file's only trailing-whitespace line, ending in exactly one space. The I-27 evidence checksums verify |
| M3T2OD-I28-C1 | I-29, this commit | Marker present immediately after the list; all six required statements present |

## Full-context search (I-29 §3)
The search covered all 24 documents: DR-0024 … DR-0029 with their packets and briefing, ADR-0009, `docs/milestones/M3-*` and `README.md`. For each `reentry` mention, the search context is the whole contiguous paragraph, list or table block containing it, plus ±4 lines. That covers headings separated from their list items.
- **Criteria:** a line is a hit if it combines open or provisional wording with an outcome, name or precedence subject, and has no supersession or DECIDED marker.
- **Classification:** every hit is classified by file and a text fingerprint, so line shifts do not matter, and an unclassified hit fails the check.
- **Result:** no unclassified hit, and no further contradiction. Each remaining historical reference is one of the following:
  - consistent (states DECIDED, or is a review-history entry or false positive);
  - historical question or recommendation text that the record answers;
  - explicitly superseded (DR-0027 "Names" row by the I-26/I-27 transition row; DR-0029 P2 list by the I-29 block).

The output is in the evidence, check [4].

## Consistency audit
| # | Item | Result |
|---|---|---|
| 1 | P1–P5, P7–P9 | DECIDED (Resolution rows unchanged) |
| 2 | P6 | NOT FULLY DECIDED: (d) PROVISIONALLY SELECTED; geodetic drag ESCALATED_FOR_INVESTIGATION |
| 3 | DR-0028 P6(b) | OPEN (ruling packet: "Nothing here is decided") |
| 4 | Q-GATE, DQ-1 … DQ-6 | Unchanged, byte-identical to `a22297d` |
| 5 | RM-3b | Unmeasured T4 candidate (I-27 text unchanged) |
| 6 | Conditional numerical accuracy tests (A-FP-2, A-LM-1, A-LM-2) | Report-only (packet r1 §6.2 byte-identical to `a22297d`) |
| 7 | Historical review records and raw evidence | Every file under `docs/reviews/` at `1f2ce7e` is byte-identical; all checksums verify |
| 8 | Scope | Documentation only; no protected path changed |

**Self-validation:**
- **Evidence directory:** `docs/reviews/raw/M3-T2-owner-decisions-I29-evidence/`.
- **Contents:** `self_validation.py.txt`, `self_validation.out` and `SHA256SUMS`.
- **Whitespace check:** check [9] records the exit status of `git diff --cached --check 1f2ce7e` exactly as returned.

- *(2026-10-25, append-only)* **Independent closure review (Codex, at `69aa2e6`): PASS**, with no finding at any severity. R2-F1, R2-F2 and I-28-C1 are confirmed RESOLVED. Record: `docs/reviews/M3-T2-owner-decisions-review-closure.md`. Nothing is accepted or authorized by the PASS.
