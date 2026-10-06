# Development Workflow

## Compute before LLM
Use the cheapest reliable deterministic mechanism that preserves higher-priority engineering goals.

Preferred order:
1. Existing approved local Toolbox asset
2. Deterministic project code/Python
3. Approved open-source library/tool
4. Cached or previously computed result
5. Small targeted LLM call
6. Broad/large LLM reasoning call

Do not ask an LLM to repeatedly calculate, scan, summarize, validate, format, or transform information that reliable deterministic software can handle. LLMs should primarily reason, choose actions, explain, and handle ambiguity.

Open-source availability does not bypass dependency approval rules.

## Feature workflow
1. Read requirements and applicable Playbook/Proof sections.
2. Inspect existing code, decisions, assumptions, and Toolbox assets.
3. Identify unresolved decisions and issue requests early.
4. Define/confirm structured interfaces and events before implementation when they are part of public subsystem boundaries.
5. Implement the smallest coherent slice.
6. Add tests at the appropriate layers.
7. Run cheap deterministic checks frequently.
8. Commit and push coherent checkpoints.
9. Validate scientifically where applicable.
10. Run mission-level behavior where applicable.
11. Update decisions/assumptions/tooling/documentation caused by the work.
12. Run feature/milestone Proof.
13. Obtain and resolve required external review.

## Teaching requirement
Explain important concepts and implementation decisions to Guillermo while working. Explanations should focus on why the system behaves as it does, important tradeoffs, and what abstractions hide. Do not reimplement complex trusted functionality solely for educational purity; teach the underlying concept when using an abstraction.

## Reusability
When a script, validator, template, reference workflow, or deterministic operation becomes reusable and approved, place it in `toolbox/` and link/reference it from the appropriate Playbook or Proof rule.
