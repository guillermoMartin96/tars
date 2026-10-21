# M3 T0 Review 09

Reviewed checkpoint: `f04f9955d5ae714cc61144990395b8225a379968`, detached HEAD, with local `origin/milestone-3-t0-reference-spike` at that commit. Remote URL: `https://github.com/guillermoMartin96/tars.git`; no live remote verification was possible. The initial tracked tree was clean. This is an independent review; I made no correction.

The R8-F1 correction describes the default implementation's near-surface behavior correctly, and the original M3-dropped mutant is now detected. Every earlier resolution-table item is RESOLVED. Two new verification/precision NOTEs below do not establish an unsafe certification in the current implementation.

## Ledger and validation

All reviewer artifacts are in `review_scratch/`. The command ledger comprises `commands.jsonl`, `inspection_commands.md`, and the retained scripts, which specify their internal subprocess commands. Logs preserve errors as well as successful retries. `record_extracts.txt` inventories 35 records read, including Reviews 01–08, their prompts, I-15, decision requests, assumptions and validation. The complete requested diffs are `correction.diff` (`115e747..HEAD`) and `full.diff` (`86df2c3..HEAD`). `changed_files.txt` gives the exact correction-pass file list, including every evidence file; `reviews_diff.txt` preserves the historical-record diff.

Environment: macOS 26.2, Darwin 25.2.0, x86_64; Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1, Accelerate BLAS/LAPACK (`env.log`, `uname.log`). CPU model and process inventory queries were denied by the sandbox; no CPU model is independently established. The runs use the supplied locked `.venv`, with no network or dependency changes.

Executed validation:

- Review 01–08 checks: **288 passed**, 194.04 s (`checks.log`). These checks are separate from the project suite.
- Red-before reconstruction at `115e747`, adding only the new check file in a scratch copy: **2 failed, 25 passed**. The failures are the docstring and record checks (`red_before.py`, `red_before.log`).
- Full project pytest: **1185 passed, 3 warnings in 1711.68s (0:28:31)** (`pytest.log`).
- M1 validator: **PASS** (`m1.log`, `m1.json`); M2 validator: **PASS**, 228/228 checks (`m2.log`, `m2.json`). Both write only into scratch. M1 and M2 GMAT compares exit 0 (`m1_compare.log`, `m2_compare.log`). These are not executions of the prohibited nine-/twenty-step Proof wrappers.
- All **14 R8 mutants** are detected by declared checks, with no unrelated failure (`smoke_r8.log`). Six selected earlier non-equivalent mutants are detected: zeroed R2 evidence, removed R3 height allowance, superseded R4 envelope, relative-only R5 conversion, R6 helper overflow, and libm-independent E4b cap. The two declared equivalents pass their establishing checks (`old_mutants.json`). This is a justified subset, not a full 87-mutant rerun: the executable AST is unchanged, all 288 control checks ran, and every new R8 mutant plus representative older mechanisms was exercised.
- My additional finite-M3 mutant **survives all 288 checks**, while an independent injected-envelope probe exposes its wrong sign (`new_mutants.py`, `new_mutants.log`, `new_mutant_checks.log`). See R9-F1.
- Every one of the **nine T0 experiments ran twice**, including GMAT, height-error and axis-ablation. All **98 tracked experiment files** were byte-identical after each complete run (`reproduce.py`, `reproduce_absolute.log`, `repro_1_changes.json`, `repro_2_changes.json`: both `[]`).
- The GMAT console SHA256 is `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`; the installed atmosphere table is `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`. Both independently match (`integrity.log`).
- Five pinned digests and **21 current spike digests**, not 20, match (`digests.log`). The additional entry is `check_review08.py`. All 19 correction-evidence manifest entries match (`math_audit.log`); this establishes stored-byte integrity, not the truth of their contents.
- `protected.txt` and `results_diff.txt` are empty: no change since the accepted baseline in `src proof toolbox scenarios tests .github uv.lock pyproject.toml`, and no result JSON change since Review 08. All full-T0 changes are under `docs/`. Independent AST canonicalization confirms no executable change in `t0_termination.py` (`math_audit.py`); the supplied comparison also passes (`ast_fixed.log`). Review 06, 07 and 08 records each have their old bytes as an exact prefix (`integrity.log`).

