# M3 T1 Independent Codex Review 01

Review of `milestone-3-t1-j2-force-model` at **97b69ef92e589ebd1b71016f49c4c9816d8c724b**, under I-18. I reviewed the implementation independently and made no tracked changes. There are **two MINOR defects and two NOTEs**, with no BLOCKER or MAJOR finding. The ordinary-domain acceleration is physically correct; the defects concern parameter immutability and unguarded numerical domain loss.

## 1. Revision, environment and evidence ledger

The checkout is detached at the pinned SHA. Its local `origin/milestone-3-t1-j2-force-model` tracking ref equals that SHA; `main` and `origin/main` equal `60648b93385a9954194730006aeac29ea14875ad`. These are local Git observations, not an authenticated remote fetch. The four T1 commits are `5fd24a2366ba116eac2b5de824da1a76b1f888cf`, `e23675c5e0147b43ef74db3292004b343574032d`, `81a0d5671089e29b6b0cb50bdb376193c67b5eff`, and the pinned HEAD. No reviewer commit, push, merge or fix was made. Initial and final tracked status/diff are empty.

Environment: macOS 26.2, Darwin 25.2.0, x86_64; CPython 3.12.15, Clang 22.1.3; NumPy 2.5.3, SciPy 1.18.1, Pydantic 2.13.5, pytest 9.1.1, Ruff 0.16.10. Hardware reports MacBookPro16,1, eight cores at 2.3 GHz. The exact CPU model is unavailable: the utility reports “Unknown” and the CPU-brand sysctl is sandbox-denied. I do not substitute the implementer's reported i9 model for an independent observation. Python reports radix 2, 53-bit precision and round-to-nearest. Precise build details are in `review_scratch/environment.json`.

The command ledger is `review_scratch/COMMANDS.md`; executed validation commands and exits are also in `review_scratch/checks-ledger.txt`. Reviewer scripts, individual mutant trees and complete failure logs are retained in scratch. This report is the raw reviewer assessment; `review_scratch/raw-reviewer-output.md` contains the identical assessment. These scratch records preserve the repository's existing historical records without modifying them, as specifically required by this review prompt.

Executed results:

- Full pytest: **1207 passed, 3 warnings in 1717.76 s (28 min 37 s), exit 0** (`pytest.log`).
- T1 files: all **26 cases pass** in the unmutated mutation control; additional complete passes are recorded for surviving reviewer mutants.
- Ruff check and format check: pass; 231 files already formatted (`ruff.log`).
- T0 checks: **314 passed in 190.77 s** (`t0.log`).
- M1 validator: **7/7**; golden comparison and cross-process determinism also pass. Position/velocity differences are zero; bit identity is true. Both process hashes equal `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` (`m1.json`, `m1_golden.log`, `m1_determinism.log`). This is not a claim that I ran the prohibited nine-step Proof shell script.
- M2 validator: **228/228**, approved thresholds, overall PASS (`m2.json`, `m2.log`). I did not rerun the prohibited twenty-step wrapper or generate GMAT output.
- Both committed T1 experiments rerun to scratch: control passes; **14/14 mutants detected**. Parsed informational and mutation JSON are exactly equal to the committed files (`info.json`, `mutation.json`, `records_audit.json`).
- Separate reruns preserve assertion-failure logs for all fourteen built-in mutants (`builtin_details.json`); none relies on import/infrastructure failure.
- Reviewer Decimal, interval, contract and adversarial computations are in `adversarial.json`, `interval_bound.json`, `contracts.json`, `path_counts.log`, `own_mutants.json` and `pm_drift.json`.

Inspected result files include both committed `docs/science/experiments/m3-t1/*results.json`, their two scratch reproductions, both validator JSON reports, all six supplied CI files, `ci_audit.json`, and the reviewer results listed above. Authority/code reads and output-size limitations are itemized in the command ledger. I inspected the applicable resolutions of DR-0024–0029, the P10 packet, ADR-0003/0004/0009, the T1 packet, SCI-0013 including its updates, VAL-0018/0020, the milestone scope/impact documents and Proof requirements. Documentary intent or historical execution is distinguished below from locally reproduced evidence.

### Supplied CI evidence

