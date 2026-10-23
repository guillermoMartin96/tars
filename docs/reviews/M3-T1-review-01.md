# M3 T1 Review 01 (independent review of the J2 force model)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session (attempt 2, the review):** `01a1664d-9051-7403-8751-2d7427fcf1cc`, 2026-10-23 01:08:41–01:40:27 UTC (2026-10-22 local).
- **Sandbox:** `workspace-write`, no network. GMAT was not provided; T1 contains no GMAT work.
- **Invocation:** `codex exec -C snap -s workspace-write --json -o codex_last_message.md - < M3-T1-codex-review01-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`97b69ef92e589ebd1b71016f49c4c9816d8c724b`**, head of `milestone-3-t1-j2-force-model`. T1 commits `5fd24a2`, `e23675c`, `81a0d56`, `97b69ef` on `main` = `60648b93385a9954194730006aeac29ea14875ad`.
- **Environment.** A fresh GitHub clone with its own `uv sync --locked` environment. The implementer exported the GitHub metadata of CI runs 39852509134, 39853032093 and 39865621259, and pytest excerpts of the three platform jobs of run 39852509134, into the clone's `review_scratch/ci/`, as implementer-supplied claims.
- **Prompt.** It was kept outside the repository during the review. It reproduces I-17 and I-18 verbatim, lists the implementer's claims as claims to verify, and maps the I-18 §3 areas A–F, §4 severities, §5 decision boundaries and §6 deliverables into the review items and required output.
- **Authority:** "Authorization I-18 — M3 T1 Independent Codex Review 01" (Tech Lead, 2026-10-22).

## Preconditions (I-18 §1), checked by the implementer before the review
| Item | Result |
|---|---|
| Branch | `milestone-3-t1-j2-force-model` |
| HEAD and origin | both `97b69ef92e589ebd1b71016f49c4c9816d8c724b` (after `git fetch`) |
| Working tree | clean |
| Final CI | I-18 §1 names run `39865621`. The run on `97b69ef` is **39865621259**: its first eight digits are `39865621`, and no other run among the repository's 200 most recent has that prefix. Completed, success on `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform` |
| `main` contains P10 | `60648b9` is `origin/main`; ancestry verified |
| Protected M1/M2 artifacts | `git diff 60648b9..97b69ef -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty; `src/` changes are constants.py +58/−0 and forces.py +39/−0 |

## Attempt 1 (no review performed)
- **Session:** `01a1664a-d2d7-78f0-a597-2220d8c70add`, 2026-10-23 01:05:41 UTC, about two minutes.
- **Cause:** the first prompt reproduced I-18 verbatim, including §1 ("Before beginning, verify … Final CI run `39865621` has all four jobs green … If any precondition fails, stop"). It did **not** state that the implementer had already verified §1, as the T0 prompts did. The offline reviewer treated §1 as its own precondition, could not authenticate CI, noted the run-number discrepancy and stopped. It ran no tests and registered no findings. Its output reads "Review execution is incomplete", with `VERDICT: REQUEST_CHANGES` and "REVIEW INCOMPLETE".
- **Response:** I relaunched once from a fresh clone of the same SHA. The only change to the prompt was an added paragraph, quoted in full in the attempt-2 prompt under "Snapshot and rules". It states that the implementer had checked the I-18 §1 preconditions, reconciles the run number, supplies the CI exports as implementer claims, and says that unauthenticated CI is a verification limit, not a reason to stop. It also tells the reviewer that an earlier attempt existed without showing it.
- **Authority:** I treated the relaunch as executing the authorized Review 01, because attempt 1 performed no review. It is not Review 02. **This interpretation is mine; the owner may rule otherwise.**
- **Files:**
  - `raw/M3-T1-codex-review01-attempt1-prompt.md`;
  - `raw/M3-T1-codex-review01-attempt1.md` (its saved report, equal to its final message plus a trailing newline);
  - `raw/M3-T1-codex-review01-attempt1-COMMANDS.md`.
