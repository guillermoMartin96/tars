# M3 T0 Review 06 (independent review of the Review 05 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a159f1-85b3-7c52-8824-949b27763276`, 2026-10-20 15:32–15:44 UTC. The reviewer ran its commands concurrently; each mutant was run against its declared checks only.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review06-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled; it was not passed by this invocation and does not change the sandbox.

**Reviewed commit:** **`fcd5997cd120c8834651d3c0da2e52899f2d9ffc`** (the validation record of the correction commit `411cabd0e7a2be57ee59baa040d0ea5607d8f00a`).
- The review ran in a fresh clone with its own `uv sync --locked` environment and a private GMAT R2026a copy, whose console digest matches the installation.
- The prompt was kept outside the repository during the review. It reproduces Authorization I-7 and Authorization I-6 verbatim, and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It presents the correction's records as claims to verify. Every commit identifier for the pass under review is a full SHA.
- **Preconditions (I-7 §1), checked by the implementer before the review:** branch `milestone-3-t0-reference-spike`, HEAD and origin `fcd5997`, clean tree; CI succeeded on `411cabd` (run 39361891229) and `fcd5997` (run 39370422938), all four jobs each; no protected path changed since `86df2c3`; the five pinned digests match. The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-7 — M3 T0 Independent Review 06" (Tech Lead, 2026-10-20), §2–§5.

**Files:**
- prompt: `raw/M3-T0-codex-review06-prompt.md`;
- raw output: `raw/M3-T0-codex-review06.md`, the reviewer's saved report `review_scratch/M3-T0-codex-review06.md`, which equals the CLI's final message plus a trailing newline. It contains no absolute path;
- reviewer scripts and logs: `raw/M3-T0-codex-review06-evidence/` (`*.py.txt`; `command-ledger.md`; `execution.json`; `mutation-subset.json`; `SHA256SUMS`). Absolute paths are redacted to `<snap>`/`<scratch>`/`<gmat>`/`<home>`/`<tmp>`;
- the implementer's reproduction: `raw/M3-T0-codex-review06-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of the two diffs (`git diff 17b2229..fcd5997`, `git diff 86df2c3..fcd5997`);
- its red-before tree (`17b2229` docs with the current `check_review05.py`; `red-before.log` is kept) and its twenty mutant trees (561 MB in all);
- `inspections.log` (1.2 MB) and its text copies of DR-0029 and the earlier reviews, all copies of committed files at the reviewed commit (the inventory `inspected_files.json` is kept);
- `__pycache__`.

**Verdict:** **REQUEST_CHANGES**, with one new MINOR finding and two NOTEs.

**Stop rule applied (authorization §5):**
- Every finding is recorded with its severity, and all three were independently reproduced by the implementer.
- The complete output is preserved.
- **The findings are not corrected, Review 07 is not started, and T0 is not accepted.** Authorization is requested.
- Not merged; T1 and T2 not started; DR-0029 P1–P10 and DR-0028 P6(b) not decided; the GMAT geodetic-drag discrepancy stays escalated; branch protection and the M1/M2 baselines unchanged.

## Resolution assessed by Review 06
| Item | Review 06 | Basis (reviewer) |
|---|---|---|
| M3T0-R5-F1 | **PARTIALLY RESOLVED** | Both Review 05 counterexamples are covered and the positive-b conversion inequalities hold in further exact-rational checks. C1 can also give b = 0 from positive vehicle parameters, which leaves the unrestricted contract undefined (R6-F1) |
| M3T0-R5-F2 | **RESOLVED** | Both empirical populations recompute to the corrected numbers; P1 shows the transition maximum; Review 04's sentence is kept and followed by an amendment |
| M3T0-R4-F1 | **PARTIALLY RESOLVED** | The coefficient, division, density and other absolute underflow terms survive recomputation and all ten R4 mutant checks, and the force decomposition composes correctly with positive-b E4a. Its unrestricted vehicle coverage still omits C1's zero quotient |
| M3T0-R3-F1 | **PARTIALLY RESOLVED** | The selection-height widening, the support-function height argument and all downward-jump checks cover the original defect. They do not repair the undefined conversion boundary in the replacement global envelope |
| M3T0-R2-F1 | **RESOLVED** | The rerun keeps the certified two-body result separate from the sampled perturbed estimate |
| M3T0-R2-F2 | **PARTIALLY RESOLVED** | The co-rotation factor is maximised with the density over the candidate heights, and the original counterexample passes. The unrestricted envelope is undefined for zero-b C1 vehicles |
| M3T0-R2-F3 | **RESOLVED** | The recomputing checks pass, and the mutation machinery requires declared failures |
| IM-1 | **RESOLVED** | A byte-identical axis-ablation rerun reproduces 0.9856650955520649 m RMS with a documented procedure |
| IM-2 | **RESOLVED** | The governing bracket ends stay explicit; 111 511.96 m fails the condition and 111 511.97 m satisfies it; the owner-directed disposition is kept and no floor changed |
| M3T0-F1 | **RESOLVED** | The chord/curvature argument and the recomputing checks remain sound |
| M3T0-F2 | **PARTIALLY RESOLVED** | The thresholds, speed bound and counterexamples reproduce. The general sufficient-condition evidence still relies on the incomplete unrestricted conversion contract |
| M3T0-F3 | **RESOLVED** | Recomputed stage offsets identify the k3 input as the inward stage |
| M3T0-F4 | **RESOLVED** | The GMAT rerun reproduces the corrected residual of about 6.95e-6 m |
| M3T0-F5 | **RESOLVED** | The records keep the owner's gates: P10 before T1, and P1–P10 before T2 |

