# M3 T2 — Decision-readiness report (drag force model)

**Status:** PLANNING RECORD. **T2 is NOT AUTHORIZED.** No production code, test, scenario, threshold, reference or CI file is changed by this work.  
**Prepared under:** "Authorization I-23 — M3 T2 Decision Readiness and DR-0029 P1–P9 Resolution Preparation" (Tech Lead, 2026-10-24), §9 A.  
**Companions:**
- `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md` (B; the per-decision assessments);
- `M3-T2-validation-strategy.md` (C);
- `M3-T2-authorization-packet.md` (D; DRAFT — NOT AUTHORIZED);
- `M3-open-issues-register.md` (E).

## 1. Verified repository baseline (I-23 §2)
Checked on 2026-10-24 before any file was created.

| Check | Result | How |
|---|---|---|
| `git fetch origin` | done | — |
| `origin/main` | `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`, **equal to the expected value** | `git rev-parse origin/main` |
| Checkout | clean; HEAD = `fc50aed` (fresh Superset worktree, not the T1 worktree) | `git status --porcelain` |
| T1 merge | `60648b9` is an ancestor of `fc50aed`; 24 commits; 0 merge commits (fast-forward). `origin/milestone-3-t1-j2-force-model` = `fc50aed` | `git merge-base --is-ancestor`, `git rev-list` |
| CI on `main` at `fc50aed` | run 40053187537 (push, `main`): `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`, all success. Run 40049043191 (branch) success | `gh run list`, `gh run view` |
| Branch protection on `main` | none ("Branch not protected"); unchanged | `gh api …/branches/main/protection` |
| T1 acceptance records | present: `docs/reviews/M3-T1-acceptance-dossier.md` ("Owner acceptance (I-22)"), `M3-T1-closure-verification.md`, `M3-T1-review-0{1,2,3}.md`, VAL-0020 and corrections 1–3 | read |
| M3 decision records | present: DR-0024 … DR-0029, DR-0029 P10 packet, ADR-0009, `M3-decision-matrix.md`, `M3-T0-decision-matrix.md`, T0 report and dossier | read |
| Repository conventions | `CLAUDE.md`; `playbook/` (PLAYBOOK, delegation, git, science, testing); `proof/` (PROOF, review, definition-of-done); templates in `toolbox/templates/` | read |
| Dependency graph | T2 depends on G1 (DR-0024) and G3 (DR-0026), and under the Tech Lead's gate on DR-0029 P1–P10 (§3). **Consistent with the historical report**; no conflict found | `M3-proposal.md` §4; `M3-T0-decision-matrix.md`; §3 below |

**Result: every precondition passed.** No stop condition applied.

- **Work location.** This work uses the fresh Superset worktree created at `fc50aed`, local branch `tars-m3-t2-readiness-853e0447`. It is pushed to the remote branch **`milestone-3-t2-decision-readiness`**, the name I-23 §3 suggests. Earlier decision branches followed the same pattern (worktree-local name, named remote branch).
- **Merge record.** Repository convention records a merge in the next branch. The I-22 merge facts are appended to the T1 dossier, the T1 report and the planning decision matrix, as T0's merge was under I-15.

## 2. T2 scope and intended outcome
**Authoritative scope** (`M3-proposal.md` §4, T2 row):
> Drag force model and spacecraft Cd/A; force-context extension (mass); analytic tests (decay rate vs an approximate semi-analytic estimate; behaviour outside the table per the G1 domain policy; energy monotonicity) | Depends on: G1, G3 | Gate / output: Unit-level VAL record; architecture scan; M1/M2 byte-identity | Review: Codex

**What the approved decisions require T2's components to be:**
- **Force context** (DR-0026 Q-G3-1; ADR-0009 items 1–2). An immutable context carries the current total mass, built by the simulator from the stage state (mass = dry + max(prop, 0), the existing M2 rule, DR-0026 §5.2). The old `acceleration(t, r, v)` signature is preserved through an adapter. Mutable mass is never injected (D1 rejected).
- **Drag** (DR-0024 Q7, SCI-0016):
  - a = −½ ρ(h) (C_d A / m) \|v_rel\| v_rel, with v_rel = v − ω × r and ω = ω_E Ẑ;
  - ω_E = 7.292115e-5 rad/s;
  - cannonball model with constant C_d and A;
  - current total mass at every derivative evaluation.
