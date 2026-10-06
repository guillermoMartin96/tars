# Toolbox

The Toolbox is the project's approved reusable machinery. It exists to reduce repeated reasoning, improve reproducibility, and save LLM tokens without sacrificing correctness.

## Directories
- `scripts/` — repeatable project operations such as mission execution, replay, export, or comparison.
- `validators/` — deterministic checks used by Proof.
- `templates/` — standard Decision Request, decision, assumption, and review formats.
- `references/` — approved local reference material or instructions for external reference tools. Do not commit third-party material unless licensing permits it.

## Promotion rule
A useful one-off solution should be promoted into the Toolbox when it is reusable, reliable, and appropriate for future agents. Once promoted, link it from the Playbook and/or Proof so future agents know to use it.

## Approval
Toolbox contents are not automatically authoritative merely because they exist. New tools should be tested and reviewed proportionally to their impact. Validators used as Proof must themselves have appropriate tests or independently checkable behavior.
