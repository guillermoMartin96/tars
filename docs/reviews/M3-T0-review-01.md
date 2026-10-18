# M3 T0 Review 01 (independent review of the reference-configuration spike)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model (the event stream reports no model name).
- **Session:** `01a1502b-6d1c-7c30-8818-55b422f9531a`.
- **Sandbox:** `workspace-write`, no network. The local `codex` wrapper reported that `--dangerously-bypass-hook-trust` was enabled for the invocation; the implementer did not pass that flag.

**Reviewed commit:** **`ca84986595fe904883a37f13bf9be64ad75a35fc`** (the pinned checkpoint), in a fresh git clone with its own `uv sync --locked` environment and a private, byte-identical copy of GMAT R2026a.
- The prompt was kept outside the repository during the review, so the reviewed tree is exactly `ca84986`.
- The prompt is committed afterwards as `raw/M3-T0-codex-review01-prompt.md`.

**Authority:** "TARS M3 — Instruction I-15: T0 Independent Review" (Tech Lead, 2026-10-18), §3–§5. Its text, and the T0 authorization I-15, are reproduced verbatim in the prompt.  
**Raw output:** `raw/M3-T0-codex-review01.md`, byte-identical to the reviewer's saved report.
- The reviewer's scratch scripts and logs are in `raw/M3-T0-codex-review01-evidence/`, with a `SHA256SUMS` file.
- Python files are stored as `*.py.txt` so the repository linter does not apply to them; their bytes are unchanged.
- Omitted as derivable or too large: the 5.3 MB authoritative diff, re-run JSON copies (byte-identical to the committed results), pytest and validator JSON.

**Verdict:** **REQUEST_CHANGES** (2 MAJOR, 2 MINOR, 1 NOTE).

**Stop rule applied (I-15 review §5):** every finding is recorded and its evidence was verified by the implementer. No correction is applied, no further review round is started, and T0 is **not** accepted. Authorization for the proposed corrections is requested.

