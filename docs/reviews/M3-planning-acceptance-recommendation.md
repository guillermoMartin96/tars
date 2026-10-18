# M3 Planning — acceptance recommendation (for the Tech Lead's decision)

**Prepared:** 2026-10-17, under I-12 §8 ("Even if Review 13 returns PASS, do not merge or begin M3 implementation. Prepare an acceptance recommendation for my decision.").
**Status: NOT ACCEPTED.** This is a recommendation. Planning acceptance, the planning merge, T0, T1 and T2 each remain the Tech Lead's separate decision. Nothing has been merged, and no M3 implementation has begun.

**Branch:** `milestone-3-planning`, documentation only (every change against `main` = `d92ab89` is under `docs/`). The package was reviewed at `59c9f9e` (Review 13 prompt commit); the content under review is `602ede0`.

## Recommendation
The planning package is ready to be presented for planning acceptance as documentation evidence. I recommend that the Tech Lead accept the M3 planning checkpoint, with every OPEN, DEFERRED, T0 → owner and NOT AUTHORIZED item below carried forward unchanged, and decide separately whether to authorize the planning merge and then T0.

Basis:
- **Independent review:** Codex Review 13 returned an unconditional PASS with no new findings, and reports every tracked finding (rounds 01–12) RESOLVED (`docs/reviews/M3-planning-review-13.md`).
- **No unresolved review finding.** Every finding of rounds 01–12 is dispositioned and recorded in `docs/milestones/M3-decision-matrix.md`, with its correction.
- **Proof:** full M1 and M2 Proof PASS at `24c2d98` in an isolated clone (9 and 20 steps; pytest 1185 passed, 0 failed, 0 skipped; m2_proof 228/228); CI success on all four jobs for `602ede0` (run 39084190524) and `24c2d98` (run 39084025411).
- **M1/M2 unchanged.** `src/`, `tests/`, `toolbox/`, `scenarios/` and `proof/` are unchanged since `d92ab89`; the pinned references and goldens have their baseline digests; the registers only gained lines (218/0 and 43/0).

## What the package decides
- **G0:** Option A, J2 + atmospheric drag (approved 2026-10-15).
- **G1–G3:** DR-0024 (physical models and constants), DR-0025 (validation strategy), DR-0026 (architecture), recorded as ADR-0009.
- **DR-0027:** termination altitude and atmosphere table, resolved with conditions.
- **DR-0028:** J-ax-1, a non-rotating Earth-axis-aligned model, with requirements R-1…R-4, and its Resolution amendments 1–9.

## Findings resolved (rounds 01–12)
| Round | Findings | Final state |
|---|---|---|
| 01 | M3P-F1…F5 | RESOLVED |
| 02 | M3P2-F1…F3 (F2 rejected with reasoning, preserved) | RESOLVED |
| 03 | M3P3-F1/F2 | RESOLVED |
| 04 | M3P4-F1/F2 (DR-0028 limitation statements) | RESOLVED (amendment 1) |
| 05 | M3P5-F1 (signed formulas) | RESOLVED (amendment 2) |
| 06 | M3P6-F1…F3 (line-of-nodes domain, node jump, wrapping interval) | RESOLVED (amendment 3) |
| 07 | M3P7-F1 (finite-only wrap) | RESOLVED (amendment 4) |
| 08 | M3P8-F1 (non-finite values, coverage minima) | RESOLVED (amendment 5) |
| 09 | M3P9-F1…F3 (oracle ±∞, per-formula order and sign, E3/E4) | RESOLVED (amendment 6) |
| 10 | M3P10-F1/F2 (exceptions in mutants; assertion classification) | RESOLVED (amendments 7–9) |
| 11 | M3P11-F1/F2 (defect-specific exercise; classification) | RESOLVED (amendments 8–9) |
| 12 | M3P12-F1/F2 (oracle observation at every step; E6 sign split) | RESOLVED (amendment 9) |

Since amendment 4, every correction has been to the verification tooling of DR-0028, not to its mathematics: the signed formulas, the convention, the oracle, the grid, the tolerances and the coverage minima are unchanged, and no finite result has changed.

