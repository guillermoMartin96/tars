# S2 H-01 correction: local implementation and validation (uncommitted)

**AUTHOR EVIDENCE.** This is the implementer's correction packet. It is not independent review evidence.
It does not change the independent verdict on H (REQUEST_CHANGES), does not close H-01, and marks no
obligation MET. Nothing has been committed or pushed. No review was launched. S2 is not accepted and
nothing was merged.

- `INSTRUCTION.md`: the owner's instruction, verbatim.
- **Baseline:**
  - H is `8074a19bf33cf5b6d20f7d211ff44f82bf28ba93`, with tree `3b70b865abfa4137227ccce0d070ba6484cdef26`.
  - The worktree is `~/.superset/worktrees/tars/milestone-3-t2-s2-geodetic`, branch
    `milestone-3-t2-s2-geodetic`.
  - It was clean at exact H before editing (`inputs/input-verification.txt`).

## 1. Inputs established

- **Review manifest:**
  - `S2-REREVIEW-H-8074a19/continuation-20261108T211523Z/MANIFEST.sha256` has sha256
    `8400c3bfd78b5457d5cd06360efb0401c05db9d407765fa30c3f60bf2f61922f`, as expected.
  - All 783 entries are OK (`inputs/review-manifest-check.log`).
- **Files read:** `review.md`, `H-01-normalization.md`, `findings-disposition.md`, `obligation-ledger.json`,
  `method-and-evidence-scope.md`, and the diagnostic's source, output, run record and environment record.
  Their hashes are in `inputs/input-verification.txt`, each confirmed present in the manifest.
- **Governing requirement:** pinned v11 (`I-93/S2-proposal-v11.md`, sha256 `f7d88086…3072809`) §3.8 step 0,
  lines 1447–1460: "**Every other type raises `TypeError`.**" The exception-propagation permission covers
  only `len(r)` and `r[0]/r[1]/r[2]`. **No message text is prescribed.**
- **Repository instructions:** `CLAUDE.md` was read.
- **Constraint checks:**
  - The mutation harness anchors (`mutate.py`) contain no text from the changed line.
  - No test or gate pins `geodesy.py`'s or the test file's bytes. Only historical evidence files cite
    H's blob, and they are not touched.

## 2. The correction (`diff/`)

**Source** (`src/tars/sim/geodesy.py`; blob `e409e263` → `82ca9aaa`, sha256 `9df9a3e9…` → `290fb095…`):

```diff
-    raise TypeError(f"geodetic input: unsupported component type {t.__name__}")
+    # A fixed message: reading t.__name__ would run a caller metaclass's hook (H-01).
+    raise TypeError("geodetic input: unsupported component type")
```

**Rationale:**
- `t = type(v)` and the `issubclass` tests against `bool`, `float` and `int` dispatch nothing to the caller.
  `type.__subclasscheck__` walks the real MRO.
- The only caller-dispatched operation on the rejection path was the `t.__name__` read in the message.
- The contract prescribes the exception type, not the text. A constant message is therefore the smallest
  change that removes the callback. It keeps no dynamic detail that could reintroduce one.
- **Not done:**
  - no `try` around the name read, which would still run the hook and need translation of a caller
    exception;
  - no descriptor bypass such as `type.__dict__['__name__'].__get__(t)`;
  - no change to the E.1 `try`, base-slot normalization, precedence or arithmetic.

**Test** (`tests/test_s2_geodetic.py`; blob `50c75e31` → `d68c7a7d`, sha256 `8383d526…` → `67f9b9e4…`):
- One new G-06 node, `test_g06_h01_unsupported_type_rejection_consults_no_metaclass_hook`.
- It uses the reviewer's exact witness: the same metaclass and sentinel text, and an ordinary built-in tuple
  `(Unsupported(), 0.0, 7.0e6)`.
- It asserts, by assertion:
  - the outcome is not the sentinel;
  - its type is exactly `TypeError`;
  - it is not a `GeodeticDomainError`;
  - it has no `__context__` or `__cause__`;
  - the hook was never called (`calls == []`).
- Existing tests are unchanged. That includes the structural len/index propagation tests (KeyError, SV-1,
  SV-2) and the accepted-type normalization tests.

