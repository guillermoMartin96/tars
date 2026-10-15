| Item | Status | Evidence |
|---|---|---|
| Safeguard 1 — Enforce `1e-7 m/s` budget | NOT MET | New spec-valid burn is accepted and executes despite exceeding the budget; see N1. |
| Safeguard 2 — Actual acceleration, executed interval, limitations | PARTIAL | Correct interval and documented limitations; estimate remains nonconservative for subnormal logarithm arguments. |
| Safeguard 3 — Reject invalid/unrepresentable timing | MET | All 16 malformed-input probes rejected as `schema_invalid`; overflowing and collapsed cutoffs rejected. |
| Safeguard 4 — Rejection vocabulary | MET | Timing failures use `burn_unschedulable`; malformed inputs preserve `schema_invalid`. |
| Safeguard 5 — D1a and retained residual | MET | Randomized probes exercised 3,451 step-downs. Both original residual reproductions pass; execution/accounting discrepancy remains `−3.47e-18 kg`. |
| Safeguard 6 — Termination cause | MET | Events distinguish completed/depleted cutoffs; removing the cause fails tests. |
| Safeguard 7 — Boundary tests | MET | Required mission-time, acceleration, depletion, and close-budget tests pass. |
| F1 | PARTIAL | Both original reproductions now reject. N1 demonstrates a remaining arithmetic gap. |
| F2 | RESOLVED | Wrong-end-mass mutation fails four tests; ±1% budget/comparison mutations fail. All 15 exercised mutations were caught. |
| F3 | RESOLVED | ADR-0007 removes the obsolete microsecond bound and separates retained residuals from integration-roundoff correction. |
| Ordinary-mission conservatism | MET | No rejections among 50,005 reference cases through `1e9 s`; maximum exact error `5.2872e-8 m/s`. Another 10,000 ordinary-envelope probes produced zero false rejections. |
| Earlier T1/T2 fixes and M1 | MET | Residual, nonnegative effective mass, and rejection-atomicity reproductions pass; 16 nondepletion comparisons and 1,000 coast ticks at each of three timesteps remain bit-identical. M1 proof passes; determinism matches `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. |

### N1 — Subnormal logarithm argument defeats the conservative estimate

**Severity:** Medium

**Claim:** The relative inflation does not cover subnormal rounding in `(F/m_end)·dt/c`. A spec-valid burn exceeding the approved budget is accepted and executes. The excess is physically negligible, approximately `5e-17 m/s`, but violates the unconditional rejection safeguard.

**Evidence:** At [propulsion.py](src/tars/sim/propulsion.py:511), use:

- `thrust_n=8.38860800614743`
- `isp_s=1.0197162129779283e307`
- Dry mass and propellant: `1 kg` each
- Ignition: `1e9 s`; commanded duration: `0.1 s`

Executed duration is `0.10000002384185791 s`. The estimate is **`9.999999984816874e-8 m/s`**, while independent 400-digit arithmetic gives **`1.0000000005000002e-7 m/s`**, including direct integration of actual acceleration. `schedule_burn` accepts; stepping completes with finite state and both transitions. See [reproduction and execution evidence](review_scratch/reproductions.txt).

The broader 12,225-case extreme search also found underestimates in both interval orderings. See [search results](review_scratch/search.txt).

**Suggested fix:** Account for absolute subnormal rounding with outward bounds, or use a safely scaled `a_max·|dt|` upper bound when the logarithm argument is tiny. Add this public-simulator reproduction as a regression.

**T2: FAIL —** Ran required pytest (**470 passed**), ruff lint/format (**passed**), determinism and M1 proof (**passed**), original reproductions, randomized/adversarial searches, ordinary-mission checks, regression comparisons, and **15 in-memory mutations**. Authored changes are confined to `review_scratch/`; `src/` and `tests/` were not modified.