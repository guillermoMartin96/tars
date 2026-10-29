# External Review: M3 T2 S1 I-48 P-5 correction and evidence classification, review 01

## Review details

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a188e2-abf2-7890-a986-26137e9256e5`.
  - This was a fresh session, from a provider separate from the implementer's.
- **Date:** 2026-10-29.
- **Reviewed material:** documentation and evidence only. Nothing is implemented.
  - The draft `M3-T2-S1-decision-I48.md`, sha256
    `e6ce0ac3756ccf11e7d7715b2a40cc375c2ecb5aabf03f8ad0b145afc0869f4f`.
  - The draft `s1-i48/` evidence. The verifier as reviewed has sha256
    `dd7c94df16f6de365f1f3e5c2c26f26a7e25b2eecd2d2826dd750a7d91185b09`.
  - `I-47.md` and `I-48.md`, the owner texts.
  - The reviewer verified the package (`pkg/SHA256SUMS`, 15 files).
- **Authorization:** I-48 §4 (owner, 2026-10-29).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review01-prompt.md` (sha256
    `94808094…d92ce9`);
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review01.md`, the final message verbatim (sha256
    `0ea1e03c…46451e`). It contains no local paths and is unedited;
  - `docs/reviews/raw/M3-T2-S1-P5-correction-codex-review01-evidence/`, which holds:
    - `REVIEW.md`, the reviewer's scripts (as `.py.txt`) and their outputs;
    - `pkg/`, verbatim;
    - `SHA256SUMS`;
    - `SCRUBBED.txt` (empty);
    - `EXCLUDED.txt`, which lists with sha256 the reviewer's copied BASE evidence tree (`base/`,
      2 762 files). That tree is kept externally in `~/projects/tars-evidence/I-48/`.
- **How it was run:**
  - a fresh full-history clone of the planning branch pinned at
    `1d9c9cd356ea71b590b4a1d13865f1f10efd657f`, with `review_scratch/` untracked;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`, with no network.

  Afterwards the tracked tree was clean.

## Verdict

**`VERDICT: REQUEST_CHANGES`** (1 MAJOR, 2 MINOR, 1 NOTE).

The reviewer's own independent results:

| Line | Result |
|---|---|
| P-5A independent result | 38/38 PASS, 1 176 entries; the draft said 1 412 |
| Historical defect analysis | CORRECT |
| P-5B classification | CORRECT (all 315 entries recomputed; the 3 regenerated hashes reproduced) |
| P-5C provenance | CORRECT for the facts at BASE; the automated gate was incomplete (R01) |
| S1 technical contract | UNCHANGED |

## Findings and dispositions

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| R01 | MAJOR | The verifier's exit status did not enforce the required P-5C sibling coverage or digest matches, and it judged "unchanged" by endpoint equality only. The reviewer's `gate_probe.py` obtained exit 0 with failed coverage. | **ACCEPTED** and corrected: six gates, including per-commit history; negative self-test (decision record §4, "Automated gate"). Closed in Review 02. |
| R02 | MINOR | The P-5A entry total is 1 176, not 1 412. | **ACCEPTED** and corrected, with the origin of 1 412 explained. Closed in Review 02. |
| R03 | MINOR | The record did not explicitly dispose of the five `reviewer-SHA256SUMS.txt` files or of the M2 `MANIFEST.json`. | **ACCEPTED** and corrected, without broadening the ruling. Closed in Review 02. |
| R04 | NOTE | `resolve` permitted manifest-directory escape; the host search hid unreadable files; basename and hash matching have limits. None of this invalidated the BASE results. | **ACCEPTED** and corrected: escapes now fail P-5A, unreadable files are counted, and the limits are stated. Closed in Review 02. |
| (item 4) | remark | The first historical block's output does not itself contain the quoted I-39 prose. | **ACCEPTED** (editorial): the record now cites the I-39 report line, extracted verbatim. Closed in Review 02. |

The reviewer's full text is `raw/M3-T2-S1-P5-correction-codex-review01-evidence/REVIEW.md`.
