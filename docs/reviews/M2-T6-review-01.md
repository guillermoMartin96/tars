# External Review: M2 Task T6: GMAT M2 finite-burn reference and O9

**Reviewer/model:** OpenAI Codex CLI (separate provider), session `01a12cd6-3430-7502-a545-b7558624d547`.  
**Date:** 2026-10-11  
**Reviewed revision:** `805d789` (diff `a0169e7..805d789`).  
**Scope:** Tech Lead T6 conditions:
- T5 baseline preserved;
- GMAT as an independent reference, from scenario inputs only;
- position, velocity, timing, mass and events compared;
- reproducibility and provenance;
- negative and mutation tests;
- DR-0016 alignment and the 11–15 µm floor;
- DR-0017 and DR-0018 separation;
- documented discrepancies;
- provisional thresholds.

**Raw:** `raw/M2-T6-codex.md`; prompt and probes in `raw/M2-T6-codex-prompt.md` and `raw/M2-T6-codex-scratch/`.

## Summary
**Verdict: FAIL.**

Confirmed by the reviewer:
- 858 tests, lint, a 212-check M2 Proof, M1 Proof, determinism, golden and GMAT M1 all pass;
- fresh GMAT M2 measurements match VAL-0014;
- all 18 row mutations across three missions are rejected;
- the inputs are derived from the scenario; the engine configuration (checked against GMAT R2026a `ChemicalThruster.cpp`) and adjacent-burn switching are correct;
- thresholds are provisional, and the DOP853 floor and the DR-0017/DR-0018 separation are respected;
- no T5 gate was loosened.

The defects are in reference acceptance, provenance, the replacement policy and standalone completeness. The committed numerical results were not wrong.

The reviewer noted that GMAT was in fact present in the review environment, so the reproduction tests ran and passed.

## Findings
All seven are **`ACCEPTED`**.

### F1: `run` stores numerically rejected references (High)
**Implementer reasoning:** Correct. `run` checked only integrity violations, never the numerical gates, and wrote the committed files before validating.  
**Fix:**
- `run` stages every artifact (script, report, console log, metadata and the updated approved-digest manifest) in a temporary directory.
- It then validates the staged reference completely: provenance, alignment, coverage, every O9 gate, gate coverage, and a clean audit of the simulator run.
- Only then does it replace the committed files, with the manifest written last as the commit marker. On failure nothing is replaced.
- **Tests:** `test_run_validates_a_staged_reference_and_replaces_nothing_on_failure` (a fake `GmatConsole` emits a +1 m row; exit 1, directory byte-identical), `test_numerical_gates_apply_to_a_consistent_but_wrong_reference`.

### F2: script comparison discards assignment placement (Medium)
**Implementer reasoning:** Correct.  
**Fix:**
- `split_script` replaces the six state literals **in place** with a placeholder, so position is part of the comparison.
- Missing or duplicated components raise an error.
- **Tests:** `test_state_assignments_must_stay_in_place_once` (move, duplicate, drop), `test_split_script_requires_each_state_component_exactly_once`.

### F3: provenance cannot establish external origin (High)
**Implementer reasoning:** Correct. Numerical agreement cannot prove origin, and the metadata checks were incomplete.  
**Fix:**
- Required metadata: mission, scenario, model, command, revision, timestamp, host, and the replacement reason.
- **Approved binary:** the GMAT version, build date and console sha256 are pinned to the approved install.
- **Console log:** bound by its sha256, and it must record GMAT's success marker with no failure or exception.
- **Approved-digest manifest:** `toolbox/references/gmat/m2/APPROVED_DIGESTS.json`, with digests and replacement history. A reference that is not in it is rejected, so any change shows in the reviewed diff.
- **Documented limit:**
  - These controls make silent or accidental substitution detectable. They cannot prove that a deliberately fabricated artifact set did not come from GMAT.
  - External origin is established by the reproduction test, which re-runs the approved GMAT and requires byte-identical reports wherever GMAT is installed, and by review of manifest changes.
- **Tests:** `test_provenance_is_required` (dropped fields, failed console, other binary, unapproved digest). `test_fabricated_reference_needs_a_manifest_change` shows that a DOP853-fabricated report with consistent metadata is rejected only by the manifest. This is the documented limit, made executable.

### F4: `generate` bypasses the replacement guard (Medium)
**Implementer reasoning:** Correct.  
**Fix:**
- `generate` writes previews to `--out` only, and refuses the reference directory.
- `run` applies the guard whenever any artifact, or a manifest entry, exists.
- **Test:** `test_generate_never_writes_into_the_references`.

### F5: missing simulator observations produce vacuous passes (Medium)
**Implementer reasoning:** Correct for standalone `compare` (the integrated Proof was protected by the T5 audit).  
**Fix:**
- `coverage_problems` requires, from the scenario:
  - every telemetry time and the horizon;
  - every predicted ignition and cutoff up to the horizon (no cutoff after it, per DR-0018);
  - every propulsion sample on a GMAT row at the contract cadence.
- Standalone `compare` also requires a clean `audit_run` of the simulator run.
- **Test:** `test_missing_observations_are_not_vacuous_passes` (states, burn end, propulsion samples). The existing cutoff-timing mutant is now also caught here: its `BurnEnded` at 677.3000000773 s is not the predicted 677.3 s.

### F6: standalone comparison accepts missing thresholds (Medium)
**Implementer reasoning:** Correct.  
**Fix:**
- `missing_gates`: every O9 metric except `gmat_rows` and `mass_samples_compared` must have a limit, or the comparison is rejected (exit 2), as the Proof's coverage check already required.
- **Test:** `test_standalone_compare_fails_closed_without_thresholds`.

### F7: the gate-disable claim was incorrect (Low)
**Implementer reasoning:** Correct. The claim in VAL-0014 was not verified for every gate.  
**Fix:**
- Each of the 15 gated O9 metrics has its own targeted corruption test (`test_each_reference_metric_fails_on_its_corruption`, `test_each_simulator_metric_fails_on_its_corruption`). A meta-test (`test_every_o9_metric_has_a_targeted_test`) pins the coverage.
- A harness then disabled each of the 15 metrics in turn, and the F1, F3, F5 and F6 checks: **every one fails a test**.
- The F2 duplicate-assignment guard alone does not, because the position-preserving comparison also rejects duplicates. It is defense in depth and now has its own unit test.
- VAL-0014 is corrected.

## References regenerated (recorded)
- The three references were regenerated through the new staged `run` with the reason recorded in the metadata and the manifest.
- **The reports are byte-identical:** same sha256 as `1de827e`. Only the metadata (new provenance fields) and the console logs (timings) changed.

## Re-verification 1
**Reviewer:** Codex, session `01a12cfd-1fe9-7ca3-b2d8-4795a952eae5`, at `94f0e75`. **Raw:** `raw/M2-T6-codex-reverify.md`, `raw/M2-T6-codex-reverify-scratch/`.

**Verdict: FAIL.**
- F2, F6 and F7 are resolved. F1, F3, F4 and F5 are partly resolved; their remainders are F8–F13 below.
- Confirmed:
  - 890 tests, a 212-check Proof and all M1 gates pass;
  - all 18 row mutations are rejected;
  - the three reports are byte-identical to `1de827e` (git history);
  - the installed GMAT matches the approved digest, and its three real reproductions passed;
  - no T5 loosening; 30 µm is above the floor; DR-0017 and DR-0018 are separate; no T7 scope.

