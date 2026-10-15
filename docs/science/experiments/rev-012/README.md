# REV-012 investigation: GMAT epoch bookkeeping and stop-time quantization

Research evidence for **VAL-0010** and **DR-0016**. This is not project code, not a Toolbox asset and not a Proof gate.

It answers two questions:
- **(a)** Why does the M1 GMAT report's epoch column drift from the `ElapsedS` label (REV-012)?
- **(b)** Why did the M2 GMAT finite-burn probe burn 1.85e-7 s short (VAL-0009, finding 3)?

## Result in one paragraph
Both effects are GMAT behaviour, verified against R2026a source and reproduced bit-exactly. Our code does nothing wrong. They are two different mechanisms.
- **(a) Epoch drift.** GMAT keeps the spacecraft epoch as a double A.1 Modified Julian Date. Every `Propagate` command re-rounds it to that double, so the rounding accumulates once per command.
  - The integrated trajectory time is not affected. States are at the labelled elapsed times to 9e-10 s.
- **(b) Burn shortfall.** It is **not** epoch-ulp quantization, as VAL-0009 had hypothesised; the 3.1e-7 s ulp was a coincidence. GMAT rounds the *final step* to a time stopping condition to a whole microsecond (`TIME_ROUNDOFF = 1e-6`).
  - After adaptive steps, any time-stopped `Propagate` therefore ends up to about 0.5 µs off. That covers ignition, burn duration and coast end alike.
  - The epoch ulp only chooses which microsecond the step rounds to.

Aligning every pre-stop step on the microsecond grid removes (b). Streaming gridded output from one `Propagate` command removes the accumulation in (a).

## Mechanisms in GMAT R2026a source
Source is the official repository, tag `GMAT-R2026a`, read on 2026-10-09: `https://sourceforge.net/p/gmat/git/ci/GMAT-R2026a/tree/`.

| Mechanism | File and function | What it does |
|---|---|---|
| M-a | `src/base/command/Propagate.cpp`, `Propagate::PrepareToPropagate` (l. 4152) and `Propagate::Execute` (l. 4610, 4617) | Each command takes `baseEpoch` from the spacecraft's (double) epoch. It then sets `currEpoch = baseEpoch + elapsedTime / SECS_PER_DAY`, where `elapsedTime` is the integrator time in seconds from the start of the command. The next command starts from that rounded double. |
| M-a | `src/base/foundation/GmatBase.cpp` (l. 223) | `hasPrecisionTime` defaults to `false`. Propagate has a two-part `GmatTime` path but takes it only when this flag is set. |
| M-b | `src/base/parameter/TimeData.cpp`, `TimeData::GetElapsedTimeReal` (l. 526) | `ElapsedSecs = (a1mjd - mInitialEpoch) * SECS_PER_DAY`, computed from the double epoch. |
| M-b | `src/base/stopcond/StopCondition.cpp`, `StopCondition::Evaluate` (l. 639) and `GetStopEpoch` (l. 898) | A time condition triggers when the goal lies between the previous and current values. The remaining step is then `dt = goal - previousAchievedValue`. |
| M-b | `src/base/command/Propagate.cpp`, `Propagate::TakeFinalStep` (l. 5501, 5640); `src/base/command/PropagationEnabledCommand.hpp` (l. 48) | `secsToStep = floor(secsToStep / TIME_ROUNDOFF + 0.5) * TIME_ROUNDOFF` with `#define TIME_ROUNDOFF 1.0e-6`. The source comment says this matches "the granularity given by other software (aka STK)". |

The resulting model of a `Propagate {Sat.ElapsedSecs = T}` command starting from epoch double `b` is:

```
natural (adaptive) steps until ElapsedSecs crosses T;  t_prev = last step time before crossing
q        = (fl(b + t_prev/86400) - b)*86400 - t_prev          (epoch quantization, |q| <= ulp(b)/2)
duration = t_prev + round_to_1us(T - t_prev - q)
epoch    = fl(b + duration/86400)                             (M-a)
```

