# Architecture Rules

## Hard invariants

### 1. Simulator owns reality
Agents may observe telemetry, reason, propose, authorize, and issue commands. They may not directly mutate physical state.

Conceptual boundary:
`execute_burn(command) -> propulsion model -> propellant/thermal effects -> force/acceleration -> numerical integration -> new physical state -> sensors/telemetry`

Agent code must not directly perform changes such as `spacecraft.velocity += delta_v`.

### 2. Crew permissions remain separated
Navigator, Flight Engineer, Commander, and Pilot have distinct responsibilities and tool permissions. Convenience is not sufficient reason to blur them. Any permission-boundary change requires a Decision Request.

### 3. Deterministic core
Physics, spacecraft systems, missions, telemetry, events, failures, and replay must be runnable and testable without an LLM. AI crews are controllers above the simulation, not part of the laws of the simulated world.

### 4. Provider-independent agent layer
Do not tightly couple project architecture to Anthropic, OpenAI, or another provider. Claude Code is the initial development environment, but model access belongs behind provider/model adapters or similarly replaceable boundaries.

### 5. Machine-readable from day one
Important observations, proposals, decisions, commands, simulation events, failures, review outcomes, seeds, and validation results must have structured representations. Human-readable summaries may be derived from structured data, not substituted for it.

### 6. Headless first
Do not begin Godot/3D implementation until the headless simulation and AI crew satisfy their defined Proof requirements and the Tech Lead authorizes the next phase.

## Engineering priority order
When tradeoffs cannot all be satisfied, prefer:
1. Scientific correctness
2. Understandability / learning
3. Reproducibility
4. Testability
5. Architecture quality
6. Development speed
7. LLM/token cost
8. Visual polish

Token cost should still be reduced whenever doing so does not compromise higher-ranked priorities.

## Non-blocking decisions
When approval is required, create a Decision Request, mark dependent work `BLOCKED`, and continue independent work. Do not stop the entire task merely because one branch of work is awaiting a decision.
