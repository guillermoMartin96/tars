# External Review: M2 Task T2 — propulsion inside the simulator

**Reviewer/model:** OpenAI Codex CLI 0.162.0, model `gpt-6.1-sol`, session `01a12845-1141-7203-972c-88ef85b8afec`. This is a separate provider from the implementer (Claude).  
**Date:** 2026-10-10  
**Reviewed revision:** `ee091df` (branch `milestone-2-propulsion-f90f9ba4`), as a git-archive snapshot without git metadata. Diff `f8e62c4..ee091df`.  
**Scope:**
- T2 code and tests: `src/tars/sim/simulator.py`, the propulsion additions, `tests/test_simulator_propulsion.py`, and the extended M1 public-API allowlist test;
- ADR-0007 T2 implementation notes and VAL-0012;
- checked against DR-0013, DR-0014 (as amended), ADR-0007, SCI-0008…0012, and the architecture and testing playbooks.

**Raw:** `raw/M2-T2-codex.md`. Prompt: `raw/M2-T2-codex-prompt.md`. Reviewer probes and mutation scripts, verbatim: `raw/M2-T2-codex-scratch/`.

## Summary
**Verdict: FAIL.**

The reviewer confirmed:
- nominal physics;
- M1 preservation: it reconstructed the pre-T2 simulator, and the state bytes match with and without a spacecraft at dt = 10, 0.1 and 7/3;
- the 7a4e1877… hash and M1 Proof PASS;
- exact reproduction of VAL-0012;
- an independent DOP853 right-hand side;
- strict `abs=0` comparisons.

It found:
- one transactional defect (F1);
- schema-ordering defects in scheduling (F2);
- an extreme-input representability inconsistency between plan and integration (F3);
- mutable retained event evidence (F4);
- a test gap: transition r/v were never checked (F5).

## Findings

### REV-T2-01 — Failed steps leave the engine schedule partially advanced (F1)
**Severity:** Medium  
**Reviewer claim:**
- Engine transitions are committed before integration succeeds. If a step raises (non-finite state), tick and physical state are unchanged, but the engine is already `BURNING`.
- A retry omits the ignition and burns 3 s instead of 2 s (0.4804 kg vs 0.3203 kg).

**Evidence:** `raw/M2-T2-codex-scratch/probes.py`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. A tick must be atomic: either everything (state, tick, engine schedule, transitions) advances, or nothing does. This is the simulator-owns-reality invariant applied to the engine state.  
**Resolution/evidence:** Fixed in `03f6e4b`.
- `_step_with_propulsion` advances a local `_EngineCursor`. `step()` commits the state, tick, engine schedule and transitions together after integration succeeds.
- Test `test_a_failed_step_leaves_engine_schedule_and_state_unchanged` reproduces the reviewer's scenario (failure at t > 2 s inside a [1, 3] s burn). It checks that state and snapshot are unchanged after the failure, and that the retry burns the planned 2 s.
- A mutant sharing the live pending list fails it.

### REV-T2-02 — Scheduling classifies malformed inputs before validating them (F2)
**Severity:** Medium  
**Reviewer claim:**
- `-inf`, `"-1"`, `True`, `np.array(-1)` and `np.bool_(True)` are rejected as `ignition_in_past` instead of `schema_invalid`.
- `10**1000` raises an uncaught `OverflowError`.

**Evidence:** `raw/M2-T2-codex-scratch/probes.py`, `extra_checks.py`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. The early-ordering checks coerced with `float()` before schema validation. The DR-0014 amendment assigns non-real and non-finite inputs to `schema_invalid`, which must take precedence. The overflow also affects `plan_burn` (`math.isfinite` on a huge int).  
**Resolution/evidence:** Fixed in `03f6e4b`.
- New `burn_scalar()` is shared by `plan_burn` and `schedule_burn`: bool, str, None, arrays, numpy bools, non-finite values and float overflow all map to `schema_invalid`. It runs before the in-past and conflict checks.
- Tests:
  - nine malformed ignitions, including the reviewer's five plus `10**1000`, at t = 10 s with a scheduled burn present;
  - five malformed durations.
- Re-running the reviewer's `probes.py` now gives `schema_invalid` for every malformed input. `np.float32(1.0)` is a valid real and is correctly rejected as `ignition_in_past`.

### REV-T2-03 — Represented event interval can disagree materially with planned consumption (F3)
**Severity:** Medium  
**Reviewer claim:**
- At ignition 1e15 s, a 0.1 s burn is represented by events 0.125 s apart (the float64 time resolution at 1e15 s).
- The integration burns 0.125 s, while the plan and the committed propellant assume 0.1 s.
- In the depletion variant, the floor absorbs 0.008 kg, contradicting ADR-0007's "≤ 1e-12 kg". Sensed Δv exceeds the rocket equation.

