# M3 T2 — Report

**Status: S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED.** S2–S6 are not started.
**PC-7(T2 overall): NONE.**

**Authority:**
- I-40, the S1 contract: `M3-T2-S1-authorization.md` on `milestone-3-t2-authorization`;
- owner rulings I-41 … I-50, recorded on that branch;
- owner instructions I-51 … I-54B:
  - I-54 authorizes this report (Commit E) only, local and not pushed;
  - I-54A authorizes the read-only T-09 verification;
  - I-54B accepts I-54A and resumes Commit E.

**Records not on the planning branch.** I-51 (Commit C), I-52 (Commit D), I-53 (B–D push), I-54
(this report), I-54A (T-09 verification) and I-54B (resumption of this report) are **not recorded on
the planning branch** or elsewhere in the repository. Their verbatim texts exist only in the
implementer's external evidence (§S1.12). Nothing here implies such a record exists.

## S1 — ForceContext, context-aware protocol and legacy adapter (PC-7(S1))

### S1.0 Governing documents (verified 2026-10-30)

All are on `milestone-3-t2-authorization` at `b0561a9a59586c30a15e8f9cbc532bc6257926c7`.

| Document | sha256 |
|---|---|
| I-40 `M3-T2-S1-authorization.md` | `1b6bc40cf657a9995211462d437794a91df3f345df88dba9d986b3a1d07b78c6` |
| Final proposal v3-S `M3-T2-S1-proposal-v3.md` (pinned by I-46 D1) | `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d` |
| Plan amendment A-1 `M3-T2-S1-test-plan-amendment-I46.md` (I-46 D2) | `04aca5f42e59748c89bdcbf2e3e6b051903068bb842aeeaa37e9e77213542db3` |
| `docs/science/experiments/m3-t2/s1-v3/prototype-v3.patch` | `6199a6e644dac0988e4a14e9d56d40b2db5f5c77fba410af314360be5753731b` |

Other decision records on that branch:
- `M3-T2-S1-decisions-I41-I43.md`;
- `M3-T2-S1-decision-I44.md`;
- `M3-T2-S1-decision-I45.md` (I-45, I-46);
- `M3-T2-S1-decision-I48.md` (the P-5 and P-3 rulings);
- `M3-T2-S1-decision-I49-I50.md` (the Commit B sequencing correction).

### S1.1 Branch and HEAD (I-40 §5 item 1)

- **Branch:** `milestone-3-t2-s1-force-context`.
- **Remote head:** `1b25254e3c0a9787e1f01c428d3f0961ef5f0184` (Commit D). It was pushed under
  I-53 as an ordinary push, `abcf755..1b25254`.
- **This report:** Commit E, local only, not pushed (I-54, I-54B).

### S1.2 BASE and ancestry (item 2)

- **BASE:** `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`. `main` and `origin/main` are still at
  BASE.
- **Ancestry:** BASE → A → B → C → D → E (this commit). Every link is a single parent, with no
  merge, rebase, amend or force-push.

### S1.3 Commits and purpose (item 3; I-40 §12)

| Commit | SHA | Purpose | Pushed |
|---|---|---|---|
| A | `abcf7553ed58138db15493044c0f34429b643286` | T-07 failure-path characterization tests: `tests/test_s1_failure_paths.py`, 29 nodes, green at BASE code | I-47/I-48. CI 40961801315 4/4 |
| B | `234874b60f7e96c85387df52e63a671d1fe7dcdf` | The red-first ancestor: `tests/test_s1_force_context.py`. Lines 1–431 are the pinned prototype file (blob `367eca1`), giving 57 nodes T-01…T-06; appended are the A-1 T-04 (d) ×3 and (e) ×1 nodes | I-53, together with C and D. **Never a push tip** (OD-3, I-50) |
| C | `fed74284119562f59724b270ed5de4f21e734506` | Production implementation: exactly the `src/` hunks of `prototype-v3.patch`. The blobs `forces.py` `f347a0f` and `simulator.py` `22ca0ab` equal the patch targets | I-53, with B and D |
| D | `1b25254e3c0a9787e1f01c428d3f0961ef5f0184` | Evidence: `docs/science/experiments/m3-t2/s1/` (97 files), including the preserved `run_record.py` | I-53. CI 41094508497 4/4 |
| E | this commit | This report | **No** (I-54, I-54B) |

### S1.4 Changed paths (item 4; I-40 §6)

BASE..D:
- `src/tars/sim/forces.py`: additive;
- `src/tars/sim/simulator.py`: the import line, `_derivative` and `_powered_derivative` with its
  closures (OD-5);
