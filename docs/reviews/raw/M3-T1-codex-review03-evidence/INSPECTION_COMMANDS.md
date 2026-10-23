# Read-only inspection and review-script ledger

All commands ran from the pinned clone root. No network commands or Proof wrappers were run. Commands that write files wrote only under `review_scratch/`, except pytest/ruff's ignored caches. Here-doc bodies are retained in their named `.py` files. `run_checks.py` records its exact subprocess argv, exits and durations in COMMANDS.md. Each own-mutant directory retains its exact diff, pytest output and JUnit XML.

Initial snapshot and discovery:
- `pwd`; `git status --porcelain`; `git rev-parse HEAD`: pinned 4b85ded298e521f5c72b606cd012dec8b56e9c5e, clean.
- `rg --files -g AGENTS.md -g '*t1*' toolbox/validators docs/science/experiments/m3-t1`: T1 experiment inventory, no AGENTS.md returned.
- `rg --files -g AGENTS.md -g '*validator*' -g '*golden*' -g '*determin*'`; `ls toolbox/validators`; `ls -a`: no AGENTS.md; validator and historical evidence inventory.
- `sed -n '1,300p' src/tars/sim/forces.py`; `cat src/tars/sim/constants.py`; `cat tests/test_constants.py`: reviewed production definitions and constant-identity assertions.
- `cat pyproject.toml`; `cat CLAUDE.md` (first 180 lines via sed): Python/dependency/test/lint configuration and project context. User's review-only instructions govern.
- `sysctl -n machdep.cpu.brand_string`: denied by sandbox. `uname -a`: Darwin 25.2.0 RELEASE_X86_64. `date -u`: progress timestamps. `ps -o pid,etime,pcpu,command -ax | rg '(pytest|run_checks|m2_proof|interval_dyadic)' | head -n 12`: ps denied by sandbox; no process inference made.

Source, authorization and records inspection:
- `sed -n '550,1050p' tests/test_zonal_j2.py`; `sed -n '1,340p' tests/test_zonal_j2.py`; `sed -n '330,530p' tests/test_zonal_j2.py`; `sed -n '275,335p' tests/test_zonal_j2.py`; `nl -ba tests/test_zonal_j2.py | sed -n '435,468p'`: inspected all test/oracle sections and new numerical/type cases.
- `cat docs/science/experiments/m3-t1/t1_review02_correction_check.py`; `sed -n '1,260p' docs/science/experiments/m3-t1/t1_mutation_check.py`; `sed -n '260,520p' docs/science/experiments/m3-t1/t1_mutation_check.py`; `sed -n '1,180p' docs/science/experiments/m3-t1/t1_review02_survivors.py`; `cat docs/science/experiments/m3-t1/README.md`: reviewed scripts, anchors, classifier and evidence descriptions.
- `cat toolbox/validators/README.md`; `cat toolbox/scripts/run_m1_proof.sh`; `cat toolbox/scripts/run_m2_proof.sh`: inspected only, did not execute wrappers.
- `cat toolbox/validators/cross_platform.py`; `cat toolbox/validators/determinism.py`; `cat toolbox/validators/m1_proof.py`; `cat toolbox/validators/m2_proof.py`: inspected CLI/default output behavior before running with scratch outputs.
- `cat docs/reviews/raw/M3-T1-codex-review01-prompt.md > review_scratch/authorization01.txt`; `cat docs/reviews/raw/M3-T1-codex-review02-prompt.md > review_scratch/authorization02.txt`: saved I-17/I-18 and I-19 text. Read relevant portions with `sed -n '430,465p'`, `sed -n '116,212p'` (authorization01), `sed -n '98,185p'` (authorization02), and heading/search queries below.
- `cat docs/reviews/M3-T1-review-02.md`; `sed -n '149,190p' docs/reviews/M3-T1-review-01.md`; `cat docs/milestones/M3-T1-report.md`; `cat docs/decisions/requests/DR-0025*`: read findings, appended corrections and owner dispositions.
- `sed -n '995,1155p' docs/science/validation.md`; `sed -n '1150,1220p' docs/science/validation.md`; `nl -ba docs/science/validation.md | sed -n '1160,1208p'`; `nl -ba src/tars/sim/forces.py | sed -n '15,48p'`: original VAL-0020 and both corrections; exact note locations.
- `rg -n 'VAL-0020|Correction 2|correction 2|dual|libm|2⁻|2\^-|1.6e|surviv' docs/science/validation.md`; `rg -n '^##|severity|MINOR|NOTE|erratum|∇' review_scratch/authorization01.txt review_scratch/authorization02.txt docs/milestones/*T1* docs/reviews/M3-T1-review-01.md`: mapped authority, errata and conditional guarantees.
- `rg -n 'R6|normal|domain|silent|finite' docs/decisions/requests/DR-0024*`; `rg -n 'ZonalJ2Gravity|WGS84_EGM2008|EarthJ2Constants' src`: domain requirement and no production consumers.
- `find docs/reviews/raw/M3-T1-codex-review02-evidence -maxdepth 2 -type f`; `sed -n '1,150p' docs/reviews/raw/M3-T1-codex-review02.md`: prior reviewer evidence inventory and conclusions.
- `sed -n '1,260p' docs/reviews/raw/M3-T1-codex-review02-evidence/interval_dyadic.py.txt`; `sed -n '1,180p' docs/reviews/raw/M3-T1-codex-review02-evidence/interval_bound.py.txt`; `sed -n '1,220p' docs/reviews/raw/M3-T1-codex-review02-evidence/path_counts.py.txt`; `cat docs/reviews/raw/M3-T1-codex-review02-evidence/certificate.py.txt`; `cat docs/reviews/raw/M3-T1-codex-review02-evidence/interval_dyadic.log`: examined interval construction, previous certificate and path counts before local execution.
- `ls docs/reviews/raw/M3-T1-review01-reproduction`; `cat docs/reviews/raw/M3-T1-review01-reproduction/reproduce_review01_output.json`; `cat docs/reviews/raw/M3-T1-review02-reproduction/reproduce_review02_output.json`; `cat docs/reviews/raw/M3-T1-codex-review02-evidence/own_mutants/results.json`; `cat docs/reviews/raw/M3-T1-codex-review02-evidence/own_mutants/*/diff.patch`: checked historical reproductions and exact exploratory mutant defects.
- `rg -n -C 5 'mu_alias_set|mu_arr|alias' docs/reviews/raw/M3-T1-review02-reproduction/reproduce_review02.py.txt`: verified mixed-time historical parameter observation.

