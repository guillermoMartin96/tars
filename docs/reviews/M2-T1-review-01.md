# External Review: M2 Task T1 — standalone propulsion model

**Reviewer/model:** OpenAI Codex CLI 0.162.0, model `gpt-6.1-sol` (provider OpenAI). This is a separate provider from the implementer (Claude), as requested by the Tech Lead.  
**Session:** `01a1246e-8ad2-7280-95b3-0cd349341b19`. One session produced **two complete reviews**:
- **A:** the first response, captured when it was shown to the Tech Lead;
- **B:** the final response file.

Codex's own log was the input-wait message ("Reading additional input from stdin…") followed by two completed turns. Both reviews are kept verbatim in `raw/`.  
**Date:** 2026-10-09  
**Reviewed revision:** `de23600` (branch `milestone-2-propulsion-f90f9ba4`), reviewed as a `git archive` snapshot without git metadata, so the reviewer could not verify the SHA. The diff was `7f174fe..de23600`.  
**Scope:** T1 code and tests (`src/tars/sim/constants.py`, `src/tars/sim/propulsion.py`, `tests/test_constants.py`, `tests/test_propulsion.py`) against DR-0010…0015, ADR-0007, SCI-0008…0012, and the T1 requirements. Prompt: `raw/M2-T1-codex-prompt.md`.  
**Raw reviews:** `raw/M2-T1-codex-A.md`, `raw/M2-T1-codex-B.md`

## Summary
Both reviews give the verdict **FAIL**. They agree on what is right:
- nominal g0, Isp conversion, mass flow, F/m, the rocket equation, depletion accounting, configurable specs and the extensible direction interface match the approved model;
- 282 tests pass, lint is clean, and the architecture scan shows no violations;
- M1's event hash `7a4e1877…` reproduces.

They found numerical-boundary defects in schedule and derived-quantity validation, and, more importantly, a **test gap**: velocity tracking is not enforced. The implementer's mutation check (VAL-0011) missed the gap because the "independent" DOP853 reference shared the production right-hand side.

The two reviews' findings are consolidated below. When they disagree on severity, the higher one is used.

## Findings

### REV-T1-01 — Collapsed, non-finite, or reduced-precision burn schedules (A-F1, B-F2, B-F3 part)
**Severity:** High (A); Medium (B)  
**Reviewer claim:**
- NumPy `float32` inputs are not normalized before arithmetic. A positive-duration burn can get cutoff = ignition, or a float32-rounded cutoff off by 1.5e-5 s.
- Ignition 1e16 s with duration 1 s collapses the cutoff; ignition and duration of 1e308 give a cutoff of `inf`.

**Evidence:** reviewer reproductions in `raw/` (both reviews).  
**Affected code/Proof:** `plan_burn`; the DR-0013 requirement that event times be exact and strictly ordered.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Confirmed by reading the code. Validation checked type and finiteness but not the arithmetic result, and only two of the outputs were converted to float. A burn whose cutoff does not lie strictly after ignition, as a finite float64, cannot be integrated by step splitting.

**Resolution/evidence:** Fixed in `af4de18`.
- `plan_burn` converts every numeric input to float64 before any arithmetic.
- It rejects (`invalid_input`) any cutoff that is non-finite or not strictly after ignition.
- Tests:
  - `test_numpy_scalar_inputs_are_normalized_to_float64`: a float32 plan equals the plan from the equivalent floats, all fields are `float`, and the reviewer's 1e-5 s case now has cutoff > ignition;
  - `test_unrepresentable_cutoff_is_rejected`: ignition 1e16 s with duration 1 s, and the reviewer's 1e-308 N engine with 1e308 s values;
  - `test_depletion_time_that_underflows_the_clock_is_rejected`.
- Mutants that remove the normalization or the cutoff check fail 1 and 3 tests respectively.

---

