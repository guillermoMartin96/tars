# M3 T0 Review 07 (independent review of the Review 06 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15b6d-4637-7e02-a01c-400a13384432`, 2026-10-20 22:27–23:02 UTC.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review07-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`03571961bc72cd41fe853ce0c4d686d783ee6938`**, the validation record of the correction commit `9e44850c6c6594a63638027d24c77aeb484eb566`.
- **Environment.** The review ran in a fresh GitHub clone with its own `uv sync --locked` environment. It had a private GMAT R2026a copy, whose console digest (`1162803d…52e2`) and atmosphere table (`75762f67…a85e`) match the installation; the reviewer checked both.
- **Prompt.** It was kept outside the repository during the review. It reproduces Authorization I-9 and Authorization I-8 verbatim, and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It presents the I-8 corrections as claims to verify. Every commit identifier of the pass under review is a full SHA.
- **Building the prompt (I-9 §2).** The Review 07 candidate prompt prepared after I-8 was inspected before use and corrected:
  - its "What to review" section was still the Review 06 list, and was rewritten from I-9 §3–§7;
  - stale counts and paths were fixed: the reviews list, the evidence description, and the reviewer-evidence and earlier-correction-evidence directories;
  - the committed seeded probe was named as re-runnable, and both CI run identifiers were given with the note that the reviewer cannot access CI;
  - the resolution table gained the two Review 06 remarks;
  - the ledger now asks for the environment.
- **Preconditions (I-9 §1), checked by the implementer before the review:**
  - branch `milestone-3-t0-reference-spike`, HEAD and origin both at `0357196`, clean tree;
  - CI succeeded on `9e44850` (run 39489593015) and `0357196` (run 39499192586), all four jobs each;
  - the five pinned digests match `86df2c3`, and no protected path changed since then.

  The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-9 — M3 T0 Independent Review 07" (Tech Lead, 2026-10-20).

