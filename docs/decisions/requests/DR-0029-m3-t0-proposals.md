# Decision Request: M3 T0 proposals: termination and atmosphere domain, GMAT method, reference missions, geodetic test points, validation-scenario parameters

**Status:** OPEN. Nothing here is decided. **Corrected after Review 01** (M3T0-F1 … F4; log at the end; authorized by "TARS M3 T0 — Review 01 Correction Authorization", 2026-10-18). **Corrected after Review 02** (M3T0-R2-F1 … F3 and IM-1; second log at the end; authorized by "Authorization: M3 T0 — Review 02 Corrections and Independent Review 03", 2026-10-18). **Corrected after Review 03** (M3T0-R3-F1; third log at the end; authorized by "Authorization I-4: M3 T0 — R3-F1 Correction and Independent Review 04", 2026-10-19). **Corrected after Review 04** (M3T0-R4-F1; fourth log at the end; authorized by "Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05", 2026-10-19). **Corrected after Review 05** (M3T0-R5-F1, R5-F2; fifth log at the end; authorized by "Authorization I-6 — M3 T0 Review 05 corrections only", 2026-10-19). **Update (2026-10-22, append-only): P10 DECIDED — Option (a)** under "I-16 — Decide DR-0029 P10 and Prepare T1 Authorization" (Tech Lead, 2026-10-22) (P10 section and Resolution). P1–P9 remain OPEN. Every other item is a proposal for the Tech Lead; no OPEN, DEFERRED or T0 → owner item elsewhere changes status because of this request. **Update (2026-10-25, append-only): P1–P5 and P7–P9 DECIDED; P6 NOT FULLY DECIDED (method (d) PROVISIONALLY SELECTED; geodetic-drag item ESCALATED_FOR_INVESTIGATION); the T2 dependency gate amended (Q-GATE)**, under "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25). Each decision is recorded verbatim in its section; see also the Resolution. The proposal text above each decision is preserved as written.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-18  
**Related milestone/issue:**
- M3 T0, authorized by "TARS — M3 T0 Reference-Configuration Spike Authorization" (I-15, 2026-10-18), §5.
- It answers the T0 obligations of:
  - DR-0027 (A-4, A-5, A-6, A-s, B-4);
  - DR-0025 (Q-G2-1, Q-G2-5, Q-G2-7);
  - DR-0024 (Q9 values).
- **Evidence:** VAL-0019 and `docs/science/experiments/m3-t0/` (result files cited as `atmosphere`, `decay`, `geodetic`, `frames`, `regression`, `gmat`, `termination` and `axis_ablation`, meaning `t0_<name>_results.json`).

Every number below was measured by the T0 spike unless it is marked **[derived]** or **[source]**. Values such as "80 km" in the evidence are **spike test values** used to exercise a mechanism. They are not proposed scenario values; DR-0027 A-3 prohibits a universal altitude.

## Summary of proposals
| # | Item | Recommendation | Needs |
|---|---|---|---|
| P1 | DR-0027 A-4: permitted termination altitudes | Rule-based admissibility, not a numerical range: h_f below the initial height, above a − b, and satisfying a stiffness bound ρ(h_f)·v̂·dt/B_min ≤ κ, with κ and the speed term v̂ chosen by the owner. A necessary numerical screen, not sufficient for the stage-domain or same-tick properties | Owner: rule, v̂ and κ. **DECIDED — A4-b, v̂ = V_b, κ = 0.01, I-26 (2026-10-25)** |
| P2 | DR-0027 A-5: crossing behaviour | End at the first committed state with h ≤ h_f (as `impact` does); report a cubic-Hermite crossing time; outcome `reentry`; missed dips documented | Owner. **DECIDED — A5-b, I-26** |
| P3 | DR-0027 A-6: domain edges and `impact` | `impact` unchanged and kept as a backstop; whenever `impact` holds, `reentry` holds too, and the same-tick precedence reports `reentry`; both can hold on one tick | Owner. **DECIDED — as proposed, I-26** |
| P4 | DR-0027 A-s: density for RK4 stages below the lower edge | (ii) fail closed | Owner. **DECIDED — (ii) fail closed, I-26** |
| P5 | DR-0027 B-4: unsupported altitudes | h < 0: fail closed (P4). 0–25 km: excluded by P1. 900–1000 km: accepted with documentation. Above 1000 km: top band extrapolated (GMAT-identical), labelled unverified; reference missions kept below 900 km | Owner. **DECIDED — region table with the wording amendment, I-26** |
| P6 | DR-0025 Q-G2-1: GMAT method | A decomposed exact configuration with a pinned setting list. Option (b) is feasible for J2 (0.076 mm), but adopting it in a validator needs a DR-0028 scope ruling. The geodetic-drag GMAT path is **escalated for investigation** | Owner, plus a DR-0028 scope ruling. **NOT FULLY DECIDED — (d) PROVISIONALLY SELECTED; geodetic drag ESCALATED; P6(b) ruling OPEN, I-26** |
| P7 | DR-0025 Q-G2-5: reference missions | RM-0 … RM-8 (table in P7), all exercised except RM-3b | Owner. **DECIDED — RM-0 … RM-8, I-26** |
| P8 | DR-0025 Q-G2-7: geodetic test points | Exact answers and forward-constructed points as the gate source; GeographicLib examples and GMAT as corroboration; the algorithm's domain stated | Owner. **DECIDED — (a) + (a′) with the reviewed gating restrictions, I-26** |
| P9 | DR-0024 Q9: C_d, A, mass, initial states | C_d 2.2 (illustrative). Vehicle V1: 850 kg, 15 m² (B 25.8 kg/m²). Vehicle V2: the M2 vehicle with A 15 m². Initial states per P7 | Owner. **DECIDED — Option (i), I-26** |
| P10 | New: J2 identity (decimal or C̄20) | Pin C̄20 as the source value, with J2 = −√5 C̄20 derived | Owner (before T1). **DECIDED — Option (a), I-16 (2026-10-22)** |

**T1/T2 readiness (recommendation, not authorization):**
- **T1 (J2):** no T0 item blocks it, once P10 is decided. *(2026-10-22: P10 decided, I-16; T1 still needs its own authorization.)*
- **T2 (drag):** BLOCKED until P1–P5, P8 and P9 are decided. *(2026-10-25: decided under I-26, and the governing T2 gate is amended to this list plus DQ-1 … DQ-6 (Resolution, Q-GATE). T2 still needs its own explicit authorization.)*
- **T4/T5:** need P6 and P7. *(2026-10-25: P7 DECIDED; P6 PROVISIONALLY SELECTED only, and its open items block geodetic GMAT acceptance in T5.)*

---

## P1 — DR-0027 A-4: permitted ranges of the per-scenario termination altitude h_f
**Problem.** A drag scenario must state h_f in metres, geodetic (A-1, A-2). Which values may it state?

**Evidence**
- **No source-backed physical limit exists** (DR-0027 A). T0 found none either; none is proposed.
- **Numerical stiffness.** The linearised drag decay rate is λ = ρ |v_rel| / B [derived; B = m/(C_d A); the largest eigenvalue of the drag Jacobian with respect to velocity]. Classical RK4 is stable on the real axis only for |λ dt| ≤ 2.785, and its local relative error is about (λ dt)⁵/120. Exact heights h* above which λ dt < κ at dt = 10 s (`termination` → `stiffness_thresholds`; root-found on the pinned table, to 0.01 m), for two speed terms v̂:
  - v_c = √(μ/(a + h)), the circular speed used originally. **It is a proxy, not a bound on |v_rel|.**
  - V_b = √(2μ/(b + h)) + ω_E (a + h) [derived], an upper bound on |v_rel| for every bound state at geodetic height h (negative two-body energy gives |v|² < 2μ/|r|, and b + h ≤ |r| ≤ a + h outside the ellipsoid).

  | B | v̂ | κ = 2.785 (stability) | κ = 1 | κ = 0.1 | κ = 0.01 |
  |---|---|---|---|---|---|
  | 25.8 kg/m² | v_c | 51 244.55 m | 59 825.08 m | 76 445.48 m | 90 185.09 m |
  | 25.8 kg/m² | V_b | 54 506.74 m | 62 842.26 m | 78 996.12 m | 92 282.07 m |
  | 100 kg/m² | v_c | 40 881.39 m | 48 614.81 m | 67 133.49 m | 82 337.14 m |
  | 100 kg/m² | V_b | 43 820.78 m | 51 724.77 m | 70 116.76 m | 84 596.12 m |

  The earlier 5 km grid (`atmosphere` → `stiffness_dt10`) reports the highest grid height still at or above κ, so it understates every threshold by up to 5 km. On the table, each threshold is a single crossing (one sign change on a 10 m grid from 0 to 400 km).

- **Decay from 180 km to the ground** (B 25.8, J2 + drag, RK4 at dt = 10 s against DOP853; `decay` → `rk4_divergence`):
  - the RK4 height error passes 1 m at 148 km;
  - it passes 100 m at 71.8 km (t = 20 680 s);
  - RK4 diverges at about 11–12 km (t = 21 070 s; the speed is no longer bounded);
  - DOP853 reaches geodetic 0 at 21 444 s (5.96 h).

  In this one decay case the speed falls during the plunge, so v_c overstates |v_rel| there. That is a property of this case, not of v_c in general (below).
- **Impact interaction [derived, exact].** For a point outside the ellipsoid, geodetic height h ≥ |r| − a (the ellipsoid lies inside the sphere of radius a), and h ≤ |r| − b. The v1/v2 `impact` condition |r| − a ≤ 0 therefore implies h ≤ a − b = **21 384.69 m**. If h_f > a − b, the termination height is reached no later than `impact` could fire.
- **The table domain starts at 0 km.** The 0–25 km band carries the disputed 0.13785 % base-altitude cell (DR-0027 B-2).

**Options**
- **A4-a: domain-only rule.** Require 0 < h_f < h_initial. Simple, but it admits h_f where RK4 at the scenario's dt is unstable or inaccurate (for example 25 km: λdt = 119 at B 25.8).
- **A4-b: rule-based admissibility.** Scenario validation rejects a drag scenario unless:
  1. a − b < h_f < h_geod(initial state);
  2. ρ(h_f) · v̂(h_f) · dt / B_min ≤ κ, where B_min uses the smallest mass the scenario can reach (dry mass), κ is a pinned project constant chosen by the owner, and v̂ is either v_c (as first proposed) or the bound V_b.

  Example consequences at dt = 10 s (exact thresholds, table above): κ = 0.01 admits h_f ≥ 90 185.09 m at B 25.8 and ≥ 82 337.14 m at B 100 with v_c, or ≥ 92 282.07 m and ≥ 84 596.12 m with V_b; κ = 0.1 admits ≥ 76 445.48 m and ≥ 67 133.49 m with v_c, or ≥ 78 996.12 m and ≥ 70 116.76 m with V_b. (λ dt at exactly 90 km, B 25.8, v_c is 0.01035, so 90 km itself is not admitted at κ = 0.01.)
  - *Pros:* no universal altitude. The bound follows each scenario's own B and dt, and it excludes the region where the measured RK4 error grows by orders of magnitude.
  - *Cons:* a new pinned constant κ; validation must evaluate the table at h_f.
- **A4-c: a fixed numerical range** (for example 80–200 km). Contrary to the spirit of A-3 (a universal number), and wrong for other B or dt.

