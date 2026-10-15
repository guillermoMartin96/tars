# M3 planning baseline and M1/M2 → M3 artifact impact analysis

**Status:** PLANNING RECORD (research and design only; no M3 implementation).  
**Date:** 2026-10-15  
**Related:** DR-0024 (G1), DR-0025 (G2), DR-0026 (G3), `M3-proposal.md`, VAL-0018.

## 1. Planning baseline (verified, not assumed)
| Item | Verified value | How |
|---|---|---|
| Baseline commit | **`main` = `d92ab894907d06b2b13aefff6c005caa0026a68f`** ("Merge pull request #3 …"; parents `63bec8d`, `f05bc1e`) | `git rev-parse origin/main`, `git log` |
| Merge content | The tree of `d92ab89` is identical to the reviewed final candidate `f05bc1e` | `git diff f05bc1e d92ab89`: empty |
| CI on the baseline | Run 38799635788 (push, `d92ab89`): `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`, all success. Three-platform gate 7.23e-6 m / 8.43e-9 m/s | `gh run view` |
| M2 Proof | 228/228 in the M2 evidence (`proof/records/evidence/M2/`, run at `017d7f6`). **Re-run at `d92ab89`: 228/228, identical check by check (§1.1)** | Evidence files; fresh re-run |
| M1 golden | `events_sha256` `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` | `proof/references/m1_final_state.json`; re-run in §1.1 |
| Pinned digests | m1.json `446e75ee…`, m2.json `9d4eab47…`, GMAT M2 manifest `f8d6bd78…`, snapshot `a2cddf4b…`, M2 golden `dc3baf7a…` | sha256 of the blobs at `d92ab89` equals `src/tars/validation/approved_digests.py` |
| **M3 implementation started?** | **No.** Checked as follows: | |
| | `src/`, `tests/`, `scenarios/`: no J2, drag, atmosphere or density code. The only J2 mention is `EARTH_J2_APPROX`, informational for M1 VAL-0007 | `git grep` at `d92ab89` |
| | No M3 scenario, threshold, reference, validator or golden exists | `git ls-tree` |
| | Remote branches: `main`, `milestone-1-orbit`, `milestone-2-propulsion-…`, `milestone-3-planning` (planning documents only), `research/flight-software-architecture` (documents only), two historical review/investigation branches | `git branch -r` |
| Planning branch | `milestone-3-planning`, created from `d92ab89`. It changes documentation and research artifacts only: `docs/milestones/`, `docs/decisions/requests/DR-0024…0026`, `docs/science/experiments/m3-planning/`, an appended planning entry in `docs/science/validation.md`, `docs/reviews/` | `git diff --stat d92ab89..milestone-3-planning` |

**Note on the prompt's branch name:** the instruction mentions `research/flight-architecture`. The branch that exists is `research/flight-software-architecture` (head `27ad862` before this checkpoint). It is treated as the same branch. This is a naming difference, not a conflict.

### 1.1 Fresh baseline re-run at `d92ab89` (detached worktree, clean)
Run on 2026-10-15 in a detached worktree at `d92ab894907d06b2b13aefff6c005caa0026a68f` with a clean tree. Host: macOS 26.2 x86_64 (i9-9880H), `uv sync --locked`.
| Check | Result |
|---|---|
| `toolbox/validators/cross_platform.py` (M1 golden) | PASS; final position and velocity difference 0.0 m and 0.0 m/s; `bit_identical_to_golden` = 1 |
| `toolbox/validators/determinism.py` (M1, cross-process) | PASS; both runs `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` |
| `toolbox/validators/m2_proof.py` | **PASS, 228/228**, thresholds approved. **Identical to `proof/records/evidence/M2/m2_proof_report.json` in every check's validator, metrics, thresholds and verdict** |

The run outputs were kept in the session scratchpad and are not committed: they would duplicate the accepted M2 evidence, which this checkpoint must not alter.

## 2. Frozen historical evidence (class A): must remain unchanged
Each entry is identified by its git object id at `d92ab89` (`git rev-parse d92ab89:<path>`; a tree id covers every file below it). "Unchanged" means: same object id, and the same pinned digest where one exists.

