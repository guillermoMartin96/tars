You are an independent code reviewer (separate provider from the implementer) for TARS Milestone 2 task T4, "scenario timeline, runner event emission, duration stop". Snapshot: current directory (commit 1d58e15). You review; you do not fix. Do not modify src/ or tests/; scratch only under ./review_scratch/.

Diff: ./T4.diff (7f373cb..1d58e15): src/tars/sim/scenario.py (ScenarioV2, SpacecraftConfig, TimelineEntry, StopConditionV2, parse_scenario), src/tars/sim/runner.py (timeline submission, event emission, duration stop, _BurnEventEmitter), a one-line-guard fix in src/tars/sim/simulator.py (powered RHS raises FloatingPointError on a non-finite stage), toolbox/scripts/run_mission.py (atomic writes, v2 summary), scenarios/m2_prograde_burn.json (vertical slice), tests/test_scenario_v2.py, tests/test_mission_m2.py, tests/test_cli.py additions, docs/contracts/m2-commands-and-events.md (section "Scenario timeline and emission (T4)"), DR-0018 (open; burns in progress at the stop), ADR-0007 "Implementation notes (T4)", DR-0014 amendment recording the Tech Lead's confirmation of T3 semantics.
Authority: DR-0010 (#4 duration stop; reference slice), DR-0014 (§5 event contract; timeline submit_t_s; approved rejection codes and precedence), DR-0017, ADR-0007, the T3 contract, docs/milestones/M2-propulsion.md, playbook/architecture.md (simulator owns reality; commands only via submit(); machine-readable; deterministic; no LLM; crew permissions separated), playbook/testing.md.

Tech Lead's T4 requirements (verify each):
- deterministic event ordering and reproducible JSONL output;
- correct correlation between submitted commands, accepted burns and emitted events;
- commanded timing and duration distinguished from actual execution;
- correct event emission for accepted, rejected, completed and interrupted burns, as applicable to the approved contract;
- duration-based stopping at boundary conditions, including burns that cross the scenario stop time;
- preservation of the M1 golden hash 7a4e1877... (exact on the reference host recorded in proof/references/m1_final_state.json; other hosts within approved cross-platform bounds), M1 Proof thresholds and existing event behavior;
- no duplicate events during retries or repeated execution;
- no partially committed state when runner execution fails;
- no new public event types, rejection codes or permission semantics without a decision request.
- Also: the distinction between the DR-0017 timing-induced Δv bound and trajectory error must not be blurred; no scope expansion (thermal, autonomous planning).

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`; `.venv/bin/ruff check . && .venv/bin/ruff format --check .`; `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py`; `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`; `PYTHONPATH=src .venv/bin/python toolbox/scripts/run_mission.py --scenario scenarios/m2_prograde_burn.json --out review_scratch/slice`.

Review with evidence (commands, probes, in-memory mutations, file:line) for: each requirement above; scenario schema strictness and edge cases (tick-grid exactness, timeline order, version selection, JSON vs Python input, hash stability/ambiguity, payload passthrough of invalid commands); emission order and cadence versus the contract text (including envelope tick/t versus event_t_s at tick boundaries, ignition at the submission tick, several engine events in one tick, depletion); stop-time boundaries (cutoff/ignition exactly at the stop, burn across the stop, pending burns, orbits stop, failures before submissions); failure paths (non-finite steps, impact/escape, unexpected exceptions) and atomicity of the CLI outputs; whether a v1 scenario still takes the exact M1 path; whether DR-0018's current behavior stays within the approved contract; test strength (would plausible wrong implementations pass?); documentation accuracy.

Output (final message, Markdown) per substantive finding:
### F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
then Summary with verdict (PASS / CONDITIONAL PASS / FAIL) and what you verified. Label pure style remarks "Note" without severity.
