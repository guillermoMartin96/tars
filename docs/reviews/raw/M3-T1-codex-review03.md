# M3 T1 Review 03

Reviewed **4b85ded298e521f5c72b606cd012dec8b56e9c5e**, detached from `milestone-3-t1-j2-force-model`; baseline `main` **60648b93385a9954194730006aeac29ea14875ad**. This was an independent, review-only examination. No tracked file was changed. The eight correction-pass commits are `56ad329`, `bbcf40e`, `304d796`, `308f126`, `a4dfda1`, `2f82c00`, `c456881`, `4b85ded`.

All eight prior findings are **RESOLVED**. I found no blocking, major or minor implementation defect. There are two nonblocking documentation/provenance notes below. The verdict is not conditional on a later test, fix, approval or relaxation of an acceptance criterion.

## 1. Environment and evidence ledger

Own execution used macOS 26.2 / Darwin 25.2.0, x86_64; CPython 3.12.15, Clang 22.1.3; NumPy 2.5.3, SciPy 1.18.1, Pydantic 2.13.5, pytest 9.1.1, Ruff 0.16.10. `platform.processor()` reports `i386`; the sandbox denied `sysctl machdep.cpu.brand_string`, so a physical CPU model is not independently established. I used the supplied `.venv`, with no network or dependency changes.

`review_scratch/COMMANDS.md` and `review_scratch/INSPECTION_COMMANDS.md` contain the command ledger; `run_checks.py` preserves the batch runner; `RESULTS_INSPECTED.md` inventories result files. Scripts, raw logs, mutant diffs and JUnit XML are retained under `review_scratch/`. Commands embedded in the saved scripts are part of this ledger. Key independently executed results:

- Full `pytest -q -p no:cacheprovider`: **1288 passed, 3 warnings in 1725.99s (0:28:45)** (`full_pytest.log`).
- Both T1 test files: **107 passed** (`check_04.log`). Final tests against archived `b1566ae` source: **26 failed, 81 passed** (`own_mutants/redfirst.log`), confirming the claimed red-first behavior, though not authenticating the implementer's historical execution.
- T0 `check_review0*.py`: **314 passed** (`check_10.log`).
- M1 validator: **7/7 PASS** (`m1.json`); golden comparison: **bit-identical**, zero position/velocity difference (`check_12.log`). Cross-process event digest: `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` in both processes (`check_13.log`).
- Cross-process determinism: PASS for all four `scenarios/m2_*.json` (`check_14.log` through `check_17.log`). M2 validator: **228/228 PASS**, six missions, approved thresholds (`m2.json`). Local six-mission platform record collected (`m2_platform.json`); this is not a three-platform execution.
- Committed mutation campaign: **46/46 killed by meaningful assertions**, passing control; no survivors (`mutation.json`, `mutation_assertions.json`).
- Review 01 correction, Review 02 correction, informational and exploratory-survivor outputs reproduce their four committed JSON files **byte for byte**. Mutation output equals its committed JSON after normalizing memory addresses in assertion messages (`records_audit.json`).
- Ruff check: PASS; Ruff format check: **236 files already formatted** (`check_20.log`, `check_21.log`).
- Protected-path diff from `60648b9`: empty. Original force definitions are AST-identical. Record prefix comparisons pass; final tracked status/diff are empty.

Inspected committed result files are the five `docs/science/experiments/m3-t1/*_results.json` files; both `docs/reviews/raw/M3-T1-review0{1,2}-reproduction/reproduce_review0{1,2}_output.json`; Review 02's `own_mutants/results.json`, its three diffs and prior interval log; and all five supplied `review_scratch/ci/run-*.json` exports. Newly inspected numerical results include `review01.json`, `review02.json`, `informational.json`, `mutation.json`, `survivors.json`, `adversarial.json`, `exact_factor.json`, `factor_cases.json`, `numerical_search.json`, `supplementary.json`, `interval_dyadic.log`, `path_counts.log`, `records_audit.json`, `ci_consistency.json`, `historical_probe.json`, and `own_mutants/results.json`, plus the validator/log files above.

