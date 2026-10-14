# Proof Record — Milestone 2: Propulsion & Orbital Maneuvers (in progress: T1–T6 complete; T7 at the threshold decision)

**Milestone result:** not yet claimed. M2 Proof (P1–P12, `docs/milestones/M2-propulsion.md` §10) is evaluated at T8.
- This record collects completed task evidence only (REV-013 lesson).
- Thresholds: none approved for M2 yet. `proof/thresholds/m2.json` is **provisional** (T5); approval follows the T7 threshold DR. DR-0015 is conditional; GMAT gate recalibration is tracked as FU-1.

## T1 — Standalone propulsion model: COMPLETE
- **Code:** `src/tars/sim/propulsion.py`, `STANDARD_GRAVITY`.
- **Review:** `docs/reviews/M2-T1-review-01.md`, Codex (separate provider). REV-T1-01…06 and N1 resolved and re-verified; rejection vocabulary decided (DR-0014 amendment, `d6f5d06`).
- **Evidence:** VAL-0011 (rocket equation, free-space closed form, mass law, independent DOP853).

## T2 — Propulsion inside the simulator: COMPLETE (2026-10-10)
- **Final revision:** `d8829a2`. CI green on ubuntu-latest x86_64 and macos-latest arm64 (run 38101527076): lint, 473 tests, cross-process determinism, cross-platform agreement with the M1 golden state, GMAT reference comparison, M1 Proof.
- **Scope delivered:**
  - augmented state y = [r, v, m_prop, dv_sensed];
  - engine state machine;
  - exact RK4 step splitting at engine events;
  - atomic ticks;
  - `schedule_burn` (approved codes; submission order);
  - `PropulsionSnapshot` and `EngineTransition` (exact-time states, immutable; end cause distinguishes depletion);
  - DR-0017 B + D1a (timing Δv bound ≤ 1e-7 m/s per burn; never past depletion; residual retained).
- **Decisions:** DR-0013, DR-0014 (amended), DR-0017; ADR-0007 with approved T2 design constraints.
- **Reviews:** `docs/reviews/M2-T2-review-01.md` (REV-T2-01…05, N1–N6) and `docs/reviews/M2-DR0017-review-01.md` (F1–F3, N1–N2). **Final independent verdict: PASS** (Codex `gpt-6.1-sol`, session `01a1288c-911d-7cd1-8cc0-5121fd2aabbd`).
- **Physics evidence:** VAL-0012 (reference burn: 0.290 m vs independent DOP853 at 53 700 s, order 4.47/4.31/4.17, mass and sensed Δv to round-off; matches the independent planning implementation within 1.6 µm).
- **M1 regression:** golden event-log sha256 `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` unchanged; M1 Proof PASS against the unchanged `proof/thresholds/m1.json`; coast with or without a spacecraft is bit-identical to the M1 path (dt = 10, 0.1, 7/3).
- **Known limitations allowed at the prototype bar:**
  - submission-order scheduling only;
  - the DR-0017 bound covers thrust-integrated Δv, not trajectory error;
  - the DOP853 reference's cross-platform floor (~11–15 µm at 53 700 s) limits GMAT gate tightness (FU-1).
- **Merge:** not merged; `main` requires separate Tech Lead authorization.

## T3 — Command and event schema: COMPLETE (2026-10-10)
- **Final revision:** `7f8597e`. CI green on ubuntu-latest x86_64 and macos-latest arm64 (run 38112957337): lint, 564 tests, determinism, cross-platform agreement with the M1 golden state, GMAT comparison, M1 Proof.
- **Scope delivered:**
  - `BurnCommand` (schema_version 1; strict; exact payload boundary);
  - `Simulator.submit()` with an immutable `CommandReceipt` (atomic rejections, approved codes, stable precedence);
  - deterministic burn IDs and command-ID correlation;
  - seven additive M2 event types (strict, frozen, valid Unicode) and pure converters keeping commanded intent separate from executed outcome.
