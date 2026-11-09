# S2 H-01 correction evidence (commit K2)

**AUTHOR EVIDENCE.** Everything in this directory was produced by the implementing author. It is not
independent review evidence, and nothing here closes H-01, marks an obligation MET, accepts S2 or
authorizes a merge.

- The independent re-review of H `8074a19bf33cf5b6d20f7d211ff44f82bf28ba93` returned
  **REQUEST_CHANGES** with one MINOR/must-fix finding, **H-01**. That verdict and its ledger (29 MET;
  OB-11 and OB-27 FAILED; OB-30 and OB-31 later-scope PENDING) remain the historical assessment of H.
- The I-104 findings remain as independently assessed at H.
- **H-01 awaits independent assessment of a corrected tip.** OB-30 and OB-31 remain later-scope
  PENDING. Acceptance and merge are not authorized.

This directory was added by commit K2, which adds nothing else. It is outside the repository's S2
`SHA256SUMS` scopes of D (`../SHA256SUMS`) and G (`../i105/SHA256SUMS`), which are unchanged; it has
its own `SHA256SUMS`.

## 1. The finding and the correction

- **Finding (independent review of H):** at `src/tars/sim/geodesy.py:110` the final `_normalize`
  branch formatted `t.__name__` into its TypeError message. A caller's metaclass `__getattribute__`
  intercepted that read, and its exception escaped instead of the required TypeError. v11 §3.8 step 0
  (pinned `~/tars-evidence/I-93/S2-proposal-v11.md`, sha256
  `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809`) requires "Every other type raises
  `TypeError`" and permits caller exceptions to propagate only from `len(r)` and `r[0]/r[1]/r[2]`. It
  prescribes no message text.
- **Correction (commit J `42ec8d6170447429ec1be8208f71cb4ee5512496`, sole parent H, tree
  `b5b9e928d4203ea82ea5178be945490ce705a1d8`):** one statement. The branch now raises
  `TypeError("geodetic input: unsupported component type")`, with one comment line. The E.1 `try`,
  base-slot normalization, check order and arithmetic are unchanged.
- **Regression test:** G-06 node
  `test_g06_h01_unsupported_type_rejection_consults_no_metaclass_hook`, the reviewer's exact witness
  (an ordinary built-in tuple `(Unsupported(), 0.0, 7.0e6)` whose first component's metaclass raises a
  ValueError sentinel on `__name__`). It asserts: no sentinel escape; exactly `TypeError`; not a
  `GeodeticDomainError`; no `__context__` or `__cause__`; and no hook call.
- **Identities** (git blob id, then file sha256):
  - `src/tars/sim/geodesy.py`: H `e409e26341ec40a0adf8123e5ea47d5fc9788d9d`
    `9df9a3e97fa9b1b917a44c502d5c6409419f1ce1f4f475cf180c9d02e7db9430`; J
    `82ca9aaab0ed63ca63a8c9ff29f6a1425a2769cb`
    `290fb095634db31a0e37c23c5e095ee54ad84db74c630aceef327118d7fdaeda`.
  - `tests/test_s2_geodetic.py`: H `50c75e31db308358795d0c34ccd4b1457a787360`
    `8383d526a52d3dfc4683c0733ecfecc1c902da8f0e7cae5548da43e643040410`; J
    `d68c7a7d1645068a34a6c430b98845beb26e9f65`
    `67f9b9e4b7fb1bcee825b95974f66cdd2ea63e14f6c86a112cfec50d80b7eac0`.
- Rationale in full: `correction/README.md` §2. Patch: `correction/diff/H01-correction.diff`; J's own
  diff `j/commit/j.diff` is byte-identical to it.

## 2. Layout

| Path | Content |
|---|---|
| `owner/` | The three owner instructions, verbatim: the H-01 correction, the J authorization and the K2/L authorization |
| `correction/` | The correction packet (`~/tars-evidence/S2-H01-correction/`): README (rationale, red/green, candidate validation), obligation-impact assessment, proposed sequence, inputs verification, diff, red/green records, candidate validation and campaign, candidate regression, scripts, and that packet's `MANIFEST.sha256` |
| `j/` | The J packet (`~/tars-evidence/S2-H01-J/`): preconditions, commit identity and push, J's CI evidence (run 42560535876), the H-01 node at exact J, the clean-J regression, scripts, the byte binding of earlier evidence to J, and that packet's `MANIFEST.sha256` |
| `k2/` | The verified preconditions for K2/L and this directory's assembler |
| `EXTERNAL.sha256` | Every file kept outside the repository, with sha256, external path and reason |
| `SCRUBBED.txt`, `SCRUB-CHECK.txt` | Files whose home or scratch path was replaced, with original sha256; the residual check |
| `SHA256SUMS` | Every file in this directory except itself |

Files with a `.txt` suffix appended (`*.py.txt`, `*.sh.txt`) are scripts stored as text. A file named
`*.tail-60.txt` is the last 60 lines of a log kept external.

## 3. Attribution (read before using any result)

1. **Red/green and the candidate campaign ran uncommitted bytes over H.** The red run executed H's
   component with the new test; green executed the corrected component with the same test bytes
   (`correction/red-green/classification.json`, 12/12 checks). The candidate validation and the
   mutation campaign (`correction/candidate/`) ran on H plus the two uncommitted files. Their bytes
   and tree are exactly J's (`j/BINDING-EARLIER-EVIDENCE-TO-J.txt`), but **that binding does not make
   them executions at J.**