### REV-T1-02 — Finite specifications produce invalid derived quantities (A-F2, B-F3)
**Severity:** Medium  
**Reviewer claim:**
- `EngineSpec(490, 1e308)` overflows exhaust velocity to infinity, so mass flow is 0 and the burn uses no propellant.
- `EngineSpec(1e308, 1e-308)` gives infinite mass flow and a zero-length depletion burn.

**Evidence:** reviewer reproductions.  
**Affected code/Proof:** `EngineSpec`, `SpacecraftSpec`, `plan_burn`; SCI-0008/0009/0012.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Input-level validation is necessary but not sufficient. Derived physical quantities must also be finite and positive. This is the same class as M1 audit F2.

**Resolution/evidence:** Fixed in `af4de18`.
- `EngineSpec` validates that exhaust velocity and mass flow are finite and positive.
- `SpacecraftSpec` validates the total mass.
- Tests: `test_engine_rejects_specs_with_invalid_derived_quantities` (c overflow, ṁ overflow, ṁ underflow to 0) and `test_spacecraft_rejects_overflowing_total_mass`.
- A mutant removing the mass-flow check fails 2 tests.
- Implementer correction: one test case was first written with thrust 1e-320 N. That gives a valid subnormal ṁ, so the case was corrected to 5e-324 N, which does underflow to 0.

---

### REV-T1-03 — Exactly sufficient propellant rejected or misclassified (A-F3, B-F1)
**Severity:** Medium  
**Reviewer claim:**
- With duration = 0.1 kg / ṁ, the check ṁ·duration rounds to 0.10000000000000002 kg, so the burn is rejected as insufficient.
- Under `burn_to_depletion` the same burn is labelled depleted.
- The existing boundary test (12 kg) happens to round favourably.

**Evidence:** reviewer reproductions.  
**Affected code/Proof:** `plan_burn` sufficiency rule; DR-0014 3C.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Confirmed. The sufficiency rule compared a rounded product with the loaded propellant, while the depletion duration was computed as a quotient. The two are not consistent at the boundary. The correct fix is a single, consistent boundary in the time domain (commanded duration vs depletion duration ṁ⁻¹·m_prop), with consumption clamped at the boundary. This is not a tolerance, so genuinely insufficient neighbours (one ulp longer) must still be rejected.

**Resolution/evidence:** Fixed in `af4de18`.
- A burn is sufficient iff `duration ≤ fl(propellant/ṁ)`. Consumption is `min(ṁ·duration, propellant)`.
- Tests for six propellant amounts, including the reviewer's 0.1 kg, under both policies:
  - a burn of exactly the depletion time completes and never exceeds the loaded propellant;
  - one ulp longer is rejected (`reject`) or depleted with used = loaded (`burn_to_depletion`);
  - one ulp shorter completes.
- Mutants restoring the product comparison, or removing the clamp, fail 3 and 2 tests.

---

### REV-T1-04 — Rocket-equation oracle unstable at extreme or near-equal mass ratios (A-F4, B-F4)
**Severity:** Medium  
**Reviewer claim:**
- `log(m0/mf)` overflows for 1e300/1e-300 although the result is finite.
- For mf = nextafter(1, 0) the result is wrong by a factor of 2; the stable `log1p` form gives the correct value.

**Evidence:** reviewer reproductions.  
**Affected code/Proof:** `rocket_equation_delta_v`, used as oracle O2 and for future `BurnEnded` telemetry.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Physically irrelevant at the reference case, where agreement is 6e-15. However, an oracle must not lose accuracy where a stable formulation costs nothing. Small mass changes (short burns, pulses) are a realistic future regime.

