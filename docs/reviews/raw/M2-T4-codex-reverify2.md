**N1: RESOLVED — evidence:** Both original probes (`guard_product.json`, `orbit_tick_ratio.json`) now exit **2** with a scenario `ValidationError`, without traceback. Against scratch-reconstructed `5098f8a`, all four defect-specific regression cases fail; the timeout-property test also fails because the property was absent. Evidence: `review_scratch/probes.txt`, `review_scratch/old-tests.txt`.

The M1 timeout remains **5908 ticks**, using identical arithmetic and operation order. Duration stops bypass the calculation. Validation-order probes show only diagnostic precedence changes for inputs with multiple errors; no command-rejection semantics change.

### M1 — Extreme duration-scenario altitude still causes runtime overflow

**Severity:** Low  
**Claim:** A finite, schema-valid duration scenario can still crash during scenario-derived arithmetic. This is separate from N1, in unchanged gravity code.

**Evidence:** Setting `initial_orbit.altitude_m=1e103`, `stop.duration_s=10.0`, and `commands=[]` validates successfully. The first step raises `OverflowError` at `src/tars/sim/forces.py:40` when evaluating `r_norm**3`; the CLI exits **1** with a traceback. Reproducer and trace: `review_scratch/duration_large_radius.json`, `review_scratch/remaining-overflow.txt`.

**Suggested fix:** Reject unsupported initial-radius calculations during scenario validation, or evaluate gravity with overflow-safe arithmetic. Add a duration-stop regression case.

### Summary

**Verdict: CONDITIONAL PASS — N1 resolved; one separate Low edge case remains.**

- **692 tests passed**; Ruff lint and format checks passed.
- Determinism reproduced exact M1 hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- M1 Proof passed all approved gates.
- M2 slice succeeded at tick **5370**, with **nine orbits**; repeated JSONL was byte-identical.
- No remaining Critical, High, or Medium issue found across the full T4 diff. Event ordering, correlation, stop boundaries, failure atomicity, and approved vocabulary remain intact.

No source or test files were modified; artifacts are under `review_scratch/`.