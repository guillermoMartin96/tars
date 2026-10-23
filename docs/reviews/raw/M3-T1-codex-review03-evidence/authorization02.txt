You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T1 Review 02** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T1 (the J2 force model). It is a fresh review of the correction pass made after T1 Review 01. You review; you do not fix. The implementer's records (the corrected code's docstrings, tests and comments, VAL-0020 and its correction section, the DR-0025 owner-disposition note, the T1 authorization packet's erratum, the Review 01 record and its appended sections, the T1 report, the experiment scripts and result files) are claims, not evidence: nothing in them is presumed correct. You are not limited to the Review 01 findings.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t1-j2-force-model`, detached at the pinned head **`1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available. GMAT is not provided; T1 contains no GMAT work (T5 scope).
  - A checkout of `src/` at the Review 01 SHA `97b69ef92e589ebd1b71016f49c4c9816d8c724b` is at `review_scratch/reviewed_src_97b69ef/src` (implementer-made with `git archive 97b69ef src`; you can recreate it yourself from git). `docs/science/experiments/m3-t1/t1_review01_correction_check.py` takes it as its first argument.
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Prefer writing experiment output into `review_scratch/` (every T1 script takes an output path). If you re-run anything in place, record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- <path>`, and report exactly what changed.
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run:
    - `pytest` (full suite about 25–30 min on this host; `tests/test_constants.py tests/test_zonal_j2.py` about 5 s);
    - `ruff check .` and `ruff format --check .`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0*.py` (about 3 min);
    - `docs/science/experiments/m3-t1/t1_j2_informational.py`, `t1_mutation_check.py` (about 3 min; copies `src/` to a temporary directory) and `t1_review01_correction_check.py`.
  - Finish with a clean tracked tree.
- **I-19 §10 preconditions were checked by the implementer, not by you.** You have no network and cannot authenticate CI. The implementer's statements of the CI facts are in "The implementer's claims" below, and the exported GitHub run metadata (`gh run view --json`) is in `review_scratch/ci/`. Treat these as implementer-supplied claims: inspect them for internal consistency and list CI authenticity as a verification limit. **This is not a reason to stop.** Perform the complete review; everything that can be checked locally must be checked.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.
- **Decision boundaries (I-19 §9, §13).** Do not resolve, and do not record as approved: DR-0029 P1–P9; Q-G2-1/P6; Q-G2-2; DR-0028 P6(b); the secular-rate tolerance or presentation; T4/T5 comparison requirements; the M3 final time step; the axis representation (T3). You may recommend. The owner's dual-number disposition (I-19 §7) is the owner's decision: assess whether it is **accurately recorded** and whether its independence is overstated anywhere; do not re-decide it.

## Commits
- **`main`** = `60648b93385a9954194730006aeac29ea14875ad` (contains the DR-0029 P10 decision).
- **T1 implementation** (reviewed by Review 01 at `97b69ef92e589ebd1b71016f49c4c9816d8c724b`): `5fd24a2`, `e23675c`, `81a0d56`, `97b69ef`.
- **Review 01 record:** `dbb960a` (`docs/reviews/M3-T1-review-01.md`, `docs/reviews/raw/M3-T1-codex-review01*`).
- **Correction pass under I-19** (`git log 97b69ef..1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4`):

  | Commit | Content (as claimed) |
  |---|---|
  | `62d3684` | Tests for F1–F4 (red against `97b69ef`) |
  | `a27f288` | `src/tars/sim/forces.py`: immutable `ZonalJ2Gravity`, explicit numerical domain |
  | `b0164fd` | `t1_mutation_check.py` (+ results), new `t1_review01_correction_check.py` (+ results) |
  | `16a8e63` | Records: DR-0025 owner disposition, packet erratum, VAL-0020 correction, Review 01 record appendices, status notes |
  | later commits, if any | validation records only (docs) — check |

