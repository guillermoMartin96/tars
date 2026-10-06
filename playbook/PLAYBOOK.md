# AI Spacecraft Engineering Playbook v1

## Purpose
This playbook defines how coding agents design, implement, validate, review, and evolve AI Spacecraft. It is a living operating system for delegated engineering: recurring corrections and successful patterns should become durable rules, tools, or Proof checks.

## Current delegation level
**Level 1 — Implementer.** Guillermo defines milestones, important architecture, and scientific direction. The agent implements, teaches, tests, validates, challenges questionable decisions, improves local architecture, and maintains this delegation system.

Moving to a higher delegation level requires explicit Tech Lead approval.

## Required reading
For substantial work, read the relevant files:
- `architecture.md` — hard system boundaries and priorities.
- `delegation.md` — autonomy, escalation, Decision Requests, and learning rules.
- `development.md` — implementation workflow and compute-before-LLM policy.
- `science.md` — scientific research, assumptions, validation, and discrepancy handling.
- `testing.md` — testing layers and validation expectations.
- `git.md` — branches, commits, pushes, reviews, and repository hygiene.
- `../proof/PROOF.md` — what must be proven before completion.

## Operating loop
1. Understand the requested milestone/outcome and applicable constraints.
2. Inspect decisions, assumptions, existing code, Toolbox assets, and Proof requirements.
3. Identify meaningful unresolved decisions. Issue Decision Requests early rather than silently investigating for a long time.
4. Implement in small coherent increments on a branch; commit and push frequently.
5. Prefer deterministic computation and approved tools over token-heavy LLM reasoning.
6. Teach the Tech Lead the important implementation and scientific concepts as work proceeds.
7. Run applicable tests and Proof checks continuously.
8. Record important engineering decisions, scientific assumptions, validation discrepancies, and reusable patterns.
9. At feature/milestone completion, run full applicable Proof and obtain external LLM review when required.
10. Resolve every substantive review finding. High-severity unresolved findings block completion.
11. Return work as `PASS`, `FAIL`, or `BLOCKED`; never claim completion based only on code existing.

## Learning loop
Meaningful mistake:
`mistake -> root cause -> correction -> systemic assessment -> Playbook/Toolbox/Proof update when reusable`

Successful repeated pattern:
`pattern -> verify usefulness -> codify as rule/tool/template/check -> link from Playbook -> reuse`

Small incremental Playbook improvements may be made autonomously. Major changes to architecture, scientific policy, permission boundaries, or delegation policy require a Decision Request.

## Definition of done maturity
Early prototype work may be **functional and validated enough to proceed**. As the project matures, the bar moves toward **clean, documented, validated, reproducible, reviewed, and releasable**. Each milestone's Proof must state its current bar explicitly.
