VERDICT: REQUEST_CHANGES

## Summary

Reviewed pinned HEAD `2cd1e6ec1bc2df13827c36d03fda5bf4b4150c09` against `a57de3f0fb1a8265f5a493a836ad6305b0396d8c`, using the owner's I-26 text supplied in the request as authority. One MAJOR recording conflict remains: the implementer leaves the approved outcome identifier `reentry` open for later confirmation. One MINOR statement incorrectly describes RM-3b as measured.

The quoted owner-decision blocks are faithful. The numerical operation sequences, Q-GATE amendment, provisional P6 handling and conditional floating-point policy otherwise reconcile correctly. All 20 changed files are under `docs/`; tracked files remain untouched by this review. No implementation, correction, investigation or authorization was performed.

## Findings

| ID | Severity | Location | Finding | Evidence and result | Proposed disposition/correction |
|---|---|---|---|---|---|
| M3T2OD-R1-F1 | MAJOR | `docs/decisions/requests/DR-0029-m3-t0-proposals.md:292`; `docs/decisions/requests/DR-0027-m3-atmosphere-validity-boundary-and-table-residuals.md:146`; `docs/decisions/requests/DR-0026-m3-force-scenario-event-architecture.md` I-26 note, outcome-name row; `docs/milestones/M3-open-issues-register.md:55` (OI-23) | The surrounding reconciliation narrows P3 by leaving the outcome identifier `reentry` open for T3 confirmation. The owner explicitly lists `reentry` in the DECIDED precedence. Deferring implementation to T3 does not defer that choice. The old “names remain proposals” row cannot override the later explicit decision. | I-26 §2 P3: precedence is `non_finite`, `reentry`, `impact`, `escape`; “This decision specifies future T3 behavior; do not implement it under I-26.” `sed -n '287,293p' docs/decisions/requests/DR-0029-m3-t0-proposals.md` shows the added claim that the identifier needs confirmation; OI-23 labels it “Open.” This conflicts with the verbatim block immediately above and the DECIDED A-6 row. | Record the outcome name as decided by I-26; append the corresponding supersession of the historical outcome-name proposal and reconcile/close OI-23. Other field names and schema/serialization details can remain T3 design. Do not implement or correct under this review; follow the I-26 REQUEST_CHANGES stop rule. |
| M3T2OD-R1-F2 | MINOR | `docs/decisions/requests/DR-0029-m3-t0-proposals.md:526` | “RM-3b is a measured candidate only” incorrectly implies measurement already exists. | The same file's RM-3b table row says “Not run”; its verbatim I-26 block at line 521 says “a candidate to be measured during T4.” The reviewed decision packet P7 items 2 and 11 also say not run/not measured. | In an authorized correction, append clarification that RM-3b is an unmeasured candidate to be measured during T4, remaining non-gating without subsequent approval. |

## Assessment of requested items 1–10

1. **Fidelity — fails on F1; minor factual issue F2.** Compared P1–P9 quoted decision blocks, Q-GATE, DQ-1–DQ-6 and the DR-0025 quoted §5 policy with I-26. No omitted or altered operative sentence found in those quotes. Surrounding text must also conform, and OI-23 does not. V2's C_d = 2.2 is supported by DR-0029's existing summary and P9 “M2 vehicle” evidence, incorporated by I-26; it is not an independent new choice. V2 for RM-7 and V1 for the remaining drag missions is consistent with the incorporated vehicle definitions. OI-27 follows the existing P8 Domain and reviewed U-20 restrictions: totality does not require accepting evolute-region points or the origin. OI-28 preserves the distinction between immutable runtime component ownership and future scenario schema/serialization; it does not authorize a schema. B-4's DECIDED label correctly records the now-defined behavior, while implementation and B-1/B-5 obligations remain separate.

2. **P6 — passes.** Checked its quote, method requirements, P6-U1–U8, DR-0025/0028 notes, matrices, briefing, register and both new packets. Method (d) is only PROVISIONALLY SELECTED; the geodetic-drag discrepancy remains escalated. U1–U3 preserve unexplained residuals; U4 the open scope ruling; U5 its J2-method dependency; U6 unexecuted/unauthorized X-1; U7 the unauthorized independent geodetic gate; U8 the still-proposed identity sub-rule. No new requirement or numerical PASS is inferred. The ruling packet offers R-a/R-b/R-c and a labeled implementer recommendation; it decides none.

3. **Dependent-record consistency — fails on F1.** Compared all I-26 additions in DR-0024–0029, ADR-0009, the two matrices, register, strategy, packets and index. Status distinctions are otherwise maintained, with historical labels explicitly superseded rather than silently rewritten. F2 also contradicts the retained mission evidence.

4. **Q-GATE — passes.** DR-0029 Resolution quotes the replacement rule faithfully. Its provenance and the amended dependency matrix explicitly supersede only the I-15 T2 clause. P10's T1 clause remains unchanged. P6's scientific blockers survive for T5; P7 obligations survive for T3/T4. Scientific, review, numerical and acceptance gates are not waived.

5. **Algorithms and arithmetic — passes.** Inspected `t0_model.py:38–42`, `:87–93`, `:96–118`, `:144–162` against packet r1 §5. Constants F = 1/INV_F and e2 = F(2−F), initial `atan2`, left-associated products, 60-iteration cap, old/new latitude convergence test with assignment before exit, and pole-safe height agree. The density path retains metres/1000, the first-next-base band rule and `rho0 * exp(-(h-base)/scale)` grouping. For finite h_m ≥ 0, including −0.0, the formula arithmetic is identical; the intended change is the metres-first lower guard. Non-finite inputs still reject. Geodesy domain rejection and return of latitude/normal are separately disclosed additions, not concealed T0 arithmetic changes. Local bitwise comparisons corroborate inspection, without proving library assumptions.