Historical local Proof-wrapper outcomes, CI execution/authenticity, external-source authenticity, and assertions about measurements preceding tolerance selection remain **documentary claims**, not my executions. I did not run either prohibited Proof wrapper.

## 2. Resolution table

| Finding | Resolution | Independent basis |
|---|---|---|
| M3T1-R1-F1 | RESOLVED | Slots and assignment/deletion guards remain; owned built-in floats remove array aliasing and float32 arithmetic; functional mutation tests pass. No stale derived cache. |
| M3T1-R1-F2 | RESOLVED | Original overflow/tiny-radius/nonfinite reproductions reject with documented diagnostics; coefficient and component-product losses now reject. No additional contract-violating loss found in the arithmetic audit or adversarial executions. |
| M3T1-R1-F3 | RESOLVED | Docstring gives r⁻³ for a·r. Independent differentiation and radial scaling agree; the old assertion is unchanged. |
| M3T1-R1-F4 | RESOLVED | All four formerly surviving committed defects fail functional assertions. Power-of-two, negative-J2, far-field and dense-latitude coverage remains. Literal scan explicitly remains heuristic. |
| M3T1-R2-F1 | RESOLVED | x/y/z reproductions and all three coefficient-chain cases reject; exact zeros, exact subnormal intermediates/factor products and subnormal final results are accepted. Independent adjacent-parameter probes distinguish exactness from tininess. |
| M3T1-R2-F2 | RESOLVED | Conversion precedes physical validation; all stored parameters are built-in floats. Array mutation cannot change them. Supported scalar/0-d inputs, unsigned integers, longdouble, subclasses and unsupported types independently probed. |
| M3T1-R2-F3 | RESOLVED | Only the module docstring changed; executable AST is identical to b1566ae. It now accurately describes 200,000 random plus four axis states, with no trajectory claim. Output unchanged. |
| M3T1-R2-O1 | RESOLVED | Explicit appended erratum states F1=3, F2=7, total=10. Original erroneous row remains. Harness enumeration and git prefix checks confirm it. |

These resolutions concern the required behavior of the actual code. They do not claim exhaustive input or mutation coverage.

## 3. I-20 §7 assessment

**1 — Underflow, legitimate zeros and domain.** `_underflows` compares the exact product of two finite binary64 operands with their rounded product only when the rounded magnitude is below the smallest normal. This implements the stated tininess-plus-inexactness definition; exact zeros/subnormals compare equal. It does not promise correct rounding of the whole physical formula. A 29,975-pair random-bit-pattern check agreed with independent rational comparisons.

The constructor checks every coefficient product that can carry underflow into later multiplication. The fourth product is covered by the final normal-coefficient requirement. Extending the fix to this same coefficient-chain defect is within I-20's bounded numerical correction and I-19's requirement not to leave the same supported failure path; it does not change unrelated models or numerical policy.

I audited positive sums for r², sqrt, s², r²·r²·sqrt(r²), coefficient division, both factor subtractions/products and all three final multiplications. Accepted r⁵ prevents a materially subnormal r²/r²-squared chain; tiny individual coordinate squares or s² can disappear only at scales irrelevant to the absolute latitude-factor majorant. Near factor cancellation, relative component accuracy is not guaranteed: the records explicitly acknowledge the existing absolute-error behavior. The last multiplication can round a final subnormal, including a true magnitude below representable resolution to zero; this is permitted and does not feed further arithmetic. Nonfinite outputs reject. No remaining materially amplified intermediate-underflow path was demonstrated.

Exact-rational work has bounded operand size: binary64 significands/exponents give rational integers with only a few thousand bits, and there is no adaptive precision or iteration. Zero products can enter this fallback even at realistic states: note R3-F1 corrects the cost description, not this bound.

For canonical constants, a conservative rounded-division bound is `(1-u)|k0|/max_float`, approximately 1.4648e-283. The smallest nonzero computed c factor is at least 2⁻⁵³; d is at least 2⁻⁵¹. Their nonzero products therefore exceed approximately 1.626e-299, safely normal. The three coefficient intermediates are normal. Thus the new **raising** checks cannot trigger in the accepted canonical domain. Exact zero factors are the fallback exception, not an underflow rejection. The stated cancellation limitation is honest when read with the necessary tiny-k condition; canonical constants cannot reach that rejecting regime.

