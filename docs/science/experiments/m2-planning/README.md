# M2 planning experiments (research only)

These scripts and outputs are **planning evidence** for Milestone 2 (VAL-0008, VAL-0009).
They are not project code, not Toolbox assets, and not Proof gates. They measure what
a finite burn does to the numerics and how GMAT models it, so that the M2 Decision
Requests and candidate tolerances rest on measurements rather than guesses.

Executed on 2026-10-09 at `63bec8d` (macOS 26.2 x86_64, Intel i9-9880H, Python 3.12.15,
NumPy 2.5.3, SciPy from `uv.lock`). GMAT R2026a (build Mar 26 2026) for the probe.

## Model under test
Same as the candidate M2 physics (DR-0011, DR-0012), starting from the M1 initial state:

```
r' = v
v' = -mu r / |r|^3 + (F / m) u        u = v/|v| (prograde, velocity-tracking) or a fixed inertial vector
m' = -F / (Isp g0)                    during the burn; 0 otherwise
```

Illustrative spacecraft (DR-0010): dry 1000 kg, propellant 300 kg, F = 490 N, Isp = 312 s,
g0 = 9.80665 m/s². Ignition at t = 600 s; duration 77.3 s, deliberately not a multiple of
dt = 10 s. Propagated to 53 700 s, like the M1 GMAT comparison.

## Files
| File | Purpose |
|---|---|
| `burn_experiment.py` → `burn_results.json` | RK4 dt = 10 s (with and without step splitting at engine cutoff) vs SciPy DOP853 (rtol 1e-13). Convergence, mass accuracy, post-burn Kepler check, finite vs impulsive, tracking vs fixed direction. |
| `limit_experiment.py` → `limit_results.json` | Impulsive-limit order (fixed Δv, thrust ×2 and duration ÷2 each row). Integrated "sensed Δv" vs the rocket equation. |
| `m2_burn_probe.script` | GMAT template. `__G__` is `ChemicalThruster.GravitationalAccel`; `__OUT__` is the report path. |
| `gmat_probe_report_g*.txt` | GMAT reports: rows at ignition, at cutoff, and at 53 700 s. Columns: TTModJulian, X, Y, Z [km], VX, VY, VZ [km/s], TotalMass [kg], SMA [km]. |
| `compare_gmat_probe.py` → `gmat_probe_comparison.json` | GMAT vs the DOP853 reference from `burn_results.json`. |

## Reproduce
```sh
D=docs/science/experiments/m2-planning
uv run --no-sync python $D/burn_experiment.py $PWD/src scenarios/m1_leo_250km.json
uv run --no-sync python $D/limit_experiment.py $PWD/src scenarios/m1_leo_250km.json
(cd $D && uv run --no-sync python compare_gmat_probe.py burn_results.json \
   gmat_probe_report_g9.80665.txt gmat_probe_report_g9.81.txt)
```
A re-run at `63bec8d` reproduced all three JSON outputs byte-for-byte. The GMAT probe requires a
local GMAT install: substitute the placeholders, then run `GmatConsole --run <script>` from GMAT's `bin/`.

The scripts carry a file-level `# ruff: noqa` so the code that produced the results is kept exactly as it ran.
