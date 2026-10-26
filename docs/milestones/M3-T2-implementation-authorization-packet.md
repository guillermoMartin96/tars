# M3 T2 — Implementation Authorization Packet (revision 2, drag force model)

- **Status: DRAFT — NOT AUTHORIZED.** This packet authorizes nothing. No T2 implementation branch exists. No production code, test, scenario, threshold, reference or CI file has changed.
- **Prepared under:**
  - "I-30 — T2 Owner-Decision Reconciliation Acceptance and Merge Authorization", §6;
  - "I-31 — Pre-Merge Whitespace Exception Amendment", §5 (owner/Tech Lead, 2026-10-26).
- **Base:** `main` = `0a9c040430138845d529b3d8691a86d0f4fea61e`. That is the accepted reconciliation (I-30 §1), fast-forwarded under I-31.
- **Relation to revision 1:** `M3-T2-authorization-packet-r1.md` stays in force for everything this revision does not change: the scope items (§2), the permitted and protected paths (§3, §4), the DQ-1 … DQ-6 decisions and operation sequences (§5), the conditional-row register (§6.2), the regression gates (§6.3) and the exclusions (§10). This revision adds:
  - the numerical acceptance strategy that I-30 §6 asks for;
  - interfaces;
  - traceability;
  - platform reproducibility requirements;
  - the test plan;
  - gates and stop conditions;
  - the exploratory Rust note;
  - the decisions needed from the owner.

  Where the two differ, this revision governs **only once the owner approves the decision named at that point** (§14).
- **Validation strategy:** `M3-T2-validation-strategy.md` (§1–§5 as reviewed, §6 as revised under I-26) keeps its row identifiers (U-, PM-, I-, X-, R- and B-rows). This packet refers to them and does not renumber them.

## 0. How to read this packet
- **Nothing here is an instruction to start T2.** Every "must" describes what a future T2 authorization would require.
- **Status labels:** DECIDED, PROPOSED (needs an owner decision, §14), DELIVERABLE (written and reviewed during T2), REPORT-ONLY, BLOCKED, NOT AUTHORIZED.
- **Evidence tags:**
  - **[S]** source actually read (cited with location);
  - **[P]** a pre-authorization probe run for this packet (§6.8; research evidence, **not T2 evidence**, single host);
  - **[R]** the implementer's reasoning;
  - **[A]** an assumption.
- **Scope of "geodetic accumulation" (PROPOSED, D-0).** I-30 §6 asks for "independently justified geodetic accumulation acceptance gates". This packet reads that as the rounding error that accumulates inside one geodetic-height evaluation:
  - through the iterated latitude and the final height formula of DQ-1 (α);
  - and its effect on the density band selection.

  This is the quantity E1 (ε_h) bounds. Accumulation of error along a **trajectory** is T4 work (the M3 Proof, DOP853 references), and this packet does not address it.

## 1. Preconditions (DR-0029 Resolution "Q-GATE"), updated
| # | Precondition | State on `main` `0a9c040` |
|---|---|---|
| PC-1 | P1–P5, P8, P9 decided | **MET** (I-26) |
| PC-2 | DQ-1 … DQ-6 decided | **MET** (I-26) |
| PC-3 | Contracts recorded and reconciled | **MET**: reconciliation accepted (I-30 §1), closure review PASS with no findings |
| PC-4 | P4 (ii) supersession of DR-0026 AR-8/§5.8 | **MET** (I-26) |
| PC-5 | Base branch | **MET**: the reconciliation is on `main` (`0a9c040`, I-31). T2 would branch from a named `main` SHA |
| PC-6 | `origin/main` verified, clean, CI green at T2 start | To be re-verified at T2 start. Post-merge CI on `0a9c040`: see the I-31 report |
| PC-7 | An explicit, separate T2 implementation authorization | **NONE** |
| PC-8 *(new)* | The owner's decisions on §14 D-0 … D-8 | **OPEN.** The T2 authorization would state which were approved. Every PROPOSED item that is not approved falls back to r1 and the I-26 policy (report-only) |

P6 and P7 are not T2 prerequisites (Q-GATE). P6's open items, the geodetic-drag residual (ESCALATED), DR-0028 P6(b) (OPEN) and X-1 (NOT AUTHORIZED), block geodetic GMAT acceptance in T5. They do not block T2.

## 2. Scope and deliverables
### 2.1 Implementation scope (unchanged from r1 §2)
- The force context and its adapter (DQ-3 (a)).
- J2 through the adapter (DQ-5 (a)).
- Pinned 1/f and ω_E.
- The atmosphere dataset and its digest (DQ-4).
- The density component (DQ-2 km route; P4, P5).
- The geodetic-height component (DQ-1 (α); P8, P2, P3).
- The drag force (DQ-6).
- Composition in the order point mass → J2 → drag.
- Versioned model identifiers.
- Tests and records.