Own constructive probe: at r=(2,0,nextafter(1,+∞)), μ=1.6584721341932835e-306, R=1, J2=0.5, k=−min_normal and c=−2⁻⁵¹. Their exact subnormal product is 2×min_subnormal and is accepted. Increasing μ by one ulp makes that product inexact and raises the component-underflow diagnostic. Signed-zero J2/coordinates and tiny final coordinates were also checked. `numerical_search.py` accepted 3,213 of 7,000 extreme-parameter trials; rational sqrt brackets bounded every accepted component within `64u·majorant + 0.5·min_subnormal`, maximum ratio 0.09037, with no representable nonzero component silently rounded to zero in that sample. This is falsification evidence, not a universal accuracy theorem.

**2 — Owned conversion and errors.** `_owned_float` extracts a 0-d element, restricts its scalar type, then calls built-in `float`; all three conversions precede physical validation and storage. My 29 accepted type cases included Python int/float subclasses, NumPy signed/unsigned widths, float16/32/64/longdouble and 0-d forms. Thirteen unsupported cases rejected, including bool/bool_, string/object-string, complex, Fraction and nonscalar arrays. Numeric object-dtype 0-d arrays are accepted when their extracted object is a supported numeric scalar; unsupported contents reject. This is consistent with the stated element-based supported-type rule and still stores an owned float. Huge positive/negative ints produce ValueError; converted NaN/∞ and invalid μ/R retain physical validation. No non-binary64 or caller-owned value reached arithmetic. Deliberate Python object-model bypasses such as `object.__setattr__` are outside the ordinary immutability promise already discussed in prior reviews.

**3 — R2-F3.** Corrected description, unchanged executable AST and byte-identical output. No trajectory work was inserted into the Review 01 script to justify its former wording.

**4 — R2-O1.** The appended historical correction is explicit and correct. The later 9-case/107-case corrections likewise preserve their original entries and accurately supersede them: 73+9+25=107; red-first 26+81=107. There are 95 cases in `test_zonal_j2.py` and 12 in `test_constants.py`.

**5 — R1 preservation.** All original reproduced failures remain fixed, with the broader ownership and underflow holes closed. Independent differentiation gives `U2=(μJ2R²/2)(r⁻³−3z²r⁻⁵)`, whose positive gradient is the implemented acceleration. Taking its dot product with r gives `−(3/2)J2μR² r⁻³(1−3s²)`. The force is autonomous and axisymmetric, so energy and h_z are mathematical invariants; the RK4 drift ratio is a finite structural test, not exact numerical conservation. Former mutant survivors are killed by real numeric/behavioral assertions.

**6 — Numerical preservation.** Each 200,004-state committed comparison reproduces with zero differences against its respective reference, b1566ae or 97b69ef. Three 6,001-state, dt=10 s RK4 trajectories at 28.5°, 51.6° and 97° are bit-identical against b1566ae; my separate execution also establishes identity against 97b69ef. My different seed and coordinate-exponent sample produced 9,919 accepted states bit-identical to **both** references, with 2,081 explicit domain rejections. Equatorial accepted endpoints and their rejected adjacent floats reproduce: 3.3773820261812166e-57 m and 4.476546622757235e61 m. The lower neighboring rejection is the component expression's overflow; the upper is r⁵ overflow. Algebraic evaluation order for existing Python-float inputs is unchanged.

**7 — Mutation and bounds.** I inspected all 46 mutants' failure messages and assertions. Their kills are functional numeric, identity, ownership or diagnostic-contract assertions, not collection errors or source-only checks. Some protection removals are killed by the required diagnostic message rather than accepting a formerly rejected state; that limitation is documented. Four original anchors retain their factor/scale/zero-offset defects after the component rewrite. Counts are 14 original +8 Review 01 +10 R1 removals +14 R2 removals; R2 splits 7/7. The classifier is unchanged; its generic `Failed` fallback remains the owner-accepted limitation, with no actual misclassification found here.

