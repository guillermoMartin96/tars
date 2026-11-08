# I-106 decision record: S2 historical run-record exception (ISSUED by the owner)

| Item | Value |
|---|---|
| Instruction | `~/tars-evidence/I-106/I-106.md` (saved verbatim) |
| Pinned plan | v11 `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809`, textually unchanged |
| Decision inputs, verified before any action | I-105 `MANIFEST.sha256` sha256 `554b93b2c908cf34d5ad7d048c56eaa92b78561a117b3624d6253481540af5cd`, all 2 207 entries OK; `gap/historical-gap-inventory.json` `8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9`; `REPLACEMENT-EXECUTIONS.md` `82bcccba8cc2ceb587977784a933c3beee081446d45a98389a45ebf1c27ff072`; `PROPOSED-COMMIT-PUSH-SEQUENCE.md` `017d847c8c6f54b384d28f2ee5b0cd7ea6d6538ed6569fda276aad0b1507f7f5` |
| Candidate state at verification | worktree HEAD = remote = E `495590033ddc0456b2b93ce08700152fae5a3123`; `tests/test_s2_geodetic.py` blob `50c75e31db308358795d0c34ccd4b1457a787360`; `tests/test_s2_xp3_listing.py` blob `9cfe6c1c7e9be031c702810aa8ed469d88c462cb` |

**Proposal versus decision.** The I-105 document `gap/PROPOSED-OWNER-DISPOSITION-I104-02.md` stays
a proposal and is unchanged. The text below is the decision the owner issued in I-106; where the two
differ, the I-106 text controls.

## Issued determination (I-106 §2, controlling wording)

Disposition (a) is approved, subject to the following.

**Excluded historical executions (exactly).** Scope and identities are fixed by the inventory sha256
`8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9`:
- RED-ORIGINAL;
- RED-SUPPLEMENTAL;
- the 50 individually identified executions of I101-CAMPAIGN;
- the 50 individually identified executions of I102-CAMPAIGN;
- the 50 individually identified executions of I103-CAMPAIGN;
- both scripts identified under D-SCRIPTS-AT-BC: `derivation_crosscheck.py` and `report_only.py`.

MN17-DIAGNOSTIC is not included. It was never acceptance evidence and needs no exception.

**What is waived.** For OB-16, OB-17, §3.11 ENV and §3.15 stop 18, only the missing-record duties
identified for these historical executions.
- Their nonconformances are retained explicitly.
- Nothing is backfilled or relabelled, and no environment is inferred for them.
- No other requirement, historical finding or future record duty is waived.

**Conditions.** The exception applies only if an independent implementation review establishes that:
1. all other acceptance evidence satisfies its applicable recording requirements;
2. the new replacement evidence establishes the conclusions relied upon for acceptance on the actual
   candidate bytes;
3. no environment or reproducibility claim relies on an excluded execution's unrecorded environment;
4. the original verified red-before-green order and blob bindings remain correctly attributed
   historical facts;
5. the I-105 supplemental red run precedes its candidate's green validation and binds exactly to the
   committed corrected tests.

**Replacement evidence.** RX-RED, RX-GREEN, RX-CAMPAIGN, RX-HOST-REPORT and RX-DERIVATION from the
pinned replacement-execution list, plus the new corrected-tip CI evidence.

**Recording requirements.**
- Each pytest replacement execution has its own complete run provenance, DL-5 ENV, listing, G-17a and
  G-17b records.
- Each scripted replacement has its own complete run provenance and a directly captured DL-5 ENV
  record, with its required outputs and source and input identities. It need not execute the pytest
  listing or G-17 tests; those results come from separately identified actual executions.
- The derivation replacement reproduces the required derivation output byte for byte. The host-report
  replacement satisfies the corrected schema and its other report obligations.
- CI jobs retain their applicable complete job provenance and platform-test records.

The scripted replacements are evidence used in acceptance. Their report-only numerical observations
do not become gates.

**Limits.**
- No relief for future runs.
- Any additional historical gap requires a separate decision.
- v11 stays textually unchanged; this external determination controls only the stated historical
  recording exception.

**Status.** I104-02 is not closed, and OB-16 and OB-17 are not MET. Both need independent assessment
against these conditions.

## Differences from the I-105 proposal

| I-105 proposal (§4) | I-106 issued decision |
|---|---|
| D-SCRIPTS-AT-BC bracketed, left to the owner to classify | Included: both scripts are excluded executions |
| "every gate-evidence run [from commit A]" excludes the listed executions | Waives only the missing-record duties identified for them |
| Scripted replacements: same record set as pytest runs (DL-5, listing, G-17a, G-17b, run record) | Scripted replacements need run provenance, a directly captured DL-5 ENV record, outputs and input identities; listing and G-17 come from actual pytest executions |
| RX-HOST-REPORT not named as replacement evidence in the exception text | RX-HOST-REPORT named |
| Report-only status of scripted observations not stated | Their report-only numerical observations do not become gates |
