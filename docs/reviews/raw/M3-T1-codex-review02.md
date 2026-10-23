# M3 T1 Independent Review 02

Reviewed **`1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4`**, detached from `milestone-3-t1-j2-force-model`, against I-19 and the repository-local I-17/I-18 authorizations. Local origin tracking refs match this HEAD and `origin/main = 60648b93385a9954194730006aeac29ea14875ad`; these are local observations, not a remote fetch. I did not write the implementation or modify tracked files. **Two MINOR defects remain; T1 is not acceptance-ready.** No acceptance, merge, correction, or subsequent review is authorized by this report.

## Evidence and execution ledger

Environment independently observed: macOS 26.2 (Darwin 25.2.0), x86_64, CPython 3.12.15 built with Clang 22.1.3; NumPy 2.5.3, SciPy 1.18.1, Pydantic 2.13.5, pytest 9.1.1, Ruff 0.16.10. Python reports radix 2, 53-bit precision, round-to-nearest, minimum normal `2.2250738585072014e-308`. The platform API reports CPU `i386`; the CPU-brand `sysctl` was sandbox-denied. The exact processor model is unverified. I used the supplied `.venv`, without synchronization or network access.

[COMMANDS.md](<SNAP>/review_scratch/COMMANDS.md) records commands, logs and inspection operations. Reviewer programs and mutant diffs are retained under `review_scratch/`. All results below are my own local execution/computation unless explicitly identified as documentary claims.

- Full pytest: **1,254 passed, 3 warnings in 1,789.38 s (29m49s), exit 0** (`pytest.log`). The warnings come from intentional overflow cases in existing regression tests.
- T1 mutation control: **73 passing cases**. Independently reconstructed `97b69ef` source: **21 failed / 52 passed**, matching the corrected red-first claim (`own_mutants/redfirst.log`). All 32 archived source files supplied for Review 01 match their Git objects (`verify_old.log`).
- Committed mutation campaign: **32/32 detected, 32 by assertion, no survivors**, control exit 0 (`mutation.json`, `mutation.log`). Counts and actual failure messages were inspected, rather than trusting the summary alone.
- T0: **314 passed in 170.38 s**, exit 0 (`t0.log`).
- M1 non-GMAT validator: **7/7**, approved thresholds (`m1.json`, `m1.log`). This is not a claim to have executed the prohibited nine-step wrapper.
- M2 validator: **228/228**, including reference snapshot, golden and committed GMAT checks, approved thresholds (`m2.json`, `m2.log`). I did not execute the prohibited twenty-step wrapper.
- M2 local cross-platform record collection: six canonical missions, all successful, exact HEAD, clean tree (`m2_local_record.json`). Fresh-process determinism passes for all four `scenarios/m2_*.json` files (`determinism_m2_*.log`). No three-platform gate is claimed from a single record.
- M1 golden comparison: zero position/velocity difference and bit identity (`golden.log`). Cross-process determinism: both event-log digests are **`7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`** (`determinism.log`). This is an event-log digest; the golden JSON file itself has a different digest.
- Ruff check and format check: exit 0; **233 files already formatted** (`lint.log`, `format.log`). Reviewer scratch is ignored by these repository checks.
- Correction experiment: **200,004 / 200,004 accelerations bit-identical**, seed 20261023; numerical boundaries and original failure reproductions match the committed file byte for byte (`correction.json`, `audit.log`).
- Informational experiment: the complete output reproduces the committed file byte for byte (`info.json`, `audit.log`), including secular rates, invariant drift and convergence. This reproduces measurements, not their physical provenance or a secular acceptance threshold.
- My separate RK4 comparison: **6,001 complete states per trajectory**, inclinations 28.5°, 51.6°, 97°, dt 10 s, all old/new trajectory bytes identical (`extra_checks.log`).
- Adversarial parameter and arithmetic results: `probe.log`, `parameter_boundary.log`, `underflow.log`, `exact_case.log`, and the rational certificate `certificate.log`, and `boundary_reason.log`.
- Expanded-grid interval certificate: **5,904 positions certified; no uncertified components**, maximum enclosed-error/minimum-computed-bound ratio **0.4114583333333321** (`interval_dyadic.log`).

