# M3 T1 Review 03 (independent review of the Review 02 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a16a57-041c-7870-bfd6-aad8e7e9d8af`; final message written 2026-10-23 20:28:46 UTC. One attempt.
- **Sandbox:** `workspace-write`, no network. GMAT was not provided; T1 contains no GMAT work.
- **Invocation:** `codex exec -C snap -s workspace-write --json -o codex_last_message.md - < M3-T1-codex-review03-prompt.md`. As in Reviews 01 and 02, the CLI wrapper on this host reports `--dangerously-bypass-hook-trust` as enabled. This invocation did not pass that flag, and the flag does not change the sandbox.

**Reviewed commit:** **`4b85ded298e521f5c72b606cd012dec8b56e9c5e`**, head of `milestone-3-t1-j2-force-model`.
- The correction pass is `56ad329`, `bbcf40e`, `304d796`, `308f126`, `a4dfda1`, `2f82c00`, `c456881` and `4b85ded`, on top of the Review 02 record `b1566ae`.
- `main` = `60648b93385a9954194730006aeac29ea14875ad`.
- **Environment.** A fresh GitHub clone detached at the pinned SHA, with its own `uv sync --locked` environment and `review_scratch/` excluded from git. The implementer placed in `review_scratch/`:
  - `reviewed_src_b1566ae/src` and `reviewed_src_97b69ef/src` (`git archive <sha> src`), the inputs of the two correction checks;
  - `ci/run-<id>.json` (`gh run view --json`) for runs 40008016629, 40002897696, 40002789138, 40002590550 and 39906870674, as implementer-supplied claims.
- **Prompt.** Kept outside the repository during the review. It:
  - reproduces I-20 verbatim and points to the Review 01 and 02 prompts for I-17, I-18 and I-19;
  - lists the implementer's claims, including the local validation and CI figures, as claims to verify;
  - states which I-20 §6 preconditions the implementer checked, and that unauthenticated CI is a verification limit, not a reason to stop;
  - maps the ten I-20 §7 items into the review.
- **Authority:** "I-20 — M3 T1 Review 02 Corrections and Review 03 Authorization" (Tech Lead), §6–§7.

## Preconditions (I-20 §6), checked by the implementer before the review
| Item | Result |
|---|---|
| Branch | `milestone-3-t1-j2-force-model` |
| HEAD and origin | both `4b85ded298e521f5c72b606cd012dec8b56e9c5e` |
| Working tree | clean |
| Local validation | at `c456881` (`4b85ded` changes one documentation file); recorded in `M3-T1-review-02.md`, "Validation of the correction pass (I-20 §6)" |
| CI | completed, success on `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform`: `a4dfda1` run **40002590550**; `2f82c00` run **40002789138**; `c456881` run **40002897696**; `4b85ded` run **40008016629**. `56ad329` … `308f126` were pushed with `a4dfda1` and have no run of their own |

## Files
- **Prompt:** `raw/M3-T1-codex-review03-prompt.md`.
- **Raw output:** `raw/M3-T1-codex-review03.md`, the reviewer's saved `review_scratch/M3-T1-codex-review03.md`. The CLI's final message is the same text without the trailing newline. Absolute paths are redacted: `<SNAP>` for the clone, `<SCRATCH>` for other scratch paths and `<HOME>` for the home directory. No other change.
- **Reviewer scripts and logs:** `raw/M3-T1-codex-review03-evidence/` (100 files, plus `SHA256SUMS` and `reviewer-SHA256SUMS`, 1.3 MB).
  - `*.py.txt` are the reviewer's scripts (renamed from `.py`). `COMMANDS.md` and `INSPECTION_COMMANDS.md` are its command ledgers. `ci/` holds the implementer-supplied CI exports.
  - `own_mutants/<mutant>/` holds `diff.patch`, `junit.xml` and `pytest.log` for the reviewer's six mutants, plus `results.json` and `redfirst.log`.
  - `reviewer-SHA256SUMS` was written by the implementer over the reviewer's unrenamed, unredacted files. `SHA256SUMS` covers the committed files.
  - **Omitted** as derivable from git or as copies:
    - `reviewed_src_*` and the two `*.tar` archives (`git archive <sha> src`);
    - the full `src/` trees of the reviewer's mutant copies, each represented by its diff;
    - `__pycache__/`;
    - the reviewer's copy of its report.
