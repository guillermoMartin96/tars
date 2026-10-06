# Mission Proof

For mission-level behavior:
- [ ] Mission input/configuration is machine-readable.
- [ ] Mission seed is explicit when any stochastic behavior exists.
- [ ] Important observations, proposals, decisions, commands, and simulator events are structured and recorded.
- [ ] Success/failure criteria are evaluated by deterministic simulation logic where possible.
- [ ] Same seed + same relevant configuration reproduces the same stochastic scenario.
- [ ] Mission failure cause is recorded in the black-box/event output.
- [ ] Agent success cannot bypass simulator physics or permission boundaries.

As the AI crew is introduced, add checks for authorization chains, tool permissions, bounded loops, provider-independent interfaces, and mission replay.