- **Lesson:** a review prompt that quotes an authorization verbatim must say which of its steps the implementer has already performed. Otherwise an offline reviewer will try to perform them itself.

## Files
- **Prompt:** `raw/M3-T1-codex-review01-prompt.md`.
- **Raw output:** `raw/M3-T1-codex-review01.md`. This is the reviewer's saved `review_scratch/M3-T1-codex-review01.md`, equal to the CLI's final message plus a trailing newline. It contained no absolute paths, so it is unredacted and unchanged.
- **Reviewer scripts and logs:** `raw/M3-T1-codex-review01-evidence/`.
  - Contents:
    - `*.py.txt`, the reviewer's scripts;
    - `COMMANDS.md`, the reviewer's command ledger;
    - `ci/`, the implementer-supplied CI exports;
    - `builtin_details/<mutant>/` (`src.diff.txt`, `pytest.log`): the reviewer's reruns of the 14 committed mutants;
    - `mutant-diffs/<mutant>/` (`src.diff.txt` and logs): the reviewer's own 8 mutants.
  - `reviewer-SHA256SUMS.txt` was written by the implementer over the reviewer's unredacted files.
  - Absolute paths are redacted to `<clone>`, `<scratch>`, `<tmp>` and `<home>`. `SHA256SUMS` covers the committed files.
  - The mutant trees are represented by implementer-made diffs of their `src/` against the reviewed `src/`.
  - **Omitted** as large or derivable from git:
    - `authority-read.txt` (388 kB; the reviewer's dump of the records it read);
    - `decision-index.txt`;
    - `docs-diff.patch` (`git diff 60648b9..97b69ef -- docs`);
    - `raw-reviewer-output.md` (identical to the saved report);
    - the unmodified files of the mutant trees.
- **Implementer's reproduction:** `raw/M3-T1-review01-reproduction/` (`reproduce_review01.py.txt`, `reproduce_review01_output.json`). It is independent of the reviewer's scripts and uses exact rationals for reference values.

## Verdict
**`VERDICT: REQUEST_CHANGES`** (attempt 2). Findings: **2 MINOR** (M3T1-R1-F1, F2) and **2 NOTE** (F3, F4). There are no BLOCKER or MAJOR findings.
- **Reviewer's summary:** "The ordinary-domain acceleration is physically correct; the defects concern parameter immutability and unguarded numerical domain loss."
- **Stop rule applied (I-18 §6–§7, REQUEST_CHANGES):** the findings are recorded and independently reproduced. **No finding is fixed.** No Review 02 is started. T1 is not accepted or merged, and T2 and T3 are not started.

## What the reviewer verified by its own execution (from the raw output and ledger)
- **Regression:**
  - full pytest: 1207 passed in 28 min 37 s;
  - ruff check and format: pass;
  - T0 checks: 314 passed;
  - M1 validator 7/7, golden comparison and cross-process determinism, with hash `7a4e1877…20a4`;
  - M2 validator 228/228.
  - The Proof wrappers were not run, as the prompt instructed.
- **T1 experiments:** both reran into scratch. The informational and mutation JSON are exactly equal to the committed files, and 14/14 mutants are detected. All 14 fail real assertions; none fails through an import or infrastructure error.
- **Physics:** the reviewer independently derived U₂ and its gradient; they reduce to the production expression. Acceleration = **+∇U** for the positive potential. J2 = −√5 C̄₂₀ follows from P̄₂₀ = √5 P₂. The equator and pole known answers, dimensions and the +Z frame are consistent. A 100-digit Decimal comparison at the 162 test points found errors no larger than 0.0333 of the allowance.
- **Numerics:**
  - The reviewer recounted the operations: acceleration 25 operations at path depth 8; dual-number gradient 123 at depth 16. On this count the "≤ 13 / ≤ 40 per path" figures are conservative.
  - It judged path depth alone insufficient for the general theorem. A separate exact-rational interval argument covering every operation, the subtraction and the computed right-hand side shows that all 162 × 3 components satisfy the gradient gate, with a worst ratio of 0.411. This holds on the gate's actual inputs, under the stated floating-point model.
  - It found a computational justification for each exact assertion within the finite domain.
- **Drift:** the invariant ratios and convergence figures reproduce. The approximately fifth-order drift also appears with **point mass only** (energy orders 4.89/4.80, h_z 5.00/5.00). It is therefore not specific to J2; it remains an unexplained observation, not a defect.
- **Isolation:** the protected-path diff is empty, and the `src/` changes are additive and unwired.
- **CI exports:** the identities are consistent. The reviewer noted a timestamp ordering oddity in the final Intel job's metadata: step start times precede the job's start time by a few seconds. It did not establish a cause, and nor have I. CI authenticity is listed as a verification limit.

## Findings and dispositions
| ID | Severity | Finding (reviewer) | Implementer's reproduction | Disposition |
|---|---|---|---|---|
| M3T1-R1-F1 | MINOR | `ZonalJ2Gravity`'s `mu`, `equatorial_radius` and `j2` are plain writable attributes (`src/tars/sim/forces.py:86`–89). The cached `_k` is not updated, so after `model.j2 = 0` the model still returns the canonical acceleration. This contradicts the packet's "immutable and validated" (`M3-T1-authorization-packet.md:36`) | **VERIFIED.** Reassigning `j2`, `mu` and `equatorial_radius` succeeds. The acceleration at a·x̂ is unchanged afterwards (−0.01591182047796651, −0, −0); a freshly built J2 = 0 model gives zeros. **Root cause:** I copied the attribute style of `PointMassGravity`, which is legacy code not covered by the packet's requirement, and wrote no test for immutability | **ACCEPTED**; not applied |
| M3T1-R1-F2 | MINOR | Silent numerical-domain loss (`forces.py:82`–89, 93–100). `r2*r2*r_norm` overflows for large finite r and returns 0 where the true value is representable. Infinite μ or a pass validation and give non-finite results. Contrary to DR-0024 R6 ("Behaviour outside it is defined, never silent") | **VERIFIED**, by exact rationals: x = 1e62 m on the equator gives −0.0 against an exact −2.633e-223; x = 1e70 gives −0.0 against −2.633e-255. Bisection puts the onset at x ≈ 4.48e61 m (7.0e54 a), where the exact value is −6.56e-222. μ = ∞ and a = ∞ are accepted and give `[-inf, nan, nan]`. Interior inputs: x = 1e-100 raises `ZeroDivisionError`, not the documented `ValueError`; x = 5e-324 raises the origin `ValueError`. **Root cause:** I validated only signs and finiteness of J2, and did not define or enforce a numerical domain. The defect is far outside any physical orbit; for comparison, the pre-existing `PointMassGravity` uses `r_norm**3` | **ACCEPTED**; not applied |
| M3T1-R1-F3 | NOTE | The docstring of `test_radial_sign_changes_at_sin2_latitude_one_third` (`tests/test_zonal_j2.py:236`) writes a·r ∝ μa²/r⁴. The dot product scales as r⁻³; r⁻⁴ is the form for a·r̂. The sign test itself is correct | **VERIFIED.** dot / (r⁻³ form) = 1 ± 7e-16 at r = a, 2a, 4a and latitudes 0°, 20°, 50°. The r⁻⁴ ratio equals r | **ACCEPTED**; not applied |
| M3T1-R1-F4 | NOTE | The 14/14 mutation result has finite coverage. Four reviewer mutants pass all 26 T1 cases: `abs(j2)`, a coefficient × (1 + 2⁻⁵¹), zero beyond 7a, and a 1 % x/y error for 0.99 < s² < 0.9999. A `float.fromhex` encoding gets past the no-J2-literal regex (`tests/test_zonal_j2.py:129`–143, 178–192, 274–290; `tests/test_constants.py:127`–139; `t1_mutation_check.py:29`–115) | **VERIFIED.** I applied the reviewer's `high_lat_band` and `negative_j2_abs` diffs to copies of `src/`; with `PYTHONPATH` set to each copy, the T1 tests report 26 passed for each. None of the 162 static sample points lies in 0.99 < s² < 0.9999. The highest latitude reached by the 97° invariant trajectory is 83°, so s² ≤ 0.985 there. The regex does not match `float.fromhex('0x1.1bcdd00abd9aap-10')`. **Root cause:** the tests use only J2 > 0 and a finite latitude grid, and the literal scan is a heuristic, which VAL-0020 did not say | **ACCEPTED** (test enhancement); not applied |

### Implementer-identified item (not a reviewer finding)
- The T1 authorization packet's §7 table says "acceleration = −∇U of the separately coded potential". With the packet's own §3 potential U = (μ/r)[1 − J2 (a/r)² P₂] (positive convention), the acceleration is **+∇U**, as the reviewer derived.
- The tests (`j2_potential`, gradient oracle) and VAL-0020 use +∇U. The error is in the packet's wording only; no code or evidence is affected.
- The packet is a historical record and is not edited. Proposed: an append-only correction note, if authorized.

## Reviewer's assessment of the unresolved T1 assumptions (T1 report §9)
| Item | Reviewer's assessment |
|---|---|
| 1. Secular-rate tolerance | Genuinely unresolved. Informational treatment complies with I-17 §8. A gate needs a derived error budget; none is chosen |
| 2. Operation counts | The path counts are conservative on recount, but a path count is not the whole proof. The reviewer's interval certificate supports the actual gradient gate on its 162 inputs. No bound for all states is established |
| 3. IEEE 754 correct rounding | A conditional assumption, checked locally for the constant's operations. Neither libm-wide nor cross-platform correctness is proven. The force docstring's "does not depend on libm" (`forces.py:74`–75) should stay qualified, because `math.sqrt` is a platform operation |
| 4. Dual-number substitution | Q1: the same derivative, yes. Q2: sufficient independence for a partially independent unit oracle, yes. Q3: avoids extra assumptions only partly: it removes complex `sqrt` and the step-size choice, but adds custom dual arithmetic and still relies on scalar `sqrt`. Q4: meets the intended strength under the stated assumptions, without exceeding its independence class. Q5: **an explicit owner disposition or DR-0025 amendment is required**, because DR-0025 Q3 and the packet name the complex step. The reviewer did not accept the substitution or amend DR-0025 |
| 5. Axis representation | Fixed +Z correctly implements T1. The representation is T3 scope |
| 6. Fifth-order drift | Reproduced, and also present without J2. Not a physical defect; the mechanism is not established |
| 7. No external comparison | Correctly disclosed. T4/T5 requirements are unchanged |
| 8. Q-G2-2 | Remains PROPOSED. The identity tests do not adopt it |

Further limitations noted by the reviewer:
- the finite sensitivity of the invariant ratio test;
- the partial correlation of the potential, energy and constant oracles: they share μ, a, J2 and the conventions;
- CI and source provenance are not authenticated;
- the Richardson estimate relies on an asymptotic assumption;
- the reviewer cannot verify, from git, that no measurement was made before the 1/2 boundary was fixed.

## Acceptance readiness
- The reviewer finds that the ordinary-domain physics, the additive isolation and the recorded measurements are sound.
- In its words, T1 is **not acceptance-ready** until F1 and F2 are corrected, or returned to the owner for direction, and the owner has dispositioned the derivative-method substitution.
- **Owner decisions this review leaves open (recommendations only, nothing recorded as approved):**
  1. authorization to correct F1–F4, with independent Review 02;
  2. a disposition of the dual-number substitution: accept it with qualified assumptions, as the reviewer recommends, or require the complex step;
  3. whether to append a correction note on the packet's "−∇U" wording;
  4. whether the attempt-1/attempt-2 handling of this review is acceptable.
- **Unchanged and undecided:** DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), the secular-rate tolerance, the T3 axis representation, T4/T5 comparison requirements and the M3 final time step.