**All six are `ACCEPTED`.** Each fix is mutation-tested: disabling it makes its tests fail.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F8 | Med | Metadata and manifest history not bound | The manifest binds the metadata digest as well. The history must be well formed, and this reference's latest record must equal its metadata (time, revision, reason, report digest). The revision must be non-null and the timestamp plausible | `test_metadata_and_history_are_bound_to_the_manifest` (metadata, host field bound only by the digest, history) |
| F9 | Med | Interrupted publication left an accepted partial replacement | `_publish`: (1) withdraw the mission's approval atomically; (2) replace each artifact atomically (temp file + rename); (3) publish the new manifest last. With the metadata digest bound (F8), a partial set is rejected either way; withdraw-first is defense in depth and is pinned | `test_interrupted_publication_never_leaves_an_accepted_mix` (interruption at each of 7 steps) |
| F10 | Med | Reproduction did not authenticate the executable | `is_approved_console` (sha256 = the pinned approved binary). The reproduction test requires it, plus GMAT's success marker. It is described as independent reproducibility evidence that cannot by itself prove the historical origin of stored bytes | `test_unapproved_executables_are_not_authenticated`; `test_gmat_reproduces_the_committed_report` |
| F11 | Med | `generate` followed symlinks into the references | Refuses symlinked or protected destinations; writes a temporary file and renames it over the entry | `test_generate_refuses_symlinks_into_the_references` |
| F12 | Med | Standalone evaluation ignored the T5 audit's numerical failures | Every audit metric group is gated with the T5 thresholds, failing closed on missing limits. The report-only rule moved to `tars.validation.m2.ungated_metrics`, shared with `m2_proof.py` (no behavior change there) | `test_standalone_evaluation_applies_the_audit_gates` (thrust acceleration, sensed Δv) |
| F13 | Low | Boundary coverage ignored same-tick reporting | Inclusion by `_expected_report_tick` (same-tick submission → k + 1). A valid scenario cannot stop at its own submission tick, so the case is exercised at the function level | `test_coverage_uses_the_same_tick_report_rule` |

**Test defect found while verifying F8.**
- The first version of the F8 test copied, in its second iteration, the references from the directory already patched by the first iteration, so the history case inherited the metadata tampering. It also edited another mission's history record.
- Fixed: the cases are parametrized separately, each history probe edits only the record under test, and a digest-only field probe was added. Each mechanism now has a test that fails without it.

**References regenerated** (third recorded replacement, so the manifest binds the metadata digest): the reports are byte-identical to `1de827e`.

## Re-verification 2
**Reviewer:** Codex, session `01a12d16-04c0-7ee3-8ef6-ebc862ffd697`, at `2d33617`. **Raw:** `raw/M2-T6-codex-reverify2.md`, `raw/M2-T6-codex-reverify2-scratch/`.

**Verdict: FAIL.**
- F9, F10, F11, F12 and F13 are resolved. F8 is partly resolved; its remainder is F14.
- Disabling each fix fails its targeted tests.
- All gates passed, and the reports are byte-identical to `1de827e`.

**Both findings are `ACCEPTED`.** Each fix is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F14 | Med | Older history records unchecked: they could be corrupted, invented or deleted; the README count was wrong | Every record is validated (GMAT mission, plausible UTC time, non-null revision, reason, digest). Records are in chronological order and hash-chained (`previous_record_sha256`). The history was **reconstructed from the committed metadata of all four generations** (12 records). Documented limit: a consistent wholesale re-chain is visible only in version control. README and VAL-0014 corrected | `test_every_history_record_is_validated` (8 cases; value probes re-chain so only the rule under test can fire); `test_wholesale_history_rewrite_is_the_documented_limit` |
| F15 | Med | A non-finite limit (`1e999` → inf) silently disabled a gate | Both threshold loaders (`load_thresholds` for M1, `load_scoped_thresholds` for M2) require every non-null limit to be a finite, nonnegative number. The committed `m1.json` and `m2.json` load unchanged; no M1 value or gating result changes | `test_threshold_loaders_reject_non_finite_or_negative_limits` (1e999, −1, NaN, string; both loaders); `test_committed_thresholds_load` |

**Test-design note.** The first F14 value probes were also caught by the chain, so disabling a single value rule went unnoticed. Each probe now re-chains after its edit, and the reordering probe keeps every mission's latest record. Each rule fails a test when disabled.

## Re-verification 3
**Reviewer:** Codex, session `01a12d2b-4bf2-74b0-ba58-8580531a3369`, at `4cd3669`. **Raw:** `raw/M2-T6-codex-reverify3.md`, `raw/M2-T6-codex-reverify3-scratch/`.

**Verdict: FAIL** (F16 is a numerical false pass).
- F14 is resolved: all 12 history records match the committed metadata, and the documented re-chain limit is honest and reproduced.
- F15's original exploit is resolved; object-valued limits remain (F17).
- All gates passed: 919 tests, 212/212 Proof, 18 row mutations and 47 threshold deletions rejected, reports byte-identical to `1de827e`.

**Both findings are `ACCEPTED`.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F16 | Med | A NaN intermediate DOP853 state passed O9, and the same pattern existed in T5's O4. Python's `max(x, nan)` returns `x` | `tars.validation.m2.worst()` turns NaN into +inf. It is used for every reference-dependent reduction in O9 (alignment, GMAT vs DOP853, ours vs GMAT) and, **as a documented T5 correction**, in O4 and O5. O9 and O4 also reject any non-finite reference component, including ones they do not reduce. `dop853_reference` raises on a non-finite integration. For finite inputs `worst` equals `max`: all 212 Proof metric values are bit-identical before and after | `test_worst_never_discards_nan`, `test_nan_reference_state_fails_o9`, `…_fails_o4`, `…_fails_the_integrated_proof`, `test_nan_in_an_unreduced_reference_component_fails_o9`, `test_dop853_reference_rejects_non_finite_integration` |
| F17 | Low | Object-valued limits accepted, causing a later crash | Both loaders validate the exact nesting (M1 group → metric; M2 group → scope → metric), then each leaf | `test_threshold_loaders_reject_object_limits`, `test_threshold_loaders_reject_a_wrong_structure` |

**Self-found while verifying F16 (T5 report naming).**
- Two different checks were named `orbit_events[…]`: the exact orbit-event contract check and the numerical orbit gate.
- Both were always evaluated, but the report had duplicate validator names. The contract check is now `orbit_events_contract[…]`; the report has 212 unique names (`test_audit_check_names_are_unique`).

## Re-verification 4
**Reviewer:** Codex, session `01a12d3d-a2b3-75b1-88e6-de9ca76d39b4`, at `7467d42`. **Raw:** `raw/M2-T6-codex-reverify4.md`, `raw/M2-T6-codex-reverify4-scratch/`.

**Verdict: FAIL.**
- F16 is resolved for intermediate states; dense output remains (F18). F17 is resolved.
- Disabling each of the 8 mechanisms fails its test.
- The T5 corrections preserve behavior: **all 773 scalar metric values across 212 checks are bit-identical**, with thresholds, statuses and results unchanged.
- O9 rejects all 21 reference-component NaN/±inf mutations, and O5 rejects NaN Kepler outputs.

