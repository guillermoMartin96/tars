# M3 T2 S1: owner decisions I-41, I-42, I-43 and their dispositions

Recorded under I-43 §7 (authorized items 1–5). The owner texts in §1–§3 are verbatim (heading levels
demoted by one so they nest under this record; no other change). sha256 of each verbatim text as
received (UTF-8, before demotion): I-41 `8e836ab09a4d582da9cb20062b45652473ee5ca96f34ec9d01b703d40d9ab31b`, I-42
`69fed7abe1133757ac9aab408e17a5c16dd6063591c072f837af14d74552bdd8`, I-43 `5fbcf3aa8bcf2cb5501a69233a6e7654cd8ed00d1d4b1c278714e38be9330349`.

This record amends nothing in `docs/milestones/M3-T2-S1-authorization.md` (I-40, commit `c91a3ef`),
which stays as committed. **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED. No production
implementation is authorized.**

## 0. Status of each decision point (as of I-43, 2026-10-28)

| Point | Source | Status |
|---|---|---|
| Coast closure: option B (validate on read) | I-41 | Selected, subject to verification. v2 implementation of it was found to change finite-`dt` behaviour (R-02, Review 02). |
| M-14 designated killer is T-07 (k), not T-07 (d) | I-42 (1) | Approved (conditional on closure review, which returned REQUEST_CHANGES for R-02, not for this point). `mutate.py.txt` corrected under I-43 (R-03). |
| T-07 (a)/(b) keep BASE behaviour; the OD-2 option-A delta is unused and must not be introduced | I-42 (2) | Confirmed. |
| U-1: powered contexts validate at construction; coast contexts validate on read (option B) | I-42 (3) | Confirmed as the I-41 reading. The coast mass source is reopened by I-43 (lazy coast context investigation). |
| v2 regression-test additions and mutation-plan corrections | I-42 (4) | Conditional on a successful closure verification: **not satisfied** (Review 02 REQUEST_CHANGES). |
| M-19 equivalent survivor | I-42 (5), I-43 (3) | **Accepted** within the independently verified scope of the current production code (Review 02 item 8). Argument: `docs/science/experiments/m3-t2/s1-proposal/README.md`. |
| Record I-41/I-42 reviews, correct R-03, preserve evidence, commit documentation | I-42 (6), I-43 (1, 2, 4, 5) | Done in this commit series. Neither review is marked PASS. |
| R-02 resolution direction: lazy coast context (Option 1) | I-43 | Investigated: `docs/milestones/M3-T2-S1-I43-lazy-coast-investigation.md`. |

## 1. I-41 (owner, 2026-10-28)

## I-41 — S1 Coast Closure Decision and Compatibility Verification

### Owner decision

I select **Option 2: Option B for the coast closure only**, subject to verification that it preserves existing finite-`dt` behavior.

This is a narrowly scoped amendment to I-40. It does not authorize implementation of additional S1 functionality, expansion of OD-2's behavioral delta, or changes to protected code outside the previously approved S1 scope.

#### 1. Required behavior

Preserve the original OD-2 authorization for T-07(a)/(b), where `dt = +inf`.

For finite `dt`, including cases where `(tick + 1) * dt` overflows to `+inf`, preserve BASE's observable behavior.

The specific regression case discovered in I-40 must remain:

- `dt = 1e308`
- Zero-force model
- Direct Simulator API
- Failure at tick 2
- Expected exception: `FloatingPointError`
- Expected classification: `non_finite`

Do not convert this failure into `ValueError`.

#### 2. Investigation and proof

Before modifying production code:

1. Verify the exact Option B definition in the approved I-39A decision record.
2. Establish whether Option B can preserve the finite-`dt` counterexample.
3. Evaluate all eight existing T-07 cases against BASE and the proposed behavior.
4. Identify any additional direct-API cases where exception type, timing, numerical output, or error classification could change.
5. Verify that the proposed coast closure respects F3 and all existing M1/M2/T0/T1 invariants.
6. Determine whether any validated-scenario behavior changes.

