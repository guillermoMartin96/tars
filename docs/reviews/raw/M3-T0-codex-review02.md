**M3 T0 Review 02 — independent review of `ead2a8417edfbb0855034098c8d85566e3fe7938`**

T0 is **BLOCKED**. The correction fixes the original counterexamples, stage numbering and residual quotation, but two numerical constructions still lack the guarantees attributed to them. I made no corrections to tracked files.

The checkout is detached at the pinned commit; local and remote branch `milestone-3-t0-reference-spike` contain it. The complete correction diff is 21 files, all under `docs/`. The full T0 diff is also confined to `docs/`; production, dependencies, thresholds, contracts, goldens and protected references are unchanged.

**Review 01 dispositions**

| Finding | Disposition | Independent evidence |
|---|---|---|
| M3T0-F1 | PARTIALLY RESOLVED | The chord/curvature theorem is sound; the eccentric and circular counterexamples reproduce. The old 4.165 m estimate is removed and 1.564 m is labelled a measurement. However, perturbed numerical “bounds” still substitute a sampled maximum for a supremum: R2-F1. |
| M3T0-F2 | PARTIALLY RESOLVED | Exact thresholds, the negative-energy speed bound, the −28 km stage counterexample and same-tick semantics are corrected. The added sufficient stage-domain derivation contains an invalid drag-envelope step: R2-F2. |
| M3T0-F3 | RESOLVED | Reexecution gives k2/k3/k4 height offsets +116.312773/−115.734153/+1.161267 m. Records identify k3 as the inward stage. |
| M3T0-F4 | RESOLVED | The GMAT rerun reproduces `6.95223445873689e-6 m`; DR-0029 and VAL-0019 quote `6.95e-6 m`, below the unchanged `1e-4 m` gate. |
| M3T0-F5 | RESOLVED | The decision matrix explicitly distinguishes the technical dependency map from the owner's controlling gate: P10 before T1 and P1–P10 before T2. This conclusion rests on record inspection. |

The entire Review 01 record at `bdcaacf` remains an exact prefix of the current record; dispositions were appended. The raw Review 01 files are unchanged in the correction diff.

**New findings**

**M3T0-R2-F1 — MINOR — sampled curvature maxima are presented as numerical upper bounds. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:166–174`, also `:187–207` for the midpoint construction; DR-0029 P2 at `docs/decisions/requests/DR-0029-m3-t0-proposals.md:109–132`; VAL-0019 at `docs/science/validation.md:783–788`.

`phase_sweep` samples U every 0.25 s, calls its maximum `sup_hddot_upper_mps2`, and multiplies it by dt²/8 to produce `trajectory_bound_m`. There is no enclosure, error allowance or proof that a maximum occurs at a sampled time. The midpoint construction likewise samples U rather than bounding its supremum.

My constrained refinement on the committed 180 km circular, i=51.6°, J2+drag case gives:

- sampled maximum: U(2645.25 s) = `0.06313395420676038 m/s²`;
- refined value: U(2645.3148035461923 s) = `0.06313395427588553 m/s²`.

Thus the recorded sample maximum is not the claimed supremum. `review_scratch/refine.py` and `refine.log` reproduce this inside the actual integration interval. A similar result occurs for the 250 km equatorial case. The differences are tiny and do **not** demonstrate a dip exceeding the reported value; the verified defect is the unsupported upper-bound interpretation. The theoretical inequality itself is correct.

Recommended correction: obtain a conservative continuous-domain bound, including numerical error, or label the perturbed values as sampled estimates and limit guaranteed numerical bounds to domains actually bounded analytically. Preserve the distinction in the JSON and records. Add an adversarial between-sample maximum check.

**M3T0-R2-F2 — MINOR — the sufficient stage-domain proof does not bound the full drag expression. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:405–437`; DR-0029 P1 at `docs/decisions/requests/DR-0029-m3-t0-proposals.md:83–89`; VAL-0019 at `docs/science/validation.md:792`.

