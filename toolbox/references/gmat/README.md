# GMAT reference: Milestone 1 two-body case

GMAT (NASA GSFC General Mission Analysis Tool, Apache-2.0) is the project's initial primary orbital reference (playbook/science.md). This directory holds the committed M1 reference, so CI never needs GMAT (DR-0005, DR-0007, ADR-0006).

| File | Purpose |
|---|---|
| `m1_two_body.script` | GMAT script generated from `scenarios/m1_leo_250km.json`. Do not edit it by hand. |
| `m1_two_body_report.txt` | GMAT ReportFile output: state every 60 s for 53 700 s. |
| `m1_two_body_metadata.json` | Provenance: GMAT version, scenario hash, sha256 of script and report, constants, model. |
| `m1_gmat_console.log` | GmatConsole output from the reference run. |

## Configuration (must match the project model)
- **Force model:** Earth point mass only (`PointMasses = {Earth}`, no `PrimaryBodies`). No drag, SRP, third bodies, or relativity (SCI-0001, SCI-0004).
- **Constants:** `Earth.Mu = 398600.4418` km³/s² and `Earth.EquatorialRadius = 6378.137` km (WGS 84, SCI-0005). These override GMAT's default Mu of 398600.4415. The comparison checks this through the initial SMA.
- **Frame and epoch:** `EarthMJ2000Eq`, epoch 01 Jan 2026 00:00:00.000 TT (SCI-0003, SCI-0007).
- **Integrator:** PrinceDormand78, Accuracy 1e-13, MaxStep 60 s. The run propagates in 60 s segments, so report times match our telemetry grid exactly.

## Workflow
```bash
# 1. Regenerate the script after any scenario change
uv run python toolbox/scripts/gmat_m1.py generate
# 2. Run GMAT and store the report and provenance (needs a local GMAT install)
uv run python toolbox/scripts/gmat_m1.py run --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" --gmat-version R2026a
# 3. Compare (refuses stale or modified references)
uv run python toolbox/scripts/gmat_m1.py compare
```

`compare` reports three differences, which together classify any discrepancy (playbook/science.md):
- ours vs GMAT
- GMAT vs the exact Kepler solution
- ours vs the exact Kepler solution

It also checks the constants match (initial SMA and period differences) and that the starting states are identical.
