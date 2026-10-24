# M3 T2 — Proposed validation strategy (drag, density, geodetic height, force context)

**Status:** PROPOSAL. **Not authorization to implement tests.** It assumes the implementer's recommendations in `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`. Every row that depends on an undecided item names that item, and changes if the owner decides differently.  
**Prepared under:** I-23 §9 C.  
**Method sources:**
- DR-0025 (Resolution principles 1–9; Q-oracles; §8 mutations; §10 threshold classes);
- DR-0024 Q4 revision 2 (FC-1 … FC-10);
- the T1 precedent (VAL-0020: derived γₙ round-off bounds, red-first tests, mutation by assertion, gating separated from informational results).

## 1. Principles carried into T2
1. **No invented tolerance.** Every gated comparison uses one of four kinds of bound:
   - **(E)** exact equality or an exact sign;
   - **(D)** a derived round-off bound γₙ = nu/(1 − nu), u = 2⁻⁵³, with the operation count stated. Counts by inspection are labelled so (T1 precedent);
   - **(T)** a bound from the cited theory's own error;
   - **(M)** a measurement, which is **reported, not gated**, unless the owner approves a threshold in a DR (DR-0025 principle 7).
2. **Evidence class stated per check:** I, P, C or R (DR-0025 principle 1). Agreement with the T0 spike is **P**: same team, same equations and constants (principle 3).
3. **Boundaries on both sides.** Exact value, one ulp inside and one ulp outside, for several values (playbook `testing.md`).
4. **Sampled results are estimates, not bounds** (T0 lesson R2-F1). A finite test set proves nothing beyond its samples.
5. **Regression checks recompute what they protect;** they never read stored values (T0 lesson R2-F3).
6. **Every assertion is load-bearing:** each named mutant must fail at least one designated assertion, for its declared reason (planning amendments 6–9; T1 campaign).
7. **Non-finite values are rejected before any tolerance comparison** (planning M3P8-F1).

## 2. Requirements under test
| ID | Requirement | Source |
|---|---|---|
| R-CTX-1 | Immutable force context carrying total mass; mutable mass never injected | DR-0026 Q-G3-1; ADR-0009 items 1–2 |
| R-CTX-2 | Old `acceleration(t, r, v)` protocol preserved through an adapter; frozen M2 `FreeSpace` works unchanged | DR-0026 Q-G3-1, §1 |
| R-CTX-3 | Mass built from the RK4 **stage** state: dry + max(prop, 0) | DR-0026 §5.2 |
| R-ORD | Canonical order: point mass, J2, drag, then thrust | ADR-0009 item 9; DR-0026 Q-G3-8 |
| R-DRAG | a = −½ ρ (C_d A/m) \|v_rel\| v_rel; v_rel = v − ω×r; ω = ω_E Ẑ | DR-0024 Q7; SCI-0016 |
| R-CONST | ω_E = 7.292115e-5 rad/s, 1/f = 298.257223563 pinned once; existing WGS 84 μ, a reused; no second literal | DR-0024 §7, Resolution; DR-0026 Q-G3-4 |
| R-DENS-1 | Table pinned verbatim by sha256 `75762f67…`; no repair; one-band 250 km subset | DR-0027 B-1, B-3; DR-0024 Q5, Q5a |
| R-DENS-2 | Band rule: band i is selected when base[i] ≤ h < base[i+1]; the top band applies above its base | T0 (GMAT `FindBand`); DR-0029 P3 |
| R-DENS-3 | Below 0 m: typed domain error | **P4 (ii), undecided** |
| R-DENS-4 | 0–25 km evaluated as published; 900–1000 km accepted; ≥ 1000 km top band extrapolated, labelled unverified | **P5, undecided** |
| R-GEOD-1 | Geodetic height on WGS 84 about +Z; stated domain; points inside the evolute region rejected | DR-0024 Q6; **P8, undecided** |
| R-GEOD-2 | Exposes n̂ (or φ) for the T3 crossing method | **P2 (A5-b), undecided**; packet N-3 |
| R-PURE | Components pure; no I/O, globals, clock, randomness or `tars.validation` import | DR-0026 AR-2; static guard |
| R-ID | Versioned model identifiers | ADR-0009 item 5 |
| R-REG | M1/M2 byte identity; T1 contract unchanged; T0 checks pass | DR-0025 principle 8; I-22 |

## 3. Validation matrix
Kind: E exact, D derived round-off, T theory, M measured and reported. Class: I independent, P partially independent, C same-model, R regression.