### 2.2 Additional T2 deliverables (needed by the §6 strategy; DELIVERABLE, reviewed before any row they support may gate)
| ID | Deliverable | Needed for |
|---|---|---|
| DL-1 | **Elementary-function premise oracle (O-1)**, test-side. It returns references for `sin`, `cos`, `atan2`, `exp` and the exact √(x² + y²) at binary64 arguments, each with a **written error bound** (series remainder, argument reduction, decimal rounding). It decides A-FP-2's premise for one call, failing closed if the reference's error band straddles the limit (§6.4) | POG rows (§6.3) |
| DL-2 | **True-height oracle (O-2)**, test-side. It computes the exact geodetic height of a binary64 point on the model ellipsoid, with a **written error bound** (Newton convergence and decimal rounding). The trig-free foot-point method of `docs/science/experiments/m3-t0/t0_oracle.py` is the model; its current text states precision, not a bound | U-17, U-18, PM-5, PM-6, U-19 (c) |
| DL-3 | **Call-tracing harness**, test-side: it records every `math` call that the geodetic and density components make, with arguments and results, and checks that the trace is **complete** (§6.4 rule 4) | POG rows |
| DL-4 | **Sequence-conformance twin**: the DQ-1 and DQ-2 operation sequences re-coded in the test from the packet r1 §5 text, not from the component, and compared **bitwise** with the component on the same platform | DQ-1/DQ-2 conformance; height-equivalent mutants (§8.3) |
| DL-5 | **Environment fingerprint** in every gate-evidence run: OS, machine, `sys.version`, `platform.libc_ver()`, the macOS version, NumPy version and the `uv.lock` digest | §7 |
| DL-6 | The §3.9 deliverable derivations T2 chooses to complete (B-3 … B-8). Rows without a reviewed derivation stay reported (G-T2-3a) | As listed in strategy §3.9 |
| DL-7 | **J-LM1-even record**: the CPython source argument for `hypot` evenness (§6.5), re-checked against the exact patch version used on each CI platform | U-19 (a′) |

## 3. Interfaces (PROPOSED; names indicative, final names are T2 design within DQ-3 and DQ-6)
| Interface | Requirement | Source |
|---|---|---|
| `ForceContext` | Frozen; carries the stage total mass as owned binary64. Built in the simulator's derivative closures from the stage state (dry + max(prop, 0)). Non-finite or non-positive mass rejected | DQ-3 (a); DR-0026 Q-G3-1, §5.2 |
| Context-aware force protocol plus a legacy adapter | `acceleration(t, r, v)` models (point mass, `ZonalJ2Gravity`, `FreeSpace`) are wrapped unchanged; arguments are passed through and results returned bitwise | DQ-3 (a), DQ-5 (a) |
| Density function `density(h_m) → ρ` | Non-finite input: a distinct error. Finite h_m < 0: the typed atmosphere-domain error, decided **in metres before conversion**. Then the DQ-2 km route exactly | DQ-2; P4; P5 |
| Geodetic function `geodetic(r) → (h, φ)` | The DQ-1 (α) sequence exactly. The domain guard rejects non-finite input, the origin and the evolute region. Returns the latitude with h (P2) | DQ-1; P8; P2 |
| Drag component | Constructor (C_d, A): positive, finite, owned binary64, immutable. Mass from `ForceContext`. v_rel = v − ω_E Ẑ × r. The T0 E4 coefficient sequence, or B-1 and E4b re-derived | DQ-6; R-DRAG |
| **Testability requirements** *(new; PROPOSED, D-6)* | (i) Elementary functions are called as `math.<name>` through the module attribute, never bound at import (`from math import sin`), so that DL-3 sees every call. (ii) The drag component's v_rel is observable to tests, or is recomputed by the identical sequence (strategy U-4 notes). (iii) The specified sequences use Python `float` scalars and `math`; NumPy is not used for their arithmetic (§7 RQ-6) | [R] §6.4, §7 |

No interface for T3 items (`reentry`, the P3 precedence, P1 admissibility, the P2 crossing event, the outcome mapping of the P4 error, scenario v3) is introduced in T2.

## 4. Permitted and protected paths
Unchanged from r1 §3 and §4. The test-side deliverables DL-1 … DL-4 live under `tests/` (new modules or helpers). They are **not** importable from `src/tars/sim`: the static guard forbids `tars.validation` in the physics core, and the oracles must not become physics dependencies.

