# M3 T2 S1: owner instructions I-49 and I-50 (Commit B sequencing correction)

- **Status:** owner instructions I-49 and I-50 (2026-10-29), recorded append-only. I-50 corrects
  I-49's execution instructions. It does **not** amend I-40 OD-3, R-6 or §12, or any other part of the
  S1 implementation contract (I-50, opening and §1).
- **Scope:** documentation only. No production code, test, CI, dependency, scenario or proof file is
  changed.
- **Historical records are not rewritten.**
  - `M3-T2-S1-authorization.md` (I-40), `M3-T2-S1-test-plan-amendment-I46.md` (A-1) and
    `M3-T2-S1-decision-I48.md` are not edited.
  - I-49 §6 is not edited. It is superseded only where §1 below says so.
- **Owner texts** (sha256 over the UTF-8 text as recorded by the implementer; heading levels demoted
  by one, no other change):
  - I-49: §4, verbatim, sha256 `4e3694dde0964a10efb3d00ae06174c01bd19ec9ca28b01af2158e7f8261b7df`;
  - I-50: §5, verbatim, sha256 `44c1714b3b5e20375818ccd387b5d6b1a4e637a01350de538b3d7bf5482c0a65`.
- **Status of S1 at this record:**
  - Commit A `abcf7553ed58138db15493044c0f34429b643286` was accepted by the owner in I-49
    (IMPLEMENTED / VERIFIED; CI run 40961801315, 4/4 `success`).
  - Commit B is authorized by I-50 for **local creation only** and is **NOT PUSHED**.
  - Commit C is **NOT AUTHORIZED**.
  - **S1 is NOT ACCEPTED and NOT MERGED.**

## 1. The correction

| Item | I-49 (superseded part) | Governing rule, unchanged | I-50 ruling |
|---|---|---|---|
| Push of Commit B | §6.2–6.3: push B with an ordinary push and wait for 4 CI jobs on its SHA | I-40 §12 step 2: "**Do not push B by itself.**" §12: "B is the only red commit, and it is never a tip." OD-3: a red-first ancestor "is never itself a push tip". R-6: CI 4/4 `success` on every push tip | Option 1. B is created locally, verified with the red-phase protocol, and left unpushed. It is never a pushed tip and triggers no CI of its own. B, C and D may be pushed together only after each is authorized and the I-40 gates are met. CI evaluates the implementation tip, not B. |

The rest of I-49 stands as far as I-50 restates it: Commit B's scope, the red-phase checks, the
independent Codex review, the evidence rules and the stop conditions.

## 2. The I-49 stop (precondition 8)

- **Preconditions 1–7:** PASS.
- **Precondition 8** ("Commit B changes are permitted by the … sequencing rules"): **FAIL.** I-49 §6
  required B to be pushed, but I-40 §12 and OD-3 forbid that.
- **Consequence had B been pushed:** CI runs every test in `tests/`, so the 61 nodes that are red by
  design would fail all three check jobs. That breaks R-6, which is stop condition §13.5. §12 then
  forbids any further push while that tip's CI has failed.
- No file was changed in the S1 worktree.
- The external evidence (I-49 report, preconditions, escalation note) is in `~/tars-evidence/I-49/`,
  with `MANIFEST.sha256` sha256 `a4db927910089a66fdd01792c56e7ed5c1747cbd342bc533efa7029fe21c1c68`.

## 3. No change to the S1 contract

The following are unchanged by this record. Each can be checked with `git diff ea7abad` on the
listed files:
- I-40 OD-3, R-6 and §12 (`M3-T2-S1-authorization.md`);
- A-1 (`M3-T2-S1-test-plan-amendment-I46.md`, sha256
  `04aca5f42e59748c89bdcbf2e3e6b051903068bb842aeeaa37e9e77213542db3`);
- the pinned proposal v3-S (`M3-T2-S1-proposal-v3.md`, sha256
  `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`).

The only path this record adds is itself.

## 4. I-49 (owner, 2026-10-29), verbatim

## I-49 — M3 T2 S1 Commit B Authorization: Red A-1 Tests

I have reviewed the I-48 final report.

**Commit A is accepted as IMPLEMENTED / VERIFIED.**

I authorize **Commit B only**, subject to the live execution prerequisites and exact scope defined below.

Commit C, Commit D, and production implementation remain NOT AUTHORIZED.

### 1. Baseline

- main / origin/main: `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`
- Planning branch: `milestone-3-t2-authorization`
- Planning correction commit: `ea7abad`
- S1 branch: `milestone-3-t2-s1-force-context`
- Commit A: `abcf7553ed58138db15493044c0f34429b643286`

Use the existing S1 implementation worktree.

Do not recreate it, rebase, merge, or force-push.

### 2. Required preconditions

Before changing any file:

