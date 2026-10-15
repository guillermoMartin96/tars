| Finding | Status | Evidence |
|---|---|---|
| REV-T2-01 | **RESOLVED** | Original NaN failure/retry now burns the planned two seconds. Force, direction-law and `thrust_acceleration` exceptions preserve state, tick, schedule, propellant reservation and transitions. A later failed tick also preserves prior event records. |
| REV-T2-02 | **PARTIAL** | All original malformed inputs, including `10**1000`, return `schema_invalid`. Expanded checks pass for idle, pending and active schedules and all four numeric `plan_burn` inputs. Larger integers still escape; see N2. |
| REV-T2-03 | **PARTIAL** | Both original `1e15` cases now return `burn_unschedulable`. Ordinary completed plans use represented duration consistently. Rounded depletion and exactly-sufficient boundaries still permit physically excessive burn intervals; see N1. |
| REV-T2-04 | **RESOLVED** | Both transition arrays have immutable `bytes` backing. Re-enabling writing raises `ValueError`; retained evidence cannot be rewritten through the original attack. |
| REV-T2-05 | **RESOLVED** | Adapted zero-transition-state mutant now fails **3 tests**. Analytic, orbital-convergence and boundary/stability checks materially improve coverage. Multiple-burn and retrograde coverage remains incomplete; see N3. |

### N1 — Representability tolerance permits burning beyond depletion
**Severity:** Medium  
**Claim:** Sufficiency is checked before interval rounding. The represented interval can exceed depletion, while planned consumption is capped at available propellant. Cutoff flooring cannot prevent negative intermediate mass.

**Evidence:** With the reference engine, ignition `1e9`, tank `ṁ × 0.1`, and commanded duration `tank / ṁ`, the default `reject` policy accepts:

- Represented duration: `0.10000002384185791 s`.
- Planned consumption: `0.01601477385766618 kg`.
- Excess integrated consumption: `3.818219629359021e-9 kg`.

With an accepted dry mass of `1e-10 kg`, RK4 raises `PropulsionSpecError` because total mass becomes `-3.718219629359021e-9 kg` before cutoff. Rollback succeeds, but the accepted plan cannot execute.

The absolute tolerance also accepts a burn at ignition `1 s` with intended duration `1.2e-16 s` as `2.220446049250313e-16 s`—approximately **85% longer**. Evidence: `review_scratch/edge_fail.txt` and `review_scratch/reverify.txt`.

**Suggested fix:** Recheck represented duration against depletion. Reject physically unrepresentable boundaries or choose a documented conservative cutoff; enforce depletion during propagation. Add nonzero-ignition sufficiency/depletion tests and a relative fidelity constraint.

### N2 — Formatting schema-rejection details can itself raise
**Severity:** Medium  
**Claim:** `burn_scalar()` catches conversion overflow, then interpolates the original value into its error message. That interpolation can fail, bypassing the structured rejection.

**Evidence:** `schedule_burn("prograde", 10**10000, 1)` raises an ordinary `ValueError` about Python’s 4,300-digit integer-string limit instead of `BurnRejectedError(SCHEMA_INVALID)`. See `review_scratch/reverify.txt`.

**Suggested fix:** Use bounded, exception-safe diagnostics or omit the offending value. Test integers exceeding the representation limit across numeric command fields.

### N3 — Transition-state tests still miss retrograde and multiple-burn evidence
**Severity:** Low  
**Claim:** The new numerical transition checks exercise single prograde burns. Existing back-to-back tests check event ordering without validating their translational states.

**Evidence:** A mutant zeroing only retrograde transition `r` and `v` survives **all 178 targeted tests**, including back-to-back burns. See `review_scratch/mutation_retrograde_transition_state.txt`.

**Suggested fix:** Check every transition against an independent oracle across several burns, including a shared cutoff/ignition boundary and retrograde thrust. Also validate orbital ignition velocity and retained cutoff records.

The **1 µs constant is plausible as a reference-case timing budget, but insufficiently justified as a universal physics rule**. VAL-0010 supports GMAT stop-step rounding; it does not establish TARS acceptance semantics. Integration error decreases with timestep, engine and mass values are configurable, and an absolute tolerance does not bound relative error for tiny burns. Escalate a decision request covering timing fidelity, depletion semantics and physical error budgets—not merely confirmation of the constant.

**FAIL** — Ran full pytest (**384 passed**), both ruff checks (**passed**), determinism (**`7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`**), all four original mutants (**3/1/5/14 failures**), adapted original and expanded probes, VAL-0012 reproduction, and archived M1 coast comparisons. Only `review_scratch/` was written; the supplied revision identity could not be independently verified because Git metadata is absent.