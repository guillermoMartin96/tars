# M3 T0 Review 06

The correction covers both Review 05 counterexamples, but the unrestricted C1 conversion still has an uncovered boundary: positive mass can produce a rounded ballistic coefficient of zero without overflow. The model then computes finite, nonzero drag while the envelope raises `ZeroDivisionError`. This is a verified MINOR finding. No unsafe published floor is demonstrated. No fix was made.

**Checkpoint and integrity.** Reviewed detached HEAD `fcd5997cd120c8834651d3c0da2e52899f2d9ffc`; local `origin/milestone-3-t0-reference-spike` matches. Initial and final tracked trees are clean. Both requested diffs were generated and inspected. The correction changes 25 files, all under `docs/`; the complete T0 diff also changes only `docs/`. The protected-path diff against `86df2c3` is empty. All five pinned artifact digests and both supplied GMAT digests match independently.

CI for `411cabd` and `fcd5997` could not be accessed offline. Its success remains an implementer claim; I cannot certify that external precondition or remote synchronization. No observed local precondition failed. The explicit offline review proceeded with this limitation, not an assertion that CI was independently verified. No commit or push was made: this snapshot review writes only to `review_scratch/`, as instructed.

**Ledger and evidence.** The complete command ledger is `review_scratch/command-ledger.md`. It includes inspections, script creation, exact driver locations, unsuccessful probes, the interrupted optional test run and final hygiene checks. `execution.json` records the exact experiment subprocess arguments, exits and timings; `mutation-subset.json` records the selected mutation commands and failures. Scripts and logs remain under `review_scratch/`.

| Independent execution | Result |
|---|---|
| Explicit `check_review01.py` through `check_review05.py` | **157 passed**, 174.43 s |
| Current `check_review05.py` copied onto archived `17b2229` docs, without a shim | **17 failed**, 1.51 s |
| All nine experiment scripts, including GMAT using the absolute console path | Every command exited 0; all inventoried experiment bytes unchanged |
| Ten R4 and ten R5 mutants, each against its declared tests | **20/20 detected** by actual declared failures |
| Standalone M1 validator | PASS |
| Standalone M2 validator, without `--quick` | PASS, **228 results** |
| GMAT M1 and M2 compare commands | PASS |
| Independent exponent-spanning rational vehicle checks | 6,657 positive finite constructions: no ratio, downward-rounding or adjacent-b monotonicity violation; 613 further C1 cases rounded to zero b |
| Additional E4b checks | 366 states, including exact half-subnormal product boundaries: zero force |
| New independent zero-b regression | **1 failed**, at the envelope's division by zero |
| Optional project pytest run | Interrupted deliberately: **293 passed**, 286.06 s; not a full-suite PASS |

The supplied 45-mutant report was also audited: 44 detections, one declared equivalent mutant and a passing control; every recorded detection includes a declared failed check. My rerun selected all ten R4 and all ten R5 mutants and executed their declared checks, rather than rerunning the entire five-file suite for each mutant. The two C1-product/C2-only mutations fail lemma checks; applying b_R only to the relative part fails envelope recomputation. These observations support the claimed reasons for detection. They do not establish exhaustive parameter coverage: zero b is absent from the committed grid and explicitly filtered out by the implementer's exhaustive sweep.

Result files inspected include all nine committed/regenerated `t0_{atmosphere,axis_ablation,decay,frames,geodetic,gmat,regression,termination,height_error}_results.json`, supplied mutation reports and correction logs, my `m1.json`, `m2.json`, mutation results, hash inventories and comparison logs. `inspected_files.json` inventories collected records and result files; `inspections.log` preserves their text. Collection is not a claim that every historical number was independently proved.

The five independently recomputed pinned hashes are:

- `proof/thresholds/m1.json`: `446e75ee8d5129a346263b5b06f873e0aed74c33fd756564e43423bbd16fdb3d`.
- `proof/thresholds/m2.json`: `9d4eab47133a4f9eb1125cf7242ada0c720fbe9e4b8dd12b0f698cc79e5f0ce9`.
- GMAT M2 manifest: `f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585`.
- M2 reference snapshot: `a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b`.
- M2 final states: `dc3baf7abb209a11ca463b9ca5001ce886c62b92b191ac76249d32924aa951dc`.

Their bytes also equal the accepted baseline. GMAT console and installed atmosphere hashes match `1162803d…52e2` and `75762f67…a85e`, respectively. All 18 current VAL-0019 script/table digest assertions match. See `digests.log`; the ledger identifies and corrects an initial reviewer parser that matched no relative paths.

**Resolution table.** Partial dispositions below concern the unrestricted replacement contract, not an observed failure at either illustrative vehicle's published floor.

| Item | Disposition | Independent evidence and reasoning |
|---|---|---|
| M3T0-R5-F1 | PARTIALLY RESOLVED | Both original counterexamples are covered; the positive-b conversion inequalities hold in additional exact-rational checks. C1 can also produce zero b from positive vehicle parameters, leaving the unrestricted contract undefined: R6-F1. |
| M3T0-R5-F2 | RESOLVED | Both empirical populations recompute to the corrected numbers; P1 displays the transition maximum; Review 04's historical sentence is retained and followed by an amendment. |
| M3T0-R4-F1 | PARTIALLY RESOLVED | The coefficient/division, density and other absolute underflow terms survive recomputation and all ten R4 mutant checks. The force decomposition composes correctly with positive-b E4a. Its unrestricted vehicle coverage still omits C1's zero quotient. |
| M3T0-R3-F1 | PARTIALLY RESOLVED | Selection-height widening, the support-function height argument and all downward-jump checks cover the original defect. These do not repair the undefined conversion boundary in the replacement global envelope. |
| M3T0-R2-F1 | RESOLVED | Rerun preserves the certified two-body/sampled perturbed distinction; between-sample refinement remains explicitly an estimate. |
| M3T0-R2-F2 | PARTIALLY RESOLVED | The height-dependent co-rotation factor is maximized with density over the candidate heights, rather than frozen at the lower edge. Its original counterexample passes. The advertised unrestricted envelope remains undefined for zero-b C1 vehicles. |
| M3T0-R2-F3 | RESOLVED | Recomputing checks pass and the mutation machinery requires declared failures. Selected corruptions genuinely fail; the new boundary coverage gap is separately identified. |
| IM-1 | RESOLVED | Axis-ablation rerun is byte-identical and reproduces approximately 0.9856650955520649 m RMS with a documented procedure. |
| IM-2 | RESOLVED | Governing bracket ends remain explicit. The drag-free nearest-centimetre quotation fails the condition; 111511.97 m satisfies it. Existing owner-directed disposition retained; no floor changed. |
| M3T0-F1 | RESOLVED | Chord/curvature argument and the independently recomputing checks remain sound; experimental rerun preserves the sweeps and distinct perturbed-motion limitations. |
| M3T0-F2 | PARTIALLY RESOLVED | Exact stiffness thresholds, escape/co-rotation speed bound, inadmissible-stage counterexample and fixed-vehicle stage tests reproduce. The generalized sufficient-condition evidence still relies on the incomplete unrestricted vehicle-conversion contract. |
| M3T0-F3 | RESOLVED | Recomputed stage offsets identify the k3 input as the inward stage. |
| M3T0-F4 | RESOLVED | GMAT rerun reproduces the corrected approximately 6.95e-6 m residual; approved gates are unchanged. |
| M3T0-F5 | RESOLVED | Matrix and authorization distinguish technical dependencies from owner gates: P10 before T1, P1–P10 before T2. |

**Independent mathematical assessment.** Write p = cd·area exactly and t = 2^-1074 = 2η₀. For C1 with positive finite b, P is positive, hence P ≥ t and p > η₀. The mixed rounding alternatives give

`p/P ≤ min(max(1/(1−u), p/(p−η₀)), p/t)`.