Git checks:
- `git diff --stat b1566ae..HEAD`; `git log --oneline b1566ae..HEAD`: eight bounded correction/evidence commits.
- `git diff b1566ae..HEAD -- docs > review_scratch/docs.diff`; `git diff 60648b9..HEAD -- src > review_scratch/src.diff`; `git diff 60648b9..HEAD -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation > review_scratch/protected.diff`: captured record/source/protected-path evidence.
- `git diff b1566ae..HEAD -- docs/science/experiments/m3-t1/t1_review01_correction_check.py`: docstring only; AST equality independently checked.
- `git log --format='%h %s' b1566ae..HEAD -- docs`; `git show --stat --oneline 4b85ded`: final head changes only the Review 02 validation record.
- `git diff --numstat 60648b9..HEAD -- src`: +58 constants, +137 forces, no deleted original lines. `git diff --numstat b1566ae..HEAD -- docs`: record sections only appended; scripts/result files appropriately replaced/added.
- Repeated `git status --porcelain`; `git diff --stat`: no tracked changes, no restoration needed.

Independent scratch executions (scripts retained verbatim):
- `.venv/bin/python -m pytest -q -p no:cacheprovider > review_scratch/full_pytest.log 2>&1`: full suite, background session.
- `.venv/bin/python review_scratch/run_checks.py > review_scratch/checks_progress.log 2>&1`: exact constituent commands/results in COMMANDS.md; includes the two git archives, extraction, T1, five T1 evidence reruns, T0, validators, determinism and ruff.
- `.venv/bin/python review_scratch/adversarial.py > review_scratch/adversarial.log 2>&1`: exact product fuzz, numeric types, independent states, zero/subnormal results, rational-fallback call counter. Also writes adversarial.json.
- `cp docs/reviews/raw/M3-T1-codex-review02-evidence/interval_dyadic.py.txt review_scratch/interval_dyadic.py`; `.venv/bin/python review_scratch/interval_dyadic.py > review_scratch/interval_dyadic.log 2>&1`: 5,904-point rational interval certificate, no uncertified cases.
- `.venv/bin/python review_scratch/own_mutants.py > review_scratch/own_mutants.log 2>&1`: six own mutants and final-tests red-first run against b1566ae. Saved per-mutant diff/pytest/JUnit; five assertion kills, one survivor; red-first 26 failed/81 passed.
- `.venv/bin/python review_scratch/audit_records.py > review_scratch/records_audit.log 2>&1`: CI heads/jobs, record-prefix and AST equality, protected paths, byte comparisons, assertion-message audit, probability calculation. First run stopped on CI timestamp discrepancy; relaxed only the unrequired cross-clock step ordering assertion, retained all head/branch/job/conclusion checks, and separately saved the anomaly. Later reruns incorporate completed evidence outputs. No production file changed.
- `.venv/bin/python review_scratch/factor_cases.py > review_scratch/factor_cases.json`: initial search found no exact factor case in its narrow parameter list; proved upper-half coefficient example rejects.
- `.venv/bin/python review_scratch/exact_factor.py > review_scratch/exact_factor.json`: constructive exact-subnormal factor example accepted; adjacent parameter rejected.
- `.venv/bin/python review_scratch/numerical_search.py > review_scratch/numerical_search.json 2> review_scratch/numerical_search.err`: three trajectories against 97b69ef and 7,000 extreme-parameter trials with exact-rational sqrt brackets/majorants. 3,213 accepted, no counterexample; 3,787 explicit domain rejections.
- `.venv/bin/python review_scratch/supplementary.py > review_scratch/supplementary.json 2> review_scratch/supplementary.err`: reference-source equivalence, extra prefix checks, actual narrow-band hit count, invalid conversions, adjacent domain boundaries.
- `cp docs/reviews/raw/M3-T1-codex-review02-evidence/path_counts.py.txt review_scratch/path_counts.py`; `.venv/bin/python review_scratch/path_counts.py > review_scratch/path_counts.log 2>&1`: operation graph depths below recorded conservative counts; not a general rounding proof.
- `.venv/bin/python review_scratch/ci_consistency.py > review_scratch/ci_consistency.json`: records supplied metadata's step-time anomaly without asserting authenticity.
- `.venv/bin/python review_scratch/historical_probe.py > review_scratch/historical_probe.json`: independently reproduces historical mixed-time parameter field.

