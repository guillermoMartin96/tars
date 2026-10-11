### F1 — `run` stores numerically rejected references as successful
**Severity:** High  
**Claim:** `cmd_run` checks `result.violations` but never applies the numerical O9 limits. It also overwrites committed artifacts before validation finishes.  
**Evidence:** `review_scratch/probes.py`, probe `run_stores_bad_reference`, supplied a well-formed report containing a 1 m position error. `run` returned **0** and printed “reference stored.” A subsequent comparison failed coast-versus-Kepler, GMAT-versus-DOP853, and simulator sample-position gates. See `toolbox/scripts/gmat_m2.py:104–152`.  
**Suggested fix:** Stage all artifacts, apply provenance, alignment, and numerical gates, then commit the complete reference atomically. Preserve existing evidence on failure.

### F2 — Script comparison discards assignment placement and duplicates
**Severity:** Medium  
**Claim:** `split_script` removes every Cartesian-state assignment wherever it appears and retains only its last value. Consequently, a materially different mission script can pass configuration verification.  
**Evidence:** Probe `initial_state_assignments_moved_to_mission_end` moved all six initial-state assignments after the final propagation and updated the script hash. Comparison returned **no violations and no failed gates** against the unchanged report. See `src/tars/validation/gmat_m2.py:282–293`.  
**Suggested fix:** Preserve assignment positions during comparison, require exactly one assignment per initial-state component in the initialization section, and tolerate only numerical differences in those six literals.

### F3 — Provenance checks cannot establish external-reference origin
**Severity:** High  
**Claim:** Comparison validates four metadata fields but ignores the claimed GMAT version, build, executable identity, command, mission identity, generation record, replacement reason, and console outcome. Numerical agreement alone can therefore certify non-GMAT data as GMAT evidence.  
**Evidence:** Two executable probes passed every O9 gate:

- `missing_provenance_failed_console`: removed all metadata except scenario hash, constants, and script/report hashes; replaced the console log with `Execution Failed: not GMAT`.
- `DOP853_fabricated_GMAT_report`: replaced the trajectory with DOP853-generated rows and analytic masses, then updated the report hash.

These demonstrate acceptance weaknesses, **not evidence that the current references are fabricated**.  
**Suggested fix:** Require and validate provenance fields, bind the console log to the artifact manifest, and retain independently reviewed reference digests and replacement/reproduction records. Explicitly distinguish numerical consistency from external-origin verification.

### F4 — `generate` bypasses the reference replacement guard
**Severity:** Medium  
**Claim:** `generate` unconditionally overwrites committed scripts without a replacement reason or review record. The `run` guard also considers only report existence.  
**Evidence:** Probe `generate_bypasses_guard` substituted a wrong generator and overwrote an existing reference script with `WRONG GENERATOR`, without authorization metadata. See `toolbox/scripts/gmat_m2.py:52–58,77`.  
**Suggested fix:** Generate previews outside the committed reference directory. Apply the replacement policy whenever any existing reference artifact would change.

### F5 — Missing simulator observations produce vacuous O9 passes
**Severity:** Medium  
**Claim:** O9 compares observations present in the log without independently requiring the expected observation coverage. Empty state-sample and burn-boundary sets yield zero errors; one mass sample suffices.  
**Evidence:** Probes `deleted_samples_and_burn_events` and `all_but_one_mass_sample_deleted` both passed every O9 gate. The latter compared only the initial mass instead of 902 observations. See `src/tars/validation/gmat_m2.py:423–446`. **T5 audits protect the integrated Proof; standalone comparison lacks that protection.**  
**Suggested fix:** Independently enforce expected sample times and predicted burn boundaries, including DR-0018 semantics. Audit the simulator run before standalone comparison.

### F6 — Standalone comparison silently accepts missing thresholds
**Severity:** Medium  
**Claim:** Removing the `o9_gmat` group disables every standalone numerical gate while preserving a successful exit. Individual missing limits have the same weakness.  
**Evidence:** `review_scratch/missing_limits.py` loaded a scratch threshold file without `o9_gmat`. `cmd_compare` returned **0**, reporting `passed: true` and `thresholds: {}`. The full Proof’s coverage check catches this; standalone `compare` does not.  
**Suggested fix:** Require coverage of every mandatory O9 metric before evaluating a comparison, sharing the Proof’s fail-closed coverage logic.

### F7 — The claimed gate-disable test coverage is incorrect
**Severity:** Low  
**Claim:** VAL-0014 states that disabling each O9 check makes a test fail, but the coast-alignment gate can be disabled without failing the T6 suite.  
**Evidence:** `review_scratch/disabled_gate.py` forced `coast_vs_kepler_position_error_max_m` to zero. **All 29 T6 tests passed.** This contradicts `docs/science/validation.md:447`.  
**Suggested fix:** Add targeted tests that fail when each mandatory check is disabled, and correct the coverage claim until verified.

## Summary

**Verdict: FAIL.** The committed numerical results pass, but reference acceptance, provenance, replacement handling, and standalone completeness checks have demonstrated weaknesses.

Verified:

- **858 tests passed**, with two expected overflow warnings.
- Ruff lint and formatting passed.
- M2 Proof: **212/212 checks passed**; M1 Proof passed.
- Determinism, golden-state comparison, and GMAT M1 comparison passed.
- Fresh GMAT M2 measurements match VAL-0014.
- All **18 row mutations** across three missions were rejected.
- Scenario-derived physics inputs, engine configuration, adjacent-burn switching, provisional thresholds, the DOP853 floor, and DR-0017/DR-0018 separation are preserved. No T5 gate loosening was found.
- The constant-thrust and depletion configuration agrees with [GMAT R2026a’s ChemicalThruster implementation](https://raw.githubusercontent.com/nasa/GMAT/R2026a/src/base/hardware/ChemicalThruster.cpp). The depletion exclusion remains consistent with the recorded authority; its specific T6 overshoot measurement was not independently reproduced.

Contrary to the prompt’s environment description, the GMAT executable path exists here: reproduction tests **ran and passed**, rather than skipping.

Review code, mutations, reports, and logs are under `review_scratch/`; no implementation fixes were made.