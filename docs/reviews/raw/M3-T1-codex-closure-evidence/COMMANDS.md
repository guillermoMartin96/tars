# Focused closure verification command ledger

All commands ran in the supplied clone with no network. Scratch mutations, archives, scripts, and outputs are under `review_scratch/`. No tracked files were edited.

- `git status --short`, `git rev-parse HEAD`, `git rev-parse main`, `git log --oneline d01d6aa..HEAD`: clean; pinned e404b0f40a3a46c0a71041636e0f87eb5fa247f3; main 60648b93385a9954194730006aeac29ea14875ad; exactly 481a62e and e404b0f (full history saved in commits.log).
- `git diff --stat d01d6aa..HEAD`, `git diff --numstat d01d6aa..HEAD -- docs`, `git diff d01d6aa..HEAD -- docs`: six files; documentation diff saved in docs.diff excluding the large new JSON (inspected through JSON parsing); test diff in tests.diff. No deleted historical lines.
- Read `src/tars/sim/forces.py`, `tests/test_zonal_j2.py`, correction 2/3 in `docs/science/validation.md`, Review 02 provenance section and raw reproduction script, mutation harness, survivors harness, README, dossier, previous command ledger, CI JSON exports. Used `cat`, `sed`, `nl`, `rg`, `head`, `tail`, `ls` for read-only inspection. A search for AGENTS.md found none. An optional `tests/test_m3*` glob had no matches; no substantive check depended on it.
- `.venv/bin/python -m pytest -q tests/test_constants.py tests/test_zonal_j2.py > review_scratch/pytest.log 2>&1`: 109 passed, 4.76 s.
- `.venv/bin/ruff check . > review_scratch/ruff.log 2>&1`: All checks passed.
- `.venv/bin/ruff format --check . > review_scratch/format.log 2>&1`: 238 files already formatted. Run before own scratch Python files were added.
- `.venv/bin/python review_scratch/verify.py > review_scratch/verify.log 2>&1`: exit 0. Script retains exact commands for git comparisons, prefix checks, canonical Fraction instrumentation, exact rational proofs, archived b1566ae alias reproduction, two independent mutated source copies, and historical test extraction. Target and alternative: each 1 failed/108 passed; target against historical tests: 107 passed. Logs: target.log, alternative.log, historical.log. Also compares all 46 historical failure sets and summarizes CI exports.
- `TMPDIR="$PWD/review_scratch" .venv/bin/python docs/science/experiments/m3-t1/t1_mutation_check.py review_scratch/mutations.json > review_scratch/mutations.log 2>&1`: fresh complete campaign; summary in mutations.log and final_checks.log.
- `TMPDIR="$PWD/review_scratch" .venv/bin/python docs/science/experiments/m3-t1/t1_review02_survivors.py review_scratch/survivors.json > review_scratch/survivors.log 2>&1`: both documented survivors survive; near_min_normal_zero killed.
- `.venv/bin/python -m pytest --collect-only -q tests/test_constants.py tests/test_zonal_j2.py > review_scratch/collection.log 2>&1`: 109; parsed split 97/12.
- `.venv/bin/python -m pytest --collect-only -q > review_scratch/full-collection.log 2>&1`: 1290 tests collected, 25.06 s. This is collection, not a full-suite pass.
- `.venv/bin/python review_scratch/reproduce_outputs.py > review_scratch/outputs.log 2>&1`: archives src from 97b69ef and b1566ae, then runs the two correction scripts and informational script, compares committed output bytes; also compares survivor output. Exact child commands are in the script. Initial attempt incorrectly resolved the venv interpreter symlink to the underlying interpreter and failed importing NumPy; corrected scratch launcher to preserve `.venv/bin/python`, reran. No product failure inferred.
- `.venv/bin/python review_scratch/final_checks.py > review_scratch/final_checks.log`: collection split, fresh/committed mutant failure-set equality, survivor summary, final tracked cleanliness.
- `git diff --check`, `git status --porcelain --untracked-files=no`: empty.

No Proof wrapper, full pytest execution, T0 execution, network request, acceptance action, or merge was performed.
