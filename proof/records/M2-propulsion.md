# Proof Record — Milestone 2: Propulsion & Orbital Maneuvers (in progress: T1–T3 complete)

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

## REV-012 — resolved
VAL-0010, DR-0016; CI-reproduced by `tests/test_rev012_evidence.py`.
