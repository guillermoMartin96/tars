**Focused closure verification — M3 T1, I-21**

This verifies the closure changes following Review 03; it is not Review 04 or an acceptance decision.

**1. Ledger and evidence basis**

Environment: supplied detached clone at `e404b0f40a3a46c0a71041636e0f87eb5fa247f3`; macOS 26.2 x86_64, Python 3.12.15 through `.venv/bin/python`; network unused. Local `main` is `60648b93385a9954194730006aeac29ea14875ad`. Exactly two commits follow `d01d6aa`: `481a62e` and `e404b0f`; no later commits exist in this snapshot.

The complete command ledger is `review_scratch/COMMANDS.md`. Independent scripts and logs are retained there, particularly `verify.py`, `verify.log`, `mutations.json`, `target.log`, `alternative.log`, `historical.log`, `outputs.log`, and `final_checks.log`.

Commands and key results:

- Git comparisons: `src/` unchanged from `4b85ded`; all specified protected paths unchanged from `60648b9`; Review 03 record, dossier, all `docs/reviews/raw`, and I-20 mutation results unchanged from `d01d6aa`. These are independently executed content comparisons.
- Documentation diff and byte-prefix checks: Review 02 clarification, VAL-0020 correction 3, and README addendum append to the prior files. The harness gains explanatory text and exactly one mutant; its earlier definitions remain intact. The results JSON is new. No historical documentation lines were deleted.
- Targeted pytest: **109 passed in 4.76 s**; collection independently confirms **97 + 12**. Existing exact-zero and legitimate-subnormal tests are unchanged and pass.
- Ruff: **All checks passed**; formatter: **238 files already formatted**. These checks preceded creation of the verifier's scratch Python scripts.
- Independent target mutation: **1 failed, 108 passed**, solely the new rejection test, with **DID NOT RAISE ValueError**. The same mutant against archived Review 03 tests: **107 passed**.
- Full mutation campaign: **47/47 detected, 47 by assertion, no survivors**. Fresh mutant exit codes and failing-test sets agree with the committed I-21 results. Comparing the committed I-20 and I-21 records independently confirms that none of the earlier 46 lost a failing test; additions involve only the new tests.
- Exploratory reproduction: `canonical_one_ulp` and `narrow_band` still survive; `near_min_normal_zero` remains killed. Survivor output and both correction-check outputs and the informational output are byte-identical to their committed counterparts.
- Full-suite collection: **1290 tests collected**. This independently supports the count, not the claimed full-suite pass. The historical 1288 plus two added cases is consistent.
- Final `git diff --check` and tracked-tree status: clean.

Files inspected include `src/tars/sim/forces.py`; the T1 tests and their historical versions; `docs/science/validation.md` correction 2 and correction 3; `docs/reviews/M3-T1-review-02.md`; the archived Review 02 reproduction script and output; the Review 03 record/dossier and reproduction evidence; the mutation harness and both result files; README; correction, informational and survivor scripts/results; and all three supplied CI exports. Conclusions below rest on independent execution/computation unless explicitly identified as documentary claims.

**2. Closure table**

| Item | Status | Evidence |
|---|---|---|
| M3T1-R3-F1 | CLOSED | Correction 3, `docs/science/validation.md:1205–1210`; independent canonical execution, Fraction instrumentation, reach-bound computation, and code inspection. |
| M3T1-R3-F2 | CLOSED | Appended provenance note, `docs/reviews/M3-T1-review-02.md:143–156`; independent archived-code alias reproduction; raw files unchanged. |
| M3T1-R3-O1 | CLOSED | `tests/test_zonal_j2.py:439–478`; exact rational computation, production rejection/companion acceptance, historical survival and fresh targeted/campaign kills. |

**3. Assessment of I-21 §7 items 1–5**

**Item 1 — Documentation corrections: verified.** At `(12756274, 0, 6378137)` m, canonical production returns `[-0.0, -0.0, -0.0005692785957521009]` without exception. Instrumenting the module's Fraction constructor records two constructions during evaluation and zero during canonical model construction. The computed latitude factor is exactly zero. The bounded-cost statement concerns comparisons, not Fraction-object counts: the code has at most two exact-product comparisons per evaluation and three at construction, each comparison constructing two operand Fractions. Short-circuiting can reduce the counts. Operand sizes are bounded by binary64; there is no iterative precision refinement.

For nonzero computed factors, subtraction spacing gives magnitude at least `2^-53` (the factor near 3 has the larger spacing `2^-51`). The canonical coefficient divided by the largest finite binary64, multiplied by `2^-53`, gives approximately `1.6262597531022472e-299`, safely normal. Rounding does not threaten that large margin. The fixed canonical construction products are normal too. Thus the corrected distinction between zero and nonzero products is sound within the stated accepted numerical domain.