For stage height H≥L and speed |v|≤s, the construction uses

`rho_sup(L) [s + omega_E(a + L)]² / (2B)`

as a drag-acceleration bound. Density is bounded at L, but the rotation-speed factor increases with H. Bounding density alone does not bound their product. At upward table jumps, `rho_sup` is constant over an interval immediately below the base, so this expression increases with height over that interval.

A direct counterexample to this intermediate bound uses L=79,999.9 m, H=80,000 m, s=11,000 m/s, B=850/33 kg/m². At the equator, choose v retrograde with magnitude s:

- claimed upper drag expression at L: `48.658376978072056 m/s²`;
- actual drag magnitude at H: `48.65837703993666 m/s²`;
- underestimate: `6.186460410617656e-8 m/s²`.

This state has negative two-body energy (`−1,220,654.393 J/kg`). `review_scratch/stage_check.py` reproduces the calculation. The simpler 25 km jump also exhibits the defect. This disproves the stated envelope lemma, rather than demonstrating failure of the quoted 118.6/124.5 km floors. In 4,000 additional near-escape random states above those floors I observed no below-domain stage; the smallest sampled stage height was 14,555 m. That safety margin does not repair the derivation.

Recommended correction: bound density and rotation speed using separate valid lower/upper stage-position bounds, or maximize the complete density-times-speed-squared expression over the allowed height interval, including band jumps and one-sided limits. Then justify the global height monotonicity/root selection and recompute the claimed sufficient floors. Add targeted tests of this new guarantee.

**M3T0-R2-F3 — NOTE — the new guarantee and sweep coverage are not protected by the 12 checks. VERIFIED.**

References: `docs/science/experiments/m3-t0/check_review01.py:114–119` and `:172–194`; no check exercises `sufficient_stage_condition`.

The tests have useful independent computations for the original dips, threshold, stress input and stage ordering. The wording checks protect against specific superseded sentences, but cannot establish the replacement derivations. The sweep check merely compares values already stored in JSON and does not assert its orbit/physics/phase coverage.

In a scratch copy, I replaced the sweep with the single row `{"max_dip_m":0,"bound_m":0}` and replaced the sufficient-stage results with a zero-height claim. All 12 checks still passed (`review_scratch/mutation.py`, `mutation.log`). Missing bounds and an entirely empty sweep are rejected, so the suite is not wholly vacuous. A second scratch mutation replacing b²/a with a was detected: one numerical curvature check failed and 11 passed (`curvature_mutation.py`, `curvature_mutation.log`). The new scientific claims nevertheless need their own coverage. Recommended: assert the sweep matrix and independently test the full stage envelope, boundary behavior and sufficiency assumptions.

**Scientific assessment and records**

The dip theorem follows by setting g=h−chord: if g''≤M, then g+Mt(dt−t)/2 is concave with zero endpoints, hence nonnegative. Since the chord is at least the lower endpoint, the dip is ≤Mdt²/8. For piecewise-smooth drag, the corresponding almost-everywhere bound must cover the force jumps.

For the exterior ellipsoid, the distance Hessian has principal eigenvalues 1/(R_i+h) and zero normal eigenvalue. The minimum surface radius is the equatorial meridional radius b²/a. This establishes the stated tangent quadratic-form bound at every exterior point. Independently constructed analytic Hessians at 2,000 random exterior states gave minimum U−h'' = `6.92436e-9 m/s²`.

The maximum normal/radius angle is `asin((a²−b²)/(a²+b²)) = 0.003358437616083471 rad`, agreeing with the numerical optimization. The two-body g(r) maximization agreed within `5.33e-15 m/s²` with an independent calculation evaluating endpoints and every real stationary root of its derivative cubic over 1,000 domains, including eccentricities approaching 0.999.

