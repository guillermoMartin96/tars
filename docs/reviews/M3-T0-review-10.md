# M3 T0 Review 10 (independent review of the Review 09 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a16146-9aef-7ae1-b0a5-05e9ec7dc795`, 2026-10-22 01:42–02:18 UTC (2026-10-21 local).
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review10-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`3c565e62e8257040b48bdd1d0d74fffc370d56d2`**, the validation record of the correction commit `cc82ae7107b22a9c033bb7d03316f4e5655724b5`.
- **Environment.** The review ran in a fresh GitHub clone with its own `uv sync --locked` environment. It had a private GMAT R2026a copy, whose console digest (`1162803d…52e2`) and atmosphere table (`75762f67…a85e`) match the installation; the implementer checked both before the review, and the reviewer checked them again.
- **Prompt.** It was kept outside the repository during the review. It reproduces Authorization I-12 verbatim and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It lists every earlier finding with its current disposition and presents the I-12 corrections as claims to verify. It requires the I-12 §6 items: verify that R9-F1 and R9-F2 are resolved, confirm that the finite-only M3 mutant is detected, inspect the polar-radius calculation independently, check every earlier finding for regressions, search for additional defects, and give an explicit verdict. It states that the reviewer is not limited to the two Review 09 findings, and it uses the same verdict rule as Reviews 07–09. Every commit identifier of the pass under review is a full SHA.
- **Preconditions (I-12 §6: "after correction and validation pass"), checked by the implementer before the review:**
  - branch `milestone-3-t0-reference-spike`, with HEAD and origin both at `3c565e6` and a clean tree;
  - the validation of `cc82ae7` recorded in `3c565e6`:
    - checks 314/314;
    - mutation 100/100 detected, with 2 equivalents and no survivor;
    - M1 Proof 9/9 and M2 Proof 20/20;
    - pytest 1185;
    - five pinned and 22 spike digests;
    - 99 files reproduced twice, and the numerical outputs equal to the I-11 baseline;
  - CI succeeded on `cc82ae7` (run 39695797213) and on `3c565e6` (run 39701788045), all four jobs each.

  The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10" (Tech Lead, 2026-10-21).

**Files:**
- **prompt:** `raw/M3-T0-codex-review10-prompt.md`.
- **raw output:** `raw/M3-T0-codex-review10.md`. This is the reviewer's saved report `review_scratch/M3-T0-codex-review10.md`, which equals the CLI's final message plus a trailing newline. Its two absolute links are redacted to `<clone>`; the text is otherwise unchanged.
- **reviewer scripts and logs:** `raw/M3-T0-codex-review10-evidence/`:
  - `*.py.txt`, the reviewer's scripts;
  - `COMMANDS.md`, the command ledger;
  - `reviewer-SHA256SUMS.txt`, written by the implementer over the reviewer's unredacted files.

  Absolute paths are redacted to `<clone>`/`<review-root>`/`<scratch>`/`<home>`/`<tmp>`. `SHA256SUMS` covers the committed files.
- **The reviewer's mutated copies of the experiment directory** (`drop_m3/`, `half_m3_corrected/`) are represented by implementer-made diffs of their `t0_termination.py` against the reviewed one (`drop_m3_t0_termination.diff.txt`, `half_m3_corrected_t0_termination.diff.txt`).

**Omitted** as large or derivable:
- the reviewer's copies of `git diff 5978bfe..3c565e6` (`correction.diff`) and `git diff 86df2c3..3c565e6` (`full.diff`; 12.9 MB together);
- its archived `docs/` tree at `5978bfe` (`baseline5978bfe/`, reconstructible from git);
- the remaining unmodified files of the two mutated copies.

**Verdict:** **`VERDICT: PASS (unconditional)`**, with **no new findings**. Every resolution-table item is RESOLVED. The reviewer found no false certification, no deficient force envelope and no unsafe published floor.

**Stop rule applied (I-12 §7, PASS):**
- The output is preserved.
- The acceptance dossier is updated: `docs/reviews/M3-T0-acceptance-dossier.md`.
- **T0 is not declared accepted.** It is not merged, and T1 and T2 are not started. No Review 11 or further correction is started.
- Not done:
  - DR-0029 P1–P10 and DR-0028 P6(b) are not decided;
  - the GMAT geodetic-drag discrepancy is not closed: it stays escalated;
  - no protected artifact, test, threshold or branch-protection setting is changed.

