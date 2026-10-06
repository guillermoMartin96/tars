# Proof Record — Milestone 1: Orbit

**Result:** `BLOCKED`. Every executable Proof check passes, but external-review finding **REV-001 (High)** is unresolved until Tech Lead decision **DR-0009** (GMAT reference gates). proof/review.md and proof/PROOF.md do not allow PASS while a High finding is open.  
**Proven revision:** `dfe4615` (branch `milestone-1-orbit`). Evidence was generated from a clean working tree.  
**Evidence:** `proof/records/evidence/M1/` contains `proof_run.log`, `m1_non_gmat.json`, `gmat_reference.json`, `cross_platform.json` and `mission_summary.json`.  
**Reproduce:** `toolbox/scripts/run_m1_proof.sh` (set `UV=` if uv is not on PATH).  
**Definition of done:** prototype phase (proof/definition-of-done.md).  
**Scenario:** `scenarios/m1_leo_250km.json` (config hash `603152ad…`): circular 250 km, i = 51.6°, epoch 2026-01-01 TT, point-mass Earth, WGS 84, RK4 dt = 10 s, 10 orbits.  
**Thresholds:** `proof/thresholds/m1.json`, **approved** (DR-0008 option A, 2026-10-05).

## Standard gate (proof/PROOF.md)
| Check | Status | Evidence |
|---|---|---|
| Unit tests pass | ✅ | 109 tests (`proof_run.log`); CI green on ubuntu-latest x86_64 and macos-latest arm64 |
| Integration tests pass | ✅ | `tests/test_simulator.py`, `tests/test_mission_m1.py`, `tests/test_cli.py` |
| Physics validation passes or discrepancies accepted | ✅ | Kepler oracle and GMAT R2026a both PASS (VAL-0002, VAL-0004) |
| Mission-level simulation passes | ✅ | 10 `OrbitCompleted` events, then `SimulationCompleted(success)`. Impact, escape, timeout and non-finite paths are tested. |
| Seed/replay checks | ✅ | No stochastic behaviour; the seed is recorded. Byte-identical replay in-process and cross-process. |
| Architecture invariants | ✅ | Scan: 0 violations (relative imports and alias attributes included). State is read-only to force models (REV-004). No public setters. |
| Machine-readable events validate | ✅ | Pydantic JSONL schemas; round-trip and rejection tests |
| Scientific assumptions recorded | ✅ | SCI-0001…0007 (SCI-0005 corrected per REV-001) |
| Engineering decisions recorded | ✅ | DR-0001…0008 resolved; DR-0009 open; ADR-0001…0006 |
| External review completed | ✅ | `docs/reviews/M1-orbit-review-01.md` |
| Every substantive finding dispositioned | ✅ | REV-001…012 |
| No unresolved Critical/High findings | ❌ | **REV-001 open, pending DR-0009** |
| No secrets/debug artifacts | ✅ | `runs/` is git-ignored; evidence is intentional |
| Branch pushed, revision identified | ✅ | `dfe4615` |

## Physics Proof (proof/physics.md, M1 scaffold)
| Requirement | Result vs approved threshold |
|---|---|
| Stable propagation for 10 orbits | Energy drift 3.83e-10 (≤ 1e-9). h drift 1.91e-10 (≤ 5e-10). e-vector drift 5.86e-10 (≤ 1.2e-9). SMA drift 2.5 mm (≤ 6 mm). Altitude stays within 249 999.994–250 000.000 m. |
| Period error vs trusted reference | Analytic T = 5 370.296 s. Max per-orbit error 5.23e-6 s (≤ 1e-5). Cumulative node timing 3.85e-5 s (≤ 8e-5). GMAT period difference 9e-13 s. |
| State drift appropriate to integrator | Position 0.298 m (≤ 0.6) and velocity 3.49e-4 m/s (≤ 7e-4) vs exact Kepler. Convergence order 4.33 (deviation ≤ 0.5). |
| GMAT discrepancy documented | Ours vs GMAT is 0.298 m (≤ 0.6). It equals our RK4 error, while GMAT vs Kepler is 7.2 µm, so it is classified as numerical (VAL-0004). |
| Cross-platform agreement (DR-0006) | Final state ≤ 8.8e-7 m and 1.0e-9 m/s on CI platforms (≤ 1e-4 m, 1e-7 m/s). A 2.9e-6 m case was seen earlier (VAL-0005). |
| No unexplained numerical instability | All errors explained: along-track phase lag; pre-asymptotic order; ulp-level platform differences. |
| Reference configuration recorded | `toolbox/references/gmat/` (script, report, metadata with command, build, hashes, host and revision; install provenance) |

## Discrepancies
| ID | Description | Classification | Status |
|---|---|---|---|
| M1-D1 | Event-log hashes differ across platforms; final state ≤ 2.9 µm | Numerical (platform floating point, 1-ulp initial-state difference) | Accepted (DR-0006/0008) |
| M1-D2 | Fitted RK4 order 4.33 | Numerical (pre-asymptotic) | Accepted (DR-0008) |
| M1-D3 | Ours vs GMAT 0.298 m | Numerical (our RK4 truncation; GMAT exact to 7 µm) | Accepted (VAL-0004) |
| M1-D4 | Same CI label gives different last bits across runs | Numerical (runner CPU variability) | Accepted (VAL-0005) |
| M1-D5 | GMAT epoch column drifts −1.07e-4 s from ElapsedS | Reference tool bookkeeping (hypothesis); no effect on states | Documented (REV-012) |

## Known limitations allowed at the prototype bar
- The model is deliberately unrealistic for a real 250 km spacecraft: no J2 (about −5.4°/day node regression) and no drag (SCI-0001, SCI-0004). M1 proves numerical fidelity to the chosen model, not real-world prediction.
- Orbit counting by ascending node excludes equatorial orbits (REV-007).

## To reach PASS
1. Tech Lead decides DR-0009.
2. Apply the approved GMAT gates in `proof/thresholds/m1.json` (and the CI compare step, if approved).
3. Re-run `run_m1_proof.sh` and close REV-001.