- **Implementer's reproduction:** `raw/M3-T1-review03-reproduction/`, run at `4b85ded` in the T1 worktree, independent of the reviewer's scripts. It contains:
  - `reproduce_review03.py.txt` and `reproduce_review03_output.json`;
  - `upper_subnormal_ignored.diff` and `upper_subnormal_ignored_pytest.log`, the reviewer's surviving mutant re-applied by the implementer.

## Verdict
**`VERDICT: PASS (unconditional)`.** There is no BLOCKER, MAJOR or MINOR finding. The reviewer raises two **NOTE** findings (M3T1-R3-F1, F2) and one unnumbered observation: a surviving mutant of its own, registered below as M3T1-R3-O1.
- **Reviewer's summary:** "All eight prior findings are **RESOLVED**. I found no blocking, major or minor implementation defect. There are two nonblocking documentation/provenance notes below. The verdict is not conditional on a later test, fix, approval or relaxation of an acceptance criterion."
- **Prior findings, per the reviewer:** M3T1-R1-F1 … F4 and M3T1-R2-F1, F2, F3 and O1 are all **RESOLVED**.
- **Scope of the coefficient-chain extension:** the reviewer judges it to be within I-20's bounded numerical correction. It is the same defect, and it does not change unrelated models or numerical policy. This is the reviewer's assessment; the owner has not ruled on it.
- **Acceptance readiness, per the reviewer:** "ready for the owner's acceptance-dossier/acceptance decision, with the two nonblocking clarifications and finite verification limits recorded."
- **Stop rule applied (I-20 §8).** The verdict is an unconditional PASS. Both NOTEs, however, are new findings that need an owner disposition. Therefore:
  - each is reproduced and classified, with a disposition proposed;
  - **neither is fixed**, and no Review 04 is started;
  - the T1 acceptance dossier is prepared (`docs/reviews/M3-T1-acceptance-dossier.md`), with the NOTE dispositions listed as open decisions.

  T1 is not accepted or merged, and T2 and T3 are not started.

## What the reviewer verified by its own execution (from the raw output and ledger)
- **Regression:**
  - full pytest 1288 passed (28 min 46 s); ruff check passes and ruff format passes (236 files); T0 checks 314 passed;
  - M1 validator 7/7; M1 golden comparison bit-identical; cross-process event-log digest `7a4e1877…20a4`;
  - fresh-process determinism for all four `scenarios/m2_*.json`; M2 validator 228/228.

  The Proof wrappers were not run, as the prompt instructed.
- **Red-first:** the final tests give 26 failed / 81 passed against the archived `b1566ae` source.
- **Correction evidence:**
  - the committed mutation campaign reruns as 46/46 killed by meaningful assertions, with every failure message inspected; the four re-anchored mutants keep their defects;
  - the Review 01 correction, Review 02 correction, informational and exploratory-survivor outputs reproduce their committed JSON files byte for byte, and the mutation output does so after normalizing memory addresses.
- **Underflow (R2-F1):**
  - a 29 975-pair random-bit-pattern check of `_underflows` against independent rational comparisons found no wrong decision;
  - an adjacent-ulp constructive probe: an exact subnormal product of 2 × min subnormal is accepted, and one ulp more in μ makes it inexact and raises;
  - a 7 000-trial extreme-parameter search accepted 3 213 states; every accepted component lies within `64u·majorant + 0.5·min_subnormal` of a rational reference (largest ratio 0.09037), with no representable non-zero component silently rounded to zero. The reviewer states that this is falsification evidence, not a theorem;
  - the canonical reach is re-derived (|k| ≥ about 1.4648e-283; factors ≥ 2⁻⁵³ and 2⁻⁵¹; products ≥ about 1.626e-299), so the raising checks cannot trigger with the canonical constants.
