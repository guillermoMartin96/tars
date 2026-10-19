# M3 T0 reference-configuration spike (research only)

**Authority:** the Tech Lead's "TARS — M3 T0 Reference-Configuration Spike Authorization" (I-15, 2026-10-18), which authorizes **T0 only**. T1, T2 and later tasks are not authorized.  
**Record:** VAL-0019 (`docs/science/validation.md`). **Proposals:** DR-0029 (`docs/decisions/requests/DR-0029-m3-t0-proposals.md`), status OPEN. No decision is taken here.  
**Branch:** `milestone-3-t0-reference-spike`, created from `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3` (PR #4 merge commit).

## Scope
- **What this is:** these scripts and outputs are T0 spike evidence: executable reference configurations and the measurements the T0 proposals rest on.
- **What it is not:** they are not project code, Toolbox assets, references, goldens, thresholds or Proof gates. No file under `src/`, `proof/`, `toolbox/`, `scenarios/` or `.github/` is changed by T0.
- **Code independence:** the spike model (`t0_model.py`) is written independently of `tars` physics. The scripts import from `src/` only the M1/M2 scenario loaders, initial states, the committed M1/M2 GMAT script generators (unchanged, called read-only) and the approved threshold loader.
- **The physics configured is the approved M3 physics** (DR-0024 Resolution; DR-0027 B-1; DR-0028 J-ax-1):
  - GM 3.986004418e14 m³/s², a 6378137 m, 1/f 298.257223563, ω_E 7.292115e-5 rad/s;
  - J2 = −√5 C̄20 with C̄20 = −0.484165143790815e-3 (EGM2008 tide-free);
  - the GMAT R2026a exponential table, pinned verbatim by sha256 `75762f67…a85e` (copy in `data/`, checked on every load);
  - geodetic height on the WGS 84 ellipsoid;
  - v_rel = v − ω_E Ẑ × r;
  - cannonball drag using the current mass.
- **Frame:** the M3 inertial frame I, with the J2 axis, the ellipsoid axis and the atmosphere rotation axis all on +Z (J-ax-1).
  - In GMAT, I is realised as true-of-epoch axes (TOEEq) fixed at the scenario epoch.
  - No rotating Earth-fixed frame and no other pole model is substituted for J-ax-1.
  - `axis_fn` in `t0_model.py` evaluates J2 and the ellipsoid about GMAT's reported Earth-fixed axis. It is a **diagnostic** for DR-0025 Q-G2-1 option (b), labelled `..._DIAGNOSTIC` wherever it is used, and is not an M3 model.
- **Spike inputs, labelled as such.** These values are not proposals for scenario values; DR-0029 states what is proposed:
  - C_d 2.2, A 15 m², m 850 kg (B 25.8 kg/m²; the GMAT R2026a defaults, measured);
  - the M2 vehicle for the burn case;
  - termination altitudes 150 … 25 km in `t0_decay.py`, 80 km in the GMAT decay case.

## Files
| Script → output | What it measures |
|---|---|
| `t0_model.py` | The spike reference: constants, pinned table loader (digest-checked), GMAT's band rule, three geodetic algorithms (iterated to convergence; Vermeille 2002 closed form; a replica of GMAT's 1e-7 rad stopping rule, diagnostic), J2 and drag accelerations, RK4 with stage recording, DOP853 (rtol 1e-13) |
| `t0_atmosphere.py` → `t0_atmosphere_results.json` | Every band boundary: value jump, slope change, band selected at the base and one ulp either side (km and m routes). Lower edge and above-top behaviour. Linearised drag stiffness against RK4's stability limit at dt = 10 s. One boundary crossing under RK4 (dt 20 … 1.25 s) against a reference restarted at the crossing, with a one-band smooth control |
| `t0_decay.py` → `t0_decay_results.json` | 180 km decay with J2 and drag to the ground. RK4 stage heights against the committed states. Termination crossings at ten spike floors, located three ways (first committed state; scalar cubic Hermite on h with dh/dt = n̂·v; vector Hermite of r), against DOP853 event times. Spherical (impact) altitude at the crossing. Missed-crossing dip on an eccentric orbit at one fixed sampling phase (a measurement; the bound is in `t0_termination`). RK4 divergence near the ground |
| `t0_geodetic.py` → `t0_geodetic_results.json` | Q-G2-7 candidate test points: exact answers (equator, axis), 640 forward-constructed points, the GeographicLib CartConvert(1) published examples, FC-4 axisymmetry |
| `t0_frames.py` → `t0_frames_results.json` | FC-2, FC-3, FC-5, FC-6, FC-8 at spike level (signs, axisymmetry, v_rel direction) |
| `t0_termination.py` → `t0_termination_results.json` | Added after Review 01 (M3T0-F1, F2, F3). Missed-crossing curvature bound (dip ≤ dt²/8 · sup ḧ⁺, ḧ ≤ n̂·a + \|v_t\|²/(h + b²/a)) against worst-case constructions and a sampling-phase × eccentricity × inclination sweep (certified for two-body motion only; J2 + drag values are sampled estimates, Review 02 R2-F1); exact drag-stiffness thresholds with the circular-speed proxy and with a bound on \|v_rel\| for every bound state; the reviewer's P1 counterexamples; a derived sufficient stage-domain condition (drag envelope corrected after R2-F2) with an adversarial stress test; the RK4 stage order |
| `t0_axis_ablation.py` → `t0_axis_ablation_results.json` | Added after Review 02 (IM-1). Reproduces the DR-0029 P6 axis-fit residual from the committed GMAT axis-probe report (no GMAT run): the full fit (reproduces `t0_gmat_results.json` → `axis`) and the quadratic-only fit (0.986 m RMS) |
| `check_review02.py` | Regression checks for M3T0-R2-F1 … F3 and IM-1 (pytest, run explicitly). Each recomputes the protected quantity: sweep coverage and dips, the certified two-body bound by a second method, the between-sample extremum, the stage-domain bounds by a second implementation, RK4 steps from adversarial bound states, a byte-for-byte rerun of `t0_termination.py`, and the axis fit |
| `mutation_check_review02.py` | Corrupts copies of the result files and scripts and shows that the checks fail for each corruption and pass on the unmodified copy (R2-F3) |
| `check_review01.py` | Regression checks for M3T0-F1 … F4 (pytest, run explicitly; not collected by the project suite). Each recomputes a reviewer counterexample and tests the records and result files against it. All but one failed at `bdcaacf`; the one that passed there reproduces the stress input |
| `t0_regression.py` → `t0_regression_results.json` | Perturbations disabled: the spike's RK4 against the committed M1 golden final state (5371 ticks); the J2 = 0 / no-drag acceleration against point mass, bitwise |
| `t0_gmat.py` → `t0_gmat_results.json`, `gmat_runs/` | GMAT R2026a. Identity regression of the splice against the committed M1/M2 GMAT scripts and reports; the M3 exact-configuration form with perturbations off under the approved M1 GMAT gates; eight trajectory configurations and the M2-burn configuration against the spike; GMAT's Earth-fixed axis in TOE axes (two-orbit probe); density probes around every boundary; GMAT's behaviour below geodetic 0; GMAT's geodetic conversion; a decay stop at 80 km |

