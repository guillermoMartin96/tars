VERDICT: REQUEST_CHANGES

## Summary

Review target: 0e37db60eed706e041666b40abb5238609a83360, diff from 0a9c040430138845d529b3d8691a86d0f4fea61e. No tracked file was modified. There are 0 BLOCKER, 3 MAJOR, 2 MINOR and 1 NOTE findings. These are recommendations, not owner decisions; T2 remains NOT AUTHORIZED.

The three committed I-31 probes reproduce byte-for-byte on this host. E1's numerical constants and the maximum per-point ratio reproduce. Finite-domain POG is a scientifically plausible route, conditional on complete actual-used-call coverage, rigorous oracles, A-FP-1, sequence conformance, domain checks and per-platform observation. The proposed count assertion does not establish trace completeness, the three-ulp negative control can be an admissible result, and the claimed monotonicity-test sensitivity is false. These require revision before accepting the proposed route as specified.

## Findings

Locations below are in docs/milestones/M3-T2-implementation-authorization-packet.md unless otherwise stated. Numerical evidence is in independent_checks.py and independent_checks.out.

| ID | Severity | Location (file:line) | Finding | Evidence | Recommended disposition |
|---|---|---|---|---|---|
| M3T2P2-R1-F1 | MAJOR | M3-T2-implementation-authorization-packet.md:155; :67; :81 | Counts, even per-function counts and order, cannot establish that every result actually used was traced. The iteration number must not be trusted from the component alone. | A masked hidden cosine leaves the entire observed trace identical, including the expected eight calls for one iteration, but changes height by 64.98137000016868 m. The construction is a nonconforming mutant, not a defect alleged in T0. DL-4/accuracy checks can detect it; the completeness assertion cannot. | Revise DL-3, D-1 and D-6. Require an audited primitive/data-flow inventory, validation of the actual-used arguments/results and iteration/stopping behavior, and masking/hidden-operation mutants. Keep source inspection and DL-4 separate. |
| M3T2P2-R1-F2 | MAJOR | M3-T2-implementation-authorization-packet.md:240; :255 | Three ulps is not necessarily outside the permitted two units of 2^-52 relative error. The required negative-control outcome can reject a correct premise checker. | sin(1), shifted upward three binary64 ulps, has error 1.773082884660813 units of 2^-52 relative and correctly passes the committed premise predicate. | Inject an error proved greater than UF*abs(f)+NU with oracle uncertainty included. Add an admissible-three-ulp positive control. Do not silently tighten A-FP-2. |
| M3T2P2-R1-F3 | MAJOR | M3-T2-implementation-authorization-packet.md:176 | The statement that any grouping, conversion or band-selection defect breaks the monotonicity conclusion is false. | Doubling the exponent scale preserves exp monotonicity and decreasing density. At 100/200 m in band 0, wrong densities 1.2165796318391242/1.208217143351689 pass, versus correct 1.208217143351689/1.1916642167256455. | Revise D-4's sensitivity rationale and disclose survivors. Assign DL-4 and separately justified formula checks as their killers. The finite-pair monotonicity implication remains valid. |
| M3T2P2-R1-F4 | MINOR | M3-T2-implementation-authorization-packet.md:69; :215; :335 | Patch-version review and the proposed fingerprint are insufficient for exact independent replay. | Build flags/configuration, binary identity, linked math-library identity and CPU dispatch are omitted. platform.libc_ver() is empty on this macOS host. Additional available metadata is preserved in independent_checks.out. | Expand provenance and distinguish source-version changes from numerical-environment changes. Reobserve premises on every run. No environment migration is proposed. |
| M3T2P2-R1-F5 | NOTE | M3-T2-implementation-authorization-packet.md:68; :251; :338 | Bitwise output agreement is useful conformance evidence, not proof of operation sequence or numerical correctness. | A shared erroneous cosine gives identical component/twin tuple bits with a 64.98137 m height error. On the probe set, truncation at 2/3 iterations changes latitude bits at 566/453 points and height bits at 296/250. | Compare both returned quantities, specify killing cases for each mutant, and retain source inspection and independent accuracy checks. |
| M3T2P2-R1-F6 | MINOR | M3-T2-implementation-authorization-packet.md:154; docs/reviews/raw/M3-T2-authorization-I31-evidence/premise_probe.py.txt:70 | The probe's half-ulp-of-output sqrt predicate does not establish correct rounding at binade boundaries. | For sqrt(nextdown(1)), an incorrect output 1.0 passes that predicate; correct rounding gives nextdown(1), also returned by this host's math.sqrt. | Qualify the probe claim. If checking correct rounding, use rigorous rounding cells with asymmetric neighbor spacing and ties-to-even. No actual host sqrt defect was found. |

