# Decision Request: M2 final acceptance thresholds (T7 threshold DR; DR-0015, FU-1)

**Status:** OPEN — awaiting the Tech Lead's decision  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-13  
**Related milestone/issue:** M2 T7. DR-0015 (threshold method), DR-0008 (M1 precedent), FU-1, DR-0021 (reference snapshot). Evidence: VAL-0016, `proof/records/evidence/M2-T7/`.

## Problem
`proof/thresholds/m2.json` is **provisional**. DR-0015 requires final values re-measured on the implemented code across three platforms, then approved in a dedicated threshold DR before any Proof claims them.

T7 measured the M2 Proof on the DR-0008 matrix (VAL-0016):
- the macOS x86_64 reference host;
- Linux x86_64: five GitHub runs on four CPU types, with and without AVX-512;
- macOS arm64: five GitHub runs.

That is 11 bundles in all, every one from a clean tree at `2870392` with identical input digests. The Proof passes 215/215 on all 11.

This DR proposes the final matrix and resolves FU-1. It also covers the O6 margin question and DR-0015's unmeasured "M2 cross-platform golden final state" row.

**Nothing has been changed:** no threshold, reference value, snapshot tolerance or check.

## How to read the matrix
- **Measured worst:** the worst value of the metric over every check that uses the limit (all missions, variants and auxiliary runs), over all 11 bundles.
- **Spread:** the largest cross-platform difference of any single check.
- **Error type:**
  - **TR:** simulator truncation, i.e. the RK4 integration error being measured.
  - **RO:** a round-off-class quantity.
  - **ORD:** a convergence-order policy.
  - **REF:** a reference-against-reference agreement, such as GMAT against DOP853 or Kepler. It is not a simulator error.
  - **AN:** an analytic or exact bound.
- **Margin:** limit divided by measured worst.

### Error budget behind every proposal (VAL-0016)
| Contribution | Size | Enters the verdict? |
|---|---|---|
| Simulator truncation (RK4, dt = 10 s) | 0.29–0.31 m at 53,700 s; ≤ 8e-3 m at burn boundaries | **Yes: this is what the gates measure** |
| Reference error (GMAT vs independent DOP853) | ≤ 4.7e-6 m | Yes, as measurement uncertainty |
| Reference platform drift (raw DOP853) | ≤ 8.1e-6 m | **No.** The snapshot removes it; verify-mode deviation ≤ 2.8e-9 m (DR-0021) |
| Simulator platform drift | ≤ 7.2e-6 m (final state); ≤ 1.1e-5 m (any metric) | Yes, as spread |
| Round-off class | ≤ 7.5e-14 relative | Yes |

The measurement uncertainty (≈ 1e-5 m) is more than four orders of magnitude below the simulator error and below every margin. Every margin is at least 1.5× (O8, a policy limit), and every truncation-type margin is at least 1.9×.

## Proposed final matrix
**Recommendation:** approve every current value unchanged, with the status changed from provisional to approved. Each rationale says why no change is proposed and what tightening or relaxing would do.

### O1–O3, O7, accounting (round-off class and exact bounds)
| Threshold | Provisional | Measured worst | Spread | Type | Proposed | Margin | Rationale and consequences |
|---|---|---|---|---|---|---|---|
| O1 propellant used, rel. to initial mass | 1e-12 | 2.2e-16 | 0 | RO | **1e-12** | 4,500× | DR-0015 round-off class; RK4 is exact for linear mass. Tightening below about 1e-14 would gate on the last few ulps, platform-fragile with no physical meaning. Relaxing would admit a real mass-law defect |
| O1 depletion residual / D1a bound | 1 | 0.305 | 0 | AN | **1** | 3.3× | Exact analytic DR-0017 D1a bound (ratio ≤ 1); not a tolerance |
| O2 sensed Δv excess over the Simpson bound, rel. | 1e-12 | 7.5e-14 | 0 | RO | **1e-12** | 13× | Round-off allowance on top of the computed RK4 truncation term (VAL-0013). Tighter than about 1e-13 falls inside the round-off of the high-thrust O6 variants |
| O2 reported rocket-equation Δv, rel. | 1e-12 | 6.7e-14 | 1.2e-16 | RO | **1e-12** | 15× | As above |
| O3 free-space velocity, rel. | 1e-12 | 1.8e-14 | 0 | RO | **1e-12** | 55× | Decimal closed form; round-off class (VAL-0011) |
| O3 free-space propellant, rel. | 1e-12 | 2.2e-16 | 0 | RO | **1e-12** | 4,700× | As above |
| O3 position order \|p − 4\| | 0.5 | 0.195 | 0 | ORD | **0.5** | 2.6× | DR-0008 order policy (approved for M1) |
| O3 timing violations | 0 | 0 | 0 | AN | **0** | — | Exact (review M2-T5 F5) |
| O7 plane rotation; inclination change (rad) | 1e-12 | 3.7e-16; 6.7e-16 | ≤ 3.3e-16 | RO | **1e-12** | ≥ 1,500× | Thrust along ±v stays in plane, so only round-off is expected |
| O7 sign violations | 0 | 0 | 0 | AN | **0** | — | Exact |
| Accounting: propellant, Δv, plan, transition, sample, thrust acceleration, direction, unit vector, Simpson excess (9 metrics) | 1e-12 | ≤ 2.9e-14 | ≤ 1.7e-16 | RO | **1e-12** | ≥ 34× | Bookkeeping identities at round-off |

