# M3 T1 Independent Review 01 — stopped at preconditions

**Review execution is incomplete. No scientific or code-review verdict has been established.** I-18 §1 requires verification of green final CI before beginning the independent review. This offline snapshot cannot establish that precondition. I stopped; the requested substantive review, tests and adversarial experiments were not performed. The verdict below means the acceptance prerequisites remain unsatisfied, not that a production defect was demonstrated.

## Snapshot and evidence

Independently executed local git checks established:

- HEAD: `97b69ef92e589ebd1b71016f49c4c9816d8c724b`, detached as specified by the snapshot instructions.
- Local `origin/milestone-3-t1-j2-force-model`: the same full SHA. This is a local tracking ref, not verification of the live remote.
- Local `main` and `origin/main`: `60648b93385a9954194730006aeac29ea14875ad`; ancestry check succeeded.
- Working tree: clean tracked files initially and at the final check; `git diff --stat` empty. No tracked files were modified. Review artifacts are under excluded `review_scratch/`.
- T1 commits: `5fd24a2366ba116eac2b5de824da1a76b1f888cf`, `e23675c5e0147b43ef74db3292004b343574032d`, `81a0d5671089e29b6b0cb50bdb376193c67b5eff`, `97b69ef92e589ebd1b71016f49c4c9816d8c724b`. No reviewer commit was created or pushed.
- The scoped diff over `src proof toolbox scenarios .github uv.lock pyproject.toml` contains only additive changes to `src/tars/sim/constants.py` and `src/tars/sim/forces.py`. The other listed paths have no diff against the baseline. This verifies snapshot isolation for those paths, not runtime regression behavior.

CI status: **NOT INDEPENDENTLY VERIFIED**. The user explicitly states that CI cannot be verified here. I-18 §1 names run `39865621`; the implementation claim names `39865621259`. Neither identity nor green status was independently established. This discrepancy is an unresolved prerequisite, not evidence that CI failed. No network request was attempted.

## Environment and ledger

Host observations: Darwin 25.2.0, macOS 26.2, x86_64; Python 3.12.15 built with Clang 22.1.3. CPU brand/model lookup was denied by the sandbox, so the precise CPU is unknown. Installed packages: NumPy 2.5.3, SciPy 1.18.1, pytest 9.1.1, ruff 0.16.10, pydantic 2.13.5, pydantic_core 2.46.5, Pygments 2.21.0, annotated-types 0.8.0, iniconfig 2.3.0, packaging 26.3, pluggy 1.6.0, tars 0.1.0, typing-inspection 0.4.4, typing_extensions 4.16.0.

The command ledger is `review_scratch/COMMANDS.md`. No committed experiment result file was inspected or regenerated. No numerical evidence was produced. Local snapshot conclusions above rest on my execution; CI statements are explicitly unverified claims from the supplied instructions.

## Assessment by I-18 §3 area

- **A — Physical correctness:** not assessed; no independent potential/acceleration derivation or boundary checks completed.
- **B — Numerical correctness:** not assessed; no rounding proof, operation recount, exactness proof or counterexample search completed.
- **C — Scientific validation:** not assessed; no integrations, convergence checks or secular comparisons executed. No classification of the observed drift order is established.
- **D — Derivative substitution:** not assessed; see the five questions below.
- **E — Architecture/regression:** only the scoped snapshot diff and baseline ancestry were verified. Protocol consumers, regression execution and full scope compliance remain unreviewed.
- **F — Test quality/mutation resistance:** not assessed; no tests or mutants executed.

## Derivative-method substitution

1. Same mathematical derivative: undetermined.
2. Independence from production acceleration: undetermined.
3. Additional numerical assumptions: undetermined.
4. Intended validation strength: undetermined.
5. Need for a decision-record amendment: undetermined; no amendment or acceptance is made.

## Unresolved assumptions

Each remains unassessed: secular-rate tolerance; operation counts; IEEE 754 correct rounding as implemented by the platform; dual-number substitution; axis representation; observed dt⁵ drift; absence of external comparison; Q-G2-2. No decision boundary was resolved. The additional unresolved review prerequisite is authenticated final-CI evidence and reconciliation of its run identifier.

## Findings register and adversarial attempts

No findings are registered. No code defect was independently reproduced, and no severity is assigned to an unverified claim. No adversarial implementation, numerical sweep or mutation attempt was performed. This empty register does not imply successful review.

## Verification limits and acceptance readiness

The required records, equations, tests, result numbers and append-only historical edits have not undergone the requested independent assessment. pytest, ruff, validators, T0 checks and T1 experiments were not run. Live origin, CI, cross-platform behavior and GMAT were not verified. No acceptance recommendation can be made. Resume this review only after the owner supplies a way to satisfy or explicitly waives the offline CI verification prerequisite and clarifies the CI run identity.

VERDICT: REQUEST_CHANGES

**T1 STATUS: IMPLEMENTED — REVIEW INCOMPLETE — NOT ACCEPTED — NOT MERGED.**
