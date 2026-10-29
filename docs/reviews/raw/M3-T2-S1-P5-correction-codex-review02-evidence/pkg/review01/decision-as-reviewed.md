# M3 T2 S1: owner ruling I-48 on precondition P-5 (and P-3), with the historical correction

- **Status:** owner ruling I-48 (2026-10-29), recorded append-only. It corrects how I-40 §4 P-5 is
  interpreted and verified. It is **not** a waiver of the evidence-integrity requirements (I-48 §1).
- **Scope:** documentation only. No production code, test, CI, dependency, scenario or proof file is
  changed. The S1 technical contract is unchanged (§6).
- **Historical records are not rewritten.**
  - `M3-T2-S1-authorization.md` (I-40) is not edited. Its P-5 text, "All 43 committed `SHA256SUMS`
    manifests verify", stays as written. This record is the correction addendum to it (I-48 P-5D).
  - The I-47 stop report is preserved as evidence (`docs/science/experiments/m3-t2/s1-i48/i47/`).
    It is not edited.
- **Owner texts:**
  - I-47 (authorizes Commit A only, conditional on the live preconditions): §8, verbatim, sha256
    `a0983f4ae2dd70dd9b22fe076925c44d2acbc096ca3c37c2be145e13ed43e5de`.
  - I-48 (this ruling): §9, verbatim, sha256
    `1bc17de1f80c7eff04877d180ff2b2b4a286a0c1d5aaf3b72a62d94ff3046edb`.

  Both hashes are over the UTF-8 text as recorded by the implementer, before heading demotion. Heading
  levels are demoted by one; no other change.
- Evidence: `docs/science/experiments/m3-t2/s1-i48/`.
- **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.** Commit A runs only after §7's gates pass.
  **Commit B is NOT AUTHORIZED.**

## 1. The original P-5 requirement (I-40 §4, unchanged)

> **P-5.** All 43 committed `SHA256SUMS` manifests verify. `git diff --stat a57de3f BASE --
> docs/science/experiments/m3-t0/` is empty.

## 2. The defective historical verification procedure (P-5D)

Source: the I-39A and I-40 session transcript, extracted verbatim, with absolute paths redacted, in
`s1-i48/historical_p5_transcript_extract.txt`.

| When (UTC) | Purpose | Selector | Check actually run | Reported |
|---|---|---|---|---|
| 2026-10-27T23:15:55Z | I-39A readiness | `git ls-files 'docs/reviews/raw/*SHA256SUMS' 'docs/science/*SHA256SUMS'` | `cd <dir> && shasum -a 256 -c SHA256SUMS` | "43 `SHA256SUMS` manifests verify"; "all 43 committed `SHA256SUMS` manifests verify, 0 mismatches" |
| 2026-10-28T02:10:50Z | I-40 P-5 | `git ls-files '*SHA256SUMS'` (43 paths) | `cd <dir> && shasum -a 256 -c --quiet SHA256SUMS` | `manifests=43 failed=0` |

**The defect.**
- The selector matches every path whose name *ends in* `SHA256SUMS`: 38 files named exactly
  `SHA256SUMS`, plus 5 reviewer-side lists.
- The check always verified the file named `SHA256SUMS` in the matched path's directory.
- Each of the 5 reviewer lists shares its directory with a `SHA256SUMS`. For those 5 paths the
  procedure re-verified that neighbour, and the reviewer list itself was never checked.
- So only **38 distinct manifests** were verified, and 5 of them were counted twice.

**Correction.** I-40's "43 verified, 0 failed" result overstated the number of distinct manifests
verified. The true figure was 38. The 38 that were verified did pass. The historical result is kept
as recorded, and this section is its correction.

I-47 found the defect when it checked the 5 lists directly. That check is
`s1-i48/i47/p5_manifests.txt` and `p5_diagnostic.txt`, and its result was 5 failures. I-47 stopped
before changing any file.

## 3. Owner authorization (I-48, summary; §9 is authoritative)