**What A4-b guarantees (corrected after Review 01 F2).** A4-b is **necessary, not sufficient**. It screens out termination altitudes where drag stiffness makes RK4 at the scenario's dt inaccurate or unstable. It does **not** guarantee that RK4 stages stay above the lower edge, that `reentry` and `impact` cannot hold on the same tick, or (with v̂ = v_c) that λ dt ≤ κ for the actual state:
- **Stage domain.** A stress input that satisfies both clauses (h_f 21 500 m; equatorial start at 22 000 m moving straight down at 10 km/s; B 1e9 kg/m²; dt 10 s; negative two-body energy) puts the k2 input at −28 000 m. In fail-closed mode the step raises `OutsideDomainError`. In the diagnostic extrapolation mode, the stages are at −28 000, −28 243.6 and −78 347.7 m and the committed state at −78 392.7 m, where `reentry` and `impact` both hold (`termination` → `admissibility_counterexamples`). It is a stress test of the rule, not a proposed vehicle.
- **Speed proxy.** At the v_c threshold for κ = 0.01 (B 25.8), an equatorial retrograde perigee with e = 0.9 has |v_rel| = 11 292 m/s and λ dt = 0.01438 > κ. V_b (11 592 m/s there) covers it, and covers every bound state by construction.
- **A sufficient stage-domain condition [derived].**
  - Geodetic height is 1-Lipschitz (it is the signed distance to a convex surface), and the RK4 stage positions are r0 + (dt/2)v0, r0 + (dt/2)(v0 + (dt/2)a(y0)) and r0 + dt(v0 + (dt/2)a(y2)).
  - So every stage of a step from a committed state at h0 > h_f stays above the lower edge if h_f exceeds the bound computed in `termination` → `sufficient_stage_condition`. Domain: every committed state with negative two-body energy, any velocity direction, no thrust. h0 is the model's **computed** geodetic height of the committed state, the only height the simulator knows (corrected after Review 03 R3-F1). The bounds used (corrected after Review 02 R2-F2 and Review 03 R3-F1):
    - speed |v0| ≤ V = √(2μ/(b + H0)), where H0 = (h0 − β)/(1 + α) is a lower bound on the true height (ε_h below);
    - computed gravity with J2 ≤ (1 + u)·max(F_g, F_J)·(1 + 3J2(a/b)²)μ/b² anywhere outside the ellipsoid (F_g, F_J ≤ 1 + 3.8e-15 enclose the rounding of the model's gravity and J2 code);
    - computed drag ≤ the corrected envelope below, at each stage's lower true-height bound L and speed bound s;
    - the stage positions as computed in binary64: |fl(r0 + fl(c·k)) − r0| ≤ (1 + u)²c|k| + u|r0| (u = 2^-53, c = dt/2 or dt), so the lower true-height bounds L_k include u|r0|. A stage's computed height is ≥ M_k = (1 − α)L_k − β, and the condition requires M_k > 0 for every stage, so that no stage raises at the 0 m edge.
  - **Drag envelope over computed heights [derived under A-FP-1 … A-FP-3] (corrected after Review 03 R3-F1).** The model evaluates density at its computed height, not at the exact geodetic height. The table density is discontinuous and drops going up at 12 bases (50, 90, 110, 120, 140, 200, 250, 450, 600, 700, 900 and 1000 km). The Review 02 envelope bounded drag at exact heights only. A point whose computed height is 9.3e-10 m below 120 km, at a true height 2.3e-11 m above it, exceeded it by 7.8e-5 (relative); constructed points exceed it at all 12 bases (`check_review03.py`). The correction:
    - **Height-error bound ε_h [derived].** |h_computed − h_true| ≤ ε_h(h) = αh + β for every point outside the ellipsoid, with α = 1.22e-15 and β = 8.88e-9 m (ε_h = 9.02e-9 m at 120 km). Derivation (`t0_termination.rounding_allowances`, E1):
      - evaluated exactly at the returned latitude, the model's final height formula is the distance from r to the supporting plane of the ellipsoid with that normal. So it never exceeds the true height and is stationary at the geodetic latitude, and a latitude error δφ costs at most ½(|r| + a + a/√(1 − e²))δφ²;
      - δφ ≤ 1.43e-15 rad: the latitude iteration is a contraction with rate ≤ 0.00683 for every |r| ≥ b, and each step's rounding is bounded;
      - the rounding of the final formula, which subtracts two terms of size |r|, is bounded operation by operation: about 13u·a, which is β;
      - the kilometre conversion of the band selection adds u·h (E2), giving ε_sel.
    - **Envelope [derived].** For a true height h ≥ L, the band is selected at a height h_s ≥ L − ε_sel(L), and |r| ≤ a + (h_s + β_sel)/(1 − α_sel). The bound is the supremum over every selection height ≥ L − ε_sel(L) of F_D·ρ(h)·e^{θ_x X}·(s + ω_E(a + (h + β_sel)/(1 − α_sel)))²/(2B). Here ρ is the table formula with the file's decimal values, X is the exponent (h − base)/H of the band, and F_D = 1 + 2.4e-15 and θ_x = 3.3e-16 enclose the rounding of the density and of the drag force (E3, E4).
      - Every band that the computed height can select is therefore included.
      - Inside each band the function still decreases, because (1 − α)(1 − θ_x)a > 2H for every scale height H. So the supremum is at L − ε_sel(L) or at a band base above it, where GMAT's rule assigns the band above.
      - It is evaluated in 60-digit decimal arithmetic with outward pads and rounded up.
    - **Underflow [derived] (corrected after Review 04 R4-F1).** The Review 03 correction used a purely relative rounding model, which fails for subnormal results. Above about 181 890 km the table density is subnormal in binary64. At 190 681 km the model's drag was 2.01 times the envelope, because the coefficient's last division rounds 0.51 × 2^-1074 up to 2^-1074. The correction carries the absolute error of every underflowing operation (≤ 2^-1075 for a product or quotient, ≤ LIBM_ULP × 2^-1074 for a library function, including exp rounding to 0) through E1–E6:
      - in the height (E1) and the kilometre conversion (E2) these terms add about 1e-316 m to β; ε_h is unchanged in binary64;
      - the density gains an absolute error N_ρ ≤ 2.95 × 2^-1074 (E3). In the top band the computed density is exactly 0 above the selection height h_zero = 191 735 430.72 m, which is 9.5e-8 m above the oracle's exact onset;
      - the envelope gains an absolute part (F_A·N_ρ/(2B) + K_W·W)·S_max² + K_1·2^-1075·S_max + 2^-1074 (E4). Here W ≈ 1.06 × 2^-1075 is the coefficient's underflow, dominated by its last division, and S_max = s + ω_E·(a + (h_zero + β_sel)/(1 − α_sel)) is the largest speed term at which the computed density can be nonzero. It is about 6.0e-316 m/s² at B 25.8 and s = 0, and 1.9e-315 m/s² at s = 11 km/s;
      - gravity with J2 gains 4 × 2^-1075 m/s² (E5), and the RK4 stage positions and velocities 2 × 2^-1075 (E6);
      - the vehicle enters the envelope only through cd·area/mass. The Review 04 correction bounded it by φ_B/B, a relative-only rounding of the conversion between B and the mass. **Corrected after Review 05 R5-F1:** the bound carries the absolute error of every rounding of the conversion that may underflow (E4a), for both constructions used: b = fl(mass/fl(cd·area)) (B 25.8) and mass = fl(fl(b·cd)·area) (B 100). The bound R = max(φ_B/B, R1, R2) equals φ_B/B wherever the conversion is normal, so the envelope for B 25.8 and B 100 is unchanged. The Review 05 vehicles (B = 2^-1074, mass 17 and 30 × 2^-1074 kg, at 180 000 km) had drag 1.94 and 1.10 times the superseded envelope, and now 0.971 and 0.550 of the corrected one. A vehicle with cd·area ≤ 2^-1075, which the first construction maps to B = +∞ (the drag-free envelope, 0), has exactly zero force (E4b). No vehicle condition is introduced. A vehicle whose mass/fl(cd·area) overflows to +∞ is outside the domain, as every overflow is. **Corrected after Review 06 R6-F1:** the first construction can round a positive mass to B = 0 (mass/fl(cd·area) ≤ 2^-1075, for example mass ≤ 16 × 2^-1074 kg with cd·area = 33 m²). The model's drag is then finite and nonzero, but the E4a derivation assumed B ≥ 2^-1074 and the envelope divided by zero. For B = 0 the bound uses only mass ≥ 2^-1074, which every positive binary64 mass satisfies: R(0) = max(cd·area/2^-1074, R(2^-1074)). The first term is attained at mass = 2^-1074 whenever fl(cd·area) ≥ 2; the max keeps R non-increasing in B. The envelope's coefficient φ_B/R(0) is positive and rounded down. For the Review 06 masses (k × 2^-1074 kg, k = 1 … 16, at 180 000 km) the model's drag is 0.9999999999988 (k = 1) down to 0.0625 (k = 16) of the corrected envelope; k = 17 (B = 2^-1074) is unchanged at 0.971. Every B > 0, the three bounds and every pre-existing termination result are unchanged to the last bit. An input outside the domain (B NaN or negative; cd or area not positive and finite) raises an error and never receives a bound, and an envelope of +∞ certifies nothing (the stage condition then reports need ≥ 0, not certified; corrected after Review 07 M3T0-R7-F1: need = −M2, finite and ≥ 0, when M2 ≤ 0 (up to h0 = 55 749.393 m with the published constants, for every B; M2 does not depend on the envelope), and need = +∞ when M2 > 0). **Qualified after Review 08 M3T0-R8-F1:** every value the stage condition returns needs a computed h0 > β (8.88e-9 m); a computed h0 ≤ β raises `ValueError` before the M2 test, for B_V1 and the drag-free vehicle alike, and strictly exterior states reach such heights (r = [a + k·2^-30, 0, 0] m, k = 1 … 9). The rejection certifies nothing.

      The reviewer's point now has drag 1.020e-315 against an envelope of 1.111e-315 m/s². Two empirical observations, not bounds (scope corrected after Review 05 R5-F2). Over the coefficient-rounding subset (equatorial points from 300 km below to 10 km above the position where the model's drag coefficient rounds up from about 0.5 × 2^-1074 to 2^-1074, retrograde speeds 0, 2 and 11 km/s; `check_review05.py`), the largest ratio of model drag to envelope is 0.983 (B 100; 0.953 for B 25.8). Over the subnormal-density points of the committed transition scan (`check_review04.py`) it is 0.99999999999886 (B 25.8) and 0.99999999999885 (B 100). Just below the smallest normal density the absolute terms are negligible, and the relative envelope is as tight there as for normal densities. No new altitude restriction is introduced: the supported domain is unchanged (outside the ellipsoid, no overflow).
    - **Assumptions (unresolved; the guarantee holds only under them). Corrected after Review 04 R4-F1:** A-FP-1 and A-FP-3 previously stated a purely relative model, and A-FP-2 a purely relative libm error. Both fail for subnormal results.
      - A-FP-1: IEEE 754 binary64 with round-to-nearest-even and **gradual underflow** (no flush-to-zero or denormals-are-zero mode). For × and ÷, fl(x op y) = (x op y)(1 + δ) + η with |δ| ≤ 2^-53, |η| ≤ 2^-1075 and δη = 0. A sum that underflows is exact, a square root is never subnormal, and a result of magnitude ≤ 2^-1075 rounds to 0. This follows from IEEE 754 itself. Whether a platform runs in that mode is checked at run time by `check_review04.py`, on the model's own operations at the R4-F1 point. It has been checked on macOS x86_64 only, because CI does not collect the T0 checks.
      - A-FP-2: libm sin, cos, atan2, hypot, exp and pow satisfy |computed − exact| ≤ LIBM_ULP × 2^-52·|exact| + LIBM_ULP × 2^-1074 with LIBM_ULP = 2. The absolute term covers subnormal results and exp rounding to 0. No relative bound is assumed there. This is an assumption about the platform library, not proved. It is measured on macOS x86_64 (the M1/M2 reference host) only (`t0_height_error.py`):
        - cos reaches 0.94 × 2^-52 relative (1.41 ulp), so the common "within 1 ulp" does not hold;
        - for subnormal results, the largest absolute errors are 0.74 (exp), 0.59 (hypot) and 0.50 (atan2) × 2^-1074.
      - **How far A-FP-2 can be weakened [derived; `termination` → `libm_sensitivity`].** Every derived constant is non-decreasing in LIBM_ULP. A floor that holds for LIBM_ULP = 2^j therefore holds for every libm within 2^j ulps. Results:
        - the published bounds (the bracket ends below) hold for every libm within 2^5 (B 25.8), 2^6 (B 100) and 2^7 (drag-free) ulps;
        - the 2-decimal values rounded up (124 456.69, 118 633.51 and 111 511.97 m) hold within 2^19, 2^17 and 2^20 ulps.

        [source] The glibc manual ("Errors in Math Functions", sourceware.org, read 2026-10-19) says the library "does not aim for correctly rounded results". It aims for "a few ulp", and its testsuite flags only errors above 9 ulp. That is a statement of intent, not a bound, but it lies within the 2^5 ulps that the published bounds tolerate. No Apple libm accuracy statement was found.

        The guarantee therefore remains conditional on a libm accuracy assumption. That assumption can be weakened from 2 ulps to the figures above. It is not established for any platform other than the one measured.
      - A-FP-3: numpy evaluates the 3-element products elementwise. The 3-term dot product x·x is within γ₃·Σx_i² + 3(1 + u)²·2^-1075, in any order, with or without fused multiply-add.
      - **E4b's zero-force cap [derived under A-FP-1 and A-FP-2; corrected after Review 06 R6-F3]:** c₀ ≤ 5/8 depends on A-FP-2. The cap c₀ = fl(0.5·ρ̂) ≤ (F_ρ·e^η₀·ρ₀,max + N_ρ)/2 + η₀ uses the density allowance, which carries the libm error of exp. It is 0.6125000000000005 at LIBM_ULP = 2 and holds for LIBM_ULP ≤ 91910196476947 (about 2^46.4); it is not libm-independent. E4a uses no libm call.
    - **Observed, not proved:** the largest height error over 13 050 sampled points is 2.06e-9 m, 0.22 of ε_h (`t0_height_error.py`).
  - **Monotonicity [derived].** H0 and every L_k increase with h0 (the coefficient of h0 is 1/(1 + α) − u/(1 − α) > 0), V decreases, and the envelope is non-increasing in its lower height and non-decreasing in its speed. So every M_k increases with h0, and the condition has a single root: every computed h0 above it satisfies the condition. The published bound is the upper end of a bisection bracket at which the outward-rounded condition holds.
  - For unrestricted bound states at dt = 10 s the bound is 111 511.96 m drag-free, 118 633.51 m at B 100 and 124 456.69 m at B 25.8. The bound for a B also covers every larger B.
    - **Quoted to the nearest centimetre (clarified after Review 04, I-5 §3).** The governing values are the bracket ends 111 511.96182508787, 118 633.50894662621 and 124 456.68544510857 m. The first rounds down: 111 511.96 m lies 1.8 mm below the drag-free bound and does not itself satisfy the condition. A sufficient 2-decimal value is 111 511.97 m. No bound changed. How bounds are quoted in a decision is for the owner.
    - **Effect of the R5-F1 correction:** none on the bounds. For B 25.8 and B 100 the conversion is normal and the envelope receives the same B, so every value in the termination results is unchanged to the last bit, including the three bounds, their root brackets and their margins.
    - **Effect of the R4-F1 correction:** the three published bounds are unchanged to the last bit. The roots are unchanged to 1e-9 m: the corrected and Review 03 brackets coincide, for example [124 456.68544484391, 124 456.68544484489] m. The margins at the published bounds are 7.2e-7, 1.0e-6 and 8.4e-7 m (`termination` → `floor_comparison`). **Effect of the R3-F1 correction:**
    - the exact roots move up by 1.9e-8 m;
    - the published values (bracket upper ends, ≤ 1e-6 m above the root) move up by 2.8e-7, 5.3e-7 and 8.5e-7 m against Review 02;
    - all three are unchanged at the quoted precision, and **the P1 recommendation is unchanged**.
  - **Checked independently** (`check_review02.py`, `check_review03.py`, `check_review04.py`, with heights and densities from an independent high-precision oracle, `t0_oracle.py`):
    - across the normal-to-subnormal transition of the top band (181 000–193 000 km), at binary64 neighbours of the smallest-normal density, of the model's coefficient rounding and of the rounding-to-zero boundary, the model's drag stays within the corrected envelope. These points cover zero, near-escape, 11 km/s and straight-down velocities, and include the R4-F1 point and constructed points that exceed any purely relative enclosure. Above h_zero the computed density and drag are exactly 0;
    - every band base (all 27 and the lower edge), with binary64 neighbours and true heights just below and above;
    - RK4 steps from high-altitude retrograde, near-escape and straight-down bound states keep every stage within its bounds, and every stage force within the bounds the condition uses;
    - a second implementation reproduces the underflow constants, the envelope, the three bounds and the libm sensitivity;
    - for 243 vehicles formed by either construction, with subnormal and normal B, products cd·area and intermediate products b·cd, cd·area/mass stays within the E4a bound, against exact rationals and the rounding intervals of round-to-nearest. A second implementation reproduces the bound and the envelope that uses it. The model's drag stays within the corrected envelope from 100 000 to 191 700 km, and vehicles with cd·area ≤ 2^-1075 have exactly zero force (`check_review05.py`);
    - after Review 06 (R6-F1): the 17 Review 06 masses; every C1 mass k × 2^-1074 kg, k ≤ 20 000, on 10 shapes (fl(cd·area) from below 2 to near the largest binary64, subnormal cd with a huge area), B = 0 included; the B = 0 / B = 2^-1074 transition on each shape; and the model's drag within the envelope at B = 0, against exact rationals and a second implementation (`check_review06.py`);
    - a second implementation reproduces the three bounds of the corrected derivation to 3e-6 m;
    - at all 12 downward jumps, exact-base and adjacent binary64 points, true heights just below and above the base, and points whose computed and true heights select different bands stay within the corrected envelope;
    - RK4 steps from near-escape, retrograde and straight-down bound states at the bounds and near the jumps keep every stage's oracle height above its lower bound;
    - in `termination` → `sufficient_stage_condition` → `stress`, 2000 states per vehicle stay above every stage's guaranteed computed-height bound (smallest margin 0.10 m).

    These are tests of the derivation, not part of it.
  - It is sufficient, not necessary.
  - A sharper guarantee needs a restriction of the admissible initial states (for example of the inward velocity). That restriction is an owner decision and is not proposed here.
