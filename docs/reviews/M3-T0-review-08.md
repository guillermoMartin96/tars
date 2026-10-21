# M3 T0 Review 08 (independent review of the Review 07 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15cda-1fe5-7292-99a6-5c56c9bcc228`, 2026-10-21 05:06–05:36 UTC.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review08-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`95fff220ea164f2d837005a68f881fbded7c624c`**, the validation record of the correction commit `9afbbbf9bd274930cff9c5b777420062ed9c3d42`.
- **Environment.** The review ran in a fresh GitHub clone with its own `uv sync --locked` environment. It had a private GMAT R2026a copy, whose console digest (`1162803d…52e2`) and atmosphere table (`75762f67…a85e`) match the installation; the implementer checked both before the review, and the reviewer checked them again.
- **Prompt.** It was kept outside the repository during the review. It reproduces Authorization I-10 verbatim and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It lists every earlier finding with its current disposition, presents the I-10 corrections as claims to verify, and requires individual reassessment of R7-F1, R7-F2, every earlier finding, both Review 06 remarks and the escalated discrepancy, and adversarial falsification beyond sweeps (I-10 §6). Every commit identifier of the pass under review is a full SHA.
- **Preconditions (I-10 §6: "only after corrections and validation pass"), checked by the implementer before the review:**
  - branch `milestone-3-t0-reference-spike`, HEAD and origin both at `95fff22`, clean tree;
  - the validation of `9afbbbf` recorded in `95fff22` (checks 261/261; mutation 73/73; M1 Proof 9/9; M2 Proof 20/20; pytest 1185; pinned and spike digests; 97 files reproduced twice);
  - CI succeeded on `9afbbbf` (run 39537301986) and `95fff22` (run 39543277180), all four jobs each.

  The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-10 — M3 T0 Review 07 Corrections and Independent Review 08" (Tech Lead, 2026-10-20).

