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
See below.
