# M3 T2 S1: owner decision I-44 and its disposition

Recorded under I-44 §8. The owner text in §1 is verbatim (heading levels demoted by one; no other
change). sha256 of the text as received (UTF-8, before demotion): `fb0e3532af3834bcdb1f3927288606704910cccecb00a63fbe6cc34636c55fd6`.

This record amends nothing in `docs/milestones/M3-T2-S1-authorization.md` (I-40) or
`M3-T2-S1-decisions-I41-I43.md`. **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED. No production
implementation is authorized; implementation commit A is not begun.**

## 0. Disposition (2026-10-28)

| Item | Status |
|---|---|
| §1 preconditions | All verified (main / origin/main `ee602c5`; planning branch at `4c0ae07`; S1 branch at BASE, no commits, `run_record.py` sha256 `435a2b7e…7353` preserved untracked; Reviews 01/02 still REQUEST_CHANGES). |
| §2 v3-S contract | Formalized in `M3-T2-S1-proposal-v3.md` §3. **STOP condition reached:** v3-S changes the coast outcome for float64 stages of the wrong shape (size < 7 or 2-D), which the dtype-only contract does not exclude: question I44-Q1, proposal v3 §7. |
| §3 proposal v3 | Drafted (`M3-T2-S1-proposal-v3.md`), status DRAFT, not reviewed. |
| §4 prototype tests, §5 mutation, §7 regression | Run on the scratch prototype: `docs/science/experiments/m3-t2/s1-v3/`. |
| §6 independent Codex review | **Not run**: held for the owner's answer to I44-Q1, on which the reviewed contract depends. |
| §8 recording | This commit series (docs only); planning branch, ordinary push. |

## 1. I-44 (owner, 2026-10-28)

## I-44 — S1 v3-S Authorization, Snapshot Contract, and Independent Review

### Owner decision

I select **Option 1: v3-S (owned snapshot)** as the design for S1 proposal v3.

The objective is to resolve R-02 while preserving U-1's owned binary64 snapshot requirement and the existing behavioral authorization boundaries.

This instruction authorizes:

1. Preparing the complete proposal v3.
2. Incorporating the v3-S design and its explicit input contract.
3. Adding the R-02 and snapshot regression tests.
4. Updating the mutation plan.
5. Performing isolated prototype verification.
6. Running a fresh independent Codex review.
7. Recording and committing authorized planning documentation and review evidence.

**Production implementation is not authorized.**

Do not begin implementation commit A.

### 1. Repository preconditions

Verify:

- main and origin/main remain at BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
- origin/milestone-3-t2-authorization contains the I-43 record at `4c0ae07`.
- The S1 implementation branch remains at BASE with no implementation commits.
- No unauthorized production changes exist.
- The run-record script remains preserved at `docs/science/experiments/m3-t2/s1/run_record.py`.
- I-41/I-42 review records retain their original REQUEST_CHANGES dispositions.

If any precondition fails, STOP.

### 2. Formalize the v3-S contract

Document the following decisions precisely.

#### U-1: owned mass snapshot

Every constructed ForceContext containing mass must own a binary64 value that cannot change because of later mutation to the originating stage array.

For the coast closure:

- Read the underlying propellant value at context construction.
- Convert the value to an owned binary64 scalar.
- Apply the existing F3 coast mass expression.
- Preserve the approved deferred-validation behavior where applicable.
- Do not retain the originating stage array solely to evaluate mass later.
- Repeated reads must return the same value or consistently raise the required validation error.

#### Supported inputs

The declared input contract remains `NDArray[np.float64]`.

Do not broaden the supported contract to Python lists or object-dtype arrays.

For supported ndarray subclasses, preserve BASE's observable execution behavior except where an explicitly authorized change is necessary.

Document that v3-S uses the underlying stored propellant value for MaskedArray inputs, rather than interpreting mask metadata.

Do not claim that a type annotation alone enforces runtime input validity.

#### Compatibility boundaries

The observed differences for object-dtype arrays and Python lists are provisionally acceptable as out-of-contract cases, but they must be explicitly documented and reviewed.