## 5. Dependency traceability
| Source | Item | Status | Where it binds T2 |
|---|---|---|---|
| DR-0024 | Q1/P10 J2 identity; Q2/Q3 constants; Q5/Q5a table, no continuity repair; Q6 geodetic height; Q7 drag model, ω_E; Q8 domain via DR-0027 B-4; Q9 vehicles via P9; §9 convert-once (departed from per DQ-2, recorded) | DECIDED | Scope items 2–7; U-9 … U-17; R-CONST |
| DR-0025 | Principles 1–9; principle 7 (no M3 threshold); §8 mutations; floating-point policy ("I-26 note") | DECIDED | §6, §8, §10; no tolerance invented |
| DR-0026 | AR-2 purity; AR-7/§5.3 (scenario owns spacecraft data in v3, reconciled by DQ-6); Q-G3-1 context; Q-G3-4 one literal; Q-G3-7 no per-sample telemetry; Q-G3-8 order; §5.8 fixed iteration or closed form (satisfied by DQ-1 per the owner) | DECIDED | §3 interfaces; U-1 … U-3, U-22, U-24 |
| DR-0027 | B-1 digest `75762f67…`; B-3 subset; A-s → P4; B-4 → P5; A-4/A-5/A-6 → P1/P2/P3 (T3) | DECIDED | U-11 … U-16; T3 items excluded |
| DR-0028 | J-ax-1 (+Z axis, no Earth orientation); P6(b) ruling OPEN | DECIDED / OPEN | Geodetic and drag about +Z; nothing of P6 in T2 |
| DR-0029 | P1–P5, P7–P9 DECIDED; P6 NOT FULLY DECIDED; Q-GATE; DQ-1 … DQ-6; `reentry` and the precedence DECIDED (implemented in T3) | DECIDED (P6 open) | §1; §2; §10 exclusions |
| ADR-0009 | Force-context identity, item 5 model identifiers, item 9 order, item 17 extension point (design only) | DECIDED | §3; R-ID |
| Packet r1 §6.2 | Conditional-row register, promotion conditions P-i … P-iii, evidence standards J-FP2, J-LM1, J-LM2 | DECIDED (policy) | §6: the promotion route proposed here |

## 6. Numerical acceptance strategy for geodetic accuracy (the I-30 §6 core item)
### 6.1 The problem
- **The bound exists.** The geodetic-height accuracy rows (U-17, U-19 (c), PM-5, PM-6, U-18) compare ĥ with a reference against **ε_h(h) = αh + β** (T0 E1, `t0_termination.rounding_allowances`; derived and reviewed in T0 Reviews 03–10). E1 is a worst-case bound for the DQ-1 (α) sequence at true height ≥ 0.
- **The bound rests on an unjustified assumption.** E1 holds only if every elementary call is within LIBM_ULP = 2 units of 2⁻⁵² relative (plus an absolute subnormal term): that is **A-FP-2**. A-FP-2 is not justified on any CI platform, so under the owner's policy every such row is **report-only**. Unless something changes, T2 would complete with **no gated geodetic accuracy check at all**, only the domain checks (U-20).
- **The numbers** [P], from `rounding_allowances()` at LIBM_ULP = 2:
  - α = 1.221e-15;
  - β = 8.878e-9 m;
  - ε_h(120 km) = 9.02e-9 m;
  - ε_h(2000 km) = 1.13e-8 m.

### 6.2 Options compared
| Option | What would justify the gate | Evidence found | Verdict |
|---|---|---|---|
| **S1. Documented accuracy guarantees (J-FP2 (i))** | Maintainers' published bounds for each platform's `sin`, `cos`, `atan2`, `exp` | **glibc** [S] (manual §19.7, "Known Maximum Errors in Math Functions"): the library "does not aim for correctly rounded results"; "some functions have bugs meaning they do not meet these goals in all cases"; the test suite flags only errors above 9 ulp. That is a statement of goals and test thresholds, not a bound. **Apple libm:** no published bound found (as recorded in r1). **CPython `hypot`** [S] (3.12.15 source comment): "faithfully rounded (less than 1 ulp error)", based on analysis and testing, not a proof | **Not achievable** for macOS, and not a bound for glibc |
| **S2. A correctly rounded library (J-FP2 (iii))** | Proven correct rounding implies A-FP-2 (and A-LM-2) | **CORE-MATH** [S] (core-math.gitlabpages.inria.fr; MIT): binary64 `exp`, `sin`, `cos`, `atan2` provided; a proof is linked for `sin` only; bivariate functions are "checked only against known hard-to-round cases". glibc 2.43 integrated seven binary64 functions, none of `exp`, `sin`, `cos`, `atan2` | **Not viable for T2.** A native dependency (needs a Decision Request and protected `pyproject.toml`/`uv.lock` changes); proofs incomplete for the functions used; DQ-1 reproduces T0's `math` calls. Possible future route (§13) |
| **S3. Tolerance derived from requirements** | An oracle comparison with a fitness-for-purpose tolerance | Would be a new M3 threshold | **Forbidden** in T2 (DR-0025 principle 7; thresholds after T6) |
| **S4. Status quo: report-only** | Nothing; the rows are reported | Already the policy | **Fallback.** T2 accuracy acceptance for geodetic height is then **BLOCKED** (§6.7) |
| **S5. Premise-Observed Gating (POG)** *(recommended)* | J-FP2 (ii), "an exhaustive check over the input domain the bound is used on". The gate is used only on a fixed, finite set of test points. On each CI platform, the test observes A-FP-2's premise **at every elementary call those evaluations actually make**, against an oracle with a written error bound. Where every premise holds, E1 applies to that evaluation on that platform by derivation, so ε_h is justified there | Feasibility [P]: 631 points, 11 867 traced calls, **0 premise violations**, worst observed error 0.766 × 2⁻⁵² (`cos`). Worst \|ĥ − h_true\| = 1.92e-9 m = **0.216 ε_h**. Runtime about 1.5 s. Single host (macOS x86_64, CPython 3.12.15) | **Recommended (D-1)** |

