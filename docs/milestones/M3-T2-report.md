# M3 T2 — Report

**Status: S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED.** S2–S6 are not started.
**PC-7(T2 overall): NONE.**

> **Superseding note (I-60, 2026-11-01).** The status line above and §S1.1–§S1.15 are the
> historical record of Commit E and are kept unchanged. The current status is in §S1.16:
> - the independent review I-58 returned REQUEST_CHANGES;
> - corrections F–H were made under I-59 and pushed under I-60;
> - under I-40 §10, E had 19 qualifying kills and 5 non-qualifying kills, and H has 24 qualifying
>   kills and 0 non-qualifying kills.
>
> **S1 is NOT ACCEPTED and NOT MERGED.**

> **Superseding note (I-62, 2026-11-02).** I-61 returned REQUEST_CHANGES on finding S1C-03. The
> stage-writer count of 26 111 in §S1.9 is superseded: the corpus has 26 112 cases, and all of them are
> byte-identical between BASE and J. The current status is in §S1.17.

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

> **Superseded in part (I-58, I-59, I-60; see §S1.16).** "24 mutants KILLED" above counted the
> per-mutant reason patterns of D. Five of those patterns (M-05, M-14, M-15, M-16, M-20) accepted a
> propagated, unasserted exception.
> - **At E, under I-40 §10:** 19 qualifying kills and 5 non-qualifying kills, plus the M-19
>   equivalent. E does not meet the criterion.
> - **At H:** 24 qualifying kills, 0 non-qualifying kills, M-19 equivalent, and a denominator of 25.
>
> The table above and the D evidence are kept unchanged as the historical record.

### S1.9 Numerical compatibility, snapshot ownership and lifetime

**T-08 (`t08/`)**: direct-API corpora, per-tick hex of r, v and the propulsion state, plus events.
They were run under `PYTHONPATH` set to the BASE tree and to the C tree, on the same host.

| Corpus | Cases | C vs BASE | sha256 (both trees) |
|---|---|---|---|
| Main direct API | 26 880 | 0 differing | `e0309486277deb101d341f23d57964d2f0c2874ab865d5be80c07f6499f0a814` |
| Stage writers | 26 111 | 0 differing | `3310fd9031bc2c0cd611168e9ae3d1164ac00e87628fbe89d4c9b99401f60415` |
| Custom integrators | 6 216 rows: 27 supported kinds, 10 out-of-contract | **0 supported-kind differences**; 392 out-of-contract (`list` 196, object `None` 196) | BASE `d21c7c4a…04d7`, C `1c9a9e89…4eba` |

> **Superseding note (I-62).** The stage-writer row's "26 111" is superseded. The corpus has
> **26 112** cases and no header line, and the comparison's `[1:]` slice skipped its first case (S1C-03).
> §S1.17 has the complete 26 112-case comparison.

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

> **Later CI (see §S1.16).** Tip E: run 41156488074, 4/4 (I-55). CI on the corrected tip H and on the
> documentation tip is recorded in §S1.16.

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

> **Superseded (I-55 … I-60; see §S1.16).** E was pushed under I-55, OD-7 was closed under I-57,
> the I-58 independent review returned REQUEST_CHANGES, and F–H were pushed under I-60. **S1 acceptance:
> NOT GRANTED. Merge: NOT AUTHORIZED.**

### S1.16 I-58 review and I-59 correction: superseding record (added under I-60, 2026-11-01)

This section is **appended**. It supersedes the statements that §S1.1–§S1.15 make about the mutation
kill count and the S1 tip. Those sections are kept unchanged as the historical record of E. Notes
inserted in §S1.8, §S1.11 and §S1.15 point here. No text of E was removed.

**Authority** (verbatim texts are kept externally in `~/tars-evidence/<ID>/`; none is recorded on the
planning branch):
- I-55: E pushed;
- I-56 and I-57: OD-7 recorded and closed;
- I-58: independent S1 review;
- I-59: corrections authorized;
- I-60: F–H approved, pushed and CI-checked, plus this record.

**History since E:**
- **E pushed (I-55).** E `0e70f540…` was pushed, and CI run 41156488074 was 4/4 `success`. §S1.10's
  "R-6 for Commit E is pending" and §S1.15's "E … is **not pushed**" are therefore historical.
- **OD-7 closed (I-56, I-57).** It was closed by `docs/milestones/M3-T2-S1-OD7-I30-section4-record.md` on the planning
  branch (`5714959`, CI run 41244497808 4/4).
- **Independent S1 review (I-58).** A Codex review of E (separate provider, fresh session, no network)
  returned **REQUEST_CHANGES**:

| Finding | Severity | Disposition |
|---|---|---|
| S1R-01: an `int`/`float` subclass whose `__float__` raises `ZeroDivisionError` escapes `ForceContext(...)` and `ForceContext.deferred(...)`, against T-01 (e) | MAJOR | ACCEPTED; corrected in F and G |
| S1R-02: M-05, M-14, M-15, M-16 and M-20 were counted KILLED on propagated, unasserted exceptions, against I-40 §10 ("a kill by an unrelated exception does not count") | MAJOR | ACCEPTED; I-40 §10 governs; corrected in H |
| S1R-03: T-01 (e) longdouble parameter is `inf` on arm64 (§S1.11) | NOTE | accepted, no change |
| S1R-04: T-09 is an external single-host verification (§S1.7) | NOTE | accepted, no change |