- **Density component** (DR-0026 Q-G3-2; DR-0024 Q5, Q5a; DR-0027 B-1):
  - the pinned GMAT R2026a table (sha256 `75762f67…`), preserved exactly as published, plus the one-band 250 km subset;
  - GMAT's band rule;
  - domain behaviour per DR-0029 P4/P5 once decided.
- **Geodetic height** (DR-0024 Q6, SCI-0017): WGS 84 a and 1/f about frame +Z (J-ax-1); the algorithm validated per P8.
- **Composition order** (ADR-0009 item 9): point mass, J2, drag, then thrust.
- **Versioned model identifiers** (ADR-0009 item 5), for example `drag_cannonball@1`, `exp_table_density@1`, `height_geodetic_wgs84@1`. The final names are a T2/T3 detail.
- **M1/M2 byte identity** (DR-0025 principle 8; VO-5), and T1's accepted contract unchanged.

**Not T2 (by the approved plan):**
- scenario v3, `PhysicsConfiguration`/`physics_id`, the `PhysicsConfigured` event, runner integration, `reentry` termination and the contract amendment (T3);
- validators, the M3 Proof, `m3.json` and DOP853 references (T4);
- GMAT M3 references (T5);
- thresholds (T6/G4).

**Intended outcome:** pure, unit-validated drag, density and geodetic-height components; a force-context path that leaves M1/M2 byte-identical; a unit-level VAL record. **Not wired into scenarios or missions**, as T1 was not.

## 3. Dependencies and blockers
### 3.1 Governing gate
- The Tech Lead's statement in I-15 (T0 series) §6, verbatim: "**Explicitly identify P10 as a prerequisite for T1 and P1–P10 as prerequisites for T2**".
- P10 is DECIDED (I-16). **P1–P9 are OPEN.**
- **T2 is therefore BLOCKED by decisions.** It also needs its own authorization (every task has needed one).

### 3.2 Technical dependency map (implementer's analysis; not governing)
| Decision | What T2 builds from it | Needed for T2 code? |
|---|---|---|
| P4 | Density below 0 m: typed domain error | Yes |
| P5 | Density in every region; top-band extrapolation | Yes |
| P8 | Geodetic test oracle; domain contract | Yes |
| P9 | Test vehicle values (alignment only) | Values only |
| P1 | Seam: ρ(h) evaluable for scenario validation (T3) | Interface only |
| P2 | Geodetic component exposes n̂ or φ (N-3) | Interface only |
| P3 | Height never depends on band selection | Interface only |
| P6 | — (T5) | No |
| P7 | — (T3–T5) | No |

**Coupled decisions:** P3 depends on P1; P5 on P4 and P1; P7 on P1 and P9 (packet §1.1).

**Independent decisions:** P2, P4, P8, P9; and P6, apart from its evidence gap and the DR-0028 scope ruling.

### 3.3 Other open items that touch T2
| Item | Status | T2 effect |
|---|---|---|
| Q-G2-4 final dt | PROVISIONAL | T2 unit tests use explicit dt; no T2 claim depends on the final dt |
| Q-G2-2 identity-check rule | PROPOSED | T2 constant identity tests are C class and do not adopt it (as in T1) |
| DR-0026 AR-8 / §5.8 "density is total" | Body text | Conflicts with P4 (ii); needs supersession in the P4 decision (packet N-2) |
| T3 axis representation | Open | T2 adds no axis parameter (I-17 precedent; J-ax-1) |
| A-FP-1 … A-FP-3 | Assumptions | Condition every derived T0 floor (packet N-1) |
| T2 design questions DQ-1 … DQ-6 | New | Draft T2 packet §5 |

