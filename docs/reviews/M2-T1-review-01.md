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

**Resolution/evidence:** pending (to cite the fix commit).

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

**Resolution/evidence:** pending.

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

**Resolution/evidence:** pending.

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

**Resolution/evidence:** pending.

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

**Resolution/evidence:** pending.

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

**Resolution/evidence:** pending.

---

### Implementer observation (not raised by the reviewers) — `invalid_input` is not in the DR-0014 vocabulary
- T1 introduced the rejection code `invalid_input`, and the T1 test's allowed-set check included it.
- DR-0014 §4 lists `schema_invalid` for non-finite and malformed inputs. It has no code for a numerically valid input that cannot form a representable schedule.
- **Escalated to the Tech Lead** as a proposed vocabulary amendment rather than changed silently: keep `schema_invalid` for type/finiteness, and add `unrepresentable_schedule`, or keep a single `invalid_input`.
- Disposition: `ESCALATED_FOR_INVESTIGATION` (decision needed).

## Proof gate
- [ ] All Critical findings resolved (none raised)
- [ ] All High findings resolved (REV-T1-01, REV-T1-05)
- [x] Every substantive finding has an explicit disposition
- [ ] Accepted fixes have been re-tested
- [ ] Escalated items have a Tech Lead decision (rejection vocabulary)

**Review gate result:** BLOCKED. Fixes are in progress; this record will be updated with commit evidence.
