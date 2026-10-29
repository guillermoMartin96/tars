# External Review: M3 T2 S1 I-46 decision record and test/mutation plan amendment A-1, plan review 01

## Review details

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a18845-7725-7a61-8f0d-d90bdebb1c23`. This was
  a fresh session, separate from proposal Reviews 01–03, from a provider separate from the
  implementer's.
- **Date:** 2026-10-29.
- **Reviewed material:** documentation and plan only. Nothing is implemented.
  - `M3-T2-S1-test-plan-amendment-I46.md` (A-1), sha256
    `04aca5f42e59748c89bdcbf2e3e6b051903068bb842aeeaa37e9e77213542db3`. It is committed unchanged.
  - `M3-T2-S1-decision-I45.md` as drafted, sha256
    `1b7bb365e1c7577130545537e93a0e8fb505dbaf471497b6314a51a2d9eab603`, with its diff against `b52f77c`.
    The committed version differs from it only in the §4.3 rows for items 5–7, which now state this
    review's outcome (finding N-02 below). Diff:
    `docs/science/experiments/m3-t2/s1-i46/decision-reviewed-vs-final.diff`.
  - `I-46.md`, the owner text, sha256 `4ba876213b6ebf96617781584117d232a0dd9b4e4dd1b4f8977ddcd399d030bd`.
  - The reviewer verified the package (`pkg/SHA256SUMS`, 4 files).
- **Authorization:** I-46 authorized work item 5 (owner, 2026-10-29).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-plan-codex-review01-prompt.md` (sha256 `ecae743d…bae74e`);
  - `docs/reviews/raw/M3-T2-S1-plan-codex-review01.md`, the final message verbatim (sha256
    `c4ac760b…3efb4`). It contains no local paths and is unedited;
  - `docs/reviews/raw/M3-T2-S1-plan-codex-review01-evidence/`, which holds:
    - `REVIEW.md`, the reviewer's scripts (as `.py.txt`) and their outputs;
    - `pkg/`;
    - `SHA256SUMS`;
    - `SCRUBBED.txt`: absolute local paths in 2 output files were replaced by `$SCRATCH`, and their
      original sha256 values are listed there;
    - `EXCLUDED.txt`: the reviewer's copied BASE, v3-S and mutant trees (198 files) with their sha256.
      Those trees are kept externally in `~/projects/tars-evidence/I-46/`. Its `MANIFEST.sha256`
      (224 files) has sha256 `90f9c204f8ff8f007856dfaeb5be8ae45f514f352db19dff19ad924ff0054d99`.
