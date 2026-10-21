# M3 T0 — acceptance dossier (for the Tech Lead's decision)

**Prepared under:** "Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09", §7 (Review 09 returned PASS): "Prepare a T0 acceptance dossier with complete evidence and outstanding limitations. Do not declare T0 accepted. Do not merge. Do not start T1/T2. Stop for my explicit acceptance decision." It also follows I-15 (review) for an unconditional PASS: "Preserve the complete review output. Verify the reviewed commit and evidence are unchanged. Prepare the T0 acceptance report. Stop for owner acceptance."

**Status: T0 is NOT accepted.** This dossier is a recommendation and an evidence index. It makes no decision. It does not merge, it does not start T1 or T2, and it does not decide DR-0029 P1–P10 or DR-0028 P6(b).

## Recommendation
- **T0 acceptance: READY** for the owner's decision. Independent Review 09 (Codex, at `f04f9955d5ae714cc61144990395b8225a379968`) returned `VERDICT: PASS (unconditional)`. Every tracked finding is RESOLVED: F1–F5, R2-F1…R2-F3, R3-F1, R4-F1, R5-F1, R5-F2, R6-F1…R6-F3, both Review 06 remarks, R7-F1, R7-F2, R8-F1, IM-1, IM-2 and the Review 08 M3 coverage observation. There are two new NOTEs (R9-F1, R9-F2), both ACCEPTED and reproduced. Neither changes a number, a floor or a certification. Under I-11 they are not corrected (see "Open NOTEs").
- **T1 (J2) readiness: BLOCKED until DR-0029 P10 is decided.** It is READY from the T0 standpoint once P10 is decided. T1 also needs its own authorization.
- **T2 (drag) readiness: BLOCKED** on DR-0029 P1–P10, and in particular P1–P5, P8 and P9. T4/T5 additionally need P6 and P7; the geodetic GMAT gates wait on the escalated investigation.

