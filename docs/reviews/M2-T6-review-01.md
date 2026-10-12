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
See below.
