## Resolution status of tracked findings

| ID | RESOLVED / NOT RESOLVED | Evidence |
|---|---|---|
| M3P12-F1 | **RESOLVED** | Reproduced false detection at `5b12eec` for both components. Corrected probe reports 600 intended / 2,400 missing and rejects the setup. Independently traced all 3,000 scheduled inputs. |
| M3P12-F2 | **RESOLVED** | Reproduced the historical E6 counterexample before and after correction. The first-order assertion now rejects it; removing that assertion is detected. Grid failures remain zero. |
| M3P11-F1 | **RESOLVED** | Reassociated fallback, wrong-component, rounding-only and partial-exercise controls reproduce historical failures and are rejected now. |
| M3P11-F2 | **RESOLVED** | All five disputed assertions have genuinely exercised, exception-free targeted protection. Remaining redundancy arguments cover matching inputs. |
| M3P10-F1 | **RESOLVED** | Historical exception controls reproduce and pass now. Expected-exception allowances remain restricted by mutation, type, message and stack. |
| M3P10-F2 | **RESOLVED** | Actual inventory reconciles: 19 identities mapped to 18 historical survivors; **12 A / 4 B / 3 C / 0 D**. |
| M3P-F1–F5 | **RESOLVED** | Atmosphere discontinuities, drag phase advance, approximate decay oracle, domain-policy wording and rotation-rate correction remain recorded. Independently recomputed all 27 density jumps. |
| M3P2-F1–F3 | **RESOLVED** | Explicit owner decisions and current authorization limits remain intact. Complete instruction history supplied; lowest-band ratio independently reproduced. F2’s historical rejected-with-reasoning disposition is preserved. |
| M3P3-F1/F2 | **RESOLVED** | General velocity derivative and identity specialization retained; complete withdrawn **558-byte** Q4 row remains verbatim. |
| M3P4-F1/F2 | **RESOLVED** | Inclination bound, distinct node measures and solar hour-angle cancellation remain correct. Preserved numerical example reproduced. |
| M3P5-F1 | **RESOLVED** | Independent passive-rotation derivation confirms both corrected signed formulas. |
| M3P6-F1–F3 | **RESOLVED** | Domain, crossing and endpoint distinctions retained; node-jump assertions and wrapping convention remain protected. |
| M3P7-F1 | **RESOLVED** | Finite-only wrapping contract and explicit nonfinite rejection retained. |
| M3P8-F1 | **RESOLVED** | Finite validation and four separate coverage minima retained; injection and assertion-removal mutations detected. |
| M3P9-F1–F3 | **RESOLVED** | Oracle infinities, component-specific order/sign removals and E3/E4 removals are protected. Intentional asymptotic step-selection limitation remains documented. |

No new findings.

## Summary

**PASS — unconditional.** No BLOCKER, MAJOR or MINOR finding remains.

Reviewed detached HEAD **`59c9f9ebccf489e76a8a916e273b4dc14f6868e5`**, parent `602ede0`, against correction baseline `142b9df` and accepted M1/M2 baseline `d92ab89`. Tracked worktree remained clean.

Full review and supporting evidence are saved in [review_scratch/M3-planning-codex-review13.md](/private/tmp/claude-501/-Users-guillermomartin--superset-worktrees-tars-quirky-shampoo-037cfd34/dfdf341f-9b4e-4ffe-869a-f148305222a6/scratchpad/i12/codex13/review_scratch/M3-planning-codex-review13.md).

Verified independently:

- **Verification repeatability and preservation:** two runs produced byte-identical output matching committed evidence. Against independently executed `5b12eec`, **zero pre-existing values changed or disappeared**; the new mutant adds 23 leaf values. Order coverage remains **506/532**, sign coverage **560/504**, each enforced separately. The 1% inclination-oracle error still produces one E3 and one E4 failure.
- **Mutation suite:** **109 attempted, 109 validly exercised, 109 detected for the intended reason**. Every other mutation classification is zero. **30/30 controls** meet their declared category, exercise result and reason. Baseline meets **0/77** direct defect predicates; **22/22** oracle schedules are fully observed.
- **Regression demonstration:** all five M3P10-F1 controls fail against `896d52d`, all four M3P11-F1 controls against `c16b3b5`, and all five M3P12-F1 controls against `5b12eec`. All 30 controls pass against the corrected harness.
- **Classification and sweep:** **36 assertion sites, 29 detected removals, seven survivors, zero exceptions**. All five validator outputs reproduce committed evidence byte-for-byte.

My independent reproduction of review 12’s oracle counterexample produced, for **each component**:

```text
5b12eec: expected rejection; intended 600, missing 0
current: invalid mutation setup; intended 600, missing 2400
```

A separate oracle trace recorded **3,000 calls, 3,000 unique inputs**, exactly matching the independently constructed schedule.

Additional variants failed closed:

