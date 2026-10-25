# M3 T2 — Authorization packet, revision 1 (drag force model)

**Status: DRAFT — NOT AUTHORIZED.** This packet authorizes nothing and carries no implied approval to execute. No T2 branch exists. No production code, test, scenario, threshold, reference or CI file has changed.  
**Prepared under:** "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25), §9 item 8.  
**Supersedes:** the decision content of `M3-T2-authorization-packet.md` (I-23 draft, reviewed in readiness Reviews 01–03). That draft is preserved unchanged as reviewed evidence. Where they differ, this revision governs.  
**Decision sources:** DR-0029 (P1–P9 recorded 2026-10-25; Resolution, Q-GATE); DR-0024, DR-0025, DR-0026 and DR-0027 ("I-26 note" in each); DQ-1 … DQ-6 (§5, verbatim).

## 0. How to read this packet
- Every "must" below describes what a **future** T2 authorization would require. **Nothing here is an instruction to start T2.**
- Status labels: **DECIDED** (owner decision), **PROVISIONALLY SELECTED**, **OPEN**, **ESCALATED_FOR_INVESTIGATION**, **NOT AUTHORIZED**.

## 1. Preconditions (amended gate, DR-0029 Resolution "Q-GATE")
| # | Precondition | State on `milestone-3-t2-owner-decisions` |
|---|---|---|
| PC-1 | P1–P5, P8 and P9 decided | **MET** (I-26) |
| PC-2 | DQ-1 … DQ-6 decided | **MET** (I-26; §5) |
| PC-3 | Resulting contracts recorded and reconciled: DR-0024 … DR-0029, ADR-0009, matrices, register, strategy, this packet | **Recorded.** The independent review of the reconciliation is pending (I-26 §7) |
| PC-4 | P4 (ii) supersession of DR-0026 AR-8/§5.8 "total density" below the lower edge | **MET** (owner's explicit instruction; DR-0026 "I-26 note") |
| PC-5 | Base branch for T2. The planning branch (`milestone-3-t2-decision-readiness`, `a57de3f`) and this branch are **not merged** to `main` (`fc50aed`) | **NOT MET.** Needs the owner's choice: merge, or direct T2 to branch from a named SHA (I-16/I-17 precedent) |
| PC-6 | `origin/main` verified, clean checkout, CI green on the base at T2 start | To be re-verified at T2 start |
| PC-7 | **An explicit, separate T2 implementation authorization** | **NONE** |

- **Not T2 prerequisites** (Q-GATE): P6, whose open items block geodetic GMAT acceptance in T5, and P7, which is DECIDED and binds T3/T4. P10 stays DECIDED and binding for T1.
- **The amendment waives no scientific, review, numerical or acceptance gate** (I-26 §3).

## 2. Scope a T2 authorization would cover
From `M3-proposal.md` §4 (T2 row) and the decisions.
1. **Force context and adapter (DQ-3 (a)):**
   - an immutable `ForceContext` carrying the current total mass, built in the simulator's derivative closures from the **stage** state (dry + max(prop, 0));
   - a context-aware protocol, with a legacy adapter for `acceleration(t, r, v)` models;
   - M1/M2 byte-identical on the same-platform regression gates (§6.3, R-1 … R-3);
   - **no change** to tick logic, engine scheduling, step splitting or atomicity.
2. **J2 (DQ-5 (a)):** the accepted T1 `ZonalJ2Gravity`, wrapped through the legacy adapter. Not rewritten, constants unchanged, no replacement model; every T1 gate preserved.
3. **Constants:** pinned 1/f = 298.257223563 and ω_E = 7.292115e-5 rad/s, additive in `tars.sim.constants`. `WGS84`, `EarthJ2Constants` and `WGS84_EGM2008_TIDE_FREE` are not edited. The derived f and e² are formed by the operation sequence of §5 DQ-1.
4. **Atmosphere dataset (DQ-4):**
   - the GMAT R2026a file, verbatim, under `src/tars/sim/data/`;
   - its SHA-256 `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e` (DR-0027 B-1) pinned in `tars.sim` and checked before parsing;
   - the one-band 250 km subset derived from it.
5. **Density component (DQ-2 km route; DR-0029 P4, P5):** GMAT band rule; fail closed below 0 m; top band extrapolated above 1000 km and labelled unverified; no continuity imposed at any base.
6. **Geodetic-height component (DQ-1 (α); DR-0029 P8, P2, P3):**
   - WGS 84 about +Z (J-ax-1);
   - the stated domain, rejecting the evolute region and the origin;
   - it returns h together with φ or n̂, as P2 requires for T3's dh/dt;
   - it never branches on band selection (P3).
7. **Drag force (DQ-6):**
   - cannonball model, a = −½ ρ (C_d A/m) |v_rel| v_rel, with v_rel = v − ω_E Ẑ × r;
   - C_d and A as immutable, owned binary64 constructor parameters, positive and finite;
   - mass from `ForceContext`;
   - numerical domain explicit (T1 R1-F2/R2-F1 pattern).
8. **Composition:** point mass → J2 → drag (thrust is added by the propulsion path, unchanged).
9. **Versioned model identifiers** (ADR-0009 item 5).
10. **Tests and records** per the validation strategy as revised (§6): a new unit-level VAL record, and SCI-0014 … SCI-0017 status updates written after the work is committed.

**Test vehicles:** where T2 unit tests use vehicle values, they use P9's V1 (850 kg, 15 m², C_d 2.2) or V2 (the M2 vehicle, 15 m², C_d 2.2), labelled **ILLUSTRATIVE — VALIDATION ONLY**. No new spacecraft schema (DQ-6).

## 3. Permitted files (for a future authorization to confirm)
| Path | Permission |
|---|---|
| `src/tars/sim/forces.py` | Additive: context protocol, adapter, drag class. `PointMassGravity`, `CompositeForceModel` and `ZonalJ2Gravity` unchanged (AST-identical) |
| `src/tars/sim/constants.py` | Additive only |
| `src/tars/sim/atmosphere.py`, `src/tars/sim/geodesy.py` (names indicative) | New |
| `src/tars/sim/data/EarthExponentialAtmosphereData.txt` | New; a verbatim copy, digest-checked |
| `src/tars/sim/simulator.py` | **DQ-3 (a):** only the derivative closures, to build `ForceContext` from the stage state. No change to tick, step-splitting, engine-schedule or atomicity logic |
| `tests/` | New T2 test modules; the existing literal-location test extended additively. `tests/test_zonal_j2.py` unchanged |
| `docs/science/validation.md`, `docs/science/assumptions.md`, `docs/science/experiments/m3-t2/` | Append-only, or new |
| `docs/milestones/M3-T2-report.md`; status notes in matrices and packets | New, or append-only |

## 4. Protected paths (a change to any of them is a stop condition)
- `proof/`, `toolbox/`, `scenarios/`, `.github/`;
- `uv.lock`, `pyproject.toml`;
- `src/tars/validation/` (including `approved_digests.py` and `architecture.py`);
- `src/tars/events/`, `src/tars/sim/scenario.py`, `src/tars/sim/runner.py`, `src/tars/sim/propulsion.py`, `src/tars/sim/integrators.py`;
- `docs/contracts/`;
- the T0 experiment files and results, and the T1 tests and evidence;
- every M1/M2 golden, reference, threshold and register entry.

## 5. Decided design (DQ-1 … DQ-6, I-26 §4, verbatim) and its specification
### DQ-1 — Geodetic algorithm: **DECIDED (α)**
> **DECIDED: α.**
>
> Reproduce the T0 iterative geodetic-height algorithm operation for operation within its applicable domain, including its starting latitude, convergence criterion and pole-safe height calculation.
>
> The T0-specific error bounds may be reused only where their original assumptions and arithmetic sequences actually apply.
>
> The T0 domain-guard defect must not be copied.
>
> Record that this deterministic, data-dependent iterative algorithm satisfies the intended T2 geodetic design requirement.

**Operation sequence to reproduce** (`docs/science/experiments/m3-t0/t0_model.py` at `a57de3f`, lines 38–42 and 144–162; T0 files are protected and unchanged):
1. Constants: a = 6378137.0; INV_F = 298.257223563; F = 1.0/INV_F; e2 = F·(2.0 − F). E1's "model ellipsoid" is defined by these binary64 values.
2. x, y, z as binary64; p = hypot(x, y).
3. Start: φ = atan2(z, p·(1.0 − e2)).
4. Iterate at most 60 times: s = sin φ; n = a/√(1.0 − e2·s·s); φ_new = atan2(z + e2·n·s, p). Stop after the update when |φ_new − φ| ≤ 1e-15.
5. Height: s = sin φ, c = cos φ; h = p·c + z·s − a·√(1.0 − e2·s·s).

**Recorded by the owner:** this deterministic, data-dependent iterative algorithm satisfies the intended T2 geodetic design requirement (DR-0026 §5.8's "fixed iteration count or a closed form"; DR-0026 "I-26 note").

**Additions that are not in the T0 function, and how they relate to the sequence:**
- **The domain guard (DR-0029 P8):** reject non-finite inputs, the origin and evolute-region points. T0's `geodetic_iterative` has no guard. A T2 guard only decides which inputs raise; on accepted inputs the arithmetic above is unchanged. The guard's predicate is a T2 design item, tested on both sides (strategy U-20).
- **The latitude (or n̂) is returned** with h (P2).
- **"The T0 domain-guard defect"** is the density guard's (DQ-2), not part of this function.

**Reuse of T0 bounds:** ε_h (E1) applies only to this sequence, at true height ≥ 0, for the inverse's own evaluation error, under A-FP-1 and A-FP-2 (decision packet N-1, P8 item 14). Under the owner's floating-point policy, a test that uses ε_h is **report-only** until A-FP-2 is promoted (§6.2).

**Conformance evidence (path (α)):**
- **Primary:** an operation-by-operation inspection of the T2 source against the sequence above, recorded in the T2 report and reviewed in the T2 review.
- **Supporting:** a same-platform bitwise comparison with the T0 spike on the T0 sample sets (strategy X-D1). It is **reported**; promoting it to a gate would need explicit approval.

### DQ-2 — Density arithmetic: **DECIDED (km route)**
> **DECIDED: km route.**
>
> Preserve the T0/GMAT kilometre-based density arithmetic for the applicable formula evaluation.
>
> The lower-domain guard must still operate on height in metres before conversion.
>
> Explicitly document the departure from DR-0024 §9's proposed convert-once-to-SI wording.
>
> Do not change the pinned atmospheric table or silently substitute a mathematically equivalent but numerically different expression.

**Operation sequence** (`t0_model.py` at `a57de3f`, lines 87–93 and 96–118; the domain guard is replaced as stated):
1. If h_m is not finite: a **distinct** error (P4).
2. **Guard, in metres, before any conversion:** if h_m < 0 (IEEE comparison; −0.0 is not below), raise the typed atmosphere-domain error (P4). *This replaces T0's guard, which tests h_km after the conversion and so accepts −2.475e-321 < h_m < 0 (open-issues register OI-21). Not copied.*
3. h = h_m/1000.0.
4. Band: the first i with h < base_km[i+1], else the top band (GMAT `FindBand`; an exact base belongs to the band above). base_km, ρ₀ and H_km are the table's decimal strings parsed to binary64.
5. ρ = ρ₀·exp(−(h − base_km)/H_km), with exactly this grouping.

On every input with h_m ≥ 0 this is the T0 km-route arithmetic. No T0 floor and no E1–E6 term changes (decision packet N-1).

**Departure from DR-0024 §9** ("converted once, at dataset load"): recorded in DR-0024 "I-26 note".

### DQ-3 — Simulator integration: **DECIDED (a)**
> **DECIDED: (a).**
>
> T2 may add the context-aware force protocol and integrate immutable ForceContext construction into the simulator's derivative closures.
>
> Current stage mass must be used.
>
> Preserve the legacy force-model interface through an adapter.
>
> Existing M1/M2 behavior must remain byte-identical on the specified same-platform regression gates.
>
> No change to tick logic, engine scheduling, step splitting or atomicity is approved by this decision.
>
> Implementation still requires separate authorization.

### DQ-4 — Dataset storage and digest: **DECIDED**
> **DECIDED: Pinned data file under `src/tars/sim/data/`, with its SHA-256 digest pinned in `tars.sim`.**
>
> Use the recorded GMAT R2026a source digest.
>
> Do not import `tars.validation.approved_digests` from the physics core.
>
> Use the approved file-access mechanism compatible with the static architecture guard.
>
> Verify the data file is packaged correctly.
>
> If packaging requires a protected `pyproject.toml` change, STOP. Do not silently adopt embedded Python bytes.
>
> The embedded-bytes alternative requires separate approval.

- **File access:** the static guard (`src/tars/validation/architecture.py`) forbids `importlib`, `os` and `tars.validation` in `tars.sim`, and does not forbid `pathlib`. The draft packet proposed `Path(__file__)`. Reading the file at load time, not on each force evaluation, keeps force evaluation free of I/O (DR-0026 AR-2).
- **Packaging, pre-authorization probe (I-26; not T2 evidence).** In a scratch copy of `a57de3f` with a probe file at `src/tars/sim/data/probe_dataset.txt`, `uv build --wheel --sdist --offline` included the file in the wheel (`tars/sim/data/probe_dataset.txt`) and in the sdist. `pyproject.toml` was byte-identical (sha256 `9b53279c…6fbf`).
  - Limits: uv 0.12.23, using its bundled `uv_build` backend; one host (macOS x86_64).
  - Record: `docs/reviews/raw/M3-T2-owner-decisions-I26-evidence/dq4_packaging_probe.out`.
  - **T2 must re-verify** with the real data file. The STOP rule stands.

### DQ-5 — J2 integration: **DECIDED (a)**
> **DECIDED: (a).**
>
> Wrap the accepted T1 J2 implementation through the legacy adapter.
>
> Do not rewrite the J2 force class, change its constants or create a replacement J2 model.
>
> Preserve all T1 evidence and validation gates.

### DQ-6 — Drag parameter ownership: **DECIDED**
> **DECIDED: Immutable drag-component constructor parameters.**
>
> C_d and cross-sectional area belong to the drag force component.
>
> Mass comes from ForceContext.
>
> Scenario v3 schema and serialization remain T3 responsibilities.
>
> No new spacecraft schema is authorized in T2.

Reconciliation with DR-0026 AR-7/§5.3 (the scenario owns spacecraft properties in v3): DR-0026 "I-26 note".

## 6. Validation requirements
### 6.1 Governing documents
- `M3-T2-validation-strategy.md`, as revised in its §6 (I-26).
- The owner's conditional floating-point policy (DR-0025 "I-26 note", verbatim).
- Red-first tests; mutation by assertion; no invented tolerance; no M3 threshold (DR-0025 principle 7).

### 6.2 Conditional-row register (I-26 §5: "identify every conditional row and the evidence required to promote it")
Under the policy, every row below is **report-only** until promoted. A row is promoted only when **all three** hold:
- (P-i) the named assumption is independently justified for the supported execution environment;
- (P-ii) the resulting criterion has been reviewed;
- (P-iii) the owner promotes it explicitly.

**Supported execution environment, for (P-i):**
- the three CI platforms: `ubuntu-latest` (Linux x86_64), `macos-latest` (macOS arm64) and `macos-15-intel` (macOS x86_64);
- CPython 3.12 (`requires-python >=3.12,<3.13`);
- the NumPy version locked in `uv.lock`.

The T0 measurements were made on macOS x86_64 only.

| Row (strategy) | What would gate | Assumption | Evidence required to promote (beyond P-ii, P-iii) |
|---|---|---|---|
| U-13 (B-9 (i)) | ρ̂ ≤ the E3 upper enclosure inside a band | A-FP-2 | **J-FP2** (below), for `exp` (and `pow`, if used). If the justified accuracy is weaker than LIBM_ULP = 2, E3 is recomputed at the justified value and reviewed |
| U-17 (B-12) | \|ĥ − h_ref\| ≤ ε_h(h) at exact-answer points, h ≥ 0, path (α) | A-FP-2 | J-FP2 for `sin`, `cos`, `atan2`, and for `hypot` (CPython's own code, not the libm). ε_h is recomputed if the justified accuracy differs from LIBM_ULP = 2 |
| U-19 (a) (B-11 (a)) | ĥ(Q_z r) = ĥ(r) exactly for quarter turns about +Z | A-LM-1 | **J-LM1** (below) |
| U-19 (c) (B-11 (c)) | \|ĥ(r) − ĥ(σr)\| ≤ 2ε_h(h), σ a quarter turn or z → −z, exterior | A-FP-2 | As U-17 |
| PM-4 (a) (B-10) | ρ̂(h₁) ≥ ρ̂(h₂) for h₁ < h₂ in one band | A-LM-2 | **J-LM2** (below) |
| PM-5 (B-12) | 1-Lipschitz plus ε_h terms, exterior | A-FP-2 | As U-17 |
| PM-6 (B-12) | \|r\| − a − ε_h ≤ ĥ ≤ \|r\| − b + ε_h, exterior | A-FP-2 | As U-17 |
| **U-23, third clause** (T0 E4b) — *newly identified as conditional under I-26* | positive C_d, A with C_d·A ≤ 2⁻¹⁰⁷⁵ ⇒ exactly zero drag | A-FP-2 (E4b's cap c₀ ≤ 5/8 uses the `exp` allowance; DR-0029 P1, R6-F3) and the spike's coefficient sequence | J-FP2 for `exp`, and a T2 drag coefficient sequence identical to T0's E4 sequence, or E4b re-derived for T2's sequence and reviewed. The strategy row listed this as exact (E), but its I-24 text already named A-FP-2; strategy §6 corrects the classification |
| U-18 (B-4) | forward-constructed points within ε_h + δ_f | A-FP-2, **and** the deliverable δ_f | The δ_f derivation (or an oracle with a stated error), reviewed (P8 decision), plus everything U-17 needs |

**Report-only regardless of any assumption** (I-26 §5): U-19 (b), exact z-reflection equality; PM-4 (b), strict decrease.

**Deliverable rows** (report-only until their derivation is written and reviewed, G-T2-3a; no assumption is promoted by deriving them): B-3 (U-7 magnitudes), B-5 (U-19 (d), PM-2), B-6 (U-21), B-7 (I-2), B-8 (I-7 (b)), and B-4 above.

**Evidence standards named in the table** (what "independently justified" would mean; none is met today):
- **J-FP2 (A-FP-2).** For each platform, identify the implementation behind each function used: libm `sin`, `cos`, `atan2`, `exp`, `pow`, and CPython 3.12's own `math.hypot`. Then provide one of:
  - (i) a documented accuracy guarantee from the implementation's maintainers, cited from a source that was actually read;
  - (ii) a proof, or an exhaustive check, over the input domain the bound is used on;
  - (iii) an implementation with a proven bound (a correctly rounded library). That is a dependency change and needs a Decision Request.

  Sampled measurements alone are not justification (T0 lesson R2-F1). The glibc manual's statement (DR-0029 P1) is a statement of intent, not a bound, and no Apple statement was found.
- **J-LM1 (A-LM-1).** A source-level argument from the pinned CPython 3.12 `math.hypot` implementation that the result is invariant under swapping the arguments and under negating either one, reviewed. Sampling (0 failures in 10⁵ pairs, I-24) is not sufficient.
- **J-LM2 (A-LM-2).** For each platform's `exp`, a documented monotonicity property, or correct rounding (which implies monotonicity), or a proof over the band-exponent range used. An error bound such as A-FP-2 does not imply monotonicity.

**Unconditional gates kept** (independently justified, I-26 §5 "preserve"):
- B-1 (U-4, PM-1) and B-2 (U-5, PM-3), under A-FP-1 only. A-FP-1 is IEEE 754 itself, checked at run time by X-P4.
- B-13 (U-12, ρ̂ = ρ₀ at the 27 bases). It is an exact check of 27 specific inputs on every CI platform, so the test observes its own premise (A-LM-0) on each platform.
- B-14's "no exception, and ρ̂ = 0 ⇒ zero drag".
- U-1, U-2, U-3, U-6, U-8 … U-11, U-14, U-15, U-16 (behaviour part), U-20, U-22, U-24, I-6, I-7 (a), X-P1, X-P2, X-P4.
- U-23 apart from its third clause.
- The R-1 … R-6 regression guarantees.

### 6.3 Regression gates (DQ-3: "the specified same-platform regression gates")
- R-1: M1 Proof 9/9; golden `7a4e1877…20a4`.
- R-2: M2 Proof 20/20; `m2_proof` 228/228; the M2 golden, snapshot, GMAT manifest and threshold digests.
- R-3: T1 109 tests; J2 hex; `zonal_j2` outputs bit-identical to `65de33f`.
- R-4: T0 314 checks.
- R-5: protected paths unchanged.
- R-6: CI's four jobs green on every pushed commit.

M1 runs in one fresh clone and M2 in another, with `uv` on PATH.

## 7. Independent review requirements
Unchanged from the I-23 draft §7, plus:
- the T2 review prompt quotes I-26 §4 and §5 verbatim;
- the review checks path (α) and route (km) conformance by inspection (§5);
- the review checks that no conditional row is presented as a gate.

Stop rules as T0/T1:
- REQUEST_CHANGES → record, reproduce and disposition each finding. No fix and no further round without authorization.
- PASS → acceptance dossier. No acceptance and no merge without explicit decisions.

## 8. Stop conditions
The I-23 draft §8 list stands, with these changes:
- **Packaging:** stop if including the data file needs a `pyproject.toml` change; never fall back to embedded bytes without approval (DQ-4).
- **Path (α)/(km):** stop if the T2 implementation cannot reproduce the §5 operation sequences exactly (for example, if a needed function differs between `math` and NumPy on a platform), rather than substituting an equivalent expression.
- **Conditional rows:** stop if T2 completion would appear to need a conditional row as a gate. Under the policy such rows are reported. Promoting one needs P-i … P-iii.
- **Scope:** stop if T2 appears to need any of: the P3 precedence, the P2 crossing event, P1 admissibility, the T3 outcome mapping of the P4 error, scenario v3, or the P6/X-1 work.

## 9. Acceptance and merge gates
Unchanged from the I-23 draft §9:
1. Codex review PASS.
2. Acceptance dossier, then the owner's explicit acceptance.
3. A separate merge authorization: fast-forward only, by ordinary push, with the post-merge checks.
4. The merge recorded in the next branch.

## 10. Explicit exclusions
**Not in T2 (each needs its own authorization):**
- **T3:** scenario v3, `PhysicsConfiguration`/`physics_id`, `PhysicsConfigured`, runner integration, `reentry` and the P3 precedence, P1 admissibility and κ's placement, the P2 crossing event, the run-outcome mapping of the P4 domain error.
- **T4:** validators, the M3 Proof, `m3.json`, DOP853 references, Q-G2-6.
- **T5:** GMAT M3 references, `.cof` generation, P6 (PROVISIONALLY SELECTED only), the DR-0028 P6(b) ruling (OPEN), X-1 (NOT AUTHORIZED), any geodetic GMAT gate (NOT AUTHORIZED).

**Not authorized anywhere by this packet:**
- thresholds, and the final M3 time step (Q-G2-4 PROVISIONAL);
- Earth orientation, higher harmonics, winds, lift, MSIS-class atmospheres;
- changes to T1's classes or constants;
- promoting A-FP-2, A-LM-1 or A-LM-2;
- deciding any OPEN item.

## 11. What the T2 authorization itself would need to state (implementer's suggestion; not a request to execute)
1. The base: a named SHA on `main` after an authorized merge of this branch, or a named SHA on this branch (PC-5).
2. That T2 implements §2 within §3 and §4, under the §5 decisions.
3. That the §6.2 register applies: every conditional row is reported.
4. The review and stop rules of §7 and §8.
5. That T3, T4 and T5 remain NOT AUTHORIZED.

- *(2026-10-25, append-only)* **Independent Review 01 of the I-26 recording (Codex, at `2cd1e6e`): REQUEST_CHANGES.** M3T2OD-R1-F1 (MAJOR): the `reentry` outcome identifier was left open although I-26 P3 decides it. M3T2OD-R1-F2 (MINOR): RM-3b was called "measured". Both are reproduced and ACCEPTED, **not applied** (I-26 §7 stop). Record: `docs/reviews/M3-T2-owner-decisions-review-01.md`.
