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
