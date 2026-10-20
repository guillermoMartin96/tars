You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 05** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 04. You review; you do not fix.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`88f9752ad03283e56f1c20d79bd28574f493e8a8`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). The implementer states that it is byte-identical to the implementer's installation (console sha256 `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`, atmosphere table `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`). Check this yourself. Pass the console as an absolute path, because the harness changes directory.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files. That is allowed. Afterwards:
    - record `git status --porcelain` and `git diff --stat`;
    - restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed;
    - report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run:
    - `pytest`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0{1,2,3,4}.py` (about 2.5 min).
  - `mutation_check_review02.py` (about 25 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify, not evidence: DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README, and the Review 04 record's correction section. Re-execute, write independent checks, and attempt counterexamples, especially against:
  - the underflow-aware rounding argument;
  - the zero-density height;
  - the envelope's absolute part;
  - the stage condition;
  - the libm sensitivity;
  - the new checks.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass:** `489d4e7`, `44260ef` (reviewed by Review 04); `c15fbd4` (the Review 04 record).
- **Review 04 correction pass (under review now):**
  - `a1feb79385a9dcba4b129a503afceebff6e7ae81`: the correction for M3T0-R4-F1, with the new checks, the extended oracle, evidence script and mutation harness, and the records;
  - `88f9752ad03283e56f1c20d79bd28574f493e8a8`: the validation record of `a1feb79385a9dcba4b129a503afceebff6e7ae81` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff c15fbd4..HEAD`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..HEAD`. The implementer claims that nothing outside `docs/` changed.

## Records to read
- **Reviews 01–04:**
  - raw outputs: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4}.md`;
  - prompts: `docs/reviews/raw/M3-T0-codex-review0{1,2,3,4}-prompt.md`. Together they contain every earlier Tech Lead text verbatim, including the I-15 T0 authorization, whose scope, constraints and validation requirements are T0's acceptance criteria. Authorizations I-4 and I-5 are also reproduced below;
  - reviewer evidence: `docs/reviews/raw/M3-T0-codex-review0{2,3,4}-evidence/`;
  - records and dispositions: `docs/reviews/M3-T0-review-0{1,2,3,4}.md`. The Review 04 record ends with this pass's correction section, its mathematical justification, the A-FP-2 status and the evidence classification.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; four correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Findings so far:**
  - **Review 01:**
    - M3T0-F1 (MAJOR): the missed-crossing bound;
    - F2 (MAJOR): P1 sufficiency, thresholds and the speed proxy;
    - F3 (MINOR): stage numbering;
    - F4 (MINOR): a misquoted residual;
    - F5 (NOTE): the dependency map against the owner gate.
  - **Review 02:**
    - R2-F1 (MINOR): sampled maxima presented as bounds;
    - R2-F2 (MINOR): the co-rotation term evaluated at the lower height bound;
    - R2-F3 (NOTE): checks that passed with zeroed evidence;
    - IM-1: the P6 "0.99 m" figure without a procedure.
  - **Review 03:** R3-F1 (MINOR): the numerical height error at density discontinuities.
  - **Review 04:**
    - R4-F1 (MINOR): the floating-point drag enclosure drops underflow errors. At 190 681 km the model's drag was 2.01 times the envelope.
    - Review 04 judged R3-F1, R2-F2 and F2 PARTIALLY RESOLVED (because of R4-F1) and all other items RESOLVED.
  - **Implementer item IM-2 (this pass, NOTE):** the drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The record is clarified, and no floor is changed.

## Correction evidence supplied by the implementer (claims to verify)
- **Approach:** I-5 Approach A, an underflow-aware bound. No altitude restriction is introduced. The supported domain is unchanged: outside the ellipsoid, no overflow.
- **Arithmetic model** (`t0_termination.py` module notes and the `rounding_allowances` docstring, E1–E6):
  - **A-FP-1:** IEEE round-to-nearest-even with gradual underflow.
    - For × and ÷: (x op y)(1 + δ) + η, with |δ| ≤ 2^-53, |η| ≤ 2^-1075 and δη = 0.
    - For ±, the relative model only: a sum that underflows is exact.
    - sqrt is never subnormal.
    - Multiplying by 0.5 is exact unless the result is subnormal.
    - A result of magnitude ≤ 2^-1075 rounds to 0.
  - **A-FP-2:** libm sin, cos, atan2, hypot, exp and pow satisfy |error| ≤ LIBM_ULP·2^-52·|exact| + LIBM_ULP·2^-1074, with LIBM_ULP = 2. No relative bound is assumed for subnormal results.
  - **A-FP-3:** the 3-term dot product x·x is within γ₃Σx_i² + 3(1 + u)²·2^-1075.
