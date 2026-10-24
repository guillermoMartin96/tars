# DR-0029 P1–P9: owner decision packet (decision readiness for M3 T2)

**Status:** PREPARED FOR OWNER REVIEW. **Nothing in this packet is decided.** Every recommendation below is the implementer's. DR-0029 P1–P9 stay OPEN, and DR-0029 is not edited except for an append-only pointer.  
**Prepared under:** "Authorization I-23 — M3 T2 Decision Readiness and DR-0029 P1–P9 Resolution Preparation" (Tech Lead, 2026-10-24), §5, §9 B.  
**Baseline:** `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`. The verification is in `docs/milestones/M3-T2-decision-readiness-report.md` §1.  
**Authoritative source of every option:** `DR-0029-m3-t0-proposals.md` (P1–P9 sections). Option identifiers and wording are DR-0029's. Where this packet and DR-0029 differ, DR-0029 governs; the differences are listed as new findings (§3).  
**Companion documents:** T2 readiness report, T2 validation strategy, draft T2 authorization packet and M3 open-issues register (`docs/milestones/M3-T2-*.md`, `docs/milestones/M3-open-issues-register.md`).

## Evidence labels used in this packet
| Label | Meaning |
|---|---|
| **[recorded]** | Stated in an accepted repository record, cited by path and section |
| **[measured]** | A numerical result committed in T0/T1 evidence; finite and host-specific unless stated |
| **[derived]** | A mathematical derivation, with its domain and assumptions |
| **[corroborated-I23]** | Checked during I-23, independently of the TARS code (§2) |
| **[judgment]** | Engineering judgment; no proof or measurement behind it |
| **[unverified]** | Assumed or reported, not checked |

## 1. Decision matrix
Classification (I-23 §9 B): **READY FOR OWNER DECISION**, **NEEDS ADDITIONAL EVIDENCE** or **BLOCKED BY ANOTHER DECISION**. "Blocked" here means the decision is coupled to another decision's outcome. Blocked items can still be decided in the same owner response, in the order given in §1.1. **Readiness is not approval.**

| # | Question (authoritative source) | Options | Implementer's recommendation | Classification | Couples to | What T2 builds from it |
|---|---|---|---|---|---|---|
| P1 | Permitted per-scenario termination altitudes h_f (DR-0027 A-4; DR-0029 P1) | A4-a, A4-b (v̂ = v_c or V_b; κ), A4-c | A4-b, v̂ = V_b, as a necessary screen. **κ is an owner value with no default.** Suggestion: κ = 0.01 [judgment] | **READY FOR OWNER DECISION** (owner supplies κ and v̂) | P3, P5, P7 (RM-8); Q-G2-4 (dt) | Nothing directly. The rule is scenario validation (T3). T2 supplies its inputs: the density and geodetic-height components |
| P2 | Crossing detection, location and reporting (DR-0027 A-5; DR-0029 P2) | A5-a, A5-b, A5-c | A5-b; missed dips documented as a limitation | **READY FOR OWNER DECISION** | P3 (outcome name); DR-0026 Q-G3-7 (no telemetry) | The geodetic component must expose the normal n̂ (or latitude), so that T3 can form dh/dt = n̂·v (§3, N-3) |
| P3 | Interaction of termination with domain edges and `impact` (DR-0027 A-6; DR-0029 P3) | Single proposal, items 1–4 | As proposed | **BLOCKED BY ANOTHER DECISION (P1)** | P1 clause 1 (a − b < h_f) | Nothing directly (T3 precedence). T2's height function must not depend on band selection (item 3) |
| P4 | Density for an RK4 stage below the lower edge (DR-0027 A-s; DR-0029 P4) | (i) evaluate the lowest band; (ii) fail closed | (ii) fail closed, with an explicit supersession of the "total density" wording in DR-0026 (§3, N-2) | **READY FOR OWNER DECISION** | P1 (evidence on when the options differ); DR-0026 AR-8/§5.8 | The density component's below-edge behaviour: a typed domain error |
| P5 | Behaviour at unsupported altitudes (DR-0027 B-4; DR-0029 P5) | Per region; alternatives for ≥ 1000 km: fail closed, ρ = 0 (rejected in DR-0024 §12) | As tabulated in DR-0029 P5 | **BLOCKED BY ANOTHER DECISION (P4, P1)** | Row h < 0 is P4; row 0–25 km relies on P1 | The density component's behaviour in every region |
| P6 | GMAT exact-configuration method (DR-0025 Q-G2-1; DR-0029 P6) | (a), (b), (c), (d) | (d) with the pinned settings list; (b) for the J2 link only if the owner rules it inside DR-0028 | **NEEDS ADDITIONAL EVIDENCE** (escalated geodetic-drag discrepancy), plus an owner **ruling** on DR-0028 scope for (b) | DR-0028 P6(b) scope ruling; Q-G2-2 | **Nothing.** T2 has no GMAT dependency (T5) |
| P7 | Reference missions (DR-0025 Q-G2-5; DR-0029 P7) | RM-0 … RM-8 (RM-3b a candidate) | RM-0 … RM-8, RM-8 floor per P1, RM-3b measured in T4 | **BLOCKED BY ANOTHER DECISION (P1, P9)** | P1 (RM-8 floor), P9 (vehicles), T3 orbit kinds (RM-6) | **Nothing.** T2 unit tests use their own documented states |
| P8 | Source of geodetic-height test points (DR-0025 Q-G2-7; DR-0029 P8) | (a), (a′), (b), (c), (d) | (a) + (a′) as the gate source; (b), (c) and the I-23 IOGP example (§2) as corroboration; domain stated. *(I-24, F2: (a′) and negative heights are reported until their terms are derived; item 14)* | **READY FOR OWNER DECISION** | T2 geodetic algorithm choice (§3, N-1) | The geodetic component's test oracle and domain contract |
| P9 | C_d, A, mass and initial-state values for validation scenarios (DR-0024 Q9; DR-0029 P9) | (i), (ii), (iii) | (i), every value labelled "illustrative, validation only" | **READY FOR OWNER DECISION** | P7 (missions) | T2 unit-test vehicle values, if the owner wants them aligned with the scenario values |

### 1.1 Suggested order for one owner response
1. **P1** (with κ and v̂). Then **P3**, which uses P1's clause 1.
2. **P4** (with the N-2 supersession). Then **P5**, whose first rows restate P4 and P1.
3. **P8, P9.**
4. **P7**, after P1 and P9.
5. **P6:** the owner may decide method (d) and the DR-0028 scope ruling now. The escalated investigation stays a precondition of any geodetic GMAT gate (T5).