## I-32 section 3 assessment

### A. POG scientific validity

The controlling r1 section 6.2 J-FP2(ii) says a proof or exhaustive check over the input domain the bound is used on; it also rejects sampled measurements alone. A fixed finite domain can be exhausted. That reading can support a pointwise result only if the domain is explicitly the recorded test inputs and their actual numerical executions, not an altitude interval, all binary64 arguments, the supported environment generally, or production inputs. D-1 explicitly requests this restricted route; it is not an already approved interpretation or a promotion. Each execution must satisfy every local hypothesis needed by the derivation. This does not establish the universal library assumption.

I inspected E1's support-function/stationarity argument, contraction and mixed underflow allowances in t0_termination.py, and the T0 review lineage. DQ-1 uses hypot, atan2, sin, cos and sqrt, ordinary float products/divisions/additions/subtractions, absolute difference, the specified stopping tolerance, and at most 60 updates. E1 requires the binary64 a/e2 model ellipsoid, true height >= 0, A-FP-1, applicable A-FP-2 calls, the specified sequence/stopping rule, and no overflow. E1 does not require exp or pow for DQ-1. E3/E4b additionally need the density exp premise and the relevant arithmetic structure; E4b's coefficient structure cannot be inferred from observing exp alone.

A module proxy cannot see C-internal sqrt calls in hypot, float.__pow__/operators, fsum's arithmetic, or user-defined conversions. This is not intrinsically fatal: observing hypot against exact sqrt(x*x+y*y) checks the aggregate contract E1 uses and covers its internal implementation without tracing its internals. DQ-1 does not use pow or fsum. However, hidden substitute operations must be excluded by a reviewed source/data-flow inventory; counts cannot establish this (F1). Casts to owned builtin floats avoid user-defined conversion behavior inside the measured path. Domain-guard computations must also be inventoried separately from the DQ-1 evaluation.

The preserved wrapper forwards arguments and returns the original float results. Across the probe points I found zero bit differences in either returned quantity between instrumented and plain execution. This is host/sample evidence, not a universal instrumentation proof. Future tests should compare traced/plain executions, reject mutable math substitutions, and validate actual-used results and control flow.

Bounded O-1 references are feasible for a finite, stated argument set using interval/rational argument reduction, series remainders and outward rounding, with special handling of exact zero and underflow. O-2 is feasible using a bracketed foot-point root with a residual/bracket-to-height enclosure and outward arithmetic. Neither stopping when a decimal sum stops changing nor Newton correction size alone is such a proof. The committed oracles do not provide those derivations; the packet correctly leaves them as deliverables. A fixed 60-digit implementation is not automatically sufficient for arbitrarily large exterior points or near-boundary classification. Adaptive precision or an explicitly fixed gated domain is needed. An uncertain exterior/interior classification must fail closed rather than discard a fixed sample.

Rule 1 is conservative when evaluated rigorously: abs(got-r)+delta <= UF*(abs(r)-delta)+NU implies the required premise. Use max(0,abs(r)-delta) in a general implementation; the packet's relative-delta restriction already makes this nonnegative. Retain NU=2*2^-1074 exactly; a relative-only comparison is unsound for subnormal/zero results. Exact r=0 under the stated relative requirement requires delta=0 and an exact-zero argument. Finite precision can still straddle a boundary, so the phrase that a small delta can never limit a decision is too strong; fail-closed handling is essential.

Every platform must independently observe its own calls. A different libm can produce different latitudes, stopping counts and argument sets. One host's observations cannot be transferred. A passing run is locally reproducible here; future independent replay requires bounded-oracle source, precision/error certificates, exact input/call encodings and build/library provenance. No accuracy row is ready for promotion now.

### B. Error budget

Running rounding_allowances() gives alpha=1.2212453270876738e-15 (dimensionless), beta=8.877691069434736e-9 m; epsilon(120000 m)=9.024240508685258e-9 m and epsilon(2000000 m)=1.1320181723610084e-8 m. Display-rounded values are not exact gate constants. The domain has no 2000 km upper limit; it is exterior points with no overflow and all other hypotheses. A finite point (DBL_MAX,DBL_MAX,0) returns infinite height in T0 and cannot be assigned E1's finite error guarantee.

