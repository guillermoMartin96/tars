# M3 T2 S1 proposal v3 (v3-S) evidence (I-44)

Supports `docs/milestones/M3-T2-S1-proposal-v3.md` (DRAFT, not reviewed; stopped on I44-Q1).
**Nothing here is production code; S1 is NOT IMPLEMENTED.** Scripts are stored as `.py.txt` /
`.sh.txt` (not linted by CI); copy to run. Same host only: macOS x86_64, CPython 3.12.15,
NumPy 2.5.3, uv.lock as at BASE; no cross-platform claim.

Trees: BASE `ee602c5`; v2 = BASE + `../s1-proposal/prototype-v2.patch`; v3-L = v2 +
`../s1-i43/v3L-vs-v2.patch`; **v3 (v3-S) = BASE + `prototype-v3.patch`** (sha256 `6199a6e644dac0988e4a14e9d56d40b2db5f5c77fba410af314360be5753731b`).

| File | What it is |
|---|---|
| `prototype-v3.patch` | Prototype v3 relative to BASE: the 4 allowlisted paths; adds T-07 (l) and the T-04 snapshot tests (86 S1 tests). |
| `discrimination.txt`, `discrimination_reasons.txt` | The 8 new nodes on BASE, v2, v3-L, v3-S with failure reasons (run from the scratch prototype clone with `PYTHONPATH` set to each tree). |
| `harness_integrators.py.txt`, `compare_integrators.py.txt`, `integrator_corpus_compare.txt` | Custom-integrator corpus (6 216 runs) and its comparison of v2, v3-L, v3-S against BASE. |
| `probe_i44.py.txt`, `probe_{base,v2,v3L,v3S}.json`, `summarize_probe.py.txt`, `probe_summary.txt` | Part A (observable) / Part B (context snapshot semantics) probe, 14 cases (I-43 probe extended). |
| `probe_shapes.py.txt`, `probe_shapes.txt` | Wrong-shape float64 stages (size 6, 2-D, size 10), coast and burn: the I44-Q1 evidence. |
| `mutate.py.txt`, `mutation_summary.txt`, `mutation_results.json` | Mutation campaign (24 mutants; verdict requires every failure to match the declared reason). Fresh-clone run. |
| `repro.sh.txt`, `regression_summary.txt` | Fresh-clone regression (derived from I-42 `repro.sh`, with the missions directory fix and the integrator corpus). Paths scrubbed to `$SCRATCH` / `<tmp>`. |
| `ast_identity.txt`, `missions.sha256`, `corpus_hashes.txt` | T-10 output, scenario output hashes (BASE and prototype), corpus hashes. |

The harness, writer-corpus and AST scripts used are `../s1-proposal/{harness,harness_writers,ast_identity}.py.txt`, unchanged.

Corpus JSONL (5–36 MB), fresh clones' logs and per-mutant trees are kept externally:
`~/projects/tars-evidence/I-44/`: `MANIFEST.sha256` sha256 `92506084ebaebdfae4b9236fb982e8c11efa137944524994bfd667d802f87e1e` (2 022 files; includes `proto-v3.bundle`, the scratch prototype commit).

Note on the integrator corpus: the first run had a defect in the `object_none` wrapper (it did not
write `None`); fixed and rerun before any result here was recorded. All recorded outputs are from
the corrected script.