**Evidence:** `raw/M2-T2-codex-scratch/probe_results.txt`.  
**Implementer disposition:** `ACCEPTED` (with one constant surfaced for Tech Lead confirmation; see resolution)  
**Implementer reasoning:**
- Correct. The plan must describe what is integrated. Absolute event times are float64, so the executable burn interval is `cutoff − ignition`, not the commanded real number.
- Fix: the plan's burn duration and consumption are computed from the represented interval, so plan, integration and propellant accounting agree to round-off.
- A burn whose represented interval differs materially from the intended duration is rejected as `burn_unschedulable`. "Materially" needs an explicit representability rule; see the resolution.

**Resolution/evidence:** Fixed in `03f6e4b`.
- The plan's `burn_duration_s` is `cutoff − ignition`, and consumption is `min(ṁ·burn_duration, propellant)`. Plan, integration and accounting agree to round-off.
- A burn whose represented interval differs from the intended duration by more than `EVENT_TIME_RESOLUTION_S = 1 µs` is `burn_unschedulable`. The reviewer's 1e15 s cases, both completed and depleted, are rejected. Basis: GMAT/STK stop granularity (VAL-0010), and a Δv effect below the burn's integration error. The constant is surfaced for Tech Lead confirmation (ADR-0007 T2 notes).
- Test `test_plan_describes_exactly_the_interval_that_is_integrated` covers boundary, interior and depletion cases. Integrated vs planned consumption agrees within the round-off bound.
- Mutants removing the rule, or computing consumption from the commanded duration, fail.
- T1 tests asserting `burn_duration_s == 77.3` were updated to the represented-interval contract (within 1 µs).
- VAL-0012 re-run: trajectories are bit-identical; the plan consumption reference moved by ≤ 7e-15 kg.

### REV-T2-04 — Retained transition arrays can be made writable and rewritten (F4)
**Severity:** Low  
**Reviewer claim:** `EngineTransition` arrays own their data, so a caller can set `writeable = True` and alter the simulator's retained event evidence. Physical state is unaffected.  
**Evidence:** reviewer snippet in `raw/M2-T2-codex.md`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Evidence records must be immutable (machine-readable from day one). Back the arrays with immutable storage, so the flag cannot be re-enabled.  
**Resolution/evidence:** Fixed in `03f6e4b`.
- `EngineTransition` arrays are `np.frombuffer` views of immutable `bytes`, so `flags.writeable = True` raises.
- Test `test_transition_arrays_cannot_be_made_writable`. The flag-based mutant fails it.

### REV-T2-05 — Tests do not validate transition position and velocity (F5)
**Severity:** Medium  
**Reviewer claim:** replacing the transition r and v with zeros passes all 155 targeted tests.  
**Evidence:** `raw/M2-T2-codex-scratch/mutations.py zero_transition_state`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:**
- Correct, and the same lesson as REV-T1-05: every published quantity needs a check that can fail.
- T3 will publish these states as BurnStarted/BurnEnded events.
- Fix: check transition states against the free-space closed form (zero force model) and an independent orbital DOP853 reference, at boundary, interior and multiple-event ticks, and verify that retained records stay stable.

**Resolution/evidence:** Fixed in `03f6e4b`.
- `test_transition_states_in_free_space_match_the_closed_form`: zero force; ignition and cutoff inside one tick; 40-digit closed form; velocity and position within 1e-14 relative.
- `test_transition_states_in_orbit_converge_to_independent_references`: interior ignition vs exact Kepler, and cutoff r and v vs independent DOP853, each at order 4 ± 0.5. Measured ratios are about 16.
- `test_boundary_event_state_equals_the_tick_snapshot_and_records_stay_stable`.
- The reviewer's zero-transition mutation (adapted to the refactored code) now fails 3 tests; it previously passed all 155.

## Re-test (implementer)
At `03f6e4b`:
- full suite: **384 passed**; T2/T1 targeted suites pass with `-W error`; ruff check and format clean;
- M1 Proof PASS on all checks; GMAT compare PASS;
- cross-process determinism and cross-platform bit-identical to the golden `7a4e1877…`.

Mutation re-check: the reviewer's four mutations (zero transition state, double sensed Δv, constant mass, no interior splits) and one mutant per fix are each killed.

