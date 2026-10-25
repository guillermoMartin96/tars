# M3 T2 — Authorization packet (drag force model)

**Status: DRAFT — NOT AUTHORIZED.** No T2 branch exists. No production code, test, scenario, threshold, reference or CI file has changed.  
**Prepared under:** I-23 §9 D.  
**Preconditions not yet met:** §1. The owner's answers to §5 change this draft. After they are given, the packet is revised and resubmitted; it is not executed as written.

## 1. Preconditions (all required before T2 branches)
| # | Precondition | State at `fc50aed` |
|---|---|---|
| PC-1 | DR-0029 P1–P9 decided, per the governing gate (I-15 T0 series §6: "P1–P10 as prerequisites for T2"), **or** the owner states a narrower T2 gate (Q-GATE, decision packet §1.2) and the decisions it names are made | P10 DECIDED; P1–P9 OPEN |
| PC-2 | The decisions recorded append-only in their home DRs: DR-0027 (A-4, A-5, A-6, A-s, B-4), DR-0024 Q9, DR-0025 (Q-G2-1, Q-G2-5, Q-G2-7); matrices updated | Not done |
| PC-3 | If P4 (ii) is chosen: the owner's statement that DR-0026 AR-8/§5.8 "total density" does not apply below the table's lower edge (packet N-2) | Not done |
| PC-4 | Answers to DQ-1 … DQ-6 (§5) | Not given |
| PC-5 | This planning branch merged to `main`, or the owner directs T2 to branch from it (the I-16/I-17 §1.3 precedent) | Not merged |
| PC-6 | `origin/main` verified, clean checkout, CI green on `main` | Verified at `fc50aed` (run 40053187537) |
| PC-7 | An explicit T2 implementation authorization from the Tech Lead | None |

## 2. Approved scope required before implementation
From `M3-proposal.md` §4 (T2 row) and the approved decisions (readiness report §2):
1. **Force context and adapter** (DR-0026 Q-G3-1; ADR-0009 items 1–2):
   - an immutable `ForceContext` (current total mass) and a context-aware protocol;
   - a legacy adapter for `acceleration(t, r, v)` models;
   - the simulator builds the context from the stage state, if DQ-3 includes the simulator.
2. **Constants** (additive, in `tars.sim.constants`):
   - pinned 1/f = 298.257223563 and ω_E = 7.292115e-5 rad/s, in a new named structure;
   - no edit to `WGS84`, `EarthJ2Constants` or `WGS84_EGM2008_TIDE_FREE`;
   - μ and a reused from `WGS84`.
3. **Atmosphere dataset:**
   - the GMAT R2026a file pinned verbatim (sha256 `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`);
   - its digest checked before parsing;
   - the one-band 250 km subset derived from it (DQ-4).
4. **Density component:** GMAT band rule; P4/P5 domain behaviour as decided; route per DQ-2.
5. **Geodetic-height component:** WGS 84 about +Z; algorithm per DQ-1; domain stated; returns h and n̂ (or φ) (packet N-3).
6. **Drag force:** cannonball; v_rel = v − ω_E Ẑ × r; C_d and A owned binary64 parameters (DQ-6); mass from the context; numerical domain explicit (the T1 R1-F2/R2-F1 pattern).
7. **Composition:** canonical order point mass → J2 → drag (thrust is added by the propulsion path, unchanged).
8. **Model identifiers and versions** (ADR-0009 item 5).
9. **Tests and records** per `M3-T2-validation-strategy.md`: a new VAL record and SCI-0014 … SCI-0017 status updates.

