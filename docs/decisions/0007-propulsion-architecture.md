# ADR-0007: Propulsion architecture (separate subsystem, augmented state, engine-event step splitting)

**Status:** Accepted  
**Date:** 2026-10-09  
**Decision owners:** Guillermo (Tech Lead, via DR-0011, DR-0012, DR-0013, DR-0014); implementing engineer

## Context
Thrust is the first force that depends on spacecraft mass. It also switches on and off at commanded times and changes simulator-owned state other than r and v. That hits the reconsider triggers in ADR-0003 ("a force needs state beyond (t, r, v)") and ADR-0004/DR-0008 ("revisit dt when finite burns arrive"). VAL-0008 measured that RK4 must not straddle an engine cutoff: doing so gave a 168 km error, against 0.290 m with splitting.

## Options considered
See DR-0013 (state, derivative boundary, discontinuity handling, M1 preservation, read-only views), DR-0012 (direction) and DR-0014 (commands).

## Decision
- **Separate propulsion subsystem** `tars.sim.propulsion`. The `ForceModel` protocol, `PointMassGravity`, `RK4` and `StateSnapshot` are unchanged. ADR-0003's trigger is answered by adding a subsystem, not by widening the protocol.
- **Model** (DR-0011): constant thrust F and Isp; ṁ = F/(Isp·g0) with `STANDARD_GRAVITY = 9.80665` m/s² in `tars.sim.constants`; thrust acceleration F/(m_dry + m_prop) along a unit direction.
- **Configurable specs** (DR-0010): engine and tank values are inputs (`EngineSpec`, `TankSpec`). The R-4D-11-class reference values live in scenarios and tests, never in physics code.
- **Direction interface** (DR-0012): a `DirectionLaw` protocol maps read-only (t, r, v) to a unit vector. `Prograde` and `Retrograde` (velocity-tracking, GMAT VNB ±V) are the M2 implementations. Future guidance modes add implementations.
- **Burn representation** (DR-0014): an immutable `BurnPlan` holds ignition time, commanded duration, cutoff time, the propellant it will use, and how it ends (`completed` | `propellant_depleted`). It is computed exactly in advance from the specs, so the simulator can split RK4 ticks at those times (DR-0013 3A).
  - Insufficient propellant is rejected by default.
  - `burn_to_depletion` must be requested explicitly.
- **Integration** (T2, implemented in `f4b9774`):
  - augmented state y = [r, v, m_prop, Δv_sensed];
  - ticks split at engine events;
  - M1 6-state path unchanged when no propulsion is configured.

## Implementation notes (T2, `f4b9774`)
These clarify how T2 implements the approved decisions.

**Approved by the Tech Lead on 2026-10-10 as deliberate M2 design constraints, not universal requirements:**
- submission-order scheduling only (M2);
- `schedule_burn` plus two read-only propulsion views in the public API;
- the propellant floor applied at cutoff;
- plans report executed intervals while preserving commanded intervals for audit.

Any of these may be revisited by a later decision.
- **Single command entry point.** `Simulator.schedule_burn(direction, ignition_t_s, duration_s, policy)` is the engine-level entry point (DR-0013 §5). It changes only the engine schedule, never r, v, mass or propellant. T3's `submit(BurnCommand) -> CommandReceipt` will wrap it, so there remains a single entry point. M1's public-API allowlist test was extended for this method and two read-only views (`propulsion_snapshot`, `engine_transitions`).
- **Burn ordering on one engine.** Burns execute in submission order. A new burn may not ignite before the cutoff of any burn already scheduled or in progress:
  - `engine_busy` if the conflict is with the burn in progress;
  - `overlaps_scheduled_burn` otherwise, including a burn that would fit in an earlier gap.
  - This keeps every accepted plan exact and immutable, since later plans were computed from the propellant left by earlier ones. Gap insertion would need re-planning and is not supported.
