# Proposed commit and push sequence, for later owner authorization only

**Nothing here is authorized or performed.** The worktree is left uncommitted and unpushed at H. The
proposal follows the F → G → H discipline that the owner has already used:
- each commit is pushed alone, onto `milestone-3-t2-s2-geodetic`;
- the sequence waits for CI 4/4 `success` on each commit before the next;
- there is no amend, rebase, force-push, CI rerun or fix-forward after a failed CI without a new owner
  instruction;
- it stops at a CI-green tip and prepares, but does not launch, an independent re-review.

## Why the red test is not pushed as its own commit

OB-18 requires CI 4/4 `success` on **every pushed commit**. A commit containing only the new test would
fail CI by design. Red-before-green is therefore established locally and bound by blob identity, as in the
D-S2-12 (i) precedent:
- the red execution ran H's component blob `e409e26341ec40a0adf8123e5ea47d5fc9788d9d` with the new test
  blob `d68c7a7d1645068a34a6c430b98845beb26e9f65`;
- the green execution ran the same test blob with the corrected component blob
  `82ca9aaab0ed63ca63a8c9ff29f6a1425a2769cb`;
- see `red-green/classification.json`.

## Sequence

### J: the correction (code)

- **Content:** exactly the two uncommitted files, `src/tars/sim/geodesy.py` and
  `tests/test_s2_geodetic.py`, as they are in the worktree now (see `diff/`).
- **Parent:** H `8074a19bf33cf5b6d20f7d211ff44f82bf28ba93`.
- **Required tree:** `b5b9e928d4203ea82ea5178be945490ce705a1d8`, recorded in
  `candidate/candidate-tree.txt` (computed with a temporary index in a disposable clone, with no commit).
  Before pushing, `git rev-parse HEAD^{tree}` must equal it, and the blobs must be `82ca9aaa…` for
  `geodesy.py` and `d68c7a7d…` for the test file. A mismatch means the committed bytes are not the
  validated bytes: stop.
- **Message:** `fix(M3-T2-S2): unsupported-type rejection reads no caller class attribute (H-01)`, with a
  body citing the review, v11 §3.8 step 0 and the red/green blob binding.
- **Push:** push J alone, then wait for CI 4/4 on J.
- **Then:** collect and archive the CI raw logs and listings as F/G/H were collected.
  - Validate the platform ENV, listing, G-17a and G-17b records.
  - Validate the RP-8 and RP-9 three-platform listings, which are new for J.
  - Run R-1 to R-4, R-S1 and R-S2 at pushed J against K, recomputed. These would be new runs. This
    packet's runs are on the identical uncommitted bytes and do not replace them.

### K2: the correction evidence (docs only)

- **Content:** a new directory `docs/science/experiments/m3-t2/s2/h01/` holding:
  - this packet's red/green records;
  - the candidate validation, campaign summary and regression summary;
  - J's CI records and their verification;
  - a `SHA256SUMS` file.
- **Path check:** the G-13 allowlist already admits paths under `docs/science/experiments/m3-t2/s2/`.
- **Exclusions:** scratch clones and virtual environments are excluded, and no historical file is
  edited.
- **Push:** push K2 alone, then wait for CI 4/4 on K2.

### L: the report append (docs only)

- **Content:** append `### S2.15 Correction record after the H re-review (H-01)` to
  `docs/milestones/M3-T2-report.md`. The append records:
  - the finding;
  - the one-statement change;
  - the red/green binding;
  - the validation;
  - the unchanged ledger standing at H.
- **What it must not do:** it must not mark OB-11 or OB-27 MET, and it must not claim acceptance.
- **Prefix rule:** H's report bytes remain an exact prefix (R-7, append-only).
- **Push:** push L alone, then wait for CI 4/4 on L. Stop at the CI-green L.

### Then

- Prepare, but do not launch, a corrected-tip re-review handoff scoped to:
  - closure of H-01 (OB-11 and the consequent OB-27);
  - the new G-06 node;
  - the J/K2/L CI and record evidence;
  - the regenerated regression and campaign evidence.
- That handoff preserves the H review's I-104 dispositions and the I-106 exception scope as fixed
  history.
- Acceptance and merge remain unauthorized until the owner decides otherwise.

## Alternative

J and L could be folded into a single code+report commit to shorten the sequence. That would mix code with
documentation that cites J's own CI. The three-commit form keeps each commit's evidence self-consistent,
as F/G/H did, so it is the recommended form.
