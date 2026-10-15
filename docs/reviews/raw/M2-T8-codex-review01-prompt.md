You are an independent reviewer from a separate provider; you did not write this code. This is TARS Milestone 2 (propulsion), task T8: the full M2 Proof run, the Proof record, the README update, and the external milestone review. Review round 1.

The snapshot is the current directory: a git clone of the branch at HEAD, with git metadata. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/`, which is git-ignored by `.git/info/exclude`.

## Context
- Milestone plan and Proof requirements P1–P12: `docs/milestones/M2-propulsion.md` (§9 defines T8: "Full Proof run, Proof record, README update, external review, dispositions"; §10 defines P1–P12).
- Proof system: `proof/PROOF.md`, `proof/review.md`, `proof/architecture.md`, `proof/physics.md`, `proof/mission.md`, `proof/definition-of-done.md` (prototype bar).
- T1–T7 are complete; each passed its own independent review (`docs/reviews/M2-T*-review-01.md`). T7 was accepted by the Tech Lead at `963dbe7` after DR-0023 (approved thresholds, three-platform final-state gate).
- T8 changes since `963dbe7` (see `git log 963dbe7..HEAD` and `git diff 963dbe7..HEAD`):
  - `toolbox/scripts/run_m2_proof.sh` (new) and the `toolbox/scripts/README.md` table;
  - the README M2 section;
  - `proof/records/evidence/M2/`: the evidence of the full run at `c304b53`, on the reference host;
  - the T8 section of `proof/records/M2-propulsion.md` and the header and T7 status updates;
  - the status line of `docs/milestones/M2-propulsion.md`.
- Review threat model and blocking rule unchanged: DR-0019 option B, DR-0020 option A, DR-0022 option B (`docs/decisions/requests/`). Bad simulator, GMAT, reference, threshold or workflow data is in scope; adversarial replacement of validator code or in-memory state is not.
- Hard constraints for T8: no approved threshold, reference baseline, golden, contract or validation semantics may change; the M1 golden hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` must hold; M2 is not declared complete (that is the Tech Lead's decision).

## Tasks
1. **Proof record accuracy.** For every claim in the T8 section of `proof/records/M2-propulsion.md` (commands table, P1–P12 table, standard gate, discrepancies, limitations), check it against the committed evidence in `proof/records/evidence/M2/` and against your own re-run. Flag any number, status or statement that is wrong, unsupported, overstated, or that marks a requirement met without adequate evidence. Check that P12 is not claimed before this review.
2. **Independent re-run.** Run, at HEAD:
   - `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider` (full suite, about 25–30 minutes);
   - `.venv/bin/ruff check . && .venv/bin/ruff format --check .`;
   - `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`, then compare it check by check (validator, metrics, thresholds, passed) with `proof/records/evidence/M2/m2_proof_report.json`;
   - `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`, `toolbox/validators/determinism.py` (M1 and each `scenarios/m2_*.json`), `toolbox/validators/cross_platform.py`, `toolbox/scripts/gmat_m1.py compare`, `toolbox/scripts/gmat_m2.py compare`, `toolbox/scripts/reference_snapshot.py verify-baseline toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz`, and `toolbox/scripts/run_mission.py` for each M2 scenario (into `review_scratch/`).
3. **`run_m2_proof.sh`.** Review it statically (it calls `uv`, which may be unavailable or offline in your sandbox; run it only if it works, with an evidence directory under `review_scratch/`). Can any failing step still produce `overall: PASS` or exit 0? Is the clean-tree flag computed before evidence is written, and is it correct? Can it overwrite `proof/records/evidence/M1/`? Does it cover every gate CI runs for M1 and M2?
4. **README.** Are the M2 commands correct and runnable as written? Is any statement about behaviour or limitations inaccurate?
5. **No semantic change.** Confirm from `git diff 963dbe7..HEAD` that no source, test, threshold, reference, golden, snapshot, contract or CI file changed, and that `proof/thresholds/m1.json`, `proof/references/m1_final_state.json` and the M1 GMAT reference files are unchanged against `main` (`git diff main..HEAD -- …`).
6. **Milestone-level review.** Judge whether the delivered M2 meets its plan (scope §2, physics §3, architecture §4, numerical requirements §5, events §6, replay §7, tests §8, Proof §10) and its non-goals, using the code, the tests and the earlier review records. Look for: any P1–P12 requirement that is not actually demonstrated by an executable check; any earlier finding left without a disposition; any open Critical or High issue; any claim in the milestone records that the code contradicts. Do not re-litigate decisions the Tech Lead approved (DR-0010…DR-0023), but report evidence that the implementation does not do what they say.

## Output
Your final message, in Markdown. Give one block per substantive finding, numbered from T8-F1:

### T8-F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...

Then a **Summary** with exactly one verdict — PASS (unconditional), REQUEST_CHANGES or FAIL — a list of what you verified (with the numbers you reproduced), and a one-line statement of whether M2 is ready for the Tech Lead's final milestone review. Label pure style remarks "Note", with no severity. A finding is blocking only if it affects a check, a reported value, an acceptance decision or a physical invariant (DR-0020).