If `T − t_prev` is a whole number of microseconds and |q| < 0.5 µs, the duration is exact. Otherwise the error is up to 0.5 µs + |q|.

GMAT R2026a accepts only epochs in [6116.0, 58127.5] MJD, so |q| ≤ 3.1e-7 s and the total error is at most about 0.81 µs.

## Environment and provenance
- **GMAT:** R2026a, build "Mar 26 2026 19:40:08"; `GmatConsole` sha256 `1162803d…52e2`, the same binary as the M1 reference.
- **Host:** macOS 26.2 x86_64.
- **Python:** 3.12 via `uv` (`uv.lock`).
- **Harness revision:** `e47ce31`. See `run_provenance.json` and `reproduce.json`.
- **Determinism:** two full runs produced byte-identical reports (combined sha256 `4bb291ae…b142`).
- **Reference reproduction:** re-running the committed M1 reference script and the committed VAL-0009 probe script gave **byte-identical** reports (`reproduce.json`).

## Experiments and key results (`results.json`)
Every case starts from the M1 initial state with point-mass Earth and WGS 84 μ. `a7000`, `a12000`, `a31041` and `a50000` are A.1 MJD epochs. `m1tt` is the M1 epoch, 01 Jan 2026 00:00 TT. The four binades give an epoch ulp of 7.9e-8, 1.6e-7, 3.1e-7 and 6.3e-7 s.

### 1. Segmented propagation (M1 pattern) — mechanism M-a

| Case | Commands | Epoch drift at end | Per command | Epoch rows bit-exact vs M-a | GMAT vs Kepler at label |
|---|---|---|---|---|---|
| `seg60_a7000` | 895 × 60 s | +3.44e-5 s | +0.489 ulp | 896/896 | 7.2 µm / 9.2e-10 s |
| `seg60_a12000` | 895 × 60 s | +3.44e-5 s | +0.244 ulp | 896/896 | same |
| `seg60_m1tt` (M1) | 895 × 60 s | **−1.063e-4 s** | −0.378 ulp | 896/896 | same |
| `seg60_a50000` | 895 × 60 s | +1.75e-4 s | +0.311 ulp | 896/896 | same |
| `seg10x6_m1tt` | 5370 × 10 s | +7.38e-4 s | +0.437 ulp | 896/896 | 11 µm / 1.4e-9 s |
| `seg300_m1tt` | 179 × 300 s | +6.25e-6 s | +0.111 ulp | 180/180 | 7.2 µm |
| `single_*` | 1 × 53 700 s | ≤ 2.8e-7 s (≤ 0.5 ulp) | — | 2/2 | 7.2 µm |
| `stream60_*` | 1 command, a row per 60 s step | ≤ ulp/2 (1.5e-7 s at M1) | single rounding per row | 896/896 | 7.2 µm; vs committed M1 reference **1.3e-9 m** |

- **The epoch is re-rounded at every command.** Python's IEEE result `e ← e + h/86400`, once per command, reproduces GMAT's A.1 epoch on every row. That includes the committed M1 drift of −1.06e-4 s.
- **The error per command is a constant.** It equals the rounding of `h/86400` against the epoch's ulp, so the drift grows linearly with the number of commands. Its sign and size depend on the epoch and the segment length.
- **The reported `Sat.ElapsedSecs` drifts by the same amount.** It equals (A1 − A1₀)·86400 exactly, so it is not a usable time axis.
- **The TT − A.1 conversion adds no accumulation.** It applies a fixed sub-ulp offset per run, for example −1.3e-7 s at the M1 epoch.
- **Not distinguished:** whether GMAT adds `fl(h/86400)` (double path) or the exact value (`GmatTime` seeded from the double) before rounding. Both models give identical results on every row here. The practical consequence is the same either way.

