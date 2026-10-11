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

## Current implementation (provisional, `9789603`)
1. **Plan = executed interval.** `burn_duration_s = D`, and consumption = `min(ṁ·D, propellant)`. Plan, integration and accounting agree to round-off (REV-T2-03).
2. **Never past depletion.** If rounding puts the cutoff after the depletion time, the cutoff steps back to the latest representable time not after depletion. Propellant never goes negative; a residual of at most ṁ·ulp(t) can remain (N1).
3. **Representability bound.** Reject (`burn_unschedulable`) if |D − d| > `EVENT_TIME_RESOLUTION_S = 1 µs`.

Items 1–2 follow directly from approved decisions (DR-0013 3A; SCI-0012, "propellant never negative"). **Item 3 is a new acceptance rule, and it is the subject of this DR.** Its current basis:
- 1 µs is the stop-time granularity GMAT and STK use (VAL-0010);
- for the reference engine, its Δv effect (≈ 4e-7 m/s) is below the burn's integration error at dt = 10 s (1.2e-6 m/s, VAL-0008).

Reviewer critique (`raw/M2-T2-codex-reverify.md`):
- GMAT granularity does not establish TARS acceptance semantics;
- engines and masses are configurable;
- integration error shrinks with dt;
- an absolute bound does not bound relative error for tiny burns. For example, 1.2e-16 s at t = 1 s is represented as 2.2e-16 s, 85 % longer, although the Δv effect is ~1e-17 m/s.

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
- Reject if `a_max · |D − d| > Δv_budget`, where `a_max = F/m_min` is the largest thrust acceleration during the burn (at end mass).
- Proposed `Δv_budget = 1e-7 m/s`: about 10× below the reference burn's own integration velocity error at dt = 10 s (1.2e-6 m/s, VAL-0008), so timing representation is never the dominant error.

**Pros**
- Physically meaningful and engine-aware.
- Tiny burns are judged by their real effect, so the reviewer's 85 % example is accepted correctly: its Δv effect is ~1e-17 m/s.
- Reference case: accepted at every mission time up to t ≈ 2e9 s; the 1e15 s case is rejected.

**Cons**
- Needs a budget value (proposed above).
- The budget is tied to a dt = 10 s integration error and would need revisiting if dt or accuracy requirements change.

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
- **D1 (recommended; current):** step the cutoff back to the latest representable time not after depletion. The burn is labelled by its policy outcome. A residual of at most ṁ·ulp(t) may remain. It is conservative and never negative.
- **D2:** reject burns whose represented interval would cross depletion. Simpler, but it rejects ordinary exact-depletion commands at some ignition times purely because of rounding.

## Recommendation
**B (Δv-error budget, 1e-7 m/s) + D1**, replacing the provisional absolute 1 µs bound. If B is approved, the change is local: one predicate in `plan_burn`, tests of the boundary on both sides, and a SCI-0012 note on the depletion residual.

## Impact
- Architecture: none (B, D1). D would change ADR-0002.
- Science/validation: timing representation provably sub-dominant to integration error; depletion semantics explicit.
- Dependencies: none.
- Effort: small (B/D1); large (D).
- Reversibility: high.

## Blocked work
- Final sign-off of the representability rule in T2. The rest of T2 is complete. The provisional 1 µs rule stays in place until this decision.

## Work continuing independently
- T3 command/event schema: the rejection codes are already approved. T4 onward when authorized.

## Requested response
`B + D1` / `A + D1` / `C …` / `D` / `D2 instead of D1` / `discuss`; and the budget value if B.

## Resolution
**Decision:** <fill after response>  
**Reasoning/notes:** ...  
**Follow-up:** ...
