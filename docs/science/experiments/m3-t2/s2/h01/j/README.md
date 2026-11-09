# S2 H-01 commit J: commit, push, own CI, and clean committed-tip validation

**AUTHOR EVIDENCE.** This is not independent review evidence. H-01 stays OPEN pending independent review.
OB-11 and OB-27 are not marked MET. No K2 or L was created, the report was not appended, no review was
launched, S2 is not accepted and nothing was merged. H's independent review, ledger (29 MET, OB-11/OB-27
FAILED, OB-30/OB-31 later-scope PENDING) and I-104 dispositions are unchanged.

- `AUTHORIZATION.md`: the owner's authorization, verbatim.
- `final-state.txt`: the worktree, remote and preservation state at the end.

## 1. Preconditions (`preconditions/`)

`preconditions/preconditions.txt` (2026-11-09T04:12:01Z) records:
- the S2-H01-correction manifest `b0ea7050…e584`, 795/795 OK, and six other evidence manifests unchanged;
- branch `milestone-3-t2-s2-geodetic`; local HEAD, local origin ref and **actual remote tip**
  (`git ls-remote`, remote `https://github.com/guillermoMartin96/tars.git`) all at H `8074a19b…`;
- only `src/tars/sim/geodesy.py` and `tests/test_s2_geodetic.py` modified, nothing staged, no stash;
- both files byte-equal to the packet's executed copies, and `git diff` byte-equal to
  `diff/H01-correction.diff`.

## 2. J (`j/`)

- **J:** `42ec8d6170447429ec1be8208f71cb4ee5512496`
- **Sole parent:** H `8074a19bf33cf5b6d20f7d211ff44f82bf28ba93`
- **Tree:** `b5b9e928d4203ea82ea5178be945490ce705a1d8` (equals the required tree; the staged tree was
  checked before committing)
- **Blobs:** `geodesy.py` `82ca9aaab0ed63ca63a8c9ff29f6a1425a2769cb`; `test_s2_geodetic.py`
  `d68c7a7d1645068a34a6c430b98845beb26e9f65`
- **Diff:** `j/j.diff` (H..J) is byte-identical to the correction packet's `diff/H01-correction.diff`.
- **Message:** `j/commit-message.txt`; commit object `j/j-commit-object.txt`.
- **Worktree clean** after the commit (`j/j-identity.txt`).

**Push** (`j/push.txt`): remote tip re-checked at H, then
`git push --porcelain origin refs/heads/milestone-3-t2-s2-geodetic:refs/heads/milestone-3-t2-s2-geodetic`.
Fast-forward `8074a19..42ec8d6`, exit 0; the remote tip is J afterwards. No force, rebase, amend or other
commit.

## 3. J's CI (`ci/ci-J-42560535876/`)

Collected with I-106 `ci_collect.sh` (unchanged; raw job logs from the GitHub API, not modified).
- **Run** 42560535876, workflow `ci`, event push, **attempt 1**, head SHA J, conclusion **success**.
  Created 04:12:45Z, updated 05:04:42Z.
- **Jobs (all attempt 1, head J, all steps succeeded):** check (ubuntu-latest) 19/19, check (macos-latest)
  19/19, check (macos-15-intel) 19/19, m2-cross-platform 10/10. `run-check.json` ok = true.
- **Test totals:** 1,518 passed and 3 skipped on each check job (H: 1,517 passed, 3 skipped). The S2 test
  file's progress lines contain no F, E or s. CI runs pytest without `-v`, so the H-01 node is not named
  in CI logs; it is named and passing in the local runs (section 4).
- **Records**, per check job (`records/`, `validation/`, `summary.stdout`): extraction complete; ENV
  records carry `GITHUB_SHA` = J and `GITHUB_RUN_ATTEMPT` 1; schema-2 census valid against the frozen
  listing (22,665 entries; 19,154 accepted, 64 evolute_region, 3,447 non_convergence); **G-17b 8,853
  Class X compared, 0 differences** (environment kind `other`); G-17a Class X differences 0, label
  differences 0, witness failures 0.
- **Class P differences (report-only, not gates):** ubuntu 2,305, macos-latest (arm64) 2,188,
  macos-15-intel 0. These are the same counts as at H.
