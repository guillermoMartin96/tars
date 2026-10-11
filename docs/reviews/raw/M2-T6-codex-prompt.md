You are an independent code reviewer (separate provider from the implementer) for TARS Milestone 2 task T6, "GMAT M2 finite-burn reference and O9 validation". Snapshot: current directory (commit 805d789). You review; you do not fix. Do not modify src/, tests/, toolbox/, scenarios/ or proof/; scratch only under ./review_scratch/.

Diff: ./T6.diff (a0169e7..805d789):
- src/tars/validation/gmat_m2.py (generator, arc plan, row labelling, alignment verification, O9 metrics, provenance);
- toolbox/scripts/gmat_m2.py (generate/run/compare with the replacement guard);
- toolbox/references/gmat/m2/ (committed GMAT R2026a references for prograde, retrograde, invalid-command missions);
- toolbox/validators/m2_proof.py (O9 integration);
- proof/thresholds/m2.json (provisional o9_gmat group and basis);
- tests/test_gmat_m2.py;
- CI;
- the GMAT README M2 section;
- VAL-0014;
- one T5 test change (an unknown-group example renamed because o9_gmat now exists).

GMAT is NOT installed in this environment. Review against the committed artifacts. The GMAT reproduction test is skipped here.

Authority:
- DR-0015 (O9 definition; conditional approval, no final tolerance before T7);
- DR-0016 (approved A: aligned stepping, streaming rows, mandatory alignment verification; never align on GMAT epoch/ElapsedSecs);
- VAL-0009 (g0 trap; GMAT a = F/m; depletion exception);
- VAL-0010 (M-a epoch re-rounding, M-b microsecond stop rounding; DOP853 cross-platform floor 11-15 um);
- DR-0009 (references are evidence; replacement guard);
- FU-1 (no gate tighter than the 11-15 um floor without independent justification);
- DR-0017 (timing Δv bound separate from trajectory error);
- DR-0018 (stop is an observation boundary);
- the T5 validators and their final review (docs/reviews/M2-T5-review-01.md).

Tech Lead's T6 conditions (verify each):
1. T5 baseline preserved: 206 M2 checks (now 212 with O9), all T5 tests, M1 behavior, golden hashes, GMAT M1 comparison, approved thresholds. T5 validators not modified or loosened.
2. GMAT is used as an independent physics reference, never with simulator output as expected truth. Inputs come from scenario inputs only.
3. Position, velocity, burn timing, mass evolution and orbital events are compared where supported.
4. Reproducibility, provenance, units, reference configuration and raw outputs are preserved.
5. O9 detects meaningful physical and numerical regressions, shown by negative and mutation tests.
6. DR-0016 epoch rounding and aligned stepping are accounted for explicitly. No tolerance below the 11-15 um floor without justification.
7. DR-0017 is kept separate from trajectory error, and DR-0018 is preserved.
8. Discrepancies, convergence and uncertainty sources are documented.
9. Thresholds stay provisional; no T7 scope.

Focus areas:
- reference independence;
- generator correctness against GMAT semantics: ChemicalThruster/FiniteBurn, VNB direction, C/K coefficients, GravitationalAccel, mass decrement, the adjacent-burn thruster switch;
- arc planning and row labelling (could rows be mislabelled while the counts still match?);
- alignment verification strength;
- O9 metric definitions and limits: are any vacuous, or set below the noise floor?;
- provenance and replacement-guard holes;
- **potential false passes**: a wrong simulator, a wrong reference, a wrong generator or a tampered artifact that still passes. Demonstrate each with executable mutations.
- Also: depletion exclusion soundness; test strength; CI wiring; documentation accuracy (VAL-0014 numbers versus a fresh compare).

Report everything you find in one round, sweeping the false-pass class completely (as in the T5 re-verifications).

Run:
- `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`
- `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
- `PYTHONPATH=src .venv/bin/python toolbox/scripts/gmat_m2.py compare`
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
