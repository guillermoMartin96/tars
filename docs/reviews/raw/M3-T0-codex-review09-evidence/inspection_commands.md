# Review 09 command ledger supplement

All paths are relative to the supplied snapshot unless absolute. `commands.jsonl` records the substantive Python command invocations, exit codes, durations and output logs. Each reviewer script is retained; its subprocess calls and iteration lists are part of this ledger. `reproduce.py` records the exact nine experiment commands, twice, including the absolute GMAT launcher. `red_before.py`, `old_mutants.py`, and `new_mutants.py` retain the exact temporary-copy and pytest commands.

Direct invocations not launched by `run.py`:

- `mkdir -p review_scratch`
- `git rev-parse HEAD`
- `git status --porcelain` (initially, during reproduction, and finally)
- `git diff --name-only 115e747..HEAD`
- `git diff --stat 86df2c3..HEAD`
- `git diff 115e747..HEAD > review_scratch/correction.diff`
- `git diff 86df2c3..HEAD > review_scratch/full.diff`
- `.venv/bin/python -m pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6,7,8}.py > review_scratch/checks.log 2>&1`
- `.venv/bin/python -m pytest -q -p no:cacheprovider > review_scratch/pytest.log 2>&1`
- `git remote -v`
- `git branch -a --contains HEAD`
- `git show 115e747:docs/science/experiments/m3-t0/t0_termination.py > review_scratch/termination_before.py`
- `git diff 115e747..HEAD -- docs/science/experiments/m3-t0/t0_termination.py`
- `shasum -a 256 '../GMAT R2026a/bin/GmatConsole'`
- `find '../GMAT R2026a' -name '*ExponentialAtmosphere*'`
- `shasum -a 256 '../GMAT R2026a/data/atmosphere/earth/EarthExponentialAtmosphereData.txt' > review_scratch/gmat_table_sha.txt`
- `ls -l '../GMAT R2026a/bin'`
- `head -45 '../GMAT R2026a/bin/gmat_startup_file.txt'`
- `.venv/bin/python review_scratch/read_records.py`
- `sysctl -n machdep.cpu.brand_string > review_scratch/cpu.log 2>&1` (sandbox denied)
- `uname -a > review_scratch/uname.log`
- `ps -eo pid,etime,pcpu,args | rg 'python|GmatConsole' | tail -22` (sandbox denied)
- `git status --porcelain > review_scratch/status_after_repro.txt`
- `git diff --stat > review_scratch/diff_after_repro.txt`

Read-only inspection commands used `cat`, `sed -n`, `head`, `tail`, `rg -n`, `rg --files`, `nl -ba`, and `ls -lt`. Targets: `pyproject.toml`; `toolbox/validators/` and the argument parsers of `m1_proof.py`, `m2_proof.py`, `gmat_m1.py`, `gmat_m2.py`; the full correction diff; `t0_model.py` (constants, height, forces, RK4); `t0_oracle.py`; `t0_termination.py` (lines 440–1460 and function index); all eight `check_review` function indexes (`check_index.txt`), `check_review07.py` lines 1–270, `check_review08.py` lines 1–304; `mutation_check_review02.py` (mutant definitions and runner); experiment README; DR-0029; VAL-0019; T0 report and decision matrix; Review 06/07 amendments; Review 08 raw review and record; Review 01 prompt including I-15; implementer `digests.py.txt`, `ast_equal.py.txt`, `smoke_r8.py.txt`, `adversarial_r8.py.txt`; and reviewer logs while processes ran. `read_records.py` retains the complete 35-record read inventory and selected-line extraction. `integrity.py` retains all git inspection commands and result JSON inventory.

The local canvas skill was read with `cat <home>/.agents/skills/canvas/SKILL.md`; its specific-deliverable exception applies to the requested Markdown review, so no canvas was created.

Reviewer file creation used shell heredocs under `review_scratch/`. Two scratch-only `sed -i ''` corrections changed `Path.resolve()` to `Path.absolute()` in `reproduce.py`; another changed the adversarial velocity multiplier from `nextafter(1,0)` to `1-1e-12` after a rounded energy check reached zero. A scratch-only Python edit expanded the C2 grid to include exact cd·area products above binary64 MAX. No tracked source was edited.

The one-line finite-M3 probe imported `t0_termination`, injected `1e8` on the first envelope call and `0` thereafter at h0=200000 and B_V1, and printed the stage bounds and both minima into `finite_m3.log`. The same exact probe is retained in `new_mutants.py`.

Tool session polling used `write_stdin` with empty input; clock reads and output/status inspections did not change files. Final report creation and final status verification are recorded in `finalize.log` and the report itself. No prohibited Proof wrapper, network operation, checkout restoration, commit, or production edit was executed.

Additional final inspections: `rg --files -g AGENTS.md -g RULE.md . .. | head -30` found none; `git rev-parse origin/milestone-3-t0-reference-spike` equals the pinned HEAD; JSON inspection counted seven M1 validator results and 228 M2 validator results; `rg -c '^\[PASS\]' review_scratch/m2.log` returns 228. `wc -w review_scratch/review_draft.md` was used to check report size. Line references were verified with `nl -ba` on `check_review08.py` and `t0_oracle.py`. A scratch-only `pole_audit.py` computes both exact ellipsoid interpretations at 90 decimal digits. No action was performed in external services.

`.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider > review_scratch/pytest_collection.log 2>&1` collected 1185 tests and identified the slow integrated-mission checks while the full suite continued. Finalization uses `.venv/bin/python review_scratch/finalize.py`, which requires the full suite to pass, records clean git status/diff-stat, replaces the draft's pytest result, writes the exact final review and hashes reviewer files. The final report text is then returned verbatim.