- Injection after the formula call: **3,000 missing** defects.
- Extra steps: **600 unscheduled** observations.
- Changed arguments or calls through another frame: **3,000 unscheduled** observations.
- Renamed oracle-value local: rejected with `KeyError`.
- Unexpected corruption of the other component: **600 unintended** values.
- Runtime exception: process failure.

Reversing step order preserved complete observation and remained valid. The declared mutations do not inspect their callers; the documented exclusion of deliberately probe-aware programs does not conceal a defect in this fixed mutation inventory.

For E6, my source-level reconstruction confirmed:

```text
Before correction, assertion present: defect rejected
Before correction, assertion removed: exit 0
Current, assertion present: first-order E6 message alone; zero grid failures
Current, assertion removed: removal detected by the new built-in mutant
```

I independently removed all **12 category-A assertions** using AST locations. Every targeted defect was exercised without exception, rejected with its assertion present, and escaped the exact/wrapping checks without it. Failure counts with/without were:

```text
W2 2/0; W5 6/0; N1 4/0; E1 1/0;
E2b 168/0; E2c 144/0; E2d 48/0; E2e 24/0;
E5b-nonfinite 2/0; E5b-defined 2/0; E5d 1/0;
E6-sign-first-order 1/0.
```

The four B classifications hold within their documented pure-function scope: W1 shares W2’s actual result; W4’s endpoint inputs occur in W2; both E6 oracle assertions share E3’s complete arguments. E3’s tolerance is tighter than E6-value’s remaining margin. Additional endpoint and E6-only defects still trigger those independent checks after removal of the B assertion. W3, W6 and E2a have appropriate diagnostic rationales.

Other independent checks:

- AST comparisons confirm unchanged oracle, formulas, wrapping, grid, first-order checks, tolerances and minima.
- **10,000** conjugated-Cartesian rotation cases agree with the oracle within **`2.22e-15` rad**, with no inclination-bound excess. Reproduced **ΔΩ = +0.259805543688°** and the crossing **Δi≈+1°, ΔΩ=180°**.
- **9,994 finite random binary64 inputs** match independent rational wrapping.
- Sensitivity and atmosphere-residual reruns reproduce committed outputs. All **27 density jumps** recompute within **`1.11e-16`**; lowest-band ratio is **`1.0013804525694443`**.
- All **81 whole-branch changed files** are under `docs/`; the correction contains the stated **15 documentation files**. Protected implementation, tests, toolbox, scenario and Proof paths are unchanged.
- All five supplied pinned hashes match and are baseline-identical. Registers retain every baseline line: assumptions **218 additions/0 deletions**, validation **43/0**.
- Prior review records/raw outputs retain their historical bytes. I-1 through I-11 are byte-identical in the new prompt. Amendments 1–9 retain correction pointers. Scoped Ruff lint/format and relative-link checks pass.

Commands executed included the five `dr0028_node_signed_*` validators and these preservation checks, using the supplied environment and `PYTHONPATH=src`:

```text
toolbox/validators/m1_proof.py --out review_scratch/m1.json
toolbox/validators/m2_proof.py --out review_scratch/m2.json
toolbox/scripts/gmat_m1.py compare
toolbox/scripts/gmat_m2.py compare
toolbox/scripts/reference_snapshot.py verify-baseline \
  toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz
toolbox/validators/cross_platform.py
toolbox/validators/m2_cross_platform.py collect \
  --out review_scratch/m2-platform.json
toolbox/validators/determinism.py
toolbox/validators/determinism.py --scenario <each of four M2 scenarios>
python -m pytest -q -p no:cacheprovider \
  tests/test_constants.py tests/test_elements.py
```

All completed successfully: **M1 standalone validator 7/7**, **full M2 standalone validator 228/228 without `--quick`**, both committed-reference GMAT comparisons, snapshot verification, local cross-platform checks, five determinism runs and **13 pytest tests**.

**Validation limits:** these are complete standalone validator executions, not complete Proof-wrapper executions. Complete Proof wrappers and full pytest were not rerun by this reviewer; no running test was interrupted. Fresh GMAT executable runs, external-source retrieval and three-platform execution were not performed. GitHub API access failed for run `39084190524`, so its reported individual CI conclusions remain independently unverified.

Remaining gates are unchanged:

- **T0:** explicit planning acceptance, separate merge/T0 authorization and successful planning merge.
- **T1:** T0 evidence and independent review, applicable checkpoint decisions and separate authorization.
- **T2:** additionally, owner decisions on DR-0027 **A-4/A-5/A-6/A-s/B-4** and applicable T0 deferrals.
- **Q-G2-1/5/7 and Q9 values:** deferred to the T0 checkpoint; **Q-G2-6:** deferred to T4. Numerical thresholds require a later measured-evidence DR. **Q-G3-7 remains NOT AUTHORIZED.**

**The planning package is ready to be presented to the Tech Lead for planning acceptance as documentation evidence.**

Nothing was merged or fixed, and no M3 implementation or T0/T1/T2 work began. Final acceptance remains the Tech Lead’s decision.
