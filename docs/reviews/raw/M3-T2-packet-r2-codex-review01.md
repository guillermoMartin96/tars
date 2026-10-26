VERDICT: REQUEST_CHANGES

## 1. Summary

**Findings: 0 BLOCKER, 3 MAJOR, 2 MINOR, 1 NOTE.**

POG is scientifically plausible for explicitly fixed finite executions, but the proposed tracing and mutation requirements need correction. The numerical error budget reproduces, and the supplied CPython source supports the proposed `hypot` evenness argument.

All three I-31 probes reproduced **byte-for-byte** on this host. No tracked files changed.

The detailed review is preserved in [review.md](review_scratch/review.md), with a structured register in [findings.json](review_scratch/findings.json).

**These are review recommendations only. No decision is approved, no row is promoted, and T2 remains NOT AUTHORIZED.**

## 2. Findings

Packet locations below refer to `docs/milestones/M3-T2-implementation-authorization-packet.md`. Reproduction evidence is in [independent_checks.out](review_scratch/independent_checks.out).

| ID | Severity | Location (file:line) | Finding | Evidence | Recommended disposition |
|---|---|---|---|---|---|
| M3T2P2-R1-F1 | MAJOR | `M3-T2-implementation-authorization-packet.md:155`, also :67, :81 | Call counts do not establish complete numerical data flow. Even matching call names, arguments, results and order cannot prove those results were actually used. | A mutant preserves the **entire observed trace**, including the expected eight calls, while using an untraced cosine result and changing height by **64.98137000016868 m**. Accuracy/DL-4 checks can detect it; the claimed completeness assertion cannot. | Revise DL-3 and D-1/D-6. Require an audited primitive/data-flow inventory, independently validated iteration/stopping behavior, and hidden-operation/trace-masking mutants. Retain source inspection separately. |
| M3T2P2-R1-F2 | MAJOR | `M3-T2-implementation-authorization-packet.md:240`, also :255 | A three-ulp perturbation need not violate A-FP-2. The mandatory negative-control outcome can therefore reject a correct checker. | `sin(1)`, shifted upward three ulps, has error **1.773082884660813 × 2⁻⁵² relative**, within the permitted two units, and correctly passes the probe predicate. | Inject an error proved outside `UF·|f| + NU`, accounting for oracle uncertainty. Include an admissible-three-ulp positive control. |
| M3T2P2-R1-F3 | MAJOR | `M3-T2-implementation-authorization-packet.md:176` | The assertion that any grouping, conversion or band-selection defect breaks the monotonicity conclusion is false. | Doubling the exponent scale preserves both the observed `exp` ordering and decreasing density while materially changing the density values. | Revise D-4’s sensitivity rationale; disclose survivors and assign DL-4 or separately justified formula checks as their killers. |
| M3T2P2-R1-F4 | MINOR | `M3-T2-implementation-authorization-packet.md:69`, also :215, :335 | Patch version and the proposed fingerprint do not fully identify an environment for exact independent replay. | Compiler flags/configuration, interpreter artifact identity, linked math-library identity and CPU dispatch are omitted. `platform.libc_ver()` is empty on this macOS host. | Expand evidence provenance and distinguish source-version invalidation from numerical-environment drift. Reobserve POG every run. No migration is needed. |
| M3T2P2-R1-F5 | NOTE | `M3-T2-implementation-authorization-packet.md:68`, also :251, :338 | Bitwise output agreement is useful conformance evidence, not proof of operation sequence or numerical correctness. | A shared faulty cosine produces identical component/twin tuple bits with a **64.98137 m** error. | Compare both height and latitude; specify mutant-killing inputs; retain source inspection and independent accuracy checks. |
| M3T2P2-R1-F6 | MINOR | `M3-T2-implementation-authorization-packet.md:154`; `docs/reviews/raw/M3-T2-authorization-I31-evidence/premise_probe.py.txt:70` | The probe’s `error ≤ ulp(output)/2` predicate does not establish correctly rounded `sqrt` at binade boundaries. | For `sqrt(nextdown(1))`, incorrect output `1.0` passes that predicate. Correct rounding gives `nextdown(1)`, which this host returns. | Qualify the probe claim. Use rigorous rounding cells with asymmetric neighbor spacing and ties-to-even if checking correct rounding. No actual host `sqrt` defect was found. |

## 3. Assessment of I-32 §3 A–G

### A. POG scientific validity

**Finite-domain POG can work, but the packet has not yet established its prerequisites.**

The controlling J-FP2(ii) text permits a proof or exhaustive check “over the input domain the bound is used on,” while rejecting sampled measurements alone. A fixed finite set can be exhausted. That supports only its explicitly recorded executions—not an altitude interval, arbitrary production inputs, or a universal library guarantee. D-1 requests this restricted route; it is not already approved.

