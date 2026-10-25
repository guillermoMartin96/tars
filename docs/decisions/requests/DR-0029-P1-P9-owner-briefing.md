# DR-0029 P1–P9: owner-decision briefing

**Status:** BRIEFING. **Nothing here is decided.** P1–P9 stay OPEN, and Q-GATE, DQ-1 … DQ-6 and the P6 investigation stay open. The recommendations are the implementer's, labelled as such, and none is adopted by this document.  
**Prepared under:** "Authorization I-24 — M3 T2 Readiness: Review 01 Corrections and Independent Review 02" (Tech Lead, 2026-10-24), §3.  
**Full assessments:** `DR-0029-P1-P9-owner-decision-packet.md`, 15 items per decision. The authoritative option text is `DR-0029-m3-t0-proposals.md`, which governs where the two differ.

## 1. The alternatives
| # | Question | Alternatives (DR-0029 identifiers) | Implementer's recommendation | Readiness |
|---|---|---|---|---|
| P1 | Which termination altitudes h_f may a drag scenario state? | **A4-a:** 0 < h_f < h_initial only. **A4-b:** clause 1, a − b < h_f < h_geod(initial); clause 2, ρ(h_f)·v̂·dt/B_min ≤ κ. **A4-c:** a fixed range (e.g. 80–200 km) | A4-b with v̂ = V_b; κ = 0.01 [judgment] | Ready; **needs κ and v̂** |
| P2 | How is the h_f crossing found and reported? | **A5-a:** first committed state at or below h_f. **A5-b:** A5-a plus a cubic-Hermite crossing time in the event (the run still ends at the committed state). **A5-c:** split the last step to land on h_f | A5-b; missed dips documented, not detected | Ready |
| P3 | How does termination interact with domain edges and `impact`? | One proposal: `impact` kept as a backstop; precedence `non_finite` → `reentry` → `impact` → `escape`; height-only termination; the exact-base ambiguity is a model property. Other precedence orders are possible | As proposed | Depends on P1 (clause 1) |
| P4 | What density does an RK4 stage below 0 m receive? | **(i)** the lowest band's formula, extrapolated; the committed-state check ends the run. **(ii)** fail closed: a typed domain error ends the run | (ii), with the DR-0026 wording exception (§4) | Ready |
| P5 | Behaviour in each altitude region | DR-0029 P5 table. For ≥ 1000 km: **extrapolate the top band**, **fail closed above 1000 km**, or ρ = 0 above a cutoff (already rejected, DR-0024 §12) | As tabulated, **with the wording amendment** in packet P5 item 14 (the 1000 km base keeps its published jump) | Depends on P4 and P1 |
| P6 | How is GMAT configured as an exact-configuration reference? | **(a)** TOEEq exchange plus a derived Earth-orientation bound. **(b)** drive the validator reference with GMAT's reported axis. **(c)** informational only. **(d)** decomposed exact configuration | (d) with a pinned settings list; (b) for the J2 link only if the owner rules (b) inside DR-0028 | **Needs evidence** (§5) |
| P7 | Which reference missions? | RM-0 … RM-8 (RM-3b a candidate); subsets or additions | RM-0 … RM-8; RM-8 floor per P1; RM-3b measured in T4 | Depends on P1, P9 |
| P8 | Source of geodetic-height gate points | **(a)** exact answers; **(a′)** forward-constructed points; **(b)** GeographicLib examples; **(c)** GMAT `Earth.Altitude`; **(d)** a printed standard (now partly available: IOGP GN 7-2, coarse) | (a) + (a′) as gate source, the others as corroboration. As corrected under I-24, only (a) at h ≥ 0 gates now; (a′) gates once its construction term is derived | Ready |
| P9 | C_d, A, mass and initial states for validation scenarios | **(i)** V1 850 kg, 15 m², C_d 2.2 (B 25.8) and V2 = the M2 vehicle with A 15 m². **(ii)** (i) plus a B 100 variant of RM-4. **(iii)** a cited real vehicle class (none read) | (i), every value labelled "illustrative, validation only" | Ready |

## 2. What can be decided together
- **One response can settle P1–P5, P7, P8 and P9**, if it follows this order:
  1. P1, then P3;
  2. P4, then P5;
  3. P8 and P9;
  4. P7.
