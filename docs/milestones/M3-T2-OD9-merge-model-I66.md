# M3 T2: OD-9 record (merge model) and S1 merge record (I-66, I-66A, I-66B)

- **Status:** APPROVED for local recording under owner instruction I-68 (2026-11-03). This version
  supersedes the earlier uncommitted OD-9 drafts preserved in the I-66, I-66A and I-66B evidence.
  Remote publication remains pending separate owner authorization.
- **State of the two records when this draft was prepared (I-67):**
  - The I-65 acceptance record, `docs/milestones/M3-T2-S1-acceptance-I65.md` (sha256
    `0af1ed97226e090cfbd8717fdf2c924d2f88a564c7bd01c2ad2dcb91b882d594`), was **committed locally**
    as `2512e1ce481f8abc3dc964220920ee82d313a9d5` on local branch `m3-t2-s1-acceptance-i65`. Its
    parent is the planning tip `5714959a94bcb8de1533a56ff9e28db10c2920ac`. It had **not** been
    pushed.
  - This OD-9 record was an **uncommitted** draft.
  - Publication of both was **pending** owner authorization. Neither had been pushed.
- **Proposed path:** `docs/milestones/M3-T2-OD9-merge-model-I66.md`, a new file, committed with
  parent `2512e1ce481f8abc3dc964220920ee82d313a9d5` on the planning line
  (`milestone-3-t2-authorization`), next to the OD-7 record (`M3-T2-S1-OD7-I30-section4-record.md`).
  It is not proposed for `main` or for the S1 branch. Publishing to the planning branch leaves this
  record and the acceptance record outside `main`.
- **S1 state recorded here:** S1 was accepted at K `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`
  (I-65). It was merged into `main` at K (I-66). Post-merge CI on `main` succeeded (run
  `41672716486`, attempt 3, I-66B), and post-merge fresh-clone validation passed (I-66B). This
  concerns S1 only: **T2 is not accepted**, and PC-7 for T2 overall remains **NONE**.
- **Purpose:** I-40 §2 defers OD-9 and requires it to be resolved before S2. I-66 decides OD-9. This
  record writes that decision down, and keeps four things apart that must not be confused:
  1. the **S1 merge authorization** (a one-time act, §2);
  2. the **general slice-by-slice merge model** (the OD-9 answer, §4);
  3. the rule that **later slices need their own acceptance and merge authorization** (§4.2);
  4. the fact that **S2 implementation remains unauthorized** (§5).
- **Not edited:**
  - `M3-T2-S1-authorization.md` (I-40, sha256
    `1b6bc40cf657a9995211462d437794a91df3f345df88dba9d986b3a1d07b78c6`);
  - `M3-T2-implementation-authorization-packet.md` (revision 2, sha256
    `641c278eaa8cb3b934e5593f595f161b8605c64ac1cfe3fc77760756ed27a929`);
  - the pinned S1 proposal `M3-T2-S1-proposal-v3.md` (sha256
    `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`);
  - the I-65 acceptance record (sha256 above);
  - `docs/milestones/M3-T2-report.md` at K (sha256
    `f3969d51da6ff9720866e95bf45660a4d58d265b079343cbb3bbc18384554180`).

  The OD-9 row in I-40 §2 stays as written; this record answers it without changing it. §3 lists the
  historical statements this record supersedes; their files are not edited.
- **Scope:** documentation only. No production code, test, CI, dependency, scenario or proof file is
  changed.

## 1. The owner texts, verbatim excerpts

The lines between each pair of fence lines are copied exactly from the owner instruction named above
the block. They are not rewrapped. The full instructions are kept in the external evidence:

- I-66: `~/tars-evidence/I-66/I-66.md`, sha256
  `d28d81577adfd3f842cb8b637edca3fe7013f0ab6fe31cd6c07460866c210265`;
- I-66A: `~/tars-evidence/I-66A/I-66A.md`, sha256
  `83c3b1b3e1860d21e798eebc0c8b9a1adf73afe23a32f22aef97691cad058078`;
- I-66B: `~/tars-evidence/I-66B/I-66B.md`, sha256
  `45032213cfdc8bb478f786ae9916c140dfb6aa9f4b8e09a003fc2720408c0489`.

