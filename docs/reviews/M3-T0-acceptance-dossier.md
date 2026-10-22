# M3 T0 — acceptance dossier (for the Tech Lead's decision)

**Prepared under:** "Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09", §7 (Review 09 returned PASS): "Prepare a T0 acceptance dossier with complete evidence and outstanding limitations. Do not declare T0 accepted. Do not merge. Do not start T1/T2. Stop for my explicit acceptance decision." It also follows I-15 (review) for an unconditional PASS: "Preserve the complete review output. Verify the reviewed commit and evidence are unchanged. Prepare the T0 acceptance report. Stop for owner acceptance."

**Updated under:** "Authorization I-12 — M3 T0 Review 09 NOTE Corrections and Independent Review 10", §7 (Review 10 returned PASS): "update the acceptance dossier, report limitations and open decisions, and stop for the explicit final T0 acceptance decision." The I-11 version of this dossier (reviewed checkpoint `f04f995`, Review 09 NOTEs open) is preserved at `5978bfe`.

**Status: T0 is NOT accepted.** This dossier is a recommendation and an evidence index. It makes no decision. It does not merge, it does not start T1 or T2, and it does not decide DR-0029 P1–P10 or DR-0028 P6(b).

## Recommendation
- **T0 acceptance: READY** for the owner's decision.
  - Independent Review 10 (Codex, at `3c565e62e8257040b48bdd1d0d74fffc370d56d2`) returned `VERDICT: PASS (unconditional)` with **no new findings**.
  - Every tracked finding is RESOLVED: F1–F5, R2-F1…R2-F3, R3-F1, R4-F1, R5-F1, R5-F2, R6-F1…R6-F3, both Review 06 remarks, R7-F1, R7-F2, R8-F1, R9-F1, R9-F2, IM-1, IM-2 and the Review 08 M3 coverage observation.
  - **No finding is open.**
- **T1 (J2) readiness: BLOCKED until DR-0029 P10 is decided.** It is READY from the T0 standpoint once P10 is decided. T1 also needs its own authorization.
- **T2 (drag) readiness: BLOCKED** on DR-0029 P1–P10, in particular P1–P5, P8 and P9. T4/T5 additionally need P6 and P7, and the geodetic GMAT gates wait on the escalated investigation.

## Branch and commits
- **Branch:** `milestone-3-t0-reference-spike`, created from `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`. `main` is an ancestor, so a fast-forward is possible.
- **Reviewed checkpoint:** `3c565e6` is 30 commits ahead of `86df2c3`. It consists of:
  - correction commit `cc82ae7` (R9-F1 checks; R9-F2 pole reference and quotation);
  - validation commit `3c565e6`.

  A further commit records Review 10 and this update.
- **Reviewed checkpoint unchanged:** at the time of this update, HEAD = origin = `3c565e6`, and the reviewer's clone is clean at `3c565e6`. The commit after it adds:
  - the Review 10 record, raw output and evidence;
  - appended notes in the T0 report, the decision matrix, VAL-0019 and DR-0029;
  - this update.

  No experiment, result, check or model file changes after `3c565e6`.