- **Option (a) approved.** The corrected P-5 semantics are P-5A–P-5D (§4).
- **P-3 ruling.** The existing S1 worktree is accepted as meeting the no-recreation requirement,
  subject to six live checks (§5).
- **Before implementation:**
  - an independent verification of the corrected procedure;
  - a fresh Codex review with 0 unresolved BLOCKER or MAJOR findings;
  - green planning CI;
  - a full live re-run of I-40 §4.
- **Then Commit A,** under the I-40 and I-47 restrictions. Commit B is not authorized.

## 4. Corrected P-5 requirements and their verification

The verification script is `s1-i48/p5_verify.py.txt`; `p5_render.py.txt` renders its output.
- It reads git objects at the named commit, not the working tree.
- It parses each manifest itself and resolves every entry against the manifest's own directory.
- Results at BASE `ee602c5`: `s1-i48/p5_result.json` and `p5_summary.txt`.

### P-5A: committed artifact manifests

**Requirement.** Every committed file named exactly `SHA256SUMS` is verified against its own path,
with its own directory as the base. 38 are expected at BASE, and all must pass with no missing or
mismatched entries.

**Result: PASS.**
- 38 manifests with 1 412 entries.
- 0 missing and 0 mismatched.
- Every entry resolves inside its manifest's directory.

Per-manifest rows are in `p5_summary.txt`.

### P-5B: reviewer-original checksum lists

**Requirement (I-48).**
- Identify each list.
- Show it is unchanged since it was first committed.
- Classify it by its original purpose.
- Check whether a committed artifact manifest covers it.
- Record its real verification limits.
- Do **not** require it to validate against the renamed or redacted committed artifacts.
- Do **not** label it PASS against the committed tree.
- Where originals are still available, verify them against the list. Where they are not, record that
  verification cannot be performed.

**Identification.** The selector is: committed names ending in `SHA256SUMS` but not equal to it. It
yields exactly the five lists below, and every one is classified **REVIEWER_ORIGINAL_CHECKSUM_LIST**.

| # | List | Documented purpose (source) | Covering committed manifest |
|---|---|---|---|
| L1 | `docs/reviews/raw/M3-T0-codex-review09-evidence/review_SHA256SUMS` | The reviewer's own checksum list, written by the reviewer (`docs/reviews/M3-T0-review-09.md:23`) | sibling `SHA256SUMS`, entry `review_SHA256SUMS`, digest matches |
| L2 | `docs/reviews/raw/M3-T1-codex-closure-evidence/reviewer-SHA256SUMS` | "covers the verifier's original files" (`docs/reviews/M3-T1-closure-verification.md:23`) | **none** |
| L3 | `docs/reviews/raw/M3-T1-codex-review02-evidence/reviewer-SHA256SUMS` | Written by the implementer over the reviewer's unrenamed, unredacted files (`docs/reviews/M3-T1-review-02.md:29`) | sibling `SHA256SUMS`, entry `./reviewer-SHA256SUMS`, digest matches |
| L4 | `docs/reviews/raw/M3-T1-codex-review03-evidence/reviewer-SHA256SUMS` | The same purpose as L3 (`docs/reviews/M3-T1-review-03.md:36`) | **none** |
| L5 | `docs/reviews/raw/M3-T2-packet-r2-codex-review01-evidence/reviewer_SHA256SUMS` | The reviewer's manifest, verbatim; its paths say `review_scratch/` and `.py` (`docs/reviews/M3-T2-packet-r2-review-01.md:24`) | sibling `SHA256SUMS`, entry `reviewer_SHA256SUMS`, digest matches |

**Original-content verification** (315 entries in all).

Classes:
- **same name / `.txt`**: hash-equal to the committed file at the listed name, or at that name plus
  `.txt` (the documented `.py` → `.py.txt` rename).
- **elsewhere**: hash-equal to a committed file outside the list's directory.
- **renamed**: hash-equal to a committed file under another name in the same directory.
- **regenerated**: the record says it was omitted as derivable. Re-deriving it with the stated git
  command gives exactly the listed hash.