## Remaining risks
- **The DR-0028 verification tooling is planning research, not a Proof gate.** Its guarantees are stated for its fixed inventory: 48 built-in mutants, 109 file-level mutations, 30 controls, and 19 classified assertions (12 A, 4 B, 3 C). The exercise probe does not defend against a copy written to detect it; this scope is documented (amendment 9), and Review 13 found that it hides no defect in the inventory. The 4 B assertions are redundant by argument; three of them (W4, E6-value, E6-sign-oracle) rely on `wrap()` and the oracle being pure functions. The 3 C assertions are diagnostic.
- **Accepted physical approximations** (decisions, not defects):
  - J-ax-1 ignores the real pole offset: 117 m after 10 orbits (J2 only) between frame z and the 2026 mean pole (VAL-0018). The node error is not bounded by the pole tilt (amendment 1).
  - The atmosphere table is conditionally approved: 25 of 28 values identical to the author's data file; disputed cells and the missing 1000 km row are documented; the printed edition was not checked (DR-0027 B).
  - dt = 10 s is provisional (Q-G2-4); M3 numerical thresholds are not approved (a later threshold DR, G4).
- **Limits of the independent review.** The reviewer ran complete standalone validators, not the Proof wrappers or the full pytest suite, could not access CI, and ran no fresh GMAT executable or three-platform execution. The implementer ran the full Proof wrappers; CI covers Ubuntu, macOS, Intel macOS and the M2 cross-platform gate.
- **Effort concentration.** Reviews 07–12 all found defects in the verification tooling rather than in the decisions. The tooling is now considerably larger than the mathematics it checks. That is not a defect, but it is a maintenance cost to weigh if the scripts are carried into later milestones.

## Open, deferred and not-authorized items, and when each is needed
Nothing below has a default. Accepting the planning checkpoint does not decide any of them. "Needed before" follows the decision matrix's recorded deferral points and its Gates section ("T2 still depends on the DR-0027 T0 proposals (A-4, A-5, A-6, A-s, B-4) and the T0-checkpoint deferrals").

| Item | State | Needed before |
|---|---|---|
| Planning acceptance | Tech Lead's decision (this recommendation) | the planning merge |
| Planning merge | Needs explicit authorization (I-2 §7) | T0 |
| T0 (reference-configuration spike) | Needs explicit authorization and the planning merge | T1 |
| Q-G2-1 GMAT exact-configuration method | DEFERRED to the T0 checkpoint | decided at the T0 checkpoint; T2 depends on it (Gates) |
| Q-G2-5 reference missions | DEFERRED to the T0 checkpoint | decided at the T0 checkpoint; T2 depends on it (Gates) |
| Q-G2-7 source of geodetic-height test points | DEFERRED to the T0 checkpoint | decided at the T0 checkpoint; T2 depends on it (Gates) |
| DR-0024 Q9 values (C_d, A, initial mass, initial state) | Principle approved; values DEFERRED to the T0 checkpoint | decided at the T0 checkpoint; T2 depends on it (Gates) |
| DR-0027 A-4 permitted termination ranges | T0 → owner | T2 |
| DR-0027 A-5 event-crossing behaviour | T0 → owner | T2 |
| DR-0027 A-6 interaction with domain boundaries and `impact` | T0 → owner | T2 |
| DR-0027 A-s density for RK4 stages below the lower edge | OPEN (T0 → owner) | T2 |
| DR-0027 B-4 behaviour at unsupported altitudes | CONDITION; behaviour OPEN (T0 → owner) | T2 |
| Q-G2-2 identity-check sub-rule | PROPOSED (classification approved) | not tied to a stage in the matrix; to be decided when identity checks are first used |
| Q-G2-6 M3 reference-snapshot treatment | DEFERRED to T4 | T4 |
| M3 numerical thresholds | Not approved; threshold DR after T6 measurement (G4) | M3 Proof |
| T1 and later | NOT AUTHORIZED; each needs T0 evidence, independent review, the applicable checkpoint decisions and separate authorization | — |
| Q-G3-7 per-sample environment/drag telemetry | NOT AUTHORIZED | — |
| Additional Earth-orientation implementation (rotation angle, pole of date, EOP); solar ephemeris, Earth-orientation provider, local-solar-time output | NOT AUTHORIZED (DR-0028) | — |
| Rust, C, FFI, firmware, RTOS, real-time, embedded | NOT AUTHORIZED (DR-0026) | — |
| AT-1…AT-7 (future flight architecture) | OPEN; no M3 stage depends on them | — |
| `research/flight-software-architecture` | Not merged | — |

## Decision requested
1. Accept, or decline, the M3 planning checkpoint as documented.
2. Separately, if accepted: authorize, or not, the planning merge into `main`.
3. Separately, after a merge: authorize, or not, T0.