- **Scope:** `git diff --name-only 86df2c3 3c565e6 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty. Every T0 change is under `docs/`.
- **Review chain:** 10 independent Codex rounds.
  - Records: `docs/reviews/M3-T0-review-{01,…,10}.md`.
  - Raw outputs and prompts: `docs/reviews/raw/M3-T0-codex-review{01,…,10}{,-prompt}.md`. The prompts hold every Tech Lead text verbatim: I-15 and I-4 to I-12.
  - Reviewer and implementer evidence: `docs/reviews/raw/`.

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
| 09 | `f04f995` | PASS (unconditional) | R9-F1, R9-F2 (NOTE), corrected under I-12 |
| 10 | `3c565e6` | **PASS (unconditional)** | none |

## How the Review 09 NOTEs were closed (I-12)
- **M3T0-R9-F1 (checks).** `check_review09.py` calls the production `stage_lower_heights` and `stage_need`, injecting only the force bound.
  - It pins need = −M3 whenever a finite M3 is the minimum. This covers the Review 09 counterexample (need = +2 499 855 380.144757, not certified) and 14 further cases of both signs.
  - It also distinguishes the three outcomes: +∞, finite non-certification and certification.
  - The finite-only M3 mutant and two related mutants are in the harness and detected.
- **M3T0-R9-F2 (check and quotation).**
  - The pole reference of `check_review08.py` is now the model's ellipsoid b² = a²(1 − e2). The model's polar radius a·√(1 − e2) is 2.48e-13 m above A·(1 − F).
  - The quotation is corrected to −2.04e-10 m, and appended amendments in the Review 07 and 08 records and VAL-0019 keep the original wording.
- **No executable change.** No executable statement of the model, oracle or termination code changed, and no value, floor, bracket or threshold changed. The numerical outputs are byte-identical to the I-11 baseline. Details: `docs/reviews/M3-T0-review-09.md` (correction and validation sections).

## Validation evidence at the reviewed checkpoint
| Check | Result | Evidence |
|---|---|---|
| T0 checks (`check_review01.py` … `check_review09.py`) | 314/314 by the implementer and by the reviewer, and again in the reproducibility clone. Red before at `5978bfe`: `check_review09.py` fails 3 of 26; the reviewer's finite-only mutant fails 16 | `raw/M3-T0-review09-findings-correction-evidence/checks_after.log`, `checks09_before_5978bfe.log`, `r9f1_mutant_vs_check09.log`; reviewer `t0checks.log`, `red_before.log` |
| Mutation harness | Control 314/314. 100/100 non-equivalent mutants (87 earlier + 13 R9) are detected by a declared check. **Survivors: none.** **Equivalent: 2**, each declared with a passing establishing check. The reviewer reran a declared subset (13 R9 + 9 earlier + 3 of its own + 2 equivalents) with no survivor | `mutation_check_review09.json`; reviewer `mutations.json`, `earlier_mutations.json`, `new_mutations.json` |
| M1 Proof (fresh clone at `cc82ae7`) | PASS, 9/9 steps, clean | `m1_proof_run.log` |
| M2 Proof (separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean | `m2_proof_run.log`, `m2_proof_stdout.txt` |
| Full pytest | 1185 passed, 3 warnings (implementer and reviewer) | `pytest_full.log`; reviewer `pytest.log` |
| M1/M2 validators and GMAT compares (reviewer) | M1 7/7, M2 228/228; both compares exit 0 | reviewer `m1.log`, `m2.log`, `compare1.log`, `compare2.log` |
| Pinned digests | All five unchanged since `86df2c3` (implementer and reviewer) | `pinned_digests.log`; reviewer `integrity.log` |
| Spike digests | All **22** VAL-0019 digests match. The count went from 21 to 22 because I-12 added `check_review09.py`; the updated entries keep their earlier digests in the record | same |
| T0 reproducibility | The implementer and, independently, the reviewer each ran all nine experiments twice, including the GMAT harness: all 99 tracked experiment files byte-identical | `reproducibility_twice.log`; reviewer `repro1_changes.json`, `repro2_changes.json` |
| Numerical outputs | **Byte-identical** to the I-11 baseline `f04f995`: no result file changed in the I-12 pass. The docstring-free AST of `t0_termination.py` is unchanged, and the model and oracle are byte-identical | `termination_regenerated.log`, `ast_docstring_free_equal.log`; reviewer `integrity.log` |
| CI | Runs 39695797213 (`cc82ae7`) and 39701788045 (`3c565e6`): all four jobs succeeded. **CI does not collect the T0 checks** (`testpaths = ["tests"]`), so CI does not validate them; they ran on macOS x86_64 only | GitHub Actions |
| GMAT installation | Console `1162803d…52e2` and atmosphere table `75762f67…a85e`, verified by both | reviewer `integrity.log` |

Environment: macOS 26.2 (Darwin 25.2.0) x86_64, Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1 from `uv.lock`, GMAT R2026a.

## What T0 delivers (I-15 §4–§5)
- **Reference configurations and regression (A, D).**
  - GMAT M3 configurations are generated by an additive splice of the committed M1/M2 generators. With perturbations off they reproduce the committed scripts and reports byte for byte.
  - The spike's RK4 is bitwise equal to the M1 golden. No tolerance was relaxed.
  - J2 matches to 0.076 mm with GMAT's polar-motion axis (a diagnostic).
- **Atmosphere and drag (B).**
  - Every band boundary is exercised, and GMAT's band rule is confirmed.
  - The RK4 stiffness threshold is 51 244.55 m for B 25.8 at dt = 10 s, and the third RK4 stage sits about 117 m below the committed path.
  - Geodetic height is validated against exact, published and GMAT points.
- **Sufficient stage-domain floors** (sufficient, not necessary): B 25.8 = 124 456.68544510857 m, B 100 = 118 633.50894662621 m, drag-free = 111 511.96182508787 m. Each certifies that every RK4 stage of a 10 s step from a committed height at or above it stays above the table's lower edge, under the premises below. Re-derived bit for bit by Reviews 09 and 10.
- **Frames (C).** DR-0028 J-ax-1 is used throughout. Its limitation against GMAT's real Earth is quantified: 0.19–0.58 m in final position, up to 1.08 m over 10 orbits, and up to 4 cm in geodetic height.
- **Decision proposals:** DR-0029 (OPEN) P1–P10, with the decision matrix `docs/milestones/M3-T0-decision-matrix.md`. Nothing is approved, and no default is proposed.

## Outstanding limitations (conditions of every guarantee)
- **A-FP-1** (IEEE binary64, round-to-nearest-even, gradual underflow): checked at run time on this host only.
- **A-FP-2** (libm accuracy, LIBM_ULP): **unresolved**, an explicitly conditional assumption. It was measured on macOS x86_64 only, and E4b depends on it explicitly (LIBM_ULP ≤ 91 910 196 476 947).
- **A-FP-3** (elementwise products; the mixed dot-product allowance): stated; one NumPy backend was observed.
- **Host evidence only.** Host measurements are not platform guarantees. No other OS, CPU or library backend was tested.
- **Contract scope.** C1 or C2 vehicles constructed from positive finite mass, cd and area; arbitrary independently supplied (mass, b) pairs are excluded. No overflow.
- **Floor conditions.** Exterior bound states with negative two-body energy, computed committed heights, no thrust, dt = 10 s.
- **Stage condition domain.** Every returned value needs a computed h0 > β (8.877691069434738e-09 m). A computed h0 ≤ β raises `ValueError`, also for exterior states just above the ellipsoid; it is never a certification (R8-F1).
- **M3 and the published values.** With the default envelope, M4 < M3 < M2 was observed in a sampled sweep, and the published results regenerate byte for byte with M3 dropped. This is a finite verification of the published values, not a proof that M3 is redundant; for injected envelopes M3 can decide need (R9-F1).
- **No certified combined J2-plus-drag missed-crossing bound.** Perturbed missed-dip values are sampled estimates.
- **The 5 287-point random search** (Review 06 remark) remains UNREPRODUCED. No conclusion uses it.
- **IM-2.** The drag-free floor quoted to the nearest centimetre (111 511.96 m) is 1.8 mm below the bound. The disposition is kept as ordered.
- **Validation coverage.**
  - Review 10 reran a declared subset of the mutation harness, not all 100 mutants. The full run is implementer evidence.
  - The Proof wrappers were run by the implementer only; the reviewer ran the validators.

## Open decisions and escalations
- **ESCALATED_FOR_INVESTIGATION:** the GMAT geodetic-drag configuration sensitivity (DR-0029 Q-G2-1/P6), at 0.14–0.38 m and unexplained. T0 does not close it.
- **DR-0029 P1–P10:** OPEN and undecided. P10 gates T1, and P1–P10 gate T2. DR-0029 also requests a ruling on whether Q-G2-1 option (b) falls under DR-0028's prohibition.
- **DR-0028 P6(b):** undecided.
- **Branch protection and rulesets:** `main` has none. Recommendations are in `M3-T0-report.md` §3; no setting was changed. Any change needs separate authorization.

## Decisions requested from the Tech Lead
1. Accept or decline T0 at the reviewed checkpoint `3c565e6`, together with the review-record commit that follows it.
2. Separately, if T0 is accepted: authorization to merge `milestone-3-t0-reference-spike` into `main`.
3. Separately:
   - DR-0029 P10, and an authorization, before T1;
   - DR-0029 P1–P10 before T2;
   - DR-0028 P6(b);
   - the branch-protection recommendations.
