# Provenance determination for the selected S3 execution (owner instruction §2)

Recorded 2026-11-11 (UTC) by the continuing implementing author (Claude Opus 5.5). The owner's
determinations come from `OWNER-INSTRUCTION.txt` in this packet, recorded verbatim. This file restates
them, ties them to the issued authority and the audited records, and states their bounds. It makes
no owner choice of its own. It does not rewrite v4 or any earlier record. It is not an extension or
reinterpretation of I-106 (inventory `8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9`, unchanged).
Densities are UNVERIFIED ABOVE 1000 KM (P5).

## 1. Authority it interprets

- PC-7(S3) `S3-PC7-issuance-v1/PC-7-S3-ISSUED.md` (sha256 `849e5c5c…`, manifest `c504eb8a…368d`):
  - §4, D-S3-04 (a): "Every targeted gate-evidence run (including phase D mutation and PK runs)
    captures its own ENV record; none inherits another run's record."
  - §8: "Every gate-evidence execution carries: commit SHA and tree-clean flag; exact command and
    exit; start/end UTC; JUnit; the §7.1 ENV record …; the `uv.lock` SHA-256 …". Also "Each host run,
    subprocess, isolated packaging target and CI job keeps its own provenance and ENV."
- v4 `S3-proposal-v4/S3-proposal-v4.md` (`0b90e9cf…54e6`): §7.3, §13.1, §15.3 and §17 item 12.
- The latest audit: `S3-phaseD-campaign-recovery-v1/assessment/EVIDENCE-AUDIT.md` (`86201f16…`) and
  `EVIDENCE-AUDIT.json`, under that packet's manifest `76658430…7571`. It records G-1…G-3 and Q-1…Q-3.

The determinations below govern only the ambiguous per-process shorthand ("each … subprocess",
"the ENV record"), and only for this selected S3 execution.

## 2. Q-1: tool processes versus Python numerical processes

**Tool and setup operations** need no S2 Python ENV record. They are:
- the Rust uv frontend (`uv build`, `uv venv`, `uv pip install`);
- incidental launchers;
- uv's interpreter-query processes;
- ensurepip helper children.

Each tool command still records:
- UTC bounds, argv, exit and output;
- the tool's version and executable sha256;
- input, output and artifact identities;
- host and run context;
- interpreter-selection and binding evidence.

**Python processes needing their own complete ENV.** The following each need their OWN complete,
actual-process S2-approved ENV record (the S2 node's `build_record()`, libm argument set included)
and the subject `uv.lock` identity:
- isolated PEP 517 build hooks;
- numerical gate processes;
- import and tamper tests;
- Python artifact-check drivers.

A banner, a path or another process's probe does not satisfy this. Tool metadata is kept separate
from numerical ENV and is never labelled as ENV. Per-check JSON is the packaging outcome record.
JUnit stays required for pytest.

**Consequence.** Any child that supplies a separately asserted numerical, import or tamper outcome
needs its own process evidence. The author's earlier classification of test-spawned children
(`EVIDENCE-PLAN.md` §2) is **not** adopted silently; it is re-examined in `feasibility/`.

## 3. Q-2: closed historical inventory (LIMITED HISTORICAL NONBLOCKING PROCEDURAL DEPARTURE)

Inventory: `determination/Q2-INVENTORY.json`, produced by `tools/hist_inventory.py`, record
`records/HIST-inventories.txt`. Every source file is covered by `S3-implementation-v1` manifest
`c137f094…8383`, and its hash was re-verified at read time.

**The departure covers exactly 22 runs: 11 in LOCAL-A and 11 in LOCAL-BC.** In each group they are:
- `01-m2-xp-collect` (M2 cross-platform record collection);
- `05-determinism`;
- `06-cross-platform`;
- `07-gmat-m1-compare`;
- `08-m1-proof`;
- `09-m2-determinism-{m2_burn_to_depletion, m2_invalid_commands, m2_prograde_burn, m2_retrograde_burn}`;
- `10-gmat-m2-compare`;
- `11-m2-proof`.

**Mechanical bound checks (all true):**
- the group subjects are LOCAL-A HEAD = A `1c4d2cc6…`, LOCAL-BC HEAD = BC `930e74f6…`, each with a
  clean status before;
- every run exited 0;
- none of the 22 has an S2 ENV record or the lock hash;
- no step file is unclassified.

**Missing fields per run:**
- the S2 ENV record;
- the libm digest;
- FP, CPU and build configuration;
- the in-process executable and libpython sha256;
- the `uv.lock` sha256.

**Boundary note.** `01-m2-xp-collect` is included because it is a cross-platform numerical check (it
runs `toolbox/validators/m2_cross_platform.py collect`). Both the audit's Q-2 category list
("determinism, cross-platform, GMAT-compare and M1/M2 Proof") and the owner's list ("M1/M2 Proof,
determinism, cross-platform and GMAT") name that category. I record the inclusion explicitly so the
reviewer can judge it.

**Not in Q-2:**
- `00-head`, `00-status`, `12-status-after` (git);
- `02-ruff-check`, `03-ruff-format` (Rust lint tool);
- `04-pytest`, which carries its own S2 ENV record and lock hash.

The historical ruff and git steps record UTC, argv, exit and output, but not the tool version or
executable sha256. They are not numerical gate processes. No exception is claimed for them. New D
runs record tool version and sha256 under Q-1.

**What the departure does not do:**
- It does not establish those environments, certify numerical correctness, make the records
  complete or assert pre-push compliance.
- It covers no failed gate, altered value, missing result or later execution.

New phase-D regressions are new D evidence with full records. They are never presented as
reconstructed pre-push evidence. The A and BC commits stay unchanged. The independent
implementation review must assess this history.

## 4. Q-3: closed historical inventory (HISTORICAL DISCOVERY WITH LIMITED PROVENANCE)

Inventory: `determination/Q3-INVENTORY.json`.

**The covered records:**
- `discovery/DISCOVERY-MANIFEST.json`: `dc62354a366e78639d85960ef5bf2ae01536e369c78085d5dceaf6d59b01e274`,
  `A_sha` = A, lock hash = the pin.
- `discovery/WITNESSES.json`: `678cb821355772579b6f43b87e552c0ca5185c9aa21336780b4f65a890f0ab53`, 8
  witnesses (M-07, M-08b, M-09, M-10, M-11, M-12, M-14, M-17), survivors [], cites the manifest
  `dc62354a…`.
- 8 run files `discovery/runs/M-*.json`, all `WITNESS`, plus 8 command records `records/P-DISC-*.txt`.
  Their per-file hashes are in the inventory.

**Fields per run.** Present: `sys.version`, `platform.platform()`, `platform.machine()`, executable
realpath and executable sha256. Absent: libm digest, FP, CPU, build configuration, libpython sha256,
and per-run lock and commit.

**What these records are, and are not:**
- They are input-selection observations only. They are not kill evidence and not complete ENV
  records.
- No rediscovery, no witness or test change, and no backfill.
- Every kill must be established independently by the fresh unchanged-BC campaign.

**Future discovery.** For any future discovery, "ENV record" means the complete approved record.
This exception covers no future discovery and no gate or kill run.

## 5. What remains NOT waived

- The old 54-run mutation campaign stays nonqualifying.
- Packaging G-1, G-2 and G-3 stay unwaived. They are to be corrected only by the new packaging chain.
- Every earlier missing record and deviation stays visible.
- No CPU, build or libm value is invented or borrowed from another execution.
