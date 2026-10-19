# Review 03 command ledger

All commands ran from the snapshot root unless a retained Python driver specifies a child working directory. `S` below abbreviates `review_scratch`, `D` abbreviates `docs/science/experiments/m3-t0`; these abbreviations are only presentation shorthand. Shell redirections place logs under S. Every reviewer-created source is retained in S. Here-document creation and the two scratch-source repair commands are recorded below; no tracked source was edited.

## Preflight and diff commands

- `mkdir -p review_scratch`; `git rev-parse HEAD`; `git status --porcelain`; `git diff --stat 5548d11..51e110b`; `git diff --name-only 86df2c3..51e110b`; `rg --files -g AGENTS.md -g '*review02*' -g '*termination*' -g '*axis_ablation*'`: correct pinned HEAD, clean tree, docs-only changes; no AGENTS.md found.
- `git diff 5548d11..51e110b > S/correction.diff`; `git diff 86df2c3..51e110b > S/full.diff`: retained full diffs.
- `git branch -a --contains HEAD`; `git log -3 --format='%h %s'`: detached checkpoint belongs to the requested branch; correction and validation commits match.
- `git diff 86df2c3..51e110b -- docs/decisions/requests/DR-0024* docs/decisions/requests/DR-0025* docs/decisions/requests/DR-0027* docs/decisions/requests/DR-0028*`: append-only notes, no accepted decisions changed.

## Executions

- Created `S/run_experiments.py` with a shell here-document; ran `.venv/bin/python S/run_experiments.py > S/experiments.log 2>&1`. Exact child command arrays and exit codes are in `S/experiments_ledger.json`. This runs `t0_{atmosphere,decay,geodetic,frames,regression,termination,axis_ablation}.py` with corresponding S JSON outputs and then `t0_gmat.py`. Seven Python outputs match committed bytes. The first GMAT attempt mistakenly resolved the console symlink; its inferred install root was wrong and it failed before running GMAT.
- `.venv/bin/python D/t0_gmat.py --gmat-console "$PWD/../GMAT R2026a/bin/GmatConsole" --out "$PWD/S/t0_gmat_results.json" > S/gmat_retry.log 2>&1`: retry succeeds; JSON and all rewritten tracked GMAT artifacts match committed bytes.
- `.venv/bin/python -m pytest -q -p no:cacheprovider D/check_review01.py D/check_review02.py > S/checks.log 2>&1`: 50 pass.
- `.venv/bin/python D/mutation_check_review02.py S/mutations.json > S/mutations.log 2>&1`: runs 17 copied-docs suites (control plus 16 mutants); output retained.
- `.venv/bin/python -m pytest -q -p no:cacheprovider > S/pytest.log 2>&1`: complete ordinary project suite; output retained.
- `.venv/bin/python toolbox/validators/m1_proof.py --out S/m1.json > S/m1.log 2>&1`: PASS.
- `.venv/bin/python toolbox/validators/m2_proof.py --out S/m2.json > S/m2.log 2>&1`: PASS, without --quick.
- `.venv/bin/python toolbox/scripts/gmat_m1.py compare > S/m1compare.json 2>&1`; `.venv/bin/python toolbox/scripts/gmat_m2.py compare > S/m2compare.json 2>&1`: all comparisons pass. The latter emits three JSON objects rather than one.
- Created `S/independent.py` with a here-document and ran `.venv/bin/python S/independent.py > S/independent.log 2>&1` twice. First attempt failed on repeated GMAT headers. A `python3` here-document replaced its `np.loadtxt(..., skiprows=1)` with explicit non-header parsing, then reran it. It checks five pinned digests, GMAT console/table digests, density jumps, a first equatorial floating-boundary search, cubic identity, rounded floors, and an independent QR axis fit. The initial equatorial search found no violation.
- Created `S/float_boundary.py` with a here-document; ran `.venv/bin/python S/float_boundary.py > S/float_boundary.log 2>&1`: near-equatorial search finds envelope violations at seven downward jumps.
- Created `S/counterexample.py` with a here-document; ran `.venv/bin/python S/counterexample.py > S/counterexample.log 2>&1`: verifies one exact float input at 80 decimal digits, including true height, speed and negative energy; confirms the envelope violation and the test's widened envelope.
- Created `S/test_boundary_guarantee.py` with a here-document; ran `.venv/bin/python -m pytest -q -p no:cacheprovider S/test_boundary_guarantee.py > S/boundary_test.log 2>&1`: one deliberately asserted guarantee fails, reproducing R3-F1.
- Created `S/audit.py` with a here-document; ran `.venv/bin/python S/audit.py > S/audit.log`: reads every T0 results JSON, extracts quoted quantities, verifies all 13 VAL-0019 script/table hashes, and verifies preservation of four prior raw review/prompt files.
- Created `S/math_audit.py` with a here-document; ran `.venv/bin/python S/math_audit.py > S/math_audit.log`: analytic normal cosine, independent endpoint calculation over 10,000 domains, endpoint-equivalence condition, old/new floors and unchanged two-body table.
- Created `S/post_audit.py` with a here-document; ran `.venv/bin/python S/post_audit.py > S/post_audit.log` twice. First run confirmed GMAT identity, empty protected diff/status/stat, then failed parsing the three-object M2 comparison output. A `python3` here-document replaced the single JSON parse with `JSONDecoder.raw_decode` iteration. Retry confirms no false comparison flags.
- Created `S/red_before.py` with a here-document; ran `.venv/bin/python S/red_before.py > S/red_before.log 2>&1`. Exact child commands are in the source: `git archive <revision> docs`, `tar -x -C <S copy>`, copy current checks, then `.venv/bin/python -m pytest -q -p no:cacheprovider <copied checks>` at 5548d11 and bdcaacf. Source and individual logs retained.
- `.venv/bin/python -` via a here-document importing sys/platform/numpy/scipy: Python 3.12.15, macOS 26.2 x86_64, NumPy 2.5.3, SciPy 1.18.1.

