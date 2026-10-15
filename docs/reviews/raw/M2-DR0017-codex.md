| Safeguard | Status | Evidence |
|---|---|---|
| 1 — Reject timing Δv error above `1e-7 m/s` | NOT MET | Two valid configurations pass `schedule_burn` despite independent errors exceeding the budget; one executes successfully. See F1. |
| 2 — Actual acceleration, executed interval, documented limitations | PARTIAL | Algebraically correct: `c·log1p(ṁ·abs(D−d)/m_end)`, with end mass after the longer interval. Completed burns use commanded duration; depleted burns use depletion duration. Floating-point evaluation can underestimate substantially. Per-burn and trajectory limitations are documented. |
| 3 — Reject non-finite/unrepresentable timing | MET | All 16 independent NaN, ±inf, and huge-integer probes returned `schema_invalid`; overflowing cutoff and collapsed interval returned `burn_unschedulable`. |
| 4 — Scheduling rejection vocabulary | MET | Representability and budget failures use `burn_unschedulable`; malformed inputs retain the approved `schema_invalid` classification. |
| 5 — D1a cutoff and retained residual | MET | Step-down precedes the budget calculation. Both policies retain the N5 residual; executed versus planned residual differs by only `−3.47e-18 kg`. Subsequent residual burns and rejection atomicity remain correct. |
| 6 — Machine-readable termination cause | MET | Cutoff transitions distinguish `completed` and `propellant_depleted`; ignition has no end cause. Removing this field fails its test. |
| 7 — Boundary tests | PARTIAL | Mission-time, acceleration, and depletion coverage exists, but arithmetic extremes and close-budget classification are missing. A wrong end-mass mutation passes all **457 tests**. |

### F1 — Floating-point evaluation permits over-budget burns

**Severity:** High  
**Claim:** The exact formula is correct, but its evaluation is not a reliable rejection bound across accepted configurations.

**Evidence:** [propulsion.py](src/tars/sim/propulsion.py:484) computes end mass as `(dry + propellant) − ṁ·duration` and forms `ṁ·abs(dt)` before dividing. Independent 100-digit calculations reproduced two false accepts through `schedule_burn`:

- **Cancellation:** `F=3e-7 N`, `Isp=3e-7/9.80665 s`, dry mass `3 kg`, propellant `1e16 kg`, ignition `3 s`, duration `9999999999999998 s`. Executed duration is `9999999999999996 s`. The computed end mass is `6 kg`; the exact smaller end mass is `5 kg`. Reported error: **`8.630462173553426e-8 m/s`**. Independent error: **`1.009416709863639e-7 m/s`**.
- **Underflow:** `F=1e-280 N`, `Isp=1e20/9.80665 s`, dry mass and propellant each `1e-310 kg`, ignition `1e-10 s`, duration `1e-11 s`. Executed duration is `1.0000000000000004e-11 s`. `ṁ·abs(dt)` underflows to zero. Reported error: **zero**. Independent error: **`2550.92705351469 m/s`**. The simulator completes the step with finite state and both transitions.

These are extreme configurations, but all pass the existing specification validators. Reproductions: [probes.py](review_scratch/probes.py), [results](review_scratch/probes.txt), [execution evidence](review_scratch/execution.txt).

**Suggested fix:** Use cancellation-resistant end-mass evaluation and scaled arithmetic that preserves small timing contributions, with conservative rounding/error handling around the budget. Reject numerically indeterminate bounds as `burn_unschedulable`. Add both reproductions as regressions.

### F2 — Tests permit the wrong end-mass choice

**Severity:** Medium  
**Claim:** The suite does not adequately discriminate the required smaller end mass or exercise the acceptance threshold closely.

**Evidence:** An in-memory mutation replacing `max(intended, executed)` with `min(intended, executed)` survives **all 457 tests**. This uses the larger mass and underestimates timing error. The named boundary test compares `1e9 s` with `1e15 s`, rather than tightly bracketing `1e-7 m/s`.

Eight other mutations were caught: zero error, initial mass, naïve logarithm, commanded duration on depletion, removed step-down, discarded residual, omitted scheduling mass, and omitted event cause. See [mutation script](review_scratch/mutations.py) and [surviving full-suite result](review_scratch/wrong_end_mass_full.txt).

**Suggested fix:** Add independent threshold cases immediately below and above the budget, covering both interval orderings and depletion step-down. Include cancellation and subnormal arithmetic cases.

### F3 — ADR retains the superseded microsecond bound

**Severity:** Low  
**Claim:** The documentation still attributes cutoff-floor behavior to a universal `1 µs` timing limit.

**Evidence:** [ADR-0007](docs/decisions/0007-propulsion-architecture.md:53) says the floor absorbs “at most ṁ × 1 µs” and quotes `1.6e-7 kg` at extreme times. DR-0017 replaces that time limit with a vehicle-dependent Δv budget. Positive D1a residuals are retained rather than absorbed by the floor. SCI-0012’s D1a note and the per-burn/trajectory limitations otherwise reflect the approved decision.

**Suggested fix:** Remove the obsolete microsecond bound and describe floor corrections separately from retained timing residuals.

`plan_burn` without dry mass deliberately returns an unchecked plan with `timing_delta_v_error_mps=None`; the public simulator entry point replans with dry mass and queued propellant. I found no separate public execution path bypassing that check. F1 defeats the check numerically.

Earlier fixes remain intact: N4 effective mass stays non-negative; 16 non-depletion comparisons remain byte-identical; pre-T2, unconfigured, and configured-coast states match byte-for-byte at `dt=10`, `0.1`, and `7/3`.

**T2 verdict: FAIL.** Ran required pytest (**457 passed**), ruff lint/format (**passed**), determinism (**exact `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`**), M1 proof (**PASS**), 3,000 independent randomized probes, arithmetic-edge/execution probes, prior regression probes, and nine in-memory mutations; only `review_scratch/` was written.