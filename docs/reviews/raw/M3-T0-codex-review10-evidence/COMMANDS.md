Command ledger — M3 T0 Review 10

All commands ran from the supplied snap directory, using zsh and the supplied .venv. Files created by the reviewer are under review_scratch. No network commands or Proof wrappers ran.

Substantive execution commands (the scripts retain exact nested subprocess argv):

1. `pwd; git rev-parse HEAD; git status --porcelain` — supplied checkpoint, initially clean.
2. `rg --files -g AGENTS.md -g '*review09*' -g '*termination*' -g '*gmat*' -g '*validator*' | head -70` — inventory; no AGENTS.md returned.
3. `mkdir -p review_scratch`.
4. `git diff 5978bfe..HEAD > review_scratch/correction.diff`.
5. `git diff 86df2c3..HEAD --stat > review_scratch/full.stat`.
6. `git diff 86df2c3..HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml > review_scratch/protected.diff` — empty.
7. `.venv/bin/python -m pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4,5,6,7,8,9}.py > review_scratch/t0checks.log 2>&1`.
8. `.venv/bin/python -m pytest -q -p no:cacheprovider > review_scratch/pytest.log 2>&1`.
9. `.venv/bin/python review_scratch/verify.py > review_scratch/integrity.log 2>&1` — OS/library versions, attempted sysctl CPU model (denied), hashes, exact byte and AST comparisons, append-only verification, then M1/M2 validators with --out in scratch and both GMAT compares. Nested commands appear in m1.log, m2.log, compare1.log, compare2.log, cpu.log, raw09.diff, results.diff.
10. `.venv/bin/python review_scratch/reproduce.py > review_scratch/reproduce.log 2>&1` — all nine experiments twice, with absolute GMAT console; nested argv in repro{1,2}_{experiment}.log; hashes of all 99 tracked files compared in repro{1,2}_changes.json.
11. `.venv/bin/python review_scratch/mutations.py > review_scratch/mutations.log 2>&1` — 13 R9 mutations, control, two declared equivalents; copied docs and all nine checks on each.
12. `.venv/bin/python review_scratch/probes.py > review_scratch/probes.log 2>&1` — independent exact E4a, E4b, pole, drag, cap and injected-stage probes.
13. `.venv/bin/python review_scratch/stages.py > review_scratch/stages.log 2>&1` — initially failed because the reviewer skipped the first element of the stage recorder. Read rk4_step, preserved failure in stages-initial-index-error.log, changed scratch script from stages[1:] to stages, reran same command successfully. No implementation defect inferred from the mistaken indexing.
14. `.venv/bin/python review_scratch/new_mutations.py > review_scratch/new_mutations.log 2>&1` — three own mutants, complete nine-file checks on each.
15. `.venv/bin/python review_scratch/red_before.py > review_scratch/red_before.log 2>&1` — git archive of 5978bfe docs into scratch; overlay current check09; run its 26 checks.
16. `.venv/bin/python review_scratch/evidence_audit.py > review_scratch/evidence_audit.log 2>&1` — SHA256SUMS, recorded counts/logs, result-file sections, register status.
17. `git diff 86df2c3..HEAD > review_scratch/full.diff` — full diff, 148222 lines.
18. `git diff 5978bfe..HEAD -- docs/reviews > review_scratch/review-records.diff`.
19. `git merge-base --is-ancestor 86df2c3 HEAD` — exit 0.
20. `git diff --name-only 5978bfe..HEAD > review_scratch/changed-files.txt` — 34 docs paths.
21. `.venv/bin/python review_scratch/published_m3.py > review_scratch/published_m3.log 2>&1` — copy experiment directory, remove M3 from minimum, regenerate full termination output into scratch, compare bytes.
22. `.venv/bin/python review_scratch/history_read.py > review_scratch/history_read.log` — all 27 review/prompt/disposition documents, extracted findings, authorizations and amendments.
23. `.venv/bin/python toolbox/validators/cross_platform.py > review_scratch/cross_platform.log 2>&1` — no --write; PASS.
24. `.venv/bin/python toolbox/validators/determinism.py > review_scratch/determinism.log 2>&1` — PASS.
25. Copied r9f2_probe_reclassify.py.txt to review_scratch/reclassify.py; `.venv/bin/python review_scratch/reclassify.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/reclassify.log 2>&1`.
26. Copied m4_binding.py.txt to review_scratch/m4_binding.py; `.venv/bin/python review_scratch/m4_binding.py > review_scratch/m4_binding.log 2>&1`.
27. `.venv/bin/python review_scratch/earlier_mutations.py > review_scratch/earlier_mutations.log 2>&1` — nine earlier mutants, each against every declared detector; no unrelated tests.
28. `uname -a; sw_vers` — Darwin 25.2.0, macOS 26.2 build 25C56, x86_64. `ps -Ao pid,etime,comm | tail -12` was denied.
29. Python inline inspections: listed h.MUTANTS; inspected JSON result keys and recursively counted ValidationResult entries (M1 7/7, M2 228/228); compared docstring-free ASTs; queried published_m3 output equality. Scripts written using shell here-documents; scratch stages script corrected using Python string replacement, with original failed log preserved.
30. Finalization: git status --porcelain and git diff --stat written to final_status.txt and final_diff_stat.txt; result/diff manifests and report written under scratch only.

