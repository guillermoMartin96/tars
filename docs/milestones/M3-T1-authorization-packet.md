# M3 T1 — Authorization Packet (J2 force model)

**Status:** PREPARED FOR OWNER REVIEW. **T1 is NOT AUTHORIZED.** No T1 branch exists, and no production code has changed.  
**Prepared under:** "I-16 — Decide DR-0029 P10 and Prepare T1 Authorization" (Tech Lead, 2026-10-22), §6–§7.  
**Classification: T1 is UNBLOCKED by decisions.** Its only open decision prerequisite, DR-0029 P10, is DECIDED (option (a)). One process question (§1.3) needs an owner answer before T1 can branch.

## 1. Repository and branch state
### 1.1 State
| Item | State |
|---|---|
| `main` | `5fded7c6df50d60564f2bd025aeaf9dab4f541cd` (T0 ACCEPTED and MERGED); CI run 39827298093 green |
| Decision branch | `m3-p10-decision-packet`, from `5fded7c`, docs only: `ecdd1f7` (I-14 merge records, P10 packet; CI run 39837840124 success), `f8c284e` (P10 decision), plus this packet's commit. Not merged; no PR |
| Branch protection | none on `main` (unchanged) |

### 1.2 P10 recorded
DR-0029 P10 reads **DECIDED — Option (a)**: the decision text is in the P10 section and the Resolution. Append-only notes are in DR-0024, SCI-0013 (status update 3), the T0 decision matrix, the planning decision matrix and the P10 packet. P1–P9, Q-G2-1/P6, Q-G2-2 and DR-0028 P6(b) are unchanged.