- **E1, E2 (height):**
  - the underflow terms enter the latitude step error and the final formula;
  - α and β change by about 1e-323 and 1e-316 m, so ε_h is unchanged in binary64;
  - β_sel gains 1000·2^-1075 for the kilometre division;
  - the relative and underflow parts are exposed separately in `FPA`.
- **E3 (density) and the zero-density height:**
  - ρ̂ ≤ F_ρ e^{η₀} ρ e^{θ_x X} + N_ρ, with N_ρ ≤ 2.95 × 2^-1074;
  - in the top band, ρ̂ = 0 exactly above the selection height h_zero = 191 735 430.72 m (`zero_density_height`, bounded outward in 60-digit decimals), 9.5e-8 m above the oracle's exact onset.
- **E4 (drag):** |d̂| ≤ F_D′ρ e^{θ_x X}S²/(2B) + (F_A N_ρ/(2B) + K_W W)S² + K_1η₀S + 2η₀.
  - W ≤ η₀(1 + φ_B/B((1 + u)³ + (1 + u)²/cd + (1 + u)/(cd·area))) is the coefficient chain's underflow. Its leading 1 is the final division, the R4-F1 mechanism.
  - The absolute part is evaluated at S_max = s + ω_E(a + (h_zero + β_sel)/(1 − α_sel)) (`_envelope_absolute`).
  - The relative part keeps Review 03's candidate set and in-band monotonicity (`_envelope_relative`).
  - `drag_envelope` now takes the vehicle's cd and area (defaults: V1, 2.2 and 15 m²).
  - `drag_envelope_relative_only` is the superseded envelope, kept to reproduce the finding.
- **E5, E6:** gravity with J2 gains 4η₀, and each RK4 stage position or velocity bound 2η₀.
- **Floors** (`termination` → `floor_comparison`):
  - unchanged to the last bit: 124 456.68544510857, 118 633.50894662621 and 111 511.96182508787 m;
  - the root brackets coincide before and after the correction to 1e-9 m;
  - the margins are 7.2e-7, 1.0e-6 and 8.4e-7 m.
- **A-FP-2 sensitivity** (`termination` → `libm_sensitivity`):
  - claimed: every constant is non-decreasing in LIBM_ULP;
  - the published bracket ends hold for every libm within 2^5, 2^6 and 2^7 ulps;
  - the 2-decimal values rounded up hold within 2^19, 2^17 and 2^20 ulps;
  - the drag-free value rounded to nearest fails at every LIBM_ULP (IM-2).
- **Platform evidence (measurement, not proof; macOS x86_64 host only, because CI does not collect the T0 checks):**
  - `t0_height_error.py` → `libm.subnormal_results` gives the subnormal-result absolute errors, exp 0.74, hypot 0.59 and atan2 0.50 × 2^-1074, and a gradual-underflow probe;
  - the glibc manual is quoted as documentation of intent only.