Do not assume compatibility merely because validated scenarios appear unaffected.

#### 3. Implementation authorization boundary

If the investigation proves Option B can satisfy all existing requirements without an unauthorized behavioral delta, prepare a precise implementation proposal and regression-test plan.

**Do not begin commit A or modify production code under this instruction.**

Present the proposed change, affected paths, compatibility evidence, and test expectations for owner approval.

If Option B cannot preserve the required behavior, record the smallest reproducible counterexample and STOP.

Do not automatically fall back to Option 1 or Option 3.

#### 4. Repository safeguards

- Preserve `main` at `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
- Do not merge, rebase, force-push, or modify protected code.
- Preserve the existing S1 worktree and its untracked run-record script.
- Check the CI status of the I-40 decision-record commit `c91a3ef367df9df6e058132fd2579345ad67afb8`.
- Verify branch ancestry, worktree cleanliness, and authorization records before proceeding.
- Use scratch clones for experiments.
- Do not modify the approved I-37 decisions.

#### 5. Independent verification

Use an independent Codex review to evaluate the proposed Option B approach, specifically its exception compatibility, numerical behavior, and authorization boundaries.

The reviewer must evaluate the finite-`dt` overflow counterexample independently rather than relying solely on the implementation author's reproduction.

Record findings without automatically correcting any scope-expanding issue.

#### 6. Deliverable

Return an **I-41 decision-readiness report** containing:

1. Verified repository baseline and CI status.
2. Exact Option B interpretation.
3. Finite-`dt` compatibility results.
4. T-07(a)–(h) compatibility matrix.
5. Proposed regression tests.
6. Impact on M1/M2/T0/T1 invariants.
7. Independent review verdict and findings.
8. Any unresolved authorization conflicts.
9. Explicit recommendation: PROCEED or STOP.

**S1 remains NOT IMPLEMENTED, NOT REVIEWED, NOT ACCEPTED, and NOT MERGED.**

No implementation authorization is granted until I review the I-41 report.

## 2. I-42 (owner, 2026-10-28)

## I-42 — S1 Proposal v2 Closure Review and Authorization Readiness

### Owner decisions

I approve the following I-41 proposal v2 decisions, subject to the independent closure review required below.

1. Correct the I-39A mutation mapping: T-07(k), not T-07(d), is the designated killer for the powered-context-before-finiteness-check mutant M-14.
2. Confirm that T-07(a)/(b) retain BASE behavior. The previously contemplated OD-2 option-A delta is unused and must not be introduced.
3. Confirm the I-41 interpretation of U-1: powered contexts validate mass at construction; coast contexts use Option B, validating mass when a consumer reads it.
4. Approve the proposed v2 regression-test additions and mutation-plan corrections, conditional on successful closure verification.
5. Accept M-19 as an equivalent survivor only if the equivalence argument is documented and independently confirmed.
6. Authorize committing the I-41 review record, corrected proposal, decisions, and appropriate reproducible evidence.

**This does not authorize S1 production implementation.**

### 1. Preserve repository state

Verify:

- main and origin/main remain at BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
- The I-40 decision record at `c91a3ef367df9df6e058132fd2579345ad67afb8` remains intact.
- The S1 implementation branch has no implementation commits.
- The existing untracked `docs/s1/run_record.py` is preserved.
- No unauthorized production or protected-path changes have occurred.

Report any discrepancy and STOP.

### 2. Preserve the I-41 evidence

Before further experimentation, preserve the v2 proposal, review package, test results, mutant results, differential corpus definitions, and relevant logs.

The prior session restart erased I-40 scratch evidence. Do not allow another avoidable loss of the I-41 record.

Record checksums and provenance. Keep transient or oversized experimental artifacts outside Git where appropriate, but preserve enough information to reproduce the conclusions.

Do not commit unrelated scratch artifacts or generated files.

### 3. Independent Codex closure review

Launch a fresh, independent Codex review of proposal v2.

The reviewer must independently examine:

- R-01's corrected argument concerning writable RK4 stage arrays.
- The ordering of powered-context construction and state-finiteness checks.
- T-07(k)'s ability to kill M-14 for the intended reason.
- The finite-`dt` overflow counterexample from I-40.
- The preservation of exception types, messages, chains, warnings, and committed state.
- The no-burn `dt = +inf` behavior.
- Deferred coast-context validation and U-1 semantics.
- The M-19 equivalence claim.
- The revised mutation table and all added regression cases.
- Compliance with F3, OD-2, OD-4, and the existing S1 scope.

Do not treat a passing prototype test suite as sufficient proof of behavioral equivalence.

### 4. Verification

Run the relevant prototype tests, mutation checks, differential comparisons, and existing proof suites in isolated environments.

Compare against BASE.

Verify that all previously reported compatibility results remain reproducible.

If the original scratch evidence is incomplete, explicitly identify what has been reconstructed and what remains unverified.

Do not claim cross-platform verification from same-host results.

### 5. Review disposition

If Codex returns PASS with no unresolved findings:

- Record the closure verdict.
- Finalize proposal v2 and its test-plan amendments.
- Commit and push the authorized documentation and reproducible evidence to the planning branch using ordinary pushes.
- Check CI on the resulting commit.
- Prepare a precise S1 implementation authorization recommendation.
- STOP before production implementation.

If Codex returns REQUEST_CHANGES:

- Record every finding and its severity.
- Do not automatically implement fixes requiring new owner decisions.
- Do not authorize implementation.
- Return the findings for owner review.

### 6. Final I-42 report

Include:

1. Repository baseline, branches, commits, and CI.
2. Preservation of I-41 evidence.
3. Independent Codex verdict.
4. R-01 closure status.
5. T-07 and mutation-plan verification.
6. M-19 equivalence disposition.
7. Finite-`dt` compatibility results.
8. M1/M2/T0/T1 regression status.
9. Remaining risks and limitations.
10. Exact implementation authorization requested from the owner.

Final status must explicitly state:

**S1 NOT IMPLEMENTED / NOT ACCEPTED / NOT MERGED.**

Do not begin commit A or any production implementation without my subsequent authorization.

## 3. I-43 (owner, 2026-10-28)

## I-43 — S1 R-02 Resolution, Lazy Coast Context Proposal v3

### Owner decisions

I select **Option 1: lazy coast context** as the preferred design direction for resolving R-02.

This authorizes investigation, prototyping in isolated scratch clones, proposal v3 preparation, and independent review.

It does not authorize production implementation.

I also authorize:

1. Recording the I-41 and I-42 review outcomes, including their REQUEST_CHANGES verdicts and unresolved findings.
2. Correcting R-03's editorial inconsistencies.
3. Accepting M-19 as an equivalent survivor within the independently verified scope of current production code.
4. Preserving reproducible evidence and recording checksums.
5. Committing and pushing authorized documentation-only changes to the existing planning branch, subject to repository and scope checks.

Do not mark either failed review as PASS.

### 1. Repository preconditions

Verify the following before making changes:

- main and origin/main remain at `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.
- The planning branch contains the I-40 record at `c91a3ef367df9df6e058132fd2579345ad67afb8`.
- The S1 implementation branch remains at BASE without implementation commits.
- No protected production paths have changed.
- The run-record script remains preserved at its verified actual location, `docs/science/experiments/m3-t2/s1/run_record.py`.

