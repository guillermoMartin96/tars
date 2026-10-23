# M3 T1 — Report (J2 force model)

**Status: T1 IMPLEMENTED. NOT REVIEWED, NOT ACCEPTED, NOT MERGED.**  
**Authority:** "I-17 — Merge P10 Decision and Authorize M3 T1 J2 Force Model" (Tech Lead, 2026-10-22). T1 only.

## 1. P10 merge (I-17 §1–§2)
- CI on `60648b9` (head of `m3-p10-decision-packet`) was green before the merge.
- `main` was fast-forwarded from `5fded7c` to **`60648b93385a9954194730006aeac29ea14875ad`**. It was an ordinary push (`5fded7c..60648b9`), with no merge commit, squash or rebase.
- The decision branch `m3-p10-decision-packet` is kept.

## 2. Branch and commits
Branch `milestone-3-t1-j2-force-model`, created from `main` = `60648b9`.

| Commit | Content |
|---|---|
| `5fd24a2` | Tests first (red): `tests/test_constants.py` (extended), `tests/test_zonal_j2.py` (new) |
| `e23675c` | `src/tars/sim/constants.py` and `src/tars/sim/forces.py`, additive |
| `81a0d56` | VAL-0020, SCI-0013 status update 4, `docs/science/experiments/m3-t1/` (informational and mutation evidence) |
| this commit | This report; append-only status notes in the T1 packet and the planning decision matrix |

## 3. Implementation
- **Constants** (`src/tars/sim/constants.py`, additive):
  - `EGM2008_C20_TIDE_FREE = -0.484165143790815e-3` is the only authoritative literal.
  - `j2_from_c20(c20) = -math.sqrt(5.0) * c20`.
  - `EarthJ2Constants` (frozen, validated: name, μ, a, C̄2,0) has a derived `j2` property and no J2 field.
  - `WGS84_EGM2008_TIDE_FREE` reuses `WGS84.mu` and `WGS84.equatorial_radius`. `WGS84` and `EARTH_J2_APPROX` are unchanged.
- **Force** (`src/tars/sim/forces.py`, additive):
  - `ZonalJ2Gravity(mu, equatorial_radius, j2)` uses the name `zonal_j2` and version 1.
  - It implements the existing `acceleration(t, r, v)` protocol.
  - The axis is the frame +Z axis. It is not a parameter, and there is no Earth orientation (DR-0028 J-ax-1).
  - It is pure, holds no state and needs no mass.
  - Formula: a = k (x(1 − 5s²), y(1 − 5s²), z(3 − 5s²)), with k = −(3/2) J2 μ a² / r⁵ and s² = z²/r².
- **Not wired anywhere:** no scenario, simulator, runner or schema uses it.

## 4. Constant representations (exact)
| Representation | Value |
|---|---|
| Canonical C̄2,0 (source literal) | `-0.484165143790815e-3`; shortest repr `-0.000484165143790815` |
| Derived J2 (binary64) | `1.0826261738522227e-3` = `0x1.1bcdd00abd9aap-10` |
| Display form (DR-0029 Q1 decimal) | `1.0826261739e-03` (`f"{J2:.10e}"`); not equal to J2; relative gap 4.41e-11 (220 334 ulps) |
| Derivation | `-math.sqrt(5.0) * C20`: one correctly rounded `sqrt`, one correctly rounded product |

## 5. Cross-platform bit identity (I-17 §11)
- **Result: IDENTICAL on all three required platforms.**
- CI run **39852509134** on `e23675c` passed `tests/test_constants.py` (12 tests) and `tests/test_zonal_j2.py` (14 cases) on each platform. The suite totals were 1204 passed, 3 skipped:

  | Job | Platform | ID | Result |
  |---|---|---|---|
  | `check (ubuntu-latest)` | Ubuntu | 120082120957 | success |
  | `check (macos-latest)` | macOS, arm64 | 120082120734 | success |
  | `check (macos-15-intel)` | macOS, Intel | 120082120540 | success |

- **What the evidence shows:**
  - `test_j2_binary64_value_is_the_p10_recorded_value` asserts `J2.hex() == "0x1.1bcdd00abd9aap-10"`, and `test_j2_derivation_is_correctly_rounded_binary64` checks correct rounding with exact rationals.
  - Both passed on each platform, so the derived value is bit-identical across platforms.
