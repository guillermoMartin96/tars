# S1 proposal v3: owned raw coast snapshot (v3-S), for owner approval; NOT implemented

> **Record status (I-45, 2026-10-28): FINAL v3-S revision. Independent Review 03: `PASS`** (0 BLOCKER,
> 0 MAJOR; R-04 MINOR corrected editorially in §4 and §6; N-01 NOTE escalated to the owner, §7).
>
> - I44-Q1 is resolved by the owner (I-45, option (a)) after contract verification (§3.2).
> - The I-44 draft (`4654ee2`) stopped on that question; this revision supersedes it.
> - The earlier review verdicts are **unchanged**: Review 01 (proposal v1) and Review 02 (proposal v2)
>   remain `REQUEST_CHANGES`. This proposal does not reverse them (§8).
> - Review 03 record: `docs/reviews/M3-T2-S1-proposal-review-03.md`. The reviewed text (sha256
>   `407c66bc…01df1b`) differs from this record only by the R-04 correction (§4, §6), the writer-corpus count (§4), the re-run note (§4a) and the
>   post-review status text (this block, §7, §8). Diff: `s1-v3s-i45/proposal-reviewed-vs-final.diff`.
> - This document authorizes nothing. **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**

- Supersedes proposal v2 (`M3-T2-S1-proposal-v2.md`, REQUEST_CHANGES in Review 02) in §2–§6 only.
- Owner decisions:
  - I-44 "Option 1: v3-S (owned snapshot)" (`M3-T2-S1-decision-I44.md`);
  - I-45 "I44-Q1 option (a)" (`M3-T2-S1-decision-I45.md`).
- Evidence:
  - `docs/science/experiments/m3-t2/s1-v3/` (I-44);
  - `docs/science/experiments/m3-t2/s1-v3s-i45/` (I-45 contract verification and re-run).
- Same host only (macOS x86_64, CPython 3.12.15, NumPy 2.5.3); no cross-platform claim.

## 1. Constraints carried forward unchanged

- **F3:** the coast mass expression is `dry + max(prop, 0.0)` (I-39A).
- **OD-2:** option A is authorized, but its delta is not used: T-07 (a)/(b) keep their BASE assertions
  (I-40, I-42).
- **OD-4:** absent mass is `None`, never `0.0`.
- **OD-5:** in `simulator.py` only the import line, `_derivative` and `_powered_derivative` (with their
  closures) change.
- **Changed paths:** the allowlist of 4 paths (T-11). No change to `Simulator.__init__`, tick logic,
  engine scheduling, step splitting or atomicity.
- **Context validation:**
  - Powered contexts validate at construction (`ForceContext(mass)`).
  - Coast contexts are `ForceContext.deferred(...)`: converted to an owned binary64 at construction
    (type errors raise then); rejected if non-finite or non-positive on **every** read; never cached,
    repaired or coerced (I-41 option B, I-42 U-1 reading).
- **R-01 (Review 01 finding; recorded CLOSED in Review 02):** the powered context is built after the
  finiteness check, the F/m check, `law.direction` and `thrust_acceleration`, and T-07 (k) pins this
  order. It is unchanged in v3: v3 does not touch the powered closure relative to v2.
- **R-03 (Review 02 MINOR) corrections (I-43):** `prototype-v2.patch` naming; T-07 (i)/(j)/(k) in the
  plan; M-14 → T-07 (k).
- **No new runtime validation.** S1 adds no rejection of stage type, dtype or shape and changes no
  unrelated input handling. Production code is not changed to enforce the contract (I-44 §2, I-45).

## 2. The change (exact; `prototype-v3.patch` relative to BASE `ee602c5`)

Identical to prototype v2 except the coast closure, which becomes:

```python
def coast(t, y):
    r, v = y[:3], y[3:6]
    prop = float(np.ndarray.__getitem__(y, _PROP))
    ctx = ForceContext.deferred(spacecraft.dry_mass_kg + max(prop, 0.0))
    return np.concatenate([v, force_model.acceleration(t, r, v, ctx), _COAST_RATES])
```

- The patch also adds a comment citing I-44/U-1, and tests T-07 (l) and the T-04 snapshot tests (§5).
- `forces.py` is byte-identical to prototype v2.
- Changed paths: the same 4 allowlisted files.
- `prototype-v3.patch` sha256 is `6199a6e6…5731b`. It was unchanged by I-45: no code was modified.

## 3. Formal definitions

### 3.1 U-1, owned mass snapshot (as applied to S1)

For every `ForceContext` built with a mass (powered and coast):