- **empty**: a zero-byte original with an empty committed counterpart of the same name. The empty
  hash matches any empty file, so only the name pairing carries information.
- **unavailable**: no copy with the listed hash exists in the committed tree, or in the host-local
  locations searched (`p5_verify.py --search-root`).

| List | Same name / `.txt` | Elsewhere | Renamed | Regenerated | Empty | **Unavailable** |
|---|---|---|---|---|---|---|
| L1 (92) | 75 | 1 | 0 | 3 | 7 | **6** |
| L2 (31) | 28 | 0 | 0 | 0 | 3 | 0 |
| L3 (80) | 74 | 0 | 0 | 0 | 2 | **4** |
| L4 (100) | 86 | 0 | 0 | 0 | 10 | **4** |
| L5 (12) | 10 | 0 | 2 | 0 | 0 | 0 |

Details:
- **Elsewhere (L1):** `M3-T0-codex-review09.md` matches the committed `docs/reviews/raw/M3-T0-codex-review09.md`.
- **Renamed (L5):** `review_scratch/findings.json` is `reviewer_findings.json`, and `review_scratch/review.md` is
  `reviewer_review.md`.
- **Regenerated (L1):** the record omitted these as "large or derivable" (`M3-T0-review-09.md:26-28`):
  - `correction.diff` = `git diff 115e747 f04f995`;
  - `full.diff` = `git diff 86df2c3 f04f995`;
  - `termination_before.py` = `git show 115e747:docs/science/experiments/m3-t0/t0_termination.py`.

  All three hash-equal the listed digests.
- **Host-local search:** it searched the evidence store, the session scratch areas, the main checkout
  and all worktrees. It found nothing beyond the committed tree. The summary is identical apart from
  its header (`p5_summary_host.txt` in the external evidence).

**Original-content verification cannot be performed for 14 entries.**
- L1: `ast.log`, `env.log`, `independent.log`, `inspection_commands.md`, `pytest.log`,
  `r6f2_up_overflow_restored.log`.
- L3: `COMMANDS.md`, `interval_bound.log`, `mutation_audit_initial_error.log`, `pytest.log`.
- L4: `COMMANDS.md`, `full_pytest.log`, `own_mutants/j2_not_owned/pytest.log`,
  `own_mutants/redfirst.log`.

The originals are not retained anywhere searched.

Each of the 14 has a committed counterpart at the listed path. Every counterpart differs from the
listed hash and contains the documented redaction tokens:
- L1: `<clone>`, `<scratch>` and similar;
- L3 and L4: `<SNAP>`, `<SCRATCH>`, `<HOME>`.

That is consistent with the documented redaction. It does **not** show that redaction is the only
difference, because the original bytes are unavailable.

**Not labelled PASS.** Under I-48 no list is labelled PASS against the committed tree.

### P-5C: integrity and provenance

| List | Git blob at BASE | Introduced by | Blob at introduction | Commits touching the path | Coverage |
|---|---|---|---|---|---|
| L1 | `c88ebb40975b95642df07b6e90f4a06c70bbad29` | `5978bfe` | identical | 1 | sibling entry digest `18042ec0…6153` matches; sibling passes P-5A |
| L2 | `28f60563605fa4faac0d8c204294789f7279ff67` | `65de33f` | identical | 1 | **git provenance only** |
| L3 | `e9f5d7599642a3ecb80afac0442251e45224b804` | `b1566ae` | identical | 1 | sibling entry digest `3101a6f3…2862` matches; sibling passes P-5A |
| L4 | `8e1ea224ad41415f575a6ecfb642cd33f09c46c6` | `d01d6aa` | identical | 1 | **git provenance only** |
| L5 | `e1698912050262fcb06cc067fe535aa133e4d23a` | `43a6c29` | identical | 1 | sibling entry digest `d7f753ee…b3c6` matches; sibling passes P-5A |

- All five are unchanged since their original commits: each path has exactly one commit, and the
  blob there equals the blob at BASE.