The reviewer states that the partial dispositions concern the unrestricted contract, not an observed failure at either illustrative vehicle's published floor. R4-F1, R3-F1, R2-F2 and F2 were each assessed on their own basis, as I-7 §2 requires; for all four the remaining ground is the same uncovered b = 0 boundary.

**The reviewer also reports:**
- **E4a, C1 (positive b):** P > 0 gives P ≥ 2η₀ and cd·area > η₀; the stated R1 follows, including subnormal cd·area and mixed intermediates. The missing case is exactly b = 0: a positive mass does not imply a positive rounded quotient.
- **E4a, C2:** a positive finite mass needs a positive Q, so Q and the mass are each ≥ 2η₀; Q_lo and M_lo are safe lower bounds. Overflow is excluded separately, not repaired by the lemma.
- **Monotonicity:** R1 decreases with b and R2 is non-increasing, so R is non-increasing; adjacent-b rational comparisons support it. For the V1 shape the switch point with the **stored, outward-rounded** φ_B is 7.416912861690675e-309 (as quoted). With the exact rational φ_B it would be 1.1125369292536007e-308; the two should not be conflated. The committed switch check uses the stored constant.
- **b_R:** rounded down (ROUND_FLOOR); the same binary64 b is returned when R = φ_B/b; both checked over 6 657 further constructions. Both envelope parts receive b_R, including N_ρ/(2b_R) and every reciprocal-vehicle term of W; S_max, h_zero and τ have no vehicle dependence.
- **E4b:** the arithmetic argument is sound given its density cap, including the exact half-subnormal product boundary (366 states, zero force). The cap c₀ ≈ 0.6125000000000004 < 5/8 inherits A-FP-2 (R6-F3).
- **Floors and invariants:** the termination output differs from `17b2229` only by the two advertised keys; the root brackets coincide; margins 7.170720652771883e-7, 1.0038993351683625e-6 and 8.427938228380506e-7 m; libm-sensitivity limits 2^5/2^6/2^7 and 2^19/2^17/2^20 reproduce. No vehicle, constant, table, root, margin, baseline, golden, threshold, contract, dependency or production file changed.
- **R5-F2 and provenance:** coefficient-subset maxima 0.9527274167782528 (B 25.8) and 0.982821819954253 (B 100); transition-scan subnormal-density maxima 0.9999999999988586 and 0.9999999999988518. The new procedure makes the subset measurement reproducible; it does not reconstruct the historical ad-hoc run. **The 5 287-point random search (and its 161 superseded-envelope violations) quoted in the Review 04 record remains an unverified provenance claim; the records do not explicitly mark it as an open gap, and it must not be counted as reproduced evidence.**
- **A-FP-1:** appropriate under round-to-nearest-even with gradual underflow; the operating mode is a condition, not a universal fact. **A-FP-2:** a legitimate explicit condition whose acceptability is an owner decision; its unresolved status is not the reviewer's reason for REQUEST_CHANGES; host measurements, the weakened allowances and CI are different kinds of evidence and none is a library guarantee. **A-FP-3:** disclosed; conditional on the evaluation order.
- **C1/C2 scope:** stated in E4a, the envelope and P1; it does not cover arbitrary independently supplied (mass, b) pairs. Restricting the lemma silently to positive computed b would be the vehicle condition option (b) excludes. **Overflow exclusion:** explicit and honest, including C1 quotient overflow; the zero-b case has no overflow and is not excluded by it.
- **Scope of guarantees:** unconditional are the snapshot and file facts, the observed host runs and exact-rational implications from their stated premises. The stage-floor guarantees remain conditional on A-FP-1…A-FP-3, the exterior finite domain, no thrust, negative two-body energy, dt = 10 s and the specified vehicle construction and shape. No unrestricted all-positive-vehicle envelope guarantee is established.
- **Its own runs:** checks 01–05 157/157 (174 s); the current `check_review05.py` on the archived `17b2229` docs, no shim: 17 failed; all nine T0 experiments, including GMAT, reproduce the committed bytes; ten R4 and ten R5 mutants against their declared checks: 20/20 detected; the supplied 45-mutant report audited (44 detected, 1 declared equivalent, passing control); the M1 validator PASS and the M2 validator PASS with 228 results (not `--quick`); the GMAT M1/M2 compares pass; the five pinned digests, the two GMAT digests and the 18 VAL-0019 digest assertions match; a partial project pytest run, interrupted at 293 passed (not a full-suite PASS). The tracked tree is clean before and after.
- **Not verified by the reviewer:** the Proof wrappers (prohibited), the complete 1185-test run, the full 45-mutant matrix, the original 5 287-point search, the implementer's 219 983-vehicle sweep, two fresh-clone reproductions, other platforms, CI (no network), external-source provenance, remote synchronisation or protection, and the cause of the escalated geodetic-drag discrepancy.