- `tests/test_s1_failure_paths.py`;
- `tests/test_s1_force_context.py`;
- `docs/science/experiments/m3-t2/s1/`.

D..E: `docs/milestones/M3-T2-report.md` only.

Every path is in the I-40 §6 allowlist (T-11, §S1.7).

### S1.5 Implemented behaviour (I-40 §5 F1–F4; v3-S §1–§3)

- **F1 `ForceContext`:**
  - immutable (`__slots__`, with `__setattr__` and `__delattr__` raising);
  - `total_mass_kg` is an owned built-in `float` or `None`; absent mass is never `0.0` (OD-4);
  - `ForceContext(m)` validates at construction (powered);
  - `ForceContext.deferred(m)` converts at construction and validates on every read (coast; I-41
    option B);
  - neither raises `OverflowError` or `ZeroDivisionError`.
- **F2:**
  - `ContextForceModel` protocol;
  - `LegacyForceAdapter`: one call with the identical `t, r, v`; returns the identical object; lets
    exceptions propagate unchanged; immutable; does not probe signatures.
- **F3 closures:**
  - `_derivative` passes `ForceContext()` (mass absent).
  - **Coast** reads `prop = float(np.ndarray.__getitem__(y, _PROP))`, the stored binary64 through
    the base-class indexer, so no subclass hook, mask or warning applies. It then builds
    `ForceContext.deferred(spacecraft.dry_mass_kg + max(prop, 0.0))`: an owned snapshot (U-1,
    v3-S §3.1).
  - **Powered** builds `ForceContext(mass)` from its existing `mass`. That happens after the
    finiteness check, the F/m check, `law.direction` and `thrust_acceleration`, so the force call
    keeps its position (R-01).
- **F4:** every legacy model, including the T1 J2 model, runs through the adapter unchanged
  (DQ-5 (a)).
- **Unchanged:**
  - no new runtime validation (v3-S §1, I-45);
  - no change to `Simulator.__init__`, tick logic, scheduling, step splitting or atomicity
    (INV-8);
  - every arithmetic expression contributing to a returned derivative (INV-4).
- **Out-of-contract behaviour** differs from BASE only as disclosed in v3-S §6: a `list` stage,
  object dtype with `None`, and wrong-shape float64 stages.

### S1.6 Preconditions (I-40 §4) and OD-2 (item 5)

**Preconditions.** The authoritative live run was the I-48 re-run (2026-10-29T20:51:38Z–21:26:33Z).
It used the I-48 corrected P-5 (P-5A–P-5D) and the I-48 P-3 ruling, which accepted the existing
worktree instead of a new one.

| Check | Result |
|---|---|
| P-1 | `main`, `origin/main` and `ls-remote` are all at BASE |
| P-2 | the only matching ref is the local S1 branch at BASE; there is no remote match |
| P-3 (I-48 ruling) | worktree at BASE, 0 commits beyond BASE, not on the remote; only `run_record.py` (`435a2b7e…7353`) untracked and `.venv/` ignored; unchanged after the run |
| P-4 | run 40593193646 on `ee602c5`: push to `main`, 4/4 `success` |
| P-5 (I-48 P-5A–D) | 38 `SHA256SUMS` manifests and 1 176 entries pass; verifier exit 0 on all six gates; result identical to the committed one; gate selftest 0 failures; historical correction in `M3-T2-S1-decision-I48.md` §2 |
| P-6 | R-1…R-4 at BASE pass (see I-48) |
| P-7 | S1 run record captured (CPython 3.12.15, macOS x86_64, `uv.lock` `6d784550…`) |

The I-47 attempt stopped at P-5 (the 43-manifest count defect); I-48 ruled on it. The first two
I-48 re-runs failed on defects in the implementer's own harness, not in any precondition. Both are
preserved, and only run 3 counts (I-48 evidence).

**OD-2.** Option A was authorized, but its T-07 (a)/(b) delta is **not used** (I-42 (2); v3-S §1).
T-07 (a) and (b) keep their BASE assertions:
- (a) `FloatingPointError("non-finite state produced at tick 1")`;
- (b) `ValueError("position must be finite")`.

No replacement expectation was recorded because none applies. Observed: both pass unchanged at A
(BASE code) and at C/D (§S1.7).

### S1.7 Test evidence: red phase, green phase, T-07…T-11 (items 6–7)

Records are in `docs/science/experiments/m3-t2/s1/`. They were recomputed for D in fresh clones, on
macOS x86_64 with CPython 3.12.15.

