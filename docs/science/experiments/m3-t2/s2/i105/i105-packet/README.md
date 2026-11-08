# I-105 correction packet (addresses I-104; nothing committed or pushed)

The instruction is quoted verbatim in `I-105.md`.

| What | Where |
|---|---|
| Finding-by-finding response, and the impact of each correction on I-104's 26 MET rows | `RESPONSE.md` |
| Exact local diff and affected paths (base E `495590033ddc0456b2b93ce08700152fae5a3123`) | `diff/tracked.diff`, `diff/untracked-ERRATUM.diff`, `diff/affected-paths.txt`, `diff/git-status-porcelain.txt` |
| Frozen test bytes (taken before any red or green execution) | `frozen/` |
| Pre-edit checkpoint: the I-104 manifest; the I-101 to I-103 manifests; local and remote state | `checkpoint/` |
| New validation evidence, with full hashes | `REPLACEMENT-EXECUTIONS.md`; the directories `red/`, `green/`, `host-report/`, `derivation/` and `campaign/` |
| Final worktree checks (ruff, G-13 working-tree scope, report prefix, erratum copy timing) | `final-worktree-checks/` |
| Environment classification of all CI and host G-17b records (I104-03) | `comparison/environment-table.json`, `comparison/host-records/` |
| Historical schema-1 host census, extracted only for the projection comparison | `comparison/historical-schema1/` |
| Historical-gap inventory and the proposed owner disposition (I104-02) | `gap/` |
| Proposed commit and push sequence, including the CI evidence the corrected emitter needs | `PROPOSED-COMMIT-PUSH-SEQUENCE.md` |
| Scripts | `scripts/` |
| Clone identities (the clones are not sealed) | `clone-inventory.txt` |

**Manifest.** `MANIFEST.sha256` covers everything here except:
- `clone-a-red/` and `clone-candidate/`, the disposable clones, which also hold their `.venv` and
  `.git`;
- `__pycache__/`;
- the manifest itself, which has a detached digest in `MANIFEST.sha256.digest`.
