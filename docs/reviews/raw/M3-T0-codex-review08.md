**M3 T0 Review 08 — independent review of `95fff220ea164f2d837005a68f881fbded7c624c`**

The original Review 07 counterexamples are now described correctly, and no numerical algorithm changed. One verified documentation defect remains in the expanded input contract: the correction record excludes near-zero computed heights as impossible for exterior states, but strictly exterior, negative-energy states attain them and the function raises instead of returning the stated finite non-certification. R7-F1 is therefore PARTIALLY RESOLVED. No false certification, deficient force envelope or unsafe published floor was found. I made no fixes.

**Checkpoint, environment and integrity**

This checkout is detached at the full pinned SHA. Its local `origin/milestone-3-t0-reference-spike` ref equals HEAD; that is a local-ref observation, not verification of the live remote. History is `72f9e00` → correction `9afbbbf9bd274930cff9c5b777420062ed9c3d42` → validation `95fff220ea164f2d837005a68f881fbded7c624c`. The correction diff has 31 files, 2,850 insertions and 21 deletions. The full baseline diff has 583 files, 101,191 insertions and four deletions. All changed paths are under `docs/`. The protected-path diff against `86df2c3ff189db26f42bd273b6fe71de502c51a3` is empty.

Host: macOS 26.2, build 25C56, Darwin 25.2.0, x86_64. CPU model querying via `sysctl` was denied; `platform.processor()` reports `i386`, which does not identify the CPU model. Python 3.12.15, Clang 22.1.3; NumPy 2.5.3, SciPy 1.18.1, pytest 9.1.1, Ruff 0.16.10, Pydantic 2.13.5. The ready `.venv` was used without synchronization or network. Backend/compiler details are retained in `review_scratch/python-environment.log`. These measurements concern this host only.

The private console hashes to `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`; its Earth atmosphere table hashes to `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`. Both supplied hashes match. This verifies those two artifacts, not the asserted byte identity of the entire installations.

All five pinned artifacts match their supplied digests and unchanged baseline bytes; all 20 VAL-0019 script/table digests match. The correction evidence manifest's 20 entries match. Both historical Review 06 and Review 07 records at `72f9e00` are exact prefixes of their current files. Earlier raw evidence is preserved. VAL-0019/DR-0029 body corrections are inline; their old Review 06 logs remain and are qualified by appended logs. The superseded termination docstring is present at `72f9e00`.

My AST comparison strips every docstring and compares the entire module: `t0_termination.py` equals `72f9e00`. The implementer's AST script independently agrees when supplied the correct two file arguments. Every result JSON is unchanged against `72f9e00`. Constants, vehicle definitions, floors, brackets, margins, thresholds, contracts, protected baselines and goldens are unchanged. The added/extended executable test scripts are real changes; “documentation only” correctly describes the numerical implementation correction, not an absence of new executable tests.

**Execution ledger and inspected results**

The complete command and inspection ledger is `review_scratch/command-ledger.md`; exact subprocess arguments and mutations are preserved in the scratch scripts and individual logs. `D` below means `docs/science/experiments/m3-t0`, `S` means `review_scratch`, and all Python commands use `.venv/bin/python`.