1. At construction the mass is a built-in `float` (binary64) owned by the context. No reference to the
   stage array, a view of it, a NumPy scalar or a callable is kept.
2. Its value is fixed at construction. Later writes to the originating stage storage cannot change it:
   by the integrator after the call, by reuse of one buffer for several stages, or through views or
   aliases.
3. Coast: the value is `dry_mass_kg + max(p, 0.0)`, where `p` is the binary64 **stored** at index 6
   of the stage array handed to the derivative, read at the call. Powered: unchanged from BASE.
4. Validation:
   - Powered: at construction (raises `ValueError`).
   - Coast: on every read. Each read either returns the same float or raises the same
     `ValueError("total_mass_kg must be finite and positive, got …")`.
5. The context does not keep the stage array alive.

### 3.2 Supported input contract (I44-Q1 resolved: I-45 option (a))

**Supported stage.** A stage `y` handed by an `Integrator` to a derivative that the `Simulator` builds
**with a spacecraft** (the coast and powered closures of `_powered_derivative`) is supported when:

1. it is an instance of `numpy.ndarray`, including any subclass that otherwise satisfies these
   conditions;
2. its dtype is binary64 (`float64`), in either byte order;
3. it is one-dimensional with exactly 8 elements;
4. it follows the documented layout `y = [r(3), v(3), m_prop, dv_sensed]`
   (`simulator.py:51`, ADR-0007, DR-0026 §1).

Without a spacecraft, the documented layout is the 6-element M1 state `y = [r, v]`. It keeps that
layout; S1 neither narrows nor changes it, and its derivative performs no element read
(contract verification C-1).

**Verification.** `s1-v3s-i45/contract_verification.md`:

- The `Integrator` protocol, the `Derivative` alias, the `Simulator` and closure docstrings, ADR-0004,
  ADR-0007, DR-0013, DR-0026, the M2 milestone and proof records, and the BASE tests all agree with
  this layout. None supports another shape.
- BASE tests pass no custom integrator to `Simulator`.
- The scenario schema admits only `rk4`.
- The `integrators.py` module docstring ("6 components") is stale but not conflicting. It is not
  edited (D-1).

**Not enforced.** The `NDArray[np.float64]` annotation enforces nothing at run time. S1 adds no
runtime validation. An unsupported stage is not rejected up front: its behaviour is whatever the
unchanged code does with it, disclosed in §6.

**Out of contract:**

- Python sequences;
- object dtype;
- other float dtypes;
- float64 stages that are not 1-D of size 8 on a spacecraft derivative.

**Stored-value semantics** (owner-acknowledged, I-44 §2):

- **MaskedArray:** the coast mass uses the **stored** element at index 6; the mask is not interpreted.
  A masked propellant yields the underlying stored value (whatever the integrator left there), not
  "no value" and not NaN.
- **A subclass that reinterprets elements through `__getitem__`** (for example, returns a scaled
  value) is read at its stored value, not its interpreted value. Example: stored 300 kg, interpreted
  600 kg → coast mass 1300 kg, where v2 gave 1600 kg.
- The **legacy force model** still receives `r = y[:3]` and `v = y[3:6]` through the subclass's own
  indexing, exactly as at BASE. Only the new mass read bypasses it.

## 4. Why v3-S avoids the R-02 changes (analysis, then evidence)

**Mechanism.** `np.ndarray.__getitem__` is the base type's C slot (`array_subscript`).

- Called unbound on an instance of any ndarray subclass, it does not invoke a Python-level
  `__getitem__` override (MaskedArray, `recarray`, user subclasses).
- For an integer index on a 1-D array it returns an array scalar built by the dtype's `getitem` from
  the stored bytes. The dtype handles byte order; strides and non-contiguous views are honoured.
- It creates no view, so no `__array_finalize__` runs.
- Indexing is not a ufunc or array function, so no `__array_ufunc__`, `__array_function__` or
  `__array_wrap__` is called.
- `float()` of an `np.float64` is exact and cannot raise or warn.

Hence, for a supported stage (§3.2), the added coast read cannot warn, raise, call user code or depend
on a mask.

**Limits: this is not a claim that bypassing subclass indexing is safe in general.**

- It changes *which value* a reinterpreting subclass yields (§3.2).
- It raises for inputs that are not ndarrays or are too small (§6).
- A subclass that stores something other than physical float64 elements in its buffer is outside
  what "stored value" can mean here. No NumPy-provided float64 subclass does that.

**What the read still does on out-of-contract inputs:**

