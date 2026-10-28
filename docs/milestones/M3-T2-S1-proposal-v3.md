# I-44 proposal v3: S1 with an owned raw coast snapshot (v3-S), for owner approval; NOT implemented

> **Record status (I-44, 2026-10-28): DRAFT, NOT REVIEWED.** Preparation stopped under I-44 §2
> ("If additional differences appear within the supported contract, STOP for owner review") on
> question **I44-Q1** (§7): the v3-S coast read changes the outcome for float64 stages of the wrong
> **shape** (size < 7, or 2-D), which the `NDArray[np.float64]` annotation does not exclude. No Codex
> review of v3 has been run. This document authorizes nothing. **S1 is NOT IMPLEMENTED, NOT
> ACCEPTED, NOT MERGED.**

Supersedes proposal v2 (`M3-T2-S1-proposal-v2.md`, REQUEST_CHANGES in Review 02) in §2–§6 only.
Owner decision implemented: I-44 "Option 1: v3-S (owned snapshot)" (`M3-T2-S1-decision-I44.md`).
Evidence: `docs/science/experiments/m3-t2/s1-v3/` (README, manifest). Same host only (macOS x86_64,
CPython 3.12.15, NumPy 2.5.3); no cross-platform claim.

## 1. Constraints carried forward unchanged

- **F3** coast mass expression `dry + max(prop, 0.0)` (I-39A); **OD-2** option A authorized but its
  delta not used: T-07 (a)/(b) keep their BASE assertions (I-40, I-42); **OD-4** absent mass is `None`;
  **OD-5** only the import line, `_derivative`, `_powered_derivative` change in `simulator.py`;
  allowlist of 4 paths (T-11).
- Powered contexts validate at construction (`ForceContext(mass)`); coast contexts are
  `ForceContext.deferred(...)`: converted to an owned binary64 at construction (type errors raise
  then), rejected if non-finite or non-positive on **every** read, never cached, repaired or coerced
  (I-41 option B, I-42 U-1 reading).
- R-01 closure (Review 02): the powered context is built after the finiteness check, F/m check,
  `law.direction` and `thrust_acceleration`; pinned by T-07 (k). Unchanged in v3.
- R-03 corrections (I-43): `prototype-v2.patch` naming, T-07 (i)/(j)/(k) in the plan, M-14 → T-07 (k).

## 2. The change (exact; `prototype-v3.patch` relative to BASE `ee602c5`)

Identical to prototype v2 except the coast closure, which becomes:

```python
def coast(t, y):
    r, v = y[:3], y[3:6]
    prop = float(np.ndarray.__getitem__(y, _PROP))
    ctx = ForceContext.deferred(spacecraft.dry_mass_kg + max(prop, 0.0))
    return np.concatenate([v, force_model.acceleration(t, r, v, ctx), _COAST_RATES])
```

(with a comment citing I-44/U-1), plus tests T-07 (l) and the T-04 snapshot tests (§5). `forces.py` is
byte-identical to prototype v2. Changed paths: the same 4 allowlisted files.

## 3. Formal definitions

### 3.1 U-1, owned mass snapshot (as applied to S1)

For every `ForceContext` built with a mass (powered and coast):

1. At construction the mass is a built-in `float` (binary64) owned by the context: no reference to
   the stage array, a view of it, a NumPy scalar or a callable is kept.
2. Its value is fixed at construction. Later writes to the originating stage storage (by the
   integrator after the call, by reuse of one buffer for several stages, through views or aliases)
   cannot change it.
3. Coast: the value is `dry_mass_kg + max(p, 0.0)` where `p` is the binary64 **stored** at index 6 of
   the stage array handed to the derivative, read at the call. Powered: unchanged from BASE.
4. Validation: powered at construction (raises `ValueError`); coast on every read (each read either
   returns the same float or raises the same `ValueError("total_mass_kg must be finite and positive,
   got …")`).
5. The context does not keep the stage array alive.

### 3.2 Input contract

- Supported: the stage `y` handed by an `Integrator` to the derivative is a NumPy `ndarray`, or a
  subclass of it, with float64 dtype (`NDArray[np.float64]`, either byte order), and the layout the
  derivative documents: `y = [r, v, m_prop, dv_sensed]`, 1-D, size 8 (**whether shape is part of the
  supported contract is I44-Q1**, §7).
- The annotation does not enforce anything at run time; S1 adds no runtime validation and changes no
  unrelated input handling.
- Out of contract (not float64 ndarrays): Python sequences, object dtype, other float dtypes.
- MaskedArray: the coast mass uses the **stored** element at index 6; the mask is not interpreted. A
  masked propellant therefore yields the underlying stored value (whatever the integrator left there),
  not "no value" and not NaN.
- A subclass that reinterprets elements through `__getitem__` (e.g. returns a scaled value) is read at
  its stored value, not its interpreted value.

