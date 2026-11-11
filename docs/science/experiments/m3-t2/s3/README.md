# M3 T2 S3 phase-D evidence (commit D)

**Densities are UNVERIFIED ABOVE 1000 KM (DR-0029 P5).** This is author evidence. It does not make
any obligation MET and it is not a review verdict. OB-S3-01…OB-S3-30 stay PENDING until the
independent S3 implementation review. OB-30 (S4/T3), OB-31 (S4), CF-S3-LABEL, CF-S3-SUBWIRE and
CF-S3-VAL also stay PENDING; S3 never meets them.

- **Subject:** committed and pushed BC `930e74f6c62719ad8aade6592493d1a1ba16c2a8` (tree
  `1d2e9cab9b0f084ab0892d4e66d59b12bb84243d`); base L `a76470fbbc70471fcea24f26bf6120098e37c57c`.
- **Authority:** PC-7(S3) (`~/tars-evidence/S3-PC7-issuance-v1/`, manifest `c504eb8a…368d`), and the
  owner instruction of 2026-11-11 (`provenance/OWNER-INSTRUCTION-2026-11-11.txt`) that decided
  Q-1, Q-2 and Q-3.
- **External evidence packet:** `~/tars-evidence/S3-provenance-contract-recovery-v1/`. Every file
  here is a copy of a file in that packet, or a citation file computed from covered external
  files. `SHA256SUMS` covers every file that commit D adds; it leaves out `commit-a/` and that
  directory's own `SHA256SUMS`.
- **Commit D adds evidence only:** no BC production, test, data, twin or frozen-witness blob
  changes.

## Dataset identity (DR-0027 B-1, option B1)

- **Source:** `src/tars/sim/data/EarthExponentialAtmosphereData.txt` is GMAT R2026a
  `data/atmosphere/earth/EarthExponentialAtmosphereData.txt`, copied verbatim.
- **Identity:** git blob `ec7f1e2023adba77711abf0c8c3c84577bbf49fc`, 661 bytes, sha256
  `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`.
- **E-BLOB:** `e-blob/E-BLOB.json` checks that the blob equals the package file in the BC export,
  and also the protected T0 copy at L.
- **Comparison with published data:** the table is 25 of 28 rows identical to the author-published
  data file (B-5). It is not claimed to agree with any printed textbook table.
- **Disputed cells:** documented in DR-0027 B-2 and not repaired.

## Contents

| Path | What it is |
|---|---|
| `provenance/` | Owner instruction; `PROVENANCE-DETERMINATION.md`; the closed Q-2 inventory (22 LOCAL-A/LOCAL-BC non-pytest runs: limited historical procedural departure) and Q-3 inventory (8 phase-P discovery runs: historical discovery with limited provenance); the recording-only capture design and its feasibility record; `LOCKED-ENV.json`; `STOP-RESOLUTION.md` (prospective stop resolution, coverage map, M-29 disclosure) |
| `packaging/` | Corrected PK-1…PK-8 chain at the committed BC export (stage0 BA-1…BA-5 sealed before any build; stage1 control, PK-1, PK-2; stage2 PK-3…PK-8). Includes `PK-COVERAGE.json`: 3 driver, 6 build-hook and 14 payload/installer ENV records, all complete. Backend `uv-build` 0.12.24, retained wheel sha256 `fa4f087d…6dc0` |
| `mutation/` | The single fresh committed-BC campaign (`CAMPAIGN.json`, kept as the driver wrote it); the re-verification from retained files (`CAMPAIGN-ASSESSMENT.json`, and `-2` from a byte-identical re-run under the ENV recorder); `MUTANT-VERIFY-2.json` (53 designated: 45 established, 8 candidate; equivalents M-13, M-25c; not applicable M-28a, M-28b, M-28c-a2) |
| `regression/` | New phase-D regression evidence (`RGATES.json`): R-1 M1 Proof 9/9 at BC and L; R-2 M2 Proof 20/20 and `m2_proof` 228/228 at BC and L; R-3 T1 correction checks byte-identical to the committed results, BC = L; R-4 T0 314 passed at BC and L; R-5 scope/protected paths; R-S1; R-S2 gate part (full suite 1584 passed at BC); ruff. Also the full-suite and R-S1 JUnit, and `rs2-host/` (R-S2 host comparison). Proof wrapper outputs are copied; the four `proof_run.log` files are cited by sha256 in `regression/proof/PROOF-LOGS.sha256` |
| `ci/BC-42937733985/` | BC CI run 42937733985, attempt 1, 4/4: run/job metadata, raw-log sha256 and, per check job, the extracted S3-POINTS, S3-DATA, S3-TABLE-HEX, S3-DL4, S3-XP3 and S2 records with completeness status (`COLLECTION.json`). DL-4: 3 758 points, 0 differences on each platform; R-S2 stable projections equal to main run 42715616493 |
| `report-only/` | S3-R-01…S3-R-05 (`REPORT-ONLY.json`): REPORT-ONLY, never gated, no bound or accuracy claim. S3-R-01 depends on A-FP-2, which is not accepted |
| `rr15/` | RR-15 (S3-T-15) author draft; only the independent review completes it |
| `red-green/`, `discovery/` | Hash citations of the A/BC red and green records and of the phase-P discovery files (`DISCOVERY-MANIFEST`, `WITNESSES.json`: "discovery, not kill evidence"), all external and covered by `S3-implementation-v1/MANIFEST.sha256` |
| `e-blob/` | E-BLOB record |
| `tools/` | Every packet tool used, as `.txt` copies; `tools/superseded/` holds the versions that ran in failed attempts |

