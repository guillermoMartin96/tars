# M3 T2 S1: I-59 correction evidence (superseding record, added under I-60)

This subdirectory is an **appended, superseding record**. It does not replace the Commit D evidence
in the parent directory.
- **D evidence stays unchanged.** The D files, including `../SHA256SUMS` (96 entries), `../README.md`
  and `../mutation/`, are byte-identical to Commit D (`1b25254e…`). `../SHA256SUMS` covers those D files
  only. It does not cover this subdirectory, which has its own `SHA256SUMS`.
- **What it supersedes.** The D mutation verdicts ("24 KILLED") were reached under per-mutant
  reason patterns. Five of those patterns accepted a propagated exception as a kill. Under the strict
  I-40 §10 criterion, those D verdicts are superseded by the records below. The D files are kept as
  historical evidence.
- **Authority.** I-58 (independent review at E: REQUEST_CHANGES, S1R-01 and S1R-02 MAJOR), I-59
  (correction authorized) and I-60 (F–H approved, push, CI, and this record). Their verbatim texts are
  kept externally in `~/tars-evidence/I-58/`, `I-59/` and `I-60/`. They are not recorded on the
  planning branch.
- **Status.** **S1 is NOT ACCEPTED and NOT MERGED.** No new independent review has been run on these
  corrections.

## Commits