**Both findings are `ACCEPTED`.** Instead of closing only the two flagged reductions, every remaining accumulator was swept:

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F18 | Med | Non-finite DOP853 dense output silently passed (altitude extrema) | Dense-output altitudes are validated at the source (`dop853_reference` raises); the extrema use `worst` | `test_dense_output_must_be_finite` |
| F19 | Med | `_merge_audits` used builtin `max`, so an auxiliary NaN disappeared | The merge uses `m2.worst` | `test_merging_auxiliary_audits_keeps_nan` (both orders), `test_nan_in_an_auxiliary_audit_fails_the_mission` (the real dt = 2.5 s auxiliary audit, O4 and O5) |
| sweep | — | Remaining builtin `max`/`min` accumulators in T5/T6 validators (O1, O2, O3, O6, O7, O8, accounting, plans, transitions, samples, orbit and node errors) | All use `worst` (now variadic) or `worst_of` (NaN-safe over an iterable). A static guard fails if a builtin `max`/`min` accumulator reappears | `test_worst_of_never_discards_nan`, `test_no_builtin_max_or_min_accumulators_in_the_validators` |

**Behavior is preserved.** The regenerated M2 Proof report is identical to the previous one (validator names, every metric and every result) across 212 checks. Each mechanism is mutation-tested: reverting the merge, the dense-output check, or any accumulator fails a test.

## Re-verification 5
**Reviewer:** Codex, session `01a12d4e-3dfd-7c02-950e-b0700971a7fd`, at `97071e6`. **Raw:** `raw/M2-T6-codex-reverify5.md`, `raw/M2-T6-codex-reverify5-scratch/`.

**Verdict: FAIL** (F20, F22; F21 weakens regression protection).
- F18 is resolved, and F19 is resolved for NaN.
- The Proof report is identical to the previous one: 773 metric bits across 212 checks.
- All 21 reference-component, 18 row and 47 threshold-deletion mutations are rejected.

**All three are `ACCEPTED`.** This round fixes the non-finite class at its root rather than one site at a time:

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F20 | Med | `-inf` passed: `worst` discarded it beside finite values, and `Check` accepted an unreduced `-inf` below an upper limit | **`Check` rejects every non-finite gated metric** (NaN, +inf, −inf). It is the last gate every metric passes through, M1 included, and M1 results are unchanged because its metrics are finite. `worst`/`worst_of` turn any non-finite value into +inf. The merge no longer uses a −inf sentinel | `test_non_finite_gated_metrics_fail_every_check`, `test_worst_rejects_negative_infinity`, `test_merging_keeps_negative_infinity_as_failure`, `test_o9_rejects_a_negative_infinity_metric`, `test_nan_in_an_auxiliary_audit_fails_the_mission[-inf]` |
| F21 | Low | The regex guard missed the original F19 expression and other common forms | An **AST scan** of all five validation files (`m2.py`, `gmat_m2.py`, `m2_proof.py`, the `gmat_m2` CLI, `thresholds.py`) for max/min-style calls (`max`, `min`, `.max()`, `.min()`, `nanmax`, `nanmin`, `amax`, `amin`, `fmax`, `fmin`). The set must equal a **reviewed allowlist of 16 calls**, each with its reason (scenario inputs, values already validated finite, results passed through `worst`, exit codes) | `test_every_max_min_call_in_the_validators_is_reviewed`, `test_the_guard_detects_common_unsafe_forms` (5 forms, including the original F19 expression) |
| F22 | Med | Node bisection compared unchecked Kepler output with zero (T5 and O9) | Every propagated value is checked. A non-finite one ends the bisection with an +inf crossing, so the timing error is +inf and the gate fails | `test_node_bisection_rejects_non_finite_oracle_output` (NaN, ±inf; O9 and T5), `test_poisoned_node_oracle_fails_the_integrated_mission` |

**Behavior is preserved:** the regenerated M2 Proof report is identical (212 checks, every metric and result). Each mechanism is mutation-tested: disabling it fails its tests, and a new unreviewed `max(...)` call fails the AST guard.

## Re-verification 6
**Reviewer:** Codex, session `01a12d5e-ecac-78e0-9681-71ba431dddda`, at `e9e06aa`. **Raw:** `raw/M2-T6-codex-reverify6.md`, `raw/M2-T6-codex-reverify6-scratch/`.

**Verdict: FAIL** (F23; F24 and F25 weaken regression protection).
- F20 is resolved. F21 and F22 are resolved for the forms they covered.
- 773 metric bits across 212 checks are identical; all mutation families are rejected.

**All three are `ACCEPTED`**, together with two review notes.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F23 | Med | An infinite Simpson allowance turned a failing error into 0: `max(err - inf, 0.0)` | `excess_over(err, allowance)` returns +inf unless both inputs are finite. Both O2 and per-sample sites use it, and the allowlist entry and justification are corrected | `test_excess_over_rejects_non_finite_inputs`, `test_infinite_simpson_allowance_cannot_hide_an_error` (normal and infinite allowance, +1e-6 m/s), `test_infinite_simpson_allowance_fails_the_integrated_mission` |
| F24 | Low | The AST guard missed NumPy ufunc reductions (`np.fmax.reduce`, …) | `.reduce`, `.accumulate`, `.reduceat`, `.outer` and `.at` resolve to their ufunc; `maximum` and `minimum` are covered | `test_the_guard_detects_common_unsafe_forms` (10 forms, including `np.fmax.reduce([dst.get(k, -math.inf), x])`) |
| F25 | Low | The integrated node test survived disabling its fix (misaligned global call counting) | Poisons only the last bisection step of each crossing, counted **per calling validator**, and asserts both node metrics are +inf. Disabling either check fails it | `test_poisoned_node_oracle_fails_the_integrated_mission` |
| note | — | Report-only metrics could be non-finite | New exact check `report_only_metrics_finite` in `m2_proof.py`; standalone O9 rejects any non-finite metric | `test_report_only_metrics_must_be_finite` |
| note | — | Bisection validated only the consumed z | The whole propagated r and v must be finite | (node tests) |

**Behavior is preserved.** All 212 previous checks are identical; the Proof now has 213 checks (`report_only_metrics_finite` added). Each mechanism is mutation-tested.

## Re-verification 7
**Reviewer:** Codex, session `01a12d76-2ae3-7092-9f1c-f2cbce1e39b3`, at `d7d77ae`. **Raw:** `raw/M2-T6-codex-reverify7.md`, `raw/M2-T6-codex-reverify7-scratch/`.

**Verdict: FAIL** (F26).
- F23, F24 (for the reported forms) and F25 are resolved.
- 773 metric bits across the 212 previous checks are identical.

**All three are `ACCEPTED` and fixed.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F26 | Med | An infinite depletion bound (patched `_ulp`) turned a failing residual ratio into 0 | The ratio is computed only against a finite, positive bound; otherwise it is +inf | `test_depletion_ratio_needs_a_finite_positive_bound` (normal, ±inf, 0), `test_infinite_depletion_bound_fails_the_integrated_mission` |
| F27 | Low | An aliased reducer (`from numpy import fmax as reducer`) bypassed the AST guard | The guard flags importing a reducer at all, and binding one to a name (`reducer = np.fmax`, `reducer = max`) | `test_the_guard_detects_common_unsafe_forms` (13 forms) |
| F28 | Low | Standalone O9 accepted non-finite T5 report-only audit metrics, and the terminal Proof check's wiring was untested | Standalone evaluation rejects any non-finite audit metric. **Self-found while testing this:** a non-finite metric made `m2_proof.py` crash while writing its report (the event schema requires finite numbers). It now writes the check as a failure with the values in its notes, so the report is always written | `test_standalone_evaluation_rejects_non_finite_report_only_audit_metrics`, `test_report_only_finiteness_is_a_terminal_proof_check` (`main` exits 1 with the check failed) |