## Proposed corrections (for authorization; none applied)
- **F1:** make the `ZonalJ2Gravity` configuration read-only, for example with read-only properties over private fields and `__slots__`, or `__setattr__` raising after construction. Add a test that reassignment raises. `PointMassGravity` is not changed.
- **F2:** define and enforce the numerical domain. Options:
  - require finite μ, a and J2 and finite r;
  - rescale the evaluation, for example computing (a/r)² and μ/r² first, so that intermediate overflow cannot produce a silent zero for representable results;
  - or reject r outside a stated finite range with `ValueError`.

  Raise `ValueError`, not `ZeroDivisionError`, for interior underflow. Add boundary tests (overflow onset, ∞ parameters, tiny radius). The choice of domain rule is an implementation decision within T1 scope, with no new physics.
- **F3:** correct the docstring to r⁻³, or state a·r̂.
- **F4:** add a negative-J2 case and a parameter-scaling case. Add deterministic samples at high latitude (s² up to 1 − 1e-4) and at more radii. Describe the literal scan as a heuristic in VAL-0020 (append-only). Optionally, add the reviewer's surviving mutants to `t1_mutation_check.py` as expected detections.

## Owner disposition (I-19; recorded 2026-10-23 UTC, append-only)
- **Authority:** "I-19 — M3 T1 Review 01 Corrections and Review 02 Authorization" (Tech Lead).
- **Checkpoint:** the I-18 checkpoint and the Review 01 result are accepted. The `REQUEST_CHANGES` verdict stands. **M3T1-R1-F1 … F4 are accepted for correction.** T1 status: IMPLEMENTED — NOT REVIEW-ACCEPTED — NOT MERGED.
- **Review 01 execution (I-19 §1):** the attempt-1/attempt-2 handling is **ACCEPTED**. Both sessions together are **Review 01**; they are not Review 01 and Review 02. Both raw sessions are preserved unchanged.
  - The owner's rationale:
    - attempt 1 performed no substantive review;
    - its stop came from a prompt/environment mismatch;
    - attempt 2 reviewed the same implementation SHA from a fresh clone;
    - the added paragraph supplied established precondition and CI facts without changing the implementation or steering the conclusion.
  - I-19 writes the SHA as `97b69ef92e524b`. The reviewed SHA is `97b69ef92e589ebd1b71016f49c4c9816d8c724b`; the two agree in their first seven characters, `97b69ef`.
