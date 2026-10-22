# M3 T0 Review 09 (independent review of the Review 08 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15ff0-1a90-7a03-861d-c17cde0c68e6`, 2026-10-21 19:28–19:59 UTC.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review09-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`f04f9955d5ae714cc61144990395b8225a379968`**, the validation record of the correction commit `0254664e300c84ae1d102bcf3f930a2dd2573428`.
- **Environment.** The review ran in a fresh GitHub clone with its own `uv sync --locked` environment. It had a private GMAT R2026a copy, whose console digest (`1162803d…52e2`) and atmosphere table (`75762f67…a85e`) match the installation; the implementer checked both before the review, and the reviewer checked them again.
- **Prompt.** It was kept outside the repository during the review. It reproduces Authorization I-11 verbatim and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It lists every earlier finding with its current disposition, presents the I-11 corrections as claims to verify, and requires the I-11 §6 items: an independent assessment of R8-F1, a regression check of every earlier finding, an evaluation of the near-surface and first-stage-infinity tests, an inspection of the M3-dropped mutant, a search for new mathematical, floating-point, verification and documentation defects and for unsupported certification claims, and an explicit verdict with finding IDs and severities. It uses the same verdict rule as Reviews 07 and 08. Every commit identifier of the pass under review is a full SHA.
- **Preconditions (I-11 §6: "only after the correction and validation pass"), checked by the implementer before the review:**
  - branch `milestone-3-t0-reference-spike`, HEAD and origin both at `f04f995`, clean tree;
  - the validation of `0254664` recorded in `f04f995` (checks 288/288; mutation 87/87 with 2 equivalents and no survivor; M1 Proof 9/9; M2 Proof 20/20; pytest 1185; five pinned and 21 spike digests; 98 files reproduced twice);
  - CI succeeded on `0254664` (run 39641717044) and `f04f995` (run 39652330844), all four jobs each.

  The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09" (Tech Lead, 2026-10-21).

**Files:**
- prompt: `raw/M3-T0-codex-review09-prompt.md`;
- raw output: `raw/M3-T0-codex-review09.md`. This is the reviewer's saved report `review_scratch/M3-T0-codex-review09.md`, which equals the CLI's final message plus a trailing newline. It contains no absolute path;
- reviewer scripts and logs: `raw/M3-T0-codex-review09-evidence/` (`*.py.txt`; `commands.jsonl` and `inspection_commands.md`, the command ledger; the reviewer's own checksum list `review_SHA256SUMS`, written by the reviewer; `reviewer-SHA256SUMS.txt`, written by the implementer over the reviewer's unredacted files). Absolute paths are redacted to `<clone>`/`<review-root>`/`<scratch>`/`<home>`/`<tmp>`. `SHA256SUMS` covers the committed files;
- the implementer's reproduction: `raw/M3-T0-codex-review09-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of `git diff 115e747..f04f995` (`correction.diff`) and `git diff 86df2c3..f04f995` (`full.diff`; 11 MB together);
- its copy of `t0_termination.py` at `115e747` (`termination_before.py`).

**Verdict:** **`VERDICT: PASS (unconditional)`**, with two new NOTEs. No BLOCKER, MAJOR or MINOR finding was raised, and every resolution-table item is RESOLVED. The reviewer found no false certification, no deficient force envelope and no unsafe published floor.

**Stop rule applied (I-11 §7, PASS):**
- The output is preserved, and both NOTEs are recorded with their severities. The implementer reproduced each one independently.
- The acceptance dossier is prepared: `docs/reviews/M3-T0-acceptance-dossier.md`.
- **T0 is not declared accepted.** It is not merged, and T1 and T2 are not started. The NOTEs are not corrected: I-11 authorizes no further correction, and Review 10 is not started.
- Not done:
  - DR-0029 P1–P10 and DR-0028 P6(b) not decided;
  - the GMAT geodetic-drag discrepancy not closed: it stays escalated;
  - no protected artifact, test or threshold changed.