**Pattern escalated (DR-0019).**
- Re-verifications 3–7 found, in each round, new instances of one open-ended class: a validator-internal helper patched to return a non-finite value, which downstream arithmetic turns into a finite pass.
- The terminal gates now reject any non-finite metric. What remains requires editing the validator's own code.
- The implementer does not decide the review's scope: DR-0019 asks the Tech Lead to define the threat model before the final round. **Round 8 has not been launched.**

**DR-0019 approved, option B (Tech Lead, 2026-10-11).**
- **In scope:** wrong simulator output or physics; tampered GMAT references or threshold files; workflow failures; invalid independent-reference outputs; missing observations or thresholds; any non-finite metric at the validation or Proof boundaries.
- **Out of scope:** replacing or modifying the validator's own helper implementations.
- **Constraint:** bad data must never pass by travelling through an (unmodified) internal helper.
- Findings F16, F18–F20, F22, F23 and F26 were reported under the earlier, open scope. All are fixed regardless and remain tested.

## Re-verification 8 (under DR-0019 B)
**Reviewer:** Codex, session `01a12dd5-9a4c-76e3-b509-c4b309ec186e`, at `6a03e1b`. **Raw:** `raw/M2-T6-codex-reverify8.md`, `raw/M2-T6-codex-reverify8-scratch/`.

**Verdict: FAIL.**
- F26–F28 are resolved, and the report is identical (212 checks, 773 metric bits).
- The reviewer stated, for each finding, why it is in scope under DR-0019 B. Each corrupts **data** (reference outputs, the manifest, the threshold file) while leaving validator code unmodified.

**All five are `ACCEPTED`.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F33 | **High** | Finite threshold inflation (1e100) let the thrust mutant (47.7 m error) pass; nothing authenticated the values | **Approval anchors** in reviewed source (`tars.validation.approved_digests`). Both loaders authenticate the file content by sha256 by default (`m1.json` approved, `m2.json` provisional), wherever it is read from. A legitimate change (for example the T7 threshold DR) must update the pin in the same reviewed commit. Only tests of malformed files opt out (`authenticate=False`) | `test_threshold_files_are_authenticated` (M1, M2, redirected reads), `test_inflated_thresholds_cannot_pass_wrong_physics`, `test_pinned_digests_match_the_committed_files` |
| F29 | Med | DOP853 dense output: only the altitude was validated | The **complete** dense-output state (r, v, m) is validated at the source, including the propellant mass law | `test_dense_output_state_is_validated_completely` (4 components × NaN/±inf) |
| F30 | Med | GMAT coast alignment discarded Kepler's velocity unchecked | Every Kepler consumer (O5, O6, GMAT alignment) uses `kepler_state`: a non-finite r or v becomes +inf in every component. Bisection already checks both | `test_gmat_coast_alignment_checks_kepler_velocity` |
| F31 | Med | Negative DOP853 propellant passed (the component was unused) | Every reference state (terminal and dense) must have propellant ≥ 0 and on the analytic mass law within the O1 round-off class (1e-12 of the initial mass; measured 5.7e-14 kg) | `test_reference_propellant_must_follow_the_mass_law` (−1 kg, off-law) |
| F32 | Med | A wholesale re-chained manifest history passed: the chain cannot authenticate itself | The manifest digest is pinned in reviewed source and checked whenever the committed references are evaluated, wherever `reference_dir` points. `run` validates a staged reference without the pin, then prints the digest that must be pinned in a reviewed change. The earlier documented limit (F14) is **closed** | `test_wholesale_history_rewrite_is_rejected_by_the_anchor`; the interrupted-publication test now expects a complete new generation to be rejected until it is pinned |

**Behavior is preserved:** the 212 previous checks are identical, 213 checks pass, and 989 tests pass. The M1 threshold file is byte-identical to `main`, so its pin authenticates exactly the approved file.

## Re-verification 9 (under DR-0019 B)
**Reviewer:** Codex, session `01a12df8-d7f5-70b3-a265-e51e434ea892`, at `1270b09`. **Raw:** `raw/M2-T6-codex-reverify9.md`, `raw/M2-T6-codex-reverify9-scratch/`.

**Verdict: FAIL.**
- F29–F33 are resolved; disabling their mechanisms causes 12, 3, 2, 1 and 2 regression failures.
- The 212 prior check records are bit-identical.

**All four are `ACCEPTED`** (all in scope: corrupted reference or summary data, validator code unmodified). F35 and F36 share a pattern: a reference output component checked only for finiteness, then unused. It is closed generally.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F34 | Med | A NaN solver time made the reference mass-law comparison NaN, which passed | Solver times must be finite, strictly increasing and exactly `[a, b]`; the mass-law comparison is NaN-safe | `test_nan_solver_time_cannot_hide_off_law_propellant`, `test_reference_mass_law_check_is_nan_safe` (uses a predicted burn, so a NaN time gives a NaN expectation) |
| F35 | Med | Finite but wrong dense velocities passed (unused after the finiteness check) | Dense velocity must equal the central difference of the dense position (relative 1e-8; measured 2.6e-10), and the dense state at the segment end must equal the terminal state | `test_dense_output_must_be_self_consistent` (zero velocity; shifted positions) |
| F36 | Med | A finite but wrong Kepler coast velocity passed GMAT alignment | **Every Kepler output** (O5, O6, GMAT alignment, both node bisections) goes through `kepler_state`, which requires two-body energy and the angular-momentum vector to be conserved (relative 1e-12; measured 9e-16). GMAT coast **velocity** is now also gated against Kepler: new metric `coast_vs_kepler_velocity_error_max_mps`, provisional limit 1e-7 m/s (the approved M1 GMAT-vs-Kepler velocity limit; measured 1.8–4.6e-9) | `test_kepler_outputs_must_conserve_two_body_invariants`, `test_gmat_coast_velocity_is_gated`, the targeted per-metric corruption (meta-test updated) |
| F37 | Med | The CLI summary's `unsubmitted_command_ids` was never reconciled | Must be present and equal the timeline entries after the submission boundary, in order | `test_cli_summary_is_reconciled_with_events` (accepted IDs, invented IDs, null, missing) |

**First use of the approval anchor.**
- The new O9 limit changed `proof/thresholds/m2.json`, so its pinned digest in `approved_digests.py` was updated in the same commit, the procedure the anchor requires.
- Existing O9 metric values are unchanged; the three O9 checks gain the new metric, all passing.

## Re-verification 10 (under DR-0019 B)
**Reviewer:** Codex, session `01a12e18-6e2c-7ff0-8082-288130e96c22`, at `b3a76eb`. **Raw:** `raw/M2-T6-codex-reverify10.md`, `raw/M2-T6-codex-reverify10-scratch/`.

**Verdict: FAIL.**
- F34–F37 are resolved (disabling them gives 2, 2, 1, 1 and 1 failures).
- The fresh 213-check report matches exactly. The three new coast-velocity metrics are 4.6e-9, 1.8e-9 and 4.5e-9 m/s against 1e-7 m/s.