| Gate | Record | Result |
|---|---|---|
| **Red first** (I-40 §9a), at B | `red_B/` | 61 failed and 29 passed. Every failure is a per-node `AttributeError: module 'tars.sim.forces' has no attribute …` (31 `ForceContext`, 30 `LegacyForceAdapter`); 0 collection errors. The 4 A-1 nodes fail in `_record_contexts` (A-1 §2). B is the red-first ancestor; it was never a push tip. |
| **Green**, at C | `green_C/` | S1 90/90 pass: the same 90 node IDs, and exactly the 61 red nodes turn green. Full suite 1 380 passed. `ruff check` and `ruff format --check` pass. |
| T-01…T-06 (including A-1 T-04 (d)/(e)) | `green_C/s1_classification.txt` | all pass at C; snapshot and lifetime behaviour in §S1.9 |
| T-07 (INV-6) | `green_C/` | 29/29, assertions unchanged from A (BASE behaviour preserved) |
| T-08 (INV-2, INV-4) | `t08/` | §S1.9 |
| T-09 (INV-7) | external, I-54A (below) | **PASS on one host (macOS x86_64)**: T-09A, T-09B and T-09C all pass. Not run on the CI platforms. |
| T-10 (§6, INV-8) | `t10_t11/ast_identity.txt` | 51 checks, 0 failures |
| T-11 (§6) | `t10_t11/t11_changed_paths.txt` | BASE..C: the 4 allowlisted production and test paths; no protected path changed |

**T-09 (INV-7), verified under I-54A.**
- **History.** T-09 was not run as I-40 §9a specifies during Commit C or D. The implementer found the
  gap while preparing this report under I-54, stopped, and escalated it. The owner authorized a
  read-only verification (I-54A, option (a)) and accepted its result (I-54B).
- **How it was run:**
  - in fresh clones of BASE `ee602c5` and D `1b25254`, outside the repository;
  - each set up with `uv sync --locked` (the same `uv.lock`, `6d784550…`);
  - on CPython 3.12.15, NumPy 2.5.3, macOS x86_64.
- **No repository change.** No production code, test or Commit D evidence was changed.
- **Evidence:** `~/tars-evidence/I-54A/` (`REPORT.md`, scripts, raw JSON, logs). Its
  `MANIFEST.sha256` has sha256
  `daae437158adb0761082f8393aeba5d63598c13041b205a494d79f9517e6ae33`.

| Part | Result |
|---|---|
| **T-09A** architecture scan | **PASS.** `pytest tests/test_validation.py::test_repository_passes_architecture_scan` at D: exit 0, 1 passed. `architecture.scan(src/tars)` returns 0 findings over 32 files. BASE is the same. |
| **T-09B** repeated evaluation bitwise identical | **PASS, 105/105 cases at both BASE and D** (massless 22, coast 31, powered 52). See below. |
| **T-09C** `vars(sim)` keys unchanged | **PASS, 230/230 checkpoints**, over 31 configurations. See below. |
| Negative control | **7/7** injected defects detected. |

- **T-09B, what was called:** the callables the simulator hands its integrator:
  - massless: `sim._derivative`;
  - coast: `_powered_derivative(None)`;
  - powered: `_powered_derivative(burn)`, for the `prograde` and `retrograde` laws.
- **T-09B, configurations:** force models `pm`, `pm_j2` and `j2`, using the S1 test fixtures, and the
  5 validated scenarios built as `run_scenario` builds them.
- **T-09B, inputs:**
  - the committed read-only state;
  - a writable copy of it;
  - the four RK4 stage inputs of tick 1;
  - a later committed state;
  - propellant at −1e-17 and at 0.

  Each closure was called twice with the identical objects.
- **T-09B, checks:** all exact:
  - type, dtype, shape, strides, flags and raw bytes are equal between the two results;
  - the first result is unchanged by the second call;
  - the input is unmutated;
  - the simulator's attributes are unchanged in identity and exact value;
  - the force model is unchanged.
- **T-09B, extra observation:** in all 105 cases, D's results are byte-identical to BASE's.
- **T-09C, configurations:** the massless, coast and powered paths, including inside-tick and
  split-tick burns and a burn-to-depletion configuration; the 5 scenarios; and 5 complete
  `run_scenario` runs.
- **T-09C, checkpoints:** after construction, after each closure is built and evaluated, after
  `schedule_burn`, and after each step.
- **T-09C, results:**
  - BASE and D have identical key sets at every checkpoint;
  - building or evaluating a closure adds no key;
  - the only two key sets are 12 keys without a spacecraft, and 13 with one. The extra key is
    `_committed_propellant_kg`, which already exists at BASE.
- **Negative control:** it injected a 1-ulp drift, a dtype change, input mutation, a simulator value
  change, a new simulator attribute (detected by both the state and the key check), and a new
  force-model attribute. All were detected.

