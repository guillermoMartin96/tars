# M3 Planning Review 11 (independent)

**Scope:** the correction authorized by the Tech Lead's instruction "I-10 — Resolve M3P10-F1 and authorize Review 11" (I-10), in commits `8f3f22a` and `0972e1a`. That covers M3P10-F1 (exception classification in the mutation check, with its controls and the regression demonstration against `896d52d`) and the classification of the 18 assertions of M3P10-F2, with the six protections added. The review also covered the earlier findings, the DR-0028 mathematics, M1/M2 preservation, scope and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a14b41-1ba4-76c2-91f2-25da7bd4e82c`, run at **`c16b3b50fe2814e6b05423bfb2de31b5f4c7f097`** (the prompt commit; parent `0972e1a`) on a fresh git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review11-prompt.md`. It carries I-1 to I-10 verbatim, each checked against the earlier prompts and the instruction text. It requires the reviewer to reproduce M3P10-F1 independently, and does not ask the reviewer to approve the package.
- Raw output: `raw/M3-planning-codex-review11.md`.

**Instruction for this outcome (I-10 §9):** "If Review 11 returns REQUEST_CHANGES: Record every finding. Do not fix the new findings. Do not initiate Review 12. Do not prepare a planning acceptance report. Stop and return the findings for my authorization."
- **None of the findings below has been applied.**
- No review 12 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** two new MINOR findings, both verification defects. There is no BLOCKER or MAJOR finding, and no mathematical or documentation defect in the committed results.

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P10-F1 | **NOT RESOLVED** | The original caught-import counterexample is now rejected correctly, but a suppressed import failure followed by an algebraically equivalent fallback still counts as detection of an assertion removal that never happened (M3P11-F1) |
| M3P10-F2 | **NOT RESOLVED** | The six added protections work, but five category B assertions have counterexamples that meet category A's definition (M3P11-F2) |

### The reviewer also confirmed independently
- **Repeatability and committed results:**
  - verification script twice, byte-identical; coverage 506/532 and 560/504, each enforced separately;
  - mutation check twice, byte-identical: 109/109, and 13/13 controls in their declared category;
  - the regression demonstration: the five controls fail at `896d52d` and pass now; an independent reproduction of the original false detection;
  - classification 18/18 and sweep 35/23/12, matching the committed outputs.
- **Preservation:** against an independent run of `896d52d`, zero changed pre-existing values and 79 added keys. Mathematical definitions and checks are unchanged apart from E5d's parameter. The 1 % Δi oracle mutant still gives one E3 and one E4 failure.
- **Mathematics:** the signed formulas, the line-of-nodes regimes, endpoints, node reversal, closed form and inclination bound were rederived. 10 000 cases agree to 4.44e-16 (rotation) and 1.33e-15 (closed-form node). The review-04 value and the crossing example reproduce, and 10 000 finite angles match rational wrapping.
- **Research reruns:** the sensitivity and atmosphere-residual scripts are byte-identical, and all 27 density jumps were recomputed (at most 1.11e-16).
- **History and scope:**
  - all 75 whole-branch changed files are under `docs/`, and the protected paths are unchanged;
  - registers 218/0 and 43/0;
  - records and raw outputs 01–10 are intact, and I-1–I-9 are preserved verbatim.
- **Preservation gates:** standalone m1_proof 7/7; full m2_proof 228/228; both GMAT comparisons; snapshot verify-baseline; the local golden comparison; all five determinism runs; Ruff.
- **Partial or unavailable, as the reviewer reported:**
  - the reviewer's attempts at the complete Proof wrappers were interrupted during pytest, so they are not Proof passes; the M2 wrapper also inherited M1-generated evidence changes;
  - CI could not be checked (no GitHub API access);
  - external source bytes, GMAT executable runs and three-platform execution were not revalidated.

## Dispositions (recorded; not applied)

### M3P11-F1 (MINOR, verification defect): a rounding difference can stand in for the intended exercised defect
**Where:** `dr0028_node_signed_verification.py`, `instrumented()` and `exercised()`; `dr0028_node_signed_mutation_check.py`, the `not_rejected` predicate.

**Finding.** `defect_exercised` is true when any call's result differs bitwise from the reference implementation. It does not check that the named defect, in its intended component and domain, was exercised.
- **Counterexample:** the reviewer kept the order assertion intact and inserted, in `formula_scaled()` for factor 2, a suppressed import failure whose fallback returns the correct formulas, with ΔΩ computed as `delta * (sin(node - phi) / tan(inc))`.
  - That reassociation differs from the reference by rounding in 940 of 3000 calls, so both doubled-coefficient mutants are "exercised" while having no order or sign failure.
  - For the doubled-Δi mutant, even Δi is unchanged; the differences are in ΔΩ only.
