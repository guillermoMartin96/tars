# Decision Request: M1 timestep and Proof tolerances (from measured convergence data)

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit; follow-up to DR-0004 and DR-0006

## Problem
DR-0004 approved fixed-step RK4 with dt = 10 s as a candidate. The final dt and Proof tolerances were to come from measured convergence data. DR-0006 requires a measured cross-platform tolerance. The data now exists; Proof cannot PASS until the thresholds are approved.

## Evidence
All measurements are deterministic, against the exact Kepler solution, for the M1 scenario: 10 orbits, 53 700 s, revision `6800d8b`+. Run `toolbox/validators/m1_proof.py`.

**Convergence study (position and energy error at t = 53 700 s)**

| dt [s] | steps | position error [m] | \|ΔE/E\| | pairwise order |
|---|---|---|---|---|
| 60 | 895 | 1 161.2 | 3.0e-6 | — |
| 30 | 1 790 | 43.52 | 9.3e-8 | 4.74 |
| 20 | 2 685 | 6.685 | 1.2e-8 | 4.62 |
| **10** | **5 370** | **0.2983** | **3.8e-10** | 4.49 |
| 5 | 10 740 | 0.01491 | 1.2e-11 | 4.32 |
| 2.5 | 21 480 | 8.224e-4 | 4.0e-13 | 4.18 |
| 1 | 53 700 | 1.523e-5 | 1.0e-14 | 4.35 |

- Fitted order over {20, 10, 5, 2.5} s: **4.33**.
- The pairwise orders fall toward 4 as dt shrinks: 4.49 → 4.32 → 4.18. That is the expected pre-asymptotic effect of the next error term (C₅·dt⁵), not a defect.
- Round-off has not yet become visible at dt = 1 s.

**Full M1 run at dt = 10 s (identical on all three platforms to the digits shown)**

| Metric | Measured |
|---|---|
| Max position error vs Kepler | 0.2983 m (purely along-track phase lag) |
| Max velocity error vs Kepler | 3.49e-4 m/s |
| Energy relative drift | 3.83e-10 |
| Angular-momentum relative drift | 1.91e-10 |
| Eccentricity-vector drift | 5.86e-10 |
| SMA drift | 2.54 mm |
| Max per-orbit period error (node-to-node) | 5.23e-6 s |
| Max cumulative node-crossing time error | 3.85e-5 s |

Two cross-checks:
- 3.85e-5 s × 7 754.8 m/s = 0.298 m. The timing error fully explains the position error.
- The minimum altitude dips 6 mm below 250 km, consistent with the SMA drift.

**Cross-platform agreement (DR-0006)**, final state after 10 orbits, relative to local macOS x86_64:

| Platform | Event-log sha256 | \|Δr\| | \|Δv\| |
|---|---|---|---|
| CI ubuntu-latest x86_64 | differs | 2.9e-6 m | 3.4e-9 m/s |
| CI macos-latest arm64 | differs | 8.8e-7 m | 1.0e-9 m/s |

Same-platform repeat runs, both in-process and in separate processes, are byte-identical on all three platforms.

## Constraints
- Tolerances must be justified, not chosen to make tests pass (playbook/testing.md).
- They must detect real regressions (a wrong coefficient, force, or constant) without failing on benign floating-point differences.

## Options
### A — dt = 10 s; thresholds ≈ 2× measured (tight regression gate)
| Validator.metric | Threshold | Measured |
|---|---|---|
| kepler_reference.position_error_max_m | 0.6 | 0.298 |
| kepler_reference.velocity_error_max_mps | 7e-4 | 3.49e-4 |
| invariants.energy_rel_drift_max | 1e-9 | 3.8e-10 |
| invariants.angular_momentum_rel_drift_max | 5e-10 | 1.9e-10 |
| invariants.eccentricity_vector_drift_max | 1.2e-9 | 5.9e-10 |
| invariants.sma_drift_max_m | 0.006 | 0.0025 |
| period.period_error_max_s | 1e-5 | 5.2e-6 |
| period.node_crossing_time_error_max_s | 8e-5 | 3.85e-5 |
| convergence.order_deviation_from_4 | 0.5 | 0.33 |
| cross-platform final \|Δr\| / \|Δv\| | 1e-4 m / 1e-7 m/s | 2.9e-6 m / 3.4e-9 m/s |
| gmat_reference.position_error_max_m | 0.6 *(pending GMAT run; valid only if GMAT-vs-Kepler ≪ 0.3 m)* | — |

**Pros**
- A 2× margin is about 10⁵ times the observed platform spread, so benign changes pass.
- Any real defect moves errors by orders of magnitude and is caught.
  - A wrong RK coefficient drops the order to 1–3.
  - A μ mismatch at GMAT's default value adds about 0.16 m along-track; that alone does not breach 0.6 m, but the initial-SMA check catches it.

**Cons**
- Changing dt, the integrator, or the scenario requires re-measuring and re-approving thresholds. That is intended.

### B — dt = 10 s; loose round-number thresholds (for example 1 m, 1e-8)
**Pros**
- Fewer re-approvals.

**Cons**
- Weaker regression detection, for example missing a 3× error growth.
- The values are not tied to measurements.

### C — dt = 5 s (1.5 cm error) with option-A-style thresholds
**Pros**
- 20× more accurate.

**Cons**
- Twice the compute, for no scientific benefit in M1. The model error (J2: hundreds of km over 10 orbits, SCI-0001) dwarfs both 0.3 m and 1.5 cm.

## Recommendation
**A.**
- dt = 10 s gives a numerical error of 0.3 m over about 417 000 km travelled (7×10⁻¹⁰ relative). That is roughly six orders of magnitude below the deliberate model simplifications, at 537 steps per orbit.
- Tight thresholds turn the M1 Proof into a sensitive regression detector for every later milestone.
- Revisit dt when precision operations (rendezvous, finite burns) or higher-fidelity forces arrive.

## Impact
- Architecture: none.
- Science/validation: thresholds are versioned in `proof/thresholds/m1.json`, marked `approved` with your name and date.
- Dependencies: none.
- Development effort: trivial.
- Token/compute impact: none.
- Reversibility: high (versioned file).

## Blocked work
- Final M1 Proof PASS.
- The GMAT threshold also needs the GMAT run.

## Work continuing independently
- GMAT installation and run.
- External review preparation.

## Requested response
`A` / `B` / `C` / `discuss` (plus any threshold you want changed)

## Resolution
**Decision:** APPROVED — Option A (Tech Lead, 2026-10-05).  
**Reasoning/notes:**
- Timestep dt = 10 s.
- Position-error threshold 0.6 m; energy-drift threshold 1e-9; cross-platform bound 1e-4 m.
- All other option-A thresholds apply as listed above, including the cross-platform velocity bound of 1e-7 m/s.

**Follow-up:**
- `proof/thresholds/m1.json` set to `approved`.
- `toolbox/validators/cross_platform.py` checks against the golden state in `proof/references/m1_final_state.json` (reference platform macOS x86_64) and runs in CI on Linux x86_64 and macOS arm64.