## Resolution assessed by Review 09
| Item | Review 09 | Basis (reviewer) |
|---|---|---|
| M3T0-R8-F1 | **RESOLVED** | Re-executed the equatorial 1–9 ulp exterior rejections for B_V1 and +∞, and k = 10 → 55 993.323394842984 m. The surface, pole, β and neighbouring-float checks pass. The docstring and the appended record qualifications disclose the attainable exterior rejection and distinguish computed from mathematical height. The pole quotation's precision is R9-F2 |
| M3T0-R7-F1 | **RESOLVED** | `stage_need(1, 2^-1074)` = 55 992.318990613036, finite with A0 = +∞; path 1 returns −M2 only after A0 succeeds; every consumer certifies only on strict negativity |
| M3T0-R7-F2 | **RESOLVED** | b_R ≤ b is restricted to b > 0; b_R(0) ≈ 1.49716862376135e-325 |
| M3T0-R6-F1 | **RESOLVED** | k = 1…17 re-executed; k = 1 ratio ≈ 0.9999999999988138 |
| M3T0-R6-F2 | **RESOLVED** | Extreme-helper tests; infinite enclosures never certify; the old overflow mutant fails five cases |
| M3T0-R6-F3 | **RESOLVED** | The cap re-solved exactly: 91910196476947 accepted, the next integer rejected |
| Review 06 remark (5 287-point search) | **RESOLVED** | Still explicitly UNREPRODUCED (a provenance resolution, not a reproduction) |
| Review 06 remark (b*, φ_B) | **RESOLVED** | 7.416912861690675e-309 (stored φ) and 1.1125369292536007e-308 (exact φ) |
| M3T0-R5-F1 | **RESOLVED** | Own exact-product grids and the 17/30-unit counterexamples enclosed; the relative-only mutant fails |
| M3T0-R5-F2 | **RESOLVED** | Subset maxima 0.9527274167782528 / 0.982821819954253 and transition maxima 0.9999999999988586 / 0.9999999999988518 distinguished |
| M3T0-R4-F1 | **RESOLVED** | 1.02021455e-315 against 1.110700085e-315 m/s² at 190 681 km; the superseded-envelope mutant is detected |
| M3T0-R3-F1 | **RESOLVED** | 0.062309014504142814 against 0.06230901450421387 m/s² at 120 km; the allowance-removal mutant is detected |
| M3T0-R2-F1 | **RESOLVED** | Sampled perturbed estimates kept distinct from certified two-body bounds; no combined J2/drag missed-dip proof claimed |
| M3T0-R2-F2 | **RESOLVED** | 48.65837703993666 against 48.658377039936795 m/s² at 79 999.9/80 000 m |
| M3T0-R2-F3 | **RESOLVED** | The zeroed-evidence mutant fails 22 selected cases |
| IM-1 | **RESOLVED** | Axis ablation byte-identical twice; RMS 0.9856650955520649 m |
| IM-2 | **RESOLVED** | need(111 511.96, ∞) = +0.0018399073878806404; need(111 511.97, ∞) = −0.008245909394966729; disposition unchanged |
| M3T0-F1 … F5 | **RESOLVED** | Each re-derived or reproduced individually (F5 on documentary evidence) |
| Review 08 M3 coverage observation | **RESOLVED** | The M3-dropped mutant is detected by the first-stage-infinity check for the intended reason; R9-F1 is a narrower surviving corruption |

The GMAT geodetic-drag discrepancy remains **ESCALATED_FOR_INVESTIGATION** (DR-0029 Q-G2-1/P6). DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

**Reviewer's own validation:**
- checks 01–08: 288/288; red before at `115e747`: 2 failed, 25 passed;
- full pytest: 1185 passed, 3 warnings;
- the M1 and M2 validators: PASS (M2 228/228); both GMAT compares: exit 0;
- the 14 R8 mutants, six earlier mutants and both declared equivalents (a declared subset, not the 87-mutant rerun);
- all nine experiments rerun twice, including GMAT, with all 98 tracked files byte-identical;
- five pinned and 21 spike digests, all matching; the protected-path diff and the result-file diff since `115e747`, both empty;
- the docstring-free AST of `t0_termination.py` unchanged;
- the old bytes of the Review 06, 07 and 08 records an exact prefix of the new ones;
- its own probes: 1 792 C1 and 1 601 C2 exact constructions, 598 exterior near-surface states on the E2 ellipsoid (1 095 rejections, 1 895 finite non-certifications, none certified), 226 force evaluations, 30 adversarial RK4 steps above the floors and 21 E4b boundary evaluations;
- the committed seed-20261022 probe, with every count reproduced.