**T-09 limitations:**
- **One host only.** It ran on one host (macOS x86_64) and **not on the CI platforms**; no
  cross-platform T-09 claim is made.
- **Not a regression gate.** The probe is external to the repository, not a committed test, so CI does
  not re-check T-09.
- **Integrator scope:** RK4 only, which is the only registered integrator. Custom integrators were not
  exercised by T-09; T-08 covers their compatibility.
- **Force-model scope:** `pm`, `pm_j2` and `j2`, and the scenarios' point-mass composites only.
  **User-defined force models were not tested.**
- **Repetition scope:** repetition was checked within one process, on the same objects. Determinism
  across processes is covered separately, by R-1, R-2 and the determinism test.
- **Failure paths were not tested** by T-09B: inputs that raise, such as non-finite states and F/m
  overflow. T-07 covers those failure paths.
- **Closure contents.** The namespace check compares top-level `vars(sim)` keys. **It does not inspect
  every object a closure captures.** In D the closures capture a `LegacyForceAdapter` instead of the
  raw model, as designed.
- **Depletion not asserted.** The burn-to-depletion configuration checks namespace keys only. **It did
  not independently assert that depletion occurred.**

### S1.8 Mutation campaign (item 8; I-40 §10 plus A-1 §3)

`mutation/`. Control: **90/90** S1 nodes pass (pytest exit 0). Kill criterion:
- a mutant is KILLED only if a designated node fails and **every** failure matches the mutant's
  declared reason pattern;
- for M-22, every designated node must fail (A-1 §3);
- each edit anchor must occur exactly once, or the campaign aborts;
- a collection error or crash cannot match a reason pattern;
- every pytest exit status was 0 or 1.

| Mutant | Designated nodes | Failed / run | Verdict |
|---|---|---|---|
| M-01 adapter copies r | test_t02_adapter_passes_identical_objects_once_and_returns_the_result | 4/4 | KILLED |
| M-02 adapter swaps r and v | test_t02_adapter_passes_identical_objects_once_and_returns_the_result | 4/4 | KILLED |
| M-03 adapter copies the result | test_t02_adapter_passes_identical_objects_once_and_returns_the_result | 4/4 | KILLED |
| M-04 adapter calls twice | test_t02_adapter_passes_identical_objects_once_and_returns_the_result | 4/4 | KILLED |
| M-05 adapter wraps exceptions | test_t02_adapter_propagates_the_identical_exception | 4/5 | KILLED |
| M-06 powered context from committed state | test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit | 3/4 | KILLED |
| M-06c coast context from committed state | test_t04_negative_round_off_propellant_gives_the_dry_mass_exactly, test_t04_invalid_coast_stage_mass_is_carried_and_rejected_on_read | 3/3 | KILLED |
| M-07 powered dry mass only | test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit | 3/4 | KILLED |
| M-07c coast dry mass only | test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit | 3/4 | KILLED |
| M-08 coast no clamp | test_t04_negative_round_off_propellant_gives_the_dry_mass_exactly | 1/2 | KILLED |
| M-09 powered context cached per sub-step | test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit | 3/4 | KILLED |
| M-10 mutable context | test_t01_a_context_is_immutable | 1/1 | KILLED |
| M-11 unowned mass (np.float64 kept) | test_t01_b_mass_is_an_owned_builtin_float | 5/5 | KILLED |
| M-12 validation removed | test_t01_c_invalid_mass_is_rejected_at_construction, test_t01_c_deferred_invalid_mass_is_rejected_when_read | 14/14 | KILLED |
| M-13 massless path gets 0.0 | test_t06_massless_path_carries_absent_mass | 1/1 | KILLED |
| M-14 powered context before the finiteness check | test_t07_k_finiteness_check_precedes_powered_context_construction | 2/3 | KILLED |
| M-15 force call before thrust_acceleration | test_t07_g_pointing_law_error_precedes_the_force_model | 1/1 | KILLED |
| M-16 coast validates at construction (option A) | test_t07_i_finite_dt_with_overflowing_tick_end_is_non_finite, test_t07_a_infinite_dt_coast_point_mass_is_non_finite, test_t07_b_infinite_dt_coast_point_mass_and_j2_fails_in_j2 | 4/4 | KILLED |
| M-17 coast repairs NaN (max argument order swapped) | test_t04_invalid_coast_stage_mass_is_carried_and_rejected_on_read | 1/1 | KILLED |
| M-18 coast passes absent mass | test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit | 3/4 | KILLED |
| M-19 powered context deferred (expected equivalent) | tests/test_s1_force_context.py, tests/test_s1_failure_paths.py | 0/90 | SURVIVED (expected equivalent) |
| M-20 premature subclass-sensitive coast read (v2) | test_t07_l_coast_closure_does_not_read_the_stage_through_a_subclass, test_t04_coast_mass_is_the_stored_propellant_of_a_subclass_stage | 4/4 | KILLED |
| M-21 lazy stage reference, dispatching read (v3-L) | test_t04_coast_context_is_an_owned_snapshot_of_the_stage_mass, test_t04_coast_context_does_not_keep_the_stage_alive | 4/4 | KILLED |
| M-21b lazy stage reference, base-class read | test_t04_coast_context_is_an_owned_snapshot_of_the_stage_mass, test_t04_coast_context_does_not_keep_the_stage_alive | 4/4 | KILLED |
| M-22 powered lazy stage reference (v3-L machinery, powered path only) | test_t04_powered_context_is_an_owned_snapshot_of_the_stage_mass, test_t04_powered_context_does_not_keep_the_stage_alive | 4/4 | KILLED |