6. **Conditional rows — passes.** Audited strategy §3 rows and B-1–B-15 against packet §6.2 and strategy §6. Covered U-13; U-17/X-G1; U-18 with δ_f; U-19(a),(c); PM-4(a); PM-5; PM-6; and U-23's third clause. X-G1's status is explicitly corrected in strategy §6.2. B-14 transition positions stay reported; its behavior part remains unconditional. U-23 reclassification is correct: E4b's c0 cap uses A-FP-2, explicitly documented in `t0_termination.py:649–656,727–730`. B-1/B-2 are conditional on their stated arithmetic structure and normal/finite domains, not A-FP-2/A-LM-1/A-LM-2. B-13 directly checks its finite set of special-value premises. Exact behavior rows retain their own explicit premises. No new tolerance or promoted unproved bound found. Exact z-reflection and strict decrease remain report-only regardless. J-FP2/J-LM1/J-LM2 demand relevant implementation guarantees/proofs rather than samples; none is represented as met. Explicit owner promotion is a future permission condition, not a current approval. Future deliverable derivations must still disclose and justify any newly introduced assumptions.

7. **Preserved contracts — passes within documentation scope.** Diff excludes all T0/T1 experiment artifacts and production/proof files. P10, the T1 J2 class/constants/gates, M1/M2 regressions and protected references remain binding. No proof suite was rerun, as instructed.

8. **No execution approval — passes.** Packet r1 is DRAFT — NOT AUTHORIZED, requires separate authorization, identifies the unmerged base-branch choice as unmet, and excludes T3/T4/T5 and P6/X-1 work. No new text grants implementation permission. Remote/CI/no-remote-branch claims are not authenticated by this review.

9. **Documentation-only/append-only — passes.** Independently compared the requested parent-to-head diff: 20 documentation files; four new files; 18 replaced pre-existing lines retain their original text with status or table-cell appends. No substantive deletion/rewrite found. No prior readiness review, correction/raw review, T0/T1 evidence or protected-path change appears in this diff. The local tracked tree is clean. The historical I-23–I-25 baseline verification was not repeated.

10. **New factual/arithmetic/citation errors — F2; otherwise checked claims pass.** Recomputed V1/V2 B values, the two quoted κ=0.01 thresholds, the 1000 km jump, F/e2 and signed-zero/negative-subnormal behavior. Source line citations resolve to the specified T0 code. The packaging log's SHA-256 matches SHA256SUMS; its quoted pyproject hash matches the repository. The log documents only a scratch probe with explicit limits and real-file re-verification required; the build itself was not independently repeated.

## Own computations and documentation checks

Reproduction command (no network):

```sh
.venv/bin/python -I review_scratch/check_review.py
```

The script disables bytecode writes before importing T0 modules read-only. Full stdout is `review_scratch/check_review.out`. Its expected git-show diagnostics for the four newly added files are captured separately in `check_review.stderr`; they are handled as new files, not failed comparisons.

```text
changed_files 20 docs_only True
protected_or_prior_evidence_changes []
preexisting_lines_with_appends 18 nonappend_violations []
probe_sha256 e23c9e3948222a3074bd481ccb075139c83132500352d24a2791829c40c6c5a2
pyproject_sha256 9b53279ca1dc690b18162923cee17b017d3560d871e9e6670b3c0ca07ac96fbf
B_V1 25.757575757575758
B_V2_initial 39.39393939393939
B_V2_final 39.018787878787876
V1_threshold_m 92282.0718994342
B100_threshold_m 84596.11573594392
F_hex 0x1.b775a84f3e128p-9
e2_hex 0x1.b6b90f1fe94f0p-8
density_conformance_samples 89 bitwise_equal True
negative_zero: T0 and packet density = 0x1.399999999999ap+0
-5e-324: T0 accepts; packet raises
-2.47e-321: T0 accepts; packet raises
-2.475e-321: both raise
geodetic_conformance_samples 1003 bitwise_equal True
1000km_relative_jump -1.598149571502283e-05
E4b_c0_max 0.6125000000000005
tracked_status ''
```

The V1 threshold uses its actual B = 850/33, not literal 25.8. T0's `B25.8` result label is rounded; the new 92,282.07 m claim is correct. The two thresholds each have one sign change on the T0 10 m grid; residuals at the computed roots are approximately 0.01 as recorded in the full output.

Commands and results:

- `git diff --stat a57de3f..2cd1e6e`: 20 files, 950 insertions, 18 deletions (the latter are line-appending replacements).
- `git diff --check a57de3f..2cd1e6e`: flags only Markdown trailing-space hard breaks on 12 added/replaced metadata lines. These follow the retained document convention; no substantive finding assigned.
- `git -c core.whitespace=-blank-at-eol diff --check a57de3f..2cd1e6e`: exit 0, empty output, saved in `review_scratch/diff-check.out`.
- `git status --porcelain --untracked-files=no`: empty. No tracked file modified.

## Limitations and disposition

No network, remote authentication, CI authentication, GMAT execution, cross-platform run or packaging-build reproduction. Baseline preconditions explicitly excluded by the request were not repeated. The sample comparisons are corroboration of source inspection, not independent proof of A-FP-2, A-LM-1 or A-LM-2. This is a documentation review, not T2 implementation acceptance or a rerun of accepted T0/T1/M1/M2 validation. No dedicated documentation-check script was identified; applicable diff, source-reference, append-only, digest and consistency checks are recorded above.

No reviewed file was authored or changed by this reviewer. Review artifacts reside only in `review_scratch/`. Under I-26 §7, reproduce/record the findings and STOP; an unapproved correction loop or T2 implementation must not begin.
