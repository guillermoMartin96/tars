# S1C-03 correction: complete T-08 writer-corpus comparison (I-62)

**Authority:** I-62, which accepts I-61 finding S1C-03 (MINOR, must-fix) and authorizes this correction to
the evidence and report only. The verbatim text is kept externally in `~/tars-evidence/I-62/I-62.md`.
No production code, tests, numerical algorithms or scientific assumptions are changed.

**Status:** S1 is NOT ACCEPTED and NOT MERGED. S2 is NOT AUTHORIZED. This directory is new; no earlier
evidence was edited.

## Defect (S1C-03)

The T-08 drivers compared each corpus with:

```python
ld = lambda f: [json.loads(l) for l in open(f"{d}/{f}")][1:]
```

The `[1:]` slice assumes a header line in every corpus:

| Corpus | Harness | Line 1 | Effect of `[1:]` |
|---|---|---|---|
| Main direct API | `harness.py` | header `{"numpy", "tars_file"}` | header skipped, as intended; all 26 880 cases compared |
| Stage writers | `harness_writers.py` | case `10.0\|w0_6_nan\|none\|leo\|none` (no header is written) | **first real case skipped**; 26 111 of 26 112 cases compared |
| Custom integrators | `harness_integrators.py` (separate comparator) | header `{"header", "integrators"}` | header skipped, as intended; not affected |

`defect/` reproduces this. It holds the I-59 comparison code, extracted verbatim from the committed
`i59/scripts/i59_gates.sh.txt`. Run on the retained I-59 BASE and H files, it prints
`writers corpus cases BASE 26111 H 26111`. `omitted_record.txt` shows that the dropped line is a real case.

Negative control NC-1 below shows the consequence. With the historical expression, a change to the first
writer case was **not detected**.

## Why the historical count was 26 111

The writer corpus has 26 112 cases:

4 time steps × 192 writer models × 2 initial states × (2 + 3 × 5) craft/burn combinations

`format/format_check.txt` rebuilds this sequence from the harness axes and matches it to every file,
in order.

Every recorded count came from the sliced comparison, which printed 26 111. Codex review 03 (I-45)
counted 26 112 JSONL lines and attributed the extra line to a header. It was a case. The count was carried
forward unchanged from I-42 onwards.

Locations of the superseded count, **none of which is edited**:

| Location | Text |
|---|---|
| Planning branch `5714959`: `M3-T2-S1-proposal-v3.md:175` (pinned) | "stage-writer corpus (26 111 cases; 26 112 JSONL lines with the header)" |
| Planning: `M3-T2-S1-decision-I45.md:62` and its copy in `docs/reviews/raw/M3-T2-S1-plan-codex-review01-evidence/pkg/` | "Stage-writer corpus (26 111 cases)" |
| Planning: `docs/reviews/M3-T2-S1-proposal-review-03.md:57` | "26 111 cases plus the header" |
| Planning: `m3-t2/s1-proposal/i42_reverification_summary.txt:21`, `s1-v3/regression_summary.txt:21`, `s1-v3s-i45/regression_summary.txt:21`, `s1-v3s-i45/README.md:34`, `s1-v3s-i45/proposal-reviewed-vs-final.diff:45` | "writer corpus cases 26111" / "26 111 cases" |
| D evidence: `s1/t08/corpus_compare.txt:2`, `s1/logs/summary.txt:41`, `s1/README.md:36`, driver `s1/scripts/d_evidence.sh.txt:54` | "writers corpus cases BASE 26111 C 26111" |
| I-59 evidence: `s1/i59/README.md:73`, driver `s1/i59/scripts/i59_gates.sh.txt:64` | "26 880 + 26 111 cases" |
| Report: `docs/milestones/M3-T2-report.md` §S1.9 table | "Stage writers \| 26 111" |

Every "0 differing" result stated for the writer corpus was true for the 26 111 cases compared. The pinned
full-file hash (`3310fd90…0415`) was also equal at both trees. The count and the per-case coverage were wrong.

## Corrected comparison

`scripts/compare_corpora.py.txt` declares the format of each corpus. It does not detect the format and
does not slice:
- `main` must have exactly one header record on line 1, and every other line must be a case;
- `writers` must have no header, and every line must be a case.

On both files it checks:
- **F1:** each line is valid JSON and the header layout matches the declared format;
- **F2:** the number of cases equals the expected count;
- **F3:** no case identity is duplicated;
- **F4:** the case-identity sequences of BASE and TIP are equal, in the same order.

It then compares:
- **C1:** every case line, byte for byte, at the same case index. This is the governing criterion, I-40
  T-08 / INV-2: same-platform identity of the per-tick hex of r, v and the propulsion state, and of all
  engine events.
- **C2:** every pair of parsed records, as a secondary check.
- **C3:** the `main` header line, reported separately from the cases.

Every case is listed with its index, file line and identity. Equivalence is established by these per-case
comparisons, not by the file hashes.

## Inputs