- **RP-8 / RP-9** (`rp8-rp9/`, committed `rp8_rp9_ci.py`, byte-identical copy): 0 outcome differences
  between every pair; iteration-count differences 18 / 24 / 10. Listing body hashes equal G's on all three
  platforms. Report-only.
  - Attempt 1 of this script failed because of my invocation (all arguments passed as one word in zsh).
    Its output is kept as `rp8-rp9/attempt1-invocation-error.stdout` with a note.

## 4. Clean committed-tip validation (offline, network denied by `sandbox-exec`)

Commands: `regression-commands.txt`. Every clone is a fresh `--no-local --no-hardlinks` clone of the
local repository, checked out detached at exact J (or K), with nothing copied in, and verified
HEAD = J, tree = `b5b9e928…`, no alternates, empty status. uv 0.12.23 `sync --locked --offline`.

**H-01 node at J** (`h01-node-at-J/`, `scripts/j_h01_node.sh`): the node plus the nine recorders in one
process. pytest exit 0, **10 passed**; `PASSED tests/test_s2_geodetic.py::test_g06_h01_…`. The run record
shows commit J and an empty status; the ENV, G-17a and G-17b records are complete (G-17b 8,853, 0
differences, `generation`); the census validates (sha `485fac74…`).

**Regression** (`regression/`, `scripts/j_rgates.sh`; its diff from the H-01 driver is
`scripts/h01_rgates-to-j_rgates.diff`: only clone creation changed, and the R-2 block is unchanged). K
`83d573bd…` was recomputed in fresh clones.
- **R-1:** M1 proof PASS at J and at K; golden `7a4e1877…` present in both.
- **R-2:** M2 proof PASS at both, 228 [PASS] and 0 [FAIL] each. **The original comparison, unchanged:
  differing keys `revision` and `sha256` only; record sha256 with K's revision substituted equals K's:
  `True`.** Recorded provenance: J `42ec8d61…` with `tree_clean` True; K `83d573bd…` with `tree_clean`
  True. Proof wrappers report `working_tree_clean_excluding_evidence: yes`. No `tree_clean` substitution
  was used.
- **R-3:** r01 and r02 correction outputs byte-identical between J and K, and equal to the committed
  results. T1 tests: 110 passed at J, 109 at K (the difference is the new H-01 node).
- **R-4:** 314 passed at both.
- **R-S1:** 100 passed; the S1 SHA256SUMS file verifies (the only non-OK line is the appended exit line).
- **R-S2:** full suite at J, **1,521 passed**, 0 failures, errors or skips (JUnit), 7 warnings (same as
  H). The H-01 testcase is present and passed. Records extracted, census valid (`485fac74…`), G-17b 8,853,
  0 differences.
- ruff check exit 0; ruff format: 302 files already formatted.
- **Run records:** 7 §3.16 run records and 7 direct DL-5 ENV probes, all exit 0. Every J record shows
  commit J and an empty status. The I-106 exception is not used for any of them.

## 5. Earlier evidence bound to J (`BINDING-EARLIER-EVIDENCE-TO-J.txt`)

The correction packet's green-executed `geodesy.py` and red/green-executed test file are byte-identical
to J's committed blobs. The packet's candidate tree equals J's tree, and its mutation campaign ran on
copies of that candidate `src`. **Those executions ran uncommitted candidate bytes on top of H; they are
not runs at J.**

## 6. Limitations

- The mutation campaign and red/green were not re-executed at J; only bound by bytes (section 5).
- The commit-D derivation (OB-02/OB-19) was not rerun; it does not involve the changed component.
- CI logs do not name individual nodes; per-node evidence at J is local (host, macOS x86_64).
- Matching ENV proxy fields do not certify an identical library or build environment (r83:83).
- K2 (evidence commit) and L (report append) do not exist; the repository records nothing about J yet.
- Independent review of J has not happened; H-01, OB-11 and OB-27 remain open/FAILED as at H.
- POG remains BLOCKED; A-FP-2 remains unaccepted; OB-30/OB-31 remain later-scope PENDING.

## 7. Manifest

`MANIFEST.sha256` covers every file in this directory except itself. Scratch clones and virtual
environments are under the session scratchpad and are not included.