- Coverage of L1, L3 and L5 by their neighbouring `SHA256SUMS` was verified directly.
- **L2 and L4 are listed in no committed `SHA256SUMS`.** Their integrity rests on git object identity
  and history alone. **Git provenance is not an independent checksum of the original reviewer
  artifacts.**

### P-5D: historical correction

Recorded in §2. The T0 half of P-5 is unchanged: `git diff --stat a57de3f ee602c5 --
docs/science/experiments/m3-t0/` is empty.

## 5. P-3 ruling: live checks required at the re-run

At the full precondition re-run, the existing worktree
`~/.superset/worktrees/tars/milestone-3-t2-s1-force-context` must show all of the following:

1. Branch `milestone-3-t2-s1-force-context` at BASE `ee602c5`.
2. Zero commits beyond BASE.
3. Not on the remote.
4. The only untracked project file is `docs/science/experiments/m3-t2/s1/run_record.py`.
5. That file has sha256 `435a2b7ef66f0d73bb7bee60f92f07247ab5a823cfb39dbe95481746db347353`.
6. The ignored `.venv/` introduces no tracked modification and violates no other prerequisite.

The worktree is not recreated, and `run_record.py` is not modified or deleted.

## 6. No change to the S1 technical contract

This ruling changes only how P-5 is verified (and confirms P-3). It does **not** change any of the
following:
- proposal v3-S (pin `dd705dd4…102d`, unchanged);
- plan amendment A-1;
- the I-40 §5 scope, the §6 allowlist or the §7 invariants;
- T-01…T-11, the §10 mutation campaign, R-1…R-6 or the §12 commit sequence;
- the §13 stop conditions or the OD-1…OD-6 decisions.

All other preconditions (P-1, P-2, P-4, P-6, P-7) keep their I-40 wording.

## 7. Gates before Commit A (I-48 §4–§6)

| Gate | Where recorded |
|---|---|
| Independent verification of the corrected procedure, and a fresh Codex review with 0 unresolved BLOCKER/MAJOR | review record committed with this ruling (`docs/reviews/M3-T2-S1-P5-correction-review-01.md`) |
| Planning CI green on the commit that records this ruling | I-48 report (a commit cannot record its own CI) |
| Full live re-run of I-40 §4 P-1…P-7, with P-3 and P-5 as ruled here; proposal and patch pins; I-46 records | I-48 report; later `M3-T2-report.md` §S1 (I-40 §4, commit E) |

## 8. I-47 (owner, 2026-10-29), verbatim

## I-47 — M3 T2 S1 Commit A Authorization and Execution

I have reviewed the I-46 report and authorize **Commit A only**, conditional on all required live preconditions passing.

This authorization does not extend to Commit B, C, D, or any production implementation.

### 1. Authorized baseline

- main / origin/main: `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`
- Planning branch: `milestone-3-t2-authorization`
- Planning HEAD: `1d9c9cd356ea71b590b4a1d13865f1f10efd657f`
- S1 implementation branch: `milestone-3-t2-s1-force-context`
- S1 worktree BASE: `ee602c5`
- Final proposal SHA-256: `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`

Preserve the approved I-46 plan amendment A-1.

Do not merge the planning branch into main or change the S1 baseline without explicit authorization.

### 2. Mandatory preconditions

Before changing any file:

1. Re-read the governing I-40 execution contract, including §4 and its P-1 through P-7 requirements.
2. Verify local and remote repository state, branch ancestry, and worktree status.
3. Verify the S1 worktree is still at BASE with zero implementation commits.
4. Preserve the existing untracked `run_record.py` and verify its recorded checksum.
5. Verify the required BASE CI result.
6. Verify all 43 required manifests and applicable evidence checksums.
7. Re-run the BASE R-1 through R-4 gates.
8. Verify the final proposal pin and I-46 decision and amendment records.
9. Confirm that the existing S1 worktree satisfies the execution contract. Do not recreate it or bypass a procedural conflict.

If any prerequisite fails or conflicts with the governing contract, STOP and report the exact issue.

Do not repair, reinterpret, or waive a failed precondition without authorization.