I inspected E1’s support-function, stationarity, contraction, stopping-rule and mixed-underflow arguments. For DQ-1, the relevant requirements include:

- The binary64 `a`/`e²` model ellipsoid.
- True height ≥ 0 and **no overflow**.
- A-FP-1 arithmetic and square-root behavior.
- Applicable A-FP-2 bounds for `hypot`, `atan2`, `sin` and `cos`.
- The specified arithmetic, stopping tolerance and maximum 60 updates.

DQ-1 uses neither `exp` nor `pow`. E3/E4b additionally require the density `exp` premise and their specified arithmetic structure.

A Python attribute proxy cannot observe C-internal operations, `float.__pow__`, operators, `fsum` arithmetic or user-defined conversions. **That is not automatically fatal:** checking `hypot` against exact √(x²+y²) establishes the aggregate contract E1 uses without tracing its internal square roots. However, hidden substitute operations must be excluded through reviewed source/data-flow evidence. Counts alone cannot do this—F1.

The preserved tracer produced **zero bit differences in either returned quantity** versus uninstrumented execution across the probe points. That supports local instrumentation neutrality, not a universal proof.

Rigorous O-1 and O-2 bounds are feasible for a stated finite domain:

- O-1 needs bounded argument reduction, series remainders and outward arithmetic, including exact-zero and underflow handling.
- O-2 needs a certified root bracket or equivalent residual-to-height enclosure, plus arithmetic-error bounds.
- Decimal stagnation and a small Newton correction alone are insufficient.
- Uncertain exterior/interior classification must fail closed rather than silently remove a fixed sample.

The packet correctly identifies the existing references as lacking written bounds. Those deliverables remain unfinished scientific dependencies.

Rule 1 is conservative when evaluated rigorously:

\[
|\hat f-r|+\delta\le UF(|r|-\delta)+NU
\]

implies the desired premise. Retain the absolute subnormal term exactly. Under the stated relative-error restriction, `r=0` requires `δ=0`; exact zeros need explicit treatment. Arbitrarily small nonzero uncertainty can still straddle a decision boundary, so it cannot literally be guaranteed never to limit a decision.

Each CI platform must observe its own actual execution. Different library results can change subsequent arguments and iteration counts. **No accuracy row is ready for promotion now.**

### B. Error-budget integrity

Recomputed from `rounding_allowances()`:

| Quantity | Reproduced value |
|---|---:|
| α | `1.2212453270876738e-15` |
| β | `8.877691069434736e-9 m` |
| ε_h(120 km) | `9.024240508685258e-9 m` |
| ε_h(2000 km) | `1.1320181723610084e-8 m` |

α is dimensionless; β and ε_h are lengths. Display-rounded coefficients should not replace the actual gate constants.

E1 has **no 2000 km upper limit**, but retains its no-overflow condition. For example, T0 returns infinite height for the finite input `(DBL_MAX, DBL_MAX, 0)`; E1 cannot supply a finite accuracy guarantee there.

The probe uses **each point’s own** ε_h. Its largest absolute error and largest ratio coincide:

- True height: `145.0304751527136 m`.
- Absolute error: `1.9198142883865285e-9 m`.
- ε_h at that point: `8.877868187224802e-9 m`.
- Ratio: **`0.216247217000713`**.

This remains an empirical maximum.

The `h_ref + δ_O` direction is correct for an **outer reference-comparison enclosure**, since ε_h increases with height. A correct E1-compliant result must satisfy the packet’s inequality.

Passing that comparison does not itself certify the strict original E1 inequality for the unknown true height: it can admit an excess up to `2(1+α)δ_O`. At the proposed maximum δ_O, this is approximately **`1.7755382138869496e-14 m`**. Distinguish this comparison budget from strict certification. A sufficient strict certificate would instead require:

\[
|\hat h-h_{\rm ref}|+\delta_O
\le \epsilon_h(\max(0,h_{\rm ref}-\delta_O))
\]

on an independently certified exterior interval.

### C. Numerical and algorithmic invariants

**Evenness:** The supplied CPython source normalizes builtin-float arguments with `fabs`. Sign changes therefore give identical coordinate arrays and branch state. This reasoning survives:

- Signed zero and `max == 0`.
- Subnormal scaling and recursion.
- Ordinary scaling and compensation.
- Infinity handling and the canonical NaN-return path.

Non-finite inputs are rejected by the geodetic domain guard. Arbitrary objects with side-effecting conversions are outside the builtin-binary64 claim.

