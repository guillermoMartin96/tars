You are an independent code reviewer (separate provider from the implementer) for the TARS spacecraft simulator. Repository snapshot: current directory (commit ee091df, branch milestone-2-propulsion). You review; you do not fix. Do not modify src/ or tests/; scratch work only under ./review_scratch/.

Scope: Milestone 2 task T2 "propulsion inside the simulator". Diff: ./T2.diff (f8e62c4..ee091df): src/tars/sim/simulator.py, src/tars/sim/propulsion.py (EngineState, PropulsionSnapshot, EngineTransition, new rejection codes), tests/test_simulator_propulsion.py, tests/test_simulator.py (public-API allowlist extended), docs (ADR-0007 "Implementation notes (T2)", VAL-0012, docs/science/experiments/m2-t2/).
Authority: DR-0013 (approved 1A+2A+3A+4A+5), DR-0014 (approved; rejection vocabulary amended 2026-10-10: schema_invalid kept, burn_unschedulable added), ADR-0007, SCI-0008..0012, playbook/architecture.md (simulator owns reality; machine-readable; deterministic), playbook/testing.md, proof/architecture.md. T2 scope: augmented state, engine state machine, exact RK4 step splitting at engine events, PropulsionSnapshot, M1 byte-identity. Out of scope: command schema/events (T3), scenario/runner (T4), GMAT (T6). Earlier T1 review for context: docs/reviews/M2-T1-review-01.md.

Run tests: `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_simulator_propulsion.py tests/test_simulator.py tests/test_propulsion.py` (full suite: drop paths, ~20 s). Lint: `.venv/bin/ruff check . && .venv/bin/ruff format --check .`. M1 regression: `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py` (expected sha256 7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4) and `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`.

Review with evidence (commands, experiments, in-memory mutations, file:line) for:
1. Physics/numerics: correctness of the augmented RHS (thrust F/m with current mass, mass flow, sensed dv), exact step splitting (event times inside ticks, on boundaries, several per tick, back-to-back, depletion), propellant floor semantics, time representation (t = tick*dt; sub-step h), determinism, M1 bit-identity (with and without a spacecraft).
2. Architecture: can any public path change r, v, mass or propellant except step()? Is schedule_burn's validation complete and are rejection codes from the approved vocabulary? Read-only views/aliasing of EngineTransition, PropulsionSnapshot, state arrays. Hidden mutable state.
3. Scheduling semantics: submission-order rule, engine_busy vs overlaps_scheduled_burn, propellant committed accounting, interactions with the current time (ignition == now, ignition inside the current tick, scheduling mid-burn), NaN/inf/str/bool/numpy inputs.
4. Test strength: can each test fail when the behavior is wrong? Try mutations (including ones the implementer did not list in the commit message). Are references independent of the code under test? Are tolerances justified and not loosened by pytest.approx defaults?
5. Anything that alters M1 behavior or approved thresholds.

Output (final message, Markdown) per substantive finding:
### F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
then Summary with verdict (PASS / CONDITIONAL PASS / FAIL) and what you verified. Label pure style remarks "Note" without severity.
