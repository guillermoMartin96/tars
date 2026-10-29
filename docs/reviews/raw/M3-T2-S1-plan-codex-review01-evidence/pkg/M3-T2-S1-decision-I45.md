# M3 T2 S1: owner decisions I-45 and I-46 and their disposition

This record is made under I-45 §5. The owner text in §3 is verbatim, with heading levels demoted by
one and no other change. The sha256 of the text as recorded by the implementer (UTF-8, before
demotion) is `a14f935836e1ce547b28ab063d2615c6477312840f75ea3f9514a902e26e7305`.

**I-46 addendum (2026-10-29).** The I-46 owner decisions D1…D7 are recorded in §4 under I-46
authorized work item 2. The owner text is in §5, verbatim, with heading levels demoted by one and no
other change. The sha256 of the I-46 text as recorded by the implementer (UTF-8, before demotion) is
`4ba876213b6ebf96617781584117d232a0dd9b4e4dd1b4f8977ddcd399d030bd`. §0–§3 are kept as written under
I-45, except that a pointer to §4 is added at the head of §1.

This record amends nothing in `M3-T2-S1-authorization.md` (I-40), `M3-T2-S1-decisions-I41-I43.md` or
`M3-T2-S1-decision-I44.md`. The only exception is the I-46 D2 test and mutation plan amendment A-1
(`M3-T2-S1-test-plan-amendment-I46.md`), which adds to I-40 §9a T-04 and §10 and changes nothing
else in them.

- It does not reverse the `REQUEST_CHANGES` verdicts of Review 01 or Review 02.
- **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**
- No production implementation is authorized, and implementation commit A has not begun. Under
  I-46, commit A remains **NOT AUTHORIZED** pending the owner's review of I-46.

## 0. Disposition (2026-10-28)

| Item | Status |
|---|---|
| §5 baseline | Verified before any change: main and origin/main at `ee602c5`; planning branch at `4654ee2` (proposal v3 draft); S1 implementation worktree at BASE with 0 commits and not on the remote; `run_record.py` preserved untracked (sha256 `435a2b7e…7353`); Review 01/02 records still `REQUEST_CHANGES`. |
| I44-Q1 decision | **Option (a) approved** (owner). Recorded here and in proposal v3 §3.2. |
| §1 contract verification | **PASS**: no evidence that other stage shapes were explicitly supported (`docs/science/experiments/m3-t2/s1-v3s-i45/contract_verification.md`).<br>**C-1 (scoping):** the documented layout is 8 elements *with a spacecraft* and 6 elements without one (the M1 path). The 8-element contract is stated for derivatives built with a spacecraft, which is the only place the coast closure exists. The M1 path keeps its documented 6-element layout, so that supported behaviour is not redefined.<br>**D-1:** the `integrators.py` module docstring ("6 components") is stale. It is not edited, because production code may not be modified.<br>Review 03 independently found the interpretation **CONSISTENT**. |
| §2 proposal v3-S | Finalized: `M3-T2-S1-proposal-v3.md`, sha256 `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`. It covers the precise contract, U-1, MaskedArray stored-value semantics, out-of-contract disclosures, the R-01/R-02 history with unchanged dispositions (§8), and the M-19 argument (§5.1). |
| §3 independent Codex review | **Review 03: `VERDICT: PASS`** (0 BLOCKER, 0 MAJOR); `docs/reviews/M3-T2-S1-proposal-review-03.md`.<br>Closure lines: R-02 CLOSED; R-01 PRESERVED; I44-Q1 CONSISTENT; M-19 EQUIVALENT CONFIRMED.<br>**R-04 (MINOR):** ACCEPTED and corrected editorially (the 2-D exception statement).<br>**N-01 (NOTE):** ACCEPTED as a coverage gap but **not applied**; escalated to the owner (§1 below).<br>**D-1 (NOTE):** not changed. |
| §4 verification | Fresh-clone re-run of the I-44 regression reproduced every result, with identical digests (`s1-v3s-i45/regression_summary.txt`; §2 below). |
| §5 recording | This commit, docs only, on the planning branch with an ordinary push. External evidence is in `~/projects/tars-evidence/I-45/`: `MANIFEST.sha256` (9 019 files) has sha256 `d4bc4b1faadb47e1cd25f25ef34fa0413dac4ed3ba2752a27778c8ec8a4aa969`. |

