VERDICT: PASS

## 1. Summary

**0 BLOCKER, 0 MAJOR, 3 MINOR, 1 NOTE.**

The corrected packet is suitable for owner decision review. **MINOR findings remain**, listed below.

Witnessed evaluation is scientifically defensible for explicitly recorded finite executions: an output bitwise equal to a premise-satisfying evaluation inherits that evaluation’s error bound. It does not establish the component’s internal operation sequence.

My independent counterexamples found no false E1-PASS. The draft oracles and witness still need the reviews, platform evidence and owner promotions explicitly required by the packet. **DL-1 and DL-2 remain draft research; POG accuracy gating remains BLOCKED.**

These are review recommendations only. No D-decision, assumption or numerical gate is approved. **T2 implementation remains NOT AUTHORIZED.**

## 2. Findings

Locations abbreviated as:

- **Packet:** `docs/milestones/M3-T2-implementation-authorization-packet.md`
- **Evidence:** `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/`

| ID | severity | location (file:line) | finding | evidence | recommended disposition |
|---|---|---|---|---|---|
| M3T2P2-R2-F1 | MINOR | Packet:88, :192 | Some wording still attributes execution-sequence evidence to output equality. DL-4 cannot enforce “no NumPy” or establish which operations produced matching bits. The numerical witness argument itself avoids this mistake. | The preserved evidence explicitly shows a component using `numpy.cos` passing with identical bits. Matching outputs establish value agreement; source inspection remains necessary for implementation conformance. | Describe DL-4 as output conformance with the specified evaluation. Retain operation-by-operation inspection for internal sequence and arithmetic requirements. |
| M3T2P2-R2-F2 | MINOR | Packet:204; Evidence/f2_premise_controls.py.txt:65 | “3 ulps passes iff f > 1.5·2ᵉ” is not an exact general rule. It omits equality, the absolute underflow allowance, and any initial error in the value being shifted. | My `boundaries.out`: exact `f=1.5`, output `f+3 ulps` **PASS**; least-normal `f+3 ulps` also **PASS**, despite `f/2ᵉ=1`. The actual enclosure checker handles both correctly. | Qualify this as intuition away from underflow, accounting for the starting error. Use the stated exact inequality for expected outcomes. |
| M3T2P2-R2-F3 | MINOR | Packet:73; Evidence/pog_lib.py.txt:347–353, :389–397 | “Any foot-point approximation” needs an admissibility qualification. The proposed construction requires a coordinate within the ellipse’s coordinate range. Its fixed Newton budget does not ensure that throughout the finite, non-overflow domain. | At `(2**1020,)*3`, the twin has finite intermediates, but DL-2 raises `ValueError: sqrt of a negative number` while constructing its surface point. This fails closed; it produces no false certificate. | State the draft’s supported range or require an admissible surface-point construction and explicit oracle-failure handling. Keep this in DL-2’s implementation-review obligations. |
| M3T2P2-R2-F4 | NOTE | Evidence/f4_fingerprint.out:59; correction record §2 item 8 | The fingerprint is not byte-identical in this restricted review environment. This does not contradict the claimed earlier rerun in the implementer’s environment. | Only CPU brand/features/leaf7 fields differ: populated in committed output, empty here. All six numerical outputs reproduce exactly. | Preserve this limitation. Unavailable fields should be identified as unavailable rather than treated as an observed empty CPU identity. |

The MINOR findings do not weaken the actual premise or strict-E1 predicates, promote any row, or invalidate the finite-execution witness principle.

## 3. F1–F6 and observations A–E