### 1.1 I-66, "Owner authorization" section (S1 merge and OD-9)

````text
I authorize the controlled fast-forward merge of the accepted M3 T2 S1 implementation into main.

Accepted source:

`83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`

Destination:

`main`, currently at BASE `ee602c5`

Owner decision on OD-9:

Select the slice-by-slice merge model: an independently accepted T2 slice may be merged into main after satisfying its governing acceptance criteria and receiving explicit owner merge authorization.

This decision applies to S1. It does not automatically authorize acceptance or merging of subsequent slices.
````

### 1.2 I-66A, "Owner authorization" section (CI recovery, attempt 2)

````text
Authorize Option (a): rerun only the failed jobs from GitHub Actions workflow run:

`41672716486`

Target:

- Branch: main
- Commit: `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`
- Original failed jobs: macOS arm64 and M2 cross-platform proof

The rerun must use the same commit and workflow configuration.

No code changes, commits, pushes, merges, rebases, force-pushes or reversions are authorized.
````

### 1.3 I-66B, "Owner authorization" section (CI recovery, attempt 3)

````text
Authorize exactly one additional failed-jobs rerun of GitHub Actions workflow:

`41672716486`

Target commit:

`83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`

Branch: `main`

Wait at least 3 hours after the completion of attempt 2 before triggering attempt 3.

This delay is an operational retry strategy, not a guarantee of GitHub runner availability.

No repository modifications are authorized.
````

### 1.4 The OD-9 question as deferred by I-40 §2 (verbatim row)

````text
| **OD-9** | Merge model: each slice merged to `main` after acceptance, or all slices stacked until T2 acceptance | S2 |
````

## 2. The S1 merge (one-time act)

### 2.1 Authorization and conditions

