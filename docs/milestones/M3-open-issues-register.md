# M3 open-issues register (outside and beside T2)

**Status:** INDEX, as of `main` = `fc50aed` (2026-10-24). **Nothing here is resolved or expanded by this register.** Each item points to its authoritative record, which governs. An item is described only as far as it touches T2 (I-23 §9 E).  
**Prepared under:** I-23 §9 E.

| # | Item | Authoritative record | Status | Blocks | T2 relation |
|---|---|---|---|---|---|
| OI-1 | **Q-G2-1 / DR-0029 P6:** GMAT exact-configuration method; geodetic-drag residual (0.137 m at interval 0; segmentation dependence) | DR-0025 Resolution; DR-0029 P6 | DEFERRED; **ESCALATED_FOR_INVESTIGATION** | T5 geodetic GMAT gates; T2 only through the governing P1–P10 gate | None technically. Proposed analysis X-1 (decision packet §5) |
| OI-2 | **DR-0028 P6(b):** is driving a *validator* reference with GMAT's reported axis inside "No additional Earth-orientation implementation is authorized"? | DR-0028 T0 note; DR-0029 P6 | Ruling requested; undecided | Choosing P6 (b) for T5 | None |
| OI-3 | **Q-G2-2:** constants verified by identity, not by trajectory gates | DR-0025 Resolution | PROPOSED | The P6 settings list relies on it | T2 constant tests are C class and do not adopt it |
| OI-4 | **Secular-rate tolerance and presentation** (T1 Q1: Ω̇, ω̇ against first-order theory, informational) | T1 report §7, §9.1; VAL-0020 | No tolerance; non-gating | Promoting Q1 to a gate | None. The analogous T2 decay-oracle comparison (Q6) is also informational until a derived bound exists |
| OI-5 | **T3 axis representation:** the fixed +Z axis has no configuration representation yet; it is to be pinned in `PhysicsConfiguration` | T1 report §9.5; T1 packet §12.1; ADR-0009 item 17 | Open (T3) | T3 | T2 adds no axis parameter |
| OI-6 | **T4/T5 comparison requirements:** DOP853 and GMAT comparisons; M3 Proof; snapshot treatment (Q-G2-6, DEFERRED to T4) | DR-0025 §9–10, Resolution | Open | T4–T6 | None |
| OI-7 | **M3 final time step** (dt = 10 s PROVISIONAL) | DR-0025 Q-G2-4 | PROVISIONAL; measured at the designated task | P1 numerical thresholds (the rule is dt-parametric); T6 | T2 uses explicit dt in tests; no claim depends on the final dt |
| OI-8 | **External corroboration:** combined J2 + drag + burn rests on GMAT alone; no real-atmosphere validation; J2 has no external comparison in T1 | DR-0025 §11–12; T1 dossier | Stated gaps | — | Unchanged. I-23 added coarse geodetic corroboration only (packet C-5) |
| OI-9 | **T4/T5 requirements tied to P7:** RM-3b unmeasured; RM-6 needs an elliptic or Cartesian v3 orbit kind | DR-0029 P7 | Open | T3–T5 | None |
| OI-10 | **A-FP-2** (libm accuracy) measured on one host; E4b depends on it | DR-0029 P1 | Assumption | Any claim resting on the T0 derived floors | T2 can measure cross-platform libm behaviour (validation strategy X-P3) |
| OI-11 | **Combined J2 + drag missed-crossing bound** | DR-0029 P2 | None derived | Any use needing a guaranteed missed-dip magnitude | None (A5-b does not need it) |
| OI-12 | **Unreproduced 5 287-point search** quoted in the T0 Review 04 record | T0 Review 04/06 records | UNREPRODUCED | Nothing | None |
| OI-13 | **Printed Vallado table not checked** (DR-0027 B-5); disputed cells documented | DR-0027 B-2, B-5 | Condition | A dataset identity change if it differs | T2 pins B-1 verbatim |
| OI-14 | **Per-sample environment telemetry** | DR-0026 Q-G3-7 | NOT AUTHORIZED | Any such event | None |
| OI-15 | **DR-0026 AR-8 / §5.8 "total density"** against P4 (ii) | DR-0026; decision packet N-2 | New, unreconciled | P4 record | Supersession requested with P4 |
| OI-16 | **Algorithm-specificity of the T0 derived floors** | Decision packet N-1 | New | Claims citing the floors | DQ-1/DQ-2 |
| OI-17 | **Gate breadth** (P1–P10 before T2) | I-15 T0 series §6; decision packet §1.2 | Governing; narrowing requested as a question only | T2 | Q-GATE |
| OI-18 | **ADR-0008 / research branch** `research/flight-software-architecture` unmerged; AT-1 … AT-7 OPEN | `docs/milestones/README.md` | Open | Flight-runtime work | None |
| OI-19 | **T1 retained limitations:** mutation survivors `canonical_one_ulp` and `narrow_band`; dt⁵ invariant drift unexplained; γ-bound operation counts by inspection | T1 dossier, "Owner acceptance (I-22)" | Accepted limitations | — | T2 does not modify T1; the T1 tests are a regression gate |
| OI-20 | **DR-0029 P5 "(continuous, GMAT-identical)"** for ≥ 1000 km. It is ambiguous: at the 1000 km base the pinned table jumps by −1.598e-5 (Review 01 F1) | DR-0029 P5; decision packet P5 item 14 | New (I-24); amendment proposed, not applied | The P5 record's wording | Strategy U-15 tests the jump |
| OI-21 | **T0 spike's km-route domain guard** accepts −2.475e-321 < h_m < 0 and returns 1.225 kg/m³ (Review 01 F4) | Decision packet P4 item 8; `docs/reviews/raw/M3-T2-readiness-I24-evidence/` | New (I-24); T0 files not edited; a VAL-0019 note is optional, for the owner | Nothing (outside every derived floor) | T2 guard in metres, before conversion (U-14; DQ-2) |
| OI-22 | **Bound derivations not yet written** (strategy §3.9 B-3 … B-8) and **unproved libm assumptions** A-FP-2, A-LM-1, A-LM-2 used by conditional rows | Validation strategy §3.9 | New (I-24); T2 deliverables | Those rows as gates | Reported until derived, or until the T2 authorization accepts the assumption |

