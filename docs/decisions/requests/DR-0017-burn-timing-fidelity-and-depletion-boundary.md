# Decision Request: Burn timing fidelity (event-time representability) and depletion boundary

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-10  
**Related milestone/issue:** M2 T2; external review M2-T2-review-01 (REV-T2-03, re-verification N1); DR-0013 3A; DR-0014; SCI-0012

## Problem
Engine events are absolute float64 times, while simulation time is `tick·dt` (ADR-0002). The engine therefore runs for the **represented interval** `D = fl(ignition + duration) − ignition`, not the commanded real duration `d`.
- **Typical mission times:** |D − d| is ≈ 1e-14 s at t ≈ 600 s and ≈ 1e-7 s at t ≈ 1e9 s, which is negligible.
- **Extreme times:** it is material. At t = 1e15 s, float64 times are 0.125 s apart, so a 0.1 s burn runs 0.125 s.

T2 must decide which burns are acceptable and how the depletion boundary is executed. The reviewer judged the provisional rule plausible but insufficiently justified as a universal rule, and recommended this DR, rather than a request to confirm the constant.

## Current implementation (provisional, `87f217d`)
1. **Plan = executed interval, for both outcomes.** `burn_duration_s = D`, and consumption = `min(ṁ·D, propellant)`. Plan, integration and accounting agree to round-off (REV-T2-03, N5).
2. **Never past depletion.** If rounding puts the cutoff after the depletion time, it steps back to the latest representable time not after depletion.
   - A `burn_to_depletion` burn can then leave a residual of at most ṁ·2·ulp(cutoff) (≈ 1e-14 kg at mission times; 1.5e-8 kg at t = 1e9 s). The residual is **retained**, not discarded (N1, N5).
   - RK4 stages use the non-negative physical propellant (N4).
3. **Representability bound.** Reject (`burn_unschedulable`) if |D − d| > `EVENT_TIME_RESOLUTION_S = 1 µs`.

Items 1–2 follow from approved decisions (DR-0013 3A; SCI-0012, "propellant never negative"). **Item 3, and the depletion-residual semantics in item 2, are the subject of this DR.** The basis for item 3:
- 1 µs is the GMAT/STK stop-time granularity (VAL-0010);
- for the reference engine its Δv effect (≈ 4e-7 m/s) is below the burn's integration velocity error at dt = 10 s (1.2e-6 m/s, VAL-0008).

## Constraints
- Never invent physics; tolerances must be justified (playbook/testing.md).
- Deterministic; M1 untouched; approved rejection vocabulary (`burn_unschedulable`).
- Must be checkable before execution, when the burn is scheduled.

## Options
### A — Absolute time bound |D − d| ≤ 1 µs (current provisional)
**Pros**
- Simple and matches external-tool granularity.

**Cons**
- Not engine-aware. A high-thrust, low-mass vehicle could accumulate a larger Δv error within 1 µs.
- Says nothing about physical significance.

### B — Δv-error budget (recommended)
**Rule:** reject if `a_max · |D − d| > Δv_budget`.
- **Budget scope:** the budget is **per burn** and is an **absolute allocation**, not a cumulative mission budget.
- **Definition of `a_max`:** `a_max = F / m_min`, where `m_min` is the smallest total mass reached over **both** the intended and the represented interval. That is dry mass + propellant remaining after the longer of the two, with propellant accounted after all previously accepted burns.
- **Implementation:** `plan_burn` does not receive dry mass today. B therefore needs the check in `Simulator.schedule_burn`, which knows the spacecraft and the queue, or a mass argument to `plan_burn`. It is small, but more than a one-line predicate.
- **Proposed value: `Δv_budget = 1e-7 m/s`, per burn.** It is about 10× below the reference burn's integration velocity error at dt = 10 s (1.2e-6 m/s, VAL-0008).
  - This is a proposed allocation, not a proof that timing representation is never dominant.
  - At finer dt, or for other engines, integration error can fall below 1e-7 m/s. The budget must be revisited if dt, the engine envelope, or mission accuracy requirements change.
  - No mission-level accuracy requirement exists yet against which to derive it.

**Scope limit:** the rule bounds the *thrust-integrated speed change* caused by timing. It does **not** by itself bound trajectory error. Pointing (velocity-tracking) and gravity act over the mistimed interval, so the trajectory effect also depends on duration and geometry. For the reference case the timing-induced trajectory error is far below the RK4 error (VAL-0012), but that is a measured case, not a general bound.

**Pros**
- Physically meaningful and engine-aware.
- Tiny burns are judged by their real effect: the reviewer's 85 % example has a Δv effect of ~1e-17 m/s and is accepted correctly.
- Reference case: accepted up to t ≈ 2e9 s (≈ 60 years); the 1e15 s case is rejected.

**Cons**
- Needs a budget value with no mission-level requirement to derive it from yet.
- Tied to the dt = 10 s reference accuracy.
- Bounds Δv, not trajectory error.

### C — Relative bound |D − d| ≤ ε·d, plus a minimum burn duration
**Pros**
- Bounds relative timing error.

**Cons**
- Two new numbers.
- Rejects physically irrelevant tiny burns.
- A minimum on-time would need engine research (minimum impulse bit) that has not been done.

### D — Exact event times: integer time base (e.g. int64 ns), or events constrained to a representable grid
**Pros**
- Eliminates representation error.

**Cons**
- Changes ADR-0002's time representation (architecture change).
- Large effort; interplay with GMAT alignment (DR-0016).
- Disproportionate for M2.

### Depletion boundary (part of this decision)
- **D1a (recommended; current):** step the cutoff back to the latest representable time not after depletion. Consumption follows the executed interval, and the residual (≤ ṁ·2·ulp(cutoff)) is retained in the tank. Plan = execution exactly, never negative. The burn is labelled `propellant_depleted` (depleted to within time resolution).
- **D1b:** as D1a, but snap the tank to exactly 0 at a depletion cutoff. "Empty means empty", but the integrated and planned accounting then differ by up to ṁ·2·ulp(cutoff), and unburned propellant is discarded. This was the earlier behavior that review N5 objected to.
- **D2:** reject burns whose represented interval would cross depletion. Simpler, but it rejects ordinary exact-depletion commands at some ignition times purely because of rounding.

## Recommendation
**B (Δv-error budget, 1e-7 m/s per burn, `a_max` over intended and represented intervals) + D1a.**
- B replaces the provisional absolute 1 µs bound.
- If B is approved, the change is contained: the check moves into `schedule_burn`, which has the mass and queue information, plus boundary tests on both sides and a SCI-0012 note on the depletion residual.
- Also record explicitly that B bounds timing-induced Δv, not trajectory error.

## Impact
- Architecture: none (B, D1a). D would change ADR-0002.
- Science/validation: timing representation provably sub-dominant to integration error; depletion semantics explicit.
- Dependencies: none.
- Effort: small (B, with the check moved into schedule_burn; D1a is already implemented); large (D).
- Reversibility: high.

## Blocked work
- Final sign-off of the representability rule in T2. The rest of T2 is complete. The provisional 1 µs rule stays in place until this decision.

## Work continuing independently
- T3 command/event schema: the rejection codes are already approved. T4 onward when authorized.

## Requested response
`B + D1a` / `A + D1a` / `… + D1b` / `… + D2` / `C …` / `D` / `discuss`; and the budget value and scope if B.

## Resolution
**Decision:** <fill after response>  
**Reasoning/notes:** ...  
**Follow-up:** ...