The two exploratory survivors reproduce. A one-ulp canonical perturbation fits the numerical gate tolerances but would fail the separate bit-identity check; the narrow-band branch is absent from the inspected production graph. Its hit probability for the random set is approximately 24.77%, and the actual set has zero hits. These arguments explain limited coverage, not immunity to hidden defects. My additional surviving mutant is recorded in §5 below, without claiming it belongs to the 46-mutant campaign.

The rerun outward-dyadic rational interval certificate encloses all 5,904 positive-J2 dense-grid cases, maximum enclosed-error/minimum-bound ratio **0.4114583333333321**, none uncertified. Negating J2 negates the ordinary graphs and preserves the absolute majorants; the tests exercise both signs. I inspected operation graphs and found their depths below the recorded conservative counts. A path count alone is not a proof for arbitrary nonlinear floating-point graphs; the finite interval certificate supplies stronger evidence for this gate's actual domain. Correctly rounded operations remain an explicit assumption, not a proven platform property.

**8 — Dual numbers and +∇U.** DR-0025 accurately records the owner's accepted T1 substitution and every stated limitation. The packet's appended erratum has the correct sign for its positive potential and preserves the original. The unit derivative oracle shares ordinary arithmetic, sqrt, constants and conventions; it is not external corroboration or proof of IEEE compliance. I neither reopen nor expand that disposition. Old terse libm wording is qualified by the recorded correctly-rounded-operation assumption.