`gmat_runs/` keeps every script GMAT ran (`<RUN>` = the run's temporary directory; `<GMAT>` = the install root), the generated `.cof` and table files, the reports and a metadata file with digests. Identity-regression runs keep digests only, because their reports equal the committed references byte for byte.

## Reproduce
From the repository root, with the locked environment (`uv sync --locked`):
```sh
D=docs/science/experiments/m3-t0
for x in atmosphere decay geodetic frames regression termination; do
  uv run --no-sync python $D/t0_$x.py $D/t0_${x}_results.json
done
uv run --no-sync python $D/t0_gmat.py --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" \
    --out $D/t0_gmat_results.json
uv run --no-sync python $D/t0_axis_ablation.py $D/t0_axis_ablation_results.json
uv run --no-sync pytest -q -p no:cacheprovider $D/check_review01.py $D/check_review02.py
uv run --no-sync python $D/mutation_check_review02.py   # about 15 min
```
- **Reproducibility:** each command was run twice from a clean state. Every output, including all `gmat_runs/` files, was byte-identical between the runs (2026-10-18).
- **Run times:** the Python scripts take seconds each; `t0_gmat.py` takes about 40 s.
- **GMAT dependence:** `t0_gmat.py` refuses to run if GMAT's own table does not match the pinned digest.

## Provenance (2026-10-18)
- **Host:** macOS 26.2 x86_64, Intel i9-9880H (the M1/M2 reference host).
- **Software:** Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1 (from `uv.lock`). No new dependency.
- **GMAT R2026a**, build Mar 26 2026:
  - `GmatConsole` sha256 `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`;
  - EOP file `eopc04_08.62-now` sha256 `52c95d68…6ed3` (data to 2026-09-14);
  - `NUTATION.DAT` `633423d2…1566`;
  - `tai-utc.dat` `3524e1ae…310c3`.

  All are recorded in `t0_gmat_results.json` → `provenance`.
- **GMAT internals read:** the public GitHub mirror `ChristopherRabotin/GMAT` (`ExponentialAtmosphere.cpp`, `AtmosphereModel.cpp`, `DragForce.cpp`, master branch, read 2026-10-18). Its version is not tied to R2026a, so every behaviour taken from it was measured on R2026a before being relied on (band rule, below-zero failure, geodetic stopping rule).
- **Script and data digests:** see VAL-0019.

## Deviations and limitations
- **Report precision:** GMAT reports carry 16–17 significant digits. The density probes' common bias of −1.43e-7 relative is a property of the probe method; it is uniform across heights.
- **The drag-geodetic GMAT path is sensitive to `Earth.NutationUpdateInterval`.** At report epochs the Earth-fixed frame is identical under both settings; the difference arises inside GMAT's steps and is not attributed. It is escalated in DR-0029 (Q-G2-1).
- **No three-platform runs:** T0 measures nothing across platforms and sets no threshold.