Inspected result files comprise the three committed `docs/science/experiments/m3-t1/*results.json`, their scratch reproductions, `m1.json`, `m2.json`, `m2_local_record.json`, `own_mutants/results.json`, all three own-mutant JUnit files, `classifier.xml`, the logs named above, the supplied Review 01 reproduction JSON, and all five `review_scratch/ci/run-*.json` exports. `mutation_audit.log` identifies the assertions and grid counts. `audit.log` records scope, historical-prefix and CI-identity checks; `details.log` records environment and result counts. The initial unquantized interval run was interrupted for excessive rational-denominator growth; the completed outward-dyadic certificate replaces it. An initial reviewer JSON-serialization error is preserved in `mutation_audit_initial_error.log`; its corrected rerun passed. An exploratory underflow calculation initially used a different multiplication order for `c`; I corrected the scratch probe and based the finding on the separate rational certificate.

The five supplied CI exports internally associate runs **39865621259**, **39885659108**, **39894033142**, **39894176897**, **39897342033** with the expected SHAs `97b69ef`, `dbb960a`, `b0164fd`, `16a8e63`, and this exact HEAD. Each lists the three platform check jobs and `m2-cross-platform` as successful. The final export identifies the full pinned SHA correctly. These are implementer-supplied metadata, not authenticated CI execution. Historical wrapper outcomes 9/9 and 20/20, historical full-suite counts, remote branch state and push history remain documentary claims.

## Review 01 resolution table

| Finding | Resolution | Evidence and reasoning |
|---|---|---|
| M3T1-R1-F1 | **PARTIALLY RESOLVED** | Ordinary assignment/deletion/addition and stale caching are corrected. Accepted mutable numerical parameters are retained by reference, so physical configuration remains mutable; R2-F2. |
| M3T1-R1-F2 | **PARTIALLY RESOLVED** | Original equatorial overflow, tiny-radius exception and infinite-parameter cases are corrected with appropriate diagnostics. Off-axis final-product underflow still returns a silent zero with a representable exact component; R2-F1. Parameter ownership also permits invalid values after validation; R2-F2. |
| M3T1-R1-F3 | **RESOLVED** | The wording is now r⁻³; the assertion is unchanged. Independent differentiation and radial-dot computations agree. |
| M3T1-R1-F4 | **RESOLVED** | All four previously surviving mutants now fail meaningful functional assertions. The stronger finite campaign and its limitations are accurately stated. Further survivors do not invalidate the scoped correction. |

## Independent mathematical and adversarial assessment

With `A = μ J2 R²/2`, the J2 potential is `U2 = A(r⁻³ − 3z²r⁻⁵)`. Its x derivative is `A(−3x/r⁵ + 15xz²/r⁷)`; y is analogous, and z is `A(−9z/r⁵ + 15z³/r⁷)`. These reduce to the implemented acceleration. The coefficient has units m⁵/s², yielding m/s² after division by r⁵ and multiplication by a coordinate. The positive-potential convention requires **+∇U**. With fully normalized `P̄20 = √5 P2`, the relation is `J2 = −√5 C̄20`, consistent with the authorized constants and their locally verified bit pattern.

Taking the dot product gives `a2·r = −(3/2)J2 μR² r⁻³(1 − 3z²/r²)`. At radii R, 2R, 4R and latitudes 0°, 20°, 50°, my computed/formula ratios range from `0.9999999999999994` to `1.0000000000000004`. This supports the corrected r⁻³ wording; the formula itself establishes the scaling.

The power-of-two exactness claim is valid under the stated binary64 arithmetic assumption. At `r = 2^e`, r² is `2^(2e)`, its square root is exactly `2^e`, and r⁵ is `2^(5e)`; the largest exponent is 1000. On the equator/pole, s² is exactly 0/1 and the factors are exactly 1 and −2. With J2 equal to ±1/2 or 3/8 and μ = R = 1, the coefficient is a small dyadic rational, division by r⁵ only shifts its exponent, and the final products remain normal and exactly representable even at e = 200. The nonzero equality assertions therefore have an analytical basis; they are not merely observed equalities. Zero assertions use numerical equality and do not establish a sign bit for zero.

The dense grid has `(361 + 8) × 4 × 4 = 5,904` positions, exercised separately for both signs of J2: 11,808 evaluations. **320 positions** lie in the previously missed `0.99 < s² < 0.9999` band. Half-degree spacing establishes intersection with latitude intervals wider than half a degree; it does not establish detection of arbitrary errors between grid points or errors below the bound. The new high-latitude mutant fails the dense gradient assertion for both J2 signs. Negative-J2 absolute-value mutation fails that assertion and the exact negative-J2 answers. The small coefficient mutant fails the exact answers. Far-field zero fails known answers, the dense gradient and domain expectations. The other four reviewer mutants also fail functional assertions (`mutation_audit.log`).