- **Consequence.** An A4-b-admissible run that violates these properties still has a defined outcome: a stage below the lower edge ends the run under P4, and a same-tick `reentry`/`impact` is resolved by the P3 precedence.

**Numerical implications (this decay case only).** In the 180 km decay run (B 25.8, dt 10 s), every spike floor from 90 to 150 km was entered with RK4 stages ≥ h_f − 600 m (`decay` → floors 90–150 km: −122 … −599 m), far above the lower edge. This is a measurement of one trajectory, not a property of every admissible run.

**Risks**
- With v̂ = v_c the formula underestimates λ for eccentric or retrograde states (above). V_b removes that, at the cost of thresholds about 2–3 km higher.
- κ is engineering judgment, labelled as such.
- A burn lowers B; the rule uses dry mass to cover that.

**Recommendation.** A4-b with v̂ = V_b, stated as a necessary screen whose residual cases end by P3 and P4. The owner chooses κ and v̂. The implementer's suggestion is κ = 0.01, because it keeps RK4's local relative error from drag stiffness near 1e-12; that figure is a derived estimate, not a measurement. Clause 1 is kept explicitly even though κ = 0.01 already implies it at these B values.

**Owner decision (2026-10-25, append-only): DECIDED — A4-b, v̂ = V_b, κ = 0.01.** Authority: "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25), §2 P1. Recorded verbatim:

> **DECIDED: A4-b.**
>
> Use:
>
> - v̂ = V_b, the derived bound for bound-state relative velocity.
> - κ = 0.01.
> - Clause 1: a − b < h_f < h_geod(initial).
> - Clause 2: ρ(h_f) × V_b × dt / B_min ≤ 0.01.
>
> The ballistic coefficient uses dry mass.
>
> Record that this is a necessary admissibility screen, not a sufficient numerical stability or trajectory-accuracy guarantee.
>
> The derivation bounds the drag velocity-Jacobian contribution only. It does not bound the full coupled dynamics or ∂a/∂r.
>
> κ is an owner-selected engineering constant, not a physically established universal threshold.
>
> The final M3 timestep remains a separate decision.

**Implementer notes on the record (no change to the decision):**
- V_b is evaluated at h_f, as defined in the Evidence above: V_b(h_f) = √(2μ/(b + h_f)) + ω_E(a + h_f). B_min = m_dry/(C_d A).
- **Consequences, not decided values.** At the provisional dt = 10 s, clause 2 admits h_f ≥ 92 282.07 m (B 25.8) and ≥ 84 596.12 m (B 100) [measured, `termination` → `stiffness_thresholds`]. They move with dt (DR-0025 Q-G2-4, PROVISIONAL) and with each scenario's B_min. No altitude is approved (DR-0027 A-3 stands).
- The derived sufficient stage-domain floors (111 511.97 / 118 633.51 / 124 456.69 m) are **not** part of the rule. They remain evidence, conditional on A-FP-1 … A-FP-3 and specific to the spike's arithmetic (decision packet N-1).
- Implementation: scenario validation at T3. Where κ is pinned is a T3 design detail. **Not authorized by I-26.**

## P2 — DR-0027 A-5: event-crossing behaviour
**Problem.** How is a crossing of h_f detected and located between committed states, and what does the run report?

**Evidence** (`decay` → `floors`, ten spike floors, B 25.8, dt = 10 s; truth = DOP853 events on the same model)

| Method | Crossing-time difference from DOP853 | Notes |
|---|---|---|
| First committed state with h ≤ h_f | −0.29 … +9.26 s | The final state is up to 3.06 km below h_f (50 km floor), 1.72 km at 80 km, 39 m at 150 km |
| + scalar cubic Hermite on h, with dh/dt = n̂·v at both ends | −0.07 … −0.41 s | No extra force evaluation. Same technique as the existing ascending-node detector |
| + vector cubic Hermite of r, then h of the interpolant | equal to the scalar method within 1.9e-4 s | — |

