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

## Proof gate
- [x] All Critical findings resolved (none raised)
- [x] All High findings resolved (none raised); all Medium/Low findings fixed in `03f6e4b`
- [x] Every substantive finding has an explicit disposition
- [x] Accepted fixes re-tested by the implementer
- [ ] Reviewer re-verification (requested)
- [ ] Tech Lead confirmation of the new `EVENT_TIME_RESOLUTION_S = 1 µs` scheduling rule

**Review gate result:** BLOCKED, pending reviewer re-verification.