| Command or driver executed | Independently observed result |
|---|---|
| `git diff 72f9e00..HEAD`; `git diff 86df2c3..HEAD`; protected/results/record diffs | Saved as `correction.diff`, `full.diff`, `protected.diff`, `results.diff`, `review-records.diff`; protected/results diffs empty |
| `pytest -q -p no:cacheprovider D/check_review0{1,2,3,4,5,6,7}.py` | **261 passed**, 188.34 s |
| Full `pytest -q -p no:cacheprovider` | **1,185 passed, 3 warnings**, 1,676.36 s (27m56s); warnings are from intentional overflow-rejection tests |
| M1 validator, `--out S/m1.json` | PASS, seven result records |
| M2 validator, `--out S/m2.json`, without `--quick` | PASS, **228** result records |
| `toolbox/scripts/gmat_m1.py compare`; `gmat_m2.py compare` | Both pass |
| `ruff check .` | All checks passed |
| `S/run_validation.py` | All nine experiments run twice, including GMAT with the absolute private console path; every command exits zero; no byte differences in either round |
| `S/red_before.py` | Current R7 checks on archived `72f9e00`: **3 failed, 20 passed**, reproducing the claimed documentation-only red/green distinction |
| `S/mutations.py` | Unmodified focused control: 23 passed; all 14 supplied R7 mutants detected; three of four new mutants detected by the focused checks |
| `S/extra_contract.py` against control and the surviving new mutant | Control passes; independent assertion detects the fourth mutant's false certification |
| `S/earlier_mutants.py` | Five historical corruptions detected by declared checks: R2 zero evidence, R4 underflow, R5 conversion, R6 zero b, R6 helper overflow |
| `S/finish_probes.py` | Independent boundary/M2 calculation, 1,850 C1 and 1,225 C2 exact-rational ratio checks, key old counterexamples, cap boundary, AST and append-only checks |
| `S/force_probes.py` | 159 finite force evaluations enclosed; 291 nonfinite extreme evaluations excluded under the no-overflow scope; 72 deliberately adversarial certified RK4 steps satisfy their stage bounds |
| `S/check_e4b.py` | 66 exact-product-boundary states have zero force; independent rational cap limit **91910196476947** |
| Committed seeded `adversarial_r7.py.txt` | All reported counts reproduced: 4,000 cases, 1,391 early returns, 727 early infinite A0 cases, 2,609 second-path cases, 1,212 second-path infinite enclosures, 1,014 certifications; 300 M2 cross-vehicle comparisons; 18,969 b_R cases |
| Copied Review 07 `test_noncert_contract.py` | One expected failure: its superseded universal-infinity assertion remains false |
| `S/test_lower_edge_contract.py` | **Two expected failures**, independently reproducing the new documentation finding for B_V1 and the drag-free vehicle |

All nine result files were parsed, inspected and regenerated: `t0_atmosphere_results.json`, `t0_axis_ablation_results.json`, `t0_decay_results.json`, `t0_frames_results.json`, `t0_geodetic_results.json`, `t0_gmat_results.json`, `t0_height_error_results.json`, `t0_regression_results.json`, and `t0_termination_results.json`. GMAT's generated scripts, reports, coefficient/table inputs and metadata were included in the byte comparisons. There are 97 tracked experiment files. Other inspected result files include `S/m1.json`, `S/m2.json`, both own mutation JSONs, the supplied 73-detection mutation report, both reproduction inventories and digest logs. Parsing historical evidence is not counted as executing it.

Reviewer invocation errors are retained: the first AST calls supplied the wrong arguments; the corrected file-to-file invocation and my own AST check pass. An initial boundary script did not catch the expected cap rejection; its completed version does. An initial force probe stopped on an overflowing model's NaN; its completed version explicitly records/excludes nonfinite cases. None was a product finding or silently counted as a passing check.

**Resolution table**

“Resolved” assesses each original defect under the disclosed scientific contract, rather than granting owner approval or a universal platform guarantee. Executed checks are evidence alongside the mathematical reasoning below.