- **Ownership (R2-F2):**
  - 29 accepted type cases: int and float subclasses, NumPy signed and unsigned widths, float16/32/64/longdouble and 0-d forms;
  - 13 rejected cases, among them bool/bool_, string and object-string arrays, complex, Fraction and non-scalar arrays.

  A numeric object-dtype 0-d array is accepted when its element is a supported scalar, which agrees with the stated element-based rule. Deliberate object-model bypasses are outside the promise, as in earlier reviews.
- **Numerical preservation:**
  - 200 004 states with zero differences against both references;
  - three RK4 trajectories (6 001 states each) bit-identical to `b1566ae`, and in the reviewer's own run also to `97b69ef`;
  - its own sample of 9 919 accepted states, bit-identical to both references, plus 2 081 explicit domain rejections;
  - the equatorial domain endpoints 3.3773820261812166e-57 m and 4.476546622757235e61 m.
- **Interval certificate:** the outward-dyadic rational certificate covers all 5 904 dense-grid cases; the largest enclosed-error to bound ratio is 0.4114583333333321.
- **Records:**
  - every record section is a strict byte-prefix extension of `b1566ae`;
  - every quoted number agrees with the reviewer's computations within the stated rounding;
  - no claim of complete IEEE 754 correctness or of complete mutation coverage;
  - DR-0025 and the +∇U erratum are accurate and not overstated;
  - the protected-path diff from `60648b9` is empty, `src/` changes are confined to `constants.py` (+58 lines) and `forces.py` (+137 lines), and the existing force classes are AST-identical.
- **CI exports:** internally consistent with the expected SHAs, the branch and all four job names, each `success`. They are listed as implementer-supplied metadata, not authenticated (see the verification limits).

## Findings and dispositions
The proposed dispositions are the implementer's. None is applied; each awaits the Tech Lead.

| ID | Severity | Finding (reviewer) | Implementer's reproduction (`reproduce_review03_output.json`) | Proposed disposition |
|---|---|---|---|---|
| M3T1-R3-F1 | NOTE | **The exact-rational fallback's reach is described too broadly.**<br>VAL-0020 correction 2, "Cost" bullet (`docs/science/validation.md:1173`), says the exact-rational comparison runs only for a product below the normal range, "which a realistic state never reaches".<br>With the canonical constants at r = (12756274, 0, 6378137) m, c = 1 − 5s² computes to exactly zero. kc = 0 is below the threshold, so `_underflows` builds Fractions, although an exact zero is not underflow.<br>The result is correct and the cost is bounded; this is a documentation overstatement | **REPRODUCED.**<br>s² computes to 0.2 and c to exactly 0.0.<br>One acceleration evaluation constructs **2** `Fraction` objects (the implementer patched `forces.Fraction` with a counting subclass).<br>The result is (−0.0, −0.0, −0.0005692785957521009) m/s²; no exception.<br>The canonical no-rejection argument is unaffected: it concerns **non-zero** factor products, and an exact zero is accepted | **ACCEPTED** (proposed), NOTE.<br>Proposed correction: an appended clarification to VAL-0020 (the original bullet stays). Non-zero factor products cannot reach the fallback with the canonical constants. Exact-zero products (a latitude factor or k·factor that is exactly 0) do reach it and are accepted; each evaluation adds at most two comparisons of exact two-operand products, so the cost stays bounded.<br>No code change (the reviewer: "An implementation optimization is unnecessary"). An `abs(product) != 0.0` short-cut is an alternative that would keep the results bit-identical; it is not proposed, because it changes code to fix a description |
| M3T1-R3-F2 | NOTE | **A historical reproduction row mixes observation times.**<br>In the implementer's Review 02 reproduction (`raw/M3-T1-review02-reproduction/reproduce_review02.py.txt:38–49`; output lines 25–28), the row `mu_alias_set_-1` reports `m.mu = 0.0` beside the acceleration computed with μ = −1. The script computes `a_neg`, sets the alias to 0, and only then reads `m2.mu` when it builds the row.<br>This predates the correction pass and does not invalidate the defect, its acceleration or the correction | **REPRODUCED** on the archived `b1566ae` code, in the same sequence:<br>μ = −1.0 when `a_neg` is computed, x = 3.991922438949618e-17 (outward);<br>μ = 0.0 when the row is written.<br>The raw row matches the latter. The `x` value and `outward: true` in the raw record are correct | **ACCEPTED** (proposed), NOTE.<br>Proposed correction: an appended provenance note in `M3-T1-review-02.md`. It explains the timing: `m.mu` in that row was read after the subsequent mutation to 0; at acceleration time μ was −1.<br>The raw script and output stay unchanged, as I-20 §10 requires them to be preserved |
| M3T1-R3-O1 | — (reviewer observation, unnumbered) | **Surviving mutant `upper_subnormal_ignored`.**<br>Replacing the helper's threshold `abs(product) < _MIN_NORMAL` with `< _MIN_NORMAL / 2` passes all 107 T1 tests: no test exercises an inexact product in [MIN_NORMAL/2, MIN_NORMAL).<br>At J2 = 2⁻¹⁰²³ + 2⁻¹⁰⁷⁴, μ = 2¹⁰⁰⁰, R = 1, the first coefficient product is about −0.75 MIN_NORMAL and inexact; the production code rejects it correctly.<br>The reviewer classes this as an optional regression-test enhancement and a finite-coverage limitation, not a production defect | **REPRODUCED.**<br>The implementer re-applied the one-line diff to a copy of `src/` and ran both T1 test files against it: **107 passed** (`upper_subnormal_ignored_pytest.log`).<br>p1 = −1.668805393880402e-308 = −0.7500000000000004 MIN_NORMAL, inexact. Production raises "-(3/2) J2 mu R^2: an intermediate product underflows".<br>In the existing coefficient-chain cases, the underflowing products are 8.9e-16, 5.5e-12 and 0.4125 times MIN_NORMAL, all below MIN_NORMAL/2. The component cases are of order 2⁻⁵³ times MIN_NORMAL | **Owner's choice; recommended: add the test.** One parametrized case in the upper subnormal band, the reviewer's example, asserting the `ValueError`, together with a `r3_upper_subnormal_band_ignored` mutant in the committed harness. This would close a gap at the boundary that the contract defines, at negligible cost, with no change to production code.<br>The alternative is to record it with Review 02's exploratory survivors as a documented limitation of finite mutation coverage (I-20 §3 precedent) |

