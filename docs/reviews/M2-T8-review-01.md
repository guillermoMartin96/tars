# Review M2-T8-01 — full M2 Proof, Proof record, README and milestone review

**Scope:** the T8 deliverables and the milestone as a whole:
- `toolbox/scripts/run_m2_proof.sh`;
- the README M2 section;
- `proof/records/evidence/M2/`;
- the T8 section of `proof/records/M2-propulsion.md`;
- a milestone-level check of the delivered M2 against its plan (`docs/milestones/M2-propulsion.md` §2–§10) and P1–P12.

**Constraints:**
- No threshold, reference baseline, golden, contract or validation semantics may change.
- The threat model is DR-0019 B, DR-0020 A and DR-0022 B.
- M2 completion is the Tech Lead's decision.

## Round 1
**Reviewer:** Codex (separate provider), session `01a13d0e-7233-7863-bdbd-9ddd1a499ab5`, at `adb3710`, using a git clone with metadata.  
**Prompt:** `raw/M2-T8-codex-review01-prompt.md`. **Raw:** `raw/M2-T8-codex-review01.md`, `raw/M2-T8-codex-review01-scratch/`.

**Verdict: REQUEST_CHANGES.** The reviewer reproduced:
- 1,185 tests passed, and Ruff is clean;
- the M2 Proof passes 228/228, matching the committed report check by check in name, metrics, thresholds and status;
- the snapshot verification covers 48,310 records and 982,324 values;
- O4 0.3127442515 m; GMAT vs DOP853 4.6591902702e-6 m; maximum utilization 0.6597;
- M1 Proof 7/7, both GMAT comparisons, five cross-process determinism runs, and the four M2 missions, whose summaries match the committed evidence exactly;
- the M1 golden `7a4e1877…`;
- golden differences of 0 m and 0 m/s, and the archived three-platform gate at 7.2320546225e-6 m and 8.4286904175e-9 m/s;
- no protected asset changed since `963dbe7`, and the M1 assets are unchanged against `main`.

It found no inconsistency in the physics, architecture, events, replay, limitations or earlier dispositions, and no open earlier Critical or High issue. All findings concern the new script and the record's wording.

| # | Sev. | Finding | Disposition | Resolution |
|---|---|---|---|---|
| T8-F1 | Med | `run_m2_proof.sh` printed `overall: PASS` before the unchecked `mkdir`/`cp`, so a failed publication still exited 0 | **ACCEPTED** | `017d7f6`: every cited artifact must exist in the run, or the result is FAIL. Same-named artifacts from earlier runs are removed before publishing, so a stale file cannot stand in. Publication failures set FAIL and exit 1. The verdict is printed after publication. |
| T8-F2 | Med | The script could overwrite `proof/records/evidence/M1/` despite the claim that it never does | **ACCEPTED** | `017d7f6`: before anything is written, the destination is resolved with `realpath`. It is refused (exit 2) if it is the M1 evidence directory, inside it, a symlink alias of it, or the repository root. |
| T8-F3 | Med | The clean-tree check failed open: with an evidence directory outside the repository, the git pathspec error left empty output, which was read as clean | **ACCEPTED** | Found independently by the implementer and fixed in `42878c6`, after the reviewed revision and before this report arrived. Only an in-repository evidence directory is excluded, and a git error counts as not clean. |
| T8-F4 | Med | "Complete M2 suite" overstated the script: it does not run the three-platform gate (`m2_cross_platform.py gate`) | **ACCEPTED** | `017d7f6`: the script, the scripts table and the README now describe it as the single-host suite, and name the CI job `m2-cross-platform` as the three-platform gate. The gate cannot run on one host because it needs three platforms' evidence from one CI run (DR-0023). The Proof record now cites the CI gate result at the proven revision. |
| T8-F5 | Low | P1 said "16 audited runs"; the validator audits 28 runs, aggregated into 16 report groups | **ACCEPTED** | `017d7f6`. Verified from `m2_proof.py`: 6 missions, 8 O8 runs (2 per burning mission), 10 O6 runs (5 each for the prograde and retrograde missions) and 4 stop-boundary variants. |

**Verification of the fixes:**
- The control flow was tested with a stub `uv` in nine cases:
  1. all steps pass → exit 0;
  2. destination is a file → FAIL, exit 1;
  3. destination is M1 → exit 2;
  4. destination is inside M1 → exit 2, and nothing is created there;
  5. destination is a symlink alias of M1 → exit 2;
  6. destination is the repository root → exit 2;
  7. a missing artifact → FAIL;
  8. a failing step → FAIL;
  9. a stale artifact → removed, and FAIL.