### O4, O5, O9 simulator-vs-reference, orbit events (simulator truncation)
| Threshold | Provisional | Measured worst | Spread | Type | Proposed | Margin | Rationale and consequences |
|---|---|---|---|---|---|---|---|
| O4 final / sample position (m), 53,700 s | 0.6 | 0.313 | 1.1e-5 | TR | **0.6** | 1.9× | About 2× measured, and equal to the approved M1 limit for the same horizon and dt. Tightening to about 0.35 m would fail benign RK4 changes; relaxing would mask a burn defect of the same order as the RK4 error |
| O4 final / sample velocity (m/s) | 7e-4 | 3.6e-4 | 1.4e-8 | TR | **7e-4** | 1.9× | As above |
| O4 cutoff / ignition position, slice, retrograde, depletion (m) | 2e-3 | 8.2e-4 | 1.2e-9 | TR | **2e-3** | 2.5× | DR-0015 candidate (about 2× measured) |
| O4 cutoff / ignition velocity, same (m/s) | 3e-6 | 1.3e-6 | 2.1e-13 | TR | **3e-6** | 2.3× | As above |
| O4 cutoff / ignition position, invalid-commands (m) | 1.6e-2 | 8.0e-3 | 6.4e-9 | TR | **1.6e-2** | 2.0× | Last cutoff after a 2,420 s coast; the error is dominated by the pre-burn coast |
| O4 cutoff / ignition velocity, invalid-commands (m/s) | 2e-5 | 1.0e-5 | 9.4e-12 | TR | **2e-5** | 2.0× | As above |
| O4 thrust direction vs reference, slice etc.; invalid-commands | 4e-10; 2.6e-9 | 1.45e-10; 1.15e-9 | ≤ 1.2e-15 | TR | **4e-10; 2.6e-9** | 2.8×; 2.3× | The O4 velocity limit divided by orbital speed (not an independent tolerance) |
| O4 initial position and velocity, rel. | 1e-12 | ≤ 1.7e-16 | ≤ 1.7e-16 | RO | **1e-12** | ≥ 6,000× | Round-off class |
| O5 coast vs Kepler, position / velocity | 0.6 m / 7e-4 m/s | 0.314 m / 3.6e-4 m/s | 1.1e-5 / 1.4e-8 | TR | **0.6 / 7e-4** | 1.9× | Approved M1 Kepler limits; same horizon and dt |
| Orbit events: node-crossing time (s) | 8e-5 | 4.0e-5 | 1.5e-9 | TR | **8e-5** | 2.0× | About 2× measured; equals the approved M1 node limit |
| Orbit events: min / max altitude error (m) | 0.013 | 6.3e-3 / 4.3e-3 | ≤ 2.4e-7 | TR | **0.013** | 2.1× / 3.0× | About 2× measured |
| O9 ours vs GMAT: sample / final position (m) | 0.6 | 0.313 | 7.2e-6 | TR | **0.6** | 1.9× | Equal to O4; the difference is our RK4 error, since ours-vs-GMAT equals ours-vs-DOP853 |
| O9 ours vs GMAT: sample / final velocity (m/s) | 7e-4 | 3.6e-4 | 8.4e-9 | TR | **7e-4** | 1.9× | As above |
| O9 ours vs GMAT: burn boundaries, position / velocity | 2e-3 m / 3e-6 m/s (invalid-commands 1.6e-2 / 2e-5) | 7.8e-4 / 1.24e-6 (8.0e-3 / 1.0e-5) | ≤ 9.4e-12 | TR | **unchanged** | ≥ 2.0× | Equal to the O4 boundary limits |
| O9 ours vs GMAT: node crossing (s) | 8e-5 | 4.0e-5 | 7.9e-10 | TR | **8e-5** | 2.0× | As for orbit events |
| O9 ours vs GMAT: mass (kg) | 1.3e-9 | 2.3e-11 | 0 | RO | **1.3e-9** | 58× | O1 round-off class (1e-12 × 1,300 kg) |

