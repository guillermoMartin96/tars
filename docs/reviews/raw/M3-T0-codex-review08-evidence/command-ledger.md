# Review 08 command ledger

All commands ran from the review checkout, without network. P means `.venv/bin/python`, D means `docs/science/experiments/m3-t0`, S means `review_scratch`, E means `docs/reviews/raw/M3-T0-review07-findings-correction-evidence`. File-creation heredocs and scratch-only Python text replacements created the scripts listed below; no tracked source was edited. Tool-call output is also part of the session transcript. Repeated progress reads (`cat`, `tail`, `head`, `sed`, `rg`) only inspect the named outputs.

## Git, inventory and environment

- `pwd`; `git rev-parse HEAD`; `git status --porcelain`; `rg --files -g AGENTS.md -g '*review07*' -g '*termination*' -g '*README*' D docs/reviews | head -60`.
- `mkdir -p S`; `git diff 72f9e00..HEAD > S/correction.diff`; `git diff 86df2c3..HEAD --stat > S/full-stat.txt`; `git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml > S/protected.diff`.
- `git diff --name-status 72f9e00..HEAD`; `git diff 72f9e00..HEAD -- D/t0_termination.py`; `git diff --numstat 72f9e00..HEAD | tail -10`.
- `uname -a`; P inline import/sys/numpy/scipy/platform version query.
- `git diff 86df2c3..HEAD > S/full.diff`; `git diff 72f9e00..HEAD -- 'D/*results.json' > S/results.diff`; `git diff 72f9e00..HEAD -- docs/reviews/M3-T0-review-06.md docs/reviews/M3-T0-review-07.md > S/review-records.diff` (D expanded in actual commands).
- P inline version metadata and `numpy.show_config()` -> S/python-environment.log. The optional YAML formatting dependency is absent; no installation attempted.
- Environment driver commands: `uname -a; sw_vers; sysctl -n machdep.cpu.brand_string; git branch -avv; git remote -v; git log -4 --oneline`. CPU sysctl denied; other commands succeeded.
- `git status --porcelain > S/interim-status.txt`; `git diff --stat > S/interim-stat.txt`; final counterparts recorded after all execution.

## Read-only source and record inspections

`cat`/`sed`/`nl -ba` read:
- D/t0_termination.py (whole file, then focused E1–E6, envelope, helper and stage ranges), D/t0_model.py (constants, density, inverse geodetic and force interfaces), D/t0_oracle.py, D/check_review07.py, D/mutation_check_review02.py, D/README.md.
- D/check_review01.py threshold/stage/wording checks and D/check_review06.py cap/switch/provenance checks; `rg -n 'def test_'` inventoried all six earlier checks.
- docs/reviews/raw/M3-T0-codex-review01.md through review07.md (whole/focused reads); all prompt authorization headings indexed in S/authorization-index.txt; Review 01 prompt's I-15 technical/validation/completed independent-review authorization read explicitly.
- docs/reviews/M3-T0-review-06.md amendment and docs/reviews/M3-T0-review-07.md correction/validation, README, DR-0029, VAL-0019, milestone report/matrix relevant corrections and scope/assumption/overflow clauses via `rg` and correction diff.
- `cat docs/decisions/requests/DR-002{4,5,6,7,8}*.md > S/decision-registers.txt`; `rg` scope/physics/decision text in assumption and decision registers.
- E/digests.py.txt, ast_equal.py.txt, adversarial_r7.py.txt, smoke_r7.py.txt, SHA256SUMS, mutation_check_review07.json.
- Review 07 reviewer extra_boundaries.py.txt and test_noncert_contract.py.txt.
- toolbox/validators/README.md; `ls toolbox/validators`; CLI argument definitions via `rg -n 'ArgumentParser|add_argument'` in validators and GMAT scripts; pyproject.toml.
- <home>/.agents/skills/canvas/SKILL.md: specific requested Markdown deliverable falls under its explicit specific-deliverable exception; no canvas created.

Search outputs retained: S/prior-findings.txt, authorization-index.txt, consumer-index.txt. Repeated progress reads inspected all experiment/check/validator/probe logs named below. Missing optional metadata `cat .../traj_j2_drag_geod_metadata.json` returned no evidence; standard GMAT reproduction remained successful.

## Executions