### 1.2 Gate statement (governing)
- **The Tech Lead's gating rule applies:** "Explicitly identify P10 as a prerequisite for T1 and P1–P10 as prerequisites for T2" (I-15 T0 series, review instruction §6; quoted verbatim in `docs/reviews/raw/M3-T0-codex-review01-prompt.md` line 275, and recorded in `docs/milestones/M3-T0-decision-matrix.md`, "Dependency statement").
- **Consequence:** under that rule, **T2 cannot be authorized until P1–P9 are all decided**, including P6, which needs evidence that does not yet exist.
- **Technical dependency map (implementer's analysis; not governing):**
  - T2's code depends on P4, P5 and P8. P9 matters only for test values.
  - P1, P2 and P3 shape T3 (scenario validation, end condition, contract), and constrain T2's component interfaces.
  - P6 and P7 have no T2 consequence.
- **Question for the owner (Q-GATE):** keep the rule (T2 waits for P6's evidence), or state a narrower gate for T2. A narrower gate could be P1–P5, P8 and P9 decided, with P6/P7 decided before T3/T4. **The implementer does not apply a narrower gate.**

## 2. Independent corroboration performed under I-23
Only checks relevant to P1–P9. Each was run in a session scratch directory; nothing was committed or changed in the repository.

| # | Claim checked | Reference | Result | Independence and limits |
|---|---|---|---|---|
| C-1 | RK4 is stable on the negative real axis for \|λdt\| ≤ 2.785 (P1) | Stability polynomial R(z) = 1 + z + z²/2 + z³/6 + z⁴/24 (any RK text, e.g. Hairer & Wanner, *Solving ODEs II*) | Root of R(z) = 1 on the negative real axis: z = −2.785293563405282 | [corroborated-I23] mathematical; uses no TARS code. It applies to the linear test equation only. The full drag-plus-gravity system is not linear |
| C-2 | RK4's local relative error from stiffness is about (λdt)⁵/120 (P1 κ rationale) | Same polynomial: e^z − R(z) = z⁵/120 + O(z⁶) | At λdt = 0.01: e^z − R(z) = −8.319e-13 against −z⁵/120 = −8.333e-13; at 0.1: −8.196e-8 against −8.333e-8 | [corroborated-I23]. A local error of the linearised problem only. κ = 0.01 → ~1e-12 per step is an estimate, not a trajectory bound (DR-0029 P1 already says so) |
| C-3 | λ = ρ\|v_rel\|/B is the largest decay rate of the drag velocity-Jacobian (P1) | ∂/∂v [−(ρ/2B)\|v\|v] = −(ρ/2B)(\|v\|I + vvᵀ/\|v\|) | Eigenvalues: −ρ\|v\|/B along v, −ρ\|v\|/(2B) twice across it (numerical check at one state agrees to 1e-16 relative) | [corroborated-I23] [derived]. **Velocity block only.** It ignores ∂a/∂r (density gradient, gravity), which the stiffness rule does not cover. DR-0029 says "linearised"; this packet makes the restriction explicit |
| C-4 | a − b = 21 384.69 m (P1 clause 1, P3) | WGS 84 a = 6 378 137 m, 1/f = 298.257223563 [NGA.STND.0036 Table 3.1] | a − b = 21 384.685754820704 m | [corroborated-I23]. The same constants as the model (shared); this checks arithmetic, not the constants |
| C-5 | A printed geodesy standard with test points exists (P8 option (d), "not available") | IOGP Publication 373-7-2, *Geomatics Guidance Note 7, part 2* (EPSG guidance note #7-2), method EPSG 9602 (geographic/geocentric conversions), as cited on epsg.io/9603-method (page revision 2021-09-08) | Input recalled by the implementer: φ = 53°48′33.82″ N, λ = 2°07′46.38″ E, h = 73.0 m (WGS 84). The closed-form forward transformation gives X = 3 771 793.968, Y = 140 253.342, Z = 5 124 304.349 m. epsg.io prints 3 771 793.97, 140 253.34, 5 124 304.35 m; the differences (−2.4, +1.9, −0.6 mm) are inside its 5 mm print rounding | **Partial.** The output values were read from epsg.io. **The input was recalled from memory and the GN 7-2 PDF was not read**; agreement to print rounding supports, but does not prove, the recollection. One point, forward direction only, at centimetre print resolution. It is external and published, but it uses the same closed-form formula as option (a′), so it checks the constants and the formula's transcription, not the inverse algorithm |
| C-6 | C_d = 2.2 has a primary basis (P9) | D. A. Vallado, D. Finkleman, "A critical assessment of satellite drag and atmospheric density modeling", *Acta Astronautica* 95 (2014) 141–165; free copy via AGI white paper | Located, **not read**. Secondary search summaries say that early thermospheric density models assumed C_d ≈ 2.2, and that measured values differ (for example ≈ 2.4 at 510 km in a 2024 *Space Weather* study) | [unverified]. **No primary citation is claimed.** DR-0029 P9's statement "no primary source read" stands |
| C-7 | GMAT's `Earth.NutationUpdateInterval` default is 60 s (P6 finding 1) | GMAT R2026a documentation | No documentation page found; the documentation mirror refused access (HTTP 403) | The value stays **[measured]** in T0 only. No documentary corroboration was obtained |

**What is not corroborated.**
- No independent source was found for the density table beyond DR-0027 B-2's record. The printed Vallado table has still not been read (B-5).
- No independent implementation of the RK4 stage-domain derivation exists beyond T0's second implementation, which shares the authors and the assumptions A-FP-1 … A-FP-3.
- **Agreement between the T0 spike and a future T2 implementation is not independent validation.** Both are coded by the project from the same equations and constants (DR-0025 principle 3).

## 3. New findings from the I-23 analysis (implementer's; for owner disposition)
Each one is classified as an implementer finding, not a review finding. None changes a DR-0029 option or recommendation.

| ID | Finding | Evidence | Affects | Proposed handling |
|---|---|---|---|---|
| **N-1** | **P1/P4's derived stage-domain floors (111 511.97 / 118 633.51 / 124 456.69 m at dt 10 s) are specific to the T0 spike's arithmetic.** ε_h (E1) is derived for `t0_model.geodetic_iterative`: its starting latitude, its stopping rule (\|Δφ\| ≤ 1e-15 or 60 iterations) and its final height formula. E2 is the kilometre route of the density evaluation, and F_D, F_g, F_J are the spike's operation sequences. A T2 implementation with a different algorithm (Vermeille, a fixed iteration count as DR-0026 §5.8 suggests, the metre route of DR-0024 §9) or a different operation order **does not inherit those floors**. | `docs/science/experiments/m3-t0/t0_termination.py` `rounding_allowances` (E1 docstring: "With the stopping rule \|dlat\| <= 1e-15 or 60 iterations"; `LAT_TOL`); `t0_model.density(units="km")` | P1 (evidence only), P4 (the "options agree above the sufficient condition" statement), T2 design | **No P1/P4 option changes:** A4-b is a necessary screen that does not rely on these floors. Before T2, the owner chooses one of two design paths (draft T2 packet §5 DQ-1/DQ-2): **(α)** T2 reproduces the spike's height algorithm and density route operation for operation, verified by inspection and by bitwise comparison over the T0 sample sets; or **(β)** T2 uses another algorithm, and every statement that cites the floors is marked as applying to the spike only, until a new derivation is authorized. **Qualification (I-24, M3T2R-R1-F4):** "operation for operation" applies to the **exterior arithmetic** the floors cover: the height, the km conversion and band selection, the density formula, drag, gravity and the stage positions. It does **not** apply to the spike's domain guard, which T2 must not copy. That guard tests h after the km conversion and accepts −2.475e-321 < h_m < 0 (P4 item 8). The corrected guard (finite h_m < 0 in metres, before conversion) changes only which inputs raise. On every input with h_m ≥ 0 it lets through the same arithmetic as the spike, so no floor and no E1–E6 term changes. Bitwise agreement on samples supports path (α) but does not prove it; the inspection of the complete operation sequence is the primary evidence (Review 01, claim 4) |
| **N-2** | **P4 option (ii) contradicts text in DR-0026.** DR-0026 AR-8 says "runtime functions are total". §5.8 says "density is total (extrapolated bands, DR-0024 §4.6)". Option (ii) makes density raise below 0 m. DR-0024 Q8's Resolution ("No indefinite extrapolation below the modelled domain") already outranks DR-0024 §4.6's candidate, and DR-0026's Resolution does not adopt AR-8 or §5.8 verbatim. Still, the text is unreconciled. | DR-0026 §3 AR-8, §5.8; DR-0024 Resolution Q8; DR-0029 P4 | P4 | If (ii) is chosen, the decision should state that AR-8's "total" and §5.8's "density is total" do not apply below the table's lower edge. The domain error is defined behaviour, mapped to a run outcome at T3 |
| **N-3** | **P2 (A5-b) needs dh/dt = n̂·v.** n̂ is the geodetic normal at the committed state. Unless T3 is to re-derive the normal, T2's geodetic component must expose it, or the latitude it is computed from, and not only h. | DR-0029 P2 table ("dh/dt = n̂·v at both ends") | P2, T2 interface | The T2 interface returns (h, n̂) or (h, φ). This is a design consequence, not an owner decision, recorded so that T2 does not ship a height-only API |
| **N-4** | **Gate breadth.** The governing P1–P10 rule makes T2 wait for P6. P6 needs evidence from GMAT runs (escalated item) that T2 does not use. | §1.2 | T2 schedule | Q-GATE (§1.2): owner's choice |
| **N-5** | **Where the dataset digest lives.** DR-0026 §5.3 says "a pinned data file plus its sha256 in reviewed source (the `approved_digests` pattern)". `approved_digests.py` is in `src/tars/validation`, which the physics core may not import (static guard, DR-0026 §1 "Static guards"). | `src/tars/validation/architecture.py`; DR-0026 §5.3 | T2 design | Pin the table digest in `tars.sim`, following the `approved_digests` *pattern*, not by importing that module. Draft T2 packet DQ-4 |
| **N-6** | **P8 option (d) is partly available.** A published, free standard with a printed WGS 84 forward example exists (C-5). | §2 C-5 | P8 | Record it as corroboration (b′) beside GeographicLib, with C-5's limits. It does not change the recommended gate source |
| **N-7** | **C-3's restriction.** The stiffness rule bounds only the velocity-Jacobian eigenvalue. ∂a/∂r terms (the density scale-height gradient times the drag magnitude, and the gravity gradient) are not in λ. Their size is not quantified in T0. | §2 C-3 | P1 | No change to the recommendation, which is "necessary, not sufficient". The P1 record should say "velocity block" explicitly. A quantification is an optional analysis (§5, X-4) |

## 4. Individual assessments
Each subsection follows I-23 §5 items 1–15. "DR-0029 Px" means the section of that name in `DR-0029-m3-t0-proposals.md`; the evidence it cites is not repeated in full here.

### P1 — Permitted termination altitudes (DR-0027 A-4)
1. **Question.** Which per-scenario termination altitudes h_f (metres, geodetic; DR-0027 A-1, A-2) may a drag scenario state? [recorded: DR-0027 Resolution A-4 "T0 → owner"; DR-0029 P1]
2. **Alternatives.**
   - A4-a: domain-only rule, 0 < h_f < h_initial.
   - A4-b: rule-based admissibility. Clause 1: a − b < h_f < h_geod(initial). Clause 2: ρ(h_f)·v̂·dt/B_min ≤ κ, with v̂ = v_c or V_b and κ pinned.
   - A4-c: a fixed numerical range. This conflicts with the spirit of DR-0027 A-3.
3. **Status.** OPEN. DR-0029 recommends A4-b with V_b; κ and v̂ are owner values with no default.
4. **Dependencies.**
   - κ's numerical consequence depends on dt (Q-G2-4, PROVISIONAL). The rule itself is parametric in dt, so a later dt decision does not reopen P1.
   - P3 item 1 relies on clause 1.
   - P5's 0–25 km row relies on the thresholds.
   - RM-8's floor (P7) is set under P1.
5. **Physical and mathematical assumptions.**
   - No source-backed physical lower limit exists [recorded: DR-0027 A].
   - λ = ρ\|v_rel\|/B, from the velocity block of the drag Jacobian [derived; corroborated C-3].
   - V_b bounds \|v_rel\| for bound states [derived, DR-0029 P1].
   - B_min uses the dry mass.
6. **Numerical consequences.**
   - Exact thresholds at dt 10 s [measured, `termination` → `stiffness_thresholds`]. For κ = 0.01 with V_b: 92 282.07 m (B 25.8) and 84 596.12 m (B 100).
   - The RK4 real-axis limit is κ ≈ 2.785 [corroborated C-1].
   - At κ = 0.01, RK4's linearised local relative error is ≈ 8.3e-13 per step [corroborated C-2]. This is not a trajectory error bound.
7. **Software architecture.**
   - A scenario-validation rule (T3) that evaluates the pinned table at h_f, and one new pinned constant κ in the physics configuration (part of `physics_id`).
   - T2 must make ρ(h) evaluable outside the force path, for validation. That is a seam requirement, not new physics.
8. **Verification.**
   - Clause-by-clause boundary tests at T3: exactly at the threshold, one ulp inside, one ulp outside.
   - A recomputation of the thresholds by an independent root-finder against the T0 values.
   - A mutation that drops each clause.
9. **Compatibility.** No M1/M2 effect: v1/v2 cannot express h_f. T1 is unaffected.
10. **Existing evidence.** DR-0029 P1 and VAL-0019, reviewed in T0 Reviews 01–10 (Review 10 PASS), and accepted with T0 (I-13).
11. **Missing evidence.**
    - The ∂a/∂r contribution to stiffness is not quantified (N-7).
    - Thresholds for the final dt do not exist (they follow Q-G2-4).
    - Neither is needed to choose the rule.
12. **Recommendation.** A4-b, v̂ = V_b, stated as a necessary screen [recorded recommendation, re-affirmed]. κ: the implementer's suggestion stays 0.01 [judgment]. The P1 record should name the velocity-block restriction (N-7).
13. **Confidence.**
    - High that A4-b is better than A4-a and A4-c, given the measured RK4 error growth and divergence.
    - κ's value is judgment.
    - The derived sufficient floors are conditional on A-FP-1 … A-FP-3 and on the spike's arithmetic (N-1).
14. **Proposed acceptance criteria (for T3).**
    - Scenario validation rejects h_f ≤ a − b, h_f ≥ h_geod(initial), and any h_f with ρ(h_f)·v̂·dt/B_min > κ.
    - Each clause is proven at its boundary on both sides.
    - The thresholds are recomputed and match the T0 values at dt 10 s. **Bound (clarified under I-24, M3T2R-R1-F6 audit):** two root brackets of the same function must overlap, and two root estimates differ by at most the sum of the two bracket widths. That needs the same density arithmetic: the T0 thresholds were root-found on the spike's evaluation of the pinned table, "to 0.01 m". If T2's density arithmetic differs (path (β), or route (m)), the comparison is reported, not gated, until the difference is bounded.
15. **Ready?** **READY FOR OWNER DECISION** (κ and v̂ required).

### P2 — Event-crossing behaviour (DR-0027 A-5)
1. **Question.** How is a crossing of h_f detected and located between committed states, and what is reported? [recorded: DR-0027 A-5; DR-0029 P2]
2. **Alternatives.** A5-a (committed state only), A5-b (A5-a plus a scalar cubic-Hermite crossing time in the event), A5-c (step splitting).
3. **Status.** OPEN; DR-0029 recommends A5-b.
4. **Dependencies.**
   - P3 (outcome precedence and name).
   - DR-0026 Q-G3-7 (no per-sample telemetry; NOT AUTHORIZED).
   - Field names are T3 contract proposals.
5. **Assumptions.**
   - **Regularity (corrected under I-24, M3T2R-R1-F5).** h(t) is **not** C² along a drag trajectory in general. The pinned density jumps at band bases (12 downward jumps and the +1.36e-3 upward jump at 25 km; DR-0029 P1, DR-0025 Resolution principle 5), so the drag acceleration, and with it ḧ = n̂·r̈ + (curvature term), jumps wherever the trajectory crosses a base with a nonzero normal component of the jump. What holds, for a trajectory outside the ellipsoid and outside the evolute region, with finitely many base crossings per step [assumption, stated]:
     - h is C¹, and ḣ = n̂·v is continuous (r is C¹; the height function is smooth there);
     - ḧ exists and is continuous except at the crossing times, where it has one-sided limits;
     - so ḣ is absolutely continuous and ḧ is bounded and piecewise continuous.
   - The chord inequality holds under exactly that regularity: dip ≤ (dt²/8)·ess sup max(ḧ, 0), with the supremum taken almost everywhere (it ignores the finitely many crossing instants) [derived: for g = h − chord, g(t0) = g(t1) = 0 and g'' ≤ M a.e. with g' absolutely continuous give g(t) ≥ −M(t − t0)(t1 − t)/2 ≥ −M dt²/8]. It does not need C².
   - **The certified numbers are unaffected:** DR-0029 P2's certified table is two-body only, where there is no drag, h is smooth, and the C² statement was true.
   - No certified bound exists for J2 + drag [recorded: DR-0029 P2, Review 02 R2-F1]. This correction does not create one.
6. **Numerical consequences.**
   - Hermite − DOP853: −0.07 … −0.41 s, which is RK4's own timing error [measured].
   - Committed-state-only: up to +9.26 s and 3.06 km low [measured].
   - Certified two-body missed-dip bound at dt 10 s: 0.74–0.80 m circular, ≈ 5.3–5.6 m at e = 0.04 [derived].
7. **Architecture.**
   - No extra force evaluation; reuses the existing Hermite technique of `AscendingNodeDetector` (`src/tars/sim/simulator.py` `_hermite_root`).
   - **T2 consequence (N-3):** the geodetic component exposes n̂ or φ.
   - A5-c would add root finding to the step loop, akin to Q-G2-3 (b), which was not approved.
8. **Verification.**
   - Crossing-time accuracy against DOP853 events on the same model (P class).
   - Agreement between the scalar and vector Hermite variants.
   - A known-answer case on a constructed trajectory.
   - Missed-dip limitation tests, two-body only, for the certified bound.
9. **Compatibility.** `impact` semantics unchanged; M1/M2 unchanged.
10. **Existing evidence.** DR-0029 P2, VAL-0019, and the GMAT stop Δ −0.023 s [measured, one case].
11. **Missing evidence.** A perturbed-motion missed-dip bound. A5-b does not need one; any use that needs a guaranteed magnitude stays blocked [recorded].
12. **Recommendation.** A5-b; missed dips documented, not detected.
13. **Confidence.** High for A5-b as specified. The perturbed missed-dip magnitude is unknown.
14. **Acceptance criteria (T3).**
    - The reported `crossing_t_s` lies in [t_{k−1}, t_k] of the final step.
    - It agrees with the scalar-Hermite root recomputed from the committed endpoints to round-off.
    - The run ends at the committed state.
    - The method identifier is versioned.
    - Documentation states that `crossing_t_s` is not a state.
15. **Ready?** **READY FOR OWNER DECISION.**

### P3 — Domain edges and `impact` (DR-0027 A-6)
1. **Question.** How does termination interact with the table's lower edge, band edges and the v1/v2 `impact` rule? [recorded: DR-0027 A-6; DR-0029 P3]
2. **Alternatives.** A single proposal with items 1–4. The precedence order (`non_finite` → `reentry` → `impact` → `escape`) is a design choice, and other orders are possible.
3. **Status.** OPEN.
4. **Dependencies.**
   - **Item 1 relies on P1 clause 1** (h_f > a − b). Under A4-a, `impact` could be the reported outcome for h_f ≤ a − b, and item 1's statement would be false.
   - Precedence names: T3 contract.
5. **Assumptions.** For a point outside the ellipsoid, \|r\| − a ≤ h ≤ \|r\| − b [derived; corroborated C-4 for a − b].
6. **Numerical consequences.** Termination uses height only and never band selection. The exact-base ambiguity is a property of the published model (DR-0024 Q5a).
7. **Architecture.** One precedence function in the runner (T3). T2's height function must not branch on band selection.
8. **Verification.**
   - A same-tick test with both `reentry` and `impact` true (the T0 stress input).
   - Tests at h exactly a − b, and one ulp either side, under P1.
9. **Compatibility.** `impact` unchanged as a backstop, so v1/v2 behaviour is unchanged.
10. **Existing evidence.** DR-0029 P3; T0 stress input `termination` → `admissibility_counterexamples`.
11. **Missing evidence.** None for the proposal as stated, once P1 is decided.
12. **Recommendation.** As proposed, decided after or with P1.
13. **Confidence.** High; the geometry is exact.
14. **Acceptance criteria (T3).**
    - The precedence is deterministic and table-driven.
    - The same-tick case reports `reentry`.
    - Whenever `impact` holds and h_f > a − b, `reentry` holds.
15. **Ready?** **BLOCKED BY ANOTHER DECISION (P1).**

### P4 — Density below the lower edge (DR-0027 A-s)
1. **Question.** What density does an RK4 stage below the table's lower edge (0 m geodetic) receive? [recorded: DR-0027 Resolution A-s OPEN; DR-0029 P4]
2. **Alternatives.** (i) evaluate the lowest band's formula, with the committed-state check ending the run; (ii) fail closed.
3. **Status.** OPEN. DR-0027's original body recommended (i); DR-0029 recommends (ii).
4. **Dependencies.**
   - P1, as evidence only: the options differ only when a stage leaves the domain.
   - N-2: DR-0026 AR-8 and §5.8 wording.
   - The failure-cause name is T3.
5. **Assumptions.**
   - DR-0024 Q8: "No indefinite extrapolation below the modelled domain" [recorded].
   - The inward RK4 stage (k3's input) sits ≈ 117 m below the path in LEO at dt 10 s [measured, derived].
6. **Numerical consequences.**
   - The two options are bitwise identical for every run whose stages stay above 0 m.
   - That is guaranteed above the derived sufficient floor (≈ 111.5–124.5 km at dt 10 s), **under A-FP-1 … A-FP-3 and for the spike's arithmetic only (N-1)**.
   - An admissible stress input reaches −28 km.
7. **Architecture.**
   - The density component raises a typed domain error (for example a `ValueError` subclass). The error leaves the step uncommitted, which the existing atomic step already guarantees for any exception.
   - The mapping to a run outcome (`outside_atmosphere_domain` or similar) is T3.
   - `Simulator.step` catches only `OverflowError` and `ZeroDivisionError`, so a domain error propagates unchanged. That is acceptable for T2 and must be handled in T3.
8. **Verification (corrected under I-24, M3T2R-R1-F4).**
   - **Raise:** the largest negative binary64 (−5e-324, i.e. −2^-1074), −2.475e-321, −1e-300, −1e-9 m, −1 m and −100 km.
   - **Evaluate band 0:** +0.0, −0.0, +5e-324 and one ulp above any interior point. **0 m is in the domain and does not raise** (the I-23 text listed it in both groups; that was a typo).
   - **−0.0** is not "below the lower edge": IEEE 754 compares −0.0 equal to 0, and `-0.0 < 0` is false. The specification says so explicitly, so that an implementation testing the sign bit (for example `math.copysign`) is not mistaken for a correct one.
   - A step whose k3 stage would go below 0 raises, and the state, tick and engine schedule are unchanged (the atomicity test pattern of REV-T2-01).
   - **Recorded T0 behaviour, which a T2 implementation must not copy (I-24 reproduction; Review 01 F4).** The spike's kilometre route (`t0_model.density(units="km")`) divides by 1000 **before** its domain check, `h_km = h_m / 1000.0; if h_km < 0: raise`. For every binary64 h_m with −2.475e-321 < h_m < 0 (from −5e-324 down to −2.47e-321, its binary64 neighbour), h_m/1000 rounds to −0.0, so the check passes and the spike returns band 0's ρ₀ = 1.225 kg/m³. The first negative input that raises is h_m = −2.475e-321, the largest-magnitude negative h whose quotient is the smallest subnormal, −5e-324. The spike's metre route (`units="m"`) compares h_m with 0 directly and raises for −5e-324. Evidence: `docs/reviews/raw/M3-T2-readiness-I24-evidence/i24_reproduction.out`.
   - This is a defect of the spike's **test-code guard**, outside every derived T0 floor (all of which assume a true height ≥ 0 and a computed stage height > 0). No T0 result changes, and no T0 file is edited. Recording it in VAL-0019 is optional and for the owner (open-issues register OI-21).
9. **Compatibility.** M1/M2 have no density, so they are unaffected.
10. **Existing evidence.** GMAT R2026a fails closed below the ellipsoid [measured]; the decay measurements; the stress input.
11. **Missing evidence.** None for the choice. The guarantee of non-occurrence is conditional (N-1, A-FP-2).
12. **Recommendation.** (ii) fail closed, with the N-2 supersession stated in the decision.
13. **Confidence.** High. It matches DR-0024 Q8 and GMAT.
14. **Acceptance criteria (T2) (corrected under I-24, M3T2R-R1-F4).** These are **proposed T2 requirements under option (ii)**, not a description of the T0 spike.
    - **The guard is applied to the height in metres, before any unit conversion:** the component raises the typed domain error for every finite h_m with h_m < 0 (IEEE comparison, so −0.0 is in the domain).
    - It returns band 0's formula for 0 ≤ h_m < 25 000 m, including h_m = −0.0.
    - Non-finite h raises a distinct error, before the domain check.
    - The raise is tested across the T0 trap interval (−5e-324, −2.47e-321 and values between, all of which the spike's km route accepts) and at −2.475e-321, and the non-raise at ±0.0 and +5e-324.
    - The atomicity of a raising step is tested.
    - Under option (i) the criteria differ (no raise; the lowest band's formula below 0), and these tests would be replaced, not loosened.
15. **Ready?** **READY FOR OWNER DECISION.**

### P5 — Unsupported altitudes (DR-0027 B-4)
1. **Question.** How does the simulator behave below the lowest base, in the 0–25 km disputed cell, in 900–1000 km and above 1000 km? [recorded: DR-0027 B-4 CONDITION; behaviour OPEN]
2. **Alternatives.** DR-0029 P5 table. For ≥ 1000 km: extrapolate the top band (recommended), fail closed above 1000 km, or ρ = 0 above a cutoff (rejected, DR-0024 §12).
3. **Status.** OPEN.
4. **Dependencies.** Row h < 0 is P4. Row 0–25 km uses P1's thresholds ("not an admissible h_f"); stages can still reach it.
5. **Assumptions.**
   - Pinned table B-1 (sha256 `75762f67…`).
   - GMAT's documented "no lower or upper altitude limit" [recorded: GMAT-UG via DR-0024 §4.6].
   - No claim of textbook agreement (B-5).
6. **Numerical consequences.**
   - Above 1000 km, pinned vs author's file: +19.6 % / +145 % / +500 % at 1100/1500/2000 km [recorded: DR-0027 B-2].
   - Drag at 1000 km ≈ 3e-9 m/s² at B 25.8 [derived].
   - In the 0–25 km cell the density is 0.13785 % lower than the author's file [recorded].
7. **Architecture.**
   - One density function, total above 0 m, with a documented label "above 1000 km: unverified".
   - Underflow: the top-band density becomes subnormal above ≈ 181 890 km and exactly 0 above ≈ 191 735 km [measured/derived in T0]. The component must return those values, not raise.
8. **Verification (corrected under I-24, M3T2R-R1-F1).**
   - Every one of the 27 bases, exactly and one ulp either side (DR-0025 principle 5; DR-0024 Q5a).
   - The disputed cells evaluated as published.
   - **At 1000 km the table is discontinuous, and the test checks that discontinuity, not continuity.** The 900 km band's left limit at 1000 km is 3.0190482489066533e-15 kg/m³ against the 1000 km row's 3.019e-15, a relative jump of −1.5981e-5 (Review 01 F1; reproduced under I-24, where two evaluation orders agree to 12 digits). 1000 km is one of DR-0029 P1's 12 downward jumps. DR-0024 Q5a ("No value is altered to force continuity") forbids removing it. The spike returns 3.0190482489066557e-15 at 1000 km − 1 ulp (900 km band), 3.019e-15 exactly at 1000 km and 3.0189999999999988e-15 at + 1 ulp, on both routes.
   - **Above 1000 km** the top band's formula is a single exponential, continuous and smooth for h > 1000 km. That smoothness *within* the band is what can be tested, by the region and value checks below.
   - Subnormal and zero densities are returned without exception.
9. **Compatibility.** None with M1/M2.
10. **Existing evidence.** VAL-0019 (`atmosphere`, `gmat` → `density_probes`).
11. **Missing evidence.**
    - No source for densities above 1000 km (unverifiable by design).
    - The printed-table check (B-5) is still open.
    - Neither blocks the decision.
12. **Recommendation.** As tabulated in DR-0029 P5.
13. **Confidence.** High for the mechanism. Above 1000 km the density is explicitly unverified.
14. **Acceptance criteria (T2) (corrected under I-24, M3T2R-R1-F1).**
    - The density component's region behaviour matches the decided table exactly.
    - Band selection follows GMAT's rule (h < base[i+1]).
    - Each base, **including 1000 km**, is tested exactly and one ulp either side. The value on each side is the formula of the band GMAT's rule selects, with the published discontinuity intact.
    - Above 1000 km, values equal the top band's formula.
    - Records label > 1000 km as unverified.
    - **No criterion requires continuity at any band base.**
    - **Wording in DR-0029 P5 (documented, not changed).** P5's proposal cell for ≥ 1000 km reads "Extrapolate the top band (continuous, GMAT-identical)". Read as "continuous at 1000 km", it contradicts DR-0029 P1's list of 12 downward jumps (which includes 1000 km) and DR-0024 Q5a. Read as "continuous within the top band above its base", in contrast to the ρ = 0 cutoff DR-0024 §12 rejected for introducing a discontinuity, it is correct. I-23 used the first reading. P5 is OPEN, so this is unapproved proposal text, but it is the text the owner would approve. **Proposed amendment, for the owner to adopt with the P5 decision or reject:** replace "(continuous, GMAT-identical)" with "(the top band's formula, continuous for h > 1000 km; the 1000 km base keeps the published −1.598e-5 relative jump, like every other base; GMAT-identical)". DR-0029 carries an append-only note of this, and its P5 table is unchanged.
15. **Ready?** **BLOCKED BY ANOTHER DECISION (P4 for its first row, P1 for its second).** It can be decided in the same response, after them.

### P6 — GMAT exact-configuration method (DR-0025 Q-G2-1)
1. **Question.** How is GMAT R2026a configured and compared so that it counts as an independent exact-configuration reference? [recorded: DR-0025 Resolution Q-G2-1 DEFERRED to T0 checkpoint; DR-0029 P6]
2. **Alternatives.**
   - (a) TOEEq exchange plus a derived Earth-orientation bound.
   - (b) drive the validator reference with GMAT's reported axis.
   - (c) informational only.
   - (d) a decomposed exact configuration.
3. **Status.** OPEN; the geodetic-drag discrepancy is **ESCALATED_FOR_INVESTIGATION**.
4. **Dependencies.**
   - **DR-0028 P6(b)**: the owner's scope ruling on whether (b) is "additional Earth-orientation implementation".
   - Q-G2-2 (the identity-check rule stays PROPOSED; the settings list relies on it).
5. **Assumptions.**
   - J-ax-1.
   - GMAT's EOP file (sha256 `52c95d68…`) defines its axis.
   - `NutationUpdateInterval` 60 s is the default [measured; not documentarily corroborated, C-7].
6. **Numerical consequences.**
   - J2 0.076 mm with GMAT's axis at interval 0.
   - Spherical drag 2 mm.
   - Geodetic drag 0.14–0.38 m, unexplained and dependent on interval and segmentation [measured].
7. **Architecture.** A T5 GMAT generator and settings list. **No T2 consequence.**
8. **Verification.** Per (d): J2 link exact (b) or bounded (a); spherical-drag link; geodetic height checked by P8 points.
9. **Compatibility.** The M3-form GMAT passes every M1 gate (6.95e-6 m against 1e-4 m) [measured].
10. **Existing evidence.** VAL-0019, DR-0029 P6 tables.
11. **Missing evidence.** Attribution of the 0.137 m geodetic-drag difference at interval 0, and of the segmentation dependence. **Smallest analysis (proposal X-1, §5).**
12. **Recommendation.** (d) with the pinned settings list. (b) for the J2 link only if the owner rules it inside DR-0028; otherwise (a). The escalated item is resolved before T5 proposes any geodetic GMAT gate.
13. **Confidence.** Medium. The method is sound for the attributed links; the geodetic link is unexplained.
14. **Acceptance criteria (T5).**
    - Every GMAT comparison records the DR-0025 principle 2 settings.
    - The J2 link meets its derived or measured bound.
    - No geodetic trajectory comparison is gated until X-1 attributes the residual.
15. **Ready?** **NEEDS ADDITIONAL EVIDENCE.**
    - Method (d) and the DR-0028 ruling can be decided now; the ruling needs no evidence.
    - Full resolution needs X-1.
    - **No T2 work depends on it**; it blocks T2 only through the governing gate (§1.2).

### P7 — Reference missions (DR-0025 Q-G2-5)
1. **Question.** Which reference missions does M3 use? [recorded: DR-0025 Resolution Q-G2-5 DEFERRED to T0; DR-0029 P7]
2. **Alternatives.** RM-0 … RM-8 as listed. RM-3b is a no-crossing candidate, not run. Subsets or additions are possible.
3. **Status.** OPEN.
4. **Dependencies.**
   - P1 (RM-8 floor).
   - P9 (vehicles V1, V2).
   - T3 orbit kinds (RM-6 needs an elliptic or Cartesian state).
   - Q-G2-4 (dt).
5. **Assumptions.**
   - M1's state lies exactly on the 250 km band base, so RM-3/4/5/7 start on a boundary.
   - Every apogee is < 900 km (P5).
6. **Numerical consequences.** Per-mission GMAT and spike residuals [measured, DR-0029 P7].
7. **Architecture.** Scenario files (T3); references (T4/T5). **No T2 consequence.**
8. **Verification.** Mission tests (T3), validators (T4), GMAT (T5).
9. **Compatibility.** RM-0 is the perturbations-off regression (M1 golden bitwise [measured on the reference host]).
10. **Existing evidence.** DR-0029 P7 table.
11. **Missing evidence.** RM-3b not measured. Smallest experiment X-2 (§5), or defer to T4 as DR-0029 recommends.
12. **Recommendation.** RM-0 … RM-8, RM-8 floor per P1, RM-3b measured in T4.
13. **Confidence.** Medium-high. The list covers DR-0025 VO-1 … VO-9.
14. **Acceptance criteria (T3/T4).** Each mission maps to its DR-0025 oracles; each scenario's values carry the P9 label; RM-8's h_f passes P1.
15. **Ready?** **BLOCKED BY ANOTHER DECISION (P1, P9).**

### P8 — Geodetic-height test points (DR-0025 Q-G2-7)
1. **Question.** What is the source of geodetic-height test points for the gate? [recorded: DR-0025 Resolution Q-G2-7 DEFERRED to T0; DR-0029 P8]
2. **Alternatives.**
   - (a) exact answers;
   - (a′) forward-constructed points;
   - (b) GeographicLib CartConvert(1) examples;
   - (c) GMAT `Earth.Altitude`;
   - (d) a printed geodesy source. **Now partly available: C-5 (IOGP GN 7-2).**
3. **Status.** OPEN.
4. **Dependencies.**
   - The T2 algorithm choice (N-1; draft packet DQ-1).
   - FC-4 (axisymmetry; DR-0024 Q4 revision 2).
5. **Assumptions.**
   - WGS 84 a, 1/f [NGA].
   - The ellipsoid axis is frame +Z (J-ax-1).
   - The algorithm is valid outside the evolute region.
6. **Numerical consequences.**
   - (a)/(a′): ≤ 3e-9 m for two algorithms [measured].
   - (b): within 5 mm print rounding.
   - (c): ≤ 1.3 mm at mid-latitude; fails on the axis.
   - C-5: ≤ 2.4 mm against cm print.
7. **Architecture.**
   - One geodetic component with a stated domain that rejects points inside the evolute region.
   - It exposes h and n̂ or φ (N-3).
8. **Verification.**
   - (a′) is independent of the inverse algorithm only if the forward formula shares no code with it. It is P class (DR-0025).
   - (a) exact answers on the equator and axis.
   - Both sides of each domain boundary.
   - FC-4 axisymmetry, exact.
9. **Compatibility.** SCI-0006 (reported altitude, `impact`) unchanged for v1/v2.
10. **Existing evidence.** VAL-0019 (`geodetic`, `gmat` → `geodetic_points`); C-5.
11. **Missing evidence.**
    - A mm-resolution printed point set (GN 7-2's own printed values were not read).
    - Not needed for the gate source recommended.
12. **Recommendation.** (a) + (a′) as the gate source. (b), (c) and C-5 as recorded corroboration with their limits. Domain stated; on-axis points tested. *(Qualified under I-24, F2: as a gate, (a) applies at h ≥ 0 now; (a′) applies once its forward-construction term is derived; negative heights are reported. Item 14.)*
13. **Confidence.** High for the gate source. The external corroboration is coarse (mm to cm).
14. **Acceptance criteria (T2) (corrected under I-24, M3T2R-R1-F2).**
    - **What E1 covers.** ε_h(h) = αh + β (α = 1.22e-15, β = 8.88e-9 m; 9.02e-9 m at 120 km) bounds |ĥ(r) − h_true(r)|. Here ĥ is the computed height of `t0_model.geodetic_iterative` for a **given binary64 input r**, and h_true is the exact geodetic height of that same r on the model's ellipsoid (a and e2 as the binary64 values the code uses).
      - **Domain:** points outside the ellipsoid (true height ≥ 0), no overflow. The derivation uses "the distance to a convex body is the maximum over supporting planes", which holds only outside, and the committed record says "true geodetic height >= 0" (`t0_termination_results.json` → `floating_point_enclosure` → `assumptions` → `domain`; `t0_termination.rounding_allowances` docstring, E1).
      - **Algorithm:** the spike's iteration and stopping rule (N-1). Under path (β) E1 does not apply at all.
      - **Error covered:** the inverse's evaluation error only. It covers neither the rounding of a forward-constructed input nor the error of a reference value.
    - **Exact-answer points (option (a)), h ≥ 0, path (α): gated with ε_h** (E1 itself rests on A-FP-2; validation strategy §3.9 B-12), provided the reference has no error of its own. It must be evaluated in exact rational arithmetic on the model's ellipsoid. Equator: r = (x, 0, 0) with binary64 x ≥ a, reference x − a. Axis: r = (0, 0, z) with |z| ≥ b_model, reference |z| − a√(1 − e2_model), using a 60-digit or exact evaluation with outward rounding, as T0's oracle does.
      - The difference between the model's ellipsoid and WGS 84's exact 1/f is a constant-definition term, reported separately and not absorbed into ε_h: b_model − b_WGS84 = +1.71e-12 m (I-24 reproduction, `i24_reproduction.out`).
    - **Forward-constructed points (option (a′)), h ≥ 0, path (α): gated only after two further terms are derived and reviewed in T2.**
      - (1) δ_f, the rounding of the forward construction r̂ = fl(forward(φ, λ, h_nom)). Then |h_true(r̂) − h_nom| ≤ |r̂ − r_exact| ≤ δ_f, because exterior geodetic height is the distance to a set, and so 1-Lipschitz. This needs both r̂ and r_exact outside the ellipsoid, for example h_nom > δ_f.
      - (2) Or, instead of δ_f, an oracle evaluation of h_true(r̂) with its own stated error.
      - The gate would then be ε_h + δ_f (or ε_h + the oracle error).
      - **Until a term is derived and reviewed, these points are reported, not gated.** No replacement number is proposed here.
    - **Negative heights (−10 km … 0) are reported, not gated**, for both (a) and (a′), until a bound is derived for points inside the ellipsoid. E1 does not apply there.
    - Path (β): every geodetic comparison is reported, not gated, until its own derivation exists.
    - Evolute-region points are rejected.
    - (b)/(c)/C-5 are reported, not gated.
    - The T0 measurements (≤ 1.9e-9 m on 640 (a′) points, ≤ 2.06e-9 m on 13 050 sampled points) are observations, not bounds, and are not proposed as thresholds.
15. **Ready?** **READY FOR OWNER DECISION.**

### P9 — Validation-scenario parameters (DR-0024 Q9)
1. **Question.** C_d, A, mass and initial states for validation scenarios. [recorded: DR-0024 Resolution Q9, "values DEFERRED to the T0 checkpoint"; DR-0029 P9]
2. **Alternatives.**
   - (i) V1 = 850 kg, 15 m², C_d 2.2 (B 25.8 kg/m²), plus V2 = the M2 vehicle with A 15 m².
   - (ii) (i) plus a B 100 variant of RM-4.
   - (iii) a cited real vehicle class (none read).
3. **Status.** OPEN.
4. **Dependencies.** P7 (which missions use which vehicle); T3 orbit kinds for initial states.
5. **Assumptions.**
   - Cannonball model: only B = m/(C_d A) enters the dynamics.
   - The validation oracles test correctness for a given B, not realism [recorded, DR-0029 P9].
   - C_d 2.2 is a convention: the GMAT default [measured] with secondary sources only [C-6].
6. **Numerical consequences.**
   - B + 1 % → 4.8 km after 10 orbits [measured, VAL-0018].
   - B 25.8 → −12.8 km/day at 250 km.
7. **Architecture.** Scenario inputs (T3). T2 unit tests may use the same values for alignment.
8. **Verification.** Exact-value identity in scenario files; the label "illustrative, validation only" present in every record.
9. **Compatibility.** V2 reuses the M2 vehicle without changing M2 scenarios.
10. **Existing evidence.** DR-0029 P9; VAL-0018/0019.
11. **Missing evidence.**
    - A primary source for C_d 2.2 (C-6 located a candidate, unread).
    - Not needed for validation-only values.
12. **Recommendation.** (i), all values labelled illustrative. (ii) only if the owner wants a low-drag case gated.
13. **Confidence.** High for validation use. No realism claim is made.
14. **Acceptance criteria (T3).**
    - Scenario values are exact as decided.
    - The GMAT C_d is set explicitly (GMAT's default is 2.2000000000000002 [measured]).
    - Records carry the label.
15. **Ready?** **READY FOR OWNER DECISION.**

## 5. Proposed analyses and experiments (NOT authorized; each needs separate authorization)
| ID | Resolves | Smallest scope | Expected outputs | Isolation | Acceptance criteria |
|---|---|---|---|---|---|
| X-1 | P6 escalation (geodetic-drag 0.137 m; segmentation dependence) | 1. Read the GMAT R2026a sources for `CalculateGeodetics` and the atmosphere's rotation-matrix caching. 2. Rerun the T0 geodetic-drag configuration at intermediate `NutationUpdateInterval` values (for example 0, 1, 10, 30, 60 s) and two segmentations. 3. Isolate a single step: GMAT density and acceleration at one state against the spike | A VAL record and a results JSON in a new directory `docs/science/experiments/m3-p6/`; no T0 file rewritten | New experiment directory; T0 results and GMAT references untouched; GMAT private copy, as in T0 | The residual is attributed term by term to within the stated GMAT height rule (≤ 1.4 mm), or the item stays escalated with what was excluded |
| X-2 | P7 RM-3b | Spike plus GMAT run of a circular 275 km mid-band mission over 53 700 s | Residual and band-change count | As X-1 | Zero band changes over the horizon, or a documented count; residual reported, not gated |
| X-3 | N-1 path (α) feasibility | Document the operation sequence of `geodetic_iterative` and `density(units="km")` as a specification T2 must match | A specification note in the T2 packet; no code | Docs only | The owner accepts or rejects path (α) |
| X-4 | N-7 | Bound \|∂a_drag/∂r\|·dt² relative to λdt at the P1 thresholds, analytically | A derivation appended to the P1 record | Docs only | A stated bound with its domain; no change to κ unless the owner decides |

None of these is required to decide P1–P5, P8 or P9.

## 6. What this packet does not do
- It decides nothing, approves nothing, and does not change any DR's Resolution.
- It does not change any number in DR-0029, VAL-0019 or any T0/T1 record.
- It does not narrow the governing T2 gate.
- It runs no experiment that writes a tracked file.

## Status update (2026-10-24, append-only): independent Review 01
- Codex Review 01 (at `5ee6a6a`): **REQUEST_CHANGES**, with 2 MAJOR (M3T2R-R1-F1: 1000 km continuity; F2: E1 reused beyond h ≥ 0), 3 MINOR (F3 strict monotonicity; F4 lower-edge typo and the −5e-324 guard; F5 C² across band edges) and 1 NOTE (F6). All are reproduced and ACCEPTED, **not applied** (I-23 §10).
- No P1–P9 classification changes. The text above is as reviewed.
- Record: `docs/reviews/M3-T2-readiness-review-01.md`.

## Correction log (I-24, 2026-10-24): Review 01 findings F1–F6
Made under "Authorization I-24 — M3 T2 Readiness: Review 01 Corrections and Independent Review 02" (Tech Lead, 2026-10-24). This is documentation only. The wording as Review 01 reviewed it is preserved at commit `5ee6a6a`, and the Review 01 record is unchanged. **No P1–P9 option, classification or recommendation changes, and nothing is decided.** Q-GATE, DQ-1 … DQ-6 and the P6 investigation stay open. The finding-by-finding matrix is in `docs/reviews/M3-T2-readiness-review-01-corrections.md`.

- **F1 (P5 items 8, 14):**
  - The continuity requirement at 1000 km is removed.
  - The 1000 km base is tested like every other base, with its published −1.598e-5 jump.
  - Smoothness is claimed only within the top band, above 1000 km.
  - The ambiguous "(continuous, GMAT-identical)" wording in DR-0029 P5 is documented, and an amendment is proposed for the owner. DR-0029's P5 table is not changed.
- **F2 (P8 item 14):** E1 is restricted to its derived domain: exterior points, the inverse's evaluation error, the spike's algorithm. Negative heights and forward-constructed points are reported until their terms are derived. The reference must be exact on the model's ellipsoid.
- **F3:** affects the validation strategy only (PM-4); no packet text claimed strict monotonicity.
- **F4 (P4 items 8, 14; N-1):**
  - The "0 m raises" typo is removed.
  - The guard is specified in metres, before conversion, with −0.0 inside the domain.
  - The spike's trap interval (−2.475e-321, 0) is recorded as T0 behaviour that T2 must not copy.
  - Path (α) is qualified so that it excludes the guard.
- **F5 (P2 item 5):** the C² claim is replaced by piecewise regularity. The chord bound is restated with an essential supremum, and the certified two-body numbers are unaffected.
- **F6 (P1 item 14):** the threshold-agreement bound is stated as the sum of the bracket widths, valid for identical density arithmetic only. The strategy's bound audit is in `M3-T2-validation-strategy.md` §3.9.
- **Classification:** unchanged.
  - READY FOR OWNER DECISION: P1 (κ, v̂), P2, P4, P8, P9.
  - BLOCKED BY ANOTHER DECISION: P3 (P1), P5 (P4, P1), P7 (P1, P9).
  - NEEDS ADDITIONAL EVIDENCE: P6.
- **Owner briefing:** `DR-0029-P1-P9-owner-briefing.md`.