The γ₁₆ allowance for equatorial/polar known answers is conservative for these tested normal values: r², s² and the relevant pole factors have exact simplifications, and coefficient, denominator, final products and independently rounded rational reference require fewer than sixteen compounded rounding factors. Including reference rounding and comparison rounding leaves margin within 2γ₁₆. This is not a global relative bound near cancellation surfaces.

For the gradient bound, graph path counts alone are insufficient: denominator reuse, division, cancellation, the computed majorant and the final comparison must be included. I inspected the earlier rational interval construction and extended it to the dense grid, with outward dyadic enclosure to control denominator growth. Each basic operation encloses relative error u plus half a minimum-subnormal unit; square roots are enclosed by integer-square-root rational brackets; subtraction and the computed right-hand side are included. All components at all 5,904 dense-grid positions are certified, with maximum enclosed-error/minimum-computed-bound ratio 0.4114583333333321. The original 162-point gate also certifies with the same maximum ratio (`interval_original_grid.log`). Reversing J2 reverses the ordinary evaluations exactly and leaves their absolute majorants unchanged, so the certificate applies to both signs. Recounted graphs have 25 operations/depth 8 for production, 27/depth 8 for its absolute expression, and 123/depth 16 for either dual evaluation (`path_counts.log`); the stated 13/40 path limits are conservative. This is a finite-domain, conditional arithmetic certificate, not external physics corroboration or proof of Python/libm conformance.

The mutation harness deletes the prior JUnit file before each subprocess, preventing stale-file reuse. It distinguishes failure/error nodes and checks assertion/DID-NOT-RAISE messages on this environment. My synthetic `pytest.fail("external worker unavailable")` is **not** classified as an assertion. Its fallback accepts type `Failed` indiscriminately if another XML producer supplies that type; this is a portability limitation, not evidence that a current kill is false. Current JUnit type attributes are empty and actual messages establish the kills. The infinite-parameter mutant is killed only by its diagnostic mismatch; the coefficient check already rejects those values, as disclosed.

Three additional mutants survive all 73 T1 cases (`own_mutants/results.json`; exact patches and JUnit files retained):

- A one-ulp coefficient perturbation confined to μ > 1e10, avoiding the synthetic μ = 1 exact-answer tests.
- A `1e-8` x/y factor error confined to `0.123456 < s² < 0.123457`.
- Returning all zeros whenever `0 < |k| < 2·MIN_NORMAL`.

These demonstrate finite sensitivity and missing extreme-parameter coverage. The records explicitly restrict completeness to the 32 named defects, so survival alone is not an additional acceptance defect. The actual production counterexamples below independently establish the remaining defects.

Ordinary attribute assignment, deletion and new attributes fail; base instances lack `__dict__`, and `vars()` fails. `copy`, `deepcopy` and pickle round trips currently fail with `AttributeError`; no copy/pickle support is promised, so I do not classify failure as an invariant violation. A normal subclass gains a dictionary, but a dictionary entry named `mu` does not override the inherited slot. Subclass method/property overrides, class monkey-patching, direct slot-descriptor writes, `object.__setattr__`, and explicit reinitialization are deliberate object-model bypasses rather than supported parameter updates. Class-level `name`/`version` mutation changes metadata, not the values used in the force formula. This is not a frozen dataclass; `dataclasses.replace` supplies no supported update path. NumPy float64 inputs behave like native floats; accepted float32/longdouble inputs retain their different arithmetic types. Accepted zero-dimensional arrays are a distinct ordinary input-alias path, addressed below.

## New findings

### M3T1-R2-F1 — MINOR — unchecked component-product underflow

**Defect; VERIFIED by execution and exact-rational reasoning.** Location: `src/tars/sim/forces.py:138–144`, especially line 142; the claimed domain is at lines 84–91 and `docs/science/validation.md:1123–1130`.

Reproduce with native Python float parameters:

```python
m = ZonalJ2Gravity(5.1827254193540115e-108, 1.0, 0.5)
r = np.array([1e40, 0.0, 4.9999999999999995e39])
m.acceleration(0.0, r, np.zeros(3))
```

