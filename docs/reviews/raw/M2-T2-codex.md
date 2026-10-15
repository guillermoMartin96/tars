### F1 — Failed steps leave the engine schedule partially advanced
**Severity:** Medium  
**Claim:** A propulsion step can fail after changing `_active` and `_pending`, while physical state and tick remain unchanged. Retrying then integrates a different burn.

**Evidence:** `src/tars/sim/simulator.py:321–335` processes engine transitions before integration succeeds; `:352–355` immediately mutates engine state. In `review_scratch/probes.py`, a force returning NaN after ignition causes an exception during a burn scheduled for `[1, 3]` seconds. Afterwards:

- Tick remains `0`, with unchanged propellant.
- Engine state is `BURNING`, with no pending plan.
- Retrying with the force restored omits ignition and consumes **0.480443215729963 kg**, instead of **0.320295477153324 kg**—three seconds of thrust instead of two.

**Suggested fix:** Compute schedule changes and transitions locally, then commit them together with the integrated state after successful propagation. Add a failed-step/retry regression test.

### F2 — Scheduling classifies malformed inputs before validating their schema
**Severity:** Medium  
**Claim:** Early coercion and conflict checks return incorrect machine-readable rejection reasons for malformed ignition inputs. Some numeric inputs escape as unstructured exceptions.

**Evidence:** `src/tars/sim/simulator.py:231–248` calls `float()` and compares ignition before `plan_burn` validates type and finiteness. After advancing to `t=10`, these inputs return `ignition_in_past`:

```python
ignition_t_s=-np.inf
ignition_t_s="-1"
ignition_t_s=True
ignition_t_s=np.array(-1)
ignition_t_s=np.bool_(True)
```

DR-0014’s amendment assigns non-real and non-finite inputs to `schema_invalid`. Furthermore, `ignition_t_s=10**1000` raises an uncaught `OverflowError`. Reproductions are in `review_scratch/probes.py` and `review_scratch/extra_checks.py`.

**Suggested fix:** Validate and normalize scalar inputs before chronological or engine-conflict checks. Convert invalid types, non-finite values, and normalization overflow into `BurnRejectedError(SCHEMA_INVALID)`. Test invalid inputs at different simulator times and with pending/active burns.

### F3 — Accepted event intervals can disagree materially with planned consumption
**Severity:** Medium  
**Claim:** The simulator integrates the rounded difference between event times, while the plan and committed propellant use the requested duration. Accepted plans can therefore deliver excess thrust and violate the stated propellant-floor bound.

**Evidence:** `src/tars/sim/propulsion.py:348–365` computes consumption from duration and cutoff from `ignition + duration`. `src/tars/sim/simulator.py:332–334` integrates with `h = cutoff - ignition`.

With a zero force model, the reference engine, ignition `1e15`, duration `0.1`, and a tick containing both events:

- Accepted duration: **0.1 s**
- Represented event interval: **0.125 s**
- Planned consumption: **0.0160147738576662 kg**
- Integrated consumption: **0.0200184673220747 kg**

A depletion variant produces a **0.25 s** interval for approximately **0.2 s** of available propellant. The cutoff floor absorbs approximately **0.00800739 kg**, far beyond ADR-0007’s stated ≤`1e-12 kg` adjustment. Sensed Δv is **0.122498529 m/s**, versus the rocket equation’s **0.097998431 m/s**.

These are extreme but accepted inputs, reproduced in `review_scratch/probe_results.txt`.

**Suggested fix:** Make representable event duration, planned consumption, and integration duration consistent. Reject materially unrepresentable intervals with `burn_unschedulable`, following an explicitly documented representability rule. Test both partial consumption and depletion.

### F4 — Public transition arrays can rewrite retained event evidence
**Severity:** Low  
**Claim:** `EngineTransition` arrays are initially non-writeable, but callers can enable writing and alter the simulator’s retained transition objects.

**Evidence:** `src/tars/sim/propulsion.py:443–451` creates owning NumPy arrays and sets their writeable flag to false. `src/tars/sim/simulator.py:171–174` returns the stored transition tuple directly. This succeeds:

```python
event = sim.engine_transitions[0]
event.r.flags.writeable = True
event.r[0] = 999
assert sim.engine_transitions[0].r[0] == 999
```

The physical position remains unchanged because transition arrays are copies. The defect affects retained event evidence rather than physical-state ownership.

**Suggested fix:** Use immutable backing storage for transition arrays, or return detached transition copies so callers cannot rewrite simulator-retained evidence. Add an aliasing test.

### F5 — Tests do not validate transition position and velocity
**Severity:** Medium  
**Claim:** The targeted suite accepts completely incorrect translational state in every ignition and cutoff record.

**Evidence:** An in-memory mutation replaces `_transition`’s `r` and `v` arguments at `src/tars/sim/simulator.py:366–367` with zero vectors. Running:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/mutations.py zero_transition_state
```

passes **all 155 targeted tests**. The event tests check times, ordering, plans, and some propulsion scalars, but never validate event `r` or `v`.

Other mutations are detected:

- Double sensed Δv: **1 failure**
- Constant initial mass during thrust: **3 failures**
- Remove interior event splitting: **8 failures**

Evidence and mutation scripts are under `review_scratch/`.

**Suggested fix:** Check ignition and cutoff states against independent free-space analytic solutions and an orbital reference. Include boundary, interior, and multiple-event ticks; verify retained records remain stable after subsequent steps.

## Summary

**Verdict: FAIL.** Nominal physics and M1 preservation are supported, but failed-step consistency, validation, representability, and transition evidence need correction.

Verified:

- Full suite: **361 passed**, using `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`.
- Both requested ruff checks passed before creating scratch files.
- M1 Proof: **PASS**, with approved thresholds unchanged; output in `review_scratch/m1.json`.
- Cross-process determinism reproduced SHA-256 **`7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`**.
- Reconstructed the pre-T2 simulator by reversing its supplied diff in scratch. After 600 steps, its state bytes matched both current no-spacecraft and spacecraft-coast paths at `dt=10`, `0.1`, and `7/3`.
- VAL-0012’s four measurement runs reproduced every corresponding saved field exactly.
- Independent free-space checks covered six events within one tick, back-to-back burns, and scheduling a future burn during an active burn.
- The DOP853 test RHS independently implements the propulsion equations, and relative `pytest.approx` assertions explicitly use `abs=0`.
- No public snapshot alias that changes physical state was found.

`src/` and `tests/` were not modified. This archive has no Git metadata, so the supplied revision identity could not be independently verified.