All nine result files were parsed and inspected: `t0_atmosphere_results.json`, `t0_axis_ablation_results.json`, `t0_decay_results.json`, `t0_frames_results.json`, `t0_geodetic_results.json`, `t0_gmat_results.json`, `t0_height_error_results.json`, `t0_regression_results.json`, `t0_termination_results.json`. The byte comparisons also include GMAT scripts, reports, inputs and metadata.

Reviewer setup failures are retained and resolved, not counted as scientific failures. An initial AST invocation supplied revision names where filenames were required. An initial reproduction resolved the Python executable symlink out of its virtual environment; the next resolved the GMAT launcher symlink and thereby changed the harness's inferred install root. Preserving both absolute launcher paths fixed these errors without changing the harness or GMAT installation. One near-escape probe initially rounded its computed energy to zero; reducing speed to `(1−10^-12)·vesc` made the required strict negative-energy premise explicit.

## Resolution table

Each row has exactly one disposition. “Resolved” assesses the original defect under its disclosed contract; it does not approve an owner decision or establish a universal libm guarantee.

| Item | Disposition | Separate evidence and reasoning |
|---|---|---|
| M3T0-R8-F1 | RESOLVED | Execution confirms the equatorial 1–9 ulp exterior states reject, for B_V1 and infinity; k=10 returns `55993.323394842984` m. Surface, pole, β and neighboring-float checks pass. The docstring and appended record qualifications now disclose the attainable exterior rejection and distinguish computed from mathematical height. The very-negative exception is separately documented. R9-F2 concerns a tiny ellipsoid/precision inconsistency in the illustrative pole calculation, not this rejection contract. |
| R7-F1 | RESOLVED | `stage_need(1,2^-1074)=55992.318990613036`, finite and positive despite infinite A0. Path 1 returns −M2 only after A0 succeeds; path 2 returns −min(M2,M3,M4). The new prerequisite closes the prior incomplete finite-return statement. Every inspected consumer certifies only strict negativity. |
| R7-F2 | RESOLVED | Active E4 and envelope summaries restrict b_R≤b to b>0. At zero the positive Decimal coefficient is about `1.49716862376135e-325`; the needed inequality remains R≥cd·area/mass. Exact conversion and dedicated checks pass. |
| R6-F1 | RESOLVED | The zero-b branch uses mass≥2^-1074 and max with R(tiny), rather than dividing by zero. Reexecuted k=1…17 counterexamples and exact constructions cover zero and its transition; the k=1 model/envelope ratio is about `0.9999999999988138`. |
| R6-F2 | RESOLVED | Extreme-helper tests cover signed infinities, out-of-range finite rationals, NaN rejection, signed zero and subnormals. Infinite enclosures do not certify on either implemented path; rejected inputs do not become bounds. The old overflow mutant fails five cases. |
| R6-F3 | RESOLVED | The cap explicitly inherits A-FP-2. Independently solving its exact affine inequality yields integer limit `91910196476947`; that value is accepted and the next is rejected. The libm-independent mutant fails. |
| Review 06 remark, 5,287-point search | RESOLVED | The original sentence remains preserved and explicitly amended **UNREPRODUCED**. Its script, seed and output remain unavailable; no conclusion here uses it. This is a provenance resolution, not reproduction of the search. |
| Review 06 remark, b* and φ_B | RESOLVED | Independent rational calculation of cη₀/(c−1), c=φ(1−u), gives `7.416912861690675e-309` for stored φ and `1.1125369292536007e-308` for exact φ. The records distinguish them. |
| M3T0-R5-F1 | RESOLVED | C1/C2 conversion bounds include absolute rounding errors and positive-subnormal lower limits. Own exact-product grids and the old 17-/30-unit counterexamples are enclosed; the relative-only mutant fails. No arbitrary independently chosen mass/b contract is inferred. |
| R5-F2 | RESOLVED | Dedicated recomputation distinguishes coefficient-subset maxima `0.9527274167782528` / `0.982821819954253` from transition maxima `0.9999999999988586` / `0.9999999999988518`. The 0.983 quotation is scoped accordingly, with historical text preserved. |
| R4-F1 | RESOLVED | The 190,681 km example reproduces drag `1.02021455e-315` versus corrected envelope `1.110700085e-315` m/s². Absolute terms and the zero-density cutoff remain; the superseded-envelope mutant is detected. |
| R3-F1 | RESOLVED | The 120 km counterexample reproduces model `0.062309014504142814` versus corrected enclosure `0.06230901450421387` m/s². Selection-height uncertainty crosses density jumps; all downward-jump checks and the allowance-removal mutant behave as required. |
| R2-F1 | RESOLVED | Reexecuted sweep/refinement checks distinguish sampled perturbed estimates from certified two-body bounds. No combined J2/drag missed-dip proof is claimed. |
| R2-F2 | RESOLVED | The 79,999.9/80,000 m example remains enclosed (`48.65837703993666` versus `48.658377039936795` m/s²). Density and co-rotation speed are maximized together; the bandwise derivative argument includes the top band. |
| R2-F3 | RESOLVED | The original zeroed-evidence mutant fails 22 selected cases, including coverage, sweep-dip and floor checks. This closes that vacuity defect; it does not imply complete mutation coverage. |
| IM-1 | RESOLVED | Both axis-ablation runs reproduce bytes and the quadratic-only two-orbit RMS `0.9856650955520649` m. Data, fit and quantity are specified. |
| IM-2 | RESOLVED | Independently `need(111511.96,∞)=+0.0018399073878806404`, while `need(111511.97,∞)=−0.008245909394966729`. The nearest-centimetre quote is identified as insufficient; the actual floor and ordered disposition remain unchanged. |
| M3T0-F1 | RESOLVED | The chord/curvature bound, worst-phase examples and analytic two-body maximization checks pass. Replacing a fixed-phase estimate with the endpoint/stationary-point argument avoids the original missed-crossing error. |
| M3T0-F2 | RESOLVED | Stiffness roots, escape/co-rotation bound and the admissible failing-stage example rerun. Necessary screens remain distinct from sufficient floors. Independent adversarial certified steps remain inside every stage bound. |
| M3T0-F3 | RESOLVED | Regenerated stage numbering identifies the inward input as k3; k2/k3/k4 offsets remain approximately +116.312773/−115.734153/+1.161267 m. |
| M3T0-F4 | RESOLVED | GMAT reruns reproduce the `6.95223445873689e-6` m residual, correctly quoted as 6.95e-6 against the unchanged 1e-4 m gate. |
| M3T0-F5 | RESOLVED | Authorization/decision-matrix inspection retains P10 before T1 and P1–P10 before T2. Technical dependencies do not override owner gates. This conclusion is documentary. |
| Review 08 M3 coverage observation | RESOLVED | The exact unconditionally M3-dropped mutant is detected by the new first-stage-infinity check for the intended reason: M3 alone prevents certification. R9-F1 identifies a narrower surviving corruption, rather than claiming this entire logic is exhaustively protected. |

