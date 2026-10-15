You are an independent reviewer from a separate provider; you did not write this code. This is TARS Milestone 2 task T8, review round 2: a re-verification after your round-1 REQUEST_CHANGES.

The snapshot is the current directory: a git clone of the branch at HEAD, with git metadata, and a ready environment in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/`, which is git-ignored by `.git/info/exclude`.

## Context
- Your round-1 review (`./previous-review.md`, at `adb3710`) returned REQUEST_CHANGES with T8-F1 to T8-F5.
- The dispositions are in `docs/reviews/M2-T8-review-01.md`, "Round 1": all five ACCEPTED. T8-F3 was fixed in `42878c6` (found independently by the implementer before your report arrived); the others in `017d7f6`. The fix diff is `./R2-fix.diff` (`adb3710..HEAD`).
- After the fixes, the full suite was re-run with the corrected script at `017d7f6`. The committed evidence (`proof/records/evidence/M2/`) and the Proof record now cite `017d7f6`. The implementer reports that `m2_proof_report.json` is byte-identical to the earlier `c304b53` run.
- Threat model, blocking rule and T8 constraints are unchanged (DR-0019 B, DR-0020 A, DR-0022 B; no threshold, reference, golden, contract or validation-semantics change; M2 completion is the Tech Lead's decision).

## Tasks
1. Verify each finding is resolved, re-running your own reproductions where you can (the round-1 `publish_probe` and `cleanliness_probe` are summarized in `docs/reviews/raw/M2-T8-codex-review01-scratch/`):
   - T8-F1: a failed publication, a missing artifact or a failing step cannot give `overall: PASS` or exit 0; a stale artifact from an earlier run cannot stand in for one this run did not produce.
   - T8-F2: the M1 evidence directory, any path inside it, any alias (symlink, `..`, trailing slash, absolute or relative path) and the repository root are refused before anything is written.
   - T8-F3: the clean-tree flag is correct for in-repository, absolute and out-of-repository destinations and fails closed on git errors.
   - T8-F4 and T8-F5: the script, README, scripts table and Proof record describe the scope and run counts accurately.

   `uv` may be unavailable; a stub `uv` on `UV=` is a valid way to exercise the script's control flow.
2. Check that the fixes introduced no new defect in the script, for example quoting, `set -u` failures, `python3` availability, or behaviour with the default destination.
3. Check the re-run evidence: `proof/records/evidence/M2/proof_run.log` (revision `017d7f6`, clean tree, 20 steps, all exit 0) and the claim that `m2_proof_report.json` is unchanged from `c304b53` (`git diff c304b53..HEAD -- proof/records/evidence/M2/m2_proof_report.json`). Check the Proof record's T8 section against the evidence again.
4. Confirm again that no source, test, threshold, reference, golden, snapshot, contract or CI file changed since `963dbe7`, and that the M1 assets are unchanged against `main`.
5. Re-run what you need to be confident; at minimum `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`, compared check by check with the committed report, and Ruff. Running the full pytest suite again is optional, because no Python changed since your round-1 run; say whether you ran it.

## Output
Your final message, in Markdown. Give one block per substantive finding, numbered from T8-F6:

### T8-F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...

Then a **Summary** with exactly one verdict — PASS (unconditional), REQUEST_CHANGES or FAIL — the status of T8-F1 to T8-F5, a list of what you verified, and a one-line statement of whether M2 is ready for the Tech Lead's final milestone review. Label pure style remarks "Note", with no severity. A finding is blocking only if it affects a check, a reported value, an acceptance decision or a physical invariant (DR-0020).