DQ-1 subsequently uses x and y only through `p`. Thus identical `p` and unchanged z imply identical arithmetic and stopping behavior for accepted points. The public component’s guard must separately preserve these sign symmetries. **D-3’s proposed evenness result is sound within these qualifications.**

**Swap symmetry:** Order dependence of the primary compensated sum is not, by itself, proof of a swap mismatch; nor does it provide a swap proof. I established no general swap theorem. The reproduced two-million-pair probe and my 225 adversarial pairs had zero mismatches. These are samples, not proof.

**D-4/B-10:** Observing `exp` order at the two actual exponent arguments is sufficient for the **pairwise** conclusion when the specified same-band preprocessing and positive multiplication are established. It proves neither interval-wide monotonicity nor correct density values. F3 supplies a meaningful passing defect.

**D-7:** Referencing the true height of the actual binary64 point is scientifically sound. It avoids pretending nominal forward coordinates are exact, subject to O-2’s bound and exterior classification.

**D-8:** Bitwise conformance usefully catches the named truncation mutants. On the probe set:

- Two-iteration truncation changes latitude bits at 566 points and height bits at 296.
- Three-iteration truncation changes latitude bits at 453 points and height bits at 250.

Compare both outputs. A shared library defect can pass conformance while failing accuracy; an accurate alternative sequence can fail conformance because it violates DQ-1/DQ-2. These are different properties.

Strict density decrease and exact z-reflection correctly remain report-only.

### D. Cross-platform reproducibility

- **RQ-1:** Useful sampled repetition check; not an unrestricted determinism theorem.
- **RQ-2:** Appropriate for constants built from the specified correctly rounded operations.
- **RQ-3:** Correctly avoids cross-platform bit equality.
- **RQ-4/D-5:** Necessary source-version invalidation, incomplete replay provenance.
- **RQ-5:** Useful active-environment checks; not proof of every arithmetic/libm operation. F6 limits the probe’s square-root claim.
- **RQ-6:** Python scalar arithmetic avoids Python-level implicit contraction. It does not constrain C-internal FMA/compiler behavior in `hypot` or libm. DL-4 covers DQ-1/DQ-2; drag still needs its specified inspection/derivation.
- **RQ-7:** Preserves the accepted same-platform regression policy.
- **RQ-8:** Essential; retain per-platform, fail-closed observation.

Record interpreter artifact/distribution identity, compiler configuration and available flags, OS build, architecture/CPU features and linked math-library provenance. Linux libc version alone need not identify libm code/dispatch. macOS version/build matters.

Prefer D-5(b), with expanded provenance. **No CI or runtime migration is proposed.**

### E. Scope and traceability

The docs-only diff preserves the controlling decisions and reconciliations:

- DR-0024 through DR-0029 and ADR-0009 remain authoritative.
- The km-route exception, stage-mass context, unchanged T1 J2, pinned table and force order are retained.
- T3 contracts/events/scenarios, T4 validators/trajectory accumulation and T5 GMAT remain excluded.
- P6 is not a T2 prerequisite under Q-GATE, but P6/P6(b) remain unresolved.
- X-1 remains unauthorized.
- No threshold or language migration is implicitly required.

All seven deliverables fit test/evidence scope:

- **DL-1/DL-2:** Need reviewed bounded algorithms.
- **DL-3:** Needs F1’s correction.
- **DL-4:** Useful partially independent conformance evidence.
- **DL-5:** Needs fuller provenance.
- **DL-6:** Unsupported derivations remain report-only.
- **DL-7:** Supports reviewed-source evenness only.

Keep P-i/P-ii/P-iii conjunctive. G-T2-10/11 must depend on the specifically approved decisions and corrected test requirements. Implementation completion on unconditional gates must remain distinct from geodetic scientific acceptance.

### F. D-0 … D-8

“APPROVE” below is a **recommendation**, not an owner decision.