The result is `[-0.0, -0.0, -2.2250738585072012e-268]`. The checked intermediates are normal: `k0 = −3.8870440645155084e-108`, `r5 = 1.7469281074217106e200`, `k = −2.2250738585072014e-308`. But `c = 2^-53`; `k*c` rounds to zero before multiplication by x. The exact acceleration's x component rounds to **`−4.303918780958246e-284`**, a normal binary64 value. `certificate.py` brackets √(x²+z²) using exact rationals and integer square root; both enclosing acceleration endpoints round to that same value. This is not based solely on a sweep or on Decimal agreement.

**Consequence:** the stated r⁵/k/result checks are insufficient to eliminate silent numerical-domain loss. This case passes the enumerated contract, but an intermediate product underflows and a representable component disappears. It is far outside physical orbital parameters, so severity is limited; no realistic-orbit regression is demonstrated.

**Recommended correction:** define and enforce the component-product domain too, or evaluate those products without avoidable intermediate underflow. Add off-axis tests with extreme but accepted parameters and both component cancellation factors. Preserve realistic-orbit results. Update the contract/evidence accordingly. **Requirement:** I-19 §§4,11(3),(10), DR-0024 R6. No unrelated force-model policy decision is needed.

### M3T1-R2-F2 — MINOR — accepted numerical inputs escape immutable binary64 ownership

**Defect; VERIFIED.** Location: `src/tars/sim/forces.py:100–115`, especially unconverted reference storage at 113–115; downstream arithmetic at 137–142.

```python
mu = np.array(398600441800000.0)  # zero-dimensional numerical array
m = ZonalJ2Gravity(mu, 6378137.0, J2)
mu[...] = -1.0
m.acceleration(0.0, np.array([6378137.0, 0.0, 0.0]), np.zeros(3))
```

Construction succeeds. Without assigning any model attribute or invoking a bypass, `m.mu` becomes −1 and the call returns finite outward acceleration `[3.991922438949618e-17, 0, 0]`. Setting the original array to zero silently removes the perturbation. The same alias exists for R and J2; mutable R can become negative after validation (`probe.log`, `parameter_boundary.log`).

Accepted NumPy float32 parameters also keep float32 arithmetic and return a float32 acceleration. Comparing the same three parameter values converted to Python floats gives equatorial x values `−0.01591181941330433` versus `−0.015911820615666403`, a relative difference about `7.56e-8`. This exceeds binary64 roundoff bounds and is not explained by initial float32 parameter rounding, because the comparison uses exactly those same input values. Longdouble inputs likewise produce a different result dtype (`extra_checks.log`).

**Supported-path judgment:** ordinary accepted numerical arguments and mutation of the caller's own array are within the ownership boundary a constructor must handle. There is no documented runtime type rejection or scalar-copy requirement. The `float` annotation alone neither enforces binary64 operations nor prevents accepted mutable objects from remaining aliased. This differs from intentionally overriding the class or invoking `object.__setattr__`. The stale-cache disagreement is fixed, but the explicit immutable-and-validated parameter requirement is not fully met.

**Recommended correction:** establish immutable binary64 scalar ownership before validation/arithmetic, or explicitly reject unsupported numerical types. Test caller-alias mutation and accepted NumPy scalar types. **Requirements:** packet §3 item 2 (`M3-T1-authorization-packet.md:36`), I-19 §§3–4 and §11(2)–(3). This is a parameter-boundary correction, not new physics.

### M3T1-R2-F3 — NOTE — correction experiment claims trajectory coverage it does not execute

**Documentation defect; VERIFIED by source inspection.** Location: `docs/science/experiments/m3-t1/t1_review01_correction_check.py:4–6`; compare its complete `main`, lines 70–145.

The module says its bit-identity check includes committed RK4 trajectory states. The actual loop checks 200,000 random states and four axis states, and no trajectory is loaded or propagated. The result file consequently contains no trajectory comparison. **Consequence:** this script's evidence scope is overstated. My separate three-trajectory execution establishes additional local evidence but does not retroactively make this script's claim true.

**Recommended correction:** remove the trajectory clause or actually perform and record that comparison. **Requirement:** I-19 §11(10), reproducible validation provenance. Nonblocking clarification; no unresolved owner decision.

## I-19 §11 assessment, items 1–10

