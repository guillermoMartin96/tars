# I-102 status: stopped for an owner decision on MI-03 (before BC2)

- Checkpoint verified (`checkpoint/checkpoint.txt`). The I-99, I-100 and I-101 manifests verify. The worktree has one uncommitted correction to `tests/test_s2_geodetic.py`. D does not exist.
- The I-101 campaign (`~/tars-evidence/I-101/commit-d/out/mutation/`) is preserved unchanged. It is recorded as INCOMPLETE because MN-17 did not meet the counting rule.
- Test correction frozen: blob 0d817de456cf837c06979a5fab601db6be7b6567, sha256 9059ff375993cf156e28fb76b5a3eb95a3601ea99c3572890cc1c1033fa8b661 (`frozen/`).
- Supplemental red run (`supp-red/`), on a fresh clone of A with `geodesy.py` absent and `constants.py` = K:
  - 112 nodes: 100 fail with ImportError, 2 fail by assertion (G-09, G-11), 10 guards pass (G-10 W1–W7, G-13 ×3);
  - none not-OK;
  - identical per node to the original red run.
- Corrected campaign plus full gates (`campaign/`), on BC with the frozen test installed (blob verified):
  - control: 74 nodes pass;
  - 49 mutants: 44 KILLED, 5 documented equivalents, NOT OK [];
  - MN-17 KILLED by an assertion in `test_g06_float_subclass_overrides_never_run`; the `__abs__` node passes;
  - ruff check 0, ruff format 0, pytest 1 518 passed, exit 0.
- STOP: MI-03 is killed only at the (nan, 0, 0) row. v11 designates (inf, 0, 0), which cannot kill it. See `MI-03-DESIGNATION.md` for the proposed change.
- Not done: BC2 commit, push, CI, D, regression, E.
