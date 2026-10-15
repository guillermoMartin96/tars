| Item | Status | Evidence |
|---|---|---|
| Safeguard 1 — `1e-7 m/s` budget | MET | N1 and both F1 reproductions reject. Repeated extreme search: 12,225 cases, zero underestimates. New search: 92,874 cases, zero bounds below independently calculated exact `a_max·abs(dt)`. |
| Safeguard 2 — Actual acceleration, executed interval, documented assumptions | PARTIAL | Bound is mathematically valid and numerical probes pass; source comments retain an incorrect universal logarithmic identity. See N2. |
| Safeguard 3 — Invalid/unrepresentable timing | MET | All 16 malformed-input probes return `schema_invalid`; overflowing and collapsed cutoffs return `burn_unschedulable`. |
| Safeguard 4 — Rejection vocabulary | MET | Timing-budget and representability failures use `burn_unschedulable`. |
| Safeguard 5 — D1a and retained residual | MET | Both residual reproductions pass; execution/accounting discrepancy remains `−3.47e-18 kg`. New queued searches exercised 1,795 step-down candidates. |
| Safeguard 6 — Termination cause | MET | Required tests pass; regression probes preserve completed/depleted transitions. |
| Safeguard 7 — Boundary tests | MET | All 473 tests pass, including N1, both interval orderings, arithmetic extremes, threshold cases, and depletion. |
| N1 / F1 | RESOLVED | Original N1 bound is approximately `1.000000000500004e-7 m/s`, causing rejection. Cancellation and underflow reproductions also reject. |
| F2 / F3 | RESOLVED | Discriminating boundary tests remain passing; ADR removes the obsolete microsecond rule and separates floor correction from retained residual. |
| New arithmetic/queue searches | MET | Both interval orderings; 14,983 subnormal results, 4,357 overflowing results, 42,726 near-cancellation cases. Verified 3,101 queued acceptances and 2,611 atomic rejections. |
| Physically reasonable burns | MET | Zero rejections in 50,005 reference cases through `1e9 s`; maximum independent error `5.2872e-8 m/s`. Additional 10,000 ordinary-envelope probes: zero false rejections. |
| Earlier T1/T2 fixes | MET | Nonnegative effective mass, retained residuals, subsequent residual burns, rejection atomicity, and 16 byte-identical nondepletion comparisons pass. |
| M1 | MET | Proof PASS; 3,000 coast ticks bit-identical to archived M1. Determinism matches `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. |

For the modeled dynamics, `m(t)=dry+max(propellant−mdot·t,0)` is positive and nonincreasing. Therefore, over either timing-difference interval, `∫F/m(t) dt ≤ F·abs(dt)/m_end`. The clamp preserves this argument even where rounded depletion slightly exceeds exact depletion. The cutoff floor acts after integration; its roundoff correction is separate from the timing allocation. This bounds the modeled thrust integral, not RK4 error, cumulative mission error, or trajectory differences. The ADR correctly describes those limitations.

Evidence and rerunnable probes are under [`review_scratch/`](review_scratch/), particularly [`adversarial.txt`](review_scratch/adversarial.txt), [`search.txt`](review_scratch/search.txt), and [`regressions.txt`](review_scratch/regressions.txt).

### N2 — Source documentation retains an invalid exact logarithmic identity

**Severity:** Low

**Claim:** The module budget comment and `timing_delta_v_error_mps` docstring still identify `c·abs(log(m(D)/m(d)))` as exact universally. With subnormal rounded mass flow, the simulator’s coefficient is `F/mdot`, which can differ materially from `c`. The stated relative excess `x/2` is also only a small-`x` approximation.

**Evidence:** Valid `EngineSpec(8e-323, 1)` gives `F/mdot=8`, while `c≈9.80665`. With dry and propellant masses `1e-320 kg` and intervals `0.1/0.2 s`, the actual integral is `0.0003952862120032422 m/s`; the documented c-log expression gives `0.0004845541913676993 m/s`. The implemented bound remains conservative. See [`documentation.txt`](review_scratch/documentation.txt).

**Suggested fix:** Describe `∫F/m dt` as authoritative; qualify the logarithmic identity by unrounded mass-flow and unclamped-mass assumptions. Mark `x/2` as asymptotic. No algorithm change is needed.

**T2: CONDITIONAL PASS — numerical fixes verified; correct N2’s documentation to finish safeguard 2.** Ran required pytest (**473 passed**), ruff lint/format (**passed**), determinism and M1 proof (**passed**), repeated reproductions/searches, new adversarial and queued-burn probes, ordinary-mission scans, and regression comparisons. Writes were confined to `review_scratch/`; `src/` and `tests/` were untouched.