1. **R1-F1–F4 resolution:** partial for F1/F2, resolved for F3/F4, as separately tabulated. Original reproductions are corrected; broader requirements have remaining counterexamples.
2. **Immutability invariant:** stale caching and standard reassignment paths are corrected. Caller-owned accepted numerical arrays remain mutable; binary64 ownership is not established. Copy/pickle failures and deliberate Python bypasses are distinguished above.
3. **Numerical domain and realistic behavior:** original failures now raise the documented classes of `ValueError`. The remaining final-product hole is R2-F1. On the canonical equator, bisection independently reproduces **3.3773820261812166e-57 ≤ x ≤ 4.476546622757235e61 m**. The upper boundary is r⁵ overflow. At the lower boundary k is still normal (about −5.99231e307); the next smaller x overflows `k*3` before multiplication by the zero z coordinate, producing a rejected NaN. Thus the lower boundary is the component-expression order, not coefficient-division overflow (`boundary_reason.log`). Monotonic arithmetic on this equatorial ray supports the adjacent-float bisection. Zero J2 still checks position/r⁵ and rejects pathological radii as documented. Signed origin, subnormal and non-finite off-axis probes raise appropriately. Realistic acceleration and trajectory bits are unchanged in my executions.
4. **r⁻³ statement:** mathematically correct, assertion unchanged, experimentally consistent.
5. **Mutation correction:** all previous survivors now fail meaningful assertions; counts are 14 original + 8 reviewer + **10** protection removals (3 F1, 7 F2). The appended correction supersedes the earlier “11”; the separate earlier table's “8 F2” is also inaccurate—the actual count is seven. The current total 32 is correct. No claim of all-defect coverage is justified or made in the correction section.
6. **Dual-number disposition:** the new DR-0025 note accurately records every owner rationale and limitation, verbatim in substance, and is append-only. It is a partially independent unit-level derivative check sharing constants, physics conventions, scalar arithmetic and sqrt. It is neither external corroboration nor proof of IEEE rounding. Some old “no libm assumption” wording is too terse in isolation, but the explicit correctly-rounded-operation assumption and new owner note supply the qualification. I do not treat that conditional guarantee as another defect or re-decide the owner’s disposition.
7. **Sign erratum:** correct. Original packet wording is preserved; appended differentiation matches my independent derivation, production, VAL-0020 and gradient tests. It changes documentation, not physics.
8. **M1/M2 regression:** locally supported by the full-suite result, validators, byte-identical golden/determinism, unchanged protected artifacts and unwired additive source. Historical wrapper and cross-platform execution authenticity remain limits.
9. **Scope:** compliant. The protected-path diff from `60648b9` is empty. The only source changes are `constants.py` (+58) and `forces.py` (+84), confined to the J2 class and required imports/constant. Existing force implementations are unchanged. No production consumer instantiates J2; no T2–T5 functionality, dependency, workflow or scenario-v3 work was introduced. `1cf0ce9` changes only two documentation files.
10. **New correctness/provenance defects:** R2-F1–F3 above. Prefix comparisons establish append-only preservation of DR-0025, packet, report, decision matrix and VAL-0020; the review record is a strict extension of `dbb960a`, and raw Review 01 files are unchanged after that commit. The milestone README extends its existing row without deleting its prior history. Corrected mutant/test counts and reproduced informational/correction outputs support the numerical records within their stated scope.

## Verification limits and acceptance readiness

All new numerical observations are from this one host. The interval and rational certificates are conditional on the explicitly assumed arithmetic model; they are not proofs of CPython/libm conformance. Random/grid/trajectory sampling establishes results only for the executed states. No network, live CI authentication, independent cross-platform execution, GMAT executable, or external physics implementation was available. I did not authenticate historical local wrapper runs, unseen measurements before tolerance selection, remote refs, branch protection or source-standard provenance. Repository-local authorized constants are the basis of the identity check.

The secular comparison remains informational: the reproduced critical-inclination rate is about 0.0112°/day, and convergence orders about 4.68/4.52 do not establish an approved timestep or a rigorous absolute trajectory error. The approximately dt⁵ invariant drift remains an unexplained observation. Potential/energy oracles share constants and conventions; the invariant ratio has finite sensitivity, as the surviving mutants demonstrate.

DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular tolerance/presentation, T4/T5 comparison requirements, final M3 timestep and T3 axis representation remain unresolved. I have approved none of them.

The ordinary-domain J2 physics and M1/M2 isolation are supported. **T1 is IMPLEMENTED — NOT REVIEW-ACCEPTED — NOT MERGED, and is not acceptance-ready.** The two MINOR defects require correction or return to the owner for direction. I made no fixes and started no further review. Final tracked status and diff are empty; all reviewer artifacts are in excluded scratch.

VERDICT: REQUEST_CHANGES