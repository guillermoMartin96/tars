You are an independent reviewer from a separate provider. You did not write any file under review. This is a **focused, documentation-only independent closure review** of the TARS M3 owner-decision recording. Independent Review 02 (record `docs/reviews/M3-T2-owner-decisions-review-02.md`; raw `docs/reviews/raw/M3-T2-owner-decisions-codex-review02.md`) returned PASS with two MINOR findings, M3T2OD-R2-F1 and M3T2OD-R2-F2. The owner authorized their correction under I-28. During I-28 the implementer found one further unmarked statement, M3T2OD-I28-C1, documented it and stopped. The owner then authorized its correction and this closure review under I-29. The Review 02 findings and the authorizations I-29, I-28, I-27 and I-26 are reproduced verbatim at the end. **The implementer's documents are claims, not evidence.**

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`69aa2e69415aa10b97bfc9b609b6a4112278bfa1`** (branch `milestone-3-t2-owner-decisions`). Relevant ancestors:
  - `1f2ce7e9b7a3d2fe243b79cf4eb099e792cad15e`: I-28 corrections (R2-F1, R2-F2) and the I-28-C1 STOP record;
  - `45f80f8523d1ed0033cf9f773d5072e719d4d442`: the Review 02 record;
  - `f3ae3876825b2966faaced3281f638b6271572ad`: what Review 02 reviewed (I-27 corrections);
  - `a22297d1ec719a58aeb7209f3d34256fa7b0756a`: the I-27 base;
  - `2cd1e6ec1bc2df13827c36d03fda5bf4b4150c09`: the I-26 recording;
  - `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- A locked Python environment is in `./.venv`; use `.venv/bin/python -I`. **The network is not available.**
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch (it is excluded from git). Do not run the M1/M2 proof scripts. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo them; no network):** the I-28 and I-29 §1 baselines and the pushes. Treat CI and remote facts as claims.
- **Decision boundaries.** You review; you do not decide or fix anything. Do not treat P6, DR-0028 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved.

## What is under review (`git diff 45f80f8..69aa2e6`, all under `docs/`)
- **I-28 (`45f80f8..1f2ce7e`):**
  - in-cell markers on `docs/milestones/M3-T0-decision-matrix.md` lines 14 and 27 (R2-F1);
  - an appended R2-F2 note in `docs/reviews/M3-T2-owner-decisions-review-01-corrections.md`;
  - new `docs/reviews/M3-T2-owner-decisions-review-02-corrections.md` (correction matrix, the full search, the I-28-C1 finding, the §4 audit);
  - `docs/reviews/raw/M3-T2-owner-decisions-I28-evidence/`.
- **I-29 (`1f2ce7e..69aa2e6`):**
  - a new "I-29 correction" block in `docs/decisions/requests/DR-0029-m3-t0-proposals.md` P2, immediately after the "Proposed outcome and fields" list, plus one Resolution-log entry (I-28-C1);
  - new `docs/reviews/M3-T2-owner-decisions-I28-C1-correction.md`;
  - `docs/reviews/raw/M3-T2-owner-decisions-I29-evidence/`.

## What you must independently assess (I-29 §5)
1. **Is R2-F1 resolved?** The T0 decision matrix must state unambiguously that `reentry` is DECIDED, that the precedence `non_finite → reentry → impact → escape` is DECIDED, that T3 implements and does not decide again, and that T3 keeps fields and serialization within the approved contract. The prior text's provenance must be preserved.
2. **Is R2-F2 resolved?** Check the I-28 note's description of the `git diff --check a22297d f3ae387` result, its cause and its effect on interpretation. Check the fresh-check claims, including that the exit status is reported faithfully, that no clean range is claimed falsely, and that the raw evidence is preserved.
3. **Is I-28-C1 resolved?** The I-29 block must sit immediately after the affected P2 passage and state all six items of I-29 §2. The original passage must be preserved, and P2's A5-b behaviour and the P3 precedence must be unchanged.
4. **Does any further contradictory `reentry` status remain?** Search **all** 24 M3 decision documents yourself, using multiline context:
   - DR-0024 … DR-0029 with their packets and briefing;
   - ADR-0009;
   - `docs/milestones/M3-*`;
   - `README.md`.

   Look for any statement that leaves the outcome name or precedence open, proposed, provisional or subject to T3 decision without an in-place or explicitly referenced supersession. Judge the implementer's classifications (I-29 evidence check [4]; I-28 record, "Examined and not treated as contradictions"), in particular DR-0027 line 96 and T0-matrix lines 15 and 41.
5. **Are the owner-approved decisions preserved?**
   - P1–P5 and P7–P9 DECIDED;
   - P6 NOT FULLY DECIDED ((d) PROVISIONALLY SELECTED; geodetic drag ESCALATED); DR-0028 P6(b) OPEN;
   - Q-GATE and DQ-1 … DQ-6 unchanged; the floating-point policy unchanged;
   - RM-3b an unmeasured T4 candidate;
   - the conditional numerical accuracy rows report-only;
   - no decision added or changed.
6. **Is historical evidence preserved accurately?** Earlier review records and raw evidence must be unchanged, with checksums verifying. The new records' statements must be accurate, including line references and the stated line shift.
7. **Is the correction documentation-only?** It must be append-only. No protected path may be touched: `src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`.
8. **Is the I-26 reconciliation ready for owner acceptance**, from the standpoint of the recording's accuracy and consistency? This is your assessment only; acceptance is the owner's decision.

## Output format
Markdown:
1. First line: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. A summary.
3. A findings table with these columns: ID (M3T2OD-CR-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location, finding, evidence, proposed disposition or correction.
4. Your assessment of items 1–8. For items 1–3, use RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED.
5. Your own computations (commands and outputs).
6. Limitations.

Severity guide:
- **BLOCKER / MAJOR:** a recorded decision that differs from the owner's text, an approval presented as already made, a waived gate, a misleading technical claim, or a scope violation.
- **MINOR:** an inaccurate or unsupported statement, or an unmarked contradictory status statement, that does not change a decision, classification or gate.
- **NOTE:** a clarity issue.

PASS means no BLOCKER or MAJOR finding remains. State explicitly whether any MINOR finding remains.

## Review 02 findings (verbatim from `docs/reviews/raw/M3-T2-owner-decisions-codex-review02.md`)

VERDICT: PASS

The authoritative corrections faithfully record I-26 P3 and P7. No BLOCKER or MAJOR finding remains. Two MINOR documentation issues remain: missing local supersession markers in historical matrix cells, and an inaccurate description of the whitespace-check output.

Reviewed commit: `f3ae3876825b2966faaced3281f638b6271572ad`, against parent `a22297d1ec719a58aeb7209f3d34256fa7b0756a`.

### Findings

| ID | Severity | Location | Finding | Evidence | Proposed disposition/correction |
|---|---|---|---|---|---|
| M3T2OD-R2-F1 | MINOR | `docs/milestones/M3-T0-decision-matrix.md:14,27,76` | Two historical cells still describe `reentry` as a T3 proposal without an in-place supersession marker. The appended clarification resolves the governing decision, but local traceability is incomplete. | Line 14 says “Event names (`reentry`, fields) remain T3 contract proposals”; line 27 says `altitude_floor_m` and `reentry` remain proposals until T3. Line 76 correctly declares `reentry` DECIDED, but specifically discusses the later dependency row rather than marking these cells. | In a separately authorized documentation correction, append local markers identifying `reentry` as decided while preserving field names as T3 design. No decision change is needed. |
| M3T2OD-R2-F2 | MINOR | `docs/reviews/M3-T2-owner-decisions-review-01-corrections.md:52`; `docs/reviews/raw/M3-T2-owner-decisions-I27-evidence/self_validation.out:31` | The correction report inaccurately says `git diff --check` reports only Markdown hard breaks. | Independent execution also reports trailing whitespace in the raw `.out` file at line 31. That whitespace is not a Markdown hard break. | Accurately describe the additional diagnostic in a subsequent authorized record. Preserve existing evidence. |

## Owner authorization I-29 (verbatim)

# TARS — Authorization I-29
## M3 Owner Decisions: I-28-C1 Correction and Independent Closure Review

You are continuing the TARS M3 owner-decision recording workflow.

I-28 corrected M3T2OD-R2-F1 and M3T2OD-R2-F2 but stopped before the independent closure review after discovering an additional contradiction, I-28-C1.

I authorize:

1. One narrowly scoped, append-only correction for I-28-C1.
2. Focused consistency and evidence verification.
3. One independent Codex closure review covering R2-F1, R2-F2 and I-28-C1.
4. A final checkpoint report.

I do not authorize acceptance, merge, implementation, or new scientific decisions.

## 1. Mandatory baseline verification

Expected state:

- Remote branch: `milestone-3-t2-owner-decisions`
- Superset local branch: `m3-t2-owner-decisions-972e4c7c`
- HEAD and remote: `1f2ce7e9b7a3d2fe243b79cf4eb099e792cad15e`
- Worktree: clean
- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- I-27 Review 02: PASS, with two MINOR findings
- R2-F1 and R2-F2: corrected under I-28, pending closure review
- I-28-C1: documented, not corrected
- I-28 CI: four jobs green on run `40261200936`

Before editing:

1. Fetch remote references.
2. Verify exact local and remote HEAD.
3. Verify the clean worktree.
4. Verify main remains at the expected baseline and is an ancestor of HEAD.
5. Read I-26, I-27 and I-28 authorizations.
6. Read the complete I-27 Review 02 record.
7. Read the I-28 correction record and the documented I-28-C1 finding.
8. Verify the relevant evidence checksums.
9. Verify the existing correction commits and CI status.

If a mandatory precondition fails, STOP and report.

Do not reset, rebase, amend, cherry-pick or force-push to work around a discrepancy.

## 2. Authorized correction: I-28-C1

### Finding

In `DR-0029-m3-t0-proposals.md`, the P2 section contains historical wording indicating that outcome names remain proposals until the v3 contract is designed at T3.

The accompanying list explicitly includes:

`outcome reentry`

This conflicts with the owner's I-26 decision establishing that `reentry` is a decided outcome name.

The governing I-26 decision is already unambiguous, but the historical passage lacks a local supersession marker.

### Required correction

Add an append-only clarification immediately after the affected P2 passage.

The clarification must state:

- The `reentry` outcome name is DECIDED under I-26.
- The precedence `non_finite → reentry → impact → escape` is DECIDED.
- T3 implements these decisions; it does not reopen them.
- Other event field names, event payload details and serialization remain T3 design responsibilities, within the approved contract.
- Any change to the decided outcome name or precedence requires a new owner decision.
- The historical P2 proposal wording is superseded only insofar as it describes `reentry` as provisional.

Preserve the original passage.

Do not alter P2's decided A5-b crossing behavior.

Do not change P3's precedence or any other approved decision.

## 3. Scope of consistency verification

After the correction:

1. Verify that the new marker resolves I-28-C1.
2. Verify that R2-F1's two decision-matrix cells remain corrected.
3. Verify that R2-F2's evidence correction remains accurate.
4. Search all 24 relevant M3 decision documents for contradictory statements about `reentry`.
5. Include multiline context checks; do not rely only on single-line matching.
6. Verify that all remaining historical references are either consistent or explicitly superseded.
7. Verify that RM-3b remains an unmeasured T4 candidate.
8. Verify that P6 remains NOT FULLY DECIDED.
9. Verify that Q-GATE and DQ-1 through DQ-6 are unchanged.
10. Verify that conditional numerical accuracy tests remain report-only where their assumptions are unverified.

If another material contradiction is found, record it and STOP rather than expanding the correction scope.

## 4. Evidence requirements

Produce focused verification evidence showing:

- The exact insertion location.
- Preservation of the original historical text.
- The new supersession marker.
- The status of all three findings.
- Results of the full-context contradiction search.
- The changed-file list.
- The result and exit status of `git diff --check`.
- Confirmation that no protected path changed.

Preserve previous raw evidence and its checksums.

Do not rewrite the I-27 or I-28 historical review records.

Commit the I-28-C1 correction and its verification evidence.

Use an ordinary, non-force push.

## 5. Independent Codex closure review

After successful self-validation, request one independent Codex closure review.

Pin the full correction commit SHA.

Supply the reviewer with:

- I-26 owner decisions.
- I-27 and I-28 authorizations.
- This I-29 authorization.
- I-27 Review 02 findings.
- I-28 corrections.
- I-28-C1 finding and correction.
- The relevant authoritative decision records.

The review must determine:

1. Whether R2-F1 is resolved.
2. Whether R2-F2 is resolved.
3. Whether I-28-C1 is resolved.
4. Whether any additional contradictory `reentry` status remains.
5. Whether the owner-approved decisions are preserved.
6. Whether historical evidence is preserved accurately.
7. Whether the correction is documentation-only.
8. Whether the I-26 reconciliation is ready for owner acceptance.

Require an explicit verdict:

- PASS
- REQUEST_CHANGES

If REQUEST_CHANGES:

- Record each finding.
- Reproduce it independently where feasible.
- Document its disposition.
- Do not correct new findings without authorization.
- Do not initiate another review round.
- STOP.

If PASS:

- Record the verdict and evidence.
- Prepare the final I-29 checkpoint.
- Do not accept or merge.

## 6. Protected scope

I-29 is documentation-only.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify accepted T0/T1 code or evidence.

Do not change pinned constants, numerical thresholds, atmosphere data or golden references.

Do not authorize or execute the P6 X-1 investigation.

Do not decide DR-0028 P6(b).

Do not begin T2 implementation.

## 7. Git and CI

Use the existing owner-decision branch and worktree.

Keep the correction commit and independent review evidence commit separate.

Push using ordinary, non-force pushes.

Verify CI on both pushed commits.

Do not open a PR.

Do not merge into main.

Do not create a T2 implementation branch.

## 8. Final checkpoint

Report:

- Full HEAD and remote SHA.
- Worktree status.
- Correction and review commits.
- Changed files.
- Verification results for R2-F1, R2-F2 and I-28-C1.
- Independent closure-review verdict.
- Any new findings.
- CI results.
- Decision-status summary.
- Remaining P6 and P8 scientific uncertainties.
- Fast-forward ancestry status.
- Readiness for owner acceptance and merge authorization.

Explicitly confirm that:

- No owner decision changed.
- No implementation file changed.
- No PR was opened.
- Nothing was merged.
- Main remains unchanged.
- T2 has not started.

## 9. Mandatory STOP

Stop after the authorized correction, independent closure review and final checkpoint.

Do not proceed to acceptance, merge, P6 investigation, or T2 implementation without another explicit owner authorization.

Begin with baseline verification.

## Owner authorization I-28 (verbatim)

# TARS — Authorization I-28
## M3 Owner Decisions: Review 02 MINOR Corrections and Final Closure Review

You are continuing the TARS M3 owner-decision recording workflow following I-26 and I-27.

I authorize correction of the two accepted MINOR findings from Independent Codex Review 02, followed by focused verification and one independent closure review.

This authorization does not accept the I-26 reconciliation, authorize a merge, or authorize T2 implementation.

## 1. Mandatory baseline

Expected repository state:

- Branch: `milestone-3-t2-owner-decisions`
- Superset local branch: `m3-t2-owner-decisions-972e4c7c`
- HEAD: `45f80f8523d1ed0033cf9f773d5072e719d4d442`
- Remote HEAD: same SHA
- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Worktree: clean
- I-27 Review 02: PASS, with two MINOR findings
- R1-F1 and R1-F2: resolved

Before editing:

1. Fetch the remote references.
2. Verify HEAD, remote HEAD, branch ancestry, and worktree cleanliness.
3. Verify Review 02's exact verdict and findings.
4. Verify the review evidence checksums.
5. Verify the previous commits' CI results.
6. Verify no protected path has changed since the accepted T1 baseline.
7. Read I-26, I-27, the Review 02 record, and the relevant decision matrix.

If any precondition fails, STOP and report.

## 2. Correct M3T2OD-R2-F1

### Finding

Two cells in the decision matrix still describe `reentry` as proposed, despite the owner's explicit I-26 decision.

### Authorized correction

Correct the two identified cells in the decision matrix.

The resulting matrix must unambiguously state:

- `reentry` is the DECIDED outcome name.
- The precedence `non_finite → reentry → impact → escape` is DECIDED.
- T3 implements these contracts; it does not decide them again.
- T3 retains responsibility for implementation-specific fields and serialization within the approved contract.

Preserve the prior text's provenance using the repository's accepted append-only or explicitly marked supersession convention.

Do not alter the outcome name, precedence, or any other P3 decision.

Search the complete relevant decision documents for additional contradictory status labels, including existing lines rather than only newly added lines.

If another material contradiction is found, document it and STOP rather than expanding this authorization.

## 3. Correct M3T2OD-R2-F2

### Finding

The correction record incorrectly states that `git diff --check` found only Markdown hard breaks.

The recorded output also contains a trailing-whitespace issue in `self_validation.out`, caused by truncation of a label.

### Authorized correction

Preserve the original raw evidence.

Add an accurate correction note to the self-validation record or its associated correction documentation.

Identify:

- The exact additional whitespace finding.
- The cause, as independently verified.
- Whether the finding affects evidence interpretation.
- The result of a fresh whitespace check.

If the generated self-validation artifact itself needs correction, preserve the original evidence and create a clearly distinguished corrected artifact rather than silently rewriting historical output.

Do not claim a clean check unless the fresh command actually passes.

Do not suppress or alter the check's exit status.

## 4. Focused consistency audit

Verify:

1. P1–P5 and P7–P9 remain DECIDED.
2. P6 remains NOT FULLY DECIDED.
3. DR-0028 P6(b) remains OPEN.
4. Q-GATE remains approved and unchanged.
5. DQ-1 through DQ-6 remain decided and unchanged.
6. The floating-point policy remains unchanged.
7. RM-3b remains an unmeasured T4 candidate.
8. The P8 numerical accuracy tests remain report-only where their assumptions are unverified.
9. No historical review evidence has been rewritten.
10. No new scientific or numerical decision has been introduced.

## 5. Independent closure review

After the corrections and self-validation:

Request one focused independent Codex closure review.

Pin the exact correction commit SHA.

Provide the original I-26 decision text, I-27 and I-28 authorizations, and both Review 02 findings.

Require the reviewer to determine:

- Whether R2-F1 is fully resolved.
- Whether R2-F2 is fully resolved.
- Whether the correction introduces a new contradiction.
- Whether the owner decisions remain unchanged.
- Whether the evidence record is accurate.
- Whether the changes comply with the authorized scope.

Require an explicit verdict of PASS or REQUEST_CHANGES.

If REQUEST_CHANGES:

- Record and reproduce the findings.
- Do not fix them without another authorization.
- Do not initiate another review round.
- STOP.

If PASS:

- Prepare a final I-28 closure report.
- Do not independently accept or merge the branch.

## 6. Scope restrictions

This is documentation-only.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify T0 or T1 implementation or evidence.

Do not change numerical constants, thresholds, datasets, golden files, or accepted science contracts.

Do not begin P6 investigation X-1.

Do not implement T2.

## 7. Git and CI

Use the existing owner-decision branch.

Keep correction and review commits separate.

Push with ordinary, non-force pushes.

Verify CI on the pushed commits.

Do not open a PR.

Do not merge.

Do not create a T2 implementation branch.

## 8. Final checkpoint

Report:

- Full HEAD SHA and remote SHA.
- Clean-worktree status.
- Commits and changed files.
- R2-F1 and R2-F2 correction evidence.
- Independent closure-review verdict.
- CI results.
- Remaining scientific uncertainties.
- Confirmation that P1–P9, Q-GATE, and DQ-1–DQ-6 have not changed.
- Fast-forward ancestry status relative to main.
- Whether the I-26 reconciliation is ready for owner acceptance.

Explicitly confirm that nothing has merged and T2 has not started.

## 9. Mandatory STOP

Stop after the corrections, independent closure review, and checkpoint report.

Do not accept, merge, or implement anything without separate owner authorization.

Begin with baseline verification.

## Owner authorization I-27 (verbatim)

# TARS — Authorization I-27
## M3 Owner Decisions: Review 01 Corrections and Independent Review 02

You are continuing the TARS Milestone 3 owner-decision recording workflow following Authorization I-26.

I authorize a narrowly scoped, documentation-only correction of the two accepted findings from Independent Codex Review 01, followed by a focused Independent Codex Review 02.

This authorization does not accept the I-26 decision reconciliation, authorize T2 implementation, approve new DR decisions, or permit merging.

## 1. Mandatory baseline verification

Expected state:

- Remote branch: `milestone-3-t2-owner-decisions`
- Superset local branch: `m3-t2-owner-decisions-972e4c7c`
- HEAD and remote: `a22297d1ec719a58aeb7209f3d34256fa7b0756a`
- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Worktree: clean
- I-26 Codex Review 01: REQUEST_CHANGES
- Open findings: M3T2OD-R1-F1 and M3T2OD-R1-F2

Before editing:

1. Fetch remote references.
2. Verify HEAD, remote HEAD, branch ancestry, and worktree cleanliness.
3. Read the complete I-26 authorization.
4. Read the owner-decision records, reconciliation notes, open-issues register, and revised T2 authorization packet.
5. Read `docs/reviews/M3-T2-owner-decisions-review-01.md`.
6. Verify the recorded reproductions and evidence checksums.
7. Verify that all I-26 changes remain documentation-only.
8. Verify that the reported CI results are green.

If any mandatory precondition fails, STOP and report the discrepancy. Do not reset or overwrite work.

## 2. Authorized correction: M3T2OD-R1-F1

### Problem

The I-26 decision explicitly approved the P3 outcome precedence:

`non_finite → reentry → impact → escape`

However, the recorded reconciliation still describes `reentry` as open for T3 confirmation.

That qualification incorrectly weakens the owner's approved decision.

### Required correction

Add an explicit, append-only clarification to the appropriate authoritative decision and reconciliation records.

The clarification must establish:

1. The `reentry` outcome name is DECIDED.
2. The P3 precedence order is DECIDED.
3. T3 is responsible for implementing these decisions, not approving them again.
4. T3 may define implementation-specific fields and serialization details only within the already approved contract.
5. Any future change to the outcome name or precedence requires a separate owner decision.

Supersede the contradictory "open for T3 confirmation" qualification only to the extent necessary.

Mark OI-23 resolved if, after inspecting its exact wording, this correction fully addresses it. Otherwise preserve the remaining scope explicitly.

Do not change any other P3 behavior.

Do not implement `reentry`.

## 3. Authorized correction: M3T2OD-R1-F2

### Problem

The I-26 reconciliation describes RM-3b as a measured candidate even though the proposed measurement has not been performed.

### Required correction

Replace the unsupported characterization with:

**RM-3b is an unmeasured candidate for evaluation during T4.**

Make clear that:

- RM-3b is not an accepted reference result.
- No measurement has been completed.
- It is not a mandatory acceptance gate.
- Any future promotion requires evidence and the applicable review and authorization.

Preserve the approved RM-0 through RM-8 reference-mission decision.

Do not create or execute an RM-3b experiment under I-27.

## 4. Consistency verification

After applying the corrections:

1. Search all I-26 decision-recording documents for contradictory statements about `reentry`.
2. Verify that the authoritative P3 resolution and dependency matrix agree.
3. Verify that the T3 implementation responsibility is distinguished from the already decided P3 contract.
4. Search for all references to RM-3b.
5. Verify that no document describes RM-3b as measured, certified, accepted, or mandatory without supporting evidence.
6. Verify that P1–P5 and P7–P9 retain their approved status.
7. Verify that P6 remains provisionally selected and unresolved.
8. Verify that the Q-GATE amendment is unchanged.
9. Verify that DQ-1 through DQ-6 are unchanged.
10. Verify that the floating-point validation policy is unchanged.

Do not use this pass to reconsider or expand the owner's decisions.

## 5. Preserve the P8 numerical-validation limitation

The I-26 checkpoint reports that A-FP-2 has not been justified on the supported CI platforms.

Consequently, the proposed numerical geodetic-height accuracy tests that depend on A-FP-2 cannot currently serve as unconditional acceptance gates.

Verify that the revised T2 authorization packet correctly preserves this limitation.

Do not:

- Accept A-FP-2 without evidence.
- Invent a replacement numerical tolerance.
- Promote conditional tests to unconditional gates.
- Claim that agreement with the T0 implementation constitutes independent validation.
- Weaken existing justified domain, boundary, or structural tests.

If the packet already represents this correctly, make no change.

If a contradiction is discovered outside the two authorized findings, record it and STOP rather than expanding scope.

The broader question of how T2 will obtain an independently justified numerical accuracy gate remains for the subsequent implementation authorization.

## 6. Documentation-only scope

Only changes necessary to correct R1-F1, R1-F2, and directly related documentary inconsistencies are authorized.

Historical review records and evidence must remain intact.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify accepted M1, M2, T0, or T1 implementation artifacts.

Do not change pinned constants, reference data, golden results, numerical thresholds, or approved scientific contracts.

No production implementation or numerical experiment is authorized.

## 7. Self-validation

Before independent review:

- Verify the corrected statements against the exact I-26 owner authorization.
- Verify all relevant decision statuses and dependencies.
- Verify append-only preservation of historical records.
- Verify that no unrelated decision was changed.
- Run applicable documentation and repository checks.
- Verify the changed-file scope.

Record the correction matrix and validation evidence.

Commit the corrections separately from the independent review record.

## 8. Independent Codex Review 02

Invoke an independent Codex reviewer using the established repository procedure.

Pin the exact correction commit SHA.

Provide the complete I-26 and I-27 authorizations and the relevant Review 01 findings.

The reviewer must evaluate:

1. Whether R1-F1 is fully resolved.
2. Whether R1-F2 is fully resolved.
3. Whether the corrections introduce new inconsistencies.
4. Whether all I-26 owner decisions remain faithfully recorded.
5. Whether P6 remains unresolved.
6. Whether Q-GATE is unchanged.
7. Whether the P8 conditional-validation limitation remains accurately represented.
8. Whether the changes comply with the documentation-only scope.

Require an explicit verdict:

- PASS
- REQUEST_CHANGES

If REQUEST_CHANGES:

- Record every finding.
- Reproduce it independently where feasible.
- Assign a documented disposition.
- Do not fix the new findings.
- Do not initiate Review 03.
- STOP for owner authorization.

If PASS:

- Prepare the final I-27 checkpoint.
- Do not independently accept the decision package.
- Do not merge.

## 9. Git and CI requirements

Use the existing owner-decision branch.

Commit the correction and review evidence separately.

Push with ordinary, non-force pushes.

Verify remote HEAD and worktree cleanliness.

Verify CI results on the pushed commits.

Do not create a PR.

Do not merge into main.

Do not create a T2 implementation branch.

## 10. Final checkpoint

Report:

- Branch and full HEAD SHA.
- Remote HEAD and worktree status.
- Exact commits and changed files.
- R1-F1 and R1-F2 correction matrix.
- Independent Review 02 verdict.
- Any new findings.
- CI results.
- P1–P9 status.
- Q-GATE and DQ-1 through DQ-6 status.
- Remaining P6 and P8 validation uncertainties.
- Readiness for owner acceptance of the I-26 reconciliation.
- Whether a fast-forward merge to main is possible.

Explicitly confirm:

- No new owner decision was made.
- No T2 implementation started.
- No protected file changed.
- No PR was opened.
- Nothing was merged.
- Main remains unchanged.

## 11. Mandatory STOP

Stop after the authorized corrections, independent Review 02, and checkpoint report.

Do not proceed to Review 03, acceptance, merge, or implementation without separate authorization.

Begin with baseline verification.

## Owner authorization I-26 (verbatim)

# TARS — Authorization I-26
## M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation

You are working on the TARS spacecraft simulation project.

This authorization follows I-23, I-24, and I-25, which prepared and independently reviewed the M3 T2 decision-readiness package.

The owner has reviewed the recommendations and explicitly approved the decisions specified below.

Your task is to record those decisions in their authoritative decision records, reconcile the resulting requirements, and prepare a revised T2 implementation authorization packet.

**This is a decision-recording authorization, NOT a T2 implementation authorization.**

## 1. Workspace and baseline

This is a new Superset workspace for the owner-decision phase.

Expected repository state:

- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Reviewed planning branch: `milestone-3-t2-decision-readiness`
- Reviewed planning HEAD: `a57de3f`
- I-25 Independent Codex Review 03: PASS, no findings
- Review 01: six findings resolved
- Review 02: three findings resolved
- T1: accepted and merged
- T2: not authorized
- DR-0029 P10: previously decided
- DR-0029 P1–P9: open before I-26

### Mandatory checks

1. Fetch all relevant remote references.
2. Verify the exact main and planning-branch SHAs.
3. Verify the reviewed planning worktree is clean.
4. Verify Review 03's verdict and the corresponding evidence.
5. Verify no protected paths changed during I-23 through I-25.
6. Read the complete authoritative decision records before editing.

Read at minimum:

- `DR-0029-m3-t0-proposals.md`
- `DR-0029-P1-P9-owner-decision-packet.md`
- `DR-0029-P1-P9-owner-briefing.md`
- `M3-T2-authorization-packet.md`
- `M3-T2-validation-strategy.md`
- DR-0024 through DR-0028, including applicable amendments
- The M3 proposal and milestone dependency matrix
- I-25 final readiness report and Review 03

The authoritative DR text governs where the briefing or packet differs.

If a discrepancy would materially change an approved choice, STOP and report it rather than guessing.

### Branching

Create a new decision-recording branch and worktree from the verified planning HEAD:

`milestone-3-t2-owner-decisions`

Follow the repository's established Superset worktree and remote-branch conventions.

Do not reuse the T1 implementation worktree.

Do not modify main directly.

## 2. Approved DR-0029 decisions

The following are explicit owner decisions.

Record them append-only in the authoritative DRs, preserving historical proposal text and decision provenance.

### P1 — Termination-altitude admissibility

**DECIDED: A4-b.**

Use:

- v̂ = V_b, the derived bound for bound-state relative velocity.
- κ = 0.01.
- Clause 1: a − b < h_f < h_geod(initial).
- Clause 2: ρ(h_f) × V_b × dt / B_min ≤ 0.01.

The ballistic coefficient uses dry mass.

Record that this is a necessary admissibility screen, not a sufficient numerical stability or trajectory-accuracy guarantee.

The derivation bounds the drag velocity-Jacobian contribution only. It does not bound the full coupled dynamics or ∂a/∂r.

κ is an owner-selected engineering constant, not a physically established universal threshold.

The final M3 timestep remains a separate decision.

### P2 — Termination crossing

**DECIDED: A5-b.**

Detect termination from committed states and report an additional scalar cubic-Hermite estimate of the crossing time.

The simulation ends at the committed state, not the interpolated crossing.

The reported crossing time is not a propagated state.

No final-step splitting is authorized.

Missed crossings or dips between committed states remain a documented limitation. Do not claim a certified perturbed-motion missed-dip bound.

T2 must expose the geodetic normal or latitude required for T3 to compute dh/dt.

### P3 — Outcome precedence

**DECIDED: Adopt the DR-0029 proposal.**

Precedence:

1. `non_finite`
2. `reentry`
3. `impact`
4. `escape`

Preserve `impact` as the legacy backstop.

Termination is determined from geodetic height, independently of atmospheric band selection.

Preserve the published density discontinuities.

This decision specifies future T3 behavior; do not implement it under I-26.

### P4 — Below-domain density

**DECIDED: Option (ii), fail closed.**

Any finite geodetic height below 0 m must cause a typed atmosphere-domain error.

The domain guard must compare height in metres before conversion to kilometres.

Negative zero is in range.

Non-finite heights receive a distinct error classification.

A failing RK4 stage must not commit a partial simulator state.

Explicitly reconcile DR-0026 AR-8 and §5.8: statements that density is total do not apply below the atmospheric table's lower edge.

T3 will define the versioned run-outcome mapping. Do not implement that mapping now.

Do not reproduce the T0 spike's negative-subnormal guard defect.

### P5 — Atmospheric altitude regions

**DECIDED: Adopt the DR-0029 P5 region table**, consistently with P1 and P4.

For heights above the 1000 km base, extrapolate the pinned top atmospheric band. Do not introduce a zero-density cutoff or a new upper-domain failure.

Preserve the pinned density table exactly.

Adopt the proposed wording amendment:

The top band's formula is continuous for h > 1000 km, but the 1000 km base retains its published relative density jump of approximately −1.598 × 10^-5.

Do not impose continuity across band boundaries.

Retain the published GMAT band-selection rule and exact-base behavior.

Explicitly label extrapolated densities above 1000 km as unverified.

### P6 — GMAT reference configuration

**NOT FULLY DECIDED.**

Approve decomposed exact-configuration method (d) as the preferred direction for subsequent validation planning, subject to its authoritative configuration requirements.

Do not mark P6 fully resolved.

The geodetic-drag discrepancy of approximately 0.14–0.38 m remains escalated.

Do not approve an independent geodetic GMAT acceptance gate.

Do not silently decide DR-0028 P6(b). Prepare a separate, explicit owner ruling on whether driving the validator with GMAT's reported axis is within the previously approved Earth-orientation scope.

The proposed X-1 investigation remains unexecuted and requires separate authorization.

Record the provisional method selection without converting unresolved evidence into a PASS.

### P7 — Reference missions

**DECIDED: RM-0 through RM-8.**

Use the P1 admissibility rule for RM-8.

Use the P9 illustrative vehicle definitions.

RM-3b is a candidate to be measured during T4, not a new mandatory gate without subsequent approval.

Preserve all previously accepted M1/M2 requirements.

### P8 — Geodetic-height reference points

**DECIDED: Options (a) and (a′), with the reviewed gating restrictions.**

Use exact mathematical answers as the primary gate source within their justified domain.

Use forward-constructed points as additional reference evidence.

Forward-constructed points become gating only after their numerical construction-error contribution has been derived and reviewed.

Negative-height cases remain report-only until appropriate bounds exist.

GeographicLib, GMAT and the identified IOGP/EPSG example are corroboration sources, not automatically authoritative inverse-height gates.

Do not claim independent verification from a reference that shares the same unexamined assumptions.

### P9 — Validation vehicles

**DECIDED: Option (i).**

Use the specified illustrative V1 and V2 vehicles from DR-0029.

V1:

- Mass: 850 kg
- Area: 15 m²
- C_d: 2.2
- Ballistic coefficient: approximately 25.8 kg/m²

V2 uses the accepted M2 vehicle mass configuration with area 15 m², as specified in DR-0029.

Every scenario and record must label these values:

**ILLUSTRATIVE — VALIDATION ONLY**

Do not claim they are validated representations of a real spacecraft.

## 3. Q-GATE — Approved amendment

The owner explicitly approves narrowing the original I-15 prerequisite for T2.

The replacement rule is:

**Before T2 implementation may be authorized:**

- P1–P5 must be decided.
- P8 and P9 must be decided.
- DQ-1 through DQ-6 must be decided.
- The resulting contracts must be recorded and reconciled.
- An explicit, separate T2 implementation authorization is required.

P10 remains previously decided and binding for T1.

P6 is not a T2 implementation prerequisite. Its unresolved scientific questions remain blockers for geodetic GMAT acceptance in T5.

P7 must be decided before its reference-mission obligations are implemented in T3/T4; it is already approved in this authorization.

This amendment supersedes only the broader T2 dependency statement from I-15. It does not waive any scientific, review, numerical or acceptance gate.

Record the supersession explicitly with provenance.

## 4. Approved T2 design decisions

### DQ-1 — Geodetic algorithm

**DECIDED: α.**

Reproduce the T0 iterative geodetic-height algorithm operation for operation within its applicable domain, including its starting latitude, convergence criterion and pole-safe height calculation.

The T0-specific error bounds may be reused only where their original assumptions and arithmetic sequences actually apply.

The T0 domain-guard defect must not be copied.

Record that this deterministic, data-dependent iterative algorithm satisfies the intended T2 geodetic design requirement.

### DQ-2 — Density arithmetic

**DECIDED: km route.**

Preserve the T0/GMAT kilometre-based density arithmetic for the applicable formula evaluation.

The lower-domain guard must still operate on height in metres before conversion.

Explicitly document the departure from DR-0024 §9's proposed convert-once-to-SI wording.

Do not change the pinned atmospheric table or silently substitute a mathematically equivalent but numerically different expression.

### DQ-3 — Simulator integration

**DECIDED: (a).**

T2 may add the context-aware force protocol and integrate immutable ForceContext construction into the simulator's derivative closures.

Current stage mass must be used.

Preserve the legacy force-model interface through an adapter.

Existing M1/M2 behavior must remain byte-identical on the specified same-platform regression gates.

No change to tick logic, engine scheduling, step splitting or atomicity is approved by this decision.

Implementation still requires separate authorization.

### DQ-4 — Dataset storage and digest

**DECIDED: Pinned data file under `src/tars/sim/data/`, with its SHA-256 digest pinned in `tars.sim`.**

Use the recorded GMAT R2026a source digest.

Do not import `tars.validation.approved_digests` from the physics core.

Use the approved file-access mechanism compatible with the static architecture guard.

Verify the data file is packaged correctly.

If packaging requires a protected `pyproject.toml` change, STOP. Do not silently adopt embedded Python bytes.

The embedded-bytes alternative requires separate approval.

### DQ-5 — J2 integration

**DECIDED: (a).**

Wrap the accepted T1 J2 implementation through the legacy adapter.

Do not rewrite the J2 force class, change its constants or create a replacement J2 model.

Preserve all T1 evidence and validation gates.

### DQ-6 — Drag parameter ownership

**DECIDED: Immutable drag-component constructor parameters.**

C_d and cross-sectional area belong to the drag force component.

Mass comes from ForceContext.

Scenario v3 schema and serialization remain T3 responsibilities.

No new spacecraft schema is authorized in T2.

## 5. Conditional floating-point gates

The owner approves the following policy:

- A-FP-2, A-LM-1 and A-LM-2 are not accepted as universal IEEE-754 guarantees.
- Tests depending on these assumptions may gate only when the precise assumption has been independently justified for the supported execution environment and the resulting criterion has been reviewed.
- Until then, those tests are report-only.
- Exact z-reflection symmetry and strict density decrease remain report-only regardless of the above assumptions.
- Do not promote an unproved numerical bound into a mandatory acceptance criterion.
- Do not invent tolerances.
- Preserve all unconditional, independently justified gates.

The revised T2 authorization must identify every conditional row and the evidence required to promote it.

## 6. Recording and reconciliation

Record the approved decisions in their authoritative home records.

Use append-only resolution entries or the repository's accepted decision-recording convention.

Update:

- DR-0024 through DR-0029 as applicable.
- The M3 decision matrix.
- The T2 dependency matrix.
- The owner-decision briefing and packet.
- The M3 open-issues register.
- The T2 validation strategy.
- The draft T2 authorization packet.
- The milestone index where needed.

Preserve historical proposal text, previous review records and prior owner decisions.

Do not retroactively rewrite the I-23/I-24/I-25 evidence.

Distinguish clearly between:

- DECIDED
- PROVISIONALLY SELECTED
- OPEN
- ESCALATED_FOR_INVESTIGATION
- NOT AUTHORIZED

In particular, P6 must not be recorded as fully decided.

## 7. Independent verification

Before requesting implementation authorization:

1. Verify every recorded decision against the owner's exact wording above.
2. Verify that all dependent DR entries are consistent.
3. Verify the new T2 gate does not waive T3/T4/T5 requirements.
4. Verify the validation strategy matches the selected algorithms and arithmetic.
5. Verify the accepted T0/T1/M1/M2 contracts are preserved.
6. Verify the revised T2 authorization draft contains no implied approval to execute.
7. Verify all changes are documentation-only.

Run applicable documentation checks.

Request an independent Codex review of the decision recording and reconciliation, including the revised dependency gate and conditional validation policy.

If the review returns REQUEST_CHANGES, record and reproduce the findings, then STOP. Do not begin an unapproved correction loop.

If the review returns PASS, prepare the final owner checkpoint.

## 8. Version-control restrictions

All changes under I-26 must be documentation-only.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify golden references, pinned constants, numerical thresholds or existing accepted implementation artifacts.

Commit the decision recording and independent review evidence separately.

Push using ordinary, non-force pushes.

Do not merge or open a PR.

Do not change main.

## 9. Final deliverables

Produce:

1. Recorded P1–P5, P7–P9 decisions.
2. P6 provisional method-selection record and unresolved investigation register.
3. Explicit Q-GATE amendment.
4. Recorded DQ-1 through DQ-6.
5. Reconciled authoritative decision documents.
6. Updated dependency matrix.
7. Revised T2 validation strategy.
8. Revised T2 implementation authorization packet, marked **DRAFT — NOT AUTHORIZED**.
9. Independent Codex review record.
10. Final I-26 checkpoint report.

The checkpoint must include:

- Branch and exact HEAD.
- Commit list.
- Changed-file list.
- CI results.
- Decision-by-decision recording matrix.
- Independent review verdict.
- Remaining blockers and scientific uncertainties.
- Exact recommended next authorization.

Explicitly confirm that T2 has not started, no implementation files have changed, and nothing has merged.

## 10. Mandatory STOP

Stop after documentation reconciliation, independent review and checkpoint reporting.

Do not create the T2 implementation branch.

Do not implement the drag force.

Do not merge the owner-decision branch.

Do not start the P6 investigation.

Do not approve DR-0028 P6(b).

Do not authorize T3, T4 or T5.

Await the owner's next explicit authorization.

Begin with baseline verification.