All three exports name the expected branch, revisions and four successful jobs: run 39852509134 at `e23675c`, 39853032093 at `81a0d56`, and 39865621259 at HEAD. The three excerpts for the first run match job IDs 120082120540, 120082120734 and 120082120957 and report twelve constant tests, fourteen J2 cases, and 1204 passed/3 skipped. The checked test code would establish the pinned constant's bit pattern if those excerpts are authentic.

There is a timestamp inconsistency in the final Intel metadata: setup begins at 22:31:44Z and checkout at 22:31:47Z, before the enclosing job's 22:31:51Z start; setup also precedes the run's 22:31:47Z creation. A clock/reporting discrepancy could explain this, but I cannot establish its cause. SHA/job/result identities otherwise agree. **CI authenticity and cross-platform execution are not independently verified.** This limitation does not prevent the local review, as the prompt explicitly directs.

## 2. Assessment A — physical correctness

Using the supplied fully normalized convention, `P̄20 = √5 P2`, so `C20 = √5 C̄20` and `J2 = −√5 C̄20`. A negative canonical C̄20 therefore gives positive J2. The production constants preserve the approved WGS84 μ and a; they do not adopt EGM2008's different scaling radius/GM. This implements the selected model rather than the complete EGM2008 field.

My independent derivation starts with `A = μ J2 a²/2` and `U2 = A(r⁻³ − 3z²r⁻⁵)`. Differentiating with respect to x gives `A(−3xr⁻⁵ + 15xz²r⁻⁷)`; y is analogous; z gives `A(−9zr⁻⁵ + 15z³r⁻⁷)`. These reduce to the production expression. With positive potential U, acceleration is **+∇U**. The negative-gradient wording in the historical packet's test table would instead apply to potential energy −U; I have not adopted that sign error as an oracle.

The coefficient has units m⁵/s², division by r⁵ and multiplication by a coordinate give m/s², and the symmetry axis is frame +Z. At the reference equator, acceleration is `−1.5 J2 μ/a²` along x; at the north pole it is `+3 J2 μ/a²` along z. Point mass is evaluated separately. The code's signs, off-axis dependence and zero-J2 algebra are correct in its ordinary numerical domain. My 100-digit Decimal comparison at all 162 test points found the acceleration error no larger than 0.033281 of the committed comparison allowance; this is supplementary measurement, not a proof.

The radial scalar is `a2·r = −(3/2)J2 μa² r⁻³(1−3sin²φ)`. Thus the radial **projection** changes sign at `asin(1/√3) = 35.26438968…°`. The production test checks the correct sign, but its docstring misstates the power for the dot product (F3).

The edge probes establish the numerical limitation in F2. At finite exterior `[1e70,0,0]`, the model returns zeros although the true equatorial acceleration is approximately `−2.6332691079270825e−255 m/s²`, representable in binary64. For `[1e200,0,0]` zero is consistent with final underflow, but that does not excuse the earlier 1e70 failure. At `[1e−100,0,0]` a denominator underflows and raises `ZeroDivisionError`; a minimum-subnormal coordinate is classified as the origin because its square rounds to zero. These interior positions are outside the external-field physical domain. NaN/∞ coordinates propagate non-finite results; infinite μ or a pass constructor validation and yield infinities/NaNs. The origin itself correctly raises ValueError. These probes are not evidence of failure on the measured LEO domain.

## 3. Assessment B — numerical correctness

Local rational tests establish nearest rounding for the actual `sqrt(5)` result and for the product of that binary64 value with the stored binary64 C̄20. The resulting J2 is `0.0010826261738522227`, hex `0x1.1bcdd00abd9aap-10`. I independently computed the display gap: **220334 ulps**, relative **4.413094884310988e−11**. The check concerns the staged binary64 derivation, not correctly rounding the exact real expression from an infinitely precise decimal coefficient in one operation.

IEEE 754 defines correctly rounded square root and multiplication when implemented conformingly in the assumed mode. Python's language-level contract does not establish every platform's libm accuracy. CPython's scalar sqrt remains a platform math-library operation. Consequently, the unconditional “does not depend on libm” wording in the source must be read with the report's explicit correctly-rounded-operation assumption. Testing sqrt(5) proves this input locally; it does not prove every sqrt used in the force or dual oracle on every platform. No project-wide Q-G2-2 rule is inferred.