### 3.1 Unit tests
| # | Check | Requirement | Kind | Class | Notes |
|---|---|---|---|---|---|
| U-1 | Context is frozen: assignment and deletion raise; mass is converted to owned binary64 (T1 R2-F2 pattern); non-finite or non-positive mass rejected | R-CTX-1 | E | C | — |
| U-2 | The adapter calls an old-protocol model with identical arguments and returns its result **bitwise**; `FreeSpace` and test doubles run unchanged | R-CTX-2 | E | R | — |
| U-3 | Stage mass: for a stage y with m_prop = −1e-17 the context carries the dry mass exactly; the context mass equals the thrust term's mass in every stage | R-CTX-3 | E | C | Guards against committed-state mass (a DR-0025 §8 mutation) |
| U-4 | Drag direction: a_d × v_rel = 0 to a γ-bound, and a_d · v_rel < 0 | R-DRAG | D, E | C | DR-0025 Q4 |
| U-5 | Scaling: doubling ρ, C_d, A or 1/m doubles a_d exactly (power-of-two scaling is exact in binary64 barring underflow or overflow); \|v_rel\|² scaling within γ | R-DRAG | E, D | C | Power-of-two factors make the check exact |
| U-6 | ω_E = 0 ⇒ v_rel = v bitwise; a point at rest in I off the axis has v_rel = −ω×r ≠ 0 | R-DRAG | E | C | FC-2 (a), (b) |
| U-7 | Signs: air velocity at r = a X̂ is +ω_E a Ŷ; prograde equatorial \|v_rel\| = \|v\| − ω_E r, retrograde \|v\| + ω_E r | R-DRAG | E/D | I (signs) | FC-5 |
| U-8 | Cross-track: v_rel not parallel to v on an inclined orbit, **sampled away from the highest-latitude point** | R-DRAG | E | C | FC-8; DR-0024 T0 note |
| U-9 | One shared axis and ω_E: J2, ellipsoid and atmosphere read the same pinned constants (identity) | R-CONST | E | C | FC-7. Not presented as adopting Q-G2-2 |
| U-10 | Constants: ω_E and 1/f literals equal the NGA strings; each literal exists once (the existing literal-location test extended); `WGS84`, `WGS84_EGM2008_TIDE_FREE` and J2 hex unchanged | R-CONST, R-REG | E | C | — |
| U-11 | Table load: the file's sha256 equals the pinned digest before parsing; a tampered copy is rejected before any physics; 28 rows; parsed values equal the file's decimal strings | R-DENS-1 | E | C | DR-0025 §8 "Datasets" |
| U-12 | Densities at every one of the 27 bases equal the table's ρ₀ exactly. At base − 1 ulp the lower band is selected, at base + 1 ulp the upper band | R-DENS-2 | E | C | DR-0024 Q5a; DR-0025 principle 5. Route per DQ-2 |
| U-13 | Inside a band: ρ(h) against the formula evaluated in exact rationals, with exp bounded by the A-FP-2 allowance, documented as an assumption | R-DENS-2 | D | C | No libm guarantee is claimed |
| U-14 | Below the edge: h = −1 ulp, −1e-9, −1, −1e5 m raise the typed error; h = 0 and +1 ulp return band 0; non-finite h raises a distinct error | R-DENS-3 | E | C | **Depends on P4** |
| U-15 | Regions: the 0–25 km cell evaluated as published (GMAT ÷ author 0.13785 % recorded, not repaired); 900–1000 km; top band continuous through 1000 km; values at 1100/1500/2000 km equal the top-band formula | R-DENS-4 | E/D | C | **Depends on P5** |
| U-16 | Far range: subnormal densities above ≈ 181 890 km and exact 0 above h_zero ≈ 191 735 430.72 m are returned without exception; drag 0 when ρ = 0 | R-DENS-4 | E | C | T0 R4-F1 transition points |
| U-17 | Geodetic exact answers: equator h = √(x²+y²) − a; axis h = \|z\| − b, both signs of z | R-GEOD-1 | D (ε_h if path (α)) | I (analytic) | **P8 (a)** |
| U-18 | Geodetic forward-constructed points: latitudes −90…90°, heights −10 km…2000 km; the inverse agrees within the derived bound | R-GEOD-1 | D | P | **P8 (a′)**. The forward formula is coded separately in the tests |
| U-19 | Axisymmetry: h(Q_z r) = h(r) for rotations about +Z (exact for quarter turns; γ-bound otherwise); z-reflection symmetry | R-GEOD-1 | E/D | C | FC-4 |
| U-20 | Domain: points inside the evolute region, and the origin, are rejected; the published reverse example (30 km, 30 km, 0) is rejected | R-GEOD-1 | E | C | DR-0029 P8 "Domain" |
| U-21 | Normal: n̂ is a unit vector to a γ-bound; n̂ is ±Ẑ on the axis and radial on the equator; dh/dt = n̂·v against a central difference of h along a straight line (truncation bound stated) | R-GEOD-2 | D/T | C | **P2-dependent interface** |
| U-22 | Composition: point mass + J2 + drag summed in that order regardless of input order; point-mass-only composition bitwise equal to `CompositeForceModel` today | R-ORD, R-REG | E | R | — |
| U-23 | Limits: no drag component ⇒ bitwise point mass (+ J2); C_d·A = 0 or ρ = 0 ⇒ exact zero drag | R-REG | E | R | DR-0025 Q11 |
| U-24 | Purity: static-guard scan covers the new modules; repeated evaluation is bitwise identical; no attribute changes after evaluation | R-PURE | E | C | Architecture scan, as in the T2 gate |

