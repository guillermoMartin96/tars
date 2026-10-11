You are an independent code reviewer (separate provider from the implementer) re-verifying TARS Milestone 2 task T5 ("validators O1-O8, m2_proof.py, provisional m2.json, reference missions"). Snapshot: current directory (commit f5f3866). You review; you do not fix. Do not modify src/, tests/, toolbox/, scenarios/ or proof/; scratch only under ./review_scratch/.

Your previous review (./previous-review.md, at a3b65f6) returned FAIL with F1-F4, all false passes. The implementer's dispositions are in docs/reviews/M2-T5-review-01.md.
- Fix diff: ./T5-fix.diff (a3b65f6..f5f3866).
- Full T5 diff: ./T5.diff (54cce8d..f5f3866).

Tasks:
1. Verify each of F1-F4 is resolved. Re-run your probes from previous-review.md: rotated initial state, 3000 s stop substituted, doubled powered sample, bogus SimulationCompleted at an active stop, deleted depletion events. Confirm the new tests fail when each fix is reverted.
2. **Sweep the whole false-pass class in this round, not only these four.** Systematically consider every simulator output the validators consume:
   - every event type and field;
   - RunResult fields: receipts, unsubmitted_command_ids, final, final_propulsion, samples, crossing_times;
   - the CLI summary, if relevant.
   For each, ask: is it checked against an independent expectation or an exact cross-consistency rule? Could a plausible wrong simulator or tampered log change it and still pass every check?
   Also consider:
   - oracles judged against the wrong time or wrong reference;
   - limits so loose they gate nothing;
   - checks that silently skip on empty input (e.g. missions with no burns, missing events);
   - threshold scoping and the unused-entry guard.
   Demonstrate each new issue with an executable mutation. Report everything you find in one round.
3. Check that the review record, VAL-0013 and m2.json limit_basis are accurate.
4. Confirm the T5 requirements still hold:
   - provisional thresholds, not weakened to pass;
   - M1 gates preserved;
   - the DR-0017 bound separate from trajectory error;
   - FU-1 preserved;
   - no T6-T8 scope.

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
Number new findings from F5. Then a Summary with a verdict (PASS / CONDITIONAL PASS / FAIL), F1-F4 status, and what you verified. Label pure style remarks "Note" without severity.
