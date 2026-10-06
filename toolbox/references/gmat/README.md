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

Before comparing, it **rejects** the reference if any of the following hold:
- The committed script differs from the script regenerated for the current scenario. This covers the constants in the `Earth.Mu` and `EquatorialRadius` lines.
- The metadata constants differ from the scenario's.
- A sha256 does not match.
- The report does not cover the full 60 s grid.

It also reports the initial SMA, period and initial-state differences, which give numerical evidence that GMAT applied the constants. These are gated by DR-0009.

**Epoch column note (REV-012):** `(Sat.TTModJulian − 31041.5)·86400 − ElapsedS` drifts to −1.07e-4 s by 53 640 s.
- The states are nevertheless at the labelled ElapsedS: GMAT matches exact Kepler at those times to 7 µm, while a 1e-4 s time offset would show as about 0.8 m.
- Our working hypothesis, not verified against GMAT internals, is accumulated rounding in GMAT's Modified-Julian epoch bookkeeping. That is the same failure mode our integer-tick time avoids (ADR-0002).
- No impact while the dynamics are time-invariant (M1). Once forces depend on absolute time (Earth rotation, ephemerides, drag), align on GMAT's epoch rather than on a script counter, and re-investigate this drift.

## Installed reference tool (provenance)
| Item | Value |
|---|---|
| Release | GMAT R2026a. Build date Mar 26 2026 19:40:08 (`GmatConsole --version`). |
| Source | https://sourceforge.net/projects/gmat/files/GMAT/GMAT-R2026a/gmat-mac-x64-R2026a-signed.dmg (official NASA GSFC project) |
| DMG | 455 494 809 bytes. MD5 `94763b2599e4e71c4ceb917464433855` matches the SourceForge-published hash. SHA-1 `5dcbf29f34a7dbdf2633974d05ee32cf0b9b8ce9`. |
| Signature | `GmatConsole` is signed by "Developer ID Application: NASA (82A95CK2HC)", identifier `gov.nasa.gsfc.gmat.console`; `codesign --verify` passes. |
| Install | Copied with `ditto` to `~/Applications/GMAT R2026a` (user-level; no admin rights, no system directories). |
| Binary | Universal x86_64/arm64. `GmatConsole` sha256 is recorded in `m1_two_body_metadata.json`. |
| Host | macOS 26.2 x86_64 |

**Startup noise:** at startup GMAT reports that the optional Python 3.12, MATLAB and proprietary plugins (CSALT, EMTG, MarsGRAM, MSISE86) failed to load. The M1 case uses none of them; the script interprets and runs fully (see `m1_gmat_console.log`).

**Reproducibility:** two consecutive runs produced byte-identical reports (sha256 `9ac597c6…`).

**Report format note:** GMAT R2026a writes the header line again when the first Report inside the `For` loop runs. The parser skips repeated headers.

## Policy: committed reference data is evidence, not a fixture (DR-0009)
The committed GMAT script, report and metadata are the reference our simulator is judged against.
- **They are never regenerated or replaced to make a failing comparison pass.** A failing `compare` is a discrepancy to investigate and classify (playbook/science.md), not a stale fixture.
- Regenerating or replacing them requires explicit review. That means a Decision Request or a reviewed record naming the reason, for example a scenario change approved by the Tech Lead or a GMAT version upgrade, plus a comparison of the old and new reference.
- `gmat_m1.py run` enforces this: it refuses to overwrite an existing reference unless `--replace-reason` is given. The reason is stored in `m1_two_body_metadata.json`.
- `compare` rejects references that are stale, edited, incomplete, or carry different constants. It gates GMAT's own agreement with the exact Kepler solution, the constants it actually applied, and the initial state (DR-0009).

## Informational realistic-model runs (DR-0005; not an M1 gate)
`informational/` holds GMAT runs from the same initial state with JGM-3 gravity (J2-only and 4×4) and Jacchia-Roberts drag (F10.7 = 70, 150, 250). The spacecraft is GMAT's default (850 kg, 15 m², Cd 2.2) and is illustrative only.
- Results and interpretation: VAL-0007 in `docs/science/validation.md`.
- Recompute the summary from the committed reports: `uv run python toolbox/scripts/gmat_m1.py realistic-summary`.
- Re-running GMAT (`realistic`) is subject to the same replacement policy (`--replace-reason`).

## Deferred: REV-012 epoch-column drift
The ~0.1 ms drift between GMAT's `TTModJulian` column and the `ElapsedS` label is **explicitly deferred** (Tech Lead, 2026-10-05). It is not an M1 blocker.
- **Trigger:** investigate it **before the first time-dependent force model** (Earth rotation, ephemerides, drag in gated validation).
- **Then:** align comparisons on GMAT's epoch rather than the script counter.
- **Note:** the informational drag runs are time-dependent but not gated. A 0.1 ms timing difference is negligible at their km scale (about 0.8 m).