### 3.2 Property-based and metamorphic tests (seeded and recorded; sampled, so not proofs)
| # | Relation | Kind |
|---|---|---|
| PM-1 | Drag power a_d · v < 0 whenever \|ω×r\| < \|v\| (DR-0024 §10 precondition), over seeded bound states | E (sign) |
| PM-2 | Rotation about +Z commutes with drag: a_d(Q r, Q v) = Q a_d(r, v) | D |
| PM-3 | Mass homogeneity: a_d(m) · m is invariant under m → 2m | E |
| PM-4 | Density monotonic inside each band (strictly decreasing in h) | E (sign) |
| PM-5 | Geodetic height is 1-Lipschitz in r: \|h(r₁) − h(r₂)\| ≤ \|r₁ − r₂\| + 2ε_h | D |
| PM-6 | Spherical and geodetic heights: \|r\| − a ≤ h ≤ \|r\| − b outside the ellipsoid | D (DR-0029 P3) |

The seeds and the number of samples are recorded. A property passing on N samples is reported as such.

### 3.3 Integration-level checks (RK4 in tests, as T1; no runner or scenario)
| # | Check | Kind | Class |
|---|---|---|---|
| I-1 | Dissipation: on drag-only and J2 + drag, E(t) − E(0) against ∫ a_d · v dt from dense outputs (DR-0025 Q5) | M → reported; a gate only with an owner-approved threshold | P |
| I-2 | Energy strictly decreases per committed step on a stated configuration (one-band, B 25.8, dt 10 s) | E (sign) on the stated configuration; measured margin recorded | P |
| I-3 | Semi-analytic decay oracle (DR-0025 Q6): one-band, spherical-height configuration, mean SMA history | T/M: **informational**. DR-0025 §10 has no derived value; T1 Q1 precedent | I (theory, approximate) |
| I-4 | RK4 order on the smooth one-band configuration (dt, dt/2, dt/4) | M, reported (principle 4; the M2 rule is not borrowed) | C |
| I-5 | Band-crossing step behaviour: error ratios across a crossing reported, not gated as an order (principle 5) | M | C |
| I-6 | Atomicity: a step whose stage raises the density domain error leaves the state, tick and engine schedule unchanged | E | C (REV-T2-01 pattern) |
| I-7 | Mass coupling during a burn: drag uses the decreasing stage mass; comparison against a run with frozen mass shows the expected sign of difference | E (sign) | C. VO-4 at unit level; full VO-4 is T4 |

### 3.4 Independent reference comparisons
| # | Reference | Use in T2 | Class |
|---|---|---|---|
| X-G1 | Exact geodetic answers | Gate (U-17) | I (analytic) |
| X-G2 | GeographicLib CartConvert(1) manual examples | Reported; 5 mm print rounding | I (external), coarse |
| X-G3 | IOGP GN 7-2 / EPSG 9602 worked example (packet C-5) | Reported; forward only; cm print on epsg.io; input recalled, PDF unread | I (external), coarse |
| X-G4 | GMAT R2026a `Earth.Altitude` values recorded in T0 | Reported; fails on the axis | I (external) |
| X-D1 | T0 spike density and drag at the T0 sample points | Reported; **bitwise** if DQ-1/DQ-2 path (α) | P |
| X-D2 | DR-0025 Q6 decay theory | Informational (I-3) | I (theory) |

GMAT and DOP853 trajectory comparisons are T4/T5 and are not part of T2.

