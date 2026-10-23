# M3 T1 evidence: J2 force component (VAL-0020)

Authority: "I-17 — Merge P10 Decision and Authorize M3 T1 J2 Force Model" (Tech Lead, 2026-10-22). Branch `milestone-3-t1-j2-force-model`, created from `main` = `60648b9`.

The gates are in `tests/test_zonal_j2.py` and `tests/test_constants.py` (run by `pytest` and CI on all three platforms). This directory holds the **informational** measurements and the test-quality evidence. Nothing here is a gate or a threshold.

| File | What it is | Command (repository root) |
|---|---|---|
| `t1_j2_informational.py` → `t1_j2_informational_results.json` | Node/perigee drift against first-order theory (7 inclinations, 300 × 1000 km, 30 orbits, RK4 dt 10 s); invariant drift against dt; RK4 convergence; margins of the two derived gates | `uv run python docs/science/experiments/m3-t1/t1_j2_informational.py docs/science/experiments/m3-t1/t1_j2_informational_results.json` |
| `t1_mutation_check.py` → `t1_mutation_check_results.json` | 14 one-line mutants of the production code; each must make the T1 tests fail; the unmutated control must pass | `uv run python docs/science/experiments/m3-t1/t1_mutation_check.py docs/science/experiments/m3-t1/t1_mutation_check_results.json` |

Reproducibility: both scripts were run twice on the reference host (macOS x86_64, Python 3.12, `uv sync --locked`); the informational output is byte-identical across the runs. The JSON records the host. Other platforms are not measured for these informational files.

## Files added by the Review 01 and Review 02 corrections (I-19, I-20; append-only)
| File | What it is | Command (repository root) |
|---|---|---|
| `t1_review01_correction_check.py` → `t1_review01_correction_check_results.json` | Review 01 reproductions before/after; bit identity with `97b69ef` on 200 004 states; equatorial numerical domain | `uv run python docs/science/experiments/m3-t1/t1_review01_correction_check.py <src at 97b69ef> OUT.json` |
| `t1_review02_correction_check.py` → `t1_review02_correction_check_results.json` | Review 02 reproductions before/after, with exactly rounded references; legitimate zeros and subnormals; domain; canonical reach; bit identity with `b1566ae` on 200 004 states and three RK4 trajectories | `uv run python docs/science/experiments/m3-t1/t1_review02_correction_check.py <src at b1566ae> OUT.json` |
| `t1_review02_survivors.py` → `t1_review02_survivors_results.json` | Status of Review 02's three exploratory mutants on the corrected code (not part of the campaign) | `uv run python docs/science/experiments/m3-t1/t1_review02_survivors.py OUT.json` |

`t1_mutation_check.py` now holds 46 mutants: the original 14, Review 01's 8, and 24 protection-removal mutants (10 for R1-F1/F2, 14 for R2-F1/F2). `<src at SHA>` is `git archive SHA src` extracted to a directory.

## Files added by the Review 03 closure (I-21; append-only)
| File | What it is | Command (repository root) |
|---|---|---|
| `t1_mutation_check.py` → `t1_mutation_check_results_i21.json` | The campaign with mutant 47, `r3_upper_subnormal_band_ignored` (M3T1-R3-O1). `t1_mutation_check_results.json` keeps the 46-mutant results of I-20 at `4b85ded` | `uv run python docs/science/experiments/m3-t1/t1_mutation_check.py docs/science/experiments/m3-t1/t1_mutation_check_results_i21.json` |
