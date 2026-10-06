# Proof Record — Milestone 1: Orbit

**Result:** `BLOCKED`. Awaiting DR-0008 (tolerance approval), the GMAT reference run (DR-0005 install), and the external review.  
**Branch:** `milestone-1-orbit`  
**Definition of done:** prototype phase (proof/definition-of-done.md).  
**Scenario:** `scenarios/m1_leo_250km.json` (sha256 config hash `603152ad…`): circular 250 km, i = 51.6°, point-mass Earth, WGS 84, RK4 dt = 10 s, 10 orbits.

## Commands
```bash
uv sync --locked
uv run ruff check . && uv run ruff format --check .
uv run pytest                                    # unit, integration, mission-level, validator tests
uv run python toolbox/validators/determinism.py  # cross-process byte-identical replay
uv run python toolbox/validators/m1_proof.py     # all non-GMAT Proof metrics -> runs/proof/*.json
uv run python toolbox/scripts/gmat_m1.py compare # after the GMAT reference is committed
```
CI runs everything except GMAT on ubuntu-latest and macos-latest (`.github/workflows/ci.yml`).

## Standard gate (proof/PROOF.md)
| Check | Status | Evidence |
|---|---|---|
| Unit tests pass | ✅ | 92 tests; CI green on Linux x86_64 and macOS arm64 |
| Integration tests pass | ✅ | `tests/test_simulator.py`, `tests/test_mission_m1.py` |
| Physics validation passes or discrepancies accepted | ⏳ | Kepler oracle ✅ (provisional thresholds); GMAT pending |
| Mission-level simulation passes | ✅ | 10 `OrbitCompleted` events then `SimulationCompleted(success)`. Impact, escape and timeout failure paths are tested. |
| Seed/replay checks | ✅ | M1 has no stochastic behaviour; the seed is recorded; byte-identical replay on each platform |
| Architecture invariants | ✅ | `tars.validation.architecture` scan: 0 violations; no public state setters (test) |
| Machine-readable events validate | ✅ | Pydantic JSONL schemas with round-trip and rejection tests |
| Scientific assumptions recorded | ✅ | SCI-0001…0007 |
| Engineering decisions recorded | ✅ | DR-0001…0007 (resolved), DR-0008 (open), ADR-0001…0006 |
| External review completed | ⏳ | Not started; scheduled after the GMAT comparison |
| Every finding dispositioned / no Critical-High open | ⏳ | — |
| No secrets/debug artifacts | ✅ | `runs/` is git-ignored; no credentials |
| Branch pushed, revision identified | ✅ | `milestone-1-orbit` |

## Physics Proof (proof/physics.md, M1 scaffold)
| Requirement | Status | Evidence |
|---|---|---|
| Stable propagation for 10 orbits | ✅ (provisional) | Energy drift 3.8e-10, SMA drift 2.5 mm, no non-finite values; altitude 249 999.994–250 000.000 m |
| Measured period error vs a trusted reference | ✅ (analytic) / ⏳ (GMAT) | Max per-orbit period error 5.2e-6 s against the analytic T = 5 370.296 s |
| Measured state drift appropriate to integrator | ✅ | 0.298 m after 10 orbits; convergence order 4.33 (DR-0008 table) |
| Documented explanation of GMAT discrepancy | ⏳ | Comparator ready; awaiting the GMAT run |
| No unexplained numerical instability | ✅ | All errors explained (along-track phase lag; pre-asymptotic order) |
| Tolerances explicit and justified | ⏳ | Proposed in DR-0008 from measured data |
| Reference configuration recorded | ✅ / ⏳ | `toolbox/references/gmat/` script and README; metadata written on the run |

## Discrepancies
| ID | Description | Classification | Status |
|---|---|---|---|
| M1-D1 | Event-log hashes differ across platforms; final state differs ≤ 2.9 µm | Numerical (floating-point, platform) | Expected under DR-0006; bound proposed in DR-0008 |
| M1-D2 | Fitted RK4 order 4.33 rather than 4.0 | Numerical (pre-asymptotic higher-order term) | Explained; order falls toward 4 as dt decreases |

## Known limitations allowed at the prototype bar
- The model is deliberately unrealistic for a real 250 km spacecraft: no J2 (about −5.4°/day node regression) and no drag (SCI-0001, SCI-0004). M1 proves numerical fidelity to the chosen model, not real-world prediction.