### 6.3 The recommendation: Premise-Observed Gating (POG)
**Definition.** A conditional row is *POG-gated* on a platform when all of the following hold:
1. **Fixed inputs.** Its inputs are a fixed, recorded, finite set. It uses no random draw at run time, or only a seeded draw that is recorded.
2. **Complete trace.** For each input, DL-3 records every elementary-function call that the component makes, and checks that the record is complete (§6.4 rule 4).
3. **Premise checked call by call.** DL-1 decides each traced call against the row's named premise (A-FP-2 for E1, E3 and E4b; A-LM-2 or the hypot swap premise for exact-equality rows), with the oracle's error bound taken against the premise.
4. **Conclusion gated where the premise holds.** If every call's premise holds, the row's conclusion is gated with the **already derived, reviewed** bound (E1 for ε_h, E3 for U-13, B-10 for PM-4 (a), and so on). No new tolerance is introduced.
5. **Premise failures are reported, never skipped.** If any traced call fails its premise, the outcome is a distinct **PREMISE-NOT-OBSERVED** result: not a pass, and not a component defect. On a gated row it is a **stop condition** (§11). The sample sets are fixed in advance, so a premise failure cannot be hidden by dropping points.

**What POG justifies** [R]:
- The gate's tolerance, on the gated inputs, on each platform that observed the premise. This is P-i for those rows in the sense of J-FP2 (ii).
- The gate keeps its discriminating power. In the mutant probe [P], an ε_h gate against the trig-free oracle rejected every one of the following:
  - spherical height;
  - dropped flattening;
  - a datum offset as small as 1e-7 m (every point);
  - a + 1 m;
  - f used for e²;
  - sin and cos swapped;
  - a geocentric start;
  - one-iteration truncation (139 of 624 points).

**What POG does not justify** (stated in every record that uses it):
- A-FP-2 for production inputs. The accuracy of ĥ on arbitrary run-time inputs stays an **unjustified assumption**, and nothing in T2 or later may cite POG as a production accuracy guarantee.
- Any cross-platform equality (§7 RQ-3).
- Any threshold on trajectories (T4/T6).
- Height-equivalent latitude defects (§8.3). Height is stationary in latitude at the solution, which E1 (i)–(ii) uses: truncation after two or three iterations and a 1e-9 rad stopping tolerance both stayed within 0.24 ε_h in the probe. These are caught by DL-4 instead.

**Promotion under the policy.** POG supplies P-i only. Each row still needs:
- P-ii: its criterion reviewed in the T2 independent review, including DL-1 … DL-3 and their error derivations;
- P-iii: explicit owner promotion at T2 acceptance.

D-1 asks the owner to accept POG as a **route** to P-i. It does not promote any row now.

### 6.4 POG rules (requirements on DL-1 … DL-3)
1. **Oracle error, fail-closed.** Say the reference r has error at most δ and the premise is |f̂ − f| ≤ L, with L = 2·2⁻⁵²·|f| + 2·2⁻¹⁰⁷⁴. The check passes only if |f̂ − r| + δ ≤ L, evaluated with |r| − δ in place of |f|. Otherwise it fails closed. δ is derived in DL-1, and must be at most 2⁻¹⁰⁰·|r|, so that the check is never the limiting factor.
2. **Exact arguments.** The traced arguments and results are the binary64 values the component actually used. They are converted exactly (`Fraction`/`Decimal` from float), and never re-rounded.
3. **`sqrt` and the arithmetic.** These are covered by A-FP-1 (IEEE 754 correct rounding), checked by X-P4. The trace may also confirm `sqrt` correct rounding on the gated calls; the probe did [P].
4. **Trace completeness.** For DQ-1, the call count is fixed by the sequence: 1 `hypot`, 1 `atan2`, then for each iteration k one `sin`, one `sqrt` and one `atan2`, then a final `sin`, `cos` and `sqrt`. The harness asserts that the observed count equals the expected count for the iteration number the component reports, or reproduces. A mutant that binds `sin` at import (bypassing the trace) must be killed by this assertion (§8.3).
5. **Domain.** E1 applies only at true height ≥ 0. Domain membership is decided by O-2, which refuses interior points. Points inside the ellipsoid are reported (P8).
6. **Reference for the conclusion.**
   - Exact-answer points (P8 (a)) use their exact reference.
   - Forward-constructed points (P8 (a′)) use **O-2's true height of the binary64 point actually produced**, with gate |ĥ − h_O| ≤ ε_h(h_O + δ_O) + δ_O. Using O-2 removes the need for the δ_f term (strategy B-4 names "an oracle with a stated error" as its alternative). Changing P8's (a′) condition from "δ_f derived" to "O-2 with a derived error bound" is an owner decision (**D-7**).

