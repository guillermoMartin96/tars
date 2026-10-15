You are an independent code reviewer (separate provider from the implementer) re-verifying TARS Milestone 2 task T4 ("scenario timeline, runner event emission, duration stop") after your previous review returned FAIL. Snapshot: current directory (commit 5098f8a). You review; you do not fix. Do not modify src/ or tests/; scratch only under ./review_scratch/.

Your previous findings: docs/reviews/raw/M2-T4-codex.md (F1 High: final PropulsionSampled could predate a submission after a failed step; F2: Python payloads not exact standard JSON, runner JSON copy changed semantics; F3: CLI output pair not published atomically; F4: duration scenarios could not round-trip serialization / with_dt; F5: tick-ratio overflow crashed). Implementer dispositions: docs/reviews/M2-T4-review-01.md (all ACCEPTED). Fix diff: ./T4-fixes.diff (1d58e15..5098f8a); full T4 diff: ./T4.diff (7f373cb..5098f8a). Your earlier probes are in docs/reviews/raw/M2-T4-codex-scratch/.

Authority and requirements are unchanged from your first review (docs/reviews/raw/M2-T4-codex-prompt.md): deterministic ordering and reproducible JSONL; command/burn/event correlation; commanded vs executed; accepted/rejected/completed/interrupted burns per the approved contract; duration stop boundaries including burns crossing the stop; M1 golden hash 7a4e1877... (exact on the reference host in proof/references/m1_final_state.json, bounds elsewhere), M1 Proof, existing event behavior; no duplicate events on retries/repeats; no partially committed state on failure; no new event types, rejection codes or permission semantics without a DR; DR-0017 Δv bound not conflated with trajectory error; no scope expansion.

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`; `.venv/bin/ruff check . && .venv/bin/ruff format --check .`; `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py`; `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`; `PYTHONPATH=src .venv/bin/python toolbox/scripts/run_mission.py --scenario scenarios/m2_prograde_burn.json --out review_scratch/slice`.

Tasks: (1) for each of F1-F5, re-run your original probe (or an equivalent) and state RESOLVED / NOT RESOLVED with evidence; check that each new test would fail against the old behavior. (2) Review the fixes for regressions or new defects (in particular: the new per-tick order — submissions before samples, no submissions at a tick that ends the run — versus the contract text, M1 byte identity, and the timeout path; the commit-marker publication protocol and its documented guarantee; the exact-JSON payload copy; StopConditionV2 serialization and hashing of the orbits-stop default). (3) Any remaining issue against the T4 requirements.

Output (final message, Markdown): per original finding "F<n>: RESOLVED|NOT RESOLVED — evidence"; then any new substantive finding as
### N<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
then Summary with verdict (PASS / CONDITIONAL PASS / FAIL). Label pure style remarks "Note" without severity.