## Results in brief (author evidence)

- **Mutation:** control CONTROL-PASSED; 53/53 designated mutants KILLED by the designated node
  with the designated tag. Each execution has its S2 ENV node in the pytest process, the
  `uv.lock` pin, and complete process records.
- **Packaging:** PK-1…PK-8 pass. The sdist is `37fc6592…dee8`. The tree wheel and the wheel built
  from the sdist are identical (`a3ca952c…f1e1`).
- **Regression:** every R gate passes (see `RGATES.json`).
- **R-S2 host comparison (`regression/rs2-host/RS2-HOST.json`):** G17A and G17B stable projections
  equal the committed host records at L (`s2/i105/green/records/`, each checked against L's
  `s2/i105/SHA256SUMS`). The libm digest is unchanged. Class P coordinate differences are 0 and
  0 (report-only). L has no committed host S2-XP3-LISTING, so the new listing (22 665 entries)
  is reported only.
- **Report-only results:**
  - S3-R-01: no listing point above the E3 upper enclosure.
  - S3-R-02: no non-increase violation.
  - S3-R-03: at most 1-ulp differences at ≤ 3 points between platforms.
  - S3-R-04: all 3 248 points at h ≥ 0 are bitwise equal to T0's `density(units="km")`.
  - S3-R-05: first subnormal at about 181 891 km and first zero at about 191 735 km.

## Disclosures for the independent implementation review

1. **M-29 driver stop (author judgment).**
   - `campaign2.py` stopped at M-29, the last mutant, with "INVALID-RECORD: process records 1
     (children expected 1)". Its static child-count expectation was wrong for a test that fails
     before it spawns a child.
   - `CAMPAIGN-ASSESSMENT.json` binds child records to the probe scripts each execution actually
     wrote, and classifies M-29 as KILLED. This is the only difference from the driver.
   - If the reviewer or owner rejects this, the M-29 kill is not established
     (`provenance/STOP-RESOLUTION.md` §3).
2. **Failed and superseded attempts in this packet, all kept:**
   - packaging stage0 run-1 (driver without `GIT_CEILING_DIRECTORIES`), stage2 run-2 (venv `home`
     check) and stage2 run-3 (ceiling below the export);
   - feasibility run-1 and run-2 (checker defects);
   - `MUTANT-VERIFY.json` (dynamic-tag check);
   - BC CI collection attempt 1 (empty logs without `--allow-escape-sequences`);
   - report-only run-1 (`Decimal(str(Fraction))`) and run-2 (Decimal overflow of
     `exact·exp(θx·X)`, replaced by the identical T0 form `ρ0·exp(−(1−θx)X)`);
   - `verify_clone_env` run-1 (relative clone path).

   The tool versions that ran are in `tools/superseded/`. No subject, test, threshold or edit
   changed between attempts.
3. **Execution classes (Q-1):**
   - **Own complete ENV:** numerical gates, hooks, import/tamper processes and artifact-check or
     verdict drivers (PK drivers, `campaign2.py`, `assess.py` re-run, `report_only.py`,
     `rs2_host.py`, `ci_collect.py` attempt 2 with its I-105 extractor children: 7 complete
     records).
   - **Tool metadata only** (run record and tool sha256): orchestration and record-analysis tools
     that produce no numerical outcome and check no package artifact (`rgates.py` orchestrator,
     `feasibility.py`, `hist_inventory.py`, `locked_env_check.py`, `mutant_verify.py`,
     `pk_coverage.py`, `verify_clone_env.py`).
   - This is an author classification; the reviewer may contest it.
   - Every Python process inside the regression clones has its own record.
4. **Offline setup:** offline `uv sync --locked` used a packet-local copy of the existing uv cache.
   Nothing was downloaded.
5. **R-3 count:**
   - The T1 selection is the S2 one (`tests/test_zonal_j2.py tests/test_constants.py`, as in
     `s2/scripts/s2_rgates.sh.txt`). It gives 110 passed (97 + 13) at both BC and L.
   - S2's BC `2b975d6` added one node to `tests/test_constants.py`. The "109" in the
     authorization text therefore predates that node.
   - The R-3 predicate in `rgates.py` was `>= 109`.
6. **Earlier history stays visible and is not waived:**
   - the old 54-run campaign (NON-QUALIFYING);
   - old packaging gaps G-1, G-2 and G-3;
   - I-106 relief does not apply;
   - Q-2 and Q-3 are bounded historical dispositions only.
