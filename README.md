# TARS Spacecraft Simulator

TARS Milestone 1 is a deterministic, headless orbital simulator with a machine-readable
scenario, JSONL events, physics validators, and a committed GMAT reference.

The approved scenario is a circular orbit 250 km above a spherical Earth, inclined
51.6°, starting on the ascending node. It uses WGS 84 constants, point-mass gravity,
fixed-step RK4 at 10 s, and ten ascending-node passages. No J2, drag, spacecraft
systems, AI crew, or 3D rendering is implemented. The two-body result is a validated
prototype, not a realistic prediction of a spacecraft at 250 km.

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
- Numerical thresholds apply to the approved scenario. A change to the scenario,
  timestep, integrator, or force model requires remeasurement and approval.

## Engineering and evidence

Start with [CLAUDE.md](CLAUDE.md), the [playbook](playbook/PLAYBOOK.md), and
[Proof requirements](proof/PROOF.md). See the [original M1 Proof record](proof/records/M1-orbit.md),
[GMAT reference workflow](toolbox/references/gmat/README.md), and
[current-behavior clarifications](docs/decisions/M1-implementation-clarifications.md).
The [independent-audit follow-up](docs/reviews/M1-independent-audit-02.md) and
[remediation Proof record](proof/records/M1-independent-audit.md) describe the latest corrections.
Historical approvals and review records remain authoritative for their stated revisions.