I independently recounted the scalar graph, including zero-valued dual-gradient paths: production acceleration **25 scalar operations, maximum path depth 8**; its absolute evaluation **27/depth 8**; ordinary and absolute dual evaluations each **123/depth 16**, including the coefficient. Thus “≤13/≤40 along a path” are conservative counts, not total-operation counts. Path depth alone is insufficient to prove the stated general graph theorem: reused denominator errors, divisions, cancellation, and the rounding of the computed majorant/comparison need treatment too.

I therefore checked the actual finite gate domain with a separate **exact-rational interval argument**, not a measured error sweep. Each operation encloses all roundings by relative `u = 2⁻⁵³` plus an absolute `2⁻¹⁰⁷⁵` allowance; rational square-root brackets use integer square root. The script separately encloses the production expression, ordinary dual gradient, both absolute evaluations, subtraction and rounded right-hand-side computation. All 162 input triples and all components satisfy the gate even with independent worst-case operation errors: the maximum upper-error/lower-bound ratio is **0.4114583333333321**. Exact zero components remain zero. This supports this gate on its actual inputs, conditional on the stated floating-point model; it does not establish a global bound for arbitrary states or validate the generic Higham attribution as worded.

For the equator/pole known answers, r², sqrt(r²), s² and the pole's factor −2 are exact at the particular integer reference radius. The non-exact coefficient/denominator/final-product paths require at most eight rounding factors; the separately evaluated expected result at most three. Including the comparison leaves ample margin inside `2γ16`. A naive independent interval evaluation without exploiting these exact operations was inconclusive at the pole, not a counterexample; the ledger records that exploratory result.

The exact assertions have computational explanations within the tested finite domain:

- The quarter-turn changes signs and swaps x/y; squares are unchanged and only the first two addends commute. It does not require reassociating a three-term sum. Negation is exact and signed multiplication gives the required rotated signed zeros.
- Reflection preserves r² and s² and reverses the z factor. Its assertion uses numerical array equality, which does not distinguish zero signs.
- J2=0 gives signed zeros without NaN intermediates. Both compared composites start from positive zero; adding zero to finite nonzero point-mass components is exact, and zero components already have the composite's canonical zero behavior. Identical RK4 arithmetic then preserves the 600-step bit identity.
- In the x-z plane both forces have zero y acceleration. RK4 stages preserve `y = vy = 0`; the test asserts numerical zeros, not identical signed-zero bytes.

Those arguments do not extend through overflow/NaN. An additional falsification search used 5000 seeded random exterior points within the tested radial range and nine points at/adjacent to the x/y cancellation surface x=2z, y=0: no gradient-bound violation, maximum utilization 0.052547 (`bound_falsification.json`). This is a measurement, not a proof. I found no ordinary-domain counterexample to the exact assertions. F2 records the missing numerical-domain protection rather than treating finite-sample exactness as a global guarantee.

## 4. Assessment C — scientific validation

The known answers and independently coded potential exercise different algebra from production. The potential and energy still share constants and physical conventions with production, so their evidence is partially independent, as DR-0025 requires; they cannot authenticate coefficient provenance or eliminate a shared physics misunderstanding.

Energy `v²/2 − μ/r − U2` is conserved analytically because the field is autonomous and conservative. Axial angular momentum is conserved because x/y accelerations share a scalar factor. The ratio test is a useful truncation-sensitive regression check, not a proof that every non-conservative implementation must fail at these two steps. Small defects can sit beneath truncation, and defects outside the trajectories are invisible.

The measured energy drift ratios at 28.5°, 51.6° and 97° are respectively **0.0011993656, 0.0012045268, 0.0012161136**; h_z ratios are **0.0009746358, 0.0009725186, 0.0009811114**. They reproduce the record. The 1/2 boundary predates the committed production implementation and has a defensible asymptotic motivation. Neither Git nor the exports can establish that no private measurement preceded it. Big-O fourth-order convergence does not itself prove a finite-step ratio, universal detection sensitivity, or a global error bound.