Short inline Python inspection commands (their computations are also retained in the named scripts/results):
- Enumerated CI step timestamps violating run/job containment; printed created/start/end times for run 40002897696. Four early macos-15-intel steps precede declared job start, first precedes run creation by 14 seconds. Possible clock skew; unauthenticated.
- Printed each committed mutant's id, failure count, first assertion test/message: all 46 have real functional/contract/identity assertions, not collection-only errors or source-only kills.
- Printed/checked exact factor-product construction before saving exact_factor.py.
- Edited only scratch audit_records.py to distinguish job endpoint consistency from step clock anomaly; no tracked writes.

Progress/readback commands:
- Repeated `cat review_scratch/checks_progress.log`, `tail -c 180/220/240/250/300/400 review_scratch/full_pytest.log`, `tail -n 2/3/4/5/9 review_scratch/check_*.log`, `ls -lh review_scratch/check_*.log`, and `tail -n 5 review_scratch/COMMANDS.md`: monitor completion without rerunning tests.
- `cat` of environment.json, adversarial.json, exact_factor.json, factor_cases.json, records_audit.log, ci_consistency.json, historical_probe.json, own_mutants.log, interval_dyadic.log, path_counts.log, check_11.log, check_12.log and check_13.log; `head`/`tail` readbacks of informational.json, numerical_search.json and supplementary.json; `tail -n 4 review_scratch/own_mutants/redfirst.log`: all outcomes summarized in the review.
- `ls review_scratch/ci`; `cat review_scratch/ci/run-40008016629.json`: final-head metadata inspected directly; all five exports inspected programmatically.

Final supplemental bookkeeping:
- `python -m pytest --collect-only -q -p no:cacheprovider > review_scratch/collected_tests.log 2>&1`: 1,288 tests collected; inspected lines 615–640 to locate the long-running M2 validation tests. This did not rerun tests.
- Byte-prefix checks using `Path.read_bytes().startswith(git show b1566ae:PATH)` for eight record files: all true (`byte_prefixes.json`).
- Final record-audit rerun after all batch outputs existed: all checks passed; mutation output normalized only for memory addresses.
- Parsed m1.json/m2.json/local platform/survivors/mutation outputs, printed result counts and Ruff outcomes; wrote scratch result inventory with SHA256 digests.
- Wrote report_draft.md with full-suite result explicitly pending; final report is generated only after that execution completes.
- Harvested completed tool sessions for run_checks, interval certificate, own mutations and numerical search: each exit 0. Full-suite session remains running until its final result is recorded.