| Path | Object id at `d92ab89` | What it proves | Why frozen |
|---|---|---|---|
| `scenarios/m1_leo_250km.json` | `4be339d0…` | M1 mission definition (v1) | `scenario_hash` `603152ad…` binds the M1 golden, GMAT M1 and the informational runs |
| `scenarios/m2_{prograde_burn,retrograde_burn,burn_to_depletion,invalid_commands}.json` | `cb1fca0d…`, `64cb6190…`, `33b379b9…`, `995b0cfe…` | M2 mission definitions (v2) | Bind the M2 golden, snapshot, GMAT M2 and the thresholds |
| `proof/thresholds/` (m1.json, m2.json) | tree `f5d6dfee…` | Approved M1 (DR-0008/0009) and M2 (DR-0023) thresholds | sha256-pinned in `approved_digests.py` |
| `proof/references/` (m1_final_state.json, m2_final_states.json) | tree `cadf6438…` | M1 golden (events hash `7a4e1877…`); M2 reference-host golden | M2 golden sha256-pinned; M1 hash is a hard constraint |
| `toolbox/references/gmat/m1_two_body.{script,report,metadata}` | `db60a883…`, `aa32cbb4…`, `eb0973a0…` | M1 against GMAT (VAL-0004, DR-0009) | Committed reference; replacement only with explicit review |
| `toolbox/references/gmat/informational/` | tree `336a1387…` | VAL-0007: realistic-model divergence, informational | Historical record. **Caveat:** its J2/realistic runs used the JGM-3 file GM (DR-0025 §13); recorded, not edited |
| `toolbox/references/gmat/m2/` | tree `359fbf01…` | O9 GMAT finite-burn references and manifest (VAL-0014) | Manifest sha256-pinned |
| `toolbox/references/snapshot/m2/` | tree `c806ed4d…` | DR-0021 approved reference snapshot, baseline 3 | sha256-pinned; DR-0021 condition 3 |
| `docs/contracts/m2-commands-and-events.md` | `da1d9553…` | M2 command and event contract | Accepted contract |
| `proof/records/M1-orbit.md`, `M1-independent-audit.md`, `M2-propulsion.md` | `e2a05c3f…`, `8eaf8dc8…`, `d8b552bc…` | Proof records (M1 PASS; M2 PASS, accepted 2026-10-15) | Accepted acceptance records |
| `proof/records/evidence/` | tree `9999f757…` | Every M1/M2 evidence bundle | Evidence of accepted Proofs |
| `src/tars/validation/`, `toolbox/validators/`, `toolbox/scripts/` | trees `86778bc5…`, `acd735ef…`, `cdcfd472…` | M1/M2 validators and acceptance logic | Must not change semantics. M3 validators are new files; the shared-module rules are in class C |
| `.github/workflows/` | tree `12d274fb…` | Required CI (M1 and M2 gates, three-platform gate) | M3 CI steps are additive only (class C) |
| `uv.lock`, `pyproject.toml` | `3837875d…`, `550b030c…` | The locked environment of all M1/M2 evidence | A lock change needs a dependency DR and re-verification of every M1/M2 gate |
| The **M1/M2 entries** of `docs/science/assumptions.md` (SCI-0001…0012) and `docs/science/validation.md` (VAL-0001…0017) | blobs `75910fd0…`, `599f6110…` | Scientific basis of M1/M2 | Append-only registers: new entries may be added, existing entries are not rewritten. Errata are appended notes approved by the Tech Lead (DR-0024 Q3, DR-0025 Q-G2-8) |
| ADR-0001…0007, DR-0001…0023 | (as at `d92ab89`) | Accepted decisions | Superseded only by new records, never edited in substance |

**Rule (proposed for adoption with G3):**
- If J2 or drag means an M1/M2 scenario would produce a different trajectory, that is a **new physics configuration with a new identity** (`physics_id`, DR-0026), expressed as a new v3 scenario.
- It is never a regeneration of an M1/M2 golden, reference or snapshot.
- v1/v2 files cannot express J2 or drag at all, because their schemas are frozen literals.