## Addendum: reviewer re-verification of fixes (`da43487`)
**Reviewer:** the same provider, OpenAI Codex `gpt-6.1-sol`, session `01a1284e-43c0-74e1-b2fd-a36cbbf49f5d`.  
**Raw:** `raw/M2-T2-codex-reverify.md`; prompt and scripts are alongside.  
**Verdict:** FAIL.

| Finding | Re-verification |
|---|---|
| REV-T2-01 | RESOLVED. The reviewer also tested exceptions from force, direction law and `thrust_acceleration`. |
| REV-T2-02 | PARTIAL: integers beyond the repr limit (N2) |
| REV-T2-03 | PARTIAL: depletion boundary and justification of the 1 µs rule (N1) |
| REV-T2-04 | RESOLVED |
| REV-T2-05 | RESOLVED; retrograde and multi-burn coverage gap (N3) |

### N1 — Representability tolerance permits burning beyond depletion
**Severity:** Medium  
**Reviewer claim:**
- Sufficiency was checked before interval rounding. At ignition 1e9 s with an exact-depletion command, the represented interval exceeds depletion by 2.4e-8 s.
- With a 1e-10 kg dry mass, the total mass goes negative mid-burn.
- Separately, the absolute 1 µs bound is not a sufficiently justified universal rule. Escalate a DR covering timing fidelity, depletion semantics and error budgets.

**Implementer disposition:**
- Executed-past-depletion defect: `ACCEPTED`.
- Representability rule: `ESCALATED_FOR_INVESTIGATION` (**DR-0017**).

**Implementer reasoning:**
- Executing past depletion violates SCI-0012 (propellant never negative); this is fixable within approved semantics.
- The choice of acceptance rule (absolute time, Δv budget, relative bound, or an exact time base) is a fidelity decision with tradeoffs, so it goes to the Tech Lead with options. The provisional 1 µs rule stays until then.

**Resolution/evidence:** Fixed in `9789603`.
- If rounding the cutoff overshoots depletion, `plan_burn` steps it back to the latest representable time not after depletion.
- Tests:
  - `test_executed_interval_never_exceeds_the_depletion_time`: ignition 0, 1, 605.5, 1e6 and 1e9 s under both policies;
  - `test_boundary_burn_at_large_time_executes_without_negative_mass`: the reviewer's case with a 1e-10 kg dry mass and zero force at t ≈ 1e9 s. Propellant stays ≥ 0 at every tick and ends at the plan's remainder (~1.5e-8 kg).
- A mutant removing the step-down fails 8 tests.
- The T1 depletion test now asserts the bounding contract (cutoff ≤ ignition + t_dep).

### N2 — Formatting schema-rejection details can itself raise
**Severity:** Medium  
**Reviewer claim:** `schedule_burn("prograde", 10**10000, 1)` raises Python's integer-string-limit `ValueError` instead of a structured rejection.  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `9789603`.
- Rejection details use `_describe()`: bounded and exception-safe, with huge ints described by bit length.
- Test `test_integers_beyond_the_repr_limit_are_schema_invalid` covers ignition and duration in `schedule_burn`, and propellant in `plan_burn`. The unsafe-repr mutant fails 2 tests.
- **Also fixed (seen in the reviewer's evidence):** an invalid `policy` combined with a past ignition returned `ignition_in_past`. Policy is now validated with the schema checks first (`test_invalid_policy_is_schema_invalid_before_chronology`).

### N3 — Transition-state tests miss retrograde and multiple-burn evidence
**Severity:** Low  
**Reviewer claim:** a mutant zeroing only retrograde transition r and v survives all 178 targeted tests.  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Tests added in `9789603`:
- `test_back_to_back_prograde_then_retrograde_transitions_match_free_space`: four transitions including the shared 604 s instant, against a 40-digit closed form;
- `test_orbital_transition_states_converge_in_both_directions`: ignition and cutoff r and v, order 4 ± 0.5.

The reviewer's retrograde-only zero-state mutant now fails 2 tests.

**Re-test at `9789603`:**
- 401 tests pass; ruff check and format clean;
- M1 Proof PASS; GMAT compare PASS;
- determinism and cross-platform bit-identical to `7a4e1877…`;
- VAL-0012 `results.json` unchanged.

## Proof gate
- [x] All Critical findings resolved (none raised)
- [x] All High findings resolved (none raised)
- [x] Every substantive finding has an explicit disposition, including N1–N3
- [x] Accepted fixes re-tested by the implementer (`9789603`)
- [ ] Reviewer re-verification of the N1–N3 fixes (requested)
- [ ] DR-0017 decision on the representability rule (escalated)

**Review gate result:** BLOCKED, pending the N1–N3 re-verification and DR-0017. T2 functionality is otherwise complete; only the representability acceptance rule is provisional.
