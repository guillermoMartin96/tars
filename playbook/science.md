# Scientific Engineering Policy

## Never invent scientific behavior
When implementation depends on unfamiliar physics or engineering:
1. Stop the dependent implementation.
2. Research authoritative sources.
3. Explain the relevant concept to Guillermo.
4. Record sources and assumptions.
5. Identify simplifications and expected limitations/errors.
6. Implement only when the model is sufficiently justified.

## Validation hierarchy
Initially, treat GMAT as the primary source of truth for orbital validation because the project is still building expertise. It is not permanently assumed infallible. Add independent authoritative validation sources as the project matures and prefer converging evidence among multiple trusted sources.

Evidence priority generally favors:
1. authoritative scientific/engineering evidence;
2. trusted validation systems and reproducible reference calculations;
3. project tests and reproducible experiments;
4. independent LLM review;
5. an implementing LLM's unsupported opinion.

## Discrepancies are data
Do not silently tune results to match a reference. Meaningful discrepancies must be investigated and documented as one of:
- expected model simplification;
- numerical error/tolerance;
- implementation error;
- incorrect assumption/requirement;
- reference/configuration mismatch;
- unresolved.

Record relevant expected vs actual values, configuration, tolerances, conclusion, and whether the discrepancy is accepted. Prediction error should become a measurable project metric as fidelity grows.

## Requirement conflicts
If physics or validation suggests an existing requirement is questionable, investigate and bring the Tech Lead a recommendation. Do not silently rewrite the requirement or distort the model to satisfy it.

## Scientific assumptions registry
Use `docs/science/assumptions.md`. Significant assumptions must have stable IDs, rationale, sources, known limitations/error, validation approach, and revisit conditions.

## Reference data is evidence, not a fixture
Committed reference outputs (for example GMAT reports) must never be regenerated or replaced in response to a failing comparison. A failure is a discrepancy to classify. Replacing reference data requires explicit review with a recorded reason, and tooling should enforce this where practical (DR-0009; `gmat_m1.py run --replace-reason`).