**Files:**
- prompt: `raw/M3-T0-codex-review07-prompt.md`;
- raw output: `raw/M3-T0-codex-review07.md`. This is the reviewer's saved report `review_scratch/M3-T0-codex-review07.md`, which equals the CLI's final message plus a trailing newline. It contains no absolute path;
- reviewer scripts and logs: `raw/M3-T0-codex-review07-evidence/` (`*.py.txt`; `command-ledger.md`; `mutation-subset.json`; `reproduction-commands.json`; the reviewer's own checksum list `reviewer-SHA256SUMS.txt`, over its unredacted files). Absolute paths are redacted to `<clone>`/`<review-root>`/`<scratch>`/`<home>`/`<tmp>`. `SHA256SUMS` covers the committed files;
- the implementer's reproduction: `raw/M3-T0-codex-review07-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of three diffs (`git diff 30a4e8d..0357196`, its focused diff, and `git diff 86df2c3..0357196`; 17 MB);
- its red-before tree (`30a4e8d` docs with the current `check_review06.py`; `red-before.log` is kept);
- its text copy of the earlier reviews;
- `__pycache__`.

**Verdict:** **REQUEST_CHANGES**, with two new NOTEs. No BLOCKER, MAJOR or MINOR finding was raised. The verdict follows from the prompt's rule that every resolution-table item must be RESOLVED: R6-F2 is PARTIALLY RESOLVED, through R7-F1.

**Stop rule applied (I-9 §8):**
- Both findings are recorded with their severity, and both were reproduced independently by the implementer.
- The complete output is preserved.
- **The findings are not corrected, Review 08 is not started, and no T0 acceptance is prepared.** Authorization is requested.
- Not done:
  - not merged, and T1 and T2 not started;
  - DR-0029 P1–P10 and DR-0028 P6(b) not decided;
  - the GMAT geodetic-drag discrepancy not closed: it stays escalated;
  - no protected artifact, test or threshold changed.

## Resolution assessed by Review 07
| Item | Review 07 | Basis (reviewer) |
|---|---|---|
| M3T0-R6-F1 | **RESOLVED** | Positive-mass proof, monotonic zero join, directed B_R, the 17 regressions and further ratio and force probes |
| M3T0-R6-F2 | **PARTIALLY RESOLVED** | Helpers and the original exception fixed; no false certification found. The universal "need = +∞" statement is not true (R7-F1) |
| M3T0-R6-F3 | **RESOLVED** | Exact affine cap and limit, both sides of the boundary, append-only reclassification |
| Review 06 provenance remark (5 287-point search) | **RESOLVED** | Old text preserved; the appended Review 04 amendment marks the claim UNREPRODUCED and historical |
| Review 06 b*/φ_B remark | **RESOLVED** | Both labelled values reproduced exactly; append-only Review 05 amendment |
| M3T0-R5-F1 | **RESOLVED** | C1 product and quotient and the C2 clamped mass bounds cover subnormal conversions; R(0) completes the missing endpoint; both original failures covered |
| M3T0-R5-F2 | **RESOLVED** | Subset and transition-scan maxima recompute and are distinguished |
| M3T0-R4-F1 | **RESOLVED** | Mixed relative and absolute force errors and W persist; the zero-density cutoff bounds the absolute part; R now includes b = 0 |
| M3T0-R3-F1 | **RESOLVED** | Selection-height widening covers every reachable band across downward jumps; oracle checks pass |
| M3T0-R2-F1 | **RESOLVED** | Perturbed rows are sampled estimates, separated from the certified two-body bound |
| M3T0-R2-F2 | **RESOLVED** | Density and the height-dependent co-rotation speed are maximized together; per-band derivative negative |
| M3T0-R2-F3 | **RESOLVED** | Evidence recomputed with coverage assertions; mutations genuinely fail |
| IM-1 | **RESOLVED** | Axis ablation reproduces byte for byte (quadratic-only RMS ≈ 0.98567 m) |
| IM-2 | **RESOLVED** | 111 511.96 m fails and 111 511.97 m satisfies the condition; the owner-directed disposition is preserved |
| M3T0-F1, F2, F3, F4, F5 | **RESOLVED** | Re-derived or reproduced individually (F5 on documentation evidence) |

The reviewer states: "'Resolved' here assesses the defect under the disclosed scientific contract; it does not approve the remaining owner decisions or assert a universal libm guarantee."

## New findings
| ID | Severity | Finding | Implementer reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R7-F1 | NOTE | **An infinite envelope does not always give need = +∞.** `stage_lower_heights` returns before M4 when M2 ≤ 0 (`t0_termination.py:1339`), and `stage_need` then returns −M2 (`:1353`), which can be finite. The universal statement is at `t0_termination.py:1304`, `M3-T0-review-06.md:126`, `validation.md:822` and `:939`, and DR-0029 `:101` and `:476`. For h0 = 1.0 m and b = 2^-1074: A0 = +∞, M3 = −∞, M2 = −55992.318990613036, M4 = None, need = 55992.318990613036. The step is still **not certified** (need > 0). No floor, force bound or certification is wrong; the stated semantics are | **VERIFIED** (`implementer-reproduction/r7_repro.py.txt`, `r7_repro.log`): the same values at h0 = 1 m and h0 = 1000 m (need 54988.92 m), for b = 2^-1074 and b = 0; need = +∞ at h0 = 1e7 m. The reviewer's `test_noncert_contract.py` fails the same way on the implementer's worktree (`reviewer_test_noncert_on_0357196.log`) | **ACCEPTED**, not applied |
| M3T0-R7-F2 | NOTE | **Two summaries keep "b_R ≤ b" without the b > 0 restriction** (`t0_termination.py:612` in the E4 summary, and `:963` in the `drag_envelope` docstring, which extends the sentence to b = 0). At b = 0, B_R = φ_B/R(0) > 0, so B_R ≤ b is false. The detailed `envelope_ballistic_coefficient` docstring and the Review 06 correction record (`M3-T0-review-06.md:117`) state the b = 0 exception correctly. This is documentation only; the implemented bound needs only R ≥ cd·area/mass | **VERIFIED**: `envelope_ballistic_coefficient(0.0, 2.2, 15.0)` = 1.497…e-325 > 0, while B_R ≤ b holds for b = 2^-1074, 2 × 2^-1074, 1e-310 and B 25.8 (`r7_repro.log`) | **ACCEPTED**, not applied |

## Implementer's validation at the reviewed commit (I-9 §7)
The reviewer ran the following itself (raw output, ledger):
- checks 01–06: 238/238;
- red-before at `30a4e8d`: 55 failed, 26 passed;
- full pytest: 1185 passed, 3 warnings;
- the M1 and M2 validators: PASS, 228 M2 results;
- both GMAT compares: PASS;
- all nine experiments rerun twice in its clone, with all 96 files byte-identical;
- its own probes: 2 005 exact directed-rounding cases, 2 896 ratio cases (768 with b = 0), 1 606 monotonicity comparisons, 23 force states and 54 E4b zero-force states;
- the committed seeded probe, reproduced;
- seven mutations, all detected: five supplied R6 mutants and two new ones;
- the five pinned artifacts and the 19 VAL-0019 digests, all matching.

The Proof wrappers write into `proof/`, so the reviewer may not run them. The implementer ran them in fresh clones at `0357196`:

| Check | Result |
|---|---|
| M1 Proof (`run_m1_proof.sh`, fresh clone at `0357196`) | PASS, 9/9 steps; clean: yes (`implementer-reproduction/m1_proof_run.log`). Full pytest in the same clone: 1185 passed, 3 warnings (`implementer-reproduction/pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`implementer-reproduction/m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Protected paths and pinned digests | `git diff --name-only 86df2c3 0357196 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty; the five pinned artifacts equal `86df2c3` |

**Environment and limits of the numerical evidence.**
- **Host.** All runs used macOS 26.2 (Darwin 25.2.0) x86_64, the M1/M2 reference host, with Python 3.12.15, NumPy 2.5.3 and SciPy 1.18.1 from `uv.lock`. The reviewer could not query the CPU model.
- **Reach of the measurements.** Host measurements (gradual underflow under A-FP-1, libm accuracy under A-FP-2) are not platform guarantees. No other OS, CPU or library backend was tested.
- **Not independently verified by the reviewer:**
  - CI;
  - the complete Proof-wrapper runs;
  - the full 61-mutant rerun;
  - the original 5 287-point search, which remains unreproduced.

## Implementer's assessment
- **Both findings are correct.**
  - **R7-F1** is an overstatement in the I-8 records and in one docstring. The early return predates I-8: it was added in `489d4e7` (the Review 03 correction), for the case where "the k2 input may already be below the edge". It always gives need ≥ 0, so it never certifies. I-8 described only the path through M4.
  - **R7-F2** is a stale clause. The I-8 pass corrected the inequality in `envelope_ballistic_coefficient` and in the Review 06 record, but not in the two summaries.
- **Why the verdict holds.** Neither finding changes a number, a floor or the soundness of a bound. The resolution-table rule still makes R6-F2 PARTIALLY RESOLVED and the verdict REQUEST_CHANGES, and that rule is applied as written.
- **Proposed correction (for authorization; none applied):**
  1. **R7-F1:**
     - either normalize `stage_need` to return +∞ whenever the enclosure is unbounded (A0, A2 or s2 infinite, or any M_k = −∞), or keep the code and document both non-certification paths: need = +∞ via M4, and need = −M2 ≥ 0 via the early return;
     - correct `t0_termination.py:1304`, the Review 06 record (by an appended note), VAL-0019 and DR-0029;
     - add a regression at h0 = 1 m and h0 = 1000 m with b = 2^-1074 and b = 0, and a mutant that reverses the chosen behaviour.

     The floors are unaffected: the bisection accepts only need < 0.
  2. **R7-F2:** qualify "b_R ≤ b" with b > 0 at `t0_termination.py:612` and `:963`, state the b = 0 case beside it, and add a static check.
  3. Rerun the checks, the mutation harness, M1/M2 Proof, the digests, reproducibility and CI. Any Review 08 needs authorization.
- **Remaining conditions (unchanged):**
  - the force and stage guarantees hold only under A-FP-1 to A-FP-3 (A-FP-2 is unresolved, and E4b depends on it explicitly);
  - the C1/C2-only scope with positive finite mass, cd and area;
  - no overflow;
  - negative two-body energy, no thrust and dt = 10 s;
  - no certified J2-plus-drag missed-dip bound;
  - the GMAT geodetic-drag discrepancy stays escalated;
  - DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

## Correction pass (Authorization I-10, 2026-10-20; appended)
"Authorization I-10 — M3 T0 Review 07 Corrections and Independent Review 08" authorizes correcting only M3T0-R7-F1 and R7-F2, then an independent Review 08. Everything above this section is preserved as written. The statuses Review 07 gave (PARTIALLY RESOLVED for R6-F2) are **not** changed here; whether they are now resolved is for Review 08 to judge.

Preconditions (I-10 §1), verified before any change: branch `milestone-3-t0-reference-spike`, HEAD = origin = `72f9e00` after a fetch, clean worktree, the Review 07 evidence committed with its `SHA256SUMS` verified, CI run 39515314270 green on all four jobs, the five pinned digests and all 19 VAL-0019 digests match, no protected path changed since `86df2c3` (`pinned_digests_before.log`).

**Both corrections are documentation only.** No executable statement changed: `t0_termination.py` with every docstring removed has the same AST as at `72f9e00` (`ast_docstring_free_equal.log`). No value, floor, bracket, margin, threshold or published result changed. Neither is a numerical algorithm fix.

| Finding | Disposition | Correction |
|---|---|---|
| M3T0-R7-F1 (NOTE) | **ACCEPTED; CORRECTED** (documentation; for Review 08 to assess) | The `stage_lower_heights` docstring and the records now state both non-certification paths (below). The code is kept, not normalised to +∞: I-10 §2 forbids changing numerical behaviour |
| M3T0-R7-F2 (NOTE) | **ACCEPTED; CORRECTED** (documentation) | "b_R ≤ b" is qualified with b > 0 in the E4 summary and the `drag_envelope` docstring, with the b = 0 case beside it |

### R7-F1: the stated non-certification semantics
The implementation, unchanged since the Review 03 correction (`489d4e7`) for this path:
- **Certification.** A step from computed height h0 is certified only when need(h0) < 0. The floor bisection (`need(lo) > 0 > need(hi)`, then `need(mid) < 0`) and `libm_sensitivity` (`need >= 0` is a failure) accept nothing else. Every need ≥ 0, finite or +∞, is a non-certification.
- **Path 1, M2 ≤ 0.** `stage_lower_heights` returns before A2 (the k2 input may already be below the edge), with A2, s3, L4 and M4 = None, and `stage_need` returns −M2: **finite and ≥ 0**. M2 = (1 − α)·L2 − β with L2 = H0 − 5(1 + u)²V − u·R0 − 2η₀ uses h0 and the constants only, not b or the envelope. With the published constants M2 ≤ 0 up to h0 = 55 749.393 m (55 749.39300208564 is the largest such binary64) for every vehicle. So this need is finite even when A0 = +∞: the reviewer's h0 = 1 m, b = 2^-1074 gives A0 = +∞, M3 = −∞ and need = 55 992.318990613036 m.
- **Path 2, M2 > 0.** need = −min(M2, M3, M4). An envelope of +∞ at A0 makes s2 = +∞, and the envelope at s2 = +∞ is +∞ again, so A2 = s3 = +∞ and L4 = M4 = −∞. A stage value beyond the binary64 range is rounded outward by `_up`/`_dn` to ±∞ with the same effect. Either gives **need = +∞**. Otherwise need is finite; it may still be ≥ 0 (not certified).
- **Other inputs.** The vehicle b = +∞ is drag-free (envelope 0) and has a finite need on both paths. A non-finite h0, or b NaN or < 0, raises `ValueError` on both paths, because the envelope is evaluated for A0 before the M2 test.
- Corrected in: the `stage_lower_heights` docstring; the VAL-0019 body and DR-0029 P1 body (inline, "corrected after Review 07"); the VAL-0019 and DR-0029 Review 07 correction logs (the Review 06 log entries are kept as written and qualified there); and an amendment appended to the Review 06 record.

### R7-F2: b_R ≤ b
- For b > 0, b_R ≤ b, and b_R is the same binary64 b where the conversion is normal. At b = 0, b_R = φ_B/R(0) > 0 = b (1.497e-325 for cd = 2.2, area = 15 m²). The envelope needs only R ≥ cd·area/mass, which holds at b = 0 (Review 06 R6-F1). Corrected at the E4 summary (`t0_termination.py`, formerly line 612) and the `drag_envelope` docstring (formerly line 963). `envelope_ballistic_coefficient` already stated it correctly.
- **Observation, not corrected (outside I-10's scope).** The module docstring of `check_review05.py` (line 9) still describes the Review 05 correction as "the envelope uses b_R = phi_B / R <= b". It was written when b = 0 raised, and describes that pass. It is a check file's historical summary, not part of the envelope's contract; I-10 names two statements, so it is left as written and reported here.

### Implementer's observation (not a finding of Review 07; not corrected)
A computed h0 ≤ β = 8.877691069434738e-09 m makes H0 < 0, and the envelope raises `ValueError` ("defined above the lower edge only"). For h0 so negative that b_lower + H0 ≤ 0 (b_lower = 6 356 752.314 m; for example h0 = −6.4e6 m or −1e308 m) the Decimal square root in V raises `decimal.InvalidOperation` instead. Both raise, and neither certifies. Such an h0 is not the computed height of a state in the domain (outside the ellipsoid), and the docstring claims nothing for it.

### Evidence (`docs/reviews/raw/M3-T0-review07-findings-correction-evidence/`)
- **Red before.** The new `check_review07.py` (23 checks) on the unmodified `72f9e00` tree: 3 fail and 20 pass (`checks07_before_72f9e00.log`). The 3 failures are the record and docstring checks (`test_r7f1_docstring_states_both_non_certification_paths`, `test_r7f1_records_state_both_paths`, `test_r7f2_docstrings_qualify_b_r_at_most_b`). The 20 passes are the contract checks. They pass because the implementation did not change: they pin its behaviour, including both Review 07 counterexamples, and fail if the semantics change (mutation below). This is the expected pattern for a documentation-only correction; it is not presented as a numerical fix.
- **The reviewer's contract test** (`test_noncert_contract.py` from the Review 07 evidence, which asserts the superseded universal need = +∞ claim) still fails on the corrected tree with need = 55992.318990613036 (`reviewer_test_noncert_after.log`): the behaviour is unchanged, and the old claim stays false.
- **Green after.** `check_review01.py` … `check_review07.py`: 261/261 (`checks_after.log`).
- **Mutation** (`mutation_check_review02.py`, run against all seven check files): the control passes 261/261; 73 of 73 non-equivalent corruptions are detected by a declared check; the 2 declared equivalents are unchanged (`mutation_check_review07.json`). The 14 new R7 mutants cover:
  - R7-F1 contract: the early-return need normalised to +∞, its sign flipped (a false certification), the early return removed, an infinite need clamped to MAX, and `_dn` not rounding below −MAX outward to −∞;
  - R7-F1 text: the universal claim restored in the docstring, the edge misquoted, the Review 06 amendment removed, and the VAL-0019 and DR-0029 body corrections reverted;
  - R7-F2: both summaries reverted, b_R = b returned at b = 0, and b_R one ulp above b.

  A first smoke run of the R7 mutants against `check_review07.py` alone left one survivor: the VAL-0019 body revert, which the new log text still masked. The record check now excludes the logs, and the full run detects it (`smoke_r7.py.txt`, `smoke_r7.log` after the fix).
- **Adversarial probe** (seed 20261021; `adversarial_r7.py.txt`, `adversarial_r7.log`): 4 000 random (h0, b) cases, h0 from 1 m to 3 × 10^9 m with a concentration at the early-return edge, b from 0 through subnormals to +∞. Path 1: 1 391 cases (727 with A0 = +∞); path 2: 2 609 (1 212 with an infinite envelope); 1 014 certified. Every case satisfies the corrected contract: no NaN; certified only with finite A0 and A2; need = −M2 finite and ≥ 0 on path 1; need = +∞ on path 2 with an infinite envelope; M2 identical across vehicles for 300 heights; and b_R ≤ b for b > 0, b_R > 0 at b = 0, on 18 969 random vehicle shapes.
- **No executable change.** The docstring-free AST of `t0_termination.py` equals `72f9e00` (`ast_docstring_free_equal.log`, `ast_equal.py.txt`; the diff is `t0_termination_docstring.diff`). `t0_termination.py` regenerates `t0_termination_results.json` byte for byte (`termination_regenerated.log`).
- **Preconditions:** `pinned_digests_before.log` (`digests.py.txt`).

### Unresolved assumptions and conditional guarantees (unchanged by this pass)
- **A-FP-2** (libm accuracy) remains an unresolved, explicitly conditional assumption, measured on macOS x86_64 only; E4b depends on it explicitly (LIBM_ULP ≤ 91910196476947). A-FP-1 (IEEE binary64 with gradual underflow) is checked at run time on this host only. A-FP-3 is stated as before.
- **Contract scope.** C1 or C2 from a positive finite binary64 mass, no overflow; not arbitrary independently supplied (mass, b) pairs.
- **Conditions of the floors.** Sufficient, not necessary; under A-FP-1 to A-FP-3, for computed committed heights, bound states with negative two-body energy, no thrust and dt = 10 s. There is no certified J2-plus-drag missed-dip bound.
- **Unchanged.** The GMAT geodetic-drag discrepancy remains escalated (DR-0029 Q-G2-1); IM-2 is unchanged; DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

### Validation
Recorded in the validation commit that follows this correction commit.

### Validation of the correction commit `9afbbbf` (appended 2026-10-20)
Evidence is in `docs/reviews/raw/M3-T0-review07-findings-correction-evidence/`. Scratch, home and temporary paths are redacted. Environment: macOS 26.2 x86_64 (the M1/M2 reference host), Python 3.12.15, the locked `uv` environment.

| Check | Result |
|---|---|
| Review 01–07 checks | `check_review01.py` … `check_review07.py`: 261/261 pass (`checks_after.log`; again in the reproducibility clone). Red before, at `72f9e00`: `check_review07.py` 3 of 23 fail, all on the docstring and records (`checks07_before_72f9e00.log`) |
| Mutation tests | Control 261/261; 73/73 non-equivalent corruptions detected by a declared check (all R4–R6 mutants and the 14 R7 mutants); 2 declared equivalent with an establishing check (`mutation_check_review07.json`) |
| Termination results | `t0_termination.py` regenerates `t0_termination_results.json` byte for byte (`termination_regenerated.log`); the docstring-free AST equals `72f9e00` (`ast_docstring_free_equal.log`) |
| M1 Proof (`run_m1_proof.sh`, fresh clone at `9afbbbf`) | PASS, 9/9 steps; `working_tree_clean_excluding_evidence: yes` (`m1_proof_run.log`). A separate full pytest run in the same clone: 1185 passed, 3 warnings (`pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Pinned digests | The five pinned artifacts equal `86df2c3` byte for byte, and all 20 VAL-0019 spike digests match (`pinned_digests.log`) |
| Production and protected files | `git diff --name-only 86df2c3 9afbbbf -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty |
| T0 reproducibility | A third fresh clone ran every T0 experiment twice, including the GMAT harness, `t0_height_error.py` and `t0_axis_ablation.py`. `git status` is empty after each run, so all 97 tracked experiment files are byte-identical; the checks then pass 261/261 (`reproducibility_twice.log`) |
| CI on `9afbbbf` | Run 39537301986 (https://github.com/guillermoMartin96/tars/actions/runs/39537301986): all four jobs succeeded (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`). CI does not collect the T0 checks (`testpaths = ["tests"]`) |
| Platform limitations | All T0 measurements and checks ran on macOS x86_64 only. A-FP-1's gradual-underflow check and the A-FP-2 libm measurements are host measurements, not platform guarantees |

### Amendment (Authorization I-11, Review 08 M3T0-R8-F1)
Appended 2026-10-21; the correction-pass text above is kept as written. Review 08 M3T0-R8-F1 shows that the correction pass described the existing behaviour incompletely, and that one sentence of it is false:
- **The false sentence.** Under "Implementer's observation" above: "Such an h0 is not the computed height of a state in the domain (outside the ellipsoid), and the docstring claims nothing for it." This is false. Strictly exterior bound states reach a computed h0 ≤ β: r = [a + k·2^-30, 0, 0] m, v = 0, for k = 1 … 9 has mathematical and computed height k·2^-30 m ≤ β = 8.877691069434738e-09 m (the reviewer's case is k = 1, r = [nextafter(a, +∞), 0, 0], h = 2^-30 m). For those states `stage_need` raises `ValueError`, for B_V1 and for the drag-free vehicle alike. At k = 10 (computed h0 = 9.31e-9 m > β) it returns need = 55 993.323394842984 m for both.
- **The incomplete statements.** "Path 1, M2 ≤ 0" (need = −M2, finite and ≥ 0) and "Other inputs" (the drag-free vehicle has a finite need on both paths) hold for a computed h0 > β only. A computed h0 ≤ β, including at the ellipsoid surface (computed h0 = 0), raises before the M2 test.
- **Mathematical and computed height.** The rejection is decided by the computed height, which is not the mathematical height (E1). On the equator near a the two coincide; at the pole, [0, 0, fl(b)] lies inside the ellipsoid (mathematical height −2.03e-10 m) with computed height 0, and [0, 0, fl(b) + 10·2^-30] has mathematical height 9.11e-9 m and computed height 9.31e-9 m.
- **What is unchanged.** The very negative case (b_lower + H0 ≤ 0, `decimal.InvalidOperation`) stays outside the exterior-state domain: by E1 the computed height of an exterior state exceeds −β. The rejection never certifies, so no floor, bound or certification changes. The behaviour itself is unchanged; only its description is corrected (`t0_termination.py`, `stage_lower_heights` docstring). Checks: `check_review08.py`. Dispositions: `docs/reviews/M3-T0-review-08.md`.

### Amendment 2 (Authorization I-12, Review 09 M3T0-R9-F2)
Appended 2026-10-21 under "Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10". The amendment above (I-11) is kept as written. One quotation in it is corrected here:
- **The pole height.** "[0, 0, fl(b)] lies inside the ellipsoid (mathematical height −2.03e-10 m)" used the flattening-defined polar radius A·(1 − F). The model's geodetic height (`geodetic_iterative`, with the binary64 a = A_WGS84 and e2 = E2_WGS84) and `t0_oracle` (B2 = a²(1 − e2)) define the ellipsoid by a and e2: the polar radius is a·√(1 − e2), which is 2.48e-13 m (2.4767215814979376e-13 m) larger than A·(1 − F). On the model's ellipsoid the mathematical height of [0, 0, fl(b)] is −2.0373635292484448e-10 m, that is **−2.04e-10 m** (−2.0348868076669469e-10 m on the A·(1 − F) ellipsoid).
- **What is unchanged.** The point is inside on either ellipsoid, and its computed height is 0. The point [0, 0, fl(b) + 10·2^-30] still has mathematical height 9.11e-9 m. No classification, rejection, floor or certification changes. Evidence: `check_review09.py` and `docs/reviews/M3-T0-review-09.md` (correction pass).
