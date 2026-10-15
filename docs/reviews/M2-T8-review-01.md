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