| Ref | SHA | Content |
|---|---|---|
| E | `0e70f540126788be8a9596d49ef422d2488f8f08` | S1 report (I-58 reviewed this tip) |
| F | `c52c0904b19d9abd701864a329350c15ce0b8b64` | `tests/test_s1_force_context.py`: 10 S1R-01 regression nodes (red at E's code) |
| G | `45053ef6c2a11f8bd8272928060df8845f65f1b1` | `src/tars/sim/forces.py`: `ForceContext._store` converts `OverflowError`/`ZeroDivisionError` from the mass conversion into `ValueError("total_mass_kg is not representable as a binary64 number")`, `from None` (+8 −2) |
| H | `2a35ebf397b474533300ee5a0169f8d5d025e86a` | both S1 test files: designated nodes of M-05, M-14, M-15, M-16 and M-20 assert the expected exception (`_assert_raises` / `_assert_no_exception`). Node IDs unchanged. |

E..H changes exactly 3 files (+159 −18): `src/tars/sim/forces.py`, `tests/test_s1_force_context.py`
and `tests/test_s1_failure_paths.py`. All three are I-40 §6 allowlisted. `_owned_float` and every other
protected function stay AST-identical to BASE (T-10 51/51).

## Findings and corrections

**S1R-01 (MAJOR).** At E, an `int` or `float` subclass whose `__float__` raises `ZeroDivisionError`
made `ForceContext(...)` and `ForceContext.deferred(...)` raise `ZeroDivisionError`. That breaks
T-01 (e) ("no input makes construction raise `OverflowError`/`ZeroDivisionError`").
- The I-59 probe also found the same leak for a 0-d `ndarray` subclass whose element read raises.
- Probe output at E: `s1r01_probe/s1r01_at_E.txt`. Probe script: `scripts/repro_s1r01.py.txt`.

G is the fix:
- it converts only those two exception types, around the whole mass snapshot;
- any other exception propagates as the identical object;
- the `TypeError` type check still runs first;
- supported inputs behave as before (2 105-input equivalence below).

**S1R-02 (MAJOR).** I-40 §10: "must fail its designated test node with an assertion failure … a
kill by an unrelated exception does not count".
- At E, five mutants (M-05, M-14, M-15, M-16, M-20) were counted KILLED only because a designated node
  failed with a propagated, unasserted exception. Each D pattern accepted that.
- H changes only those designated nodes. Each now asserts the expected exception's type, message and
  identity, so a wrong exception fails as an `AssertionError` that names it.
- The mutants, their edits and the 25-mutant denominator are unchanged.

## Results

All results were recomputed in fresh clones, on one host: macOS x86_64, CPython 3.12.15, NumPy
2.5.3 (`run_records/`).

| Gate | Record | Result |
|---|---|---|
| Red first, at F (S1R-01 nodes vs E's code) | `red_F/` | 3 failed, 97 passed. The 3 failures are the int/float `ZeroDivisionError` nodes and the 0-d ndarray node. Each is `AssertionError: expected ValueError …, got ZeroDivisionError: sentinel`. The OverflowError, precedence and narrowness nodes already pass at E. |
| Green, at G | `green_G/` | S1 100/100 (90 original + 10 new) |
| Tip H | `tip_H/` | S1 100/100. Full suite 1 390 passed (1 380 at E + 10). `ruff check` and `ruff format --check` exit 0. H's T-07 file run against BASE's `src/` passes 29/29 (`t07_at_base_src.txt`), on this host only. |
| **Mutation, corrected harness, at H** | `mutation/corrected_H/` | Control 100/100. **24 KILLED under strict I-40 §10** (every failing designated node is an assertion failure, class A or B; 0 class C; every failure matches the declared reason). **0 non-qualifying kills.** M-19 SURVIVED as the documented equivalent mutant (v3-S §5.1), 0/100. Denominator 25. |
| Same corrected harness, at E (historical) | `mutation/corrected_E/` | **19 qualifying, 5 non-qualifying** (M-05, M-14, M-15, M-16, M-20) + M-19 equivalent. **E does not meet the I-40 §10 criterion.** |
| Committed D results, re-classified strictly | `mutation/strict_classification_committed_D.txt` | The same 19 / 5 / 1 split as E |
| Per-mutant table and assertion evidence | `per_mutant_kill_classification.md` | Edits and designated nodes identical E vs H for all 25 mutants. Failing nodes identical. M-19's node total grows 90 → 100 only because its designated nodes are the two whole S1 files. |
| Supported-input ForceContext equivalence, E vs H | `fc_equivalence/compare.txt` | 2 105 inputs, direct + deferred + read: **0 differing** |
| T-10 / T-11 | `t10_t11/` | 51/51 AST-identical. BASE..H ⊆ the I-40 §6 allowlist. E..H = the 3 paths above. |

Also recomputed at H for I-59, with the records kept externally in `~/tars-evidence/I-59/run1/`
(sha256 manifest `da4a6032e6815db9c4658c0a0922fdb63bf94796fe1b472fd1efc57ba64cd567`, 3 770 entries):
- T-08: 26 880 + 26 111 cases, 0 differing. Custom integrators: 0 supported-kind differences, 392
  out-of-contract as disclosed. All 6 corpus hashes equal D's.
- T-09: scan passes, comparison passes, negative control 7/7.
- Validated scenarios: 10 files byte-identical to BASE.
- R-1: golden `7a4e1877…20a4`.
- R-2: 228/228.
- R-3: 109 tests, outputs byte-identical.
- R-4: 314 passed.

Platform CI on H is recorded in `docs/milestones/M3-T2-report.md` §S1.16 and in `ci_H/`.

## Limitations that remain

- **S1R-03 (NOTE, no change).** On macOS arm64, `np.longdouble` is binary64, so the T-01 (e)
  extended-precision parameter becomes `inf` there (report §S1.11).
- **S1R-04 (NOTE, no change).** T-09 is an external verification on one host. It is not a CI gate.
- **No dedicated mutant for G.** The fix itself has no mutant in the campaign; the 25-mutant
  denominator was preserved as instructed. Reverting G restores exactly the state `red_F/` shows
  failing.
- **The pinned `classify_nodes` labels F's 3 red nodes "not-as-declared".** That tool predates I-59 and
  expects `AttributeError`. Their actual failure is the declared I-59 assertion.

## Files

- `scripts/` (`.txt` suffix, so CI does not lint them; copy one to run it):
  - `repro_s1r01`: the S1R-01 probe;
  - `classify_i40_10`: the strict A/B/C classifier;
  - `mutate_i59`: the D `mutate.py` with only these changes:
    - the reason patterns of M-05, M-14, M-15, M-16 and M-20 now require the new assertion messages;
    - every failure must be assertion-class (`AssertionError`, `assert`, or pytest `Failed:`), as I-40
      §10 requires;
    - failure messages are kept to 2 000 characters and matched with `re.S`.

    Mutant IDs, edits, designated nodes and order are unchanged. `mutate_i59_vs_pinned_mutate.diff.txt`
    is the exact diff;
  - `fc_equivalence`: the 2 105-input probe (v2; v1 was defective and is kept externally);
  - `i59_gates`: the driver.
- `SCRUBBED.txt`: the files in which absolute local paths were replaced, with their original sha256
  (the originals are in the external evidence).
- `SHA256SUMS`: every other file in this subdirectory.
