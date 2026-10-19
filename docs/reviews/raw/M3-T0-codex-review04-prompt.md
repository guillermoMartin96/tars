You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T0 Review 04** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T0 (the reference-configuration spike). It is a fresh review of the correction pass made after Review 03. You review; you do not fix.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t0-reference-spike`, detached at the pinned checkpoint **`44260ef3`**, with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available.
- **GMAT:** a private, writable copy of GMAT R2026a is at `../GMAT R2026a/` (console `../GMAT R2026a/bin/GmatConsole`). The implementer states it is byte-identical to the implementer's installation (console sha256 `1162803d…52e2`, atmosphere table `75762f67…a85e`). Check this yourself. Pass the console as an absolute path; the harness changes directory.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed experiments in place rewrites their own output files. That is allowed. Afterwards, record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- docs/science/experiments/m3-t0` if anything changed, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run:
    - `pytest`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review01.py docs/science/experiments/m3-t0/check_review02.py docs/science/experiments/m3-t0/check_review03.py` (about 2–3 min).
  - `mutation_check_review02.py` (about 15–20 min with 4 threads) copies `docs/` into a temporary directory and does not modify the tree. You may run it, or a subset of its mutants.
  - Finish with a clean tracked tree.
- **Do not accept the implementer's conclusions.** The corrected records are claims to verify, not evidence: DR-0029, VAL-0019, the T0 report, the decision matrix, the experiment README and the Review 03 dispositions. Re-execute, write independent checks, and attempt counterexamples, especially against:
  - the height-error derivation;
  - the corrected envelope;
  - the stage condition;
  - the oracle;
  - the new checks.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed.

## Commits
- **Accepted baseline:** `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`, the merge commit of PR #4 (the accepted M3 planning baseline).
- **T0 spike and Review 01:** `3729ffd`, `294e1f5` and `ca84986` (reviewed by Review 01); `bdcaacf` (the Review 01 record and the P1–P10 decision matrix).
- **Review 01 correction pass:** `03e8f63`, `ead2a84` (reviewed by Review 02); `5548d11` (the Review 02 record).
- **Review 02 correction pass:** `14d98f0`, `51e110b` (reviewed by Review 03); `c6c0fff` (the Review 03 record).
- **Review 03 correction pass (under review now):**
  - `489d4e7`: the correction for M3T0-R3-F1, with the oracle, the new checks, the evidence script and the extended mutation harness;
  - `44260ef`: the validation record of `489d4e7` (Proof, digests, reproducibility, CI).
- **Complete correction diff:** `git diff c6c0fff..44260ef3`. Run it yourself.
- **Full T0 diff:** `git diff 86df2c3..44260ef3`. The implementer claims nothing outside `docs/` changed.

## Records to read
- **Reviews 01–03:**
  - raw outputs `docs/reviews/raw/M3-T0-codex-review0{1,2,3}.md`;
  - prompts `docs/reviews/raw/M3-T0-codex-review0{1,2,3}-prompt.md`. Together they contain every earlier Tech Lead text verbatim: the I-15 T0 authorization (whose scope, constraints and validation requirements are T0's acceptance criteria), the T0 review instruction, the Review 01 correction authorization and the Review 02 correction authorization;
  - reviewer evidence `docs/reviews/raw/M3-T0-codex-review0{2,3}-evidence/`;
  - records and dispositions `docs/reviews/M3-T0-review-0{1,2,3}.md`. The Review 03 record ends with this pass's correction section and evidence classification.
- **Decision and assumption registers:**
  - `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (OPEN; three correction logs at the end);
  - DR-0024 … DR-0028 in `docs/decisions/requests/`;
  - `docs/science/assumptions.md`;
  - VAL-0019 in `docs/science/validation.md`;
  - `docs/milestones/M3-T0-report.md`;
  - `docs/milestones/M3-T0-decision-matrix.md`.
