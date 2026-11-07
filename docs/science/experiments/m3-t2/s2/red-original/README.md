# S2 red run (D-S2-12 (i); v11 §3.14 step 2), uncommitted, on top of commit A 6c05e53

- `record_red_run.sh` ran with `geodesy.py` absent and `constants.py` at K (`absence-proof.txt`).
- `git-status-porcelain.txt`: the 3 changed test files. `test-file-identities.txt`: their git blob ids and sha256. These are bound to commit BC (stop 14 if a blob differs).
- `red-pytest.log` (unfiltered, `-v -rA`), `red-junit.xml`, `red-pytest.exit` (1).
- `classify_red.py` writes `red-classification.json`: 131 nodes.
  - 101 fail with a per-test ImportError (absent interface).
  - 4 fail by assertion (G-11, G-12b, G-09 architecture node, the new 1/f literal-location function).
  - 26 pass: guards (G-10, G-13, G-12a, twin sanity) and the unchanged pre-existing test_constants tests.
  - No collection error, and no node fails for an undeclared reason.
- **Draft provenance.** The test files were copied from drafts RECREATED on 2026-11-06 (`draft-identities-before-copy.txt`). They are new working material, not recovered originals.
  - `test_constants.py` and `test_s2_geodetic.py` are byte-identical to their drafts.
  - `test_s2_geodetic_conformance.py` differs from its draft only by ruff's import-order fix (I001), applied before recording.
