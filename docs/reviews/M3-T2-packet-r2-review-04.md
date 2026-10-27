# External Review: M3 T2 packet r2, Review 04 (closure review of the I-35 corrections)

- **Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17b90-6fa7-7271-b53d-6ebd5aff3b2b`. The reviewer is from a separate provider from the implementer, in a fresh session separate from Reviews 01–03.
- **Date:** 2026-10-26
- **Reviewed revision:** `154378c14f9eed0fbede53b48e4544079485694e`, the I-35 correction commit (`git diff d30e449..154378c`: six files, all under `docs/`), on branch `milestone-3-t2-authorization`.
- **Authorization:** I-35 §5 (owner/Tech Lead, 2026-10-26).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review04-prompt.md`: the prompt, with I-35 verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review04.md`: the **complete** final message, verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review04-evidence/`:
    - the reviewer's scripts and outputs: `independent` and `history`;
    - `reviewer_i35_checks.out`, which is byte-identical to the committed I-35 output;
    - `implementer_rerun.txt`;
    - `SHA256SUMS`.
  - **Not committed:**
    - the reviewer's copies of `i35_checks.py` and `pog_lib.py`, and its `pog_lib.out` usage note;
    - `__pycache__/`;
    - the JSONL event stream.
- **How it was run:**
  - a fresh clone pinned at the full SHA;
  - `uv sync --locked`;
  - `review_scratch/` excluded from git;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`;
  - no network.

  The tracked tree was clean afterwards, and HEAD was unchanged.
- **Timing:** the review was launched while CI for `154378c` was still running. CI status is reported in the I-35 checkpoint.

## Summary
**`VERDICT: PASS`.** 0 BLOCKER, 0 MAJOR, **1 MINOR**, 0 NOTE.

| Item | Review 04 |
|---|---|
| R3-F1, fingerprint field count | **CLOSED.** 47 full-path fields: 3 differ, 44 agree. 44 distinct leaf names. No value changed. One wording slip is raised as R4-F1 |
| R3-F2, Newton denominators | **CLOSED.** `_foot_point` uses a² + t and b² + t. The reviewer derived the ≈1.5× growth independently, from u′ ≈ (3/2)u − u³/(2C). It reproduces (2¹³⁸,)³ as non-converged but admissible (−0.288401), and (2¹³⁹,)³ as inadmissible (+0.274521, `ValueError`) |
| Fingerprint reporting | **Accurate.** `[U] unavailable` separates inaccessible metadata from a numerical validation failure. In this sandbox the reviewer's own three queries again returned exit status 1 with "Operation not permitted", and no CPU value was observed. Review 02's cause remains inferred and is not backfilled. The §7.1 rule is documentation-only |
| Provenance | **Preserved.** Each manifest verifies, and each file is byte-identical to its historical commit: I-33 (18/18), Review 02 (12/12), I-34A (5/5), Review 03 (11/11). The I-35 manifest (3/3) verifies, and its output reruns byte-identically |
| Closed items | R2-F1 … F3 remain resolved. Readiness M3T2R-R2-F1 … F3 remain closed |
| Scope, contradictions | No unauthorized expansion. No new substantive contradiction |

## Findings register and dispositions
Each disposition is the implementer's evaluation. **No correction is made.** I-35 does not authorize correcting new findings, and limits its scope to R3-F1, R3-F2 and fingerprint reporting.

| ID | Severity | Location | Finding | Implementer's reproduction | Disposition |
|---|---|---|---|---|---|
| M3T2P2-R4-F1 | MINOR | `docs/reviews/M3-T2-packet-r2-review-02-corrections.md:36` | "Three names repeat across sections" should say **two** repeated names. `note` appears 3 times and `[O] version` twice, so (3 − 1) + (2 − 1) = 3 paths collapse. The listed names and sections, and the 47/3/44 count, are correct | **Confirmed:** line 36 reads "Three names repeat across sections: `note` 3 times … and `[O] version` twice". The I-35 output itself reports `repeated: {'note': 3, '[O] version': 2}` (collapse 3 paths) | **ACCEPTED.** A wording correction for a separately authorized documentation pass. No evidence change is needed. Not corrected |

## Reruns
- `history`: byte-identical in the same pinned clone.
- `independent`: identical except lines 21–23, the three `sysctl` probes:
  - **reviewer's sandbox:** exit status 1, with "Operation not permitted";
  - **implementer's unrestricted rerun:** exit status 0, and the values equal the committed I-33 values (`implementer_rerun.txt`).

  This is a second sandbox in which the restricted-`sysctl` cause is observed.
- This evidence manifest verifies 6/6.

## Evidence note
**`git diff --check` on this review commit exits 2.** The one flagged line is in the reviewer's raw `independent.out`, line 24 (`diff check 0` followed by two trailing spaces). The raw evidence is kept as received and is not altered to make the check pass (I-29 and Review 02 precedent). Every other file in the commit passes the check.

## Proof gate
- [x] All Critical findings resolved: none raised.
- [x] All High findings resolved: none raised (0 BLOCKER, 0 MAJOR).
- [x] Every substantive finding has an explicit disposition: R4-F1 is ACCEPTED and **not corrected**.
- [x] Accepted Review 03 fixes re-tested: R3-F1 and R3-F2 are CLOSED by independent reproduction.
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: POG accuracy gating is BLOCKED pending review of DL-1 … DL-4. A-FP-2 rows are report-only. P6 geodetic drag is ESCALATED_FOR_INVESTIGATION.

**Review gate result: PASS.** The I-35 corrections close R3-F1 and R3-F2. **This PASS approves no decision, promotes no row, and authorizes no T2 implementation, numerical gate, correction pass or merge.**

**T2 implementation remains NOT AUTHORIZED.**
