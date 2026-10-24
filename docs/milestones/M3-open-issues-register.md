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
