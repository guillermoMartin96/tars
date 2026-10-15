# Milestone plans

Each milestone's scope, non-goals, architecture, implementation sequence, and draft Proof live here. Approval of a plan happens through its Decision Requests.

The repository has no multi-milestone roadmap document. Milestones are authorized one at a time by the Tech Lead (see DR-0010).

| Milestone | Plan | Status |
|---|---|---|
| M1 Orbit | (predates this directory) [Proof record](../../proof/records/M1-orbit.md) | PASS, merged |
| M2 Propulsion & Orbital Maneuvers | [M2-propulsion.md](M2-propulsion.md), [Proof record](../../proof/records/M2-propulsion.md) | PASS; accepted by the Tech Lead 2026-10-15; merge to `main` authorized (PR #3) |
| M3 | not defined | A planning proposal follows M2's acceptance. Nothing is authorized |

## Known forward requirements (recorded, not authorized)
These are the only forward-looking commitments on record. They are not a roadmap: milestone objectives beyond M2 have not been defined in this repository.
- **M5 (Tech Lead, 2026-10-15):** develop the Mission Laboratory alongside AI Navigator capabilities: isolated mission forks, maneuver comparisons and safe recommendations. Earlier milestones must not implement M5 capabilities.
- **Architectural direction (Tech Lead, 2026-10-15; ADR-0008, on the research branch until merged separately):**
  - Python remains the validated simulation reference.
  - Rust is the preferred candidate for a future onboard Flight Core investigation.
  - Deterministic authorization stands between AI recommendations and commands.
  - No C or Rust implementation is authorized.
- **From the playbook:** no 3D work until the headless simulator and the AI crew satisfy their Proof (`playbook/architecture.md`).