| Item | Disposition | Separate evidence and reasoning |
|---|---|---|
| M3T0-R7-F1 | **PARTIALLY RESOLVED** | Original 1 m/subnormal-b example and both returned paths now agree with code. Independent 100-digit M2 calculation confirms the edge and vehicle independence. However, the broadened finite-need/input statements omit attainable exterior heights below β; the record's exclusion is false: R8-F1. |
| M3T0-R7-F2 | **RESOLVED** | Both active summaries now qualify b_R ≤ b with b > 0 and state b = 0 separately. The returned Decimal at zero is positive, about 1.49716862376135e-325. Exact-rational conversion checks and seeded shape probes corroborate downward rounding for positive b. |
| M3T0-R6-F1 | **RESOLVED** | Reexecuted masses k·2^-1074 for k=1…17, including all 16 zero-b masses. At k=1, model/envelope = 0.9999999999988138; k=17 gives 0.9705882352929661. R(0) follows directly from mass ≥ 2^-1074; zero-b-removal mutant fails 22 declared cases. |
| M3T0-R6-F2 | **RESOLVED** | Helpers correctly bracket signed infinities, finite values beyond ±MAX, subnormal/signed-zero values and exact rationals; NaN/types are rejected. The old overflow mutant fails five cases. Unbounded returned enclosures never certify; the remaining lower-height documentation defect is separately assigned to R7-F1/R8-F1. |
| M3T0-R6-F3 | **RESOLVED** | Exact affine cap recomputed independently; valid at 91910196476947, rejected at the next integer. E4b explicitly inherits A-FP-2 and the historical classification is amended. |
| Review 06 remark: 5,287-point search | **RESOLVED** | Record inspection and passing provenance check confirm the original search remains explicitly **UNREPRODUCED**, with old wording preserved. Resolution means honest provenance, not reproduction of that search. |
| Review 06 remark: b* and φ_B | **RESOLVED** | Switch formula cη₀/(c−1), c=φ(1−u), distinguishes stored and exact φ. Executed rational checks reproduce 7.416912861690675e-309 and 1.1125369292536007e-308, respectively. Both are labelled in the amended record. |
| M3T0-R5-F1 | **RESOLVED** | C1 and C2 carry absolute rounding terms; own exact-rational checks cover both constructions and extreme products. Original 17-/30-unit masses are enclosed, at ratios approximately 0.970588/0.55. Relative-only mutant fails seven declared cases. |
| M3T0-R5-F2 | **RESOLVED** | Reexecuted checks distinguish coefficient-subset maxima 0.9527274167782528/0.982821819954253 from transition maxima 0.9999999999988586/0.9999999999988518. Current bodies scope the 0.983 quotation correctly; history is amended. |
| M3T0-R4-F1 | **RESOLVED** | Original 190,681 km point gives drag 1.02021455e-315 against corrected 1.110700085e-315 m/s². Mixed absolute/relative terms, coefficient-division underflow and zero-density cutoff remain. Absolute-part-removal mutant fails eight declared cases. |
| M3T0-R3-F1 | **RESOLVED** | Original 120 km point is enclosed: model 0.062309014504142814 versus envelope 0.06230901450421387 m/s². Selection-height widening and all twelve downward-jump checks pass; the independent foot-point oracle is not the model's height/band implementation. |
| M3T0-R2-F1 | **RESOLVED** | Perturbed rows remain sampled estimates; between-sample refinement checks pass. Certified two-body maximization is separately labelled. No global perturbed missed-dip bound is claimed. |
| M3T0-R2-F2 | **RESOLVED** | Original 79,999.9/80,000 m example gives model 48.65837703993666 versus envelope 48.658377039936795 m/s². Density and co-rotation speed are maximized together; the checked derivative is negative throughout each band. |
| M3T0-R2-F3 | **RESOLVED** | Reexecuting the original zeroed sweep/floor corruption fails 22 declared checks. Coverage and independent recomputation prevent the original vacuous pass. This does not imply every possible mutation is covered. |
| IM-1 | **RESOLVED** | Both axis-ablation reruns reproduce bytes and the documented quadratic-only two-orbit RMS, 0.9856650955520649 m. Quantity, data and procedure are specified. |
| IM-2 | **RESOLVED** | Independently, need(111511.96,∞)=+0.0018399073878806404; need(111511.97,∞)=−0.008245909394966729. Governing floor/bracket and the owner's existing disposition are preserved. |
| M3T0-F1 | **RESOLVED** | Chord/curvature proof rechecked; worst-phase/midpoint cases and analytic two-body maximum checks pass. Perturbed sampling is not promoted into proof. |
| M3T0-F2 | **RESOLVED** | Exact stiffness roots, escape/co-rotation speed bound and admissible failing-stage example reexecute. Necessary screens are distinguished from sufficient floors; actual adversarial stages above the floors stay enclosed. The lower-height return-contract defect does not invalidate those sufficient floors. |
| M3T0-F3 | **RESOLVED** | Regenerated k2/k3/k4 offsets are approximately +116.312773/−115.734153/+1.161267 m; records identify the inward input as k3. |
| M3T0-F4 | **RESOLVED** | GMAT rerun reproduces 6.95223445873689e-6 m, correctly quoted as 6.95e-6 m against the unchanged 1e-4 m gate. |
| M3T0-F5 | **RESOLVED** | Documentation/authorization inspection preserves the controlling owner gates: P10 before T1 and P1–P10 before T2, regardless of narrower technical dependencies. This is a records conclusion, not a numerical computation. |

