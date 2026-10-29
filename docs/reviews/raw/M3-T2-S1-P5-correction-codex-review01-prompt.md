# Independent review 01: TARS M3 T2 S1, I-48 correction of precondition P-5 and evidence classification

You are an independent reviewer from a different provider than the implementer. This is a **fresh**
review session. Review is evidence, not authority.

## What is under review

I-40 (`docs/milestones/M3-T2-S1-authorization.md` §4) sets precondition P-5:

> All 43 committed `SHA256SUMS` manifests verify. `git diff --stat a57de3f BASE --
> docs/science/experiments/m3-t0/` is empty.

Under I-47 the implementer re-ran P-5 live and stopped. Of the 43 files matched by
`git ls-files '*SHA256SUMS'`, five reviewer-side checksum lists fail a direct check. The implementer
also found that the historical I-40 procedure always ran `shasum -c SHA256SUMS` in each matched
directory. If that is right, it verified only 38 distinct manifests, and the five lists were never
checked.

The owner issued I-48 (verbatim in `review_scratch/pkg/I-48.md`). It approves corrected P-5
semantics P-5A–P-5D and a P-3 ruling, and it requires this review before any implementation.

The implementer drafted:

1. **The decision/addendum record:** `review_scratch/pkg/M3-T2-S1-decision-I48.md`. It is a new
   file. It records the original requirement, the defective procedure, the corrected requirements,
   the owner authorization, the verification results, and I-47 and I-48 verbatim in §8–§9 (headings
   demoted by one).
2. **The evidence:** `review_scratch/pkg/s1-i48/`:
   - `p5_verify.py.txt`, the verifier;
   - `p5_render.py.txt`;
   - `p5_result.json` and `p5_summary.txt`, the results at BASE;
   - `historical_p5_transcript_extract.txt`, the historical commands and outputs, redacted;
   - `i47/`, the I-47 stop evidence;
   - `README.md`.

Nothing is implemented. No production code or test is changed. Commit A has not been made.

## Setup and rules

- **Working directory:** a fresh full-history clone of the planning branch, pinned at
  `1d9c9cd356ea71b590b4a1d13865f1f10efd657f`. BASE is `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
  The history includes `115e747`, `f04f995` and `86df2c3`. Only `git` and the system `python3`
  (standard library) are needed. Run Python with `python3 -I -B`.
- **Materials:** `review_scratch/pkg/`. Verify `review_scratch/pkg/SHA256SUMS` first.
- **Do not modify any tracked file of the clone.** Work only in `review_scratch/reviewer/`. You may
  check out BASE into a separate directory with `git worktree add` or `git archive` inside
  `review_scratch/`.
- No network. Do not fix anything; report.
- **Owner constraints you must hold the records to (I-48):**
  - the reviewer lists must not be required to validate against renamed or redacted committed
    artifacts;
  - they must not be labelled PASS against the committed tree;
  - available originals are verified where feasible, and unavailable ones are recorded as
    unverifiable;
  - git provenance must be stated as not being an independent checksum;
  - I-40 and I-47 historical records must not be rewritten;
  - the S1 technical contract must not change.

## Evaluation items

1. **Package.** Does `SHA256SUMS` verify? Do the verbatim sections §8 and §9 of the decision record
   equal `I-47.md` and `I-48.md` once the heading demotion is undone? The stated sha256 values are
   `a0983f4a…5de` and `1bc17de1…edb`.
2. **Independent P-5A.** Write **your own** verifier. Do not reuse `p5_verify.py.txt`. Check every
   committed file named exactly `SHA256SUMS` at BASE against its own directory. Do you get exactly
   38 manifests, all passing, with 1 412 entries and no missing or mismatched entry? Are any entries
   resolved outside their directory, or ambiguous (paths with `./`, subdirectories, `review_scratch/`
   prefixes)?
3. **Identification.** At BASE, are the files whose names end in `SHA256SUMS` exactly the 38 plus the
   five lists L1–L5? Is there any other checksum-list-like committed file that P-5 should arguably
   cover (for example `*SHA256SUMS.txt`, `MANIFEST.json`)? Does the record's scope statement handle
   them correctly given I-40's wording and I-48?
4. **Historical defect (P-5D).** From `historical_p5_transcript_extract.txt`, is the analysis in
   decision record §2 correct?
   - Did both historical procedures verify the neighbouring `SHA256SUMS` rather than the matched
     file?
   - Is "38 distinct, 5 counted twice" right?
   - Reproduce the historical loop at BASE and confirm it reports 43 OK.
   - Is the correction worded without rewriting the historical record or verdicts?
5. **P-5B classification.** For each list L1–L5:
   - Is the documented purpose correctly quoted from its review record?
   - Independently recompute the per-entry classes: same name or `.txt`, elsewhere in the tree,
     renamed, regenerated from git, empty, unavailable.
   - Check the 315-entry table and the list of 14 unavailable entries.
   - Are the three "regenerated" entries correct? Reproduce the git commands and the hashes, and check
     the review-09 record's statement that they were omitted as derivable.
   - Is any hash-equality match misleading (empty-file collisions, one blob matching several names)?
   - Is any entry mislabelled as verified?
6. **Limitations.** Are the 14 unavailable entries described accurately? Is the redaction-token
   observation stated without over-claiming? Is anything labelled PASS against the committed tree
   that should not be?
7. **P-5C.** For each list, check:
   - that it is unchanged since its introducing commit (blob identity, single commit, `--follow`
     history);
   - its coverage by the sibling `SHA256SUMS` (L1, L3, L5: entry present, digest equal, sibling
     verifies);
   - that L2 and L4 are covered by **no** committed `SHA256SUMS`.

   Is the statement that git provenance is not an independent checksum present and correct?
8. **Verifier correctness.** Read `p5_verify.py.txt` for defects. Does its exit code reflect every
   P-5A and P-5C condition? Does reading git objects (not the working tree) introduce any gap?
   Does `--search-root` or the `.txt`-suffix matching risk false positives? Does it treat paths
   safely?
9. **P-3 ruling (record §5).** Are the six live checks a faithful transcription of I-48 §2?
10. **No contract change (record §6).** Does anything in the record change or reinterpret the S1
    technical contract, the I-40 allowlist, tests, mutation campaign, gates, commit sequence or stop
    conditions, or any other precondition?
11. **Any other inconsistency** an implementer could misread when executing the corrected P-5 at the
    precondition re-run.

## Output

Your final message must contain, in this order:
1. `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. A findings table with columns ID, severity (BLOCKER/MAJOR/MINOR/NOTE), location, finding, and
   evidence/reproduction. BLOCKER = Critical; MAJOR = High.
3. Explicit lines:
   - **P-5A independent result: 38/38 PASS / OTHER (state it)**;
   - **Historical defect analysis: CORRECT / INCORRECT**;
   - **P-5B classification: CORRECT / INCORRECT**;
   - **P-5C provenance: CORRECT / INCORRECT**;
   - **S1 technical contract: UNCHANGED / CHANGED**.
4. A short section per evaluation item 1–11 saying what you read, ran and observed.

PASS requires 0 BLOCKER and 0 MAJOR findings. Save your scripts, outputs and a full `REVIEW.md` under
`review_scratch/reviewer/`.