- **Findings so far:**
  - **Review 01:** M3T0-F1 (MAJOR, missed-crossing bound), F2 (MAJOR, P1 sufficiency, thresholds, speed proxy), F3 (MINOR, stage numbering), F4 (MINOR, misquoted residual), F5 (NOTE, dependency map vs owner gate).
  - **Review 02:** M3T0-R2-F1 (MINOR, sampled maxima presented as bounds), R2-F2 (MINOR, co-rotation term at the lower height bound), R2-F3 (NOTE, checks passed with zeroed evidence), and implementer item IM-1 (P6 "0.99 m" without a procedure).
  - **Review 03:** M3T0-R3-F1 (MINOR) — the drag envelope omitted the numerical height error at density discontinuities, and the adversarial check hid it with `min(low, h_model)`. Review 03 judged R2-F2 and F2 PARTIALLY RESOLVED (because of R3-F1) and all other items RESOLVED.

## Correction evidence supplied by the implementer (claims to verify)
- **Height-error bound ε_h** (`t0_termination.py`, `rounding_allowances` docstring E1–E6; DR-0029 P1; Review 03 record, "Mathematical justification"):
  - **Claim:** |h_computed − h_true| ≤ ε_h(h) = αh + β for every binary64 point outside the ellipsoid, where h_true is the exact distance to the ellipsoid (a = A_WGS84, e² = E2_WGS84, as exact values). α = 1.2212e-15 and β = 8.8777e-9 m, so ε_h = 9.02e-9 m at 120 km.
  - **Geometric argument:**
    - the height formula evaluated exactly at the returned latitude λ is the distance from r to the supporting plane with normal n(λ), so H(λ) ≤ h with H′(φ) = 0;
    - H″ = −H − M, which gives a second-order latitude term;
    - the latitude iteration is a contraction with k ≤ 0.00683 for every |r| ≥ b;
    - the per-step rounding η gives |λ − φ| ≤ 1.43e-15 rad.
  - **Rounding:** the final formula's rounding is bounded operation by operation: (1 + u)(Θ₁₂|r| + θ₄a) + u|H|.
  - **Assumptions:**
    - A-FP-1: IEEE binary64, round to nearest, correctly rounded + − × / √;
    - A-FP-2: libm sin, cos, atan2, hypot, exp and pow have relative error ≤ 2 × 2^-52. This is an assumption, measured on the implementer's host (macOS x86_64) only. There, cos reaches 1.41 ulp (0.94 × 2^-52 relative), which is why 2 × 2^-52 and not 1 is assumed;
    - A-FP-3: numpy elementwise products, and a 3-term dot product within γ₃.
  - **Supported domain:** exterior points; no overflow.
- **Selection height, density, drag, gravity and RK4 stages (E2–E6):** derived relative rounding factors F_D, θ_x, F_g and F_J; the band-selection allowance ε_sel = ε_h(1 + u) + u·h; the stage-arithmetic bounds |fl(r0 + fl(c k)) − r0| ≤ (1 + u)²c|k| + u|r0|.
- **Corrected envelope** (`drag_envelope`): for true heights ≥ L, the supremum over selection heights ≥ L − ε_sel(L) of F_D ρ(h) e^{θ_x X}(s + ω_E(a + (h + β_sel)/(1 − α_sel)))²/(2B). Here ρ is the exact table formula with the file's decimal values. The candidates are L − ε_sel(L) and every base above it (band above, GMAT's rule). The function is claimed to decrease in-band when (1 − α)(1 − θ_x)a > 2H. It is evaluated in 60-digit decimal arithmetic with outward pads, then rounded up.
- **Stage condition** (`stage_lower_heights`, `sufficient_stage_condition`):
  - **Height convention:** it is now stated for the computed committed height h0, with H0 = (h0 − β)/(1 + α).
  - **Lower bounds:** L_k are the lower true-height bounds and M_k = (1 − α)L_k − β the lower computed-height bounds; M_k > 0 is required.
  - **Monotonicity in h0** is claimed.
  - **Published floor:** the upper end of a bisection bracket at which the outward-rounded need is negative.
  - **Floors:** 124 456.68544510857 m (B 25.8), 118 633.50894662621 m (B 100), 111 511.96182508787 m (drag-free). The exact roots are claimed to move by +1.9e-8 m against Review 02; the published values are unchanged at 2 decimals. The P1 recommendation is unchanged.
