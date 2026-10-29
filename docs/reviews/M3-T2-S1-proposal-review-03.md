# External Review: M3 T2 S1 ForceContext proposal v3-S (I-45), Review 03

## Review details

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a184fc-7d2a-7752-ab1e-841084fc3cdf`.
  It is a fresh session, separate from Reviews 01 and 02, from a provider separate from the
  implementer's.
- **Date:** 2026-10-28.
- **Reviewed material:** a **proposal and scratch prototype**, not committed work.
  - `I-45-proposal-v3S.md`, sha256 `407c66bcabeea38dbf4408b01ac56954031e5069d5444642a01df5847001df1b`.
    It was copied in `raw/M3-T2-S1-proposal-codex-review03-evidence/pkg/` and is recorded as
    `docs/milestones/M3-T2-S1-proposal-v3.md` with only the R-04 correction below.
  - `prototype-v3.patch` relative to BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`, sha256
    `6199a6e644dac0988e4a14e9d56d40b2db5f5c77fba410af314360be5753731b`
    (`docs/science/experiments/m3-t2/s1-v3/prototype-v3.patch`).
  - Material for building v2 and v3-L: `prototype-v2.patch`, `v3L-vs-v2.patch`.
  - The implementer's scripts: main, writer and custom-integrator corpora, mutation, AST, probes.
    Their outputs are mutation results, the corpus comparison, the probe summary and discrimination.
  - Owner records: I-40, I-41–I-43, the I-43 investigation, I-44 and I-45 verbatim, Review 01/02
    records, and the I-45 contract verification.
  - The reviewer verified the package manifest (25 files, `pkg/SHA256SUMS`).
- **Authorization:** I-45 §3 (owner, 2026-10-28).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review03-prompt.md` (sha256 `5e9c64bc…cdb690`);
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review03.md`, the complete final message verbatim
    (as received, sha256 `89573efa…17405b`), except that one absolute local path in the final
    sentence is replaced by `$SCRATCH`. The original is kept externally;
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review03-evidence/`: `REVIEW.md`, `REPRODUCE.md`,
    the reviewer's scripts (as `.py.txt`) and small outputs. Absolute local paths in 12 files are
    scrubbed; their original sha256 values are listed in `SCRUBBED.txt`. Copied trees, corpora and per-mutant
    trees are listed with sha256 in `EXCLUDED.txt` and kept externally
    (`~/projects/tars-evidence/I-45/`).
- **How it was run:**
  - a fresh clone pinned at BASE, `uv sync --locked`, `review_scratch/` untracked;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`, no network;
  - afterwards the tracked tree was clean and HEAD unchanged (`ee602c5`). The reviewer's own
    125-file manifest verifies.

## Summary

**`VERDICT: PASS`.** 0 BLOCKER, 0 MAJOR, 1 MINOR (R-04), 2 NOTE (N-01, D-1).

| Closure line | Review 03 |
|---|---|
| **R-02** (Review 02 MAJOR) | **CLOSED** |
| **R-01** (Review 01 MAJOR; CLOSED in Review 02) | **PRESERVED** |
| **I44-Q1 interpretation** | **CONSISTENT** |
| **M-19** | **EQUIVALENT CONFIRMED** (for current production behaviour) |

| Item | Reviewer's independent result |
|---|---|
| Contract (I44-Q1) | Inspected protocols, interfaces, documentation and tests independently. 8 elements describe spacecraft stages; M1 remains 6. The generic RK4 tests on small ODE vectors do not establish alternative spacecraft-stage shapes. |
| R-02 | Own 336-case Euler / midpoint / RK4 corpus: 0 BASE-vs-v3-S execution differences, 36 for v2. The supplied 6 216-case corpus independently reproduced 0 supported-input differences. |
| U-1 ownership | A recording adapter captured coast **and powered** contexts. Built-in floats, hex unchanged after storage mutation, repeated reads agree, stage weakrefs expire. Shared, row and strided storage tested. |
| `np.ndarray.__getitem__` | Hostile `__getitem__`, `__array_finalize__`, `__array_ufunc__`, `__array_function__`, `__array_wrap__`, `__float__`/`item` and properties did not run on supported reads. Byte order, strides, read-only and `memmap` were correct. No supported counterexample found. |
| MaskedArray, reinterpreting subclasses | Stored value used, as disclosed. Masked, nomask and all-false match BASE under both warning policies. Legacy models still receive subclass-indexed `r`, `v`. |
| Exceptions and warnings | Type, message, cause/context, warning order, callback timing, committed hex and retries compared. Main (26 880) and writer (26 112, the reviewer counting JSONL lines; 26 111 cases plus the header) corpora are byte-identical between BASE and v3-S. Signalling-NaN probes found no difference. |
| Finite-dt overflow, dt = +inf | Split-tick failures at tick 2 reproduced with committed state unchanged. The runner classifies them `non_finite`. T-07 (a)/(b)/(j) keep BASE's `+inf` behaviour. |
| R-01 ordering | Powered closure ASTs match v2. Order: finiteness → F/m → direction → `thrust_acceleration` → context → force. |
| Scope | Exactly 4 allowlisted paths. Simulator outside the permitted regions is AST-identical, including `__init__`. No runtime stage validation added. Local M1/M2 proof reports byte-identical. T0 314/314 on both trees; T1 outputs match. |
| Tests | v3-S: 1 376 passed. BASE with the proposed tests: 1 319 passed and 57 expected `AttributeError` failures, no collection errors. T-07 (l) distinguishes v2; the snapshot and lifetime tests distinguish v3-L. |
| Mutation | All 23 declared non-equivalent mutants killed for their stated reasons. M-19 survives, equivalent. |
| Records | Earlier REQUEST_CHANGES verdicts are explicitly unchanged; R-03 references are corrected. |
| Platform | Same host only; remote CI and cross-platform jobs were not run by the reviewer. |

