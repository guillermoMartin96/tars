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

## Re-verification
See below.