**All four are `ACCEPTED`.**
- **Implementer note on F38–F40.** Each corruption left the checked quantity unchanged:
  - the O6 SMA is invariant to negating both r and v;
  - the altitude extrema depend only on |r|;
  - interior solver nodes were never consumed.

  None could have changed a verdict. They are closed anyway with general consistency checks rather than argued away.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F38 | Med | A Kepler output on the wrong side of the orbit passed: invariants do not fix the phase | `kepler_state` also requires a **round trip**: propagating the result by −Δt must recover the input state (relative 1e-10; measured 8.1e-14) | `test_kepler_output_on_the_wrong_side_of_the_orbit_is_rejected` |
| F39 | Med | Interior dense states could be corrupted with the endpoints kept; derivative-stencil components were unchecked | The dense interpolant must reproduce **every solver node** (relative 1e-12; measured 0), and every component of every stencil evaluation must be finite | `test_interior_dense_corruption_is_rejected`, `test_non_finite_stencil_evaluations_are_rejected` |
| F40 | Med | Negated interior solver nodes passed (unused) | Covered by the node reconciliation above | `test_interior_solver_node_corruption_is_rejected` |
| F41 | Med | A no-propulsion CLI summary could claim fuel and an active engine | Every final propulsion field must be present. Without propulsion they must be exactly empty (null, null, null, null, []) | `test_no_propulsion_cli_summary_must_be_empty` (5 fields: wrong and missing) |

- **Mutation tests.** Each mechanism fails its tests when disabled. A first mutation of the node check was itself wrong (it made the check always raise); it was redone by removing the `raise`.
- **Documentation.** The VAL-0014 metric count is corrected (16 gated O9 metrics since F36).
- **Results.** 1 005 tests pass; the M2 Proof report is identical to `b3a76eb` (213 checks).

## Re-verification 11 (under DR-0019 B)
**Reviewer:** Codex, session `01a12e30-3e5c-7023-98e3-4a5e4be213df`, at `1a11ff7`. **Raw:** `raw/M2-T6-codex-reverify11.md`, `raw/M2-T6-codex-reverify11-scratch/`.

**Verdict: FAIL.**
- F41 is resolved; F38–F40 are partly resolved (remainders F42–F45).
- The fresh 213-check report is identical. All other corruption sweeps are rejected.

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| F42 | Med | Kepler output negated in both directions (the round trip cancels) | **`ESCALATED_FOR_INVESTIGATION`** to the Tech Lead as **DR-0020**. The corruption cannot change any verdict (O6 consumes only the SMA, which is invariant), and detecting it needs a second independent propagator (a regress) |
| F43 | Med | Interior solver nodes and dense output negated consistently | **`ESCALATED_FOR_INVESTIGATION`** (DR-0020). Interior nodes are unused, the altitude extrema consume only \|r\|, and every consumed state is exact; detecting it needs a second integrator |
| F44 | Med | Finite but wrong velocity or propellant at the stencil points | **`ACCEPTED`, fixed.** Stencil points are kept inside the segment, and their states must be finite and on the mass law. Their velocity must be continuous with the tick's (relative 1e-5). The central difference is taken about the stencil midpoint, which is also validated. Tests: `test_finite_invalid_stencil_states_are_rejected` (velocity-only and propellant-only probes, each pinning its own check) |
| F45 | Med | Solver-node reconciliation skipped on segments without telemetry ticks | **`ACCEPTED`, fixed.** `_check_solver_nodes` runs for every segment. Test: `test_solver_nodes_are_reconciled_on_tickless_segments` |
| F46 | Med | A staged GMAT report shifted by one day passed (epoch never anchored) | **`ACCEPTED`, fixed.** The first row's A.1 MJD must equal the configured TT epoch converted to A.1 (TT − A.1 = 32.184 − 0.0343817 s) within 1 µs; the committed references match exactly. Tests: `test_time_shifted_staged_report_is_rejected`, `test_epoch_anchor_matches_the_committed_references` |

**Report preserved:** the M2 Proof report is identical (213 checks). Each F44–F46 mechanism fails its test when disabled. **Round 12 has not been launched; it waits for DR-0020.**

## Residual risk accepted under DR-0020 (Tech Lead, 2026-10-11)
DR-0020 was approved as option A, with conditions. Under it, a reference-output finding is blocking only if the corruption could affect a validation check, a reported value, an acceptance decision or an explicitly required physical invariant. F42 and F43 are **not fixed**; their residual risk is **accepted** and recorded here.

| Finding | Mutation mechanism | Why it cannot affect the current validation contract | Residual risk accepted |
|---|---|---|---|
| **F42** | Every Kepler return in the O6 midpoint propagation, forward and in the −Δt round trip, has r and v negated. The round trip then cancels, and the two-body invariants are preserved | O6 consumes only the semi-major axis after the midpoint impulse. Negating r and v preserves \|v\| and \|r\|, so the energy and the SMA are unchanged, and every O6 metric is identical. Every other Kepler consumer compares Kepler's output with another independent state, so a negated output would fail there: O5 against simulator samples, GMAT coast alignment against GMAT rows, and the node bisection's crossing times against the simulator's | A Kepler phase error consistent across forward and backward calls, in a quantity no check consumes. Detecting it needs a second independent propagator, and the same question applies to that one |
| **F43** | Interior DOP853 solver nodes and the dense output are negated together, consistently, keeping the segment endpoints and the propellant. Node reconciliation and the derivative check stay self-consistent | The interior solver nodes are unused. The dense output feeds only the altitude extrema, which depend on \|r\| and are unchanged. Every consumed state (segment ends, all marks, all comparisons) is the exact, unchanged integrator state | Internally inconsistent values inside one reference's internal representation, consumed by no check. Detecting it needs a second independent integrator, with the same regress |

**Unused intermediate values, named for DR-0020 condition 4.** They must be validated before any of them is relied on:
- DOP853 interior solver nodes (`sol.y[:, 1:-1]`);
- dense-output velocity and propellant at telemetry ticks (beyond the existing consistency checks);
- dense-output positions except through \|r\| (superseded by F49: the full position vector at every tick is now consumed by the anchor reconciliation);
- Kepler output beyond the quantities each consumer compares;
- the GMAT epoch column (used only for spacing and the epoch anchor).

**Amendment after F49 (round 14 note).** F43's rationale above describes the contract before F49. Since F49, the DOP853 dense positions at the ticks are consumed as full vectors by the anchor reconciliation, and F43's exact mutation (interior nodes and dense output negated) is now **rejected**: the reviewer re-ran it in round 14. F43 stays recorded as accepted residual risk for its mechanism; it is not marked fixed by this note.

**Preserved (DR-0020 condition 3).**
- No check, threshold or test was removed or weakened.
- All existing checks stay enforced: finite values, physical consistency (two-body invariants, Kepler round trip, solver-node reconciliation, dense self-consistency), the mass law, GMAT and DOP853.

## Re-verification 12 (under DR-0019 B and DR-0020 A)
**Reviewer:** Codex, session `01a12e64-2402-7002-871c-524bd30c03c9`, at `d36c4c4`. **Raw:** `raw/M2-T6-codex-reverify12.md`, `raw/M2-T6-codex-reverify12-scratch/`.

**Verdict: FAIL** (F47, F48; both blocking under DR-0020 A).
- F42 and F43 are accurately recorded as accepted residual risk; the reviewer confirms the relevance analysis for those mechanisms.
- F44–F46 are resolved. The fresh 213-check report is identical.