## 4. Why v3-S avoids the R-02 changes (analysis, then evidence)

`np.ndarray.__getitem__` is the C slot of the base type (`array_subscript`). Called unbound on an
instance of any ndarray subclass, it does not invoke a Python-level `__getitem__` override
(MaskedArray, `recarray`, user subclasses). For an integer index on a 1-D array it returns an array
scalar built by the dtype's `getitem` from the stored bytes (byte order handled by the dtype); it
creates no view (so no `__array_finalize__`), and indexing is not a ufunc or array function (no
`__array_ufunc__`/`__array_function__`/`__array_wrap__`). `float()` of an `np.float64` is exact and
cannot raise or warn. Hence, for a 1-D float64 ndarray or subclass of size ≥ 7, the added coast read
cannot warn, raise, call user code or depend on a mask. It does not make subclass bypass "safe" in
general: it changes *which value* a reinterpreting subclass yields (§3.2) and it raises for inputs that
are not ndarrays or are too small (§6).

What the read still does: for a non-ndarray it raises `TypeError` (descriptor requires `ndarray`); for
object dtype it returns the stored object (`float(None)` raises `TypeError`); for size < 7 or 2-D it
raises `IndexError`. BASE's **powered** closure already performs `float(y[_PROP])` and raises the same
`IndexError` for those shapes (`probe_shapes.txt`).

Evidence (`s1-v3/`):

| Check | Result |
|---|---|
| Custom-integrator corpus (`harness_integrators.py`): 6 216 runs; 27 supported integrator kinds (Euler and RK4 with each of 12 float64 stage wrappers: plain, masked propellant, nomask, all-false mask, raising / scaling / warning `__getitem__`, `__array_finalize__` subclass, `recarray`, read-only, strided view, big-endian; plus shared-buffer RK4, row-view RK4, write-after) and 10 out-of-contract kinds; 7 force models (zero, point mass, PM+J2, NaN-after, propellant stage-writer, raising, list-returning); dt ∈ {0.5, 10, 1e308, +inf}; with and without burn and spacecraft; warnings recorded and as errors; 3 attempts each | **v3-S vs BASE: 0 differing rows on supported kinds**; 392 differing rows, all out of contract (`list` 196, object `None` 196); object floats, float32, longdouble identical. v2 vs BASE: 500 supported rows differ (masked, raising, warning `__getitem__`) plus object `None` 196. v3-L vs BASE: 0 |
| Probe Part A (14 cases, warnings recorded / as errors) | v3-S = BASE on every supported case; `list` and object `None` raise `TypeError` |
| Probe Part B (contexts read after the step, stage mutated, re-read; lifetime) | v3-S: every context 1300.0 / 1300.0 / 1300.0, never keeps the stage alive; masked → stored 1300; raising / warning `__getitem__` → 1300, no warning; scaling `__getitem__` → stored 1300 (v2 gave the interpreted 1600). v3-L: 1123 / 1000 after writes, keeps the stage alive, read-time warnings and exceptions |
| Main direct-API corpus (26 880) and stage-writer corpus (26 112) | v3 = BASE byte for byte (`e0309486…a814`, `3310fd90…0415`); option-A control still differs in 964 cases; M-14 differs in 46 writer cases, M-19 in 0 |

## 4a. Regression (fresh clones, `repro.sh.txt`, `regression_summary.txt`)

| Check | BASE | v3 prototype |
|---|---|---|
| S1 tests (86) | T-07 29/29 green; T-01…T-06 57 red, AttributeError, 0 collection errors | 86/86 |
| Full pytest suite | 1 290 passed | 1 376 passed (1 290 + 86) |
| M1 Proof (`run_m1_proof.sh`) | PASS, 9/9 steps | PASS, 9/9 steps |
| M2 Proof (`run_m2_proof.sh`) | PASS, 20/20 steps | PASS, 20/20 steps |
| R-3 / T1 (correction checks r01, r02; 109 tests) | identical / 109 passed | identical / 109 passed |
| R-4 / T0 (`check_review0*.py`) | 314 passed | 314 passed |
| Scenarios (5, `run_mission.py`) | — | output trees byte-identical to BASE (stdout differs only in the printed output path) |
| T-10 AST identity / T-11 changed paths | — | 51 checks, 0 failures / the 4 allowlisted paths |
| Mutation campaign (24 mutants) | — | control 86/86; 23 killed, each for its declared reason; M-19 survives 0/86 |

## 4b. I-44 §4 coverage map

