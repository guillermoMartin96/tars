# AI Spacecraft Proof System v1

Proof defines what "finished" means. The agent may not declare a feature or milestone complete until every applicable required check is satisfied or the result is explicitly `BLOCKED`.

## Result states
- **PASS** — all required Proof checks pass; no unresolved blocking findings.
- **FAIL** — one or more required checks fail.
- **BLOCKED** — completion depends on an unresolved Tech Lead decision, authoritative scientific investigation, or other explicitly documented blocker.

## Proof principles
1. Prefer executable/deterministic proof over LLM judgment.
2. Unit tests alone do not prove simulation correctness.
3. Scientific discrepancies must be understood/documented rather than hidden.
4. Stochastic behavior must be seed-reproducible.
5. High-severity unresolved external-review findings block Proof.
6. Hard architectural invariants are Proof requirements, not suggestions.
7. Early milestones may use a prototype definition of done, but allowed limitations must be explicit.

## Standard feature/milestone gate
Apply what is relevant:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Physics validation passes or discrepancies are explicitly accepted by the Tech Lead
- [ ] Mission-level simulation passes
- [ ] Seed/replay checks pass for stochastic behavior
- [ ] Architecture invariants pass
- [ ] Machine-readable events validate
- [ ] Relevant scientific assumptions are recorded
- [ ] Relevant engineering decisions are recorded
- [ ] Required external review completed
- [ ] Every substantive review finding dispositioned
- [ ] No unresolved Critical/High findings
- [ ] No secrets/debug artifacts/accidental generated files
- [ ] Branch is pushed and identifies the revision being proven

## Evidence record
Each milestone should produce or link to a concise Proof record containing:
- revision/commit SHA;
- commands/checks executed;
- machine-readable validator outputs where available;
- mission seed/configuration where applicable;
- reference-system configuration/version where applicable;
- discrepancies and their disposition;
- external-review record;
- final PASS/FAIL/BLOCKED result.

See the specialized Proof files for architecture, physics, mission, review, and definition-of-done requirements.