- **Oracle:** `t0_oracle.py` gains `top_band_height(rho)`. Its static independence from the model is unchanged.
- **Checks** (`check_review04.py`, 48 checks; each states the defect it detects): the reviewer's counterexample; the normal-to-subnormal transition scan; binary64 neighbours of the smallest-normal, coefficient-flip and zero boundaries; the zero-density height; every band base and the lower edge; the height-error bound at high altitude; high-altitude RK4 stages; a second implementation of the underflow constants, the envelope, the floors and the sensitivity; the 2-decimal quotation; the platform's gradual underflow on the model's own operations; the exp subnormal accuracy; a static guard on the stage condition's envelope; and record wording.
- **Mutation harness** (`mutation_check_review02.py`): the control and 35 mutants, each run against checks 01–04. Claimed: the control passes 140/140; 34 are detected by a declared check; 1 (`script_two_body_without_stationary_points`) is equivalent.
  - The 10 R4 mutants and their declared checks:
    - `r4_absolute_part_removed` (the original defect): reviewer, scan, neighbours, stages, envelope second implementation;
    - `r4_coefficient_underflow_term_removed` and `r4_coefficient_last_division_term_removed`: reviewer, scan, neighbours, envelope second implementation;
    - `r4_density_underflow_term_removed`: envelope second implementation only, because it is too small for any constructed point;
    - `r4_zero_density_height_too_low`: the zero-density, envelope and constants checks;
    - `r4_libm_absolute_term_ignored`: constants, envelope;
    - `r4_gravity_and_stage_underflow_terms_removed` and `r4_height_underflow_terms_removed`: the constants check only (about 1e-323);
    - `r4_stage_condition_uses_superseded_envelope`: the static guard only, because the floors are numerically identical;
    - `r4_oracle_density_in_binary64`: the reviewer check.
  - Results: `docs/reviews/raw/M3-T0-review05-correction-evidence/mutation_check_review04.json`. The mutation run was made on the tree before the last record edits; no script changed after it.
- **Red-before / green-after:**
  - `docs/reviews/raw/M3-T0-review05-correction-evidence/checks04_before_c15fbd4.log`: 17 of 48 checks fail on the `c15fbd4` tree with a documented two-part shim. 7 are behavioural, 8 fail on missing constants or results, 1 is the static guard and 1 the records check;
  - `checks_after.log`: 140/140.
- **Validation claims you cannot fully see:**
  - M1 Proof and M2 Proof at `a1feb79385a9dcba4b129a503afceebff6e7ae81` in separate fresh clones;
  - the five pinned digests;
  - byte-identical double runs of all T0 experiments, including GMAT;
  - CI on `a1feb79385a9dcba4b129a503afceebff6e7ae81` and `88f9752ad03283e56f1c20d79bd28574f493e8a8`.

  The logs are in `docs/reviews/raw/M3-T0-review05-correction-evidence/`. You cannot access CI; state that.

## Tech Lead's authorization for this pass (I-5), verbatim

# Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05

You are authorized to correct the outstanding M3T0-R4-F1 finding, validate the correction, and conduct exactly one independent Codex Review 05.

**This authorization does not approve T0, any DR-0029 decision, DR-0028 P6(b), T1, T2, or a merge.**

## 1. Establish and verify the baseline

Confirm:

- Branch: `milestone-3-t0-reference-spike`
- HEAD: `c15fbd4`, matching origin
- Clean working tree
- Review 04 verdict: `REQUEST_CHANGES`
- R4-F1: ACCEPTED, unresolved
- No changes outside `docs/` since `86df2c3`
- M1/M2 pinned baselines unchanged

Read the applicable decision records, T0 report, previous reviews, validation scripts, and Authorization I-4.

If the baseline differs materially, stop and report the discrepancy.

## 2. Correct R4-F1

The defect is that the existing drag-envelope proof assumes a relative floating-point rounding model that is invalid when density calculations enter the subnormal regime.

Review 04 demonstrated a violation at approximately 190,681 km, where computed drag exceeds the envelope by approximately 2.01×.

Investigate three approaches in priority order.

### Approach A — Underflow-aware bound (preferred)

Develop a conservative numerical error bound that accounts for:

- Normal and subnormal binary64 values
- Gradual underflow and rounding to zero
- Absolute rounding error where relative bounds fail
- Intermediate operations, including exponential evaluation
- Any platform-dependent floating-point assumptions
- Propagation of density error into drag acceleration
- The existing geodetic-height selection uncertainty

Do not assume that the exponential library's error is bounded by a fixed relative tolerance in the subnormal regime.

Distinguish mathematical assumptions, experimentally measured behavior, and proven guarantees.

Use independently evaluated high-precision references.

### Approach B — Rigorously restricted applicability

If Approach A cannot produce a defensible global guarantee, determine whether the stage condition can be proven never to require the drag envelope in the underflow regime.

A restriction is acceptable only if:

1. The permitted altitude domain is explicit.
2. The stage condition is proved to remain inside that domain for every relevant case.
3. Boundary and numerical uncertainty are included.
4. No circular dependency exists between the stage-floor proof and the proposed domain restriction.
5. The documentation clearly identifies the restricted guarantee.

Testing alone does not establish the required proof.

### Approach C — Withdraw the affected guarantee

If neither A nor B can be rigorously justified, do not invent a replacement guarantee.

Document the limitation, identify affected conclusions, and stop for my decision before proceeding to Review 05.

## 3. Preserve existing mathematical and numerical contracts

Do not modify approved constants, reference configurations, GMAT artifacts, thresholds, golden files, physics implementation, or M1/M2 validation semantics.

Preserve the corrected geodetic-height envelope from R3-F1 unless the new proof demonstrates that an amendment is necessary.

Recompute all three stage floors using the corrected analysis.

Compare:

- Previous exact roots
- Corrected exact roots
- Published stage floors
- Safety margins
- Applicable stage conditions

Do not silently change a published floor or relax a requirement.

If any floor must change, stop and request authorization.

## 4. Regression and adversarial validation

Extend the existing independent high-precision oracle and regression harness.

At minimum, test:

- The original R4-F1 counterexample
- Normal-to-subnormal transition
- Smallest normal and representative subnormal densities
- Values approaching zero
- Density underflow to zero
- Every atmospheric band boundary
- Both sides of every downward density discontinuity
- Binary64 neighbors of critical boundaries
- Geodetic-height selection uncertainty
- High-altitude retrograde and near-escape cases
- All three stage-floor configurations

Include adversarial mutation tests that deliberately reintroduce the original defect.

For each new test, state which mathematical or implementation defect it detects.

Preserve the independent oracle. Do not use implementation outputs as expected values.

Do not conceal failures through clipping, arbitrary tolerances, or substitutions that make the tested inequality easier to satisfy.

## 5. Resolve or explicitly retain assumptions

Revisit assumption A-FP-2.

Its current support is insufficient for an unconditional cross-platform guarantee.

Determine whether the corrected argument requires A-FP-2, whether the assumption can be weakened, or whether the guarantee must remain conditional.

Do not promote macOS x86_64 measurements to a universal mathematical guarantee.

Record the assumptions and their precise consequences in the applicable decision and evidence documents.

Do not approve an open decision on my behalf.

## 6. Validate the correction

Run:

1. The full existing T0 regression suite.
2. All new R4-F1 boundary tests.
3. Independent high-precision comparisons.
4. Relevant mutation tests.
5. M1 Proof.
6. M2 Proof.
7. Pinned-digest verification.
8. Reproducibility verification.
9. All four CI jobs.

Document commands, environments, results, commits, and evidence locations.

Where applicable, demonstrate that the new regression tests fail against the defective baseline and pass against the corrected version.

Any unexpected failure must be investigated rather than dismissed.

## 7. Independent Codex Review 05

Only after the correction and required validations pass, invoke an independent Codex reviewer.

Provide:

- The complete relevant T0 specification
- Authorization I-4 and I-5
- Reviews 01–04 and their dispositions
- The R4-F1 correction
- Mathematical derivations
- Assumption register
- Regression and mutation evidence
- Stage-floor calculations
- Reproducibility results
- M1/M2 Proof evidence
- Relevant commits and diffs

Require Codex to independently evaluate:

1. Whether R4-F1 is resolved.
2. Whether the underflow-aware rounding argument is mathematically sound.
3. Whether absolute and relative errors are propagated correctly.
4. Whether any claimed domain restriction is rigorously established.
5. Whether the geodetic-height uncertainty remains correctly incorporated.
6. Whether stage-floor conclusions remain justified.
7. Whether earlier findings remain resolved.
8. Whether regression tests genuinely detect the original defects.
9. Whether unsupported cross-platform assumptions remain.
10. Whether any new BLOCKER, MAJOR, or MINOR finding exists.

Require an explicit `PASS` or `REQUEST_CHANGES` verdict.

The reviewer must independently check the argument rather than merely accept the author's conclusions.

## 8. Review disposition and stopping rules