## 4. T0/T1 contracts T2 must preserve
| Contract | Source | How T2 preserves it |
|---|---|---|
| M1 golden `events_sha256` `7a4e1877…20a4`; M1 Proof 9/9 | DR-0006/0008; `proof/references/m1_final_state.json` | Gate: unchanged bytes |
| M2 Proof 20/20, `m2_proof` 228/228; M2 golden, snapshot, GMAT M2 manifest digests | DR-0023, DR-0021; `approved_digests.py` | Gate: unchanged |
| Frozen M2 validator `FreeSpace` implementing `acceleration(t, r, v)` | DR-0026 §1 | Adapter keeps the old protocol working |
| v1/v2 schemas and code paths | DR-0026 AR-6 | Not touched in T2 |
| T1 `ZonalJ2Gravity` numerical contract (domain errors, owned binary64 parameters, immutability), `EarthJ2Constants`, `WGS84_EGM2008_TIDE_FREE`, J2 = `0x1.1bcdd00abd9aap-10` | T1 dossier, VAL-0020 + corrections 1–3 (I-22) | No edit to T1 classes or constants. If J2 is composed under the context protocol, it goes through the adapter, unchanged |
| T0 checks (314) and the 27 T0 digests (22 spike, 5 pinned) | T0 dossier; T0 merge record | Gate: the 314 checks still pass |
| P10: one canonical C̄20 | DR-0029 P10 | No new J2 literal |
| DR-0027 B-1/B-3: table pinned verbatim, no silent repair | DR-0027 | Digest-checked load; the disputed cells evaluated as published |

## 5. Existing evidence
- **Physics and numerics (T0, accepted):** VAL-0019 and `docs/science/experiments/m3-t0/`. Contents:
  - band boundaries, both evaluation routes;
  - drag decay;
  - geodetic algorithms (two);
  - frames;
  - GMAT exact configurations;
  - stiffness thresholds;
  - stage-domain condition;
  - missed-crossing bounds.
  It was reviewed over 10 Codex rounds, with Review 10 an unconditional PASS.
- **Planning (accepted):** VAL-0018; DR-0024 … DR-0028 with their evidence scripts.
- **T1 (accepted):** a pattern for pure components with owned parameters, numerical-domain errors, red-first tests and mutation campaigns; CI bit identity on three platforms.
- **I-23 corroboration:** packet §2, C-1 … C-7.

## 6. Evidence gaps
| Gap | Blocks | Smallest remedy |
|---|---|---|
| P6 geodetic-drag attribution (escalated) | P6 full resolution; under the governing gate, T2 | Packet X-1 (GMAT source read plus interval sweep plus single-step isolation) |
| RM-3b not run | P7 completeness (not T2) | X-2, or defer to T4 as DR-0029 recommends |
| Derived floors specific to the spike's arithmetic (N-1) | Nothing in P1–P9. A T2 claim that cites the floors needs path (α) or a re-derivation | Owner chooses DQ-1 path (α) or (β) |
| No primary source for C_d 2.2 (C-6) | Nothing (illustrative values) | Optional: read Vallado & Finkleman (2014) |
| Printed Vallado table not read (DR-0027 B-5) | Nothing (B-1 pinned with conditions) | Unchanged |
| No independent atmosphere-realism validation | Nothing (DR-0025 §12.1, a stated gap) | Unchanged |
| A-FP-2 (libm accuracy) measured on one host | Any T2 statement that relies on the T0 derived floors | Cross-platform measurement (T2 validation strategy X-P) |
| ∂a/∂r stiffness contribution (N-7) | Nothing (P1 is a necessary screen) | Packet X-4 |

## 7. Scientific and architectural risks
| Risk | Likelihood | Impact | Mitigation in the draft packet |
|---|---|---|---|
| The force-context change alters M1/M2 bits (summation order, an extra array operation in the derivative) | Medium | Regression; contract break | Adapter that calls old-protocol models unchanged; the point-mass-only path keeps `np.zeros(3)` plus a left fold; M1 golden and M2 Proof in the same change; a stop condition |
| `exp` differs across platform libms; drag amplifies differences (B + 1 % → 4.8 km) | Medium | Cross-platform spread | T2 measures the unit-level spread on the three CI platforms; no bound is borrowed from M1/M2 (DR-0025 §7) |
| Geodetic algorithm or density route differs from the spike, so cited floors do not apply | Medium | Overstated claims | DQ-1/DQ-2 decided before implementation; records cite the floors only under path (α) |
| Underflow and subnormal density far above the table (≈ 181 890 km and up) | Low (unphysical heights) | Silent loss or raising inconsistency | Tests at T0's transition points; returned exactly as computed, never raised |
| Scope creep into T3 (scenario v3, `reentry`, events) | Medium | Violates the plan | Explicit exclusions; stop condition |
| The pinned data file needs a packaging change (`pyproject.toml` is protected) | Low–Medium | Stop | Verify that `uv_build` includes the data file without configuration; else stop and raise a DR |
| Physics core importing `tars.validation` for the digest | Low | Static-guard failure | Pin the digest in `tars.sim` (N-5) |
| Treating spike-vs-T2 agreement as validation | Medium | Overclaiming | Classified P (same team, same equations) per DR-0025 principle 3 |

