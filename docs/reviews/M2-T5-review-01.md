# External Review: M2 Task T5: validators O1–O8, m2_proof.py, provisional m2.json, reference missions

**Reviewer/model:** OpenAI Codex CLI (separate provider), session `01a12c67-83ca-73d0-9a25-daabfb76cb99`.  
**Date:** 2026-10-11  
**Reviewed revision:** `a3b65f6` (diff `54cce8d..a3b65f6`).  
**Scope:** Tech Lead T5 requirements:
- independent expectations, no circular validation;
- success and failure paths: depletion, rejections, overlap, stop during a burn;
- ordering, traceability, accounting, replay;
- same-tick reporting tested and documented;
- provisional thresholds with recorded measurements;
- M1 gates preserved;
- DR-0017 bound kept separate from trajectory error;
- FU-1 preserved;
- no T6–T8 scope.

Focus: validator correctness, numerical assumptions, missing edge cases, false passes.

**Raw:** `raw/M2-T5-codex.md`; prompt and probes in `raw/M2-T5-codex-prompt.md` and `raw/M2-T5-codex-scratch/`.

## Summary
**Verdict: FAIL.**

Confirmed by the reviewer:
- 762 tests, lint, M2 Proof, M1 Proof, determinism, cross-platform and GMAT M1 comparison all pass;
- fresh measurements match VAL-0013;
- the independent RHS, DOP853 segmentation and the O5, O6 and O8 methods are sound;
- the receipts, rejection coverage, overlap, control runs and same-tick behavior are exercised;
- thresholds remain provisional; the DR-0017 bound stays separate; FU-1 is recorded; T6–T8 are not started.

The defects are **false passes**. Four mutants passed all 76 Proof checks:
- a wrong initial orbit;
- a run stopped at 3000 s;
- corrupted powered samples or completion state;
- deleted depletion events.

## Findings
All four are **`ACCEPTED`**. Each fix is mutation-tested: with the fix reverted, its new test fails.

### F1: O4 trusts an unverified initial state
**Severity:** High.  
**Implementer reasoning:** Correct. The DOP853 reference was seeded from `SimulationStarted`, a simulator output that the documented independence exceptions did not list. A 90°-rotated initial orbit was therefore self-consistent everywhere.  
**Fix:**
- `expected_initial_state()` derives the circular-orbit state from the scenario elements with an independently written rotation.
- O4 is seeded from that state and gates `initial_position_rel_error` and `initial_velocity_rel_error` (round-off class 1e-12; measured 0).
- **Test:** `test_wrong_initial_orbit_fails_o4`.

### F2: Successful termination is not checked against the requested horizon
**Severity:** High.  
**Implementer reasoning:** Correct. The lifecycle prediction, O4 and the cadence check followed the log's own end time. (Found independently as a self-review item while the review ran; the uncommitted fix was not in the reviewed snapshot.)  
**Fix:**
- `check_outcomes` uses `scenario.stop.duration_s` and flags a log that ends elsewhere.
- O4 compares the final state with the reference at the scenario horizon (`horizon_s`).
- The receipt count is now derived from the timeline (`expected_submissions`), and `RunResult.unsubmitted_command_ids` is checked against it instead of trusted.
- **Tests:** `test_premature_success_fails_outcomes_and_o4`, `test_missing_receipt_is_detected_independently_of_the_runner`, `test_run_ending_before_the_scenario_stop_is_detected`.

### F3: Powered samples and boundary completion states escape validation
**Severity:** Medium.  
**Implementer reasoning:** Correct. O4 compared only cutoff and final states, and O5 excludes powered arcs, so samples during a burn were unchecked. The DR-0018 boundary check never reconciled `SimulationCompleted` with the samples.  
**Fix:**
- O4 compares **every** `StateSampled` with the reference (`sample_position_error_max_m`, `sample_velocity_error_max_mps`; same provisional limits as the final state).
- `check_final_consistency()` requires that `SimulationCompleted`, the final `StateSampled`, `RunResult.final`, the last `PropulsionSampled` and `RunResult.final_propulsion` agree exactly. It runs for every mission and in the boundary check.
- **Tests:** `test_corrupted_powered_sample_fails_o4`, `test_inconsistent_final_state_is_detected`, `test_bogus_completion_at_an_active_stop_is_detected`.

### F4: Missing depletion events are accepted
**Severity:** Medium.  
**Implementer reasoning:** Correct. Pairing was enforced only from `PropellantDepleted` forward.  
**Fix:**
- Every `BurnEnded(end_cause="propellant_depleted")` must be immediately preceded by a `PropellantDepleted` with the same `burn_id`, `command_id` and `event_t_s`.
- **Test:** `test_missing_or_mismatched_depletion_event_is_detected` (deletion and mismatch).

## Measurement note
O4 now restarts DOP853 at every sample time (895 segments instead of a few). Reference values shift by at most about 7 µm, for example slice final 0.290351 → 0.290344 m. This is within the documented 11–15 µm cross-platform floor of the reference (VAL-0010 addendum). VAL-0013 is updated.

## Re-verification
See below.