| Item | Value |
|---|---|
| BASE | `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (fresh GitHub clone) |
| J | `f47cf0d0fcc5e5ca01167aa689c7228e03127215` (fresh GitHub clone; `src/` and `tests/` equal H) |
| Harnesses | the I-59 pinned copies; `harness.py` `35791177…8772` and `harness_writers.py` `5b49304c…5648` equal the committed D copies (checked by the driver) |
| Invocation | as in D and I-59: J's venv, with `PYTHONPATH` set to each tree's `src` |
| Host | macOS 26.2 x86_64, CPython 3.12.15, NumPy 2.5.3, uv 0.12.23 (`env.txt`) |
| Pinned hashes | main `e0309486…a814`, writers `3310fd90…0415` (I-44/I-45) |

`corpora/` records the hashes of the four freshly regenerated corpora and the four retained I-59 corpora. All
eight equal the pinned hashes. The corpora themselves (30–36 MB each) are kept externally in
`~/tars-evidence/I-62/`, as in D and I-59.

## Results

| Comparison | Format | Cases compared | Identical | Different | Checks | Verdict |
|---|---|---|---|---|---|---|
| Fresh BASE vs J | writers | **26 112** (index 0 = line 1 … index 26 111 = line 26 112) | 26 112 | 0 | F1–F4 pass; C2 0 | ALL_CASES_IDENTICAL |
| Fresh BASE vs J | main | 26 880 (line 2 … line 26 881) | 26 880 | 0 | F1–F4 pass; C2 0; C3 header identical | ALL_CASES_IDENTICAL |
| I-59 BASE vs H (retained files) | writers | 26 112 | 26 112 | 0 | F1–F4 pass; C2 0 | ALL_CASES_IDENTICAL |
| I-59 BASE vs H (retained files) | main | 26 880 | 26 880 | 0 | F1–F4 pass; C2 0; C3 header identical | ALL_CASES_IDENTICAL |

- **Previously omitted case.** The case at index 0, `10.0|w0_6_nan|none|leo|none`, is compared and is
  byte-identical.
- **No differences.** No previously untested case differs.
- **Per-case listing.** `compare_fresh/writers.cases.tsv` (sha256 `4455ab44…6b3b`, 26 112 rows) lists
  every writer case. The I-59 listing is byte-identical to it.
- **Main listings.** They are byte-identical between the fresh and I-59 comparisons (sha256 `5b7d0f7e…856a`,
  26 880 rows) and are kept externally.

## Negative controls (`negative_controls/`)

Each control modifies a copy of the fresh J corpus and runs two comparators:
- **historical:** the D/I-59 expression, verbatim;
- **corrected:** `compare_corpora.py`.

A value change flips the last hex digit of one float in one record. The record is re-serialized as the
harness does, and the script first checks that this reproduces the unmodified line exactly.

| ID | Modification | Historical | Corrected |
|---|---|---|---|
| NC-0 | none, writers (baseline) | 0 differing | exit 0, identical |
| **NC-1** | **first writer case** (index 0), `steps[0].ok.r[0]` | **0 differing: NOT DETECTED** | **exit 1, DIFF at case index 0, line 1, `10.0\|w0_6_nan\|none\|leo\|none`** |
| NC-2 | middle writer case (index 13 056) | 1 differing | exit 1, DIFF at index 13 056 |
| NC-3 | last writer case (index 26 111) | 1 differing | exit 1, DIFF at index 26 111 |
| NC-4 | first writer case deleted | detected (shifted) | exit 2, F2 + F4 |
| NC-5 | writer index 1 replaced by a copy of index 0 | detected | exit 2, F3 duplicate + F4 |
| NC-6 | writer index 0 and 1 swapped | detected | exit 2, F4 order |
| NC-7 | header line prepended to the writer corpus | detected (shifted) | exit 2, F1 |
| NC-8 | none, main (baseline) | 0 differing | exit 0, identical |
| NC-9 | first main case (index 0, line 2) | 1 differing | exit 1, DIFF at index 0 |
| NC-10 | last main case (index 26 879) | 1 differing | exit 1, DIFF at index 26 879 |
| NC-11 | main header removed | detected (shifted) | exit 2, F1 + F2 + F4 |
| NC-12 | main header only (`numpy` value) | 0 differing: not detected | exit 1, C3 header differs, cases 0 |

**Result: 13/13 controls behave as expected.** NC-1 shows that the historical comparison could not see the
first writer case, and that the corrected comparison does.

## Files

- `scripts/`: the corrected comparator, the format and count check, the negative controls and the driver
  (`s1c03_run.sh`). Stored as `.txt`, as in the D and I-59 directories.
- `defect/`: the verbatim I-59 comparison code, its output on the I-59 files, and the identity of the
  omitted line.
- `format/format_check.txt`:
  - per-file line, header and case counts;
  - unique identities;
  - identity sequence against the harness axes, for 8 files (`corpora/` = fresh, `t08/` = I-59).
- `corpora/`: input hashes, fresh and I-59.
- `compare_fresh/` and `compare_i59/`: per-comparison summaries, plus the complete writer per-case
  listing.
- `negative_controls/`: the combined output and each corrected-comparator summary.
- `logs/summary.txt`: the driver log, with clone SHAs and trees, harness checks, hash checks and every
  result.
- `env.txt`: the host environment.
- `SHA256SUMS`: covers every other file in this directory.

**Reproduce:**

```bash
s1c03_run.sh OUT_DIR CLONE_DIR I59_T08_DIR
```

The scripts must be copied with the `.py`/`.sh` names, next to a `pinned/` directory that holds the two
harness files from `../scripts/*.py.txt`.

**Run history.** A first full run (run 1) gave the same results. Its log is identical apart from timestamps.
It was repeated as run 2, recorded here, after two display-only edits:
- the negative-control detail lines now include the `TIP: F2/F3` messages;
- the format check now labels each file with its source directory.

Both runs are kept externally.

**Redactions:** none. Output paths are relative by construction. The only URL is the public repository
used by the earlier drivers.

## Limitations

- **One host, same platform.** This is a same-host comparison on macOS x86_64. It is not a cross-platform
  or accuracy claim.
- **Scope.** It covers the T-08 main and writer corpora only. The integrator corpus was not affected
  (its header is real); its I-59 and I-61 results are unchanged.
- **Superseded statements.** Every 26 111 statement in the locations above is superseded by this
  directory and by report §S1.17. None is edited.
