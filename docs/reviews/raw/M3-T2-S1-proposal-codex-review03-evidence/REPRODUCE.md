Run from the unchanged BASE clone root, offline, using its existing locked `.venv`.

All outputs and copied trees are under this directory. Source trees are `base`, `v2`, `v3s`, `v3l`; BASE has the proposed S1 tests added only inside scratch. v2/v3l have v3 tests added by discriminate.py. The mutation tool creates a `.venv` symlink in its scratch prototype root solely to find the existing interpreter.

Initial build and packaged evidence runs:

```sh
(cd review_scratch/pkg && shasum -a 256 -c SHA256SUMS)
.venv/bin/python -B review_scratch/reviewer/build.py
.venv/bin/python -B review_scratch/reviewer/run_checks.py
.venv/bin/python -B review_scratch/reviewer/run_extra.py
.venv/bin/python -B review_scratch/reviewer/corpora.py
.venv/bin/python -B review_scratch/reviewer/discriminate.py
.venv/bin/python -B review_scratch/reviewer/regression.py
.venv/bin/python -B review_scratch/reviewer/validators.py
.venv/bin/python -B review_scratch/reviewer/more_checks.py
.venv/bin/python -B review_scratch/reviewer/t1_checks.py
```

Before rerunning build.py remove only the generated four source-tree directories; patches are relative to BASE and cannot be reapplied to already patched trees. Before rerunning run_extra.py remove its existing v3s/.venv symlink. T1 scripts require the preserved historical forces.py files beneath 97b69ef/ and b1566ae/ (extracted with `git show REV:src/tars/sim/forces.py`). Initial run_checks.py's full-suite collection failure predates copying proof fixtures; regression.py is the corrected full-suite run.

Independent probes (repeat for each desired tree):

```sh
PYTHONPATH="$PWD/review_scratch/reviewer/v3s/src" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/independent.py
PYTHONPATH="$PWD/review_scratch/reviewer/v3s/src" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/ownership.py
PYTHONPATH="$PWD/review_scratch/reviewer/v3s/src" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/edge_probe.py
PYTHONPATH="$PWD/review_scratch/reviewer/v3s/src" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/overflow_order.py
PYTHONPATH="$PWD/review_scratch/reviewer/v3s/src" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B review_scratch/reviewer/runner_probe.py
.venv/bin/python -B review_scratch/reviewer/raw_probe.py
.venv/bin/python -B review_scratch/reviewer/inspect_contract_scope.py
.venv/bin/python -B review_scratch/reviewer/analyze.py
.venv/bin/python -B review_scratch/pkg/compare_integrators.py review_scratch/reviewer/base.jsonl review_scratch/reviewer/v2.jsonl review_scratch/reviewer/v3s.jsonl review_scratch/reviewer/v3l.jsonl
```

For M-19 use PYTHONPATH pointing at reviewer/mutations/M-19/src with ownership.py. Raw output equality and the source argument establish current-production equivalence; mutation survival alone does not.

`SHA256SUMS` covers reviewer-authored scripts, final report and top-level outputs plus mutation JSON/JUnit; copied source trees and large per-mutant source copies are reproducible from the verified package. No external CI, network, or new GMAT execution is claimed. M1/M2 proof validators and reference-based checks run locally; uv-based shell wrappers were not rerun because the task specifies the pre-synced interpreter and no network.

Additional reviewer-only missing mutant:

```sh
.venv/bin/python -B review_scratch/reviewer/powered_mutant.py
.venv/bin/python -B review_scratch/reviewer/check_ownership.py review_scratch/reviewer/ownership.txt
.venv/bin/python -B review_scratch/reviewer/check_ownership.py review_scratch/reviewer/powered-lazy-own.txt
```

The final command is expected to fail for changed powered mass. The generated mutant passes the 86 supplied S1 tests. This corroborates the suggested coverage addition without changing any supplied test or actual prototype implementation.

`rerun_own.py` regenerates the independent execution corpus with explicit propulsion hex fields; run `analyze.py` afterwards. After full pytest completion, `finalize.py` checks exact expected counts, fills the report's regression paragraph, verifies the untouched tracked tree and hashes all top-level reviewer artifacts and mutation JUnit/JSON.
