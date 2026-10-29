# Independent review 02: TARS M3 T2 S1, I-48 P-5 correction, closure of Review 01

You are an independent reviewer from a different provider than the implementer. This is a **fresh**
review session. You have not seen Review 01's session. Review is evidence, not authority.

## Context

I-40 (`docs/milestones/M3-T2-S1-authorization.md` §4) precondition P-5 reads:

> All 43 committed `SHA256SUMS` manifests verify. `git diff --stat a57de3f BASE --
> docs/science/experiments/m3-t0/` is empty.

The owner's I-48 ruling (verbatim: `review_scratch/pkg/I-48.md`) replaces that wording with the
corrected semantics P-5A–P-5D. It requires a fresh Codex review with 0 unresolved BLOCKER or MAJOR
findings before any implementation.

The implementer's draft was reviewed in **Review 01**:
- verdict `REQUEST_CHANGES`;
- materials in `review_scratch/pkg/review01/`: the final message, `REVIEW.md`, the reviewer's probes,
  and the decision record and verifier exactly as reviewed;
- findings: R01 MAJOR, R02 MINOR, R03 MINOR, R04 NOTE, plus a remark under item 4.

The implementer revised the draft. The revised materials are:
- `review_scratch/pkg/M3-T2-S1-decision-I48.md`: §10 gives the Review 01 dispositions; Review 02 is
  a placeholder;
- `review_scratch/pkg/s1-i48/`, the evidence;
- diffs against the reviewed versions: `review_scratch/pkg/decision-review01-vs-now.diff` and
  `review_scratch/pkg/verifier-review01-vs-now.diff`.

Nothing is implemented. No production code or test is changed. Commit A has not been made.

## Setup and rules

- **Working directory:** a fresh full-history clone of the planning branch, pinned at
  `1d9c9cd356ea71b590b4a1d13865f1f10efd657f`. BASE is `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
  Only `git` and the system `python3` (standard library) are needed. Run Python with `python3 -I -B`.
- Verify `review_scratch/pkg/SHA256SUMS` first.
- **Do not modify any tracked file of the clone.** Work only in `review_scratch/reviewer/`.
- No network. Do not fix anything; report.
- **Owner constraints the records must respect (I-48):**
  - the reviewer lists must not be required to validate against renamed or redacted artifacts;
  - they must not be labelled PASS against the committed tree;
  - available originals are verified where feasible, and unavailable ones are recorded;
  - git provenance is stated as not being an independent checksum;
  - I-40 and I-47 records are not rewritten;
  - the S1 technical contract is unchanged.

## Evaluation items

1. **Package and verbatim texts.** Does `SHA256SUMS` verify? Do §8 and §9 still equal `I-47.md` and
   `I-48.md` once the heading demotion is undone (sha256 `a0983f4a…5de`, `1bc17de1…edb`)?
2. **R01 closure.** Read the revised `p5_verify.py.txt`.
   - Does exit 0 now require every P-5A, P-5B and P-5C condition, including:
     - the expected coverage (L1/L3/L5: sibling entry present, digest equal, sibling PASS; L2/L4: in
       no committed `SHA256SUMS`);
     - history evaluated per commit, not by endpoint equality only?
   - Re-run Review 01's `gate_probe.py` approach, adapted to the new interface, and write your own
     negative probes.
   - Run `p5_gate_selftest.py.txt` (it needs an empty scratch directory) and judge whether it is
     meaningful.
   - Is any gate vacuous, or able to pass when it should fail?
3. **R02 closure.** Is the P-5A total now correct, and is the explanation of the earlier 1 412
   correct (1 176 + 236 from I-47's direct check)? Use `s1-i48/i47/p5_manifests.txt`.
4. **R03 closure.** Is the "Out of P-5 scope" disposition accurate, without broadening the owner's
   ruling? Check that the five `reviewer-SHA256SUMS.txt` files are covered by passing sibling
   manifests.
5. **R04 closure.**
   - Does P-5A now fail on a manifest-directory escape?
   - Are unreadable files in the host search reported?
   - Are the hash and basename limits stated accurately?
6. **Remark (item 4) closure.** Does §2 now cite primary sources only? Check the appended block in
   `historical_p5_transcript_extract.txt`.
7. **Regression.**
   - With the revised verifier at BASE, are all Review 01 results unchanged: 38/38, 315 entry
     classes, 14 unavailable, the P-5C facts?
   - Does `p5_result.json` reproduce exactly?
   - Did the revision introduce any new error, over-claim or inconsistency into the record, or any
     change to the S1 technical contract, allowlist, tests, mutation campaign, gates, commit sequence
     or other preconditions?
8. **Dispositions.** Is §10's account of Review 01 faithful? Are any of Review 01's points
   mis-stated, or left unaddressed?
9. **Any other issue** that would let the corrected P-5 pass when it should fail at the precondition
   re-run, or that an implementer could misread.

## Output

Your final message must contain, in this order:
1. `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. A findings table with columns ID (use the prefix R2-), severity (BLOCKER/MAJOR/MINOR/NOTE),
   location, finding, and evidence/reproduction. BLOCKER = Critical; MAJOR = High.
3. Explicit closure lines, each CLOSED / OPEN: **R01**, **R02**, **R03**, **R04**, **item-4 remark**.
4. Explicit lines:
   - **P-5A independent result: 38/38 PASS / OTHER**;
   - **S1 technical contract: UNCHANGED / CHANGED**.
5. A short section per evaluation item 1–9 saying what you read, ran and observed.

PASS requires 0 BLOCKER and 0 MAJOR findings. Save your scripts, outputs and a full `REVIEW.md` under
`review_scratch/reviewer/`.
