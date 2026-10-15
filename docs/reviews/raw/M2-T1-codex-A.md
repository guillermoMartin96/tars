### F1 — Accepted burns can have collapsed or non-finite cutoff times
**Severity:** High  
**Claim:** The schedule does not consistently use float64 arithmetic or validate its resulting cutoff. This violates the event-time contract needed by DR-0013 step splitting.

**Evidence:** `src/tars/sim/propulsion.py:279–283` accepts NumPy real scalars, but only ignition and commanded duration are converted to Python floats when constructing the plan; cutoff arithmetic occurs beforehand at line 315.

Running `PYTHONPATH=src .venv/bin/python -` with:

```python
e = EngineSpec(490, 312)
b = plan_burn(e, np.float32(300), np.float32(600), np.float32(1e-5))
print(b.ignition_t_s, b.cutoff_t_s, b.propellant_used_by(b.cutoff_t_s))
```

produced `600.0 600.0 0.0`, despite positive duration and planned consumption. Python-float ignition `1e16`, duration `1` also collapses the cutoff. With `EngineSpec(1e-308, 312)`, ignition and duration both `1e308`, the accepted cutoff is `inf`.

**Suggested fix:** Normalize accepted numeric inputs before arithmetic. Reject schedules whose cutoff is non-finite or cannot represent a positive elapsed burn, using a stable rejection code. Test float32 inputs and representability boundaries.

### F2 — Finite specifications can produce invalid derived physics
**Severity:** Medium  
**Claim:** Validation checks individual inputs but allows overflow/underflow to invalidate exhaust velocity, mass flow, and depletion duration.

**Evidence:** `src/tars/sim/propulsion.py:68–80` validates thrust and Isp separately; derived values are unchecked before use at lines 299–310.

Experiments using `PYTHONPATH=src .venv/bin/python -` showed:

- `plan_burn(EngineSpec(490, 1e308), 300, 0, 10)` accepts a completed burn with `mass_flow_kgps=0` and zero consumption because exhaust velocity overflowed.
- `plan_burn(EngineSpec(1e308, 1e-308), 300, 0, 10, "burn_to_depletion")` returns infinite mass flow, zero burn duration, and 300 kg planned consumption. Consumption at cutoff is nevertheless zero.

These outputs conflict with SCI-0008/0009/0012. Existing parameter tests exercise invalid inputs, not invalid derived quantities.

**Suggested fix:** Validate representable, finite, positive exhaust velocity and mass flow, and validate derived burn quantities before returning a plan. Reject unsupported ranges explicitly.

### F3 — Exactly sufficient propellant can be rejected or misclassified
**Severity:** Medium  
**Claim:** The sufficiency comparison is sensitive to a division/multiplication round-trip, while the boundary test covers only a favorable value.

**Evidence:** At `src/tars/sim/propulsion.py:300–310`, the rounded product is compared directly with available fuel. Running:

```python
e = EngineSpec(490, 312)
duration = 0.1 / e.mass_flow_kgps
plan_burn(e, 0.1, 0, duration)
```

raised:

```text
insufficient_propellant: needs 0.10000000000000002 kg, 0.1 kg loaded
```

With explicit `burn_to_depletion`, the same request is labeled `propellant_depleted` even though actual and commanded durations compare equal. `tests/test_propulsion.py:251–255` checks only 12 kg, which avoids this rounding direction.

**Suggested fix:** Define a narrowly bounded floating-point equality rule for sufficiency and clamp boundary consumption to available fuel. Test round-trip boundaries in both directions, plus genuinely insufficient neighboring cases; avoid a broad tolerance that silently accepts shortages.

### F4 — Rocket-equation oracle loses accuracy at numerical boundaries
**Severity:** Medium  
**Claim:** Computing the mass ratio directly can overflow unnecessarily and gives substantial relative error for very small mass changes.

**Evidence:** `src/tars/sim/propulsion.py:141` uses `math.log(m0_kg / mf_kg)`. Experiments produced:

```text
rocket_equation_delta_v(1, 1e308, 1e-308) = inf
```

The mathematical result is finite, approximately `1418.392417284332`.

For `m0=1`, `mf=np.nextafter(1., 0.)`, the function returned `2.2204460492503128e-16`; the stable `-log1p(mf - 1)` reference gives `1.1102230246251565e-16`, a factor-of-two difference.

Tests at `tests/test_propulsion.py:350–362` cover ordinary ratios and equal masses, leaving both boundaries untested.

**Suggested fix:** Use `log1p` for nearby masses and a formulation that avoids ratio overflow for widely separated masses. Add independent high-precision boundary references.

### F5 — All targeted tests pass with forbidden inertial-hold prograde behavior
**Severity:** High  
**Claim:** The tests do not enforce velocity tracking across successive derivative evaluations, a material SCI-0011/DR-0012 requirement.

**Evidence:** In a separate Python process, I monkeypatched `Prograde.direction` to cache and return its first direction:

```python
original = Prograde.direction
def frozen_direction(self, t, r, v):
    if not hasattr(self, "_review_frozen_direction"):
        self._review_frozen_direction = original(self, t, r, v)
    return self._review_frozen_direction
Prograde.direction = frozen_direction
```

Then I ran the targeted suite through `pytest.main(...)`: **73 passed**. No source or test files were modified.

The direct direction test evaluates one state. The DOP853 test at `tests/test_propulsion.py:508–515` supplies the same production-dependent RHS to both integrators, so both follow the wrong pointing law and still converge. The energy-sign test also accepts inertial hold. DR-0012 records a **69 m SMA difference** between tracking and inertial hold for the reference burn.

**Suggested fix:** Call each direction-law instance with successive nonparallel velocities and assert the corresponding current directions. Add a powered-orbit reference whose pointing formula is implemented independently of the production direction law.

### Summary

**Verdict: FAIL** — nominal physics and M1 preservation pass, but schedule validation and velocity-tracking coverage need correction.

Verified:

- Requested targeted tests: **73 passed**.
- Full suite: **282 passed**, including the architecture scan.
- `.venv/bin/ruff check .`: **All checks passed**.
- Nominal `g0`, Isp conversion, mass flow, `F/m`, rocket equation, depletion accounting, configurable specs, and extensible direction interface match the approved model.
- Read-only outputs, unaliased direction arrays, and frozen specifications pass existing checks.
- Boundary experiments exposed F1–F4; an in-memory mutation demonstrated F5.
- Two M1 runs both reproduced the committed event hash: `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- No implementation or test files were changed. Git metadata was unavailable, so commit/branch identity could not be independently verified.