The reported approximately fifth-order invariant drift is **an unexplained observation, not a demonstrated J2 defect**. My point-mass-only control gives energy orders 4.8932/4.8033 and h_z orders 5.0000/4.9976 at 20/10/5 s. This demonstrates the behavior is not specific to the J2 implementation. It does not establish its mechanism in the nonlinear J2 integrations. I do not promote the report's suggested explanation into a result.

All informational result fields reproduce exactly. The 30-orbit horizon is 175910 s, about two days; the seven secular cases span 28.5°–150°. The printed node discrepancies −0.27%…+0.26%, perigee discrepancies below 1% away from critical inclination, and critical-inclination rate approximately 0.0112°/day agree with the result file. The inclination used is 63.4349°, not the exact critical angle, so first-order theory gives a small nonzero rate. Osculating-element fits and time averages of osculating elements are not an exact mean-element transformation. No secular acceptance tolerance is justified or introduced here.

The reproduced convergence differences are **123.051048, 4.801722, 0.209886 m**, orders **4.67956/4.51588**, and Richardson estimate **0.223878 m** at 10 s. The estimate assumes fourth-order asymptotics; it is not an independently measured absolute position error. These figures, invariant orders/drifts, orbit parameters and gradient utilization (0.0357132, printed as 3.6%) support the rounded numeric statements in VAL-0020/report/README. SCI-0013's new update makes no additional numerical validation claim. Historic Proof and cross-platform claims retain the limitations already stated.

## 5. Assessment D — derivative-method substitution

1. **Same mathematical derivative? Yes.** Dual multiplication, quotient and sqrt rules differentiate the separately expressed U2 with respect to Cartesian coordinates. This is the intended acceleration derivative. Unlike a finite complex step, dual arithmetic has no step-size truncation term.
2. **Sufficient independence? Yes for a partially independent unit oracle.** The potential is separately coded; generic differentiation replaces manually coding its acceleration. It shares μ/a/J2 and normalization assumptions. Decimal comparison and the rational interval argument add independent arithmetic checks, not external physical provenance.
3. **Avoids additional unverified assumptions? Only partly.** It removes complex-sqrt behavior and step-size choices. It adds custom dual arithmetic and still assumes scalar arithmetic/sqrt behavior. “No libm assumption” is too broad if it includes scalar sqrt. The local certificate and tests check the relevant implementation, not all platforms.
4. **Meets/exceeds intended strength? In my technical assessment, it meets the intended sampled, partially independent gradient check under the stated scalar floating-point assumptions.** The independent interval result supports the selected allowance. It does not exceed the independence class or establish correctness outside the samples.
5. **Decision amendment required? Yes, an explicit owner disposition/amendment should record the replacement**, because DR-0025 Q3 and the T1 packet specifically name complex step. I recommend considering dual numbers with qualified assumptions and evidence. **I neither amend DR-0025 nor accept the substitution on the owner's behalf.**

## 6. Assessment E — architecture and regression isolation

`ZonalJ2Gravity` structurally conforms to `acceleration(t,r,v)` and returns a three-vector. It reads position and constructor configuration only, has no mass/context/orientation dependency, does not mutate input state, and performs no I/O. It is unwired: production searches find definitions, not runner/scenario instantiation. Simulator consumers continue to use the unchanged protocol, including coast and burn paths. Parameter immutability, however, is not implemented (F1).

The protected-path diff is empty. Across `src proof toolbox scenarios .github uv.lock pyproject.toml`, the only changes are **constants +58/−0 and forces +39/−0**. Existing point mass/composition, validation, schemas, runner, workflows, dependencies, lockfile and protected artifacts are unchanged. T2–T5 production work, v3 scenarios and M3 Proof are absent. Local M1 golden/determinism and M2 validation support isolation; they do not authenticate earlier wrapper executions or remote CI.

Historical scientific entries and decision records are preserved. SCI-0013 gains a status insertion; VAL-0020 is appended; authorization/decision-matrix status notes are appended. The milestone README modifies its existing row only by adding a dated continuation retaining prior text. This is a logical append within the row, not a literal end-of-file-only append. I found no substantive historical rewrite.

## 7. Assessment F — tests and adversarial attempts