## Baseline verified before the review (I-15 review §2)
- **HEAD:** `ca84986`, equal to `origin/milestone-3-t0-reference-spike`.
- **Worktree:** clean.
- **CI:** four successful jobs on `294e1f5` (run 39138140001) and on `ca84986` (run 39144298212), from the GitHub check-runs API.
- **Proof at `294e1f5`:** full local M1 Proof 9/9 and M2 Proof 20/20 (`M3-T0-report.md` §2).
- **Scope:** `git diff --name-only 86df2c3 HEAD -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty.
- **Digests:** the five pinned digests match `approved_digests.py`.

## What the reviewer verified by its own execution (from the raw ledger)
- **Re-runs:** all five Python experiments, and the full GMAT harness on the private GMAT copy, re-ran byte-identically: six result files and all 67 `gmat_runs/` files. The tracked tree stayed clean.
- **Tests and validators:** `pytest` 1185 passed (3 warnings). `m1_proof.py` and `m2_proof.py` (228/228) passed with `--out` into scratch. `gmat_m1.py compare` and `gmat_m2.py compare` passed. The five digests match.
- **Independent code:**
  - a J2 potential gradient agrees with the spike acceleration to 3.66e-13 m/s²;
  - a nearest-point ellipse distance agrees with the geodetic height to 1.2e-10 m;
  - the table lookup agrees exactly;
  - the predicted probe bias −aτ/v = −1.42857e-7 explains the common density-probe bias;
  - the two-orbit axis fit has rank 15 against 10 for one orbit.
- **Mutations:**
  - a J2 sign reversal, a J2 axis on X, and removing co-rotation each change the frame checks discriminatingly;
  - v instead of v_rel changes drag by 9.53 %;
  - spherical instead of geodetic height is 10.6 km at the test point;
  - a lower-band-at-base substitution changes density by up to 0.136 %.
- **Not independently verified** (stated by the reviewer):
  - CI, and the historical 9-/20-step Proof wrapper runs;
  - branch-protection settings and I-14;
  - external sources (Vallado, NGA, GeographicLib, the GMAT source mirror);
  - three-platform execution;
  - the one-command planning re-run;
  - the "0.99 m" quadratic-fit figure (see IM-1);
  - the cause of the escalated geodetic-drag residual.

## Findings and dispositions
| ID | Severity | Finding (reviewer) | Implementer verification | Disposition |
|---|---|---|---|---|
| M3T0-F1 | MAJOR | The missed-crossing "bound" a e n² dt²/8 = 4.17 m (`t0_decay.py` `missed_crossing_bound`; DR-0029 P2; VAL-0019) is not a bound. It came from one fixed sampling phase. With perigee at the middle of a 10 s step the dip is 4.99 m (Kepler) and 4.82 m (spike J2 + drag), and a circular inclined orbit dips 0.45 m where the formula gives 0. The spherical perigee curvature is μe/r_p² = a e n²/(1 − e)², and geodetic height adds latitude-dependent curvature | **VERIFIED independently** (the implementer's own DOP853 computation): perigee mid-step 4.98764 m (Kepler) and 4.81710 m (J2 + drag) > 4.16525 m; circular 51.6° at the equator crossing 0.45162 m. **Root cause:** a fixed-phase sample maximum was presented with a formula that omits the (1 − e)⁻² factor and the ellipsoid's curvature | **ACCEPTED**; not applied |
| M3T0-F2 | MAJOR | P1 (A4-b) does not guarantee what DR-0029 claims for every admissible run (P1, P3 item 2, P4 "never alters a valid run"). A P1-admissible stress input (h_f 21 500 m, initial h 22 000 m inward at 10 km/s, B 1e9 kg/m², dt 10 s, bound energy) puts an RK4 stage at −28 000 m (fail closed) and, in extrapolation mode, ends below both the floor and `impact` in one tick. The circular-speed proxy underestimates λ for eccentric or retrograde states (0.0144 > κ 0.01). "κ = 0.01 admits h_f ≥ 90 km" is wrong: λdt(90 km) = 0.01035, and the exact threshold is 90 185.09 m | **VERIFIED** (the reviewer's script re-run by the implementer gives identical values: P1 λdt 4.98e-6; stage heights −28 000 / −28 243.6 / −78 347.7 m; `OutsideDomainError`; λdt(90 km) 0.0103500; threshold 90 185.09 m). **Root cause:** necessary conditions were presented as sufficient; conclusions from one decay case were generalised; a 5 km grid value was quoted as a threshold | **ACCEPTED**; not applied |
| M3T0-F3 | MINOR | The inward RK4 evaluation is the **third** stage (k3's input, r + (dt/2) v₂), not the second (DR-0029 P4; VAL-0019; `M3-T0-report.md` §4). At the 180 km state the offsets are +116.31 m (k2), −115.73 m (k3) and +1.16 m (k4) | **VERIFIED** (same values; `t0_model.rk4_step` records the stages in the order k2, k3, k4 inputs, and the 115.7 m minimum is the k3 input). The measurement itself is correct | **ACCEPTED**; not applied |
| M3T0-F4 | MINOR | The M3-form perturbations-off GMAT vs Kepler residual is quoted as 4.86e-6 m (DR-0029 P6 table; VAL-0019). The committed JSON gives 6.95223445873689e-6 m. The 1e-4 m gate still passes | **VERIFIED** (`t0_gmat_results.json` → `regression_m3_form.metrics.gmat_vs_kepler_position_error_max_m` = 6.95223445873689e-6). **Root cause:** 4.86e-6 m was the value of an earlier run at GMAT's default `NutationUpdateInterval`, before interval 0 became the T0 configuration; the record was not re-read after the final run | **ACCEPTED**; not applied |
| M3T0-F5 | NOTE | The technical dependency map (T2: P1–P5, P8, P9; T4/T5: P6, P7; T1: P10) must be kept distinct from the owner's gate in the completed I-15 (P10 before T1; P1–P10 before T2), which the implementer had not received at `ca84986` | Agreed. `M3-T0-decision-matrix.md` states both, and applies the owner's gate | **ACCEPTED** (handled in the decision matrix; DR-0029 text unchanged) |

### Implementer-identified item (not a reviewer finding)
- **IM-1 (MINOR, proposed):** DR-0029 P6 says "a quadratic-only fit leaves a 0.99 m residual".
  - **What the number is:** the RMS fit residual (0.9857 m) of an intermediate two-orbit axis-probe run with a quadratic-only basis, made during T0 development. That run's output was overwritten when the diurnal basis replaced it, so **no committed artifact supports the number**.
  - **Reviewer's attempt:** it found 0.419 m with its own quadratic-only fit, a different quantity and procedure, and marked the figure not independently reproduced.
  - **Proposed correction:** either reproduce it with a committed diagnostic or replace it with a qualitative statement ("a quadratic-only basis cannot represent the diurnal polar-motion circle"), citing the committed rank and residual evidence.

## Proposed corrections (for authorization; none applied)
1. **F1:**
   - Replace the missed-crossing bound in `t0_decay.py`, DR-0029 P2 and VAL-0019 with a justified bound on geodetic-height curvature over a stated domain (eccentricity, altitude, latitude), or present only measurements.
   - Add sampling-phase and eccentricity sweeps (including perigee at mid-step and circular inclined orbits) to the experiment.
   - Keep the 1.56 m figure as a fixed-phase measurement.
2. **F2:**
   - Restate P1 (A4-b) as necessary, not sufficient.
   - Either specify an admissible initial-state, velocity, dt and B domain with a derived stage-height and relative-speed bound, or state explicitly that admissible scenarios outside it fail closed.
   - Base the stiffness criterion on a bound of |v_rel| instead of circular speed.
   - Replace the grid thresholds with exact ones (κ = 0.01: 90 185.09 m at B 25.8; recompute the others).
   - Correct P3 item 2 and P4's "leaves every valid run unchanged" accordingly, and limit the decay-case conclusions to that case.
3. **F3:** say "third stage (input of k3)" in DR-0029 P4, VAL-0019 and the T0 report.
4. **F4:** quote 6.95e-6 m in DR-0029 P6 and VAL-0019.
5. **IM-1:** as above.
6. **Re-verification after correction:**
   - rerun the affected experiments twice for byte identity;
   - lint;
   - full M1/M2 Proof (no production file is touched, so only to show the checkpoint is unchanged);
   - CI;
   - a further independent review round, which itself needs authorization.

## Lessons (for the learning loop; proposed, not yet codified)
- A bound must be derived over the whole stated domain and tested at its worst case (here, the sampling phase), not inferred from one sampled run.
- Before recording a number, re-read it from the final committed artifact. Never quote a value from a superseded run.
- When a rule admits a set of inputs, state whether it is necessary or sufficient for each claimed property, and try to construct an admissible counterexample before claiming sufficiency.