### 3. Commit A scope

Implement only the T-07 tests specified for Commit A in the approved S1 plan.

Required behavior:

- Preserve the 29 existing T-07 test nodes.
- All 29 must pass against BASE.
- No force-context production implementation.
- No changes to the other S1 test groups.
- No implementation of the four new A-1 tests yet.
- No M-22 mutant implementation yet.

Follow the exact file allowlist, sequencing, and commit requirements in I-40.

Do not infer permission to modify additional files from this instruction.

### 4. Verification

After implementing Commit A:

1. Run the required local checks and test gates.
2. Confirm T-07 passes 29/29 at BASE.
3. Verify the permitted file diff and absence of production changes.
4. Verify the original BASE behavior and applicable regression gates remain unchanged.
5. Create Commit A only after all required checks pass.
6. Push using an ordinary push, without rebase or force-push.
7. Wait for the required four-job CI matrix.
8. Confirm all four jobs pass on the exact pushed Commit A SHA.

If CI fails, stop and report the failure without beginning Commit B.

Do not claim that Commit A validates the prototype or establishes cross-platform correctness for the future implementation.

### 5. Stop conditions

Stop immediately for:

- Any failed I-40 precondition
- Any unexpected baseline or ancestry change
- Any checksum mismatch
- Any unauthorized file modification
- Any test regression
- Any unresolved contract conflict
- Any failed required CI job
- Any need to expand the authorized scope

Preserve evidence and report the issue without speculative fixes.

### 6. Required final report

Provide:

1. Exact baseline, branch, and final Commit A SHAs
2. P-1 through P-7 results
3. Manifest and checksum verification
4. T-07 results
5. Complete changed-file list
6. Local test and regression results
7. CI run IDs and four-job outcomes
8. Confirmation that production code is unchanged
9. Confirmation that the I-46 A-1 amendment remains intact
10. Remaining risks and blockers
11. Explicit readiness assessment for Commit B

Final status must state:

**Commit A IMPLEMENTED / VERIFIED**, only if all required gates pass.

**S1 NOT ACCEPTED / NOT MERGED.**

**Commit B NOT AUTHORIZED.**

Stop after Commit A. Await my explicit authorization before proceeding.

## 9. I-48 (owner, 2026-10-29), verbatim

## I-48 — S1 P-5 Owner Ruling, Verification Correction, and Conditional Commit A Execution

I have reviewed the I-47 stop report.

I approve **Option (a)**, subject to the requirements below.

This is an explicit owner ruling correcting the interpretation and verification procedure for I-40 §4 P-5. It is not a waiver of evidence integrity requirements.

### 1. P-5 ruling

The original statement that all 43 committed SHA256SUMS manifests verified was inaccurate.

The I-40 verification procedure iterated over 43 filenames but repeatedly verified the neighboring file named `SHA256SUMS`, resulting in only 38 distinct manifests being checked.

I authorize the following corrected P-5 semantics:

**P-5A — Committed artifact manifests**

Every committed manifest named exactly `SHA256SUMS` must be independently verified using its own path and intended verification base directory.

Expected count at BASE: 38.

All 38 must pass, with no missing or mismatched covered files.

**P-5B — Reviewer-original checksum lists**

The five separately named reviewer-side checksum lists must be:

1. Identified individually.
2. Verified as unchanged from their original committed Git versions.
3. Classified according to their original purpose.
4. Checked for coverage by a committed artifact manifest.
5. Recorded with their actual verification limitations.

Do not require these original reviewer checksum lists to validate against renamed or redacted committed artifacts when their documented purpose was to checksum the original reviewer files.

Do not label them PASS against the committed artifact tree.

For any reviewer-original files that are still available, verify them against their corresponding original checksums where feasible.

For reviewer-original files that are unavailable, record that original-content verification cannot be performed.

**P-5C — Integrity and provenance**

Verify that the five reviewer lists have not been modified since their original commits.

For the three lists reportedly covered by neighboring committed manifests, verify that coverage directly.