All fourteen committed mutants fail actual assertions: reversed sign, 1.4 coefficient, wrong z factor, wrong latitude coefficient, x/y asymmetry, z scaling, radial denominator perturbation, axis permutation, zero-J2 offset, decimal sqrt5, perturbed sqrt5, J2 sign, final C̄20 digit, and rounded-decimal J2. The “power” mutant perturbs denominator magnitude; it is not a changed radial exponent. The “axis” permutation also alters component interpretation, so it is not a comprehensive correctly transformed tilted-axis test.

My eight additional file-level mutants yield:

- **Detected:** unnormalized C̄20 used in place of J2 scaling; μ/radius swap; replacing the x/y latitude coefficient 5 by 3; a 1% x/y error restricted to `0.36 < z²/r² < 0.37`. The last is caught by the invariant test, despite missing the static gradient grid.
- **Survive all 26 cases:** forcing negative J2 positive; multiplying the coefficient by `1 + 2⁻⁵¹`; returning zero beyond seven reference radii; and a 1% x/y error restricted to `0.99 < z²/r² < 0.9999`.

The high-latitude survivor is wrong inside the sampled radial range, between the static latitude samples, while the polar test checks only plane invariance. These are concrete demonstrations that test success is not a proof of the complete field. Near-roundoff survival is expected for a tolerance-based check. None of these injected defects is present in the reviewed production expression.

The source-literal guard is a regular-expression heuristic. A value encoded with `float.fromhex('0x1.1bcdd00abd9aap-10')` bypasses its decimal pattern; source review, not that test alone, establishes the current architecture. The unchanged `EARTH_J2_APPROX` is the historical informational constant, not a newly introduced authoritative M3 value. The canonical/derived class structure is correct; the frozen constant set and exact-rational/pinned-output tests go beyond simply comparing two calls to the same expression.

## 8. Findings register

### M3T1-R1-F1 — MINOR — mutable parameters violate the stated component contract

**Type:** defect. **VERIFIED.** References: `src/tars/sim/forces.py:86`–89; `docs/milestones/M3-T1-authorization-packet.md:36` explicitly requires immutable, validated constructor parameters.

Reproduction: instantiate the canonical model, evaluate at `[a,0,0]`, then assign `model.j2 = 0`. Assignment succeeds, but acceleration remains `[-0.01591182047796651,−0,−0]`, while a freshly constructed zero-J2 model returns zeros. μ and radius are writable too; cached `_k` remains unchanged. See `contracts.py`, `contracts.json`.

**Consequence:** externally visible configuration can disagree with the force evaluated, contrary to the immutable component scope and future identity expectations. The component is unwired, limiting current impact.

**Recommended correction:** enforce immutability of the new force configuration and cached coefficient, and test rejected parameter reassignment. Do not change legacy point-mass behavior or introduce T2/T3 machinery. Relevant requirements: authorization packet §3/§8, I-18 §3E and ADR-0009's pinned model-configuration principle.

### M3T1-R1-F2 — MINOR — silent numerical-domain loss for finite exterior inputs

**Type:** defect. **VERIFIED.** References: `src/tars/sim/forces.py:82`–89 and 93–100.

Reproduction: canonical parameters and `[1e70,0,0]` produce exact returned zeros because `r2*r2*r_norm` overflows, although the correct x acceleration is a representable `−2.6332691079270825e−255`. Infinite μ/radius are also accepted and generate non-finite accelerations. `adversarial.py` records both behavior and a 100-digit independent equatorial calculation.

**Consequence:** callers can receive plausible zero gravity after intermediate overflow rather than final physical underflow, with no documented/enforced numerical-domain restriction. This is outside demonstrated mission scales and does not invalidate the LEO results.

**Recommended correction:** use appropriately scaled evaluation or explicitly define and enforce a supported finite numerical domain; reject non-finite configuration/state inputs rather than silently producing invalid results. Add boundary tests for that contract. No new physical model or later-task integration is needed. Relevant requirements: DR-0024 R6 (explicit domain), I-18 §3A/B (large-r, overflow and parameter behavior).

### M3T1-R1-F3 — NOTE — radial dot-product docstring has the wrong radius power

**Type:** nonblocking documentation clarification. **VERIFIED.** Reference: `tests/test_zonal_j2.py:236`.

The documented `a_J2·r ∝ μa²/r⁴` has acceleration units; the dot product has specific-energy units and is proportional to `μa²/r³`. The r⁻⁴ expression belongs to `a_J2·r̂`. This follows directly from the derivative in §2 and is independently checkable algebra. The sign test itself is correct.