## Branch and commits
- **Branch:** `milestone-3-t0-reference-spike`, created from `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`. `main` is an ancestor (fast-forward possible). The reviewed checkpoint `f04f995` is 27 commits ahead of `86df2c3`. Further commits record this review and this dossier.
- **Reviewed checkpoint unchanged:** at preparation time, HEAD = origin = `f04f995` and the reviewer's clone is clean at `f04f995`. The commits after it add the Review 09 record, its raw output and evidence, appended notes in the T0 report and decision matrix, and this dossier. No experiment, result, check or model file changes after `f04f995`.
- **Scope:** `git diff --name-only 86df2c3 f04f995 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty. Every T0 change is under `docs/`.
- **Review chain:** 9 independent Codex rounds. Records: `docs/reviews/M3-T0-review-0{1,…,9}.md`. Raw outputs and prompts (which hold every Tech Lead text verbatim: I-15, I-4 to I-11): `docs/reviews/raw/M3-T0-codex-review0{1,…,9}{,-prompt}.md`. Reviewer and implementer evidence: `docs/reviews/raw/`.

| Round | Reviewed commit | Verdict | New findings |
|---|---|---|---|
| 01 | `ca84986` | REQUEST_CHANGES | F1, F2 (MAJOR); F3, F4 (MINOR); F5 (NOTE); IM-1 |
| 02 | `ead2a84` | REQUEST_CHANGES | R2-F1, R2-F2 (MINOR); R2-F3 (NOTE) |
| 03 | `51e110b` | REQUEST_CHANGES | R3-F1 (MINOR) |
| 04 | `44260ef` | REQUEST_CHANGES | R4-F1 (MINOR); IM-2 (implementer) |
| 05 | `88f9752` | REQUEST_CHANGES | R5-F1, R5-F2 (MINOR) |
| 06 | `fcd5997` | REQUEST_CHANGES | R6-F1 (MINOR); R6-F2, R6-F3 (NOTE); two remarks |
| 07 | `0357196` | REQUEST_CHANGES | R7-F1, R7-F2 (NOTE) |
| 08 | `95fff22` | REQUEST_CHANGES | R8-F1 (NOTE); M3 coverage observation |
| 09 | `f04f995` | **PASS (unconditional)** | R9-F1, R9-F2 (NOTE) |

## Validation evidence at the reviewed checkpoint
| Check | Result | Evidence |
|---|---|---|
| T0 checks (`check_review01.py` … `check_review08.py`) | 288/288, by the implementer and by the reviewer; again in the reproducibility clone | `raw/M3-T0-review08-findings-correction-evidence/checks_after.log`; `raw/M3-T0-codex-review09-evidence/checks.log` |
| Mutation harness | Control 288/288; 87/87 non-equivalent mutants detected by a declared check; **survivors: none**; **equivalent: 2** (declared, each with a passing establishing check). The reviewer reran a declared subset (14 R8 + 6 earlier + 2 equivalents) and found one new survivor (R9-F1) | `mutation_check_review08.json`; reviewer `old_mutants.json`, `new_mutants.log` |
| M1 Proof (fresh clone at `0254664`) | PASS, 9/9 steps, clean | `m1_proof_run.log` |
| M2 Proof (separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean | `m2_proof_run.log`, `m2_proof_stdout.txt` |
| Full pytest | 1185 passed, 3 warnings (implementer and reviewer) | `pytest_full.log`; reviewer `pytest.log` |
| M1/M2 validators and GMAT compares (reviewer) | PASS; M2 228/228; both compares exit 0 | reviewer `m1.log`, `m2.log`, `m1_compare.log`, `m2_compare.log` |
| Pinned digests | All five unchanged since `86df2c3` (implementer and reviewer) | `pinned_digests.log`; reviewer `digests.log` |
| Spike digests | All **21** VAL-0019 digests match. There are 21 rather than 20 because I-11 added `check_review08.py`; the updated `t0_termination.py` and `mutation_check_review02.py` entries keep their earlier digests in the record | same |
| T0 reproducibility | All nine experiments run twice, including the GMAT harness, by the implementer and independently by the reviewer: all 98 tracked experiment files byte-identical | `reproducibility_twice.log`; reviewer `repro_1_changes.json`, `repro_2_changes.json` |
| Numerical outputs | **Byte-identical** to `115e747`, and no result file changed in the I-11 pass. The docstring-free AST of `t0_termination.py` is unchanged | `termination_regenerated.log`, `ast_docstring_free_equal.log`; reviewer `results_diff.txt`, `ast_fixed.log` |
| CI | Runs 39641717044 (`0254664`) and 39652330844 (`f04f995`): all four jobs succeeded. **CI does not collect the T0 checks** (`testpaths = ["tests"]`), so CI does not validate them; they ran on macOS x86_64 only | GitHub Actions |
| GMAT installation | Console `1162803d…52e2` and atmosphere table `75762f67…a85e`, verified by both | reviewer `integrity.log` |

Environment: macOS 26.2 (Darwin 25.2.0) x86_64, Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1 from `uv.lock`, GMAT R2026a.

## What T0 delivers (I-15 §4–§5)
- **Reference configurations and regression (A, D).** GMAT M3 configurations are generated by an additive splice of the committed M1/M2 generators. With perturbations off they reproduce the committed scripts and reports byte for byte, and the spike's RK4 is bitwise equal to the M1 golden. No tolerance was relaxed. J2 matches to 0.076 mm with GMAT's polar-motion axis (a diagnostic).
- **Atmosphere and drag (B).** Every band boundary is exercised, and GMAT's band rule is confirmed. The RK4 stiffness threshold is 51 244.55 m for B 25.8 at dt = 10 s. The third RK4 stage sits about 117 m below the committed path. Geodetic height is validated against exact, published and GMAT points.
- **Sufficient stage-domain floors** (sufficient, not necessary): B 25.8 = 124 456.68544510857 m, B 100 = 118 633.50894662621 m, drag-free = 111 511.96182508787 m. Each certifies that every RK4 stage of a 10 s step from a committed height at or above it stays above the table's lower edge, under the premises below. Re-derived by the reviewer bit for bit.
- **Frames (C).** DR-0028 J-ax-1 is used throughout. Its limitation against GMAT's real Earth is quantified: 0.19–0.58 m final and up to 1.08 m over 10 orbits; up to 4 cm in geodetic height.
- **Decision proposals:** DR-0029 (OPEN) P1–P10, with the decision matrix `docs/milestones/M3-T0-decision-matrix.md`. Nothing is approved; no default is proposed.

## Outstanding limitations (conditions of every guarantee)
- **A-FP-1** (IEEE binary64, round-to-nearest-even, gradual underflow): checked at run time on this host only.
- **A-FP-2** (libm accuracy, LIBM_ULP): **unresolved**, an explicitly conditional assumption. It was measured on macOS x86_64 only, and E4b depends on it explicitly (LIBM_ULP ≤ 91 910 196 476 947).
- **A-FP-3** (elementwise products; the mixed dot-product allowance): stated; one NumPy backend was observed.
- **Host evidence only.** Host measurements are not platform guarantees. No other OS, CPU or library backend was tested.
- **Contract scope.** C1 or C2 vehicles constructed from positive finite mass, cd and area; arbitrary independently supplied (mass, b) pairs are excluded. No overflow.
- **Floor conditions.** Exterior bound states with negative two-body energy, computed committed heights, no thrust, dt = 10 s.
- **Stage condition domain.** Every returned value needs a computed h0 > β (8.877691069434738e-09 m). A computed h0 ≤ β raises `ValueError`, also for exterior states just above the ellipsoid; it is never a certification (R8-F1).
- **No certified combined J2-plus-drag missed-crossing bound.** Perturbed missed-dip values are sampled estimates.
- **The 5 287-point random search** (Review 06 remark) remains UNREPRODUCED. No conclusion uses it.
- **IM-2.** The drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The disposition is kept as ordered.

## Open NOTEs from Review 09 (ACCEPTED, reproduced, not corrected under I-11)
- **M3T0-R9-F1 (checks only).** A mutant that drops M3 from the stage minimum only when M3 is finite passes all 288 checks. The committed code is correct: an injected envelope of 10^8, then 0, gives need = +2.4999e9; the mutant would return −89 239.7. Proposed: add that finite M3-dominant case and the mutant.
- **M3T0-R9-F2 (check and quotation precision).** The pole check uses the F-defined polar radius, while the model and oracle use the E2 ellipsoid; they differ by 2.48e-13 m. The quoted −2.03e-10 m is −2.04e-10 m on the E2 ellipsoid. No classification, floor or certification changes; the seeded probe classifies identically. Proposed: derive from E2 and amend the quotation append-only.

Details and reproduction: `docs/reviews/M3-T0-review-09.md`. Whether these are corrected before or after acceptance is the Tech Lead's decision. Either needs authorization.

## Open decisions and escalations
- **ESCALATED_FOR_INVESTIGATION:** the GMAT geodetic-drag configuration sensitivity (DR-0029 Q-G2-1/P6), at 0.14–0.38 m and unexplained. It is not closed by T0.
- **DR-0029 P1–P10:** OPEN, undecided. P10 gates T1; P1–P10 gate T2. A ruling on whether Q-G2-1 option (b) falls under DR-0028's prohibition is requested in DR-0029.
- **DR-0028 P6(b):** undecided.
- **Branch protection and rulesets:** none on `main`. Recommendations are in `M3-T0-report.md` §3; no setting was changed. This needs separate authorization.

## Decisions requested from the Tech Lead
1. Accept or decline T0 at the reviewed checkpoint `f04f995` (with the review-record commits that follow it).
2. Disposition of the two Review 09 NOTEs: correct them before acceptance, after acceptance, or record them as accepted limitations.
3. Separately, if T0 is accepted: authorization to merge `milestone-3-t0-reference-spike` into `main`.
4. Separately: DR-0029 P10 (and an authorization) before T1; P1–P10 before T2; DR-0028 P6(b); the branch-protection recommendations.