## New findings
| ID | Severity | Finding (reviewer) | Implementer's independent reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R6-F1 | MINOR | **C1 underflow to b = 0 is outside the purportedly unrestricted conversion** (`t0_termination.py:585–595`, the unsupported b ≥ 2η₀ inference at `:589`; the division at `:849`; the envelope conversion at `:911`; unrestricted claims at DR-0029 `:101` and `:466`, `validation.md:816`, `M3-T0-report.md:37` and the decision matrix's status paragraph; the implementer's sweep filters the case at `exhaustive_e4a.py.txt:18`). With cd 2.2, area 15 m² (P = 33), mass 2^-1074 kg, r = (186378137, 0, 0) m, v = 0: C1 gives **b = 0**. True and computed heights are exactly 180 000 000 m and the energy is negative. Density 2.5706399040162615e-305, finite nonzero drag ≈ 1.58576009e28 m/s²; the envelope raises `ZeroDivisionError: Fraction(1, 0)`. The reviewer's regression (mass 16 × 2^-1074, just below the Review 05 case) fails identically after checking finite force and the host's exp/pow errors against A-FP-2. Not an overflow and not a zero-mass vehicle; no unsafe published floor is shown | **VERIFIED** twice. (1) Own script (`implementer-reproduction/r6f1_repro.py.txt`, `.log`) on the committed `t0_model.acceleration`, `t0_oracle` and `drag_envelope`: for every mass k × 2^-1074 kg with k = 1 … 16, C1 gives b = 0, the model's drag is finite and nonzero (1.585760e28 down to 9.911001e26 m/s², equal to the 60-digit oracle drag), and `drag_envelope` raises `ZeroDivisionError`. k = 17 (the Review 05 case, b = 2^-1074) is covered, ratio 0.970588235292966. (2) The reviewer's `test_zero_b.py` run on this worktree: 1 failed, same error (`reviewer_test_zero_b_on_fcd5997.log`).<br>**Root cause:** the E4a C1 derivation took "b finite and mass > 0" as implying b ≥ 2η₀. A finite C1 quotient also rounds to 0 when mass/P ≤ η₀. The implementation's `1/(b − η₀)` and the envelope then divide by a non-positive quantity. The implementer's grid and exhaustive sweep both excluded b = 0, so no check exercised it. The B 25.8 and B 100 vehicles (b normal) and the drag-free limit are unaffected | **ACCEPTED**; not applied |
| M3T0-R6-F2 | NOTE | **`_up`/`_dn` infinity handling is narrower than the helper's advertised contract** (`t0_termination.py:489–499`; the Review 05 record's "Outward rounding" paragraph). `_up(Fraction(2**1024))` still raises `OverflowError`; `_up(-Decimal(2)**1024)` returns −∞, which is not an upper bound; `_dn(Decimal('-Infinity'))` raises; `stage_lower_heights(1e7, 2^-1074)` propagates an infinite A0 to a failing `_dn`. The live upper-bound callers use non-negative quantities, and the published searches and result files stay finite | **VERIFIED** (`implementer-reproduction/r6f2_repro.py.txt`, `.log`): `_up(Decimal(2)**1024)` = inf; `_up(Fraction(2**1024))` OverflowError; `_up(-Decimal(2)**1024)` = −inf; `_dn(Decimal('-Infinity'))` and `_dn(-Decimal(2)**1024)` OverflowError; `stage_lower_heights(1e7, 2^-1074)` OverflowError. No published floor or committed result is affected | **ACCEPTED**; not applied |
| M3T0-R6-F3 | NOTE | **E4b's evidence classification omits its inherited density assumption** (`M3-T0-review-05.md:159` "E4a and E4b use no libm call", and `:167` "Derived under A-FP-1"; `t0_termination.py:598–599` and the `c0_max` computation in `rounding_allowances`). c₀ ≤ 5/8 uses the density/libm allowance; replacing exp by 4 (IEEE arithmetic kept, A-FP-2 violated) makes the force nonzero at cd = 2^-1074, area = 1/2. A dependency demonstration, not a counterexample under the declared assumptions | **VERIFIED** (`implementer-reproduction/r6f3_repro.py.txt`, `.log`): `zero_force_c0_max` is built from F_ρ, which carries the libm allowance; it rises with LIBM_ULP (0.6125000000000004 at 2, 0.6126495361328126 at 2^40), and the 5/8 check fails at LIBM_ULP = 2^48. E4b therefore holds under A-FP-1 **and** A-FP-2 (with very large slack), not under A-FP-1 alone | **ACCEPTED**; not applied |