### 3.5 Numerical boundary tests (summary)
- Every band base ±1 ulp (U-12).
- The lower edge ±1 ulp and the negative range (U-14).
- 1000 km continuity (U-15).
- The normal → subnormal → zero transition of the top band (U-16).
- The axis, the equator and the evolute boundary (U-17, U-20).
- Mass at depletion with negative round-off (U-3).
- Parameter domains: C_d, A and mass positive and finite, and their products' underflow or overflow. This follows T1 R1-F2/R2-F1: every intermediate product of the coefficient chain either is normal or raises, unless exact.

### 3.6 Cross-platform checks
| # | Check | Gate? |
|---|---|---|
| X-P1 | Same-platform byte-identical repetition of all unit outputs (DR-0006) | Yes (E) |
| X-P2 | On the three CI platforms: constant literals and derived constants bit-identical (as T1's J2) | Yes (E), for constants built from correctly rounded operations only |
| X-P3 | Density, drag and geodetic outputs across platforms (libm `exp`, `sin`, `cos`, `atan2`, `hypot`): measured differences in ulps | **Measured, reported.** No bound is borrowed (DR-0025 §7). Evidence for A-FP-2 on platforms beyond the T0 host |
| X-P4 | A-FP-1 runtime check (gradual underflow, no flush-to-zero) in CI | Proposed as a gate (E). T0's check is host-only, because CI does not collect T0 checks |

### 3.7 Regression guarantees
| # | Guarantee | Evidence |
|---|---|---|
| R-1 | M1 Proof 9/9; golden `7a4e1877…20a4` | `run_m1_proof.sh`, fresh clone |
| R-2 | M2 Proof 20/20, `m2_proof` 228/228; the M2 golden, snapshot, GMAT manifest and threshold digests | `run_m2_proof.sh`, separate fresh clone |
| R-3 | T1: 109 tests; J2 hex; `zonal_j2` outputs bit-identical to `65de33f` on the T1 correction-check state sets | Recompute, never read stored values |
| R-4 | T0: 314 checks pass | `docs/science/experiments/m3-t0/check_review0*.py` |
| R-5 | Protected paths unchanged since `fc50aed` | `git diff --stat` |
| R-6 | CI four jobs green on every pushed commit | GitHub Actions |

### 3.8 Mutation campaign (gate sensitivity; DR-0025 §8 restricted to T2 scope)
Each mutant must be killed by a designated assertion, for its declared reason. Detection by an unrelated exception does not count (planning M3P10-F1).
- **Drag:** sign flipped; v instead of v_rel; ω_E sign flipped; ω_E = 0; ω×r computed as r×ω; C_d A/m inverted; dry mass instead of total; committed mass instead of stage mass.
- **Height:** spherical instead of geodetic; altitude datum offset; flattening dropped; the latitude iteration truncated.
- **Density:** scale height km/m error; table shifted one row; band rule `≤` instead of `<`; below-edge extrapolation instead of raise (P4); top-band cutoff to 0 (P5); digest check skipped.
- **Composition:** order changed; adapter that copies or reorders arguments.
- **Protections:** each domain guard removed (T1 R1/R2 protection-removal pattern).

**Expected limitation:** finite coverage. Survivors are documented, not hidden (T1 precedent).

## 4. Proposed acceptance gates for T2 (to be confirmed in the T2 authorization)
| Gate | Content |
|---|---|
| G-T2-1 | U-1 … U-24 pass; the decision-dependent rows match the owner's decisions |
| G-T2-2 | PM-1 … PM-6 pass on the recorded seeds and samples |
| G-T2-3 | I-2, I-6 and I-7 pass. I-1, I-3, I-4 and I-5 are reported in the VAL record as non-gating |
| G-T2-4 | X-G1 gated; X-G2 … X-G4 and X-D1 reported with their classes |
| G-T2-5 | X-P1, X-P2 and X-P4 pass on the three CI platforms; X-P3 measured and recorded |
| G-T2-6 | R-1 … R-6 pass |
| G-T2-7 | The mutation campaign is killed by assertion, with survivors documented |
| G-T2-8 | VAL record (unit-level) and SCI-0014 … SCI-0017 status updates written after the work is committed (playbook: records describe completed work only) |
| G-T2-9 | Independent Codex review per the authorization; no unresolved High finding |

## 5. Not covered by T2 (by design)
- Scenario-level termination (P1–P3; T3).
- GMAT (P6; T5) and reference missions (P7; T3–T5).
- Trajectory thresholds (T6/G4).
- Long-duration decay to the end condition (VO-9; T4).
- Full VO-3/VO-4 (T4).