The separate GMAT geodetic-drag configuration discrepancy remains **ESCALATED_FOR_INVESTIGATION** under DR-0029 Q-G2-1/P6. Its reproduced outputs do not explain or resolve its cause. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided.

The stale `check_review05.py:9` inequality is an explicitly disclosed historical summary of the positive-b Review 05 pass. The active envelope contract and both statements named by R7-F2 now state the zero exception. I do not treat that historical sentence as a remaining active-contract defect.

**Mathematical assessment and adversarial attempts**

For missed crossings, g=h−chord has zero endpoints. If g''≤M, adding Mt(dt−t)/2 yields a concave function, hence g≥−Mt(dt−t)/2 and dip≤Mdt²/8. Exterior distance-Hessian eigenvalues are 1/(R_i+h), bounded with minimum curvature radius b²/a. Substitution of the negative-energy two-body speed relation gives the recorded radial function; checking endpoints and real stationary roots covers its maximum. This does not provide an analogous bound for a numerically sampled J2-plus-drag trajectory.

For E1–E3, the support-plane height is stationary at true geodetic latitude; its second derivative and the contraction tail give an absolute height allowance across cancellation. The kilometre conversion widens selection uncertainty. For true h≥L, reachable selection heights form a widened lower domain. The logarithmic derivative of density times co-rotation speed squared is negative within each pinned band under the recorded inequality, so the lower endpoint and subsequent bases suffice, including the unbounded top band. The absolute density/force terms cannot be discarded: their supremum is restricted using the derived zero-density height, not an imposed altitude cutoff.

For E4a, positive finite binary64 mass is at least t=2^-1074. Under C1 with b>0, P≥t and mixed rounding gives the product-ratio bound and P/mass≤max((1+u)/b,1/(b−t/2)). At b=0 the information retained is mass≥t, yielding p/mass≤p/t; taking the maximum with R(t) preserves monotonicity. For C2, positive rounded Q and mass are each ≥t; clamping their mixed lower bounds at t yields Q_lo and M_lo. Thus R=max(φ/b,R1,R2), with its separate zero endpoint, covers either construction. Decimal b_R=φ/R is rounded downward; because R≥φ/b, b_R≤b for positive b. At zero that inequality is inapplicable, while R remains the needed ratio bound.

I independently checked 3,075 exact C1/C2 constructions across subnormal, huge and mixed-scale cd/area/mass values. I also reran the zero/subnormal conversion counterexamples and exponent-spanning supplied probes. No ratio-bound violation appeared. These are counterexample searches supporting the algebra, not substitutes for it.

For E4b, given c₀≤5/8, the two area cases force the rounded numerator to zero at p≤t/2, including ties. Establishing that cap requires the density/libm allowance. My exact rational cap computation and 66 product-boundary force states exercise both cases and the integer cap boundary. They pass.

For stages, height is 1-Lipschitz in the exterior region, and the mixed binary64 displacement/velocity inequalities compose with E1 and the acceleration envelope. M2 contains H0,V,R0 and fixed constants only. The independent calculation gives M2(55749.39300208564)≈−8.570260040849265e-13 m, while the next float, 55749.39300208565, gives +6.450559689046285e-12 m. The stated binary64 edge is correct on the evaluating path.