If Review 05 returns `REQUEST_CHANGES`:

- Record every finding and severity.
- Independently reproduce each actionable finding where feasible.
- Preserve raw review evidence.
- Do not fix new findings.
- Do not start Review 06.
- Do not declare T0 accepted.
- Stop for my authorization.

If Review 05 returns unconditional `PASS`:

- Record the review and evidence.
- Prepare a final T0 acceptance report.
- Identify all remaining open decisions and assumptions.
- Stop for my explicit acceptance.

A PASS from Codex does not itself authorize merging or starting T1/T2.

## 9. Git and scope discipline

- Work only on the authorized T0 branch.
- Keep changes within the authorized documentation and validation scope.
- Do not modify M1/M2 baselines.
- Do not force-push.
- Preserve append-only decision and review history.
- Commit logically separated corrections, validation records, and review records.
- Verify remote synchronization and clean working-tree status.
- Do not alter branch protection.
- Do not merge.

## 10. Final checkpoint report

Report:

1. Branch, HEAD, commits, and working-tree state.
2. Selected correction approach and rationale.
3. Mathematical proof and its assumptions.
4. R4-F1 regression results.
5. Mutation-test results.
6. Updated stage-floor comparison.
7. Status of A-FP-2.
8. Status of every previous review finding.
9. M1/M2 Proof and pinned-digest results.
10. Reproducibility and four-platform CI results.
11. Independent Review 05 verdict.
12. Remaining open decisions and risks.
13. Whether T0 is eligible for my acceptance review.
14. The exact authorization needed next.

**Stop at the checkpoint. No merge, no T1/T2, and no automatic additional review rounds.**

## Previous Tech Lead authorization (I-4, for Review 04), verbatim

# Authorization I-4: M3 T0 — R3-F1 Correction and Independent Review 04

You are authorized to correct M3T0-R3-F1, validate the correction, and conduct exactly one independent Codex Review 04.

**T0 remains BLOCKED. This authorization does not approve T0, DR-0029, DR-0028 P6(b), merging, or starting T1/T2.**

## 1. Verify the checkpoint

Confirm:

- Branch: `milestone-3-t0-reference-spike`
- Expected HEAD: `c6c0fff`
- Local HEAD matches origin.
- Working tree is clean.
- Review 03 verdict is `REQUEST_CHANGES`.
- M3T0-R3-F1 is accepted but not corrected.
- No changes outside `docs/` since `86df2c3`.

Stop and report any material discrepancy.

## 2. Correct M3T0-R3-F1

The current drag envelope can be violated when floating-point rounding places the computed altitude on the opposite side of a discontinuous atmospheric density boundary from the true altitude.

The reported counterexample near 120 km demonstrates this issue. Additional cases were found near 200 km and 250 km.

### A. Establish the height-error bound

Derive a justified upper bound, ε_h, on the difference between the model-computed altitude and the corresponding mathematically defined altitude.

Requirements:

1. Explicitly identify the altitude calculation and its floating-point operations.
2. State the arithmetic assumptions, precision, rounding behavior, and supported numerical domain.
3. Account for cancellation, intermediate rounding, and coordinate transformations where applicable.
4. Distinguish a proven worst-case bound from an empirically observed maximum.
5. Use high-precision calculations as independent verification, not as a substitute for a proof.
6. If a rigorous global bound cannot be established, document the limitation and keep the affected guarantee blocked.

Do not choose ε_h solely because it passes the known counterexamples.

### B. Correct the drag envelope

Using the justified height-error bound:

1. Expand the relevant altitude domain conservatively to include all true heights consistent with the model-computed height.
2. Re-derive the drag envelope over the expanded domain.
3. Explicitly account for discontinuities in the atmospheric density table.
4. Check whether monotonicity arguments remain valid across band boundaries.
5. Recompute affected stage floors and margins.
6. Document the derivation, assumptions, units, and numerical results.

Do not modify the published atmospheric density table, gravitational constants, or underlying M1/M2 physics.

If the corrected envelope cannot support a claimed sufficient condition, withdraw that guarantee rather than weakening the verification.

### C. Adversarial boundary tests

Add independent tests at all 12 identified density-drop boundaries.

