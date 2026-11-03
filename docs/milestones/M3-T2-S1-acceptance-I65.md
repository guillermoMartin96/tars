# M3 T2 S1: owner acceptance record (I-65)

- **Status:** **M3 T2 S1 ACCEPTED** by the owner/Tech Lead at
  K `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f` (I-65, 2026-11-03). **NOT MERGED.** T2 S2 is **NOT
  AUTHORIZED**. PC-7 for T2 overall: **NONE**.
- **Scope:** documentation only. This file is the only change. No production code, test, CI,
  dependency, scenario, proof, evidence or governing file is changed.
- **Historical records are not rewritten.**
  - `M3-T2-S1-authorization.md` (I-40), `M3-T2-S1-proposal-v3.md` (pinned), the I-41 … I-56 decision
    records and all committed S1 evidence (D, `i59/`, `s1c03/`) are not edited.
  - `docs/milestones/M3-T2-report.md` at K is not edited. Its last status line (§S1.17, "Status after
    I-62") reads `... NOT ACCEPTED / NOT MERGED`. That line is the historical status at K; this record
    supersedes it for acceptance only (see §7).
- **Owner text:** §1 reproduces the "Owner decision" section of I-65 verbatim, heading levels demoted by
  one, no other change. sha256 of that section as recorded by the implementer (from its heading through
  "This acceptance does not authorize T2 S2.", with a final newline):
  `a12b0bb35321c97b99222a1a898156b3c011fb4b92ee29b332cd4cd5fa82ad48`. The full I-65 text is kept
  externally (`~/tars-evidence/I-65/I-65.md`, sha256
  `1701028db4b7afc05c1b82c3586703ac77bfafd750ffdd660deb62e2066e3b97`).

## 1. I-65 owner decision (verbatim)

### Owner decision

I formally accept M3 T2 S1 at:

`83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`

Acceptance is based on the completed I-58 through I-64 correction and review sequence, including the independent PASS at I-64.

The following findings are closed:

- S1R-01: RESOLVED
- S1R-02: RESOLVED
- S1C-03: RESOLVED

The following limitations are accepted as nonblocking:

- S1C-01: arm64 long-double coverage limitation
- S1C-02: T-09 external probe and CI coverage limitation

S1 implementation and verification are accepted within their explicitly authorized scientific boundaries.

This acceptance does not authorize T2 S2.

## 2. The accepted commit

| Item | Value |
|---|---|
| Accepted S1 tip K | `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f`, tree `03e01038bf9b84060a8a7d7b126dfa225cb9f513` |
| Branch | `milestone-3-t2-s1-force-context` (local, tracking and remote = K at this record) |
| BASE (`main`) | `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`, an ancestor of K |
| Planning (`milestone-3-t2-authorization`) | `5714959a94bcb8de1533a56ff9e28db10c2920ac`, the parent of this record |
| BASE..K | 10 commits, linear, 0 merges; 290 paths (288 added, 2 modified), all within the I-40 §6 allowlist |

| Commit | SHA | Content | Authority; push CI |
|---|---|---|---|
| A | `abcf7553ed58138db15493044c0f34429b643286` | T-07 failure-path characterization tests | I-49; CI run `40961801315`, 4/4 |
| B | `234874b60f7e96c85387df52e63a671d1fe7dcdf` | red-phase tests T-01 … T-06 and A-1 T-04 (d)/(e); never a push tip | I-50; pushed with C and D under I-53 |
| C | `fed74284119562f59724b270ed5de4f21e734506` | ForceContext, legacy adapter and context-aware closures (v3-S) | I-51; pushed under I-53 |
| D | `1b25254e3c0a9787e1f01c428d3f0961ef5f0184` | S1 gate evidence | I-52; pushed under I-53; CI run `41094508497`, 4/4 |
| E | `0e70f540126788be8a9596d49ef422d2488f8f08` | S1 verification report | I-54, I-54A, I-54B; pushed under I-55; CI run `41156488074`, 4/4 |
| F | `c52c0904b19d9abd701864a329350c15ce0b8b64` | S1R-01 regression tests | I-59; pushed with G and H under I-60 |
| G | `45053ef6c2a11f8bd8272928060df8845f65f1b1` | S1R-01 production fix | I-59 |
| H | `2a35ebf397b474533300ee5a0169f8d5d025e86a` | S1R-02 test assertion corrections | I-59; CI run `41363138188`, 4/4 |
| J | `f47cf0d0fcc5e5ca01167aa689c7228e03127215` | I-58 review, I-59 corrections and H CI recorded | I-60; CI run `41367826201`, 4/4 |
| K | `83d573bdb4933f5d2376423d6b8e9f3348a4ab6f` | complete 26 112-case writer-corpus comparison (S1C-03) | I-62; pushed under I-63; CI run `41538766579`, 4/4 |

Production code changed BASE..K: `src/tars/sim/forces.py` and `src/tars/sim/simulator.py` only.
`src/` and `tests/` are byte-identical at H, J and K.

## 3. Corrective review history

All reviews: OpenAI Codex CLI 0.162.0, separate provider, fresh session, fresh GitHub clone at the
reviewed SHA, `review_scratch/` excluded from git, no network, no tracked writes. External evidence
lives under `~/tars-evidence/I-nn/`; each directory has a `MANIFEST.sha256`.

| Step | Target | What happened | Identifiers | Evidence manifest sha256 |
|---|---|---|---|---|
| I-58 | E | First independent S1 review. **REQUEST_CHANGES**: S1R-01 MAJOR, S1R-02 MAJOR, S1R-03 NOTE, S1R-04 NOTE | thread `01a194ab-dddc-7700-a8b1-a68193ec32fe` (model not recorded in the I-58 evidence); 2026-11-01T01:14:13Z → 01:55:11Z | `de02632c8d86b25660c86421d8eb3fe85346d48138e01b02e5bdcd96776d17c2` |
| I-59 | E → F, G, H | Owner accepted S1R-01 (MAJOR, narrow production fix) and S1R-02 (MAJOR, I-40 §10 governs, test assertions corrected); S1R-03/04 accepted as notes. Mutation campaign and regression gates rerun locally | local-only branch at the time | `da4a6032e6815db9c4658c0a0922fdb63bf94796fe1b472fd1efc57ba64cd567` |
| I-60 | H, J | H and J pushed (ordinary fast-forward); evidence reconciled in J | CI H run `41363138188`, J run `41367826201`, both 4/4 success | `5f72c32d912d782efdead1e2b49eeb26a8c065d339f6bec381bafc2b2165998f` |
| I-61 | J | Independent corrective closure review. **REQUEST_CHANGES**: S1R-01, S1R-02 resolved; new S1C-03 MINOR must-fix; S1C-01 (= S1R-03) and S1C-02 (= S1R-04) NOTE | `gpt-6.1-sol`, thread `01a19d41-45ac-77d0-9dba-ecf0af3020bb`; 2026-11-02T17:14:22Z → 18:25:39Z | `641254128a7962f2160729cb3c373d5f988f4959650c7f2cfa6287af9248dc16` |
| I-62 | J → K | Owner accepted S1C-03 (MINOR, must-fix) and authorized an evidence and report correction only. K created locally | — | `b6ef24ab734dabfbaf1fb93f95fc8eb60789166918e76c9bf05cce8c0ed235b9` |
| I-63 | K | K pushed (ordinary fast-forward J → K); CI verified; closure review package prepared | CI K run `41538766579`, 4/4 success | `639ac7c48a45d14a85d834ec9bce1be3978be3fa1b904d04fdadf16885bbe5bf` |
| I-64 | K | Independent S1C-03 closure review. **PASS**, no findings (0 BLOCKER, 0 MAJOR, 0 MINOR, 0 NOTE) | `gpt-6.1-sol`, thread `01a19f0e-7b81-73b0-92b5-541dcab58ad0`; 2026-11-03T01:38:08Z → 02:11:16Z; prompt sha256 `457b789af4a9ae1c5ebdbcaa1c987cba5448ad2ae197a731e6a3b914d72183f2` | `3c36e1a875a11b122f96c27b45c138d466b18c3154fcbda810f405670d6d1e9b` |
| I-65 | K | Owner acceptance (§1) | this record | `~/tars-evidence/I-65/MANIFEST.sha256` |

The S1 report's §S1.16 (added in J) and §S1.17 (added in K) record I-58 … I-62 in the repository.

## 4. Final dispositions of the five findings

| Finding | Raised | Severity | Final disposition (I-65) | Basis |
|---|---|---|---|---|
| S1R-01 | I-58 | MAJOR | **RESOLVED** | Fix G with tests F (I-59); I-61 found it resolved; I-64 found K does not change it (`src/`, `tests/` at K equal H and J) |
| S1R-02 | I-58 | MAJOR | **RESOLVED** | Test corrections H and campaign rerun (I-59); I-61 found it resolved; I-64 found K does not change it |
| S1C-03 | I-61 | MINOR, must-fix | **RESOLVED** | K (I-62); I-64 independently regenerated the corpora and compared all 26 112 writer and 26 880 main cases, including writer case index 0 |
| S1C-01 (= I-58 S1R-03) | I-58, restated I-61 | NOTE | **Accepted nonblocking limitation:** arm64 long-double coverage | On arm64 the T-01 (e) extended-range parameter overflows to infinity during collection, so it exercises infinity rather than finite extended-range narrowing there. Disclosed in the report; a platform-conditioned test change would need separate authorization |
| S1C-02 (= I-58 S1R-04) | I-58, restated I-61 | NOTE | **Accepted nonblocking limitation:** T-09 external probe and CI coverage | T-09's repeated-evaluation and namespace probes are external, single-host observations, not committed CI gates. Whether to add CI coverage is a future owner decision |

No finding is open. No BLOCKER or MAJOR was ever left unresolved.

## 5. Governing acceptance criteria

From I-40 (`M3-T2-S1-authorization.md`, sha256 `1b6bc40cf657a9995211462d437794a91df3f345df88dba9d986b3a1d07b78c6`), quoted:

- §14: "**PASS:** 0 BLOCKER, 0 MAJOR, and the requested reproductions succeed."
- §14: "**Blocking finding:** any byte change on an M1/M2/T1/T0 path, an out-of-allowlist change, a
  scope breach, an unsupported claim, irreproducible evidence, or an undisclosed T-07 delta."
- §14: "The S1 independent review needs **separate** authorization. CI success never substitutes for it."
- §15: "S1 acceptance needs an explicit owner decision."

How they are met at K:

| Criterion | Result at K |
|---|---|
| Independent review PASS | I-64 PASS, 0 findings |
| No unresolved BLOCKER or MAJOR | none (§4) |
| Requested reproductions succeed | I-64: corpora regenerated at BASE and K, every case compared, 8 own and 13 committed negative controls, S1 tests 100/100 and full suite 1 390/1 390 on macOS x86_64 |
| Allowlist / scope (T-11) | BASE..K: 290 paths, 0 outside the I-40 §6 allowlist; no change under `docs/decisions/`, `docs/science/assumptions.md`, `proof/`, `playbook/`, `toolbox/`, `.github/`, `pyproject.toml` or `uv.lock` |
| CI on the push tip (R-6, OD-3) | K run `41538766579`: 4/4 success (below) |
| Explicit owner decision | I-65 (§1) |

## 6. Evidence supporting acceptance

**CI on K, run `41538766579`** (head K, push event, all steps success):

| Job | ID | Runner | CPython | Result |
|---|---|---|---|---|
| check (ubuntu-latest) | `125597244690` | ubuntu-24.04 x86_64 | 3.12.3 | 1 387 passed, 3 skipped (GMAT); T-07 29/29; force-context 71/71 |
| check (macos-latest) | `125597245072` | macos-26 arm64 | 3.12.10 | same counts |
| check (macos-15-intel) | `125597245128` | macos-15 x86_64 | 3.12.10 | same counts |
| m2-cross-platform | `125620360158` | ubuntu-24.04 | 3.12.3 | PASS (position 7.23205e-06 m, velocity 8.42869e-09 m/s, 0 violations) |

The results match the H and J runs. CI does **not** run the T-08 corpus comparison, the S1C-03 comparison
or its negative controls, or the external T-09 probes. Those ran on one macOS x86_64 host only.

**Committed evidence at K:** D (`docs/science/experiments/m3-t2/s1/`, `SHA256SUMS` 96 entries),
I-59 (`s1/i59/`, 154 entries), I-62 (`s1/s1c03/`, 32 entries). All three verify at K: in the implementer's fresh-clone check (I-63)
and independently in the I-64 review.

**T-08 / INV-2 (same-platform byte identity), BASE vs K:** 26 880 main cases and 26 112 writer cases
byte-identical; corpus sha256 main `e0309486277deb101d341f23d57964d2f0c2874ab865d5be80c07f6499f0a814`, writers
`3310fd9031bc2c0cd611168e9ae3d1164ac00e87628fbe89d4c9b99401f60415`, equal to the pinned values.

## 7. Remaining limitations and boundaries

Accepting S1 does not change any of the following:

- **The two accepted limitations**, S1C-01 and S1C-02 (§4).
- **Platform scope.** Byte-identity (T-08) and the T-09 probes are same-host results on macOS x86_64.
  Other platforms are covered only by what CI runs (T-07 and the test suite, three platforms; M2
  cross-platform gate). No cross-platform or accuracy claim is made.
- **Scientific boundaries.** I-40 §3.2 (packet §17.2, I-37 §3) stands unchanged: no A-FP-2 or A-LM row is
  promoted; POG accuracy gating remains BLOCKED; DL-1 … DL-4 remain unreviewed drafts; numerical
  thresholds and production numerical sequences are unchanged; no CI modification is authorized.
  I-40 §15 stands: DL-1 … DL-7 stay unreviewed or unbuilt; no row is promoted; DR-0028 P6(b) stays
  OPEN; X-1 is NOT AUTHORIZED; geodetic GMAT acceptance stays in T5.
- **Deferred owner decisions.** OD-8 (before S4), **OD-9 (merge model, before S2)**, OD-10 (before
  S5), OD-11 (before U-19 (a′)) and **OD-12 (before S2)** remain undecided (I-40 §2).
- **Report status at K.** The report on the S1 branch still ends with the I-62 status line
  (`... NOT ACCEPTED / NOT MERGED`). This record, not the report, carries the acceptance.

## 8. Acceptance is not authorization for later work

- **Merge:** not authorized by this record. I-40 §15: "Any merge needs a separate authorization:
  fast-forward only, ordinary push, pre-merge ancestry check, post-merge fresh-clone validation, and CI
  on `main` green."
- **T2 S2 … S6:** not authorized. I-40 §15: "S2–S6 each need their own PC-7 authorization." OD-9 and
  OD-12 must be resolved before S2.
- **T2 overall:** PC-7 NONE.
- **Push of this record:** not authorized by I-65 §4. It is committed locally on branch
  `m3-t2-s1-acceptance-i65`, whose parent is the planning tip `5714959`.