## 3. Red before green (`red-green/`; `scripts/red_green.sh`, `scripts/classify_red_green.py`)

**Setup:**
- A disposable `--no-local --no-hardlinks` clone of the local repository, at exact H (HEAD and tree
  verified).
- `UV_OFFLINE=1 UV_PYTHON_DOWNLOADS=never …/uv sync --locked --offline` exited 0.
- uv 0.12.23, sha256 `566a2724…`. Network was denied with `sandbox-exec`.
- **Command, identical for both phases** (`red/command.txt` and `green/command.txt`):
  `pytest -v -rA -p no:cacheprovider --junitxml=… <H-01 node> tests/test_s2_environment_record.py
  tests/test_s2_xp3_listing.py tests/test_s2_dl4_points.py`.
  - This is one process: the target node plus the nine recorders.
  - Each phase has its own run record, ENV record, schema-2 listing, G-17a report and G-17b record.

**Red and green runs:**

| | Component executed | Test executed | Window (UTC) | Result |
|---|---|---|---|---|
| **red** | H: blob `e409e263…`, sha256 `9df9a3e9…` | blob `d68c7a7d…`, sha256 `67f9b9e4…` | 00:23:35–00:23:39 | exit 1. The target is a JUnit `<failure>` (not an error, skip or collection error): `AssertionError: H-01: the metaclass sentinel escaped; hook calls ['__name__']`. The 9 recorders pass and the records are complete. |
| *worktree source edited* | | | mtime 00:23:48 | |
| **green** | candidate: blob `82ca9aaa…`, sha256 `290fb095…` | same bytes (verified) | 00:23:52–00:23:55 | exit 0, 10 passed. The records are complete. |

- `red-green/classification.json` checks all of this: 12 of 12 checks true, including the ordering
  "test edited < red start < red end < source edited < green start".
- **Validator mistake, retained:** a first classification attempt mis-compared a porcelain string; the run
  record strips a leading space. It is kept in `classification-attempt1-validator-mistake.json`, with a
  note. It did not involve any execution.

## 4. Validation of the candidate bytes (all offline, network denied, disposable clones)

The candidate is H plus the two uncommitted files.
- Every validation clone was verified equal to the worktree, file for file (4,785 files).
- **Candidate tree:** `b5b9e928d4203ea82ea5178be945490ce705a1d8`, computed with a temporary index and no
  commit.
- **Interpreter:** CPython 3.12.15, interpreter sha256 `de2897e0…`. Its ENV fields match the generation
  record.

### Candidate checks (`candidate/`, `scripts/candidate_validate.sh`)

| Check | Result |
|---|---|
| ruff check / ruff format --check | exit 0 / exit 0 |
| G-13 scope, working-tree form vs K | PASS, no problems |
| Reviewer's probe, **unchanged bytes**, on the candidate | It now observes `TypeError("geodetic input: unsupported component type")`, `metaclass_hook_calls: []`, `is_sentinel: false`. The probe asserts the *defect*, so its exit 1 is the expected outcome on a corrected component. |
| Complete S2 test suite (5 S2 test files) | **130 passed**, with no failures, errors or skips |
| Full test suite | **1,521 passed**: H's 1,520 plus the new node. No failures, errors or skips. |
| S2 records from each pytest execution | ENV, G-17a and G-17b are ok. The schema-2 listing has 22,665 entries and its body sha verifies. The census validation against the frozen listing is valid. The census CSV is byte-identical across red, green, the S2 suite and the full suite. |
| **G-17b exact Class X replay** | 8,853 Class X entries compared, **0 differences**. The comparison is bit for bit with signed zeros distinguished, in environment kind *generation*. |
| G-17a | all 6 nodes pass in every execution |
| Host report-only script (RP-1 to RP-7, RP-9 host census) | exit 0. All 11 outputs are **byte-identical** to the independent reviewer's H host-report results. They are report-only observations, not gates. |
| **Mutation campaign** (pinned I-105 `mutate.py`, sha256 `0ca9d707…`, unchanged; mutants applied to copied `src/` only) | The control passes all 76 designated nodes. 44 mutants are KILLED by qualifying assertion failures and the 5 approved equivalents survive. NOT OK: []. **The independent audit** (`candidate/campaign-audit.json`) confirms each of the following: (a) all 50 executions have complete records and 9 passing recorders; (b) no `<error>` or skip is counted; (c) every kill is an assertion-form `<failure>`; (d) MG-02 fails only with `(0.0, nan, 7000000.0)` and MG-04 only with `(0.0, 0.0, 7000000.0)`; (e) each executed mutant hash equals the candidate plus its recorded edits; (f) verdicts, edits and node bindings are identical to the reviewer's H campaign. |