**Recommendation:** correct the scalar description or use the unit radial vector. Relevant requirement: I-18 §3A, dimensional correctness. No production error is inferred.

### M3T1-R1-F4 — NOTE — mutation success has finite input/parameter coverage

**Type:** proposed test enhancement. **VERIFIED.** References: `tests/test_zonal_j2.py:129`–143, 178–192, 274–290; `tests/test_constants.py:127`–139; `docs/science/experiments/m3-t1/t1_mutation_check.py:29`–115.

The four surviving reviewer mutants and their complete passing logs provide concrete counterexamples to interpreting 14/14 detection as broad correctness certification. The decimal-only literal pattern also misses equivalent hex encoding. See `own_mutants.py`, `own_mutants.json`, and `contracts.json`.

**Consequence:** wrong parameter handling or unsampled latitude/radius behavior can escape current tests. No such error was found in ordinary-domain production algebra.

**Recommendation:** consider signed/parameter-scaling cases and additional deterministic latitude/radius coverage, and describe literal scans as heuristics. Retain the reported mutation result as evidence for its fourteen named cases. Relevant requirements: I-18 §3F and DR-0025 VO-8. Exhaustive testing or zero rounding tolerance is not requested.

## 9. Unresolved assumptions and decisions

Each T1 report §9 item is assessed separately:

1. **Secular-rate tolerance:** genuinely unresolved; informational treatment complies with I-17 §8. First-order/osculating mismatch needs a derived error budget before gating. No tolerance is chosen here.
2. **Operation counts:** the path-count upper limits are conservative in my recount. A path count is not the whole numerical proof; my finite-domain interval certificate independently supports the actual gradient gate. A general all-state bound is not established.
3. **IEEE correct rounding:** conditional numerical assumption, locally checked for the constant operations and used explicitly by the interval model. Whole-libm or cross-platform correctness is not proven. The report acknowledges the condition; source wording should remain qualified when reused.
4. **Dual substitution:** technically suitable at the intended evidence class, but explicit owner disposition remains necessary. No acceptance or amendment is made in this review.
5. **Axis representation:** fixed +Z correctly implements T1. Configuration representation remains T3 scope; no configurable axis is added or selected.
6. **Fifth-order drift:** reproduced observation, also present without J2. It is not a physical correctness defect; its detailed mechanism remains unestablished here.
7. **No external comparison:** correctly disclosed T1 limitation. I did not run GMAT, create a T4 validator, or claim external trajectory validation. Later comparison requirements remain unchanged.
8. **Q-G2-2:** remains proposed. Local identity tests do not approve a project-wide replacement for trajectory validation.

Additional limitations are F1/F2's mutable/numerical-domain contracts; the finite sensitivity of the invariant ratio; partial correlation of potential/energy/constant oracles; unauthenticated CI and source provenance; and the asymptotic assumptions in the Richardson estimate. P1–P9, Q-G2-1/P6, DR-0028 P6(b), final M3 timestep and T4/T5 requirements remain unresolved as before.

## 10. Verification limits and readiness

All local evidence is from one x86_64 host and the provided locked environment. Decimal results are independent high-precision computations, not directed-rounding proofs; the separate rational interval argument supplies the bounded sampled-domain claim under explicit arithmetic assumptions. No sweep is treated as a global proof. No local NGA standard or Higham source was available to reauthenticate the cited table/theorem; the canonical literal is verified against the authorized value, and normalization/sign are derived independently. No network or GMAT was available. Historical test-first intent, pre-branch CI, old wrapper executions, live remote state, branch protection and other platforms cannot be authenticated from this clone.

The ordinary-domain physics, additive isolation, recorded measurements and substantial test evidence are sound. **T1 is not acceptance-ready until F1 and F2 are dispositioned and corrected or explicitly returned for owner direction.** The derivative-method change also needs the owner's explicit disposition. No acceptance recommendation is issued, no finding is fixed, and Review 02 is not started.

VERDICT: REQUEST_CHANGES

**T1 STATUS: IMPLEMENTED — REVIEWED — NOT ACCEPTED — NOT MERGED.**