1. `P -m pytest -q -p no:cacheprovider D/check_review0{1,2,3,4,5,6,7}.py > S/t0-checks.log 2>&1`: 261 passed.
2. `P -m pytest -q -p no:cacheprovider > S/pytest.log 2>&1`: full project suite, final result in that log.
3. `P toolbox/validators/m1_proof.py --out S/m1.json > S/m1.log 2>&1`: PASS, seven results.
4. `P toolbox/validators/m2_proof.py --out S/m2.json > S/m2.log 2>&1`: PASS, 228 results, non-quick.
5. `P S/run_validation.py > S/validation-driver.log 2>&1`. The script retains exact argument vectors and every log starts with COMMAND. It ran environment commands above; `P -I E/digests.py.txt <absolute checkout>`; both `toolbox/scripts/gmat_m{1,2}.py compare`; `P -m ruff check .`; the implementer's 4000-case probe via `P -I E/adversarial_r7.py.txt <absolute D>`; and every experiment twice. For each round: `P <absolute D>/t0_X.py <absolute D>/t0_X_results.json`, X=atmosphere, decay, geodetic, frames, regression, termination, height_error; `P <absolute D>/t0_gmat.py --gmat-console <absolute private install>/bin/GmatConsole --out <absolute D>/t0_gmat_results.json`; `P <absolute D>/t0_axis_ablation.py <absolute D>/t0_axis_ablation_results.json`. Two byte-hash comparisons found zero changes. Final `git status --porcelain; git diff --stat` empty. GMAT and table hashes computed independently with hashlib.
6. `P S/independent.py > S/independent.log 2>&1`: boundary matrix, rational C1/C2, old counterexamples. Initial script stopped at the expected cap-rejection boundary because I had not caught ValueError. `P S/finish_probes.py > S/independent-complete.log 2>&1` catches that expected exception and finishes the independent AST/append-only checks. Exact C1/C2 counts 1850/1225.
7. AST script was initially invoked incorrectly with a directory and then with revision text; both reviewer invocation errors are retained in S/ast.log and ast-retry.log. Correct command: `git show 72f9e00:D/t0_termination.py > S/old_termination.py`; `P -I E/ast_equal.py.txt S/old_termination.py D/t0_termination.py > S/ast-correct.log 2>&1`: identical AST. Own independent AST comparison also passed.
8. `P S/force_probes.py > S/force-probes.log 2>&1`: initial extreme force probe stopped on NaN from an overflowing model evaluation. Scratch script changed to count/exclude nonfinite model evaluations under the disclosed no-overflow scope. Rerun -> S/force-probes-complete.log: 159 finite force states covered, 291 nonfinite extremes excluded, 72 certified adversarial actual RK4 steps covered; strict-exterior lower-edge exception reproduced.
9. `P S/mutations.py > S/mutations.log 2>&1`: copies docs under S/mutants, runs each of 14 supplied R7 and four own mutants plus unmodified control against check_review07.py. Control 23 passed; 17 mutations failed; own_M3_ignored survived that focused set. Exact subprocess arguments and file edits in source; individual output logs and mutation-results.json retained.
10. `P S/extra_contract.py > S/extra-contract.log 2>&1`: independent pulsed enclosure makes original need +inf, M3-ignored expression negative. Both signs of zero, positive and infinite need rejected by floor/libm consumers. Script then extended with optional module path; `P S/extra_contract.py S/mutants/own_M3_ignored/docs/science/experiments/m3-t0 > S/own-M3-independent-detection.log 2>&1`: expected assertion failure detects surviving mutant's false certification. Original control rerun passes.
11. `P S/record_integrity.py > S/record-integrity.log 2>&1`: 20 evidence-manifest entries match; Review 06/07 old records exact prefixes; 97 tracked experiment files; parses all nine result JSONs; results diff empty.
12. `P S/red_before.py > S/red-driver.log 2>&1`: git archive 72f9e00 docs into S/before72, copies only new check_review07.py, runs 23 checks: 3 failed, 20 passed. Full log S/red-before.log.
13. `P -m pytest -q -p no:cacheprovider S/test_lower_edge_contract.py > S/lower-edge-contract.log 2>&1`: two expected failures reproduce current documentation claim for an exterior bound state with B_V1 and drag-free vehicle.
14. `P S/summary.py > S/result-summary.log 2>&1`: parsed M1/M2 reports, all termination thresholds/floors/brackets/margins/libm sensitivities/stage order, GMAT, height-error and axis-ablation results; enumerated full and correction paths, all docs-only.
15. `P S/check_e4b.py > S/e4b.log 2>&1`: 66 exact-product-boundary states have zero force; independent rational cap limit exactly 91910196476947.
16. `cp docs/reviews/raw/M3-T0-codex-review07-evidence/test_noncert_contract.py.txt S/test_noncert_contract.py`; `P -m pytest -q -p no:cacheprovider S/test_noncert_contract.py > S/old-reviewer-contract.log 2>&1`: one expected failure, old universal-infinity claim remains false. `P -I docs/reviews/raw/M3-T0-codex-review07-evidence/extra_boundaries.py.txt > S/review07-extra-boundaries.log 2>&1`: passes.
17. `P S/earlier_mutants.py > S/earlier-mutants.log 2>&1`: five historical mutants against declared checks across seven modules using -k. R2-F3 zero evidence: 22 failures; R4 absolute part: eight; R5 conversion: seven; R6 zero b: 22; R6 helper overflow: five. All detected without collection errors. Individual exact commands/logs and earlier-mutation-results.json retained.
18. Inline P parsed supplied/own mutation JSON and validator JSON: supplied counts 73 detected, two equivalent, one passing control; own focused control/survivor two zero exits, 17 detected; M1/M2 reports passed.

Clock queries/session polling only observed/waited for the above runs. No prohibited Proof wrapper was run. No tracked file needed restoration because all outputs remained byte-identical. No network, commit, push, merge, owner decision or subsequent review was performed.

Additional read-only progress diagnosis: `P -m pytest --collect-only -q > S/collected-tests.log 2>&1`; inline Python counted completed progress dots and mapped them to the collected cases. Exactly 1185 cases were collected; around case 897 the run was in `tests/test_reference_snapshot.py`, followed by historical attribution tests. This did not execute or alter any test. Final report and ledger were written/updated only under S; the finding's termination references were corrected to current lines 1312–1324 and 1340.

Completed full project suite: 1185 passed, three expected overflow-test warnings, 1676.36 seconds. Final `git status --porcelain` and `git diff --stat` were saved to final_status.txt/final_diff_stat.txt, both empty. No restoration required.