**Both are `ACCEPTED`.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F47 | Med | A consistent interior corruption of DOP853 nodes and dense output (a translation, or r and v scaled together) changed the **consumed** radii of the altitude extrema. It reversed an acceptance: a 0.1 m overstated maximum altitude passed | **The extrema no longer consume DOP853 dense output.** Every segment end is **anchored independently of SciPy**: on coasts to validated Kepler from the segment start (≤ 1e-7 m and 1e-10 m/s; measured 2.9e-9 m and 2.9e-12 m/s); during burns to a fixed-step RK4 written in the validator (h = 0.01 s; ≤ 1e-6 m, 1e-9 m/s and 1e-9 kg; measured 3.8e-8 m, 1.1e-10 m/s and 1.5e-10 kg). The tick radii come from those anchors. Each segment must also start exactly at the requested state. The dense checks remain (DR-0020 condition 3) | `test_dense_radii_corruption_cannot_change_the_extrema`, `test_overstated_altitude_stays_rejected_under_reference_corruption` (the reversal case), `test_segment_end_corruption_is_rejected_by_the_anchor`, `test_burn_segment_end_is_anchored_to_the_independent_rk4`, `test_segment_must_start_at_the_requested_state` |
| F48 | Med | Finite 1e200 velocities overflowed the norms, and `inf <= tol·inf` passed the derivative check | `within(err, bound)` requires err and bound finite and err ≤ bound. It is used for every reference tolerance comparison (nodes, dense derivative, stencil, terminal, anchors) | `test_overflowing_finite_velocities_are_rejected` |

**Report change (documented).** Only the altitude-extrema metrics change, because they now come from the anchors instead of the DOP853 interpolant: `min_altitude_error_m` and `max_altitude_error_m` in the orbit_events checks, by at most 2.0e-8 m. Every check still passes, and every other metric is identical.

**Test design.** The first F47 probes were caught by other checks (the derivative stencil, node reconciliation), so the anchors were not pinned. The probes now corrupt only what each anchor alone can see: radii at exact interior ticks, a consistent shift after the segment start, and a moved start node.

**Runtime.** The full M2 Proof now takes about 114 s, because of per-tick Kepler anchoring with round trips.

## Re-verification 13 (under DR-0019 B and DR-0020 A)
**Reviewer:** Codex, session `01a12e99-e8c0-7fa1-b240-85492b7ff544`, at `1017c55`. **Raw:** `raw/M2-T6-codex-reverify13.md`, `raw/M2-T6-codex-reverify13-scratch/`.

**Verdict: FAIL** (F49, blocking under DR-0020 A).
- F42 and F43 remain accepted residual risk; the reviewer reconfirms the relevance analysis.
- F44–F48 are resolved. Disabling each F47/F48 mechanism fails its targeted tests.
- All eight required commands pass (1,016 tests). The fresh 213-check report is identical to `1017c55`'s.

**`ACCEPTED`.** The F47 fix made the anchor's tick positions a **consumed** value (the altitude extrema), and DR-0020 condition 4 requires validating such a value before relying on it. Only the segment-end anchor call was reconciled.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F49 | Med | Kepler tick states returned at 1.001 × the requested time of flight keep the energy, the angular momentum and the round trip. They changed `max_altitude_error_m` and reversed an acceptance (0.01301 m > 0.013 m clean; ≈ 0.012976 m corrupted) | **Every consumed anchor tick is reconciled with the validated DOP853 dense output** at the same tick, with the anchor limits: ≤ 1e-7 m on coasts and ≤ 1e-6 m during burns (measured maxima 2.8e-8 m over 15,362 coast segments and 2.4e-8 m over 299 burn segments). An extremum therefore moves only if two independent references (Kepler or the in-validator RK4, and SciPy DOP853) are corrupted consistently at the same ticks | `test_kepler_tick_corruption_is_rejected`, `test_kepler_tick_corruption_cannot_reverse_acceptance`, `test_rk4_burn_tick_corruption_is_rejected` |

**Changed tests (stricter, not weaker).** `test_dense_radii_corruption_cannot_change_the_extrema` and `test_overstated_altitude_stays_rejected_under_reference_corruption` corrupt the dense radii at the ticks. They previously asserted that the extrema were unchanged; that corruption is now **rejected**, and the tests assert the rejection. The clean-reference half of the reversal test is unchanged.

**Mutation.** With the F49 check disabled, all five tests above fail.

**Report.** Unchanged: the check only accepts or rejects the reference and moves no metric.

**Consumed reference quantities (inventory, updated for F49).**
- DOP853 segment-end states: the marks and every comparison. Anchored to Kepler or RK4.
- Anchor tick positions: the altitude extrema, through \|r\|. Reconciled with the DOP853 dense output (F49).
- DOP853 dense positions at the ticks: consumed only as F49's cross-check. Self-consistent (nodes, derivative, terminal).
- Kepler output in O5, O6 and the GMAT coast alignment: each compares with another independent state, except the O6 SMA (F42, accepted).

**Limit of the method (not a new acceptance).** A corruption applied consistently to **both** independent references at the same ticks would still pass. That is the regress described in DR-0020 for F42 and F43, now requiring two separate implementations to agree on the same wrong value.

## Re-verification 14 (under DR-0019 B and DR-0020 A)
**Reviewer:** Codex, session `01a12ec0-bdd9-7fd3-a011-f7658ec2be53`, at `683a224`. **Raw:** `raw/M2-T6-codex-reverify14.md`, `raw/M2-T6-codex-reverify14-scratch/`.

**Verdict: FAIL** (F50, F51).
- F44–F49 are resolved. Both F49 probes are rejected, and disabling the tick reconciliation fails five targeted tests. The revised F47 assertions are confirmed stricter.
- F42 is re-probed and remains accepted residual risk. F43's exact mutation is now rejected (by F49).
- All eight required commands pass (1,019 tests). The fresh 213-check report matches `1017c55`, except for CPU metadata.

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| F50 | Med | Kepler tick states (1.001 × flight time) and DOP853 dense positions corrupted **consistently with each other** at 17,876 ticks pass the F49 reconciliation and reverse an acceptance: 0.01301 m rejected with clean references, 0.012976 m accepted | **`ESCALATED_FOR_INVESTIGATION`** (DR-0021). This is the two-reference regress that DR-0020 named for its option B. Fixing this instance (tick continuity against the stencil) adds another reference for the next consistent corruption to target |
| F51 | Med | O6 midpoint Kepler returns at 10 × the flight time, forward and in the round trip, keep the invariants and the round trip but change the reported and gated O6 values; every check still passes | **`ESCALATED_FOR_INVESTIGATION`** (DR-0021). Fixable by a DOP853 cross-check of the midpoint (in scope under every DR-0021 option); not started, because option A would cover it differently |
| note | — | Stale docs: the F43 rationale and unused-value inventory after F49; the VAL-0014 epoch-column description omitted the F46 anchor | **`ACCEPTED`, fixed.** An amendment note under "Residual risk accepted under DR-0020" (F43 stays accepted residual risk, not marked fixed); the inventory line marked superseded; VAL-0014 now describes the epoch anchor |

**T6 is blocked on DR-0021.** No further review round runs until it is decided.