## Findings register and dispositions

| ID | Severity | Location | Finding | Implementer's reproduction | Disposition |
|---|---|---|---|---|---|
| M3T2S1-R3-F1 (R-04) | MINOR | Proposal §4 ("for size < 7 or 2-D it raises `IndexError`") and §6 | The 2-D claim is too broad. For a (8, 1) stage, BASE's coast raises `ValueError` (concatenate) and v3-S raises `TypeError: only 0-dimensional arrays can be converted to Python scalars`. Both stay at tick 0. | **Confirmed** (`docs/science/experiments/m3-t2/s1-v3s-i45/probe_r04.txt`, coast and burn, shapes (1, 8), (8, 1), (2, 4)). BASE's powered closure raises the same exception as v3-S's coast for each shape (`IndexError`, `TypeError`, `IndexError`). The stage is out of contract (I-45 option (a)). | **ACCEPTED. Corrected** (editorial only, I-45 §2 "Correct any inconsistent statements"): proposal §4 and §6 now state the shape-dependent exception. No design, code or test change. |
| M3T2S1-R3-N1 (N-01) | NOTE | T-04 snapshot coverage; mutation plan | The dedicated after-write and lifetime regressions exercise only coast contexts. A powered lazy-reference mutant (v3-L machinery in the powered closure only) passes all 86 S1 tests. The reviewer's independent ownership assertions kill it (mass changes through a shared-buffer alias; stages kept alive). The actual prototype passes those assertions. | **Confirmed by reading** the reviewer's `check-powered-lazy.txt` (before 0x1.444p+10, after 0x1.18cp+10, 4 stages alive) and `powered-lazy-tests.txt` (86 passed). | **ACCEPTED as a coverage gap; NOT applied under I-45.** Adding a powered snapshot/lifetime test and a mutant M-22 changes the approved test and mutation plan, and I-45 §3 forbids modifying the design or expanding the authorization automatically. **Escalated to the owner** as a recommended addition before or with commit A. U-1 for powered contexts is currently established by code reading, the reviewer's independent probes and the I-44 probe, not by a committed regression test. |
| M3T2S1-R3-N2 (D-1) | NOTE | BASE `src/tars/sim/integrators.py:3–4` | The module docstring's "y = [r, v] (6 components)" is stale for spacecraft simulations. Disclosed accurately. | Same as the I-45 contract verification D-1. | **ACCEPTED; not changed** (production source; I-45 "Do not modify production code"). Left for a separately authorized documentation change. |

## Proof gate

- [x] All Critical findings resolved: none raised.
- [x] All High findings resolved: none raised in Review 03. R-02 (Review 02) is recorded **CLOSED**
  by this review for proposal v3-S and prototype v3.
- [x] Every substantive finding has an explicit disposition.
- [x] Accepted fixes have been re-tested: R-04 by the implementer's probe. The correction is
  editorial and no code changed.
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none. N-01 is
  escalated as a test-coverage decision, not a scientific claim.

**Review gate result: PASS.**

- This verdict applies to proposal v3-S and prototype v3 only.
- It does **not** convert or reverse the REQUEST_CHANGES verdicts of Review 01 (proposal v1) or
  Review 02 (proposal v2), which stand as recorded.
- It authorizes nothing. Implementation requires the owner's explicit authorization.
- **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**