**M-11: KILLED 5/5.** The implementer's I-52 chat report stated "1/1", which was a transcription
error. The committed `mutation_results.json` has always recorded 5 of 5 parametrized nodes failing,
all by `AssertionError`. The committed evidence is unchanged.

"Failed / run" counts the parametrized nodes collected under the designated tests. The table is
generated from `mutation/mutation_results.json`, which records for each mutant the exact edits,
per-node results, pytest exit status and failure messages.

- **24 mutants KILLED; 1 survivor, M-19.**
  - M-19 builds the powered context with `ForceContext.deferred(mass)`.
  - It is the documented **equivalent** mutant (v3-S §5.1): `thrust_acceleration` already rejects
    any non-finite or non-positive `mass` before the construction, and in S1 nothing reads the
    powered context's mass.
  - I-43 accepted it within the verified scope of the current production code. Codex reviews of
    Commit D re-confirmed it.
  - If a later stage adds a powered-mass consumer, or moves the construction before
    `thrust_acceleration`, the equivalence must be re-established.
- **M-22 (A-1):** all 4 designated nodes fail by assertion, by the mechanism A-1 §3 predicts:
  - write-after reads `DRY + 123`;
  - shared-buffer and row-view read `DRY`;
  - the lifetime node finds the stage still alive.
- **Writer corpus:** M-14 differs from BASE in 46 cases and M-19 in 0, as planned
  (`mutation/writer_corpus_mutants.txt`).
- **Pinned campaign:** the other 23 non-equivalent mutants are identical to the pinned I-44 campaign
  (`s1-v3/`) in verdict, counts and failing nodes. M-19's denominator grows from 86 to 90 only
  because of the A-1 nodes (`mutation/compare_with_pinned_s1v3.txt`).

### S1.9 Numerical compatibility, snapshot ownership and lifetime

**T-08 (`t08/`)**: direct-API corpora, per-tick hex of r, v and the propulsion state, plus events.
They were run under `PYTHONPATH` set to the BASE tree and to the C tree, on the same host.

| Corpus | Cases | C vs BASE | sha256 (both trees) |
|---|---|---|---|
| Main direct API | 26 880 | 0 differing | `e0309486277deb101d341f23d57964d2f0c2874ab865d5be80c07f6499f0a814` |
| Stage writers | 26 111 | 0 differing | `3310fd9031bc2c0cd611168e9ae3d1164ac00e87628fbe89d4c9b99401f60415` |
| Custom integrators | 6 216 rows: 27 supported kinds, 10 out-of-contract | **0 supported-kind differences**; 392 out-of-contract (`list` 196, object `None` 196) | BASE `d21c7c4a…04d7`, C `1c9a9e89…4eba` |

All hashes equal the pinned I-44/I-45 references (`s1-v3s-i45/corpus_hashes.txt`). The 5 validated
scenarios give byte-identical output trees (`missions/missions.sha256`).

**Scope of the compatibility claim:**
- It is a same-host comparison (macOS x86_64, CPython 3.12.15, the `uv.lock` at BASE).
- It covers the corpora and scenarios above only.
- It is not an accuracy claim and not a cross-platform claim.
- "Supported input" means the v3-S §3.2 contract: a 1-D float64 ndarray of 8 elements, in the
  documented layout, on a spacecraft derivative; or the 6-element M1 state without one.
- The 392 out-of-contract differences are exactly the v3-S §6 disclosures. They are not
  supported-input differences.