## 1. Points for the owner (none authorized by this record)

> **Resolved by I-46 (§4).** Points 1–3 below were decided by the owner in I-46 (D2, D3/D4, D5).
> Point 4 remains open: commit A is not authorized. The text below is kept as written under I-45.

1. **N-01: powered snapshot coverage.**
   - The committed snapshot and lifetime tests (T-04 (a)/(b)) exercise coast contexts only.
   - A powered lazy-reference mutant passes all 86 S1 tests. Review 03's independent ownership
     assertions kill it, and the actual prototype passes them.
   - U-1 for powered contexts therefore currently rests on code reading, the reviewer's probes and the
     I-44 probe, not on a committed regression test.
   - The implementer recommends authorizing, before or with commit A:
     - a powered after-write, shared-buffer and lifetime test (a burn variant of T-04 (a)/(b));
     - a mutant M-22 (lazy powered context) in the campaign.
   - This changes the approved test plan, so it was not done under I-45.
2. **Final acceptance** of the out-of-contract disclosures (proposal §6, including R-04's (8, 1) row)
   and of the stored-value semantics (§3.2).
3. **D-1:** an optional, separately authorized docstring correction in `integrators.py`.
4. **Implementation commit A:** not authorized. It awaits the owner's explicit decision.

## 2. Verification (I-45 §4; same host only)

| Check | BASE | Prototype v3-S |
|---|---|---|
| S1 tests | T-07 29/29 pass; T-01…T-06 57 fail by AttributeError; 0 collection errors | 86/86 |
| Full pytest suite | 1 290 passed | 1 376 passed |
| Main direct-API corpus (26 880 cases) | `e0309486…a814` | identical; option-A control differs in 964 cases |
| Stage-writer corpus (26 111 cases) | `3310fd90…0415` | identical |
| Custom-integrator corpus (6 216 rows) | `d21c7c4a…04d7` | `1c9a9e89…4eba`: 0 supported rows differ; 392 out-of-contract rows differ (`list` 196, object `None` 196) |
| Mutation (24 mutants) | — | control 86/86; 23 killed for their declared reasons; M-19 survives 0/86; writer corpus: M-14 differs in 46 cases, M-19 in 0 |
| M1 Proof | PASS, 9/9 steps | PASS, 9/9 steps |
| M2 Proof | PASS, 20/20 steps | PASS, 20/20 steps |
| T1 (R-3) | r01 and r02 identical; 109 passed | r01 and r02 identical; 109 passed |
| T0 (R-4) | 314 passed | 314 passed |
| T-10 / T-11 | — | 51 checks, 0 failures / the 4 allowlisted paths |
| Scenarios (5) | — | output trees byte-identical; stdout differs only in the printed path |

How to read the corpus columns:

- **BASE** is the reference behaviour.
- **Prototype** rows that equal BASE show preserved supported behaviour.
- **Out-of-contract rows** are disclosures under proposal §6, not supported-input differences.
- Review 03 independently reproduced the corpora, Proofs, T0/T1 and the test discrimination.

All runs are same-host only (macOS x86_64, CPython 3.12.15, NumPy 2.5.3). No cross-platform claim is
made. Planning-branch CI covers only the documentation commit, not the prototype.

## 3. I-45 (owner, 2026-10-28)

## I-45 — Resolve I44-Q1 and Independently Review S1 Proposal v3-S

### Owner decision

I approve **I44-Q1 option (a)**, subject to independent verification of the existing interface contract.

For S1, the supported integrator stage is:

- A NumPy ndarray with binary64 (`float64`) elements.
- One-dimensional.
- Exactly eight elements.
- Following the existing documented state layout.
- Including ndarray subclasses that otherwise satisfy the supported contract.

This decision clarifies the intended supported stage representation. It does not authorize unrelated API restrictions or general runtime validation.

Do not modify production code to enforce the contract.

### 1. Contract verification

Before finalizing the decision record, independently inspect:

1. The Integrator protocol.
2. Derivative and Simulator interfaces.
3. Existing state-layout documentation.
4. Existing tests and supported custom-integrator behavior.
5. Any conflicting public documentation or explicit compatibility guarantees.

Determine whether the 1-D, eight-element requirement is consistent with the existing documented interface.

If the investigation identifies evidence that malformed shapes were explicitly supported, STOP and return the conflict for owner review.

Do not silently redefine existing supported behavior.

### 2. Finalize proposal v3-S

If the contract verification passes:

- Record the I44-Q1 decision.
- Update proposal v3-S with the precise supported-input contract.
- Preserve U-1's owned binary64 snapshot requirement.
- Preserve the v3-S stored-value semantics for MaskedArray.
- Explicitly document differences for out-of-contract inputs.
- Preserve R-01 and R-02 findings and their historical review dispositions.
- Correct any inconsistent statements or references.

The proposal must not claim that the earlier REQUEST_CHANGES verdicts have been reversed.

### 3. Independent Codex review

Run a fresh independent Codex review of the finalized proposal and prototype.

Require independent examination of:

- The I44-Q1 input-contract interpretation.
- R-02 closure.
- U-1 snapshot ownership.
- The use of `np.ndarray.__getitem__`.
- MaskedArray stored-value behavior.
- Subclasses that reinterpret indexing.
- Array views, aliases, and shared buffers.
- Exception and warning compatibility.
- Finite-dt overflow behavior.
- R-01 preservation.
- OD-2, OD-4, F3, and existing authorization boundaries.
- T-07(l) and snapshot regression tests.
- Mutation coverage and M-19 equivalence.

Codex must independently reproduce representative compatibility cases.

If the reviewer returns REQUEST_CHANGES, record the findings and STOP. Do not automatically expand the authorization or modify the design.

### 4. Verification

Re-run the applicable:

- S1 prototype tests.
- Custom-integrator differential corpus.
- Main direct-API differential corpus.
- Stage-writer differential corpus.
- Mutation campaign.
- M1 Proof.
- M2 Proof.
- T0 checks.
- T1 checks.
- Full pytest suite.
- AST identity and changed-path checks.

Correctly distinguish BASE behavior, prototype behavior, and unsupported-input disclosures.

Do not claim cross-platform validation from single-host prototype runs.

### 5. Repository and evidence controls

Verify the repository baseline before making changes:

- main and origin/main remain at `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
- The planning branch contains proposal v3 at `4654ee2`.
- The S1 implementation branch remains at BASE.
- The run-record script remains preserved.

Commit only authorized documentation and reproducible evidence to the planning branch.

Use ordinary pushes. Do not merge into main.

Preserve external evidence with SHA-256 manifests.

Check CI on the final planning commit.

### 6. Final I-45 report

Return:

1. Repository state and CI.
2. I44-Q1 contract-verification result.
3. Final proposal v3-S revision and checksum.
4. Independent Codex verdict and findings.
5. R-02 closure disposition.
6. Snapshot and mutation results.
7. Custom-integrator compatibility results.
8. M1/M2/T0/T1 regression results.
9. Remaining limitations and unresolved findings.
10. Explicit recommendation for S1 implementation authorization.

**S1 NOT IMPLEMENTED / NOT ACCEPTED / NOT MERGED.**

Do not begin implementation commit A.

Await my explicit authorization after I review the independent verdict.

## 4. I-46 owner decisions and disposition (2026-10-29)

The owner accepted Review 03's `PASS` "as a proposal-level verdict, not as implementation acceptance".

### 4.1 Baseline (I-46 work item 1), verified before any change

| Item | Observed |
|---|---|
| main / origin/main | `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (unchanged) |
| Planning branch | `milestone-3-t2-authorization` at `b52f77cb6693243b1ba681753627bb79c7005264`, local and remote; main is an ancestor |
| Planning CI on `b52f77c` | run 40801015917 `success`: check on ubuntu-latest, macos-15-intel and macos-latest, plus m2-cross-platform (4/4) |
| S1 implementation worktree | branch `milestone-3-t2-s1-force-context` at BASE `ee602c5`. It has 0 commits beyond BASE and is not on the remote. Its only untracked content is `docs/science/experiments/m3-t2/s1/run_record.py` (sha256 `435a2b7ef66f0d73bb7bee60f92f07247ab5a823cfb39dbe95481746db347353`, preserved, not touched). |
| Proposal v3-S | sha256 `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`, equal to the D1 pin |
| In-repo evidence manifest | `docs/science/experiments/m3-t2/s1-v3s-i45/MANIFEST.sha256`: 0 failures |
| External evidence | `~/projects/tars-evidence/I-45/MANIFEST.sha256` (sha256 `d4bc4b1faadb47e1cd25f25ef34fa0413dac4ed3ba2752a27778c8ec8a4aa969`): 0 failures |

### 4.2 Decisions

| Decision | Owner decision (summary; §5 is authoritative) | Disposition |
|---|---|---|
| **D1** Proposal baseline | FINAL v3-S is the S1 implementation design baseline, pinned to `dd705dd4…102d`. Reviews 01 and 02 stay `REQUEST_CHANGES`. | **Recorded.** The proposal file is not edited, so the pin holds. Review 01/02 records are unchanged. |
| **D2** N-01 | Add a powered-context snapshot-and-lifetime regression test and mutant M-22, and update the approved test and mutation plan. Preserve all existing test requirements. | **Recorded as plan amendment A-1** (`M3-T2-S1-test-plan-amendment-I46.md`): T-04 (d), 3 nodes; T-04 (e), 1 node; M-22. All existing T-01…T-11 and M-01…M-21b requirements are kept. **Plan only; nothing is implemented.** |
| **D3** Compatibility disclosures | The proposal §6 out-of-contract differences are accepted. They do not expand or redefine the contract. | **Recorded.** The supported contract stays as in proposal §3.2. |
| **D4** Stored-value semantics | The stored-value snapshot semantics for MaskedArray and ndarray subclasses are accepted within the contract. The legacy model's existing behaviour outside the new context boundary is preserved. | **Recorded.** A-1 deliberately does not mirror T-04 (c) on the powered path, because that would change the legacy `y[_PROP]` read (A-1 §2). |
| **D5** D-1 | Correct the stale docstring in commit A only if the existing allowlist and scope permit it. Otherwise defer. | **Deferred.** `src/tars/sim/integrators.py` is protected under I-40 §6 ("every other `src/` file"), and commit A is T-07 only (I-40 §12). The correction needs a separately authorized change. |
| **D6** Runtime enforcement | No runtime contract validation in S1. | **Recorded.** A-1 adds only observing tests and a scratch mutant. |
| **D7** Platform evidence | The prototype evidence is single-host (macOS x86_64, CPython 3.12.15, NumPy 2.5.3) and must not be called cross-platform validated. The established CI matrix is required after implementation. | **Recorded.** R-6 (CI 4/4 on every push tip) is unchanged and applies. |

### 4.3 Work items

| I-46 item | Status |
|---|---|
| 1 Baseline | PASS (§4.1) |
| 2 Record decisions | This section and §5 |
| 3 Plan update | A-1 |
| 4 Consistency check | A-1 §5: no contradiction with the gates, the allowlist, the commit sequence or the proposal. The only change to the pinned proposal's content is its §5 counts, which A-1 supersedes under D2. |
| 5 Independent review | Codex plan review 01 (`docs/reviews/M3-T2-S1-plan-review-01.md`) |
| 6 Findings | Per that record |
| 7 CI | On the final planning commit, reported in the I-46 report |
| 8 Commit A readiness | Reported to the owner. **Commit A NOT AUTHORIZED.** |

**S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**

## 5. I-46 (owner, 2026-10-29)

## I-46 — S1 v3-S Owner Decisions and Commit A Readiness

The I-45 report is acknowledged.

I accept Codex Review 03's PASS as a proposal-level verdict, not as implementation acceptance.

The following decisions are authorized:

**D1 — Proposal baseline**

Accept FINAL v3-S as the S1 implementation design baseline, pinned to SHA-256:

`dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`

Preserve Reviews 01 and 02 as REQUEST_CHANGES. Do not rewrite their historical verdicts.

**D2 — N-01**

Authorize the addition of:

1. A powered-context snapshot-and-lifetime regression test mirroring the coast ownership tests.
2. Mutant M-22, which deliberately retains a lazy reference in the powered path and must be killed by the new regression test.

Update the approved S1 test and mutation plan accordingly. Preserve all existing test requirements.

**D3 — Compatibility disclosures**

Accept the documented §6 differences for out-of-contract inputs, including descriptor errors, object-dtype None behavior, and malformed stage-shape exception differences.

These differences are not authorization to expand or redefine the supported integrator contract.

**D4 — Stored-value semantics**

Accept the documented stored-value snapshot semantics for MaskedArray and ndarray subclasses within S1's approved contract.

Preserve the legacy model's existing behavior outside the new context boundary.

**D5 — D-1**

Accept the stale integrator docstring as a documented issue. Correct it in Commit A only if that correction is explicitly permitted by the existing file allowlist and implementation scope. Otherwise defer it to a separately authorized change.

**D6 — Runtime enforcement**

Do not add runtime contract validation as part of S1. Preserve the documented contract and existing supported-input behavior.

**D7 — Platform evidence**

The prototype evidence is limited to macOS x86_64, CPython 3.12.15, NumPy 2.5.3.

Do not describe the prototype as cross-platform validated. Require the established CI matrix after implementation.

### Authorized work

1. Verify the repository baseline, branch ancestry, worktree cleanliness, proposal checksum, evidence manifest, and final CI status.
2. Record these owner decisions in the existing decision record.
3. Incorporate the N-01 test and mutation additions into the S1 plan.
4. Check that the additions do not contradict existing gates, the approved scope, or the final proposal.
5. Obtain a fresh independent Codex review of the updated decision and test-plan records.
6. Resolve any findings within the explicitly authorized documentation scope, without silently expanding authorization.
7. Run applicable checks and obtain green CI on the final planning commit.
8. Report whether every prerequisite for Commit A is satisfied.

### Restrictions

- Do not begin Commit A.
- Do not modify production code.
- Do not implement the new tests or mutant yet; update the plan only.
- Do not merge into main.
- Do not rebase or force-push.
- Do not alter the preserved S1 worktree or its untracked run_record.py.
- Do not broaden S1's runtime contract.
- Do not reinterpret earlier Codex verdicts.
- Stop and escalate any new contract contradiction, BLOCKER, MAJOR finding, or required scope expansion.

### Required final report

Provide:

- Exact repository and branch SHAs
- Decision-record changes
- Updated test and mutation counts
- Independent Codex review verdict and findings
- CI results
- Scope and checksum verification
- Remaining risks
- Explicit Commit A readiness recommendation

Final status must remain:

**S1 NOT IMPLEMENTED / NOT ACCEPTED / NOT MERGED.**

Commit A remains NOT AUTHORIZED pending my review of I-46.
