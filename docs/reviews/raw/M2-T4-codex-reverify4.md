F1: RESOLVED — Failure-after-submission tests pass; final propulsion samples match the retained schedule.
F2: RESOLVED — Payload validation tests pass; `binary.json` exits 2 without traceback.
F3: RESOLVED — CLI staging and interrupted-publication tests pass.
F4: RESOLVED — Duration round-trip, `with_dt`, and hash-canonicalization tests pass.
F5: RESOLVED — Original `overflow.json` exits 2 without traceback.
N1: RESOLVED — `guard_product.json` and `orbit_tick_ratio.json` both exit 2 without traceback.
M1: RESOLVED — Original large-radius probe exits 2; rounding-boundary probe exits 1 with a complete `non_finite` event log.
K1: RESOLVED — `initial_norm.json` and `dt_8.json` exit 1 with complete, hash-verified logs ending at tick 0.
K2: RESOLVED — `huge_orbits_309.json` exits 2 with a validation error, without traceback.
K3: RESOLVED — `coast_188.json` exits 1 with a complete `non_finite` log; no step is committed.
K4: RESOLVED — `burn_40.json` exits 1 with a complete `non_finite` log; acceptance remains recorded, with no failed-step engine events.
K5: RESOLVED — `empty_forces.json` exits 2 with a validation error, without traceback.

**Note:** Injected overflow and division-by-zero failures preserve position, velocity, tick, propulsion schedule, and transitions. Retrying emits ignition and cutoff once. An injected `RuntimeError` still propagates. The broad catch can classify a future programming error raising either arithmetic exception as `non_finite`; no such defect was found in normal operation.

**Note:** NumPy’s norm can overflow even when the mathematical norm is finite. The new guard therefore excludes some representable extreme vectors, but no physically meaningful state within this Earth-orbit model.

### Summary

**Verdict: PASS.**

- **705 tests passed**; Ruff lint and formatting passed.
- M1 event bytes reproduce the exact hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`; all M1 Proof gates pass.
- M2 slice succeeds at tick **5370**, with nine orbits; repeated JSONL is byte-identical.
- The **4,728-case sweep** found no uncaught exceptions; 39 long runs retain the original two-step inspection cap.
- No remaining Critical, High, or Medium T4 issue found.

Source and tests were unchanged. Generated artifacts are under `review_scratch/`.