### 2. Finite burns — mechanism M-b
Each case coasts 600 s, burns T s and coasts to 53 700 s, using the probe's propagator settings (`InitialStepSize` 10 s, `MaxStep` 60 s).
- The burn duration is measured from propellant: (m₀ − m)/ṁ, resolution about 1e-12 s.
- The stop offsets of the coasts are measured against Kepler.
- A per-step `ReportFile` subscriber records the accepted steps inside each burn.

| Burn T | Measured duration error (all 5 epochs) | M-b prediction error |
|---|---|---|
| 1, 10, 17.3 s (stop within the first steps) | ≤ 1e-12 s | ≤ 2e-12 s |
| 60 s | −5.713e-7 s (+4.287e-7 s at `a7000`: the epoch's q selects the other microsecond) | ≤ 1.3e-12 s |
| 77.3, 120.7, 333.3 s | −1.847e-7 s (independent of epoch) | ≤ 2.3e-12 s |

- **M-b predicts all 35 durations to the mass resolution.** The error does **not** scale with the epoch ulp.
- **The 77.3 s case reproduces VAL-0009's −1.85e-7 s.** The last natural step ends at 62.171959… s, and the remainder is rounded to 15.128041 s.
- **The coast stops show the same mechanism:** ignition +3.24e-7 s, and the final stop between −5.5e-7 and +5.5e-7 s.
- **Attribution of the VAL-0009 1.17 cm** (`attribution.burn_m1tt_77.3`): re-running DOP853 with GMAT's three measured offsets reduces GMAT − reference from 1.17 cm / 1.34e-5 m/s to **6.8 µm / 8e-9 m/s**.
- **Sensitivities at 53 700 s, per µs:**
  - burn duration: 6.2 cm;
  - final stop time: 7.7 mm;
  - ignition shift: 0.1 mm.

### 3. Methodology variants

| Variant | Result |
|---|---|
| `burnstep_*`: ask for a single natural step over the burn | Works for 60 s. For 77.3 s the integrator cut the step (error −4.4e-8 s), so this is unreliable. |
| `aligned_*` (77.3, 120.7, 333.3 s at `a7000`, `a50000`, `m1tt`): coast `InitialStepSize = MaxStep = 60 s`, burn `InitialStepSize = MaxStep = 1 s` | Burn duration error ≤ 6e-10 s, which is mass round-off over 79–335 steps. Ignition 2e-13 s; final stop ≤ 1e-9 s (the Kepler-check floor). GMAT vs independent DOP853 **with no correction: 12 µm, 1.4e-8 m/s** (against 1.17 cm). Identical at all three epochs. |

## Reproduce
```sh
D=docs/science/experiments/rev-012
uv run --no-sync python $D/rev012.py generate      # scripts/ (committed)
uv run --no-sync python $D/rev012.py run           # needs GMAT R2026a; writes reports/
uv run --no-sync python $D/rev012.py analyze       # results.json from the committed reports
uv run --no-sync python $D/rev012.py reproduce     # M1 reference + VAL-0009 probe, byte compare
```
`analyze` needs only the committed reports, not GMAT.

## Files
| Path | Content |
|---|---|
| `rev012.py` | Generator, runner and analysis (ruff-clean). |
| `scripts/*.script` | 61 generated GMAT scripts. `__OUT__` and `__STEPS__` are report-path placeholders. |
| `reports/*.txt` | GMAT reports at 17 significant digits. `*.steps.txt` holds per-step subscriber rows during burns. |
| `results.json` | All measured and predicted quantities. |
| `run_provenance.json`, `reproduce.json` | GMAT binary hash and build, host, harness revision; reproduction of the committed references. |

## Limits
- Measurements cover point-mass Earth only, one host and GMAT R2026a.
- The time-dependent-force impact in VAL-0010 is an order-of-magnitude estimate, not a measurement.
- Aligned stepping relies on steps being MaxStep-limited. A generated reference must check this every time, using the per-step rows or the mass and Kepler timing checks. It is not guaranteed for stiffer cases.
