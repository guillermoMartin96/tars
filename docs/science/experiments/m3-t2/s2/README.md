# M3 T2 S2 evidence (commit D; v11 §3.14 step 4)

This directory is S2's committed gate evidence, at the v11 §3.16 location
`docs/science/experiments/m3-t2/s2/`. Commit A's own record is in `commit-a/`, which commit A created and D does not change.

**Status: S2 is NOT ACCEPTED and NOT MERGED.** Implementation-level obligations (IN-1, OB-xx) stay
PENDING until the independent §5.2 implementation review. Nothing here is an accuracy claim. Every
report-only row is labelled report-only, and none is a gate (stop 9).

## Authority

| Record | Kind | sha256 (kept externally in `~/tars-evidence/`) |
|---|---|---|
| Pinned proposal v11 (`I-93/S2-proposal-v11.md`) | approved design (I-97: A/B/C, OD-12 resolved) | `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809` |
| I-97 decision record | owner decision | `71e2fc58f2eba721558175125d75cf792b8b521524f2df95e7a6d3219d7e32ed` |
| I-99 (`I-99/I-99.md`) and PC-7(S2) as issued (`I-99/PC-7-S2-ISSUED.md`) | implementation authorization | `366fa98f…3e86`, `940a3244…be6d` |
| I-101 (`I-101/I-101.md`) | owner determination: "the generation environment" | `3bfe20a92c8dd3bab96e8c6d79eefde6c333970cbfa93f1a237502d39398d2d2` |
| I-102 (`I-102/I-102.md`) | owner sequence adjustment: MN-17 test correction, supplemental commit BC2 | `790e5492ead6a3c370e9cea96747a14112fe8794a9ccdd3b4c1eb0fd6b0114ab` |
| I-103 (`I-103/I-103.md`) | owner external amendment to v11 §3.12: MI-03's designated killer | `9358b879ca835d937d5501c3047462e57464f536c3aacb6c97d684b809de9855` |

- v11 itself is unchanged. I-101, I-102 and I-103 are external owner records.
- `evolute-guard-derivation.md` quotes I-101 and I-103 and summarizes I-102.

## Commits and CI

| Commit | SHA | Content | CI (attempt 1; all four jobs executed in attempt 1) |
|---|---|---|---|
| K (base) | `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f` | `main` | — |
| A | `6c05e53c5ffcb892dacaa6f84e12a163830a4119` | twin, frozen listing, G-17a/G-17b, G-10, G-12a, ENV and X-P3 records | 42265640238: 4/4 success |
| BC | `2b975d626e92c76a18efc873e0991084db30617a` | `geodesy.py`, the `constants.py` addition, S2 gate tests (byte-identical to the original red record) | 42301740647: 4/4 success |
| BC2 | `5bd8340255d673965a2525f19e9fb32210de54b7` | I-102 test correction to one G-06 node (`tests/test_s2_geodetic.py` only) | 42394082295: 4/4 success |
| D | this commit | this directory (outside `commit-a/`) only | this push |

The red run was uncommitted (D-S2-12 (i)). No commit was amended, rebased or force-pushed, and no
CI job was rerun.

## Sequence adjustment (I-102, I-103) and the original stop

1. **Stop 8 at the first D campaign (BC; I-101).**
   - MN-17 ("the component value used as given, instead of the base-slot value") failed its G-06
     override node only by an uncaught `GeodeticDomainError`. That is not an assertion failure, so it
     is not a kill (v11 §3.12).
   - The campaign's MN-17 node list had also omitted the designated `__abs__` case.
   - Record: `mutation/i101-bc-incomplete/` (with `STOP-RECORD.md`; INCOMPLETE) and
     `mutation/i101-mn17-diagnostic/`, a one-off diagnostic and not campaign evidence.
2. **I-102 correction.**
   - `test_g06_float_subclass_overrides_never_run` now captures a `GeodeticDomainError` as an
     observed wrong outcome and rejects it by an explicit assertion. The stored-value result and the
     no-override assertion are kept, and any other exception still propagates. No production change.
   - The corrected file was frozen (blob `0d817de456cf837c06979a5fab601db6be7b6567`, sha256
     `9059ff375993cf156e28fb76b5a3eb95a3601ea99c3572890cc1c1033fa8b661`). Then came a **supplemental
     red run** on a fresh clone of A, with `geodesy.py` absent and `constants.py` = K (`red-supplemental/`).
   - The campaign's MN-17 node list gained the `__abs__` node.
3. **MI-03 designation (I-103).**
   - v11's killer "G-06 (inf, 0, 0)" cannot distinguish the mutant: the §3.7.5 pre-filter returns
     before any `Fraction` is built for an infinite component.
   - The owner replaced it with "G-06 (nan, 0, 0), node
     `test_g06_section_3_8_order_table[r0-non_finite]`". The transformation is unchanged.
   - Analysis: `mutation/i102-bc2-candidate/MI-03-DESIGNATION.md`.
   - The I-102 campaign (`mutation/i102-bc2-candidate/`) used the earlier whole-test MI-03
     designation and is kept as history. The final campaign is `mutation/i103-bc2/`.

## Results