**Resolution/evidence:** Fixed in `af4de18`.
- `c·log1p((m0 − mf)/mf)`, with fallback `c·(ln m0 − ln mf)` when the ratio overflows; overflowing results are rejected.
- Test `test_rocket_equation_is_accurate_from_tiny_to_extreme_mass_ratios` compares six cases with a 50-digit `decimal` reference, at ≤ 4.5e-16 relative and `abs=0`. The cases include the reviewer's nextafter, 1e300/1e-300 and 1e308/1e-308 inputs.
- The naive-log mutant fails 5 tests.
- **Implementer finding while fixing:**
  - The near-equal case initially *passed* against the unfixed code, because `pytest.approx` adds a default absolute tolerance of 1e-12 to `rel`.
  - That floor had also weakened earlier T1 assertions on small quantities (mass flow ≈ 0.16 kg/s; propellant at 10 s).
  - All relative comparisons in `tests/test_propulsion.py` now pass `abs=0` explicitly. The previously weakened assertions still pass at their stated relative bounds.

---

### REV-T1-05 — Tests do not distinguish velocity tracking from ignition-held pointing (A-F5, B-F5)
**Severity:** High (A); Medium (B)  
**Reviewer claim:**
- Monkeypatching `Prograde.direction` to cache its first result leaves all 73 targeted tests passing.
- The direction test evaluates one state.
- The DOP853 test feeds the same production right-hand side to both integrators.
- The energy-sign check accepts inertial hold.

**Evidence:** in-memory mutation by both reviewers; no files were modified.  
**Affected code/Proof:** `tests/test_propulsion.py`; DR-0012, SCI-0011 (a 69 m SMA difference is material).

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Correct, and this is the most important finding. The implementer's mutation set (VAL-0011) did not include a stateful pointing mutant. The DOP853 cross-check was described as "independent", but its pointing law was the code under test. That claim in VAL-0011 needs correcting.

**Lesson:** an independent reference must not share the code path it is meant to check.

**Resolution/evidence:** Fixed in `af4de18` (tests).
- `test_direction_law_tracks_each_new_velocity` calls one law instance with four successive non-parallel velocities, for prograde and retrograde.
- `test_powered_arc_converges_at_fourth_order_to_independent_reference` compares production model + RK4 with DOP853 on `_independent_tracking_rhs`. That reference uses no production propulsion code: pointing `±v/√(v·v)` inline, ṁ from raw spec inputs. Convergence order over dt 20 → 10 → 5 must satisfy |p − 4| ≤ 0.5 (the DR-0008 policy), for both directions.
- **The reviewer's exact frozen-Prograde monkeypatch now fails 2 tests** (it previously passed all 73).
- VAL-0011's description of the old DOP853 test as an independent reference is corrected in the validation log.

---

### REV-T1-06 — Public helpers validate inputs incompletely (B-F6)
**Severity:** Low  
**Reviewer claim:**
- `thrust_acceleration` accepts `True` as 1 kg, and raises `TypeError` instead of `ValueError` for string mass.
- `Prograde.direction` accepts a 2-vector.
- Velocity normalization overflows or underflows for finite vectors (1e200, 1e-200).

**Evidence:** reviewer reproductions.  
**Affected code/Proof:** `thrust_acceleration`, `_velocity_unit`.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** Consistent scalar and vector validation should apply everywhere, and normalization should be scale-invariant. Low impact: no physical state reaches these magnitudes.

**Resolution/evidence:** Fixed in `af4de18`.
- `thrust_acceleration` uses the shared scalar validator, so `True`, strings and `None` raise `ValueError`.
- It checks F/m for overflow before multiplying by the vector. This avoids an inf·0 = NaN `RuntimeWarning`, which the tests run with `-W error` to catch.
- `_velocity_unit` enforces a finite 3-vector shape and pre-scales by the largest component.
- Tests cover non-numeric mass, overflow, 2-, 4- and 1×3-shaped inputs, and scales 1e200, 1e-200 and 1e-310.
- The unscaled-norm mutant fails 3 tests.

---

### Implementer observation (not raised by the reviewers) — `invalid_input` is not in the DR-0014 vocabulary
- T1 introduced the rejection code `invalid_input`, and the T1 test's allowed-set check included it.
- DR-0014 §4 lists `schema_invalid` for non-finite and malformed inputs. It has no code for a numerically valid input that cannot form a representable schedule.
- **Escalated to the Tech Lead** as a proposed vocabulary amendment rather than changed silently: keep `schema_invalid` for type/finiteness, and add `unrepresentable_schedule`, or keep a single `invalid_input`.
- Disposition: `ESCALATED_FOR_INVESTIGATION` (decision needed).

