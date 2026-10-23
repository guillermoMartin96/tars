# M3 T1 Review 01 command ledger

All commands ran from the pinned clone root. No network commands, proof shell scripts, tracked edits, commits, merges, or pushes were performed. `review_scratch/` is ignored. Shell compound reads below are grouped exactly by purpose; the tool transcript is the raw source for their stdout. Long-running validation commands and exit codes are also recorded verbatim in `checks-ledger.txt`.

## Initial inventory and reads

- `pwd; git status --porcelain; git rev-parse HEAD; rg --files -g 'AGENTS.md' -g '*DR-002*' -g '*ADR-000*' -g '*t1*' -g '*T1*'`: pinned HEAD; empty status; relevant files found; no AGENTS.md returned.
- `cat src/tars/sim/constants.py src/tars/sim/forces.py tests/test_constants.py tests/test_zonal_j2.py`: complete implementation and new tests inspected.
- `mkdir -p review_scratch; cat docs/milestones/M3-T1-report.md docs/science/experiments/m3-t1/README.md docs/science/experiments/m3-t1/t1_mutation_check.py; rg -n 'VAL-0020|gamma|γ|40|13|round' docs/science/validation.md; ls toolbox/validators; ls review_scratch/ci`: reports, harness, bounds, validators, and six supplied CI files inspected.
- `cat docs/decisions/requests/DR-002{4,5,6,7,8,9}*.md docs/milestones/M3-T1-authorization-packet.md docs/milestones/M3-proposal.md docs/milestones/M3-baseline-and-impact.md proof/PROOF.md proof/review.md proof/definition-of-done.md > review_scratch/authority-read.txt`: captured authority inputs. `cat review_scratch/authority-read.txt` exceeded tool output size; relevant sections were read separately below. This capture is not independent experimental evidence.
- `cat src/tars/sim/integrators.py; rg --files docs/decisions | rg '0003|0004|0009'; cat toolbox/validators/README.md; cat pyproject.toml; git diff --stat 60648b9..HEAD; git branch -avv`: 15 changed paths; only two production files; detached HEAD; main and remote tracking refs as expected.
- `sed -n '995,1118p' docs/science/validation.md; rg -n 'SCI-0013|Status update 4|status update 4' docs/science/assumptions.md; sed -n '1,250p' docs/science/experiments/m3-t1/t1_j2_informational.py; cat docs/decisions/0003* docs/decisions/0004* docs/decisions/0009*`: complete VAL-0020, experiment script, applicable ADRs inspected.
- `rg -n 'Q3|complex|VO-1|FC-6|domain|Q10|T1' docs/decisions/requests/DR-0025-m3-validation-strategy.md docs/milestones/M3-T1-authorization-packet.md docs/milestones/M3-proposal.md; sed -n '534,578p' docs/science/assumptions.md; git diff 60648b9..HEAD -- docs/milestones/README.md docs/science/assumptions.md; rg -n 'ZonalJ2Gravity|EarthJ2Constants|WGS84_EGM2008|ForceModel|acceleration\(' src/tars/sim`: SCI status, append-only changes and consumers inspected.
- `sed -n '1,180p' docs/decisions/requests/DR-0025-m3-validation-strategy.md; sed -n '1,250p' docs/milestones/M3-T1-authorization-packet.md`: validation matrix and complete authorization packet inspected.
- `rg -n '^##|^###|Q-G2-2|P10|Option \(a\)|J-ax-1' docs/decisions/requests/DR-002{4,5,6,7,8,9}*.md > review_scratch/decision-index.txt; cat review_scratch/decision-index.txt`: decision section inventory; long output truncated, relevant resolutions read separately.
- `sed -n '215,245p' docs/decisions/requests/DR-0025-m3-validation-strategy.md; sed -n '287,330p' docs/decisions/requests/DR-0026-m3-force-scenario-event-architecture.md; sed -n '59,114p' docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md; sed -n '83,125p' docs/decisions/requests/DR-0027-m3-atmosphere-validity-boundary-and-table-residuals.md; rg -n '^##|P10|DECIDED' docs/decisions/requests/DR-0029-m3-t0-proposals.md`: governing resolutions and outstanding items inspected.
- `git log --format='%H %s' 60648b9..HEAD; git status --porcelain; git diff --stat`: four expected commits; clean tracked tree.
- `git diff --numstat 60648b9..HEAD -- src proof toolbox scenarios .github uv.lock pyproject.toml`: constants +58/-0; forces +39/-0; no other changes in these paths.
- `nl -ba src/tars/sim/forces.py | tail -46; nl -ba docs/milestones/M3-T1-authorization-packet.md | sed -n '34,43p'; nl -ba tests/test_zonal_j2.py | sed -n '215,256p'; nl -ba src/tars/sim/constants.py | sed -n '58,68p'`: exact finding references verified.
- `cat .github/workflows/ci.yml | head -85; cat toolbox/validators/cross_platform.py | tail -35; cat toolbox/validators/determinism.py | tail -35`: CI matrix and non-writing validator CLI paths checked.