## Read-only file inspections

Commands used `cat`, `sed -n`, `rg -n`, `nl -ba`, `head`, `tail`, and `ls -l` on the following inputs. These commands only displayed files; they did not execute experiments:

- `cat D/t0_termination.py`; `cat D/README.md D/check_review02.py D/mutation_check_review02.py`; `cat D/t0_axis_ablation.py`; `cat D/t0_axis_ablation_results.json`.
- `cat` of both prior raw reviews, both prior prompts and both review records into `S/prior_records.txt`; `rg -n '^#|F[1-5]|Authorization|bound|sufficient' S/prior_records.txt`.
- `cat DR-0029`; `cat docs/milestones/M3-T0-report.md docs/milestones/M3-T0-decision-matrix.md`; `cat docs/science/assumptions.md`; `cat docs/decisions/requests/DR-002{4,5,6,7,8}*.md > S/decision_registers.txt`.
- `sed -n '/## VAL-0019/,$p' docs/science/validation.md` (also saved to `S/val0019.txt`); `cat S/val0019.txt`.
- `sed -n '1,100p'` and `'100,300p'` on the Review 01 prompt; `sed -n '1,220p' S/correction.diff`.
- `cat` of correction-evidence `pinned_digests.log`, `reproducibility_twice.log`, `mutation_check_review02.json`; `cat .../m1_proof_run.log | tail -15`; `tail -15 .../m2_proof_run.log`; `sed -n '118,150p' docs/reviews/M3-T0-review-02.md`.
- `rg -n 'def density|def geodetic_iterative|band_index' D/t0_model.py`; `sed -n '70,210p' D/t0_model.py`.
- `sed -n '280,355p'`, `'250,280p'` on D/check_review02.py; `rg -n '^def test_' D/check_review02.py`; numbered excerpts `'410,437p'`, `'433,442p'` from the same file.
- Numbered excerpts `'435,470p'` from D/t0_termination.py and `'103,120p'` from DR-0029; `rg -n 'h_f|sup over|Monotonicity' DR-0029`.
- `sed -n '210,235p' D/mutation_check_review02.py`.
- `rg -n 'ArgumentParser|add_argument' toolbox/validators/m1*.py toolbox/validators/m2*.py toolbox/scripts/gmat_m1.py toolbox/scripts/gmat_m2.py`; `rg --files toolbox/validators`; `sed -n '1,55p' toolbox/validators/m2_proof.py`.
- GMAT troubleshooting: `sed -n '55,100p'`, `'865,905p'`, `'80,125p'` on D/t0_gmat.py; `rg -n 'GMAT-R|Contents|install|startup' D/t0_gmat.py`; `ls -la '../GMAT R2026a'` and its `bin`; `cat '../GMAT R2026a/bin/gmat_startup_file.txt' | head -45`. No installation change was needed.
- `rg -n 'test_|sleep|subprocess|timeout' tests/test* | head -50`; `rg 'passed in'` on the two supplied Proof logs (no match); `rg -n 'PASS|FAIL|passed|overall' S/m1compare.json S/m2compare.json`.
- `cat <home>/.agents/skills/canvas/SKILL.md`: specific requested Markdown review deliverable falls under its explicit specific-deliverable exception; no canvas created.