## Re-test (implementer)
At `af4de18`:
- full suite: **327 passed**;
- `ruff check` and `ruff format --check` clean (after `c48f789`, which excludes `docs/reviews/raw/` so verbatim reviewer evidence is not reformatted; CI had failed on `d07337a` for this reason);
- CI green on ubuntu-latest x86_64 and macos-latest arm64 (run 38030869877);
- M1 Proof PASS on all checks against approved thresholds, GMAT compare PASS, cross-process determinism and cross-platform bit-identical to the golden `7a4e1877…`;
- no diff to M1 simulator, runner, event, force, integrator, state or scenario code since `63bec8d`.

Mutation re-check: the reviewer's frozen-Prograde mutant and ten implementer mutants (one per fix plus the original T1 set) are each killed.

## Addendum: reviewer re-verification of fixes
**Reviewer:** the same provider, OpenAI Codex `gpt-6.1-sol`, session `01a1247c-feb7-7e13-a861-fd38967098e4`.  
**Revision:** `af4de18`, as a git-archive snapshot (no git metadata, so the reviewer could not verify the SHA).  
**Raw:** `raw/M2-T1-codex-reverify.md` (prompt: `raw/M2-T1-codex-reverify-prompt.md`).  
**Verdict:** CONDITIONAL PASS.
- The reviewer re-ran its original reproductions: 118 targeted tests and 327 in the full suite pass, and both ruff checks are clean.
- Under the frozen-Prograde mutation, 2 tests fail as expected; the orbital error stalls at about 34 m.

| Finding | Re-verification |
|---|---|
| REV-T1-01 | RESOLVED |
| REV-T1-02 | RESOLVED |
| REV-T1-03 | RESOLVED |
| REV-T1-04 | RESOLVED (independent 100-digit references agree within about 1 ulp) |
| REV-T1-05 | RESOLVED |
| REV-T1-06 | RESOLVED |

The reviewer also confirmed that the ruff exclusion keeps the verbatim evidence unchanged.

### N1 — Positive burn consumption can underflow to zero (raised in re-verification)
**Severity:** Low  
**Reviewer claim:** `plan_burn(EngineSpec(1e-308, 312), 300, 0, 1e-100)` is accepted as completed with `propellant_used_kg = 0.0`, because ṁ·duration underflows.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Same class as REV-T1-02. A burn with thrust must consume a representable, positive mass. Not a regression from the fix.  
**Resolution/evidence:** Fixed in `b015c54`. `plan_burn` rejects (`invalid_input`) a plan whose consumption is not > 0. Test `test_positive_burn_with_underflowing_consumption_is_rejected` failed before the fix and passes after. Re-test at `b015c54`: 328 passed; M1 determinism hash `7a4e1877…`; M1 Proof PASS.

### Rejection vocabulary (escalated; the reviewer concurs)
The reviewer confirms that `invalid_input` is absent from the approved DR-0014 §4 list. The test's permissive allowed-set does not amount to approval. The decision must be made before T3 freezes the command and event schemas.

## Proof gate
- [x] All Critical findings resolved (none raised)
- [x] All High findings resolved: REV-T1-01 and REV-T1-05 (`af4de18`), re-verified by the reviewer
- [x] Every substantive finding has an explicit disposition, including N1
- [x] Accepted fixes re-tested by the implementer and re-verified by the reviewer (N1 by the implementer only; it is a one-line rule with a failing-then-passing test)
- [ ] Escalated item (rejection vocabulary) has a Tech Lead decision

**Review gate result:** PASS for T1's code findings. The only open item is the escalated rejection-vocabulary decision. It does not block T1 behavior, but it must be settled before T3 defines the command/event schema.