**Implementer's observations (not dispositions and not reviewed):**
- R6-F1 is the same class as R5-F1, one step further down. Underflow to exactly zero is a distinct rounding outcome from underflow to a subnormal, and the lemma's premises (b finite, mass > 0) were stated without checking that they imply its denominators' positivity. The published floors use B 25.8, B 100 and the drag-free limit, whose conversions are normal; they do not depend on the defect.
- The reviewer's remark on the provenance of the 5 287-point search is correct: the I-6 report to the Tech Lead named it as an open point, but no record marks it. It is not a numbered finding.
- The reviewer's remark on the switch point is correct: the records quote b* with the stored, outward-rounded φ_B (`FP["phi_B"]`), which the code uses; the exact rational φ_B gives 1.11e-308.

## Proposed correction (for authorization; none applied)
1. **R6-F1, keeping option (b) and the unrestricted domain:**
   - in C1, bound P/mass also through the positive-mass fact mass ≥ 2η₀ (P/mass ≤ P/(2η₀)), which holds for every b including b = 0; take R1 as the smaller of that and the quotient bound, which needs b − η₀ > 0 only where it is used. b = 0 then gives the finite R = cd·area/(2η₀) and a finite envelope. Alternatively return +∞ (no certification) for b = 0, which is conservative but not informative. Choosing between them is within option (b); the second makes such vehicles uncertifiable;
   - correct the C1 premise in the E4a docstring and records ("b finite and mass > 0" does not give b ≥ 2η₀);
   - add regressions for k = 1 … 16 (b = 0) and the transition at k = 16/17, include b = 0 in the grid, remove the b > 0 filter from the exhaustive sweep, and add a mutant that drops the new case.
2. **R6-F2:** make `_up` and `_dn` sign-aware and overflow-safe for Fraction and Decimal inputs (or narrow their docstrings to the cases used), and make an unbounded stage enclosure return an explicit non-certification result instead of an incidental exception.
3. **R6-F3:** classify E4b as derived under A-FP-1 with the density cap of E3 (hence A-FP-2, with the slack stated), and correct "E4a and E4b use no libm call" to say that E4b's cap inherits the density allowance.
4. **Records:** mark the 5 287-point random search as unreproduced historical evidence by an append-only note; state which φ_B the b* figure uses.
5. **Update** DR-0029 P1/P4, VAL-0019, the T0 report and the decision matrix; rerun the checks, mutation, M1/M2 Proof, the digests, reproducibility and CI. Any Review 07 needs authorization.

