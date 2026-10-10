### F1 — A burn at the computed depletion time can be rejected
**Severity:** Medium  
**Claim:** Default sufficiency validation can reject a burn whose duration equals the model’s computed depletion duration.

**Evidence:** `PYTHONPATH=src .venv/bin/python review_scratch/probe.py` produced:
```text
exact depletion p=0.1 product=0.10000000000000002
BurnRejectedError insufficient_propellant:
needs 0.10000000000000002 kg, 0.1 kg loaded
```
The duration was `0.1 / engine.mass_flow_kgps`. Multiplying it back at `src/tars/sim/propulsion.py:300–305` introduces a rounding error and rejects the burn. The exactly-sufficient test at `tests/test_propulsion.py:251` uses only 12 kg, which happens to round favorably.

**Suggested fix:** Use a consistent depletion-time boundary for planning and sufficiency checks, and clamp consumption at that boundary. Test several propellant amounts and adjacent representable durations; preserve rejection for genuinely insufficient propellant.

### F2 — NumPy scalar inputs reduce schedule precision
**Severity:** Medium  
**Claim:** Accepted NumPy scalars can cause float32 arithmetic inside an otherwise float64 model, violating the burn schedule’s own invariants.

**Evidence:** `plan_burn` validates `Real` inputs at `src/tars/sim/propulsion.py:279–283` but does not normalize them before arithmetic at lines 300–315. With `np.float32` inputs for the reference burn:
```text
cutoff_t_s:                         677.2999877929688
ignition_t_s + commanded_duration:  677.3000030517578
cutoff discrepancy:                -1.52587890625e-05 s
propellant discrepancy:             5.534227884851362e-07 kg
```
The cutoff and consumption remain NumPy float32 values, while ignition and commanded duration become Python floats. These discrepancies exceed ordinary float64 rounding and undermine DR-0013’s event-time splitting.

**Suggested fix:** Normalize all accepted numeric inputs to Python floats before comparisons and arithmetic. Test NumPy float32/float64 and integer scalars against equivalent normalized inputs.

### F3 — Finite inputs can produce invalid engine properties and event times
**Severity:** Medium  
**Claim:** Input validation does not ensure that derived quantities remain finite, positive, and representable.

**Evidence:** The probe command returned:
```text
EngineSpec(490., 1e308): exhaust_velocity=inf, mass_flow=0.0
```
Its burn was accepted with zero propellant consumption. Conversely, `EngineSpec(1e308, 1e-300)` produced infinite mass flow and an accepted depletion plan with zero duration.

It also returned:
```text
ignition=1e16, duration=1: cutoff=1e16
ignition=1e308, duration=1e308: cutoff=inf
```
Relevant calculations are at `src/tars/sim/propulsion.py:75–80, 299–315`. A positive-duration burn can therefore have simultaneous ignition/cutoff, or no finite cutoff. Neither is suitable for exact event splitting. Existing tests cover non-finite inputs, not non-finite or collapsed results.

**Suggested fix:** Validate derived exhaust velocity, mass flow, total mass, consumption, duration, and cutoff. Reject schedules that cannot represent a finite cutoff strictly after ignition, using the documented rejection vocabulary.

### F4 — The rocket-equation oracle is numerically unstable at extreme mass ratios
**Severity:** Medium  
**Claim:** Forming `m0 / mf` directly can return infinity when the correct delta-v is finite, and loses accuracy for small mass changes.

**Evidence:** `src/tars/sim/propulsion.py:141` evaluates `c * log(m0 / mf)`. The probe returned:
```text
rocket_equation_delta_v(3000., 1e300, 1e-300) = inf
```
The mathematical result is approximately `4.144653e6 m/s`, which is representable.

For `m0=1`, `mf=nextafter(1, 0)`, and `c=3000`:
```text
model:             6.661338147750938e-13
stable log1p form:  3.330669073875470e-13
```
The current tests at `tests/test_propulsion.py:366–383` cover moderate ratios and equal masses, leaving these failures undetected.

**Suggested fix:** Use `log1p((m0-mf)/mf)` near equal masses and an overflow-safe logarithmic formulation for large ratios. Verify both against high-precision arithmetic.

### F5 — Tests do not distinguish velocity tracking from ignition-held pointing
**Severity:** Medium  
**Claim:** All scoped tests pass when prograde pointing is changed to hold its first direction, contrary to DR-0012 and SCI-0011.

**Evidence:** Ran:
```text
PYTHONPATH=src .venv/bin/python review_scratch/mutation_tracking.py
73 passed in 0.61s
```
The script monkeypatches `Prograde.direction` in memory to cache its first result per instance. No source or test files were changed.

The direct pointing test evaluates only one state (`tests/test_propulsion.py:145–149`). The orbital DOP853 comparison uses the same model-backed RHS for both integrators (`tests/test_propulsion.py:508–512`), so both integrate the same incorrect direction law. The energy-sign check also passes for ignition-held thrust over this short burn.

**Suggested fix:** Exercise the same direction-law instance with changing velocities, for both prograde and retrograde. Add an orbital reference RHS that computes velocity tracking independently of the production direction law.

### F6 — Public force and direction helpers incompletely validate inputs
**Severity:** Low  
**Claim:** These helpers accept malformed inputs and reject some valid finite vectors because of unstable normalization.

**Evidence:** The probe command showed:
```text
thrust_acceleration(engine, [1,0,0], True) → [490,0,0]
Prograde.direction(..., [1,0])            → [1,0]
Prograde.direction(..., [1e200,0,0])      → ValueError
Prograde.direction(..., [1e-200,0,0])     → ValueError
```
Mass validation at `src/tars/sim/propulsion.py:120` treats `True` as 1 kg, unlike spec and burn validation. `_velocity_unit` at lines 159–164 does not check three-vector shape, and its norm overflows or underflows for finite nonzero vectors. String mass input raises `TypeError` despite the helper documenting `ValueError`.

**Suggested fix:** Apply consistent scalar validation, enforce finite three-vector shape, and use scaled normalization or a stable norm. Add malformed-shape, bool/string, and large/small finite-vector tests.

### Summary

**Overall verdict: FAIL.** Nominal physics and M1 preservation pass; numerical boundary handling and velocity-tracking regression coverage need correction.

Verified:

- Scoped tests: **73 passed** using the requested command.
- Full suite: **282 passed in 41.06 s**.
- `.venv/bin/ruff check .`: **All checks passed**, before adding scratch experiments.
- Nominal `g0`, mass flow, `F/m`, rocket equation, prograde/retrograde definitions, default rejection, and explicit depletion match the cited requirements.
- Existing quadrature and free-space tests exercise production acceleration against analytic references.
- Architecture scan: **no violations**; propulsion remains disconnected from the simulator.
- M1 final position/velocity differences from golden: **zero**.
- M1 event hash exactly matches:
  `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- Read-only, unaliased direction outputs work for ordinary inputs.

Only `review_scratch/` files were created. This snapshot has no usable Git metadata, so commit and branch identity could not be independently verified.