The quotient alternatives give `mass/P ≥ min(b/(1+u), b−η₀)`. Positive binary64 b implies b ≥ t, so both denominators are positive and inversion gives the stated R1. This derivation is valid for subnormal p and mixed intermediates; using exact rational inputs avoids prematurely rounding the product. Its missing case is precisely b = 0: positivity of mass does not imply positivity of its rounded quotient.

For C2, a positive finite mass requires positive Q. Thus Q and mass are each at least t. Taking the minimum of the normal relative and underflow absolute lower bounds, then clamping at t, gives Q_lo. Applying the same reasoning to Q·area gives M_lo. Monotonicity of the positive product makes substituting Q_lo safe, so p/M_lo bounds p/mass. This uses the positive-mass premise; C2 constructions that round mass to zero do not define a positive-mass vehicle. Overflowing intermediates are excluded separately, not repaired by the lemma.

For fixed positive cd and area, R1 decreases with b. Q_lo and M_lo are non-decreasing, so R2 is non-increasing; the maximum with φ/b is therefore non-increasing. My adjacent-b rational comparisons support this derivation. For the V1 shape, the switch using the **stored outward-rounded** φ is `7.416912861690675e-309`, consistent with the quoted 7.42e-309. Using the exact rational φ_B instead would give `1.1125369292536007e-308`; these constants should not be conflated. The committed switch check uses the stored constant.

For positive b, b_R = φ/R is rounded downward by Decimal division with ROUND_FLOOR. The ordinary b object is returned unchanged when R = φ/b. I checked both properties over 6,657 additional constructions. Both relative and absolute envelope routines receive b_R. In particular, N_ρ/(2b_R) and every reciprocal-vehicle term in W use it. S_max, h_zero and τ have no vehicle conversion to replace. Independent rational checks also confirm that dividing the stored F_D and F_A by the stored φ preserves their required exact-factor bounds; the different outward-rounded constants do not introduce a lost factor here.

E4b's final arithmetic argument is sound **given its density cap**. At p ≤ η₀, when area ≤ 1/4 the post-cd product times area is strictly below η₀. Otherwise positivity and binary64 spacing force cd = t and area ≤ 1/2; the last product is at most η₀, with equality rounding to zero by ties-to-even. The exact boundary and neighbouring product constructions were exercised. Then division by positive mass and multiplication by finite velocity factors preserve zero. The derived cap is approximately `0.6125000000000004 < 5/8`. That cap inherits A-FP-2 through the density calculation; see R6-F3.

**Floors and invariants.** The regenerated termination output differs from `17b2229` only by the two advertised additions: `/floating_point_enclosure/constants/zero_force_c0_max` and `/sufficient_stage_condition/review05_counterexamples`. No pre-existing value changes. Experiment reproduction and the JSON comparison independently confirm this.

| Vehicle | Published floor, m | Recomputed root bracket, m | Positive condition margin, m |
|---|---|---|---|
| B25.8 | 124456.68544510857 | [124456.68544484391, 124456.68544484489] | 7.170720652771883e-7 |
| B100 | 118633.50894662621 | [118633.5089461096, 118633.50894611058] | 1.0038993351683625e-6 |
| Drag-free | 111511.96182508787 | [111511.96182425194, 111511.96182425291] | 8.427938228380506e-7 |

Before/after brackets coincide. Sensitivity checks reproduce log2 libm allowances 5/6/7 for these ends and 19/17/20 for upward centimetre quotations. No vehicle, constant, table, root, margin, baseline, golden, threshold, contract, dependency or production file changed in this correction. The experiments' isolation and decision authority remain intact.

**R5-F2 and provenance.** My recomputation gives coefficient-subset maxima `0.9527274167782528` for B25.8 and `0.982821819954253` for B100. The committed transition-scan subnormal-density maxima are `0.9999999999988586` and `0.9999999999988518`. These round to the corrected quotations. The new procedure makes the subset measurement reproducible now; it does not reconstruct its historical ad-hoc execution.