## Lessons (proposed, not yet codified)
- When a lemma's premise says "finite and positive", check every rounding outcome of the premise's inputs, including exactly zero, not only subnormal results.
- A sweep that filters out inputs (here `0 < b < inf`) cannot be cited as covering them; state the filter wherever the sweep is cited.
- A helper's docstring is a contract: "+∞ beyond the largest" must hold for every input type and sign the helper accepts, or the docstring must say which.

## Correction pass (Authorization I-8, 2026-10-20; appended)
"Authorization I-8 — M3 T0 Review 06 Corrections" authorizes a focused correction of R6-F1, R6-F2 and R6-F3, and of the provenance and switch-point records. It is correction authorization only: T0 remains BLOCKED and NOT ACCEPTED, and Review 07 needs separate authorization. Everything above this section is preserved as written. The statuses Review 06 gave (PARTIALLY RESOLVED for R5-F1, R4-F1, R3-F1, R2-F2 and F2) are **not** changed here; whether they are now resolved is for an independent review to judge.

Preconditions (I-8 §1), verified before any change: branch `milestone-3-t0-reference-spike`, HEAD = origin = `30a4e8d`, clean worktree, CI run 39452378624 green on all four jobs, no protected path changed since `86df2c3`, the five pinned digests match.

| Finding | Disposition | Correction |
|---|---|---|
| M3T0-R6-F1 (MINOR) | **ACCEPTED; CORRECTED** (for an independent review to assess) | E4a at b = 0 through mass ≥ 2^-1074 (below). `inverse_ballistic_bound`, `envelope_ballistic_coefficient`, the E4a docstring and the records |
| M3T0-R6-F2 (NOTE) | **ACCEPTED; CORRECTED** | `_up`/`_dn` over the extended reals with NaN and type rejection; envelope and stage-condition input validation; explicit non-certification |
| M3T0-R6-F3 (NOTE) | **ACCEPTED; CORRECTED** (records) | E4b reclassified as derived under A-FP-1 and A-FP-2; the cap's LIBM_ULP limit computed and published (`zero_force_cap`) |
| Provenance remark (5 287-point search) | **ACCEPTED; CORRECTED** (records) | Marked UNREPRODUCED by an amendment appended to the Review 04 record. The original script, seed and outputs could not be recovered |
| Switch-point remark (b*) | **ACCEPTED; CORRECTED** (records) | Both values stated, by an amendment appended to the Review 05 record |

### R6-F1: the mathematical correction and its domain
- **Domain of E4a.** b is a non-negative finite binary64 (−0.0 is 0; b = +∞ is E4b). cd and area are positive and finite. The vehicle's b was formed by C1, b = fl(mass/fl(cd·area)), or C2, mass = fl(fl(b·cd)·area), with mass a positive finite binary64. Overflow stays excluded by the existing domain condition. Inputs outside this domain raise `ValueError` and never receive a bound.
- **b > 0 (unchanged).** b is a binary64, so b > 0 means b ≥ 2η₀ = 2^-1074. Then b = (mass/P)(1 + δ) or mass/P + η gives P/mass ≤ max((1 + u)/b, 1/(b − η₀)), with b − η₀ ≥ η₀ > 0. The premise "b finite and mass > 0 give b ≥ 2η₀" in the Review 05 docstring was false (it holds for P, not for b). The bound for b > 0 is unchanged, and so is every value it produced.
- **b = 0 (new).** mass/P ≤ η₀ rounds to 0, so b carries no information on the mass beyond mass > 0. Every positive binary64 is ≥ 2^-1074, so cd·area/mass ≤ cd·area/2^-1074 (exact rationals, no rounding). The supremum over C1 masses with b = 0 is attained at mass = 2^-1074 whenever fl(cd·area) ≥ 2 (below 2, b = 0 is unreachable: 2^-1074/P > η₀). C2 with b = 0 gives mass 0, so b = 0 is a C1 case only.
  - R(0) = max(cd·area/2^-1074, R(2^-1074)). The max with the bound at the smallest positive b is not needed for the bound itself. It keeps R non-increasing on all b ≥ 0: R(0) ≥ R(2^-1074) ≥ R(b) for every b ≥ 2^-1074, since R is non-increasing on b > 0 (φ_B/b, R1 and R2 each are). Without it, R(0) < R(2^-1074) whenever cd·area is below about 2.
  - **Denominator positivity.** The only divisor is the constant 2^-1074 > 0. b_R = φ_B/R(0) > 0 because R(0) is finite and positive (cd·area finite and positive). The envelope divides by b_R only.
  - **Rounding direction.** R(0) is exact. b_R is rounded down (ROUND_FLOOR, 60 digits), so the envelope's ratio φ_B/b_R ≥ R(0). The envelope is then rounded up. `envelope_ballistic_coefficient` returns b itself only when b > 0 and R = φ_B/b.
  - **Subnormal arithmetic.** Nothing in R(0) is evaluated in binary64. The model's own subnormal operations (the coefficient chain and its division by a subnormal mass) are the E4 terms already derived under A-FP-1. The vehicle enters them only through cd·area/mass ≤ R, which now holds at b = 0.
  - b_R ≤ b no longer holds at b = 0 (b_R > 0 = b). The envelope needs only R ≥ cd·area/mass, so nothing depends on b_R ≤ b.