On archived `b1566ae` production, the alias sequence independently gives μ = −1 at acceleration time, outward x = `3.991922438949618e-17`, then μ = 0 when the row is constructed. The appended interpretation is accurate; the original script/output and Review 03 evidence remain byte-identical to `d01d6aa`.

**Item 2 — Boundary construction: verified.** Write `u = 2^-1074`. The input μ = `(2^52 + 1)u` is representable and normal: the spacing at MIN_NORMAL is exactly u. With J2 = 1/2, p1 = −3/4 exactly. The exact p2 is `−(3·2^50 + 3/4)u`; the rounded p2 is `−(3·2^50 + 1)u`. Distances to the neighboring representable values are u/4 and 3u/4, so this is inexact and not a tie. Both magnitudes are strictly between `2^51 u` and `2^52 u`.

Independent Fraction equalities verify that both subsequent multiplications by `R = 2^10` are exact. The final coefficient is normal, approximately `−1.749869284693536e-302`. Parameters are finite and positive where required; p1 and p3 do not underflow. Production therefore raises specifically for p2, with `-(3/2) J2 mu R^2: an intermediate product underflows`, rather than the finite-normal-coefficient check.

For companion μ = `2^52 u`, p2 is exactly `−3·2^50 u`, strictly in the same band. Both later multiplications are exact and the final coefficient is normal, approximately `−1.7498692846935354e-302`. Construction/evaluation succeed; the existing formula oracle passes the already established `2γ16` bound.

**Item 3 — Intended mutation detection: verified.** Harness lines 311–316 replace only `_underflows`' threshold with MIN_NORMAL/2; exactness logic is retained. The independent copy produces exactly the claimed missing-exception failure. Removing this check admits the model, demonstrating that an unrelated constructor rejection does not satisfy the new test. Exact arithmetic separately excludes other rejection paths.

As an independently chosen alternative wrong implementation, I exempted the single rounded upper-band product `−0x0.c000000000001p-1022` from underflow rejection while retaining the original threshold and other exactness checks. The tests catch this too: exactly the new rejection test fails, **1 failed, 108 passed**, with DID NOT RAISE. This is additional detection evidence, not a completeness claim.

**Item 4 — Scope and behavior: verified.** Git content comparisons establish production/protected-path immutability. The test diff adds two cases and a test-only exact rational unit. No pinned constant, API, domain rule, or tolerance changes. The companion reuses the established formula oracle and tolerance. Existing zero/subnormal tests were preserved and independently passed. No owner decisions were made.

**Item 5 — Records, numbers, and blocking findings: verified within the limits below.** The new sections' arithmetic, canonical coordinates/result, Fraction count, two/three comparison bound, 109/97/12 counts, historical 107 count, 47/46 mutant counts, targeted failure, and surviving-mutant statements are independently supported as described above. Historical records are preserved. Dates and authorization/disposition labels are documentary provenance, not independently authenticated authority.

CI export inspection finds the expected SHA and four successful jobs for run 40034728330. Run 40020290720 attempt 1 records only the macOS Intel Upload Proof report step failing; its lint, test and Proof steps succeed. Attempt 2 records success. This is internally consistent with the supplied account. The exports do not establish the ENOTFOUND error text, push grouping, or authenticity. No unresolved new finding blocks this focused closure.

The dossier itself is unchanged at this pinned snapshot and still awaits the subsequent closure/checkpoint completion contemplated by I-21 §8. This report supplies independent verification evidence; it does not claim that the later owner checkpoint has already been appended.

**4. New findings**

None. No concrete new defect requiring a numbered finding was independently reproduced.

**5. Verification limits**

The implementer's fresh-clone Proof runs, 9/9 and 20/20 step results, 228/228 validator result, approved-threshold status, 314 T0 passes, 1290 full-suite passes/three warnings, exit-127 wrapper attempts and reruns, golden digest execution result, and CI authenticity were not independently reproduced or authenticated. The supplied golden digest agrees with the historical recorded value; protected golden artifacts are unchanged. These remain documentary claims, not fresh validation evidence from this verifier. I did not run either prohibited Proof wrapper, the full suite, or T0 checks; focused tests, production immutability, and direct numerical/mutation checks were sufficient for this closure scope.

This is finite test and code-inspection evidence, not exhaustive numerical or mutation coverage. The two exploratory survivors remain documented limitations. No DR item, secular tolerance, T4/T5 requirement, final time step, T3 axis representation, or external corroboration question is resolved here. T1 remains **IMPLEMENTED — REVIEW PASSED — NOT ACCEPTED — NOT MERGED**; acceptance and merge eligibility decisions remain with the owner.

VERDICT: CLOSURE VERIFIED
