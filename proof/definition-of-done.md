# Definition of Done

## Prototype phase — current default
A feature may be complete when it is functional and validated enough to safely support the next learning/development step.

Allowed only when explicitly documented:
- non-blocking TODOs;
- known model simplifications;
- deferred cleanup that does not undermine correctness or the next milestone.

Not allowed:
- hidden scientific uncertainty;
- unexplained validation failures;
- violated hard architecture invariants;
- irreproducible stochastic failures;
- unresolved Critical/High review findings;
- claiming tests/checks were run when they were not.

## Mature/release phase — future target
The bar should evolve toward clean interfaces, complete documentation, resolved warnings, reproducible results, validated scientific behavior, comprehensive tests, reviewed decisions/assumptions, and releasable repository state.

A milestone may override the prototype default with a stricter explicit definition.