## Reviewer observations not registered as findings
- **CI timestamp anomaly.** In the export of run 40002897696 (`c456881`), the first step of `check (macos-15-intel)` starts at 18:23:19Z, before the run's `createdAt` (18:23:33Z) and the job's `startedAt` (18:23:39Z). The implementer confirms these values in the export. The reviewer: "Clock skew is possible; this is an internal timestamp anomaly, not proof of falsification or failure. The pinned-head export has no such observed anomaly."
  - **Proposed disposition:** no action. The values are GitHub's metadata as exported; the job's conclusion is `success`. The run is not on the pinned head.
- **Object-dtype 0-d arrays** with a supported numeric element are accepted. This agrees with the stated element-based supported-type rule and still stores an owned `float`. **Proposed disposition:** no change; it is consistent with the recorded contract.
- **Not resolved, as required (I-20 §9; I-19 §9):** DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), the secular-rate tolerance and presentation, T4/T5 comparison requirements, the M3 final time step, the T3 axis representation and external corroboration. The reviewer approved none. The approximately dt⁵ invariant drift remains an observation.

## Verification limits (from the reviewer, confirmed by the setup)
- **One host.** All new numerical observations come from one host: macOS 26.2, x86_64, CPython 3.12.15, NumPy 2.5.3. The sandbox denied the CPU model query.
- **Arithmetic model.** The rational and interval certificates assume the documented arithmetic model; they do not establish CPython, libm or NumPy correctness on every platform.
- **Finite reach.** Tests, random sets, dense grids and mutation campaigns have finite reach.
- **Not available to the reviewer:** network, signatures, live CI, cross-platform runs, a GMAT executable and an external J2 implementation.
- **Not authenticated:** the historical Proof wrapper outcomes (9/9, 20/20), the implementer's local runs and the CI exports. These are documentary claims to the reviewer.