The probe computes each ratio with that point's own true-height reference. The largest ratio and largest absolute error coincide at true height 145.0304751527136 m: error=1.9198142883865285e-9 m, epsilon=8.877868187224802e-9 m, ratio=0.216247217000713. This is an empirical maximum only.

The plus-delta height argument is the correct direction for an outer comparison enclosure: h_true <= h_ref+delta and epsilon increases with h. Therefore a correct E1-compliant result must satisfy abs(hat-h_ref) <= epsilon(h_ref+delta)+delta. Passing that comparison is not sufficient to certify the strict original E1 inequality for the unknown true height: it can admit an excess up to 2*(1+alpha)*delta. At delta=beta*1e-6 that excess is 1.7755382138869496e-14 m. If a strict certificate is intended, require abs(hat-h_ref)+delta <= epsilon(max(0,h_ref-delta)) on a certified exterior interval; this may fail closed for a valid result. The packet's outer reference-comparison budget is defensible if described that way. Domain classification and mathematical proof remain separate.

### C. Invariants

The supplied source checksum matches. math_hypot converts each builtin-float argument, applies fabs and constructs its coordinate array before vector_norm. For sign changes the arrays, maximum and found_nan state match; the zero/one-element return, infinity-before-NaN branch, subnormal rescaling/recursion and ordinary scaling/compensation paths therefore match. This supports sign-evenness independently of accuracy under the reviewed build semantics. NaNs produce the same canonical return path; infinity dominates NaN; signed zero becomes positive zero. NaN/inf are rejected by geodesy's domain guard, so D-3 should state its operational domain. Arbitrary objects with side-effecting conversions are outside the builtin-float claim.

DQ-1 uses x/y only through p after conversion; the accepted domain must also be sign invariant. For accepted points, identical p and unchanged z make the full DQ-1 computation identical, including early exit. D-3's evenness proposal is sound. Guard equivariance must be checked separately for the public component.

The supplied compensated vector_norm code does not provide a swap proof simply because its primary csum is order dependent; conversely, that dependence alone is not a proof that swaps differ. No general swap proof was established here. The 2 million pairs and my 225 adversarial pairs have zero swap/evenness mismatches; these are samples only. The adversarial set includes signed zeros, signed subnormals, smallest normals, huge/equal values, infinities and a payload NaN. Keep swaps conditional unless separately proved or observed for the gated points.

For one pair of correctly selected same-band heights, observing exp order at the two actual exponent arguments is enough for B-10's pairwise conclusion, together with the specified monotone preprocessing and positive rho0 multiplication. Equal exponents/results are valid. It proves neither exp monotonicity over an interval nor correct density values; F3 supplies a meaningful survivor. Wrong exponent sign can be detected; positive exponent-scale errors need not be. Strict decrease and exact z-reflection remain report-only.

D-7's actual-rounded-point oracle is scientifically preferable to pretending nominal forward coordinates are exact. DL-4 is valuable against the named truncation mutants, especially when latitude is compared; it can pass with common libm defects and can fail for an accurate but numerically different sequence. The latter is a real DQ-1/DQ-2 contract violation, not necessarily a numerical-accuracy failure. It is P-class evidence, not an independent physics oracle.

### D. Reproducibility

RQ-1 is a sampled same-environment repetition check; RQ-2 is appropriate for constants built from the specified correctly rounded operations. RQ-3 correctly avoids cross-platform bit equality. RQ-4/D-5 track source-version invalidation but do not fully identify a build. RQ-5 checks the active rounding/underflow environment on selected operations; it is not a proof of every hardware or libm operation, and the probe sqrt check has F6's limitation. RQ-6 avoids Python-level implicit FMA and NumPy reordering for the specified sequences, but says nothing about C-internal contraction in hypot or the platform library. Its DL-4 only covers DQ-1/DQ-2, so drag arithmetic still needs its specified inspection/derivation. RQ-7 preserves the accepted same-platform regressions; I did not run M1/M2 proofs. RQ-8 is necessary and should remain fail-closed.

