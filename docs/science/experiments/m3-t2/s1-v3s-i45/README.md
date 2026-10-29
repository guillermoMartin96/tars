# M3 T2 S1 proposal v3-S evidence, I-45 (contract verification, R-04, re-run)

This evidence supports `docs/milestones/M3-T2-S1-proposal-v3.md` (final v3-S revision) and
`docs/milestones/M3-T2-S1-decision-I45.md`. It adds to `../s1-v3/` (I-44) and does not replace it.

- **Nothing here is production code; S1 is NOT IMPLEMENTED.**
- The prototype is unchanged from I-44: `../s1-v3/prototype-v3.patch`, sha256
  `6199a6e644dac0988e4a14e9d56d40b2db5f5c77fba410af314360be5753731b`.
- Scripts are stored as `.py.txt` / `.sh.txt` so CI does not lint them; copy one to run it.
- Same host only: macOS x86_64, CPython 3.12.15, NumPy 2.5.3, `uv.lock` as at BASE. No
  cross-platform claim.

## Files

| File | What it is |
|---|---|
| `contract_verification.md` | I-45 §1: independent inspection of the `Integrator` protocol, `Derivative`, `Simulator`, layout docs, tests and guarantees. Result PASS, with C-1 (8 elements with a spacecraft; 6-element M1 path unchanged) and D-1 (stale `integrators.py` docstring, not edited). |
| `probe_r04.py.txt`, `probe_r04.txt` | Implementer's reproduction of Review 03 R-04: 2-D stages (1, 8), (8, 1), (2, 4), coast and burn, on BASE and v3-S. |
| `proposal-reviewed-vs-final.diff` | The text Review 03 reviewed vs the committed proposal: the R-04 correction, the writer-corpus count, the re-run note and the post-review status text. |
| `repro.sh.txt`, `regression_summary.txt` | Fresh-clone re-run of the I-44 regression script. The only change is the scratch commit message. Paths are scrubbed to `$SCRATCH` / `<tmp>`. |
| `corpus_hashes.txt`, `integrator_corpus_compare.txt`, `missions.sha256`, `ast_identity.txt` | Re-run outputs. All corpus and mission digests are identical to `../s1-v3/`. |

## Re-run (I-45 §4), BASE vs prototype

The re-run reproduced I-44 exactly.

- **S1 tests:**
  - prototype 86/86;
  - BASE: T-07 29/29 pass, T-01…T-06 57 fail (AttributeError, no collection errors).
- **Full suite:** BASE 1 290 passed; prototype 1 376 passed.
- **Corpora:**
  - main corpus: 26 880 cases, 0 differ (`e0309486…a814`);
  - option-A control: still differs in 964 cases;
  - stage-writer corpus: 26 111 cases, 0 differ (`3310fd90…0415`);
  - custom-integrator corpus: 6 216 rows, 0 supported rows differ; the 392 out-of-contract rows that
    differ are `list` 196 and object `None` 196.
- **Mutation:** control 86/86; 23 killed, each for its declared reason; M-19 survives 0/86. In the
  writer corpus, M-14 differs in 46 cases and M-19 in 0.
- **Proofs:** M1 PASS 9/9 steps and M2 PASS 20/20 steps, on both trees.
- **T1 (R-3):** r01 and r02 identical; 109 passed.
- **T0 (R-4):** 314 passed.
- **Scope:** T-10 51 checks, 0 failures; T-11 shows the 4 allowlisted paths.
- **Scenarios:** output trees byte-identical. Stdout differs only in the printed output path.

## External evidence

Kept in `~/projects/tars-evidence/I-45/`, with `MANIFEST.sha256` (sha256 in the decision record).
It holds the corpus JSONL files, logs, per-mutant trees and the Codex Review 03 scratch directory
(package, reviewer output, events). It excludes Python virtual environments and full fresh-clone
working trees, which are reproducible from BASE plus the patch.