- **Propellant accounting.** Sufficiency is checked against the analytic propellant remaining after all accepted burns. The integrated propellant tracks it to round-off (≤ 3e-13 kg, VAL-0012).
- **Represented burn interval (REV-T2-03, `03f6e4b`).** Event times are absolute float64 values, so the engine runs for exactly `cutoff − ignition`. The plan's `burn_duration_s` and consumption describe that represented interval.
  - **Timing budget (DR-0017 B, `0e64717`; conservative evaluation after review M2-DR0017).** This replaces the provisional 1 µs bound.
    - A burn is `burn_unschedulable` if the exact rocket-equation Δv difference between the executed and intended intervals exceeds `TIMING_DELTA_V_BUDGET_MPS = 1e-7 m/s` per burn.
    - `timing_delta_v_error_mps()` gives a **conservative upper estimate** of `c·|ln(m(D)/m(d))|`, evaluated as `c·log1p((F/m_end)·|D − d|/c)`, and the plan records it:
      - `m_end` is a lower bound on the smaller end mass, with the cancellation uncertainty subtracted;
      - forming `F/m_end` first avoids underflow;
      - a small relative inflation covers residual rounding;
      - overflow rejects.
    - `schedule_burn` always applies it with the spacecraft's dry mass.
    - It bounds Δv, not trajectory error.
  - **Never past depletion (N1, `9789603`; N4/N5, `87f217d`):** if rounding puts the cutoff after the depletion time, it steps back to the latest representable time not after depletion.
    - Consumption follows the executed interval for both outcomes, and the residual (≤ ṁ·2·ulp(cutoff)) is retained.
    - RK4 stages use the non-negative propellant.
    - Retain vs snap-to-empty is a DR-0017 choice (D1a vs D1b).
- **Propellant floor (SCI-0012).** At a cutoff whose plan uses the entire tank, the integrated propellant is set to exactly 0. Otherwise it is clamped at ≥ 0.
  - The floor only corrects integration round-off: ≤ 3e-13 kg measured at mission times (VAL-0012).
  - It is separate from the D1a timing residual. A depletion cutoff stepped back before depletion leaves a positive residual (≤ ṁ·2·ulp(cutoff)), which is **retained**, not absorbed. Its Δv effect is bounded by the DR-0017 budget.
  - This is the only point where the simulator adjusts an integrated value, and it enforces a physical constraint.
- **Atomic ticks (REV-T2-01, `03f6e4b`).** The engine schedule advances on a local cursor within a tick and is committed together with the state only when integration succeeds. A failed step changes nothing.
- **Schema first (REV-T2-02).** `schedule_burn` validates ignition and duration (`burn_scalar`) before chronology and engine-conflict checks.
- **Ticks without engine events** integrate exactly `h = dt`, as M1 does. Coasts are therefore bit-identical to the M1 path for any dt (tested at dt = 10, 0.1, 7/3).
- **Event times** are exact floats. A tick containing events is split into RK4 sub-steps `[t0, e1, …, t1]`; at a shared instant, cutoff is processed before ignition (back-to-back burns).

## Reasoning
- Keeps every approved M1 boundary and byte-identical M1 output.
- Gives exact analytic oracles (mass law, rocket equation, free-space motion).
- Follows the playbook chain: command → propulsion → force → integration → telemetry.

## Consequences
### Positive
- Propulsion is testable on its own (T1) before simulator integration (T2).
- Direction modes and engine models are extensible.

### Negative / tradeoffs
- The simulator gains a second derivative path (with propulsion) alongside the M1 path. Both must be maintained.

## Validation
- T1: unit tests against the rocket equation, mass conservation, the free-space closed form and an independent integrator.
- T2 onward: DR-0015 oracles; the M1 golden hash is unchanged.

## Reconsider when
- Throttling, multiple engines/tanks, attitude dynamics, or mass-dependent non-thrust forces (drag) are introduced.

## Related
- Decision Requests: DR-0010…DR-0015
- Scientific assumptions: SCI-0002 (revised), SCI-0008…SCI-0012
- Validation: VAL-0008, VAL-0009