Read/search operations (no mutations):

- `cat` check_review09.py and the experiment README.
- `sed` t0_termination.py ranges 1–300, 380–850, 850–1200, 1280–1470, 1230–1282: all stage code, force enclosure, exact helpers, mathematical derivation, floor and sensitivity consumers.
- `sed` t0_model.py ranges 130–180, 245–305, 312–358: constants, ellipsoid/height, J2, drag, actual RK4 stage recorder.
- `sed` check_review02.py ranges 1–130, 130–205; `cat` t0_oracle.py first 90 lines: independent bound method and exact ellipsoid definition.
- `sed` mutation_check_review02.py first 120 lines and 880–925; `tail -110`: mutant transformations, outcome classification and all-check runner.
- `cat` toolbox/validators/README.md and approved_digests.py; `head` cross_platform.py, `sed` determinism.py 28–65; `rg -n 'argparse|add_argument'` validators and gmat_m1/m2 scripts: permitted interfaces and write behavior.
- `sed` validation.md 851–888, raw Review01 prompt 1–160 and 120–150, acceptance dossier 1–150, raw Review09 30–120; `tail -80` Review09 record.
- `cat` m4_binding.py.txt and r9f2_probe_reclassify.py.txt before executing scratch copies; `head -35` Review09 probe.py.txt.
- `rg --files` inventories of review09 evidence and probe scripts; `rg -n` headings across raw reviews 01–09 and findings/history extraction using history_read.py.
- `rg -n 'sha256|SHA256'` validation.md; `rg -n` geodetic/acceleration definitions in model; `rg -n 'C1|C2|A-FP|overflow|negative|UNREPRODUCED|5287|5 287'` report and DR0029; `rg -n 'stage_lower_heights|stage_need\('` every experiment Python consumer; `rg -n` R9 mutant names; `rg -n` flattening/polar-reference expressions across experiment Python; `rg -n` Python/library/pytest settings in pyproject.toml. All searches inspected in tool output.
- `head -90` correction.diff; `git diff 86df2c3..HEAD --numstat | tail -5`; `wc -l` full.diff; `head -35` changed-files.txt.
- `head`, `tail`, `cat`, `rg` progress/result reads of t0checks.log, pytest.log, integrity.log, probes.log, stages.log, mutations.log, new_mutations.log, earlier_mutations.log, red_before.log, reproduce.log, repro1_gmat.log, published_m3.log, history_read.log, evidence_audit.log, reclassify.log, m4_binding.log, cross_platform.log, determinism.log and compare1/2.log; repeated during running work. These reads never modified inputs.
- UTC clock tool used for progress timestamp; no waiting beyond short tool yields.

Result files inspected: all nine t0_*_results.json (atmosphere, decay, geodetic, frames, regression, termination, height_error, gmat, axis_ablation), all tracked experiment files by byte hashes, scratch M1/M2 JSON reports, implementer mutation_check_review09.json and smoke_r9.json/log, own mutation JSONs, and reproducibility change JSONs. Full numerical artifacts are regenerated rather than accepted from stored values.

Additional scratch-only commands: environment.txt was generated with platform.uname, sys.version, importlib.metadata.distributions and numpy.show_config (pyyaml display warning only); corrected_m3_mutant.py reran the numerically corrected Decimal M3 mutant; m2_binding.py separately exercised a strict M2 minimum using signed synthetic injections, explicitly outside the force-bound contract.

Progress diagnostics: `pytest --collect-only -q -p no:cacheprovider` wrote collection.log (1185 tests); Python counted progress dots and read surrounding collected node IDs; rg inspected test_poisoned_node_oracle_fails_the_integrated_mission and prior pytest log runtime lines (26:57 and 28:31). No test was canceled or skipped. final_integrity.py independently checked docs-only scope, both numerical baselines and clean status. new_mutations.json was amended from its preserved initial version to record the corrected Decimal mutant detection instead of the invalid type-error run.

`.venv/bin/python review_scratch/surface.py > review_scratch/surface.log 2>&1`: own 6000-point near-surface height/classification and certification search, 5384 exterior, no false certification. Final JSON summaries count 13 R9 detections, 9 earlier detections and 3 own detections, plus the control and two equivalents.

`.venv/bin/python review_scratch/independent_stage_math.py > review_scratch/independent_stage_math.log 2>&1`: 110-digit independent E1/E6 calculation, all nine outward-rounded bounds match at three injected-envelope cases.

Additional inspections: loaded smoke_r9.json (all 13 R9 entries) with Python; computed remaining B64/curvature expressions against exact E2 geometry into ellipsoid_remaining.log, verifying the stage b_lower is below the exact polar radius. Progress waits used interruptible clock.sleep (one 30-second wait and repeated 45-second waits); one write_stdin poll of the pytest process used yield_time_ms=1000. No wait exceeded 45 seconds. finalize.py writes the final identical review only after checking the completed pytest summary, all mutation classifications, reproducibility JSONs and clean git state.