### 6.5 A-LM-1, split by a source argument (PROPOSED, D-3)
Source [S]: CPython v3.12.15 `Modules/mathmodule.c`, sha256 `436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281`, `math_hypot` and `vector_norm`.

- **Evenness: an exact source argument.** `math_hypot` replaces every argument with `fabs(x)` before anything else. `hypot(±x, ±y)` therefore calls `vector_norm` with a bit-identical coordinate array, and returns bit-identical results. This needs no accuracy assumption. It gives a **new unconditional exact row, U-19 (a′)**: ĥ is unchanged under the half-turn (x, y) → (−x, −y) about +Z and under the reflections x → −x and y → −y, because DQ-1 sees x and y only through p = hypot(x, y). The argument is valid for the reviewed patch version only (DL-7, §7 RQ-4).
- **Symmetry under swapping arguments: not provable from the source.** For n = 2 the loop forms csum = fl(fl(1 + x²_hi) + y²_hi), which depends on the order. The maintainers claim faithful rounding and an empirical commutativity test, not a proof.
  - Probe [P]: 0 swap mismatches and 0 negation mismatches in 2 × 10⁶ pairs. That is a sample, not a proof.
  - **Exact quarter-turn equality, U-19 (a), therefore stays conditional on A-LM-1 (symmetry part).** It may be POG-gated (the premise hypot(x, y) = hypot(y, x), observed at each gated point; D-4), or it stays report-only.
- J-LM1 in r1 asked for both properties from the source. This packet supplies evenness only.

### 6.6 A-LM-2 (PM-4 (a), non-increasing density in a band)
- **J-LM2 is not met:**
  - no documented monotonicity for either platform's `exp` [S: the glibc manual states no such property];
  - correct rounding is not available (S2);
  - an exhaustive check over the band-exponent range is infeasible (about 2⁶² binary64 values) [R].
- **Recommendation (D-4): POG with premise A-LM-2 at the traced `exp` arguments.** For each gated pair (h₁ < h₂, same band) the harness observes x₁ ≤ x₂ ⇒ exp(x₁) ≤ exp(x₂) for the two traced calls. The gate then asserts ρ̂(h₁) ≥ ρ̂(h₂) through B-10.
- **Why this is not tautological** [R]: the premise concerns `exp` alone. The conclusion also tests TARS's band selection, its exponent sign and grouping, and the km conversion. A defect in any of those breaks the conclusion while the premise holds.
- **PM-4 (b) (strict decrease) and U-19 (b) (exact z-reflection) stay report-only regardless** (owner policy).

### 6.7 What stays BLOCKED or report-only
- **If D-1 is not approved:**
  - every A-FP-2 row stays report-only: U-13, U-17, U-19 (c), PM-5, PM-6, U-18 and U-23's third clause;
  - **T2 acceptance of geodetic-height accuracy is BLOCKED.** T2 could still be accepted on its unconditional gates (structural, domain, exact and regression), if the owner chooses, with that limitation recorded.
- **U-18 / P8 (a′):** report-only unless D-7 is approved and DL-2's error derivation passes review.
- **Rows with no derivation (B-3 … B-8):** report-only until derived and reviewed (G-T2-3a). POG does not change this, because POG needs a derived conclusion to gate.
- **Exact z-reflection (U-19 (b)) and strict decrease (PM-4 (b)):** report-only, always.
- **Production accuracy of ĥ:** A-FP-2 remains unjustified (§6.3).

### 6.8 Pre-authorization probe evidence ([P]; research, not T2 evidence)
- **Location:** `docs/reviews/raw/M3-T2-authorization-I31-evidence/`. It contains:
  - `premise_probe.py.txt` / `.out`: the T0 `geodetic_iterative` with traced `math` calls, the premise checks and the ε_h comparison against `t0_oracle.true_height`;
  - `mutant_probe.py.txt` / `.out`: 13 mutants against the ε_h gate;
  - `hypot_probe.py.txt` / `.out`: evenness and swap behaviour of `hypot`;
  - `SHA256SUMS`.