1. Re-read the governing I-40 execution contract and the I-46 A-1 amendment.
2. Verify the current S1 branch HEAD equals Commit A locally and remotely.
3. Verify the working tree is clean apart from the previously authorized untracked and ignored files.
4. Verify Commit A CI run `40961801315` passed all four required jobs.
5. Verify the original T-07 tests still pass 29/29.
6. Verify the final v3-S proposal and prototype patch checksums.
7. Verify the I-46 and I-48 decision records and amendments remain unchanged.
8. Confirm that the intended Commit B changes are permitted by the governing file allowlist and sequencing rules.

If any prerequisite fails or the governing contract conflicts with this authorization, STOP and escalate.

Do not reinterpret or waive failed conditions.

### 3. Authorized Commit B scope

Implement only the red tests authorized for Commit B by the governing S1 plan, including the I-46 A-1 additions.

The amended S1 plan requires:

- 90 total S1 test nodes.
- 29 T-07 nodes, already committed in A.
- 61 remaining nodes that must fail at BASE with the expected AttributeError.
- Four new powered-context ownership nodes from A-1:
  - T-04(d), three nodes.
  - T-04(e), one node.

Preserve the exact approved test definitions, assertions, and expected behavior.

Do not weaken assertions to obtain expected results.

Do not introduce alternate production behavior.

Do not implement M-22 yet unless the governing Commit B contract explicitly requires it. If the contract differs from this authorization, STOP for clarification.

### 4. Red-phase verification

The purpose of Commit B is to establish failing tests before production implementation.

Required results:

1. All 29 existing T-07 tests continue to pass.
2. All 61 remaining S1 tests fail for the expected missing implementation, with no collection errors.
3. No unexpected failures occur in previously passing tests.
4. No production source files change.
5. No test expectations are weakened.
6. The four A-1 powered ownership nodes are included and fail for the intended reason.
7. All required static checks and applicable BASE regression gates pass.

**Expected red-phase failures are not grounds for changing the tests to make them green.**

Follow the governing execution contract for recording and evaluating intentional red-phase results.

### 5. Independent review

After the tests are implemented, obtain an independent Codex review of Commit B.

The review must examine:

- Test fidelity to the pinned v3-S proposal.
- Fidelity to the A-1 amendment.
- Expected red-phase failure classification.
- Preservation of T-07 baseline behavior.
- Absence of production implementation.
- Correctness of snapshot, ownership, and lifetime assertions.
- Potential vacuous assertions or tests that could pass without enforcing the intended contract.
- Compliance with the approved file allowlist.

Require zero unresolved BLOCKER or MAJOR findings.

Record all findings and their dispositions.

Do not silently expand scope to resolve findings.

### 6. Commit and CI

If all required local and review gates pass:

1. Create Commit B containing only authorized test changes.
2. Push with an ordinary push.
3. Wait for all four required CI jobs on the exact pushed SHA.
4. Evaluate CI according to the governing red-phase protocol.

Do not assume ordinary green CI is required if the approved red-phase contract specifies another mechanism for intentional failures.

Do not alter CI configuration to hide expected failures.

If the CI outcome differs from the approved red-phase protocol, STOP.

### 7. Evidence integrity

Use a dedicated TARS evidence directory that is verified not to be inside an unrelated Git checkout.

Preserve the existing I-48 evidence without modification.

Record checksums for new evidence.

Do not move, rewrite, or delete historical evidence merely to standardize directory locations.

### 8. Stop conditions

STOP for:

- Failed preconditions
- Unexpected test behavior
- Unexpected CI behavior
- Contract or scope conflicts
- Checksum mismatches
- Unauthorized file modifications
- Unresolved BLOCKER or MAJOR review findings
- Any need to change production code
- Any requirement to alter the approved test contract

Do not proceed to Commit C.

### 9. Final report

Provide:

1. Exact branch and commit SHAs
2. Preconditions and their results
3. Changed-file list
4. T-07 baseline results
5. Red-phase results, including all 61 expected failures
6. A-1 test results
7. Independent Codex verdict and findings
8. Static checks and regression results
9. CI run IDs and outcomes
10. Evidence checksums
11. Remaining risks and blockers
12. Explicit readiness recommendation for Commit C

Final status must state:

**Commit A IMPLEMENTED / VERIFIED.**

**Commit B IMPLEMENTED / RED-PHASE VERIFIED**, only if all required gates pass.

**S1 NOT ACCEPTED / NOT MERGED.**

**Commit C NOT AUTHORIZED.**

Stop and await my explicit authorization.

## 5. I-50 (owner, 2026-10-29), verbatim

## I-50 — M3 T2 S1 Commit B Sequencing Correction and Local Red-Phase Authorization

I have reviewed the I-49 stop report.

**Owner decision: Option 1 is approved.**

The governing I-40 §12 sequencing takes precedence over the conflicting I-49 §6 instruction.

