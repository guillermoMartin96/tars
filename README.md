# TARS Spacecraft Simulator

TARS Milestone 1 is a deterministic, headless orbital simulator with a machine-readable
scenario, JSONL events, physics validators, and a committed GMAT reference.

The approved scenario is a circular orbit 250 km above a spherical Earth, inclined
51.6°, starting on the ascending node. It uses WGS 84 constants, point-mass gravity,
fixed-step RK4 at 10 s, and ten ascending-node passages. No J2, drag, spacecraft
systems, AI crew, or 3D rendering is implemented. The two-body result is a validated
prototype, not a realistic prediction of a spacecraft at 250 km.

Milestone 2 adds physically modelled propulsion (in review, not yet merged): spacecraft dry
and propellant mass owned by the simulator; one ideal constant-thrust, constant-Isp engine
(mass flow F/(Isp·g0), a = F/m); finite prograde or retrograde burns with velocity-tracking
pointing and exact RK4 step splitting at ignition, cutoff and depletion; a strict
`BurnCommand` submitted through `Simulator.submit()` with documented rejection codes and no
state change on rejection; and seven additive JSONL event types. M1 behaviour is
byte-identical. Attitude dynamics, throttling, multiple engines, abort/cancel and Δv-target
commands, AI crew and 3D are not implemented.

## Running and checking M1

Python 3.12 and the dependencies pinned in `uv.lock` are required. With an existing
locked environment, run from the repository root:

```sh
uv run --no-sync python toolbox/scripts/run_mission.py \
  --scenario scenarios/m1_leo_250km.json --out runs/m1
uv run --no-sync pytest
uv run --no-sync python toolbox/validators/m1_proof.py --out runs/proof/m1.json
uv run --no-sync python toolbox/scripts/gmat_m1.py compare
uv run --no-sync python toolbox/validators/determinism.py
uv run --no-sync python toolbox/validators/cross_platform.py
```

The mission writes `events.jsonl` and `summary.json`. The GMAT comparison reads the
committed reference; it does not require a GMAT installation. The complete
`toolbox/scripts/run_m1_proof.sh` workflow performs `uv sync --locked` and overwrites
the original evidence directory; use individual commands and a separate output
directory when preserving historical evidence. Dependency installation requires
approval when operating under a review task that prohibits setup.

## Running and checking M2

Scenario files use `schema_version: 2` (spacecraft, command timeline, `stop.duration_s`):
`scenarios/m2_prograde_burn.json` (the vertical slice), `m2_retrograde_burn.json`,
`m2_burn_to_depletion.json` and `m2_invalid_commands.json`. The SciPy-based validators need
the dev dependency group (installed by `uv sync --locked`).

```sh
uv run --no-sync python toolbox/scripts/run_mission.py \
  --scenario scenarios/m2_prograde_burn.json --out runs/m2
uv run --no-sync python toolbox/validators/m2_proof.py --out runs/proof/m2.json
uv run --no-sync python toolbox/scripts/gmat_m2.py compare
uv run --no-sync python toolbox/validators/determinism.py --scenario scenarios/m2_prograde_burn.json
uv run --no-sync python toolbox/validators/m2_cross_platform.py collect --out runs/xp/local.json
```

`toolbox/scripts/run_m2_proof.sh` runs the whole M2 suite, including every M1 gate, and
writes `proof/records/evidence/M2/` (pass another directory to keep the committed evidence).
Thresholds are `proof/thresholds/m2.json` (approved, DR-0023); reference values come from
the sha256-pinned snapshot `toolbox/references/snapshot/m2/` (DR-0021). The commands and
events contract is `docs/contracts/m2-commands-and-events.md`.

## Configuration and validation boundaries

- `stop.orbits` counts ascending-node passages after the start. For the approved
  ascending-node start, ten passages represent ten full revolutions. For other
  starting phases, the first passage completes only a partial revolution.
- Equatorial initial orbits are rejected because they lack ascending-node crossings.
- Scenario configuration supports the named `WGS84` constants only. The underlying
  gravity model accepts an injected `mu`, but JSON scenarios cannot override constants.
- Typed numerical scenario and event fields must be finite. GMAT report rows must
  have the expected width and finite values before numerical comparisons are made.
- Same-platform replay is byte-identical with pinned dependencies. Cross-platform
  agreement is measured against the golden state with approved tolerances.
- Numerical thresholds apply to the approved scenarios. A change to a scenario,
  timestep, integrator, force model, or the propulsion model requires remeasurement,
  a reviewed reference-snapshot baseline where M2 references change, and approval.
- M2 burns execute in submission order. The spacecraft is illustrative (R-4D-11-class
  engine), not a real vehicle. A burn still active at the stop has no `BurnEnded`
  (DR-0018); the final `PropulsionSampled` records it.

## Engineering and evidence

Start with [CLAUDE.md](CLAUDE.md), the [playbook](playbook/PLAYBOOK.md), and
[Proof requirements](proof/PROOF.md). See the [original M1 Proof record](proof/records/M1-orbit.md), the
[M2 plan](docs/milestones/M2-propulsion.md) and [M2 Proof record](proof/records/M2-propulsion.md),
[GMAT reference workflow](toolbox/references/gmat/README.md), and
[current-behavior clarifications](docs/decisions/M1-implementation-clarifications.md).
The [independent-audit follow-up](docs/reviews/M1-independent-audit-02.md) and
[remediation Proof record](proof/records/M1-independent-audit.md) describe the latest corrections.
Historical approvals and review records remain authoritative for their stated revisions.
