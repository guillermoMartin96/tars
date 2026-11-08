# Owner determination I-106: S2 historical run-record exception (ISSUED)

This is the decision the owner issued in instruction I-106 (2026-11-08). The external record is
`~/tars-evidence/I-106/` (`I-106.md`, the instruction verbatim; `DECISION-RECORD.md`).

**Decision versus proposal.**
- The I-105 text in `gap/PROPOSED-OWNER-DISPOSITION-I104-02.md` stays a **proposal**, unchanged.
- The text quoted below is the **issued decision**, and it controls.
- §2 of this file shows where the two differ.

| Decision input | sha256 |
|---|---|
| Pinned v11 (textually unchanged) | `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809` |
| `gap/historical-gap-inventory.json` (fixes the scope and identities of the excluded executions) | `8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9` |
| `REPLACEMENT-EXECUTIONS.md` (I-105 packet; copied here) | `82bcccba8cc2ceb587977784a933c3beee081446d45a98389a45ebf1c27ff072` |
| `PROPOSED-COMMIT-PUSH-SEQUENCE.md` (I-105 packet) | `017d847c8c6f54b384d28f2ee5b0cd7ea6d6538ed6569fda276aad0b1507f7f5` |
| I-105 packet manifest | `554b93b2c908cf34d5ad7d048c56eaa92b78561a117b3624d6253481540af5cd` |

## 1. Issued text (I-106 §2, verbatim)

> 2. Owner-approved bounded exception
>
> Approve disposition (a), subject to the following controlling wording.
>
> The excluded historical executions are exactly:
> - RED-ORIGINAL;
> - RED-SUPPLEMENTAL;
> - the 50 individually identified executions of I101-CAMPAIGN;
> - the 50 individually identified executions of I102-CAMPAIGN;
> - the 50 individually identified executions of I103-CAMPAIGN;
> - both scripts identified under D-SCRIPTS-AT-BC: derivation_crosscheck.py and report_only.py.
>
> Their scope and identities are fixed by the inventory hash above. MN17-DIAGNOSTIC is not included: it was never acceptance evidence and needs no exception.
>
> For OB-16, OB-17, §3.11 ENV and §3.15 stop 18, waive only the missing-record duties identified for these historical executions. Retain their nonconformances explicitly. Do not backfill, relabel or infer an environment for them. This does not waive other requirements, historical findings or future record duties.
>
> The exception is conditional on independent implementation review establishing that:
> - all other acceptance evidence satisfies its applicable recording requirements;
> - the new replacement evidence establishes the conclusions relied upon for acceptance on the actual candidate bytes;
> - no environment or reproducibility claim relies on an excluded execution’s unrecorded environment;
> - the original verified red-before-green order and blob bindings remain correctly attributed historical facts;
> - the I-105 supplemental red run precedes its candidate’s green validation and binds exactly to the committed corrected tests.
>
> The replacement evidence includes RX-RED, RX-GREEN, RX-CAMPAIGN, RX-HOST-REPORT and RX-DERIVATION from the pinned replacement-execution list, plus the new corrected-tip CI evidence.
>
> Recording requirements:
> - Each pytest replacement execution must have its own complete run provenance, DL-5 ENV, listing, G-17a and G-17b records.
> - Each scripted replacement must have its own complete run provenance and directly captured DL-5 ENV record, together with its required outputs and source/input identities. It need not pretend to execute pytest listing or G-17 tests; those results remain supplied by separately identified actual executions.
> - The derivation replacement must reproduce the required derivation output byte for byte. The host-report replacement must satisfy the corrected schema and its other report obligations.
> - CI jobs retain their applicable complete job provenance and platform-test records.
>
> The scripted replacements are evidence used in acceptance; their report-only numerical observations do not become gates.
>
> This exception grants no relief for future runs. Any additional historical gap requires a separate decision. Pinned v11 stays textually unchanged; this external determination controls only the stated historical recording exception.
>
> I104-02 and OB-16/OB-17 are not declared closed or MET by this instruction. That requires independent assessment against these conditions.
>

## 2. Differences from the I-105 proposal

| I-105 proposal (§4) | I-106 issued decision |
|---|---|
| D-SCRIPTS-AT-BC in brackets, for the owner to classify | Included: both scripts are excluded executions |
| "every gate-evidence run [from commit A]" excludes the listed executions | Only the missing-record duties identified for them are waived |
| Scripted replacements need the same record set as pytest runs | Scripted replacements need run provenance, a directly captured DL-5 ENV record, outputs and input identities. Listing and G-17 results come from actual pytest executions |
| RX-HOST-REPORT not named in the exception text | RX-HOST-REPORT named as replacement evidence |
| The status of the scripted runs' numerical observations not stated | Their report-only numerical observations do not become gates |

## 3. Status

- **I104-02 is not closed, and OB-16 and OB-17 are not MET.** The author's checks establish neither.
- **What closes them:** an independent implementation review that assesses the five conditions in §1
  against the corrected candidate's evidence.
