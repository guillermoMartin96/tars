# M3 T1 Review 02 (independent review of the Review 01 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a16723-7af7-7b32-a1b3-87d2eeab7a65`; final message written 2026-10-23 05:34:51 UTC (2026-10-22 local). One attempt.
- **Sandbox:** `workspace-write`, no network. GMAT was not provided; T1 contains no GMAT work.
- **Invocation:** `codex exec -C snap -s workspace-write --json -o codex_last_message.md - < M3-T1-codex-review02-prompt.md`. As in Review 01, the CLI wrapper on this host reports `--dangerously-bypass-hook-trust` as enabled; this invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4`**, head of `milestone-3-t1-j2-force-model`. Correction pass `62d3684`, `a27f288`, `b0164fd`, `16a8e63`, `1cf0ce9` on top of the Review 01 head `97b69ef`; `main` = `60648b93385a9954194730006aeac29ea14875ad`.
- **Environment.** A fresh GitHub clone detached at the pinned SHA, with its own `uv sync --locked` environment and `review_scratch/` excluded from git. The implementer placed in `review_scratch/`:
  - `reviewed_src_97b69ef/src` (`git archive 97b69ef src`), the input of `t1_review01_correction_check.py`;
  - `ci/run-<id>.json` (`gh run view --json`) for runs 39897342033, 39894176897, 39894033142, 39885659108 and 39865621259, as implementer-supplied claims.
- **Prompt.** Kept outside the repository during the review. It reproduces I-19 verbatim, points to the Review 01 prompt for I-17/I-18, lists the implementer's claims (including the local validation and CI figures) as claims to verify, states which I-19 §10 preconditions the implementer had checked, says that unauthenticated CI is a verification limit and not a reason to stop, and maps the ten I-19 §11 items into the review.
- **Authority:** "I-19 — M3 T1 Review 01 Corrections and Review 02 Authorization" (Tech Lead), §11.

## Preconditions (I-19 §10–§11), checked by the implementer before the review
| Item | Result |
|---|---|
| Branch | `milestone-3-t1-j2-force-model` |
| HEAD and origin | both `1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4` |
| Working tree | clean |
| Local validation | at `16a8e63` (`1cf0ce9` changes two documentation files only); recorded in `M3-T1-review-01.md`, "Validation of the correction pass" |
| CI | completed, success on `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform`: `b0164fd` run **39894033142**; `16a8e63` run **39894176897**; `1cf0ce9` run **39897342033**. `62d3684` and `a27f288` were pushed with `b0164fd` and have no run of their own |

## Files
- **Prompt:** `raw/M3-T1-codex-review02-prompt.md`.
- **Raw output:** `raw/M3-T1-codex-review02.md`, the CLI's final message, which equals the reviewer's saved `review_scratch/M3-T1-codex-review02.md` except for that file's trailing newline. Absolute paths are redacted: `<SNAP>` for the clone, `<SCRATCH>` for other scratch paths and `<HOME>` for the home directory. No other change.
- **Reviewer scripts and logs:** `raw/M3-T1-codex-review02-evidence/` (82 files including `SHA256SUMS`, 860 kB).
  - `*.py.txt` are the reviewer's scripts (renamed from `.py`); `COMMANDS.md` is its command ledger; `ci/` holds the implementer-supplied CI exports; `own_mutants/<mutant>/` holds `diff.patch` and `junit.xml` for the reviewer's three surviving mutants, plus `results.json` and `redfirst.log`.
  - `reviewer-SHA256SUMS` was written by the implementer over the reviewer's unrenamed, unredacted files. `SHA256SUMS` covers the committed files.
  - Absolute paths are redacted as above.
  - **Omitted** as derivable from git or as copies: `reviewed_src_97b69ef/`, the full `src/` trees of the reviewer's mutant copies and `own_mutants/old_src/` (each represented by its diff or by `git archive 97b69ef src`), `__pycache__/`, and the reviewer's copy of its report.
- **Implementer's reproduction:** `raw/M3-T1-review02-reproduction/` (`reproduce_review02.py.txt`, `reproduce_review02_output.json`), run at `1cf0ce9` in the T1 worktree. It is independent of the reviewer's scripts; the R2-F1 reference value uses exact rationals and an integer-square-root bracket.

## Verdict
**`VERDICT: REQUEST_CHANGES`**. Findings: **2 MINOR** (M3T1-R2-F1, F2) and **1 NOTE** (F3). No BLOCKER or MAJOR. The reviewer also reports, without numbering it, a count inaccuracy in this Review 01 record (registered below as M3T1-R2-O1).
- **Reviewer's summary:** "The ordinary-domain J2 physics and M1/M2 isolation are supported. **T1 is IMPLEMENTED — NOT REVIEW-ACCEPTED — NOT MERGED, and is not acceptance-ready.** The two MINOR defects require correction or return to the owner for direction."
- **Review 01 findings, per the reviewer:** R1-F1 **partially resolved** (ordinary reassignment and stale caching fixed; accepted mutable parameters still aliased — R2-F2); R1-F2 **partially resolved** (the original overflow, tiny-radius and infinite-parameter cases fixed; off-axis product underflow remains — R2-F1); R1-F3 **resolved**; R1-F4 **resolved** (all four previous survivors now fail meaningful functional assertions).
- **Stop rule applied (I-19 §12, REQUEST_CHANGES):** every finding is reproduced and classified, and a disposition is proposed. **No finding is fixed.** No Review 03 is started. T1 is not accepted or merged; T2 and T3 are not started.

## What the reviewer verified by its own execution (from the raw output and ledger)
- **Regression:** full pytest 1254 passed (29 min 49 s); ruff check and format pass (233 files); T0 checks 314 passed; M1 validator 7/7; M2 validator 228/228; M1 golden comparison bit-identical and cross-process event-log digest `7a4e1877…20a4`; fresh-process determinism for all four `scenarios/m2_*.json`; local M2 record collection for the six canonical missions. The Proof wrappers were not run, as the prompt instructed.
- **Correction evidence:** the committed mutation campaign reruns as 32/32 detected, all by assertion; the reviewer inspected the failure messages. The correction check reproduces byte for byte (200 004 states bit-identical); the informational results reproduce byte for byte. Red-first: the committed tests give 21 failed / 52 passed against a reconstructed `97b69ef` source. The reviewer's own RK4 comparison (6 001 states per trajectory at 28.5°, 51.6° and 97°, dt 10 s) is bit-identical between old and new code.
- **Physics:** independent derivation of U₂ and its gradient; **+∇U** confirmed; J2 = −√5 C̄₂₀ consistent; a·r ∝ r⁻³ confirmed by derivation and by computation.
- **Numerics:** the power-of-two known answers are exact by analysis, not only by observation. An outward-dyadic interval certificate covers all 5 904 dense-grid positions for both signs of J2 (maximum enclosed-error / bound ratio 0.411; the original 162-point gate certifies with the same maximum). The equatorial domain 3.3773820261812166e-57 m … 4.476546622757235e61 m reproduces. The reviewer identifies the lower limit as overflow of `k*3` in the z expression (giving a NaN that is rejected), not overflow of the coefficient division; the upper limit is r⁵ overflow.
- **Immutability:** ordinary assignment, deletion and new attributes fail; no `__dict__`. Subclass dictionaries, slot-descriptor writes, `object.__setattr__` and reinitialization are classed as deliberate object-model bypasses, not supported update paths. `copy`/`deepcopy`/pickle fail with `AttributeError`; no support is promised, so this is not classed as a violation.
- **Records:** DR-0025 owner note accurate and not overstated; packet erratum correct; all record changes append-only; scope compliant (protected-path diff from `60648b9` empty; `src/` changes confined to `constants.py` and the J2 class in `forces.py`).
- **CI exports:** internally consistent with the expected SHAs, all four jobs successful. Listed as implementer-supplied metadata, not authenticated.

## Findings and dispositions
Proposed dispositions are the implementer's. None is applied; each awaits the Tech Lead.

| ID | Severity | Finding (reviewer) | Implementer's reproduction (`reproduce_review02_output.json`) | Proposed disposition |
|---|---|---|---|---|
| M3T1-R2-F1 | MINOR | Unchecked component-product underflow. `ZonalJ2Gravity(5.1827254193540115e-108, 1.0, 0.5)` at r = (1e40, 0, 4.9999999999999995e39) passes every enumerated check (`k0`, `r5`, `k` all normal) but `c` = 2⁻⁵³ and `k*c` underflows to zero, so the x component is returned as −0.0 where the exact value rounds to the normal −4.303918780958246e-284. The stated domain checks do not eliminate silent loss (I-19 §4, §11(3); DR-0024 R6) | **REPRODUCED.** Result `[-0.0, -0.0, -2.2250738585072012e-268]`; `k` = −2.2250738585072014e-308 (normal); `c` = 2⁻⁵³ exactly; `k*c` = −0.0. Both rounded ends of the exact-rational bracket of the x component are −4.303918780958246e-284 (normal). **Reach (implementer's analysis):** with the canonical constants, \|k\| ≥ \|k0\| / max binary64 = 1.46e-283 everywhere inside the accepted domain and the smallest nonzero \|c\| or \|3 − 5s²\| is at least 2⁻⁵³, so \|k·c\| ≥ 1.6e-299 is normal: the defect needs non-physical parameters and cannot occur with the authorized constants | **ACCEPTED** (proposed), MINOR. Proposed correction: extend the numerical contract to the component products (for example, reject when a nonzero factor product `k*c` or `k*(3 - 5 s2)` is not a normal binary64), keeping the evaluation order so that valid results stay bit-identical; add off-axis tests with extreme accepted parameters for both factors; update the contract and evidence |
| M3T1-R2-F2 | MINOR | Accepted numerical inputs escape immutable binary64 ownership. A zero-dimensional NumPy array passed as μ (or R, J2) is stored by reference; mutating the caller's array after construction changes `m.mu` and the result (μ = −1 gives outward acceleration; μ = 0 removes the perturbation; R can become negative after validation). NumPy float32 parameters keep float32 arithmetic and return float32 (relative difference 7.56e-8 against the same values as Python floats) (packet §3 item 2; I-19 §3, §11(2)) | **REPRODUCED.** μ alias set to −1: x = +3.991922438949618e-17 (outward). Set to 0: x = −0.0. R alias set to −6378137: `m.equatorial_radius` = −6378137.0 accepted silently (the result is unchanged because only R² enters). float32: result dtype float32, x = −0.01591181941330433 against −0.015911820615666403 for the same values as Python floats, relative difference 7.556e-8. Canonical construction with Python floats is unaffected | **ACCEPTED** (proposed), MINOR. This is the "another supported mutation path" that I-19 §3 forbids retaining. Proposed correction: take ownership at construction by converting each parameter with `float()` before validation (the same idiom the method already uses for the position), so Python-float inputs stay bit-identical; add tests for caller-alias mutation and for NumPy scalar inputs. Rejecting non-`float` types is the alternative; the owner may prefer it |
| M3T1-R2-F3 | NOTE | `t1_review01_correction_check.py` docstring (lines 4–6) says the bit-identity check includes "the committed RK4 trajectories' states"; `main` checks 200 000 random states and four axis states and loads no trajectory | **REPRODUCED.** The docstring mentions trajectories; the code after it does not. The results file contains no trajectory comparison | **ACCEPTED** (proposed), NOTE. Proposed correction: remove the clause (the reviewer's own three-trajectory check is reviewer evidence only and does not make the script's claim true). Performing the comparison is the alternative |
| M3T1-R2-O1 | NOTE (reported by the reviewer under §11 item 5, not numbered) | This Review 01 record's corrections table (R1-F2 row) says "8 F2 protection-removal mutants"; the actual count is 7. The appended count correction fixed "11" but not this "8" | **REPRODUCED.** The harness has 3 `f1_*` and 7 `f2_*` protection-removal mutants. Total 32 unchanged | **ACCEPTED** (proposed), NOTE. Proposed correction: an appended count note in `M3-T1-review-01.md` (the original line stays) |

## Reviewer observations not registered as findings
- **Three further surviving mutants** (`own_mutants/`): a one-ulp coefficient perturbation confined to μ > 1e10; a 1e-8 x/y factor error confined to 0.123456 < s² < 0.123457; returning zeros when 0 < |k| < 2 × min normal. The reviewer: the records limit completeness to the 32 named mutants, so survival is not an acceptance defect. **Proposed disposition:** no change; recorded as a limit of finite mutation coverage. The third is in the region of R2-F1 and may be killed by its correction tests; that is not claimed.
- **Mutation classifier portability:** the fallback accepts a JUnit failure type `Failed` regardless of message if another XML producer emits it. Current kills are established by their messages. **Proposed disposition:** no change in T1; noted as a limitation.
- **"Does not depend on libm" wording:** too terse in isolation, but qualified by the stated correctly-rounded-operation assumption and the DR-0025 owner note. Not a defect per the reviewer; unchanged (outside I-19 scope, as recorded in Review 01).
- **Not resolved, as required (I-19 §9):** DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular-rate tolerance and presentation, T4/T5 comparison requirements, the M3 final time step, the T3 axis representation, lack of external corroboration and the IEEE-754 assumption. The reviewer approved none. The approximately dt⁵ invariant drift remains an observation.

## Verification limits (from the reviewer, confirmed by the setup)
- All new numerical observations are from one host (macOS x86_64, CPython 3.12.15). The interval and rational certificates are conditional on the stated arithmetic model.
- No network, live CI authentication, cross-platform execution, GMAT executable or external physics implementation. The historical Proof wrapper outcomes (9/9, 20/20) are documentary claims to the reviewer.

## Owner disposition (I-20; recorded 2026-10-23 UTC, append-only)
- **Authority:** "I-20 — M3 T1 Review 02 Corrections and Review 03 Authorization" (Tech Lead). It acknowledges the I-19 checkpoint and accepts Review 02's findings, as reproduced, for correction.
- **R2-F1 (MINOR): ACCEPTED.** Correct the remaining silent underflow in component products. Distinguish legitimate zeros. Keep valid realistic-orbit results bit-identical. No blanket rejection of subnormal inputs or outputs. No claim of complete IEEE 754 correctness.
- **R2-F2 (MINOR): ACCEPTED, conversion chosen.** Convert μ, R and J2 to owned built-in `float` values before validation. Define and test the supported numeric types. Reject unsupported or non-convertible inputs with clear errors.
- **R2-F3 (NOTE): ACCEPTED.** Correct the docstring. No trajectory work is to be added.
- **R2-O1 (NOTE): ACCEPTED.** An explicit erratum: F1 3, F2 7, total 10.
- **Mutation coverage (I-20 §3):**
  - the three exploratory survivors are accepted as a documented verification limitation;
  - the classifier observation is accepted as a limitation, and the classifier is not to be changed on hypothetical runner behavior.
- The other observations stand as recorded above.

## Corrections (I-20; recorded 2026-10-23 UTC, append-only)
| Finding | Correction | Commit | Evidence |
|---|---|---|---|
| M3T1-R2-F1 | A product below the normal range that is **inexact** (IEEE underflow) raises `ValueError`: k (1 − 5 s²) and k (3 − 5 s²) in the acceleration, and the coefficient products −(3/2) J2, × μ, × R in the constructor. Exact zeros, exact subnormal products and subnormal final components are returned. Evaluation order is unchanged | `304d796` | 5 new test functions (8 cases); 7 R2-F1 mutants killed; `t1_review02_correction_check_results.json` |
| (R2-F1, coefficient) | The same defect in the coefficient chain, **found by the implementer** while auditing every multiplication chain. Review 02 did not report it. J2 = 3 × 2⁻¹⁰⁷⁴ with μ = 2¹⁰⁰⁰ gave a normal coefficient 11 % wrong. Included under R2-F1 per I-19 §3 (do not fix only the reproduced example while the same path remains). **The owner may rule it out of scope** | `304d796` | `test_coefficient_product_underflow_raises_instead_of_an_inaccurate_result` (one case per product) |
| M3T1-R2-F2 | Parameters converted to built-in `float` before validation. Supported: `int` (not `bool`), `float`, NumPy integer and floating scalars, zero-dimensional arrays of those. Others raise `TypeError`; an out-of-range `int` raises `ValueError` | `304d796` | 7 new test functions; 7 R2-F2 mutants killed |
| M3T1-R2-F3 | Docstring now says 200 000 random states and four axis states, no trajectory. Output unchanged (byte-identical) | `a4dfda1` | `t1_review01_correction_check_results.json` reproduces |
| M3T1-R2-O1 | Erratum appended to `M3-T1-review-01.md` (F1 3, F2 7, total 10) | records commit | `M3-T1-review-01.md`, "Erratum (M3T1-R2-O1)" |

- **Red-first:** the final tests give **26 failed, 69 passed** (95 T1 cases) against `b1566ae`. The `56ad329` message says 24/69 of 93: two coefficient cases were added in `308f126`.
- **Before and after** (`t1_review02_correction_check_results.json`):

| Case | Before (`b1566ae`) | After | Exact |
|---|---|---|---|
| Review 02 x case | `[-0.0, -0.0, -2.2250738585072012e-268]` | raises "a component product underflows" | x = −4.303918780958246e-284 |
| y variant | y = −0.0 | raises | y = −4.303918780958246e-284 |
| (3 − 5 s²) factor | z = −3.025521829374199e-283 | raises | z = −1.3478448085169703e-283 |
| coefficient chain | x = −1.925929944387236e-34 | raises "an intermediate product underflows" | x = −2.1666711874356403e-34 |
| μ 0-d array set to −1 after construction | x = +3.99e-17 (outward) | x = −0.01591182047796651 (canonical) | — |
| float32 parameters | float32 result, x = −0.01591181941330433 | float64, x = −0.015911820615666403 (= the values as floats) | — |
| `"398600441800000.0"`, `[mu]` | `TypeError` from `math.isfinite` | `TypeError` "mu must be a real number …" | — |
| J2 = `True` | accepted as J2 = 1 | `TypeError` | — |
| μ = 10⁴⁰⁰ (int) | `OverflowError` | `ValueError` "not representable as a binary64 number" | — |

- **Legitimate results, unchanged:**
  - an exact zero factor and coordinate gives `[-0.0, -0.0, -9.891604774494805e-268]`;
  - J2 = 0 gives zeros;
  - an exact subnormal intermediate gives x = −1.4444474582904269e-34;
  - a subnormal final component gives y = −6.2167845e-317.
  - All equal the exactly rounded values (zeros with a sign bit).

## Mutation coverage after the corrections (I-20 §3; recorded 2026-10-23 UTC, append-only)
1. **Committed campaign:** 46 mutants, **46 killed by assertion**, none surviving (`t1_mutation_check_results.json`).
2. **Review 02's exploratory mutants** on the corrected code (`t1_review02_survivors_results.json`):
   - `near_min_normal_zero`: killed;
   - `canonical_one_ulp`: survives;
   - `narrow_band`: survives.
3. **Limits:** finite sampling and mutation testing do not establish the absence of defects. VAL-0020 correction 2, "Mutation limitations", gives the triggering conditions and why the two survivors do not invalidate the authorized T1 criteria. No survivor is found to violate an explicit required invariant or acceptance gate. Nothing is elevated.