## New findings
| ID | Severity | Finding | Implementer reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R9-F1 | NOTE | **A finite M3 can be omitted without failing a check.** A mutant that keeps `-min(M2, M3, M4)` when M3 = −∞ but returns `-min(M2, M4)` when M3 is finite passes all 288 checks. With an injected envelope of 10^8 at the first call and 0 after it, at h0 = 200 km and b = B_V1: M2 = 144 867.2696173568, M3 = −2 499 855 380.144757 and M4 = 89 239.71048326683. The code returns need = +2 499 855 380.144757 (not certified), and the mutant returns −89 239.71048326683 (a false certification). The I-11 finite control (`test_r8_finite_injected_envelope_certifies`) always has M4 < M3, so it never makes a finite M3 the minimum (`check_review08.py:224`, `:241`, `:248`; `t0_termination.py:1385`). A test-coverage gap, not a defect in the committed code; the injected envelope is a propagation test, not a physical force | **Reproduced** (`implementer-reproduction/repro_r9f1.py.txt`, `.log`): the same five values exactly, and a second case at h0 = 1 000 km (the mutant certifies there too). The mutant (`r9f1_mutant.diff`) passes all 288 checks in a scratch copy of `docs/`, with the mutated module confirmed loaded (`r9f1_mutant.sh.txt`, `r9f1_mutant_checks.log`). With the A0 = +∞ envelope the mutant still returns +∞, which is why the I-11 regression does not see it | **ACCEPTED, not applied** (I-11 §7: no further correction is authorized) |
| M3T0-R9-F2 | NOTE | **The pole check's exact ellipsoid is not the model's.** `check_review08.py:59` takes A·(1 − F) as the exact polar radius. The height formula and `t0_oracle.py` (`:38`, `:42`) use A·√(1 − E2), with binary64 E2. These differ by 2.4767215814979376e-13 m. At z = fl(b) the mathematical height is −2.0348868076669469e-10 m on the first and −2.0373635292484448e-10 m on the second. So the quotation "−2.03e-10 m" (`t0_termination.py:1319`; `validation.md:833`; the Review 07 amendment and the Review 08 correction section) is the F-defined value; on the model's E2 ellipsoid it rounds to −2.04e-10 m. The interior classification, computed height 0, the rejection transition, the E1 enclosure and every floor are unaffected | **Reproduced** (`implementer-reproduction/repro_r9f2.py.txt`, `.log`): the same three values, and E2 = fl(F(2 − F)). Impact checked: the 37 541 states of the seed-20261022 probe (which also classifies on the F ellipsoid) classify identically on the E2 ellipsoid, 36 769 exterior in both (`r9f2_probe_reclassify.py.txt`, `.log`). The pole check's k = 0…12 outcomes cannot change, since the 2.5e-13 m difference is far below the 2^-30 m grid spacing | **ACCEPTED, not applied** (I-11 §7) |

## Implementer's assessment
- **Both findings are correct.** R9-F1 is a gap in the test I wrote for the Review 08 observation. I made the infinite case M3-dominant but chose a finite control where M3 is never the minimum, so a conditional omission survives. R9-F2 is an imprecision in a check and in a quotation I wrote: I took the F-defined polar radius as "the model's ellipsoid", while the model and the oracle use E2.
- **Neither changes a number, a floor or a certification.** The committed `stage_need` uses M3 in every case. The pole classification is unchanged on either ellipsoid.
- **Proposed correction (for authorization; none applied):**
  1. **R9-F1 (checks only):** add the reviewer's finite first-call-only envelope (10^8, then 0) at several heights, asserting need = −M3 > 0 and that `-min(M2, M4)` would certify. Add the finite-M3 omission as a mutant in the harness.
  2. **R9-F2 (check and documentation):** derive the pole expectation from A²(1 − E2) as E1 and the oracle do. Change the quotation by an appended amendment to −2.04e-10 m (E2 ellipsoid), or name the F-defined ellipsoid explicitly. Preserve the earlier wording.
  3. Rerun the checks, the mutation harness and the record checks. Neither item touches executable model or termination code.