Separately, the GMAT geodetic-drag discrepancy remains **ESCALATED_FOR_INVESTIGATION**, DR-0029 Q-G2-1/P6. Reproducibility does not resolve its cause. DR-0029 P1–P10 and DR-0028 P6(b) remain undecided.

## Derivation, semantics and adversarial attempts

For default FP and the default envelope, H0=(h0−β)/(1+α)−10^-35. At h0=β it is negative; the next binary64 height differs by about `1.6543612251060553e-24`, overwhelmingly exceeding the pad. Thus for relevant finite binary64 heights near the domain, H0<0 exactly at h0≤β. `_dn` preserves its negative sign and `drag_envelope` rejects before inspecting b or reaching M2. This applies to zero, subnormal, normal and infinite nonnegative b. Nonfinite h0 rejects at entry. Very negative h0 can fail earlier in the Decimal velocity expression; E1, h≥0 and α<1 imply computed h≥−β, excluding that case for exterior states under the assumptions. These statements concern the default contract, not arbitrary user-supplied envelope/FP overrides.

M2 is independent of b. My 100-digit computation places its ideal root near `55749.3930020856432185897843` m. At binary64 `55749.39300208564`, the implemented M2 is approximately −8.57026e-13; at its successor it is +6.45056e-12. Both signed zeros of need fail strict negativity. On path 2 any required −∞ stage lower bound makes need +∞. Invalid b is rejected by A0 where that envelope is reached. Huge finite heights through MAX return finite arithmetic results in probes; this does not waive the model's no-overflow premise.