| Item | Resolution | Independent assessment |
|---|---|---|
| F1: trace-to-computation integrity | **RESOLVED** | The witness removes the need to establish the component’s traced data flow. My hidden-cosine mutant preserves the complete trace, changes height by `64.98137000016868 m`, and is SEQUENCE-NONCONFORMANT under the corrected witness. Twin integrity still requires source review. |
| F2: negative controls | **PARTIALLY RESOLVED** | The checker and concrete controls are corrected. My sin(1)+3-ulp result passes at `1.773082884660813` relative units; +5 ulps fails at `2.9614779904389343`. The explanatory “iff” remains inaccurate—R2-F2. |
| F3: density sensitivity | **RESOLVED** | The universal detection claim is withdrawn. My doubled-scale-height mutant remains decreasing while changing density at 2 km by approximately `14.79%`. The revised gate assignments disclose this blind spot. |
| F4: environment provenance | **RESOLVED** | Build, executable, OS, library and CPU provenance are expanded; unknowns and limitations are acknowledged. Metadata is no longer presented as a reproducibility proof. |
| F5: conformance versus correctness | **PARTIALLY RESOLVED** | Numerical correctness is correctly separated. My shared faulty cosine gives identical component/twin bits, changes height by `55.99864490889013 m`, and is rejected by the premise check. Execution-sequence wording still needs qualification—R2-F1. |
| F6: sqrt boundary | **RESOLVED** | My reproduction confirms that the old predicate accepts `sqrt(nextdown(1)) → 1.0`; the exact rounding-cell test rejects it. Host result is `0x1.fffffffffffffp-1`. |
| A: comparison semantics | **RESOLVED** | Strict E1 is checked over the full enclosure, without added tolerance. INCONCLUSIVE fails closed. The outer comparison rule is explicitly withdrawn. |
| B: overflow | **RESOLVED** | Finite inputs are distinguished from finite intermediates. `(DBL_MAX,DBL_MAX,0)` reports OUT-OF-DOMAIN. R2-F3 concerns oracle coverage inside the non-overflow domain, not an overflow escape. |
| C: oracle zeros | **RESOLVED** | Exact identities return exact zero; zero-crossing uncertainty fails closed. No impossible absolute-precision requirement remains. |
| D: coefficients | **RESOLVED** | The operative coefficients are exact Fractions, independently reproduced below. |
| E: Rust portability | **RESOLVED** | The logical qualification is sound: pinned libm source alone does not establish cross-platform bits. External factual claims remain unverified offline. |

## 4. POG’s scientific defensibility

### Witness argument

The corrected inference is valid under these hypotheses:

1. The twin faithfully evaluates DQ-1 using the specified binary64 constants, grouping, updates and stopping rule.
2. Every relevant elementary result consumed by that twin satisfies its required contract.
3. A-FP-1 holds for the twin’s arithmetic.
4. The input is exterior, and the applicable evaluation has no overflow.
5. E1’s derivation applies to that evaluation.
6. The component’s returned height has exactly the twin’s bits.

E1 bounds the twin’s output value. Bitwise equality transfers that bound to the component’s returned value, regardless of its internal implementation.

Comparing latitude as well as height adds useful conformance discrimination. It does not turn output equality into proof of internal execution.

### E1 and the twin

I compared the twin with r1 §5, `t0_model.py`, and the E1 derivation and coefficients in `t0_termination.py`.

The twin preserves:

- binary64 `a` and `e²`;
- initial `atan2(z,p*(1-e²))`;
- left-associated `e²*s*s` and `e²*n*s`;
- at most 60 updates;
- the stopping comparison after computing the update;
- final `p*c + z*s - a*sqrt(...)` grouping.

E1’s support-function stationarity argument, contraction argument, stopping allowance, arithmetic rounding terms and mixed underflow terms address this sequence. The checked square-root contract is sufficient for the square-root assumption. Aggregate `hypot` checking is appropriate: E1 needs its mathematical contract, not observations of its C-internal operations.

**Arithmetic remains assumed.** The witness does not observe correctness of every `+`, `−`, `×` or `÷`. Runtime probes provide limited environmental checks, not exhaustive arithmetic certification. E1’s correctness also remains a reviewed mathematical dependency.

### Completeness and self-tests

The call-list assertion and per-index injection are useful regression controls. The supplied evidence reproduces detection at **31/31 indices** across its two selected executions.

They are not a general proof of twin data flow. A twin could record expected calls while consuming hidden substitutes. Therefore the independent source review required by §6.7 is essential. With that review retained, the strategy is defensible.

### Premise and strict-E1 decisions

For a fixed-sign enclosure,

\[
g(f)=|\hat f-f|-UF|f|-\nu
\]

is convex and piecewise linear. Its maximum occurs at an endpoint; its minimum occurs at an endpoint or at `f= f̂`. The implementation uses these facts correctly.

The strict-E1 predicate uses the corresponding argument for

\[
g(h)=|\hat h-h|-\alpha h-\beta.
\]

