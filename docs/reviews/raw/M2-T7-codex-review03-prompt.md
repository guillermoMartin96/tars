You are an independent reviewer from a separate provider; you did not write this code. You are reviewing TARS Milestone 2 task T7, round 3: the application of the approved DR-0023 and the implementation of the M2 cross-platform final-state gate.

The snapshot is the current directory: a git clone of the branch at HEAD (see `git log`), with git metadata. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/` or `proof/`. Put scratch files only under `./review_scratch/`, which is git-ignored by `.git/info/exclude`.

## Context
- The T7 measurement and DR-0023 passed your round 2, unconditionally, at 8fe709f.
- The Tech Lead then approved DR-0023 on 2026-10-14. The approval and its conditions are in the "Resolution" section of `docs/decisions/requests/DR-0023-m2-final-thresholds.md`. In summary:
  1. Finalize every existing M2 threshold value unchanged. Update `m2.json` and its approved digest in the same reviewed commit. Alter no numerical threshold, reference value, tolerance, scenario or existing acceptance check.
  2. FU-1 is approved for closure. The O9 GMAT-vs-DOP853 thresholds stay at 3e-5 m and 3.5e-8 m/s. The record must document the pinned-snapshot rationale, host dependence, noise-floor measurements and actual detection guarantees, and must not claim absolute physical accuracy.
  3. O6: no change. The dedicated SMA tolerance class is recorded only as a future improvement that needs separate approval and a reviewed snapshot baseline.
  4. Implement the DR-0015 cross-platform final-state gate: position ≤ 1e-4 m and velocity ≤ 1e-7 m/s. The implementation must:
     - compare identical canonical mission inputs at the same pinned revision;
     - require macOS x86_64, Linux x86_64 and macOS arm64;
     - use Euclidean position and velocity differences;
     - validate provenance, input digests, platform identity, completeness and revision consistency;
     - fail closed when evidence is missing, corrupted, inconsistent or stale;
     - test threshold boundaries, deliberate perturbations, missing platforms, mismatched inputs and malformed evidence;
     - be a required CI acceptance gate;
     - retain evidence beyond the 90-day CI artifact expiry;
     - preserve every existing M1 and M2 acceptance criterion.
- **Threat model** (DR-0019 B, DR-0022 B): bad simulator, reference, threshold and workflow *data* are in scope. Deliberate modification of validator code or in-memory state is out of scope. A finding is blocking only if it has a concrete effect on a check, a reported value, an acceptance decision or a physical invariant (DR-0020).

## Changes to review
`./R3.diff` covers 77995b9..HEAD. Of the commits:
- 27e5b8b is the implementation.
- 0f95de3 adds the golden record, its pin and the archived evidence.
- 777d1f3 makes the M2 Proof's `Gates` load and validate the golden itself, and adds fail-closed Proof tests.
- The last commit adds this prompt.

The files are:
- `proof/thresholds/m2.json` and `src/tars/validation/approved_digests.py`;
- `src/tars/validation/thresholds.py`;
- the new `src/tars/validation/m2_cross_platform.py` and `toolbox/validators/m2_cross_platform.py`;
- the M2 Proof integration in `toolbox/validators/m2_proof.py`;
- `.github/workflows/ci.yml`: `macos-15-intel` added to the matrix, a collect step and the `m2-cross-platform` job;
- `proof/references/m2_final_states.json`, the golden record;
- `proof/records/evidence/M2-T7/cross-platform/`, the archive;
- the new `tests/test_m2_cross_platform.py`, with edits to existing tests;
- VAL-0017 in `docs/science/validation.md`, the DR-0023 Resolution and Implementation sections, `proof/physics.md` and `toolbox/validators/README.md`.

The T7 reference-host bundle at 2870392, which you reviewed in round 2, is in `./t7-reference-host/`. Its `bundle.json` → `mission_finals` holds the T7 final states. `./m2_proof_before.json` is the pre-change M2 Proof report, 215 checks, from the same host.

## Tasks
1. **DR-0023 items 1–3.**
   - Verify that every pre-existing `m2.json` limit is numerically unchanged. Only the status, approval fields, basis and limit_basis text change, plus the new `cross_platform` group.
   - Verify that the digest pin matches.
   - Check the FU-1 and O6 text against the DR-0023 conditions and the VAL-0016 evidence. Look in particular for any claim of absolute accuracy and for the detection figures.
2. **Preservation.**
   - Run the M2 Proof and compare it with `./m2_proof_before.json`. Every earlier check must be present, with identical thresholds and metrics; only additions are allowed.
   - Confirm that the M1 thresholds, the M1 golden (`proof/references/m1_final_state.json`, event-log digest 7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4), the reference snapshot baseline 3 pin, the GMAT manifest pin and all tolerances are unchanged.
   - Confirm that no CI step was removed or weakened.
3. **The gate's correctness and fail-closed behaviour.**
   - Look for any way that missing, corrupted, inconsistent, stale, mislabelled or wrong-platform evidence could pass. Cases to consider:
     - records from another revision or another CI run;
     - duplicates;
     - Rosetta;
     - a mislabelled platform id;
     - a non-finite or malformed vector;
     - missing or extra missions;
     - a changed scenario;
     - a PR merge commit compared with a push commit;
     - partial artifact download;
     - a failed platform job;
     - the `!cancelled()` condition.
   - Check that the Euclidean metrics and the boundary semantics (≤ limit passes) are right.
   - Check the golden handling: the pin, the reference-host requirement, staleness, and how the M2 Proof behaves when the golden is missing or invalid.
4. **Evidence and claims.**
   - Re-run the gate on the archive: `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_cross_platform.py gate proof/records/evidence/M2-T7/cross-platform/{reference-host,ubuntu-latest,macos-latest,macos-15-intel}.json --revision 27e5b8bf4e1d159388b16570a65c37e1a7db9518`.
   - Recompute the VAL-0017 figures independently from the records: per-mission worst values, the per-pair maxima, the bit-identity of reference host and Intel runner, and the bit-identity with the T7 reference-host bundle.
   - Check the manifest digests and that the golden matches `reference-host.json` byte for byte.
   - Check the provenance in each record: revision, clean tree, CI run, runner architecture, CPU.
5. **Platform coverage.**
   - CI's macOS x86_64 is a GitHub `macos-15-intel` runner, not the local reference host. The reference host enters through the pinned golden record, which every platform's M2 Proof checks, and through the archive.
   - Assess whether this satisfies "require macOS x86_64, Linux x86_64, and macOS arm64" without an unapproved substitution, and say clearly if you think it is a decision for the Tech Lead.
6. **Tests.**
   - Do the new tests actually exercise boundaries, perturbations, missing platforms, mismatched inputs and malformed evidence?
   - Would they fail if the corresponding check were removed? Mutation-test a few checks in a scratch copy under `review_scratch/`, never in place.

## Run
- `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`. The full suite takes about 20 minutes. You may first run `tests/test_m2_cross_platform.py`, `tests/test_m2_validation.py` and `tests/test_gmat_m2.py`, but run the full suite at least once.
- `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/cross_platform.py`
- `PYTHONPATH=src .venv/bin/python toolbox/scripts/gmat_m1.py compare` and `PYTHONPATH=src .venv/bin/python toolbox/scripts/gmat_m2.py compare`
- the archive gate command above, plus `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_cross_platform.py collect --out review_scratch/local.json`. The local record will show `tree_clean` false if you leave untracked files outside `review_scratch/`.

## Output
Your final message, in Markdown. Give one block per substantive finding, numbered from T7-F7:

### T7-F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...

Then a **Summary** with exactly one verdict — PASS (unconditional), REQUEST_CHANGES or FAIL — and a list of what you verified. Label pure style remarks "Note", with no severity.