- **Dual-number substitution (I-19 §7):** ACCEPTED for T1. It is recorded in DR-0025 (Resolution, owner-disposition note) with the owner's stated rationale and limitations.
- **Packet sign wording (I-19 §8):** recorded as an erratum, appended to `docs/milestones/M3-T1-authorization-packet.md`. The relation is +∇U for the positive potential, checked against the potential convention, Review 01's derivation and the gradient tests.
- **Unchanged and open (I-19 §9):**
  - DR-0029 P1–P9, Q-G2-1/P6, Q-G2-2, DR-0028 P6(b);
  - the secular-rate tolerance and its presentation; T4/T5 comparison requirements; the M3 final time step; the axis representation (T3);
  - the lack of external corroboration; the broader IEEE 754 rounding-model assumption.
  - The dt⁵ drift remains an observation. The CI metadata timestamp oddity was not investigated: it does not affect reproducibility, correctness or review integrity.

## Corrections (I-19 §2–§6; recorded 2026-10-23 UTC, append-only)
| Finding | Correction | Commit | Evidence |
|---|---|---|---|
| M3T1-R1-F1 | `ZonalJ2Gravity`: `__slots__` (no `__dict__`); `__setattr__`/`__delattr__` raise `AttributeError` for every name; no cached derived value (the coefficient is computed from the stored parameters on each call, with the same arithmetic) | `a27f288` | `test_parameters_are_immutable_after_construction`; mutants `f1_setattr_allowed`, `f1_delattr_allowed`, `f1_instance_dict` killed |
| M3T1-R1-F2 | Explicit numerical contract with three classes: valid; invalid-domain (rejected before the arithmetic); arithmetic outside the binary64 normal range ("outside the J2 numerical domain …"). `ValueError` throughout, with the message naming the cause (VAL-0020 correction). Valid results are bit-identical to `97b69ef` | `a27f288` | Six new tests; 8 F2 protection-removal mutants killed; `t1_review01_correction_check_results.json` (before/after for every Review 01 reproduction; 200 004 states bit-identical; domain 3.38e-57 … 4.48e61 m on the equator) |
| M3T1-R1-F3 | Docstring corrected to r⁻³; assertion unchanged | `62d3684` | The Review 01 reproduction (`reproduce_review01_output.json`, F3 rows) |
| M3T1-R1-F4 | Exact power-of-two known answers (±J2, last-bit coefficient, out to 2²⁰⁰ R); far-field known answers to 1000 R; dense latitude gradient for ±J2 (5 904 points, including 0.99 < s² < 0.9999); literal scan labelled a heuristic and extended to the hex spelling. Mutation harness: anchors updated, the reviewer's 8 and 11 F1/F2 mutants added, kills classified from JUnit XML, and detection by assertion required | `62d3684`, `b0164fd` | **32/32 killed, all by assertion; no survivors** (`t1_mutation_check_results.json`) |