## Executions

Created the reviewer scripts listed here using shell heredocs. Their complete source is preserved beside this ledger. Only scratch scripts were edited, including corrections to the reviewer's interval implementation; no scratch result from a failed development iteration is used as evidence.

- `.venv/bin/python review_scratch/run_checks.py`: launches the seven commands in `checks-ledger.txt`, with one log per command. No tracked experimental output path is used.
- `.venv/bin/python review_scratch/adversarial.py > review_scratch/adversarial.log`: exit 0; Decimal acceleration comparison; display gap; finite extreme, non-finite, subnormal, and parameter probes. `adversarial.json` records values and environment. The initial CPU sysctl probe returned no CPU model.
- `.venv/bin/python review_scratch/own_mutants.py > review_scratch/own_mutants.log`: exit 0; seven file-level mutants, each in its own copied src tree. Three survive all 26 T1 cases; four fail assertions. Individual commands, exits and log tails in `own_mutants.json`; full logs in the seven named subdirectories.
- `.venv/bin/python review_scratch/interval_bound.py > review_scratch/interval_bound.json`: final exit 0; all 162 gradient comparison points certified, maximum interval ratio 0.4114583333333321. Development iterations initially omitted absolute lifting of a negative scalar and then encountered an interval/dual dispatch TypeError; these were corrected only in the reviewer script and rerun. A subsequent revision adds the gradual-underflow absolute allowance to every rounding. Only the final saved script/output supports the conclusion.
- `.venv/bin/python review_scratch/contracts.py > review_scratch/contracts.log`: exit 0; all public parameters writable; changing J2 to zero leaves nonzero force; source-literal guard can miss hex forms.
- Inline `.venv/bin/python` execution of the interval helper at equator and pole: conservative naive interval fractions 0.703125 and 1.015625 of the known-answer bound. The latter is NOT a violation; independent intervals overestimate exact operations. Exact r2, sqrt(r2), s2 and multiplication by 2 at the pole give the tighter analytic count described in the report. This exploratory computation is not used as a certificate.
- `.venv/bin/python review_scratch/path_counts.py > review_scratch/path_counts.log`: exit 0; production 25 scalar operations, depth 8; absolute acceleration 27/depth 8; each dual evaluation 123/depth 16. Depth includes paths through zero-valued gradient terms.
- `.venv/bin/python review_scratch/records_audit.py > review_scratch/records_audit.log`: exit 0; committed and reproduced informational/mutation JSON equal; protected diff empty; tracked status empty; environment/hardware summary captured. The hardware utility cannot identify the CPU model. Hardware identifiers are not repeated in the report.
- `.venv/bin/python review_scratch/builtin_mutant_details.py > review_scratch/builtin_details.log`: exit 0; reruns each of the 14 built-in mutants with complete failure logs; all fail with AssertionError, not infrastructure/import exceptions.
- `.venv/bin/python review_scratch/pm_drift.py > review_scratch/pm_drift.log`: exit 0; point-mass-only control also exhibits approximately fifth-order invariant drift.
- `.venv/bin/python toolbox/validators/cross_platform.py > review_scratch/m1_golden.log`: exit 0; zero position/velocity differences and bit-identical M1 state.
- `.venv/bin/python toolbox/validators/determinism.py > review_scratch/m1_determinism.log`: exit 0; two identical M1 hashes, matching the committed golden hash.
- Inline Python JSON inspection read every file in `review_scratch/ci/`: three metadata files have expected SHA/branch/run/job results; three excerpts report constants 12, J2 14, total 1204 passed/3 skipped. No authenticity conclusion is inferred.
- Inline JSON inspections read `m1.json`, `m2.json`, `info.json`, `mutation.json`, `records_audit.json`, `own_mutants.json`, `builtin_details.json`, and committed T1 result files: M1 7 validator results; M2 228; informational numeric tables match their printed rounding.
- Repeated `cat`, `tail -3`/`tail -5`, and `wc -c` commands on the logs/JSON above monitored process completion and inspected saved results. They do not constitute additional independent experiments.
- `ps -Ao pid,etime,pcpu,command | rg 'interval_bound|pytest|run_checks'`: exit 1; process listing denied by sandbox. No conclusion drawn.