The exterior inequalities b+h≤|r|≤a+h and negative two-body energy justify V_b by the triangle inequality. Random checks had positive speed-bound slack. The longitudinal velocity-Jacobian decay-rate magnitude is rho|v_rel|/B; the transverse magnitude is half that. RK4's real-axis limit applies to the frozen linearized drag subsystem, not to a general accuracy guarantee for the coupled discontinuous equations. The J2 norm factor 3 J2(a/r)² is valid; its maximum occurs on the axis. The RK4 stage-position formulas and the exterior distance Lipschitz argument are correct; R2-F2 concerns the acceleration bound used with them.

All 16 quoted stiffness roots satisfy their defining equations to `4.62e-14` in lambda·dt. None of these roots lies at a band discontinuity. The exact circular-speed kappa=0.01 heights are 90,185.091659 m and 82,337.143817 m; the bound-speed heights are 92,282.071899 m and 84,596.115736 m. The corrected threshold table, stage values, dip table, minimum sweep margin (`0.0247353 m`), maximum perturbed-bound excess (`0.1789477 m`), decay figures and GMAT residual quotation agree with their result files.

The sweep samples 40 phases, samples height at 0.05 s, and refines only 12 leading candidates. It is empirical evidence over that grid, not a proof over arbitrary phase, state or eccentricity. No arbitrary-phase guarantee follows from its deterministic reproduction.

J-ax-1 remains the model convention: J2, ellipsoid and atmosphere rotation use +Z. GMAT-axis substitutions remain explicitly diagnostic; no rotating frame was substituted in the correction. Changing the P1 recommendation to V_b is disclosed and directly addresses F2; no owner option is accepted or defaulted. P1–P10, the P6 scope ruling and the escalated geodetic-drag investigation remain open.

**IM-1:** I independently reproduce the questioned figure from the committed two-orbit report: a quadratic-only least-squares fit of Earth-fixed z against TOE position gives `0.9856650955520649 m RMS`, rounding to 0.99 m (`audit.py`). This supplies reproducible support for the number without relying on the overwritten intermediate run. Explicitly naming the RMS quantity and procedure would improve traceability; I do not raise it as an additional defect.

**Execution ledger and inspected files**

All commands ran locally without network. D=`docs/science/experiments/m3-t0`, S=`review_scratch`, P=`docs/decisions/requests`. Scratch programs preserve the exact independent calculations and child argument vectors. File-creation heredocs wrote only S. Repeated progress reads used `cat`, `tail`, `ls`, and session polling on the logs listed below; they did not modify evidence.

