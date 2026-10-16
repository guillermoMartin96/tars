# Milestone plans

Each milestone's scope, non-goals, architecture, implementation sequence, and draft Proof live here. Approval of a plan happens through its Decision Requests.

The repository has no multi-milestone roadmap document. Milestones are authorized one at a time by the Tech Lead (see DR-0010).

| Milestone | Plan | Status |
|---|---|---|
| M1 Orbit | (predates this directory) [Proof record](../../proof/records/M1-orbit.md) | PASS, merged |
| M2 Propulsion & Orbital Maneuvers | [M2-propulsion.md](M2-propulsion.md), [Proof record](../../proof/records/M2-propulsion.md) | PASS; accepted by the Tech Lead 2026-10-15; merge to `main` authorized (PR #3) |
| M3 J2 + atmospheric drag | [M3-proposal.md](M3-proposal.md), [baseline and impact](M3-baseline-and-impact.md), DR-0024…0028 | PLANNING. G0 approved 2026-10-15 (Option A). G1–G3 resolved 2026-10-15 (DR-0024/0025/0026; ADR-0009); DR-0027 resolved with conditions; DR-0028 APPROVED J-ax-1 (2026-10-15, third checkpoint; [decision matrix](M3-decision-matrix.md)); review 04 limitation corrections recorded 2026-10-16 (fourth checkpoint). Planning merge and T0 need the Tech Lead's explicit checkpoint approval; **T1 and later not authorized; M3 implementation not started** |

## Known forward requirements (recorded, not authorized)
These are the only forward-looking commitments on record. They are not a roadmap: milestone objectives beyond M2 have not been defined in this repository.

**Source:** the Tech Lead's instruction "TARS — M2 Final Acceptance and M3 Planning Authorization" (2026-10-15), sections B (architectural direction) and C (M5 requirement). The architectural decisions are recorded in full in ADR-0008, "Tech Lead decisions", and RES-0001 §12, on branch `research/flight-software-architecture` (commit `27ad862`). That branch is not merged; merging it needs separate approval.
- **M5 (Tech Lead, 2026-10-15):** develop the Mission Laboratory alongside AI Navigator capabilities: isolated mission forks, maneuver comparisons and safe recommendations. Earlier milestones must not implement M5 capabilities.
- **Architectural direction (Tech Lead, 2026-10-15; ADR-0008, on the research branch until merged separately):**
  - Python remains the validated simulation reference.
  - Rust is the preferred candidate for a future onboard Flight Core investigation.
  - Deterministic authorization stands between AI recommendations and commands.
  - No C or Rust implementation is authorized.
- **From the playbook:** no 3D work until the headless simulator and the AI crew satisfy their Proof (`playbook/architecture.md`).
- **Added by the Tech Lead's M3 planning instruction (2026-10-15):**
  - **Mission Laboratory intent (M5; not designed or implemented).** The chain is: live spacecraft/mission state → isolated mission-state fork → candidate maneuver/scenario simulations → outcome comparison → safety/constraint evaluation → AI recommendation → human/authorization boundary → only then potential execution. The AI must not modify live spacecraft state by running an exploratory simulation. Earlier milestones use this only to avoid architecture that makes deterministic isolated simulation unnecessarily hard (DR-0026 §8).
  - **Planning constraint:** revisit the language/runtime decision before implementing software intended to cross from simulator or ground tooling into flight-runtime or embedded execution. Recorded in ADR-0008 as PC-1, on `research/flight-software-architecture` at `2d6d7e5` (not merged). The Tech Lead's 2026-10-15 decision checkpoint refers to the same constraint as **AC-1** and keeps it ACCEPTED: before software crosses into flight-runtime, embedded, firmware or hardware execution, there must be an explicit architecture/runtime decision. AT-1 to AT-7 stay OPEN for M3.