- **P6:** method (d) and the DR-0028 scope ruling can be decided now. Its full resolution needs the evidence in §5.
- The independent items are P2, P4, P8 and P9. They can be decided in any order.

## 3. P1: what κ and v̂ are, and how to choose them
- **What the rule screens.**
  - The drag force damps the velocity at a rate λ = ρ|v_rel|/B. This is the largest decay rate of the drag Jacobian with respect to velocity; it ignores ∂a/∂r (packet N-7).
  - Classical RK4 at step dt is stable on the negative real axis only for λ·dt ≤ 2.785. Its local relative error is about (λ·dt)⁵/120.
  - Clause 2 rejects any h_f at which λ·dt, evaluated at h_f with the scenario's smallest ballistic coefficient B_min (dry mass), exceeds κ.
- **v̂ is the speed in that estimate. It must stand in for |v_rel|, which varies along the orbit.**
  - v_c = √(μ/(a + h)) is the circular speed, a proxy. It underestimates λ for eccentric or retrograde states: at the v_c threshold, an e = 0.9 retrograde perigee gives λ·dt = 0.0144 against κ = 0.01.
  - V_b = √(2μ/(b + h)) + ω_E(a + h) is a proven upper bound on |v_rel| for every bound state at that height. It raises the thresholds by about 2–3 km.
  - **Selection principle:** choose V_b if the screen must hold for every bound state, and v_c if a proxy is acceptable.
- **κ is the largest admitted λ·dt, a pinned project constant. No source fixes it; it is owner judgment.**
  - κ near 2.785 guards stability only.
  - κ = 0.01 keeps the linearised local relative error from stiffness near 1e-12 per step. This is an estimate, not a trajectory bound.
  - At dt = 10 s with V_b, the exact thresholds are:

    | κ | B 25.8 kg/m² | B 100 kg/m² |
    |---|---|---|
    | 2.785 | 54 506.74 m | 43 820.78 m |
    | 1 | 62 842.26 m | 51 724.77 m |
    | 0.1 | 78 996.12 m | 70 116.76 m |
    | 0.01 | 92 282.07 m | 84 596.12 m |

  - **Selection principle:** κ trades how low h_f may go against the RK4 accuracy margin at h_f. The implementer suggests 0.01 [judgment].
- **What A4-b does not do.** It is a **necessary screen, not a sufficient one**. It does not keep RK4 stages above 0 m: a P1-admissible stress input reaches −28 km. Residual cases end by P4 and P3.

## 4. P4: consequences of fail-closed (ii)
- **Behaviour.** A stage below 0 m raises a typed domain error. The step is not committed (the existing atomic step guarantees this), and T3 maps the error to a defined run outcome. A name such as `outside_atmosphere_domain` is proposed.
- **Agreement with existing records:** DR-0024 Q8 ("no indefinite extrapolation below the modelled domain") and GMAT R2026a, which stops 1 m below the ellipsoid.
- **When it matters.** Option (ii) and option (i) give bitwise-identical runs whenever no stage goes below 0 m. That is guaranteed for h_f above ≈ 111.5–124.5 km at dt = 10 s, under A-FP-1 … A-FP-3 and for the T0 spike's arithmetic only (packet N-1). Below that, a run that (i) would continue on extrapolated density instead ends with a defined error.
- **Required wording exception.** DR-0026 AR-8 ("runtime functions are total") and §5.8 ("density is total") conflict with (ii). The decision should say that they do not apply below the table's lower edge (packet N-2).
- **Specification detail (I-24, Review 01 F4).**
  - The guard tests the height in metres, before any unit conversion. −0.0 is in the domain.
  - The T0 spike's guard runs after the conversion, so it accepts −2.475e-321 < h < 0. T2 must not copy it.
  - This changes no T0 result.
- **Cost.** `Simulator.step` does not catch the new error today, so T3 must handle it. One more failure cause appears in the v3 contract.

## 5. P6: the evidence still required
- **The gap.** GMAT's geodetic-drag trajectories differ from the spike by 0.14–0.38 m. The difference is 0.137 m even with Earth-orientation updates every step (interval 0), and it depends on run segmentation. It is unexplained; the J2 and spherical-drag links are explained (0.076 mm, 2 mm).
- **Smallest analysis (packet X-1, not authorized):**
  1. Read GMAT R2026a's `CalculateGeodetics` and its rotation-matrix caching.
  2. Rerun the T0 configuration at intermediate `NutationUpdateInterval` values and two segmentations.
  3. Compare GMAT's and the spike's density and acceleration at one state.