1. `mkdir -p review_scratch`; `git status --porcelain`; `git rev-parse HEAD`; `git diff --stat bdcaacf..ead2a84`; `git diff --name-only 86df2c3..ead2a84`. Initial status empty; HEAD correct; all changed paths under docs. `git branch -a --contains HEAD` confirmed the named branch and detached review checkout. `rg --files -g AGENTS.md -g '*approved*' -g '*digest*'` found the digest anchors and no AGENTS.md.
2. `git diff bdcaacf..ead2a84 > S/correction.diff`; `git diff 86df2c3..ead2a84 > S/full-t0.diff`; concatenated the complete T0 report, T0 matrix, Review 01 record, original prompt and raw output into `S/preflight.txt`, then read them. Read D/README.md, D/check_review01.py, D/t0_termination.py, D/t0_model.py and P/DR-0029-m3-t0-proposals.md with `cat`. Inspected `S/correction.diff`, including the documentation and result changes. `git diff bdcaacf..ead2a84 -- D/t0_decay_results.json` confirmed that only the old estimate fields and sampling description changed; every other decay output is unchanged.
3. Used `sed -n` on D/t0_gmat.py at 65–130, 335–365, 400–500 and 875–905; D/t0_model.py at 1–240 and 230–370; DR-0029 at 1–185, 24–52, 50–145 and 255–269; Review 01 record at 1–220; original review prompt at 1–230 and raw review at 1–240; validation.md at 730–820; M3 decision matrix at 1–100; DR-0028 at 59–114; DR-0024 at 335–390. `rg -n` located decision resolutions, gates, numbered sections, axis-fit code, digests and entrypoints. Read the supplied Hessian, digest and double-reproduction evidence. Read `src/tars/validation/approved_digests.py`. These are inspections, not independent confirmation of historical runs.
4. Read both Proof wrapper scripts with `sed -n '1,140p'` / `'1,170p'` and listed `toolbox/validators`; neither wrapper was executed.
5. Created and ran `.venv/bin/python S/run.py > S/run.log 2>&1`. It inventoried all 85 tracked experiment files by SHA-256, then ran `.venv/bin/python D/t0_X.py D/t0_X_results.json` for X=`atmosphere decay geodetic frames regression termination`, all exit 0. Individual logs are `S/X.log`; exact command vectors and timings are in `S/commands.json`.
6. That runner's first GMAT command mistakenly resolved the console symlink to its app-internal target, making the harness infer the wrong data root; it exited 1 before running experiments (`S/gmat.log`). `ls -l '../GMAT R2026a/bin'`, `find '../GMAT R2026a' -name EarthExponentialAtmosphereData.txt`, and inspection of the harness identified my path error. Retried `.venv/bin/python D/t0_gmat.py --gmat-console "$PWD/../GMAT R2026a/bin/GmatConsole" --out D/t0_gmat_results.json > S/gmat_retry.log 2>&1`: exit 0, all harness cases completed. This was a reviewer invocation error, not a repository finding.
7. The runner executed `.venv/bin/python -m pytest -q -p no:cacheprovider D/check_review01.py`: **12 passed**. It also executed `.venv/bin/python -m pytest -q -p no:cacheprovider`: interrupted with Ctrl-C (exit 130) before completion; no full-suite pass is claimed.
8. Created and ran `.venv/bin/python S/more.py > S/more.log 2>&1`. Its exact validator commands are `.venv/bin/python toolbox/validators/m1_proof.py --out S/m1.json`, `toolbox/validators/m2_proof.py --out S/m2.json`, `toolbox/scripts/gmat_m1.py compare`, and `toolbox/scripts/gmat_m2.py compare`, each using the same Python prefix: all exit 0. Reports/logs: `m1.json`, `m2.json`, `m1.log`, `m2.log`, `m1compare.log`, `m2compare.log`; command vectors in `more_commands.json`. M1 passes and M2 passes 228/228.
9. `more.py` executed `git archive bdcaacf`, extracted it only under S/before, copied in the current check file, and ran `.venv/bin/python -m pytest -q -p no:cacheprovider S/before/D/check_review01.py`: **11 failed, 1 passed**, preserved in `before_checks.log`. The passing check reproduces the stress input. Some failures are absence of the new result/module, not independent tests of a derivation. Hash comparisons in this script also passed.
10. Created and ran `.venv/bin/python S/independent.py > S/independent.log 2>&1`: analytic principal-curvature checks, normal angle, speed and J2 bounds, threshold residuals, density-envelope counterexample, and exact preservation of the original review prefix. Its first peak refinement mistakenly allowed a negative time; I excluded that result and replaced it with the constrained, all-orbit check in the next command.
11. Created and ran `.venv/bin/python S/refine.py > S/refine.log 2>&1`: nine J2+drag trajectories, constrained refinements inside each actual integration interval. R2-F1 uses this corrected computation.
12. Created and ran `.venv/bin/python S/audit.py > S/audit.log 2>&1`: quadratic-only axis fit; five pinned digests; private console/table hashes; script hashes; result-file inventory and sweep margins. Every script/table digest quoted in VAL-0019 matches.
13. Ran an inline Python scan of left/right densities at every table base: confirmed upward jumps, including 80 km. Created and ran `.venv/bin/python S/stage_check.py > S/stage_check.log`: R2-F2 and 4,000 random stage-domain trials.
14. Created and ran `.venv/bin/python S/mutation.py > S/mutation.log`: scratch-only copied records/results, mutated sweep and stage-floor claims, then the explicit 12-check pytest invocation. **12 passed** on the mutant.
15. Created and ran `.venv/bin/python S/curvature_mutation.py > S/curvature_mutation.log`: curvature-radius mutant detected (1 failed, 11 passed). Created and ran `.venv/bin/python S/orbit_max.py > S/orbit_max.log`: 1,000 independent endpoint/stationary-root maximizations; maximum difference `5.33e-15 m/s²`.
16. Inline Python rehashed the 85 inventoried files after the GMAT retry, writing `S/reproduction_now.json`: `{}`. It also ran `git diff --name-only 86df2c3..ead2a84 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml`: empty. Inline Python loaded the M1/M2 validator reports; all results passed. Progress inspection also used `ls -lT S/run.log S/commands.json`, `rg -n` on test timeout/subprocess references, and the UTC clock tool. A process-status attempt, `ps -axo pid,etime,pcpu,command | rg 'pytest|review_scratch/run.py'`, was denied by the sandbox and provided no evidence.
17. Created the complete review under S. After inspecting historical pytest durations with `rg -n` on both supplied Proof logs and checking `testpaths`/`addopts` in pyproject.toml, interrupted the optional full pytest session with Ctrl-C (exit 130). `git status --porcelain > S/status_after_run.txt`; `git diff --stat > S/diff_after_run.txt`: both empty. Final `git status --porcelain > S/final_status.txt` and `git diff --stat > S/final_diff_stat.txt` were also empty. A final 85-file hash comparison (`reproduction_final.json`) was `{}`.