- **How it was run:**
  - a fresh clone of the planning branch pinned at `b52f77cb6693243b1ba681753627bb79c7005264`, whose
    `src/` and `tests/` equal BASE;
  - `uv sync --locked`, with `review_scratch/` untracked;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`, with no network.

  Afterwards the tracked tree was clean, HEAD was unchanged, and
  `git diff -- src tests docs/milestones/M3-T2-S1-proposal-v3.md` was empty.
- **Owner restriction observed:** "Do not implement the new tests or mutant yet." The reviewer did not
  author T-04 (d)/(e) or add M-22 to the campaign. Its results come from throwaway probes, labelled as
  such: `probe.py` records scalar expected masses at each call, and `run.py` reproduces Review 03's
  powered lazy mutant in a scratch copy.

## Summary

**`VERDICT: PASS`.** 0 BLOCKER, 0 MAJOR, 0 MINOR, 2 NOTE.

| Line | Plan review 01 |
|---|---|
| **D1 pin** | **HOLDS** |
| **I-46 recording** | **FAITHFUL** |
| **A-1 vs gates and scope** | **CONSISTENT** |
| **M-22 kill by the planned nodes** | **EXPECTED** |

| Item | Reviewer's independent result |
|---|---|
| Package, pin | All 4 package sums verify. The proposal sha256 equals the D1 pin. Proposal, `src/` and `tests/` are unchanged. The in-repo I-45 evidence manifest verifies. |
| Verbatim | §5 with the demotion reversed is byte-identical to `I-46.md`, sha256 `4ba87621…30bd`. |
| D1–D7 | Faithfully recorded. D3 keeps proposal §3.2's contract; D4 keeps powered legacy indexing; D5's deferral is correct (`integrators.py` is protected); D6 adds no enforcement; D7 makes no cross-platform claim. |
| Historical verdicts | Reviews 01/02 remain `REQUEST_CHANGES`; Review 03 remains a proposal-level `PASS`. §0–§3 are byte-identical apart from the declared §1 pointer. |
| T-04 (d)/(e) design | **v3-S probe:** powered call counts are 1 (write-after), 4 (shared buffer), 4 (row views) and 1 (lifetime Euler). The burn covers the whole 0.5 s tick in one integrator step, and every call takes the powered branch. Stage masses vary within the step (`0x1.4500000000000p+10`, `0x1.44fd7008ecc49p+10`, `0x1.44fae011d9892p+10`); every snapshot matches bit for bit, and every stage is released. **BASE probe:** each case reaches `AttributeError` (no `LegacyForceAdapter`), and the existing modules collect. |
| T-04 (c) not mirrored | Consistent with D2 and with the preserved legacy `float(y[_PROP])` powered read. |
| M-22 | **Scratch mutant:** passes the existing 86 nodes (the N-01 gap). **Probes:** write-after reads 1123 (`0x1.18c…p+10`) instead of 1300; shared-buffer and row-view read the dry mass 1000 (`0x1.f4…p+9`); the lifetime stage stays alive. Each planned node is therefore expected to fail its stated assertion. The mutant is non-equivalent, and M-19's argument is undisturbed. |
| Counts | The arithmetic checks: 90 / 61 / 1 380 / 1 319 + 61 / 25 / 24 / 90. **Reviewer runs:** S1 nodes 86 on v3-S; BASE 29 passed and 57 failed. The amended figures remain predictions. |
| Gates, scope | The allowlist, invariants, red-first rule, mutation criterion and commit sequence are kept. Commit A stays T-07 only. |
| Pinned proposal | No contradiction beyond the authorized supersession of the §5 counts. |

**Reviewer limitation (not a finding):** the optional full-suite attempt could not collect. The copied
minimal trees lack `proof/thresholds/m2.json`, and 3 collection errors occur (`full-proper.txt`,
`full.txt`). The reviewer did not use it as evidence. The focused S1 runs completed.

## Findings register and dispositions

| ID | Severity | Location | Finding | Disposition |
|---|---|---|---|---|
| M3T2S1-P1-N1 (reviewer N-01) | NOTE | A-1 §6; decision §4.3 | Execution of the new nodes, the M-22 mutation evidence and the final planning CI remain outstanding. This verdict accepts the plan only. | **ACCEPTED; no change needed.** A-1 §6 already lists these as owed at implementation. Planning CI is reported in the I-46 report. |
| M3T2S1-P1-N2 (reviewer N-02) | NOTE | Decision record §4.3, items 5–7 | The review, CI and report entries named destinations, not completed evidence. | **ACCEPTED; corrected editorially** (I-46 work item 6, documentation scope). §4.3 now names this record and its outcome, and states that CI is reported in the I-46 report. No decision text changed. |

**Readiness observations.** These are not findings; the reviewer gave them under evaluation item 11.
They are carried into the I-46 report.

- The I-40 §4 execution preconditions (P-1…P-7) are live checks. They must be re-run in the execution
  session, immediately before work on the S1 branch. Historical summaries do not substitute.
- The dedicated S1 branch and worktree already exist at BASE with the preserved `run_record.py`. They
  must not be recreated blindly. Any procedural conflict with I-40 §4 is to be escalated.
- Commit A stays T-07 only. It is pushed only after local gates, and it must reach CI 4/4 before B.
- The reviewer's recommendation was "NOT READY TO BEGIN A pending owner authorization and remaining
  planning/execution verification".

## Proof gate

- [x] All Critical findings resolved: none raised.
- [x] All High findings resolved: none raised.
- [x] Every substantive finding has an explicit disposition.
- [x] Accepted fixes have been re-tested: N-02 is editorial and was re-checked by diff; no code or test
  changed.
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none.

**Review gate result: PASS.**

- It applies to the I-46 decision record and plan amendment A-1 only.
- It does not alter Reviews 01/02 (`REQUEST_CHANGES`) or Review 03 (proposal-level `PASS`).
- It implements nothing and authorizes nothing.
- **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED. Commit A is NOT AUTHORIZED.**