**Corrective commits** (I-59; approved and pushed under I-60):

| Commit | SHA | Change |
|---|---|---|
| F | `c52c0904b19d9abd701864a329350c15ce0b8b64` | `tests/test_s1_force_context.py`: 10 S1R-01 regression nodes, red at E's code |
| G | `45053ef6c2a11f8bd8272928060df8845f65f1b1` | `src/tars/sim/forces.py`, `ForceContext._store`: an `OverflowError` or `ZeroDivisionError` raised while converting the mass becomes `ValueError("total_mass_kg is not representable as a binary64 number")` `from None`, on both construction paths. Other exceptions propagate unchanged; the `TypeError` type check still runs first. |
| H | `2a35ebf397b474533300ee5a0169f8d5d025e86a` | both S1 test files: the designated nodes of M-05, M-14, M-15, M-16 and M-20 assert the expected exception's type, message and identity. Node IDs are unchanged. |

E..H changes 3 allowlisted files (+159 −18). `_owned_float`, the simulator and the derivative
arithmetic are unchanged (T-10 51/51). The supported-input behaviour of `ForceContext` is unchanged:
2 105 inputs, E vs H, 0 differing.

**S1R-01 regression coverage (F):**
- int and float subclasses whose conversion raises `ZeroDivisionError` or `OverflowError`, on direct
  and deferred construction (`ValueError`, message, suppressed context);
- a 0-d `ndarray` subclass whose element read raises;
- other conversion errors propagate as the identical object;
- the type check runs before conversion;
- a subclass that converts is validated as before.

Red first, at F against E's code: 3 failed, 97 passed. Each failure is
`AssertionError: expected ValueError …, got ZeroDivisionError: sentinel`. Green at G and H: 100/100.

**Mutation campaign: historical E versus corrected H.**
- The 25 mutants, their edits and designated nodes, and the denominator of 25 are unchanged.
- The kill criterion is I-40 §10 applied strictly: every failing designated node must be an assertion
  failure, either a plain assertion or an assertion that validates an expected exception, and must
  match the mutant's declared reason.

| | E (historical, as committed in D and reported in §S1.8) | H (corrected) |
|---|---|---|
| Qualifying kills (I-40 §10) | **19** | **24** |
| Non-qualifying kills (unasserted exception) | **5**: M-05, M-14, M-15, M-16, M-20 | **0** |
| Documented equivalent survivor | M-19 (v3-S §5.1) | M-19, unchanged (0/100) |
| Denominator | 25 | 25 |

- §S1.8's "24 mutants KILLED" counted the five non-qualifying kills, because the D reason patterns
  accepted a propagated exception. **E does not meet the I-40 §10 criterion.** The same corrected
  harness run at E gives 19 / 5. Strict re-classification of the committed D results gives the same
  split.
- At H, every failing designated node of all 24 non-equivalent mutants is an assertion failure that
  matches its declared reason. Failing nodes are identical to E's.
- M-19's node total grows from 90 to 100 only because its designated nodes are the two whole S1 files.

**Regression gates at H** (fresh clones, macOS x86_64 host):
- T-07 29/29;
- T-08 0 differing, with all 6 corpus hashes equal to D's;
- T-09 scan, comparison and negative control (7/7) pass;
- T-10 51/51;
- T-11 within the allowlist;
- 10 validated-scenario files byte-identical to BASE;
- R-1 golden `7a4e1877…20a4`;
- R-2 228/228, mission records identical;
- R-3 109 passed, outputs byte-identical;
- R-4 314 passed;
- full suite 1 390 passed;
- `ruff check` and `ruff format --check` exit 0.