- for a non-ndarray, it raises `TypeError` (the descriptor requires `ndarray`);
- for object dtype, it returns the stored object (`float(None)` raises `TypeError`);
- for a 1-D stage of size < 7, or a 2-D stage whose first axis has length ≤ 6 (for example (1, 8)
  or (2, 4)), it raises `IndexError`;
- for a 2-D stage whose first axis has length > 6 (for example (8, 1)), index 6 selects a row, and
  `float()` of that row raises `TypeError: only 0-dimensional arrays can be converted to Python
  scalars` (Review 03 R-04; `s1-v3s-i45/probe_r04.txt`).

BASE's **powered** closure already performs `float(y[_PROP])` and raises the same exception for each of
these shapes: `IndexError` for size 6, (1, 8) and (2, 4); `TypeError` for (8, 1) (`probe_shapes.txt`,
`s1-v3s-i45/probe_r04.txt`).

**Evidence (`s1-v3/`; re-run under I-45 in `s1-v3s-i45/`):**

| Check | Result |
|---|---|
| Custom-integrator corpus (`harness_integrators.py`) | **v3-S vs BASE: 0 differing rows on supported kinds.** 392 differing rows, all out of contract (`list` 196, object `None` 196), all with a spacecraft. Identical to BASE: object floats, float32, longdouble. v2 vs BASE: 500 supported rows differ (masked, raising and warning `__getitem__`), plus object `None` 196. v3-L vs BASE: 0. |
| Probe Part A (14 cases, warnings recorded and raised as errors) | v3-S = BASE on every supported case. `list` and object `None` raise `TypeError`. |
| Probe Part B (contexts read after the step, stage mutated, re-read; lifetime) | v3-S: every context reads 1300.0 / 1300.0 / 1300.0 and never keeps the stage alive. Masked → stored 1300. Raising / warning `__getitem__` → 1300, no warning. Scaling `__getitem__` → stored 1300 (v2 gave the interpreted 1600). v3-L: 1123 / 1000 after writes, keeps the stage alive, and moves warnings and exceptions to read time. |
| Main direct-API corpus (26 880 cases) and stage-writer corpus (26 111 cases; 26 112 JSONL lines with the header) | v3 = BASE byte for byte (`e0309486…a814`, `3310fd90…0415`). The option-A control still differs in 964 cases. M-14 differs in 46 writer cases, M-19 in 0. |

Corpus axes: 6 216 runs over 27 supported integrator kinds and 10 out-of-contract kinds.

- **Supported kinds:**
  - Euler and RK4, each with 12 float64 stage wrappers: plain, masked propellant, nomask, all-false
    mask, raising / scaling / warning `__getitem__`, `__array_finalize__` subclass, `recarray`,
    read-only, strided view, big-endian;
  - shared-buffer RK4, row-view RK4, write-after.
- **Force models (7):** zero, point mass, point mass + J2, NaN-after, propellant stage-writer, raising,
  list-returning.
- **Other axes:** dt ∈ {0.5, 10, 1e308, +inf}; with and without burn and spacecraft; warnings recorded
  and raised as errors; 3 attempts each.

## 4a. Regression (fresh clones, `repro.sh.txt`, `regression_summary.txt`)

| Check | BASE | v3 prototype |
|---|---|---|
| S1 tests (86) | T-07 29/29 green; T-01…T-06 57 red by AttributeError; 0 collection errors | 86/86 |
| Full pytest suite | 1 290 passed | 1 376 passed (1 290 + 86) |
| M1 Proof (`run_m1_proof.sh`) | PASS, 9/9 steps | PASS, 9/9 steps |
| M2 Proof (`run_m2_proof.sh`) | PASS, 20/20 steps | PASS, 20/20 steps |
| R-3 / T1 (correction checks r01, r02; 109 tests) | identical / 109 passed | identical / 109 passed |
| R-4 / T0 (`check_review0*.py`) | 314 passed | 314 passed |
| Scenarios (5, `run_mission.py`) | — | output trees byte-identical to BASE (stdout differs only in the printed output path) |
| T-10 AST identity / T-11 changed paths | — | 51 checks, 0 failures / the 4 allowlisted paths |
| Mutation campaign (24 mutants) | — | control 86/86; 23 killed, each for its declared reason; M-19 survives 0/86 |

This table is the I-44 result. The I-45 fresh-clone re-run (`s1-v3s-i45/regression_summary.txt`)
reproduced every row, with identical corpus hashes, test counts and Proof step counts.

## 4b. I-44 §4 coverage map

All items are green on v3. Exception types, warnings, state commitment and state hex are recorded for
each.

