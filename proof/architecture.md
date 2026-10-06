# Architecture Proof

For applicable features/milestones, prove:
- [ ] Agents cannot directly mutate physical simulation state.
- [ ] Physical commands flow through simulator/system interfaces (for example, burn -> propulsion -> force -> integration -> telemetry).
- [ ] Crew tool/permission boundaries are enforced by code, not only prompts.
- [ ] No permission boundary changed without an approved Decision Request.
- [ ] Core simulation runs without an LLM/provider dependency.
- [ ] Model-provider-specific code is isolated behind replaceable boundaries where applicable.
- [ ] Important actions/state transitions emit machine-readable events.
- [ ] No 3D dependency has entered the headless core before authorization.

Prefer automated validators/tests for these checks as the implementation grows.