- **The verdict rule permits PASS.** Under I-11 §7 the next steps are the acceptance dossier and the Tech Lead's decision. Whether the two NOTEs are corrected before or after acceptance is for the Tech Lead.
- **Remaining conditions (unchanged):**
  - the force and stage guarantees hold only under A-FP-1 to A-FP-3 (A-FP-2 is unresolved, and E4b depends on it explicitly);
  - the C1/C2-only scope with positive finite mass, cd and area;
  - no overflow;
  - negative two-body energy, no thrust and dt = 10 s;
  - no certified J2-plus-drag missed-dip bound;
  - host measurements on macOS x86_64 only;
  - the GMAT geodetic-drag discrepancy stays escalated;
  - DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

## Correction pass (Authorization I-12, 2026-10-21; appended)
"Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10" authorizes correcting M3T0-R9-F1 and M3T0-R9-F2, full revalidation, and one independent Review 10. Everything above this section is preserved as written, including the Review 09 verdict (PASS, unconditional) and its raw output. T0 remains NOT ACCEPTED.

Preconditions (I-12 §1), verified before any change:
- branch `milestone-3-t0-reference-spike`, with HEAD = origin = `5978bfe` after a fetch, and a clean worktree;
- `86df2c3` is an ancestor, and CI run 39668100686 succeeded;
- the five pinned digests and all 21 VAL-0019 digests match, and no protected path has changed since `86df2c3` (`pinned_digests_before.log`).

**Checks and documentation only.** No executable statement of the model (`t0_model.py`), the oracle (`t0_oracle.py`) or the termination code changed. The docstring-free AST of `t0_termination.py` equals `5978bfe` (`ast_docstring_free_equal.log`), and `t0_model.py` and `t0_oracle.py` are byte-identical. No value, floor, bracket, margin, threshold, constant or reference configuration changed. No defect in the numerical implementation was found.

| Item | Disposition | Correction |
|---|---|---|
| M3T0-R9-F1 (NOTE) | **ACCEPTED; CORRECTED** (checks only; for Review 10 to assess) | `check_review09.py` pins need = −M3 whenever a finite M3 is the stage minimum, through the production `stage_lower_heights` and `stage_need`. This uses the Review 09 counterexample and 14 further cases of both signs, and distinguishes +∞, finite ≥ 0 and certification. Three R9-F1 mutants were added to the harness, among them the reviewer's |
| M3T0-R9-F2 (NOTE) | **ACCEPTED; CORRECTED** (check and documentation; for Review 10 to assess) | The pole reference of `check_review08.py` is now the model's ellipsoid b² = a²(1 − e2) (was A·(1 − F)), with heights to 80 digits. A consistency regression ties it to the model's computed polar radius and the oracle. The quotation −2.03e-10 m is corrected to −2.04e-10 m in the `stage_lower_heights` docstring and the pole-check docstring. Appended amendments in the Review 07 and Review 08 records and VAL-0019 keep the original sentences |

### R9-F1: a finite binding M3
- **The gap.** The Review 08 regression made M3 the minimum only through M3 = −∞, and its finite control always had M4 < M3. So `if math.isfinite(M3): return -min(M2, M4)` passed every check.
- **The regression** (`check_review09.py`). Each case calls `tt.stage_lower_heights` and `tt.stage_need`, with only the force bound injected through their `envelope` argument (10^4 … 10^8 at the first call, 0 after it). It asserts need = −M3 exactly, where the case precondition is that M3 is finite and strictly below M2 and M4.
  - **Review 09 counterexample** (h0 = 200 km, B_V1, 10^8): M2 = 144 867.2696173568, M3 = −2 499 855 380.144757 and M4 = 89 239.71048326683. The code returns need = +2 499 855 380.144757, a finite non-certification. Under the reviewer's mutant the regression fails with `need = -89239.71048326683`, a false certification (`r9f1_mutant_vs_check09.log`).
  - **Negative M3 binding** (at h0 = 200 km, 1 000 km and 10 000 km): the committed code does not certify, and the mutant certifies.
  - **Positive M3 binding** (for example h0 = 1 000 km, 10^4): need = −697 703.7734500183. The step is certified with the M3 margin; the mutant returns −895 407.5469000572.
  - **Three outcomes** at 200 km are classified separately: A0 = +∞ gives need = +∞, 10^8 gives a finite need > 0, and a constant 1 gives a certification.