2. **The dirty-candidate R-2 comparison returned False.** On the uncommitted candidate, the original
   comparison (substituting K's revision only) printed `False`, because the candidate record also has
   `tree_clean` false (`correction/regression-candidate/logs/summary.txt`). A supplementary author
   comparison substituting revision and `tree_clean` returned `True`
   (`correction/regression-candidate/r2-supplementary-check.txt`). **The supplementary comparison did
   not replace the original, which remains a failed comparison on that candidate.**
3. **The clean-J original R-2 comparison subsequently returned True.** At exact committed J, in clean
   clones, the unchanged original comparison printed `True`; J's record has `tree_clean` true
   (`j/regression-clean-J/logs/summary.txt`). No `tree_clean` substitution was used.
4. **Author audits are author evidence.** `correction/candidate/campaign-audit.json`
   (`correction/scripts/audit_campaign.py.txt`) and `correction/red-green/classification.json` were
   written by the author, separately from the drivers. "Independent" in `correction/README.md` §4
   means only separate from the campaign driver; it is not independent review.
5. **Failed helper commands remain recorded, with their consequences:**
   - `correction/red-green/classification-attempt1-validator-mistake.json` and its NOTE: one
     classification check compared a porcelain string with its leading space, which the run record
     strips. Validator mistake only; no execution was involved; the corrected comparison is
     `classification.json`.
   - `j/ci/ci-J-42560535876/rp8-rp9/attempt1-invocation-error.stdout` and its NOTE: the first RP-8/RP-9
     invocation passed its three arguments as one word (zsh does not word-split), exit 1, no output
     written. The unchanged script was rerun with explicit arguments.
   - Expected nonzero exits, not failures of the component: the red run (pytest exit 1) and the
     reviewer's unchanged metaclass probe on the candidate (`correction/candidate/reviewer-probe/`,
     exit 1, because it asserts the defect and the corrected component no longer shows it). The
     probe is a counterexample diagnostic, not a conformance test.
   - Authoring slips in scripts before execution (a macOS `date %N` format, two sed-introduced Python
     syntax errors in the classifier) produced no records; they are noted in the author session only.
6. **The I-106 exception does not cover any execution here.** Its issued scope is the 154 named
   historical executions fixed by inventory sha256
   `8116984313a017126014abf3cbdd87ec65d2db4ab8fce82697d31188e9e2f7e9`. Every execution in this
   directory carries its own §3.16 run record and DL-5 ENV record.

## 4. Results recorded here

- **Red** (H component + new test): the H-01 node fails by assertion, "the metaclass sentinel
  escaped; hook calls ['__name__']". **Green** (corrected component, same test bytes): 10 passed.
- **Candidate validation** (uncommitted, offline): S2 suite 130 passed; full suite 1 521 passed; G-17b
  8 853 Class X, 0 differences; host report-only outputs byte-identical to the H reviewer's; ruff and
  G-13 pass; campaign 44 qualifying kills and 5 approved equivalents, exact MG-02/MG-04 witnesses.
- **J's CI** (run 42560535876, attempt 1, 4/4 success on exact J): per platform, schema-2 census valid,
  G-17b 8 853 Class X compared with 0 differences (`other`), Class P differences 2 305 ubuntu, 2 188
  macos-latest, 0 macos-15-intel (report-only), RP-8/RP-9 0 outcome differences (report-only).
- **Clean-J validation** (offline, fresh clean clones of exact J): H-01 node passes; R-1 to R-4 pass
  against recomputed K `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`; R-S1 100 passed; R-S2 1 521 passed
  with valid records.

## 5. External evidence (not contained in the repository)

Large logs, raw CI logs, campaign stdout and listings, and duplicate censuses are kept outside, listed
by sha256 in `EXTERNAL.sha256`. The packets they come from are sealed by their manifests:

- `~/tars-evidence/S2-H01-correction/MANIFEST.sha256`, sha256
  `b0ea705039b483359886a77b44911eb6117c1a5775ed5b86b5eef7c0d895e584` (795 entries; copy:
  `correction/MANIFEST.sha256`). Its 49 copied mutant `src/` trees are outside that manifest too
  (`correction/candidate/campaign/MUTANT-SOURCE-TREES-NOTE.txt`).
- `~/tars-evidence/S2-H01-J/MANIFEST.sha256`, sha256
  `a6a808615df46091e3075a40988d6459317ae8e574800b8bd5c620bbbf1ee130` (335 entries; copy:
  `j/MANIFEST.sha256`).
- The independent H review: `~/tars-evidence/S2-REREVIEW-H-8074a19/continuation-20261108T211523Z/`,
  manifest sha256 `8400c3bfd78b5457d5cd06360efb0401c05db9d407765fa30c3f60bf2f61922f`. It is referenced,
  not copied.
- Scrubbed copies differ from the external originals only by the whole-path replacements listed in
  `SCRUBBED.txt`; the original sha256 of each is given there.

## 6. Limitations

- The campaign and red/green were not re-executed at J; they are bound to J by bytes and tree only.
- The commit-D derivation (OB-02/OB-19) was not rerun; it does not involve the changed component.
- CI runs pytest quietly, so CI logs do not name the H-01 node; per-node evidence is from host runs.
- Matching ENV proxy fields do not certify an identical library or build environment (r83:83).
- POG accuracy gating remains BLOCKED; A-FP-2 remains unaccepted and unjustified; Class P remains
  report-only. No accuracy, promotion or cross-platform claim is made.