If any precondition fails, STOP and report the discrepancy.

### 2. Resolve R-02 without expanding behavioral authorization

Investigate the proposed lazy coast context design.

The objective is to eliminate the additional coast-stage mass read introduced by proposal v2 while preserving BASE behavior for existing consumers.

Specifically investigate:

- Whether a coast closure can construct a context without accessing `y[_PROP]`.
- Whether the stage array can be retained safely.
- Whether lazy mass evaluation introduces observable differences when stage arrays are mutated after context creation.
- Whether retaining the array creates aliasing or lifetime hazards.
- Whether repeated reads can return different results.
- Whether warning and exception timing changes.
- Whether the approach preserves U-1's intended semantics.
- Whether the implementation can remain within the four previously allowlisted production paths.

**Do not assume that lazy read-time computation is equivalent to an owned binary64 snapshot.**

If the two requirements cannot both be satisfied, identify the precise conflict and STOP for an owner decision.

Do not silently weaken U-1.

### 3. Compatibility experiments

Use isolated scratch clones only.

Reproduce R-02 with:

1. A float64 MaskedArray with masked propellant.
2. An ndarray subclass whose `__getitem__` raises.
3. An object-dtype array containing None, as an out-of-contract control.
4. A standard RK4 float64 ndarray control.
5. A custom integrator that mutates the stage array after context creation.
6. Repeated context reads before and after stage mutation.
7. Array views and aliased storage.
8. Warning-as-error execution.