- **Limits:**
  - one host (macOS x86_64, CPython 3.12.15); not run on the CI platforms (that would need a CI change, which is protected);
  - the decimal references used here (T0's `d_sin`, `d_cos`, `d_atan2`) stop when the series sum stops changing and **carry no written error bound**. DL-1 and DL-2 must supply bounded versions;
  - they used the T0 spike, not T2 code.

### 6.9 Error budget (geodetic height, path (α), at true height ≥ 0)
| Term | Value or requirement | Source |
|---|---|---|
| Component evaluation error | ≤ ε_h(h) = αh + β; α = 1.221e-15, β = 8.878e-9 m (LIBM_ULP = 2) | E1 [S: `t0_termination.rounding_allowances`] |
| O-2 reference error δ_O | DELIVERABLE (DL-2). Requirement: δ_O ≤ 1e-6 β (≈ 9e-15 m), so that it is negligible against β | [R] |
| O-1 per-call reference error δ | DELIVERABLE (DL-1). Requirement: ≤ 2⁻¹⁰⁰ relative | [R] §6.4 rule 1 |
| Gate inequality | \|ĥ − h_ref\| ≤ ε_h(h_ref + δ_O) + δ_O (exact references: δ_O = 0) | §6.4 rule 6 |
| Observed margin (probe, one host) | max \|ĥ − h_true\| = 1.92e-9 m = 0.216 ε_h | [P] |
| Not budgeted here | The model ellipsoid vs WGS 84 b (+1.71e-12 m, reported separately per U-17); P6's 0.14–0.38 m GMAT residual (T5, ESCALATED) | Strategy U-17; DR-0029 P6 |

## 7. Platform floating-point reproducibility requirements
| ID | Requirement | Gate? |
|---|---|---|
| RQ-1 | Same-platform bitwise repetition of every T2 output (X-P1) | Gate (E) |
| RQ-2 | Constant literals and derived constants (f, e², ω_E, J2 identity) bit-identical on the three CI platforms (X-P2) | Gate (E) |
| RQ-3 | **No cross-platform bitwise expectation** for any output that depends on `exp`, `sin`, `cos`, `atan2` or `hypot`. Cross-platform differences are measured in ulps (X-P3) and reported. No tolerance is borrowed (DR-0025 §7; ADR-0008 TL-7 by analogy) | Report |
| RQ-4 | **Environment fingerprint** (DL-5) recorded with all gate evidence. Rows resting on a source argument (U-19 (a′)) are valid only for a reviewed CPython patch version. CI installs the latest 3.12.x (`.python-version` = `3.12`), so a patch-version change on any platform invalidates DL-7 until re-checked (**D-5** chooses between pinning the patch version and re-checking it) | Gate (stop on unreviewed version) |
| RQ-5 | A-FP-1 at run time on each platform (X-P4): round-to-nearest-even, gradual underflow, no flush-to-zero | Gate (E) |
| RQ-6 | The DQ-1, DQ-2 and DQ-6 sequences are evaluated in Python `float` scalars and `math` calls, operation for operation. CPython does not contract `a*b + c` into FMA. NumPy is not used for their arithmetic, because a NumPy dot or norm may use FMA or SIMD reordering (A-FP-3) | Gate by inspection and DL-4 |
| RQ-7 | M1/M2 regression gates stay same-platform (R-1 … R-3), as approved | Gate |
| RQ-8 | POG premises are observed **separately on each CI platform**. A premise failure on any platform for a gated row is a stop condition, never a skip | Gate / stop |

## 8. Test plan
### 8.1 Red-first discipline (packet r1 §6.1; T1 precedent)
For each row:
1. Write the test.
2. Run it against the absent or stubbed component, and record that it fails **for its declared reason**.
3. Implement.
4. Record that it passes.

The red and green runs are recorded in the T2 report. A test that passes before the implementation exists is a defect in the test.

### 8.2 Adversarial and boundary cases (in addition to strategy §3.5)
- **Geodetic:**
  - coordinates at ±0.0 (all sign combinations), near-axis p down to subnormal, and |z| = b exactly ±1 ulp;
  - x = a exactly ±1 ulp on the equator;
  - points just outside and inside the evolute region (the guard's predicate ±1 ulp);
  - |r| near overflow of the squared terms;
  - every non-finite component;
  - the published reverse example (30 km, 30 km, 0) rejected (U-20).
- **POG harness:**
  - a deliberately perturbed `math` (via the trace proxy) that returns results 3 ulp off: the premise check must report PREMISE-NOT-OBSERVED, not PASS;
  - an oracle whose error band straddles the limit: the check must fail closed.
- **Density:** the strategy's U-12, U-14 and U-15 sets, plus the km-route trap interval (−2.475e-321 < h_m < 0), which must raise.
- **Drag:** C_d·A at the E4b cap (POG-conditional), a zero parameter raising, mass at depletion with −1e-17 propellant, v_rel = 0, and ρ̂ subnormal and 0.

### 8.3 Mutation strategy (strategy §3.8, extended)
- **Each mutant needs a designated killing assertion**, with the reason it fails. Survivors are documented.
- **Height-equivalent mutants, a new finding [P]:**
  - **The mutants:** truncating the latitude iteration after 2 or 3 steps, and loosening the stopping tolerance to 1e-9 rad, change ĥ by less than 0.24 ε_h.
  - **What does not kill them:** an accuracy gate on h, because height is stationary in latitude at the solution.
  - **Designated killers:**
    - DL-4, the bitwise conformance with the DQ-1 sequence on the same platform;
    - for the latitude returned to T3, U-21. U-21 stays report-only until B-6 is derived, so it is not a designated killer before then.
  - **Consequence:** strategy §3.8's "the latitude iteration truncated" mutant is killed by DL-4, not by U-17.
- **POG harness mutants:**
  - premise check disabled, or always true: killed by the 3-ulp perturbation test;
  - trace bypassed (`from math import sin` in the component): killed by trace completeness (§6.4 rule 4);
  - oracle bound ignored (δ = 0): killed by the straddle test;
  - PREMISE-NOT-OBSERVED downgraded to a skip: killed by a test that asserts the run fails.
- **Protection removal (T1 pattern):** each domain guard removed (non-finite, origin, evolute, h_m < 0, digest) must be killed.

## 9. Regression protection
- R-1 … R-6 (r1 §6.3) unchanged: M1 Proof 9/9 with its golden; M2 Proof 20/20 and `m2_proof` 228/228 with their digests; T1's 109 tests, J2 hex and `zonal_j2` outputs bit-identical to `65de33f`; T0's 314 checks; protected paths unchanged; CI's four jobs green on every pushed commit.
- **R-7 (new): completed M3 records unchanged.** DR-0024 … DR-0029, ADR-0009 and the reconciliation and review records on `main` `0a9c040` may receive append-only status notes only.
- Regression checks recompute; they never read stored values (strategy principle 5).

## 10. Independent review and acceptance gates
r1 §7 and strategy §4 (G-T2-1 … G-T2-9, as revised in strategy §6.2) stand, with these changes:
- **G-T2-1 / G-T2-2:** the conditional parts gate only for rows **promoted under the policy**. With D-1 (and D-3, D-4, D-7 where relevant) that means:
  - DL-1 … DL-3 and their error derivations reviewed (P-ii);
  - the premise observed on all three CI platforms (RQ-8);
  - the owner's explicit promotion at acceptance (P-iii).
- **G-T2-10 (new):** DL-4 bitwise conformance passes on each CI platform; DL-5 fingerprints recorded; DL-7 matches every platform's CPython patch version.
- **G-T2-11 (new):** the POG harness mutants (§8.3) are killed.
- **Review content:**
  - the T2 review prompt quotes I-26 §4–§5, I-30 §4 and the approved §14 decisions verbatim;
  - it checks that no conditional row is presented as a gate unless promoted;
  - it checks that no POG record claims production accuracy.
- **Stop rules as before:** REQUEST_CHANGES → record, reproduce and disposition each finding; no fix and no new round without authorization. PASS → acceptance dossier; no acceptance or merge without explicit decisions.

## 11. Stop conditions (in addition to r1 §8)
1. **Premise not observed:** PREMISE-NOT-OBSERVED on any gated input on any CI platform. Record it, and do not drop the point or re-sample.
2. **Oracle derivations:** the DL-1 or DL-2 derivation cannot meet its §6.9 requirement, or does not pass review. The dependent rows stay report-only; never substitute a sampled reference.
3. **Trace:** the trace cannot be made complete (for example, a component call path that the harness cannot observe).
4. **Platform drift:** a CI platform's CPython patch version differs from the one DL-7 reviewed (unless D-5 chose pinning and the pin holds).
5. **Sequence conformance:** DL-4 shows that the component cannot reproduce the DQ-1 or DQ-2 sequence bitwise on a platform. Stop; do not substitute an equivalent expression (r1 §8).
6. **Scope:** T2 appears to need a tolerance, a threshold, a T3/T4/T5 item, P6/X-1 work, a dependency change (S2), or a protected-path change.
7. **Scientific dependency:** any T2 gate would come to depend on A-FP-2, A-LM-1 (symmetry) or A-LM-2 beyond the POG-observed inputs.

## 12. Exclusions
Unchanged from r1 §10:
- **T3:** scenario v3, `physics_id`, the runner, `reentry` and the P3 precedence, P1 admissibility, the P2 crossing event, the P4 outcome mapping.
- **T4:** validators, the M3 Proof, DOP853, trajectory accumulation.
- **T5:** GMAT, P6, P6(b), X-1, any geodetic GMAT gate.
- **Not authorized anywhere:** thresholds, the final dt, Earth orientation, higher harmonics, changes to T1, promoting A-FP-2, A-LM-1 or A-LM-2 outside the POG route, and deciding any OPEN item.

## 13. Rust: exploratory note (no decision requested; no migration or rewrite proposed)
**Standing decisions** (RES-0001 and ADR-0008, branch `research/flight-software-architecture`, `2d6d7e5`, unmerged):
- Python stays the reference (TL-1).
- Rust is the preferred candidate for a future Flight Core investigation only (TL-2).
- The language is deferred until hardware, real-time, numerical, memory and assurance requirements exist (TL-6).
- No C or Rust implementation (TL-9).
- Planning constraint PC-1 applies: revisit before any software crosses into flight or embedded execution.
- AT-1 … AT-7, U2 (assurance standard) and U3 (milestone mapping) are open.

**This note adds nothing to those decisions.**

**What T2's numerical work adds to that research** [R], with sources [S]:
1. **Transcendental reproducibility is a platform property, in Rust as in Python.**
   - Rust's `f64::sin`, `cos` and `exp` carry the documented note: "The precision of this function is non-deterministic. This means it varies by platform, Rust version, and can even differ within the same execution from one invocation to the next" [S: doc.rust-lang.org, `f64`]. `atan2` "currently corresponds to the `atan2` from libc".
   - `sqrt` and `mul_add` are documented as correctly rounded IEEE 754 operations [S: same page].
   - A Rust Flight Core would therefore face the same A-FP-2 problem as T2. Within-execution non-determinism would also defeat RQ-1-style repetition unless the implementation is pinned.
2. **A pinned, portable implementation exists**, but it is not a correctness proof:
   - the `libm` crate is "a port of MUSL's libm to Rust", usable in stable `#![no_std]`. It has been merged into `compiler-builtins`, and the standalone repository was archived on 2025-04-28 [S: github.com/rust-lang/libm];
   - pinning one software libm gives cross-platform bit reproducibility (RES-0001 §6 layer 2), but not accuracy guarantees. POG-style premise checks would carry over unchanged.
   - CORE-MATH (S2) is the route to proven correct rounding, function by function.
3. **Assurance tooling:**
   - Ferrocene states qualification for ISO 26262 (ASIL D), IEC 61508 (SIL 3, "with support for customer certification toward SIL 4") and IEC 62304 (Class C), with a certified core-library subset for ASIL B and SIL 2 [S: ferrocene.dev];
   - DO-178C is not listed there;
   - which standard would apply to TARS is RES-0001 U2, still open.
4. **Space-domain evidence is early-stage:**
   - Seidel and Beier, "Bringing Rust to Safety-Critical Systems in Space" (IEEE 3S 2024; arXiv:2405.18135) [S: abstract]: recommendations, plus a partial rewrite of a C satellite communication component, finding three vulnerabilities;
   - an ESA/DLR study (activity 4000140242, "cRustacea") was found in search results, but its pages require a login and were **not read**; no claim is made from it;
   - no flagship NASA mission flying Rust flight software was found.

**Conclusion** [R]: Rust has a plausible future role in a Flight Core that would cross into embedded execution (PC-1). T2 shows that the numerical question (which libm, and how its accuracy is justified) must be settled **independently of the language**, and that the POG approach would transfer. No action is proposed. AT-1 … AT-7 remain open.

## 14. Decisions requiring owner approval
| ID | Decision | Recommendation | If not approved |
|---|---|---|---|
| D-0 | Scope of "geodetic accumulation" = the error accumulated within one geodetic evaluation and its band-selection effect; trajectory accumulation is T4 | Approve | Clarify the intended scope; §6 may need extension |
| **D-1** | Accept **Premise-Observed Gating** (§6.3–§6.4) as a route to P-i (J-FP2 (ii) over the gated finite domain) for the A-FP-2 rows. It explicitly does **not** justify A-FP-2 for production inputs. No row is promoted by this decision | **Approve** | A-FP-2 rows stay report-only; geodetic accuracy acceptance **BLOCKED** (§6.7) |
| D-2 | Accept DL-1 … DL-7 as T2 deliverables, each reviewed before it supports a gate | Approve with D-1 | Without DL-1 … DL-3, POG cannot run |
| D-3 | Accept the CPython 3.12.15 source argument for `hypot` **evenness** (J-LM1-even), giving unconditional row U-19 (a′); quarter-turn symmetry stays conditional | Approve | U-19 (a′) is not added; U-19 (a) stays report-only |
| D-4 | Allow POG for the A-LM-1 symmetry premise (U-19 (a)) and the A-LM-2 premise (PM-4 (a)) | Approve | Both stay report-only |
| D-5 | CPython patch version: (a) pin `.python-version` to an exact 3.12.x, or (b) record and re-check it on every run, stopping on any unreviewed version | (b): no CI or environment change; (a) is a wider change affecting M1/M2 environments | — |
| D-6 | Testability requirements in §3 (module-attribute `math` calls; v_rel observable; no NumPy in the specified sequences) | Approve | POG cannot guarantee trace completeness; RQ-6 is unenforced |
| D-7 | P8 (a′): gate forward-constructed points against **O-2's true height of the binary64 point** (DL-2 bound) instead of deriving δ_f | Approve | U-18 stays report-only until δ_f is derived |
| D-8 | Make DL-4 (bitwise conformance with the DQ-1/DQ-2 sequences, same platform) a **gate** under G-T2-10. Today X-D1 (bitwise vs the T0 spike) is reported only | Approve: it is the only killer of height-equivalent latitude mutants (§8.3) | Those mutants survive; DQ-1 conformance rests on inspection alone |

## 15. What the T2 authorization itself would need to state
1. The base: a named `main` SHA (at least `0a9c040`), re-verified at T2 start (PC-6).
2. That T2 implements r1 §2 within r1 §3–§4, under the DQ-1 … DQ-6 decisions, with the §3 interfaces.
3. Which of D-0 … D-8 are approved, quoted verbatim.
4. That every conditional row is reported unless promoted at acceptance through the approved route (P-i … P-iii).
5. The §10 gates, the §11 stop conditions and r1 §8.
6. That T3, T4 and T5 remain NOT AUTHORIZED, as do P6, P6(b), X-1, thresholds and any dependency change.

**T2 implementation remains NOT AUTHORIZED.**