| Decision | Recommendation | Justification | Required evidence | Dependencies | Consequences of approval | Remaining blocker |
|---|---|---|---|---|---|---|
| D-0 | APPROVE | Correctly separates per-evaluation rounding from T4 trajectory accumulation. | Explicit E1/E2 scope traceability. | I-30 interpretation; T4 exclusion. | Bounds the requested T2 analysis. | None for this scope recommendation. |
| D-1 | REVISE | Finite-domain route is valid in principle; trace completeness is unsupported as specified. | F1/F2 corrections; bounded oracles; full hypothesis inventory; platform certificates. | A-FP-1, D-2/D-6; D-7 where applicable. | Opens a route to P-i only. | DL-1…DL-3 validation and later owner promotion. |
| D-2 | REVISE | Deliverables fit scope but inherit tracing/provenance defects. | Corrected DL-3/DL-5; oracle derivations; independent review and mutation matrix. | Revised D-1/D-6; D-8 for its gate. | Adds future test-side evidence work. | Reviewed deliverables do not yet exist. |
| D-3 | APPROVE | `fabs` normalization supports sign-evenness; DQ-1 then sees identical p. | Source/build provenance; guard-equivariance checks. | DL-7, D-5, exact DQ-1 sequence. | Adds sign-reflection/half-turn equality only. | Unreviewed build/version; no swap proof. |
| D-4 | REVISE | Local premises can support local conclusions, but sensitivity is overstated. | Correct pairwise predicate; same-band/preprocessing checks; disclosed survivors and killers. | Corrected tracing; B-10/B-11; D-3 for sign part. | Local metamorphic gates only. | No universal monotonicity/swap justification; promotion remains separate. |
| D-5 | REVISE | Prefer (b), but patch version is not the whole environment. | Expanded artifact/build/library fingerprint and invalidation policy. | DL-5/DL-7; RQ-8. | Stops unreviewed source versions without migration. | Incomplete replay provenance. |
| D-6 | REVISE | Attribute calls and scalar floats help but do not prove completeness. | Primitive/data-flow audit; iteration validation; masking mutants; traced/plain comparisons. | D-1/DL-3; DQ-1/DQ-2. | Constrains future testability. | F1 and explicit treatment of hidden/operator paths. |
| D-7 | APPROVE | Correctly references the actual rounded point. | Rigorous O-2 error/exterior certificate; clear comparison semantics. | D-1/DL-2; P-ii/P-iii. | Alternative route for U-18. | O-2 certificate and promotion remain pending. |
| D-8 | APPROVE | Useful explicit conformance gate alongside inspection and accuracy checks. | Independent twin; both returned quantities; fixed mutant-killing cases; platform runs. | Exact DQ-1/DQ-2; independent review. | Makes specified output differences acceptance failures. | Actual twin/kill matrix remains future work. |

### G. Rust boundary

I located and read RES-0001 and ADR-0008 at research-branch SHA `2d6d7e59c880ace48c25fd8ed3bcd18ecdfc5233`.

The packet preserves Python as reference, Rust only as a future candidate, TL-6’s requirements-based deferral, TL-9’s prohibition, PC-1’s boundary trigger and the open AT items.

The new Rust/libm/Ferrocene/arXiv factual claims could not be independently verified offline. Pinning software-libm source alone should not be asserted to guarantee cross-platform bits without target/compiler/FMA qualifications. POG’s logical principle can transfer; its current implementation assumptions cannot simply be presumed to transfer unchanged.

No language implementation or migration is authorized or required.

## 4. Required corrections or additional research

1. Replace count-based completeness justification with audited actual-used data flow and stronger mutants.
2. Replace the unqualified three-ulp negative control with a proved premise violation.
3. Correct D-4’s sensitivity claims and identify surviving defects’ designated killers.
4. Expand replay provenance and correct the square-root probe claim.
5. Complete independent validation of O-1/O-2 bounds and domain classification before dependent rows gate.
6. Demonstrate DL-4’s mutation matrix for both height and latitude; preserve all promotion and scope boundaries.

## 5. Computations and preserved evidence

Commands used:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/premise_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/premise_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/mutant_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/mutant_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/hypot_probe.py > review_scratch/hypot_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/independent_checks.py > review_scratch/independent_checks.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/final_state.py > review_scratch/final_state.out
```

Reproduced probe output includes **631 eligible points, 11,867 calls, zero measured premise violations and zero ε_h failures**. The mutant and two-million-pair outputs also match their committed bytes.

The supplied source SHA-256 independently matches:

```text
436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281
```

All seven I-31 manifest entries verify.

`review_scratch/` contains:

- `premise_probe.py/.out`
- `mutant_probe.py/.out`
- `hypot_probe.py/.out`
- `independent_checks.py/.out`
- `final_state.py/.out`
- `findings.json`
- `review.md`
- `SHA256SUMS`

The scratch manifest also verifies.

## 6. Limitations and final state

No network, other-platform execution, live CI query, GMAT run or M1/M2 proof run was performed. External web-source claims remain unverified. Existing unbounded T0 references limit the empirical accuracy evidence; this review does not replace their required rigorous derivations.

Final HEAD remains **`0e37db60eed706e041666b40abb5238609a83360`**, detached, with a **clean tracked tree**. No commit, push or correction pass occurred.

CI at this SHA is **reported by the implementer as four green jobs**, not independently queried.

**T2 implementation remains NOT AUTHORIZED.**