Do not introduce general-purpose runtime rejection or change unrelated input handling.

If additional differences appear within the supported contract, STOP for owner review.

### 3. Proposal v3

Prepare a complete, internally consistent proposal incorporating:

- The v3-S architecture.
- U-1 snapshot semantics.
- R-01 closure evidence.
- R-02 resolution evidence.
- R-03 editorial corrections.
- F3, OD-2, and OD-4 constraints.
- T-07(i), (j), (k), and (l).
- The new snapshot regression test.
- The corrected M-14 mutation mapping.
- M-19's documented equivalence disposition.
- Explicit unsupported-input compatibility disclosures.

Explain why the implementation avoids the R-02 behavior changes for supported inputs.

Do not simply assert that bypassing subclass indexing is universally safe. Analyze relevant ndarray subclass and view behavior.

### 4. Required prototype tests

In isolated scratch clones, verify:

1. Standard float64 ndarray coast stages.
2. MaskedArray with masked propellant.
3. ndarray subclass whose indexing raises.
4. Custom integrators using ndarray subclasses.
5. Stage mutation after context construction.
6. Multiple contexts sharing a stage buffer.
7. Array views and aliased storage.
8. Repeated reads before and after mutation.
9. Warning-as-error execution.
10. Finite-dt overflow from I-40.
11. dt = +inf T-07(a)/(b).
12. Object-dtype and list inputs as out-of-contract controls.
13. Invalid mass and NaN propagation.
14. Powered-context ordering and R-01 preservation.

The snapshot test must distinguish v3-S from v3-L.

The R-02 test must distinguish v3-S from v2.

Record exception types, warnings, state commitment, and numerical outputs.

### 5. Mutation verification

Update the mutation campaign to include:

- A mutant reintroducing the premature subclass-sensitive coast read.
- A mutant replacing owned snapshots with lazy stage references.
- The corrected M-14 mapping to T-07(k).
- The accepted M-19 equivalent survivor.

Each non-equivalent mutant must be killed for its intended reason.

Do not classify a surviving mutant as equivalent without a defensible explanation and independent confirmation.

### 6. Independent Codex review

Run a fresh independent Codex review of proposal v3 and the prototype.

Require explicit findings on:

- R-02 closure.
- U-1 ownership and snapshot correctness.
- Supported ndarray subclass compatibility.
- MaskedArray semantics.
- Out-of-contract input differences.
- Exception and warning timing.
- Mutation-test adequacy.
- R-01 preservation.
- F3, OD-2, OD-4, and S1 scope compliance.
- Any new behavioral differences.

Codex must independently reproduce the important compatibility cases rather than relying exclusively on the author's test results.

If the reviewer identifies a new MAJOR finding or an authorization conflict, record it and STOP.

Do not automatically expand the behavioral authorization.

### 7. Regression verification

Run the relevant:

- S1 prototype tests.
- Mutation campaign.
- Direct-API differential corpus.
- Stage-writer corpus.
- Custom-integrator corpus.
- M1 Proof.
- M2 Proof.
- T0 checks.
- T1 checks.
- Full pytest suite.
- AST identity and changed-path checks.

Preserve reproducibility evidence and disclose platform limitations.

### 8. Recording and CI

Commit authorized proposal and review documentation to the planning branch using ordinary pushes.

Preserve external evidence with SHA-256 manifests.

Do not merge into main.

Check CI on the final planning commit.

Do not modify the S1 implementation branch.

### 9. Final I-44 report

Return:

1. Repository state and CI.
2. Proposal v3 commit and checksum.
3. Formal U-1 and input-contract definitions.
4. R-02 compatibility results.
5. Snapshot regression results.
6. Mutation campaign results.
7. Independent Codex verdict.
8. M1/M2/T0/T1 preservation results.
9. Outstanding findings and limitations.
10. Exact recommendation for implementation authorization.

**S1 NOT IMPLEMENTED / NOT ACCEPTED / NOT MERGED.**

Stop before commit A and await my decision.
