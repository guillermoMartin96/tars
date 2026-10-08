# Milestone 1 implementation clarifications

**Date:** 2026-10-08

**Scope:** F3 and F4 from the independent audit of `6cf072a`. This follow-up describes
existing M1 behavior; it does not amend an approval or introduce a new decision.

## Constants (ADR-0003)

ADR-0003 says scenarios may supply constant overrides. The actual JSON schema accepts
only the named `WGS84` constants; no numerical overrides are exposed. Constants are
centralized and the gravity constructor accepts `mu` as a parameter, so model-level
injection exists. The narrower scenario interface satisfies the approved M1 case.
Supporting new scenario constants would need its own validation and approval.

## Final timestep and tolerances (ADR-0004)

ADR-0004 records the candidate timestep and pending finalization. The later approvals
in [DR-0008](requests/DR-0008-m1-proof-tolerances.md) and
[DR-0009](requests/DR-0009-gmat-reference-gates.md) finalize dt = 10 s and the limits
in `proof/thresholds/m1.json`. The implemented integrator protocol is
`step(f, t, y, dt)`, rather than the conceptual argument order in ADR-0004.
This note links the historical proposal to the implemented, approved result.

## Orbit-count semantics (DR-0007)

The runner counts ascending-node passages. DR-0007 fixes M1's starting argument of
latitude to zero, so each passage completes another full revolution. For other
allowed starting phases, the first passage occurs before a full revolution; ten
passages therefore take between nine and ten periods. For example, a 270° start
finishes near 9.25 periods (49 680 s at the first 10 s tick after the tenth passage).

The schema and event documentation now make this existing behavior explicit.
Changing the meaning of the stop condition, imposing new initial-phase restrictions,
or adding an alternative revolution counter is outside this remediation. Any such
change must be proposed to the Tech Lead before implementation. General phase tests
document behavior; approved M1 physics gates still use the unchanged DR-0007 scenario.

## Reference comparison (ADR-0006)

The exported GMAT reports are whitespace-delimited text, not CSV. DR-0009 authorizes
comparison against the committed report in CI without installing or running GMAT.
Reference replacement remains subject to explicit review. The GMAT comparison ends
at 53 700 s; the off-cadence mission final state at 53 710 s is checked against Kepler.

Original ADRs, Decision Requests, thresholds, and reference artifacts are preserved.