- The M1 evidence was unchanged after these tests.
- The clean-tree check was tested on clean and dirty trees with in-repository, absolute and outside destinations.
- The full suite was then re-run with the corrected script (below).
- **Full re-run with the corrected script** at `017d7f6` (clean tree, reference host, 2026-10-15T01:27Z): all 20 steps exit 0, `overall: PASS`, 1,185 tests passed. `m2_proof_report.json` is byte-identical to the `c304b53` run. The committed evidence and the Proof record now cite `017d7f6`.

## Round 2 — re-verification of T8-F1 to T8-F5
**Reviewer:** Codex, session `01a13d4b-a7ac-7382-aef2-0b1b8f8bbf87`, at `31f2fc1` (git clone). **Prompt:** `raw/M2-T8-codex-review02-prompt.md`. **Raw:** `raw/M2-T8-codex-review02.md`.

**Verdict: PASS (unconditional; no new substantive findings). T8-F1 to T8-F5 are resolved.**

Verified:
- **Script, exercised with a stub `uv`:**
  - default and successful publication, a failed step, a failed publication, a missing artifact, and removal of stale artifacts;
  - the guards for M1 and the repository root, including absolute and relative paths, descendants, symlinks, `..` and trailing slashes, all refuse before any step runs;
  - the clean-tree flag for relative, absolute and outside destinations, for dirty trees and for git errors;
  - quoting with spaces, and `set -u`.
- **Descriptions:** the script, README, scripts table and Proof record accurately state the single-host scope, the separate CI gate and the 28 runs in 16 groups.
- **Evidence:** the log names `017d7f6`, a clean tree, and 20 steps all exiting 0.
- **Fresh M2 Proof:** 228/228. It matches the committed report check by check; only the CPU metadata in notes differs. Ruff is clean.
- **Protected files:** none changed since `963dbe7`, and the M1 assets are unchanged against `main`.
- The full pytest suite was not re-run, because no Python changed since round 1, where 1,185 tests passed.

**Note (no severity):** `git diff c304b53..HEAD` shows the report as added, because the `c304b53` evidence was first committed in `9101970`. The reviewer compared `9101970..HEAD` instead: `m2_proof_report.json` is byte-identical.

## Review gate
- [x] Reviewer and revisions recorded (rounds 1 and 2)
- [x] Scope explicit
- [x] Every substantive finding has severity, evidence and a disposition (T8-F1 to T8-F5: ACCEPTED)
- [x] Accepted fixes re-tested by the implementer and re-verified by the reviewer
- [x] No Critical or High finding raised; none open

**T8 review closed: PASS (unconditional).** The reviewer also states that M2 is ready for the Tech Lead's final milestone review. Completion remains the Tech Lead's decision.

## Round 3 — pre-merge check of the Tech Lead acceptance commit
**Reviewer:** Codex, session `01a140f4-cd5e-7e62-85a7-d76e82a671cf`, at `d5a5c28` (git clone). **Prompt:** `raw/M2-T8-codex-review03-prompt.md`. **Raw:** `raw/M2-T8-codex-review03.md`.

**Verdict: PASS (unconditional).** The reviewer independently satisfied acceptance conditions 1, 2, 3, 5 and 6. Condition 4 (CI) is the implementer's.
- **Condition 1:** the PR diff is M2 work and records. `3dfffb3` changes exactly the four records; later commits only add or revise the round-3 prompt.
- **Condition 2:** protected paths are unchanged since `963dbe7`; all five sha256 pins match; all 24 existing M1 assets are byte-identical to `origin/main`.
- **Condition 3:** the fresh M2 Proof gives 228/228, matching the committed evidence check by check. The evidence log names `017d7f6`, and only records changed after it.
- **Condition 5:** round 2 records an unconditional PASS, and no blocking finding is open.
- **Condition 6:** the working tree is clean, before and after the review.
- **DR-0015:** the approval is supported by VAL-0010/DR-0016 and VAL-0013…0017/DR-0023. Residual risks and margins are unchanged. The records do not claim the merge has happened.

| # | Sev. | Finding | Disposition | Resolution |
|---|---|---|---|---|
| T8-F6 | Low (non-blocking) | The new M5 and architectural-direction statements in `docs/milestones/README.md` cannot be corroborated from the snapshot | **ACCEPTED** | The README now cites its source: the Tech Lead's instruction of 2026-10-15 (sections B and C). The architectural decisions are recorded in ADR-0008 and RES-0001 §12 on `research/flight-software-architecture` (`27ad862`), which stays unmerged pending separate approval. |

**T8 review gate: PASS.** No Critical or High finding was raised in any round, and none is open.