**Files:**
- prompt: `raw/M3-T0-codex-review08-prompt.md`;
- raw output: `raw/M3-T0-codex-review08.md`. This is the reviewer's saved report `review_scratch/M3-T0-codex-review08.md`, which equals the CLI's final message plus a trailing newline. It contains no absolute path;
- reviewer scripts and logs: `raw/M3-T0-codex-review08-evidence/` (`*.py.txt`; `command-ledger.md`; the mutation JSON files; the reviewer's own checksum list `reviewer-SHA256SUMS.txt`, over its unredacted files). Absolute paths are redacted to `<clone>`/`<review-root>`/`<scratch>`/`<home>`/`<tmp>`. `SHA256SUMS` covers the committed files;
- the implementer's reproduction: `raw/M3-T0-codex-review08-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of `git diff 72f9e00..95fff22` (`correction.diff`) and `git diff 86df2c3..95fff22` (`full.diff`; 9.7 MB together);
- its concatenated copy of the decision registers (`decision-registers.txt`) and its copy of `t0_termination.py` at `72f9e00` (`old_termination.py`);
- its red-before tree (`before72/`, `72f9e00` docs with the current `check_review07.py`; `red-before.log` is kept) and its control and 23 mutated trees (`mutants/`, 735 MB; the mutation logs and JSON are kept);
- `__pycache__`.

**Verdict:** **REQUEST_CHANGES**, with one new NOTE. No BLOCKER, MAJOR or MINOR finding was raised. The verdict follows from the prompt's rule that every resolution-table item must be RESOLVED: R7-F1 is PARTIALLY RESOLVED, through R8-F1. The reviewer found no false certification, no deficient force envelope and no unsafe published floor.

**Stop rule applied (I-10 §7):**
- The finding is recorded with its severity, and it was reproduced independently by the implementer.
- The complete output is preserved.
- **The finding is not corrected, Review 09 is not started, and no T0 acceptance dossier is prepared.** Authorization is requested.
- Not done:
  - not merged, and T1 and T2 not started;
  - DR-0029 P1–P10 and DR-0028 P6(b) not decided;
  - the GMAT geodetic-drag discrepancy not closed: it stays escalated;
  - no protected artifact, test or threshold changed.

## Resolution assessed by Review 08
| Item | Review 08 | Basis (reviewer) |
|---|---|---|
| M3T0-R7-F1 | **PARTIALLY RESOLVED** | The Review 07 counterexample and both returned paths now agree with the code; an independent 100-digit M2 calculation confirms the edge (M2(55 749.39300208564) ≈ −8.57e-13 m, the next float +6.45e-12 m) and vehicle independence. The finite-need and input statements omit attainable exterior heights below β, and the record's exclusion is false (R8-F1) |
| M3T0-R7-F2 | **RESOLVED** | Both summaries qualify b_R ≤ b with b > 0 and state b = 0 separately; b_R(0) ≈ 1.49716862376135e-325; exact-rational and seeded checks of downward rounding |
| M3T0-R6-F1 | **RESOLVED** | Masses k·2^-1074, k = 1…17, re-executed; k = 1 ratio 0.9999999999988138; zero-b-removal mutant fails 22 declared cases |
| M3T0-R6-F2 | **RESOLVED** | Helpers bracket signed infinities, beyond-MAX values, subnormals, signed zeros and rationals; NaN and types rejected; unbounded enclosures never certify. The lower-height documentation defect is assigned to R7-F1/R8-F1 |
| M3T0-R6-F3 | **RESOLVED** | Cap recomputed independently: valid at 91910196476947, rejected at the next integer |
| Review 06 provenance remark (5 287-point search) | **RESOLVED** | Still explicitly UNREPRODUCED; old wording preserved |
| Review 06 b*/φ_B remark | **RESOLVED** | 7.416912861690675e-309 (stored φ_B) and 1.1125369292536007e-308 (exact φ_B) reproduced |
| M3T0-R5-F1 | **RESOLVED** | C1 and C2 absolute terms; 3 075 exact constructions; relative-only mutant fails seven declared cases |
| M3T0-R5-F2 | **RESOLVED** | Subset and transition maxima recomputed and distinguished |
| M3T0-R4-F1 | **RESOLVED** | The 190 681 km point: drag 1.02021455e-315 against envelope 1.110700085e-315 m/s²; absolute-part-removal mutant fails eight declared cases |
| M3T0-R3-F1 | **RESOLVED** | The 120 km point enclosed (0.062309014504142814 against 0.06230901450421387 m/s²); twelve downward-jump checks |
| M3T0-R2-F1 | **RESOLVED** | Perturbed rows remain sampled estimates; no global perturbed missed-dip bound claimed |
| M3T0-R2-F2 | **RESOLVED** | 79 999.9/80 000 m: 48.65837703993666 against 48.658377039936795 m/s²; per-band derivative negative |
| M3T0-R2-F3 | **RESOLVED** | The original zeroed-evidence corruption fails 22 declared checks |
| IM-1 | **RESOLVED** | Axis ablation reproduces byte for byte; quadratic-only RMS 0.9856650955520649 m |
| IM-2 | **RESOLVED** | need(111 511.96, ∞) = +0.0018399073878806404; need(111 511.97, ∞) = −0.008245909394966729; disposition preserved |
| M3T0-F1 … F5 | **RESOLVED** | Re-derived or reproduced individually (F5 on documentation evidence) |

The reviewer states: "'Resolved' assesses each original defect under the disclosed scientific contract, rather than granting owner approval or a universal platform guarantee." The GMAT geodetic-drag discrepancy remains **ESCALATED_FOR_INVESTIGATION** (DR-0029 Q-G2-1/P6). The reviewer judged the implementer's `check_review05.py:9` observation to be a disclosed historical summary, not an active-contract defect.

## New finding
| ID | Severity | Finding | Implementer reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R8-F1 | NOTE | **The lower-height exception is excluded by a false domain assertion.** The Review 07 correction record (`M3-T0-review-07.md:155`) says a computed h0 ≤ β "is not the computed height of a state in the domain (outside the ellipsoid)". Strictly exterior, bound states attain such heights: r = [nextafter(a, +∞), 0, 0], v = 0 has exact and computed height 2^-30 = 9.313225746154785e-10 m and energy ≈ −6.249e7 J/kg. For it, `stage_need` raises `ValueError: the envelope is defined above the lower edge only` (H0 < 0, the A0 envelope is evaluated before the M2 test), for b = B_V1 and for b = +∞, instead of returning the finite need stated for path 1 and for the drag-free vehicle (`t0_termination.py:1312`–`:1324`; `M3-T0-review-06.md:195`; `M3-T0-review-07.md:145`, `:147`). Not a false certification; no floor affected | **Reproduced** (`implementer-reproduction/repro_r8f1.py.txt`, `repro_r8f1.log`): the same raise for x = a (computed h0 = 0), a + 1 ulp and a + 8 and 9 ulps (h0 = 7.45e-9 and 8.38e-9 m ≤ β = 8.877691069434738e-09 m); a + 10 ulps (h0 = 9.31e-9 m > β) returns need = 55 993.323394842984 for both vehicles | **ACCEPTED, not applied** (I-10 §7) |

## Reviewer observation recorded by the implementer (not numbered by the reviewer)
In its adversarial section the reviewer reports a new mutant, `own_M3_ignored` (`return -min(s["M2"], s["M4"])` in `stage_need`), that survives its focused checks. With an injected envelope of +∞ at A0 and 0 after it (a propagation test, not a physical force), the committed code returns need = +∞ (M3 = −∞) and the mutant returns −9 929 692.324580478, a false certification. The reviewer's own assertion detects it.

**Implementer reproduction** (`implementer-reproduction/m3_injected.py.txt`, `.log`; `m3_dropped_mutant.sh.txt`, `.log`): the injected case reproduces exactly. **All 261 checks of `check_review01.py` … `check_review07.py` pass against the mutant**, and `t0_termination_results.json` regenerates byte-identically under it. So M3 never decides a published result, and no committed check pins M3's role in the minimum. This is a coverage gap in the checks and the mutation harness, not a defect in the committed code. It is not corrected here (I-10 §7).

## Implementer's validation at the reviewed commit
The reviewer ran the following itself (raw output, ledger):
- checks 01–07: 261/261;
- red-before at `72f9e00`: 3 failed, 20 passed;
- full pytest: 1185 passed, 3 warnings;
- the M1 and M2 validators: PASS, 228 M2 results; both GMAT compares: PASS;
- all nine experiments rerun twice in its clone, including GMAT, with all 97 files byte-identical;
- the committed seeded probe, with every count reproduced; its own probes (3 075 exact C1/C2 constructions, 159 finite and 291 excluded non-finite force evaluations, 72 adversarial RK4 steps, 66 E4b zero-force states);
- mutations: all 14 R7 mutants, five earlier ones and four new ones (three detected by the focused checks; the fourth is the observation above);
- the docstring-free AST of `t0_termination.py` equal to `72f9e00`; every result JSON unchanged;
- the five pinned artifacts and the 20 VAL-0019 digests, all matching; the protected-path diff empty.

The Proof wrappers write into `proof/`, so the reviewer may not run them. The implementer ran them in fresh clones at `95fff22`:

| Check | Result |
|---|---|
| M1 Proof (`run_m1_proof.sh`, fresh clone at `95fff22`) | PASS, 9/9 steps; clean: yes (`implementer-reproduction/m1_proof_run.log`). Full pytest in the same clone: 1185 passed, 3 warnings (`implementer-reproduction/pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`implementer-reproduction/m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Protected paths and pinned digests | `git diff --name-only 86df2c3 95fff22 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty; the five pinned artifacts equal `86df2c3` (recorded at `95fff22`; the reviewer checked again) |
| T0 checks after recording this review | `check_review01.py` … `check_review07.py`: 261/261; `ruff check` and `ruff format --check` clean |

**Environment and limits of the numerical evidence.**
- **Host.** All runs used macOS 26.2 (Darwin 25.2.0) x86_64, the M1/M2 reference host, with Python 3.12.15, NumPy 2.5.3 and SciPy 1.18.1 from `uv.lock`. The reviewer could not query the CPU model.
- **Reach of the measurements.** Host measurements (gradual underflow under A-FP-1, libm accuracy under A-FP-2) are not platform guarantees. No other OS, CPU or library backend was tested.
- **Not independently verified by the reviewer:** CI; the Proof-wrapper runs; the full 73-mutant rerun; the original 5 287-point search, which remains unreproduced.

## Implementer's assessment
- **The finding is correct, and the defect is mine.** The false sentence is in the Review 07 correction record I wrote under I-10. On the equator the geodetic height of x is exactly x − a, so the binary64 points 1 to 9 ulps (2^-30 m each) above the equatorial radius are exterior states with computed 0 < h0 ≤ β. The I-10 adversarial probe sampled h0 from 1 m upward and so never reached (0, β]. The behaviour has been unchanged since the envelope's lower-edge check was introduced; it raises, so it never certifies.
- **The reviewer observation is correct.** The M3 term is required for soundness when only A0 is unbounded, but no check fails without it.
- **Why the verdict holds.** Neither item changes a number, a floor or the soundness of a bound. The resolution-table rule makes R7-F1 PARTIALLY RESOLVED and the verdict REQUEST_CHANGES, and that rule is applied as written.
- **Proposed correction (for authorization; none applied):**
  1. **R8-F1 (documentation, no numerical change):** state the precondition h0 > β for every returned need, and that a computed h0 ≤ β (attainable by exterior states within about 8.9 nm of the ellipsoid, and h0 = 0 on it) raises `ValueError` before the M2 test, for every b. Separately keep the `decimal.InvalidOperation` case for very negative h0 as outside the exterior-state domain. Correct the `stage_lower_heights` docstring (`:1312`–`:1324`); amend the Review 07 record (`:145`, `:147`, `:155`) and the Review 06 amendment (`:195`) by appended notes; qualify the VAL-0019 body (`validation.md:827`), DR-0029 (`:101`, `:484`) and the report (`M3-T0-report.md:66`). Add a regression with r = [nextafter(a, +∞), 0, 0] and with a + 9 and a + 10 ulps, for b = B_V1 and b = +∞, and mutants that hide the exception or reintroduce the false exclusion. Do not change the floor or domain policy.
  2. **M3 coverage gap (checks only):** add a check with an injected envelope that is +∞ at A0 and finite after it, asserting need = +∞, and add `own_M3_ignored` to the mutation harness.
  3. Rerun the checks, the mutation harness, M1/M2 Proof, the digests, reproducibility and CI. Any Review 09 needs authorization.
- **Remaining conditions (unchanged):**
  - the force and stage guarantees hold only under A-FP-1 to A-FP-3 (A-FP-2 is unresolved, and E4b depends on it explicitly);
  - the C1/C2-only scope with positive finite mass, cd and area;
  - no overflow;
  - negative two-body energy, no thrust and dt = 10 s;
  - no certified J2-plus-drag missed-dip bound;
  - the GMAT geodetic-drag discrepancy stays escalated;
  - DR-0029 P1–P10 and DR-0028 P6(b) are undecided.