### O6 and O8 (orders and ratios)
| Threshold | Provisional | Measured worst | Spread | Type | Proposed | Margin | Rationale and consequences |
|---|---|---|---|---|---|---|---|
| O6 impulsive-limit order \|p − 2\| | 0.05 | 0.0041 | 3.8e-7 | ORD | **0.05** | 12× | DR-0015 candidate (10× the measured deviation). See "O6" below for the snapshot margin |
| O6 slice ΔSMA ratio deviation | 1e-5 | 2.6e-6 | 3.7e-14 | TR | **1e-5** | 3.9× | Physical finite-burn effect, scenario-specific (DR-0015) |
| O8 RK4 order \|p − 4\| (dt 10 → 5 → 2.5) | 0.5 | 0.33 | 1e-3 | ORD | **0.5** | 1.5× | Approved DR-0008 policy. The orders are 4.14–4.33: pre-asymptotic at dt = 10 s, as in M1. Tightening below about 0.35 would fail the approved policy's own pre-asymptotic behaviour |

### O9 GMAT gates (FU-1)
| Threshold | Provisional | Measured worst | Spread | Type | Proposed | Margin | Rationale and consequences |
|---|---|---|---|---|---|---|---|
| GMAT vs DOP853, position max / final (m) | 3e-5 | 4.66e-6 | **0** | REF | **3e-5** | 6.4× | See FU-1 below |
| GMAT vs DOP853, velocity (m/s) | 3.5e-8 | 5.39e-9 | **0** | REF | **3.5e-8** | 6.5× | Scaled by the measured velocity/position ratio |
| GMAT coast rows vs Kepler (m; m/s) | 1e-4; 1e-7 | 4.0e-6; 4.6e-9 | 0 | REF | **1e-4; 1e-7** | 25×; 22× | Approved M1 GMAT-vs-Kepler limits (DR-0009). Tightening would add a gate not approved for M1 |
| GMAT mass vs analytic (kg) | 1.3e-9 | 2.3e-11 | 0 | RO | **1.3e-9** | 58× | O1 round-off class |
| Step spacing from the GMAT epoch (s) | 1e-6 | 2.3e-7 | 0 | AN | **1e-6** | 4.3× | Epoch resolution (2 ulp of A.1 MJD); an unaligned step would differ by seconds |
| Burn duration from GMAT mass (s) | 1e-9 | 1.4e-10 | 0 | AN | **1e-9** | 7.1× | About 2× the VAL-0010 maximum (6e-10 s) |

### Not in `m2.json`, recorded for completeness
- The **DR-0021 reproducibility tolerances** are verification tolerances, not physics thresholds, and are already approved under DR-0021 condition 4. T7's 11 bundles, including the non-AVX-512 host, confirm the measured maxima are unchanged: verify-mode 2.8e-9, 2.0e-7 and 5.4e-7 m by class. **No change.**
- **Exact contract checks** (event order, traceability, outcomes, determinism, DR-0018 boundary, snapshot) are not tolerances. **No change.**

## FU-1 — the GMAT gates and the DOP853 platform floor
**Finding.** FU-1 required "no gate tighter than [the 11–15 µm DOP853 cross-platform floor] unless the reference is made platform-robust". T7 shows:
- The raw DOP853 reference still drifts by **8.1e-6 m** between platforms (record mode). That is the floor, re-measured.
- Since DR-0021, **the Proof never consumes the raw reference.** It consumes the approved snapshot values, once the runtime agrees within 5e-8 m. As a result, every O9 GMAT-vs-reference metric has **exactly zero cross-platform spread** on all 11 bundles. For the verdict, the reference is platform-robust.
- The measured 4.66e-6 m is a real, platform-independent difference between two independent references, GMAT's integrator and DOP853. It is not noise.

