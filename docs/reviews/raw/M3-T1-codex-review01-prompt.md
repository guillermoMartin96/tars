You are an independent reviewer from a separate provider; you did not write any of the files under review. This is **M3 T1 Review 01** of the TARS spacecraft simulator's Milestone 3 (J2 + atmospheric drag), Task T1 (the J2 force model). It is the first independent review of T1. You review; you do not fix. The implementer's records (the T1 report, VAL-0020, the SCI-0013 status update, test docstrings and comments, the experiment README and result files) are claims, not evidence: nothing in them is presumed correct. Do not substitute the implementer's report for your own verification.

## Snapshot and rules
- **The current directory** is a fresh git clone of branch `milestone-3-t1-j2-force-model`, detached at the pinned head **`97b69ef92e589ebd1b71016f49c4c9816d8c724b`** (full SHA), with git metadata.
  - A ready, locked Python environment is in `./.venv`. Use `.venv/bin/python` or `uv run --no-sync`.
  - The network is not available. GMAT is not provided; T1 contains no GMAT work (T5 scope).
- **Do not modify tracked files.**
  - Put scratch files, mutated copies and your own scripts only under `./review_scratch/`, which is excluded from git.
  - Re-running the committed T1 experiments in place rewrites their result files. That is allowed only if you then record `git status --porcelain` and `git diff --stat`, restore with `git checkout -- docs/science/experiments/m3-t1`, and report exactly what changed. Prefer writing their output into `review_scratch/` (both scripts take an output path argument).
  - Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`; they write into `proof/records/evidence/`. You may run:
    - `pytest` (full suite about 25 min on this host; `tests/test_constants.py tests/test_zonal_j2.py` about 1 min);
    - `ruff check .` and `ruff format --check .`;
    - the validators in `toolbox/validators/`, with `--out` into `review_scratch/`;
    - the T0 checks: `pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review0*.py` (about 3 min);
    - `docs/science/experiments/m3-t1/t1_j2_informational.py` (a few minutes) and `t1_mutation_check.py` (copies `src/` to a temporary directory; does not modify the tree).
  - Finish with a clean tracked tree.
- **I-18 §1 preconditions were checked by the implementer, not by you.** I-18 §1 is addressed to the implementer and was verified before this review was launched:
  - branch `milestone-3-t1-j2-force-model`, HEAD and origin both `97b69ef92e589ebd1b71016f49c4c9816d8c724b`, clean tree;
  - `main` = `60648b9`, containing the P10 decision;
  - no change to protected M1/M2 artifacts since `60648b9`;
  - final CI: I-18 §1 writes run `39865621`; the run on `97b69ef` is **39865621259** (the I-18 number is its leading eight digits; no other run in the repository's 200 most recent runs has that prefix). It completed with success on all four jobs.

  You have no network, so you cannot authenticate CI. The implementer exported the GitHub run metadata (`gh run view --json`) of runs 39852509134, 39853032093 and 39865621259, and the pytest excerpts of the three platform `check` jobs of run 39852509134, into `review_scratch/ci/`. Treat these as implementer-supplied claims: inspect them, check them for internal consistency, and list CI authenticity as a verification limit. **This is not a reason to stop.** Perform the complete review; everything that can be checked locally must be checked.
  - *Note:* an earlier invocation of this review (attempt 1) stopped at these preconditions because this prompt did not state that the implementer had checked them. That attempt produced no review; it is preserved and recorded, and you are not shown it.
- **A PASS must be unconditional.** Acceptance criteria are not relaxed. A guarantee that is explicitly conditional on a stated, unresolved assumption is not by itself a defect, but you must judge whether the condition is stated honestly and completely, and whether anything is claimed beyond it.
- **Decision boundaries (I-18 §5).** Do not resolve, and do not record as approved: DR-0029 P1–P9; Q-G2-1/P6; Q-G2-2; the secular-rate acceptance tolerance; the T3 axis representation; T4/T5 external-comparison requirements; the M3 final time step. You may recommend. Do not introduce a secular-rate gate without a justified tolerance. Do not amend DR-0025 or accept the dual-number substitution: assess it.

## Commits
- **`main`** = `60648b93385a9954194730006aeac29ea14875ad` (contains the DR-0029 P10 decision; fast-forwarded under I-17). T1 branches from it.
- **T1 commits** (`git log 60648b9..97b69ef`):

  | Commit | Content (as claimed) |
  |---|---|
  | `5fd24a2` | Tests first (red): `tests/test_constants.py` (extended), `tests/test_zonal_j2.py` (new) |
  | `e23675c` | `src/tars/sim/constants.py`, `src/tars/sim/forces.py` (additive) |
  | `81a0d56` | VAL-0020 (`docs/science/validation.md`), SCI-0013 status update 4 (`docs/science/assumptions.md`), `docs/science/experiments/m3-t1/` |
  | `97b69ef` | `docs/milestones/M3-T1-report.md`; append-only status notes in `docs/milestones/M3-T1-authorization-packet.md`, `docs/milestones/M3-decision-matrix.md`, `docs/milestones/README.md` |

## Records to read
- Authority: I-17 and I-18 (verbatim below); `docs/milestones/M3-T1-authorization-packet.md`.
- Decisions: `docs/decisions/requests/DR-0024-…` through `DR-0029-…` (including `DR-0029-P10-owner-decision-packet.md`); ADR-0003, ADR-0004 and ADR-0009 in `docs/decisions/`.
- Science: SCI-0013 in `docs/science/assumptions.md` (all status updates); VAL-0018 and VAL-0020 in `docs/science/validation.md`.
- Plan and acceptance: `docs/milestones/M3-proposal.md` (§4 T1, §5 validation), `docs/milestones/M3-baseline-and-impact.md`, `proof/PROOF.md`, `proof/review.md`, `proof/definition-of-done.md`.
- Code: `src/tars/sim/constants.py`, `src/tars/sim/forces.py`, `src/tars/sim/integrators.py`, and any consumer of the force protocol.
- Tests and evidence: `tests/test_constants.py`, `tests/test_zonal_j2.py`, `docs/science/experiments/m3-t1/` (README, both scripts, both result files).

## The implementer's claims (to verify, not to trust)
1. **Constant identity.** C̄2,0 = −0.484165143790815e-3 (EGM2008 tide-free, NGA.STND.0036 Table 5.1) is the only authoritative literal; J2 = −√5·C̄2,0 is derived (`-math.sqrt(5.0) * c20`), = 1.0826261738522227e-3 = `0x1.1bcdd00abd9aap-10`; the decimal 1.0826261739e-3 is its 11-significant-digit display form, 4.41e-11 relative from J2 (220 334 ulps). No J2 literal exists in `src/`.
2. **Correct rounding.** Under IEEE 754 the derivation is deterministic; the tests verify correct rounding of `sqrt(5)` and of the product with exact rationals on each platform rather than assuming it.
3. **Cross-platform.** CI run 39852509134 (on `e23675c`) passed the constant tests on ubuntu-latest, macos-latest (arm64) and macos-15-intel, so J2 is bit-identical there. CI runs 39853032093 (`81a0d56`) and 39865621259 (`97b69ef`) were green on all four jobs. (You cannot verify CI; say so.)
4. **Force.** `ZonalJ2Gravity` (`zonal_j2`, v1) implements the J2 perturbing acceleration about frame +Z, through the existing `acceleration(t, r, v)` protocol, with no axis/mass/context/orientation dependency, pure and unwired.
5. **Error bounds.** Known answers within 2γ₁₆; the gradient check within γ₆₄·(sum of both evaluations in absolute value), based on Higham's forward error analysis, with operation counts "by inspection" (≤ 13 for the acceleration, ≤ 40 for the dual-number gradient). Largest observed error 3.6 % of the bound.
6. **Exact assertions.** Axisymmetry under a 90° rotation and z-reflection; J2 = 0 bitwise equal to point mass (single evaluations and 600 RK4 steps); polar orbit y = v_y = 0 exactly over 5 370 steps.
7. **Invariant drift gate.** drift(dt 5 s)/drift(dt 20 s) ≤ 1/2, fixed before measurement from RK4's O(dt⁴) global error vs ≈ 1 for a non-conservative force. Measured ≈ 1.2e-3 (energy), ≈ 9.8e-4 (h_z). Observed drift order ≈ 5, "not explained".
8. **Secular rates (informational).** Node rate within −0.27…+0.26 % of first-order theory; perigee within ≤ 1 % except at the critical inclination (0.011 °/day vs ≈ 0). No tolerance; not gated.
9. **Mutation.** 14 one-line production mutants all detected; the control passes.
10. **Derivative method.** Forward-mode dual numbers replace the complex step named in DR-0025 Q3; claimed to test the same derivative without a libm assumption.
11. **Regression.** M1 Proof 9/9 and M2 Proof 20/20 (m2_proof 228/228) at `81a0d56`; pytest 1207; T0 checks 314; protected paths unchanged since `60648b9`; `src/` diff purely additive.

## Tech Lead's authorization I-17, verbatim
# I-17 — Merge P10 Decision and Authorize M3 T1 J2 Force Model

DR-0029 P10 is DECIDED — Option (a).

M3 Task T1 is authorized subject to the gates and scope below.

## 1. CI gate before proceeding

Before merging or creating the T1 branch, wait for CI on:

`60648b9`

Proceed only if all required CI jobs pass.

If CI fails:

**STOP.**

Report the failure and do not merge the P10 branch or create T1.

## 2. Merge the P10 decision branch

If CI is green, fetch and verify:

- `origin/main` remains `5fded7c6df50d60564f2bd025aeaf9dab4f541cd`;
- `origin/m3-p10-decision-packet` is at `60648b9`;
- the decision branch is clean;
- it contains only the authorized documentation/decision work;
- it descends directly from the expected main baseline;
- a strict fast-forward merge is possible.

If any condition differs, STOP and report it.

If all conditions pass:

1. fast-forward `main` to `60648b9`;
2. use no merge commit;
3. do not squash or rebase;
4. push by ordinary fast-forward push only;
5. verify local `main` and `origin/main` both equal `60648b9`.

P10 should therefore become part of the authoritative baseline before T1 begins.

Do not delete the decision branch under this authorization.

## 3. Create T1 branch

After the P10 merge is verified, create:

`milestone-3-t1-j2-force-model`

from the new `main` at `60648b9`.

T1 must therefore begin with the recorded P10 decision already in its ancestry.

## 4. T1 objective

Implement the M3 J2 force component as an independently testable force model.

T1 does **not** integrate J2 into scenarios, missions or the production mission runner.

The implementation must preserve the architectural invariant established by P10:

**one canonical C̄₂₀ value → derived J2 → all downstream representations**

There must not be an independently authoritative J2 literal.

## 5. Constants

Add the M3 constant representation described in the authorization packet while leaving the existing WGS84 constants unchanged unless an already-approved plan explicitly requires otherwise.

Canonical value:

`C̄₂₀ = −0.484165143790815e−3`

Derive:

`J2 = −√5 × C̄₂₀`

Do not introduce an independently maintained J2 physical constant.

Tests must establish the intended binary64 derivation and the relationship between the derived value and the rounded/display value from DR-0024 Q1.

Do not convert the display representation into a second source of truth.

## 6. J2 force component

Implement the planned version-1 `zonal_j2` force component using the existing:

`acceleration(t, r, v)`

interface.

For T1:

- retain the existing force interface;
- do not introduce the T2 mass-carrying interface;
- do not perform speculative interface work for T2;
- keep the J2 symmetry axis fixed to the frame **+Z axis**;
- do not introduce an injectable or configurable axis;
- do not add an Earth-orientation model.

Configuration of the axis belongs to later authorized work.

The point-mass contribution must remain independently evaluated as required by the approved design.

## 7. Test-first implementation

Follow the proposed test-first sequence.

Tests must independently exercise the implementation rather than merely reproducing its internal computation.

Include the planned checks for:

- canonical C̄₂₀ and derived J2;
- deterministic binary64 derivation;
- rounded/display-value relationship;
- independently expressed potential-gradient comparison;
- sign behavior;
- limiting cases;
- `J2 = 0` reducing exactly to the intended point-mass behavior;
- conservation behavior appropriate to the autonomous axisymmetric model;
- energy;
- z-component of angular momentum;
- node drift;
- perigee drift;
- RK4 convergence characterization;
- M1 regression;
- M2 regression;
- golden-output preservation where required by the approved plan.

M1/M2 protected outputs must remain byte-identical where that is an existing invariant.

## 8. Numerical tolerances

Do not invent, tune or reverse-engineer an acceptance tolerance from observed output merely to make a test pass.

In particular, the approximate analytical node/perigee drift comparison must not acquire an arbitrary threshold based on the implementation's measured error.

If an approved analytical or numerical basis establishes a defensible tolerance, document that derivation and use it.

Otherwise:

1. calculate the comparison;
2. report the measured discrepancy;
3. record why no acceptance threshold has yet been justified;
4. classify the check as informational/non-gating as appropriate;
5. raise the issue in the T1 report.

A reported comparison must not be presented as a validated acceptance criterion unless its tolerance has been independently justified.

## 9. Validation record

Create the planned:

`VAL-0020`

and the appropriate append-only SCI-0013 status update.

Clearly distinguish:

- analytical expectations;
- measured results;
- regression checks;
- acceptance criteria;
- informational/non-gating measurements;
- unresolved assumptions.

Do not strengthen an empirical observation into a proof or bound.

## 10. Scope exclusions

T1 does not authorize:

- drag or atmosphere implementation;
- T2;
- the mass-carrying force interface;
- scenario version 3;
- mission-runner integration;
- the M3 physics-identity record assigned to later work;
- M3 Proof implementation;
- T4 validators;
- T5 GMAT reference generation;
- Earth-orientation modeling;
- configurable J2 axes;
- changes to the lock file unless an unforeseen necessity is reported and separately authorized;
- changes to workflows;
- changes to branch protection;
- resolution of DR-0029 P1–P9;
- resolution of Q-G2-1/P6;
- resolution of Q-G2-2;
- resolution of DR-0028 P6(b);
- selection of the final M3 time step.

Do not pull later milestone work forward merely because it would make T1 more convenient.

## 11. Cross-platform requirement

The P10/J2 representation must be exercised by CI on the project's required platforms.

Specifically determine whether the derived J2 binary64 representation is identical on:

- Ubuntu CI;
- macOS CI;
- macOS Intel CI.

Do not assume cross-platform bit identity from the single-host T0 evidence.

If the representation differs across required platforms:

**STOP and report the discrepancy before proceeding with acceptance preparation.**

Do not hide the discrepancy behind a tolerance.

Q-G2-2 remains unresolved; T1 testing must not silently convert its proposed rule into an approved project-wide rule.

## 12. Stop conditions

Stop and return for owner direction if:

- CI on `60648b9` fails;
- the P10 branch cannot be strictly fast-forwarded;
- the expected main baseline has moved unexpectedly;
- T1 requires functionality assigned to T2/T3/T4/T5;
- a required tolerance cannot be justified and the affected check must be gating;
- the canonical/derived constant architecture cannot be maintained;
- derived J2 differs across required CI platforms;
- a protected M1/M2 output changes unexpectedly;
- an existing approved architecture must be changed;
- a new decision is required.

Do not make an architectural decision merely to unblock yourself.

## 13. Completion gate

When the scoped T1 implementation and validation are complete:

1. ensure the T1 branch is pushed;
2. ensure the working tree is clean;
3. run the complete required local validation;
4. obtain green CI on the T1 HEAD;
5. prepare the T1 implementation/validation report.

Then **STOP before independent review**.

Do not invoke Codex or begin another independent-review cycle without separate owner authorization.

Do not merge T1.

Do not begin T2.

## 14. Final T1 implementation report

Return:

1. P10 merge result and resulting `main` commit;
2. T1 branch and exact HEAD;
3. commits created;
4. files changed;
5. implementation summary;
6. exact canonical and derived constant representations;
7. cross-platform bit-identity result;
8. tests and validation results;
9. analytical drift predictions versus measured values, clearly distinguishing informational checks from gates;
10. M1/M2 regression results;
11. VAL-0020 status;
12. unresolved assumptions or limitations;
13. confirmation that excluded work was not performed;
14. confirmation that T1 is **IMPLEMENTED, NOT REVIEWED, NOT ACCEPTED, NOT MERGED**.

Then stop for authorization of the independent T1 review.

## Tech Lead's authorization I-18 (this review), verbatim
# Authorization I-18 — M3 T1 Independent Codex Review 01

**Decision: AUTHORIZE INDEPENDENT REVIEW ONLY.**

T1 remains IMPLEMENTED, NOT REVIEWED, NOT ACCEPTED, NOT MERGED.

## 1. Preconditions

Before beginning, verify:

- Branch: `milestone-3-t1-j2-force-model`
- HEAD and origin: `97b69ef92e589ebd1b71016f49c4c9816d8c724b`
- Working tree clean.
- Final CI run `39865621` has all four jobs green.
- `main` contains the P10 decision at `60648b9`.
- No unexpected changes to protected M1/M2 artifacts.

If any precondition fails, stop and report the discrepancy.

## 2. Independent review

Invoke Codex as an independent reviewer.

Codex must inspect the actual repository implementation, tests, scientific decisions, validation evidence, and T1 authorization packet.

Do not substitute the implementation author's report for independent verification.

Review against DR-0024 through DR-0029, the T1 authorization packet, SCI-0013, VAL-0020, and applicable M3 acceptance requirements.

Do not modify production code or correct findings during this review.

## 3. Required review areas

### A. Physical correctness

Verify:

- EGM2008 C̄₂₀ normalization and sign convention.
- `J2 = -sqrt(5) × C̄₂₀`.
- Consistency with the approved WGS84 gravitational parameter and equatorial radius.
- J2 acceleration equations, dimensional correctness, and coordinate conventions.
- Equatorial, polar, off-axis, and zero-J2 behavior.
- Axisymmetry and radial-sign properties.
- Singularities, invalid inputs, and floating-point edge cases.

Independently derive the expected acceleration rather than relying exclusively on implementation tests.

### B. Numerical correctness

Examine:

- Binary64 constant derivation and cross-platform bit identity.
- Whether the claimed rounding behavior follows from IEEE 754 guarantees or platform-specific observations.
- The operation counts underlying γ₁₆ and γ₆₄.
- Potential cancellation, overflow, underflow, and intermediate rounding.
- Whether tolerance bounds actually cover their asserted error sources.
- Whether exact-equality assertions are mathematically and computationally justified.

Distinguish proven guarantees from empirical observations and assumptions.

Do not silently adopt Q-G2-2.

### C. Independent scientific validation

Review:

- Known-answer tests at the equator and pole.
- The separately implemented potential-gradient comparison.
- Conservation of energy and axial angular momentum.
- Long-duration integration behavior.
- RK4 convergence and invariant-drift measurements.
- Secular node and perigee precession comparisons.
- Critical-inclination behavior.
- Polar-orbit stability.

Determine whether the tests could pass despite an incorrect J2 implementation.

Evaluate whether the reported `dt⁵` invariant-drift behavior is a defect, an unexplained observation, or a documentation limitation. Do not invent an explanation.

### D. DR-0025 derivative-method substitution

The implementation uses forward-mode dual numbers instead of the complex-step method named in DR-0025.

Assess independently whether the substitution:

1. Tests the same mathematical derivative.
2. Preserves sufficient independence from the production acceleration implementation.
3. Avoids additional unverified numerical assumptions.
4. Meets or exceeds the intended validation strength.
5. Requires an explicit decision-record amendment.

**This substitution is not yet accepted by this authorization.**

### E. Architecture and regression isolation

Verify:

- `ZonalJ2Gravity` conforms to the existing force interface.
- No unauthorized mass, context, orientation, or state dependencies were introduced.
- The implementation remains additive and unwired.
- M1/M2 behavior and protected artifacts remain unchanged.
- T2, T3, T4, T5, scenario v3, and M3 Proof remain outside T1.
- No new dependency, workflow, lockfile, or branch-protection changes occurred.

### F. Test quality and mutation resistance

Examine the new tests and all 14 mutation cases.

Determine whether they provide independent evidence or merely reproduce implementation assumptions.

Identify missing boundary tests, correlated test oracles, insufficient assertions, and untested scientific behavior.

## 4. Findings and severity

Classify findings as:

- **BLOCKER:** Invalidates essential physical correctness, scientific evidence, or required isolation.
- **MAJOR:** Substantial correctness, numerical, architecture, or verification defect.
- **MINOR:** Limited defect requiring correction before acceptance.
- **NOTE:** Nonblocking clarification, improvement, or documented limitation.

For every finding, provide:

- Unique finding ID.
- Severity.
- Exact file and line references.
- Reproduction or independently checkable reasoning.
- Consequence.
- Recommended correction.
- Relevant decision or validation requirement.

Clearly distinguish defects from proposed enhancements and unresolved decisions.

## 5. Decision boundaries

Do not independently resolve:

- DR-0029 P1–P9.
- Q-G2-1/P6.
- Q-G2-2.
- The secular-rate acceptance tolerance.
- T3 axis representation.
- T4/T5 external comparison requirements.
- Any remaining M3 final-time-step decision.

You may recommend decisions, but do not record them as approved.

Do not introduce a secular-rate gate without a justified tolerance.

Do not amend DR-0025 or accept the dual-number substitution on my behalf.

## 6. Review deliverables

Produce:

1. Independent Codex Review 01 report.
2. Raw reviewer output.
3. Findings register with severity and reproducible evidence.
4. Assessment of each unresolved T1 assumption.
5. T1 acceptance-readiness assessment.
6. Explicit review verdict: `PASS` or `REQUEST_CHANGES`.

Record the review using the repository's established append-only documentation conventions.

If the review is PASS, prepare an acceptance recommendation for my consideration, but do not accept T1.

If the review is REQUEST_CHANGES, record and independently reproduce findings where feasible, but do not correct them.

## 7. Stop conditions

After recording the review:

**STOP and return the report to me.**

Do not:

- Fix findings.
- Start Review 02.
- Merge T1.
- Mark T1 accepted.
- Start T2 or T3.
- Modify unrelated milestones.
- Resolve outstanding architecture or scientific decisions.

Ordinary fast-forward pushes of authorized review documentation are permitted. No force-pushes.

## 8. Final report

Report the exact branch, HEAD, origin, working-tree state, commits, CI status, Codex verdict, findings, independently reproduced evidence, and unresolved decisions.

End with:

**T1 STATUS: IMPLEMENTED — REVIEWED — NOT ACCEPTED — NOT MERGED.**

If review execution cannot complete, state the actual review status instead.

Await my next authorization.

## What to review
Evaluate each item independently, with your own derivation, execution or computation wherever possible. **A numerical sweep is not a substitute for a valid mathematical argument**: for every bound or exactness claim, check the proof against the code, and use sweeps to seek counterexamples. **Actively try to falsify**: construct an incorrect J2 implementation that the tests accept, inputs that break a bound, and states where an exact assertion would fail.
1. **Physical correctness (I-18 §3 A).** Derive the J2 potential and acceleration yourself from the fully normalized C̄2,0 (normalization factor √5 for n = 2, m = 0; sign convention U = (μ/r)[1 − J2 (a/r)² P₂(sin φ)]), check dimensions and frame, and compare to the code. Check the WGS 84 μ and a used, equatorial/polar/off-axis/J2 = 0 behaviour, axisymmetry, the radial-sign boundary (35.26°), r → 0, very large r, non-finite inputs, subnormal and overflowing coordinates, and parameter validation.
2. **Numerical correctness (I-18 §3 B).** Verify the binary64 derivation and whether correct rounding is guaranteed by IEEE 754 (and by CPython's `math.sqrt` and float `*`) or only observed. Recount the operations behind γ₁₆ and γ₆₄ for every path the bound is applied to, including the dual-number arithmetic and the "absolute" evaluation; check that the bounds cover every error source they claim to (including the final comparison itself), and where overflow/underflow/cancellation could invalidate them over the sampled domain. Check every exact-equality assertion for mathematical and computational justification (e.g. which IEEE properties make the rotation and reflection exact, why J2 = 0 gives bitwise point mass in `CompositeForceModel`, why the polar y-components are exactly zero). Distinguish proven guarantees, platform observations and assumptions. Do not adopt Q-G2-2.
3. **Scientific validation (I-18 §3 C).** Review the known answers, the separately coded potential and its gradient, energy and h_z conservation, long integrations, RK4 convergence, the invariant-drift gate and its decision boundary, the secular node/perigee comparison, the critical inclination and polar-orbit invariance. Decide whether the tests could pass with an incorrect J2 implementation (write such implementations). Classify the reported dt⁵ invariant-drift behaviour as a defect, an unexplained observation or a documentation limitation; do not invent an explanation. If you can demonstrate a mechanism with evidence, state it as such.
4. **DR-0025 derivative-method substitution (I-18 §3 D).** Answer the five questions of I-18 §3 D individually, with evidence. Do not accept the substitution or amend DR-0025; state whether, in your view, a decision-record amendment is required.
5. **Architecture and regression isolation (I-18 §3 E).** Verify protocol conformance, no new dependencies on mass/context/orientation/state, additive and unwired code (search for consumers), that `git diff 60648b9..97b69ef -- src proof toolbox scenarios .github uv.lock pyproject.toml` shows only the two additive `src` changes, and that T2–T5, scenario v3 and the M3 Proof are absent. Run pytest (at least the new files and a regression subset; the full suite if feasible), ruff, the M1/M2 validators with output into `review_scratch/`, and the T0 checks.
6. **Test quality and mutation resistance (I-18 §3 F).** Inspect all new tests and the 14 mutants; re-run `t1_mutation_check.py`; write your own mutants (including plausible wrong implementations: sign or factor errors, wrong axis, P₂ vs other forms, unnormalized C20 used as J2, μ/a swaps, errors that only appear off-axis or at mid latitudes, errors below the test tolerances). Identify correlated oracles (an oracle that shares code, constants or formulas with the implementation), insufficient assertions, missing boundary tests and untested behaviour. Check that the no-J2-literal test cannot be trivially defeated and that the constants test does not merely restate the implementation.
7. **Records.** Check every number quoted in VAL-0020, the SCI-0013 update, the T1 report and the experiment README against the code, the result files and your own computation; check that gates and informational measurements are not mixed, that no tolerance was tuned to observed output (I-17 §8), and that the historical records touched by T1 were changed append-only (`git diff 60648b9..97b69ef -- docs`).
8. **Unresolved assumptions.** Assess each of the T1 report §9 items (secular-rate tolerance; operation counts; IEEE 754 correct rounding; dual-number substitution; axis representation; dt⁵ drift; no external comparison; Q-G2-2) and any further assumption you identify.
9. **Environment.** Record the precise environment (OS, CPU, Python and library versions) and the limitations of all numerical evidence.

## Required output
1. **Ledger:** your environment; every command you ran with its key output; every result file you inspected; and, for each conclusion, whether it rests on your own execution or computation, or only on documentation.
2. **Assessment by area:** A–F of I-18 §3, each with your evidence.
3. **Derivative-method substitution:** the five I-18 §3 D questions, answered individually.
4. **Unresolved assumptions:** one assessment per item in review item 8.
5. **Findings register.** Number them `M3T1-R1-F1`, `M3T1-R1-F2`, …. Each gives:
   - a severity (BLOCKER, MAJOR, MINOR or NOTE, as defined in I-18 §4);
   - exact file and line references;
   - a reproduction or independently checkable reasoning;
   - the consequence;
   - a recommended correction;
   - the relevant decision or validation requirement;
   - whether it is a defect, a proposed enhancement or an unresolved decision;
   - **VERIFIED** or **NOT INDEPENDENTLY REPRODUCED**.

   Do not report a finding without concrete evidence.
6. **Adversarial attempts:** what you tried in order to break the implementation or its tests, and the outcome of each.
7. **Verification limits:** what you could not check.
8. **T1 acceptance-readiness assessment.**
9. **Final verdict:** exactly one line, either `VERDICT: PASS (unconditional)` or `VERDICT: REQUEST_CHANGES`. Any BLOCKER, MAJOR or MINOR finding requires REQUEST_CHANGES. NOTEs alone permit PASS.
10. Write the complete review, identical to your final message, to `review_scratch/M3-T1-codex-review01.md`, and save your own scripts and logs under `review_scratch/`, with a command ledger in `review_scratch/COMMANDS.md`.