Every T0 result file inspected and rerun: `t0_atmosphere_results.json`, `t0_decay_results.json`, `t0_geodetic_results.json`, `t0_frames_results.json`, `t0_regression_results.json`, `t0_termination_results.json`, `t0_gmat_results.json`. The GMAT harness rewrote/reproduced its 67 tracked script, report, table, coefficient and metadata artifacts; the axis-probe report was additionally used by my independent fit. All 85 tracked experiment files match the initial inventory byte for byte. No tracked output changed, so no restoration was necessary.

Five pinned digest comparisons, independently computed:

- `proof/thresholds/m1.json`: `446e75ee8d5129a346263b5b06f873e0aed74c33fd756564e43423bbd16fdb3d` — MATCH.
- `proof/thresholds/m2.json`: `9d4eab47133a4f9eb1125cf7242ada0c720fbe9e4b8dd12b0f698cc79e5f0ce9` — MATCH.
- GMAT M2 manifest: `f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585` — MATCH.
- M2 snapshot: `a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b` — MATCH.
- M2 golden: `dc3baf7abb209a11ca463b9ca5001ce886c62b92b191ac76249d32924aa951dc` — MATCH.

Private GMAT console: `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`; installed atmosphere table: `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`. Both match the supplied claims.

**Verification limits and recommendation**

I independently ran the standalone validators, comparisons, experiments and checks described above. I did **not** execute the prohibited Proof wrappers. Full pytest was started, then deliberately interrupted: the supplied logs show a normal runtime of about 29 minutes, and this docs-only review already had completed targeted checks and standalone validators. The historical 1185-pass pytest result is not independently confirmed here. The historical 9/9 and 20/20 wrapper results at `03e8f63` are supported only by supplied logs. I made one complete experimental reproduction, rather than independently repeating the implementer's two fresh-clone runs.

CI was inaccessible. The four-job success claims at `03e8f63` ([run 39168509344](https://github.com/guillermoMartin96/tars/actions/runs/39168509344)) and `ead2a84` ([run 39173057402](https://github.com/guillermoMartin96/tars/actions/runs/39173057402)) remain documentation-only. I could not verify remote branch protection, external scientific sources, other platforms, or the cause of the escalated geodetic-drag discrepancy. Random checks and floating-point refinements do not certify global bounds.

T0 remains **BLOCKED** pending correction authorization and resolution of the findings. P1–P10 and the P6 scope ruling remain owner decisions. This review does not authorize acceptance, merging, T1, T2, fixes or Review 03.

VERDICT: REQUEST_CHANGES
