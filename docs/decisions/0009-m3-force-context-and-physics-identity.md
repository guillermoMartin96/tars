# ADR-0009: M3 force context, environment components and physics identity

**Status:** Accepted (design decision, Tech Lead 2026-10-15 via DR-0026). **Not implemented.** M3 implementation is not authorized by this record.  
**Date:** 2026-10-15  
**Decision owners:** Guillermo (Tech Lead, via DR-0024, DR-0025, DR-0026); implementing engineer

> Numbering: ADR-0008 is the flight-software architecture record on the unmerged research branch `research/flight-software-architecture`. Its number is reserved; this record is ADR-0009.

## Context
- M3 adds J2 and atmospheric drag (G0, Option A). Drag is the first non-thrust force that needs spacecraft mass. That meets the reconsider triggers of ADR-0003 ("a force needs state beyond (t, r, v)") and ADR-0007 ("mass-dependent non-thrust forces (drag)").
- Adding physics to existing scenarios would let "the same scenario" silently mean different physics, and could change M1/M2 bytes.

## Options considered
DR-0026 §4: D1 (inject mutable mass into forces), D2 (an immutable context argument with a legacy adapter), D3 (D2 plus environment components, physics identity and scenario v3), D4 (a plugin framework).

## Decision
**D3, with the owner's constraints (DR-0026 Resolution):**
1. Forces receive a small **immutable force-evaluation context** holding the minimum shared runtime state they need, including the current total mass. Mutable mass is never injected into force implementations.
2. The **old force signature is preserved through an adapter**, so frozen M1/M2 behaviour stays reproducible.
3. **Density is a separate component** consumed by drag.
4. A **`PhysicsConfiguration`** with deterministic canonical serialization and a SHA-256 identity (`physics_id`) defines "which physics".
5. **Model identifiers are versioned** (for example `zonal_j2@1`). A change to equations, constants or algorithm creates a new version.
6. **Scenario format v3 is additive.** Historical v1/v2 scenarios and their artifacts are never mutated.
7. An additive **`PhysicsConfigured`** event records the configuration of v3 runs.
8. **Validation fails closed** when the expected physics identity does not match the active configuration.
9. **Force composition and order are deterministic and documented:** point mass, J2, drag, then thrust.
10. **Earth/model constants and datasets are pinned physics configuration**, never inline scenario overrides.
11. **Every historical physics/model version is retained** for as long as a frozen validation artifact or a supported historical scenario depends on it. There is no time-based deletion.
12. **A decay run ends at an explicitly defined event or model-validity boundary.** Its numerical definition is OPEN (DR-0027).
13. **No general plugin framework** in M3.

## Reasoning
- D2/D3 keep forces pure and state ownership with the simulator (ADR-0002), which D1 would break and which future isolated mission forks need.
- An identity that includes values and dataset digests makes physics changes visible, instead of relying on file names or schema versions alone.
- A plugin framework has no M3 need and conflicts with the static determinism guards.

## Consequences
### Positive
- M1/M2 paths stay frozen and regression-gated.
- Future forces (higher-order gravity, third body, SRP, attitude-dependent aerodynamics) are additive components and versions (DR-0026 §6).

### Negative / tradeoffs
- A signature change behind an adapter, and a second scenario schema version, to maintain.
- Retained model versions accumulate while artifacts depend on them (owner's retention rule).

## Validation
- M1 golden hash, M2 Proof, M2 cross-platform goldens and the M2 reference snapshot reproduce exactly with perturbations off.
- Identity-mismatch tests fail closed. DR-0025 seams.

## Reconsider when
- A force needs mutable or history-dependent state.
- A time-dependent Earth orientation, ephemerides or absolute time are introduced.
- A second language implementation is authorized (ADR-0008 AT items; no Rust, C, FFI, RTOS or embedded work is authorized here).

## Related
- Decision Requests: DR-0024, DR-0025, DR-0026, DR-0027.
- Scientific assumptions: SCI-0013 to SCI-0017.
- Proof: M3 Proof (not yet defined).
- Code/PR/commit: none (not implemented).