- **Oracle** (`t0_oracle.py`):
  - exact geodetic height by Newton on the Lagrange parameter of the foot point, 60-digit decimals;
  - the table read as decimal strings, with GMAT's band rule;
  - claimed to share no altitude or band-selection code with `t0_model.py`;
  - cross-validated in `check_review03.py` by Vermeille's closed form in decimals.
- **Checks:**
  - **`check_review03.py`** (42 checks):
    - the reviewer's 120 km counterexample, and constructed counterexamples at all 12 downward jumps, including 200 and 250 km;
    - per-jump boundary points: exact-base equatorial points and their ±3 adjacent binary64 values; true heights 1e-8 … 1e-9 m below and above; crossing points;
    - ε_h against sampled errors;
    - the derivation's constants and the floors by a second implementation;
    - an oracle self-test, and static independence guards;
    - RK4 stages with oracle heights (near-escape, retrograde, straight-down, near the jumps);
    - a provenance rerun of `t0_height_error.py`, and record wording.
  - **`check_review02.py`:** the adversarial test now takes its bound at the oracle's true height and measures the model's drag vector directly, with no allowance. `min(low, h_model)` is removed.
- **Empirical side** (`t0_height_error.py` → `t0_height_error_results.json`): the libm measurement; the observed height error, at most 2.06e-9 m over 13 050 points (0.22 of ε_h); the crossing counts at the 12 jumps.
- **Mutation harness** (`mutation_check_review02.py`): the control (unmodified copy) and 25 mutants, each run against the full Review 01–03 check set in a copied `docs/` tree. Claimed: the control passes 92/92; 24 mutants are detected by at least one of their declared checks; 1 (`script_two_body_without_stationary_points`) is declared equivalent. The 9 mutants added in this pass, with their declared checks, are:
  - `r3_height_allowance_removed` (the ε_h allowance replaced by none): the reviewer test, the per-jump tests, the boundary points and the derivation-constants check;
  - `r3_height_allowance_below_observed_error` (the allowance divided by 10, below the observed maximum error): the reviewer, per-jump and boundary tests. In the run, only the boundary points (and the derivation and provenance checks) failed; the reviewer and per-jump tests passed;
  - `r3_height_allowance_slightly_below_bound` (the allowance × 9/10, above every observed error): the derivation-constants check only;
  - `r3_envelope_lower_limit_unwidened` (the envelope's lower selection height not widened by ε_sel) and `r3_envelope_band_of_unwidened_limit` (band candidates taken from the unwidened limit): the reviewer, per-jump and boundary tests;
  - `r3_model_exact_base_in_band_below` (`<` → `<=` in the model's band selection, so an exact base goes to the band below): the boundary points;
  - `r3_oracle_returns_the_model_height` (the oracle returns `geodetic_iterative`): the oracle self-test, the static-independence guard and the two-oracle agreement;
  - `r3_review02_oracle_reverted_to_model_height` (the Review 02 adversarial test reverted to the model height): the static Review 02 guard;
  - `r3_allowance_removed_and_review02_oracle_reverted` (both): claimed to show that the reverted Review 02 adversarial test is blind while `check_review03.py` detects the defect.
  The provenance checks fail for most script mutants because they rerun the scripts; the harness counts a mutant as detected only if one of its *declared* checks fails. Per-mutant expected and failed checks are in Results: `docs/reviews/raw/M3-T0-review04-correction-evidence/mutation_check_review03.json`.
- **Red-before / green-after:**
  - `docs/reviews/raw/M3-T0-review04-correction-evidence/checks03_before_c6c0fff.log`: the new checks on the `c6c0fff` tree, with a one-line alias shim, `drag_envelope_exact_height = drag_envelope`, documented in the log;
  - `checks_after.log`;
  - `mutation_check_review03.json`.
- **Validation claims you cannot fully see:** M1 Proof and M2 Proof at `489d4e7` in separate fresh clones; five pinned digests; byte-identical double runs of all T0 experiments, including the GMAT harness; CI on `489d4e7` and `44260ef`. Logs are in `docs/reviews/raw/M3-T0-review04-correction-evidence/`. You cannot access CI; state that.

## Tech Lead's authorization for this pass, verbatim
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
1. **Is ε_h rigorously justified over the claimed domain?**
   - Re-derive or refute each step: the support-function and stationarity properties, the H″ bound, the contraction constant and the per-step rounding η, the stopping rule, and the operation-by-operation rounding bound of the final formula with its cancellation.
   - Are the assumptions A-FP-1 … A-FP-3 stated correctly and sufficient? Is the domain stated correctly (exterior points; the pole; the equator; very small and very large heights; subnormals)?
   - Compare ε_h with your own high-precision measurements. Try to construct a binary64 point whose error exceeds ε_h.
   - Is the libm assumption, and how it was chosen, honestly presented, and is the measurement sound?
2. **Does the corrected envelope conservatively handle every atmospheric discontinuity?**
   - All band boundaries, upward and downward jumps, exact bases, the kilometre conversion, the top band and the lower edge.
   - The radius term with the height error; F_D, θ_x and the vehicle-mass construction; the in-band monotonicity condition; the candidate set; the decimal evaluation and its padding.
   - Attempt counterexamples with your own oracle.
3. **Do the stage floors and the sufficient condition follow from the corrected derivation?**
   - Gravity rounding (F_g, F_J and the G bound), the RK4 stage arithmetic, the computed-height convention for h0, and M_k > 0 at the 0 m edge.
   - Monotonicity in h0; the bisection and the outward rounding.
   - Recompute the floors yourself. Try near-escape, retrograde equatorial, straight-down, polar and at-floor states, and stages that land near the downward jumps.
4. **Is the regression oracle independent?** Does `t0_oracle.py` share any altitude or band-selection logic with `t0_model.py`? Is it accurate? Are the expected values in `check_review02.py` / `check_review03.py` taken from it and not from the implementation?
5. **Do the mutation tests detect the relevant defects?**
   - The four required defect classes: height allowance removed or reduced; wrong band at a discontinuity; wrong altitude limit; oracle reverted.
   - Is the classification sound? Could a mutant be counted as detected for an unrelated reason? Is any mutant counted as evidence that does not violate the invariant? Do the declared-only-by-derivation and combined mutants mean what the implementer says?
   - Are there corruptions that still pass?
6. **Are M3T0-F2, M3T0-R2-F2 and M3T0-R3-F1 fully resolved?**
7. **Do the previous findings remain resolved?** M3T0-F1, F3, F4, F5; R2-F1, R2-F3; IM-1.
8. **Are there new mathematical, numerical or verification defects?** These include record correctness: check every number quoted in DR-0029, VAL-0019, the T0 report, the decision matrix, the README and the Review 03 correction section against the committed result files and your own computation.
9. **Were scope and decision authority preserved?**
   - No production change.
   - No change to approved physics, constants, the atmosphere table, frames, thresholds, goldens, references, M1/M2 contracts or validation semantics.
   - No new dependency; nothing beyond T0.
   - No DR-0029 item (P1–P10) or DR-0028 P6 (b) treated as decided; no recommendation changed without disclosure.
   - The geodetic-drag discrepancy is still escalated.

Also re-run the Python experiments (and the GMAT harness where practical) and compare the outputs byte for byte, and re-check the five pinned digests.

## Required output
1. **Ledger:** every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Resolution table** for M3T0-R3-F1, R2-F1, R2-F2, R2-F3, IM-1 and M3T0-F1 … F5. Give each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your evidence.
3. **New findings.** Number them `M3T0-R4-F1`, `M3T0-R4-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE);
   - file and line references;
   - concrete evidence or a reproducible counterexample;
   - a recommended correction;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
4. **Verification limits:** what you could not check.
5. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any finding in the resolution table that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
6. Write the complete review, identical to your final message, to `review_scratch/M3-T0-codex-review04.md`.