- **Authorized by:** I-66 (owner, 2026-11-03), §1.1.
- **What:** fast-forward of `main` from BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` to K
  `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`.
- **Basis:** S1 accepted at K (I-65); independent closure review PASS with 0 findings (I-64); CI run
  `41538766579` 4/4 success at K on the S1 branch.
- **Conditions (I-40 §15):** "Any merge needs a separate authorization: fast-forward only, ordinary
  push, pre-merge ancestry check, post-merge fresh-clone validation, and CI on `main` green."

### 2.2 Merge and push

Times are UTC on 2026-11-03. Each time is labelled with what it measures.

- **16:17:40Z:** start of the I-66 §3 procedure (final clean-worktree, ref and ancestry checks),
  as recorded in `~/tars-evidence/I-66/merge_push.txt`.
- **16:17:41Z:** local `main` fast-forwarded, as recorded by the local reflog:
  `main@{2026-11-03T16:17:41Z}: merge 83d573bdb4933f5d2376423d6b8e9f3348a4ab6f: Fast-forward`.
- **Push:** `git push origin main`, an ordinary push without force. Output:
  `ee602c5..83d573b  main -> main`.
- **16:17:46Z:** end of the post-push verification (local, tracking and remote `main` all equal to
  K), as recorded in `merge_push.txt`. This is when the verification finished, not when the server
  received the push.
- **16:17:47Z:** GitHub created run `41672716486` (attempt 1) for the push (`created_at`).
- **Result:** `main` HEAD is K, tree `03e01038bf9b84060a8a7d7b126dfa225cb9f513`, the reviewed K
  tree. No merge commit was created; BASE..K is 10 linear commits.

### 2.3 Post-merge CI on `main`

Run `41672716486`: workflow `ci` (`.github/workflows/ci.yml`, blob
`9d3908ab7cdcd8aeecc1b6bd3f0dde49daef44aa`, unchanged between BASE and K), event `push`, branch
`main`, head K. For each attempt, "created" is GitHub's `created_at` and "completed" is its
`updated_at` once the attempt had concluded.

- **Attempt 1:** created 16:17:47Z, completed 17:26:31Z. Conclusion **failure**.
  - `check (ubuntu-latest)` job `126045045979`: success; `1387 passed, 3 skipped, 3 warnings`.
  - `check (macos-15-intel)` job `126045045312`: success; `1387 passed, 3 skipped, 3 warnings`.
  - `check (macos-latest)` (arm64) job `126045045754`: cancelled with no runner and 0 steps.
    GitHub annotation: "The job was not acquired by Runner of type hosted even after multiple
    attempts".
  - `m2-cross-platform` job `126085539043`: failure, because the arm64 evidence was missing:
    `runs/xp-in/macos-latest.json: not a JSON object`.
- **Attempt 2 (I-66A):** command `gh run rerun 41672716486 -R guillermoMartin96/tars --failed`,
  recorded at 17:37:28Z just before it was issued. Created 17:37:31Z, completed 17:52:57Z.
  Conclusion **failure**. The arm64 job `126091969560` was again cancelled with the same annotation,
  and `m2-cross-platform` job `126100243921` failed with the same missing-file message.
- **Wait (I-66B):** 10 942 s (3 h 2 min) elapsed between the completion of attempt 2 (17:52:57Z) and
  the I-66B precondition check (20:55:19Z). I-66B requires at least 3 hours.
- **Attempt 3 (I-66B):** the same command, recorded at 20:55:30Z just before it was issued. Created
  20:55:33Z, completed 21:29:57Z. Conclusion **success**.
  - `check (macos-latest)` (arm64) job `126199692658`: executed 20:55:50Z to 21:29:30Z on runner
    `GitHub Actions 1000001376`, image `macos-26-arm64` version `20261026.0455.2`, CPU
    `Apple M1 (Virtual)`. Every step succeeded: lint; tests `1387 passed, 3 skipped, 2 warnings`;
    M1 Proof and M2 Proof, each `thresholds: approved; overall: PASS`.
  - `m2-cross-platform` job `126217835492`: executed 21:29:32Z to 21:29:56Z. It downloaded evidence
    from all three platforms and ran the command below. The command and the three output lines are
    copied verbatim from the job log and are not rewrapped.

    ```text
    uv run python toolbox/validators/m2_cross_platform.py gate runs/xp-in/macos-15-intel.json runs/xp-in/ubuntu-latest.json runs/xp-in/macos-latest.json --revision "83d573bdb4933f5d2376423d6b8e9f3348a4ab6f" --run-id "41672716486" --report runs/proof/m2_cross_platform.json
    ```

    ```text
    [PASS] m2_cross_platform: final_position_difference_m=7.23205e-06, final_velocity_difference_mps=8.42869e-09
    [PASS] m2_cross_platform_evidence: violations=0
    overall: PASS
    ```

    The approved thresholds in the gate report are `final_position_difference_m` 0.0001 and
    `final_velocity_difference_mps` 1e-07. They were not changed.
  - `check (ubuntu-latest)` job `126199684323` and `check (macos-15-intel)` job `126199652870`:
    success. These are the attempt-1 results, which GitHub carries over when it reruns only failed
    jobs. Those two jobs were not executed again.
- **CPython in CI:** 3.12.3 on Ubuntu (both the check and the M2 gate job); 3.12.10 on macOS Intel
  and on macOS arm64.
- **Result:** GitHub reports the overall conclusion of run `41672716486` as **success**, with 4/4
  jobs at head K. Attempts 1 and 2 remain in the run history as failures. The cause of both was
  runner provisioning for the arm64 job; no test or numerical check failed.

### 2.4 Post-merge fresh-clone validation (I-66B §5, resuming I-66 §5)

The run started at 21:32:20Z and its result was recorded at 22:04:22Z.

- **Host:** macOS 26.2 x86_64; uv 0.12.23; CPython 3.12.15, numpy 2.5.3, scipy 1.18.1. CPython
  3.12.15 differs from CI's 3.12.3 and 3.12.10.
- **Ref and tree:** a fresh clone from GitHub gave `main` HEAD = K and tree
  `03e01038bf9b84060a8a7d7b126dfa225cb9f513`.
- **Evidence manifests:** the D, I-59 and S1C-03 manifests verify, with 96, 154 and 32 entries and
  0 failures.
- **Environment and tests:**
  - `uv sync --locked` succeeded.
  - Full test suite: `1390 passed, 3 warnings in 1894.69s (0:31:34)`. GMAT R2026a is installed on
    this host, so the 3 GMAT tests that CI skips were executed.
  - `ruff check`: "All checks passed!".
  - `ruff format --check`: "274 files already formatted".
- **Tracked changes:** none after all steps.
- **Result:** PASS.

### 2.5 Conditions met

| I-40 §15 condition | Evidence |
|---|---|
| Fast-forward only | §2.2: reflog "Fast-forward", no merge commit |
| Ordinary push | §2.2: `git push origin main`, no force |
| Pre-merge ancestry check | I-66 §1 items 9 and 10, and the I-66 §3 final checks |
| Post-merge fresh-clone validation | §2.4: PASS |
| CI on `main` green | §2.3: run `41672716486` attempt 3, success |

This authorization was used up by that single fast-forward. It authorizes no other merge.

Evidence manifests (sha256 of each `MANIFEST.sha256`):

- I-66, `~/tars-evidence/I-66/`:
  `82ca964f865521f2d0a9663c8209d237f7276eeccbb9422bc455db7b06af35c9`;
- I-66A, `~/tars-evidence/I-66A/`:
  `76ce34dcda5de51bb5fc1434b951ae1f17005e3fc4182d9bcbbf790dbc31de3a`;
- I-66B, `~/tars-evidence/I-66B/`:
  `875928f1e1fd03bda895054fc7ed8ca7bd69ef23caf844bca9ce524130276a42`.

## 3. Historical statements superseded by this record

This record supersedes only two kinds of statement: the **merge state** of S1 and the **status of
OD-9**. The statements stay unchanged in their files as historical records; they are not edited.
Every other part of the statements quoted below stays as it is.

### 3.1 I-65 acceptance record, lines 3 to 5

```text
- **Status:** **M3 T2 S1 ACCEPTED** by the owner/Tech Lead at
  K `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f` (I-65, 2026-11-03). **NOT MERGED.** T2 S2 is **NOT
  AUTHORIZED**. PC-7 for T2 overall: **NONE**.
