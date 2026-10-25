VERDICT: REQUEST_CHANGES

## Summary

One **MAJOR** recording conflict remains: the reconciliation leaves `reentry` open for T3 confirmation, although I-26 explicitly names it in the approved outcome precedence. One **MINOR** statement incorrectly describes RM-3b as already measured.

The numerical specifications, Q-GATE amendment, provisional P6 status and conditional floating-point classifications otherwise check out.

Full review and reproduction evidence: [Review-01.md](review_scratch/Review-01.md).

## Findings

| ID | Severity | Location | Finding | Evidence and result | Proposed disposition/correction |
|---|---|---|---|---|---|
| M3T2OD-R1-F1 | MAJOR | DR-0029:292; DR-0027:146; DR-0026 I-26 outcome-name row; open-issues register OI-23 | The reconciliation leaves the approved outcome identifier `reentry` open for T3 confirmation. This narrows P3. | I-26 explicitly decides precedence `non_finite` → `reentry` → `impact` → `escape`. DR-0029 nevertheless says the historical outcome-name proposal was “not explicitly superseded”; OI-23 labels the identifier “Open.” Deferring implementation to T3 does not defer the owner’s choice. | Append a reconciliation recording `reentry` as decided and superseding the historical outcome-name proposal. Reconcile OI-23. Other field names and schema details may remain T3 design. No correction performed. |
| M3T2OD-R1-F2 | MINOR | DR-0029:526 | “RM-3b is a measured candidate only” incorrectly implies completed measurement. | The retained RM-3b row says “Not run.” The owner’s quoted decision says “a candidate to be measured during T4.” The reviewed decision packet also says not measured. | Clarify, in an authorized correction, that RM-3b remains an unmeasured candidate for T4, without a mandatory gate. |

## Assessment of items 1–10

1. **Decision fidelity — fails on F1.** The P1–P9, Q-GATE, DQ-1–DQ-6 and floating-point policy quotations faithfully reproduce the operative owner text. The surrounding `reentry` qualification does not. V2’s C_d = 2.2 follows the incorporated DR-0029 summary and P9 evidence. V2 for RM-7 and V1 for other drag missions is consistent with those vehicle definitions. OI-27 follows P8’s existing domain restrictions; OI-28 distinguishes runtime component ownership from future scenario serialization. B-4 correctly records decided behavior while preserving implementation and other table obligations.

2. **P6 — passes.** Method (d) remains PROVISIONALLY SELECTED; geodetic drag remains escalated. P6-U1–U8 preserve the unexplained residuals, scope ruling, method dependency, unauthorized investigation/gate and proposed identity sub-rule. The separate ruling packet presents options and a labeled recommendation without deciding them.

3. **Dependent records — fails on F1.** Compared the I-26 additions across DR-0024–0029, ADR-0009, matrices, register, strategy, packets and index. Status distinctions otherwise agree. F2 also contradicts retained mission evidence.

4. **Q-GATE — passes.** Supersession explicitly affects only the I-15 T2 clause. P10’s T1 clause and all scientific, review, numerical and acceptance gates remain binding. P6 blockers survive for T5; P7 obligations survive for T3/T4.

5. **Algorithms/arithmetic — passes.** Inspected packet §5 against the cited T0 source: derived F/e2, starting latitude, iteration cap, convergence test using old/new latitude, assignment before exit, pole-safe height, kilometre grouping and band selection agree. For finite h_m ≥ 0, including −0.0, the density arithmetic matches T0. The metres-first lower guard supplies the intended correction. Geodesy domain rejection and latitude/normal output are separately disclosed additions.

6. **Conditional-row register — passes.** Audited strategy §3 and B-1–B-15. Covered U-13, U-17/X-G1, U-18, U-19(a)/(c), PM-4(a), PM-5, PM-6 and U-23’s third clause. E4b explicitly depends on A-FP-2, so U-23’s reclassification is correct. B-14 transition positions remain reported. B-1/B-2 retain their arithmetic/domain premises; B-13 directly checks its finite special-value premises. Exact z-reflection and strict decrease remain report-only regardless. No invented tolerance or promoted unproved bound found. J-FP2/J-LM1/J-LM2 require relevant guarantees or proofs, and none is represented as met.

7. **Preserved contracts — passes within documentation scope.** T0/T1 artifacts, P10, J2 implementation/constants, M1/M2 references and protected paths are unchanged. Existing validation contracts remain binding.

8. **No execution approval — passes.** Packet r1 is DRAFT — NOT AUTHORIZED, requires separate authorization and honestly identifies the unmerged base choice as unmet. T2–T5 and P6/X-1 execution remain unauthorized.

9. **Documentation-only/append-only — passes.** All 20 changed files are under `docs/`. Four are new. The 18 replaced historical lines retain their text with status or table-cell appends. No substantive deletion, protected-path change or prior review/evidence rewrite appears in this diff. Tracked tree remains clean.

10. **New factual/arithmetic/citation errors — F2; other checked claims pass.** Recomputed vehicle B values, thresholds, F/e2, the 1000 km jump and signed-zero/subnormal behavior. T0 line citations resolve correctly. Packaging-log and `pyproject.toml` digests match; the build itself was not repeated.

## Own computations

Command:

```sh
.venv/bin/python -I review_scratch/check_review.py
```

Selected output:

```text
changed_files 20 docs_only True
preexisting_lines_with_appends 18 nonappend_violations []
B_V1 25.757575757575758
B_V2_initial 39.39393939393939
B_V2_final 39.018787878787876
V1_threshold_m 92282.0718994342
B100_threshold_m 84596.11573594392
F_hex 0x1.b775a84f3e128p-9
e2_hex 0x1.b6b90f1fe94f0p-8
density_conformance_samples 89 bitwise_equal True
geodetic_conformance_samples 1003 bitwise_equal True
1000km_relative_jump -1.598149571502283e-05
E4b_c0_max 0.6125000000000005
tracked_status ''
```

Additional results:

- −0.0 produces identical T0/packet density bits.
- At −5e-324 and −2.47e-321 m, T0 accepts; the specified guard raises.
- At −2.475e-321 m, both raise.
- Packaging-log SHA-256 matches `SHA256SUMS`.
- Plain `git diff --check` flags only Markdown hard-break trailing spaces; disabling that whitespace category yields exit 0.
- Final tracked status is empty.

The quoted V1 threshold correctly uses B = 850/33; T0’s “B25.8” label is rounded.

## Limitations

No network, remote/CI authentication, GMAT execution, cross-platform validation or packaging-build reproduction. Excluded baseline checks and M1/M2 proof scripts were not rerun. Sample agreement corroborates source inspection; it does not prove the floating-point assumptions.

No tracked files were modified. Review artifacts are confined to `review_scratch/`. Per I-26 §7, record/reproduce these findings and **STOP without an unapproved correction loop or implementation**.