**Platform CI on H.** Run **41363138188** of workflow `ci`
(https://github.com/guillermoMartin96/tars/actions/runs/41363138188) was a push run on
`milestone-3-t2-s1-force-context` with head SHA `2a35ebf397b474533300ee5a0169f8d5d025e86a`.
Conclusion: **`success`, 4/4.**

| Job | Runner image / arch | CPython (from the log) | Conclusion | pytest | T-07 file | `test_s1_force_context.py` |
|---|---|---|---|---|---|---|
| check (ubuntu-latest) | ubuntu-24.04 / x86_64 | 3.12.3 | success | 1 387 passed, 3 skipped | 29/29 | 71/71 |
| check (macos-latest) | macos-26-arm64 / arm64 | 3.12.10 | success | 1 387 passed, 3 skipped | 29/29 | 71/71 |
| check (macos-15-intel) | macos-15 / x86_64 | 3.12.10 | success | 1 387 passed, 3 skipped | 29/29 | 71/71 |
| m2-cross-platform | ubuntu-24.04 | 3.12.3 | success | — | — | — |

- **Totals:** 1 387 + 3 = 1 390 on every check job, equal to the local full suite at H. The 3 skips are
  the existing `tests/test_gmat_m2.py:326` GMAT skip.
- **I-40 §8:** the modified T-07 file passes all 29 nodes on all three required platforms, with no
  failure, error or skip.
- **Job metadata:** every step of every job concluded `success`. Per-file counts were parsed from the
  raw job logs, fetched through the jobs logs API.
- **Platform-specific:** on macos-latest (arm64), the T-01 (e) longdouble `RuntimeWarning` appears as at
  D and E (S1R-03).
- **Records:** `docs/science/experiments/m3-t2/s1/i59/ci_H/` holds the run and job metadata and the
  summary. The raw logs are kept externally in `~/tars-evidence/I-60/ci_H/`.
- **CI on this documentation commit** is recorded in the I-60 external evidence. A commit cannot quote
  its own CI run.

**Evidence.**
- **In the repository:** `docs/science/experiments/m3-t2/s1/i59/`, a new subdirectory with its own
  `README.md`, `SHA256SUMS` and `SCRUBBED.txt`.
- **D evidence unchanged.** The Commit D files in `docs/science/experiments/m3-t2/s1/`, including
  `SHA256SUMS`, `README.md` and `mutation/`, are byte-identical to D and remain the historical record.
  Their mutation verdicts are superseded only as stated above.
- **External evidence:**

| Instruction | Location | MANIFEST.sha256 sha256 |
|---|---|---|
| I-58 | `~/tars-evidence/I-58/` | `de02632c8d86b25660c86421d8eb3fe85346d48138e01b02e5bdcd96776d17c2` (unchanged; 1 056 entries) |
| I-59 | `~/tars-evidence/I-59/` | `da4a6032e6815db9c4658c0a0922fdb63bf94796fe1b472fd1efc57ba64cd567` (3 770 entries) |
| I-60 | `~/tars-evidence/I-60/` | — (written after this commit, so it cannot be quoted here) |

**Remaining limitations:**
- **S1R-03.** On macOS arm64 the T-01 (e) longdouble parameter exercises `inf`, not a finite
  extended-precision value. Coverage differs by platform; the test passes everywhere.
- **S1R-04.** T-09 is an external verification on one host (macOS x86_64). It is not a committed CI
  gate.
- **Local gates on one host only.** All local gates above, including T-08, T-09 and R-1…R-4, ran
  on one macOS x86_64 host. CI covers only its own jobs. No new cross-platform claim is made.
- **No dedicated mutant for G.** The fix itself has no mutant; the denominator of 25 was preserved.
  Reverting G gives the state F's red record shows failing.
- **No independent review of F–H yet.** The corrections have not been independently reviewed.

**Status after I-60:** `S1 IMPLEMENTED / REVIEWED (I-58: REQUEST_CHANGES) / CORRECTED (F–H) / NOT RE-REVIEWED / NOT ACCEPTED / NOT MERGED`.
- **S1 acceptance:** NOT GRANTED.
- **Merge:** NOT AUTHORIZED.
- **S2:** NOT AUTHORIZED.
- **Next independent review:** NOT STARTED.

### S1.17 I-61 review and I-62 S1C-03 correction: superseding record (added under I-62, 2026-11-02)

This section is **appended**. It supersedes every statement that the stage-writer (T-08) corpus has
26 111 cases. Notes inserted at the top of this report and after the §S1.9 table point here.
§S1.1–§S1.16 are otherwise unchanged; no text was removed.

**Authority** (verbatim texts are kept externally in `~/tars-evidence/<ID>/`; none is recorded on the
planning branch):
- I-61: independent closure review of J `f47cf0d0…`;
- I-62: S1C-03 accepted as MINOR / must-fix, and this evidence and report correction authorized. I-62
  authorizes no production, test, algorithm or assumption change.

**I-61 review.** OpenAI Codex (codex-cli 0.162.0) ran in a fresh session (thread
`01a19d41-45ac-77d0-9dba-ecf0af3020bb`) against a fresh clone detached at J.

**Verdict: REQUEST_CHANGES.**

| Finding | Severity | Reviewer assessment; owner disposition |
|---|---|---|
| S1R-01 (I-58) | — | Reviewer: resolved, independently reproduced at E and fixed at H/J |
| S1R-02 (I-58) | — | Reviewer: resolved; E 19 qualifying / 5 non-qualifying / 1 equivalent and J 24 / 0 / 1 reproduced |
| S1C-01 (S1R-03) | NOTE | Reviewer: nonblocking, disclosed limitation (the arm64 longdouble parameter is `inf`). I-62 makes no separate ruling |
| S1C-02 (S1R-04) | NOTE | Reviewer: nonblocking, disclosed limitation (T-09 B/C are external, single-host probes). I-62 makes no separate ruling |
| **S1C-03** | **MINOR, must-fix** | **Owner: accepted as MINOR / must-fix (I-62).** The writer corpus has 26 112 cases, not 26 111 |

The I-61 evidence is in `~/tars-evidence/I-61/`, with `MANIFEST.sha256` sha256
`641254128a7962f2160729cb3c373d5f988f4959650c7f2cfa6287af9248dc16` (2 710 entries).

**The S1C-03 defect.** The D and I-59 drivers loaded every corpus with
`[json.loads(l) for l in open(f)][1:]`, which assumes a header line:
- the main corpus starts with a header record, so the slice was correct there;
- the stage-writer corpus has no header, so the slice dropped its first real case,
  `10.0|w0_6_nan|none|leo|none`;
- the integrator corpus has a real header and its own comparator, so it is not affected.

The miscount began in I-42 and was carried through I-44, I-45, D, I-59 and §S1.9. Codex review 03
(I-45) counted 26 112 JSONL lines and took the extra line for a header.

**Historical claims and corrected results:**

| Statement | Historical | Corrected (I-62) |
|---|---|---|
| Writer corpus size | 26 111 cases (§S1.9, D, I-59, planning) | **26 112 cases, no header line**; also derived independently from the harness axes, 4 × 192 × 2 × (2 + 3 × 5) |
| Writer cases compared per case | 26 111 (index 0 never compared) | **26 112**, index 0 … 26 111 |
| Writer result | 0 differing of 26 111 | **0 differing of 26 112**, byte for byte (I-40 T-08 / INV-2), fresh BASE vs J and retained I-59 BASE vs H |
| Main corpus | 26 880 cases, 0 differing | Unchanged and re-verified: 26 880 cases, 0 differing, header identical |
| Corpus sha256 | main `e0309486…a814`, writers `3310fd90…0415` | Unchanged; all 8 regenerated or retained files equal the pinned hashes |

**Pinned proposal v3.** `M3-T2-S1-proposal-v3.md` line 175, on the planning branch at `5714959`, reads
"stage-writer corpus (26 111 cases; 26 112 JSONL lines with the header)". **That count is incorrect.**
The 26 112 JSONL lines are 26 112 cases, and the writer corpus has no header. The byte-for-byte
BASE equality the proposal records holds for all 26 112 cases. The proposal is pinned and **is not
modified**. The same applies to:
- `M3-T2-S1-decision-I45.md:62`;
- `M3-T2-S1-proposal-review-03.md:57`;
- the `s1-proposal/`, `s1-v3/` and `s1-v3s-i45/` summaries listed in `s1/s1c03/README.md`.

**Corrected comparison** (`docs/science/experiments/m3-t2/s1/s1c03/`).
- **Comparator.** The format of each corpus is declared: `main` has exactly one header record, `writers`
  has none. There is no unconditional slice.
- **Format checks.** Every line is valid JSON with the declared header layout; the case count is as
  expected; case identities are unique; BASE and J have the same identity sequence, in the same order.
- **Comparison.** Every case line is compared byte for byte, with a parsed-record comparison as a
  secondary check. Every case is listed with its index, file line and identity.
- **Results:** all 26 112 writer cases and all 26 880 main cases are identical, for both fresh BASE vs J
  and retained I-59 BASE vs H. The previously omitted case is compared and is identical. No previously
  untested case differs.
- **Negative controls:** 13/13 behave as expected. A one-digit change to the first writer case is
  **not detected** by the historical expression and **is detected** by the corrected comparator, at case
  index 0. Changes to a middle case and to the last case are detected by both. Deletion, duplication,
  reordering, header insertion and header removal are each detected by the corrected comparator as
  format failures.

**Scope.** This commit adds `docs/science/experiments/m3-t2/s1/s1c03/` and inserts lines into this
report. `src/`, `tests/`, the D evidence, the `i59/` evidence and the planning branch are unchanged.
The corpora (30–36 MB each) and the run logs are kept externally in `~/tars-evidence/I-62/`. That
manifest is written after this commit, so it cannot be quoted here.

**Limitations (unchanged):**
- S1C-01 / S1R-03 and S1C-02 / S1R-04 remain as stated in §S1.16.
- T-08 remains a same-host comparison (macOS x86_64). It is not an accuracy claim or a cross-platform
  claim.
- The scientific boundaries recorded in §S1.14–§S1.16 are unchanged. No tolerance, accuracy gate or
  assumption is added or promoted.

**Status after I-62:** `S1 IMPLEMENTED / REVIEWED (I-58: REQUEST_CHANGES) / CORRECTED (F–H) / RE-REVIEWED (I-61: REQUEST_CHANGES, S1C-03) / S1C-03 CORRECTION PREPARED (I-62; local, not pushed, not re-reviewed) / NOT ACCEPTED / NOT MERGED`.
- **S1 acceptance:** NOT GRANTED.
- **Merge:** NOT AUTHORIZED.
- **S2:** NOT AUTHORIZED.
- **Push of this correction:** NOT AUTHORIZED at the time of writing.
- **Further independent review:** NOT STARTED.

## S2 — Geodetic height and latitude behind a domain guard (PC-7(S2))

**Status (commit E): S2 IMPLEMENTED / VALIDATED LOCALLY AND ON CI / NOT REVIEWED / NOT ACCEPTED / NOT
MERGED.** The §5.2 independent implementation review has not been launched. Every S2 and S2-C
obligation (OB-01 to OB-29, OB-32, OB-33) is PENDING. OB-30 and OB-31 are carried forward (L).
Nothing in this section is an accuracy claim. A geodetic acceptance means only that DQ-1's stop
test was met within its limit and the outputs are finite (OD-12 item 3).

This section is appended. Every earlier line of this report is byte-identical to K.

### S2.0 Governing documents and owner determinations

| Record | Where | sha256 |
|---|---|---|
| S2 proposal v11, approved by I-97 (A/B/C; OD-12 resolved) | external, `~/tars-evidence/I-93/S2-proposal-v11.md` | `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809` |
| I-97 decision record | external, `~/tars-evidence/I-97/DECISION-RECORD.md` | `71e2fc58f2eba721558175125d75cf792b8b521524f2df95e7a6d3219d7e32ed` |
| PC-7(S2), issued by I-99 (2026-11-05) | external, `~/tars-evidence/I-99/PC-7-S2-ISSUED.md` | `940a3244ad532b86c0893f1bdfedafea19727ee0a607f7993c9f7214c80ebe6d` |
| I-101: "the generation environment" | external, `~/tars-evidence/I-101/I-101.md` | `3bfe20a92c8dd3bab96e8c6d79eefde6c333970cbfa93f1a237502d39398d2d2` |
| I-102: MN-17 test correction; supplemental commit BC2 | external, `~/tars-evidence/I-102/I-102.md` | `790e5492ead6a3c370e9cea96747a14112fe8794a9ccdd3b4c1eb0fd6b0114ab` |
| I-103: external amendment to v11 §3.12, MI-03's designated killer | external, `~/tars-evidence/I-103/I-103.md` | `9358b879ca835d937d5501c3047462e57464f536c3aacb6c97d684b809de9855` |

- These records are not on this branch. Recording them on the planning branch needs its own
  authorization (D-S2-8 (a), D-S2-9 (a)).
- v11 is unchanged. I-101, I-102 and I-103 are external owner records.
- Their texts and effect are reproduced in `docs/science/experiments/m3-t2/s2/README.md` and
  `evolute-guard-derivation.md` §1 and §5.

**I-101, quoted in substance.** For v11 §3.10 and the G-17a/G-17b replay rules, "the generation
environment" means equality of these fields:
- `sys.version`;
- `platform.platform()`;
- `platform.machine()`;
- the `uv.lock` sha256;
- the sha256 of the interpreter executable, with its real path resolved before hashing.

Path equality is not compared. The commit SHA and the CI-only fields are excluded from the equality
but stay mandatory under §3.16. Equal fields select the replay case only. They do not prove library or
build identity (r83:83). The author chose these fields before I-101 approved them; it was not prior
authorization.

### S2.1 Branch, base, commits and CI

The branch is `milestone-3-t2-s2-geodetic`, from K `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f` (`main`).
The history is linear. Every commit was pushed alone and is a push tip with its own CI run, and
every job executed in attempt 1.

| Commit | SHA | Content | CI run |
|---|---|---|---|
| A | `6c05e53c5ffcb892dacaa6f84e12a163830a4119` | DL-4 twin, generator, frozen listing, G-17a/G-17b, G-10, G-12a, ENV and X-P3 record tests, `commit-a/` record | 42265640238, 4/4 success |
| BC | `2b975d626e92c76a18efc873e0991084db30617a` | `src/tars/sim/geodesy.py`; `WGS84_INVERSE_FLATTENING` added to `constants.py`; S2 gate tests (byte-identical to the red record) | 42301740647, 4/4 success |
| BC2 | `5bd8340255d673965a2525f19e9fb32210de54b7` | I-102 correction of one G-06 test (`tests/test_s2_geodetic.py` only) | 42394082295, 4/4 success |
| D | `37251004406c9d9959123ed862d1ab6b13d7dccc` | evidence: `docs/science/experiments/m3-t2/s2/` (outside `commit-a/`) | 42398881403, 4/4 success |
| E | this commit | this section only | recorded outside this commit |

No commit was amended, rebased, squashed or force-pushed. No CI job was rerun, and nothing was
merged.

Per-job provenance is in `docs/science/experiments/m3-t2/s2/ci/*/run.json` and
`jobs-attempt1.json`. That covers each job's log URL, the attempt, the head SHA, and that the job was
executed rather than carried over.

### S2.2 Changed paths (K..D) and protected paths

- **Added:**
  - `src/tars/sim/geodesy.py`;
  - `tests/s2_dl4_geodetic_twin.py`, `tests/s2_dl4_point_sets.py`, `tests/s2_dl4_points.txt`;
  - `tests/test_s2_dl4_points.py`, `tests/test_s2_environment_record.py`;
  - `tests/test_s2_geodetic.py`, `tests/test_s2_geodetic_conformance.py`, `tests/test_s2_xp3_listing.py`;
  - `docs/science/experiments/m3-t2/s2/**`.
- **Modified (additive, AST-checked by G-13):**
  - `src/tars/sim/constants.py`: one constant with its comment;
  - `tests/test_constants.py`: one test function.
- **E** adds only this appended section.
- **G-13 scope check: PASS for K..BC, K..BC2 and K..D.** `forces.py`, `simulator.py` and
  `docs/science/assumptions.md` are byte-identical to K (D-S2-13 (a): no `assumptions.md` entry).
- No dependency, CI, `.python-version` or protected-path change was made.

### S2.3 Implemented behaviour

`tars.sim.geodesy.geodetic(r) -> (h, phi)`:
- **Evaluation:** DQ-1 (α), the operation sequence of packet r1 §5 lines 89-94, operation for
  operation, with f and e2 derived from `WGS84_INVERSE_FLATTENING` and never stored.
- **Checks, in this order (§3.8):**
  - structure and type-exact normalization (`bool` and other types raise `TypeError`;
    float and int subclasses are read from their base slot);
  - `not_binary64`;
  - `non_finite`;
  - `origin`;
  - `evolute_region`: the exact closed rational predicate on the model ellipsoid, behind the proven
    2^16 pre-filter;
  - evaluation in a `try` that covers exactly E.1 and catches only `ArithmeticError`/`ValueError`
    (`numerical_failure`);
  - post-checks `numerical_failure` → `overflow` → `non_convergence` (60 updates, stop test
    `|dphi| <= 1e-15`).
- **Errors:** every rejection is a `GeodeticDomainError(ValueError)` with a fixed `reason`,
  `category` and message.
- **No caller:** nothing in `forces.py`, `simulator.py` or elsewhere calls `geodetic` (S4 scope).

### S2.4 Red and green evidence

- **Original red run** (uncommitted on A; `geodesy.py` absent; `constants.py` = K):
  - 131 nodes: 101 fail with a per-test `ImportError`, and 4 fail by assertion.
  - 26 pass: guards (G-10, G-12a, G-13, twin sanity) and unchanged existing tests.
  - 0 collection errors, and no node fails for an undeclared reason.
  - The test files came from drafts recreated on 2026-11-06 (new working material, recorded as such).
  - All three test blobs at BC equal the red record (stop 14 not reached).
- **Supplemental red run (I-102)** on a fresh clone of A, with the frozen corrected
  `tests/test_s2_geodetic.py` (blob `0d817de456cf837c06979a5fab601db6be7b6567`, sha256
  `9059ff375993cf156e28fb76b5a3eb95a3601ea99c3572890cc1c1033fa8b661`):
  - 112 nodes: 100 `ImportError`, 2 assertion, and 10 component-free guards pass
    (G-10 W1–W7, G-13 ×3).
  - Identical per node to the original red run of that file.
  - BC2's blob equals the supplemental record.
- **Green** (host, macOS x86_64, CPython 3.12.15):
  - **BC:** pre-commit worktree and a fresh clone both give 1 518 passed, ruff check and format exit 0.
  - **BC2 tree:** 1 518 passed, ruff exit 0.
  - **CI:** 1 515 passed, 3 skipped on each `check` job, at A, BC, BC2 and D.

### S2.5 Mutation campaign (v11 §3.12, amended by I-103 for MI-03 only)

- **Rule.** Each mutant is applied to a scratch copy. A kill counts only if a designated node fails
  and every failure is assertion-type. The unmutated control must pass, and JUnit is recorded.
- **I-101 campaign at BC: INCOMPLETE (stop 8).**
  - Control 73/73.
  - 43 KILLED; 5 documented equivalents.
  - MN-17 ("the component value used as given, instead of the base-slot value") failed its G-06
    override node only by an uncaught `GeodeticDomainError`, which is not a kill.
  - The campaign's MN-17 node list had also omitted the designated `__abs__` case.
  - Stop record: `mutation/i101-bc-incomplete/STOP-RECORD.md`.
- **I-102 correction.**
  - The override test now captures that `GeodeticDomainError` as an observed wrong outcome and
    rejects it by an explicit assertion. The stored-value result and the no-override assertion are
    kept, and any other exception propagates.
  - MN-17's node list gained the `__abs__` node.
  - No production change. The uncaught exception is not counted, and MN-17 is not equivalent.
- **I-103 amendment.**
  - v11's MI-03 killer "G-06 (inf, 0, 0)" cannot distinguish the mutant: the pre-filter returns
    before any `Fraction` is built for an infinite component.
  - The owner replaced it with "G-06 (nan, 0, 0), node
    `test_g06_section_3_8_order_table[r0-non_finite]`". The transformation is unchanged, and no
    exemption is granted.
- **Final campaign (I-103, BC2 tree): PASS.**
  - Control 74/74.
  - 49 mutants: 44 KILLED by assertion on their designated nodes.
  - 5 documented equivalent survivors (ME-01 to ME-04, M-W2), with v11's proofs reproduced in the
    derivation note §6.
  - NOT OK: none.
  - MN-17 is killed at `test_g06_float_subclass_overrides_never_run`
    (`('raised', 'not_binary64') != ('returned', …)`). MI-03 is killed at the NaN node.
- **History kept** in `mutation/`: i101 (incomplete), the MN-17 diagnostic, i102 (earlier MI-03
  designation), and i103 (final).

### S2.6 Listing, derivation and DL-4

- **The frozen listing** (`tests/s2_dl4_points.txt`, sha256 `0983900a…7c31`, committed in A):
  22 665 entries (22 601 `passes`, 64 `evolute_region`) and 8 853 class X entries.
- **G-17b:** 0 class X differences on every CI job (A, BC, BC2, D) and on the host.
- **G-17a:** class X, label and witness-slot differences are 0 everywhere. Class P coordinate
  differences are report-only: 2 188 (macOS arm64), 2 305 (Ubuntu), 0 (macOS x86_64, the
  generation environment under I-101).
- **M1 derivation (§3.7.6; OB-19):**
  - all 8 G-03 boundary pairs were located by M1 bisection without the polynomial;
  - each equals its G-03 constant, and M2, the classical values and the polynomial agree.
- **M1 cross-check of every listing label (OB-02):** 0 of 22 665 disagree; smallest |relative
  margin| 2.569e-19. Stop 15 not reached.
- **G-08 (DL-4 outcome conformance, bitwise at accepted points):** green on every CI job and the host.

### S2.7 Report-only rows (not gates; not bounds)

- **Host RP-1 to RP-7 and RP-9** at BC; the component bytes are identical at BC2 and D.
  - RP-6a PS-NEG dispatch 18/2/180, max |dh| 1.18e-9 m.
  - RP-7 X-D1: 0 bit differences over 656 points.
  - RP-9: the census equals the component at 22 665 of 22 665 entries.
- **RP-8 / RP-9 by the CI log route** (BC and BC2, identical):
  - 0 outcome differences between any two platforms;
  - 19 154 accepted, 64 `evolute_region`, 3 447 `non_convergence` on each;
  - max |dh| 1.49e-8 m, max |dphi| 5.6e-16 rad.
- **Ulp distances near h = 0.** Where h = 0 on one platform and h = −2^-30 m on another, the ulp
  distance is enormous. Those 22 to 30 pairs per platform pair are counted separately.
- No `numerical_failure` occurred on any platform for any non-injected input (stop 17 not reached).

### S2.8 Regression (§3.13) at D

R-1 to R-4 ran in fresh clones of D (`37251004406c9d9959123ed862d1ab6b13d7dccc`, tree
`6fa4a31d1236edc48ccfaa03111de4bd9fdb3c0f`), with BASE = K recomputed in separate fresh clones from
GitHub. The host was macOS x86_64 with CPython 3.12.15, on 2026-11-07, from 18:50Z to 19:32Z.

- Driver: `docs/science/experiments/m3-t2/s2/scripts/s2_rgates.sh.txt`, the I-101 version. The run
  used an I-103 adaptation that generalizes the clone-path normalization and adds R-S1 and R-S2.
- Full record: external, `~/tars-evidence/I-103/regression/`.

| Gate | D | BASE K (recomputed) |
|---|---|---|
| **R-1** M1 Proof | PASS, 9/9 steps; golden `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4` | PASS, 9/9; same golden |
| **R-2** M2 Proof | PASS, 20/20 steps; `m2_proof` 228 [PASS] / 0 [FAIL] | PASS, 20/20; 228 / 0 |
| **R-3** T1 | 110 passed: T1's 109 plus the one new `test_constants.py` function. r01/r02 correction checks byte-identical to the committed results, and between D and K | 109 passed; identical |
| **R-4** T0 | 314 passed | 314 passed |
| **R-5** | G-13 PASS for K..D; protected paths byte-identical to K | — |
| **R-6** | CI 4/4 `success`, attempt 1, on every pushed commit: A, BC, BC2, D (E: see the S2 handoff) | — |
| **R-7** | K..D changes no completed M3 record. Every changed path is in §3.6's allowlist (S2.2) | — |
| **R-S1** | S1's 100 tests pass unchanged; S1's `SHA256SUMS` verifies (96 OK, 0 failed) | — |
| **R-S2** | full suite 1 518 passed (K: 1 390 on the host), exit 0 | — |

**R-2 semantic comparison.**
- In `m2_final_states_record.json`, only `revision` and the record's `sha256` differ.
- The `missions` block is identical. Substituting K's revision reproduces K's record `sha256`.
- All 229 PASS/FAIL, digest, golden, snapshot, manifest and threshold lines of `m2_proof_stdout.txt`
  are identical after temp-path normalization. 0 other lines differ.

**Metadata-only differences in the proof logs:**
- revision and date;
- uv timings;
- pytest count, 1 390 → 1 518;
- `ruff format` file count, 274 → 290;
- the S2 tests' warnings-summary output, which includes the X-P3 listing.

### S2.9 Merge record (§3.17; r1 §9 item 4; D-S2-9 as proposed)

- **S1 merge.** BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` → K
  `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`, on 2026-11-03.
  - It was a fast-forward by ordinary push (`ee602c5..83d573b main -> main`).
  - 10 linear commits, with no merge commit (re-verified: `git rev-list --count` 10,
    `--merges` 0).
  - K tree `03e01038bf9b84060a8a7d7b126dfa225cb9f513` (re-verified).
- **Post-merge CI: run 41672716486.**
  - Attempts 1 and 2 failed because the arm64 runner was not provisioned.
  - Attempt 3 succeeded, 4/4 at K.
  - Two of the four jobs, `check (ubuntu-latest)` and `check (macos-15-intel)`, are attempt-1
    results that GitHub carried over, and were not executed again. Re-verified: their attempt-3
    start times equal attempt 1's (16:17:50Z, 16:17:54Z). See the OD-9 record §2.3.
- **Post-merge fresh-clone validation:** PASS (OD-9 record §2.4).
- **S1 acceptance:** I-65, recorded at planning O in `docs/milestones/M3-T2-S1-acceptance-I65.md`
  (blob `ffc4875a07892326d61f010fb0958b2726fc8707`).
- **Merge and OD-9 record:** planning O `6498957d354c8230273d116aa9495fffe762c141`,
  `docs/milestones/M3-T2-OD9-merge-model-I66.md` (blob
  `de959954d9f8bd47e6b50ebb78bd7b6e8e58c228`), §2 and §4.
- **Supersession, stated without editing the lines.**
  - The element "NOT MERGED" in this report at K, lines 3, 537, 687 and 778, is superseded by the
    merge.
  - Every other element of those lines is unchanged, as the OD-9 record §3.3 states.
  - The earlier text of this report stays byte-identical.
- **Observation, not acted on.** Line 13 of this report at K, inside the I-60 superseding note, reads
  "**S1 is NOT ACCEPTED and NOT MERGED.**". It is not listed in the OD-9 record §3.3 or in v11's
  proposed merge record. This record does not extend the supersession to it on the author's
  authority. It is noted for the owner and the §5.2 review.
- **Planning integration** is not performed and stays deferred.

### S2.10 Carry-forward for S4 and T3 (§5.4 OB-29)

- **F-17.** `GeodeticDomainError` subclasses `ValueError`, so a broad `except ValueError` would catch
  it. S4 and T3 must design their error handling with that in mind.
- **§3.18 item 15.** `numerical_failure` has an undetermined cause and is not a domain
  classification. S4 and T3 must not handle it as an ordinary numerical domain rejection.
- **D-S2-2 (c), owner's destination for the versioned model identifiers** (r1 §2 item 9;
  ADR-0009 item 5): **S4** (I-97). No identifier is assigned in S2.
  - The exact definition an identifier would version is recorded in
    `docs/science/experiments/m3-t2/s2/evolute-guard-derivation.md` §3.
  - OB-31 is PENDING in S4.
- **OB-30** (S4 and T3 each address F-17 and §3.18 item 15 in their own designs, verified by
  their own reviews) is PENDING in those scopes and is never marked MET by S2.

### S2.11 D-S2-11 (b-iv): the P8 evidence sentence

`docs/decisions/requests/DR-0029-m3-t0-proposals.md:568` reads: "Both inverse algorithms are valid
outside the evolute region near the centre."
- For DQ-1 as specified, with its 60-iteration cap, this is contradicted near the equatorial cusp
  outside E (v11 §3.20; F-01).
- There the iteration does not meet its stop test within 60 iterations, and S2 rejects such points
  with `non_convergence`. On the frozen listing these are 3 081 DG-CUSP and 366 DG-DEEP points
  (RP-6b; host, CI identical).
- DR-0029 is not edited, and no status note is added.

### S2.12 Stops, deviations and open items

1. **Interrupted gate run (I-99/I-100).** The first host run of A's gates was killed at 61% when a
   session ended. It is preserved as incomplete evidence and was never counted as PASS. I-101
   authorized the replacement run, which passed.
2. **Generation-environment fields.** The author applied an interpretation without authority. I-100
   reported it, and I-101 approved it afterwards (S2.0).
3. **Stop 8 (MN-17), then I-102 and BC2.** See S2.5.
4. **MI-03 designation, then I-103.** See S2.5. This is an owner amendment of a designated witness
   only.
5. **A defect caught before BC.** A `geodesy.py` comment repeated the `6378137.0` literal, and the
   existing test `test_wgs84_literals_only_in_constants_module` failed on it. The comment was
   corrected before BC was committed, and no test changed.
6. **Recreated drafts.** `/tmp` was cleared between sessions. The red-run test drafts were recreated
   and recorded as new working material, not as recovered originals.
7. **Log-format handling (documented, verified by sha256).** Two changes are made only when
   extracting records, and the extracted records are checked against the sha256 each test computed.
   - pytest indents warning-summary lines by two spaces. Exactly that indent is removed.
   - GitHub job logs carry a timestamp on every line and a U+FEFF at chunk starts. Both are removed.
8. **Open:** the line-13 observation in S2.9.

### S2.13 Obligations

- **PENDING:** OB-01 to OB-29, OB-32 and OB-33. They are marked MET only by the §5.2 independent
  implementation review, from implementation evidence. Nothing is MET now.
- **Carried forward (L):** OB-30 (S4, T3) and OB-31 (S4).

**Status after E: S2 IMPLEMENTED / VALIDATED (local and CI) / NOT REVIEWED / NOT ACCEPTED / NOT
MERGED.** The independent implementation review is not started, and merging is not authorized.