**9 — M1/M2 isolation.** Locally supported by the full suite and validator/golden/determinism checks above. `git diff 60648b9..HEAD -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty. Only `constants.py` (+58 lines) and `forces.py` (+137 lines) differ in src; existing force classes are AST-identical. J2 remains unwired, with no production consumer. Historical wrapper claims of 9/9 and 20/20 were not independently authenticated or rerun.

**10 — New defects and provenance.** Record sections in VAL-0020, both review records, the T1 report and decision matrix are strict byte-prefix extensions of b1566ae; the experiment README also preserves its earlier text. Existing DR-0025/packet dispositions remain. Script/result changes are identifiable evidence updates, not silent rewrites of historical records. `4b85ded` changes only the Review 02 validation record. Numeric counts, before/after values, canonical reach, sampling, trajectory and mutation summaries agree with the local computations within their stated rounding. No complete-IEEE or complete-mutation claim is made. The two notes below do not invalidate those results.

## 4. New findings

**M3T1-R3-F1 — NOTE — rational-fallback reach is described too broadly. VERIFIED.**

Location: `docs/science/validation.md:1173`; implementation `src/tars/sim/forces.py:36`.

The cost note says a realistic state never reaches a product below normal and therefore the exact-rational comparison. With canonical constants and r=(12756274,0,6378137) m, c computes exactly zero. Instrumenting `Fraction` records **two calls** during acceleration evaluation; the correct returned acceleration is (−0,−0,−0.0005692785957521009) m/s² (`adversarial.py`, `adversarial.json`). Zero is below the helper's magnitude threshold even though it is not underflow.

Consequence: a minor performance/evidence-description overstatement. Cost remains bounded, the result is correct, and the canonical no-underflow-rejection argument remains valid. Recommended clarification: say **nonzero** factor products cannot reach this regime with canonical constants; exact-zero products can enter the fallback. An implementation optimization is unnecessary. Requirement: I-20 §7(1),(10), accurate bounded-cost documentation. Classification: **nonblocking documentation clarification**, not an unresolved numerical decision or acceptance-gate defect.

**M3T1-R3-F2 — NOTE — a historical reproduction row mixes observation times. VERIFIED.**

Locations: `docs/reviews/raw/M3-T1-review02-reproduction/reproduce_review02.py.txt:38–49`; corresponding `reproduce_review02_output.json:25–28`.

The row labeled `mu_alias_set_-1` records `m.mu=0.0` beside the positive acceleration produced with μ=−1. The script computes `a_neg`, mutates μ to zero, then reads `m2.mu` while constructing that earlier row. My isolated archived-code reproduction records μ=−1 at acceleration time, x=3.991922438949618e-17, and μ=0 at reporting time (`historical_probe.py`, `historical_probe.json`).

Consequence: the raw row's parameter field is not a contemporaneous snapshot. It does not invalidate the historical aliasing defect, its acceleration, or the current correction; the new correction check records correct independent before/after outcomes. Recommended clarification: append a provenance note explaining the timing; preserve the historical raw file. Requirement: I-20 §7(10) and preservation of review evidence. Classification: **nonblocking historical provenance clarification**, predating this correction pass; no unresolved physics or owner-policy decision.

## 5. Adversarial attempts

- Tried caller mutation of all three 0-d inputs, float32 persistence, unsupported convertibles, integer extremes, signed zeros, subnormal coordinates/results, near-zero factors, coefficient-chain loss and adjacent exact/inexact subnormal products. No production counterexample to the corrected contract was found.
- Searched 29,975 finite random operand pairs for a wrong exactness decision; none found. Searched 7,000 extreme parameter/geometry cases against rational references; no accepted result violated the stated test majorant or showed an amplified silent zero. Sampling is not exhaustive.
- Applied six own source mutants, retaining diffs/JUnit/logs under `own_mutants/`: five fail assertions—zero-only underflow detection, losing radius ownership, losing J2 ownership, rejecting zero J2, and flushing final subnormals. **`upper_subnormal_ignored` survives all 107 tests**: replacing the helper's threshold with `min_normal/2` leaves a coverage gap. At J2=`2^-1023+2^-1074`, μ=`2^1000`, R=1, the first product is approximately −0.75 min_normal and inexact; actual production correctly rejects it. This is an optional regression-test enhancement and a further finite-coverage limitation, not a defect present in production or a claim that all exploratory mutants are killed. No actual required invariant was found violated in the reviewed code.
- Reapplied Review 02's exact exploratory defects, checked all four re-anchors, and checked the source graph for the surviving narrow-band branch. No classifier misclassification was demonstrated.

## 6. Verification limits

All numerical executions are on one supplied host/environment. The rational references and interval certificate assume the documented arithmetic model; they do not establish CPython/libm/NumPy correctness for every operation or platform. Tests, random sets, dense grids and mutation campaigns have finite reach. Input ownership does not promise resistance to deliberate Python object-model bypasses. Numeric object-array handling is element-based, as described above.

No network, signatures, live CI, independent cross-platform run, GMAT executable, or external J2 implementation was available. The five CI exports have the expected full SHAs, branch, completed/success conclusions and all four required job names. Their authenticity is unverified. In run **40002897696**, early macos-15-intel step timestamps precede its declared job start; setup begins at 18:23:19Z, whereas run creation is 18:23:33Z and job start 18:23:39Z. Clock skew is possible; this is an internal timestamp anomaly, not proof of falsification or failure. The pinned-head export has no such observed anomaly. Historical local validation, remote refs and prelaunch gate timing cannot be authenticated.

I have not approved DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular tolerances/presentation, T4/T5 comparison requirements, the M3 final timestep, the T3 axis representation or external corroboration. The secular and convergence outputs remain informational, and approximately dt⁵ invariant drift remains an observation. The dual-number disposition and explicit floating-point assumptions are recorded limitations, not newly imposed conditions on this verdict.

## 7. Acceptance readiness

The reviewed T1 correction pass is **ready for the owner's acceptance-dossier/acceptance decision**, with the two nonblocking clarifications and finite verification limits recorded. This review does not accept or merge T1, authorize T2/T3, or decide any deferred item. No fix was made. The tracked tree is clean; all new artifacts are excluded scratch files.

[Saved review](<SNAP>/review_scratch/M3-T1-codex-review03.md) · [Command ledger](<SNAP>/review_scratch/COMMANDS.md) · [Inspection ledger](<SNAP>/review_scratch/INSPECTION_COMMANDS.md)

VERDICT: PASS (unconditional)
