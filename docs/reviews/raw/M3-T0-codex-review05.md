# M3 T0 Review 05

Two new MINOR findings remain. The original 190,681 km counterexample is covered, but the claimed unrestricted enclosure still omits underflow in the conversion to ballistic coefficient. An empirical maximum is also mis-scoped. No fix was made.

## Checkpoint and scope

Reviewed detached HEAD `88f9752ad03283e56f1c20d79bd28574f493e8a8`, contained in local `origin/milestone-3-t0-reference-spike`. Both requested diffs were generated: `review_scratch/correction.diff` and `full.diff`. The correction changes 22 files, all under `docs/`; the complete T0 diff also changes only `docs/`. Production, dependencies, physics constants, atmosphere data, frames, thresholds, goldens, references and M1/M2 validation semantics are unchanged. Earlier raw reviews/prompts are unchanged relative to `c15fbd4`.

These are my git/file checks. Remote synchronization and CI were inaccessible. DR-0029 P1–P10 and DR-0028 P6(b) remain open; the GMAT geodetic-drag discrepancy remains escalated. No acceptance, merge, T1/T2 work or further review round is authorized by this review.

## Ledger and reproduced evidence

The detailed command ledger is `review_scratch/command-ledger.md`. It records shell inspections, script creation, subprocess commands, unsuccessful reviewer attempts and progress checks. Exact experiment subprocess arguments, exits and timings are in `execution.json`; red-before and mutation arguments/results are in `adversarial_runs.json`. Reviewer programs and logs remain under `review_scratch/`.

| Execution | Independently obtained result |
|---|---|
| `.venv/bin/python -m pytest -q -p no:cacheprovider` on `check_review01.py` through `check_review04.py` | **140 passed**, 202.02 s |
| `review_scratch/run_evidence.py`, followed by the corrected GMAT invocation recorded in the ledger | All nine experiment JSON outputs reproduce committed bytes; generated GMAT artifacts also match |
| `toolbox/validators/m1_proof.py --out review_scratch/m1.json` | PASS |
| `toolbox/validators/m2_proof.py --out review_scratch/m2.json` | PASS, 228 checks, without `--quick` |
| `toolbox/scripts/gmat_m1.py compare`; `gmat_m2.py compare` | Successful comparisons |
| `review_scratch/adversarial_runs.py` | Red-before: **17 failed, 31 passed** with the documented two-part shim; corrected control: 48 passed; all ten R4 mutants fail declared checks |
| `review_scratch/independent.py` | 3,200 additional constructions on both illustrative vehicles; no corrected-envelope violation; 17 superseded-envelope violations |
| `review_scratch/test_r5.py` | **1 failed**, independently reproducing R5-F1 below |
| Optional full project pytest run | Intentionally interrupted after **285 passed in 277.88 s**; not a full-suite PASS |

The first GMAT invocation mistakenly resolved the executable symlink, causing installation-root discovery to fail before GMAT ran. The retry used the absolute `bin/GmatConsole` path without resolving that symlink and succeeded. An initial digest parser included non-claim lines; the corrected comparison checks the 17 actual VAL-0019 script/table digest assertions, all matching. These are reviewer-tooling issues, not product findings.

Result files inspected: all nine committed and regenerated `t0_{atmosphere,axis_ablation,decay,frames,geodetic,gmat,regression,termination,height_error}_results.json`; supplied `mutation_check_review04.json`; own `independent.json`, `adversarial_runs.json`, `execution.json`, `m1.json`, `m2.json`, hash inventories and digest comparisons. `inspected_files.json` inventories the decision/assumption registers, reviews/prompts, report, matrix, README and supplied correction logs; their complete text is retained in `inspections.log`. Historical Proof and CI claims remain documentation evidence.

My seven digest calculations match the supplied values:

- M1 thresholds: `446e75ee8d5129a346263b5b06f873e0aed74c33fd756564e43423bbd16fdb3d`.
- M2 thresholds: `9d4eab47133a4f9eb1125cf7242ada0c720fbe9e4b8dd12b0f698cc79e5f0ce9`.
- GMAT M2 manifest: `f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585`.
- M2 snapshot: `a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b`.
- M2 final states: `dc3baf7abb209a11ca463b9ca5001ce886c62b92b191ac76249d32924aa951dc`.
- GMAT console: `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`.
- Installed atmosphere table: `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`.

## Resolution table

