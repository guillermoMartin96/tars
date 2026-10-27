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
- **Corrected under I-33** (owner/Tech Lead, 2026-10-26), after independent Review 01 (`docs/reviews/M3-T2-packet-r2-review-01.md`, REQUEST_CHANGES):
  - corrections are made in place and marked *(corrected under I-33, …)*;
  - the reviewed text is preserved at `0e37db6`;
  - the correction map is §16, and the correction record is `docs/reviews/M3-T2-packet-r2-review-01-corrections.md`;
  - evidence is in `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/` (research, not T2 evidence).
- **Corrected under I-34A** (owner/Tech Lead, 2026-10-26), for the three MINOR findings of independent Review 02 (`docs/reviews/M3-T2-packet-r2-review-02.md`, PASS):
  - the corrections are marked *(I-34A, R2-Fn)*;
  - the Review 02 text is preserved at `5f96119`;
  - the record is `docs/reviews/M3-T2-packet-r2-review-02-corrections.md`, and the map is §16;
  - evidence is in `docs/reviews/raw/M3-T2-packet-r2-I34A-evidence/`.
  - No decision or threshold is changed, and no acceptance requirement is loosened. DL-2 gains one recorded review obligation: a supported domain and failure reporting (R2-F3).
- **Corrected under I-35** (owner/Tech Lead, 2026-10-26), after Review 03 (`docs/reviews/M3-T2-packet-r2-review-03.md`, PASS):
  - the packet's only substantive change is the §7.1 rule for unavailable probes, plus this note and the §16.2 map;
  - the R3-F1 and R3-F2 corrections are in the I-34A correction record, §3a;
  - evidence is in `docs/reviews/raw/M3-T2-packet-r2-I35-evidence/`.

  No owner decision is made or changed.