For exact replay record interpreter distribution/artifact identity, available compiler/configuration/flags, OS build, architecture/CPU features and linked math-library version/identity in addition to DL-5. On Linux libc version alone need not identify libm's actual code/dispatch; on macOS the OS build and math-library provenance matter. CPython patch identity identifies neither all of these nor downstream patches. Reobserving finite premises limits the scientific risk of drift; it does not make historical numerical replay automatic. Prefer the packet's no-migration route D-5(b), with expanded provenance.

### E. Scope and traceability

The docs-only diff preserves the controlling DR-0024...0029 records and ADR-0009. Their I-26/I-27/I-29 updates govern historical proposal wording. The packet preserves the km-route exception, stage-mass adapter, unchanged T1 J2, pinned table, current-mass drag, ordered composition and versioned identifiers. T3 contracts/events/scenarios, T4 validators/trajectory accumulation and T5 GMAT remain excluded. P6 is not a T2 prerequisite under Q-GATE, but P6/P6(b) remain unresolved and X-1 remains unauthorized. No new threshold or language implementation is implicitly required.

DL-1/DL-2 need actual reviewed bounded algorithms; DL-3 needs F1's correction; DL-4 is useful P-class conformance; DL-5 needs F4's metadata; DL-6 stays optional with unsupported rows reported; DL-7 supports only reviewed-source evenness. All seven can remain test/evidence deliverables without becoming runtime dependencies. Keep promotion conditions P-i/P-ii/P-iii conjunctive and distinguish completion on unconditional gates from geodetic scientific acceptance. G-T2-10/11 must be tied to the specifically approved decisions and revised test requirements, not imply unconditional promotion. Existing scope, oracle, premise, sequence and platform stops are appropriate once their predicates are corrected.

### F. Individual decisions

APPROVE below means a reviewer recommendation for the stated proposal, not an owner approval or a row promotion.

| Decision | Recommendation | Justification | Required evidence | Dependencies | Consequence of approval | Remaining blocker |
|---|---|---|---|---|---|---|
| D-0 | APPROVE | Separates one-evaluation rounding/band selection from T4 trajectory error. | Explicit scope wording and E1/E2 traceability. | I-30 interpretation; T4 exclusion. | Bounds the requested T2 analysis. | No scientific blocker to this scope recommendation. |
| D-1 | REVISE | Finite-domain route is valid in principle, but count completeness is unsupported. | F1/F2 corrections, bounded O-1/O-2, full hypothesis inventory and per-platform run certificates. | A-FP-1, D-2/D-6 and D-7 where applicable. | Opens a route to P-i only, not production accuracy. | DL-1...DL-3 derivations/validation and later owner promotion. |
| D-2 | REVISE | Deliverables fit scope but inherit tracing and provenance defects. | Corrected DL-3/DL-5, oracle derivations, independent review and mutation matrix. | Revised D-1/D-6; D-8 for the added gate. | Authorizes future test-side evidence work if separately included in T2 authorization. | Deliverables do not exist as reviewed gate evidence. |
| D-3 | APPROVE | fabs normalization supports evenness for builtin binary64 inputs; later DQ-1 sees only p. | Reviewed source/build provenance and guard sign-equivariance checks. | DL-7 and D-5; exact DQ-1 sequence. | Adds only sign-reflection/half-turn equality. | Unreviewed build/version stops; no swap proof supplied. |
| D-4 | REVISE | Finite-pair order and swap premises can support their local conclusions, but sensitivity claims overstate coverage. | Correct pairwise predicate/order, same-band and preprocessing checks, F3 survivor disclosure, designated killers. | D-3 for sign part, corrected tracing, B-10/B-11 structure. | Local metamorphic gates only. | No universal monotonicity/swap justification; explicit owner promotion remains. |
| D-5 | REVISE | Prefer (b), but patch version is not the whole numerical environment. | Expanded artifact/build/library fingerprint and precise invalidation policy. | DL-5/DL-7; RQ-8 reobservation. | Stops unreviewed source versions without CI/runtime migration. | Exact replay provenance currently incomplete. |
| D-6 | REVISE | Attribute calls, owned floats and scalar arithmetic help but do not prove completeness. | Primitive/data-flow audit, iteration validation, hidden-operation/masked-trace mutants, traced/plain comparison. | D-1/DL-3 and DQ-1/DQ-2. | Constrains future testability and numerical structure. | F1; C-internal aggregate contracts and operator paths must be distinguished. |
| D-7 | APPROVE | Correctly references the actual binary64 point and avoids a forward-construction comparison error. | Rigorous O-2 error and exterior classification; stated outer-comparison semantics. | D-1/DL-2 and P-ii/P-iii. | Offers an alternative route for U-18. | No reviewed O-2 error certificate yet; no promotion now. |
| D-8 | APPROVE | Useful explicit algorithm-conformance gate alongside source inspection and independent accuracy. | Independently coded twin, comparisons of h and phi, fixed cases killing every named mutant, per-platform results. | Exact DQ-1/DQ-2; T2 independent review. | Makes specified output differences acceptance failures. | The actual twin/kill matrix is future work; output agreement alone proves no global sequence theorem. |