The E1 support-plane formula is stationary at the geodetic normal; contraction and second-order latitude error justify the height allowance, rather than a sampled maximum. E2 widens height selection through kilometre conversion. In E3/E4 the logarithmic derivative of density times co-rotation speed squared is negative on each band under the stated inequality, so the widened lower endpoint and all later band bases suffice, including the unbounded top band. Absolute underflow terms require the derived zero-density cutoff and cannot be discarded.

For C1, P≥tiny whenever finite b is constructed from positive mass, and the mixed absolute/relative bounds enclose both product and quotient rounding. At b=0 only mass≥tiny is needed. For C2, clamping the intermediate Q and mass lower bounds at tiny is valid for positive binary64 results. Taking the maximum of φ/b and both construction bounds covers their union. Downward Decimal rounding of φ/R preserves the needed ratio inequality. E4b's two area cases force the numerator to zero at cd·area≤η₀ only after establishing the A-FP-2-dependent c₀ cap.

For stages, the height distance is 1-Lipschitz, E6 bounds rounded position/velocity displacements, and E1 converts true lower bounds to computed-stage lower bounds. Positive M2 permits A2; certification requires every M_k>0. For missed crossings, subtracting the endpoint chord and using an upper second-derivative bound gives dip≤M·dt²/8. The separate two-body radial maximization is analytic; numerical J2/drag sweeps do not establish its perturbed analogue.

Independent attempts (`independent.py`, `independent_final.log`, `probe.py`, `math_audit.py`):

- 1,792 C1 and 1,601 C2 exact-rational constructions, including tiny/huge cd and area and C2 exact products beyond MAX: no ratio-bound violation.
- 598 exterior near-surface states classified using exact model E2, at new latitudes and binary64 displacements: E1 holds; across five b values, 1,095 intentional rejections and 1,895 finite non-certifications, no certification.
- 226 finite force evaluations at band edges, subnormal/top-band densities and speeds from zero/subnormal through 1e100: no enclosure violation. 74 non-finite evaluations were excluded, not treated as confirming evidence.
- 30 deliberately inward/retrograde, nearly polar/equatorial, near-escape RK4 steps just above the three floors: every actual computed stage exceeds its bound and zero.
- 21 E4b product-boundary coefficient evaluations: zero numerator; exact cap boundary and its successor checked separately.
- NaN, negative b, ±0, subnormal b, huge b, infinity, nonfinite h0, β neighbors, the M2 edge, overflowed enclosures, and finite heights through MAX were probed. No default-path false certification was found under the premises.
- The supplied seed-20261022 probe independently reproduces all reported counts: 37,541 states; 36,769 exterior by its stated F-based classification; 7,687 exterior computed heights≤β; 15,374 rejections; 58,164 returned needs; zero certifications; 400 first-stage-infinity cases, with 371 omissions that would certify. Its classification convention is distinguished from the exact E2 grid above (R9-F2).

The floors reproduce exactly as `124456.68544510857`, `118633.50894662621`, `111511.96182508787` m, with margins `7.170720652771883e-7`, `1.0038993351683625e-6`, `8.427938228380506e-7` m. Floors, root brackets, constants, vehicles, thresholds and result bytes are unchanged.

## New findings

**M3T0-R9-F1 — NOTE — finite M3 can be omitted without failing the committed checks. VERIFIED.**

References: `docs/science/experiments/m3-t0/check_review08.py:224`, `:241`, `:248`; `t0_termination.py:1385`.

My scratch mutant retains the existing minimum for infinite M3 but uses `-min(M2,M4)` when M3 is finite. All 288 checks pass. At h0=200000, B=B_V1, inject envelope 1e8 on its first call and zero thereafter. Current code gives M2=`144867.2696173568`, M3=`−2499855380.144757`, M4=`89239.71048326683`, hence need=`+2499855380.144757`. The mutant returns `−89239.71048326683`. Reproduce with `new_mutants.py`; complete output is in `new_mutants.log`.

The infinity regression correctly closes the identified original gap. Its finite control always has M4<M3, so it does not pin a finite M3-dominant minimum. Recommended strengthening: add the above finite, first-call-only large envelope and assert positive need, then include this narrower mutant. This is a propagation/test-contract example, not a claim that the injected force is physical or that the current code falsely certifies a physical step.