The final report and this ledger are reviewer records, written only in scratch. Final status/diff verification and the final pytest result are appended below when completed.

Additional completed commands:

- `date -u; stat -f '%SB %Sm' -t '%H:%M:%S' review_scratch/pytest.log`: recorded timing of full-suite progress; no scientific inference.
- `rg --files | rg -i 'nga|wgs84|0036|higham|\.pdf$'`: no local NGA standard or Higham source found. Source provenance cannot be reauthenticated offline.
- `.venv/bin/python review_scratch/ci_audit.py > review_scratch/ci_audit.log`: exit 0; all three metadata exports parsed; two final Intel steps start before their enclosing job timestamp. Exact anomalies in `ci_audit.json`.
- Reran `.venv/bin/python review_scratch/own_mutants.py > review_scratch/own_mutants.log` after adding an eighth mutant (`0.99 < z²/r² < 0.9999`, x/y factor perturbed by 1%). Four survive, four detected. Updated source and JSON are final evidence.
- Inline Python wrote `review_scratch/environment.json`: OS/kernel, Python compiler/build, float properties and installed versions. CPU-model sysctl denied (exit 1); hardware utility reports x86_64, eight cores, 2.3 GHz and unknown processor model.
- Read-only `cat toolbox/scripts/run_m1_proof.sh; sed -n '1,120p' toolbox/scripts/run_m2_proof.sh`: inspected wrapper contents without executing them. Wrapper 9/9 and 20/20 are historical claims, distinct from the locally rerun validator result counts.
- Saved `git diff 60648b9..HEAD -- docs` to `docs-diff.patch` and the requested production/protected-path diff to `isolation-diff.patch`.
- Reviewed report line references with `nl -ba`; corrected only scratch report wording/references.
- `.venv/bin/python review_scratch/bound_falsification.py > review_scratch/bound_falsification.log`: exit 0; 5009 points (5000 seeded random exterior points plus exact/cancellation-neighbor cases), no gradient-bound violation, maximum allowance utilization 0.05254653030164237. A falsification search, not a proof.

## Final verification

- Direct reads of DR-0024 Resolution/conventions (`sed -n '336,450p' ...`) and DR-0029 P10 (`sed -n '390,432p' ...`) confirmed the approved constants, fixed-frame model, and unchanged decision boundaries.
- Resumed the validation orchestrator with `write_stdin(session_id=50054)`: all seven commands exit 0.
- `tail -22 review_scratch/pytest.log`: **1207 passed, 3 warnings in 1717.76 s (28:37)**. Warnings arise in adversarial/non-finite validation tests; see complete pytest log.
- `git status --porcelain; git diff --stat`: both empty, including after all experiment/validator executions. No restore was needed; committed experiment results were never rewritten.
- `git rev-parse HEAD origin/milestone-3-t1-j2-force-model main origin/main`: pinned T1 SHA twice; `60648b93385a9954194730006aeac29ea14875ad` twice.
- Updated only the scratch report's final pytest result and copied it byte for byte to `raw-reviewer-output.md`. The final assistant message reproduces that complete report.
- Final inline Python asserted identical report/raw bytes, no placeholder, empty tracked status/diff, and wrote `final-verification.json`: report SHA-256 `f4a4f59a0c37a76628b2abc5036c33cf6d4cfb9593034e4c17930c8c16f60b15`. Exit 0. This final ledger append affects scratch only.
