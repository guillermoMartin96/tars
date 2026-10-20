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