The historical 5,287-point search and its 161 superseded-envelope violations remain an unverified provenance claim. I did not recover or reproduce that original search. The inspected Review 04 amendment describes the ad-hoc origin of 0.983 but does not explicitly mark the separate 5,287-point search as an open provenance gap. It must not be counted as independently reproduced evidence. This limitation does not undermine the recomputed population maxima or constitute a new numerical counterexample.

**Assumptions and scope.**

- **A-FP-1:** The mixed IEEE binary64 model is appropriate under round-to-nearest-even and gradual underflow. Underflowing sums of binary64 operands are exact; nonzero square roots of nonzero binary64 values cannot be subnormal. Operating mode is a condition, not a universal fact about every host. Host probes pass. The missing zero quotient in E4a is not an exception to IEEE arithmetic.
- **A-FP-2:** The records generally disclose the relative-plus-absolute libm bound as unresolved. Its acceptability is an owner decision. It is a legitimate explicit condition for a mathematical guarantee, and its unresolved status alone is not my reason for REQUEST_CHANGES. Host measurements, weakened required allowances and CI are different kinds of evidence; none proves a universal library guarantee. The E4b classification needs the qualification in R6-F3.
- **A-FP-3:** Elementwise products and the mixed dot-product allowance are disclosed. The derivation is conditional on this evaluation behavior; host execution is not a portability theorem.
- **C1/C2 scope:** The constructions are stated in E4a, the envelope and P1, and cover the illustrative vehicles. They do not authorize arbitrary independently supplied mass/b pairs. The broader “every vehicle/no vehicle condition” summaries are incomplete because C1 may round a positive mass ratio to zero. Restricting the lemma silently to positive computed b would introduce exactly the missing vehicle condition; it would not fulfill option (b).
- **Overflow exclusion:** Explicit and generally honest, including C1 quotient overflow to +infinity. C1's P = 0 case is treated separately by E4b. The zero-b counterexample has no overflow and is not excluded by that condition. Infinite envelope bounds are conservative numerical bounds, but their existence does not establish that every actual force overflows.

Unconditionally established here are the snapshot/file facts, observed host executions and reproductions, and exact-rational implications from their stated premises. The stage-floor guarantees remain conditional on the stated floating-point assumptions, exterior/finite computation domain, no thrust, negative two-body energy, dt = 10 s and specified vehicle construction/shape. They are not unconditional cross-platform guarantees. No unrestricted all-positive-vehicle envelope guarantee is established at this checkpoint.

**New findings.**