| Item | Disposition | Evidence |
|---|---|---|
| M3T0-R4-F1 | PARTIALLY RESOLVED | Original point and both fixed vehicles pass underflow checks; unrestricted parameter conversion still fails through R5-F1. |
| M3T0-R3-F1 | PARTIALLY RESOLVED | Height widening, independent oracle and all downward-jump checks pass; the replacement global force-enclosure contract remains incomplete. |
| M3T0-R2-F1 | RESOLVED | Rerun and checks preserve sampled-estimate labels and separate the certified two-body result. |
| M3T0-R2-F2 | PARTIALLY RESOLVED | Radius-product correction, candidate maximization and original counterexample pass; unrestricted global enclosure remains affected by R5-F1. |
| M3T0-R2-F3 | RESOLVED | Recomputing checks pass; mutation classification requires declared failures. New parameter coverage gap is identified separately. |
| IM-1 | RESOLVED | Byte-identical axis-ablation rerun reproduces 0.9856650955520649 m RMS; procedure remains documented. |
| IM-2 | RESOLVED | Governing bracket ends are explicit; tests confirm 111511.96 m fails the condition and 111511.97 m satisfies it. |
| M3T0-F1 | RESOLVED | Chord/curvature reasoning remains sound; sweep and two-body recomputation checks pass. |
| M3T0-F2 | PARTIALLY RESOLVED | Thresholds, speed bound and counterexamples reproduce; unrestricted sufficient-condition evidence still depends on the incomplete global contract. |
| M3T0-F3 | RESOLVED | Reproduced stage offsets identify the k3 input as the inward stage. |
| M3T0-F4 | RESOLVED | GMAT rerun reproduces the corrected approximately 6.95e-6 m residual and unchanged gates. |
| M3T0-F5 | RESOLVED | Record inspection preserves owner gates: P10 before T1 and P1–P10 before T2. |

The partial dispositions concern the unrestricted statement, not an observed failure at the two illustrative vehicles’ floors.

## Mathematical and numerical assessment

The A-FP-1 mixed model is valid for finite binary64 operations under round-to-nearest-even and gradual underflow. One can choose a relative error for normal results and an absolute error for underflowing products/quotients, with δη=0. Underflowing sums/differences of binary64 operands are exact; nonzero square roots cannot be subnormal; multiplication by 0.5 is exact except when it underflows; ties at half the smallest subnormal round to zero.

For E1, the support-function formula, stationary latitude and contraction argument correctly turn latitude error into an absolute height allowance across cancellation. The explicit underflow contributions enter both the iteration and final formula. E2 adds the kilometre-division allowance to selection uncertainty. The candidate set retains the lower selection endpoint and subsequent band bases, including downward discontinuities. My additional heights use a separate 90-digit ellipsoid foot-point **bisection**, rather than the committed Newton oracle. No fixed-vehicle counterexample was found.

For E3, the exponential’s absolute error survives multiplication by the table coefficient, giving the stated Nρ; rounding the final product supplies its half-subnormal term. My independent decimal top-band inversion gives the exact density half-subnormal onset

`191735430.719878400062362441221301… m`.

The stored outward bound is `191735430.7198785 m`, higher by `9.46771700295e-8 m`. The cutoff is a derived zero-force property, not an altitude restriction. Selection uncertainty correctly converts it into the radius used by S_max.

For E4, the final coefficient division’s absolute error is now included in W. The dot-product allowance, square root, shared scalar product error, final component-product errors and τ lead to the stated relative/absolute decomposition **provided the mass-to-B inequality at lines 570–571 holds**. Maximizing the absolute part at S_max is conservative. R5-F1 concerns the unjustified assertion that rounded parameter construction always supplies that prerequisite.

For E5–E6, the added component underflow allowances and stage displacement/velocity allowances are consistent with the recorded operation order. I found no additional defect in these terms. The new constant-only mutants test agreement with the derivation; they are not behavioural demonstrations of errors of order 1e-323.

For the original reviewer point, my Decimal norm gives drag `1.02021454616158e-315`, superseded envelope `5.0632192e-316`, corrected envelope `1.110700085e-315 m/s²`. Both illustrative vehicles pass the transition, zero, band-boundary, high-altitude stage and independent-envelope checks.

The recomputed floor brackets are:

| Vehicle | Corrected root bracket, m | Published end, m | Positive margin, m |
|---|---|---|---|
| B25.8 | [124456.68544484391, 124456.68544484489] | 124456.68544510857 | 7.17072e-7 |
| B100 | [118633.5089461096, 118633.50894611058] | 118633.50894662621 | 1.00390e-6 |
| Drag-free | [111511.96182425194, 111511.96182425291] | 111511.96182508787 | 8.42794e-7 |

Before/after brackets coincide. The committed second implementation also passes. These results support the unchanged floors for the stated illustrative parameters; they do not repair the unrestricted parameter-conversion claim.

Height monotonicity follows from the shrinking selection domain, decreasing speed bound and positive coefficient `1/(1+α)−u/(1−α)`. The absolute envelope is independent of the lower height. Sensitivity thresholds reproduce: log2 LIBM_ULP limits 5/6/7 for published ends and 19/17/20 for upward centimetre quotations. The relevant constants increase with LIBM_ULP through positive factors or positive denominators that decrease over the evaluated range. The nearest-centimetre drag-free quotation fails even at the smallest tested library allowance.

A-FP-2 remains necessary and unproved. The records generally distinguish conditional derivations from host measurements correctly. Neither finite samples nor the glibc statement of intent establishes a universal bound. I could not verify the external quotation offline. A-FP-1’s operating mode and A-FP-3 are probed on this host only. No unconditional cross-platform numerical guarantee follows from this evidence; I do not convert the disclosed assumption into one.