This ruling corrects my earlier instruction. It does not amend OD-3, R-6, or the underlying S1 implementation contract.

### 1. Sequencing ruling

Commit B is the intentional red-phase commit.

It must:

- Be created locally.
- Remain unpushed.
- Be verified using the approved red-phase protocol.
- Never become a pushed branch tip.
- Not trigger CI as an independently pushed commit.

Commit B, C, and D may eventually be pushed together only after each has received the required owner authorization and the governing execution gates are satisfied.

CI must evaluate the completed implementation tip according to I-40, not the intentionally failing Commit B.

Do not change CI configuration or weaken test expectations.

### 2. Existing baseline

- main / origin/main: `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`
- Commit A: `abcf7553ed58138db15493044c0f34429b643286`
- S1 branch: `milestone-3-t2-s1-force-context`
- Final proposal SHA-256: `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`

Preserve the existing implementation worktree and `run_record.py`.

Do not recreate the worktree, rebase, merge, or force-push.

### 3. Preconditions

Before making changes:

1. Record this owner ruling as an append-only correction to the I-49 execution instructions.
2. Verify that the correction does not modify I-40's OD-3, R-6, or §12 requirements.
3. Reconfirm the S1 branch is still at Commit A locally and remotely.
4. Verify the working tree remains unchanged.
5. Verify Commit A's four-job CI result.
6. Verify the approved proposal and A-1 amendment checksums.
7. Confirm the authorized Commit B file allowlist.

The I-49 precondition 8 conflict is resolved by this ruling.

Do not rerun unrelated historical work unless the governing contract requires it.

STOP for any new contradiction or failed prerequisite.

### 4. Commit B scope

Implement only the approved red-phase S1 tests.

The amended test plan requires:

- 29 existing T-07 nodes, unchanged.
- 57 original T-01 through T-06 nodes.
- Four additional A-1 powered-context ownership nodes.
- 90 total S1 test nodes.

The four new A-1 nodes must follow the approved specification:

- T-04(d): three parametrized cases.
- T-04(e): one case.

Implement the A-1 additions from their approved specification, not from assumptions about the pinned prototype patch.

Do not implement production force-context behavior.

Do not implement M-22, which belongs to the later mutation-evidence phase.

### 5. Required red-phase verification

Before committing:

1. Confirm all 29 T-07 nodes pass.
2. Confirm all 61 remaining S1 nodes fail with the expected AttributeError.
3. Confirm there are no test collection errors.
4. Confirm the four A-1 nodes fail for the intended missing implementation.
5. Confirm the previously passing BASE tests remain unaffected.
6. Run required static checks.
7. Verify all modified paths are allowlisted.
8. Verify production source files are unchanged.

Do not modify assertions to make the red tests pass.

Do not classify intentional red-phase failures as ordinary product regressions.

Preserve complete test output and JUnit evidence.

### 6. Independent Codex review

Obtain an independent review of the local Commit B changes.

The reviewer must examine:

- Fidelity to the pinned v3-S proposal.
- Fidelity to the I-46 A-1 amendment.
- Correctness of all 61 expected red-phase failures.
- Preservation of the 29 T-07 tests.
- Powered snapshot and lifetime test strength.
- Absence of vacuous or insufficient assertions.
- Absence of production changes.
- Compliance with the approved scope and file allowlist.

Require zero unresolved BLOCKER or MAJOR findings.

If a finding requires changes beyond the authorized test scope, STOP and escalate.

### 7. Local commit

After all required verification and review gates pass:

1. Create Commit B locally.
2. Record its exact SHA.
3. Verify its parent is Commit A.
4. Verify the complete committed diff.
5. Confirm Commit B remains unpushed.
6. Preserve the required evidence and checksums.

**Do not push Commit B.**

**Do not start Commit C.**

**Do not run CI on Commit B as a pushed branch tip.**

### 8. Evidence

Use the dedicated TARS evidence directory outside unrelated Git repositories.

Preserve the I-48 and I-49 evidence.

Create an I-50 evidence manifest and verify it.

Do not rewrite historical evidence.

### 9. Final report

Provide:

1. Exact repository and branch SHAs
2. Confirmation of the sequencing correction
3. Preconditions and results
4. Changed-file list
5. T-07 results
6. Results for all 61 expected red nodes
7. A-1 test results
8. Independent Codex verdict and findings
9. Static checks and regression results
10. Commit B SHA and parent verification
11. Confirmation B was not pushed
12. Evidence manifest checksum
13. Remaining risks and readiness for Commit C

Final status:

**Commit A IMPLEMENTED / VERIFIED.**

**Commit B IMPLEMENTED / RED-PHASE VERIFIED**, only if all required gates pass.

**Commit B NOT PUSHED.**

**Commit C NOT AUTHORIZED.**

**S1 NOT ACCEPTED / NOT MERGED.**

Stop and await my explicit authorization.