Compare BASE, proposal v2, and the proposed v3 prototype.

Record exception types, messages, warning behavior, state commitment, and numerical results.

Distinguish supported inputs from deliberately out-of-contract controls.

### 4. Regression and mutation plan

Prepare proposal v3 with:

- A direct regression test for R-02.
- A mutation that reintroduces the premature coast mass read.
- A test that kills that mutant for the intended reason.
- Explicit tests for snapshot timing and repeated reads.
- The previously approved T-07(i), (j), and (k) cases.
- The corrected M-14 mapping to T-07(k).
- The documented M-19 equivalence disposition.

Preserve the existing T-01 through T-06 requirements unless an unavoidable conflict is identified.

Do not change expected assertions merely to make the prototype pass.

### 5. Independent review

Once proposal v3 and its experimental evidence are complete, run a fresh independent Codex review.

Require the reviewer to evaluate:

- Closure of R-02.
- U-1 semantics and snapshot timing.
- Custom-integrator compatibility.
- Array subclass behavior.
- Exception and warning timing.
- Mutation-test effectiveness.
- Preservation of R-01 closure.
- F3, OD-2, OD-4, and the existing authorization boundaries.
- Any new observable behavior introduced by lazy evaluation.

A successful test suite does not substitute for an independent compatibility argument.

If Codex returns REQUEST_CHANGES, record the findings and STOP without automatically expanding scope.

### 6. Regression verification

Re-run the relevant:

- S1 prototype tests.
- Mutation campaign.
- Direct-API differential corpus.
- Stage-writer corpus.
- Custom-integrator compatibility cases.
- M1 Proof.
- M2 Proof.
- T0 checks.
- T1 checks.
- Full pytest suite.
- AST and changed-path checks.

Preserve BASE comparisons and disclose any missing or incomplete evidence.

Do not claim cross-platform validation unless it has actually been performed.

### 7. Record and preserve findings

Commit the authorized I-41/I-42 review records and R-03 editorial corrections on the planning branch.

Record proposal v3 separately with its evidence, decisions, and independent review verdict.

Preserve the evidence under the established external evidence directory, with checksums and a reproducibility manifest.

Avoid committing oversized or temporary experiment outputs.

Use ordinary pushes only.

Check CI after pushing.

Do not merge into main.

### 8. Final report

Return an I-43 report containing:

1. Repository baseline and CI status.
2. I-41/I-42 record commits.
3. Exact proposed v3 architecture.
4. R-02 compatibility matrix.
5. U-1 snapshot-semantics analysis.
6. Regression and mutation results.
7. Independent Codex verdict.
8. M1/M2/T0/T1 preservation results.
9. New findings and unresolved conflicts.
10. Recommendation: PROCEED or STOP.
11. Exact next owner authorization required.

**S1 remains NOT IMPLEMENTED / NOT ACCEPTED / NOT MERGED.**

Do not begin implementation commit A without subsequent explicit owner authorization.
