You are an independent reviewer from a separate provider; you did not write this code. This is TARS Milestone 2 task T7, review round 4: a re-verification after your round-3 REQUEST_CHANGES.

The snapshot is the current directory: a git clone of the branch at HEAD, with git metadata. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/` or `proof/`. Put scratch files only under `./review_scratch/`, which is git-ignored by `.git/info/exclude`.

## Context
- Your round-3 review (`./previous-review.md`) at fbdbe77 returned REQUEST_CHANGES with one finding, T7-F7 (High): a relabelled Linux record could fill the macOS x86_64 slot.
- The disposition is in `docs/reviews/M2-T7-review-01.md`, section "Round 3": ACCEPTED and fixed in 4c0d2ef. The fix diff is `./R4-fix.diff` (fbdbe77..HEAD).
- The same commit also relaxes one Proof-integration test, `test_proof_fails_closed_on_an_unusable_or_disagreeing_golden[perturbed]`. It had failed on Linux CI because it expected exactly 1.5e-4 m, ignoring that platform's genuine drift from the macOS x86_64 golden.
- Everything else is unchanged from what you verified in round 3: the DR-0023 approval conditions (`docs/decisions/requests/DR-0023-m2-final-thresholds.md`, Resolution), the threat model (DR-0019 B, DR-0022 B) and the blocking rule (DR-0020).

## Tasks
1. Verify that T7-F7 is resolved.
   - Re-run your own reproduction (`review_scratch/wrong_platform.py` from round 3 is not present; reconstruct it) and variants:
     - CI provenance removed;
     - runner OS set to a value consistent with the fake label, but the environment OS left as Linux;
     - the environment OS forged consistently but the runner OS left as Linux.
   - Look for any remaining way a record from one platform can be accepted as another required platform, using data edits only.
2. Check that the new checks reject no genuine record: the four archived records, and a fresh `collect` on this host.
3. Check that the test relaxation (abs 1e-5 m) does not weaken what the test proves. It must still fail for a golden that agrees, and still show the Proof fails on a 1.5e-4 m disagreement.
4. Confirm that no other behaviour changed, that no threshold, reference, tolerance or check changed, and that the round-3 verified items still hold.

## Run
- `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`, the full suite, about 25 minutes;
- `.venv/bin/ruff check . && .venv/bin/ruff format --check .`;
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`;
- the archive gate: `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_cross_platform.py gate proof/records/evidence/M2-T7/cross-platform/{reference-host,ubuntu-latest,macos-latest,macos-15-intel}.json --revision 27e5b8bf4e1d159388b16570a65c37e1a7db9518`.

## Output
Your final message, in Markdown. Give one block per substantive finding, numbered from T7-F8:

### T7-F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...

Then a **Summary** with exactly one verdict — PASS (unconditional), REQUEST_CHANGES or FAIL — and a list of what you verified. Label pure style remarks "Note", with no severity.