- **Acceptance:** the residual is attributed term by term to within GMAT's height rule (≤ 1.4 mm), or it stays escalated, with what was excluded recorded.
- **What it blocks:** geodetic GMAT gates (T5) and, under the governing gate, T2. No T2 code depends on it.
- **Separately, a ruling is needed (no evidence required):** is option (b) inside DR-0028's "no additional Earth-orientation implementation"?

## 6. Q-GATE: keep or narrow the T2 gate
The governing rule (I-15 T0 series §6) is "P1–P10 as prerequisites for T2". P10 is decided.

| | Keep P1–P10 | Narrow to P1–P5, P8, P9 (P6, P7 before T3/T4) |
|---|---|---|
| T2 start | After X-1 is authorized, run and reviewed, and P6 is decided | After one decision response and the DQ answers |
| Risk | Lowest risk of a decision changing T2's ground, but P6 and P7 have no T2 code consequence | P6's outcome cannot change T2 code: it concerns T5's GMAT configuration. P7 can still be decided with P1 and P9 at no cost |
| What is lost | Schedule: T2 waits on GMAT work unrelated to it | The rule's simplicity. A narrowed rule must be stated explicitly and recorded |
| Implementer's view | — | Narrow [judgment] |

**The implementer does not apply either option.**

## 7. Questions requiring the owner's approval
1. **P1:** choose A4-a, A4-b or A4-c. If A4-b, state **κ** (a number) and **v̂** (v_c or V_b).
2. **P2:** choose A5-a, A5-b or A5-c.
3. **P3:** accept the proposal (items 1–4) or state another precedence.
4. **P4:** choose (i) or (ii). If (ii), state that DR-0026 AR-8/§5.8 "total" does not apply below the lower edge.
5. **P5:** accept the table, choosing extrapolate or fail closed for ≥ 1000 km. **Adopt or reject the wording amendment** in packet P5 item 14.
6. **P6:** choose (a)–(d). **Rule on DR-0028 scope for (b).** Authorize X-1 or not.
7. **P7:** accept RM-0 … RM-8, or state a subset or additions; say whether RM-3b is measured in T4.
8. **P8:** choose the gate source. The corrected criteria gate (a) at h ≥ 0, and leave (a′) and negative heights reported until their terms are derived.
9. **P9:** choose (i), (ii) or (iii), and confirm the "illustrative, validation only" label.
10. **Q-GATE:** keep P1–P10, or state a narrower gate.
11. **DQ-1 … DQ-6** (draft T2 packet §5): geodetic algorithm (α)/(β); density route (km)/(m); simulator wiring; data file and digest location; J2 under the adapter; drag parameter ownership.
12. **Optional:** record the T0 spike's guard behaviour (OI-21) in VAL-0019.

Not a DR-0029 question, but raised by the I-24 bound audit and to be settled in the T2 authorization itself: whether rows conditional on A-FP-2, A-LM-1 or A-LM-2 may gate (validation strategy §3.9). If they are not accepted, those rows are reported only. *(Updated under I-25:)* A-LM-1 is now hypot symmetry and evenness only. Exact z-reflection symmetry and strict density decrease are reported only, whatever is accepted (Review 02 R2-F1, R2-F2).


## Status update (2026-10-24, append-only): independent Review 02
- Codex Review 02 (at `f44a94f`): **REQUEST_CHANGES**, with 2 MAJOR and 1 MINOR. All three are reproduced and ACCEPTED, **not applied** (I-24 §6 stop rule):
  - M3T2R-R2-F1: z-reflection exactness also needs cos to be even, which A-LM-1 omits (U-19, B-11).
  - R2-F2: PM-4 (b) cites a two-sided E3 allowance, but E3 is one-sided (PM-4 (b), B-9).
  - R2-F3: extremum wording in packet P4 item 8.
- Review 01: F1, F2, F4 and F5 are RESOLVED; F3 and F6 are PARTIALLY RESOLVED (through R2-F1 and R2-F2).
- No P1–P9 classification changes. The text above is as reviewed at `f44a94f`.
- Record: `docs/reviews/M3-T2-readiness-review-02.md`.
- *(I-25, append-only)* The closing note on conditional rows is updated for R2-F1/R2-F2. The decision content of §1–§7 is unchanged.