**M3T0-R6-F1 — MINOR — C1 underflow to zero b remains outside the purported unrestricted conversion. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:585`–`:595`, especially the unsupported b ≥ 2η₀ inference at `:589`; division at `:849`; envelope conversion at `:911`. Unrestricted claims: DR-0029 `:101` and `:466`; `docs/science/validation.md:816`; `docs/milestones/M3-T0-report.md:37`; decision-matrix opening status paragraph. The implementer sweep filters the case out at `docs/reviews/raw/M3-T0-review05-findings-correction-evidence/exhaustive_e4a.py.txt:18`.

Reproduce with `.venv/bin/python review_scratch/zero_b.py` or the independent failing regression `.venv/bin/python -m pytest -q -p no:cacheprovider review_scratch/test_zero_b.py`.

Use the unchanged shape cd = 2.2, area = 15 m²; mass = 2^-1074 kg; r = (186378137, 0, 0) m; v = 0. Then P = 33 and C1 gives **b = 0**. True and computed height are exactly 180000000 m; energy is negative. Density is `2.5706399040162615e-305`; the coefficient is `8.585004598740571e19`; computed drag is finite and nonzero, approximately `1.58576009e28 m/s²`. The bound raises `ZeroDivisionError: Fraction(1, 0)`. The regression uses mass = 16·2^-1074, immediately below the original 17-unit case, and fails identically after checking finite force and host exp/pow errors against A-FP-2.

Positive mass and finite b do not imply b ≥ 2η₀. This case satisfies the stated vehicle/exterior/no-overflow conditions and cannot be discarded as an overflowing force or a zero-mass vehicle. It does not show an unsafe published floor.

Recommended correction: cover rounded-zero C1 quotients while preserving the authorized unrestricted vehicle domain, propagate that case through the envelope, and add boundary regressions. For example, the available positive-mass fact mass ≥ 2η₀ provides additional ratio information even when the quotient loses all information. Do not silently impose b > 0 as a new vehicle prerequisite. Reassess the affected global-contract dispositions after correction.

**M3T0-R6-F2 — NOTE — infinity handling is narrower than the helper's advertised contract. VERIFIED.**

References: `t0_termination.py:489`–`:499`; Review 05 record's “Outward rounding” paragraph. Reproduce with `review_scratch/probe.py` or `infinity.py`.

`_up(Fraction(2**1024))` still raises `OverflowError` before reaching the new infinity branch. `_up(-Decimal(2)**1024)` returns -infinity, which is not an upper bound on that finite negative number. `_dn(Decimal('-Infinity'))` raises on Fraction conversion. Positive Decimal overflow does return +infinity as intended. An infinite A0 can propagate through Decimal stage arithmetic to a negative-infinite lower bound and fail in `_dn`; `stage_lower_heights(1e7, 2^-1074)` demonstrates that path.

The audited live upper-bound callers use nonnegative quantities; published floor searches and result files remain finite. I have not demonstrated an unsafe accepted floor or an in-domain full RK4 trajectory from these helper probes, so this is a NOTE. Recommended correction: accurately scope the helper claim or make signed/type-specific overflow behavior consistent, and ensure an unbounded stage enclosure produces an explicit non-certification result rather than an incidental conversion exception.

**M3T0-R6-F3 — NOTE — E4b's evidence classification omits its inherited density assumption. VERIFIED.**

References: `docs/reviews/M3-T0-review-05.md:159` and `:167`; `t0_termination.py:598`–`:599` and the c0_max calculation in `rounding_allowances`.

The classification puts E4b under “Derived under A-FP-1,” but c₀ ≤ 5/8 is obtained using the density/libm allowance. `review_scratch/e4b-dependency.py` deliberately replaces exp by 4, retaining IEEE arithmetic while violating A-FP-2; at cd = 2^-1074 and area = 1/2 the force becomes nonzero. This is a dependency demonstration, not a counterexample under all declared assumptions. The main P1 enclosure already names A-FP-2, which limits the consequence to the classification wording.

Recommended correction: distinguish the algebraic implication “c₀ ≤ 5/8 implies zero force under A-FP-1” from establishing that density cap using A-FP-2. Do not characterize the latter as independent of the unresolved library condition.

**Verification limits and readiness.** I did not run the prohibited Proof wrappers, the full 45-mutant matrix, the original 5,287-point search, the implementer's 219,983-vehicle sweep, two fresh-clone reproductions, or other platforms. The optional project suite was interrupted; the implementer's complete 1185-test result remains documentation evidence. Standalone validators and the GMAT comparisons are separate executed evidence, not substitutes for an asserted wrapper run. CI, external-source provenance, remote protection and synchronization were inaccessible. Not every historical number in append-only planning records was independently re-derived; corrected conversion/maxima claims, floors, roots, margins and current digest assertions received the checks described above.

The GMAT geodetic-drag discrepancy remains escalated; reproducing its outputs does not identify or close its cause. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided. Existing IM-2 disposition is unchanged. No acceptance, merge, T1/T2 work, correction or Review 07 was started.

Final `git status --porcelain` and `git diff --stat` are empty. **Exactly zero tracked files changed**, including regenerated experiment and GMAT artifacts; no checkout restoration was necessary. Complete review and evidence are confined to `review_scratch/`.

T0 is not ready for an acceptance-candidate recommendation. The next action requires the Tech Lead's authorization to address R6-F1 and validate the correction; this review makes no correction and awaits that decision.

VERDICT: REQUEST_CHANGES