- **Owner decisions recorded under I-37** (owner/Tech Lead, 2026-10-27; append-only, §17): D-0 … D-8 **APPROVED with conditions**; D-6 (i) stays withdrawn. The §14 proposal table is preserved as written. **This packet still authorizes nothing: T2 implementation remains NOT AUTHORIZED (PC-7).**

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
| PC-8 *(new)* | The owner's decisions on §14 D-0 … D-8 | **OPEN.** The T2 authorization would state which were approved. Every PROPOSED item that is not approved falls back to r1 and the I-26 policy (report-only). *(I-37, 2026-10-27, append-only: **MET**. D-0 … D-8 are recorded in §17. PC-7 is unchanged.)* |

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
| DL-1 | **Elementary-function premise oracle (O-1)**, test-side. *(Corrected under I-33, F2 and observation C.)* For each traced call it returns a **rigorous rational enclosure** [lo, hi] of the exact value of `sin` or `cos` (\|x\| ≤ 2), `atan2` (x ≥ +0), `exp`, or the exact √(x² + y²). Each enclosure has a written derivation: series remainders, directed rounding and exact identities at zeros. Out-of-domain arguments are refused. The premise is decided over the whole enclosure (§6.4 rule 1): PASS, FAIL or INCONCLUSIVE, and INCONCLUSIVE fails closed. A draft with derivations exists ([P], I-33; **unreviewed**) | POG rows (§6.3) |
| DL-2 | **True-height oracle (O-2)**, test-side. *(Corrected under I-33, observation A.)* It returns an enclosure [L, U] of the geodetic height of a binary64 point on the model ellipsoid (a = 6378137, e2 the binary64 value of DQ-1 step 1):<br>• **U:** the distance to a point exactly on the ellipsoid;<br>• **L:** the support-function bound (m·r − σ(m))/\|m\|, which certifies an exterior point when L ≥ 0.<br>The method needs no convergence argument **provided the construction is admissible** *(corrected under I-34A, R2-F3)*: the constructed surface point lies exactly on the ellipsoid (so its constructed coordinate lies within the ellipse's range), and the support direction m is nonzero. Given an admissible construction, any foot-point approximation gives a valid enclosure, and its quality only affects the width. A draft with derivations exists ([P], I-33; **unreviewed**).<br>• **The draft's coverage is not established** (I-34A, R2-F3). With its fixed Newton budget it is not admissible throughout the twin's finite-intermediate domain (§6.4 rule 5). It raises `ValueError` while constructing the surface point at (2¹⁰²⁰, 2¹⁰²⁰, 2¹⁰²⁰), where the twin's intermediates are finite. On every sampled off-axis ray it raises from \|r\| ≈ 2¹³⁹ upward; on the sampled axis and equatorial rays it does not. At the origin (m = 0, outside DQ-1's guarded domain) it raises `ZeroDivisionError` (`i34a_minor.out`). These samples are corroboration, not a supported-domain bound.<br>• An oracle exception **fails closed**: no enclosure and no verdict. It is never converted into a pass or an enclosure (§6.3 step 6). A reviewed supported domain, and how oracle failure is reported, are DL-2 implementation-review obligations (I-33 derivations §5) | U-17, U-18, PM-5, PM-6, U-19 (c) |
| DL-3 | **Witness harness**, test-side. *(Replaced under I-33, F1.)* It supplies the library object through which **the DL-4 twin** makes every elementary call. It records each call's arguments and result, and returns the result object unchanged. It checks:<br>• the twin's call list against the list DQ-1 implies for the iteration count;<br>• that every arithmetic and library intermediate is finite (observation B);<br>• completeness, by a **fault-injection self-test**: a definite premise violation injected at each call index in turn must be reported.<br>The component is **not** instrumented. Tracing the component may be kept as a diagnostic, but no conclusion rests on it (§6.3) | POG rows |
| DL-4 | **Sequence-conformance twin**: the DQ-1 and DQ-2 operation sequences re-coded in the test from the packet r1 §5 text, not from the component, and compared **bitwise** with the component on the same platform, comparing **both h and φ** *(I-33, F5)*. Under POG it is also the **witness**: the evaluation whose premises DL-3 observes (§6.3). Conformance shows that the component's outputs equal the specified sequence's on that platform. **It does not show numerical correctness**: a faulty library shared by the component and the twin passes conformance (§6.3, F5). *(I-34A, R2-F1.)* It is **output** conformance. It does not show which operations the component performed, nor that it avoids NumPy: a component using `numpy.cos` matches the twin bit for bit at all 631 exterior points (`pog_pipeline.out` (3b)). Throughout this packet, "sequence conformance" (DL-4, G-T2-10, D-8) means this output equality. Internal sequence and arithmetic requirements are verified by operation-by-operation source inspection (r1 §5 DQ-1, "Primary") | DQ-1/DQ-2 conformance; POG witness; height-equivalent mutants (§8.3) |
| DL-5 | **Environment record** in every gate-evidence run. *(Expanded under I-33, F4.)* The fields are in §7.1, each marked as observed, partly observed or not observable. Recording identifies an environment; **it does not prove numerical reproducibility** | §7 |
| DL-6 | The §3.9 deliverable derivations T2 chooses to complete (B-3 … B-8). Rows without a reviewed derivation stay reported (G-T2-3a) | As listed in strategy §3.9 |
| DL-7 | **J-LM1-even record**: the CPython source argument for `hypot` evenness (§6.5), re-checked against the exact patch version used on each CI platform. *(Corrected under I-33, F4.)* It is also re-checked against the interpreter build record of §7.1: the build-configuration fields and the executable digest | U-19 (a′) |

## 3. Interfaces (PROPOSED; names indicative, final names are T2 design within DQ-3 and DQ-6)
| Interface | Requirement | Source |
|---|---|---|
| `ForceContext` | Frozen; carries the stage total mass as owned binary64. Built in the simulator's derivative closures from the stage state (dry + max(prop, 0)). Non-finite or non-positive mass rejected | DQ-3 (a); DR-0026 Q-G3-1, §5.2 |
| Context-aware force protocol plus a legacy adapter | `acceleration(t, r, v)` models (point mass, `ZonalJ2Gravity`, `FreeSpace`) are wrapped unchanged; arguments are passed through and results returned bitwise | DQ-3 (a), DQ-5 (a) |
| Density function `density(h_m) → ρ` | Non-finite input: a distinct error. Finite h_m < 0: the typed atmosphere-domain error, decided **in metres before conversion**. Then the DQ-2 km route exactly | DQ-2; P4; P5 |
| Geodetic function `geodetic(r) → (h, φ)` | The DQ-1 (α) sequence exactly. The domain guard rejects non-finite input, the origin and the evolute region. Returns the latitude with h (P2) | DQ-1; P8; P2 |
| Drag component | Constructor (C_d, A): positive, finite, owned binary64, immutable. Mass from `ForceContext`. v_rel = v − ω_E Ẑ × r. The T0 E4 coefficient sequence, or B-1 and E4b re-derived | DQ-6; R-DRAG |
| **Testability requirements** *(new; PROPOSED, D-6; corrected under I-33, F1)* | (i) *Withdrawn under I-33.* Module-attribute `math` calls no longer support any conclusion: POG observes the twin, not the component (§6.3), so how the component binds its functions does not matter. (ii) The drag component's v_rel is observable to tests, or is recomputed by the identical sequence (strategy U-4 notes). (iii) The specified sequences use Python `float` scalars and `math`, and NumPy is not used for their arithmetic (§7 RQ-6). This is an **implementation** requirement, verified by operation-by-operation source inspection (r1 §5 DQ-1, "Primary"). *(Corrected under I-34A, R2-F1: r2/I-33 said "DL-4 enforces it at the tested points". DL-4 cannot: it compares outputs only, and a `numpy.cos` component matches the twin bit for bit, `pog_pipeline.out` (3b).)* DL-4 adds output conformance at the tested points | [R] §6.4, §7 |

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
- **The numbers** [P], from `rounding_allowances()` at LIBM_ULP = 2, displayed rounded. The gate uses the exact `Fraction`s (§6.4 rule 7; *I-33, observation D*):
  - α = 1.221e-15 (1.2212453270876738e-15);
  - β = 8.878e-9 m (8.877691069434736e-9 m);
  - ε_h(120 km) = 9.02e-9 m;
  - ε_h(2000 km) = 1.13e-8 m.
- **E1's domain** *(I-33, observation B)*: true height ≥ 0 **and no overflow**. E1 has no upper height limit, but finite inputs can overflow (§6.4 rule 5).

### 6.2 Options compared
| Option | What would justify the gate | Evidence found | Verdict |
|---|---|---|---|
| **S1. Documented accuracy guarantees (J-FP2 (i))** | Maintainers' published bounds for each platform's `sin`, `cos`, `atan2`, `exp` | **glibc** [S] (manual §19.7, "Known Maximum Errors in Math Functions"): the library "does not aim for correctly rounded results"; "some functions have bugs meaning they do not meet these goals in all cases"; the test suite flags only errors above 9 ulp. That is a statement of goals and test thresholds, not a bound. **Apple libm:** no published bound found (as recorded in r1). **CPython `hypot`** [S] (3.12.15 source comment): "faithfully rounded (less than 1 ulp error)", based on analysis and testing, not a proof | **Not achievable** for macOS, and not a bound for glibc |
| **S2. A correctly rounded library (J-FP2 (iii))** | Proven correct rounding implies A-FP-2 (and A-LM-2) | **CORE-MATH** [S] (core-math.gitlabpages.inria.fr; MIT): binary64 `exp`, `sin`, `cos`, `atan2` provided; a proof is linked for `sin` only; bivariate functions are "checked only against known hard-to-round cases". glibc 2.43 integrated seven binary64 functions, none of `exp`, `sin`, `cos`, `atan2` | **Not viable for T2.** A native dependency (needs a Decision Request and protected `pyproject.toml`/`uv.lock` changes); proofs incomplete for the functions used; DQ-1 reproduces T0's `math` calls. Possible future route (§13) |
| **S3. Tolerance derived from requirements** | An oracle comparison with a fitness-for-purpose tolerance | Would be a new M3 threshold | **Forbidden** in T2 (DR-0025 principle 7; thresholds after T6) |
| **S4. Status quo: report-only** | Nothing; the rows are reported | Already the policy | **Fallback.** T2 accuracy acceptance for geodetic height is then **BLOCKED** (§6.7) |
| **S5. Premise-Observed Gating (POG)** *(recommended; corrected under I-33, F1)* | J-FP2 (ii), "an exhaustive check over the input domain the bound is used on". The gate is used only on a fixed, finite set of test points. On each CI platform the test establishes, **for the output value the component returns**, that it is an evaluation of the DQ-1 sequence whose every elementary result satisfies A-FP-2:<br>• it observes the premise at every call of an independently written twin, against bounded oracles;<br>• it requires the component's output to equal the twin's bitwise (witnessed evaluation, §6.3).<br>E1 then applies to that output by derivation | **Feasibility, not proof** [P]:<br>• **I-31:** 631 points, 11 867 traced calls, 0 premise violations; worst \|ĥ − h_true\| = 1.92e-9 m = 0.216 ε_h; unbounded references.<br>• **I-33 rerun with the draft bounded oracles and the strict rule:** 631 E1-PASS and 2 points not certified exterior, out of 633. Same single host (macOS x86_64, CPython 3.12.15)<br>The oracle derivations are unreviewed (§6.7) | **Recommended (D-1)**. **BLOCKED as a gate** until DL-1 … DL-4 are reviewed (§6.7) |

### 6.3 The recommendation: Premise-Observed Gating (POG)
**Why the r2 design was replaced** *(I-33, F1)*. Packet r2 traced the component's own `math` calls and checked their number (old rule 4). Review 01 showed that this cannot link the checked values to the computation:
- a component can make every expected call, in order, and then discard a result in favour of an untraced one;
- the reviewer's example keeps an identical 8-call trace and is 64.98 m wrong.

Reproduced in I-33: the r2 count check passes that mutant (`f1_witness.out`). No proxy on the component can see:
- a function bound at import;
- a NumPy or C-level call;
- a value replaced after tracing;
- the internals of a native function such as `hypot`.

**Corrected definition: witnessed evaluation** *(I-33, F1)*. A conditional row is *POG-gated* on a platform at a point when all of the following hold:
1. **Fixed inputs.** Its inputs are a fixed, recorded, finite set. It uses no random draw at run time, or only a seeded draw that is recorded.
2. **A complete witness.**
   - The DL-4 twin (DQ-1 or DQ-2, written from the r1 §5 text) evaluates the point. It makes every elementary call through the DL-3 library object.
   - The twin is test code, so its completeness is a property of reviewed code. It is checked by the call-list assertion and by fault injection at every call index (§6.4 rule 4).
   - All of the twin's intermediates are finite (§6.4 rule 5).
3. **Bitwise conformance.** The component's returned values (h and φ; ρ for density) equal the twin's bit for bit. Otherwise the outcome is **SEQUENCE-NONCONFORMANT**, a failure.
4. **Premise observed on the consumed values.** DL-1 decides the row's named premise for every call result the twin's arithmetic consumed: A-FP-2 for E1, E3 and E4b; A-LM-2 or the hypot swap premise for exact-equality rows. Every sqrt result is checked for exact correct rounding (§6.4 rule 3).
5. **Conclusion gated where everything holds.** The row's conclusion is gated with the **already derived, reviewed** bound (E1 for ε_h, E3 for U-13, B-10 for PM-4 (a), and so on), under the strict comparison of §6.4 rule 6. No new tolerance is introduced.
6. **Failures are reported, never skipped.** A premise that is not observed (FAIL or INCONCLUSIVE) gives the distinct result **PREMISE-NOT-OBSERVED**: not a pass, and not a component defect. On a gated row it is a **stop condition** (§11). The sample sets are fixed in advance, so a failure cannot be hidden by dropping points.

**Why witnessed evaluation links the checked values to the computation** [R; drafted in the I-33 evidence, `DL1-DL2-draft-derivations.md` §4, **unreviewed**]:
- The claim concerns the **output value**.
- If the component's output equals, bit for bit, the output of the DQ-1 sequence evaluated with elementary results that each satisfy A-FP-2 (under A-FP-1 for the arithmetic), then E1 bounds that output.
- What the component did internally does not matter. Hidden calls, discarded values and values replaced after a call either change the output bits, which is a failure, or leave them unchanged, in which case the pass is still sound.

**I-33 adversarial results** [P] (`f1_witness.out`, `pog_pipeline.out`):

| Case (I-33 §2) | Result |
|---|---|
| Correct trace with a hidden incorrect cosine (+1e-5) | SEQUENCE-NONCONFORMANT at 615 of 633 points. The rest are axis points, where p = 0 makes the cosine irrelevant and the output bits identical |
| A traced result discarded (stale sin) | Nonconformant at 163 points. At the other 468 the bits are identical |
| An unobserved call supplying the value: the same function bound at import, or `numpy.cos` | E1-PASS at all 631 exterior points, with bits identical to the correct component (sound). A perturbed unobserved call (2⁻⁴⁰ relative) is nonconformant at 608 points |
| One invocation omitted from the harness (a twin calling `math.cos` directly) | Killed by the call-list assertion (22 calls against 23 expected) |
| A faulty `math` shared by the component and the twin (F5) | Conformance passes, but PREMISE-NOT-OBSERVED (FAIL) |
| Fault injection at every call index of the correct twin | Detected at 8/8 and 23/23 indices on the two probe points |

- **Soundness check:** over 8 mutants and 633 points, **no** mutant reached E1-PASS with output bits different from the correct component's.
- **What the harness observes:** the values the twin consumes, and the component's returned values.
- **What it does not observe:**
  - the component's internal operations;
  - native internals (CPython's `hypot` loop and its internal square roots; the libm algorithms);
  - any other argument.
- **Native functions** are checked at the level of their **mathematical contract**: `hypot` against the exact √(x² + y²), which is what E1 uses. A `hypot` result 1 ulp high passes (within A-FP-2); a 2⁻⁴⁰ relative error gives PREMISE-NOT-OBSERVED.
- **Instrumentation:** the component is not instrumented. The twin's library object returns the result object unchanged: 5/5 points are bit-identical with and without it.

**If the witness cannot be established** (the twin cannot be reviewed as a faithful transcription, or the component cannot meet bitwise conformance on a platform), **POG accuracy gating stays BLOCKED** (§6.7).

**What POG justifies** [R]:
- The gate's tolerance, on the gated inputs, on each platform where every step above holds. This is P-i for those rows in the sense of J-FP2 (ii).
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
- *(I-33, F5)* **Numerical correctness from conformance alone.** Bitwise conformance shows that the component's outputs equal the twin's evaluation of the specified sequence. It does not show which operations produced them *(I-34A, R2-F1)*. A faulty component and a faulty reference can agree exactly: a shared faulty cosine gives identical bits and a 51 m error (`f1_witness.out`). The accuracy claim comes only from steps 4 and 5 (premise and E1), never from conformance.

**Promotion under the policy.** POG supplies P-i only. Each row still needs:
- P-ii: its criterion reviewed in the T2 independent review, including DL-1 … DL-3 and their error derivations;
- P-iii: explicit owner promotion at T2 acceptance.

D-1 asks the owner to accept POG as a **route** to P-i. It does not promote any row now.

### 6.4 POG rules (requirements on DL-1 … DL-4) *(rules 1 and 3–7 corrected or added under I-33)*
1. **Premise decision over the oracle's enclosure, failing closed** *(F2; observation C)*.
   - A-FP-2 is |f̂ − f| ≤ UF·|f| + ν, with UF = 2·2⁻⁵² and ν = 2·2⁻¹⁰⁷⁴ (`t0_termination.py` lines 455–457). It is a relative-plus-absolute bound, **not a fixed number of ulps**.
   - **Ulp metric** *(corrected under I-34A, R2-F2)*.
     - **Definition:** ulp(f) = 2^(e′ − 52), with e′ = max(⌊log₂ |f|⌋, −1022). This is the binary64 spacing at the exact value f, and it is 2⁻¹⁰⁷⁴ below 2⁻¹⁰²².
     - **Exact allowance:** a displacement |f̂ − f| = k·ulp(f) satisfies A-FP-2 iff k ≤ A(f), where A(f) = (UF·|f| + ν)/ulp(f) = 2·|f|/2^e′ + 2^(−1021 − e′). The comparison is inclusive.
       - The first term is between 2 (f = 2ᵉ) and 4 (f → 2ᵉ⁺¹), depending on where f lies in the binade.
       - The second term, ν, is 2 ulps at e′ = −1022 and halves with each binade above.
     - **Review 02's two cases:**
       - f = 1.5 gives A = 3 + 2⁻¹⁰²¹, so 1.5 + 3 ulps passes;
       - f = 2⁻¹⁰²² gives A = 4, so 2⁻¹⁰²² + 3 ulps passes.
     - **Corollary, for exactly representable f only:** for e ≥ −969, 3 ulps passes iff f ≥ 1.5·2ᵉ. Below that, ν admits more.
     - **Withdrawn:** r2/I-33's "3 ulps passes iff f > 1.5·2ᵉ" was wrong at equality and near underflow.
     - **Starting error:** when the exact f is not binary64 (the usual case), "fl(f) + k ulps" is not a displacement of k·ulp(f). sin(1) + 3 nextafter steps lies 2.984·ulp(f) from sin 1. That is 1.77 × 2⁻⁵² relative, against UF = 2 × 2⁻⁵²: inside, since 2.984 ≤ A = 3.366.
     - **Expected outcomes** therefore always come from the exact inequality, never from an ulp count. The checker, UF, ν and the 32 controls are unchanged (`i34a_minor.out`: closed form = checker at 36 855/36 855 displacements).
   - DL-1 returns an enclosure [lo, hi] of f. The decision uses convexity, so it is exact over the whole enclosure:
     - **PASS** iff the inequality holds at both ends of the enclosure;
     - **FAIL** iff it is violated at every point of the enclosure;
     - otherwise **INCONCLUSIVE**, which counts as PREMISE-NOT-OBSERVED.
   - No δ is added to any tolerance.
   - **Width requirement:** a relative width of at most 2⁻³²⁰, or an exact value.
   - **Exact zeros** come only from identities in DQ-1's call domain: hypot(0, 0), atan2(±0, x > 0) and sin(±0). They are returned exactly.
   - Every other exact value is provably nonzero there, and its enclosure excludes 0. So no impossible absolute precision is ever required: below the subnormal range, ν dominates.
   - The old requirement "δ ≤ 2⁻¹⁰⁰·|r|, so that the check is never the limiting factor" is withdrawn. It cannot hold at r = 0, and a straddling enclosure can always occur. INCONCLUSIVE handles that case.
2. **Exact arguments.** The arguments and results are the binary64 values **the twin consumed**. They are converted exactly (`Fraction` from float) and never re-rounded.
3. **`sqrt` and the arithmetic** *(F6)*.
   - Every sqrt result the twin consumes is checked for **exact correct rounding**: √a must lie in r's rounding cell, between the midpoints with each neighbour (whose spacings differ at a binade boundary), ties to even. The test compares a with the squared midpoints in exact rationals.
   - The I-31 probe's predicate, |r − √a| ≤ ulp(r)/2, accepts the wrong result sqrt(nextdown(1)) → 1.0 and must not be used. The exact test rejects it (`f6_sqrt.out`).
   - +, −, × and ÷ are covered by A-FP-1 (IEEE 754), checked by the X-P4 run-time probes, and are **not** observed per operation. This is the one E1 hypothesis taken as an accepted assumption rather than observed (DL1-DL2 draft §4, H3).
4. **Witness completeness** *(F1)*.
   - The twin makes every elementary call through the DL-3 library object, which returns the result object unchanged.
   - The harness asserts that the recorded call list equals the list DQ-1 implies for the twin's iteration count it: hypot, atan2, it × (sin, sqrt, atan2), sin, cos, sqrt.
   - A **fault-injection self-test** perturbs one call index at a time by a definite violation (2⁻³⁰ relative, or 2⁻¹⁰⁰⁰ for an exact zero), and requires PREMISE-NOT-OBSERVED for each index.
   - A twin mutant that calls one function directly is killed by the call-list assertion.
   - The component is not traced for any conclusion.
5. **Domain** *(observation B)*.
   - E1 applies only at true height ≥ 0, which is certified by O-2's lower end L ≥ 0. Points that are not certified are reported (P8).
   - E1 also needs **no overflow** ("Supported domain: points outside the ellipsoid, no overflow", `t0_termination.py`; "every overflow is outside the domain", DR-0029). Finite inputs do not imply finite results: (DBL_MAX, DBL_MAX, 0) overflows in `hypot`, and (DBL_MAX, 0, DBL_MAX) overflows in p·c + z·s; T0 returns h = ∞ for both.
   - The twin therefore requires every arithmetic and library intermediate to be finite. Otherwise the result is **OUT-OF-DOMAIN**: reported, and no bound applied.
   - A sufficient condition is max(|x|, |y|, |z|) ≤ 2¹⁰²⁰. It is drafted in `observations.out` B, where the box corners give finite intermediates (largest 2^1020.79). This condition is the **twin's** domain, not DL-2's coverage: the draft DL-2 raises inside it (§2.2 DL-2; I-34A, R2-F3).
   - Production behaviour on such inputs is unchanged by this packet: DQ-1's arithmetic, then DQ-2's distinct non-finite-height error (P4). No accuracy claim is made there.
6. **Reference and comparison semantics** *(observation A)*.
   - **Exact-answer points** (P8 (a)) use their exact reference.
   - **Forward-constructed points** (P8 (a′)) use **O-2's enclosure [L, U] of the true height of the binary64 point actually produced** (D-7). Using O-2 removes the need for the δ_f term: strategy B-4 names "an oracle with a stated error" as its alternative.
   - **Every gate enforces strict E1.** That is |ĥ − h| ≤ α·h + β for every h in [L, U], decided by convexity:
     - **PASS** iff it holds at both L and U;
     - **FAIL** iff it fails on all of [L, U];
     - otherwise **INCONCLUSIVE**, which fails closed.
   - **No oracle term is added to the tolerance.** r2's rule "|ĥ − h_O| ≤ ε_h(h_O + δ_O) + δ_O" is withdrawn: it admits outputs that violate E1 at the true height by up to 2(1 + α)·δ_O. With δ_O = 1e-6·β, 80 binary64 outputs near 1 m are admitted by it and INCONCLUSIVE under the strict rule (`observations.out` A).
   - The DL-2 draft's widths (at most 2.8e-92 m (measured 2.72e-92)) make the INCONCLUSIVE band negligible in practice.
   - Changing P8's (a′) condition from "δ_f derived" to "O-2 with a derived error bound" is an owner decision (**D-7**).
   - **If O-2's bound cannot be established in review, the forward-constructed rows stay BLOCKED (report-only).** The alternatives for the owner are in §14, D-7.
7. **Exact coefficients** *(observation D)*.
   - The gate uses α and β as the exact `Fraction`s returned by `t0_termination.rounding_allowances()`. The 4 102-bit denominator of α is not shortened.
   - Displayed decimals (1.221e-15, 8.878e-9 m) are for presentation only.
   - Rounding β up to 8.9e-9 m would loosen ε_h by 2.2e-11 m at 120 km and admit errors that E1 does not bound (`observations.out` D).

### 6.5 A-LM-1, split by a source argument (PROPOSED, D-3)
Source [S]: CPython v3.12.15 `Modules/mathmodule.c`, sha256 `436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281`, `math_hypot` and `vector_norm`.

- **Evenness: an exact source argument.** `math_hypot` replaces every argument with `fabs(x)` before anything else. `hypot(±x, ±y)` therefore calls `vector_norm` with a bit-identical coordinate array, and returns bit-identical results. This needs no accuracy assumption. It gives a **new unconditional exact row, U-19 (a′)**: ĥ is unchanged under the half-turn (x, y) → (−x, −y) about +Z and under the reflections x → −x and y → −y, because DQ-1 sees x and y only through p = hypot(x, y). The argument is valid for the reviewed patch version only (DL-7, §7 RQ-4). *(I-33, F4: and for a reviewed build of it. The `fabs` normalization is in the source, but the claim is about the compiled artefact.)*
- **Symmetry under swapping arguments: not provable from the source.** For n = 2 the loop forms csum = fl(fl(1 + x²_hi) + y²_hi), which depends on the order. The maintainers claim faithful rounding and an empirical commutativity test, not a proof.
  - Probe [P]: 0 swap mismatches and 0 negation mismatches in 2 × 10⁶ pairs. That is a sample, not a proof.
  - **Exact quarter-turn equality, U-19 (a), therefore stays conditional on A-LM-1 (symmetry part).** It may be POG-gated (the premise hypot(x, y) = hypot(y, x), observed at each gated point; D-4), or it stays report-only.
- J-LM1 in r1 asked for both properties from the source. This packet supplies evenness only.

### 6.6 A-LM-2 (PM-4 (a), non-increasing density in a band)
- **J-LM2 is not met:**
  - no documented monotonicity for either platform's `exp` [S: the glibc manual states no such property];
  - correct rounding is not available (S2);
  - an exhaustive check over the band-exponent range is infeasible (about 2⁶² binary64 values) [R].
- **Recommendation (D-4): POG with premise A-LM-2 at the witnessed `exp` arguments.** For each gated pair (h₁ < h₂, same band):
  - the DQ-2 twin's two `exp` calls satisfy x₁ ≥ x₂ ⇒ exp(x₁) ≥ exp(x₂);
  - the component's ρ̂(h₁) and ρ̂(h₂) equal the twin's bitwise.

  The gate then asserts ρ̂(h₁) ≥ ρ̂(h₂) through B-10. This is a **local, pairwise** conclusion: it is not monotonicity over an interval, and it says nothing about correct density values.
- *(Corrected under I-33, F3.)* **Withdrawn claim.** Packet r2 said here that a defect in band selection, exponent sign, grouping or km conversion "breaks the conclusion while the premise holds". That is false. Non-increase survives every defect that keeps the exponent a decreasing function of h inside a band.
- **The I-33 kill matrix** [P] (`f3_density.out`; 13 mutants against the T0 spike's km-route density, which equals DQ-2 for h ≥ 0). PM-4 (a) kills **only the flipped exponent sign**. Its survivors include:
  - the Review 01 doubled scale height, and a halved one;
  - ρ₀ × (1 + 1e-6);
  - a 1 m base offset;
  - h·0.001 in place of h/1000;
  - the metre route;
  - an exact base assigned to the band below;
  - the next band's parameters;
  - no top-band extrapolation;
  - a regrouping exp(−h/H + base/H);
  - a tampered table file.
- **The discriminating gates, each with its defect class and its blind spots** [P]:

  | Gate | Detects | Blind spots (I-33 survivors) | Status |
  |---|---|---|---|
  | U-11 digest before parsing (DR-0027 B-1) | Any change to the table file | Every code defect in how the values are used | Unconditional (E) |
  | U-12 (a), ρ̂(base) = ρ₀ exactly at the 27 bases and at 0 m | Wrong ρ₀, base offset, an exact base assigned to the band below, the next band's parameters, tampered values | Scale-height, conversion, grouping, sign and top-band defects: the exponent is exactly 0 at a base | Unconditional (E; A-LM-0) |
  | U-12 (b), band selection at base ± 1 ulp against the test-side formula of each band (bitwise) | Every formula defect visible at those 54 points (here all except two) | The rule for an **exact** base (caught by U-12 (a)); the bit-identical regrouping. It is a narrow conformance check | Unconditional (E) |
  | PM-4 (a), non-increase in a band | Exponent-sign defects only | Every order-preserving defect above | POG-conditional (A-LM-2); **supplementary invariant only** |
  | U-13, ρ̂ ≤ E3 upper enclosure | Outputs above E3's km-route enclosure at some sample: here the defects that raise density (doubled scale height, ρ₀ high, base offset, next band, sign, no top extrapolation, tampered value), **and** numerically different rewrites (metre route, exp(−h/H + base/H)), since E3 is specific to the km-route sequence | Every defect that **lowers** density (halved scale height, h·0.001, an exact base in the band below): E3 is one-sided | POG-conditional (A-FP-2) |
  | U-15, the 1000 km discontinuity and top-band values | Top-band and 1000 km boundary defects, and global defects visible there | Defects confined to bands below 900 km (by construction). I-33 survivors: h·0.001, metre route, tampered table, bit-identical regrouping | Unconditional (E) |
  | **DL-4**, bitwise conformance with the DQ-2 twin at every sample point | **Every** mutant except the regrouping exp((base − h)/H), which is **bitwise identical** to the specified grouping (fl(b − h) = −fl(h − b)) and therefore harmless | A defect that changes no output bit at the sampled points; numerical correctness (F5) | Gate under D-8 |
  | Lower-side value check (two-sided bound) | — | — | **Report-only**: no derived two-sided bound (strategy B-9 (ii)) |

- **Designated killers.**
  - Scale-height, conversion, grouping and band-parameter defects: DL-4 and U-12 (b), with U-13 for the defects that raise density.
  - Dataset defects: U-11 and U-12 (a).
  - Exponent sign: PM-4 (a), U-13 and DL-4.
- **No accuracy claim for density rests on PM-4 (a).**
- **PM-4 (b) (strict decrease) and U-19 (b) (exact z-reflection) stay report-only regardless** (owner policy).

### 6.7 What stays BLOCKED or report-only
- **POG accuracy gating is BLOCKED** *(I-33, §9)* until all of the following are complete:
  - DL-1 and DL-2 derivations reviewed (P-ii);
  - the DL-3 witness harness and the DL-4 twin reviewed: the twin as a faithful transcription of DQ-1/DQ-2, and the harness's completeness self-test;
  - the premise observed on each CI platform (RQ-8);
  - the owner's promotion of each row (P-iii).

  The I-33 drafts (`DL1-DL2-draft-derivations.md`) are **unreviewed research**. The remaining proof obligations are listed in their §5. This BLOCKED state holds even if D-1 is approved: D-1 accepts the route, not the evidence.
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
  - the decimal references used here (T0's `d_sin`, `d_cos`, `d_atan2`) stop when the series sum stops changing and **carry no written error bound**. DL-1 and DL-2 must supply bounded versions. *(I-33: at their default 55 digits, `d_cos` loses relative accuracy near π/2 through cancellation, 7e-49 relative at cos ≈ 6e-17. An unbounded "precision" is not a bound.)*;
  - they used the T0 spike, not T2 code.
- **I-33 evidence** *(added)*: `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/`. It contains:
  - draft bounded oracles (`pog_lib`) and the witness (`witness`), with derivations (`DL1-DL2-draft-derivations.md`, **unreviewed**);
  - the F1, F2, F3, F4 and F6 probes and the observation checks;
  - `SHA256SUMS`.

  Same host and limits; research only.

### 6.9 Error budget (geodetic height, path (α), at true height ≥ 0)
| Term | Value or requirement | Source |
|---|---|---|
| Component evaluation error | ≤ ε_h(h) = αh + β; α and β the **exact** `Fraction`s (displayed: α = 1.2212453270876738e-15, β = 8.877691069434736e-9 m; LIBM_ULP = 2) *(I-33, observation D)* | E1 [S: `t0_termination.rounding_allowances`] |
| Domain | True height ≥ 0 (O-2: L ≥ 0) **and** every intermediate finite (no overflow; §6.4 rule 5) *(I-33, observation B)* | E1 [S] |
| O-2 enclosure width | DELIVERABLE (DL-2). Requirement: (U − L)/2 ≤ 1e-6·β (≈ 9e-15 m). I-33 draft: at most 2.8e-92 m (measured 2.72e-92) on the 633 I-31 points [P, unreviewed] | [R] |
| O-1 enclosure width | DELIVERABLE (DL-1). Requirement: relative width ≤ 2⁻³²⁰, or exact. I-33 draft: at most 1.8e-99 relative [P, unreviewed] | [R] §6.4 rule 1 |
| Gate inequality | **Strict E1**: \|ĥ − h\| ≤ αh + β for every h in [L, U], by convexity; INCONCLUSIVE fails closed. No oracle term in the tolerance *(I-33, observation A)* | §6.4 rule 6 |
| Observed margin (probe, one host) | max \|ĥ − h_true\| = 1.92e-9 m, at h = 145.03 m, where that point's own ε_h is 8.8779e-9 m: **0.216247**, compared point by point. **An empirical maximum, not a bound** | [P] I-31; reproduced by Review 01 and I-33 |
| Not budgeted here | The model ellipsoid vs WGS 84 b (+1.71e-12 m, reported separately per U-17); P6's 0.14–0.38 m GMAT residual (T5, ESCALATED) | Strategy U-17; DR-0029 P6 |

## 7. Platform floating-point reproducibility requirements
| ID | Requirement | Gate? |
|---|---|---|
| RQ-1 | Same-platform bitwise repetition of every T2 output (X-P1) | Gate (E) |
| RQ-2 | Constant literals and derived constants (f, e², ω_E, J2 identity) bit-identical on the three CI platforms (X-P2) | Gate (E) |
| RQ-3 | **No cross-platform bitwise expectation** for any output that depends on `exp`, `sin`, `cos`, `atan2` or `hypot`. Cross-platform differences are measured in ulps (X-P3) and reported. No tolerance is borrowed (DR-0025 §7; ADR-0008 TL-7 by analogy) | Report |
| RQ-4 | **Environment record** (DL-5, §7.1) with all gate evidence. *(Corrected under I-33, F4.)* The source-dependent claims are of two kinds, and the record serves them differently:<br>(a) **Source arguments** (U-19 (a′), DL-7) depend on the CPython source **and** the interpreter build. The patch version is necessary but not sufficient: the same version built with other flags or compilers is a different artefact. They are valid only for a reviewed (patch version, build configuration, executable digest). Any unreviewed value is a stop condition for those rows.<br>(b) **POG rows** do not rest on the environment record. They re-observe their premises on every run (RQ-8), so an environment change cannot invalidate a passing run, though it can make a premise fail (a stop). For these rows the record serves traceability and replay.<br>CI installs the latest 3.12.x (`.python-version` = `3.12`). **D-5** chooses between pinning and recording plus re-checking; this packet recommends recording plus stopping on unreviewed values, with no CI or runtime change | Gate (stop on unreviewed build, for (a)) |
| RQ-5 | A-FP-1 at run time on each platform (X-P4): round-to-nearest-even, gradual underflow, no flush-to-zero | Gate (E) |
| RQ-6 | The DQ-1, DQ-2 and DQ-6 sequences are evaluated in Python `float` scalars and `math` calls, operation for operation. CPython does not contract `a*b + c` into FMA. NumPy is not used for their arithmetic, because a NumPy dot or norm may use FMA or SIMD reordering (A-FP-3) | Gate by inspection. DL-4 checks output conformance only and cannot show that NumPy is absent *(I-34A, R2-F1)* |
| RQ-7 | M1/M2 regression gates stay same-platform (R-1 … R-3), as approved | Gate |
| RQ-8 | POG premises are observed **separately on each CI platform**. A premise failure on any platform for a gated row is a stop condition, never a skip | Gate / stop |

### 7.1 Environment record (DL-5), observable and unobservable *(added under I-33, F4)*
Each field is marked:
- **[O]** observed reliably by a probe in the process;
- **[P]** partly observed, or a proxy;
- **[U]** not observable from the process, and recorded as such, never guessed.
- **Unavailable probes** *(I-35)*. A probe whose command exits non-zero, or returns nothing, is recorded as `[U] unavailable` together with its exit status and diagnostic (stderr). It is never recorded as an observed empty value.
  - Example: in a restricted review sandbox, `sysctl machdep.cpu.brand_string` exits with status 1 and `Operation not permitted` (Review 03 evidence).
  - This is inaccessible metadata, **not** a numerical validation failure.
  - This is a documentation requirement on the record. The I-33 draft probe does not implement it yet (it records `''`), and changing the probe needs separate authorization.

A host run of the draft probe is `f4_fingerprint.out` (macOS x86_64).

| Field | Kind | Note |
|---|---|---|
| Python implementation, `sys.version`, `version_info`, `platform.python_build()`, compiler string | [O] | The patch version alone does not identify the build |
| Interpreter executable sha256; libpython sha256 (shared builds) | [O] / [P] | Identifies the artefact that DL-7's source argument is about |
| Build configuration: `CC`, `CFLAGS`, `OPT`, `CONFIG_ARGS`, `PY_CFLAGS_NODIST` (LTO/PGO), `HOST_GNU_TYPE` | [P] | How CPython was built. It does **not** describe the system libm |
| OS: `platform.platform()`, `uname` (node name redacted), macOS version and build (`sw_vers`), `libc_ver()` | [O] / [P] | `libc_ver()` is empty on macOS |
| libm: Linux `gnu_get_libc_version()` and the `libm.so.6` digest; macOS: libm is in libSystem in the dyld shared cache | [O] / [P] Linux; **[U]** macOS | On macOS the OS build is the only proxy for the libm binary |
| libm variant dispatch: glibc selects FMA/AVX2 variants of `sin`, `cos` and `exp` at load time from CPU features | **[U]** | Not reported to the process. CPU flags are a partial proxy only |
| CPU: machine, brand, feature flags (x86 FMA/AVX2; arm64 FP features) | [O] / [P] | |
| Floating-point configuration: round-to-nearest-even, ties to even, gradual underflow, no flush-to-zero, no FMA contraction in Python arithmetic, `sys.float_info` | [O] | Run-time probes (X-P4 style). They show the configuration, not every operation |
| NumPy version; `uv.lock` sha256 | [O] | NumPy is excluded from the specified sequences (RQ-6) |
| **libm behaviour digest**: sha256 of the bit patterns of `sin`, `cos`, `atan2`, `exp`, `hypot` and `sqrt` on a fixed set of 6 235 arguments (7 410 results) | [O] | The only field that observes results directly, and **only on its own arguments**. It detects a change; it proves nothing about other arguments |

**Limits:**
- **Recording these fields does not establish numerical reproducibility.**
- No field is a substitute for POG's per-run premise observation.
- [U] fields cannot be checked, and the record says so.
- No CI or runtime migration is proposed: pinning or changing runners would need its own authorization (D-5 (a)).

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
- **POG harness** *(corrected under I-33, F2, F6)*. Every expected outcome follows from the numerical inequality, computed by a closed form (pass window [hi(1 − UF) − ν, lo(1 + UF) + ν] for f > 0) that is separate from the decision procedure under test (`f2_premise_controls.out`):
  - **negative controls (must FAIL):**
    - a perturbation proved outside A-FP-2, for example sin(x) with sin x = 0.5(1 + 1.7e-12), at the bottom of its binade, plus 3 ulps (3.16 units of 2⁻⁵²);
    - sin(1) + 5 ulps (allowance 3.37 ulps);
    - exp(−ln 2 + 1e-9) + 3 ulps;
  - **positive control (must PASS):** sin(1) + 3 ulps (1.77 × 2⁻⁵² relative, against UF = 2 × 2⁻⁵²: inside A-FP-2; §6.4 rule 1, I-34A). The r2 control "3 ulp off must be reported" is **withdrawn**, because it would have rejected a correct checker;
  - **boundary pairs:** for sin, cos, atan2 and exp, the largest and the smallest passing double must PASS, and the next double outward must FAIL;
  - **subnormal regime:** exp(−744) ± 1 or 2 subnormal ulps. The absolute term ν decides: −2 and ±1 PASS, +2 and +3 FAIL;
  - **oracle uncertainty:** an enclosure straddling the window edge must give INCONCLUSIVE, which is treated as PREMISE-NOT-OBSERVED;
  - **exact identities:** sin(+0) → 2⁻¹⁰⁷⁴ PASS and → 3·2⁻¹⁰⁷⁴ FAIL; exp(0) → 1 + 2⁻⁵² PASS and → 1 + 3·2⁻⁵² FAIL;
  - **sqrt** (F6): sqrt(nextdown(1)) → 1.0 must be rejected and nextdown(1) accepted. For every tested argument (powers of two and their neighbours across the whole range, plus random arguments), exactly one of r and its two neighbours on each side is accepted;
  - **fault injection at every call index** of the twin (§6.4 rule 4).
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
  - *(I-33)* Over the 633 I-31 points:
    - truncation after 2 iterations is nonconformant at 566 points;
    - a 1e-9 stopping tolerance is nonconformant at 575 points;
    - at the remaining points their outputs are bit-identical to the correct component, so passing there is harmless (`pog_pipeline.out`).
- **POG harness mutants** *(corrected under I-33, F1, F2)*:
  - premise check disabled, or always true: killed by the constructed negative controls (§8.2), not by a 3-ulp perturbation;
  - premise check too strict (for example a fixed 2-ulp rule): killed by the sin(1) + 3 ulps positive control and the boundary pairs;
  - one twin call not routed through the library object: killed by the call-list assertion and by per-index fault injection (§6.4 rule 4);
  - a component that binds `sin` at import, calls NumPy, discards a result or replaces a value after a call: **not a harness defect**. The witness decides on the component's output bits, so either it is SEQUENCE-NONCONFORMANT or its pass is sound (§6.3, I-33 results);
  - oracle enclosure ignored (the midpoint used as exact): killed by the straddle test;
  - INCONCLUSIVE treated as PASS: killed by the straddle test;
  - PREMISE-NOT-OBSERVED downgraded to a skip: killed by a test that asserts the run fails;
  - the outer comparison rule in place of strict E1: killed by the observation A construction (`observations.out`);
  - rounded α or β in place of the exact Fractions: killed by a test asserting the gate's coefficients equal `rounding_allowances()` exactly.
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
- **G-T2-10 (new):** DL-4 bitwise conformance passes on each CI platform, for both h and φ. DL-5 records are made (§7.1). DL-7 matches every platform's reviewed (patch version, build configuration, executable digest) *(I-33, F4)*. **G-T2-10 is a sequence-conformance gate. It is not, and does not stand in for, an accuracy gate** *(I-33, F5)*.
- **G-T2-11 (new):** the POG harness mutants (§8.3) are killed, and the §8.2 controls give their derived outcomes.
- **Review content:**
  - the T2 review prompt quotes I-26 §4–§5, I-30 §4 and the approved §14 decisions verbatim;
  - it checks that no conditional row is presented as a gate unless promoted;
  - it checks that no POG record claims production accuracy.
- **Stop rules as before:** REQUEST_CHANGES → record, reproduce and disposition each finding; no fix and no new round without authorization. PASS → acceptance dossier; no acceptance or merge without explicit decisions.

## 11. Stop conditions (in addition to r1 §8)
1. **Premise not observed:** PREMISE-NOT-OBSERVED on any gated input on any CI platform. Record it, and do not drop the point or re-sample.
2. **Oracle derivations:** the DL-1 or DL-2 derivation cannot meet its §6.9 requirement, or does not pass review. The dependent rows stay report-only; never substitute a sampled reference.
3. **Witness** *(corrected under I-33, F1)*:
   - the twin cannot be reviewed as a faithful transcription of DQ-1/DQ-2;
   - or the harness's completeness self-test (call list, per-index fault injection) fails;
   - or the component is SEQUENCE-NONCONFORMANT at a gated point on a platform.

   POG accuracy gating then stays BLOCKED for the affected rows.
4. **Platform drift** *(corrected under I-33, F4)*: a CI platform's CPython patch version, build configuration or executable digest differs from the one DL-7 reviewed. This stops the source-argument rows only (U-19 (a′)), unless D-5 chose pinning and the pin holds.
5. **Sequence conformance:** DL-4 shows that the component cannot reproduce the DQ-1 or DQ-2 sequence bitwise on a platform. Stop; do not substitute an equivalent expression (r1 §8).
6. **Scope:** T2 appears to need a tolerance, a threshold, a T3/T4/T5 item, P6/X-1 work, a dependency change (S2), or a protected-path change.
7. **Scientific dependency:** any T2 gate would come to depend on A-FP-2, A-LM-1 (symmetry) or A-LM-2 beyond the POG-observed inputs.
8. **Strict E1 and domain** *(added under I-33, observations A and B)*:
   - a gated point gives E1-FAIL, which would contradict E1 or an oracle: stop and investigate;
   - or a gated point gives E1-INCONCLUSIVE, OUT-OF-DOMAIN (a non-finite intermediate) or NOT-CERTIFIED-EXTERIOR: record it, and do not drop the point.

   Points outside E1's domain are classified when the gated list is fixed, before any run, and are reported, as P8 requires for negative heights. A listed point that falls outside the domain at run time is a stop, never a skip.

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
   - *(Qualified under I-33, observation E.)* Pinning one software libm **removes one source** of cross-platform difference (RES-0001 §6 layer 2). It does not by itself give bit-identical results:
     - the same source can compile differently for different target architectures, compilers, flags and optimisation levels;
     - FMA contraction, vectorisation and fast-math settings can change results;
     - the arithmetic configuration (rounding mode, subnormal handling) must match.

     Bitwise portability would have to be established for a pinned (source, toolchain, flags, target) tuple, and observed. It gives no accuracy guarantee. The POG **principle** (observe the premise on the values actually consumed) would carry over; its present implementation, in Python with `fractions`, would not;
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
| **D-1** *(revised under I-33, F1)* | Accept **Premise-Observed Gating by witnessed evaluation** (§6.3–§6.4) as a route to P-i (J-FP2 (ii) over the gated finite domain) for the A-FP-2 rows. That means: the premise observed on every value an independently written twin consumes; the component's output equal to the twin's bitwise; strict E1. It explicitly does **not** justify A-FP-2 for production inputs. **No row is promoted, and the gate stays BLOCKED until DL-1 … DL-4 are reviewed** (§6.7) | **Approve the route** | A-FP-2 rows stay report-only; geodetic accuracy acceptance **BLOCKED** (§6.7) |
| D-2 *(revised under I-33)* | Accept DL-1 … DL-7 as T2 deliverables, as corrected: DL-3 is the witness harness (it no longer traces the component); DL-5 is the expanded environment record. Each is reviewed before it supports a gate. The I-33 drafts of DL-1, DL-2 and DL-3 are research inputs, not deliverables | Approve with D-1 | Without DL-1 … DL-4, POG cannot run |
| D-3 | Accept the CPython 3.12.15 source argument for `hypot` **evenness** (J-LM1-even), giving unconditional row U-19 (a′); quarter-turn symmetry stays conditional. *(I-33, F4: valid for a reviewed (patch version, build configuration, executable digest), RQ-4 (a).)* | Approve | U-19 (a′) is not added; U-19 (a) stays report-only |
| D-4 *(revised under I-33, F3)* | Allow POG (witnessed) for the A-LM-1 symmetry premise (U-19 (a)) and the A-LM-2 premise (PM-4 (a)). **PM-4 (a) is a supplementary invariant**: it detects exponent-sign defects only (§6.6 kill matrix). Density defects are assigned to U-11, U-12 (a)/(b), U-13, U-15 and DL-4, each with its stated blind spots | Approve, with the §6.6 assignment | Both stay report-only; the §6.6 unconditional gates and DL-4 (if D-8) still apply |
| D-5 *(revised under I-33, F4)* | CPython environment: (a) pin `.python-version` to an exact 3.12.x, or (b) record the §7.1 environment on every run and stop the source-argument rows on any unreviewed (patch version, build configuration, executable digest) | (b): no CI or runtime change. (a) is a wider change affecting M1/M2 environments, and would itself need authorization. Neither proves numerical reproducibility; POG rows re-observe their premises every run | — |
| D-6 *(revised under I-33, F1)* | Testability requirements in §3: (ii) v_rel observable; (iii) no NumPy in the specified sequences (a conformance requirement). Item (i), module-attribute `math` calls, is withdrawn because no conclusion rests on tracing the component | Approve (ii) and (iii) | v_rel unobservable (U-4 by recomputation only); RQ-6 enforced by DL-4 alone |
| D-7 *(revised under I-33, observation A)* | P8 (a′): gate forward-constructed points against **O-2's enclosure of the true height of the binary64 point** (DL-2), under **strict E1** (§6.4 rule 6), instead of deriving δ_f | Approve, subject to DL-2's review. If DL-2's bound cannot be established, the alternatives are:<br>(a) derive δ_f (strategy B-4);<br>(b) keep U-18 report-only.<br>Both are owner choices | U-18 stays report-only until δ_f is derived |
| D-8 *(clarified under I-33, F5)* | Make DL-4 (bitwise conformance with the DQ-1/DQ-2 sequences, same platform, both h and φ) a **gate** under G-T2-10. Today X-D1 (bitwise vs the T0 spike) is reported only. It is a **sequence-conformance** gate, never an accuracy gate | Approve: it is the only killer of height-equivalent latitude mutants (§8.3), the main killer of density formula defects (§6.6), and the witness link of POG (§6.3) | Those mutants survive; DQ-1 conformance rests on inspection alone; POG cannot run |

**Reading note (I-34A, R2-F1; no decision is changed).** D-6 calls item (iii) "a conformance requirement", and its "if not approved" column says "RQ-6 enforced by DL-4 alone". Read both as corrected in §3 (iii) and §7 RQ-6:
- item (iii) is verified by source inspection;
- DL-4 shows output conformance only;
- RQ-6 is not enforced by DL-4 in any case.

"Sequence conformance" in D-8 has the meaning defined in §2.2 DL-4. Each decision's proposal and recommendation are unchanged, and D-0 … D-8 remain PROPOSED.

**Owner decisions (2026-10-27, append-only): recorded under I-37 in §17.** The table and reading note above are preserved as proposed.

## 15. What the T2 authorization itself would need to state
1. The base: a named `main` SHA (at least `0a9c040`), re-verified at T2 start (PC-6).
2. That T2 implements r1 §2 within r1 §3–§4, under the DQ-1 … DQ-6 decisions, with the §3 interfaces.
3. Which of D-0 … D-8 are approved, quoted verbatim.
4. That every conditional row is reported unless promoted at acceptance through the approved route (P-i … P-iii).
5. The §10 gates, the §11 stop conditions and r1 §8.
6. That T3, T4 and T5 remain NOT AUTHORIZED, as do P6, P6(b), X-1, thresholds and any dependency change.

## 16. I-33 correction map
The reviewed text is preserved at `0e37db6`. The dispositions are in `docs/reviews/M3-T2-packet-r2-review-01-corrections.md`.

| Review 01 item | Where corrected |
|---|---|
| F1 (MAJOR) trace-to-computation | §2.2 DL-3, DL-4; §3 testability (i) withdrawn; §6.2 S5; §6.3 (witnessed evaluation; I-33 adversarial results); §6.4 rule 4; §8.3; §11 item 3; §14 D-1, D-2, D-6 |
| F2 (MAJOR) negative controls | §6.4 rule 1; §8.2 POG harness; §8.3 |
| F3 (MAJOR) density and D-4 | §6.6 (withdrawn claim; kill matrix; gate table; designated killers); §14 D-4 |
| F4 (MINOR) environment | §2.2 DL-5, DL-7; §7 RQ-4; §7.1; §10 G-T2-10; §11 item 4; §14 D-3, D-5 |
| F5 (NOTE) conformance ≠ correctness | §2.2 DL-4; §6.3 ("What POG does not justify"); §10 G-T2-10; §14 D-8 |
| F6 (MINOR) sqrt boundary | §6.4 rule 3; §8.2 |
| Observation A, comparison semantics | §6.4 rule 6; §6.9; §11 item 8; §14 D-7 |
| Observation B, overflow | §6.4 rule 5; §6.9; §11 item 8 |
| Observation C, oracle zeros | §6.4 rule 1; §2.2 DL-1 |
| Observation D, coefficients | §6.4 rule 7; §6.9 |
| Observation E, Rust portability | §13 item 2 |
| I-33 §9, DL-1/DL-2 derivations | §6.7 (BLOCKED until reviewed); drafts in the I-33 evidence, `DL1-DL2-draft-derivations.md` (unreviewed) |

**Unchanged:**
- scope (§2.1);
- paths (§4);
- traceability (§5);
- RQ-1 … RQ-3 and RQ-5 … RQ-8;
- exclusions (§12);
- §15;
- every owner decision: DR-0024 … DR-0029, DQ-1 … DQ-6, P1–P5 and P7–P9 DECIDED, P6 NOT FULLY DECIDED, P6(b) OPEN, X-1 NOT AUTHORIZED.

D-0 … D-8 remain **PROPOSED**.

### 16.1 I-34A correction map (Review 02 MINOR findings)
The Review 02 text is preserved at `5f96119`. The record is `docs/reviews/M3-T2-packet-r2-review-02-corrections.md`.

| Review 02 item | Where corrected |
|---|---|
| M3T2P2-R2-F1 (MINOR) DL-4 enforcement overclaim | §2.2 DL-4; §3 testability (iii); §6.3 ("What POG does not justify", F5 item); §7 RQ-6; reading note after the §14 table (D-6, D-8 rows unchanged) |
| M3T2P2-R2-F2 (MINOR) 3-ulp rule | §6.4 rule 1 (ulp metric, exact allowance, corollary, starting error); §8.2 positive control |
| M3T2P2-R2-F3 (MINOR) DL-2 admissibility | §2.2 DL-2; §6.4 rule 5 |
| M3T2P2-R2-F4 (NOTE) fingerprint fields | Investigated only; a correction is proposed in the record and **not applied** (I-34A §3) |

**Unchanged by I-34A:**
- every threshold, constant and control;
- every DL acceptance requirement. None is loosened. DL-2 records one added review obligation (R2-F3), as Review 02 recommended;
- D-0 … D-8;
- the readiness findings M3T2R-R2-F1 … F3 (closed under I-25) and the Readiness Review 03 conclusions;
- the I-33 evidence and the Review 01 and Review 02 records.

### 16.2 I-35 correction map (Review 03 findings)
| Item | Where corrected |
|---|---|
| M3T2P2-R3-F1 (MINOR) fingerprint field count | `docs/reviews/M3-T2-packet-r2-review-02-corrections.md` §2 item 1 |
| M3T2P2-R3-F2 (NOTE) a² + t notation | the same record, §1 R2-F3 row |
| Fingerprint reporting (`[U] unavailable`) | §7.1 (rule); the same record, §2 (observed cause and representation) |

The packet is otherwise unchanged by I-35.

## 17. Owner decisions (2026-10-27, append-only): I-37
- **Authority:** "I-37 — M3 T2 Owner Decision Recording" (owner/Tech Lead, 2026-10-27). Baseline `42fc823afdd81c0e6d876e482e948b2428e7c064`, CI run 40536225099 green on 4/4 jobs, no recorded finding open.
- **Owner confirmation:** I-37 was issued as "PROPOSED — awaiting owner confirmation". The owner confirmed it explicitly on 2026-10-27 ("Confirmed, record them": record I-37 §2 and §3 exactly as written).
- **Recorded verbatim (I-37 §2):**

  > - D-0: APPROVED.
  > - D-1: APPROVED, conditional POG route only.
  > - D-2: APPROVED, DL-1 through DL-7 required and independently reviewed before gating.
  > - D-3: APPROVED, restricted to reviewed CPython builds.
  > - D-4: APPROVED, with the documented limits of local premises.
  > - D-5: APPROVED, option (b).
  > - D-6 (ii): APPROVED.
  > - D-6 (iii): APPROVED.
  > - D-7: APPROVED, conditional on validated DL-2 enclosures.
  > - D-8: APPROVED, as an output-conformance gate, not an accuracy gate.
  >
  > D-6 item (i) remains withdrawn.

### 17.1 Decision table
Each row maps the owner's decision to the §14 alternative it approves. The §14 text is preserved as written.

| ID | §14 alternative approved | Owner decision (I-37 §2) | Conditions kept |
|---|---|---|---|
| D-0 | The proposal: geodetic accumulation = the error within one geodetic evaluation and its band-selection effect; trajectory accumulation is T4 | **APPROVED** | Trajectory accumulation stays T4 work |
| D-1 | Accept POG by witnessed evaluation as a route to P-i (J-FP2 (ii) over the gated finite domain) for the A-FP-2 rows | **APPROVED, conditional POG route only** | The route only, not the evidence. It does not justify A-FP-2 for production inputs. No row is promoted. Gating stays BLOCKED (§6.7) |
| D-2 | Accept DL-1 … DL-7 as T2 deliverables, as corrected under I-33 | **APPROVED, DL-1 through DL-7 required and independently reviewed before gating** | Each DL is reviewed before it supports a gate. The I-33 drafts are research inputs, not deliverables. DL-2's review covers its supported domain and failure reporting (R2-F3) |
| D-3 | Accept the CPython 3.12.15 `hypot` evenness source argument (J-LM1-even), giving U-19 (a′) | **APPROVED, restricted to reviewed CPython builds** | Valid only for a reviewed (patch version, build configuration, executable digest) (RQ-4 (a), DL-7). Quarter-turn symmetry U-19 (a) stays conditional |
| D-4 | Allow POG (witnessed) for the A-LM-1 symmetry premise (U-19 (a)) and the A-LM-2 premise (PM-4 (a)), with the §6.6 assignment | **APPROVED, with the documented limits of local premises** | Pairwise, local conclusions only: no interval-wide monotonicity or swap theorem. PM-4 (a) is a supplementary invariant (exponent sign only). No density accuracy claim rests on it. PM-4 (b) and U-19 (b) stay report-only |
| D-5 | Option **(b)**: record the §7.1 environment on every run, and stop the source-argument rows on any unreviewed (patch version, build configuration, executable digest) | **APPROVED, option (b)** | Option (a), pinning `.python-version`, is **not** chosen. No CI or runtime change. Recording does not prove numerical reproducibility. Unavailable probes are recorded as `[U] unavailable` (§7.1) |
| D-6 (ii) | The drag component's v_rel is observable to tests, or recomputed by the identical sequence | **APPROVED** | U-4 / B-1 assume the test sees the component's own v_rel |
| D-6 (iii) | The specified sequences use Python `float` scalars and `math`; NumPy is not used for their arithmetic | **APPROVED** | Read as corrected in §3 (iii) and §7 RQ-6 (§14 reading note): an **implementation** requirement verified by operation-by-operation source inspection. DL-4 cannot enforce it |
| D-6 (i) | — | **Remains withdrawn** | No conclusion rests on tracing the component |
| D-7 | Gate P8 (a′) forward-constructed points against O-2's enclosure of the true height of the binary64 point (DL-2), under strict E1, instead of deriving δ_f | **APPROVED, conditional on validated DL-2 enclosures** | No oracle term in the tolerance. U-18 stays report-only until DL-2's bound passes review. If it cannot be established, the §14 fallbacks ((a) derive δ_f; (b) keep U-18 report-only) remain **owner choices, not decided here** |
| D-8 | Make DL-4 (bitwise conformance with the DQ-1/DQ-2 sequences, same platform, both h and φ) a gate under G-T2-10 | **APPROVED, as an output-conformance gate, not an accuracy gate** | "Sequence conformance" means output equality (§2.2 DL-4). It does not establish numerical correctness (F5) or internal implementation (R2-F1) |

### 17.2 Acceptance boundaries (I-37 §3, recorded verbatim)
> 1. No A-FP-2 or A-LM row is automatically promoted.
> 2. POG accuracy gating remains BLOCKED.
> 3. DL-1 through DL-4 remain unreviewed drafts.
> 4. Per-platform testing remains outstanding.
> 5. Numerical thresholds and production numerical sequences remain unchanged.
> 6. D-6 (iii) requires source inspection; DL-4 alone cannot enforce the implementation requirement.
> 7. No CI modifications are authorized.
> 8. No production implementation is authorized.

- **Promotion is still per row (P-iii):** each row needs the reviewed DL deliverables (P-ii), the premise observed on every CI platform (RQ-8) and the owner's explicit promotion at acceptance.
- **Unchanged by I-37:** every threshold and constant; the DQ-1 … DQ-6 sequences; DR-0024 … DR-0029 (P6 NOT FULLY DECIDED, P6(b) OPEN, X-1 NOT AUTHORIZED); the §14 proposal text; every review record and every evidence file.
- **PC-7 (an explicit, separate T2 implementation authorization) remains NONE.** A T2 authorization would quote these decisions verbatim (§15 item 3).

**T2 implementation remains NOT AUTHORIZED.**
