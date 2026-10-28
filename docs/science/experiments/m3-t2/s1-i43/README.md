# M3 T2 S1, I-43 lazy coast context investigation: evidence

Supports `docs/milestones/M3-T2-S1-I43-lazy-coast-investigation.md`. Scratch only; nothing here is
production code. Scripts are stored as `.py.txt` / `.sh.txt` (not linted by CI); copy to run.

Source trees used: BASE `ee602c5`; v2 = BASE + `../s1-proposal/prototype-v2.patch`;
v3-L = v2 + `v3L-vs-v2.patch`; v3-S = v2 + `v3S-vs-v2.patch`. Same host: macOS x86_64, CPython 3.12.15,
NumPy 2.5.3.

| File | What it is |
|---|---|
| `probe_i43.py.txt` | Part A (production-observable) and Part B (context semantics) probe. argv: tree root, output JSON. |
| `probe_{base,v2,v3L,v3S}.json` | Its outputs. |
| `probe_ooc.py.txt`, `probe_ooc.txt` | Extra out-of-contract controls (`list`, float32), all four trees. |
| `test_s1_r02_draft.py.txt`, `draft_tests.txt` | Draft T-07 (l) R-02 regression and T-04 snapshot tests, run on all four trees, with failure reasons. |
| `verify_variants.sh.txt`, `verify_variants.txt` | 78 v2 S1 tests and both corpora on v3-L and v3-S. |
| `corpus_hashes.txt` | sha256 of the v3-L/v3-S corpus outputs (equal to the BASE hashes in `../s1-proposal/README.md`). |

Corpus JSONL outputs (30–36 MB each) are kept externally: `~/projects/tars-evidence/I-43/`
(`MANIFEST.sha256`).
