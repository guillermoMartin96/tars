# Proof Record — Milestone 2: Propulsion & Orbital Maneuvers (in progress: T1–T4 complete)

**Milestone result:** not yet claimed. M2 Proof (P1–P12, `docs/milestones/M2-propulsion.md` §10) is evaluated at T8.
- This record collects completed task evidence only (REV-013 lesson).
- Thresholds: none approved for M2 yet. DR-0015 is conditional; GMAT gate recalibration is tracked as FU-1.

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
  - stop semantics: a burn crossing the stop is an observation horizon, under DR-0018 (open);
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
- **Decisions:** DR-0014 amendment (T3 semantics confirmed 2026-10-11); DR-0018 (open, blocks nothing); ADR-0007 T4 notes. **Contract:** `docs/contracts/m2-commands-and-events.md` §"Scenario timeline and emission (T4)".
- **Review:** `docs/reviews/M2-T4-review-01.md`. Codex FAIL, then three CONDITIONAL PASS rounds, then **PASS**. 13 findings (F1–F5, N1, M1, K1–K5) were all accepted, resolved and mutation-tested; most of the K-class predates T4.
  - **Final independent verdict: PASS** (session `01a12bec-aac4-7d11-9b17-ae683ddb6f86`).
- **Known limitations allowed at the prototype bar:**
  - no explicit end event for burns still active at the stop (DR-0018);
  - the envelope tick of an ignition at its own submission tick is the next tick (documented);
  - FU-1 remains open for T7.
- **Not started:** T5 and later (needs authorization). The draft PR (#3) is not merged.

## REV-012 — resolved
VAL-0010, DR-0016; CI-reproduced by `tests/test_rev012_evidence.py`.
