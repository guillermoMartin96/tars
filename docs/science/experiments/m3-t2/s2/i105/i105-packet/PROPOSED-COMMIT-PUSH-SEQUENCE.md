# Proposed commit and push sequence (I-105; NOT authorized; nothing has been committed or pushed)

This sequence appends three commits to E on `milestone-3-t2-s2-geodetic`:
- F: the test correction;
- G: the evidence;
- H: the report correction.

It follows the PC-7(S2) pattern. Each commit is pushed alone. After each push I wait for CI 4/4
`success` on attempt 1 with every job executed. A failed CI is a stop, with no rerun and no
fix-forward. There is no amend, rebase or force-push, and E and every earlier commit stay as they
are.

## F — tests only

**Content.** Exactly two paths. Their blobs must equal the I-105 frozen record and the red-run
record (stop 14):
- `tests/test_s2_geodetic.py`, blob `50c75e31db308358795d0c34ccd4b1457a787360`;
- `tests/test_s2_xp3_listing.py`, blob `9cfe6c1c7e9be031c702810aa8ed469d88c462cb`.

The working tree's documentation changes are not staged in F.

**Proposed message.**
`test(M3-T2-S2): exact MG-02/MG-04 witness nodes; census schema 2 (commit F, I-105, I104-01, I104-04)`

**Before committing.**
- Blob equality with `frozen/identities.txt` and `red/test-file-identities.txt`.
- `git diff --name-only E..F` is exactly those two paths.
- G-13 scope over K..F passes.

**CI evidence needed for F.** This is the new evidence the corrected emitter needs. It cannot exist
before F is pushed. For each of the three `check` jobs:
- run ID, attempt and head SHA; per job, whether it was executed or carried over; log URL; raw-log
  sha256;
- records extracted from the raw logs with `strip_gh_timestamps.py` and `scripts/extract_s2_records_v2.py`:
  `S2-ENV-RECORD`, `S2-G17A-REPORT`, `S2-G17B-RECORD`, and the schema-2 `S2-XP3-LISTING` (count
  and body sha256 verified);
- `scripts/validate_census.py … ci` on each job's census;
- G-17b with 0 differences on 8 853 class X entries on each job. `environment_kind` is recorded as
  observed; `other` is expected for every CI job;
- the full suite: 1 517 passed and 3 skipped on each `check` job. This number is expected, not
  observed.

**F CI comparisons.** Each job's schema-2 census, projected onto the schema-1 columns, is compared
with the same platform's archived E census. RP-8 and RP-9 are recomputed over F's three listings,
report-only.

## G — evidence only

**Content.** New paths under `docs/science/experiments/m3-t2/s2/i105/`, with nothing outside them:
- `ERRATUM.md`, already in the working tree;
- `README.md`;
- `SHA256SUMS`, covering `i105/` only;
- `red/`, with the I-105 supplemental red run: log, JUnit, classification, run record and
  extracted records;
- `binding/`, with F's blobs against the red record, and the candidate tree against F's tree;
- `green/`: logs over 1 MB kept by sha256 and tail, as in D, with the full logs external;
- `campaign/`: `mutation_results.json`, per-execution run records, extraction statuses and JUnit.
  The stdout logs stay external, with sha256;
- `host-report/`: the schema-2 RP-9 host census, with its run record and DL-5 probe;
- `derivation/`: the replacement derivation run;
- `gap/`: the inventory and the proposed disposition;
- `ci/F-<run>/`;
- `scripts/*.txt`.

The home path is scrubbed by whole-path replacement before commit. I-105 campaign messages are kept
untruncated, so the scrub can match them, and the scrubbed files are listed with their original
sha256.

**Proposed message.**
`docs(M3-T2-S2): I-105 correction evidence and erratum (commit G, I-105)`

**CI:** 4/4 on G, recorded in H.

## H — report only

**Content.** `docs/milestones/M3-T2-report.md`, append-only: E's bytes stay an exact prefix.
- §S2.14 as it now stands in the working tree.
- Appended after it, a short paragraph giving the F and G SHAs and CI runs, and the evidence
  location. This is written only after G's CI is green.

**Proposed message.**
`docs(M3-T2-S2): record the I-104 review and I-105 corrections (commit H, I-105)`

**CI:** 4/4 on H.

## After H

Stop, and prepare the handoff for a new, separately authorized §5.2 review of H. I-104's 26 MET rows
are not carried forward (`RESPONSE.md` §6). This sequence needs a new owner authorization: I-105
authorizes none of these commits or pushes.
