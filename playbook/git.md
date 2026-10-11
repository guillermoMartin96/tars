# Git and Review Workflow

## Branching
Agents work on dedicated feature/milestone branches and push those branches frequently. Direct pushes to `main` are not the normal workflow.

## Commits
Commit frequently at coherent engineering checkpoints. Avoid both giant milestone-sized commits and meaningless micro-commits.

Temporary intermediate commits may fail tests while work is actively being assembled. Before a feature/milestone is presented for review or declared complete, the branch must return to the applicable Proof-valid state.

Commit messages should communicate intent. Conventional-style prefixes such as `feat`, `fix`, `test`, `docs`, `refactor`, and `chore` are preferred when useful.

## Before review checkpoint
- applicable automated tests/checks pass;
- working tree has been reviewed;
- no secrets or credentials are present;
- no accidental debug/generated artifacts are tracked;
- decisions/assumptions affected by the work are recorded;
- applicable Proof has been run.

## External LLM review
Completed features and milestones may be reviewed by Claude, ChatGPT, or other capable models. Review is evidence, not authority.

Use `toolbox/templates/review-findings.md`. Every substantive finding must be explicitly classified by the implementing agent as:
- `ACCEPTED`
- `REJECTED_WITH_REASONING`
- `ESCALATED_FOR_INVESTIGATION`

High-severity unresolved findings prevent the relevant Proof from passing.

## Engineering decision log
Important decisions belong in `docs/decisions/` using the engineering-decision template. Record context, options, decision, reasoning, consequences, and reconsideration triggers.

## Confirm CI after pushing (lesson from M2)
- Check the CI result of each pushed commit before stacking further work on it, not only at review checkpoints.
- In M2, twelve commits were pushed while a test that passed locally failed on both CI platforms: the DOP853 reference differs across CPUs at the µm level. That also meant CI skipped the M1 determinism and GMAT steps for those commits.
- Local results are evidence for one platform only.