## Review 01 findings and their current dispositions
| ID | Severity | Finding (Review 01) | Disposition |
|---|---|---|---|
| M3T1-R1-F1 | MINOR | `mu`, `equatorial_radius`, `j2` writable; cached coefficient stale after reassignment; contradicts the packet's immutability requirement | ACCEPTED; claimed corrected in `a27f288` |
| M3T1-R1-F2 | MINOR | silent numerical-domain loss: `r2*r2*r_norm` overflow gives exact zeros where the result is representable (x ≥ ~4.5e61 m); infinite μ/R accepted; tiny radius `ZeroDivisionError`; DR-0024 R6 | ACCEPTED; claimed corrected in `a27f288` |
| M3T1-R1-F3 | NOTE | test docstring: a·r ∝ r⁻⁴ should be r⁻³ | ACCEPTED; claimed corrected in `62d3684` |
| M3T1-R1-F4 | NOTE | finite mutation coverage: reviewer mutants `abs(j2)`, coefficient × (1 + 2⁻⁵¹), zero beyond 7 R, 1 % x/y error for 0.99 < s² < 0.9999 survived all 26 T1 cases; hex literal bypasses the regex | ACCEPTED; claimed corrected in `62d3684`, `b0164fd` |

Review 01's reviewer mutant diffs are in `docs/reviews/raw/M3-T1-codex-review01-evidence/mutant-diffs/` (against the `97b69ef` source).