## 8. Readiness assessment
| Area | State |
|---|---|
| Decisions (governing gate P1–P10) | **NOT READY.** P10 decided; P1, P2, P4, P8 and P9 ready for decision; P3, P5 and P7 coupled (decidable together); P6 needs evidence |
| Decisions (technical map: P4, P5, P8; P1–P3 interfaces; P9 values) | Ready for decision in one owner response |
| Design questions (draft packet §5, DQ-1 … DQ-6) | Owner answers needed before T2 branches |
| Evidence for T2 code | Sufficient for the decision-dependent components, once decided |
| Authorization | None |

**Overall: T2 is BLOCKED BY DECISIONS.**
- Under the governing gate it stays blocked until P6's evidence exists (X-1) or the owner narrows the gate.
- Under the technical map it could be authorized once P1–P5, P8 and P9 are decided and DQ-1 … DQ-6 are answered.

## 9. Recommended next authorization
**Recommended (implementer's view; for the owner):**
1. **Decision authorization:** decide P1–P5, P8 and P9 in one response, in the packet's order, with κ and v̂ for P1 and the N-2 supersession for P4. Record the decisions append-only in DR-0029, DR-0027, DR-0024 and DR-0025, and update the matrices.
2. **Gate ruling (Q-GATE):** either
   - (a) keep the governing gate and authorize X-1 so that P6 can close; or
   - (b) narrow the T2 gate to P1–P5, P8 and P9, with P6/P7 to be decided before T3/T4. **Implementer's suggestion: (b)** [judgment]. P6 and P7 have no T2 code consequence, and X-1 needs GMAT runs unrelated to T2. P7 depends on P1 and P9, so it can also be decided with them at no cost.
3. **Answers to DQ-1 … DQ-6** (draft T2 packet §5).
4. Then, separately: **T2 implementation authorization**, based on the draft packet once revised with those answers.

## 10. Actions not performed
- No production code, test, proof harness, scenario, golden, constant, threshold or CI change.
- No experiment that writes a tracked file.
- No DR decision, and no change to any Resolution.
- No T2 or T3 work.
- No merge, and no PR.

## Status update (2026-10-24, append-only): independent Review 01
- Codex Review 01 (at `5ee6a6a`): **REQUEST_CHANGES**, with 2 MAJOR (M3T2R-R1-F1: 1000 km continuity; F2: E1 reused beyond h ≥ 0), 3 MINOR (F3 strict monotonicity; F4 lower-edge typo and the −5e-324 guard; F5 C² across band edges) and 1 NOTE (F6). All are reproduced and ACCEPTED, **not applied** (I-23 §10).
- No P1–P9 classification changes. The text above is as reviewed.
- Record: `docs/reviews/M3-T2-readiness-review-01.md`.

## Status update (2026-10-24, append-only): I-24 corrections of Review 01
- Under Authorization I-24, M3T2R-R1-F1 … F6 are corrected in the decision packet, the validation strategy and the draft T2 packet. The matrix is in `docs/reviews/M3-T2-readiness-review-01-corrections.md`; the reviewed wording is preserved at `5ee6a6a`.
- **Unchanged:**
  - §1 … §10 of this report;
  - the P1–P9 classification;
  - the governing gate (P1–P10; Q-GATE open);
  - DQ-1 … DQ-6 (open);
  - the P6 investigation (open, X-1 not authorized).
- **Additions to §6 (evidence gaps), from the F6 audit:**
  - Derivations B-3 … B-8 (strategy §3.9) do not exist. They are T2 deliverables; until they are reviewed, their checks are reported, not gated.
  - Rows resting on A-FP-2, A-LM-1 or A-LM-2 gate only if the T2 authorization accepts those assumptions.
  - Neither gap blocks a P1–P9 decision.
- **Additions to §6, from F1 and F4:**
  - DR-0029 P5's "(continuous, GMAT-identical)" wording is ambiguous; an amendment is proposed for the owner (packet P5 item 14; DR-0029 append-only note).
  - The T0 spike's km-route guard accepts −2.475e-321 < h_m < 0 (packet P4 item 8). It affects no T0 result.
- Owner briefing: `docs/decisions/requests/DR-0029-P1-P9-owner-briefing.md`.