**M3T0-R9-F2 — NOTE — the pole test's exact ellipsoid differs slightly from the model/oracle ellipsoid. VERIFIED.**

References: `docs/science/experiments/m3-t0/check_review08.py:59`; `t0_oracle.py:38`, `:42`; `t0_termination.py:1319`; `docs/science/validation.md:833`.

The new check calls A·(1−binary64 F) the exact model polar radius. The height formula and oracle instead use A·sqrt(1−binary64 E2). These differ by `2.4767215814979376e-13` m. At z=B_WGS84, their mathematical heights are respectively `−2.0348868076669469e-10` and `−2.0373635292484448e-10` m; computed height is zero in both interpretations. The latter rounds to −2.04e-10 at three significant figures, rather than the new −2.03e-10 quotation. See `pole_audit.py`, `pole_audit.log`.

Recommended correction: derive the pole expectation from the same exact E2 ellipsoid as E1/oracle, and align the approximate quotation or explicitly identify the F-defined ellipsoid. Interior classification, the zero computed height, the rejection transition, E1 enclosure and every published floor are unaffected. This is a precision/verification NOTE, not an unresolved instance of the original exterior-state exclusion.

## Assumptions, scope and verification limits

- **A-FP-1:** honestly states nearest-even binary64, gradual underflow, mixed absolute/relative errors and the relevant operation behavior. Host underflow checks pass; the mode is not proved across other platforms.
- **A-FP-2:** honestly and explicitly unresolved. The formula is relative LIBM_ULP·2^-52 plus absolute LIBM_ULP·2^-1074, including subnormal outputs; host maxima are measurements. The floor-sensitivity calculation is conditional, not a libm accuracy proof. E4b explicitly inherits this assumption and its cap limit.
- **A-FP-3:** honestly specifies elementwise products and the mixed three-term dot-product allowance, allowing evaluation order/FMA variation within that bound. The proof is conditional on this behavior; one NumPy backend does not prove every backend.
- **C1/C2:** the operative derivation states the two constructions from positive finite mass, cd and area. Zero b under C1 is covered; C2 at zero cannot form a positive vehicle. Arbitrary independently supplied mass/b pairs are outside that guarantee. Superseded “every vehicle” wording is qualified by the later contract.
- **No overflow:** honestly stated, including quotient overflow to infinity. Very large-height arithmetic probes and excluded non-finite forces do not establish an overflow-permitted guarantee. The E4b zero-product infinity is a separate supported case.
- **Negative energy:** honestly required for the escape-speed bound, together with exterior states, no thrust and dt=10 s. A sampled orbit population does not replace this premise.

Unconditionally established here are repository/byte facts, exact computations and observed host results. The force enclosures and sufficient floors remain mathematical implications **conditional on** A-FP-1/2/3 and the stated model, construction, exterior, no-overflow, negative-energy, no-thrust and step-size premises. I find no concealed relaxation of those premises or active claim of a certified combined J2-plus-drag missed-crossing bound. The review verdict does not turn the explicitly unresolved libm assumption into a platform guarantee.

I could not access CI runs **39641717044** or **39652330844**, fetch the remote, verify branch protection, or independently execute the prohibited Proof wrappers. Their success remains recorded implementer evidence, distinct from my validators/compares. CI's `testpaths=["tests"]` excludes the T0 check files. I did not rerun the complete 87-mutant matrix, recover the original 5,287-point search, verify external printed-source provenance, test another platform, establish a universal libm theorem, or explain the GMAT discrepancy. Historical CI/preflight events and wrapper timings remain documentation-only. Current correction counts, numerical results and byte claims were independently checked as detailed above.

Final tracked status and diff-stat are empty (`final_status.txt`, `final_diff_stat.txt`). Exactly **zero tracked files changed** after the reruns; no checkout restoration was necessary. Reviewer setup edits, scripts, mutants and logs remain only in scratch.

T0 is **not accepted or merged**. No T1/T2 work, owner decision, new correction or acceptance dossier was undertaken. Under I-11, the implementer may next prepare the acceptance dossier; explicit Tech Lead acceptance is still required. The two NOTEs permit PASS under the requested rule; every required resolution item is RESOLVED.

VERDICT: PASS (unconditional)
