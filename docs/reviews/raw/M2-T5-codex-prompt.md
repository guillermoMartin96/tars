You are an independent code reviewer (separate provider from the implementer) for TARS Milestone 2 task T5, "validators O1-O8, m2_proof.py, provisional m2.json, reference missions". Snapshot: current directory (commit a3b65f6). You review; you do not fix. Do not modify src/, tests/, toolbox/, scenarios/ or proof/; scratch only under ./review_scratch/.

Diff: ./T5.diff (54cce8d..a3b65f6):
- src/tars/validation/m2.py (oracles O1-O8 and contract checks);
- src/tars/validation/m2_missions.py (missions and hand-declared receipts);
- src/tars/validation/thresholds.py (scoped M2 threshold loader);
- toolbox/validators/m2_proof.py;
- proof/thresholds/m2.json (PROVISIONAL);
- scenarios/m2_retrograde_burn.json, m2_burn_to_depletion.json, m2_invalid_commands.json;
- tests/test_m2_validation.py;
- the CI workflow;
- docs: VAL-0013 in docs/science/validation.md; DR-0018, now approved option A; the contract note on same-tick reporting.

Authority:
- DR-0015 (oracles O1-O9; threshold method; conditional approval: no tolerance final before T7);
- DR-0014 and its amendment (rejection codes, precedence, ID consumption);
- DR-0017 (timing Δv budget; depletion residual D1a);
- DR-0018 (approved A: a stop is an observation boundary; no fabricated BurnEnded; the final PropulsionSampled preserves the active-burn state);
- the contract docs/contracts/m2-commands-and-events.md;
- docs/milestones/M2-propulsion.md (§8 test plan, §10 P1-P12);
- VAL-0008/0010/0011/0012;
- playbook/testing.md.

Tech Lead's T5 requirements (verify each):
1. Validators independently calculate expected physical quantities wherever practical. No circular validation that merely repeats simulator outputs.
2. Successful operations and applicable failure paths are exercised: depletion, rejected commands, overlapping burns, observation ending during an active burn.
3. Event ordering, command-to-burn traceability, conservation/accounting invariants and deterministic replay are verified.
4. The known same-tick submission/ignition reporting behavior is explicitly tested and documented; approved T3 semantics are unchanged.
5. Numerical thresholds stay provisional until T7. Measured values, methodology, units and evidence are recorded. Thresholds are not weakened or finalized merely to make tests pass.
6. All M1 regression gates, platform-specific golden-hash expectations and GMAT reference checks are preserved.
7. The DR-0017 timing-induced Δv bound is kept separate from trajectory-error measurements.
8. FU-1 (T7 GMAT recalibration; 11-15 um DOP853 cross-platform floor) is preserved.
9. No scope expansion into T6-T8 (GMAT M2 reference, threshold DR, final Proof).

Focus areas:
- validator correctness;
- numerical assumptions;
- missing edge cases;
- **potential false passes**: would a plausible wrong simulator, or a wrong log, still pass each check? Prove it with in-memory mutations or monkeypatches.
- Are the hand-declared receipts and predictions truly independent of the simulator?
- Are tolerance bases sound and consistent with DR-0015? Are any limits so loose that they gate nothing?
- O4 DOP853 settings and segment handling; O5 arc boundaries; O6 method (midpoint, impulsive reference); O8 dt choice.
- DR-0018 boundary checks and the control-run check.
- Event-order/cadence rules versus the contract text.
- Threshold loader scope and unused-entry guard.
- Test strength; CI wiring; documentation accuracy (VAL-0013 numbers versus a fresh run).

Run:
- `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`
- `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/determinism.py`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/cross_platform.py`
- `PYTHONPATH=src .venv/bin/python toolbox/scripts/gmat_m1.py compare`

Output (final message, Markdown), one block per substantive finding:
### F<n> — <title>
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
Then a Summary with a verdict (PASS / CONDITIONAL PASS / FAIL) and what you verified. Label pure style remarks "Note" without severity.