## 3. New M3 evidence (class B): introduced by M3, none exists yet
| Artifact | Proposed by | Notes |
|---|---|---|
| `scenarios/m3_*.json` (schema v3) | DR-0026 | Reference missions per DR-0025 Q-G2-5. Each carries its environment selection; `physics_id` is derived |
| Pinned atmosphere dataset(s) and their digests | DR-0024 §7, DR-0026 §5.3 | The full table plus a one-band validation table |
| Named constant set (WGS 84 + EGM2008 C̄20, or as decided) | DR-0024 §7 | New set beside `WGS84`; `WGS84`'s M1 meaning unchanged |
| `proof/thresholds/m3.json` | DR-0025 §9–10 | Provisional, then approved by an M3 threshold DR; digest pinned |
| `proof/references/m3_final_states.json` | DR-0025 §9 | Keyed by mission and `physics_id` |
| `toolbox/references/gmat/m3/` | DR-0025 Q8 | Generated `.cof`, atmosphere file copy, TOEEq scripts, reports, metadata, digest manifest |
| `toolbox/references/snapshot/m3/` | DR-0025 Q-G2-6 | Only if the DR-0021 mechanism is extended to M3 |
| `toolbox/validators/m3_proof.py`, `toolbox/scripts/run_m3_proof.sh`, M3 tests | DR-0025 | New files |
| `proof/records/M3-*.md`, `proof/records/evidence/M3/` | M3 Proof | — |
| SCI-0013…0017, VAL-0018+ | DR-0024, DR-0025 | Appended register entries |
| ADR-0009 (force context, physics identity) | DR-0026 Q-G3-11 | PROPOSED until implemented and proven |

## 4. Potentially versioned shared infrastructure (class C)
Infrastructure that M1, M2 and M3 will all run through. Each change must be **additive**, keep the v1/v2 paths byte-identical, and be proven by the class-A gates in the same change.
| Component | Today | M3 change (proposed) | Protection |
|---|---|---|---|
| `tars.sim.forces` | `ForceModel(t, r, v)`, `CompositeForceModel` | New context protocol plus a legacy adapter; new pure components (DR-0026 D2/D3) | M1 golden byte-identical; M2 Proof 228/228; the frozen M2 validator's `FreeSpace` keeps working unchanged |
| `tars.sim.simulator` | Derivatives call `force_model.acceleration(t, r, v)` | Derivatives build `ForceContext` from the stage state | Same gates; atomic-tick and step-splitting tests unchanged |
| `tars.sim.constants` | `WGS84`, `STANDARD_GRAVITY`, `EARTH_J2_APPROX` | Adds a named M3 set; nothing existing edited | WGS 84 literal test; M1 golden |
| `tars.sim.scenario` | v1, v2 | Adds v3; v1/v2 classes untouched | `scenario_hash` of every M1/M2 scenario unchanged (tested) |
| `tars.events.schema` | M1 and M2 events | Adds `PhysicsConfigured`; possibly an additive `failure_cause` value (DR-0026 Q-G3-6) | M1/M2 event bytes unchanged; round-trip tests |
| `tars.sim.runner` | v1 / v2 paths | Adds the v3 path | M1/M2 mission tests and goldens |
| `approved_digests.py` | Pins m1, m2, GMAT M2, snapshot, M2 golden | Adds M3 pins in new entries; existing digests untouched | Review |
| CI workflow | M1/M2 gates | Adds M3 steps; no M1/M2 step removed or weakened | Review; DR-0021 condition 7 spirit |
| Determinism and cross-platform tooling | M1/M2 | Extended to M3 missions with M3-only bounds | M2 bounds never reused (DR-0025 §7) |
| GMAT script generators | `gmat.py`, `gmat_m2.py` | A new M3 generator; existing generators unchanged | GMAT M1/M2 compares unchanged |

## 5. Observations on historical records (reported, not edited)
1. **SCI-0005 wording.** It calls GM = 3.986004418e14 "TT-compatible". IERS Conventions (2010) Table 1.1 labels that value TCG-compatible; the TT-compatible value is 3.986004415e14 (§1.2). M1 configured GMAT with the same value, so **no M1 result changes**. Proposed: an appended erratum note, if the Tech Lead agrees (DR-0024 Q3).
2. **VAL-0007 metadata.** The informational GMAT runs override `Earth.Mu`, but GMAT's gravity field applies the coefficient file's GM: JGM-3, 3.986004415e14, with R = 6378136.3 m (measured in the M3 probe). The ~0.6 m effect is negligible against those runs' 741–1 325 km results, and they gate nothing. Proposed: an appended note (DR-0025 Q-G2-8).

Neither observation affects an accepted check, threshold or acceptance decision.
