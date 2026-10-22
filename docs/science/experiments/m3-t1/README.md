# M3 T1 evidence: J2 force component (VAL-0020)

Authority: "I-17 — Merge P10 Decision and Authorize M3 T1 J2 Force Model" (Tech Lead, 2026-10-22). Branch `milestone-3-t1-j2-force-model`, created from `main` = `60648b9`.

The gates are in `tests/test_zonal_j2.py` and `tests/test_constants.py` (run by `pytest` and CI on all three platforms). This directory holds the **informational** measurements and the test-quality evidence. Nothing here is a gate or a threshold.

| File | What it is | Command (repository root) |
|---|---|---|
| `t1_j2_informational.py` → `t1_j2_informational_results.json` | Node/perigee drift against first-order theory (7 inclinations, 300 × 1000 km, 30 orbits, RK4 dt 10 s); invariant drift against dt; RK4 convergence; margins of the two derived gates | `uv run python docs/science/experiments/m3-t1/t1_j2_informational.py docs/science/experiments/m3-t1/t1_j2_informational_results.json` |
| `t1_mutation_check.py` → `t1_mutation_check_results.json` | 14 one-line mutants of the production code; each must make the T1 tests fail; the unmutated control must pass | `uv run python docs/science/experiments/m3-t1/t1_mutation_check.py docs/science/experiments/m3-t1/t1_mutation_check_results.json` |

Reproducibility: both scripts were run twice on the reference host (macOS x86_64, Python 3.12, `uv sync --locked`); the informational output is byte-identical across the runs. The JSON records the host. Other platforms are not measured for these informational files.
