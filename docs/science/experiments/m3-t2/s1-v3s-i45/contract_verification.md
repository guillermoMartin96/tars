# I-45 §1 contract verification: I44-Q1 (supported integrator stage shape)

Inspected at BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (clean worktree). Read-only; no file
changed. Searches: `grep -rniE` over `*.md`, `*.py`, `*.json`, `*.yaml`, `*.toml` (excluding `.venv`)
for "custom integrator", "third-party", "Integrator protocol", "integrator … shape/contract/compat/
subclass/plug", "state vector", "y = [r", "[r, v, m_prop", "ndarray subclass", "MaskedArray"; plus every
`def step(`, `Integrator`, `INTEGRATORS`, `integrator=` use in `src/` and `tests/`.

**Result: PASS, with one scoping clarification (C-1).** No document, test or guarantee supports a stage
of another shape. Every statement of the layout gives 8 elements with a spacecraft and 6 without.

## 1. Integrator protocol (`src/tars/sim/integrators.py`)

- `Derivative = Callable[[float, NDArray[np.float64]], NDArray[np.float64]]`.
- `Integrator(Protocol)`: `name: str`, `order: int`,
  `step(f, t, y: NDArray[np.float64], dt) -> NDArray[np.float64]`.
- Neither states a shape. The module docstring says "The simulator's state vector is y = [r, v]
  (6 components)". That text predates M2 and describes only the no-spacecraft path (see D-1).
- The only implementation is `RK4`. It builds every stage from `y` and the derivative's output
  (`y + h*k`), so it preserves the shape of the committed state.
- `INTEGRATORS = {"rk4": RK4}`.

## 2. Derivative and Simulator interfaces (`src/tars/sim/simulator.py`)

- `_PROP, _DV = 6, 7`, with the comment "Augmented state layout with a spacecraft: y = [r(3), v(3),
  m_prop, dv_sensed]" (line 51).
- The `Simulator` docstring: "Without a spacecraft the state is y = [r, v], and stepping is exactly
  the M1 path. With a spacecraft, y = [r, v, m_prop, dv_sensed]."
- `_powered_derivative`, which holds the coast and powered closures and builds the derivative only
  when a spacecraft is configured: "RHS for y = [r, v, m_prop, dv_sensed] with the engine off or on."
- At BASE the powered closure already reads `float(y[_PROP])`. The coast closure returns
  `concatenate([v, a, _COAST_RATES])`, which is only well-formed for a 1-D stage.
- `_derivative` (no spacecraft) uses `y[:3], y[3:]`, and the committed state there has 6 elements.
  S1 adds no element read on this path.
- `__init__` builds the committed state as `concatenate([r0(3), v0(3)] [+ [m_prop, 0.0]])` and keeps it
  read-only.
- The integrator is chosen from the scenario only as `integrator: Literal["rk4"]` (`scenario.py:69`).
  `"euler"` is rejected (`tests/test_scenario.py:33`, `tests/test_m2_validation.py:887`). A custom
  integrator can be passed only through the direct `Simulator(...)` API.

## 3. State-layout documentation

All of the following agree on 6 elements (no spacecraft) and 8 elements (spacecraft):

- `docs/decisions/0007-propulsion-architecture.md`: "augmented state y = [r, v, m_prop, Δv_sensed]" and
  "M1 6-state path unchanged when no propulsion is configured".
- `docs/decisions/requests/DR-0013-…` (1A).
- `docs/decisions/requests/DR-0026-…` §1: "y = [r, v] (M1 path), or y = [r, v, m_prop, Δv_sensed] with a
  spacecraft (ADR-0007)".
- `docs/milestones/M2-propulsion.md:120`.
- `proof/records/M2-propulsion.md:37`.
- `tests/test_simulator_propulsion.py:3`.
- ADR-0004 and `docs/decisions/M1-implementation-clarifications.md` define the protocol only as
  `step(f, t, y, dt)` and state no other layout.

## 4. Tests and supported custom-integrator behaviour

- No BASE test passes a custom `Integrator` to `Simulator`.
- No BASE test hands a derivative a stage of another shape, or a list, object, masked or subclass stage.
- The only non-RK4 integrator is `_euler_step` in `tests/test_integrators.py`, ADR-0004's negative
  control. It integrates a 2-component oscillator directly and never goes through `Simulator`.
- No BASE corpus covers custom integrators. The I-44 custom-integrator corpus is new evidence, not
  an existing guarantee.

## 5. Conflicting documentation or compatibility guarantees

- None found. `docs/contracts/` holds only `m2-commands-and-events.md` (commands and events), which
  does not mention integrators.
- README, `proof/PROOF.md` and the playbooks make no API-compatibility statement about integrators or
  stage shapes.

## Findings

- **C-1 (scoping, no conflict).** I-45 says the supported stage has "exactly eight elements" and
  follows "the existing documented state layout". The documented layout has 8 elements only with a
  spacecraft; without one it has 6 (M1 path).
  - The I44-Q1 differences occur only in the coast closure, which exists only with a spacecraft.
  - The decision record and proposal therefore state the contract as 1-D float64 of size 8 **for
    derivatives built with a spacecraft** (coast and powered closures).
  - The 6-element M1 path keeps its documented layout. S1 does not change its handling of any input.
    Its derivative still makes no element read, and the I-44 corpora rows without a spacecraft are
    identical to BASE.
  - This is a statement of scope, not a new restriction. Reading "exactly eight" literally for the
    M1 path would redefine documented, supported behaviour, which I-45 §1 forbids.
- **D-1 (stale documentation, recorded only).** The `integrators.py` module docstring
  ("y = [r, v] (6 components)") predates the M2 augmented state. It does not support other shapes;
  it is merely incomplete. It is production source, so it is **not** edited under I-45 ("Do not modify
  production code"). Recorded for a later authorized change.
- **No evidence that malformed shapes were explicitly supported.** BASE behaviour on such shapes is
  incidental: a size-6 coast stage with a spacecraft commits, a (1, 8) coast stage raises `ValueError`
  from `concatenate`, and the powered closure raises `IndexError` for both. This behaviour is
  undocumented and untested, and the documented spacecraft layout excludes it. The I-45 §1 STOP
  condition is not met.