- **Scope:** this is an observation about these CI platforms for this constant. It does **not** adopt DR-0025 Q-G2-2 (identity-check rule), which stays PROPOSED.

## 6. Tests and validation
| Check | Result |
|---|---|
| New tests | 8 new constant tests (12 in `test_constants.py`) and 12 J2 test functions (14 cases with parametrization) in `test_zonal_j2.py` |
| pytest, full suite (local, reference host) | 1207 passed |
| pytest in CI, 3 platforms (`e23675c`) | 1204 passed, 3 skipped, on each |
| ruff check / format | clean |
| Mutation check | 14/14 mutants detected; control passes |
| T0 checks (`docs/science/experiments/m3-t0/check_review0*.py`) | 314 passed |
| CI on `81a0d56` (run 39853032093) | success on all four jobs |

Gates and informational results are kept separate in VAL-0020.
- **Gates:**
  - constant identity;
  - known answers (2γ₁₆);
  - gradient against a separately coded potential (γ₆₄ bound; largest error 3.6 % of the bound);
  - exact axisymmetry and z-reflection;
  - radial sign;
  - J2 = 0 exactly zero, and bitwise point mass (single evaluations and 600 RK4 steps);
  - polar-plane exact invariance (5 370 steps);
  - the invariant-drift structural test, ratio drift(dt 5)/drift(dt 20) ≤ 1/2. The boundary was fixed before measuring. Measured ≈ 1.2e-3 (energy) and ≈ 9.8e-4 (h_z).
- **Non-gating:** secular rates, drift orders, RK4 convergence (§7).

## 7. Drift predictions vs measured (INFORMATIONAL, not gates)
- Orbit 300 × 1000 km, RK4 dt 10 s, 30 orbits. Theory is first-order secular J2, compared with osculating elements.
- Node rate Ω̇: within −0.27 % … +0.26 % of theory at every inclination tested (28.5°–150°). Regression for i < 90°, advance for i > 90°.
- Perigee rate ω̇: within ≤ 1 % of theory, except at the critical inclination 63.4349°, where it measured 0.011 °/day against a first-order ≈ 0. The sign changes where 5 cos² i − 1 predicts.
- **No tolerance exists** for this comparison, and none was set (I-17 §8). Deriving one, for example by mean-element conversion or a second-order theory, is an open item for the owner (§9).
- Invariant drift falls about as dt⁵ (orders 4.7–5.0), faster than the O(dt⁴) bound. Observed, not explained.
- RK4 convergence on J2: observed orders 4.68 and 4.52 (pre-asymptotic). Estimated RK4 position error at dt 10 s over 58 640 s: 0.22 m.
- Full tables are in VAL-0020 and `docs/science/experiments/m3-t1/t1_j2_informational_results.json`.

## 8. M1/M2 regression (VO-5)
| Check at `81a0d56` (fresh clone, reference host) | Result |
|---|---|
| M1 Proof (`run_m1_proof.sh`) | PASS (9/9), working tree clean |
| M2 Proof (`run_m2_proof.sh`, run alone from a clean tree) | PASS (20/20 steps), working tree clean; pytest 1207 passed; m2_proof 228/228; M1 golden `7a4e1877…` matched |
| Protected paths since `60648b9` | unchanged: `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`, `src/tars/validation/`, simulator, runner, scenario, events, contracts |
| `src/` diff | additive only (constants.py +58 lines, forces.py +39 lines; 0 lines deleted) |
| CI (`e23675c`), all four jobs incl. `m2-cross-platform` | success |

- The M1/M2 Proofs gate the M1 golden, the pinned digests and the reference outputs. Their passing means the protected outputs are byte-identical.
- The proof scripts' evidence was written in the scratch clone and discarded. No evidence file in this branch changed.

## 9. Unresolved assumptions and open items (for the owner)
1. **Secular-rate tolerance:** none exists. The Q1 comparison is reported only. Promoting it to a gate needs a derived tolerance (for example a mean-element or second-order error estimate), which T1 did not invent.
2. **Operation counts** behind the γ₁₆/γ₆₄ bounds are by inspection, not mechanically verified.
3. **IEEE 754:** correct rounding of the basic operations is assumed. It is checked per platform for `sqrt` and the constant product only.
4. **Gradient method:** forward-mode dual numbers stand in for the complex step named in DR-0025 Q3. The idea is the same, but the dual-number method needs no libm assumption. The owner may want to confirm this substitution.
5. **Axis representation:** the fixed +Z axis has no configuration representation. Its pinning in `PhysicsConfiguration` is T3 scope.
6. **dt⁵ invariant drift:** observed, not explained.
7. **External comparison:** T1 includes no GMAT or DOP853 comparison (T4/T5).
8. **Q-G2-2:** stays PROPOSED. T1's identity tests and the cross-platform result do not adopt it.