All ten independently rerun R4 mutants fail declared checks; their Review 04 failure-name sets exactly match the supplied matrix restricted to that module. Counts are 8/8/8/1/3/3/1/1/1/1 in the supplied R4 mutant order. The density, tiny gravity/height/stage and static-envelope cases have the disclosed derivation/static classifications. The other 25 supplied mutants, including the equivalent stationary-point case, were inspected but not rerun. The test suite does not exercise the rounded-B counterexample below.

## New findings

**M3T0-R5-F1 — MINOR — rounded ballistic-coefficient construction is not underflow-safe. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:570–571` (claimed prerequisite), `:639` (relative-only φ_B), `:804–806` (public envelope contract); DR-0029 `:102` and `:453` (unchanged unrestricted domain).

The conditional E4 derivation requires `mass/(cd·area) ≥ b/φ_B`. The assertion that `b = fl(mass/fl(cd·area))` supplies this relation fails when that quotient is subnormal. The public envelope contract omits this extra vehicle prerequisite.

Reproduce with `.venv/bin/python review_scratch/vehicle_counterexample.py` for the first construction, or the default-parameter failing regression:

`.venv/bin/python -m pytest -q -p no:cacheprovider review_scratch/test_r5.py`

The latter uses:

```text
r = [186378137.0, 0, 0] m; v = [0, 0, 0] m/s
true height = computed height = 180000000 m
Cd = 2.2; area = 15 m²; mass = 17 × 2^-1074 kg
b = mass / (Cd × area) = 2^-1074 in binary64
```

The exact ratio `mass/(Cd·area)` is approximately `2.54518666039430e-324`, whereas `b/φ_B` is approximately `4.94065645841246e-324`: the required inequality is false.

Computed drag is `9.328000516634905e26 m/s²`; `drag_envelope(180000000, 0, b)` returns `4.805333599484291e26 m/s²`, underestimating it by **1.94117647058593×**. Position is exterior, energy is negative, parameters are positive and all force intermediates are finite. The approved J2+drag acceleration confirms the same drag component. `counterexample_trace.log` shows that the exp and pow errors here are within A-FP-2; this is not a library-assumption failure.

The second claimed construction also fails: with `b = 2^-1074` and `mass = fl(fl(b·2.2)·15) = 30 × 2^-1074`, both rounded constructors reproduce the same mass/B pair, yet drag/envelope is `1.09999999999869` (`both_constructions.log`).

This is an extreme positive mass, not either illustrative vehicle. It disproves the unrestricted construction/contract; it does not demonstrate an unsafe published floor.

Recommended correction: propagate absolute error through the conversion to B, or evaluate the needed ratio directly from exact binary64 mass/Cd/area values. Alternatively disclose and enforce a rigorously justified vehicle prerequisite, subject to the owner’s scope decision. Add this counterexample; do not silently narrow the supported domain or change floors.

**M3T0-R5-F2 — MINOR — the 0.983 empirical maximum is incorrectly scoped. VERIFIED.**

References: `docs/reviews/M3-T0-review-04.md:141`; `docs/decisions/requests/DR-0029-m3-t0-proposals.md:102`; transition construction in `check_review04.py:210` onward.

The correction record calls 0.983 the largest observed model-drag/envelope ratio “in the subnormal regime”; DR-0029 calls the coefficient-rounding point the tightest observed case. The committed transition scan itself contradicts that scope.

Replaying its seed and first point gives:

- B25.8, point 0: density `2.135449735119324e-308`, ratio `0.999999999998695…`.
- B100, point 0: density `1.3067422079269955e-308`, ratio `0.999999999998814…`.

Both densities are subnormal. Inputs and calculation are retained in `review_scratch/committed_scan_ratio.log`; a simple equatorial check at 182000000 m independently gives the same near-unity behaviour (`subnormal_ratio.log`). These are covered points, not envelope violations.

Recommended correction: scope 0.983 explicitly to the coefficient-flip subset, if that is the measured quantity, and report the transition scan separately. Remove the claim that it is the tightest case over the whole subnormal regime. No floor change is implied.

## Verification limits and checkpoint

I did not run the prohibited Proof wrappers. Supplied clean-clone M1/M2 wrapper and complete 1185-test results remain historical documentation claims; my standalone validators and partial project-suite run are separate evidence. I performed one complete experimental reproduction, not two fresh-clone runs. I reran ten R4 mutants and their control, not the complete 35-mutant matrix.

CI was inaccessible: neither checkpoint’s four-job success was independently verified. Other platforms, remote synchronization/protection, external-source provenance and a universal libm error theorem were not checked. The cause of the escalated GMAT discrepancy remains unresolved. Reproduced JSON bytes verify numerical experiment results; they do not independently prove every historical planning number quoted in the append-only records.

Final `git status --porcelain` and `git diff --stat` are empty. Exactly **zero tracked files changed**, including regenerated GMAT artifacts. No checkout restoration was necessary. Reviewer artifacts are confined to `review_scratch/`.

T0 is not eligible for unconditional acceptance at this checkpoint. The next step requires explicit owner authorization for a bounded correction/validation pass addressing these findings and, separately, any subsequent independent review. No correction or additional review was started.

VERDICT: REQUEST_CHANGES