- **The Hermite residual is the RK4 trajectory's own timing error**, not interpolation error. The two Hermite variants agree to 1.9e-4 s while both differ from DOP853 by up to 0.41 s, the RK4 truncation error at dt = 10 s.
- **GMAT, independently:** GMAT's own stop at geodetic 80 km happens at 20 640.941 s, against the spike's 20 640.965 s (`gmat` → `decay`, Δ = −0.023 s).
- **Missed crossings (corrected after Review 01 F1).** A trajectory can dip below h_f between two committed states and come back.
  - **Bound [derived].** For any step of length dt, the dip below the lower committed height is at most (dt²/8) · sup max(ḧ, 0) over the step. Outside the ellipsoid, ḧ ≤ n̂·a + |v_t|²/(h + b²/a), where:
    - n̂ is the geodetic normal and v_t the velocity tangent to the level surface;
    - b²/a = 6 335 439.33 m is the smallest radius of curvature of the WGS 84 ellipsoid.

    For two-body motion this gives a bound over the whole orbit that depends only on the perigee radius, e and dt (`termination` → `missed_crossing`):

    | Perigee | e = 0 | 0.005 | 0.01 | 0.02 | 0.04 | 0.1 |
    |---|---|---|---|---|---|---|
    | 80 km | 0.80 m | 1.40 m | 2.00 m | 3.20 m | 5.61 m | 12.82 m |
    | 150 km | 0.77 m | 1.36 m | 1.95 m | 3.12 m | 5.48 m | 12.54 m |
    | 250 km | 0.74 m | 1.31 m | 1.88 m | 3.02 m | 5.30 m | 12.15 m |

    It scales with dt². The two-body maximisation over [r_p, r_a] is in closed form (the endpoints and the real roots of a cubic), so these values are certified up to floating-point rounding; a second maximisation method agrees to 1e-12 relative.
  - **Perturbed motion (corrected after Review 02 R2-F1): no certified bound is derived in T0.** The chord inequality still holds, but evaluating sup ḧ over a J2 + drag orbit needs an enclosure of a numerical trajectory, which T0 does not construct. The values below for J2 + drag are each a **sampled estimate**: dt²/8 × the maximum of the pointwise bound over samples of a numerical trajectory. Such an estimate is not a bound. Refining between the 0.25 s samples raises it by up to 8.6e-10 m (180 km circular, 51.6°; the reviewer's case).
  - **Measured.** With the lowest point at mid-step, a 250 × 800 km orbit (e = 0.0398, i = 51.6°) dips **4.99 m** (Kepler; certified bound 5.28 m) and **4.82 m** (J2 + drag; sampled estimate 5.11 m, not a bound). A circular 250 km, 51.6° orbit dips **0.45 m** at the equator crossing (certified bound 0.74 m), from the ellipsoid's curvature alone.
  - A sweep covers 9 orbits (circular to 250 × 2000 km; i = 0, 51.6 and 97°), two-body and J2 + drag, and 40 sampling phases.
    - **Two-body rows:** no measured dip exceeds the certified bound; the smallest margin is 0.025 m and the largest dip is 13.30 m at 250 × 2000 km.
    - **J2 + drag rows (empirical):** the largest dip is 13.33 m at 250 × 2000 km. Every measured dip is below the sampled estimate for its row (smallest gap 0.036 m) and below the certified two-body bound of its initial osculating orbit (smallest gap 0.087 m). These are observations on 9 orbits, not a guarantee for perturbed motion.
  - The earlier figure of 1.56 m (`decay` → `missed_crossing`) is the maximum at one fixed sampling phase. It is a measurement, not a bound.

**Options**
- **A5-a:** committed-state detection only (the v1/v2 `impact` semantics); report the committed state.
- **A5-b:** A5-a, plus a refined crossing time by scalar cubic Hermite on h, reported in the event. The run still ends at the committed state.
- **A5-c:** split the last step to land on h_f (root finding inside the step loop).
  - A new numerical component, akin to DR-0025 Q-G2-3 (b), which was not approved.
  - It changes the final state's definition.

**Proposed outcome and fields** (names remain proposals until the v3 contract is designed at T3, DR-0027 A):
- outcome `reentry` (DR-0026 §5.6);
- `termination_altitude_m` (the configured h_f);
- `crossing_t_s` (Hermite);
- the committed final tick and t;
- the geodetic height of the committed final state;
- a method identifier (for example `hermite_h_v1`) so the definition is versioned with the physics identity.

**Risks**
- Missed dips are not detected. At dt = 10 s the certified two-body bound is 0.74–0.80 m for circular orbits (perigee 80–250 km) and about 5.3–5.6 m for e = 0.04. It grows with e and with dt². For J2 + drag no bound is established; the sweep's observations are empirical (above).
- A5-b reports a time that does not belong to a committed state, so consumers must not read it as a state.

**Recommendation.** A5-b, with missed dips documented as a known limitation and not detected. In a decaying orbit the next pass crosses lower. The recommendation does not rely on a perturbed-motion bound. Any use that needs a guaranteed missed-dip magnitude for J2 + drag (for example a contract field or a gate) has no supporting bound in T0 and stays blocked until one is derived.

**Owner decision (2026-10-25, append-only): DECIDED — A5-b.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P2. Recorded verbatim:

> **DECIDED: A5-b.**
>
> Detect termination from committed states and report an additional scalar cubic-Hermite estimate of the crossing time.
>
> The simulation ends at the committed state, not the interpolated crossing.
>
> The reported crossing time is not a propagated state.
>
> No final-step splitting is authorized.
>
> Missed crossings or dips between committed states remain a documented limitation. Do not claim a certified perturbed-motion missed-dip bound.
>
> T2 must expose the geodetic normal or latitude required for T3 to compute dh/dt.

**Implementer notes on the record (no change to the decision):**
- The field names proposed above (`termination_altitude_m`, `crossing_t_s`, the method identifier) remain T3 contract proposals (DR-0027 A, "Names").
- The certified two-body missed-dip table stays as recorded. No J2 + drag bound exists (Review 02 R2-F1); any use needing one stays blocked.
- The last sentence is a **T2 interface requirement** (decision packet N-3). Implementation needs the separate T2 authorization.

## P3 — DR-0027 A-6: interaction with domain edges and `impact`
**Evidence**
- a − b = 21 384.69 m [derived]. At the 25 km spike floor, the spherical altitude at the crossing was 22.3 km at latitude −15.8° (`decay`), consistent with the inequality in P1.
- **The 250 km band base coincides with the M1 reference orbit's altitude.**
  - GMAT computed 249.9999999999982 km for that state and selected the 200 km band; the spike computed exactly 250 000.0 m and selected the 250 km band (`gmat` → `trajectories`).
  - With geodetic height the orbit changes band 29–39 times in 10 orbits (P7).
  - At an exact base, the selected band is decided by round-off in any implementation.
- **GMAT's band rule** (h ≥ base[k] selects band k) is confirmed at ±1 km around all 27 boundaries to the probe bias of 1.43e-7 (`gmat` → `density_probes`). Probes exactly on a base mix both bands inside GMAT's integrator stages.

**Proposal**
1. `impact` (spherical ≤ 0, SCI-0006) is unchanged and stays active in v3 as a backstop. At any committed state where `impact` holds, |r| ≤ a gives h ≤ a − b < h_f, so `reentry` holds too [derived]. With the precedence of item 2, `impact` is therefore never the reported outcome while h_f > a − b.
2. Same-tick precedence, deterministic: `non_finite` → `reentry` → `impact` → `escape`. **P1 does not prevent `reentry` and `impact` from holding on the same tick** (Review 01 F2 stress input: the committed state at −78 392.7 m satisfies both); the precedence decides the outcome.
3. Termination uses height only. It never depends on which band a base height selects.
4. The round-off ambiguity at an exact base is a property of the published model (DR-0024 Q5a), not a defect. Reference-mission design should treat it explicitly (P7).

**Owner decision (2026-10-25, append-only): DECIDED — the proposal above (items 1–4).** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P3. Recorded verbatim:

> **DECIDED: Adopt the DR-0029 proposal.**
>
> Precedence:
>
> 1. `non_finite`
> 2. `reentry`
> 3. `impact`
> 4. `escape`
>
> Preserve `impact` as the legacy backstop.
>
> Termination is determined from geodetic height, independently of atmospheric band selection.
>
> Preserve the published density discontinuities.
>
> This decision specifies future T3 behavior; do not implement it under I-26.

**Implementer notes on the record (no change to the decision):**
- Item 1's implication (`impact` ⇒ `reentry`) holds because P1 clause 1 is decided (h_f > a − b).
- The decision text names the outcome `reentry`. DR-0027 A's row "the outcome name `reentry` remain[s a] proposal until the v3 schema is designed" is not explicitly superseded by I-26. T3 contract design confirms the identifier (open-issues register OI-23). The precedence order itself is decided. *(Superseded by the I-27 correction below (M3T2OD-R1-F1): the outcome name `reentry` is DECIDED and is not reconfirmed at T3. The sentence is kept as originally written.)*
- T2 consequence: the geodetic-height function never branches on band selection.

**I-27 correction (2026-10-25, append-only; Review 01 M3T2OD-R1-F1).** Authority: "TARS — Authorization I-27: M3 Owner Decisions: Review 01 Corrections and Independent Review 02" (owner/Tech Lead, 2026-10-25), §2. It records no new decision; it removes a qualification that weakened the I-26 decision above.
1. **The outcome name `reentry` is DECIDED** (I-26 §2 P3, precedence item 2).
2. **The P3 precedence `non_finite` → `reentry` → `impact` → `escape` is DECIDED.**
3. **T3 implements these decisions; it does not approve or reconfirm them.**
4. T3 may define implementation-specific fields and serialization details (for example `termination_altitude_m`, `crossing_t_s`, the method identifier) **only within this already approved contract.**
5. **Any future change to the outcome name or the precedence requires a separate owner decision.**

The implementer note above ("… not explicitly superseded by I-26. T3 contract design confirms the identifier …") is superseded to that extent and kept as written. DR-0027 A's "Names" row is superseded for the **outcome name only**: field names remain T3 design within the contract. No other P3 behaviour changes, and nothing is implemented.

## P4 — DR-0027 A-s: density for an RK4 stage below the lower edge
**Evidence**
- **RK4's third stage (the input of k3) sits below the committed path in LEO** [derived from the stage formula]. It evaluates r + (dt/2) v₂ with v₂ = v + (dt/2) a, which lies about g (dt/2)² − v² (dt/2)²/(2r) ≈ 117 m inside the arc at dt = 10 s.
  - At the 180 km state the stage inputs sit at +116.31 m (k2), −115.73 m (k3) and +1.16 m (k4) from the initial height (`termination` → `stage_order`).
  - Measured in the 180 km decay case: 115.7–117.7 m below the lower committed height in every 10 km band from 120 to 180 km (`decay` → `stages`).
  - During that case's plunge (50–110 km) the stages stay above the lower committed height.
- **In the crossing step,** stages went at most 599 m below h_f for spike floors 90–150 km, and 3.05 km below at 50 km.
- **GMAT R2026a fails closed:** a probe 1 m below the ellipsoid stops the run with "Exponential atmosphere: Position vector is inside central body" (`gmat` → `density_probes` → `below_zero_probe`).

**Options**
- **(i)** Evaluate the lowest band's formula for stages below the lower edge; the committed-state check ends the run.
- **(ii)** Fail closed: a run error with a defined cause.

**Analysis**
- **Where the options differ (corrected after Review 01 F2).**
  - In the measured decay case no stage came near the lower edge: for floors 90–150 km, stages stayed at least 89.4 km above it.
  - P1 alone does not guarantee this. A P1-admissible stress input puts the k2 input at −28 km (P1, "What A4-b guarantees"). For such a run, option (i) evaluates the lowest band below its domain and continues to the committed-state checks (there, a state at −78.4 km where `reentry` and `impact` both hold). Option (ii) ends the run with a defined failure.
  - The two options give identical runs whenever no stage goes below the lower edge, which is guaranteed for h_f above the derived sufficient condition (≈ 111.5–124.5 km at dt = 10 s for unrestricted bound states, P1), under the floating-point assumptions A-FP-1 … A-FP-3 stated there (corrected after Review 03 R3-F1, Review 04 R4-F1 and Review 05 R5-F1).
- Option (i) would silently extend the model below its domain, against DR-0024 Q8, "no indefinite extrapolation below the modelled domain", and against GMAT's behaviour.
- Option (ii) makes a misconfiguration (or a defect that produces such a state) visible.

**Recommendation.** (ii) fail closed. The cause name is designed at T3; a candidate is a new additive `failure_cause` value such as `outside_atmosphere_domain`.

**Owner decision (2026-10-25, append-only): DECIDED — Option (ii), fail closed.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P4. Recorded verbatim:

> **DECIDED: Option (ii), fail closed.**
>
> Any finite geodetic height below 0 m must cause a typed atmosphere-domain error.
>
> The domain guard must compare height in metres before conversion to kilometres.
>
> Negative zero is in range.
>
> Non-finite heights receive a distinct error classification.
>
> A failing RK4 stage must not commit a partial simulator state.
>
> Explicitly reconcile DR-0026 AR-8 and §5.8: statements that density is total do not apply below the atmospheric table's lower edge.
>
> T3 will define the versioned run-outcome mapping. Do not implement that mapping now.
>
> Do not reproduce the T0 spike's negative-subnormal guard defect.

**Implementer notes on the record (no change to the decision):**
- **Reconciliation recorded:** DR-0026 "I-26 note" states that AR-8's "runtime functions are total" and §5.8's "density is total" do not apply below the table's lower edge (0 m geodetic). DR-0024 §4.6's candidate "extrapolate the lowest band" is not adopted (DR-0024 "I-26 note").
- **Guard, as specified** (decision packet P4 items 8 and 14, Review 03 PASS): finite h_m < 0 raises, by IEEE comparison of the metres value before any conversion. h_m = −0.0, +0.0 and +5e-324 are evaluated in band 0. Non-finite h raises a distinct error first. The T0 spike's km-route trap interval (−2.475e-321 < h_m < 0, open-issues register OI-21) is the defect not to be reproduced. No T0 file or result changes.
- **Atomicity:** the existing atomic step leaves state, tick and engine schedule unchanged when a stage raises (validation strategy I-6). `Simulator.step` does not catch the new error; the T3 mapping is not implemented now.
- Error class names are a T2 design detail.

## P5 — DR-0027 B-4: domain behaviour at unsupported altitudes
| Region | Evidence | Proposal |
|---|---|---|
| h < 0 (below the lower edge) | GMAT fails closed (P4) | Fail closed (P4) |
| 0 ≤ h < 25 km (disputed base cell, −0.13785 %; largest jump, +1.36e-3 at 25 km) | `atmosphere` → `boundaries` | Not an admissible h_f under P1 at the B values studied, for any κ up to RK4's stability limit (thresholds ≥ 40 881.39 m). Stages and the final committed state can still reach it (P1, "What A4-b guarantees"). Evaluated as published if reached, with no repair (B-3) |
| 25–900 km | 25 rows identical to the author's file (DR-0024 §3.4); GMAT density matches the spike in every band (`gmat` → `density_probes`) | Normal domain |
| 900–1000 km (scale height 181.05 vs 181.045 km) | Density consequence ≤ 1.5e-5 (DR-0027 B-2) | Accept; document |
| ≥ 1000 km (top band, unverifiable row) | GMAT extrapolates the top band; the spike matches it at 1001, 1100, 1500 and 2000 km to the probe bias. Against the author's file: +19.6 % / +145 % / +500 % at 1100/1500/2000 km (DR-0027 B-2) | Extrapolate the top band (continuous, GMAT-identical). Every record says that density above 1000 km is unverified. No M3 reference mission goes above 900 km (P7) |

**Alternatives for ≥ 1000 km**
- **Fail closed** above 1000 km: strict, but it ends real trajectories that briefly cross the top.
- **ρ = 0 above a cutoff:** rejected already (DR-0024 §12) because it introduces a discontinuity.

**Numerical implication [derived].** At 1000 km and B 25.8 the drag acceleration is about 3e-9 m/s². A ±500 % density error there changes a 10-orbit trajectory by metres only if the spacecraft stays above 1000 km for the whole run.

**Owner decision (2026-10-25, append-only): DECIDED — the P5 region table, with the wording amendment.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P5. Recorded verbatim:

> **DECIDED: Adopt the DR-0029 P5 region table**, consistently with P1 and P4.
>
> For heights above the 1000 km base, extrapolate the pinned top atmospheric band. Do not introduce a zero-density cutoff or a new upper-domain failure.
>
> Preserve the pinned density table exactly.
>
> Adopt the proposed wording amendment:
>
> The top band's formula is continuous for h > 1000 km, but the 1000 km base retains its published relative density jump of approximately −1.598 × 10^-5.
>
> Do not impose continuity across band boundaries.
>
> Retain the published GMAT band-selection rule and exact-base behavior.
>
> Explicitly label extrapolated densities above 1000 km as unverified.

**Governing reading of the table (append-only; the table text above is unchanged):**
- **h < 0:** fail closed (P4).
- **0 ≤ h < 25 km:** evaluated as published, no repair (DR-0027 B-3). Not an admissible h_f under P1 (κ = 0.01; thresholds ≥ 84 596.12 m at dt 10 s for B ≤ 100). Stages and committed states can still reach it.
- **25–900 km:** normal domain.
- **900–1000 km:** accepted and documented.
- **≥ 1000 km:** the top band's formula, extrapolated, labelled **unverified** in every record. No zero-density cutoff and no upper-domain failure. Subnormal densities and exact zeros far above the table (T0 R4-F1) are returned, not raised.
- **The ≥ 1000 km cell's "(continuous, GMAT-identical)" is read as amended by the owner:** the top band's formula is continuous for h > 1000 km; the 1000 km base keeps its published relative jump (≈ −1.598e-5), as every base keeps its own. GMAT's band rule (h < base[i+1] selects band i; an exact base belongs to the band above) applies unchanged.
- No M3 reference mission goes above 900 km (P7).

## P6 — DR-0025 Q-G2-1: GMAT exact-configuration method
**Evidence** (`gmat`; 53 700 s from the M1 state unless noted; spike = DOP853 rtol 1e-13, converged to µm; GMAT = PrinceDormand78, accuracy 1e-13, maximum step 60 s)

| Configuration | GMAT vs spike (J-ax-1): final / maximum | GMAT vs spike driven by GMAT's axis (diagnostic) | Attribution |
|---|---|---|---|
| J2 only, `Earth.NutationUpdateInterval` = 60 s (GMAT default) | 0.273 / 1.05 m | 0.083 m, along-track only | The default holds GMAT's Earth-orientation matrix for 60 s |
| **J2 only, `NutationUpdateInterval` = 0** | **0.192 / 1.03 m** | **0.076 mm** | **Fully attributed:** GMAT's Earth-fixed +Z (polar motion: a 0.349″ circle per sidereal day around the celestial pole, measured) |
| Drag, one-band table, spherical height | 2.05 mm | 2.05 mm | Axis-independent floor; not further attributed |
| Drag, full table, spherical height | 1.98 mm | 2.01 mm | Same floor |
| Drag, full table, geodetic, interval 60 s | 0.186 m | 0.040 m; **4.2 mm** with GMAT's 1e-7 rad height rule | Attributed: polar-motion tilt of GMAT's ellipsoid, plus GMAT's height stopping rule (≤ 1.4 mm in height, `geodetic`) |
| Drag, full table, geodetic, interval 0 | 0.327 m | 0.175 m; 0.137 m with the height rule | **NOT attributed.** GMAT's Earth-fixed frame at report epochs is identical under both settings (height from the fitted axis = height from GMAT's Earth-fixed coordinates to 0.6 µm). The difference arises inside GMAT's steps |
| J2 + drag, geodetic (i 51.6°; 97°; 250 × 800 km) | 0.20 / 1.08; 0.58 / 0.70; 0.24 / 0.86 m | 0.18; 0.23; 0.095 m | Not attributed (contains the geodetic path) |
| J2 + drag + M2 burn | 0.24 / 0.94 m; mass 2.9e-9 kg | — | J-ax-1 residual only |
| Perturbations off, exact-configuration form | Every approved M1 GMAT gate passes unchanged (GMAT vs Kepler 6.95e-6 m against the 1e-4 m limit; `gmat` → `regression_m3_form`) | — | — |