| Gate | Record | Tested tree | Result |
|---|---|---|---|
| Red first, original (§3.14 step 2) | `red-original/` | A plus the 3 test files, uncommitted | 131 nodes: 101 ImportError, 4 assertion, 26 guards or unchanged tests pass; 0 not-OK |
| Red first, supplemental (I-102) | `red-supplemental/` | fresh clone of A plus the frozen corrected file | 112 nodes: 100 ImportError, 2 assertion (G-09, G-11), 10 guards pass (G-10 W1–W7, G-13 ×3); 0 not-OK; identical per node to the original red run of this file |
| Blob binding (stop 14) | `binding/binding-bc.txt`, `binding/bc2-*.txt` | BC, BC2 | BC: the 3 test blobs equal the original red record. BC2: `tests/test_s2_geodetic.py` blob equals the supplemental record; BC..BC2 changes only that file |
| Green | `green/bc-pre-commit/`, `green/bc-fresh-clone/` | BC | ruff check 0, ruff format 0, pytest 1 518 passed (both runs) |
| Green | `green/bc2-candidate/` | BC2 tree (`binding/candidate-equals-bc2.txt`) | ruff check 0, ruff format 0, pytest 1 518 passed |
| G-13 scope | `derivation/g13_scope_check_BC.json`, `binding/g13_scope_check_BC2.json` | K..BC, K..BC2 | PASS, PASS |
| Mutation (final) | `mutation/i103-bc2/` | BC2 tree | control 74/74 pass; 49 mutants: 44 KILLED by assertion on designated nodes, 5 documented equivalents (ME-01 to ME-04, M-W2; proofs in `evolute-guard-derivation.md` §6); NOT OK [] |
| Mutation (history) | `mutation/i101-bc-incomplete/`, `mutation/i102-bc2-candidate/` | BC; BC2 tree | I-101: 43 KILLED, 5 equivalent, MN-17 KILLED_WRONG_REASON (stop 8). I-102: 44/5, earlier MI-03 designation |
| §3.7.6 boundary derivation, M1 listing cross-check | `derivation/derivation_crosscheck.json` | independent of the component | all 8 G-03 pairs, located by M1 bisection, equal the G-03 constants (M2, classical and polynomial agree); 0 of 22 665 listing labels disagree with M1; smallest \|M1 relative margin\| 2.569e-19 |
| Report-only RP-1 to RP-7, host RP-9 | `report-only/host-bc/` | BC (component bytes identical at BC2) | report-only; see `report_only_summary.json` |
| RP-8 (X-P3) and RP-9 by the log route | `report-only/ci-bc-42301740647/`, `report-only/ci-bc2-42394082295/` | BC, BC2 CI | 0 outcome differences between any two platforms; census 19 154 accepted, 64 evolute_region, 3 447 non_convergence on each; max \|dh\| 1.49e-8 m, max \|dphi\| 5.6e-16 rad; BC2 identical to BC. Report-only |
| ENV, G-17a, G-17b per CI job | `ci/*/records/` | A, BC, BC2 | G-17b 0 differences on 8 853 class X entries on every job; G-17a class X, label and witness differences 0; class P 2 188 (macOS arm64), 2 305 (Ubuntu), 0 (macOS x86_64; the generation environment under I-101) |

The listing `tests/s2_dl4_points.txt` is as committed in A: sha256
`0983900a9d1733a71000e6e91aeb8373c5b4fe320ba972f363f540f0e52d7c31`, recorded in `commit-a/SHA256SUMS`.

## Attribution

- Evidence computed on BC stays attributed to BC: the original red binding, BC green, the I-101
  campaign, the derivation, the host report-only rows and BC's CI.
- Evidence that establishes the corrected tip is attributed to BC2: the supplemental red binding,
  the BC2-candidate green, the I-102 and I-103 campaigns, and BC2's CI with its log-derived RP-8 and RP-9.
- `src/` is byte-identical between BC and BC2 (`binding/bc2-scope.txt`).

## Run records

- Host runs: macOS x86_64, CPython 3.12.15, `uv.lock` sha256
  `6d784550fa46f0c79a80ba77012a7179d585916bad97bff26b26ac7d4e7850cf` (`run_records/`).
- CI runs: `ci/*/run.json` and `jobs-attempt1.json` give each job's log URL, the run attempt, the head
  SHA and per-job attempt. Every job executed in attempt 1; none was carried over.
- Records were extracted from the raw job logs with `ci/strip_gh_timestamps.py.txt` and
  `ci/extract_s2_records.py.txt`. Each record is verified by its own sha256
  (`extraction-status.json`). The raw logs stay external, with sha256 in `ci/*/raw-logs.sha256`.

## Kept externally

These are kept under `~/tars-evidence/I-99` … `I-103`, each with a `MANIFEST.sha256`:
- the raw CI job logs;
- the host pytest logs (2.7 MB each, because they embed the X-P3 listing; sha256 and last 60 lines
  in `green/*/`);
- the mutant source trees;
- the fresh clones;
- the owner instruction texts.

R-1 to R-4 run after D, in fresh clones (§3.14 step 5). Commit E records them.

## Files

- `scripts/`: the evidence scripts, as `.txt` so that CI does not lint them.
- `SCRUBBED.txt`: the files in which the absolute home path was replaced by `$HOME`, with their
  original sha256.
- `SHA256SUMS`: covers every file in this directory except itself and `commit-a/`, which has its own.