When the early return is reached, need=−M2≥0. On the second path, need=−min(M2,M3,M4), so an outward −∞ stage lower bound cannot certify. The floor solver accepts only strict negativity; `libm_sensitivity` rejects ≥0; `floor_comparison` reports sufficiency using <0. `stage_stress` checks actual stages rather than converting nonnegative need into a certification. Result writers serialize those results. Explicit consumer probes reject +0, −0, finite positive and +∞ need. No NaN-returning normal path was found. Nonfinite h0 and invalid b raise in the supported evaluation region; very negative heights can fail earlier in Decimal sqrt.

Own force attempts included band bases and their neighbours, subnormal densities, the top-band cutoff, zero/subnormal b, speed zero/subnormal/11 km/s/1e10/1e100, and tiny masses. The 159 finite evaluations stayed enclosed; the tightest ratio was 0.9999999999999978. The 291 excluded nonfinite cases provide no affirmative evidence about an overflow-permitted domain. Seventy-two near-floor, near-escape inward/retrograde steps at equatorial and nearly polar positions satisfy every computed stage bound. Huge finite h0 through MAX was also probed as an arithmetic stress test; certifications there are not claims that overflowing model trajectories meet the no-overflow premise.

Mutation testing was deliberately bounded: all 14 new supplied R7 mutants, five representative older regressions, and four new reviewer mutants, because the numerical module's executable AST is unchanged and the complete 261-check control was already executed. This is not a rerun of all 73 supplied non-equivalent mutants. Three new mutants replace the early need with −0, make drag-free need infinite, or make M2 depend on b; focused checks detect them. A fourth drops M3 from the minimum and survives the focused checks. My independent injected-envelope probe returns +∞ at A0 and zero at A2: current code returns need=+∞ because M3=−∞, whereas that mutant returns −9929692.324580478 and falsely certifies. The independent assertion detects it. The injected envelope is a test of contract propagation, not an alleged physical force counterexample.

**New finding**

**M3T0-R8-F1 — NOTE — the lower-height exception is excluded using a false domain assertion, leaving the stated finite-need contract incomplete. VERIFIED.**

References: `docs/reviews/M3-T0-review-07.md:145`, `:147`, and especially `:155`; `D/t0_termination.py:1312`–`:1324` for the new finite-need wording and `:1340` for A0 evaluation before M2; `docs/reviews/M3-T0-review-06.md:195` for the amendment's unrestricted lower-height summary.

Take binary64 position r=[nextafter(6378137,+∞),0,0]=[6378137.000000001,0,0] m, v=0, mass=850 kg, Cd=2.2, area=15 m². Its exact equatorial height is **2^-30 = 9.31322574615478515625e-10 m**, strictly positive. Computed height equals it; energy is approximately −62494807.15136723 J/kg; density is finite and positive. This is a strictly exterior, bound state with no overflowing input calculation.

For h0 equal to that computed height and either B=850/33 or B=+∞, `stage_need` raises `ValueError: the envelope is defined above the lower edge only`. H0=(h0−β)/(1+α)−1e-35 is negative, so the A0 envelope rejects it before M2 is tested. The mathematical M2 is negative, but no finite need is returned. The surface point [a,0,0] also computes exactly h0=0.

The correction record acknowledges these exceptions but then says such h0 is not the computed height of a state outside the ellipsoid and the docstring claims nothing for it. The strictly exterior example disproves that exclusion, while the new docstring begins with bounds for any bound committed state at computed h0 and states finite need for the early-return and drag-free cases without this precondition. This is an incomplete description of unchanged behavior, not an algorithm regression. It does not falsely certify a step and does not affect a published floor.

Reproduce with `.venv/bin/python review_scratch/force_probes.py` or the focused `.venv/bin/python -m pytest -q -p no:cacheprovider review_scratch/test_lower_edge_contract.py`. The latter has two expected failures on the current candidate. Exact inputs, values and exception text are in `force-probes-complete.log` and `lower-edge-contract.log`.