- **Result.** At the Review 06 point, the model's drag is 0.9999999999988 (k = 1) to 0.0625 (k = 16) of the corrected envelope (1.5857600878298153e28 m/s² for every k ≤ 16). k = 17 (b = 2^-1074) is unchanged at 0.9705882352929661. The reviewer's `test_zero_b.py` case is k = 1. The bound is tight at k = 1, which is expected: R(0) is attained there.
- **Not changed.** No vehicle condition is introduced. Every positive ballistic coefficient, the three floors (124456.68544510857, 118633.50894662621 and 111511.96182508787 m), their root brackets and margins, and every pre-existing termination result are unchanged to the last bit. Only the keys `review06_counterexamples` and `zero_force_cap` are added (`termination_results_diff.txt`).

### R6-F2: the rounding helpers
- **`_up(q)`** is the smallest binary64 ≥ q in the extended reals: +∞ above the largest finite binary64 (MAX), −MAX below −MAX, ±∞ for ±∞. **`_dn(q)`** mirrors it: MAX above MAX, −∞ below −MAX. Zero is returned as +0.0. q may be an int, Fraction, float or Decimal. NaN (quiet or signalling) raises `ValueError`, and any other type raises `TypeError`.
- **Infinite bound versus invalid input versus failed certification.**
  - A finite envelope value is a certified bound.
  - +∞ is still an upper bound but certifies nothing: the exact bound exceeds MAX, or s = +∞.
  - In `stage_lower_heights` an infinite A0 or A2 makes the speeds after it +∞ and the heights after it −∞, so need(h0) = +∞: the step is **not certified** at h0. The floor bisection only accepts need < 0.
  - The reviewer's `stage_lower_heights(1e7, 2^-1074)` now returns A2 = s3 = +∞ and L4 = M4 = −∞ (need = +∞) instead of an incidental OverflowError.
  - Invalid inputs raise `ValueError`: low not finite or < 0, s NaN or < 0, b NaN or < 0, cd or area not positive and finite, h0 not finite.
- **Unsupported inputs**, documented in the docstrings: NaN, non-real types, b = +∞ for `inverse_ballistic_bound` (E4b; the envelope returns 0 for it).
- No published value changed. The published vehicles' floors and brackets are re-checked bit for bit.

### R6-F3: E4b and A-FP-2
- The cap c₀ = fl(0.5·ρ̂) ≤ (F_ρ·e^η₀·ρ₀,max + N_ρ)/2 + η₀ uses F_ρ = (1 + UF)(1 + u)² and N_ρ = (1 + u)²·ρ₀,max·ν + η₀, with UF = LIBM_ULP × 2^-52 and ν = LIBM_ULP × 2^-1074, the libm allowance of the density's exp. **c₀ ≤ 5/8 depends on A-FP-2.**
- c₀ is affine in LIBM_ULP. It is 0.6125000000000005 at LIBM_ULP = 2, and the cap holds while LIBM_ULP ≤ 91910196476947 (about 2^46.4). `rounding_allowances` refuses to derive the constants above that limit.
- `check_review06.py` derives the limit by a second implementation. It checks that the derived constant equals it at LIBM_ULP = 1, 2, 2^8, 2^20 and 2^40, that it holds at the limit, and that it fails at limit + 1, 2^47 and 2^48.
- The limit is far above the 2^5 to 2^7 ulps the published bounds tolerate, so it does not narrow the guarantee. It is a dependency, not libm-independence. A-FP-2 is not strengthened.