**Snapshot ownership and lifetime (U-1).** The following tests pass at C:
- T-04 (a): coast snapshot under write-after, shared-buffer and row-view integrators;
- T-04 (b): coast stage not kept alive;
- T-04 (c): stored value for masked and raising subclasses;
- A-1 T-04 (d): powered snapshot;
- A-1 T-04 (e): powered stage not kept alive.

The lazy-reference mutants M-21, M-21b and M-22 are killed (§S1.8).

### S1.10 Regression gates R-1…R-6 (item 9; I-40 §11)

**Formal R-1…R-4** were run under I-52 at D's exact tree `75d56dbcece04510c6d8d79857ffde33ee86dff4`
(scratch stage commit `e27b7c8`; the real D has the identical tree). They used fresh clones, with
BASE recomputed in separate fresh clones.

| Gate | D | BASE (recomputed) |
|---|---|---|
| **R-1** M1 Proof | PASS, 9/9 steps; golden `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` | PASS, 9/9; same golden |
| **R-2** M2 Proof | PASS, 20/20 steps; `m2_proof` 228 [PASS] / 0 [FAIL] | PASS, 20/20; 228 / 0 |
| **R-3** T1 | 109 passed; the r01/r02 correction checks are byte-identical to the committed results, and between D and BASE | 109 passed; identical |
| **R-4** T0 | 314 passed | 314 passed |
| **R-5** | T-10 51/51; T-11 compliant; BASE..D over the protected paths is empty | — |
| **R-6** | CI 4/4 `success` on push tips A (`40961801315`) and D (`41094508497`) | — |

**R-2 semantic comparison.** In `m2_final_states_record.json`, the `missions` block (per mission:
`status`, `final_tick`, `final_t`, `r`, `v`, `events_sha256`) is **identical** to BASE. So are
`schema`, `tree_clean`, `platform`, `environment`, `ci` and `inputs`. In `m2_proof_stdout.txt`, all
229 PASS/FAIL, digest, golden, snapshot, manifest and threshold lines are identical after temp-path
normalization.

**R-2 metadata-only differences**, recorded separately:
- `revision`, and the record's `sha256`. The latter is the digest of the whole record except
  itself, so it includes `revision` (`src/tars/validation/m2_cross_platform.py:151–152`).
  Substituting the BASE revision into the D record reproduces the BASE `sha256` exactly.
- In the proof logs: dates, temp paths, uv timings, and test and format counts.
  - pytest: BASE 1 290, D 1 380 = 1 290 + 90 S1 nodes;
  - `ruff format`: BASE 266 files, D 270 = 266 + the 2 S1 test files + `run_record.py` + the S1
    `README.md`. ruff 0.16 also checks Markdown.

**History.** A first formal run on a pre-correction D tree (`b08656f`) gave the same results. D was
then corrected for review finding D1-01 (§S1.12), and the formal gates were re-run on the final
tree. These results were not reused.

**R-6 for Commit E is pending.** E is not pushed (I-54, I-54B). I-40 §12 step 6 expects E to be pushed with
CI 4/4; that push needs separate authorization.

### S1.11 CI runs and per-platform status (item 10; I-40 §9)

