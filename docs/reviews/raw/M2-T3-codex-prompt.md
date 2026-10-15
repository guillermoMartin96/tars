You are an independent code reviewer (separate provider from the implementer) for TARS Milestone 2 task T3, "command and event schema". Snapshot: current directory (commit d413edd). You review; you do not fix. Do not modify src/ or tests/; scratch only under ./review_scratch/.

Diff: ./T3.diff (72b3f0d..d413edd): src/tars/sim/commands.py (BurnCommand, CommandReceipt), Simulator.submit() and burn/command IDs in src/tars/sim/simulator.py, propulsion.py additions (DUPLICATE_COMMAND_ID, correlation fields), src/tars/events/schema.py (7 new event types), src/tars/sim/burn_events.py (converters), tests/test_commands.py, docs/contracts/m2-commands-and-events.md, ADR-0007 "Implementation notes (T3)".
Authority: DR-0014 (approved; rejection vocabulary amended 2026-10-10: schema_invalid kept, burn_unschedulable added, no invalid_input), DR-0017, ADR-0007, docs/milestones/M2-propulsion.md, playbook/architecture.md (simulator owns reality; machine-readable; deterministic; provider-independent; crew permissions separated — no new AI permissions), playbook/testing.md.
Tech Lead's T3 requirements: versioned, machine-readable schemas; exact adherence to approved rejection codes; stable command and event correlation IDs; separate commanded intent from executed outcomes; immutable, deterministic event records; backward compatibility with approved T2 interfaces (schedule_burn, propulsion_snapshot, engine_transitions, plan_burn, M1 behavior and golden event hash 7a4e1877...); no new AI permissions or unrelated architectural changes. Emission timing/runner wiring is T4 (out of scope).

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`; `.venv/bin/ruff check . && .venv/bin/ruff format --check .`; `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py` (expect 7a4e1877...); `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`.

Review with evidence (commands, probes, in-memory mutations, file:line) for: each requirement above; schema strictness and edge cases (JSON vs Python input, huge/odd values, unicode/control characters in IDs or issuer, payload types); receipt and event immutability (including nested/aliasing, e.g. receipts holding mutable objects); correctness and completeness of intent-vs-outcome fields (e.g. are any 'executed' fields actually derived from the plan, or 'commanded' from execution?); correlation stability and uniqueness; rejection precedence and atomicity (no state change on rejection, including the seen-ID registry and burn counter); determinism; JSONL round-trip/discriminated-union parsing including M1 events; whether the M1 golden hash and T2 interfaces are preserved; test strength (would plausible wrong implementations pass?); documentation accuracy.

Output (final message, Markdown) per substantive finding:
### F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
then Summary with verdict (PASS / CONDITIONAL PASS / FAIL) and what you verified. Label pure style remarks "Note" without severity.