## 10. CI on the T1 head
- `81a0d56`: CI run 39853032093, success on `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform`.
- The commit that adds this report is docs only. Its CI result is reported with the final status (I-17 §14), not in this file.
- *Note on the first M2 run:* it ran in the same clone straight after the M1 Proof, which had rewritten tracked M1 evidence. It reported `working_tree_clean_excluding_evidence: no` (overall PASS). It was rerun alone from a clean checkout, with the result in §8.

## 11. Excluded work: not done (I-17 §10)
None of the following was done:
- drag or atmosphere; T2; a mass-carrying or `ForceContext` interface;
- scenario v3; runner integration; physics-identity record;
- M3 Proof; T4 validators; T5 GMAT generation;
- Earth orientation or configurable axes.

Nothing else changed either:
- no change to the lock file, dependencies, workflows or branch protection;
- no resolution of DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b) or the final time step (Q-G2-4 stays PROVISIONAL);
- no Codex or other independent review was started;
- T1 was not merged, and T2 was not started.

## 12. Next gate
Independent T1 review (Codex), which needs separate owner authorization (packet §11).

## Status update (recorded 2026-10-23 UTC, append-only)
- **Independent Codex Review 01** was run under "Authorization I-18 — M3 T1 Independent Codex Review 01" (Tech Lead) at `97b69ef92e589ebd1b71016f49c4c9816d8c724b`. Verdict: **`REQUEST_CHANGES`**. Record: `docs/reviews/M3-T1-review-01.md`.
- **Findings:** 2 MINOR and 2 NOTE, all reproduced independently and **ACCEPTED, not applied**:
  - M3T1-R1-F1: mutable parameters;
  - M3T1-R1-F2: silent overflow and non-finite parameters;
  - M3T1-R1-F3: radial docstring power;
  - M3T1-R1-F4: finite mutation coverage.
- **The sections above remain as written.**
  - §9 item 4 (the dual-number substitution) awaits an owner disposition. The reviewer recommends an explicit DR-0025 amendment or disposition.
  - §8's regression results were reproduced by the reviewer with the validators (not the wrappers).
- **Status:** T1 **IMPLEMENTED — REVIEWED — NOT ACCEPTED — NOT MERGED**. Corrections and Review 02 need separate authorization.

## Status update (recorded 2026-10-23 UTC, append-only): Review 01 corrections (I-19)
- Under I-19, the attempt-1/attempt-2 handling of Review 01 is accepted, and M3T1-R1-F1 … F4 are corrected:
  - tests `62d3684`;
  - code `a27f288`;
  - evidence `b0164fd`;
  - records: VAL-0020 correction, DR-0025 owner disposition (dual numbers accepted for T1), packet erratum (+∇U), Review 01 record.
- **Mutation:** 32/32 killed by assertion. **Valid outputs:** bit-identical to `97b69ef`.
- The validation results and Review 02 are recorded in `docs/reviews/M3-T1-review-01.md` and the Review 02 record.
- **Status:** IMPLEMENTED — NOT REVIEW-ACCEPTED — NOT MERGED.

## Status update (recorded 2026-10-23 UTC, append-only): Review 02 (I-19 §11)
- Codex Review 02 of `1cf0ce9`: **REQUEST_CHANGES**, 2 MINOR (M3T1-R2-F1 component-product underflow with non-physical parameters; M3T1-R2-F2 accepted NumPy parameters stored by reference and not converted to binary64) and 1 NOTE (R2-F3, correction-check docstring), plus a count note (R2-O1). R1-F3 and R1-F4 resolved; R1-F1 and R1-F2 partially resolved. Record: `docs/reviews/M3-T1-review-02.md`.
- All findings reproduced by the implementer; dispositions proposed, **none applied** (I-19 §12). No Review 03.
- **Status:** T1 IMPLEMENTED — REVIEWED TWICE — NOT ACCEPTED — NOT MERGED. T2 and later are NOT AUTHORIZED.
