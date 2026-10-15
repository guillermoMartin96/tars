**M1: NOT RESOLVED — evidence:** The original `1e103 m` probe now exits **2** with a validation error and no traceback. However, `altitude_m=5.643803094122361e102` passes validation and still overflows during the **first gravity evaluation**; see K1.

Against scratch-reconstructed `354914d`, all three new regression tests fail. The duration and CLI cases detect the original defect; the orbits case fails only because the validation message changed. Evidence: `review_scratch/old-tests.txt`.

### K1 — Period validation does not cover the actual gravity radius

**Severity:** Low  
**Claim:** The M1 guard checks nominal radius cubed, but the Cartesian norm can round upward and overflow. Large RK4 intermediate radii also remain unguarded.  
**Evidence:** `review_scratch/initial_norm.json` validates; its nominal radius is `5.643803094122361e102`, while the computed norm is `5.643803094122362e102`. The CLI exits **1** with `OverflowError` at `src/tars/sim/forces.py:40`. Separately, `review_scratch/dt_8.json` uses normal altitude and `dt_s=duration_s=sample_interval_s=1e100`; an RK4 stage crashes at the same line. Traces: corresponding `*.cli.txt` files.  
**Suggested fix:** Validate the actual initial-state gravity calculation and turn unsupported numerical stages into recorded mission failures, preserving ordinary M1 arithmetic.

### K2 — Large integer orbit counts crash validation

**Severity:** Low  
**Claim:** Timeout arithmetic converts an unrestricted integer to float before checking representability.  
**Evidence:** `stop.orbits=10**309` raises `OverflowError: int too large to convert to float` at `src/tars/sim/scenario.py:112` in both schema versions. The CLI exits **1** with a traceback instead of **2**. Reproducer: `review_scratch/huge_orbits_309.json`; trace: `review_scratch/huge_orbits_309.cli.txt`.  
**Suggested fix:** Catch arithmetic overflow around the entire timeout expression and raise a validation `ValueError`.

### K3 — Altitude sampling overflows for a finite committed state

**Severity:** Low  
**Claim:** Finite Cartesian components can produce an infinite NumPy norm, causing event creation to crash.  
**Evidence:** With altitude `1e100` and `dt_s=duration_s=sample_interval_s=1e200`, validation succeeds and the first step commits finite coordinates. `_altitude()` at `src/tars/sim/runner.py:102` returns infinity; `StateSampled` then raises `ValidationError`. The CLI exits **1** without a recorded completion. Reproducer and trace: `review_scratch/coast_188.json`, `review_scratch/coast_188.cli.txt`.  
**Suggested fix:** Use an overflow-safe norm and check derived telemetry before constructing events.

### K4 — Representable engine rates can still yield unrepresentable acceleration

**Severity:** Low  
**Claim:** Spacecraft validation checks mass, exhaust velocity, and mass flow, but an accepted burn can immediately overflow `F/m`.  
**Evidence:** Dry mass and propellant each `1e-300 kg`, thrust `1e100 N`, Isp `1e100 s`, and burn duration/tick/stop `1e-300 s` validate and schedule successfully. The first powered stage raises `ValueError: thrust acceleration F/m overflows for mass 2e-300` at `src/tars/sim/propulsion.py:148`. Reproducer and trace: `review_scratch/burn_40.json`, `review_scratch/burn_40.cli.txt`.  
**Suggested fix:** Reject unsupported acceleration configurations or translate numerical acceleration failures into the existing recorded failure path.

### K5 — Empty force-model configuration crashes at start-up

**Severity:** Low  
**Claim:** The schema accepts `force_models=[]`, but constructing the runner rejects it with an uncaught exception. This is pre-existing.  
**Evidence:** An otherwise ordinary duration scenario raises `ValueError: at least one force model is required` in `CompositeForceModel`; CLI exit **1** with traceback. Reproducer and trace: `review_scratch/empty_forces.json`, `review_scratch/empty_forces.cli.txt`.  
**Suggested fix:** Require at least one force model during scenario validation.

### Summary

**Verdict: CONDITIONAL PASS — M1 remains partially unresolved; additional Low crash paths remain.**

- **695 tests passed**; Ruff lint and formatting passed.
- Determinism reproduced exact M1 hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- M1 Proof passed every gate; timeout remains **5908 ticks**.
- M2 slice succeeded at tick **5370**, with **nine orbits**; repeated JSONL was byte-identical.
- Reviewed the full T4 diff and swept **4,728 arithmetic cases**, plus radius-boundary probes. Longer valid runs were capped for inspection and were not counted as defects.
- No remaining Critical, High, or Medium T4 issue found.

No source or test files were edited. Review artifacts are under `review_scratch/`.