## Status update (2026-10-25, append-only): I-26 owner decisions
Under "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25). The rows above are kept as written. Each authoritative record governs.

| # | Was | Now |
|---|---|---|
| OI-1 | DEFERRED; ESCALATED | Q-G2-1/P6 **PROVISIONALLY SELECTED (d)**, not decided. The geodetic-drag item stays **ESCALATED_FOR_INVESTIGATION**. **No longer a T2 blocker** (Q-GATE). It blocks geodetic GMAT acceptance in T5. Register: DR-0029 P6, P6-U1 … P6-U8. X-1 **NOT AUTHORIZED** |
| OI-2 | Ruling requested | **OPEN.** Not decided by I-26; ruling packet `DR-0028-P6b-owner-ruling-packet.md` prepared |
| OI-3 | PROPOSED | Unchanged (P6-U8) |
| OI-7 | PROVISIONAL | Unchanged. The P1 rule is dt-parametric, and "the final M3 timestep remains a separate decision" (P1) |
| OI-9 | Open | P7 **DECIDED**. RM-3b is a T4 candidate, not a gate; RM-6's orbit kind is T3 |
| OI-10 | Assumption | **Owner policy (DR-0025 "I-26 note"):** not accepted as universal. Dependent rows are report-only until justified for the supported environment and reviewed (packet r1 §6.2, J-FP2) |
| OI-11 | None derived | Unchanged. P2 forbids claiming a certified perturbed-motion bound |
| OI-15 | New, unreconciled | **RESOLVED** by the P4 decision: DR-0026 "I-26 note" |
| OI-16 | New | **RESOLVED for T2 design** by DQ-1 (α) and DQ-2 (km). The floors still apply only to the spike's sequence, and T2 reproduces it |
| OI-17 | Governing; narrowing a question | **RESOLVED:** Q-GATE amended (DR-0029 Resolution) |
| OI-20 | Amendment proposed | **RESOLVED:** amendment adopted with P5 (DR-0029 P5) |
| OI-21 | New; VAL-0019 note optional | Behaviour decided (P4: "do not reproduce"). **The optional VAL-0019 note was not answered and stays open** |
| OI-22 | New | **Policy decided:** A-FP-2, A-LM-1, A-LM-2 rows are report-only until promoted (packet r1 §6.2). B-3 … B-8 stay T2 deliverables |
| Others (OI-4 … OI-6, OI-8, OI-12 … OI-14, OI-18, OI-19) | — | Unchanged |

**New items found during the I-26 reconciliation (implementer's; for the owner):**

| # | Item | Authoritative record | Status | Blocks |
|---|---|---|---|---|
| OI-23 | **Outcome identifier `reentry`.** The owner's P3 precedence names it. DR-0027 A's row ("names remain proposals until the v3 schema is designed") is not explicitly superseded | DR-0029 P3; DR-0027 "I-26 note" | Open; confirmed at T3 contract design | T3 contract only |
| OI-24 | **U-23's third clause** (C_d·A ≤ 2⁻¹⁰⁷⁵ ⇒ zero drag) rests on T0 E4b, which depends on A-FP-2. It was labelled exact in strategy §3.1 and missing from the §3.9 audit | Strategy §6.3; packet r1 §6.2 | **Reclassified Conditional**; report-only | That clause as a gate |
| OI-25 | **P8 (a)'s tolerance is conditional.** Exact answers are the decided gate source, but their tolerance ε_h rests on A-FP-2. So, under the policy, no geodetic accuracy comparison gates in T2 until A-FP-2 is promoted. Domain rejection (U-20) gates unconditionally | DR-0029 P8 notes; strategy §6.2 | Consequence of two decisions; recorded | A geodetic accuracy gate in T2 |
| OI-26 | **T2 base branch.** `milestone-3-t2-decision-readiness` (`a57de3f`) and `milestone-3-t2-owner-decisions` are not merged to `main` (`fc50aed`) | Packet r1 PC-5 | Owner choice | T2 start |
| OI-27 | **DR-0026 §5.8 "the height conversion … is total"** against DR-0029 P8's requirement that the height function reject evolute-region points and the origin. It follows from P8 and is recorded as such; the owner did not word it explicitly | DR-0026 "I-26 note" | Flagged for the owner's confirmation | Nothing; T2 implements P8's domain |
| OI-28 | **DQ-6 and DR-0026 AR-7/§5.3:** the component holds C_d and A at run time; the v3 scenario remains their source (T3). This is the implementer's reading of "Scenario v3 schema and serialization remain T3 responsibilities" | DR-0026 "I-26 note" | Recorded reading; for the owner to confirm or correct | T3 design only |
