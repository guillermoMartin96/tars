All Python invocations used the clone's `.venv/bin/python -B` and `PYTHONDONTWRITEBYTECODE=1` (utility scripts without project imports also used -B). No network used.

Package verification: `(cd review_scratch/pkg && shasum -a 256 -c SHA256SUMS)`; all ten matched. HEAD: ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd.

Prototype preparation: copy src, tests, scenarios into reviewer/proto, then `patch -p1 -d review_scratch/reviewer/proto < review_scratch/pkg/prototype-v2.patch`. `.venv` symlink points to the original venv. An initial nested git-apply invocation did not apply files; verified source before rerunning all affected checks. No tracked changes occurred.

Reproduce own probes from repository root:
```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B review_scratch/reviewer/probes.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/proto/src .venv/bin/python -B review_scratch/reviewer/probes.py
```
Repeat each for masked_probe.py and warnings_error.py. `independent.py` is the separate 26-case corpus (writer, view, alias, injected stage, finite overflow, BaseException and arithmetic failures), run against BASE, proto, M14-own, M19-own and coastA. Build variants with make_variants.py.

Reproduced provided harness.py and harness_writers.py against BASE and proto with the same PYTHONPATH pattern and output filename argument. Byte comparison and independent case comparisons: summarize.py / summary.txt.

Mutation campaign: `.venv/bin/python -B review_scratch/pkg/mutate.py "$PWD/review_scratch/reviewer/proto" "$PWD/review_scratch/reviewer/mutations"`. XML and JSON retained. Control 78 passed; 20 mutants killed; M19 survives. Own M14 also run with pytest -k t07_k; own M19 ran both S1 files.

BASE red/green: `PYTHONPATH=src .venv/bin/python -B -m pytest -q -p no:cacheprovider review_scratch/reviewer/proto/tests/test_s1_failure_paths.py review_scratch/reviewer/proto/tests/test_s1_force_context.py --junitxml=review_scratch/reviewer/base-tests.xml`. 27 pass, 51 AttributeError failures, no collection errors.

AST identity: `.venv/bin/python -B review_scratch/pkg/ast_identity.py . review_scratch/reviewer/proto`. 51 checks, no failures.

scenarios.py launches toolbox/scripts/run_mission.py for all five unchanged scenario JSON files against both trees and compares events.jsonl and summary.json bytes.

Full copied test suite additionally launched using prototype PYTHONPATH and -p no:cacheprovider; see full-tests.log for its eventual result/limitation.

T1: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/proto/src .venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_propulsion.py` -> 115 passed. The full copied suite stopped during collection because the scratch copy lacked proof/thresholds/m2.json; no full-suite pass claimed.