- **Result:** the run is classified "expected rejection" for `order_assertion_disabled`. The full harness entrypoint with this mutation reports PASS, with all 13 controls passing.
- **Not affected:** the committed mathematical results are not invalidated; the defect is in the claimed reason-specific detection guarantee.

**Disposition: ACCEPTED.** The implementer reproduced it independently with the committed `run()` and `classify()`: the same construction was classified "expected rejection".
- **Cause:** amendment 7 closed the case of a mutant suppressed to the exact reference result (the `exception_suppressed_inside_mutant` control), but measured "exercised" as any bitwise inequality. A fallback that differs only by rounding, or only in another component, therefore passes as the intended defect.
- **Relation to M3P10-F1:** the original uncaught-import counterexample is fixed; this is the same class of false detection by another route, so M3P10-F1 is not fully resolved.

**Proposed change (not made):**
- Tie "exercised" to the named defect. For each built-in mutant, declare the component it corrupts and a minimum size of difference, or a predicate on the injected result. Examples: the doubled-Δi mutant must differ from the reference in Δi by at least a stated fraction of the first-order term; a NaN mutant must return NaN in its component.
- Add the reviewer's reassociated-fallback construction as a negative control.
- Consider pairing each assertion-removal mutation with an intact-assertion run of the same built-in mutant.

### M3P11-F2 (MINOR, verification defect): five "redundant" assertions protect failures their stated substitutes miss
**Where:** `dr0028_node_signed_assertion_classification.py`, category B entries W5, E1, E2e, E5b-nonfinite and E5b-defined; DR-0028 amendment 7, the classification table and the dependency statements.

**Finding.** Overlap shown for one defect does not establish redundancy across the property an assertion protects. For each of these five, the reviewer gives a defect that the intact script rejects only through that assertion, and that leaves no failure when only that assertion is removed:

| Assertion | Counterexample | Intact | Without the assertion |
|---|---|---|---|
| E1 | `tilt_fn` = Rz(0.01)·tilt_matrix: a proper rotation that keeps the endpoints equatorial | E1 deviation 1.0e-2 | no failure |
| E2e | identity rotation only at φ = 37°, δ = 2° (outside E1's sampled tilts) | E2 endpoint not equatorial | no failure |
| E5b-nonfinite | NaN node difference only at i = 0.1°, Ω = 0°, φ = 1° (359 valid samples remain; both crossings asserted) | 2 failures | no failure |
| E5b-defined | node undefined only at φ = 1° and 2° (non-crossing) | 358 defined samples, per tilt sign | no failure |
| W5 | wrap returns 1.01 for the input 1.0 only (not among W2's inputs) | 6 failures | no failure |

- The reviewer reproduced both E5b cases through the full entrypoint: exit 1 with the assertion present, exit 0 and PASS without it.
- The reviewer found the six A demonstrations sound, the W1/W4 and E6 redundancy adequate within its stated scope, and the three C rationales reasonable.

**Disposition: ACCEPTED.** The implementer reproduced the E5b-defined and W5 counterexamples independently. With the assertion intact, they give 2 and 6 failures; with only that assertion removed, 0 and 0.
- **Cause:** the category B evidence in amendment 7 demonstrated overlap for one chosen defect per assertion. It did not show that the independent check covers the whole property the assertion protects.
- **Effect:** amendment 7's totals (6 A, 9 B, 3 C) and its dependency statements for E1/E2e, E5b and W5 are not supported. By the reviewer's evidence, these five meet category A. That would make 11 A, 4 B and 3 C, subject to the Tech Lead's decision.

**Proposed change (not made):**
- Reclassify W5, E1, E2e, E5b-nonfinite and E5b-defined as category A, and add a narrowly targeted built-in mutant for each, using the reviewer's constructions as the starting point.
- Correct amendment 7's classification totals and dependency statements with an appended amendment.
- For the remaining B entries (W1, W4, E6-value, E6-sign), state the scope of the redundancy claim explicitly.

## Validation evidence at the reviewed commits (implementer)
- **`0972e1a`**, isolated clone:
  - M1 Proof overall PASS (9 steps, exit 0), full pytest 1185 passed, 0 failed, 0 skipped;
  - M2 Proof overall PASS (20 steps, exit 0), full pytest 1185 passed, with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism for four scenarios and m2_proof;
  - the evidence differs only in run metadata.
- **CI** for `0972e1a`: run 39056505376, workflow completed with conclusion success; each of the four jobs (check ubuntu-latest, macos-latest, macos-15-intel; m2-cross-platform) completed with conclusion success. The reviewer could not verify this independently.
- **Worktree:** each of the five experiment tools ran twice with byte-identical outputs.

## Status after this review
- This is not an unconditional PASS, so the I-10 §9 stop condition applies.
- **No acceptance report has been prepared, and no review 12 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** decisions on M3P11-F1 and M3P11-F2, and on any further review.
