# Prospective stop resolution and evidence-coverage map (owner instruction §5), recorded before D

Author record, 2026-11-11 (UTC). This is not independent approval of the implementation. It does not
approve any deviation retroactively. Densities are UNVERIFIED ABOVE 1000 KM (P5).

## 1. Stops resolved prospectively, by new evidence only

| Earlier stop | Earlier (non-qualifying) attempts, kept historical | New qualifying evidence (this packet) |
|---|---|---|
| v4 §17 item 20 (BA-3 not recorded) and the packaging gaps G-1/G-2/G-3 | `S3-implementation-v1/packaging/run-1` (old PK; no BA before the build; 3.14.7 hooks; no per-process ENV); `S3-phaseD-recovery-v1/packaging/pk` (banner/static-hash hooks; drivers without ENV; artificial `[U]` CPU fields) | `packaging/run-2` (stage0: BA-1…BA-5 re-verified and sealed before any build; stage1: control, PK-1, PK-2, binding) and `packaging/run-4` (stage2: PK-3…PK-8). Records: `records/PK-stage0-run-2.txt`, `PK-stage1-run-2.txt`, `PK-stage2-run-4.txt`. Completeness re-check: `assessment/PK-COVERAGE.json` (3 driver, 6 hook and 14 wrapper ENV records, all complete; hook records = hook calls). Artifacts: sdist `37fc6592…dee8`, tree wheel and from-sdist wheel `a3ca952c…f1e1` |
| v4 §17 item 12 (the campaign had no ENV/lock record) | `S3-implementation-v1/mutation/` (54 runs without ENV). It stays NON-QUALIFYING and is not waived | `campaign/CAMPAIGN.json` (driver) and `campaign/CAMPAIGN-ASSESSMENT.json` (re-verification from the retained files): control CONTROL-PASSED, 53/53 KILLED, every execution with the S2 ENV node in-process, the lock pin, and complete process records |

Superseded or failed attempts inside this packet are kept and disclosed: `packaging/` root (run-1 stage0),
`packaging/run-3` (stage2), `feasibility/` run-1 and run-2, `campaign/MUTANT-VERIFY.json`, and the
campaign driver's M-29 verdict (§3).

## 2. Historical dispositions (owner §2)

- **Q-2:** `determination/Q2-INVENTORY.json`, exactly 22 LOCAL-A/LOCAL-BC non-pytest numerical runs.
  This is a limited historical non-blocking procedural departure. The new D regressions are new D
  evidence.
- **Q-3:** `determination/Q3-INVENTORY.json`, the 8 phase-P discovery runs at A: historical discovery
  with limited provenance, not kill evidence.
- **Q-1:** tool and setup processes carry tool metadata only. Every Python numerical gate, hook,
  import or tamper process and every artifact-check driver carries its own ENV record
  (`feasibility/CAPTURE-DESIGN.md` §3).

## 3. Disclosure: the campaign driver's M-29 stop

- **What happened.** `campaign2.py` stopped after the last mutant, M-29, with "INVALID-RECORD:
  process records 1 (children expected 1)". The driver took the expected child count from the
  designated nodes: one per node of a spawning test.
- **Why no child existed.** Under M-29, `test_s3_t02c_missing_file` fails at its first, in-process
  assertion (`S3-T-02c/CAT in-process ('raised', 'unexpected:FileNotFoundError')`). That assertion
  comes before `_copy_tree` and `_probe`. The run's `tmp_path` (`test_s3_t02c_missing_file0`)
  contains no `copy/` and no `s3_probe.py`, so no child process existed.
- **Every real process is recorded.** The one process that ran, pytest itself, has a complete and
  bound record. The ENV node passed. The designated node failed with `AssertionError` carrying
  `S3-T-02c/CAT`.
- **Nothing was skipped.** M-29 is the last mutant in the frozen order, so no execution was skipped
  by the stop, and nothing was re-executed.
- **Re-verification.** `tools/campaign/assess.py` re-verified all 54 executions from the retained
  files. It binds child records to the probe scripts each execution actually wrote: control 3/3;
  M-18, M-20a, M-20b, M-23b 1/1; all others 0/0. The only difference from the driver is
  M-29 INVALID-RECORD → KILLED.
- `CAMPAIGN.json` is unchanged.
- **My judgment.** No required record is missing. The stop came from my driver's over-strict
  heuristic, not from an unmet requirement. I therefore continue under §5. This judgment is
  disclosed for the independent review. If the owner or reviewer disagrees, the M-29 kill is
  not established and D's mutation evidence is incomplete.

## 4. Evidence-coverage map (Python processes in new gate-evidence executions)

| Area | Executions | Python processes with own complete ENV | Tool steps (metadata only) |
|---|---|---|---|
| Packaging | PK-1, PK-2, control, PK-3…PK-8 | 3 drivers, 6 build hooks, 14 payload/installer/setup | uv build/venv/pip (Rust), git, shasum, otool, ls |
| Campaign | control + 53 mutants | 54 pytest main processes + 7 `-I` children; S2 ENV node in each pytest | git archive/ls-tree |
| Campaign setup | venv creation | 1 (wrapper) | — |
| D regressions | see `d/rgates/RGATES.json` (next) | every process in the clone venvs (recorder) | uv sync, git, ruff, shasum |
