# M3 T2 S1 I-46 evidence (owner decisions D1–D7, plan amendment A-1, plan review 01)

This evidence supports `docs/milestones/M3-T2-S1-decision-I45.md` §4–§5 and
`docs/milestones/M3-T2-S1-test-plan-amendment-I46.md`. It adds to `../s1-v3/` and `../s1-v3s-i45/`
and replaces neither.

- **Nothing here is production code or an implemented test. S1 is NOT IMPLEMENTED.**
- **No prototype, corpus, proof or mutation run was repeated for I-46.** The round changed
  documentation only. The design baseline (proposal v3-S, sha256 `dd705dd4…102d`) and prototype
  v3 (`../s1-v3/prototype-v3.patch`) are unchanged, so the I-45 results in `../s1-v3s-i45/` stand as
  recorded.
- The predictions in A-1 §4 are supported by plan review 01's throwaway probes. The probes are in
  `docs/reviews/raw/M3-T2-S1-plan-codex-review01-evidence/`, and they are not the planned tests.

| File | What it is |
|---|---|
| `baseline.txt` | I-46 work item 1. Recorded before commit: main and planning-branch refs on the remote, ancestry, S1 worktree state and the `run_record.py` sha256, the proposal pin, the I-45 manifests and CI on `b52f77c`. |
| `decision-reviewed-vs-final.diff` | The decision record as plan review 01 reviewed it, against the committed record. The only change is the N-02 correction in §4.3. |

External evidence is in `~/projects/tars-evidence/I-46/`, listed in `MANIFEST.sha256`. It holds the
Codex events log, the untrimmed reviewer directory with its copied trees, the review prompt and the
owner text.

Same host only (macOS x86_64, CPython 3.12.15, NumPy 2.5.3). No cross-platform claim.