### 1.3 Process question: does the P10 record need to reach `main` before T1 branches?
- **No written rule requires it.** Precedent: the planning records reached `main` (PR #4) before T0 branched from `86df2c3`. Later status records (the T0 merge) were written in the next branch.
- **T1 cites the P10 decision** in its constants, tests and VAL record. If T1 branches from `main` as it stands, the decision it implements exists only on an unmerged branch.
- **Options, for the owner:**
  - **(A)** Authorize a fast-forward merge of `m3-p10-decision-packet` into `main` (docs only; `main` is its base), then branch T1 from the new `main`. *Recommended:* the decision is on `main` before the code that implements it, and T1's diff stays code-only.
  - **(B)** Branch T1 from the head of `m3-p10-decision-packet`. The decision records then reach `main` with T1.
- I have not merged anything. I-16 does not authorize a merge.

## 2. T1 objective
Implement the approved J2 zonal-gravity force as a **pure, unit-validated force component**, with the P10 constant identity, and record its unit-level validation. It is not wired into scenarios or missions.

## 3. Exact proposed scope (from the approved M3 plan)
**M3 proposal §4, T1:** "J2 force model, pure; analytic unit tests (secular Ω̇, ω̇ rates, energy and polar angular-momentum conservation)". Depends on G1 (DR-0024, resolved; realization DR-0028 J-ax-1, approved). Output: a unit-level VAL record. Review: Codex.

In scope:
1. **Constants** (`src/tars/sim/constants.py`, additive): a named M3 Earth constant set beside the unchanged `WGS84` (baseline-and-impact §3). It holds the canonical C̄20 = −0.484165143790815e-3 (EGM2008 tide-free, NGA.STND.0036 Table 5.1), with J2 derived as `-math.sqrt(5.0) * C20`, and the existing WGS 84 μ and a. It holds no independent J2 literal (I-16 §3).
2. **J2 component** (`src/tars/sim/forces.py`, additive): a pure class implementing the existing `ForceModel` protocol `acceleration(t, r, v)`.
   - Acceleration of U = (μ/r)[1 − J2 (a/r)² P₂(z/r)] about the frame z axis (SCI-0013; DR-0028 J-ax-1: the axis is the frame z axis, with the identity transformation).
   - Constructor parameters μ, a and J2 are immutable and validated. It has no axis or orientation parameter (§12.1).
   - Model name `zonal_j2`, version 1 (ADR-0009 item 5).
   - The existing `PointMassGravity` and `CompositeForceModel` are unchanged.
3. **Tests** (new test files; the existing constants test is extended): see §7.
4. **Records:** a new VAL-0020 (unit-level J2 validation) appended to `docs/science/validation.md`; a SCI-0013 status update ("implemented as a component; not integrated"); a T1 Proof/evidence note.

## 4. Proposed branch name
`milestone-3-t1-j2-force-model`. It follows `milestone-3-planning` and `milestone-3-t0-reference-spike`, and is created from `main` under option (A) or from the decision branch under option (B). It is not created yet.

## 5. Implementation approach
- **TDD:** each oracle is written as a failing test first.
- **Separation:**
  - the acceleration is the production code;
  - the potential used by the Q2 invariant and Q3 gradient oracles is coded **separately, in the tests**, so those oracles do not reuse the formula under test (DR-0025 Q2 "independent only if the potential is coded separately").
- **Constant derivation:**
  - J2 is computed once at import from C̄20, using IEEE 754 correctly rounded `sqrt` and one multiplication; no libm transcendental is involved.
  - A test asserts its binary64 value, `float.hex`, equals that of 1.0826261738522227e-3. This is an expected-value check, not a second authoritative literal.
- **Propagation in tests:** the secular-rate and conservation oracles propagate point mass + J2 through the existing RK4 integrator and `CompositeForceModel` directly in the tests. They do not use the runner, scenarios or events.
- **Commits:** small, pushed frequently; CI checked after each push (playbook `git.md`).

## 6. Dependencies on P10
- Constant structure (canonical C̄20 → derived J2): P10 (a).
- The derivation test and the display check of the decimal (|J2 − 1.0826261739e-3| / J2 < 5e-11, with the 4.41e-11 gap recorded): P10 (a).
- A future generated GMAT `.cof` must derive from the same constant. That is T5 scope, not T1. T1 must not hand-maintain a second value anywhere.

## 7. Required tests and validation
| Oracle (DR-0025) | Test | Evidence class |
|---|---|---|
| Constants | C̄20 literal equals the NGA string; J2 bit-for-bit = −√5·C̄20; decimal display check; `WGS84` unchanged; literals only in `constants.py` (existing pattern extended to C̄20) | C (identity). Not presented as satisfying the Q-G2-2 rule, which is still PROPOSED |
| Q3 gradient | acceleration = −∇U of the separately coded potential, by complex step, at sampled points including high latitude and near the equatorial plane | P (unit) |
| FC-6 / Q11 signs | inward extra pull at the equator; outward along +Z at the pole; node regression < 0 for i < 90°, > 0 for i > 90°, ≈ 0 at 90°; apsidal sign change across 63.4° | I (theory) for signs |
| Q11 limit | J2 = 0 gives a zero acceleration; point mass + J2(0) equals point mass bitwise for the tested states | R |
| Q2 invariants | energy E = v²/2 − μ/r + (μ J2 a²/2r³)(3z²/r² − 1) and h_z conserved along RK4 propagation; drift measured against dt (dt, dt/2) to show the drift is integrator truncation | P |
| Q1 secular rates | fitted Ω̇, ω̇ against first-order (3/2)/(3/4) n J2 (a/p)² theory | I (theory, approximate) |
| Q10 order | RK4 at dt, dt/2, dt/4 on J2 (a smooth RHS): order ≈ 4 measured and reported | C. Reported, not gated by the M2 rule (DR-0025 principle 4) |
| VO-5 regression | full M1 Proof (9/9), M2 Proof (20/20, 228 PASS), M1 golden `7a4e1877…`, the pinned digests, pytest, ruff; T0 checks 314/314 still pass | R |

**Tolerances:**
- No M3 acceptance threshold exists (DR-0025 principle 7), and T1 creates none.
- Unit-test tolerances are derived or measured and justified in VAL-0020: round-off scale for the identity and gradient checks; measured truncation for the invariants.
- The Q1 tolerance must cover first-order-theory and mean-versus-osculating error. VAL-0018 measured +0.53 % for the node rate with osculating a₀. The tolerance is derived from that error source, not invented.

## 8. Numerical and physics invariants
- The simulator owns state. The J2 component is pure: no state, no I/O, no mutation, deterministic.
- One canonical value → all derived representations (P10).
- The axis is the frame z axis under J-ax-1. There is no Earth rotation angle, precession, nutation or polar motion (DR-0028; ADR-0009 item 17).
- The J2 reference radius is the WGS 84 a, and μ is the WGS 84 GM (DR-0024 Q2/Q3).
- Composition order, when composed: point mass, then J2 (ADR-0009 item 9).
- M1/M2 bytes are unchanged; v1/v2 cannot express J2 (frozen schemas).
- J2 = 0 is an exact identity case.

## 9. Stop conditions
Stop and report, without working around the problem, if:
- any M1/M2 gate, golden, digest or T0 check changes;
- an oracle disagrees beyond a justified tolerance, or a tolerance cannot be justified without inventing one;
- T1 appears to need the force context, mass, the scenario v3 schema, physics-identity serialization, runner or event changes, or any Earth-orientation input;
- a dependency or lock-file change appears necessary;
- the J2 derivation is not bit-identical across the CI platforms;
- the implementation is complete and validated. Then I stop for the independent-review authorization.

## 10. Explicit exclusions
- Drag, density, atmosphere, geodetic height, the termination/`reentry` semantics (T2/T3; P1–P5, P8, P9).
- The `ForceContext` protocol and its legacy adapter (T2 "force-context extension").
- `PhysicsConfiguration`/`physics_id`, the `PhysicsConfigured` event, scenario v3, runner integration and reference scenarios (T3).
- Validators, the M3 Proof script, `m3.json`, DOP853 references (T4).
- GMAT M3 references and `.cof` generation (T5); P6/Q-G2-1, DR-0028 P6(b).
- Thresholds; the M3 time step (Q-G2-4 stays PROVISIONAL).
- Any Earth-orientation model; higher harmonics.
- Changes to `src/tars/validation/`, `toolbox/`, `proof/thresholds`, `proof/references`, `.github/workflows`, `uv.lock`, `pyproject.toml`, scenarios, the events schema, the simulator or the runner.
- Deciding P1–P9 or any other open item; branch-protection changes.

## 11. Independent-review gate
- After implementation, a Proof run and green CI, I stop for authorization of an independent **Codex T1 review**.
- The review prompt includes the T1 authorization verbatim and pins the full SHA.
- Stop rules as in T0:
  - REQUEST_CHANGES → record and reproduce the findings, disposition each one (ACCEPTED / REJECTED_WITH_REASONING / ESCALATED_FOR_INVESTIGATION), apply no fix without authorization;
  - PASS → acceptance-candidate report, with no merge.
- Unresolved High findings block T1.

## 12. Remaining uncertainty that could affect authorization
1. **Axis parameter.** I propose no axis parameter: J-ax-1 makes the axis the frame z axis, and an injectable axis would look like the Earth-orientation hook that DR-0028 does not authorize. ADR-0009 item 17 says the axis is "pinned physics configuration", which T3's `PhysicsConfiguration` will carry. Confirm that T1 may defer the axis's configuration representation to T3.
2. **Force signature.** T1 uses the existing `(t, r, v)` protocol, because J2 needs no mass. T2 adds the context and adapter, and J2 then migrates or is adapted. If you prefer T1 to wait for the context protocol, T1 depends on T2's design.
3. **Q1 tolerance.** The first-order secular rate is approximate, and a defensible tolerance must come from a derived error estimate or a measured mean-element fit. If neither can be justified within T1, the Q1 test can only be reported, not asserted. I would raise that rather than pick a number.
4. **Cross-platform behaviour.** The bit-for-bit derivation assumes IEEE 754 `sqrt` on every CI platform. CI's three platforms test this assumption for the first time; it is not established yet.
5. **Q-G2-2** (identity-check rule) stays PROPOSED. T1's constant tests do not resolve it.
6. **Process question §1.3** (merge the decision branch first, or branch from it).

## Status update (recorded 2026-10-22, append-only)
- **Authorized:** "I-17 — Merge P10 Decision and Authorize M3 T1 J2 Force Model" (Tech Lead, 2026-10-22). It chose §1.3 option (A).
  - `m3-p10-decision-packet` was fast-forwarded into `main`, so `main` = `60648b93385a9954194730006aeac29ea14875ad`.
  - The decision branch is kept.
  - T1 branched from that `main` as `milestone-3-t1-j2-force-model`.
- **§12 answers given by I-17:**
  - item 1: the axis is fixed to the frame +Z axis and is not injectable;
  - item 2: the existing `acceleration(t, r, v)` interface, with no mass interface;
  - item 3: no invented tolerance. Measurements without a justified tolerance are reported as non-gating (I-17 §8);
  - item 4: bit identity across the three platforms must be confirmed, or work stops (I-17 §11).
- **Result:** T1 is **IMPLEMENTED; NOT REVIEWED, NOT ACCEPTED, NOT MERGED**. See `docs/milestones/M3-T1-report.md` and VAL-0020.
  - The derived J2 is bit-identical on the three CI platforms (CI run 39852509134).
- The independent T1 review (§11) needs separate owner authorization.

## Erratum (recorded 2026-10-23 UTC, append-only)
- **Authority:** I-19 §8 ("I-19 — M3 T1 Review 01 Corrections and Review 02 Authorization", Tech Lead).
- **Statement corrected:** the §7 table row "Q3 gradient" reads "acceleration = −∇U of the separately coded potential". **This is a sign-convention error in this packet's wording.** The correct relation is **acceleration = +∇U**. The original text above is preserved.
- **Basis:**
  - §3 item 2 of this packet uses the positive potential convention: U = (μ/r)[1 − J2 (a/r)² P₂(z/r)], P₂(s) = (3s² − 1)/2.
  - For that convention the acceleration is +∇U. The point-mass term checks this: ∇(μ/r) = −μ r/r³, which is the attraction.
  - The J2 term is U₂ = −(μ J2 a²/2)(3z²/r⁵ − 1/r³). Its gradient is (μ J2 a²/2)(−3x/r⁵ + 15xz²/r⁷, −3y/r⁵ + 15yz²/r⁷, −9z/r⁵ + 15z³/r⁷) = −(3/2) J2 μ a²/r⁵ · (x(1 − 5z²/r²), y(1 − 5z²/r²), z(3 − 5z²/r²)). That is the implemented acceleration (`src/tars/sim/forces.py`).
  - Codex T1 Review 01 derived the same result independently ("With positive potential U, acceleration is +∇U"; `docs/reviews/raw/M3-T1-codex-review01.md` §2).
  - The T1 tests check it numerically: `test_acceleration_is_the_gradient_of_the_separately_coded_potential` and `test_gradient_holds_at_every_latitude_band` compare the acceleration with **+∇U₂**, computed by dual numbers.
  - VAL-0020 states "a = ∇U₂".
- **Effect:** none on the implemented J2 physics, the tests or the evidence, which already use +∇U. Only this packet's wording was wrong.

## Status update (recorded 2026-10-24 UTC, append-only)
- T1, authorized by this packet under I-17, was **ACCEPTED** by the Tech Lead under I-22 at `65de33ffce72bb504dc28a3d17dbb0ae57b7a36b`, after Reviews 01–03 and the I-21 closure verification. Record: `docs/reviews/M3-T1-acceptance-dossier.md`. A fast-forward merge is conditionally authorized. T2 and later are not authorized.
