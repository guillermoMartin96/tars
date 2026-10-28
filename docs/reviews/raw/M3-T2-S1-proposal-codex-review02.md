VERDICT: REQUEST_CHANGES

| ID | Severity | Location | Finding | Evidence/reproduction |
|---|---|---|---|---|
| R-02 | MAJOR | Prototype `simulator.py:466`; proposal §3.3 | Added coast propellant scalar conversion changes finite-dt behavior for ndarray subclasses supplied by custom integrators. | Standard NumPy `MaskedArray`: BASE commits without warnings; prototype emits `UserWarning`. With warnings treated as errors, prototype fails before commit. See `masked_probe.py`, `warnings_error.py` and saved outputs. |
| R-03 | MINOR | Proposal §2, §6.4; mutation script M-14 | Stale references remain: `prototype.patch`, omitted T-07(k), and an explicit M-14 node naming (d) before running both complete files. | Actual M-14 failures correctly come from (k), NaN/+inf parameters. |

**R-01 closure: CLOSED.**

1. **Powered safety:** Independent stage writers, custom integrators, views and aliased arrays found no invalid mass reaching powered context construction. The validated local float survives subsequent stage mutations.
2. **Ordering:** Confirmed finiteness → F/m → direction → thrust acceleration → context → force, matching BASE apart from context construction.
3. **M-14:** Independently built mutant. T-07(k) fails for NaN/+inf because `ValueError` replaces `FloatingPointError`; −inf passes and pins nothing.
4. **Finite-dt overflow:** BASE/prototype agree at `1e308`, `8.98846567431158e307`, and `1.2e308`. Coast option A changes the exception. Runner classifies the preserved exception as `non_finite`.
5. **Exceptions/state:** Independent probes matched exception chains, warnings, call timing, state and retries, except the separate subclass counterexample R-02.
6. **Infinite dt:** No burn admitted; T-07(a)/(b) retain BASE behavior.
7. **Context semantics:** Repeated deferred reads validate without repair/cache; supported masses become owned floats; absent mass is `None`.
8. **M-19:** Equivalence independently confirmed for unchanged production code; own probes match and all 78 S1 tests pass.
9. **Tests/mutations:** Prototype 78 pass. BASE: 27 regression passes, 51 expected per-node `AttributeError` failures, no collection errors. Twenty mutants killed; M-19 survives.
10. **Scope:** AST checks pass; permitted paths only. Five scenario output pairs are byte-identical; 115 propulsion tests pass. Broader copied-suite collection stopped on missing scratch threshold files.
11. **Editorial:** R-03 records stale references; §3.3 also needs correction for R-02’s demonstrated assumption.

Full evidence and reproduction instructions: [REVIEW.md](review_scratch/reviewer/REVIEW.md). Package hashes verified; tracked files remain unchanged.