## Resolution assessed by Review 10
| Item | Review 10 | Basis (reviewer) |
|---|---|---|
| M3T0-R9-F1 | **RESOLVED** | The production `stage_need`/`stage_lower_heights` are called directly, and only the envelope is injected. The exact counterexample gives need +2499855380.144757; the finite-only mutant gives −89239.71048326683 and fails 16 checks. Positive binding-M3 cases and the three outcome classes also execute |
| M3T0-R9-F2 | **RESOLVED** | Own 110-digit calculation on the exact binary64 a/e2 gives a polar height of −2.0373635292484448e-10 m and a radius difference from A(1−F) of 2.4767215814979376e-13 m. The corrected reference, the oracle consistency and the appended quotations agree. The remaining `B_WGS84` uses were inspected (`ellipsoid_remaining.log`) |
| M3T0-R8-F1 | **RESOLVED** | The surface, equatorial exterior-ulp, pole and β-transition checks pass; own β/zero probes reject, and a rejection never certifies |
| M3T0-R7-F1 | **RESOLVED** | `stage_need(1, tiny)` = 55992.318990613036 is finite with A0 unbounded; the infinity-normalizing mutant is detected |
| M3T0-R7-F2 | **RESOLVED** | b_R ≤ b is carried only for b > 0; the zero-coefficient mutant is detected |
| M3T0-R6-F1 | **RESOLVED** | k = 1…17 rerun; own exact-rational subnormal/zero-b probes; the zero-branch-removal mutant fails |
| M3T0-R6-F2 | **RESOLVED** | Extended-real rounding tests; own huge-height/overflowed-envelope probes do not certify |
| M3T0-R6-F3 | **RESOLVED** | LIBM_ULP = 91910196476947 is accepted and its successor rejected (own derivation); A-FP-2 is carried into E4b |
| Review 06 remark (5 287-point search) | **RESOLVED** | Still explicitly UNREPRODUCED (a resolution of its representation, not of its provenance) |
| Review 06 remark (b*, φ_B) | **RESOLVED** | 7.416912861690675e-309 (stored φ) and 1.1125369292536007e-308 (exact φ) |
| M3T0-R5-F1 | **RESOLVED** | Old counterexamples and 14 999 own exact constructions are enclosed; the relative-conversion mutant fails |
| M3T0-R5-F2 | **RESOLVED** | The populations are recomputed; 0.983 is scoped to the coefficient subset |
| M3T0-R4-F1 | **RESOLVED** | The 190 681 km example passes; own top-band force probes are enclosed; the absolute-part-removal mutant fails |
| M3T0-R3-F1 | **RESOLVED** | The 120 km counterexample and the downward-boundary checks pass; the allowance-removal mutant fails |
| M3T0-R2-F1 | **RESOLVED** | Sampled perturbed estimates are kept distinct from the analytic two-body bound |
| M3T0-R2-F2 | **RESOLVED** | The 79 999.9/80 000 m counterexample and own band/base/speed probes pass; the lower-end-only rotation mutant fails |
| M3T0-R2-F3 | **RESOLVED** | The zeroed-evidence mutant fails all 22 selected detectors |
| IM-1 | **RESOLVED** | Two reruns reproduce 0.9856650955520649 m RMS |
| IM-2 | **RESOLVED** | need(111 511.96) = +0.0018399073878806404, need(111 511.97) = −0.008245909394966729; disposition and floor unchanged |
| M3T0-F1 … F5 | **RESOLVED** | Each individually, F5 on documentary evidence (k3 offsets and the Kepler residual 6.95223445873689e-6 m re-executed) |
| Review 08 M3 coverage observation | **RESOLVED** | The always-drop-M3 mutant is detected by the first-stage-infinity check; R9 also detects the finite-only omission |

The GMAT geodetic-drag discrepancy remains **ESCALATED_FOR_INVESTIGATION** (DR-0029 Q-G2-1/P6). DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

**Reviewer's own validation:**
- checks 01–09: 314/314, and `check_review09.py` against an archived `5978bfe` tree: 3 failed and 23 passed (red before);
- full pytest: 1185 passed, 3 warnings;
- the M1 validator (7/7) and the M2 validator (228/228, without `--quick`) pass, and both GMAT compares exit 0. These are validators and compares, not the Proof wrappers, which the prompt forbade it to run;
- a mutation subset (a declared subset, not the 100-mutant rerun):
  - 25/25 non-equivalent mutants detected: all 13 R9 mutants, nine earlier ones and three of its own (M3 displacement halved, M4 displacement halved, M3 replaced by its absolute value);
  - the two declared equivalents pass 314/314 each;
  - the control passes 314/314;
  - it audited the committed full-matrix JSON and its SHA256SUMS;
- all nine experiments rerun twice, including GMAT, with all 99 tracked files byte-identical;
- five pinned and 22 spike digests, all matching; an empty protected-path diff; append-only review records; Review 09's raw output unchanged;
- its own probes:
  - 7 944 C1 and 7 055 C2 exact constructions;
  - 996 E4b zero-force evaluations;
  - 420 drag comparisons at band bases, extreme speeds and subnormal density (maximum ratio 0.9999999999999979);
  - 5 384 exterior surface points (8 037 rejections, 8 115 finite non-certifications, none certified);
  - 180 adversarial RK4 steps (smallest stage-bound gap 6.8e-8 m);
  - envelopes injected so that each of M2, M3 and M4 is the minimum;
  - an independent 110-digit implementation of the stage inequalities;
  - a byte-identical regeneration of the termination results with M3 always dropped.

## New findings
None. The reviewer reports no BLOCKER, MAJOR, MINOR or NOTE finding. It recorded two errors in its own scripts and corrected them, with both runs kept:
- a float/Decimal type error in its first M3 mutant, which it does not count as detection;
- an index error in its first stage probe.

Neither is a finding against the repository.

## Implementer's assessment
- **The verdict is PASS under the I-12 verdict rule.** There are no findings, and every item in the resolution table is RESOLVED.
- **What the review rests on.** The review rests on the reviewer's own execution for most items, as its ledger states. For R9-F1 and R9-F2 it rests on its own derivation and computation. It explicitly relies on implementer evidence only for:
  - the full 100-mutant run;
  - the Proof wrappers (9/9, 20/20);
  - CI.
- **Remaining conditions (unchanged):**
  - The force and stage guarantees hold only under A-FP-1 to A-FP-3. A-FP-2 is unresolved, and E4b depends on it explicitly.
  - The scope is C1/C2 only, with positive finite mass, cd and area.
  - No overflow.
  - Negative two-body energy, no thrust and dt = 10 s.
  - A computed h0 > β is required for any returned need.
  - There is no certified J2-plus-drag missed-crossing bound.
  - Host measurements are from macOS x86_64 only.
  - The 5 287-point search is UNREPRODUCED.
  - The GMAT geodetic-drag discrepancy stays escalated.
  - DR-0029 P1–P10 and DR-0028 P6(b) are undecided.
- **Next step:** the Tech Lead's explicit final T0 acceptance decision (I-12 §7).