## 3. Permitted files and components (subject to DQ answers)
| Path | Permission |
|---|---|
| `src/tars/sim/forces.py` | Additive: context protocol, adapter, drag class. Existing classes (`PointMassGravity`, `CompositeForceModel`, `ZonalJ2Gravity`) unchanged (AST-identical) |
| `src/tars/sim/constants.py` | Additive only |
| `src/tars/sim/atmosphere.py`, `src/tars/sim/geodesy.py` (names indicative) | New |
| Data file location (DQ-4), for example `src/tars/sim/data/EarthExponentialAtmosphereData.txt` | New, verbatim copy |
| `src/tars/sim/simulator.py` | **Only if DQ-3 includes it:** the derivative functions build the context. No change to tick, step-splitting, engine-schedule or atomicity logic |
| `tests/test_force_context.py`, `tests/test_drag.py`, `tests/test_atmosphere.py`, `tests/test_geodesy.py` (indicative); the existing literal-location test extended | New or additive |
| `docs/science/validation.md` (new VAL record), `docs/science/assumptions.md` (SCI status updates), `docs/science/experiments/m3-t2/` | Append-only, or new |
| `docs/milestones/M3-T2-report.md`; append-only status notes in matrices and packets | New, or append-only |

## 4. Protected paths (must be unchanged; any need to change one is a stop condition)
- `proof/` (thresholds, references, records, evidence);
- `toolbox/` (validators, scripts, references, templates);
- `scenarios/`;
- `.github/workflows/`;
- `uv.lock`, `pyproject.toml`;
- `src/tars/validation/` (including `approved_digests.py` and `architecture.py`; the guard's `rglob` already covers new `tars.sim` modules);
- `src/tars/events/`, `src/tars/sim/scenario.py`, `src/tars/sim/runner.py`, `src/tars/sim/propulsion.py`, `src/tars/sim/integrators.py`;
- `docs/contracts/`;
- T0 experiment files and results;
- T1 tests and evidence (`tests/test_zonal_j2.py` and `docs/science/experiments/m3-t1/` unchanged; `tests/test_constants.py` additive only);
- every M1/M2 entry of the science registers (append-only).

## 5. Design questions for the owner (answer before T2 branches)
| ID | Question | Options | Implementer's recommendation and reason |
|---|---|---|---|
| **DQ-1** | Geodetic algorithm | **(α)** reproduce `t0_model.geodetic_iterative` operation for operation (start latitude, stopping rule \|Δφ\| ≤ 1e-15 or 60 iterations, pole-safe height). **(β)** another algorithm: Vermeille closed form, or a fixed iteration count as DR-0026 §5.8's body text suggests | **(α)** [judgment]. It is the only algorithm with a derived height-error bound ε_h (E1), on which the P1/P4 sufficient-floor statements rest (packet N-1). It is deterministic and total on its domain (the early exit is a data-dependent branch, not non-determinism). The owner should state that this satisfies DR-0026 §5.8's intent. **Qualified under I-24 (M3T2R-R1-F2, F4):** E1 covers exterior points (true height ≥ 0) and the inverse's own evaluation error only, under A-FP-2; negative heights are outside it. "Operation for operation" excludes the spike's domain guard (see DQ-2). |
| **DQ-2** | Density evaluation route | **(km)** convert h to km and apply the table formula, as GMAT and the T0 envelope (E2) do. **(m)** convert the table to SI once at load, as DR-0024 §9's body text says | **(km)** [judgment]. GMAT-identical arithmetic (T5 exact configuration) and coverage by the T0 derivation. T0 shows identical band selection on both routes at, and one ulp either side of, all 27 bases [measured]; the density bits can differ. (km) departs from DR-0024 §9's "converted once, at dataset load". §9 is request-body text, not a Resolution item, but the owner should accept the departure explicitly. **Domain guard (I-24, M3T2R-R1-F4):** on either route, the lower-edge guard compares the height **in metres** with 0, **before** the km conversion; −0.0 is in the domain. The spike converts first, so it accepts −2.475e-321 < h_m < 0 and returns 1.225 kg/m³ for −5e-324; T2 must not copy that. The corrected guard changes only which inputs raise, all of them below the edge. Every input with h_m ≥ 0 reaches the same arithmetic, so no T0 floor or E1–E6 term changes |
| **DQ-3** | Does T2 wire the context into `Simulator`? | **(a)** yes: derivatives build `ForceContext` from the stage state; M1/M2 byte identity gated. **(b)** no: protocol and adapter only; the simulator change moves to T3 | **(a)**. The M3 proposal's T2 gate lists "M1/M2 byte-identity", and VO-4's mass coupling needs the stage mass. The change is confined to the three derivative closures |
| **DQ-4** | Where the dataset and its digest live | Data file under `src/tars/sim/data/`, read with `Path(__file__)`. `importlib.resources` is forbidden by the static guard. The digest pinned in `tars.sim` (packet N-5). Alternative: the file's bytes embedded as a Python literal plus its digest | Data file plus a `tars.sim` digest. **Stop condition** if the wheel build needs a `pyproject.toml` change (protected) to include it. The embedded-bytes form is the fallback, with the owner's approval |
| **DQ-5** | J2 under the context protocol | **(a)** wrapped by the legacy adapter, with T1's class untouched. **(b)** a new context-aware J2 version | **(a)**. It preserves T1's accepted contract and its evidence; a new version would need a new identity and re-validation |
| **DQ-6** | Drag parameter ownership in T2 | C_d and A as immutable constructor parameters of the drag component (scenario v3 is T3); test vehicles per P9 | As stated. The spacecraft schema stays T3 (DR-0026 Q-G3-10) |

## 6. Validation requirements
- `M3-T2-validation-strategy.md` gates G-T2-1 … G-T2-9.
- Red-first tests, committed before the code (T1 precedent).
- Every tolerance is exact, derived with its operation count, or measured and reported. **No invented tolerance; no M3 threshold** (DR-0025 principle 7).
- *(Added under I-24, M3T2R-R1-F6.)* The strategy's §3.9 bound audit governs which rows gate:
  - **Gate** rows gate.
  - **Conditional** rows gate only if this authorization, once issued, explicitly accepts the named assumption (A-FP-2, A-LM-1, A-LM-2). This draft does not assume that it will.
  - **Deliverable** rows are reported until their derivation has been reviewed (G-T2-3a).
- The M1 Proof and the M2 Proof run in separate fresh clones, with `uv` on PATH; the T0 314 checks; the T1 109 tests; CI green on three platforms plus `m2-cross-platform` for every pushed commit.
- Determinism: same-platform byte identity; cross-platform differences measured and recorded, not bounded.

## 7. Independent review requirements
- After implementation, validation and green CI: **stop** for authorization of an independent **Codex T2 review**.
- The prompt pins the full SHA. It quotes the T2 authorization and every relevant owner text verbatim, and states which preconditions the implementer has already performed (T1 Review 01 lesson).
- Reviewer scope:
  - physics correctness against the cited equations;
  - M1/M2 and T1 preservation;
  - numerical domains, including underflow and subnormals;
  - test strength (mutation);
  - scope compliance;
  - the decision conformance of P4, P5 and P8.
- Stop rules, as T0/T1:
  - REQUEST_CHANGES → record, reproduce and disposition each finding (ACCEPTED / REJECTED_WITH_REASONING / ESCALATED_FOR_INVESTIGATION). No fix without authorization; no further review round without authorization.
  - PASS → acceptance dossier. No acceptance, no merge.
- Unresolved Critical or High findings block T2.

## 8. Stop conditions
Stop and report, without working around the problem, if:
- any M1/M2 gate, golden, digest, T0 check or T1 test result changes;
- a protected path would need to change (§4), including `pyproject.toml` for packaging;
- T2 appears to need scenario v3, `PhysicsConfiguration`, events, runner or `reentry` work (T3), or GMAT (T5);
- an oracle disagrees beyond a justified bound, or a bound cannot be justified without inventing one;
- the pinned table's digest does not match the GMAT R2026a file recorded in DR-0027 B-1;
- a derived constant is not bit-identical across the three CI platforms;
- a decided behaviour (P4/P5/P8) proves not implementable as decided;
- a dependency or lock-file change appears necessary;
- the implementation is complete and validated: stop for the review authorization.

## 9. Acceptance and merge gates
1. Codex review PASS (unconditional, or conditional with every condition closed).
2. Acceptance dossier, then the owner's **explicit** acceptance.
3. A **separate** merge authorization. Fast-forward only, by ordinary push; pre-merge ancestry check; post-merge fresh-clone validation; CI on `main` green.
4. The merge is recorded in the next authorized branch.

## 10. Explicit exclusions
- Scenario v3, `PhysicsConfiguration`/`physics_id`, `PhysicsConfigured`, runner integration, the `reentry` end condition, P1 admissibility validation, the P2 crossing event and P3 precedence (T3).
- Validators, the M3 Proof, `m3.json`, DOP853 references, snapshot decisions (Q-G2-6) (T4).
- GMAT M3 references, `.cof` generation, P6 and the DR-0028 P6(b) ruling (T5).
- Thresholds; the final M3 time step (Q-G2-4 stays PROVISIONAL).
- Any Earth-orientation model or configurable axis; higher harmonics; winds; lift; MSIS-class atmospheres.
- Changes to T1's accepted classes or constants.
- Deciding any open DR item; branch-protection changes.

## Status update (2026-10-24, append-only): independent Review 01
- Codex Review 01 (at `5ee6a6a`): **REQUEST_CHANGES**, with 2 MAJOR (M3T2R-R1-F1: 1000 km continuity; F2: E1 reused beyond h ≥ 0), 3 MINOR (F3 strict monotonicity; F4 lower-edge typo and the −5e-324 guard; F5 C² across band edges) and 1 NOTE (F6). All are reproduced and ACCEPTED, **not applied** (I-23 §10).
- No P1–P9 classification changes. The text above is as reviewed.
- Record: `docs/reviews/M3-T2-readiness-review-01.md`.

## Correction log (I-24, 2026-10-24): Review 01 findings
Made under Authorization I-24; documentation only. The reviewed wording is preserved at `5ee6a6a`. **Still DRAFT — NOT AUTHORIZED.**
- DQ-1 is qualified with E1's domain (F2).
- DQ-2 now specifies the metres-first guard and records the spike's trap interval (F4).
- §6 refers to the strategy's bound audit (F6).
- DQ-1 … DQ-6 are **unanswered and unchanged in substance**.
- Preconditions PC-1 … PC-7 are unchanged, and none is met.


## Status update (2026-10-24, append-only): independent Review 02
- Codex Review 02 (at `f44a94f`): **REQUEST_CHANGES**, with 2 MAJOR and 1 MINOR. All three are reproduced and ACCEPTED, **not applied** (I-24 §6 stop rule):
  - M3T2R-R2-F1: z-reflection exactness also needs cos to be even, which A-LM-1 omits (U-19, B-11).
  - R2-F2: PM-4 (b) cites a two-sided E3 allowance, but E3 is one-sided (PM-4 (b), B-9).
  - R2-F3: extremum wording in packet P4 item 8.
- Review 01: F1, F2, F4 and F5 are RESOLVED; F3 and F6 are PARTIALLY RESOLVED (through R2-F1 and R2-F2).
- No P1–P9 classification changes. The text above is as reviewed at `f44a94f`.
- Record: `docs/reviews/M3-T2-readiness-review-02.md`.
- *(I-25, append-only)* After the R2-F1/R2-F2 corrections, §6's list of conditional assumptions (A-FP-2, A-LM-1, A-LM-2) is still accurate. A-LM-1 is now narrower (hypot only), and exact z-reflection and strict density decrease are reported only. No change is needed in this draft. **Still DRAFT — NOT AUTHORIZED.**

- *(2026-10-24, append-only)* **Independent Review 03 (at `628623b`): PASS, no findings.** R2-F1 … R2-F3 resolved; Review 01 findings remain closed. Record: `docs/reviews/M3-T2-readiness-review-03.md`. Nothing is approved by the PASS.

- *(2026-10-25, append-only)* **Superseded for decision content by `M3-T2-authorization-packet-r1.md` (I-26), which is also DRAFT — NOT AUTHORIZED.** The owner decided P1–P5 and P7–P9, provisionally selected P6 (d), amended the T2 gate (Q-GATE) and decided DQ-1 … DQ-6 under I-26. This draft is kept as reviewed in readiness Reviews 01–03.