- **Why no published value moves.** With the default envelope, M4 < M3 < M2 at the heights the check pins, and in every path-2 case of a sampled sweep: 8 835 heights from 55.75 km to 20 000 km, all three vehicles (`m4_binding.log`; a sample, not a proof). `t0_termination_results.json` regenerates byte for byte with M3 dropped (Review 08 implementer reproduction).

### R9-F2: the model's polar radius
- **The model's expression.** `geodetic_iterative` (a = A_WGS84, e2 = E2_WGS84 = fl(F(2 − F))) returns h = p cos φ + z sin φ − a√(1 − e2 sin²φ). At the pole φ = π/2 (sin φ = 1, p = 0), so h = z − fl(a·√(1 − e2)), and fl(a·√(1 − e2)) = fl(b) = `B_WGS84`. `t0_oracle` uses B2 = a²(1 − e2). The model's ellipsoid is therefore defined by the binary64 a and e2, with polar radius a·√(1 − e2). This radius is irrational, and b² is exact.
- **Recomputed at 80 digits.**
  - a·√(1 − e2) − A·(1 − F) = 2.4767215814979376e-13 m.
  - At z = fl(b), the mathematical height is −2.0373635292484448e-10 m on the model's ellipsoid (**−2.04e-10 m**) and −2.0348868076669469e-10 m on the A·(1 − F) ellipsoid.
  - [0, 0, fl(b) + k·2^-30] has mathematical height k·2^-30 − 2.0373635e-10 m, and 9.11e-9 m at k = 10 on either ellipsoid.
- **Unchanged.** The point is inside on both ellipsoids, its computed height is 0, and the k = 9 → 10 transition and E1 are unchanged. The seed-20261022 probe's 37 541 states classify identically on both ellipsoids (Review 09 implementer reproduction).
- **The consistency regression** (`check_review09.py`) asserts the following:
  - fl(a·√(1 − e2)) = fl(b), and the model's pole height equals z − fl(a·√(1 − e2)) at four heights;
  - the reference b² of `check_review08.py` equals a²(1 − e2) exactly and the oracle's B2 to 58 digits;
  - its 13 pole heights equal the 80-digit model heights (to 1e-40 m) and the oracle (to 1e-30 m);
  - fl(b) − b lies in (−2.03737e-10, −2.03736e-10) m, which separates the two ellipsoids, and [0, 0, fl(b)] is rejected as interior by the oracle.

  The pole check in `check_review08.py` also asserts that interval.

### Evidence (`docs/reviews/raw/M3-T0-review09-findings-correction-evidence/`)
- **Red before.** `check_review09.py` against the unmodified `5978bfe` tree fails 3 and passes 23 (`checks09_before_5978bfe.log`). The 3 failures are the pole reference, the docstrings and the records. The 23 passes are the R9-F1 contract checks, which pin the committed implementation's correct behaviour. For R9-F1 the red state is shown by mutation: the reviewer's mutant passes all 288 earlier checks (Review 09 implementer reproduction) and fails 16 R9-F1 checks of `check_review09.py` (`r9f1_mutant_vs_check09.log`).
- **Green after.** `check_review01.py` … `check_review09.py`: 314 passed, 0 failed (288 earlier + 26 new; `checks_after.log`).
- **Mutation** (`mutation_check_review02.py`, run against all nine check files): the control passes 314/314; all 100 non-equivalent mutants (87 earlier + 13 new R9) are detected, each by at least one of its declared checks; 2 are declared equivalent (`r6f2_float_nan_accepted`, `script_two_body_without_stationary_points`, as before); none survive (`mutation_check_review09.json`).
- **Smoke run** of the R9 mutants against the checks they target (`smoke_r9.py.txt`, `smoke_r9.log`).
- **No executable change.** The docstring-free AST of `t0_termination.py` equals `5978bfe` (`ast_docstring_free_equal.log`), and `t0_termination_results.json` regenerates byte for byte (`termination_regenerated.log`).
- **Preconditions:** `pinned_digests_before.log`.