```

- **Superseded:** only "**NOT MERGED.**". S1 is merged into `main` at K (§2).
- **Unchanged:** "ACCEPTED", "T2 S2 is NOT AUTHORIZED" and "PC-7 for T2 overall: NONE".

### 3.2 I-65 acceptance record, lines 159 and 160

```text
- **Deferred owner decisions.** OD-8 (before S4), **OD-9 (merge model, before S2)**, OD-10 (before
  S5), OD-11 (before U-19 (a′)) and **OD-12 (before S2)** remain undecided (I-40 §2).
```

- **Superseded:** only the listing of OD-9 as undecided. OD-9 is decided (I-66, §4).
- **Unchanged:** OD-8, OD-10, OD-11 and OD-12 remain undecided.

### 3.3 `docs/milestones/M3-T2-report.md` at K (on `main` and on the S1 branch)

Line 3:

```text
**Status: S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED.** S2–S6 are not started.
```

Line 537:

```text
`S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED`
```

Line 687:

```text
**Status after I-60:** `S1 IMPLEMENTED / REVIEWED (I-58: REQUEST_CHANGES) / CORRECTED (F–H) / NOT RE-REVIEWED / NOT ACCEPTED / NOT MERGED`.
```

Line 778:

```text
**Status after I-62:** `S1 IMPLEMENTED / REVIEWED (I-58: REQUEST_CHANGES) / CORRECTED (F–H) / RE-REVIEWED (I-61: REQUEST_CHANGES, S1C-03) / S1C-03 CORRECTION PREPARED (I-62; local, not pushed, not re-reviewed) / NOT ACCEPTED / NOT MERGED`.
```

- **Superseded:** only the element "NOT MERGED" in each of these four lines.
- **Not addressed by this record:** every other element of those lines. Acceptance is recorded in
  the I-65 acceptance record, not here. Changing the report on `main` would itself require a commit
  to `main`, which needs a separate authorization.

### 3.4 Not superseded

The following statement in the I-65 acceptance record (lines 161 and 162) still accurately describes
the report, and is not superseded:

```text
- **Report status at K.** The report on the S1 branch still ends with the I-62 status line
  (`... NOT ACCEPTED / NOT MERGED`). This record, not the report, carries the acceptance.