**Options.**
- **(a) Keep 3e-5 m / 3.5e-8 m/s (recommended).** That is about 2× the worst plausible value if the snapshot were ever re-baselined on another host: 4.66 µm plus 8.1 µm of reference drift ≈ 12.8 µm, doubled ≈ 2.6e-5 m, rounded to 3e-5. The O9 gate then does not depend on which host generated the baseline, and still catches any GMAT or reference change above about 25 µm, roughly 0.01 % of the 0.31 m simulator error.
- **(b) Tighten to 1e-5 m / 1.2e-8 m/s** (about 2× measured, permitted because the reference is now platform-robust).
  - It detects GMAT or reference changes above about 5 µm.
  - It couples the gate to the snapshot host: a future baseline generated on a non-reference host could fail at about 12.8 µm without any physical change.
- **(c) Relax.** Not recommended: there is no measured need, and it would hide GMAT configuration errors.

**Recommendation: (a)**, and close FU-1 as resolved. The floor is accounted for, the gate stays above it, and the snapshot makes the verdict platform-independent.

## O6 — the 0.0405 snapshot margin bound
**Finding.**
- The 0.0405 figure is not a measured error. It is DR-0021's worst-case bound: the most the O6 metric could move if each impulsive SMA shifted by the whole simulator-seeded length tolerance (1e-5 m).
- O6 is very sensitive to that shift. It is an order computed from finite-minus-impulsive SMA differences that shrink to 0.5 mm at the finest level, so a shift δ moves the order by about δ(1/d₃ + 1/d₄)/ln 2.
- The 1e-5 m class tolerance is sized for O5's long Kepler arcs (5.4e-7 m measured).
- The impulsive SMA's own cross-platform variation is **1.86e-9 m**, about 5,000× smaller.

**Effect on the decision.**
- With the limit at 0.05 (proposed unchanged), the margin check passes: 0.0041 + 0.0366 = 0.0405 < 0.05.
- The bound only matters if the O6 limit is tightened below about 0.041.
- The measured O6 cross-platform spread is 3.8e-7.

**Options.**
- **(a) No change (recommended for this DR).** The 0.05 limit is the DR-0015 candidate and passes with its margin bound.
- **(b) A dedicated O6 impulsive-SMA reproducibility class, approved separately.** Apply the DR-0021 rule (the 1-2-5 step at or above max(10 × 1.86e-9, 10 ulp of 6.8e6 m)), giving **2e-8 m**. The O6 margin bound becomes 0.0041 + 0.00007 ≈ 0.0042.
  - It needs a snapshot schema change (a distinct unit or class for the SMA part), so it means **a new baseline (baseline 4)** with independent verification and its own approval under DR-0021 condition 3.
  - It is justified on measurement grounds, but it is not needed unless the O6 limit is tightened.

**Recommendation: (a)** now. Adopt (b) only together with any future tightening of the O6 limit.

## DR-0015's open row — M2 cross-platform golden final state
**Measured:**
- M2 final states differ across platforms by at most **7.2e-6 m and 8.4e-9 m/s** (prograde slice).
- The M1 equivalent is 2.9e-6 m and 3.4e-9 m/s.
- The burn amplifies drift by about 2.5×, as DR-0015 anticipated.

**Proposal:** a new cross-platform gate for every M2 mission's final state, at the **approved M1 bounds: 1e-4 m and 1e-7 m/s**. That gives a 14× and 12× margin, and it carries the M1 precedent (DR-0008) over without assuming transfer: the 2.5× burn amplification is measured.

Implementing it means a new validator, committed golden M2 final states from the reference host, and a CI step. That is new verification scope, so it is **proposed for approval, not implemented.**

**Options:**
- **(a)** Approve the bounds and authorize the implementation, either in T7 before the final review or in T8.
- **(b)** Approve the bounds only, and implement in T8.
- **(c)** Do not add the gate, relying on the 215 checks passing on all three platforms.

**Recommendation: (a)**, as a small implementation task before T8.

## Decisions requested
1. **Approve the matrix**: every current `m2.json` value unchanged, status changed to approved. Applying it is a reviewed change of `m2.json` with its digest updated in the same commit (DR-0020 condition 5).
2. **FU-1:** option (a), keep the O9 GMAT gates and close FU-1.
3. **O6:** option (a), no change; a dedicated SMA class only with a future O6 tightening.
4. **M2 cross-platform final state:** option (a), bounds 1e-4 m / 1e-7 m/s, implementation authorized.

## Impact
- **Science and validation:** no threshold value changes. M2 thresholds become approved, which T8 requires.
- **Architecture:** none under the recommendations, apart from the proposed cross-platform validator in item 4.
- **Reversibility:** high. Any later change goes through a reviewed `m2.json` change with its digest.

## Blocked work
- Applying approved values (`m2.json` status, digest).
- The cross-platform final-state gate.
- T8.

## Requested response
Items 1–4: approve, amend or `discuss`.