## Progress and integrity inspections

Repeated `tail -3`, `tail -5`, `tail -8`, `tail -10` and `tail -40` inspected S logs for checks, pytest, mutations, red-before, experiments, GMAT initial/retry, M1/M2 validators, and comparisons; `cat` displayed the independent, boundary, audit and post-audit logs. `ls -l S/*.log` inspected timestamps; repeated `ls -l S/mutations.json` initially reported it absent while running. Repeated `git status --porcelain` and `git diff --stat` remained empty, including after the GMAT rerun. No checkout restoration was needed. Tool-session polls only retrieved completion status for these already-recorded commands.

The final review and this ledger were written under S with shell here-documents. A final integrity command rechecked HEAD/status/stat and compiled the verification summaries. No M1/M2 Proof wrapper was run.

Additional final inspections: `rg -n '^def stage_lower|^def sufficient' D/t0_termination.py` located the stage derivation; inline `.venv/bin/python` read M1/M2 report keys and counted 228 passing M2 result entries; `cat S/{atmosphere,decay,frames,geodetic,regression,gmat_retry}.log` inspected all rerun summaries. A `clock__curr_time` tool call read UTC time only. Inline Python updated only the scratch review's pending result text and line reference.

Final navigation also ran `wc -w S/M3-T0-codex-review03.md` (1893 words before final substitutions), `.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider > S/collection.log 2>&1`, and `sed -n '285,335p' S/collection.log` to locate progress in the expensive existing M2 tests. These did not change test selection for the running complete suite. `clock.sleep` waited 50 seconds; subsequent session polls only waited for the existing jobs.

Created `S/polar_floor.py` with a here-document; `.venv/bin/python S/polar_floor.py > S/polar_floor.log` ran 108 explicit exact-floor/next-float/plus-1-micrometre states at equator and both poles, near escape, inward/outward/prograde/retrograde. All stage heights and computed lower-bound margins were positive; minimum stage heights were 25083.55, 13806.14 and 11.74682 m. `cat S/polar_floor.log` inspected the results. Subsequent inline Python added this evidence to the scratch review. Another inline Python read the new mutation JSON, compared each failure set with the committed evidence, and updated the scratch review: control 50 passed, 15 detected, one equivalent, identical failure sets.

Final run: `tail -25 S/pytest.log` verified 1185 passed, 3 warnings in 1747.56 s; the warnings come from intentional overflowing-velocity/norm rejection tests. `git rev-parse HEAD`, `git status --porcelain`, `git diff --stat`, and another `.venv/bin/python S/post_audit.py > S/post_audit.log` confirmed the pinned SHA, byte-identical GMAT output, passing comparisons, empty protected diff and clean tracked tree. Inline Python replaced the scratch review's pending suite result, made its ledger link absolute, and documented the warnings. Progress inspections also used collection excerpts `365,400p`, `575,590p`, `850,865p`, and `880,930p`. The final `cat S/M3-T0-codex-review03.md` supplied the identical final response text. No tracked restoration was needed.