## DR-0021 implementation (approved option A with conditions, 2026-10-12)
F50 and F51 were escalated to DR-0021. The Tech Lead approved option A: an approved reference snapshot. Their disposition is now **`ACCEPTED`, fixed by the snapshot**. Record: VAL-0015; artifact `toolbox/references/snapshot/m2/` (baseline 1).

| Condition | Implementation | Evidence |
|---|---|---|
| 1. Complete coverage | Every reference oracle output passes through `reference_snapshot.pin`: initial state, predicted burns, Simpson and DR-0017 bounds, DOP853 bounds, ticks, start, segment ends, anchor ticks and ends, extrema, node crossings, O5 and O6 Kepler, O3 closed forms, O9 arcs, labels, epoch, expected mass, alignment Kepler and GMAT node crossings. Inventory and seven explicit exclusions with reasons in VAL-0015 | 48,279 records, 920,849 values; coverage is complete per entrypoint (every approved value must be reproduced) |
| 2. Independent baseline | Generated at `ad1c33b` from a clean tree (environment, `uv.lock` and Proof report digests recorded); the recording run passed the Proof and the GMAT evaluations; `verify-baseline` checks the snapshot's own values against the committed GMAT rows and the physical invariants | DOP853 vs GMAT ≤ 4.66e-6 m, 5.39e-9 m/s (gates 3e-5 m, 3.5e-8 m/s); `test_approved_artifact_is_pinned_and_verified` |
| 3. Immutable baseline | sha256 `031c7e7b…e99e` pinned in `approved_digests.py`; `generate` refuses the approved path and writes candidates only; CI only measures; documented change procedure in the snapshot README | `test_generate_refuses_to_write_the_approved_artifact`, `test_only_the_tool_writes_snapshots_and_ci_only_measures`, `test_tampered_artifact_is_rejected` |
| 4. Measured tolerance | Verify-mode deviations measured on 9 environments; 10× the maximum, rounded up to 1-2-5; ref/gmat values consumed from the snapshot (a within-tolerance deviation moves no metric); sim-seeded gates must keep a margin larger than the worst within-tolerance shift (`reference_snapshot_margins`) | VAL-0015 table; O6 margin 0.0405 against 0.05 |
| 5. No circularity | Verification reads the committed, authenticated artifact; nothing regenerates it in a test or a run | coordinated Kepler + DOP853 tests below |
| 6. F50, F51 regressions | `test_f50_acceptance_flip_is_rejected` (clean: rejected on the limit; coordinated corruption: rejected by the snapshot); `test_f51_wrong_time_kepler_in_o6_is_rejected`; `test_joint_corruption_defeats_the_runtime_checks_without_the_snapshot`; `test_coordinated_radial_shift_of_both_references_is_rejected` | each fails when the tolerance comparison is disabled |
| 7. Existing gates | No check, threshold or test removed or weakened; the two new exact checks are additions | M2 report: the 213 previous checks are byte-identical, plus `reference_snapshot` and `reference_snapshot_margins` (215) |

**Mutation results.** Disabling each mechanism fails its targeted tests:

| Mechanism disabled | Failing tests |
|---|---|
| Tolerance comparison | 9, including F50, F51 and the coordinated shift |
| Substitution | 1 |
| Coverage | 2 |
| Authentication | 1 |
| Margin check | 1 |
| Unexpected-key check | 1 |
| Kind check | 3 |

**Design notes.**
- The tick grid is pinned exactly as an index range plus dt. The runtime grid must be k·dt bit for bit.
- DOP853 dense tick output is excluded; it is pinned transitively through F49.
- Record-mode cross-platform drift (6.8 µm) is not the tolerance basis. Verify mode restarts each segment from its approved state, and that is the behaviour measured.

**Open point for T7.** If T7 tightens `order_deviation_from_2_max` below about 0.041, the impulsive SMA needs its own measured class: the sim-seeded length tolerance is set by O5.

## Re-verification 15 (under DR-0019 B, DR-0020 A and DR-0021 A)
**Reviewer:** Codex, session `01a13192-dbc6-7f42-97ea-d016f726c136`, at `2b1e452`. **Raw:** `raw/M2-T6-codex-reverify15.md`, `raw/M2-T6-codex-reverify15-scratch/`.

**Verdict: FAIL** (F52, F53).
- F50 and F51 are resolved in runtime verification, and their regressions fail when the comparison is disabled.
- DR-0021 conditions 1, 3, 5, 6 and 7 are verified; 2 and 4 had the gaps below.
- The 215-check report keeps the 213 earlier records unchanged. All nine commands pass (1,058 tests).

**Both are `ACCEPTED`.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F52 | Med | The O5 margin used the per-component tolerance as the bound on a Euclidean norm. A Kepler state 1.6 ns late moved the vector by 12.4 µm with every component under 10 µm, and reversed O5 (0.60000100 m to 0.59998859 m) with no snapshot or margin problem | `o5_snapshot_shifts` uses √3 × the tolerance for both position and velocity. O6 is unaffected: its bound is on the scalar impulsive SMA | `test_o5_margin_uses_the_vector_norm_bound` |
| F53 | Med | `verify-baseline` did not independently check O6. A recording under F51's corruption, and zeroed O6 values with an SMA of −1e30 m, were both approved | `verify-baseline` now recomputes **every** record from its pinned inputs and the scenario, independently of the runtime references (VAL-0015 table), with a full-coverage requirement, fail-closed evaluation, and DOP853 against GMAT. The O5, O6, Simpson, DR-0017 and O3 pins now carry their inputs, so **baseline 2** is pinned (`f5a7e40`): key set identical, every common value bit-identical, five labels gained input parts | `test_baseline_verification_rejects_invalid_o6_values`, `..._wrong_time_o6_recording`, `..._an_f50_recording`, `..._each_corrupted_value` (11 kinds), `..._requires_coverage`, `..._fails_closed_on_unreadable_records`, `test_the_approved_baseline_passes_independent_verification` |

**Beyond the finding.** I extended F53's fix past O6 because the same gap covered every propagated value: a baseline recorded under F50's corruption would also have been approved. It is now rejected.

**Mutation results.** Disabling a verifier check fails its targeted tests:

| Check disabled | Failing tests |
|---|---|
| O6 Kepler | 2 |
| Segment | 1 |
| Coverage | 1 |
| Each fail-closed wrapper | 1 |

**Re-measurement.** Eight more hosts were measured against baseline 2. The maxima by class are identical, and the new flight-time parts are exact, so `sim s` is 1e-11 s by the zero-measured rule.

## Re-verification 16 (under DR-0019 B, DR-0020 A and DR-0021 A)
**Reviewer:** Codex, session `01a13291-c7ac-7140-ab84-7c3e8a4e80d5`, at `8cd661d`. **Raw:** `raw/M2-T6-codex-reverify16.md`, `raw/M2-T6-codex-reverify16-scratch/`.

**Verdict: FAIL** (F54–F57).
- F52 is resolved, and so are F53's reported O6 mechanisms. F50 and F51 are resolved with intact sessions.
- All nine commands pass (1,076 tests). The 215-check report keeps the 213 earlier records unchanged.
- Baseline 2's provenance, justification and comparison are verified (920,849 common values bit-identical).

