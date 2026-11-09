Authorize the H-01 correction commit J only, its push, its own CI observation, and clean committed-tip validation. Do not create K2 or L yet.

PRECONDITIONS

Verify the correction packet:
`$HOME/tars-evidence/S2-H01-correction/`

Its MANIFEST.sha256 must hash to:
`b0ea705039b483359886a77b44911eb6117c1a5775ed5b86b5eef7c0d895e584`

Verify every entry. Read the proposed sequence and applicable governing instructions.

Confirm:
- Branch: milestone-3-t2-s2-geodetic.
- Local HEAD and actual remote branch tip are H:
  `8074a19bf33cf5b6d20f7d211ff44f82bf28ba93`
- Only these two working files differ:
  `src/tars/sim/geodesy.py`
  `tests/test_s2_geodetic.py`
- Their contents match the validated correction packet exactly.
- Existing evidence manifests remain unchanged.

Network is authorized only for checking the target remote identity, pushing J, and observing/downloading J’s own CI evidence. No dependency downloads or unrelated network activity.

Stop on a precondition mismatch. Do not reset or overwrite unexpected changes.

CREATE J

Stage and commit exactly the two corrected files, with H as its sole parent.

Required tree:
`b5b9e928d4203ea82ea5178be945490ce705a1d8`

Required blobs:
- geodesy.py:
  `82ca9aaab0ed63ca63a8c9ff29f6a1425a2769cb`
- test_s2_geodetic.py:
  `d68c7a7d1645068a34a6c430b98845beb26e9f65`

Verify the committed parent, tree, blobs, exact diff, and clean worktree before pushing. Stop on any mismatch; do not amend.

Commit message:
`fix(M3-T2-S2): unsupported-type rejection reads no caller class attribute (H-01)`

Include a body citing the independent H review, v11 §3.8 step 0, and the exact red/green source/test bindings.

Push J alone using a normal fast-forward push. No force-push, rebase, amend, or additional commit.

CI AND CLEAN-TIP VALIDATION

Observe J’s own CI run and archive its raw logs, identities, attempts, job results, and required records.

Require all four jobs to succeed on exact J. Validate each platform’s ENV, schema-2 listing, G-17a, G-17b, and applicable RP-8/RP-9 records. Preserve Class P differences as report-only.

If CI fails, stop after recording the failure. Do not rerun CI or fix forward.

After CI succeeds, use fresh detached no-hardlink scratch clones of exact J for the required clean committed-tip checks. Use offline locked uv setup and locally cached dependencies.

Run R-1 through R-4, R-S1, and R-S2 against freshly recomputed K:
`83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`

Run the original R-2 comparison unchanged. It must succeed with clean committed provenance; do not substitute tree_clean or weaken the comparison. Record the actual provenance and investigate any unexpected dirty state without relabelling the check.

Confirm the H-01 regression passes on exact J. Bind the earlier author mutation campaign and red/green evidence to J’s exact source/test bytes; do not describe those earlier executions as runs at J.

Satisfy all applicable new run-record and ENV/DL-5 duties. The I-106 historical exception does not cover new runs.

EVIDENCE AND STOP

Write a new additive execution packet under:
`$HOME/tars-evidence/S2-H01-J/`

Preserve all existing evidence and record:
- this authorization;
- preconditions and actual remote identity;
- full J SHA, parent, tree, blobs, and diff;
- push result;
- J CI provenance, raw evidence, and record validation;
- clean-tip regression commands, results, and direct environment records;
- preservation checks;
- hashes and a verified manifest.

Do not create K2/L, append the report, launch another review, close H-01, mark OB-11/OB-27 MET, accept S2, or merge.

H’s historical review and ledger remain unchanged. Preserve all existing scientific boundaries and later-scope PENDING obligations.

Stop after reporting J’s exact identity, CI result, clean-tip validation results, remaining limitations, worktree status, and evidence manifest hash.
