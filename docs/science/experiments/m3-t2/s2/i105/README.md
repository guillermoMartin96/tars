# S2 correction evidence after the I-104 review (I-105, I-106)

**What this directory is.**
- It holds only new evidence for the corrected candidate.
- No earlier S2 evidence file or manifest is changed: D's `SHA256SUMS` and `commit-a/SHA256SUMS`
  are untouched, and D's `SHA256SUMS` does not cover this directory.
- This directory's own `SHA256SUMS` covers every file here except itself.

**Commits.**
- E `495590033ddc0456b2b93ce08700152fae5a3123` was reviewed by I-104, which returned REQUEST_CHANGES.
- F `9ff5ca903332f4ca3c05b697e6d9bd4224ec8932` holds the two corrected test files only:
  - `tests/test_s2_geodetic.py`, blob `50c75e31db308358795d0c34ccd4b1457a787360`;
  - `tests/test_s2_xp3_listing.py`, blob `9cfe6c1c7e9be031c702810aa8ed469d88c462cb`.

  Its CI run 42442590220 succeeded 4/4 on attempt 1.
- G is the commit that adds this directory.

**Status.**
- Findings I104-01 to I104-04 are not closed by the author. OB-16 and OB-17 are not MET.
- I-104's MET rows were findings for E and do not carry forward.
- All of these need a new, separately authorized independent implementation review.

## Index

| Path | Content |
|---|---|
| `ERRATUM.md` | Additive erratum: each superseded statement quoted with its path and line (I104-01 to I104-04) |
| `DISPOSITION-I106.md` | The owner's **issued** I-106 exception for the historical run-record gap (I104-02), verbatim, and its differences from the proposal |
| `gap/PROPOSED-OWNER-DISPOSITION-I104-02.md` | The I-105 **proposal**, unchanged; superseded by the issued decision where they differ |
| `gap/historical-gap-inventory.json` | Inventory of the excluded historical executions, sha256 `8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9` |
| `owner/` | I-105 and I-106 verbatim, and the I-106 decision record |
| `i105-packet/` | I-105 response, `REPLACEMENT-EXECUTIONS.md` (sha256 `82bcccba…f027`), the proposed sequence (`017d847c…f7f5`) and the I-105 manifest |
| `red/` | RX-RED: the I-105 supplemental red run, on a fresh clone of A with `geodesy.py` absent and the two frozen test files. It has its own run record, ENV, G-17a, G-17b and schema-2 listing |
| `green/` | RX-GREEN: the full suite on the candidate (fresh clone of E plus the corrections), with its own records |
| `campaign/` | RX-CAMPAIGN: the complete corrected §3.12 campaign. Each of its 50 executions has a run record, ENV, G-17a, G-17b, extraction status and JUnit |
| `host-report/` | RX-HOST-REPORT: `report_only_v2.py` (schema-2 RP-9 host census), with its run record and directly captured DL-5 ENV record |
| `derivation/` | RX-DERIVATION: `derivation_crosscheck.py` on the candidate, with its run record and DL-5 ENV record. Its output is byte-identical to D's |
| `binding/` | The I-105 frozen identities and local diff; the I-106 pre-F checks (blob equality with the red record and the green candidate; red before green); F's commit record and G-13 over K..F |
| `ci/F-42442590220/` | F's CI: run and job provenance, raw-log sha256, records extracted from each check job, census validation, per-job summary, and RP-8/RP-9 recomputed (report-only) |
| `comparison/` | The environment table for all 15 CI test jobs at A to E (I104-03), and the host and E CI records it was built from |
| `checkpoint/`, `final-worktree-checks/` | I-105 starting-state verification and the final worktree checks |
| `scripts/` | I-105 and I-106 scripts, stored as `.txt` |
| `EXTERNAL.sha256` | Files kept outside the repository, by sha256 (large logs, campaign stdout and listings, mutant trees, duplicate censuses) |
| `SCRUBBED.txt`, `SCRUB-CHECK.txt` | Files in which the home path was replaced by `$HOME`, with their original sha256, and the post-scrub check |

The full external record is `~/tars-evidence/I-105/` (manifest sha256
`554b93b2c908cf34d5ad7d048c56eaa92b78561a117b3624d6253481540af5cd`) and `~/tars-evidence/I-106/`.
