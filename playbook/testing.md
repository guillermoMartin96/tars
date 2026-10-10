# Testing and Validation

## Required testing layers
Meaningful simulation capabilities should be tested at the appropriate combination of:
1. Unit tests
2. Integration tests
3. Physics validation
4. Mission-level simulation

Passing unit tests alone is not sufficient evidence that physics is correct.

## Reproducibility
Every stochastic mission/failure configuration must be driven by an explicit seed. Logs and mission artifacts must record it. A failed mission must be replayable from the same seed and relevant configuration.

## Deterministic tests first
Use deterministic tests/validators for objective claims. Do not ask an LLM to judge something a program can prove reliably.

Examples include orbital invariants within tolerance, event schema validity, permission enforcement, seed replay, resource limits, and expected mission termination conditions.

## Tolerances
Scientific tolerances must be explicit, justified, and versioned with the relevant assumption/decision when material. Do not create arbitrary tolerances solely to make tests pass.

## Early vs mature completion
Prototype milestones may tolerate documented TODOs or limitations if the applicable Proof explicitly allows them and they do not invalidate the milestone's purpose. Known limitations must not be hidden.

As the project matures, Proof should tighten toward no unexplained warnings, complete documentation, clean interfaces, resolved high-severity review findings, and release-quality validation.

## Floating-point tolerance lessons (from M1)
- **Ideally-zero quantities need magnitude-relative bounds.** Examples are r·v on a circular orbit, or a zero component of a vector. Their round-off noise scales with the operands (ε·|r||v|), so an absolute bound that passes on one CPU can fail on another. Compare against the operand magnitude, or compare whole vectors relative to their norm.
- **Verify generated inputs for external tools by parsing them.** Do not compare them with strings built by the same formatting code. Example: NumPy 2's `repr` emits `np.float64(...)`, which GMAT cannot read.
- **Cross-platform runs differ in the last bits.** Same-platform replay must be byte-identical; cross-platform agreement is checked with a measured bound (DR-0006).

## Test-strength lessons (from M2 T1 review)
- **An independent reference must not share the code under test.** A DOP853 reference that called the production pointing law could not detect a wrong pointing law (REV-T1-05). Write the reference right-hand side from the equations, not from production helpers.
- **`pytest.approx(x, rel=r)` also allows an absolute error of 1e-12 by default.** For small quantities that floor dominates and silently weakens the check. Pass `abs=0` whenever a relative bound is intended.
- **Prove boundary rules on both sides.** Test the exact boundary, one ulp inside, and one ulp outside, for several values. A single "exact" case can pass only because its rounding falls the favourable way (REV-T1-03).
- **Run the full lint before committing documentation too.** ruff formats Python code blocks inside Markdown.