### Regression (`regression/`, `scripts/h01_rgates.sh`)

The script is the I-106 driver with the reviewer's offline adaptation; the diff is in
`scripts/s2_rgates-I106-to-H01.diff`.
- **Candidate clones:** dA, dB and dC. Each is H with the worktree changes copied in.
- **K clones:** bA, bB and bC at K `83d573bd…`, **recomputed**, not read from stored results.
- **Records:** every phase has its own §3.16 run record and a direct DL-5 probe. All 14 records exited 0.

| | Result on the candidate (vs recomputed K) |
|---|---|
| R-1 (M1 proof) | PASS at the candidate and at K. The pinned golden `7a4e1877…` is present in both. |
| R-2 (M2 proof) | PASS at both, each with 228 [PASS] and 0 [FAIL]. The semantic lines are identical (229). The missions are identical. See the note below. |
| R-3 (T1) | The r01 and r02 correction outputs are byte-identical, candidate vs K, and both equal the committed results. T1 tests: 110 passed at the candidate, 109 at K. |
| R-4 (T0) | 314 passed at both. |
| R-S1 | 100 S1 tests pass. The S1 SHA256SUMS file verifies; the only non-OK line is the appended exit line. |
| R-S2 | Full suite: 1,521 passed. The records extract and the census validates. |
| ruff | check exit 0; format reports 302 files formatted |

**R-2 note.** The M2 record's differing keys are `revision`, `sha256` and **`tree_clean`**. The candidate is
deliberately uncommitted, so the proof wrappers record `working_tree_clean: no`. The inherited check
substitutes only K's revision, so it prints `False`.
- `regression/r2-supplementary-check.txt` substitutes K's revision **and** `tree_clean`, and then
  reproduces K's record hash: `True`.
- The proof diffs differ only in `proof_run.log` and temporary-path lines. This is the same shape as
  I-106: M1 has 22,781 diff lines (vs 22,775) and M2 has 22,831 (vs 22,825). The six extra lines come from
  the changed test count and timings.

## 5. Limitations

- **Uncommitted bytes.** Every execution here ran uncommitted candidate bytes on top of commit H. Run
  records bind them by blob and sha256, and by the candidate tree id. They are not runs of a pushed commit,
  and they do not satisfy OB-18 (CI 4/4) or any CI-platform evidence (CI3 G-rows, RP-8 three-platform
  listings). Those require the proposed commits and their own CI.
- **Proof wrappers report `working_tree_clean: no`** for candidate clones. This is expected for the same
  reason.
- **Host only.** All executions ran on this host (macOS x86_64, generation environment). Class P
  observations on other platforms are not produced here. They stay report-only.
- **Not rerun:** the commit-D derivation (M1 label cross-check, boundary pairs). It does not involve the
  component and is byte-identical in inputs.
- **What the environment record shows.** Matching ENV proxy fields do not certify an identical library or
  build environment (r83:83).
- **I-106 exception.** It is not extended to any execution in this packet. Each new execution carries its
  own records.

## 6. Status and next steps

- **Obligations:** see `OBLIGATION-IMPACT.md`. H's independent ledger remains the standing assessment:
  29 MET, OB-11 and OB-27 FAILED, OB-30 and OB-31 later-scope PENDING.
- **I-104 findings:** they remain as independently resolved at H.
- **H-01:** it remains OPEN pending independent review of a pushed corrected tip.
- **Commit and push:** a proposed sequence, for later authorization only, is in
  `PROPOSED-COMMIT-SEQUENCE.md`.
- **Scratch:** disposable clones, virtual environments and the 49 copied mutant `src/` trees are in the
  session scratchpad and are excluded from the manifest
  (`candidate/campaign/MUTANT-SOURCE-TREES-NOTE.txt`).
- **Manifest:** `MANIFEST.sha256` covers every file in this directory except itself.