### Unresolved assumptions and conditional guarantees (unchanged by this pass)
- **A-FP-2** (libm accuracy) remains an unresolved, explicitly conditional assumption, measured on macOS x86_64 only. E4b depends on it explicitly (LIBM_ULP ≤ 91910196476947).
- **A-FP-1** is checked at run time on this host only, and A-FP-3 is stated as before. Host measurements are not platform guarantees.
- **Contract scope.** C1 or C2 vehicles constructed from a positive finite binary64 mass, cd and area; no overflow.
- **Conditions of the floors.** Sufficient, not necessary; under A-FP-1 to A-FP-3, for computed committed heights > β, bound states with negative two-body energy, no thrust and dt = 10 s. There is no certified J2-plus-drag missed-dip bound.
- **Unchanged.** The GMAT geodetic-drag discrepancy remains escalated (DR-0029 Q-G2-1); IM-2 is unchanged; DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

### Validation
Recorded in the validation commit that follows this correction commit.

### Validation of the correction commit `cc82ae7` (appended 2026-10-21)
Evidence is in `docs/reviews/raw/M3-T0-review09-findings-correction-evidence/`. Scratch, home and temporary paths are redacted. Environment: macOS 26.2 x86_64 (the M1/M2 reference host), Python 3.12.15, the locked `uv` environment.

| Check | Result |
|---|---|
| Red before, green after | At `5978bfe`, `check_review09.py` fails 3 of 26 (pole reference, docstrings, records) (`checks09_before_5978bfe.log`). The reviewer's finite-only M3 mutant fails 16 R9-F1 checks (`r9f1_mutant_vs_check09.log`). At `cc82ae7`, all 26 pass |
| Review 01–09 checks | `check_review01.py` … `check_review09.py`: 314/314 pass, 288 earlier plus 26 new (`checks_after.log`; again in the reproducibility clone) |
| Mutation tests | Control 314/314. 100/100 non-equivalent corruptions are detected by a declared check: the 87 earlier mutants and the 13 R9 mutants, including `r9f1_m3_dropped_when_finite`. **Survivors: none.** **Equivalent: 2**, the same two as before (`r6f2_float_nan_accepted`, `script_two_body_without_stationary_points`) (`mutation_check_review09.json`) |
| Termination results | `t0_termination.py` regenerates `t0_termination_results.json` byte for byte (`termination_regenerated.log`); its docstring-free AST equals `5978bfe` (`ast_docstring_free_equal.log`) |
| M1 Proof (`run_m1_proof.sh`, fresh clone at `cc82ae7`) | PASS, 9/9 steps; `working_tree_clean_excluding_evidence: yes` (`m1_proof_run.log`). A separate full pytest run in the same clone gave 1185 passed, 3 warnings, unchanged from I-11 (`pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`m2_proof_run.log`, `m2_proof_stdout.txt`). The rewritten `m2_final_states_record.json` differs from the committed one only in its `revision` field and the record's own `sha256` field, as at I-11 |
| Pinned and spike digests | The five pinned artifacts equal `86df2c3` byte for byte, and all 22 VAL-0019 spike digests match at `cc82ae7` (`pinned_digests.log`). The count is 22, not 21: this pass adds `check_review09.py` and updates the `t0_termination.py` (docstring), `check_review08.py` and `mutation_check_review02.py` entries; VAL-0019 keeps their previous digests |
| Production and protected files | `git diff --name-only 86df2c3 cc82ae7 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty |
| T0 reproducibility | A third fresh clone ran every T0 experiment twice, including the GMAT harness, `t0_height_error.py` and `t0_axis_ablation.py`. `git status` was empty after each run, so all 99 tracked experiment files are byte-identical; the checks then passed 314/314 (`reproducibility_twice.log`) |
| Numerical outputs vs the I-11 baseline | No tracked `*_results.json` or `.csv` file under `docs/science/experiments/m3-t0/` differs between `f04f995` (I-11 validation) and `cc82ae7`, so **the numerical outputs are byte-identical** |
| CI on `cc82ae7` | Run 39695797213 (https://github.com/guillermoMartin96/tars/actions/runs/39695797213): all four jobs succeeded (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`). CI does not collect the T0 checks (`testpaths = ["tests"]`), so CI does not validate them |
| Platform limitations | All T0 measurements and checks ran on macOS x86_64 only. A-FP-1's gradual-underflow check and the A-FP-2 libm measurements are host measurements, not platform guarantees. The M4-binding statement for the default envelope rests on a sampled sweep (`m4_binding.log`) and on the byte-identical regeneration with M3 dropped; it is not a proof |