### Provenance and b*
- **The 5 287-point random search** quoted in the Review 04 record is marked **UNREPRODUCED** there by an appended amendment. Its script, seed and outputs were never committed and could not be recovered. No conclusion rests on it. The seeded probe of this pass is committed with its script and log (`adversarial_r6.py.txt`, `adversarial_r6.log`).
- **b*** = cη₀/(c − 1), c = φ(1 − u):
  - with the stored φ_B (1 + 4u, the binary64 that the implementation uses) it is 7.416912861690675e-309. This is the figure the Review 05 record quoted;
  - with the exact φ_B = (1 + u)/(1 − u)² it is (1 + u)·2^-1023 = 1.1125369292536007e-308.

  Both describe valid bounds: R takes the max of its terms for any φ ≥ φ_B. `check_review06.py` checks the implementation's switch at each. No constant changed.

### Evidence (`docs/reviews/raw/M3-T0-review06-findings-correction-evidence/`)
- **Red before.** The new `check_review06.py` (81 checks) on the unmodified `30a4e8d` tree: 55 fail and 26 pass (`checks06_before_30a4e8d.log`).
  - The 55 failures:
    - 24 are R6-F1 behaviour: ZeroDivisionError at the 16 Review 06 masses and in the 8 b = 0 checks;
    - 8 are R6-F1 domain rejections;
    - 19 are R6-F2: helper extremes, random rationals, an unsupported type, the non-certification, the envelope and stage input validation;
    - 4 are record checks.
  - The 26 passes are expected. They are k = 17 (b > 0, already covered); C2 near b = 0; NaN inputs, which the old helpers rejected incidentally; finite in-range helper rows; the unchanged published vehicles; the E4b cap's LIBM_ULP behaviour (the code already enforced the cap, so the defect was its classification); and the equivalence check below.
- **Green after.** `check_review01.py` … `check_review06.py`: 238/238 (`checks_after.log`).
- **Mutation** (`mutation_check_review02.py`, run against all six check files): the control passes 238/238; 59 of 61 corruptions are detected by a declared check, including all 10 R4-F1 and all 10 R5 mutants; 2 are declared equivalent (the two-body stationary-point mutant, and removing the explicit float NaN guard in `_exact`, because `Fraction(nan)` raises ValueError itself; `test_r6f2_float_nan_is_rejected_even_without_the_explicit_guard` establishes it); about 42 min (`mutation_check_review06.json`). The 16 new mutants cover:
  - R6-F1: the b = 0 case removed (the original defect), its bound halved, the monotonicity max dropped, b_R rounded up, and the domain check removed;
  - R6-F2: the overflow cases removed from `_up`, `_up` returning −∞ below −MAX, an infinite Decimal raising (the Review 06 symptom), −0.0 escaping, the float NaN guard removed (equivalent), the infinite-speed guard removed, and the envelope's speed validation removed;
  - R6-F3: the cap computed without the libm allowance, and the Review 05 amendment removed;
  - records: the UNREPRODUCED mark removed, and the exact-φ_B b* unlabelled.
  - A first run (`mutation_run1_with_survivors.json`) left two survivors. The float NaN guard is a true equivalent and is now declared as one. The infinite-speed guard was **not** equivalent: far above h_zero the decimal table density underflows to 0, and 0 × ∞ raises InvalidOperation. The non-certification check now covers that case (`drag_envelope(1e12, inf, 1.0)`), and the rerun detects the mutant. Both runs are kept.
- **Adversarial probe** (seed 20261020; `adversarial_r6.py.txt`, `adversarial_r6.log`). Every case is within the bound, compared in exact rationals:
  - 79 951 random C1 vehicles (37 241 with b = 0), with cd and area across the whole binary64 range, including masses at the b = 0 boundary and its successor. The largest (cd·area/mass)/R is 1 exactly, at mass = 2^-1074, where R(0) is attained;
  - 20 780 C2 vehicles;
  - 4 934 monotonicity pairs R(b) ≥ R(next b), including b = 0;
  - 353 random b = 0 force states, all covered, with a largest drag/envelope of 0.983.
- **Termination results.** Only two keys are added; every pre-existing value is bit-identical (`termination_results_diff.txt`).

