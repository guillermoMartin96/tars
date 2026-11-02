# I-59 per-mutant kill classification (I-40 §10)

Classes per failing designated node: **A** assertion failure; **B** assertion that validates an expected exception (the assertion names it); **C** unasserted exception / harness error / missing node. Only A and B count, and every failure must also match the mutant's declared reason. Edits and designated nodes are identical in both runs (checked below).

| Mutant | E, original harness (I-52 patterns) | E, strict I-40 §10 | H, corrected harness | H, strict I-40 §10 | Failing nodes E → H |
|---|---|---|---|---|---|
| M-01 adapter copies r | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-02 adapter swaps r and v | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-03 adapter copies the result | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-04 adapter calls twice | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-05 adapter wraps exceptions | KILLED 4/5 | NOT_KILLED_I40_10 (A=0 B=0 C=4) | KILLED 4/5 | KILLED_I40_10 (A=0 B=4 C=0) | same |
| M-06 powered context from committed state | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-06c coast context from committed state | KILLED 3/3 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/3 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-07 powered dry mass only | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-07c coast dry mass only | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-08 coast no clamp | KILLED 1/2 | KILLED_I40_10 (A=1 B=0 C=0) | KILLED 1/2 | KILLED_I40_10 (A=1 B=0 C=0) | same |
| M-09 powered context cached per sub-step | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-10 mutable context | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | same |
| M-11 unowned mass (np.float64 kept) | KILLED 5/5 | KILLED_I40_10 (A=5 B=0 C=0) | KILLED 5/5 | KILLED_I40_10 (A=5 B=0 C=0) | same |
| M-12 validation removed | KILLED 14/14 | KILLED_I40_10 (A=14 B=0 C=0) | KILLED 14/14 | KILLED_I40_10 (A=14 B=0 C=0) | same |
| M-13 massless path gets 0.0 | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | same |
| M-14 powered context before the finiteness check | KILLED 2/3 | NOT_KILLED_I40_10 (A=0 B=0 C=2) | KILLED 2/3 | KILLED_I40_10 (A=0 B=2 C=0) | same |
| M-15 force call before thrust_acceleration | KILLED 1/1 | NOT_KILLED_I40_10 (A=0 B=0 C=1) | KILLED 1/1 | KILLED_I40_10 (A=0 B=1 C=0) | same |
| M-16 coast validates at construction (option A) | KILLED 4/4 | NOT_KILLED_I40_10 (A=1 B=0 C=3) | KILLED 4/4 | KILLED_I40_10 (A=1 B=3 C=0) | same |
| M-17 coast repairs NaN (max argument order swapped) | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | KILLED 1/1 | KILLED_I40_10 (A=1 B=0 C=0) | same |
| M-18 coast passes absent mass | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | KILLED 3/4 | KILLED_I40_10 (A=3 B=0 C=0) | same |
| M-19 powered context deferred (expected equivalent) | SURVIVED (expected equivalent) 0/90 | EQUIVALENT_SURVIVED (A=0 B=0 C=0) | SURVIVED (expected equivalent) 0/100 | EQUIVALENT_SURVIVED (A=0 B=0 C=0) | same |
| M-20 premature subclass-sensitive coast read (v2) | KILLED 4/4 | NOT_KILLED_I40_10 (A=0 B=0 C=4) | KILLED 4/4 | KILLED_I40_10 (A=0 B=4 C=0) | same |
| M-21 lazy stage reference, dispatching read (v3-L) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-21b lazy stage reference, base-class read | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |
| M-22 powered lazy stage reference (v3-L machinery, powered path only) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | KILLED 4/4 | KILLED_I40_10 (A=4 B=0 C=0) | same |

Edits and designated nodes identical for all 25 mutants (E original vs H corrected): **True**. M-19's total grows 90 → 100 because its designated nodes are the two whole S1 files, which gained the 10 S1R-01 nodes.