Signed values, exact zero, subnormal allowances and boundary uncertainty are handled conservatively. Zero-crossing premise enclosures return INCONCLUSIVE. Negative lower height bounds prevent exterior certification.

No tested refusal, uncertainty or oracle exception produced E1-PASS.

### Draft DL-1 and DL-2 mathematics

My inspection supports the enclosure constructions within their stated operational domains:

- Rational square-root bounds follow from integer-square inequalities.
- Directed fixed-point term recurrences preserve lower and upper bounds.
- Alternating-series remainders are valid once the remaining terms decrease.
- Positive-series tails have valid geometric majorants.
- Positive interval squaring and reciprocal operations preserve exp enclosures.
- Euler’s arctangent series can independently be established by its recurrence and differential identity, with zero initial value.
- Machin’s identity is consistent with tangent addition and the principal-angle ranges.
- The ellipsoid support function supplies a lower distance bound.
- Distance to an exactly on-surface point supplies an upper bound.
- A nonnegative certified support separation establishes exterior membership.

I found no enclosure-containment counterexample. My additional independent Decimal Taylor/exp cross-checks passed **200 comparisons**. Those cross-checks are corroboration, not rigorous reference proofs.

DL-2’s approximate Newton result need not converge to make a valid bound **provided the subsequent construction produces an admissible surface point and nonzero support direction**. R2-F3 identifies the missing operational qualification.

## 5. Remaining unproved assumptions and obligations

- A-FP-1 for every arithmetic operation, including rounding mode and gradual underflow.
- Correct interpreter execution, exact rational/integer infrastructure, and absence of interference with the harness.
- Complete source review of the twin, library routing, iteration and stopping behavior.
- Complete implementation review of DL-1/DL-2 against their mathematical bounds and refusal paths.
- E1’s mathematical derivation and its applicability to every gated execution.
- DL-2 coverage and explicit failure handling for the fixed gated domain.
- Required authoritative citations for the draft derivations.
- Separate observations on all three CI platforms.
- Reviewed build/source correspondence for DL-7.
- Required derivations for other conditional and deliverable rows, including density/drag conclusions where applicable.
- Explicit owner approval of the proposed route and subsequent promotion of individual rows.

Universal production-input A-FP-2, A-LM-1 and A-LM-2 remain unjustified. POG does not discharge them.

## 6. D-0 … D-8 recommendations

“APPROVE” below is a recommendation for owner consideration, **not an approval**.

| Decision | Recommendation | Justification | Required evidence | Dependencies | Consequences of approval | Remaining blocker |
|---|---|---|---|---|---|---|
| D-0 | APPROVE | Correctly separates evaluation error from trajectory accumulation. | E1/E2 scope traceability. | T4 exclusion. | Defines the requested analysis scope. | None for this scope recommendation. |
| D-1 | APPROVE | Witnessed evaluation is a valid finite-execution route. | Reviewed twin, harness, bounded oracles and hypothesis inventory; platform records. | A-FP-1, E1, D-2, output agreement; D-7 where applicable. | Accepts a route to P-i only. | DL reviews, platform evidence and owner promotion. |
| D-2 | APPROVE | Deliverables address the necessary scientific and evidence work. | Independent DL-1…DL-7 reviews, including R2-F3. | D-1; applicable source and environment requirements. | Makes this future test/evidence work explicit. | Drafts are not completed accepted deliverables. |
| D-3 | APPROVE | Supplied source supports sign-evenness for the reviewed build. | Source/build correspondence and guard-equivariance evidence. | DL-5, DL-7, D-5; specified DQ-1 evaluation. | Adds sign-reflection/half-turn row only. | No swap theorem; platform builds still require review. |
| D-4 | APPROVE | Local symmetry/order premises support local conclusions; density blind spots are disclosed. | Pairwise witness checks, same-band preprocessing, reviewed B-10/B-11 and discriminating density checks. | D-1/D-2; D-3 for source-evenness part. | Allows local supplementary metamorphic gates after promotion. | No interval-wide theorem or current promotion. |
| D-5 | APPROVE option (b) | Recording plus stopping is appropriate without migration. | Available provenance, explicit unknowns and build invalidation records. | DL-5/DL-7; RQ-8. | Stops source-dependent rows on unreviewed builds. | Actual reviewed platform fingerprints. |
| D-6 | APPROVE (ii), (iii) | Test visibility and prescribed scalar arithmetic are reasonable requirements. | Source inspection for arithmetic implementation; observable/recomputed `v_rel`. | DQ-1/DQ-2/DQ-6; RQ-6. | Establishes future testability and implementation requirements. | DL-4 alone cannot enforce internal implementation—R2-F1. |
| D-7 | APPROVE | Bounding the actual rounded point avoids an unsupported forward-construction error term. | Reviewed O-2 enclosure and exterior certificate; strict-E1 predicate. | D-1/DL-2; P-ii/P-iii. | Opens the proposed alternative for U-18. | DL-2 validation and promotion remain pending. |
| D-8 | APPROVE | Output conformance provides useful mutation discrimination and the witness link. | Both returned quantities, independent twin review, fixed mutant-killing inputs and platform runs. | DQ-1/DQ-2; D-1 for POG use. | Adds an output-conformance gate. | Actual reviewed implementation and platform evidence; source inspection remains separate. |

