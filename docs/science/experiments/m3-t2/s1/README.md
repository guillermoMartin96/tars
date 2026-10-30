# M3 T2 S1 evidence (Commit D; I-40 §12 step 4, authorized by I-52)

This directory holds the S1 gate evidence for the I-40 allowlisted location `docs/science/experiments/m3-t2/s1/`.
- **Governing documents on the planning branch `milestone-3-t2-authorization`:** I-40
  (`M3-T2-S1-authorization.md`), the pinned proposal v3-S (sha256 `dd705dd4…102d`), plan
  amendment A-1 (`04aca5f4…db3`), and owner rulings I-48 (`M3-T2-S1-decision-I48.md`) and
  I-49/I-50 (`M3-T2-S1-decision-I49-I50.md`).
- **Owner authorizations not yet in a repository record:** I-51 (Commit C) and I-52 (this
  commit). Their verbatim texts are kept externally, in `~/tars-evidence/I-51/I-51.md` (sha256
  `fd610dc9…f551`) and `~/tars-evidence/I-52/I-52.md` (sha256 `6cf0e045…17d9`). Recording them in the repository is left to a
  later authorized record.
- **Status:** **S1 is NOT ACCEPTED and NOT MERGED.** The S1 independent review, Commit E (the
  `M3-T2-report.md` §S1) and the B–D push are not authorized by I-52.
- **Same host only:** macOS x86_64, CPython 3.12.15, `uv.lock` sha256 `6d784550…` (see
  `run_records/`). No cross-platform claim is made. The CI matrix runs on the push tip (R-6).

| Commit | SHA | Content |
|---|---|---|
| BASE | `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` | `main` |
| A | `abcf7553ed58138db15493044c0f34429b643286` | `tests/test_s1_failure_paths.py`: the T-07 nodes (29), green at BASE. Pushed; CI 40961801315 4/4. |
| B | `234874b60f7e96c85387df52e63a671d1fe7dcdf` | `tests/test_s1_force_context.py`: T-01…T-06 (57 nodes) plus A-1 T-04 (d)/(e) (4 nodes). The red-first ancestor; never a push tip (OD-3, I-50). |
| C | `fed74284119562f59724b270ed5de4f21e734506` | `src/tars/sim/forces.py`, `src/tars/sim/simulator.py`: exactly the `src/` hunks of the pinned `prototype-v3.patch`. |
| D | this commit | this directory only |

All records here were **recomputed for Commit D** in fresh clones of B and C (and of BASE, from
GitHub). They do not copy earlier results. Driver: `scripts/d_evidence.sh.txt`. Its phase-1 log is
`logs/summary.txt`.

## Results

| Gate | Record | Result |
|---|---|---|
| Red first (I-40 §9a), at B | `red_B/` | 61 failed and 29 passed. Every failure is a per-node `AttributeError: module 'tars.sim.forces' has no attribute …` (31 `ForceContext`, 30 `LegacyForceAdapter`); 0 collection errors; T-07 29/29 pass. The 4 A-1 nodes fail in `_record_contexts` (A-1 §2). Classification: `red_B/s1_classification.txt`. |
| Green, at C | `green_C/` | S1 90/90 pass. Full suite 1 380 passed (3 warnings, as at BASE). `ruff check` and `ruff format --check` exit 0. |
| Mutation (I-40 §10 + A-1 §3), at C | `mutation/` | Control 90/90. 25 mutants: 24 KILLED, each by its declared reason on the designated nodes; M-19 SURVIVED as the documented equivalent (v3-S §5.1), 0/90. **M-22 KILLED: all 4 designated nodes, by assertion.** Writer corpus: M-14 differs in 46 cases, M-19 in 0, as planned. `compare_with_pinned_s1v3.txt`: the 23 non-equivalent pinned mutants are identical to the I-44 campaign in verdict, counts and failing nodes. M-19 differs only in total nodes (86 → 90, the A-1 additions). |
| T-08 (INV-2, INV-4), BASE vs C | `t08/` | Main direct-API corpus: 26 880 cases, 0 differing; sha256 `e0309486…a814` for both trees. Writer corpus: 26 111 cases, 0 differing; `3310fd90…0415`. Custom-integrator corpus: 6 216 rows, **0 supported-kind differences**, 392 out-of-contract (`list` 196, object `None` 196) as disclosed in v3-S §6. All hashes equal the pinned I-44/I-45 references. |
| T-10 (§6, INV-8) | `t10_t11/ast_identity.txt` | 51 checks, 0 failures. |
| T-11 (§6) | `t10_t11/t11_changed_paths.txt` | BASE..C: the 4 allowlisted production and test paths. No protected path changed. D adds only this directory. |
| Validated scenarios, BASE vs C | `missions/missions.sha256` | All 5 output trees byte-identical (10 files). |
| Run records (I-40 §9) | `run_records/` | One per gate run, produced by `run_record.py`. |

R-1…R-4 run **at D** in fresh clones (I-40 §12 step 5), after this directory is fixed. Their results
are therefore recorded outside this commit, in the I-52 report and the external evidence. Commit E
would record them in the repository.

## Files

- `run_record.py`: the I-40 §9 S1 run-record script.
  - It was written at the I-40 execution on 2026-10-27, at this path, as the P-7 tool.
  - It was preserved untracked and unchanged through I-41…I-52, with sha256
    `435a2b7ef66f0d73bb7bee60f92f07247ab5a823cfb39dbe95481746db347353`, as recorded in the I-44 …
    I-50 decision records.
  - It is committed here byte for byte. It is a `.py` file and passes `ruff check` and
    `ruff format`. Pytest does not collect it (`testpaths = ["tests"]`).
- `scripts/` (`.py.txt` and `.sh.txt`, so CI does not lint them; copy one to run it):
  - `harness`, `harness_writers` and `ast_identity`: pinned `s1-proposal/` versions, unchanged;
  - `harness_integrators` and `compare_integrators`: pinned `s1-v3/` versions, unchanged;
  - `mutate`: the pinned `s1-v3/mutate.py.txt` plus three changes:
    - M-22 exactly as in A-1 §3;
    - A-1's rule that every M-22 designated node must fail;
    - the exact edits, results and pytest exit status recorded per mutant;
  - `classify_nodes`: the per-node red/green classifier;
  - `d_evidence.sh`: the driver.
- `mutation/`:
  - `mutation_results.json`: per mutant, the exact edits, designated nodes, declared reason pattern,
    per-node results, pytest exit status and verdict;
  - `mutation_summary.txt`;
  - `junit/`, `stdout/`;
  - `writer_corpus_mutants.txt`;
  - `compare_with_pinned_s1v3.txt`.
- `SCRUBBED.txt`: the files whose absolute local paths were replaced by `$SCRATCH` or `$HOME`, with
  their original sha256 values.
- `SHA256SUMS`: covers every other file in this directory.

**Kept externally** in `~/tars-evidence/I-52/`, with its `MANIFEST.sha256`:
- the corpus JSONL (210 MB; the hashes are in `t08/corpus_hashes.txt`);
- the mutant source trees;
- the mission output trees;
- the fresh clones' full logs.

The kill criterion is unchanged from I-40 §10. A mutant counts as KILLED only if a designated node
fails and every failure matches its declared reason, and every M-22 node must fail. A mutant whose
edit anchor does not occur exactly once aborts the campaign. A collection error or crash does not
match any reason pattern, so it cannot count as a kill.
