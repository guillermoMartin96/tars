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
- **Qualification (re-verification):** this fix covered the reference missions' samples only. The O8 auxiliary runs (the reviewer's 630 s probe) were still unchecked; that is F6 below.

### F4: Missing depletion events are accepted
**Severity:** Medium.  
**Implementer reasoning:** Correct. Pairing was enforced only from `PropellantDepleted` forward.  
**Fix:**
- Every `BurnEnded(end_cause="propellant_depleted")` must be immediately preceded by a `PropellantDepleted` with the same `burn_id`, `command_id` and `event_t_s`.
- **Test:** `test_missing_or_mismatched_depletion_event_is_detected` (deletion and mismatch).

## Measurement note
O4 now restarts DOP853 at every sample time (895 segments instead of a few). Reference values shift by at most about 7 µm, for example slice final 0.290351 → 0.290344 m. This is within the documented 11–15 µm cross-platform floor of the reference (VAL-0010 addendum). VAL-0013 is updated.

## Re-verification 1
**Reviewer:** Codex, session `01a12c6f-fe4c-7a31-8bbd-276f9691c34e`, at `f5f3866`. **Raw:** `raw/M2-T5-codex-reverify.md`, with its probes and a complete field inventory in `raw/M2-T5-codex-reverify-scratch/` (`audit.md`).

**Verdict: FAIL.**
- F1, F2 and F4 are resolved. F3 is resolved for the reference missions but not for auxiliary runs (F6).
- Asked to sweep the whole false-pass class in one round, the reviewer found 11 more (F5–F15). Each is backed by a mutant that passes all 76 checks.
- All gates passed: 772 tests, lint, M2 Proof, M1 Proof, determinism, cross-platform, GMAT M1.
- No threshold weakening was found; M1, DR-0017 separation, FU-1 and scope were confirmed.

**All eleven are `ACCEPTED`.** They were closed together by restructuring rather than by patching: `tars.validation.m2.audit_run()` checks every output of one run. `m2_proof.py` applies it to every run it creates: missions, derived variants, DR-0018 stop variants, and O6/O8 auxiliary runs. Each fix is mutation-tested (disabling it makes its tests fail); some mutants are also caught by overlapping checks.

| # | Sev. | Finding | Fix | Tests |
|---|---|---|---|---|
| F5 | Med | O3 used the reported cutoff time | Closed form at the requested interval; reported ignition/cutoff must equal it (`timing_violations`) | `test_o3_detects_a_wrong_burn_duration` |
| F6 | Med | O6/O8 auxiliary telemetry unchecked | Auxiliary runs fully audited; O8 variants keep the 60 s telemetry grid so every sample has a reference state | `test_auxiliary_runs_are_audited`, `test_m2_proof_audits_auxiliary_and_boundary_runs` |
| F7 | **High** | Coast-only missions had no trajectory gate | O4 (independent initial state, every sample, horizon) and O5 run on every mission | `test_missions_without_burns_have_a_trajectory_gate` |
| F8 | Med | `RunResult` and CLI summary only partly reconciled | `check_result_consistency` (receipts incl. plans, samples, crossings, initial, status, times, final propulsion plans and direction); `cli_summary_violations` on the CLI's own summary builder | `test_returned_result_is_reconciled_with_events` (8 cases), `test_cli_summary_is_reconciled_with_events` |
| F9 | Med | Intermediate propulsion telemetry unpredicted | `propulsion_sample_checks`: schedule, propellant and sensed Δv predicted at every sample from accepted commands and elapsed burn time | `test_intermediate_propulsion_samples_are_predicted` (4 cases) |
| F10 | Med | Thrust direction unchecked between state samples | Direction vs the DOP853 reference velocity at every burning sample | `test_reversed_thrust_between_state_samples_is_detected` |
| F11 | Med | Transition payloads unchecked | Ignition state vs reference; transition propellant vs prediction; mass identities; thrust unit vector; depletion residual = `BurnEnded` propellant | `test_transition_payloads_are_checked` (5 cases) |
| F12 | Med | Plans, timing claims and D1a cutoff unverified | Predictions now include the exact represented cutoff (D1a re-implemented from the decision); every plan field; DR-0017 bound recomputed as F·\|D−d\|/m_end; configured budget = 1e-7 | `test_plans_and_timing_claims_are_checked` (5), `test_depletion_cutoff_shift_is_detected` |
| F13 | Low | Configuration and rejection provenance unchecked | `SimulationStarted` identity vs scenario; direction laws; issuer; declared `schema_errors`; schema-invalid intent all null | `test_start_provenance_is_checked` (4), `test_rejection_provenance_is_checked` (3) |
| F14 | Med | Orbit and altitude reporting unchecked | Node crossings located independently (DOP853 + Kepler bisection), count and timing; numbering; `altitude_m = \|r\| − R`; extrema vs samples and reference apsides | `test_orbit_and_altitude_reporting_is_checked` (6) |
| F15 | Med | Missing threshold group silently disabled gates | Every emitted metric must be gated unless declared report-only (`thresholds_cover_all_metrics`) | `test_missing_threshold_group_is_reported` |

Also corrected, as noted by the reviewer:
- The VAL-0013 and `m2.json` wording on where the largest sample error occurs.
- The F3 record above, which now carries the auxiliary-run qualification.

**New numerical finding while closing F6 (implementer).** The O6 high-thrust auxiliary runs exceeded the O2 1e-12 gate: 2.0e-11 relative at 16× thrust.
- The analytic RK4/Simpson truncation bound predicts this error to 2–3 % at every level, so it is a known mechanism, not a defect.
- The O2 gate now applies the unchanged round-off allowance to the error in excess of the computed bound. Details are in VAL-0013 and the `m2.json` basis.
- This is flagged for the T7 threshold DR.

## Re-verification 2
See below.