**Configuration findings (each one changes the reference by more than its own residual)**
1. **`Earth.NutationUpdateInterval`:** the default of 60 s moves the J2 reference by 8 cm (along-track) against 0.076 mm at 0. It must be pinned explicitly.
2. **GMAT's default C_d is 2.2000000000000002** (measured). Any scenario value must be set explicitly.
3. **GMAT's gravity field applies the `.cof` GM, not `Earth.Mu`** (VAL-0018, confirmed by the regression in `gmat` → `regression_m3_form`). The `.cof` must be generated from the pinned constants.
4. **GMAT's geodetic height** uses a 1e-7 rad stopping rule (≤ 1.4 mm error) and fails exactly on the axis. It belongs in the error budget of every geodetic comparison.
5. **GMAT's Earth orientation depends on its EOP file** (sha256 `52c95d68…`, data to 2026-09-14). The file must be recorded, because the axis it implies changes with it.
6. **States are exchanged in TOEEq fixed at the scenario epoch.** The echo of the initial state is 1.9e-9 m.
7. **GMAT's geodetic-drag result also depends on how the run is segmented into `Propagate` commands.** The planning probe was rerun unmodified on 2026-10-18 and reproduced byte for byte. Same physics, three GMAT configurations:

   | GMAT configuration | Geodetic-drag residual vs the spike |
   |---|---|
   | One 53 700 s `Propagate`, default interval (planning probe) | 0.383 m |
   | 895 × 60 s `Propagate`s, default interval (T0) | 0.186 m |
   | 895 × 60 s `Propagate`s, interval 0 (T0) | 0.327 m |

   - **J2 also varies:** 0.189 / 0.273 / 0.192 m. Its variation is fully explained: at interval 0 GMAT matches the spike driven by GMAT's axis to 0.076 mm.
   - **Spherical drag does not vary:** 2.0 mm in all three.
   - **Only the geodetic-drag variation is unexplained.** It is part of the escalated item below.

**Options**
- **(a) TOEEq exchange plus a derived bound on the Earth-orientation residual.**
  - Measured J-ax-1 residuals: 0.19–0.58 m final, up to 1.08 m maximum.
  - The polar-motion part is derived from GMAT's own EOP data.
  - The interval-0 geodetic part is not yet bounded.
- **(b) Drive the validator reference with GMAT's reported Earth-fixed axis.**
  - Feasible and exact for J2: 0.076 mm.
  - Recovering the axis needs two non-coplanar orbits, because one orbit plane leaves the out-of-plane component undetermined.
  - It also needs the diurnal polar-motion term. Fitting the axis without it leaves a **0.986 m RMS** residual, against 7.8e-5 m with it (reproduced after Review 02 IM-1; `axis_ablation`, from `t0_axis_ablation.py`):
    - *Quantity:* the least-squares residual of GMAT's Earth-fixed Z coordinate of a spacecraft, modelled as u(t)·r_TOE, where u(t) is GMAT's Earth-fixed +Z axis in TOE axes. It is a fit residual of an axis model, in metres at orbital radius, not a trajectory error.
    - *Data:* GMAT's axis-probe report `gmat_runs/axis_probe__m1_two_body_report.txt` (sha256 `ee1cab2b…3bb5`, equal to GMAT's run metadata). The two point-mass spacecraft are the M1 orbit and a polar orbit with its node on +Y. Both are reported in GMAT TOE (TOEEq at 2026-01-01 TT) and GMAT EarthFixed, in km converted to m.
    - *Sampling:* every 60 s from 0 to 53 700 s, 896 epochs × 2 spacecraft = 1792 equations.
    - *Models:* the full model u(t) = Σ c_k φ_k with φ = [1, t/t_end, (t/t_end)², cos ω_E t, sin ω_E t] (15 unknowns, as in `t0_gmat.py`). The quadratic-only model drops the diurnal pair (9 unknowns).
    - *RMS:* √(mean of e_i²) over all 1792 equations. The quadratic-only model's largest residual is 4.03 m.
    - *Command:* `uv run --no-sync python t0_axis_ablation.py t0_axis_ablation_results.json` in `docs/science/experiments/m3-t0/` (no GMAT run).
    - *Expected result and tolerance:* 0.9856650955520649 m within 1e-6 m. Reruns on one platform agree bit for bit. 1e-6 m exceeds the worst-case rounding scale of the fit (cond × eps × max|z| = 5.7e-7 m for the full model) and is 78 times smaller than the full-fit residual. The full model reproduces `gmat` → `axis` → `fit_rms_residual_m`, which ties the data file to the committed GMAT result.
    - The number is evidence for option (b)'s feasibility only. It is not a proposed threshold, and the DR-0028 scope ruling on (b) stays open.
  - **Scope question:** the validator would contain a J2 and an ellipsoid evaluated about a time-dependent, data-derived pole. DR-0028 says "No additional Earth-orientation implementation is authorized". The axis is GMAT output consumed as data, not an Earth-orientation model, but whether that falls inside the prohibition is the owner's ruling, not the implementer's. **Dependent work (choosing (b) for T5) is blocked on that ruling; nothing else is.**
- **(c) GMAT informational only** for configurations that cannot be matched exactly.
- **(d) [new] Decomposed exact configuration.** Each link is checked where GMAT can be exact; the geodetic trajectory comparison stays informational until the escalated item is resolved.
  - GMAT J2 against the validator reference, under (b) or under the (a) bound.
  - GMAT spherical-height drag against the validator reference: 2 mm and axis-independent. This checks density, rotation, ballistic coefficient and mass with no Earth-orientation effect.
  - Geodetic height checked separately, by P8 points and by GMAT's own altitude (≤ 1.3 mm at mid-latitudes).

**ESCALATED_FOR_INVESTIGATION.** The 0.137 m geodetic-drag difference at `NutationUpdateInterval` = 0 and the 0.18–0.23 m combined residuals are not explained.
- Candidate next steps (T5): read the R2026a sources for `CalculateGeodetics` and the atmosphere's rotation-matrix caching; repeat with intermediate intervals; isolate per step.
- Until then, no geodetic trajectory comparison can be called exact.

**Recommendation.** (d), with the pinned setting list above. Option (b) for the J2 link only if the owner rules that it is inside DR-0028; otherwise the (a) bound for J2. The escalated item is resolved before T5 proposes any geodetic GMAT gate.

**Owner decision (2026-10-25, append-only): NOT FULLY DECIDED — method (d) PROVISIONALLY SELECTED.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P6. Recorded verbatim:

> **NOT FULLY DECIDED.**
>
> Approve decomposed exact-configuration method (d) as the preferred direction for subsequent validation planning, subject to its authoritative configuration requirements.
>
> Do not mark P6 fully resolved.
>
> The geodetic-drag discrepancy of approximately 0.14–0.38 m remains escalated.
>
> Do not approve an independent geodetic GMAT acceptance gate.
>
> Do not silently decide DR-0028 P6(b). Prepare a separate, explicit owner ruling on whether driving the validator with GMAT's reported axis is within the previously approved Earth-orientation scope.
>
> The proposed X-1 investigation remains unexecuted and requires separate authorization.
>
> Record the provisional method selection without converting unresolved evidence into a PASS.

**Status of P6 and DR-0025 Q-G2-1: PROVISIONALLY SELECTED (method (d)); not decided; the geodetic-drag item stays ESCALATED_FOR_INVESTIGATION.** P6 is not a T2 prerequisite (Q-GATE amendment, Resolution). Its open questions block geodetic GMAT acceptance in T5.

