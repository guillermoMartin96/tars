# ADR-0005: Machine-readable events (JSONL) and scenario configuration

**Status:** Accepted  
**Date:** 2026-10-05  
**Decision owners:** implementing engineer (Level-1 local architecture)

## Context
Architecture invariant 5 requires structured representations of simulation events, seeds, and validation results from day one.

## Options considered
### Option A
Pydantic models serialized as JSON Lines; JSON scenario files validated by Pydantic.

### Option B
Free-text logs.

## Decision
**Events**
- Each event carries `schema_version`, `type`, `tick`, and `t` (seconds), plus a typed payload.
- M1 event types:
  - `SimulationStarted`: scenario, effective constants, integrator, dt, seed, config hash.
  - `StateSampled`
  - `OrbitCompleted`: ascending-node crossing, with interpolated crossing time.
  - `SimulationCompleted`: status, final state, invariant summary.
  - `ValidationResult` (emitted by validators).

**Output and configuration**
- `run_mission.py` writes `events.jsonl` and `summary.json` into a git-ignored `runs/` directory.
- Scenarios are JSON, validated by Pydantic. This adds no extra parser dependency.

## Reasoning
- Pydantic is pre-approved, and its validation is deterministic.
- JSONL is streamable and diff-friendly.
- Human summaries are derived from the structured data.

## Consequences
### Positive
- Proof validators consume events directly.
- Replay and debugging become simple.

### Negative / tradeoffs
- Schema evolution must be versioned.

## Validation
- Tests round-trip every event type.
- Invalid scenarios are rejected.
- The mission-level test checks the event sequence.

## Reconsider when
- Event volume makes JSONL too slow. Consider a binary columnar format for telemetry only.

## Related
- Proof: proof/architecture.md, proof/mission.md