For the remaining two, verify their committed Git object identity and history. Record explicitly that Git provenance is not an independent checksum of the original reviewer artifacts.

**P-5D — Historical correction**

Record that I-40's original "43 verified, 0 failed" claim overstated the number of distinct manifests verified.

Preserve the original record and its historical result. Add a clearly identified correction or addendum.

Do not silently rewrite historical evidence or verdicts.

### 2. P-3 ruling

I accept the existing S1 worktree as compliant with the no-recreation requirement, provided live verification confirms:

- Branch `milestone-3-t2-s1-force-context` remains at BASE `ee602c5`.
- There are zero implementation commits.
- The branch remains unpushed.
- The only untracked project file is the preserved `run_record.py`.
- Its SHA-256 matches the recorded value.
- The ignored `.venv/` does not introduce tracked modifications or violate another explicit execution prerequisite.

Do not recreate the worktree.

Do not delete or modify `run_record.py`.

### 3. Required contract correction

Record this ruling in an append-only decision/addendum document within the existing planning scope.

Clearly distinguish:

- The original P-5 requirement
- The defective historical verification procedure
- The corrected P-5A through P-5D requirements
- The owner authorization
- The resulting verification evidence

Do not modify production code or tests while recording this correction.

Do not rewrite I-40 or I-47 historical reports to imply they originally performed the corrected verification.

### 4. Independent review

Before implementation:

1. Verify the corrected P-5 procedure independently.
2. Obtain a fresh Codex review of the correction and evidence classification.
3. Require zero unresolved BLOCKER or MAJOR findings.
4. Record any MINOR findings and resolve those affecting verification correctness.
5. Verify the correction introduces no change to the approved S1 technical contract.

If this requires a planning commit, use the existing planning branch and an ordinary push.

Wait for required planning CI before proceeding.

Do not merge planning into main.

### 5. Re-run all preconditions

After the correction is reviewed and recorded, re-run the entire I-40 §4 precondition sequence from the beginning.

Apply the explicit P-3 and P-5 owner rulings above.

All other preconditions retain their original requirements.

Do not reuse I-47 PASS results without live re-verification.

Specifically:

- Re-verify repository and branch state.
- Re-verify BASE CI.
- Execute corrected P-5A through P-5D.
- Execute R-1 through R-4.
- Complete P-7.
- Verify the proposal and prototype patch pins.
- Verify I-46 decision records and amendment A-1.

If any precondition fails, STOP.

### 6. Commit A authorization

My prior conditional authorization of Commit A remains in effect.

Once all corrected preconditions pass and the independent review and required planning CI are green, execute Commit A under the original I-40 and I-47 restrictions.

Commit A must contain only the approved T-07 tests.

Required results:

- 29/29 T-07 nodes pass at BASE.
- No production code modifications.
- No unauthorized file changes.
- Required local checks pass.
- Commit A is pushed using an ordinary push.
- All four required CI jobs pass on the exact pushed Commit A SHA.

Do not proceed to Commit B.

### 7. Stop conditions

STOP for any:

- Failed precondition
- Unexpected checksum mismatch
- Unexplained Git history or provenance discrepancy
- Reviewer finding that invalidates the corrected verification
- Scope or contract expansion
- Unauthorized file change
- Local test regression
- Required CI failure

Do not silently repair or waive failures.

### 8. Final report

Report:

1. P-5 original defect and corrected procedure
2. Individual results for all 38 committed-file manifests
3. Classification and provenance of all five reviewer lists
4. Exact planning correction commit and CI results
5. Independent Codex verdict and findings
6. Complete P-1 through P-7 results
7. BASE regression gates
8. Commit A SHA, changed files, and test results, if executed
9. Commit A CI run and four-job results
10. Remaining risks and explicit next authorization gate

If all gates pass, report:

**Commit A IMPLEMENTED / VERIFIED.**

**S1 NOT ACCEPTED / NOT MERGED.**

**Commit B NOT AUTHORIZED.**

If any gate fails, report the stopping point and leave implementation unchanged.