### G. Rust research boundary

I located and read RES-0001 and ADR-0008 via origin/research/flight-software-architecture at 2d6d7e59c880ace48c25fd8ed3bcd18ecdfc5233. The packet preserves Python as reference, Rust only as preferred future candidate, TL-6's requirements-based deferral, TL-9's implementation prohibition, PC-1's future boundary trigger and the open AT items. No migration is authorized or required.

The new Rust/libm/Ferrocene/arXiv factual claims could not be independently verified offline. In particular, pinning software-libm source alone should not be asserted to guarantee cross-platform bits without accounting for target/compiler/FMA/features. RES-0001 section 6 layer 2 does not itself prove that guarantee. POG's logical principle transfers to future work; its current numerical oracles and data-flow assumptions cannot be presumed to transfer unchanged to a different implementation. These observations do not create a language decision or a T2 prerequisite.

## Required corrections or additional research

1. Correct F1's trace/data-flow justification and strengthen its adversarial coverage before D-1/D-6 are accepted as specified.
2. Replace the unqualified three-ulp negative-control requirement with a proved premise violation, and retain admissible perturbation controls.
3. Correct D-4's sensitivity claims and explicitly assign surviving formula/scale/conversion defects to other gates.
4. Expand replay provenance and correct the sqrt-probe claim; use rounding-cell validation if claiming correct rounding.
5. Complete and independently review O-1/O-2 error bounds, exact inputs/traces and domain certificates before any dependent accuracy row gates. Record reference-comparison versus strict-certification semantics explicitly.
6. Demonstrate the DL-4 mutant matrix for both returned quantities and maintain P-i/P-ii/P-iii and all scope stops. No new CI/runtime/library/language migration is proposed.

## Computations and preserved artifacts

Commands run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/premise_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/premise_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/mutant_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/mutant_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/hypot_probe.py > review_scratch/hypot_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/independent_checks.py > review_scratch/independent_checks.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/final_state.py > review_scratch/final_state.out
```

The first three scripts are unchanged copies of committed .py.txt evidence. Their outputs reproduce byte-for-byte: 631 eligible points, 11867 calls, zero measured premise violations, zero epsilon failures; the 13-mutant output and 2-million-pair hypot output also match. These remain unbounded-reference feasibility measurements.

Supplied mathmodule.c SHA256 independently verified: 436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281. All seven entries in the I-31 evidence manifest also verify. The extra source file remains outside the repository and unchanged.

review_scratch contains premise_probe.py/.out, mutant_probe.py/.out, hypot_probe.py/.out, independent_checks.py/.out, final_state.py/.out, findings.json, this review.md and a SHA256SUMS manifest. The independent checks preserve full numerical counterexamples and available runtime/build metadata. final_state.out preserves tracked-tree checks and artifact hashes. This report and findings.json record the verdict and structured findings. The review prompt remains in the task's conversation record; it was not copied or altered as repository documentation.

## Limitations and final state

No network, other CI host, live CI query, external source verification, GMAT run, M1/M2 proof run or production T2 implementation was available or performed. The supplied CI-green/remote-sync preconditions remain implementer claims, as instructed. No local precondition failure was found: HEAD matches, the initial tracked tree was clean, and the reviewed diff is docs-only. This was a focused scientific/architectural review, not a new formal proof of every E1-E6 coefficient or a reproduction of the full historical T0 campaign. The local T0 oracles' missing rigorous bounds limit all empirical accuracy outputs here.

Final HEAD remains 0e37db60eed706e041666b40abb5238609a83360, detached. Tracked files remain clean; no commit or push was made, consistent with the snapshot's no-tracked-edits rule and offline restriction. CI at this SHA is reported by the implementer as four green jobs and was not independently queried. No correction pass was started. T2 implementation remains NOT AUTHORIZED.
