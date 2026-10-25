# M3 T2 — Proposed validation strategy (drag, density, geodetic height, force context)

**Status:** PROPOSAL. **Not authorization to implement tests.** It assumes the implementer's recommendations in `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`. Every row that depends on an undecided item names that item, and changes if the owner decides differently. **Update (2026-10-25, append-only): revised under I-26 (§6). The owner's decisions replace the recommendations; rows that depend on A-FP-2, A-LM-1 or A-LM-2 are report-only until promoted (register: `M3-T2-authorization-packet-r1.md` §6.2). Still not authorization to implement tests.**  
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

   **Added under I-24 (M3T2R-R1-F6):**
   - A (D) or (T) bound whose derivation is not written down and reviewed is **not** a gate. It is listed in §3.9 as a T2 derivation deliverable, and the check is reported until the derivation passes review.
   - A bound that holds only under an unproved platform assumption is labelled with that assumption, and gates only if the T2 authorization accepts the assumption explicitly; otherwise it is reported. Examples: A-FP-2 (libm accuracy), or A-LM (§3.9: libm symmetry, oddness and monotonicity, which IEEE 754 does not require).
   - Every exact-sign or exact-equality row states its admissible sample domain, including the zero cases.
   - Wherever possible, the test side of a relation is evaluated in **exact rational arithmetic on the component's binary64 inputs and outputs**, so that the only rounding to bound is the component's own.
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
| U-4 | Drag direction (corrected under I-24, F6). Both relations are evaluated in exact rationals on the binary64 a_d and v_rel. (a) Parallelism: \|(a_d × v_rel)_i\| ≤ (2u/(1 − u))·\|a_j\|·\|v_k\| for each cyclic (i, j, k), with u = 2⁻⁵³. (b) Sign: a_d · v_rel < 0. **Domain:** ρ̂ > 0, the scalar coefficient c ≠ 0 (it can underflow to 0 even when ρ̂ > 0), v_rel ≠ 0, and every nonzero product c·v_rel,i normal (no underflow). **Zero cases, tested separately:** ρ̂ = 0, c = 0 or v_rel = 0 ⇒ a_d = 0 exactly (E). | R-DRAG | D (§3.9 B-1), E | C | DR-0025 Q4. The derivation assumes the T0 structure a_i = fl(c·v_rel,i), one scalar c for all components, and that the test sees the component's own v_rel (exposed, or recomputed by the identical operation sequence). Otherwise re-derive |
| U-5 | Scaling (corrected under I-24, F6): multiplying C_d, A or (through m → m/2) 1/m by 2 doubles a_d exactly. If the component accepts an injected density, the same holds for ρ. **Domain:** the scaled parameter enters only through multiplications and divisions, and every intermediate stays normal and finite at both scales. The "\|v_rel\|² scaling within γ" clause is **removed**: v_rel cannot be scaled independently of r and v, and no bound was derived | R-DRAG | E (§3.9 B-2) | C | Exact: in the normal range, multiplying by 2 commutes with every rounding |
| U-6 | ω_E = 0 ⇒ v_rel == v under IEEE equality (±0 compare equal; a component v_i = −0.0 may come back as +0.0, so the check is not bitwise on the sign of zero). A point at rest in I, off the axis, has v_rel = −ω×r ≠ 0 | R-DRAG | E | C | FC-2 (a), (b). Needs ω as a component parameter in tests (the pinned constant is unchanged) |
| U-7 | Signs: air velocity at r = a X̂ has the sign of +Ŷ (fl(ω_E·a) > 0, exact sign). The prograde/retrograde equatorial magnitudes \|v_rel\| = \|v\| ∓ ω_E r are **reported, not gated**, until their rounding bound is derived (§3.9 B-3) | R-DRAG | E (sign); M (magnitude) | I (signs) | FC-5 |
| U-8 | Cross-track: v_rel not parallel to v on an inclined orbit, **sampled away from the highest-latitude point** | R-DRAG | E | C | FC-8; DR-0024 T0 note |
| U-9 | One shared axis and ω_E: J2, ellipsoid and atmosphere read the same pinned constants (identity) | R-CONST | E | C | FC-7. Not presented as adopting Q-G2-2 |
| U-10 | Constants: ω_E and 1/f literals equal the NGA strings; each literal exists once (the existing literal-location test extended); `WGS84`, `WGS84_EGM2008_TIDE_FREE` and J2 hex unchanged | R-CONST, R-REG | E | C | — |
| U-11 | Table load: the file's sha256 equals the pinned digest before parsing; a tampered copy is rejected before any physics; 28 rows; parsed values equal the file's decimal strings | R-DENS-1 | E | C | DR-0025 §8 "Datasets" |
| U-12 | Densities at every one of the 27 bases equal the table's ρ₀ exactly. At base − 1 ulp the lower band is selected, at base + 1 ulp the upper band | R-DENS-2 | E | C | DR-0024 Q5a; DR-0025 principle 5. Route per DQ-2. **Justification (I-24, F6):** at an exact base the exponent is exactly 0 on both routes (the bases are integers in km and in m, and h/1000 is exact for them), and exp(±0) = 1 exactly (A-LM-0, §3.9). Lower-band selection at base − 1 ulp on the km route was checked at all 27 bases (Review 01 claim 8; I-24 reproduction): exhaustive for these 27 inputs, not a general property |
| U-13 | Inside a band: ρ̂(h) against the formula evaluated by an oracle with stated error. **One-sided check (clarified under I-25, R2-F2):** ρ̂ must not exceed E3's **upper** enclosure (`t0_termination.rounding_allowances`), which holds for the spike's operation sequence (path (α), route (km)) **under A-FP-2**. E3 gives no lower bound, so no lower-side check is gated; the lower-side difference is reported | R-DENS-2 | D, conditional on A-FP-2 | C | **Gates only if the T2 authorization accepts A-FP-2 for test purposes; otherwise reported** (I-24, F6). No libm guarantee is claimed. Under path (β) or route (m), E3 must be re-derived |
| U-14 | Below the edge (corrected under I-24, F4). **Raise:** h = −5e-324, −2.47e-321 (the spike's km-route trap interval, which the spike accepts), −2.475e-321, −1e-300, −1e-9, −1 and −1e5 m. **Band 0:** h = +0.0, −0.0, +5e-324. **Non-finite h:** a distinct error, checked first. The guard compares h in metres with 0 **before** any unit conversion | R-DENS-3 | E | C | **Depends on P4.** Proposed T2 requirement under (ii), not T0 behaviour (packet P4 items 8, 14) |
| U-15 | Regions (corrected under I-24, F1): the 0–25 km cell evaluated as published (GMAT ÷ author 0.13785 % recorded, not repaired); 900–1000 km. **At 1000 km: the published discontinuity is tested, not continuity.** 1000 km − 1 ulp gives the 900 km band (spike: 3.0190482489066557e-15); exactly 1000 km gives the row ρ₀ 3.019e-15; + 1 ulp gives the top band. The relative jump −1.598e-5 is recorded. Above 1000 km: values at 1001/1100/1500/2000 km equal the top-band formula | R-DENS-4 | E | C | **Depends on P5.** DR-0024 Q5a forbids forcing continuity. The top band is smooth only for h > 1000 km |
| U-16 | Far range: densities are returned without exception wherever they are subnormal or exactly 0, and drag is exactly 0 when ρ̂ = 0. The transition points (≈ 181 890 km; h_zero ≈ 191 735 430.72 m) are T0's for the spike's km-route sequence (E3) | R-DENS-4 | E | C | T0 R4-F1. **Under path (β) or route (m) the transition points are recomputed for T2's sequence**; "no exception" is required either way (I-24, F6) |
| U-17 | Geodetic exact answers (corrected under I-24, F2). Equator: r = (x, 0, 0) with binary64 x ≥ a, reference x − a. Axis: r = (0, 0, z) with \|z\| ≥ b, both signs of z, reference \|z\| − a√(1 − e2). Both references are evaluated exactly, or by a 60-digit oracle with outward rounding, **on the model's ellipsoid**. Gate: \|ĥ − h_ref\| ≤ ε_h(h) | R-GEOD-1 | D (E1, §3.9 B-12) **only for h ≥ 0 and path (α); conditional on A-FP-2** | I (analytic) | **P8 (a)**. Points with x < a or \|z\| < b (negative height) are **reported**. Under path (β): reported until derived. The model/WGS 84 ellipsoid difference (b +1.71e-12 m) is reported separately |
| U-18 | Geodetic forward-constructed points (corrected under I-24, F2): latitudes −90…90°, heights −10 km…2000 km | R-GEOD-1 | **Reported**; D only after §3.9 B-4 | P | **P8 (a′)**. The forward formula is coded separately in the tests. Gate for h_nom ≥ 0 (and h_nom > δ_f) under path (α) **only once** δ_f (forward-construction rounding) or an oracle-error term is derived and reviewed: bound ε_h + δ_f. Negative heights stay reported. No number is proposed now |
| U-19 | Symmetry (corrected under I-25, M3T2R-R2-F1). **Mathematics vs binary64:** the exact geodetic height is invariant under rotations about +Z and under the reflection z → −z, since the ellipsoid has both symmetries. Whether the *computed* height is invariant depends on library behaviour that no adopted assumption fixes. (a) **Quarter turns about +Z, exact equality:** the spike's path (α) sequence sees x and y only through p = hypot(x, y). So ĥ(Q_z r) = ĥ(r) exactly if hypot is symmetric and even (A-LM-1), and nothing else is needed. (b) **z-reflection, exact equality: diagnostic, reported, never gated.** It would also need sin and atan2 to be odd and cos to be even, and no adopted assumption covers that (Review 02 R2-F1: a cos error of 2 ulp, which A-FP-2 permits, moves ĥ by 9.3e-10 m at φ = 0.6). (c) **z-reflection and quarter turns, bounded comparison:** \|ĥ(r) − ĥ(σr)\| ≤ 2ε_h(h), evaluated in exact rationals (§3.9 B-11). (d) General rotations are reported until a γ-bound is derived (§3.9 B-5) | R-GEOD-1 | (a) E, **conditional on A-LM-1**; (b) M, diagnostic; (c) D (E1), **conditional on A-FP-2**, exterior and path (α) only | C | FC-4. (a) gates only if the T2 authorization accepts A-LM-1, and (c) only if it accepts A-FP-2 (the same condition as U-17); otherwise reported. (c) detects only asymmetries larger than 2ε_h (≈ 1.8e-8 m at 120 km). The finer exact check stays diagnostic |
| U-20 | Domain: points inside the evolute region, and the origin, are rejected; the published reverse example (30 km, 30 km, 0) is rejected | R-GEOD-1 | E | C | DR-0029 P8 "Domain" |
| U-21 | Normal (corrected under I-24, F6). **Reported, not gated** until §3.9 B-6 is derived: \|n̂\| − 1; n̂ against ±Ẑ on the axis and against the radial direction on the equator; dh/dt = n̂·v against a central difference of h. **The I-23 "±Ẑ on the axis" was stated as exact and is not:** on the axis the spike's latitude is fl(π/2) = 1.5707963267948966 and cos of it is 6.12e-17 (I-24 reproduction). An n̂ built from φ therefore has a nonzero x component there. Exact on the equator only: φ = 0 and n̂_z = 0 exactly (atan2(+0, p > 0) = +0, A-LM-0) | R-GEOD-2 | M until derived | C | **P2-dependent interface** |
| U-22 | Composition: point mass + J2 + drag summed in that order regardless of input order; point-mass-only composition bitwise equal to `CompositeForceModel` today | R-ORD, R-REG | E | R | — |
| U-23 | Limits (corrected under I-24, F6): no drag component ⇒ bitwise point mass (+ J2); ρ̂ = 0 ⇒ exactly zero drag; positive C_d and A with C_d·A ≤ 2⁻¹⁰⁷⁵ ⇒ exactly zero drag (T0 E4b, derived for the spike's coefficient sequence under A-FP-1 and A-FP-2; re-derive for another sequence). **C_d·A = 0 from a zero parameter is outside the parameter domain** (§3.5: C_d, A positive and finite) **and must raise**, not return zero. I-23 listed it as a zero-drag case, contradicting §3.5 | R-REG | E | R | DR-0025 Q11; T1 R1-F2 domain pattern |
| U-24 | Purity: static-guard scan covers the new modules; repeated evaluation is bitwise identical; no attribute changes after evaluation | R-PURE | E | C | Architecture scan, as in the T2 gate |

### 3.2 Property-based and metamorphic tests (seeded and recorded; sampled, so not proofs)
| # | Relation | Kind |
|---|---|---|
| PM-1 | Drag power a_d · v < 0 (corrected under I-24, F6). The I-23 precondition \|ω×r\| < \|v\| makes the **exact** v_rel·v positive, but not the computed one. Domain: states whose **computed** v_rel satisfies v_rel·v > u·Σ\|v_rel,i v_i\|, checked in exact rationals, plus U-4's domain (ρ̂ > 0, no underflow). On that domain the sign is exact (§3.9 B-1). States outside it are reported | E (sign) on the stated domain |
| PM-2 | Rotation about +Z commutes with drag: a_d(Q r, Q v) = Q a_d(r, v) | **Reported** until §3.9 B-5 is derived (I-24, F6). Even quarter turns are not claimed exact: a dot product evaluated with FMA (allowed by A-FP-3) is not symmetric under x ↔ y |
| PM-3 | Mass homogeneity: fl(a_d,i(2m)·2m) = fl(a_d,i(m)·m) exactly | E (§3.9 B-2). Domain: no underflow or overflow at m and 2m (I-24, F6) |
| PM-4 | Density inside one band (corrected under I-24, F3). (a) **Non-increasing:** h₁ < h₂ in the same band ⇒ ρ̂(h₁) ≥ ρ̂(h₂). Equal outputs from neighbouring inputs are expected: ρ̂(1.0) = ρ̂(next(1.0)) in the spike, 800 of 2 858 sampled adjacent pairs in band 0 are equal (I-24), and on the km route distinct h_m can share fl(h_m/1000). Conditional on exp being monotone (A-LM-2); every other operation is a correctly rounded monotone operation. (b) **Strict decrease: reported only, never gated** (corrected under I-25, M3T2R-R2-F2). The exact table formula decreases strictly inside a band, a mathematical property. Whether two computed values differ needs a **lower** as well as an upper bound on ρ̂, relative to the exact formula at the two **input** heights, including the km-conversion error and the additive (subnormal) term. The T0 derivation E3 gives only an upper enclosure, ρ̂ ≤ F_ρ e^η₀ ρ(h_s) exp(θ_x X) + N_ρ, at the rounded selection height h_s (`t0_termination.rounding_allowances`). No lower bound is inferred from it, and none from passing samples. Promoting (b) to a gate needs a written two-sided derivation, reviewed, and explicit authorization (§3.9 B-9). (c) In the zero tail (above h_zero): ρ̂ = 0 for both, so only (a) applies | (a) E (sign), **conditional on A-LM-2**: gates only if the T2 authorization accepts it; otherwise reported. (b) M, reported |
| PM-5 | Geodetic height: \|ĥ(r₁) − ĥ(r₂)\| ≤ \|r₁ − r₂\| + ε_h(h₁) + ε_h(h₂), both sides in exact rationals (compare squares for the norm). **Domain (I-24, F2):** both points outside the ellipsoid (exterior height is a distance, hence 1-Lipschitz), path (α). ε_h is evaluated at the upper bound (ĥ + β)/(1 − α) of the true height | D (E1, §3.9 B-12), exterior and path (α) only; **conditional on A-FP-2**; otherwise reported |
| PM-6 | \|r\| − a − ε_h ≤ ĥ ≤ \|r\| − b + ε_h, \|r\| in exact rationals (DR-0029 P3's exact inequality, plus E1 for the computed height). **Domain (I-24, F2):** outside the ellipsoid, path (α). Negative heights reported | D (E1, §3.9 B-12), exterior and path (α) only; **conditional on A-FP-2** |

The seeds and the number of samples are recorded. A property passing on N samples is reported as such.

### 3.3 Integration-level checks (RK4 in tests, as T1; no runner or scenario)
| # | Check | Kind | Class |
|---|---|---|---|
| I-1 | Dissipation: on drag-only and J2 + drag, E(t) − E(0) against ∫ a_d · v dt from dense outputs (DR-0025 Q5) | M → reported; a gate only with an owner-approved threshold | P |
| I-2 | Energy change per committed step on a stated configuration (one-band, B 25.8, dt 10 s) | **M, reported** (corrected under I-24, F6). Not derived: RK4's per-step energy truncation error has no fixed sign, and no derivation shows that the drag dissipation dominates it and the rounding of the energy evaluation. Gate only after §3.9 B-7 | P |
| I-3 | Semi-analytic decay oracle (DR-0025 Q6): one-band, spherical-height configuration, mean SMA history | T/M: **informational**. DR-0025 §10 has no derived value; T1 Q1 precedent | I (theory, approximate) |
| I-4 | RK4 order on the smooth one-band configuration (dt, dt/2, dt/4) | M, reported (principle 4; the M2 rule is not borrowed) | C |
| I-5 | Band-crossing step behaviour: error ratios across a crossing reported, not gated as an order (principle 5) | M | C |
| I-6 | Atomicity: a step whose stage raises the density domain error leaves the state, tick and engine schedule unchanged | E | C (REV-T2-01 pattern) |
| I-7 | Mass coupling during a burn: (a) **E:** at each derivative evaluation, the drag term's mass equals the stage mass (the U-3 identity, observed through the context); (b) the trajectory difference against a frozen-mass run is **reported** (corrected under I-24, F6): its sign over a coupled trajectory is not derived (§3.9 B-8) | (a) E; (b) M | C. VO-4 at unit level; full VO-4 is T4 |

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
- The lower edge (corrected under I-24, F4): ±0.0, +5e-324, −5e-324, the spike's km-route trap interval down to −2.475e-321, and the negative range (U-14). The guard acts in metres, before conversion.
- The 1000 km base (corrected under I-24, F1): the published −1.598e-5 discontinuity and the band selection at −1 ulp, exactly and +1 ulp, like every other base (U-15). **No continuity requirement at any base** (DR-0024 Q5a).
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

### 3.9 Bound audit (added under I-24, M3T2R-R1-F6)
Every (D) or (T) bound in §3.1–§3.3, and every exact claim that rests on more than correctly rounded IEEE 754 operations. **Status:**
- **Gate:** derived here or in an accepted record, on its stated domain.
- **Conditional:** derived, but only under a named unproved assumption. It gates only if the T2 authorization accepts that assumption; otherwise it is reported.
- **Deliverable:** no derivation yet. Reported, not gated. The derivation is a T2 deliverable, reviewed before the check may gate. No placeholder number is proposed.

**Assumptions used** (beyond A-FP-1, IEEE 754 binary64 with round-to-nearest-even and gradual underflow, checked at run time by X-P4):
- **A-FP-2:** T0's libm accuracy assumption (DR-0029 P1). Unproved; measured on one host.
- **A-LM-0:** exp(±0) = 1, sin(±0) = ±0 and atan2(±0, x > 0) = ±0 exactly. These are special values that the C standard's Annex F specifies; I-24 recalled this and did not re-read it. They are also measured on the I-24 host (U-12, U-21).
- **A-LM-1 (narrowed under I-25, R2-F1):** hypot is symmetric and even in each argument, used by U-19 (a) only. IEEE 754 does not require it. 0 failures in 10⁵ random pairs on the I-24 host [measured; not a proof]. Note that CPython's `math.hypot` is CPython's own code, not the platform libm.
  - The I-24 text also listed the oddness of sin and atan2. That part is withdrawn, because no row now relies on it.
  - **Not assumed anywhere:** the oddness of sin and atan2, and the evenness of cos. Exact z-reflection symmetry would need all three, so it is diagnostic only (U-19 (b)). The T0 accuracy assumption A-FP-2 is **not** strengthened to supply them.
- **A-LM-2:** exp is monotone non-decreasing. This does not follow from an error bound such as A-FP-2, and IEEE 754 does not require it of a non-correctly-rounded exp.

| ID | Row(s) | Bound or exact claim | Derivation and evidence | Assumptions | Valid domain | Status |
|---|---|---|---|---|---|---|
| B-1 | U-4, PM-1 | (a) \|(a × v_rel)_i\| ≤ (2u/(1 − u))·\|a_j\|·\|v_k\|; (b) a·v_rel and (PM-1, on its margin domain) a·v have the sign of the coefficient | [derived, I-24] a_i = fl(c·v_i) = c·v_i(1 + δ_i), \|δ_i\| ≤ u. Then (a × v)_x = c·v_y·v_z(δ_y − δ_z), and \|c·v_y\| ≤ \|a_y\|/(1 − u). For (b), a·v_rel = c·Σv_i²(1 + δ_i) and (1 − u)Σv_i² > 0. PM-1: a·v = c(v_rel·v + Σδ_i v_rel,i v_i) | A-FP-1. Structure a_i = fl(c·v_rel,i) with one scalar c (the T0 E4 sequence). The test uses the component's own v_rel. The test side is evaluated in exact rationals | c ≠ 0, v_rel ≠ 0, every nonzero c·v_rel,i normal; PM-1 also needs v_rel·v > u·Σ\|v_rel,i v_i\| | **Gate** (path (α) structure; re-derive otherwise) |
| B-2 | U-5, PM-3 | Exact doubling and halving | [derived, I-24] In the normal range, fl(2x) = 2fl(x) and fl(x/2) = fl(x)/2 for every rounding, so a factor of 2 entering only through × and ÷ passes through every rounding exactly | A-FP-1 | Every intermediate normal and finite at both scales | **Gate** |
| B-3 | U-7 | \|v_rel\| = \|v\| ∓ ω_E r on equatorial states, to a rounding bound | Not derived | — | — | **Deliverable** |
| B-4 | U-18 | ε_h + δ_f for forward-constructed points | E1 is derived (T0, exterior, path (α)); δ_f, the forward construction's rounding, is not. Alternative: an oracle for h_true(r̂) with a stated error | A-FP-1, A-FP-2 (E1 uses libm sin, cos, atan2, hypot) | h_nom ≥ 0 with h_nom > δ_f; path (α) | **Deliverable** (δ_f); reported until then |
| B-5 | U-19 (general rotations), PM-2 | Rotation equivariance to a γ-bound | Not derived. The rotation itself is rounded, and FMA in a dot product breaks x ↔ y symmetry | — | — | **Deliverable** |
| B-6 | U-21 | \|n̂\| − 1; n̂ vs ±Ẑ and radial; central-difference truncation of dh/dt | Not derived. I-24 measured that the axis normal is not exactly ±Ẑ (cos(fl(π/2)) = 6.12e-17) | — | — | **Deliverable** |
| B-7 | I-2 | Per-step energy decrease | Not derived (RK4's energy truncation error has no fixed sign) | — | — | **Deliverable**; reported |
| B-8 | I-7 (b) | Sign of the frozen-mass trajectory difference | Not derived over a coupled trajectory | — | — | **Deliverable**; reported |
| B-9 | U-13 (upper side); PM-4 (b) | (i) E3 **upper** enclosure of ρ̂; (ii) strict decrease for separated inputs | (i) [derived, T0 E3 in `t0_termination.rounding_allowances`] for the spike's km-route sequence: **one-sided** (upper) only. (ii) Not derived: it needs a two-sided bound referenced to the input heights, including the km conversion and the additive term, and E3 provides none (Review 02 R2-F2) | A-FP-2 | (i) inside one band; path (α), route (km) | (i) **Conditional** (A-FP-2), upper side only. (ii) **Deliverable**, reported; a gate only after a reviewed two-sided derivation and explicit authorization *(corrected under I-25)* |
| B-10 | PM-4 (a) | Non-increase inside a band | [derived, I-24] fl(h/1000), the subtraction, the division by the scale height and the multiplication by ρ₀ > 0 are correctly rounded, hence monotone; the negation reverses order exactly | **A-LM-2** | Inside one band | **Conditional** (A-LM-2) |
| B-11 | U-19 | (a) exact quarter-turn equality; (b) exact z-reflection equality; (c) \|ĥ(r) − ĥ(σr)\| ≤ 2ε_h(h) for σ a quarter turn about +Z or z → −z | *(Corrected under I-25, R2-F1.)* (a) [derived] Under a quarter turn the operands of path (α) differ only inside p = hypot(x, y); under A-LM-1, p is identical, so every later operation is identical. (b) Not derived from adopted assumptions: the I-24 claim omitted cos (`t0_model.py:161`). (c) [derived from E1] σ is exact in binary64 (a negation or a swap) and is a symmetry of the ellipsoid, so h_true(σr) = h_true(r) exactly. E1 bounds each computed height: \|ĥ(r) − ĥ(σr)\| ≤ \|ĥ(r) − h\| + \|h − ĥ(σr)\| ≤ 2ε_h(h). Evaluate ε_h at the upper bound h ≤ (ĥ(r) + β)/(1 − α) | (a) A-LM-1; (b) —; (c) A-FP-1, A-FP-2 (via E1) | (a) path (α); (c) both points outside the ellipsoid (true height ≥ 0), path (α), no overflow | (a) **Conditional** (A-LM-1); (b) **diagnostic, reported**; (c) **Conditional** (A-FP-2) |
| B-12 | U-17, PM-5, PM-6 | ε_h(h) = αh + β | [derived, T0 E1] Reviewed in T0 Reviews 03–10 | A-FP-1, A-FP-2 | **True height ≥ 0** (exterior), no overflow, path (α); the inverse's evaluation error only | **Conditional** (A-FP-2), on that domain only. T0's floors rest on the same assumption |
| B-13 | U-12 | ρ̂(base) = ρ₀ exactly | [derived, I-24] The exponent is exactly 0 at an integer base on both routes; then A-LM-0. Lower-band selection at −1 ulp is checked exhaustively for the 27 bases on the km route | A-LM-0 | The 27 bases and the lower edge | **Gate** (A-LM-0 is a special value the standard fixes, and is checked directly by the test) |
| B-14 | U-16 | Transition points (subnormal onset, h_zero) | [derived, T0 E3] for the spike's sequence | A-FP-1, A-FP-2 | Path (α), route (km) | Positions **reported**; "no exception and ρ̂ = 0 ⇒ zero drag" is a **Gate** (E) |
| B-15 | packet P1 item 14 | Two threshold estimates differ by ≤ the sum of their bracket widths | [derived] two brackets of the same root of the same function overlap | Same density arithmetic | Path (α), route (km) | **Gate** on that domain; otherwise reported |

**Rows with no bound, checked for the other F6 risk, zero cases:**
- U-1, U-2, U-3, U-9, U-10, U-11, U-14, U-15, U-20, U-22, U-24, I-6 and the X-P rows are exact (E) with no hidden bound.
- U-8: the non-parallel check is the exact rational cross product of the binary64 v and the component's own v_rel, which must be nonzero. That makes it exact, with the same v_rel access assumption as B-1.
- U-3: dry + max(prop, 0) is exact for finite positive owned dry mass (Review 01, claim 8).
- U-6 has a signed-zero caveat (stated in the row).
- U-23: a zero parameter is a domain error (stated in the row).
- U-20: its boundary classification is defined by the component's own predicate; test points are taken on both sides of it, as computed.

**Effect:** gates G-T2-1 … G-T2-3 (§4) cover the **Gate** rows only. **Conditional** rows gate only if the T2 authorization explicitly accepts the named assumption. **Deliverable** rows are reported, and become gates only after their derivation has been reviewed.

## 4. Proposed acceptance gates for T2 (to be confirmed in the T2 authorization)
| Gate | Content |
|---|---|
| G-T2-1 | U-1 … U-24 pass, in their **Gate** parts (§3.9), plus their **Conditional** parts if the T2 authorization accepts the named assumption. The decision-dependent rows match the owner's decisions. Reported parts are recorded *(corrected under I-24, F6)* |
| G-T2-2 | PM-1 and PM-3 pass on their stated domains. PM-4 (a), PM-5 and PM-6 also pass if the T2 authorization accepts their assumptions (A-LM-2, A-FP-2). All on the recorded seeds and samples. PM-2 and PM-4 (b) are reported *(corrected under I-24, F2, F3, F6; I-25, R2-F2)* |
| G-T2-3 | I-6 and I-7 (a) pass. I-1, I-2, I-3, I-4, I-5 and I-7 (b) are reported in the VAL record as non-gating *(corrected under I-24, F6)* |
| G-T2-3a | Every **Deliverable** derivation in §3.9 that T2 produces is written down with its operation count, domain and assumptions, and reviewed in the T2 review before its row may gate *(added under I-24, F6)* |
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

## Status update (2026-10-24, append-only): independent Review 01
- Codex Review 01 (at `5ee6a6a`): **REQUEST_CHANGES**, with 2 MAJOR (M3T2R-R1-F1: 1000 km continuity; F2: E1 reused beyond h ≥ 0), 3 MINOR (F3 strict monotonicity; F4 lower-edge typo and the −5e-324 guard; F5 C² across band edges) and 1 NOTE (F6). All are reproduced and ACCEPTED, **not applied** (I-23 §10).
- No P1–P9 classification changes. The text above is as reviewed.
- Record: `docs/reviews/M3-T2-readiness-review-01.md`.

## Correction log (I-24, 2026-10-24): Review 01 findings F1–F6
Made under Authorization I-24 (Tech Lead, 2026-10-24); documentation only. The wording Review 01 reviewed is preserved at commit `5ee6a6a`. **This is still a proposal, not an authorization to implement tests.** No decision is assumed beyond what the header states. The finding-by-finding matrix is in `docs/reviews/M3-T2-readiness-review-01-corrections.md`.
- **F1:** U-15 and §3.5 test the published 1000 km discontinuity (−1.598e-5) and the band selection at ±1 ulp. They no longer require continuity; the top band is claimed smooth only above its base.
- **F2:** U-17, PM-5 and PM-6 use E1 only for exterior points (true height ≥ 0), under path (α), with exact references on the model's ellipsoid. U-18 is reported until a forward-construction (or oracle) term is derived (B-4). Negative heights are reported.
- **F3:** PM-4 tests non-increase (conditional on A-LM-2). Strict decrease is tested only for inputs separated by the E3 allowance (conditional on A-FP-2), and equal outputs are expected.
- **F4:** U-14 and §3.5 put the guard in metres before conversion. They test −5e-324, the spike's trap interval and ±0.0.
- **F5:** no strategy row claimed C². The P2 correction is in the decision packet.
- **F6:**
  - New: principle 1 additions and the §3.9 bound audit (B-1 … B-15, assumptions A-LM-0 … A-LM-2).
  - U-4, U-5, PM-1 and PM-3 are given derivations and domains.
  - U-7 (magnitudes), U-21, PM-2, I-2 and I-7 (b) are reported until derived.
  - U-13, U-19 and PM-4 are made conditional.
  - Gates G-T2-1 … G-T2-3 are restricted accordingly, and G-T2-3a is added.
- **Related defects found during the I-24 audit:**
  - U-21's "±Ẑ on the axis" was not exact.
  - U-23's "C_d·A = 0 ⇒ zero drag" contradicted §3.5's parameter domain.
  - U-6's "bitwise" ignored the sign of zero.
  - U-16's transition points are specific to the spike's arithmetic.
  - All four are corrected in their rows.


## Status update (2026-10-24, append-only): independent Review 02
- Codex Review 02 (at `f44a94f`): **REQUEST_CHANGES**, with 2 MAJOR and 1 MINOR. All three are reproduced and ACCEPTED, **not applied** (I-24 §6 stop rule):
  - M3T2R-R2-F1: z-reflection exactness also needs cos to be even, which A-LM-1 omits (U-19, B-11).
  - R2-F2: PM-4 (b) cites a two-sided E3 allowance, but E3 is one-sided (PM-4 (b), B-9).
  - R2-F3: extremum wording in packet P4 item 8.
- Review 01: F1, F2, F4 and F5 are RESOLVED; F3 and F6 are PARTIALLY RESOLVED (through R2-F1 and R2-F2).
- No P1–P9 classification changes. The text above is as reviewed at `f44a94f`.
- Record: `docs/reviews/M3-T2-readiness-review-02.md`.

## Correction log (I-25, 2026-10-24): Review 02 findings R2-F1, R2-F2
Made under "Authorization I-25 — M3 T2 Decision Readiness: Review 02 Corrections and Independent Review 03" (Tech Lead); documentation only. The wording Review 02 reviewed is preserved at `f44a94f`. Matrix: `docs/reviews/M3-T2-readiness-review-02-corrections.md`.
- **R2-F1 (U-19, A-LM-1, B-11):**
  - Exact z-reflection equality is now **diagnostic and reported**, never gated. It would need the oddness of sin and atan2 and the evenness of cos, and no adopted assumption supplies them; A-FP-2 is not strengthened.
  - A-LM-1 is **narrowed** to hypot symmetry and evenness, which is all that exact quarter-turn equality needs.
  - A bounded comparison, |ĥ(r) − ĥ(σr)| ≤ 2ε_h, is derived from the reviewed E1. It is conditional on A-FP-2, for exterior points under path (α), the same conditions as U-17.
- **R2-F2 (PM-4 (b), B-9, U-13, G-T2-2):**
  - Strict decrease is **reported only**. E3 is an upper enclosure, and no lower bound is inferred from it or from samples. Promoting the test needs a reviewed two-sided derivation and explicit authorization.
  - U-13 is stated as one-sided (upper).
  - PM-4 (a), non-increase under A-LM-2, is unchanged.
- The I-24 F3 entry above describes the state at `f44a94f` and is superseded by this entry for PM-4 (b).

- *(2026-10-24, append-only)* **Independent Review 03 (at `628623b`): PASS, no findings.** R2-F1 … R2-F3 resolved; Review 01 findings remain closed. Record: `docs/reviews/M3-T2-readiness-review-03.md`. Nothing is approved by the PASS.

## 6. Revision under I-26 (2026-10-25): owner decisions and the conditional floating-point policy
Made under "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25). Documentation only. **This section governs where it differs from §1–§5.** The text above is preserved as reviewed at `628623b` (Review 03 PASS). **This is still not authorization to implement tests; T2 is NOT AUTHORIZED.**

### 6.1 Decision-dependent rows are now fixed
| Item | Was | Now |
|---|---|---|
| Header assumption ("assumes the implementer's recommendations") | Recommendations | **Owner decisions.** P1–P5, P7–P9 DECIDED; P6 PROVISIONALLY SELECTED; DQ-1 (α), DQ-2 (km), DQ-3 (a), DQ-4, DQ-5 (a), DQ-6 DECIDED |
| R-DENS-3 (U-14) | P4 (ii), undecided | **DECIDED** as written: guard in metres before conversion; −0.0, +0.0, +5e-324 evaluated in band 0; non-finite a distinct error checked first; the T0 km-route trap interval raises |
| R-DENS-4 (U-15, U-16) | P5, undecided | **DECIDED** as written: the 1000 km base keeps its −1.598e-5 jump; no continuity requirement at any base; the top band extrapolated above 1000 km, values labelled unverified in records; subnormal and zero densities returned |
| R-GEOD-1 (U-17 … U-20) | P8, undecided | **DECIDED**: (a) the primary gate source within its justified domain; (a′) reported until δ_f is derived and reviewed; negative heights reported; X-G2 … X-G4 corroboration only. **The gate status of the tolerance follows §6.2** |
| R-GEOD-2 (U-21) | P2 (A5-b), undecided | **DECIDED**: the component exposes φ or n̂. U-21's accuracy checks stay reported until B-6 is derived |
| "Path (α)", "route (km)" qualifiers (U-4, U-13, U-16, U-17, U-19, PM-5, PM-6, B-1, B-9 … B-15, X-D1) | Conditional on DQ-1/DQ-2 | **Apply**: DQ-1 (α) and DQ-2 (km) are decided. The operation sequences are specified in `M3-T2-authorization-packet-r1.md` §5. Every "under path (β) or route (m)" alternative is **void** |
| Test vehicles | P9, undecided | **V1/V2**, labelled **ILLUSTRATIVE — VALIDATION ONLY** |

### 6.2 Owner policy on conditional floating-point gates (DR-0025 "I-26 note", verbatim there)
- **A-FP-2, A-LM-1 and A-LM-2 are not accepted as universal guarantees.**
- Every row that depends on them is **report-only** until the precise assumption is independently justified for the supported execution environment, the resulting criterion is reviewed, and the owner promotes the row.
- **Exact z-reflection symmetry (U-19 (b)) and strict density decrease (PM-4 (b)) are report-only regardless.**
- **The conditional-row register is `M3-T2-authorization-packet-r1.md` §6.2.** It lists every conditional row, its assumption and the evidence required to promote it, and it governs row status.
- **Consequences for §3 and §4:**
  - The "gates only if the T2 authorization accepts" wording in U-13, U-17, U-19, PM-4 (a), PM-5, PM-6 and B-9 … B-12 now reads: *report-only until promoted under the policy* (register conditions P-i … P-iii). A T2 authorization does **not** promote a row by accepting an assumption in general terms.
  - **G-T2-1 and G-T2-2:** their "plus their Conditional parts if the T2 authorization accepts the named assumption" clauses are replaced by "plus the Conditional parts promoted under the policy". Today none is promoted, so the gates cover the Gate rows only.
  - **G-T2-4:** X-G1 (exact geodetic answers) is the decided gate *source*. The comparison's tolerance ε_h rests on A-FP-2, so X-G1 is **reported until promoted**. Its domain checks (U-20) gate unconditionally.

### 6.3 Classification correction found during the I-26 reconciliation
- **U-23, third clause** ("positive C_d and A with C_d·A ≤ 2⁻¹⁰⁷⁵ ⇒ exactly zero drag") is labelled **E** in §3.1, but it rests on T0 E4b, which the row itself says is "derived … under A-FP-1 and A-FP-2". §3.9 did not list it.
- **Corrected classification: Conditional (A-FP-2), report-only until promoted.** It is also specific to the spike's coefficient sequence; T2 must use that sequence or re-derive.
- U-23's other clauses are unchanged:
  - no drag component ⇒ bitwise point mass (+ J2);
  - ρ̂ = 0 ⇒ exactly zero drag;
  - a zero parameter raises.
- Recorded in the open-issues register (OI-24).

### 6.4 Gates kept unconditional (I-26 §5: "Preserve all unconditional, independently justified gates")
- **B-1, B-2:** A-FP-1, which is IEEE 754 itself, checked by X-P4.
- **B-13:** an exact check of the 27 base inputs, run on every CI platform, so the test observes A-LM-0 directly on each platform.
- **B-14's behaviour part.**
- Every row §3.9 lists as exact with no hidden bound, except U-23's third clause (§6.3).
- **The regression guarantees R-1 … R-6.**
- **B-15 (T3, not T2):** its premise "same density arithmetic" includes the same `exp` results, so it holds on the platform that produced the T0 thresholds (macOS x86_64) or wherever identical density bits are shown. This is recorded for T3, and no T2 row changes.

### 6.5 Not changed
- Every derivation (B-1 … B-15), domain, sample set, evidence class and mutation in §3.
- §5 (not covered by T2).
- No tolerance is added and no threshold is proposed.