Recommended correction: keep numerical behavior unchanged; document the prerequisite for returning a numeric need and the lower-height exception path, amend the false exterior-domain sentence, and qualify the relevant finite-need summaries. Add a regression using a strictly exterior state below β. Separately retain the very-negative-height Decimal exception as outside the exterior-state scope. Do not silently change the floor/domain policy to hide the exception.

**Assumptions, guarantees and limits**

- **A-FP-1:** honestly states binary64, nearest-even, gradual underflow and mixed absolute/relative errors. Its mathematical consequences follow under that mode; host probes pass. The operating mode is not proved for other platforms.
- **A-FP-2:** honestly labels the libm mixed error bound as unresolved and conditional. The relative coefficient is LIBM_ULP·2^-52 and the absolute coefficient LIBM_ULP·2^-1074; the label “ulps” is interpreted through this formula, not as a correctly-rounded-library theorem. Host measurements and libm-sensitivity results are not universal guarantees. E4b's inherited dependence and cap are explicit.
- **A-FP-3:** honestly states elementwise products and the mixed three-term dot-product allowance. The proof is conditional on that evaluation behavior; this host's NumPy execution does not prove every backend's behavior.
- **C1/C2 scope:** explicitly specified in E4a and the active envelope contract, including positive finite mass/cd/area. It does not cover arbitrary independently supplied mass/b pairs. Zero b under C1 is covered; C2 with zero b cannot construct positive mass. Historical “every vehicle” summaries must be read with those constructions, not as lifting them.
- **Overflow exclusion:** stated explicitly, including quotient overflow to +∞. E4b's zero-product case is separate. An infinite enclosure does not prove an actual model force overflows. My nonfinite force cases and huge-height arithmetic probes do not relax the exclusion.
- **Lower-height contract:** incompletely stated as detailed in R8-F1; exterior/no-overflow premises do not exclude all h0≤β. This defect is independent of the honestly disclosed floating-point assumptions.

Unconditionally established here are snapshot/digest/diff facts, observed host executions, the counterexample, and exact-arithmetic implications from explicit premises. The sufficient numerical floors remain conditional on A-FP-1/2/3, the specified model/vehicle construction, exterior finite computations without overflow, negative two-body energy, no thrust and dt=10 s. The published floors reproduce exactly: 124456.68544510857, 118633.50894662621 and 111511.96182508787 m. Their positive margins reproduce as 7.170720652771883e-7, 1.0038993351683625e-6 and 8.427938228380506e-7 m. No universal cross-platform libm or perturbed missed-crossing guarantee is established.

I could not access CI runs **39537301986** or **39543277180**, fetch the live remote, or inspect current protection/settings. Their successful four-job status remains documentation-only. CI does not collect the T0 checks (`testpaths=["tests"]`). The prohibited nine-/twenty-step Proof wrappers were not run; supplied wrapper PASS logs remain historical claims, distinct from my executed validators/compares. I did not rerun the entire 73-mutant matrix, recover the original 5,287-point search, prove a global libm theorem, test other OS/CPU/library platforms, verify printed-source provenance, or determine the cause of the GMAT escalation. I verified the current correction's numerical counts and values through the executions described above, not every historical planning number or historical CI event.

Final tracked status and diff-stat are recorded in `review_scratch/final_status.txt` and `review_scratch/final_diff_stat.txt`: both empty. Exactly **zero tracked files changed**, including regenerated experiment/GMAT artifacts; no checkout restoration was necessary. Reviewer scripts, logs and this complete review are confined to `review_scratch/`.

T0 is not accepted. Because R7-F1 remains partially resolved, the prescribed verdict is REQUEST_CHANGES even though the new defect is a NOTE and no unsafe certification was found. The next step requires Tech Lead authorization for the bounded documentation/validation correction and any subsequent independent review. I have made no correction, started no Review 09, prepared no acceptance dossier, merged nothing, begun no T1/T2 work and decided no owner proposal.

VERDICT: REQUEST_CHANGES