| I-44 §4 item | Where |
|---|---|
| 1 standard float64 stage | T-04/T-05 bit-for-bit tests; probe `rk4_control`; corpus `plain` |
| 2 MaskedArray, masked propellant | T-07 (l); T-04 stored-propellant test; probe `masked`; corpus `masked_prop` (+ nomask, all-false) |
| 3 raising indexing | T-07 (l); T-04 stored-propellant test; probe and corpus `raising_getitem` |
| 4 custom integrators with subclasses | corpus (Euler/RK4 × 12 wrappers); probe `scaling`/`warning_getitem`, `recarray`, `byteswapped`, `strided` |
| 5 mutation after construction | T-04 snapshot test [write-after]; probe `mutate_after` |
| 6 shared stage buffer | T-04 snapshot test [shared-buffer RK4]; probe `shared_buffer` |
| 7 views and aliased storage | T-04 snapshot test [row-view RK4]; probe `views`, `strided` |
| 8 repeated reads before and after mutation | T-04 snapshot test; probe Part B read1 / read2 / after mutation |
| 9 warnings as errors | T-07 (l); probe Part A error mode; corpus `error` mode |
| 10 finite-dt overflow (I-40) | T-07 (i); corpus dt = 1e308; main corpus |
| 11 dt = +inf, T-07 (a)/(b) | T-07 (a)/(b) BASE assertions; corpus dt = +inf |
| 12 object dtype, list | probe and corpus (§6) |
| 13 invalid mass, NaN propagation | `test_t01_c_*` (construction and deferred read); `test_t04_invalid_coast_stage_mass_is_carried_and_rejected_on_read`; corpus `nan_after` |
| 14 powered ordering, R-01 | T-07 (d), (g), (k); writer corpus; corpus `stage_writer` with burn |

## 5. Tests (v2 plan plus)

**T-07 (l)** (`tests/test_s1_failure_paths.py`; R-02 regression; green at BASE):

- A custom integrator hands the coast derivative (i) a MaskedArray with the propellant masked, or
  (ii) a float64 subclass whose `__getitem__(6)` raises.
- With warnings raised as errors, the tick commits, and r, v and the propulsion snapshot equal those
  of the same integrator on a plain copy, bit for bit.

**T-04 snapshot** (`tests/test_s1_force_context.py`; red at BASE by AttributeError):

- (a) `test_t04_coast_context_is_an_owned_snapshot_of_the_stage_mass`
  [write-after, shared-buffer RK4, row-view RK4]: after the integrator has overwritten the stage
  storage, every coast context reads `(DRY + PROP).hex()` twice, as a built-in float.
- (b) `test_t04_coast_context_does_not_keep_the_stage_alive` (weakref).
- (c) `test_t04_coast_mass_is_the_stored_propellant_of_a_subclass_stage` [masked, raising
  `__getitem__`].

**Discrimination** (`discrimination.txt`, `discrimination_reasons.txt`):

| Tree | T-07 (l) | T-04 (a) | T-04 (b) | T-04 (c) |
|---|---|---|---|---|
| BASE | pass | fail (AttributeError) | fail (AttributeError) | fail (AttributeError) |
| v2 | fail (`UserWarning` raised as error; `LookupError`) | pass | pass | fail (`ValueError … nan`; `LookupError`) |
| v3-L | pass | fail by assertion (1123 / 1000 ≠ 1300) | fail (stage kept alive) | fail (`ValueError`, `LookupError` at read) |
| v3-S | pass | pass | pass | pass |