- **Contract:** `docs/contracts/m2-commands-and-events.md`. **Decisions:** DR-0014 (amended), ADR-0007 T3 notes.
- **Review:** `docs/reviews/M2-T3-review-01.md`. REV-T3-01…07 and N1–N6 resolved. **Final independent verdict: PASS** (Codex `gpt-6.1-sol`, session `01a1294e-fbc4-7741-97bc-3ed3e3937f73`).
- **Compatibility:**
  - T2 interfaces unchanged (`schedule_burn` exact signature; snapshot and transition fields additive with defaults);
  - M1 golden hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` unchanged; M1 Proof PASS.
- **Out of scope / not authorized:** event emission and scenario timeline (T4); abort/cancel and Δv-target commands; crew permissions.

## T4 — Scenario timeline, runner event emission, duration stop: COMPLETE (2026-10-11)
- **Final revision:** `ddf3f35`. CI is green on ubuntu-latest x86_64 and macos-latest arm64 (run 38158129299). CI covers lint, 705 tests, cross-process determinism, cross-platform agreement with the M1 golden state, GMAT comparison and M1 Proof.
- **Scope delivered:**
  - scenario schema version 2 (`ScenarioV2`):
    - an optional spacecraft;
    - a command timeline of raw payloads passed verbatim to `submit()`;
    - `stop.duration_s` or an orbits stop;
    - an exact tick grid;
  - runner emission of all seven T3 event types in a fixed, documented order and cadence;
  - correlation of command IDs and burn IDs through every event;
  - commanded intent kept separate from executed outcome;
  - stop semantics: a burn crossing the stop is an observation horizon (DR-0018, approved option A on 2026-10-11);
  - numerical failures recorded as `non_finite`;
  - CLI v2 summary with commit-marker publication;
  - vertical-slice scenario `scenarios/m2_prograde_burn.json`.
- **Vertical slice (DR-0010 A), evidence for P1:**
  - ignition at 600.0 s (tick 60) and cutoff at 677.3 s (tick 68), with `end_cause: completed`;
  - executed duration 77.29999999999995 s (the represented interval);
  - DR-0017 timing bound 1.6e-14 m/s (a Δv bound, not a trajectory bound);
  - propellant used 12.3794 kg, within 9e-15 of the plan;
  - sensed Δv 29.2758 m/s, within 2.3e-14 of the rocket equation;
  - orbit 250.0 × 351.0 km; `success` at 53 700 s with 9 node passages;
  - events sha256 `42316356…` (1814 events), byte-identical across repeated runs and processes.
  - Precise P2–P4 metrics are T5 validators.
- **M1 regression:**
  - golden event-log sha256 `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` is unchanged on the reference host;
  - CI hosts stay within the approved cross-platform bounds;
  - M1 Proof passes against the unchanged `proof/thresholds/m1.json`, and the GMAT comparison passes;
  - the v1 scenario hash and the M1 timeout limit (5908 ticks) are unchanged;
  - a v2 scenario without propulsion reproduces the M1 events.
- **Decisions:** DR-0014 amendment (T3 semantics confirmed 2026-10-11); DR-0018 (approved option A, 2026-10-11); ADR-0007 T4 notes. **Contract:** `docs/contracts/m2-commands-and-events.md` §"Scenario timeline and emission (T4)".
- **Review:** `docs/reviews/M2-T4-review-01.md`. Codex FAIL, then three CONDITIONAL PASS rounds, then **PASS**. 13 findings (F1–F5, N1, M1, K1–K5) were all accepted, resolved and mutation-tested; most of the K-class predates T4.
  - **Final independent verdict: PASS** (session `01a12bec-aac4-7d11-9b17-ae683ddb6f86`).
- **Known limitations allowed at the prototype bar:**
  - no explicit end event for burns still active at the stop (DR-0018 option A, approved: by design);
  - the envelope tick of an ignition at its own submission tick is the next tick (documented);
  - FU-1 remains open for T7.
- T5 was authorized on 2026-10-11 (below).

## T5 — Validators O1–O8, m2_proof.py, provisional m2.json, reference missions: COMPLETE (2026-10-11)
- **Final revision:** `21dac47`. CI is green on ubuntu-latest x86_64 and macos-latest arm64 (run 38171632918). CI covers lint, 829 tests, cross-process determinism (M1 and every M2 scenario), cross-platform M1 golden agreement, GMAT M1 comparison, M1 Proof and the full M2 Proof.
- **Decision:** DR-0018 approved, option A (`fc3483a`).
- **Delivered:**
  - `src/tars/validation/m2.py`:
    - oracles O1–O8;
    - `audit_run()`, which checks every simulator output of a run against an independent expectation or an exact rule;
    - predictions from scenario inputs only, including the exact DR-0017 D1a cutoff.
  - `src/tars/validation/m2_missions.py`: the missions with hand-declared receipts and diagnostics.
  - `toolbox/validators/m2_proof.py`:
    - audits every run it creates: missions, derived variants, four DR-0018 stop variants, and the O6 and O8 auxiliary runs;
    - requires every emitted metric to be gated unless it is declared report-only.
  - `proof/thresholds/m2.json` (**provisional**; basis per group).
  - Scenarios `m2_retrograde_burn`, `m2_burn_to_depletion` and `m2_invalid_commands`, plus derived empty-tank and no-propulsion variants. Together they exercise all 10 rejection codes.
  - `tests/test_m2_validation.py`: 124 tests, including log mutations and physics mutants.
- **Evidence:** `proof/records/evidence/M2-T5/m2_proof_report.json` and stdout, at `21dac47` on the reference host: **206 / 206 checks PASS**, thresholds provisional. Measurements, methods and units are in **VAL-0013**.
  - **O1/O2:** propellant used ≤ 9.2e-17 of the initial mass. Sensed Δv vs the rocket equation ≤ 5.6e-14 relative; zero excess over the analytic RK4 (Simpson) truncation bound.
  - **O3:** free-space velocity 1.8e-14 relative; position order 3.80 and 3.88; timing exact.
  - **O4:** vs independent DOP853 at 53 700 s: 0.290 / 0.313 / 0.289 / 0.297 / 0.298 m.
  - **O5:** coast ≤ 0.314 m.
  - **O6:** |p − 2| ≤ 0.0041; slice ratio 2.6e-6.
  - **O7:** signs exact; plane rotation ≤ 1.5e-16 rad.
  - **O8:** orders 4.28–4.33 and 4.14–4.21.
  - **Node crossings:** ≤ 4.0e-5 s.
  - **Altitude extrema:** ≤ 6.3e-3 m.
- **P-requirement evidence, provisional thresholds:**
  - **P1:** slice ignition and cutoff exact.
  - **P2:** O1, O2.
  - **P3:** O7; prograde raises and retrograde lowers SMA and energy; apsides are reported.
  - **P4:** O3–O6, O8.
  - **P6:** same-platform determinism. Cross-platform M2 bounds are T7.
  - **P7:** declared receipts; the control runs are bit-identical; depletion is exact (D1a).
  - **P9:** schema version and re-validation.
  - **P10:** M1 is unchanged.
  - P5 (GMAT, T6), the threshold approval (T7) and P11/P12 (T8) remain.
- **Same-tick reporting** (approved T3 behavior, unchanged): a burn submitted at tick 60 for ignition at 600 s is reported at tick 61. It is tested and documented in the contract.
- **DR-0018 (A) verified:**
  - no fabricated `BurnEnded`;
  - the final sample shows the active or pending burn;
  - physics up to the stop is byte-identical to a longer run;
  - a cutoff or ignition exactly at the stop is emitted.
- **Numerical finding:** the sensed-Δv error at high mass flow is RK4 (Simpson) truncation, predicted by the analytic bound to 2–3 %. The O2 gate applies the unchanged round-off allowance to the error beyond that computed bound. Flagged for T7.
- **M1 regression:**
  - the golden sha256 `7a4e1877…` is exact on the reference host;
  - CI hosts are within the approved bounds;
  - M1 Proof, GMAT M1 and `m1.json` are unchanged.
- **DR-0017 separation:** each burn's timing Δv bound is reported and recomputed as a timing quantity only. Trajectory error comes only from O4, O5 and O8.
- **Review:** `docs/reviews/M2-T5-review-01.md`. Codex FAIL → FAIL → FAIL → **PASS**. 18 findings (F1–F18), all accepted, resolved and mutation-tested. **Final independent verdict: PASS** (session `01a12c9d-d05d-7973-83ed-f9fbfb734ee2`).
- **Limitations at the prototype bar:**
  - Thresholds are provisional, measured on one reference host and two CI hosts; T7 has not run.
  - O9/GMAT M2 is T6.
  - FU-1 is open: GMAT gates must respect the 11–15 µm DOP853 floor.
  - The validators need the dev group (SciPy).
- **Next:** T6 (authorized 2026-10-11; see below).

## T6 — GMAT M2 finite-burn reference and O9: COMPLETE (2026-10-13)
- **Final revision reviewed:** `e7c0148`. A post-review documentation-only wording correction (round 18's note) follows.
- **CI:** green on ubuntu-latest and macos-latest, every job confirmed complete (run 38482342000). CI covers lint, 1,101 tests, cross-process determinism (M1 and every M2 scenario), cross-platform M1 golden agreement, GMAT M1 and M2 comparisons, the M1 Proof and the full M2 Proof, verified against the reference snapshot.
- **Decisions:**
  - DR-0019 approved, option B (review threat model).
  - DR-0020 approved, option A (verdict relevance; F42 and F43 accepted residual risk).
  - DR-0021 approved, option A (approved reference snapshot; seven conditions, confirmed complete).
  - DR-0022 approved, option B (validator runtime state out of scope; two accidental-corruption safeguards).
- **GMAT configuration and reproduction.**
  - GMAT R2026a: NASA-signed `GmatConsole`, build "Mar 26 2026 19:40:08", sha256 `1162803d…52e2` (pinned in `gmat_m2.APPROVED_GMAT`).
  - Aligned stepping (DR-0016): coasts at 60 s, burns at 1 s, one-step realignment arcs. Point-mass Earth. Ideal constant-thrust engine with velocity-tracking VNB pointing. Standard gravity overridden to the TARS value (VAL-0009).
  - Rows are labelled from the step schedule; the first epoch is anchored to the configured TT epoch in A.1.
  - Missions: `m2_prograde_burn`, `m2_retrograde_burn`, `m2_invalid_commands`. Depletion is excluded from GMAT (VAL-0009 finding 4).
  - **Reproduce:**
    - `uv run python toolbox/scripts/gmat_m2.py generate --out <dir>` previews the scripts;
    - `... gmat_m2.py run` stages, evaluates and publishes, then prints the digest to pin;
    - `... gmat_m2.py compare` checks the committed references (no GMAT needed).
  - Raw scripts, reports, console logs and metadata are in `toolbox/references/gmat/m2/`. The reports are byte-identical to `1de827e`. The manifest has a hash-chained history and its sha256 is pinned in `approved_digests.py`.
- **O9 results against provisional limits** (reference host; `evidence/M2-T6/m2_proof_report.json` and stdout; VAL-0014):

| Metric (worst of 3 missions) | Value | Limit |
|---|---|---|
| GMAT vs independent DOP853, position / velocity | 4.66e-6 m / 5.39e-9 m/s | 3e-5 m / 3.5e-8 m/s |
| GMAT coast vs Kepler, position / velocity | 4.01e-6 m / 4.63e-9 m/s | 1e-4 m / 1e-7 m/s |
| GMAT mass vs analytic | 2.25e-11 kg | 1.3e-9 kg |
| Step spacing; burn duration from mass | 2.34e-7 s; 1.41e-10 s | 1e-6 s; 1e-9 s |
| Simulator vs GMAT, samples and final | 0.313 m / 3.64e-4 m/s | 0.6 m / 7e-4 m/s |
| Simulator vs GMAT, burn boundaries (slices; invalid-commands) | 7.8e-4 m; 8.0e-3 m | 2e-3 m; 1.6e-2 m |
| Simulator vs GMAT, mass; node crossings | 2.25e-11 kg; 3.99e-5 s | 1.3e-9 kg; 8e-5 s |

  GMAT agrees with the independent DOP853 reference to the 11–15 µm floor class. The simulator-versus-GMAT differences match the simulator-versus-DOP853 differences of O4, so they are TARS's RK4 error (dt = 10 s), not a modelling disagreement. No O9 gate is below the 15 µm floor (FU-1 respected).
- **M2 Proof:** **215 / 215 checks PASS** against reference snapshot baseline 3. The 213 checks from before DR-0021 are byte-identical in name, metrics, thresholds and result, plus the exact checks `reference_snapshot` and `reference_snapshot_margins`. All 48,310 records and 982,324 values are compared.
- **Reference snapshot (DR-0021, VAL-0015).**
  - Every reference-derived value is pinned and verified: DOP853, the Kepler and RK4 anchors, O5, O6, node crossings, O3, O9 and the scenario predictions. Seven exclusions are documented.
  - **Baseline 3** (`a2cddf4b…448b`) was generated from a clean tree. It was approved by `verify-baseline`, which checks:
    - the inventory against a fresh recording;
    - every part recomputed independently (universal-variable Kepler, LSODA, re-derived scenario values);
    - node crossings enumerated independently;
    - DOP853 against GMAT.
  - **Tolerances:** the smallest 1-2-5 value ≥ max(10 × measured, 10 ulp). Measured over 24 cross-platform runs.
  - **Acceptance protection:** ref and gmat values are consumed from the snapshot. Sim-seeded gates keep margins above the worst shift a within-tolerance deviation could cause.
  - **DR-0022 B safeguards:** the digest is re-verified at the end of every run, and verification mode is asserted.
- **Negative and mutation tests:**
  - `tests/test_gmat_m2.py` (184): artifact, threshold, row and workflow mutants; provenance; anchors; the F47–F51 coordinated-corruption regressions.
  - `tests/test_reference_snapshot.py` (82): ledger mechanics, authentication, immutability, margins, the F50/F51/F52 regressions, baseline-approval corruptions (F53–F56), fail-closed sessions (F57) and the DR-0022 safeguards.
  - Every mechanism was mutation-tested: disabling it fails its targeted tests (review record).
- **Review:** `docs/reviews/M2-T6-review-01.md`. 18 Codex rounds, 59 findings:
  - F42 and F43: accepted residual risk (DR-0020);
  - F50 and F51: fixed by DR-0021;
  - F58: rejected with reasoning (DR-0022);
  - every other finding: accepted and fixed.

  **Final independent verdict: unconditional PASS** (round 18, session `01a13786-1001-7861-8f77-87cd0ff53796`).
- **Impact on O1–O8 and M1:**
  - O1–O8 checks and values are unchanged, except the documented T6 refinements: the altitude extrema are now taken from the independent anchors (≤ 2e-8 m change, review round 12), and all 213 prior checks are identical since then.
  - M1 Proof, GMAT M1, `m1.json` and the golden sha256 `7a4e1877…` are exact on the reference host and within approved bounds on CI.
- **DR-0017 / DR-0018:** the timing Δv bound stays separate from trajectory error, and the stop semantics are preserved and verified.
- **Limitations at the prototype bar:**
  - The M2 thresholds remain provisional until T7.
  - GMAT runs on the reference host only; CI compares the committed artifacts.
  - The validators need the dev group (SciPy).
  - The O6 margin bound is 0.0405 against 0.05 (a T7 consideration).
  - The Proof takes about 135 s.
- **Next:** T7 (authorized 2026-10-13; see below).

## T7 — Three-platform measurement and threshold decision: MEASUREMENT COMPLETE, DECISION PENDING (2026-10-13)
- **Measured:** 11 bundles on the DR-0008 matrix at `2870392`: the macOS x86_64 reference host, Linux x86_64 ×5 on four CPU types, and macOS arm64 ×5. Clean trees, identical input digests. VAL-0016; evidence in `proof/records/evidence/M2-T7/`.
- **Results:**
  - M2 Proof 215/215 on all 11.
  - Determinism byte-identical everywhere: cross-process for the four M2 scenario files and M1, and in process for all six missions.
  - Simulator cross-platform drift ≤ 7.2e-6 m (final state).
  - Reference drift is removed from the verdict by the snapshot: zero spread on every O9 reference metric.
  - Every margin is ≥ 1.5× (O8 policy) and ≥ 1.9× for truncation-type gates.
- **Decision request:** DR-0023.
  - Approve every provisional value unchanged.
  - FU-1: keep the O9 GMAT gates and close FU-1.
  - O6: no change (a dedicated SMA class only with a future tightening).
  - Add an M2 cross-platform final-state gate at the M1 bounds (proposed, not implemented).
- **Not changed:** thresholds, reference values, snapshot tolerances and checks. `m2.json` stays provisional until DR-0023 is approved. T8 is not started, and PR #3 is not merged.

## REV-012 — resolved
VAL-0010, DR-0016; CI-reproduced by `tests/test_rev012_evidence.py`.