Corrected harness at E (same harness, E's tests): {"KILLED_I40_10": 19, "NOT_KILLED_I40_10": 5, "EQUIVALENT_SURVIVED": 1} — **E does not meet the corrected criterion.**

## Assertion evidence for the five mutants changed by I-59 (H, corrected harness)

### M-05 adapter wraps exceptions
- declared reason: `^AssertionError: expected the identical \w+, got RuntimeError: x\b`
- `test_t02_adapter_propagates_the_identical_exception[exc0]` class B: `AssertionError: expected the identical ValueError, got RuntimeError: x`
- `test_t02_adapter_propagates_the_identical_exception[exc1]` class B: `AssertionError: expected the identical FloatingPointError, got RuntimeError: x`
- `test_t02_adapter_propagates_the_identical_exception[exc2]` class B: `AssertionError: expected the identical OverflowError, got RuntimeError: x`
- `test_t02_adapter_propagates_the_identical_exception[exc3]` class B: `AssertionError: expected the identical ZeroDivisionError, got RuntimeError: x`
- at E: C: RuntimeError: x

### M-14 powered context before the finiteness check
- declared reason: `^AssertionError: expected FloatingPointError matching .*, got ValueError: total_mass_kg must be finite and positive`
- `test_t07_k_finiteness_check_precedes_powered_context_construction[nan]` class B: `AssertionError: expected FloatingPointError matching '^non-finite state during a burn at t = 2\\.0$', got ValueError: total_mass_kg must be finite and positive, got nan`
- `test_t07_k_finiteness_check_precedes_powered_context_construction[inf]` class B: `AssertionError: expected FloatingPointError matching '^non-finite state during a burn at t = 2\\.0$', got ValueError: total_mass_kg must be finite and positive, got inf`
- at E: C: ValueError: total_mass_kg must be finite and positive, got inf; C: ValueError: total_mass_kg must be finite and positive, got nan

### M-15 force call before thrust_acceleration
- declared reason: `^AssertionError: expected ValueError matching .*, got RuntimeError: force\b`
- `test_t07_g_pointing_law_error_precedes_the_force_model` class B: `AssertionError: expected ValueError matching '^velocity-tracking direction is undefined for zero velocity$', got RuntimeError: force`
- at E: C: RuntimeError: force

### M-16 coast validates at construction (option A)
- declared reason: `^AssertionError: .*total_mass_kg must be finite and positive`
- `test_t07_i_finite_dt_with_overflowing_tick_end_is_non_finite[1e+308]` class B: `AssertionError: expected FloatingPointError matching '^non-finite state produced at tick 2$', got ValueError: total_mass_kg must be finite and positive, got nan`
- `test_t07_i_finite_dt_with_overflowing_tick_end_is_non_finite[8.98846567431158e+307]` class B: `AssertionError: expected FloatingPointError matching '^non-finite state produced at tick 2$', got ValueError: total_mass_kg must be finite and positive, got nan`
- `test_t07_a_infinite_dt_coast_point_mass_is_non_finite` class B: `AssertionError: expected FloatingPointError matching '^non-finite state produced at tick 1$', got ValueError: total_mass_kg must be finite and positive, got nan`
- `test_t07_b_infinite_dt_coast_point_mass_and_j2_fails_in_j2` class A: `AssertionError: `
- at E: A: AssertionError: ; C: ValueError: total_mass_kg must be finite and positive, got nan

### M-20 premature subclass-sensitive coast read (v2)
- declared reason: `^Failed: raised (UserWarning: Warning: converting a masked element to nan|LookupError: stage propellant read through the subclass|ValueError: total_mass_kg must be finite and positive, got nan)`
- `test_t07_l_coast_closure_does_not_read_the_stage_through_a_subclass[masked_propellant]` class B: `Failed: raised UserWarning: Warning: converting a masked element to nan.`
- `test_t07_l_coast_closure_does_not_read_the_stage_through_a_subclass[raising_getitem]` class B: `Failed: raised LookupError: stage propellant read through the subclass`
- `test_t04_coast_mass_is_the_stored_propellant_of_a_subclass_stage[masked_propellant]` class B: `Failed: raised ValueError: total_mass_kg must be finite and positive, got nan`
- `test_t04_coast_mass_is_the_stored_propellant_of_a_subclass_stage[raising_getitem]` class B: `Failed: raised LookupError: stage propellant read through the subclass`
- at E: C: LookupError: stage propellant read through the subclass; C: UserWarning: Warning: converting a masked element to nan.; C: ValueError: total_mass_kg must be finite and positive, got nan

