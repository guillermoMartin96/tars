# External Review: M3 T2 S1 I-48 P-5 correction, review 02 (closure of review 01)

## Review details

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a188ea-aa72-7f63-9408-a3e873077af9`.
  - This was a fresh session, separate from Review 01's, from a provider separate from the
    implementer's.
- **Date:** 2026-10-29.
- **Reviewed material:** documentation and evidence only. Nothing is implemented.
  - The revised `M3-T2-S1-decision-I48.md`, sha256
    `4504322a2040130514aec15bd44fb3b67146993b0e30ebe6589942a2e4f2d676`.
  - The revised `s1-i48/` evidence. The verifier has sha256
    `44031533a76aa34ccf9454529ddda23318fc5528be07050103b0b65aa3ed8b8f`.
  - Review 01's materials.
  - Diffs of the decision record and the verifier against the Review 01 versions.
  - The reviewer verified the package (`pkg/SHA256SUMS`, 26 files).
- **What changed after this review:**
  - Every reviewed `s1-i48/` evidence file is committed byte-identical. Two files were added after
    the review: the diff named below and `MANIFEST.sha256`.
  - The decision record differs only by the editorial R2-01/R2-02 text and the §10 entry for this
    review. Diff: `docs/science/experiments/m3-t2/s1-i48/decision-review02-vs-final.diff`.
- **Authorization:** I-48 §4 (owner, 2026-10-29).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review02-prompt.md` (sha256
    `2e7a3e43…3146731`);
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review02.md`, the final message verbatim (sha256
    `af8bdbf5…6fcfa38`). It contains no local paths and is unedited;
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review02-evidence/`, which holds:
    - `REVIEW.md`, the reviewer's scripts (as `.py.txt`) and their outputs;
    - `pkg/`, verbatim;
    - `SHA256SUMS`;
    - `SCRUBBED.txt`: local scratch paths in 2 output files were replaced by `$SCRATCH`, and their
      original sha256 values are listed there;
    - `EXCLUDED.txt`, which lists with sha256 the reviewer's throwaway probe repositories
      (`merge-repo/`, `merge-revert-repo/`) and the self-test scratch directory (7 047 files). These
      are kept externally in `~/projects/tars-evidence/I-48/`.
- **How it was run:**
  - a fresh full-history clone pinned at `1d9c9cd356ea71b590b4a1d13865f1f10efd657f`;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`, with no network.

  Afterwards the tracked tree was clean.

## Verdict

**`VERDICT: PASS`** (0 BLOCKER, 0 MAJOR, 1 MINOR, 1 NOTE).

| Line | Result |
|---|---|
| R01, R02, R03, R04, item-4 remark | all **CLOSED** |
| P-5A independent result | 38/38 PASS |
| S1 technical contract | UNCHANGED |

Highlights of the reviewer's checks:
- All 27 fresh negative exit-status probes returned 1.
- Merge-commit edit and edit/revert repositories fail the history gate.
- The supplied self-test passes 12/12; the reviewer called it "meaningful but not exhaustive".
- 315 classifications, 14 unavailable originals and the P-5C facts were recomputed, all unchanged.
- The JSON and the summary reproduce byte for byte.

## Findings and dispositions

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| R2-01 | MINOR | Calling all five `.txt` lists "implementer-written" overstated the evidence: T0 Reviews 07/08 call theirs the reviewer's own. Scope and coverage remain correct. | **ACCEPTED**, corrected editorially. Each attribution is now stated with its source. |
| R2-02 | NOTE | The host search reports candidate-file read errors but not directory-traversal errors, so "0 unreadable" does not prove complete traversal. | **ACCEPTED** as a stated limitation (decision record §4 P-5B). The verifier is not changed after review: the host search is informational and is not a gate. |

The reviewer's full text is `raw/M3-T2-S1-P5-correction-codex-review02-evidence/REVIEW.md`.