## The implementer's claims for this pass (to verify, not to trust)
1. **F1.** `ZonalJ2Gravity` uses `__slots__` (no instance `__dict__`); `__setattr__` and `__delattr__` raise `AttributeError` for every name; no derived value is cached — the coefficient −(3/2) J2 μ R² is recomputed from the stored parameters on each call with the same operations, so results are unchanged.
2. **F2 contract** (class docstring; VAL-0020 correction): three classes, all `ValueError` with distinct messages — (1) valid inputs return the formula, bit-identical to `97b69ef`; (2) invalid-domain inputs rejected before state arithmetic (μ or R non-finite or ≤ 0; J2 non-finite; −(3/2) J2 μ R² not a finite normal binary64 unless J2 = 0; non-finite position; origin); (3) arithmetic outside the binary64 normal range ("outside the J2 numerical domain …": |r|² underflow to zero for a non-zero position; |r|⁵ not normal; scaled coefficient not normal; non-finite result). For canonical constants on the equator the accepted range is 3.3773820261812166e-57 m ≤ x ≤ 4.476546622757235e61 m. The physical boundary (surface/termination) is deliberately not enforced (DR-0029 P1–P9 open).
3. **Bit identity.** 200 004 valid states (seeded, 6 378 km–100 000 km, all latitudes) give bit-identical accelerations to `97b69ef`; the committed informational results reproduce byte for byte.
4. **F3.** Docstring corrected; assertion unchanged.
5. **F4.** New tests: exact power-of-two known answers (μ = R = 1, J2 ∈ {1/2, −1/2, 3/8}, r = 2^e, e ∈ {1, 10, 50, 100, 200}; claimed exact in binary64); far-field known answers to 1000 R (2γ₁₆); dense latitude gradient for ±J2 on 5 904 points; literal scan labelled a heuristic and extended to the hex spelling.
6. **Mutation.** 32 committed mutants (14 original, 8 reviewer, 10 F1/F2 protection removals; the VAL-0020 correction section and `b0164fd`'s message first said 11, corrected by appended notes; check the actual list), **32 killed, all by assertion** (classified from pytest JUnit XML), no survivors; `f2_infinite_parameters_accepted` is killed only via the diagnostic message (behaviourally redundant with the coefficient check).
7. **Red-first.** The committed tests give 21 failed / 52 passed against `97b69ef` (the `62d3684` commit message says 20/52, a count taken before one test was added — recorded).
8. **Records.** DR-0025 owner-disposition note (dual numbers accepted for T1, rationale as stated by the owner); packet erratum (+∇U); VAL-0020 correction section; Review 01 record appendices; status notes — all append-only.
9. **Regression and CI.** Local validation at `16a8e63` (records-only `1cf0ce9` adds no code): M1 Proof 9/9 and M2 Proof 20/20, each in a separate clean clone with a clean tree afterwards; `m2_proof` 228/228; pytest 1254 passed; M1 golden digest `7a4e1877…20a4` unchanged; T0 checks 314; mutation 32/32 by assertion; ruff clean; protected-path diff `97b69ef..16a8e63 -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` empty. CI (GitHub Actions, 4 jobs each: check on ubuntu-latest, macos-latest, macos-15-intel; m2-cross-platform), all `success`: `b0164fd` run 39894033142; `16a8e63` run 39894176897; `1cf0ce9` (this head) run 39897342033. Earlier: `dbb960a` run 39885659108; `97b69ef` run 39865621259. Exports are in `review_scratch/ci/`. `62d3684` and `a27f288` were pushed together with `b0164fd` and have no runs of their own (`62d3684` is red-first by design). You cannot authenticate any CI fact or the implementer's local runs; re-run what you can.

## Tech Lead's authorization I-19 (this review), verbatim
# I-19 — M3 T1 Review 01 Corrections and Review 02 Authorization

I accept the I-18 checkpoint and Codex Review 01 result.

T1 remains:

**IMPLEMENTED — NOT REVIEW-ACCEPTED — NOT MERGED**

The Review 01 `REQUEST_CHANGES` verdict stands. The four reproduced findings M3T1-R1-F1 through M3T1-R1-F4 are accepted for correction.

## 1. Review 01 execution disposition

The attempt-1 / attempt-2 handling is **ACCEPTED**.

Treat both sessions together as **Review 01**, not as Review 01 and Review 02.

Rationale:

- Attempt 1 did not perform a substantive review.
- It ran no tests and produced no findings.
- Its stop resulted from a prompt/environment mismatch: the reviewer was asked, implicitly, to verify CI state it could not access.
- Attempt 2 reviewed the same T1 implementation SHA, `97b69ef92e524b`, from a fresh clone.
- The added paragraph supplied already-established precondition/CI information and documented the reviewer's inability to verify that external state; it did not change the implementation under review or bias the reviewer toward a desired technical conclusion.
- Both attempts have been preserved, so the execution history remains auditable.

Record this disposition in the T1 review/acceptance trail. Do not rewrite or delete either raw session.

## 2. Authorized correction scope

You are authorized to correct exactly:

- **M3T1-R1-F1 — MINOR:** enforce the required immutability of J2 force-model parameters.
- **M3T1-R1-F2 — MINOR:** eliminate the identified silent numerical failure modes and bring invalid/non-finite behavior into conformance with the applicable contract.
- **M3T1-R1-F3 — NOTE:** correct the erroneous radial-dot-product scaling statement from r^-4 to r^-3.
- **M3T1-R1-F4 — NOTE:** strengthen the T1 mutation/verification coverage so the demonstrated surviving mutants are killed by meaningful assertions, including the uncovered high-latitude band behavior.

The correction pass may add or strengthen tests, validation evidence, reproduction artifacts and documentation necessary to prove those corrections.

Do not use this authorization for unrelated refactoring, architecture changes, performance work, or expansion of T1 scope.

## 3. F1 requirements

Correct parameter mutability at the appropriate ownership boundary.

After construction, the force model's physical parameters must not admit reassignment that creates disagreement between externally visible state and the values actually used by the force calculation.

Add regression coverage demonstrating the invariant.

Do not merely hide the reproduced example while retaining another supported mutation path with the same inconsistency.

## 4. F2 requirements

Correct the reproduced extreme-input behavior consistently with the governing numerical/error-handling contracts.

At minimum, explicitly test the reproduced classes of failure:

- finite inputs whose intermediate arithmetic overflows or becomes non-finite;
- extremely small/nonphysical radius inputs;
- any path where the implementation could otherwise silently return a finite-looking acceleration after invalid intermediate arithmetic.

The correction must not change valid realistic-orbit J2 results merely to accommodate pathological inputs.

Preserve the distinction between:

1. valid physical inputs;
2. invalid-domain inputs; and
3. arithmetic that becomes non-finite during evaluation.

Record the exact resulting contract and evidence.

Do not broaden this into a general numerical-policy redesign for unrelated force models.

## 5. F3 requirements

Correct the inaccurate test/documentation statement only.

The radial dot product `a·r` scales as r^-3 for the tested J2 relation.

Do not alter correct physics or assertions merely to match the old wording.

## 6. F4 requirements

The existing statement that the committed mutation campaign is effective must be supported by the actual tests.

Add meaningful coverage sufficient to kill the reproduced surviving mutants, including coverage of the identified high-latitude gap.

Do not satisfy this requirement with tests that merely inspect source text or implementation literals.

After correction, rerun the committed mutation campaign and report:

- total committed mutants;
- mutants killed;
- any surviving mutants;
- which real assertions kill the newly covered cases.

If any committed mutant survives, do not claim complete mutation coverage.

## 7. Dual-number substitution disposition

The dual-number derivative substitution is **ACCEPTED for T1** as the independent unit-level derivative check, subject to the limitations already identified by Review 01.

Record the disposition in DR-0025 or the appropriate authoritative decision record.

The rationale must state that:

- it checks the same required derivative;
- it is sufficiently independent for the intended unit-level verification purpose;
- it removes the complex-square-root and finite-step-size assumptions of the previous approach;
- it still shares ordinary floating-point arithmetic and scalar-square-root assumptions and therefore is not an independent external physics implementation;
- its acceptance does not elevate it into external corroboration or a proof of IEEE-754 rounding behavior.

Do not expand T1 to build another derivative oracle unless Review 02 demonstrates that this disposition is insufficient.

## 8. Authorization-packet sign inconsistency

Append a correction/erratum for the T1 authorization packet statement that says:

`acceleration = -∇U`

For the positive-potential convention actually used by T1 and VAL-0020, the applicable relation is:

`acceleration = +∇U`

Preserve the original authorization packet/history; do not silently rewrite historical evidence.

The correction must make clear that this is a documentation/sign-convention error in the packet, not a change to the implemented J2 physics.

Verify the correction against the governing potential convention and the independently derived Review 01 result before recording it.

## 9. Preserve unresolved items

Do **not** resolve, silently close, or expand scope into the currently open items merely because they were mentioned by Review 01.

They remain open unless already governed by an existing decision:

- DR-0029 P1–P9;
- Q-G2-1 / P6;
- Q-G2-2;
- DR-0028 P6(b);
- secular-rate tolerance/presentation;
- T4/T5 comparison requirements;
- M3 final time step;
- axis representation/T3 scope;
- lack of external corroboration;
- the broader IEEE-754 rounding-model assumption.

The unexplained dt^5 drift observation remains an observation unless new evidence establishes a defect.

Do not expand T1 to investigate unrelated CI metadata oddities unless they affect reproducibility, correctness, or review integrity.

## 10. Validation before Review 02

After applying the corrections, run the complete validation appropriate to T1.

At minimum verify:

- all T1 tests;
- the strengthened mutation checks;
- T0 checks;
- M1 regression/golden/determinism validation;
- M2 validation;
- lint/static checks required by the repository;
- all relevant CI jobs.

Confirm that M1 and M2 behavior remains unchanged.

Record the exact commit(s), commands, results and CI run identifiers.

Do not start Review 02 while required CI is red or pending.

## 11. Independent Review 02

If and only if the correction pass and required validation are green, launch **Codex Independent Review 02** from the corrected T1 head.

Review 02 must independently verify at least:

1. R1-F1 through R1-F4 are actually resolved.
2. The parameter-immutability implementation satisfies the intended invariant rather than only the original reproduction.
3. F2 no longer permits the reproduced silent numerical failures and does not damage realistic-orbit behavior.
4. The corrected r^-3 statement is mathematically and experimentally consistent.
5. The strengthened mutation suite kills the previously demonstrated surviving mutants.
6. The dual-number disposition is accurately recorded and its independence is not overstated.
7. The `+∇U` authorization-packet erratum is consistent with the implemented potential convention and VAL-0020.
8. M1/M2 regression guarantees remain intact.
9. No unrelated scope was introduced.
10. No new correctness, verification, provenance, or reproducibility defect has been introduced.

Provide the reviewer the necessary repository-local evidence and already-established external CI facts, clearly identifying anything the review environment cannot independently access.

Do not steer the reviewer toward PASS.

## 12. Stop conditions

If Review 02 returns `REQUEST_CHANGES`, or identifies any new BLOCKER, MAJOR, MINOR, or NOTE requiring owner disposition:

- reproduce and classify the finding independently;
- record the evidence and proposed disposition;
- do **not** fix the new finding;
- do **not** start Review 03;
- stop and report back to me.

If Review 02 returns an unconditional `PASS` with no unresolved review findings:

- prepare the T1 acceptance dossier/status report;
- do **not** accept T1 on my behalf;
- do **not** merge T1;
- stop for my explicit acceptance decision.

## 13. Scope boundaries

This authorization does **not** authorize:

- accepting T1;
- merging T1;
- starting T2 or T3;
- deciding DR-0029 P1–P9;
- resolving Q-G2-1/P6, Q-G2-2, or DR-0028 P6(b) beyond existing authority;
- changing M3's final time step;
- expanding T1 into external corroboration work;
- unrelated production changes.

Use ordinary commits and pushes only. No force-push.

At the next checkpoint report the branch, exact HEAD/origin SHA, worktree state, commits made, changed paths, local validation, CI state, disposition of every Review 01 finding, the recorded dual-number/sign-convention decisions, and the complete Review 02 verdict/evidence.

Proceed with the Review 01 correction pass and, if all gates above are satisfied, Independent Review 02.

## Earlier Tech Lead authorizations
I-17 (T1 authorization) and I-18 (Review 01) are reproduced verbatim in `docs/reviews/raw/M3-T1-codex-review01-prompt.md`. Read them there.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical argument**: for every exactness, bound or contract claim, check the proof against the code, and use sweeps to seek counterexamples. **Actively try to falsify**: construct mutation paths, inputs and wrong implementations that the corrected tests accept.
1. **R1-F1 … R1-F4 resolved?** For each, decide independently, re-running Review 01's reproductions and your own.
2. **F1 invariant, not just the reproduction (I-19 §3).** Look for any supported path by which externally visible parameters can disagree with the values used (assignment, deletion, new attributes, `__dict__`, `vars()`, `copy`/`deepcopy`/`pickle`, `dataclasses.replace`-like patterns, subclassing, class-attribute mutation of `name`/`version`, NumPy scalar inputs, mutable inputs). State which paths you consider "supported" and why; distinguish deliberate bypasses such as `object.__setattr__`.
3. **F2 (I-19 §4).** Verify the three-class contract against the code; search for any remaining path returning a finite-looking or zero acceleration after invalid intermediate arithmetic (all components, off-axis points, near the domain boundaries, NumPy inputs, signed zeros, subnormal inputs, J2 = 0 with extreme radii, extreme but valid parameters); check that each error message matches its class; check the claimed domain bounds independently; verify that valid realistic-orbit results are unchanged (bit identity vs `97b69ef`, your own sampling, RK4 trajectories). Judge whether the contract is stated exactly and whether anything is claimed beyond it.
4. **F3.** Mathematical and experimental consistency of the r⁻³ statement.
5. **F4 and the mutation suite.** Verify the exactness argument of the power-of-two test operation by operation; verify the dense grid covers what is claimed; re-run `t1_mutation_check.py`; verify that each previously surviving mutant is killed by a meaningful assertion (not by source inspection, collection errors or unexpected exceptions); check the JUnit-based classification for correctness (could a non-assertion failure be classified as an assertion, or a stale JUnit file be read?); write your own new mutants against the corrected code, including mutants that evade the new tests.
6. **Dual-number disposition (I-19 §7).** Verify that DR-0025's note records the owner's disposition and rationale accurately and append-only, and that no record (including VAL-0020, test docstrings and the Review 01 record) overstates the method's independence or presents it as external corroboration or proof of IEEE 754 rounding.
7. **+∇U erratum (I-19 §8).** Verify it against the potential convention, the implemented acceleration, VAL-0020 and the gradient tests; verify the original packet text is preserved.
8. **M1/M2 regression.** Run pytest, the M1/M2 validators (output into `review_scratch/`), the M1 golden and determinism checks; verify `git diff 60648b9..1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4 -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty and that `src/` changes are confined to `src/tars/sim/constants.py` and `src/tars/sim/forces.py` (the latter only in `ZonalJ2Gravity` and its imports).
9. **Scope.** No unrelated production, architecture, performance or T2–T5 work; no decision resolved.
10. **New defects.** Search for new correctness, verification, provenance or reproducibility defects introduced by the correction pass, including in the records (check every number quoted in the new record sections against the code, result files and your own computation; check append-only status with `git diff 97b69ef..1cf0ce9311fc9bc8e0cb4cfec41a3ae07d782ca4 -- docs`).
11. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** environment; every command run with key output; every result file inspected; for each conclusion, whether it rests on your own execution/computation or only on documentation.
2. **Resolution table:** M3T1-R1-F1 … F4, each exactly one of RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with evidence and reasoning.
3. **Assessment of I-19 §11 items 1–10**, each separately.
4. **New findings.** Number them `M3T1-R2-F1`, `M3T1-R2-F2`, …. Each gives: severity (BLOCKER, MAJOR, MINOR or NOTE, as defined in I-18 §4); exact file and line references; reproduction or independently checkable reasoning; consequence; recommended correction; relevant decision or validation requirement; whether it is a defect, a proposed enhancement or an unresolved decision; **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**. Do not report a finding without concrete evidence.
5. **Adversarial attempts** and their outcomes.
6. **Verification limits.**
7. **T1 acceptance-readiness assessment.**
8. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding, or any Review 01 finding that is not RESOLVED, requires REQUEST_CHANGES. NOTEs alone permit PASS.
9. Write the complete review, identical to your final message, to `review_scratch/M3-T1-codex-review02.md`, save your scripts and logs under `review_scratch/`, and keep a command ledger in `review_scratch/COMMANDS.md`.