**All four are `ACCEPTED`.** Each mechanism is mutation-tested.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F57 | High | Corrupting `Session.approved` to `None` after authentication silently skipped all comparisons and the coverage check. It restored the F50 reversal and the F51 O6 change while the Proof passed | A verify session without its authenticated ledger (never loaded, or lost after loading) reports `no authenticated reference ledger` on every pin and at finish. Records that were consumed but not compared are problems. `records_verified` counts only compared records | `test_session_without_its_ledger_fails_closed` |
| F54 | Med | `verify-baseline` checked coverage of the supplied records only. It approved changed arc steps, a powered count of 999, a renamed counter, a bogus entrypoint, removed O5 records and an unknown label | `verify-baseline` compares the candidate with a **fresh recording** of the reviewed code: records, counters, entrypoints, part names and shapes must match exactly. Verification is tracked **per part**, so every part must pass an explicit check. Arcs and steps are re-derived independently | `test_baseline_verification_requires_the_complete_inventory` (6 cases) |
| F55 | Med | Node verification checked only the supplied roots. It approved duplicated, emptied and removed crossing lists | Crossings and powered intervals are **enumerated independently** over the reference marks: count, order and times, by bisection on the independent Kepler. The marks are now pinned (`dop853.marks`, exact) → **baseline 3** | `test_baseline_verification_enumerates_node_crossings` (3 cases) |
| F56 | Med | O5 flight times ×10 (states recomputed to match) and an O3 case at 100 s passed | **Input parts** (O5 and O6 seeds and flight times, Simpson windows, DR-0017 inputs, O3 start and duration, marks) must be bit-identical to the fresh recording, where they come from the simulator and the scenario, never from a reference. O3's duration must equal the Proof's | `test_baseline_verification_rejects_wrong_o5_inputs`, `..._a_wrong_o3_case` |

**Baseline 3** (`9d49b60`, generated at `58be803` from a clean tree) adds the 31 marks records; every common value is bit-identical to baseline 2. `verify-baseline` passed at generation and standalone, against a separate fresh recording. The independent crossing enumeration reproduces every pinned crossing exactly.

**CI correction after `9917bb7`.** The bit-exact input comparison failed on CI hosts, whose simulator-seeded inputs differ within the measured tolerance. Two snapshot tests failed on both platforms. Inputs are now compared within their class's reproducibility tolerance (exact for exact records). The F56 probes stay rejected: flight times and the O3 duration are exact classes. Test: `test_inputs_are_compared_within_their_reproducibility_tolerance` (0.5× tolerance accepted, 2× rejected).

## Re-verification 17 (under DR-0019 B, DR-0020 A and DR-0021 A)
**Reviewer:** Codex, session `01a136d4-fd41-7d51-87de-00d94e7a4bda`, at `9917bb7`. **Raw:** `raw/M2-T6-codex-reverify17.md`, `raw/M2-T6-codex-reverify17-scratch/`.

**Verdict: FAIL** (F58, F59).
- F54–F57 are resolved for their reported mechanisms. All eight probes reject, and the regressions fail when their mechanisms are disabled.
- All nine commands pass (1,092 tests). The 215-check report against baseline 3 keeps the 213 earlier records unchanged.
- The inventory, per-part recomputation, provenance, 24 measurements, substitution, O5 margins and O6 corners are verified.

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| F58 | High | Editing the authenticated ledger's contents in memory, or switching the session's mode to `record`, after authentication lets the F50 reversal and the F51 O6 change pass the Proof | Escalated to DR-0022, then **`REJECTED_WITH_REASONING`** under DR-0022 B (see below). This mutates the validator's own runtime state, the same class as F57 taken further. Any in-memory guard is itself mutable, so there is no fixed point. Whether DR-0019 B's exclusion covers validator runtime state is a scope decision for the Tech Lead |
| F59 | Med | The 10-ulp floor for zero-measured time classes used 6,000 s; the pinned times reach 53,700 s (10 ulp = 7.3e-11 s), so the 1e-11 s tolerances falsely rejected deviations within the documented allowance | **`ACCEPTED`, fixed.** One uniform rule for every class: the smallest 1-2-5 value ≥ max(10 × measured, 10 ulp of the class's largest snapshot value). Time classes are 1e-10 s; `ref kg` is 5e-12 kg (10 ulp of 1,300 kg = 2.3e-12). The measured maxima are recorded in `reference_snapshot.MEASURED`. Test: `test_tolerances_follow_the_documented_rule` recomputes the rule from the artifact |

**T6 is blocked on DR-0022.** No further review round runs until it is decided.

## DR-0022 implementation (approved option B with conditions, 2026-10-13)

### F58: `REJECTED_WITH_REASONING`, not fixed
F58's mechanism has two forms. Both act after the artifact is authenticated and both need write access to the validator's own memory while it runs:
- (a) edit the in-memory ledger's values, so a corrupted reference agrees with the edited ledger;
- (b) set the session's `mode` to `record` and `approved` to `None`, which skips verification.

DR-0019 B, as clarified by DR-0022 condition 1, places deliberate modification of the validator's executable code, control flow or in-memory state outside the T6 threat model. Such an actor can equally rewrite the loaded thresholds, a `Check`'s result or the report before it is written. Any in-memory guard is itself in-memory state open to the same edit, so there is no fixed point inside the process. Code review and trusted execution address this class.

Option B's safeguards do not change that. They are not claimed to detect deliberate edits, and F58 is not recorded as fixed by them.

### Safeguards (DR-0022 B), and what they detect

**1. Snapshot digest at the end of every verification run** (`Session._integrity_problems`, called by `finish`):
- the in-memory ledger is re-hashed (canonical JSON, about 0.8 s) and compared with the hash taken when it was loaded;
- the artifact file is re-read and re-hashed, and compared both with the bytes loaded and with the pinned `APPROVED_REFERENCE_SNAPSHOT_SHA256`.

A mismatch is a `reference snapshot digest` problem, and the `reference_snapshot` check fails.

**2. Execution mode** (`run_mode_problems`, used by `m2_proof.py` and by `gmat_m2.py`'s `_evaluate`, which `compare` and `run` use). Without an explicit recorder (only the snapshot tool passes one), the entrypoint fails if:
- no session ran;
- the session was not in verify mode;
- the session compared no value.

The failure goes into the Proof's `reference_snapshot` check and into the GMAT rejection reasons. The Proof still has 215 checks.

| Detects (accidental corruption and wrong execution state) | Does not detect |
|---|---|
| a bug that writes into the loaded ledger during the run | a deliberate edit that also updates the stored load-time hash, or patches the check |
| the artifact file replaced or modified during the run | edits to `APPROVED_REFERENCE_SNAPSHOT_SHA256` or to validator code (code review) |
| a Proof or GMAT comparison that ran in record mode, without a session, or verified nothing (for example a wiring regression) | a deliberate mode switch combined with an edit of the mode check, or any other in-process tampering (outside the threat model, F58) |

**Tests (each fails when its safeguard is disabled):**
- `test_ledger_changed_during_the_run_is_detected`;
- `test_artifact_replaced_during_the_run_is_detected` (the file re-hash and the pin at finish);
- `test_a_clean_session_passes_the_integrity_checks`;
- `test_run_mode_problems` (missing session, record mode, nothing compared);
- `test_gmat_comparison_in_the_wrong_mode_fails`;
- `test_m2_proof_in_the_wrong_mode_fails`.

**Preserved (condition 6).** No threshold, reference value, tolerance or acceptance semantics changed. The M2 report still has 215 checks.

## Re-verification 18 (final, complete T6 checkpoint; under DR-0019 B, DR-0020 A, DR-0021 A and DR-0022 B)
See below.