Include:

- True heights immediately below each boundary.
- True heights immediately above each boundary.
- Exactly representable boundary values where applicable.
- Adjacent floating-point representable values.
- Cases where computed and true heights select different density bands.
- The original 120 km counterexample.
- The additional 200 km and 250 km counterexamples.
- Near-escape and retrograde stress cases.

Use sufficiently precise reference calculations to independently evaluate the expected density and drag.

**Remove the `min(low, h_model)` substitution from the adversarial oracle.**

The test oracle must use the independently established true-height reference and must not reproduce the same altitude-selection logic as the implementation under test.

### D. Mutation verification

Extend the mutation suite to demonstrate that the new checks fail when:

1. The height-error allowance is removed or reduced below its justified bound.
2. The incorrect density band is selected at a discontinuity.
3. The drag envelope is evaluated using the wrong altitude limit.
4. The adversarial oracle is changed back to the self-referential implementation.

Show red-before/green-after evidence.

A mutant that does not actually violate the intended invariant must not be counted as evidence that the invariant is protected.

## 3. Update the evidence and decision records

Update the relevant T0 technical reports, derivations, and review disposition records.

Preserve the original findings and reviewer language.

Explicitly distinguish:

- Mathematically proved guarantees.
- Numerically verified results.
- Empirical observations.
- Unresolved assumptions.
- Owner decisions still required.

Record whether the correction changes the proposed P1 recommendation or any stage floor.

Do not approve or close DR-0029 P1–P10.

Do not approve DR-0028 P6(b).

Keep the GMAT geodetic-drag discrepancy escalated.

## 4. Validation

Run:

1. Focused R3-F1 regression tests.
2. Boundary and high-precision reference tests.
3. Mutation tests.
4. All existing Review 01–03 regression checks.
5. The full relevant pytest suite.
6. Complete M1 and M2 Proof procedures in clean environments.
7. Pinned-digest verification.
8. T0 reproducibility verification, including GMAT where applicable.

Verify that no authorized M1/M2 baseline, golden, threshold, contract, or validation semantics changed.

Commit and push the corrections.

Wait for all four required CI jobs to finish successfully.

If validation fails, correct only defects within the authorized scope. Stop if a resolution requires changing approved physics, validation thresholds, or decision authority.

## 5. Independent Codex Review 04

After successful validation, conduct exactly one independent Codex review.

Provide:

- Review 01, 02, and 03 findings and dispositions.
- The complete R3-F1 correction diff.
- Height-error derivation.
- Atmospheric boundary analysis.
- Corrected drag-envelope derivation.
- Recomputed stage floors.
- Independent high-precision reference calculations.
- Regression and mutation evidence.
- M1/M2 Proof and CI results.
- Current decision and assumption registers.

Require Codex to evaluate:

1. Whether ε_h is rigorously justified over the claimed domain.
2. Whether the corrected envelope conservatively handles every atmospheric discontinuity.
3. Whether the stage floors and sufficient conditions follow from the corrected derivation.
4. Whether the regression oracle is independent.
5. Whether the mutation tests detect the relevant defects.
6. Whether F2, R2-F2, and R3-F1 are fully resolved.
7. Whether previous findings remain resolved.
8. Whether any new mathematical, numerical, or verification defects exist.
9. Whether scope and decision authority were preserved.

Require an explicit `PASS` or `REQUEST_CHANGES` verdict supported by evidence.

Do not request a favorable verdict.

Preserve the raw review output.

## 6. Mandatory stop conditions

If Review 04 returns `REQUEST_CHANGES`:

- Record all findings.
- Independently reproduce them where feasible.
- Do not fix new findings automatically.
- Do not start Review 05.
- Stop for my authorization.

If Review 04 returns unconditional `PASS`:

- Prepare a T0 acceptance candidate report.
- Include the complete evidence matrix and remaining decision dependencies.
- Stop for my explicit acceptance.

In either case:

- Do not merge.
- Do not start T1 or T2.
- Do not approve DR-0029 P1–P10.
- Do not approve DR-0028 P6(b).
- Do not alter branch protection.
- Do not modify approved M1/M2 baselines.

## 7. Final checkpoint report