### Unresolved assumptions and conditional guarantees (unchanged by this pass)
- **A-FP-2** (libm accuracy) remains an unresolved, explicitly conditional assumption, measured on macOS x86_64 only. It is not a platform guarantee, and E4b now depends on it explicitly. A-FP-1 (IEEE binary64 with gradual underflow) is checked at run time on this host only. A-FP-3 is stated as before.
- **Contract scope.** The contract covers ballistic coefficients formed by C1 or C2 from a positive finite binary64 mass, with no overflow. It does not cover arbitrary independently supplied (mass, b) pairs.
- **Conditions of the floors.** The floors are sufficient, not necessary. They hold under A-FP-1 to A-FP-3 for computed committed heights, bound states with negative two-body energy, no thrust, dt = 10 s, and the stated vehicle constructions.
- **Unchanged.** The GMAT geodetic-drag discrepancy remains escalated (DR-0029 Q-G2-1), and IM-2 is unchanged. DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

### Validation
Recorded in the validation commit that follows this correction commit.

### Validation of the correction commit `9e44850` (appended 2026-10-20)
Evidence is in `docs/reviews/raw/M3-T0-review06-findings-correction-evidence/`. Scratch, home and temporary paths are redacted. Environment: macOS 26.2 x86_64 (the M1/M2 reference host), Python 3.12.15, the locked `uv` environment.

| Check | Result |
|---|---|
| Review 01–06 checks | `check_review01.py` … `check_review06.py`: 238/238 pass (`checks_after.log`; again in the reproducibility clone). Red before, at `30a4e8d`: `check_review06.py` 55 of 81 fail (`checks06_before_30a4e8d.log`) |
| Mutation tests | Control 238/238; 59/59 non-equivalent corruptions detected by a declared check (all R4, R5 and 15 R6 mutants); 2 declared equivalent with an establishing check (`mutation_check_review06.json`; the first run with two survivors is `mutation_run1_with_survivors.json`) |
| Floors and termination results | Only `zero_force_cap` and `review06_counterexamples` added; every other value bit-identical, including the three floors, the root brackets and the margins (`termination_results_diff.txt`) |
| M1 Proof (`run_m1_proof.sh`, fresh clone at `9e44850`) | PASS, 9/9 steps; `working_tree_clean_excluding_evidence: yes` (`m1_proof_run.log`). A separate full pytest run in the same clone: 1185 passed, 3 warnings (`pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Pinned digests | The five pinned artifacts equal `86df2c3` byte for byte, and all 19 VAL-0019 spike digests match (`pinned_digests.log`) |
| Production and protected files | `git diff --name-only 86df2c3 9e44850 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty |
| T0 reproducibility | A third fresh clone ran every T0 experiment twice, including the GMAT harness, `t0_height_error.py` and `t0_axis_ablation.py`. `git status` is empty after each run, so all 96 tracked experiment files are byte-identical; the checks then pass 238/238 (`reproducibility_twice.log`) |
| CI on `9e44850` | Run 39489593015 (https://github.com/guillermoMartin96/tars/actions/runs/39489593015): all four jobs succeeded (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`). CI does not collect the T0 checks (`testpaths = ["tests"]`) |
| Platform limitations | All T0 measurements and checks ran on macOS x86_64 only. A-FP-1's gradual-underflow check and the A-FP-2 libm measurements are host measurements, not platform guarantees |

### Amendment (Authorization I-10, Review 07 M3T0-R7-F1)
Appended 2026-10-20; the text above is kept as written. Review 07 found that the R6-F2 statement "so need(h0) = +∞" holds only when M2 > 0. A step is certified only when need < 0 (the floor bisection and `libm_sensitivity` accept nothing else), and the stage condition reports a non-certification on two paths:
- **M2 ≤ 0:** `stage_lower_heights` returns before M4 (the k2 input may already be below the edge; this return dates from the Review 03 correction, `489d4e7`), and `stage_need` returns need = −M2, finite and ≥ 0. M2 depends on h0 only, not on B or the envelope; with the published constants M2 ≤ 0 up to h0 = 55 749.393 m. The value is finite even when A0 = +∞: h0 = 1 m, B = 2^-1074 gives need = 55 992.318990613036 m;
- **M2 > 0:** need = −min(M2, M3, M4). An envelope of +∞ at A0 or A2, or a stage value outside the binary64 range, gives M3 or M4 = −∞ and need = +∞, as in the reviewer's case `stage_lower_heights(1e7, 2^-1074)` above.

Both are non-certifications, so no floor, bound or certification changes. Review 07 M3T0-R7-F2 is corrected in the docstrings only: "b_R ≤ b" holds for B > 0, as stated above for B = 0. Checks: `check_review07.py`.
