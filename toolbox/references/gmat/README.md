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

## REV-012 epoch-column drift: RESOLVED (2026-10-10)
The drift was deferred by the Tech Lead on 2026-10-05, then investigated before M2's first time-dependent (scheduled-thrust) force model. The root cause is verified GMAT behavior: **VAL-0010**, DR-0016 (approved), evidence in `docs/science/experiments/rev-012/`, CI-reproduced by `tests/test_rev012_evidence.py`.
- **Epoch drift (M-a).** Each `Propagate` command re-rounds the double A.1 MJD epoch, so drift grows with the number of commands. For M1 (895 × 60 s) this gives −1.063e-4 s, reproduced bit-exactly on all rows.
  - The integrated states are at the requested elapsed times (9e-10 s), so **M1's approved comparison, which aligns on the `ElapsedS` labels, is unaffected**.
  - The committed M1 reference still reproduces byte-for-byte.
- **Stop-time rounding (M-b).** GMAT rounds the final step to a time stop condition to 1 µs (`TIME_ROUNDOFF`). This, not epoch quantization, explains the M2 probe's 1.85e-7 s burn shortfall.
- **Method for M2 burn references (DR-0016).**
  - Use aligned stepping (`InitialStepSize = MaxStep` dividing every stop time), with mandatory alignment verification, and stream report rows from one `Propagate` per arc.
  - Do **not** align comparisons on GMAT's epoch or `Sat.ElapsedSecs` columns: both carry the M-a drift. The earlier guidance in this section said the opposite and is superseded.
- Measured on the reference burn at 53 700 s: GMAT vs independent DOP853 is 1.17 cm with natural stepping and 12 µm with aligned stepping.

# GMAT reference: Milestone 2 finite burns (T6, O9)

`m2/` holds committed GMAT R2026a references for the M2 missions `m2_prograde_burn`, `m2_retrograde_burn` and `m2_invalid_commands`. CI compares against them without GMAT. Authority: DR-0015 option A (GMAT as a gated reference), DR-0016 A (aligned stepping and mandatory verification), DR-0009 (references are evidence).

| File (per mission) | Purpose |
|---|---|
| `<mission>.script` | Generated from the scenario by `toolbox/scripts/gmat_m2.py`. Do not edit. |
| `<mission>_report.txt` | One row per GMAT integrator step: arc number, A1 MJD, r, v, total mass. |
| `<mission>_metadata.json` | Provenance: GMAT build, console sha256, scenario hash, script/report sha256, constants, model, replace reason. |
| `<mission>_console.log` | GmatConsole output (paths scrubbed). |