Report:

1. Branch, HEAD, commits, and working-tree status.
2. R3-F1 correction and its mathematical justification.
3. Original and recomputed stage floors.
4. Boundary-test results.
5. Mutation-test results.
6. Previous finding dispositions.
7. M1/M2 Proof results and pinned digests.
8. CI results.
9. Codex Review 04 verdict.
10. Outstanding decisions and escalations.
11. Whether T0 is eligible for my acceptance review.
12. Exact authorization required next.

**Proceed with the R3-F1 correction and Review 04 only. Stop at the next checkpoint.**

## What to review
Evaluate each of the following independently, with your own execution or computation wherever possible.
1. **Is M3T0-R4-F1 resolved?** Reproduce the reviewer's point and test the corrected envelope on your own subnormal-regime constructions: positions, velocities and both vehicles.
2. **Is the underflow-aware rounding argument mathematically sound?**
   - Check the mixed model of A-FP-1: the δη = 0 form, exact underflowing sums, sqrt, multiplication by 0.5, and rounding to 0.
   - Re-derive E1–E6 operation by operation against the model's code (`t0_model.py`: `geodetic_iterative`, `density`, `acceleration`, `j2_accel`, `rk4_step`).
3. **Are absolute and relative errors propagated correctly?**
   - Check:
     - the density term N_ρ;
     - the coefficient chain W, including the final division;
     - the dot product, sqrt and the two products with v_rel;
     - the factor τ;
     - the S_max argument;
     - the zero-density height h_zero and its outward rounding;
     - the gravity and stage terms.
   - Look for a term that is missing, double-counted or bounded in the wrong direction.
4. **Is any claimed domain restriction rigorously established?** The implementer claims none is introduced. Check:
   - that the h_zero cutoff is a derived property of the computed force, not a restriction;
   - whether the vehicle parameters (cd, area) entering W constitute an undisclosed restriction;
   - that "no overflow" is the only remaining domain condition.
5. **Does the geodetic-height uncertainty remain correctly incorporated?** Check ε_h, ε_sel and the band candidates of Review 03, now with the underflow terms, at the bases and at high altitude.
6. **Do the stage-floor conclusions remain justified?**
   - Recompute the floors and the roots.
   - Check that the floors are unchanged, the margins and the monotonicity in h0, and the libm sensitivity, including its monotonicity-in-LIBM_ULP argument.
   - Check IM-2: the 2-decimal quotations against the bounds.
7. **Do earlier findings remain resolved?** M3T0-F1 … F5, R2-F1 … F3, IM-1 and R3-F1.
8. **Do the regression tests genuinely detect the original defects?**
   - Re-run the red-before.
   - Check that every claimed detection is real.
   - Check whether a mutant could be counted as detected for an unrelated reason.
   - Check whether the derivation-only and static-guard classifications are sound.
   - Look for corruptions that still pass. Check that no expected value comes from the implementation.
9. **Do unsupported cross-platform assumptions remain?**
   - Is A-FP-2's status honestly stated: required, weakened and conditional?
   - Are the platform measurements presented only as measurements?
   - Is the glibc quotation used correctly?
   - Is the remaining A-FP-1 assumption, that gradual underflow is the platform's mode, stated correctly?
10. **Is there any new BLOCKER, MAJOR or MINOR finding?** This includes record correctness: check every number quoted in DR-0029, VAL-0019, the T0 report, the decision matrix, the README and the Review 04 correction section against the committed result files and your own computation. Also check scope and decision authority:
    - no production change;
    - no change to approved physics, constants, the atmosphere table, frames, thresholds, goldens, references, M1/M2 contracts or validation semantics;
    - no new dependency;
    - no DR-0029 item or DR-0028 P6(b) treated as decided;
    - the geodetic-drag discrepancy still escalated.

Also re-run the Python experiments (and the GMAT harness where practical), compare the outputs byte for byte, and re-check the five pinned digests.

## Required output
1. **Ledger:** every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and M3T0-F1 … F5. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence.
3. **New findings.** Number them `M3T0-R5-F1`, `M3T0-R5-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
4. **Verification limits:** what you could not check.
5. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any item in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
6. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review05.md`.