**"Authoritative configuration requirements" of method (d)**, as recorded (no new requirement is added):
- DR-0025 Resolution principle 2: every GMAT comparison records the force model (degree/order, `.cof` file with its GM/R/C̄20, tide model), state-exchange frame and axes, constants, atmosphere model and table file with digest, drag model (C_d, area, mass, `DragModel`), propagator, step and error-control settings, and every other setting needed to reproduce it.
- The seven configuration findings above: `Earth.NutationUpdateInterval` pinned explicitly; C_d set explicitly (GMAT's default is 2.2000000000000002); the `.cof` generated from the pinned constants (GMAT applies the `.cof` GM); GMAT's geodetic height rule (1e-7 rad, ≤ 1.4 mm) in the error budget, and its failure on the axis; the EOP file recorded (sha256 `52c95d68…`); states exchanged in TOEEq fixed at the epoch; the `Propagate` segmentation recorded.
- The setting list relies on DR-0025 Q-G2-2's identity-check sub-rule, which stays **PROPOSED**.

**Unresolved investigation register (P6).** Every row stays open until a separate authorization resolves it.

| # | Item | Status | Blocks |
|---|---|---|---|
| P6-U1 | Geodetic-drag residual 0.137 m at `NutationUpdateInterval` = 0 (0.175 m without GMAT's height rule), not attributed | **ESCALATED_FOR_INVESTIGATION** | Any geodetic GMAT gate (T5) |
| P6-U2 | Dependence of the geodetic-drag residual on `Propagate` segmentation and interval: 0.383 / 0.186 / 0.327 m | **ESCALATED_FOR_INVESTIGATION** | Same |
| P6-U3 | Combined J2 + drag geodetic residuals with GMAT's axis (0.18, 0.23, 0.095 m), not attributed; they contain the geodetic path | ESCALATED (with P6-U1) | Geodetic J2 + drag GMAT comparisons |
| P6-U4 | DR-0028 P6(b) scope ruling: is driving a validator reference with GMAT's reported axis inside the approved Earth-orientation scope? | **OPEN**; ruling packet prepared (`DR-0028-P6b-owner-ruling-packet.md`); not decided by I-26 | Choosing (b) for the J2 link (T5) |
| P6-U5 | J2-link method: (b) GMAT axis (0.076 mm) or (a) derived Earth-orientation bound | OPEN; depends on P6-U4 | T5 J2 GMAT link |
| P6-U6 | Investigation X-1 (decision packet §5) | **NOT AUTHORIZED**; unexecuted | P6-U1, P6-U2 attribution |
| P6-U7 | An independent geodetic GMAT acceptance gate | **NOT AUTHORIZED** | — |
| P6-U8 | DR-0025 Q-G2-2 identity-check sub-rule | PROPOSED | The setting list's reliance on it |

The attributed links are unchanged evidence, not a PASS: J2 0.076 mm with GMAT's axis at interval 0; spherical-height drag 2.0 mm, axis-independent; M3-form GMAT passes every M1 gate (6.95e-6 m).

## P7 — DR-0025 Q-G2-5: reference missions
All are exercised in `gmat` (GMAT vs spike) unless noted. Horizon 53 700 s (the M1/M2 horizon) unless noted.

| Id | Configuration | Purpose (DR-0025 oracles) | T0 evidence |
|---|---|---|---|
| RM-0 | v3 point mass (perturbations off), M1 state | VO-5 regression | M3-form GMAT passes every M1 gate; spike RK4 bitwise equal to the M1 golden |
| RM-1 | J2 only, M1 orbit | Q1, Q2, Q3, Q10, Q8 | 0.192 m (J-ax-1); 0.076 mm (GMAT axis) |
| RM-2 | Drag, one-band 250 km table, spherical height | Q4, Q5, Q6 decay oracle, Q10 (smooth) | 2.05 mm |
| RM-3 | Drag, full table, geodetic, M1 orbit | Q5, Q7, Q8, band crossings | 0.327 m; 39 band changes in 10 orbits |
| RM-3b | Drag, full table, geodetic, circular 275 km (mid-band) | Full table without band crossings over the horizon | **Not run** (candidate only) |
| RM-4 | J2 + drag, geodetic, M1 orbit (**primary**) | VO-3 | 0.199 m final / 1.08 m maximum; 29 band changes |
| RM-5 | J2 + drag, geodetic, circular 250 km, i = 97° | Node advance (i > 90°, Q11 sign) | 0.583 m |
| RM-6 | J2 + drag, geodetic, 250 × 800 km, i = 51.6° | ω̇ (eccentric), 9 bases spanned, 151 band changes | 0.237 m final / 0.858 m maximum |
| RM-7 | J2 + drag + M2 prograde burn (M2 vehicle, A 15 m²) | VO-4 | 0.240 m; mass 2.9e-9 kg |
| RM-8 | J2 + drag, geodetic, circular 180 km → h_f (P1) | VO-9 decay, A-5 crossing | GMAT stop at 80 km (spike test value) within 0.023 s; 5.96 h to the ground |

**Note on the 250 km base.**
- The M1 initial altitude is exactly the 250 km band base, so RM-3, RM-4, RM-5 and RM-7 start on a boundary and cross it repeatedly.
- That makes them good boundary cases (DR-0025 principle 5), but they cannot serve as no-crossing cases; RM-3b is proposed for that role.
- RM-2 is unaffected, because the one-band table has no boundary.

**Recommendation.** RM-0 … RM-8, with the RM-8 floor set by each scenario under P1 and RM-3b to be measured in T4. All apogees are below 900 km (P5).

**Owner decision (2026-10-25, append-only): DECIDED — RM-0 through RM-8.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P7. Recorded verbatim:

> **DECIDED: RM-0 through RM-8.**
>
> Use the P1 admissibility rule for RM-8.
>
> Use the P9 illustrative vehicle definitions.
>
> RM-3b is a candidate to be measured during T4, not a new mandatory gate without subsequent approval.
>
> Preserve all previously accepted M1/M2 requirements.

**Implementer notes on the record (no change to the decision):**
- The missions are RM-0, RM-1, RM-2, RM-3, RM-4 (primary), RM-5, RM-6, RM-7 and RM-8, as tabulated. RM-3b is a measured candidate only. *(Corrected by I-27 (M3T2OD-R1-F2): RM-3b is an **unmeasured** candidate for evaluation during T4; see the I-27 correction below. The sentence is kept as originally written.)*
- Vehicles (P9 option (i)): V2 for RM-7; V1 for the other drag missions (RM-2 … RM-6, RM-8). RM-0 and RM-1 have no drag.
- RM-8's h_f is chosen by its scenario and must pass P1 (clause 2 at dt 10 s with V1 admits h_f ≥ 92 282.07 m [measured]); no value is chosen here.
- RM-6 needs an elliptic or Cartesian v3 orbit kind (T3 schema decision, unchanged).
- The obligations are implemented in T3/T4/T5, each under its own authorization. **Not authorized by I-26.**

**I-27 correction (2026-10-25, append-only; Review 01 M3T2OD-R1-F2).** Authority: "TARS — Authorization I-27: M3 Owner Decisions: Review 01 Corrections and Independent Review 02" (owner/Tech Lead, 2026-10-25), §3. **RM-3b is an unmeasured candidate for evaluation during T4.**
- It is **not** an accepted reference result. **No measurement has been completed:** the table above says "Not run", and X-2 (decision packet §5) is not authorized.
- It is **not** a mandatory acceptance gate.
- Any future promotion requires evidence and the applicable review and authorization.

The P7 decision (RM-0 … RM-8) is unchanged. No RM-3b experiment is created or run.

## P8 — DR-0025 Q-G2-7: source of geodetic-height test points
**Evidence** (`geodetic`; `gmat` → `geodetic_points`)

| Candidate | Independence | Result |
|---|---|---|
| (a) Exact answers: equator h = √(x² + y²) − a; axis h = \|z\| − b | Analytic | Iterative: 0 error; Vermeille: ≤ 5.5e-10 m |
| (a′) 640 points from the closed-form forward transformation (latitudes −90…90°, heights −10 km … 2000 km) | Different formula (forward), shares no code with the inverse | Iterative ≤ 1.9e-9 m; Vermeille ≤ 2.9e-9 m |
| (b) GeographicLib CartConvert(1) manual examples (WGS 84; printed to 0.01 m) | Published, external | Forward within 4.5 mm; inverse within 4.2 mm (inside the 5 mm rounding) |
| (c) GMAT R2026a `Earth.Altitude` / `Latitude` | Independent implementation | ≤ 1.3 mm at mid-latitudes; 15 mm at 89.999999°; **fails exactly on the axis** (h ≈ −N) |
| (d) A geodesy text or standard with printed test points | — | Not available to the project; would need acquisition |

**Domain.**
- Both inverse algorithms are valid outside the evolute region near the centre.
- The published reverse example (30 km, 30 km, 0) lies inside it: the iterative algorithm returns a non-nearest solution (0.86 m from GeographicLib's), and Vermeille divides by zero.
- Every M3 state is far outside this region, but the production function must state its domain and reject points outside it.

**Recommendation.** (a) and (a′) as the gate source (exact to round-off), with (b) and (c) recorded as external corroboration. The production height function's domain is stated, and on-axis points are tested explicitly.

**Owner decision (2026-10-25, append-only): DECIDED — options (a) and (a′), with the reviewed gating restrictions.** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P8. Recorded verbatim:

> **DECIDED: Options (a) and (a′), with the reviewed gating restrictions.**
>
> Use exact mathematical answers as the primary gate source within their justified domain.
>
> Use forward-constructed points as additional reference evidence.
>
> Forward-constructed points become gating only after their numerical construction-error contribution has been derived and reviewed.
>
> Negative-height cases remain report-only until appropriate bounds exist.
>
> GeographicLib, GMAT and the identified IOGP/EPSG example are corroboration sources, not automatically authoritative inverse-height gates.
>
> Do not claim independent verification from a reference that shares the same unexamined assumptions.

**Implementer notes on the record (no change to the decision):**
- "The reviewed gating restrictions" are those of decision packet P8 item 14 (I-24 correction, Review 03 PASS): exact references evaluated exactly on the model's ellipsoid; true height ≥ 0; path (α) (DQ-1, decided); the inverse's own evaluation error only; evolute-region points rejected.
- **Consequence under the owner's floating-point policy (I-26 §5; validation strategy §6):** the tolerance for exact-answer points is ε_h (T0 E1), which rests on A-FP-2. A-FP-2 is not accepted as a universal guarantee, so **exact-answer comparisons are report-only in T2 until A-FP-2 is independently justified for the supported environment and the criterion reviewed.** The source is decided; the tolerance's gating status is conditional. The exact domain checks (evolute and origin rejection) are unconditional.
- Corroboration sources: GeographicLib CartConvert(1) examples, GMAT R2026a `Earth.Altitude`, and IOGP GN 7-2 / EPSG 9602 (decision packet C-5: input recalled, PDF unread, forward only, cm print). C-5 uses the same closed-form forward formula as (a′), so it does not independently verify (a′).

## P9 — DR-0024 Q9: validation-scenario parameters
**Evidence and basis**
- **C_d 2.2** is GMAT R2026a's default (measured, `gmat`; VAL-0007 used it).
  - It is commonly described as the conventional value for compact satellites in free-molecular flow. **[secondary]** Search results attribute the value to Cook and to Izakov via an abstract by K. Moe; that abstract and the primary sources were **not read**, so no primary citation is claimed.
  - In the cannonball model C_d enters only through B = m/(C_d A). The validation oracles test the model's correctness for a given B, not the realism of C_d.
- **B 25.8 kg/m²** (850 kg, 15 m², C_d 2.2; the GMAT defaults):
  - it gives measurable decay (−12.8 km/day at 250 km, VAL-0018);
  - it continues VAL-0007/VAL-0018;
  - drag-only RK4 error at dt = 10 s: 4.6 m (VAL-0018).
- **B 100 kg/m²:** a low-drag variant (0.70 m RK4 error in J2 + drag, VAL-0018).
- **M2 vehicle** (1000 kg dry + 300 kg propellant, DR-0010): with A 15 m² and C_d 2.2, B = 39.4 kg/m² before the RM-7 burn and 39.0 kg/m² after it (final mass 1287.62 kg, measured in GMAT).
- **Sensitivity:** B + 1 % moves the 10-orbit trajectory by 4.8 km (VAL-0018). B is therefore a pinned scenario input with an exact value, never tuned.

**Options**
- **(i)** V1 = 850 kg, 15 m², C_d 2.2 (B 25.8), plus V2 = the M2 vehicle with A 15 m², for RM-7.
- **(ii)** As (i), plus a B 100 variant of RM-4.
- **(iii)** A cited real vehicle class: no source was read in T0.

**Initial states**
- Circular states use the M1 construction (altitude, inclination, RAAN 0, argument of latitude 0, epoch 2026-01-01 TT as metadata).
- RM-6 needs an elliptic state (perigee/apogee construction, `t0_model.perigee_state`) or a Cartesian state. Which v3 orbit kinds exist is a T3 schema decision.

**Recommendation.** (i), with every value labelled "illustrative, validation only" in the scenarios and records, as DR-0010 did for the engine. Option (ii) only if the owner wants a low-drag case gated.

**Owner decision (2026-10-25, append-only): DECIDED — Option (i).** Authority: I-26 (owner/Tech Lead, 2026-10-25), §2 P9. Recorded verbatim:

> **DECIDED: Option (i).**
>
> Use the specified illustrative V1 and V2 vehicles from DR-0029.
>
> V1:
>
> - Mass: 850 kg
> - Area: 15 m²
> - C_d: 2.2
> - Ballistic coefficient: approximately 25.8 kg/m²
>
> V2 uses the accepted M2 vehicle mass configuration with area 15 m², as specified in DR-0029.
>
> Every scenario and record must label these values:
>
> **ILLUSTRATIVE — VALIDATION ONLY**
>
> Do not claim they are validated representations of a real spacecraft.

**Implementer notes on the record (no change to the decision):**
- V1: B = 850/(2.2 × 15) = 25.7575… kg/m² [derived]; "25.8" is its rounded display.
- V2, as specified in this DR (Evidence, "M2 vehicle"): 1000 kg dry + 300 kg propellant (DR-0010), A = 15 m², C_d = 2.2 (the summary row's "C_d 2.2 (illustrative)"). B ≈ 39.4 kg/m² before the RM-7 burn and ≈ 39.0 after it [measured in GMAT]. V2 is used for RM-7. No M2 scenario changes.
- Option (ii) is not adopted: no B 100 mission is gated. B 100 remains in the evidence (thresholds, T0 floors).
- Initial states follow this DR's "Initial states" paragraph. Which v3 orbit kinds exist (RM-6) is a T3 schema decision.
- The required label is **ILLUSTRATIVE — VALIDATION ONLY**. It replaces the lower-case wording of the recommendation above in every scenario and record.

## P10 — New: identity of the pinned J2 value
**Evidence.** DR-0024 Q1 records "J2 = 1.0826261739e-3 (= −√5 × −0.484165143790815e-3)". The two are not the same double: −√5 C̄20 = 1.0826261738522227e-3, a relative difference of −4.4e-11 (`t0_model.J2_FROM_C20`). A generated `.cof` carries C̄20.

**Options**
- **(a)** Pin C̄20 (the NGA source value) and derive J2.
- **(b)** Pin the decimal J2 and write C̄20 = −J2/√5 into the `.cof`.

**Trajectory effect.** Negligible: about 6.7 m × (4.4e-11 / 8.6e-6) ≈ 3e-5 m [derived from the VAL-0018 tide-system sensitivity]. The physics identity (DR-0026) must still contain exactly one of them.

**Recommendation.** (a), because the source publishes C̄20.

**Owner decision (2026-10-22, append-only): DECIDED — Option (a).** Authority: "I-16 — Decide DR-0029 P10 and Prepare T1 Authorization" (Tech Lead, 2026-10-22), §1. Recorded verbatim:

> **DR-0029 P10 — DECIDED:** The canonical identity of the approved J2 representation from DR-0024 Q1 is the EGM2008 tide-free coefficient
>
> `C̄₂₀ = −0.484165143790815e−3`
>
> from NGA.STND.0036 Table 5.
>
> `J2` is derived from that canonical value using:
>
> `J2 = −√5 × C̄₂₀`
>
> which in the project's IEEE-754 binary64 computation gives approximately:
>
> `J2 = 1.0826261738522227e−3`.
>
> The decimal `1.0826261739e−3` appearing in DR-0024 Q1 is a rounded display representation, not an independent canonical constant.
>
> There shall be exactly one canonical stored physical value for this identity. Simulator constants, physics identities, generated GMAT coefficient/reference material, tests and future M3 references must derive consistently from that value.
>
> This decision selects the representation within the already-approved DR-0024 Q1. It does **not** reopen Q1's physical value or tide-system decision.

**Basis (I-16 §2, as stated by the owner):** provenance (C̄20 is the published coefficient; J2 is derived); a single source of truth; T0 continuity (accepted T0 J2 computations used this representation); reference consistency (the GMAT coefficient-file path originates from C̄20); round-trip behaviour in the existing environment; lower migration cost. The trajectory comparison of (a) against (b) is supporting experimental evidence only, not a bound, certification or proof of physical equivalence.

**Required invariant (I-16 §3):** one canonical value → all derived representations; no independent authoritative literals for both C̄20 and J2. Implementation belongs to T1 and is not authorized by I-16.

**Implementer notes on the record (no change to the decision):**
- The decision text cites "Table 5". The coefficient is in NGA.STND.0036 v1.0.0 **Table 5.1** (DR-0024 [NGA] reference, SCI-0013); the citation is read as Table 5.1.
- The supporting comparison, from the unreviewed scratch probe `docs/science/experiments/m3-p10/` (one orbit, one host), is 3.20e-5 m (DOP853) and 3.48e-5 m (RK4, dt 10 s) after 53 700 s. The owner's "approximately 3.5e-5 m" matches the RK4 value.
- The round-trip statement rests on that same probe on one host (`.14e` coefficient-file print of C̄20 reads back to the identical binary64). It is not cross-platform evidence.

**Not decided by P10 (I-16 §4):** DR-0029 P1–P9; Q-G2-1/P6; DR-0025 Q-G2-2; DR-0028 P6(b); the final M3 time step; A-FP-2; E4b insofar as it depends on A-FP-2; the combined J2-plus-drag missed-crossing bound; cross-platform validation limitations; the unreproduced 5 287-point search; any sampled-sweep evidence as a proof; branch-protection recommendations. Their status is unchanged.

## Impact
- **Architecture:** P2–P5 decide one v3 end condition, one failure cause, one domain rule and one pinned constant (κ). P6 decides the GMAT generator's settings. No production change is made here.
- **Science/validation:** VAL-0019; SCI-0015/0016/0017 limitations (unsupported altitudes, termination); DR-0025 oracle design.
- **Dependencies:** none.
- **Reversibility:** high until T2/T3 implement them. After that, a change creates a new physics identity.

## Blocked work
- **T2/T3** (drag, end conditions, contract): P1–P5, P8, P9.
- **T1:** P10. *(2026-10-22: P10 DECIDED, I-16; this block is lifted. T1 still needs its own authorization.)*
- **T4/T5:** P6 and P7. Choosing P6 (b) additionally needs the DR-0028 scope ruling. The escalated geodetic-drag investigation blocks only geodetic GMAT gates.
- **Any use that needs a guaranteed missed-dip magnitude for J2 + drag** (P2): no perturbed-motion bound exists in T0 (Review 02 R2-F1). A5-b as recommended does not need one.
- *(2026-10-25, append-only, I-26.)* The list above is superseded for T2 by the Q-GATE amendment (Resolution):
  - **T2:** P1–P5, P8, P9 and DQ-1 … DQ-6 are decided and recorded. It needs the reconciliation reviewed and a separate explicit authorization. It is **not** blocked by P6.
  - **T3/T4:** P1–P3 and P7 are decided, and each task needs its own authorization.
  - **T5:** geodetic GMAT acceptance stays blocked by P6-U1 … P6-U3, and the J2 link method by the DR-0028 P6(b) ruling (P6-U4).

## Work continuing independently
- None of the implementation. T1 and later are not authorized.
- The independent review of T0: Review 01 returned REQUEST_CHANGES (`docs/reviews/M3-T0-review-01.md`); F1–F4 are corrected here. Review 02 returned REQUEST_CHANGES (`docs/reviews/M3-T0-review-02.md`); R2-F1 … F3 and IM-1 are corrected here. Review 03 returned REQUEST_CHANGES (`docs/reviews/M3-T0-review-03.md`); R3-F1 is corrected here. Review 04 returned REQUEST_CHANGES (`docs/reviews/M3-T0-review-04.md`); R4-F1 is corrected here. Review 05 returned REQUEST_CHANGES (`docs/reviews/M3-T0-review-05.md`); R5-F1 and R5-F2 are corrected here. Any Review 06 needs separate authorization.

## Requested response
For each of P1–P10: accept, choose an option, or `discuss`. P1 needs κ. P6 needs a ruling on whether option (b) falls inside DR-0028's prohibition on additional Earth-orientation implementation.

## Resolution
**Decision:** (pending)

*(2026-10-22, append-only)* **P10: DECIDED — Option (a)** ("I-16 — Decide DR-0029 P10 and Prepare T1 Authorization" (Tech Lead, 2026-10-22)): C̄20 = −0.484165143790815e-3 (EGM2008 tide-free, NGA.STND.0036 Table 5.1) is the single canonical value; J2 = −√5·C̄20 is derived (binary64 1.0826261738522227e-3); 1.0826261739e-3 is a display rounding. DR-0024 Q1 is not reopened. Decision text verbatim in the P10 section. **P1–P9: still pending.** DR-0028's scope ruling for P6 (b) remains undecided; Q-G2-1 remains escalated.

*(2026-10-25, append-only)* **Owner decisions under "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation"** (owner/Tech Lead, 2026-10-25). The text of each decision is recorded verbatim in its section above.

| # | Status | Summary |
|---|---|---|
| P1 | **DECIDED** | A4-b; v̂ = V_b; κ = 0.01; clauses 1 and 2; dry-mass B_min; a necessary screen only (velocity-Jacobian block; not ∂a/∂r; not the coupled dynamics); κ an engineering constant; final dt separate |
| P2 | **DECIDED** | A5-b; run ends at the committed state; Hermite time is not a state; no step splitting; missed dips a documented limitation; T2 exposes n̂ or φ |
| P3 | **DECIDED** | Precedence `non_finite` → `reentry` → `impact` → `escape`; `impact` kept as backstop; height-only termination; discontinuities preserved; T3 behaviour, not implemented now |
| P4 | **DECIDED** | (ii) fail closed; finite h < 0 m raises a typed domain error; guard in metres before conversion; −0.0 in range; non-finite a distinct error; no partial commit; DR-0026 AR-8/§5.8 reconciled; T3 outcome mapping not implemented now; the T0 guard defect not reproduced |
| P5 | **DECIDED** | Region table; top band extrapolated above 1000 km, labelled unverified; no cutoff, no upper failure; table preserved; wording amendment adopted; no continuity imposed; GMAT band rule and exact-base behaviour kept |
| P6 | **NOT FULLY DECIDED** | Method (d) **PROVISIONALLY SELECTED**; geodetic-drag 0.14–0.38 m **ESCALATED_FOR_INVESTIGATION**; no independent geodetic GMAT gate (**NOT AUTHORIZED**); DR-0028 P6(b) ruling **OPEN** (separate packet); X-1 **NOT AUTHORIZED**. Register P6-U1 … P6-U8 |
| P7 | **DECIDED** | RM-0 … RM-8; RM-8 under P1; P9 vehicles; RM-3b a T4 candidate, not a gate; M1/M2 requirements preserved |
| P8 | **DECIDED** | (a) primary gate source within its justified domain; (a′) evidence, gating only after its construction-error term is derived and reviewed; negative heights report-only; GeographicLib, GMAT and IOGP/EPSG corroboration only |
| P9 | **DECIDED** | Option (i): V1 850 kg, 15 m², C_d 2.2 (B ≈ 25.8 kg/m²); V2 the M2 vehicle with 15 m²; label **ILLUSTRATIVE — VALIDATION ONLY** |
| P10 | DECIDED (I-16, unchanged) | Binding for T1 |

**Q-GATE — amendment of the T2 dependency gate (APPROVED).** Recorded verbatim from I-26 §3:

> The owner explicitly approves narrowing the original I-15 prerequisite for T2.
>
> The replacement rule is:
>
> **Before T2 implementation may be authorized:**
>
> - P1–P5 must be decided.
> - P8 and P9 must be decided.
> - DQ-1 through DQ-6 must be decided.
> - The resulting contracts must be recorded and reconciled.
> - An explicit, separate T2 implementation authorization is required.
>
> P10 remains previously decided and binding for T1.
>
> P6 is not a T2 implementation prerequisite. Its unresolved scientific questions remain blockers for geodetic GMAT acceptance in T5.
>
> P7 must be decided before its reference-mission obligations are implemented in T3/T4; it is already approved in this authorization.
>
> This amendment supersedes only the broader T2 dependency statement from I-15. It does not waive any scientific, review, numerical or acceptance gate.

- **Superseded text (preserved where it stands):** "Explicitly identify P10 as a prerequisite for T1 and P1–P10 as prerequisites for T2" (I-15 T0 series, review instruction §6; `docs/milestones/M3-T0-decision-matrix.md`, "Dependency statement"; decision packet §1.2). Only its T2 clause is superseded. The T1 clause is unchanged.
- **DQ-1 … DQ-6** are decided under I-26 §4 and recorded in `docs/milestones/M3-T2-authorization-packet-r1.md` §5, with their reconciliations in DR-0024 and DR-0026 ("I-26 note").
- **Not decided by I-26:** P6 in full; DR-0028 P6(b); X-1; the final M3 time step (Q-G2-4); DR-0025 Q-G2-2; A-FP-2, A-LM-1 and A-LM-2 as universal guarantees (I-26 §5); any T2, T3, T4 or T5 authorization.

<!-- review01-correction-log -->
## Correction log (Review 01, 2026-10-18)
Authority: "TARS M3 T0 — Review 01 Correction Authorization" (Tech Lead). The superseded wording is preserved at commit `bdcaacf`. No option, identifier, recommendation status or owner decision changed; DR-0029 stays OPEN.
- **M3T0-F1 (P2):** the missed-crossing "analytic bound" a e n² dt²/8 = 4.17 m was a fixed-phase estimate, not a bound. It is replaced by the derived curvature bound and its sweeps (`t0_termination.py`). 1.56 m is kept, labelled as a single-phase measurement. The P2 risk is restated.
- **M3T0-F2 (P1, P3, P4, P5, summary):**
  - The 5 km grid heights are replaced by exact thresholds; "κ = 0.01 admits h_f ≥ 90 km" was wrong (90 185.09 m).
  - A4-b is stated as necessary, not sufficient, with the reviewer's counterexamples and a derived sufficient stage-domain condition.
  - The speed term is made explicit: v_c as first proposed, or the bound V_b, which is the implementer's corrected recommendation. The owner chooses either.
  - P3 items 1–2: the same-tick claim is withdrawn and the impact/reentry implication is stated exactly.
  - P4: the claim that the options never differ for a valid run is withdrawn; the conditions under which they differ are stated.
  - P5: "unreachable" for 0–25 km is narrowed to "not an admissible h_f".
  - The decay-case statements are limited to that case.
- **M3T0-F3 (P4):** the inward stage is the third stage (the input of k3), not the second.
- **M3T0-F4 (P6 table):** the M3-form GMAT vs Kepler residual is 6.95e-6 m (committed result), not 4.86e-6 m (a superseded run at GMAT's default `NutationUpdateInterval`).
- **Not changed:** IM-1 (the P6 "0.99 m" figure) is outside the authorized correction scope and stays as recorded, flagged in `docs/reviews/M3-T0-review-01.md`.
<!-- /review01-correction-log -->

<!-- review02-correction-log -->
## Correction log (Review 02, 2026-10-18)
Authority: "Authorization: M3 T0 — Review 02 Corrections and Independent Review 03" (Tech Lead). The superseded wording is preserved at commit `5548d11`. No option, identifier, recommendation status or owner decision changed; DR-0029 stays OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R2-F1 (P2):** J2 + drag values that had been called bounds are relabelled as sampled estimates. The statement that the sweep never exceeds the bound is restricted to the certified two-body rows. The two-body maximisation is made closed-form. The recommendation is now stated to need no perturbed bound, and uses that would need one are recorded as blocked.
- **M3T0-R2-F2 (P1):** the drag factor of the sufficient stage-domain condition is maximised over every height above each stage's lower bound, instead of being evaluated at that lower bound. The monotonicity in h0 is derived. The three bounds are recomputed: B 25.8 moves by 1.1e-7 m and the others are unchanged.
- **M3T0-R2-F3:** the regression checks recompute what they protect (`check_review02.py`); mutation evidence is in VAL-0019.
- **IM-1 (P6):** "0.99 m" is replaced by the reproduced 0.986 m RMS, with its quantity, data, sampling, RMS definition, command and tolerance.
<!-- /review02-correction-log -->

<!-- review03-correction-log -->
## Correction log (Review 03, 2026-10-19)
Authority: "Authorization I-4: M3 T0 — R3-F1 Correction and Independent Review 04" (Tech Lead). The superseded wording is preserved at commit `c6c0fff`. No option, identifier, recommendation status or owner decision changed; DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R3-F1 (P1, P4):** the stage-domain drag envelope bounded drag at exact heights. It now bounds the model's computed drag over every band that the computed height can select, using a derived height-error bound ε_h and the rounding of the density, drag, gravity and RK4 stage arithmetic, under the stated floating-point assumptions A-FP-1 … A-FP-3. The bound is stated for the computed committed height. The three bounds are unchanged at the quoted precision (exact roots +1.9e-8 m). The superseded sentence "the supremum is attained at L or at a band base above L" was true for exact heights only. P4's guarantee now names the assumptions. The P1 recommendation is unchanged.
<!-- /review03-correction-log -->

<!-- review04-correction-log -->
## Correction log (Review 04, 2026-10-19)
Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05.
- **M3T0-R4-F1 (P1, P4):** the drag enclosure assumed relative rounding for subnormal results. A-FP-1 to A-FP-3 now state the mixed absolute and relative model, with gradual underflow. E1–E6 carry the absolute error of every underflowing operation, and the envelope gains an absolute part bounded up to the zero-density height h_zero. No domain restriction is introduced.
  - The three bounds are unchanged to the last bit, and the roots to 1e-9 m.
  - A-FP-2 remains an assumption. Its weakest sufficient form is quantified (2^5 to 2^7 ulps for the published bracket ends).
  - The quotation of the drag-free bound to the nearest centimetre is clarified (111 511.96 m is 1.8 mm below it; 111 511.97 m suffices).
  - The P1 recommendation is unchanged.
<!-- /review04-correction-log -->

<!-- review05-correction-log -->
## Correction log (Review 05, 2026-10-19)
Authorization I-6 — M3 T0 Review 05 corrections only. The superseded wording is preserved at commit `17b2229`. No option, identifier, recommendation status or owner decision changed; DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R5-F1 (P1, P4):** the envelope bounded cd·area/mass by φ_B/B, a relative-only rounding of the conversion between B and the mass, which fails for a subnormal B. The bound now carries the absolute error of every underflowing rounding of either construction (E4a), and a vehicle with cd·area ≤ 2^-1075 has exactly zero force (E4b). The domain is unchanged, and no vehicle condition is introduced. The three bounds and every other termination result are unchanged to the last bit. The P1 recommendation is unchanged.
- **M3T0-R5-F2 (P1):** the coefficient-rounding case was described as the tightest observed case, with 0.983. 0.983 is the maximum over the coefficient-rounding subset. The committed transition scan reaches 0.99999999999886 at subnormal densities. Both are now stated with their scope.
<!-- /review05-correction-log -->

<!-- review06-correction-log -->
## Correction log (Review 06, 2026-10-20)
Authorization I-8 — M3 T0 Review 06 Corrections. The superseded wording is preserved at commit `30a4e8d`. No option, identifier, recommendation status or owner decision changed; DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R6-F1 (P1, P4):** under C1 a positive mass can round to B = 0, where the envelope divided by zero. E4a now covers B = 0 through mass ≥ 2^-1074. The three bounds and every pre-existing termination result are unchanged to the last bit. The P1 recommendation is unchanged.
- **M3T0-R6-F2:** the rounding helpers now handle infinite and out-of-range values in both directions and reject NaN. An unbounded stage enclosure reports need = +∞ (not certified) instead of raising.
- **M3T0-R6-F3 (P1):** c₀ ≤ 5/8 depends on A-FP-2; E4b is now classified as derived under A-FP-1 and A-FP-2.
- **Records:** the 5 287-point random search quoted in the Review 04 record is marked UNREPRODUCED, and the switch point b* is quoted for the stored and for the exact φ_B (Review 04 and 05 records, amended).
<!-- /review06-correction-log -->

<!-- review07-correction-log -->
## Correction log (Review 07, 2026-10-20)
Authorization I-10 — M3 T0 Review 07 Corrections and Independent Review 08. The superseded wording is preserved at commit `72f9e00`. Documentation only; no option, identifier, recommendation status or owner decision changed; DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R7-F1 (P1):** the Review 06 entry above ("reports need = +∞") is kept as written and qualified here: a step is certified only when need < 0; need = −M2, finite and ≥ 0, when M2 ≤ 0 (up to h0 = 55 749.393 m with the published constants, for every B; M2 does not depend on the envelope), and need = +∞ when M2 > 0. No floor changes; the floor bisection accepts need < 0 only.
- **M3T0-R7-F2 (P1):** "b_R ≤ b" holds for B > 0 only; at B = 0, b_R = φ_B/R(0) > 0. Two docstring summaries are qualified.
<!-- /review07-correction-log -->

<!-- review08-correction-log -->
## Correction log (Review 08, 2026-10-21)
Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09. The superseded wording is preserved at commit `115e747`. Documentation and checks only; no option, identifier, recommendation status or owner decision changed; DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) stays open.
- **M3T0-R8-F1 (P1):** the Review 07 entry above ("need = −M2, finite and ≥ 0, when M2 ≤ 0 … for every B") is kept as written and qualified here: it holds for a computed h0 > β only. A computed h0 ≤ β raises `ValueError` before the M2 test, for B_V1 and the drag-free vehicle, and strictly exterior states reach such heights. No floor changes; the floor bisection accepts need < 0 only.
<!-- /review08-correction-log -->
<!-- review09-correction-log -->
## Correction log (Review 09, 2026-10-21)
Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10. Checks and documentation only. No option, identifier, recommendation status or owner decision changed. DR-0029 P1–P10 stay OPEN, and DR-0028's scope ruling for P6 (b) is still undecided. No P1 bound, floor or margin changes.
- **M3T0-R9-F1 (P1 evidence):** a check now pins need = −M3 whenever a finite M3 is the stage minimum (`check_review09.py`), and the finite-only M3 mutant is in the mutation harness. The stage condition's code and every published value are unchanged.
- **M3T0-R9-F2 (P1 evidence):** the pole example's mathematical height is −2.04e-10 m on the model's ellipsoid (polar radius a·√(1 − e2)), not −2.03e-10 m (A·(1 − F)). It does not appear in this DR's text; recorded here for traceability. Dispositions are in `docs/reviews/M3-T0-review-09.md`.
- **Review 10 (2026-10-21):** independent Review 10 (Codex, at `3c565e6`) returned PASS (unconditional) with no new findings (`docs/reviews/M3-T0-review-10.md`). This DR's status is unchanged: OPEN, P1–P10 undecided, Q-G2-1 escalated.
<!-- /review09-correction-log -->
- **P10 decision packet (2026-10-22, append-only):** under "I-15 — M3 Transition: Resolve DR-0029 P10 Before T1" (not the 2026-10-18 T0 authorization of the same number), an owner decision packet for P10 is prepared in `DR-0029-P10-owner-decision-packet.md`. Classification: CONDITIONALLY INDEPENDENT. Recommendation unchanged: (a). New, unreviewed scratch evidence (`docs/science/experiments/m3-p10/`): trajectory effect (a) vs (b) 3.2e-5 m on the M1 orbit (one host, not a bound); under (b) the T0 `.cof` format `.14e` does not round-trip J2. **P10 stays OPEN**; this DR's status is unchanged. T0 was fast-forward merged into `main` (`5fded7c`) under I-14.
- **P1–P9 decision packet (2026-10-24, append-only):** under "Authorization I-23 — M3 T2 Decision Readiness and DR-0029 P1–P9 Resolution Preparation", a readiness packet is in `DR-0029-P1-P9-owner-decision-packet.md`.
  - Classification: READY FOR OWNER DECISION P1, P2, P4, P8, P9; BLOCKED BY ANOTHER DECISION P3 (P1), P5 (P4, P1), P7 (P1, P9); NEEDS ADDITIONAL EVIDENCE P6.
  - It adds implementer findings N-1 … N-7 and corroboration C-1 … C-7. No option, number or recommendation in this DR changes.
  - **P1–P9 stay OPEN.**
- **P5 wording note (2026-10-24, append-only; I-24):** P5's cell for ≥ 1000 km, "Extrapolate the top band (continuous, GMAT-identical)", is ambiguous.
  - Read as continuity *at* the 1000 km base, it contradicts P1's list of 12 downward jumps (which includes 1000 km; relative jump −1.598e-5) and DR-0024 Q5a.
  - Read as continuity *within* the top band above its base, it is correct.
  - **Proposed amendment, not applied, for the owner to adopt or reject with the P5 decision:** "(the top band's formula, continuous for h > 1000 km; the 1000 km base keeps the published −1.598e-5 relative jump, like every other base; GMAT-identical)". Details: `DR-0029-P1-P9-owner-decision-packet.md`, P5 item 14.
  - The P5 table above is unchanged. **P1–P9 stay OPEN.**

- *(2026-10-25, append-only)* **Independent Review 01 of the I-26 recording (Codex, at `2cd1e6e`): REQUEST_CHANGES.** M3T2OD-R1-F1 (MAJOR): the `reentry` outcome identifier was left open although I-26 P3 decides it. M3T2OD-R1-F2 (MINOR): RM-3b was called "measured". Both are reproduced and ACCEPTED, **not applied** (I-26 §7 stop). Record: `docs/reviews/M3-T2-owner-decisions-review-01.md`.
- *(2026-10-25, append-only)* **I-27 corrections (Review 01 findings).** M3T2OD-R1-F1 is corrected in P3 ("I-27 correction"): `reentry` and the precedence are DECIDED, and T3 implements them without reconfirming them. M3T2OD-R1-F2 is corrected in P7 ("I-27 correction"): RM-3b is an unmeasured T4 candidate. The superseded sentences are kept, each marked in place. **No decision is added or changed.** P1–P5 and P7–P9 stay DECIDED; P6 stays NOT FULLY DECIDED. Q-GATE, DQ-1 … DQ-6 and the floating-point policy are unchanged. Matrix: `docs/reviews/M3-T2-owner-decisions-review-01-corrections.md`.

- *(2026-10-25, append-only)* **Independent Review 02 (Codex, at `f3ae387`): PASS**, with no BLOCKER or MAJOR finding. Two MINOR findings are ACCEPTED and **not applied** (I-27 §11): M3T2OD-R2-F1, two pre-I-26 cells in `M3-T0-decision-matrix.md` (lines 14 and 27) still call `reentry` a proposal without an in-place marker; M3T2OD-R2-F2, the `git diff --check` description in the I-27 correction record omits a trailing space in `self_validation.out:31`. Record: `docs/reviews/M3-T2-owner-decisions-review-02.md`. Nothing is approved by the PASS.