**Tip D: run 41094508497** (https://github.com/guillermoMartin96/tars/actions/runs/41094508497), a
push run on `milestone-3-t2-s1-force-context`, head SHA
`1b25254e3c0a9787e1f01c428d3f0961ef5f0184`. Conclusion **`success`**.

| Job | CPython (from the log) | Conclusion | pytest |
|---|---|---|---|
| check (ubuntu-latest) | 3.12.3 | success | 1 377 passed, 3 skipped |
| check (macos-latest) | 3.12.10 | success | 1 377 passed, 3 skipped |
| check (macos-15-intel) | 3.12.10 | success | 1 377 passed, 3 skipped |
| m2-cross-platform | 3.12.3 | success | — |

- **Skips:** 1 377 + 3 = 1 380 on every check job. The 3 skips are the existing
  `tests/test_gmat_m2.py:326` skip, "GMAT R2026a not installed (CI never runs GMAT)", as at BASE and
  A.
- **Tip A: run 40961801315**, 4/4 `success`: 1 316 passed and 3 skipped per check job (BASE CI 1 287
  + 29 T-07). The T-07 file shows 29 passing nodes on each platform.

**CI metadata discrepancies at tip D** (none is a CI failure):
1. **Monitoring inconsistencies.** The first `gh run watch` exited with status 1 while the run was
   in progress. The run-level API then reported "completed / success" while `m2-cross-platform` was
   still queued. Neither was accepted: all 4 jobs were polled through the jobs API until each was
   `completed` / `success`.
2. **Stale step metadata on macos-15-intel.** The job concluded `success`, but the API still lists
   step 8 "Tests" as `in_progress` and steps 9–16 as `pending`. `gh run view --log` also omitted
   that step's output.
3. **Raw-log verification.** The raw job log, fetched through the jobs logs API
   (`gh api --allow-escape-sequences repos/…/actions/jobs/124196655496/logs`), contains:
   - the Tests step output, "1377 passed, 3 skipped, 3 warnings in 3258.65s", with both S1 files
     fully green;
   - the output of every later step: determinism, M1 cross-platform, GMAT comparison, M1 and M2
     Proof.

   Evidence is in the I-53 external evidence (`ci_job_macos-15-intel_raw.log`, `ci_job_steps.txt`,
   `ci_discrepancies.txt`).

**Extended-precision coverage limitation (T-01 (e)):**
- On macOS arm64 (`macos-latest`), `np.longdouble` is binary64. The T-01 (e) parameter
  `np.longdouble(1e300) * 1e300` (`tests/test_s1_force_context.py:99`) overflows to infinity when it
  is evaluated at collection. That causes the one additional `RuntimeWarning` on that job (2
  warnings against 1 at A).
- On arm64 that node therefore exercises `inf`, which is rejected with `ValueError`, and **not** the
  intended huge finite extended-precision value. On x86_64 (`ubuntu-latest`, `macos-15-intel`, and
  the local host) it exercises the finite 80-bit value.
- The test passes on every platform, **but cross-platform test coverage is not identical.**
- The pinned test is not modified. Any change needs separate authorization.

**Run records** (I-40 §9): one per gate run is in `docs/science/experiments/m3-t2/s1/run_records/`,
produced by `run_record.py`. The CI CPython lines are those in the table above.

### S1.12 Evidence, manifests and independent reviews (item 11)

**In the repository:**
- `docs/science/experiments/m3-t2/s1/SHA256SUMS`: 96 entries covering every other file in the
  directory. It verifies from git objects at D.
- `SCRUBBED.txt` lists the 6 files whose local paths were replaced, with their original sha256
  values.

**External evidence** (implementer's host; not in the repository). Each directory has a
`MANIFEST.sha256`, all verified 2026-10-30:

| Instruction | Location | MANIFEST.sha256 sha256 |
|---|---|---|
| I-48 | `~/projects/tars-evidence/I-48/` | `4a34928606efa31521295c37feb5f036a6243f5ab91cbd6ef2992ad39f4005f4` |
| I-49 | `~/tars-evidence/I-49/` | `a4db927910089a66fdd01792c56e7ed5c1747cbd342bc533efa7029fe21c1c68` |
| I-50 | `~/tars-evidence/I-50/` | `13a6be0f47ce6cd0e8cdea272087100f44bd19da62aa6d46c05ce525e81e58a0` |
| I-51 | `~/tars-evidence/I-51/` | `15b4b5544eef3d127e49a8eb22e8a89018212a3f60eb032e1d4bd0a23c73ede0` |
| I-52 | `~/tars-evidence/I-52/` | `6abe18be2b1222859ac60d5639766d79bf4277ba5b09d9dfa8ea1ea39821e739` (includes the verified B..D bundle `commitD/commitBCD.bundle`) |
| I-53 | `~/tars-evidence/I-53/` | `e1aba2f364722ddc401beeb89de3e3eab38f3d12f2bbf5beef6808165cb4cc9b` |
| I-54 | `~/tars-evidence/I-54/` | `2a1419c836f4cc982181dd6cb3971de3f88c3d11579d27488326322a6f750e61` (T-09 escalation and draft report) |
| I-54A | `~/tars-evidence/I-54A/` | `daae437158adb0761082f8393aeba5d63598c13041b205a494d79f9517e6ae33` (T-09 verification) |
| I-54B | `~/tars-evidence/I-54B/` | — (this commit's preconditions and verification; that manifest is written after this report is fixed, so it cannot be quoted here) |

The verbatim owner texts of I-51 (sha256 `fd610dc9…f551`), I-52 (`6cf0e045…17d9`), I-53, I-54,
I-54A and I-54B are in those directories only.

**Independent reviews already completed.** These are Codex reviews: a separate provider, a fresh
session, no network. **None of them is the S1 independent review of I-40 §14.**

| Review | Subject | Verdict | Findings and disposition |
|---|---|---|---|
| Proposal 01 | proposal v1 | REQUEST_CHANGES (stands) | R-01 MAJOR, recorded CLOSED in 02 |
| Proposal 02 | proposal v2 | REQUEST_CHANGES (stands) | R-02 MAJOR, remedied by v3-S; R-03 corrected |
| Proposal 03 | v3-S and prototype | PASS | R-04 corrected; N-01 answered by A-1; D-1 not changed |
| Plan 01 (I-46) | A-1 | PASS | 2 NOTE |
| P-5 correction 01 / 02 (I-48) | I-48 record and verifier | REQUEST_CHANGES, then PASS | R01–R04 corrected and closed |
| Commit B 01 (I-50) | red-phase tests | PASS | B1-01 NOTE |
| Commit C 01 (I-51) | production code | PASS | C1-01 NOTE |
| Commit D 01 (I-52) | D evidence and the local A–D sequence | PASS | D1-01 MINOR **ACCEPTED**, corrected in D before it was committed (the README stated wrongly that I-51/I-52 were on the planning branch); D1-02 NOTE (multi-platform CI then outstanding, since satisfied by run 41094508497) |

Records of reviews up to I-48 are in `docs/reviews/` on the planning branch. The Commit B, C and D
review records are in the external evidence only.

### S1.13 Protected paths (item 12)

`git diff BASE..D` touches no protected path:
- `.python-version`, `pyproject.toml`, `uv.lock`, `.github/`, `proof/`, `toolbox/`, `scenarios/`;
- `docs/` outside the two allowlisted locations;
- any other `src/` file.

T-10 is 51/51 AST-identical for every protected class and function (I-40 §6). `git diff D..E`
touches no `src/` or `tests/` path (I-40 §12 step 6).

### S1.14 Deviations, unexpected behaviour and open questions (item 13)

**Process deviations, each ruled on by the owner:**
- **I-47 stop at P-5.** I-40 P-5's "43 manifests" counted 5 reviewer-side lists that cannot verify
  by design. I-48 corrected the procedure (P-5A–D) and accepted the existing worktree (the P-3
  ruling).
- **I-49 sequencing conflict.** I-49 asked for B to be pushed alone, which I-40 §12 forbids. I-50
  approved option 1: B local, then pushed with C and D.

**Implementer-side defects, disclosed and preserved:**
- I-48 precondition runs 1 and 2 failed on harness bugs: a missing output directory, the selftest's
  `.py` naming, `gh` resolving the wrong repository, and `set -u` swallowing a line. Run 3 is the
  valid run.
- A full-suite run left ignored `src/**/__pycache__` (I-50). It was removed, and later runs set
  `PYTHONDONTWRITEBYTECODE=1`.
- **The T-09 gap.** T-09 (I-40 §9a) was not run as specified during Commits C and D. None of the B,
  C or D reports claimed it, and none of the reviews of those commits noticed it was missing.
  - The implementer found it while preparing this report (I-54) and stopped.
  - I-54A authorized a read-only verification; it passed, on one host (§S1.7).
  - I-54B accepted it. No code, test or Commit D evidence was changed.
- **The M-11 transcription error.** The implementer's I-52 chat report stated M-11 as "1/1". The
  committed record says **KILLED 5/5**, and §S1.8 uses the committed record.

**Observations:**
- **CI metadata** (§S1.11) and **T-01 (e) on arm64** (§S1.11).
- **External evidence location.** The I-48 directory sits inside an unrelated git checkout
  (`~/projects` is a separate repository). From I-49 on, evidence uses `~/tars-evidence/`, which is
  outside any checkout. Nothing was committed to the unrelated repository.
- **Planning-branch hazard (I-48).** At the planning tip, a file named `SHA256SUMS` is not always a
  manifest of committed artefacts. 3 such files fail a direct check, each for a recorded reason.
  P-5's scope is BASE.

**Open questions for the owner:**
- OD-7 must be resolved before the S1 independent review can be authorized (I-40 §2). OD-8 … OD-12
  stay deferred, each to its stated slice.
- I-51 … I-54B are to be recorded in a repository record if the owner wishes.
- Whether to amend T-01 (e) for arm64 coverage.
- Whether T-09 should become a committed regression gate that CI runs on every platform. Today it
  is external and was run on one host (§S1.7).
- The integrators docstring (I-46 D5, deferred).

### S1.15 Status (item 14)

`S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED`

- A–D are implemented, verified and pushed, with tip CI 4/4.
- T-09 was verified externally under I-54A, on one host, and accepted by I-54B.
- E (this report) is created and verified locally. It is **not pushed**, pending a separate
  authorization to push it.
- The **independent S1 review** (I-40 §14) is **NOT AUTHORIZED**; OD-7 is still open.
- **S1 acceptance: NOT GRANTED. Merge: NOT AUTHORIZED.** PC-7(T2 overall): NONE.