| I-44 §4 item | Where (all green on v3; exception types, warnings, commitment and state hex recorded) |
|---|---|
| 1 standard float64 stage | T-04/T-05 bit-for-bit tests; probe `rk4_control`; corpus `plain` |
| 2 MaskedArray, masked propellant | T-07 (l), T-04 (c); probe `masked`; corpus `masked_prop` (+ nomask, all-false) |
| 3 raising indexing | T-07 (l), T-04 (c); probe and corpus `raising_getitem` |
| 4 custom integrators with subclasses | corpus (Euler/RK4 × 12 wrappers); probe `scaling`/`warning_getitem`, `recarray`, `byteswapped`, `strided` |
| 5 mutation after construction | T-04 (a) write-after; probe `mutate_after` |
| 6 shared stage buffer | T-04 (a) shared-buffer RK4; probe `shared_buffer` |
| 7 views and aliased storage | T-04 (a) row-view RK4; probe `views`, `strided` |
| 8 repeated reads before/after mutation | T-04 (a); probe Part B read1/read2/after-mutation |
| 9 warnings as errors | T-07 (l); probe Part A error mode; corpus `error` mode |
| 10 finite-dt overflow (I-40) | T-07 (i); corpus dt = 1e308; main corpus |
| 11 dt = +inf, T-07 (a)/(b) | T-07 (a)/(b) BASE assertions; corpus dt = +inf |
| 12 object dtype, list | probe and corpus (§6) |
| 13 invalid mass, NaN propagation | T-01 (c), T-04 invalid-coast test; corpus `nan_after` |
| 14 powered ordering, R-01 | T-07 (d), (g), (k); writer corpus; corpus `stage_writer` with burn |

## 5. Tests (v2 plan plus)

- **T-07 (l)** (`tests/test_s1_failure_paths.py`, R-02 regression, green at BASE): a custom
  integrator hands the coast derivative (i) a MaskedArray with the propellant masked, (ii) a float64
  subclass whose `__getitem__(6)` raises; with warnings raised as errors the tick commits and r, v and
  the propulsion snapshot equal those of the same integrator on a plain copy, bit for bit.
- **T-04 snapshot** (`tests/test_s1_force_context.py`, red at BASE by AttributeError):
  (a) `…_is_an_owned_snapshot_of_the_stage_mass` [write-after, shared-buffer RK4, row-view RK4]: every
  coast context reads `(DRY + PROP).hex()` twice, as a built-in float, after the integrator has
  overwritten the stage storage; (b) `…_does_not_keep_the_stage_alive` (weakref);
  (c) `…_is_the_stored_propellant_of_a_subclass_stage` [masked, raising `__getitem__`].

Discrimination (`discrimination.txt`, `discrimination_reasons.txt`): BASE: T-07 (l) passes, the 6
T-04 snapshot nodes fail by AttributeError. v2: T-07 (l) fails (`UserWarning` raised as error;
`LookupError`), (c) fails (`ValueError … nan`; `LookupError`), (a)/(b) pass. v3-L: T-07 (l) passes,
(a) fails by assertion (1123 / 1000 ≠ 1300), (b) fails (stage kept alive), (c) fails (`ValueError`,
`LookupError` at read). v3-S: all pass. S1 total 86 tests (v2's 78 + 8 nodes).

## 6. Out-of-contract compatibility disclosures (v3-S vs BASE)

| Stage handed to the coast derivative | BASE | v3-S |
|---|---|---|
| Python `list` | as BASE's arithmetic allows (commit, or its own errors) | `TypeError: descriptor '__getitem__' requires a 'numpy.ndarray' object but received a 'list'` before the force model |
| object dtype, propellant `None` | commit (or later errors) | `TypeError: float() argument must be …, not 'NoneType'` (as v2) |
| object dtype, float propellant; float32; longdouble | — | identical to BASE |
| float64, size 6 (no propellant element) — **I44-Q1** | coast commits; powered raises `IndexError` | `IndexError: index 6 is out of bounds for axis 0 with size 6` on coast too (as v2) |
| float64, 2-D (1, 8) — **I44-Q1** | coast `ValueError` (concatenate dimensions); powered `IndexError` | `IndexError` on coast too (as v2) |
| float64, size 10 | commit | identical |

## 7. Authorization points for the owner

- **I44-Q1 (blocking).** Is the stage shape part of the supported contract? (a) Supported = 1-D
  float64 stage of size 8 (the documented `y = [r, v, m_prop, dv_sensed]`; BASE's powered closure
  already requires index 6): then the shape rows of §6 are out-of-contract disclosures and v3 proceeds
  to review. (b) Shape is not part of the contract: then v3-S changes supported behaviour for those
  stages and needs an explicit authorization or a different design. Implementer recommendation: (a).
- The out-of-contract deltas of §6 (`list`, object `None`) as provisionally accepted by I-44.
- The MaskedArray and reinterpreting-subclass semantics of §3.2 (stored value).
- Test and mutation additions (§5, `mutation_summary.txt`): M-20 (v2's subclass-sensitive read) killed
  by T-07 (l) and (c); M-21 / M-21b (lazy references, dispatching and base-class) killed by the
  snapshot and lifetime tests; M-14 killed by T-07 (k); M-19 the documented equivalent survivor.
