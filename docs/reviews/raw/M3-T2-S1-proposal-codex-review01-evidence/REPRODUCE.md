Run from repository root, offline. The scratch src trees are already prepared.

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B review_scratch/reviewer/probe.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/proto/src .venv/bin/python -B review_scratch/reviewer/probe.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/option_a/src .venv/bin/python -B review_scratch/reviewer/probe.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/early/src .venv/bin/python -B review_scratch/reviewer/probe.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/check_results.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/proto/src .venv/bin/python -B -m pytest -q -p no:cacheprovider review_scratch/reviewer/test_early_mass.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=review_scratch/reviewer/mutants/M-14/src .venv/bin/python -B -m pytest -q -p no:cacheprovider review_scratch/reviewer/test_early_mass.py
```

The last command must fail with the independent exception-type assertion. early/src/tars/sim/simulator.py is byte-identical to mutants/M-14/src/tars/sim/simulator.py. For edge cases replace probe.py with edges.py under BASE/proto PYTHONPATH; saved edges_base.json and edges_proto.json match. The supplied mutation script was run against reviewer/proto with its .venv symlink, copied tests/scenarios and pyproject.toml; results are in mutants/ and mutations.txt. This review does not reuse harness.py.
