You are an independent reviewer from a separate provider; you did not write this code. This is TARS Milestone 2, review round 3 of the T8 review record: a narrow pre-merge check of the Tech Lead acceptance commit.

The snapshot is the current directory: a git clone of the branch at HEAD, with git metadata, and a ready environment in `./.venv`. You review; you do not fix. Do not modify tracked files. Put scratch files only under `./review_scratch/` (git-ignored by `.git/info/exclude`).

## Context
- Your round 2 at `31f2fc1` returned an unconditional PASS. Commit `cd8fdd8` recorded it.
- The Tech Lead then accepted M2, contingent on six conditions verified before the merge:
  1. the PR #3 diff (`origin/main..HEAD`) contains only authorized M2 changes;
  2. contracts, numerical thresholds, GMAT references, golden artifacts and validation semantics are unchanged;
  3. the M2 Proof passes 228/228, and the evidence corresponds to the verified code revision;
  4. CI is green on the merge candidate (the implementer checks this separately);
  5. the T8 review is an unconditional PASS with no unresolved blocking findings;
  6. the working tree is clean, and no unreviewed changes have been introduced.
- The Tech Lead also directed that DR-0015 be updated from conditionally approved to approved, citing evidence for both conditions, with the accepted residual risks and margins preserved.
- The implementer's acceptance commit is `3dfffb3` (`git show 3dfffb3`). It is records-only. Later commits only add this prompt under `docs/reviews/raw/`. The commit changes:
  - `proof/records/M2-propulsion.md` (header);
  - `docs/decisions/requests/DR-0015-…md`;
  - `docs/milestones/M2-propulsion.md`;
  - `docs/milestones/README.md`.

## Tasks
1. Confirm that `3dfffb3` changes only those four record files, that later commits add only review prompts, and that `git diff cd8fdd8..HEAD` and `git diff 017d7f6..HEAD` touch no code, test, scenario, threshold, reference, golden, snapshot, contract, validator or CI file.
2. Check every factual statement added by `3dfffb3` against the repository: the digests (`shasum -a 256`), the paths unchanged since `963dbe7`, the M1 assets identical to `origin/main`, 228/228, the evidence revision, and the review status. Check DR-0015's cited evidence for both conditions: VAL-0010/DR-0016, and VAL-0013…0017/DR-0023. Flag anything wrong, overstated or unsupported, and any residual risk or margin that was dropped or altered.
3. Independently check conditions 1, 2, 3, 5 and 6 yourself:
   - for condition 1, inspect `git diff --name-status origin/main..HEAD` and the content of modifications to files that pre-exist on `origin/main`;
   - for condition 3, run `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json` and compare it with `proof/records/evidence/M2/m2_proof_report.json`.
4. Confirm that the records do not claim the merge has already happened.

## Output
Your final message, in Markdown: one block per substantive finding, numbered from T8-F6, using the same format as before (Severity, Claim, Evidence, Suggested fix). Then a **Summary** with exactly one verdict (PASS (unconditional), REQUEST_CHANGES or FAIL), and your result for each of conditions 1, 2, 3, 5 and 6. Label pure style remarks "Note". A finding is blocking only if it affects a check, a reported value, an acceptance decision or a physical invariant (DR-0020).
