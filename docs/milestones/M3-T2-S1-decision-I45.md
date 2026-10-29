# M3 T2 S1: owner decision I-45 and its disposition

This record is made under I-45 §5. The owner text in §3 is verbatim, with heading levels demoted by
one and no other change. The sha256 of the text as recorded by the implementer (UTF-8, before
demotion) is `a14f935836e1ce547b28ab063d2615c6477312840f75ea3f9514a902e26e7305`.

This record amends nothing in `M3-T2-S1-authorization.md` (I-40), `M3-T2-S1-decisions-I41-I43.md` or
`M3-T2-S1-decision-I44.md`.

- It does not reverse the `REQUEST_CHANGES` verdicts of Review 01 or Review 02.
- **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**
- No production implementation is authorized, and implementation commit A has not begun.

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