- **Not changed (out of I-19 scope):** the force docstring sentence "does not depend on libm or BLAS". Review 01 §3 discussed its qualification but did not register it as a finding.
- **Correction to a commit message:** `62d3684`'s message says "20 failed, 52 passed" against `97b69ef`. That count was taken before the subnormal-coefficient test was added. The committed tests give **21 failed, 52 passed** (73 cases).
- **Count correction:** in the corrections table above and in `b0164fd`'s commit message, "11 F1/F2 mutants" should read **10** (3 F1 + 7 F2). The total is unchanged: 14 + 8 + 10 = 32.

## Validation of the correction pass (I-19 §10; recorded 2026-10-23 UTC, append-only)
Run at `16a8e63b0b209e08df94ed4df0f59c4991e0ac7a`, in fresh clones (M1 and M2 Proofs in separate clean clones), on the reference host:

| Check | Command | Result |
|---|---|---|
| M1 Proof | `bash toolbox/scripts/run_m1_proof.sh` | **PASS**, 9/9 steps, `working_tree_clean_excluding_evidence: yes`. Includes the M1 golden comparison and cross-process determinism |
| M2 Proof | `bash toolbox/scripts/run_m2_proof.sh <scratch evidence dir>` | **PASS**, 20/20 steps, tree clean. `m2_proof` 228/228. pytest **1254 passed**, 3 warnings. M1 golden hash `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. Ruff check and format pass |
| T0 checks | `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0*.py` | **314 passed** |
| Mutation | `python docs/science/experiments/m3-t1/t1_mutation_check.py OUT` | control passes; **32/32 detected, 32 by assertion, none surviving**. The summary equals the committed result file |
| Informational | `python docs/science/experiments/m3-t1/t1_j2_informational.py OUT` | byte-identical to the committed results |
| Correction check | `python docs/science/experiments/m3-t1/t1_review01_correction_check.py <97b69ef src> OUT` | reproduces the committed file byte for byte. 200 004 states bit-identical |
| Tree | `git status --porcelain` | clean |

- **pytest count:** 1254 = 1207 at `97b69ef` + 47 new T1 cases (73 T1 cases now, 26 before).
- **Protected paths:** `git diff 97b69ef..16a8e63 -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty. `src/` changes are confined to `src/tars/sim/forces.py`: `ZonalJ2Gravity`, its imports and `_MIN_NORMAL`.
- **CI:**
  - The correction commits `62d3684`, `a27f288` and `b0164fd` were pushed together; CI run **39894033142** ran on `b0164fd`. `16a8e63`: run **39894176897**.
  - The results, and the run on the commit that adds this section, are reported at the checkpoint.
  - Review 02 starts only after the final head's run is green on all four jobs.
