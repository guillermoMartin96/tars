# M3 owner-decision recording: Review 01 corrections (I-27)

**Authority:** "TARS — Authorization I-27: M3 Owner Decisions: Review 01 Corrections and Independent Review 02" (owner/Tech Lead, 2026-10-25).  
**Base:** `a22297d1ec719a58aeb7209f3d34256fa7b0756a` (branch `milestone-3-t2-owner-decisions`). Review 01 reviewed `2cd1e6e`.  
**Findings record:** `docs/reviews/M3-T2-owner-decisions-review-01.md` (unchanged).  
**Scope:** documentation only, append-only. **No owner decision is added or changed.**

## Baseline (I-27 §1)
| Check | Result |
|---|---|
| HEAD = remote = `a22297d1…6a0756a`; local branch `m3-t2-owner-decisions-972e4c7c` | Yes |
| `origin/main` = `fc50aed5…4942`; `a57de3f` and `main` are ancestors of HEAD (linear) | Yes |
| Worktree clean | Yes (0 entries) |
| I-26 changes documentation only | Yes (0 files outside `docs/` in `a57de3f..a22297d`) |
| Evidence checksums: the I-26 probe and the Review 01 evidence | OK (all `shasum -c`) |
| CI | Green on `a57de3f` (40209939903), `2cd1e6e` (40211118324) and `a22297d` (40211666223), all four jobs |
| Findings reproduced | F1: `reentry` deferred at DR-0029 (P3 note), DR-0027 (Names row), DR-0026 (§5.6 row) and OI-23. F2: DR-0029 P7 note "measured candidate" against the table's "Not run" |

## Correction matrix
| Finding | Location | Correction (append-only) |
|---|---|---|
| **M3T2OD-R1-F1** (MAJOR) | DR-0029 P3 | New "I-27 correction" block establishing I-27 §2 items 1–5: `reentry` DECIDED; precedence DECIDED; T3 implements and does not reconfirm; T3 defines fields and serialization only within the approved contract; any change needs a separate owner decision. The superseded note sentence is marked in place and kept |
| | DR-0027 "I-26 note", "Names" row | In-cell marker: the outcome name is DECIDED, superseding A's "Names" row **for the outcome name only**. Field names (including `altitude_floor_m`) remain T3 design within the contract |
| | DR-0026 "I-26 note", §5.6 row | In-cell marker: `reentry` DECIDED; T3 implements, not reconfirms |
| | Open-issues register OI-23 | In-cell marker, plus an I-27 status update: **RESOLVED**. OI-23's whole scope was the outcome identifier, so no remaining scope needs preserving |
| | `M3-decision-matrix.md`, `M3-T0-decision-matrix.md` (dependency matrix) | I-27 notes. The P3 resolution and the dependency matrix agree, and "T3 precedence" means implementation |
| **M3T2OD-R1-F2** (MINOR) | DR-0029 P7 | New "I-27 correction" block: **RM-3b is an unmeasured candidate for evaluation during T4**; not an accepted reference result; no measurement completed; not a mandatory gate; promotion needs evidence, review and authorization. The superseded note sentence is marked in place and kept |
| | DR-0025 "I-26 note", Q-G2-5 cell; owner briefing answer row 7 | In-cell clarifications. Their "measured in T4" wording, added in I-26, could be read as a completed measurement, so they now say "unmeasured" (directly related documentary inconsistency, I-27 §6) |
| | Open-issues register OI-9; matrices | I-27 notes |
| Log | DR-0029 Resolution | An I-27 corrections entry |

**Left unchanged on purpose:**
- **Pre-I-26 recommendation text** ("RM-3b measured in T4" in the decision packet §1 and P7 item 12, and in the briefing §1). It is historical proposal text in the future sense, not a claim of measurement.
- **Packet r1 §10** ("T3: … `reentry` and the P3 precedence"). It lists implementation excluded from T2, so it does not contradict the decision.
- **Packet r1 P8 limitation (I-27 §5).** It already matches the policy:
  - U-17 (exact answers with ε_h), U-19 (c), PM-5, PM-6 and U-18 are A-FP-2-conditional and report-only;
  - U-20 domain rejection is an unconditional gate;
  - the T0 bitwise comparison (X-D1) is "supporting, reported", and the strategy classes it P, not independent;
  - no tolerance is introduced.

  **No change.**

## Self-validation (I-27 §4, §7)
Results are in `docs/reviews/raw/M3-T2-owner-decisions-I27-evidence/self_validation.out`. They cover:
1. no remaining statement that `reentry` is open, proposed or awaiting confirmation, except where a marker supersedes it;
2. no RM-3b statement in I-26/I-27 text that claims a measurement, certification, acceptance or a gate;
3. P1–P9 status rows unchanged;
4. Q-GATE, DQ-1 … DQ-6 and the floating-point policy blocks byte-identical to `a22297d`;
5. append-only against `a22297d`;
6. docs only, with no protected path changed;
7. links resolve;
8. `git diff --check` reports only the Markdown hard breaks.

- *(2026-10-25, append-only)* **Independent Review 02 (Codex, at `f3ae387`): PASS**, with no BLOCKER or MAJOR finding. Two MINOR findings are ACCEPTED and **not applied** (I-27 §11): M3T2OD-R2-F1, two pre-I-26 cells in `M3-T0-decision-matrix.md` (lines 14 and 27) still call `reentry` a proposal without an in-place marker; M3T2OD-R2-F2, the `git diff --check` description in the I-27 correction record omits a trailing space in `self_validation.out:31`. Record: `docs/reviews/M3-T2-owner-decisions-review-02.md`. Nothing is approved by the PASS.
- *(2026-10-25, append-only)* **I-28 correction (M3T2OD-R2-F2).** Self-validation item 8 above ("`git diff --check` reports only the Markdown hard breaks") is inaccurate and is kept as written. `git diff --check a22297d f3ae387` reports four lines, exit status 2: lines 3–5 of this record (Markdown hard breaks, intended) **and line 31 of `raw/M3-T2-owner-decisions-I27-evidence/self_validation.out`**, which ends in one space character. Cause, verified: the self-validation script prints each compared block's label truncated to 45 characters (`a[:45]`, script line 46), and the DR-0025 label "**Owner policy on conditional floating-point gates" is cut just after a space. The truncation affects the printed label only: the comparison uses the full blocks (`same = old == new`), so the "[3] identical" result and the interpretation of the evidence are unaffected. The evidence file is preserved unchanged; its checksum is pinned in `SHA256SUMS` and still verifies. The fresh check is recorded in `M3-T2-owner-decisions-review-02-corrections.md`.