```

## 4. OD-9: the general merge model

### 4.1 Decision

OD-9 is answered with the first of the two I-40 options: **slice-by-slice**. In the owner's words:
"an independently accepted T2 slice may be merged into main after satisfying its governing
acceptance criteria and receiving explicit owner merge authorization."

The other I-40 option, "all slices stacked until T2 acceptance", is not selected.

### 4.2 What the model permits, and what it does not

The model sets the **shape** of future merges. It is not itself a merge authorization. For any later
slice Sn (S2 … S6), all of the following stay separately required, each by its own owner decision:

1. a PC-7(Sn) implementation authorization (I-40 §15: "S2–S6 each need their own PC-7
   authorization");
2. completion of Sn's governing acceptance criteria, including its independent review;
3. an explicit owner **acceptance** of Sn at a named commit;
4. an explicit owner **merge authorization** for that commit.

"This decision applies to S1. It does not automatically authorize acceptance or merging of
subsequent slices." Accepting a slice does not imply its merge, and the slice-by-slice model does
not imply that any slice is accepted.

Unless a later merge authorization says otherwise, the I-40 §15 merge conditions are the reference
conditions: fast-forward only, ordinary push, pre-merge ancestry check, post-merge fresh-clone
validation, and CI on `main` green. This record does not change them.

### 4.3 Consequence noted, not decided

The slice-by-slice model and a later slice's starting commit are separate questions:

- **The model** governs only how an accepted slice reaches `main`: one slice at a time, after its
  own acceptance and its own merge authorization. After each such merge, `main` contains every slice
  merged so far.
- **The starting commit** (base) of each later slice is not set by the model. The base for each
  later slice remains subject to that slice's own PC-7 authorization. This record does not decide
  it, and does not imply that a later slice must start from `main` or from any other commit.

The planning line (`milestone-3-t2-authorization`, which holds I-40 and the other owner records) is
not on `main`, and the S1 merge did not bring it in. Publishing this record and the I-65 acceptance
record to the planning line leaves both outside `main`. How, or whether, planning records reach
`main` is not decided here.

## 5. What stays unauthorized, open or limited

- **T2 S2: NOT AUTHORIZED.** Answering OD-9 removes one of the I-40 prerequisites for S2. It does
  not authorize S2. **OD-12** (OI-27 confirmation) must also be resolved before S2 (I-40 §2), and S2
  needs its own PC-7 authorization.
- **S3 to S6:** not authorized. OD-8 (before S4), OD-10 (before S5) and OD-11 (before U-19(a′)) stay
  open.
- **PC-7 for T2 overall:** NONE. T2 is not accepted.
- **Accepted S1 limitations (I-65):** S1C-01 (arm64 long-double coverage limitation) and S1C-02
  (T-09 external probe and CI coverage limitation) remain accepted as nonblocking. They are not
  closed by the merge.
- **Platform scope:** T-08 byte identity and the T-09 probes are same-host results on macOS x86_64.
  CI does not run the T-08 corpus comparison, the S1C-03 comparison or the T-09 probes. The green CI
  on `main` makes no further cross-platform or accuracy claim.
- **Scientific boundaries (I-40 §15, unchanged):** DL-1…DL-7 stay unreviewed or unbuilt; POG
  accuracy gating stays BLOCKED; no row is promoted; DR-0028 P6(b) stays OPEN; X-1 NOT AUTHORIZED;
  geodetic GMAT acceptance stays in T5.
- **Publication:** when this draft was prepared (I-67), the I-65 acceptance record was committed
  locally (`2512e1ce481f8abc3dc964220920ee82d313a9d5`) but not pushed, and this record was
  uncommitted. Pushing the acceptance record, and committing and pushing this record, each need
  owner authorization.

## 6. OD status after approval of this record

| ID | Status |
|---|---|
| OD-7 | not restated here; unchanged by this record |
| OD-8 | OPEN (before S4) |
| **OD-9** | **DECIDED (I-66): slice-by-slice** |
| OD-10 | OPEN (before S5) |
| OD-11 | OPEN (before U-19(a′)) |
| OD-12 | OPEN (before S2) |