## 7. Contradictions and scope

The internal wording contradictions are R2-F1 and R2-F2. R2-F3 qualifies an overbroad draft-oracle description.

I found no new owner-decision or scope contradiction:

- The correction diff contains only the packet, correction record and research evidence under `docs/`.
- Decision records, T0 code, production code, tests, protected paths and dependency files are unchanged.
- D-0…D-8 remain proposed.
- P6/P6(b) remain unresolved and X-1 unauthorized.
- T3/T4/T5 remain excluded.
- Exact z-reflection and strict density decrease remain report-only.
- Implementation completion remains separate from scientific accuracy acceptance.
- The Rust note preserves the research branch’s deferral and no-implementation boundaries.

## 8. Computations and preserved evidence

Commands:

```sh
.venv/bin/python -I review_scratch/run_evidence.py > review_scratch/run_evidence.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/independent_checks.py > review_scratch/independent_checks.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/boundaries.py > review_scratch/boundaries.out
.venv/bin/python -I review_scratch/final_state.py > review_scratch/final_state.out
```

The runner copies and executes the committed evidence using the README arguments and disables bytecode writing for T0 imports.

Results:

- I-33 manifest: **18/18 verified**.
- I-31 manifest: **7/7 verified**.
- Review 01 manifest: **14/14 verified**.
- Numerical reruns: **6/6 byte-identical**.
- Fingerprint rerun: differs only in the three unavailable CPU fields described above.
- Reproduced pipeline: **631 E1-PASS; 2 not certified exterior**.
- Reproduced controls and counts: 32 premise controls, 13 density mutants, 5,198 sqrt arguments, and 8 mutants × 633 points.
- Supplied `mathmodule.c` SHA-256:

```text
436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281
```

Independently recomputed coefficients:

```text
alpha          1.2212453270876738e-15
beta           8.877691069434736e-09 m
epsilon(120km) 9.024240508685258e-09 m
epsilon(2000km)1.1320181723610084e-08 m
```

`review_scratch/` contains these `.py`/`.out` pairs:

- `run_evidence`
- `independent_checks`
- `boundaries`
- `final_state`
- `f1_witness`
- `f2_premise_controls`
- `f3_density`
- `f4_fingerprint`
- `f6_sqrt`
- `observations`
- `pog_pipeline`
- `pog_lib`
- `witness`

It also contains generated `__pycache__/`. Helper-module `.out` files identify their use by the preserved checks.

## 9. Limitations and final state

This is a single-host, offline review. I did not query CI, verify the push or independently reconstruct the implementer’s historical prerequisite checks. **Current CI status is unverified.** No M1/M2 proof scripts were run.

External Rust, Ferrocene, library and publication claims remain unverified against web sources. The portability assessment concerns the packet’s qualified reasoning, not independent confirmation of those external facts.

The computations do not prove absence of every adversarial defect. The required DL reviews and per-platform evidence remain necessary.

Final HEAD is **`5f96119bcc54d2154cdff50a873791f5f9b26d73`**, detached. The tracked tree is clean; `git diff --check 43a6c29 HEAD` passes. No tracked file was modified.

**PASS permits owner decision review only. T2 implementation and POG numerical gates remain unauthorized.**