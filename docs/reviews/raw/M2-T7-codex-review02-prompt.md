You are an independent reviewer (separate provider from the implementer) reviewing TARS Milestone 2 task T7, "three-platform measurement and threshold decision preparation", round 2. Snapshot: current directory (commit 8fe709f). You review; you do not fix. Do not modify src/, tests/, toolbox/, scenarios/ or proof/; scratch only under ./review_scratch/.

Context:
- T6 is complete (unconditional PASS at e7c0148). T7 is authorized as a measurement, analysis and decision-preparation task. It is NOT authorization to change acceptance criteria. No threshold, reference value, snapshot tolerance or check may be changed in T7.
- The specification: DR-0015 (threshold method: re-measure on the implemented code across three platforms, like DR-0008, then a threshold DR), DR-0008 (the M1 precedent and its platform matrix: macOS x86_64 reference host, Linux x86_64 CI, macOS arm64 CI), FU-1 in docs/milestones/M2-propulsion.md section 12a, DR-0021 and DR-0022.
- Deliverables to review:
  - toolbox/scripts/m2_t7_measure.py (collect and analyze);
  - .github/workflows/m2-t7-measure.yml;
  - proof/records/evidence/M2-T7/ (11 bundles plus analysis.json);
  - VAL-0016 in docs/science/validation.md;
  - docs/decisions/requests/DR-0023-m2-final-thresholds.md (the proposed final matrix, FU-1, O6, the M2 cross-platform final-state gate);
  - the T7 sections of proof/records/M2-propulsion.md and docs/milestones/M2-propulsion.md.
- Complete bundles, including the record-mode files record.json.gz, are in ./t7-bundles/<label>/. The T7 diff is ./T7.diff (d0eaa6c..8fe709f); the fix diff is ./T7-fix2.diff (843ba09..8fe709f).
- Your round-1 review (./previous-review.md) returned REQUEST_CHANGES with T7-F1 to T7-F6. Dispositions are in docs/reviews/M2-T7-review-01.md: all accepted and corrected, with no proposed value changed. The analyzer now also reports Euclidean reference drift, and a flattened-shape bug found while adding it is fixed.

Tasks:
0. Verify that T7-F1 to T7-F6 are resolved: re-check each corrected figure and statement against the evidence, and check the analyzer change (vector norms, restored shapes) for correctness.
1. **Measurement validity.**
   - Does the collector measure what VAL-0016 and DR-0023 claim, on the platforms claimed, with the stated provenance (clean tree, revision, identical input digests, environment, commands, output digests)?
   - Is any required measurement missing, or reported as done when it is not? That includes position, velocity, mass, timing, burn boundaries, node crossings, O1–O9 margins, cross-platform drift, determinism, and reference variation kept separate from simulator integration error.
   - Is the platform coverage the DR-0008 matrix, with no unapproved substitution?
2. **Analysis correctness.**
   - Recompute independently from the bundles: the per-threshold worst cases, the cross-platform spreads, the margins, the final-state drift, the verify-mode and record-mode reference variation, and the O6 SMA variation and margin bounds.
   - Report any figure in VAL-0016 or DR-0023 that does not match the evidence, or that the analyzer computes wrongly (for example wrong grouping of thresholds, missing checks, or a spread computed across non-comparable checks).
3. **Error attribution.** Is measurement uncertainty correctly distinguished from simulator error? Are the FU-1 finding (zero spread on O9 reference metrics because of the snapshot) and the O6 analysis sound? Are any claims overstated?
4. **The threshold proposals.** For every proposed value, check that it is supported by the evidence and that the stated rationale and consequences are accurate. Flag any proposal that would conceal a simulator defect, that is optimized merely to make tests pass, or that changes an approved contract without saying so.
5. **Scope and preservation.**
   - Confirm that no threshold, reference value, snapshot tolerance, check or acceptance semantics changed.
   - Confirm that m2.json is unchanged and provisional, and that M1 and T1–T6 behaviour is preserved.
   - Confirm that no T8 work was started.

Run:
- `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider`
- `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m2_proof.py --out review_scratch/m2.json`
- `PYTHONPATH=src .venv/bin/python toolbox/validators/m1_proof.py --out review_scratch/m1.json`
- `PYTHONPATH=src .venv/bin/python toolbox/scripts/gmat_m2.py compare`
- `PYTHONPATH=src .venv/bin/python toolbox/scripts/m2_t7_measure.py analyze --out review_scratch/analysis ./t7-bundles/*`, then compare the result with proof/records/evidence/M2-T7/analysis.json.

Output (final message, Markdown), one block per substantive finding:
### T7-F<n> — <title> (number new findings from T7-F7)
**Severity:** Critical | High | Medium | Low
**Claim:** ...
**Evidence:** ...
**Suggested fix:** ...
A finding is blocking only if it has a concrete effect on a measurement result, a reported figure, a proposed threshold or its justification, or the decision the Tech Lead is asked to make. Then a Summary with a verdict, exactly one of PASS (unconditional), REQUEST_CHANGES or FAIL, and what you verified. Label pure style remarks "Note" without severity.