- T-07 (l) distinguishes v3-S from v2.
- T-04 (a)/(b) distinguish v3-S from v3-L.
- S1 total: 86 tests (v2's 78 + 8 nodes).

**Mutation** (`mutation_summary.txt`; each kill is checked against a per-mutant reason pattern on
every failing node):

- M-20 (v2's subclass-sensitive read) is killed by T-07 (l) and T-04 (c).
- M-21 and M-21b (lazy references, dispatching and base-class) are killed by T-04 (a)/(b).
- M-14 is killed by T-07 (k).
- M-19 survives as the documented equivalent mutant (§5.1).

### 5.1 M-19 equivalence (carried from proposal v2 §3.4; unchanged by v3)

M-19 builds the powered context with `ForceContext.deferred(mass)` instead of `ForceContext(mass)`.

**Why it is equivalent.**

- The powered closure reaches the construction only after `thrust_acceleration(engine, …, mass)`.
- `thrust_acceleration` already rejects any `mass` that is not a finite positive real
  (`_require_positive`).
- So the `mass` reaching construction is always valid. Eager construction cannot raise, and a
  deferred context validates the same value on read with the same result.
- In S1 nothing reads the powered context's mass (the legacy adapter ignores it).

The two variants are therefore observationally identical for every input that reaches the line.

**Evidence and status.**

- Evidence: 0/86 tests fail; the writer corpus differs in 0 cases.
- Review 02 item 8 independently confirmed this.
- I-43 accepted M-19 "within the independently verified scope of the current production code".
- If a later stage adds a powered-mass consumer or moves the construction before
  `thrust_acceleration`, the equivalence must be re-established.
- Review 03 is asked to re-confirm it.

## 6. Out-of-contract compatibility disclosures (v3-S vs BASE; all with a spacecraft)

These inputs are outside §3.2. v3-S does not reject them up front. The table records what changes
relative to BASE.

| Stage handed to the coast derivative | BASE | v3-S |
|---|---|---|
| Python `list` | whatever BASE's arithmetic does: in the corpus, commits in 48 of the 196 differing rows; otherwise raises its own errors (`TypeError: can't multiply sequence…`, `RuntimeError`, `FloatingPointError`, warnings) | `TypeError: descriptor '__getitem__' requires a 'numpy.ndarray' object but received a 'list'`, before the force model; tick not committed |
| object dtype, propellant `None` | commits, or fails later (corpus: 70 of the 196 differing rows commit) | `TypeError: float() argument must be a string or a real number, not 'NoneType'`; tick not committed (as v2) |
| object dtype with float propellant; float32; longdouble | — | identical to BASE |
| float64, size 6 (no propellant element) | coast commits; powered raises `IndexError` | `IndexError: index 6 is out of bounds for axis 0 with size 6` on coast too (as v2) |
| float64, 2-D (1, 8) or (2, 4) | coast raises `ValueError` (concatenate dimensions); powered raises `IndexError` | `IndexError: index 6 is out of bounds for axis 0 with size 1` (or `size 2`) on coast too |
| float64, 2-D (8, 1) (Review 03 R-04) | coast raises `ValueError` (concatenate dimensions); powered raises `TypeError` (0-dimensional conversion) | `TypeError: only 0-dimensional arrays can be converted to Python scalars`; tick not committed |
| float64, size 10 | commits | identical |

- I-44 §2 provisionally accepts the `list` and object-dtype deltas as out of contract.
- I-45 option (a) places the shape rows out of contract.
- None of these rows is a supported-input difference.

## 7. Authorization points for the owner

- **Resolved (I-45):** I44-Q1, option (a), scoped per §3.2 (C-1).
- **Review 03 N-01 (escalated, not applied):** the snapshot and lifetime regressions cover coast
  contexts only. A powered lazy-reference mutant passes all 86 S1 tests. Adding a powered
  snapshot/lifetime test and mutant (M-22) would change the approved test plan, so it is left to the
  owner. Recommended before or with commit A.
- **Open, for the owner:**
  - final acceptance of the §6 disclosures;
  - the stored-value semantics of §3.2;
  - the test and mutation additions of §5;
  - any authorization of implementation commit A.

  None is authorized by this document.

## 8. Review history (dispositions unchanged)

| Review | Subject | Verdict | Findings | Status in this proposal |
|---|---|---|---|---|
| 01 (`M3-T2-S1-proposal-review-01.md`) | proposal v1 | **REQUEST_CHANGES** | R-01 MAJOR (powered context reachable with an invalid mass via writable stages) | Remains REQUEST_CHANGES. R-01 recorded CLOSED for v2 in Review 02. v3 keeps v2's powered closure (§1). |
| 02 (`M3-T2-S1-proposal-review-02.md`) | proposal v2 | **REQUEST_CHANGES** | R-02 MAJOR (coast read dispatches to subclasses), R-03 MINOR (stale references) | Remains REQUEST_CHANGES; R-02 recorded OPEN there. v3-S is the proposed remedy (§2, §4). R-03 corrected under I-43. |
| 03 (`M3-T2-S1-proposal-review-03.md`) | this proposal and prototype v3 | **PASS** | R-04 MINOR (2-D exception statement), N-01 NOTE (powered snapshot test coverage), D-1 NOTE (stale `integrators.py` docstring) | R-02 recorded CLOSED, R-01 PRESERVED, I44-Q1 CONSISTENT, M-19 EQUIVALENT CONFIRMED. R-04 corrected; N-01 escalated (§7); D-1 not changed (production source). |

A new verdict on v3 does not alter the verdicts of Reviews 01 and 02. Those reviews judged v1 and v2,
and their records stand as written.
