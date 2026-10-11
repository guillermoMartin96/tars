You are an independent code reviewer (separate provider from the implementer) performing the final re-verification of TARS Milestone 2 task T4 ("scenario timeline, runner event emission, duration stop"). Snapshot: current directory (commit b820588). You review; you do not fix. Do not modify src/ or tests/; scratch only under ./review_scratch/.

History: review FAIL (F1-F5) -> re-verification 1 CONDITIONAL PASS (N1) -> re-verification 2 CONDITIONAL PASS: N1 resolved, M1 Low open (finite altitude 1e103 m overflowed r^3 in gravity on a duration-stop run). Records: docs/reviews/raw/M2-T4-codex*.md and docs/reviews/M2-T4-review-01.md. Fix diff: ./T4-M1.diff (354914d..b820588); full T4 diff: ./T4.diff (7f373cb..b820588). Your probe: docs/reviews/raw/M2-T4-codex-reverify2-scratch/duration_large_radius.json.

Requirements unchanged (docs/reviews/raw/M2-T4-codex-prompt.md), including M1 golden hash 7a4e1877... (exact on the reference host) and M1 Proof.

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`; `.venv/bin/ruff check . && .venv/bin/ruff format --check .`; `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py`; `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`; `PYTHONPATH=src .venv/bin/python toolbox/scripts/run_mission.py --scenario scenarios/m2_prograde_burn.json --out review_scratch/slice`.

Tasks: (1) M1 finding: re-run your probe; RESOLVED / NOT RESOLVED with evidence; would the new tests fail against 354914d? (2) To close this class of issue in one round, sweep ALL scenario-derived arithmetic at validation and at the start of a run (initial state, period, tick counts, sampling, spacecraft masses and engine rates, timeline times) for any remaining finite, schema-valid input that crashes with an uncaught exception (OverflowError, ZeroDivisionError, ValueError, etc.) instead of being rejected as invalid input or ending as a recorded mission failure. Report all you find together, with severity. Distinguish crashes from extreme-but-well-defined behavior (for example a very long run), which is not a defect. (3) Any remaining Critical/High/Medium issue against the T4 requirements across the full T4 diff.

Output (final message, Markdown): "M1: RESOLVED|NOT RESOLVED — evidence"; any new substantive finding as
### K<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
then Summary with verdict (PASS / CONDITIONAL PASS / FAIL). Label pure style remarks "Note" without severity.