## Configuration (generated from scenario inputs only)
- **Earth:** point mass, WGS 84 `Mu` and radius, as M1.
- **Spacecraft:** dry mass and tank fuel from the scenario; `AllowNegativeFuelMass = false`.
- **Engine:** one `ChemicalThruster` per direction used.
  - Local VNB axes, `ThrustDirection1 = ±1` (prograde/retrograde, DR-0012).
  - `C1 = F` [N], `K1 = Isp` [s], and **every other C2..C16, K2..K16 explicitly 0**.
  - `GravitationalAccel = 9.80665` (standard g0; GMAT's default differs, VAL-0009).
  - `DecrementMass = true`, `DutyCycle = 1`, `ThrustScaleFactor = 1`.
- **Burns:** `BeginFiniteBurn`/`EndFiniteBurn` around exactly the predicted burn arcs. The arcs come from the commanded times via `tars.validation.m2.predict_burns`, never from simulator output.
- **Integrator:** PrinceDormand78, Accuracy 1e-13.
- **Aligned stepping (DR-0016 A):** every arc is one `Propagate` with `InitialStepSize = MaxStep = h`:
  - h = 60 s on grid-aligned coasts;
  - h = 1 s during burns;
  - h = the arc length for the short arcs that realign a cutoff to the 60 s telemetry grid (for example 677.3 → 720 s).
  - Every stop then lands on a natural step, so GMAT's microsecond stop rounding (M-b) is a no-op.
- **Row times** are assigned from the step schedule. GMAT R2026a writes the first arc's start state, then one row per step; later arcs do not repeat their start. GMAT's epoch and `ElapsedSecs` columns are **not** used as time labels, because they carry the per-command re-rounding (M-a).

## Mandatory alignment verification (DR-0016), run before a reference is stored and on every compare
- the row count of every arc equals the schedule;
- step spacing from GMAT's epoch column agrees with the schedule (measured 2.3e-7 s, the epoch resolution);
- burn duration from GMAT's own mass agrees with the predicted burn (measured ≤ 1.4e-10 s);
- every coast row agrees with exact Kepler propagation of its arc's GMAT start state (measured ≤ 4.0e-6 m).

## Workflow
```bash
uv run python toolbox/scripts/gmat_m2.py generate --out runs/gmat_m2_preview   # previews only
uv run python toolbox/scripts/gmat_m2.py run --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" --gmat-version R2026a
uv run python toolbox/scripts/gmat_m2.py compare             # O9; also inside m2_proof.py
```

- **Replacement guard.** `run` refuses to touch any existing reference artifact or manifest entry without `--replace-reason`. The reason is stored in the metadata and in the history of `APPROVED_DIGESTS.json`.
- **Staged validation and publication.** `run` stages every artifact and validates it completely before replacing anything: provenance, alignment, coverage, every O9 gate and every T5 audit gate, failing closed on missing limits. On failure nothing is replaced. Publication then:
  1. withdraws the mission's approval;
  2. replaces each artifact atomically;
  3. publishes the new manifest last.

  An interruption at any step leaves either the old reference intact or an unapproved mission that every check rejects. It never leaves an accepted mix.
- **`generate`** writes previews only and never touches the references.
- **`compare` rejects a reference when** the simulator run fails its T5 audit, an expected observation is missing, an O9 metric has no threshold, or:
  - the metadata lacks a required field, or names a binary other than the approved GMAT R2026a install (pinned sha256);
  - the console log is not bound by its digest or does not record success;
  - the digests (script, report, console log and metadata) are not in the reviewed `APPROVED_DIGESTS.json`, or this reference's latest history record disagrees with its metadata;
  - any non-state script line differs from the regenerated script (constants, every engine coefficient, g0, masses, arcs, steps);
  - the initial-state literals differ beyond the approved DR-0009 bound;
  - the metadata constants differ;
  - a sha256 does not match;
  - the rows are not step-aligned.
- **Reproducibility.** Re-running GMAT reproduces every committed report byte for byte (`tests/test_gmat_m2.py::test_gmat_reproduces_the_committed_report`, skipped where GMAT is not installed).
- **Replacement history.** There have been four generations of each reference, all with byte-identical reports:
  1. `1de827e`, the initial reference;
  2. `a346fbe`, after the header comment was reworded;
  3. `94f0e75`, after provenance fields were added (review M2-T6 F1/F3);
  4. `2d33617`, after the manifest began binding metadata (review M2-T6 F8/F9).

  Every generation is a record in the manifest history, reconstructed from the committed metadata.
- **History semantics** (review M2-T6 F14):
  - Each record must name a GMAT mission and carry a plausible UTC timestamp, a non-null revision, a non-empty reason and a report digest.
  - Records are in time order. Each holds the sha256 of the previous record, so the history is a hash chain; the first record holds null.
  - Editing, inserting, reordering or deleting records breaks the chain or the ordering and is rejected.
  - **Limit:** deleting records *and* consistently re-chaining the remainder passes the checks. Only review of the manifest's version-control history reveals that (executable as `test_wholesale_history_rewrite_is_the_documented_limit`).
- **Thresholds.** Every non-null limit must be finite and nonnegative. An overflowing JSON number such as `1e999`, which parses as infinity, is rejected at load (review M2-T6 F15).
- **What provenance can and cannot prove.** The checks above make silent or accidental substitution detectable. They cannot prove GMAT origin against deliberate fabrication.
- **The reproduction test** verifies that the installed executable *is* the approved GMAT (sha256), that it reports success, and that it reproduces the committed reports byte for byte. That is authenticated, independent reproducibility evidence. Together with review of `APPROVED_DIGESTS.json` changes, it is the basis for trusting the references; by itself it cannot prove the historical origin of stored bytes.
- `generate` refuses symlinked or protected destinations.

## Depletion is not compared with GMAT
- **What happens.** GMAT's stop-condition logic takes a full step past the stop before backing up.
  - In a burn to depletion, that step drives the tank negative: −0.0064 kg in the T6 probe.
  - With `AllowNegativeFuelMass = false`, GMAT stops with "The value of … for field FuelMass … is not an allowed value" (VAL-0009 finding 4).
- **Not worked around.** Allowing negative fuel would change the reference model.
- **Validated instead analytically:** O1, O2 and the DR-0017 D1a residual, as DR-0015 provides.
