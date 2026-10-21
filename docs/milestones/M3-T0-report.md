# M3 T0 checkpoint report (reference-configuration spike)

**Status:** T0 experimental work and validation complete at `294e1f5`. **The independent Codex review has not started:** the copy of I-15 received by the implementer ends at the start of §8, so §8 has not been read. **No decision is taken here; T1 and later are not authorized.**  
**Status update (2026-10-18, append-only):** independent **Review 01 (Codex, at `ca84986`): REQUEST_CHANGES**: M3T0-F1 and F2 (MAJOR), F3 and F4 (MINOR), F5 (NOTE), all ACCEPTED and verified, **not applied**; plus implementer item IM-1. Record: `docs/reviews/M3-T0-review-01.md`. Owner decision matrix: `M3-T0-decision-matrix.md`. T0 is not accepted. Corrections and any further review round await authorization.  
**Status update (2026-10-18, append-only):** under "TARS M3 T0 — Review 01 Correction Authorization", F1–F4 are corrected in the T0 records and experiments, with regression checks (`docs/science/experiments/m3-t0/check_review01.py`); dispositions in `docs/reviews/M3-T0-review-01.md`. IM-1 is outside that scope and unchanged. Review 02 follows. T0 is not accepted.  
**Status update (2026-10-18, append-only):** **Review 02 (Codex, at `ead2a84`): REQUEST_CHANGES.** F3, F4 and F5 are RESOLVED; F1 and F2 are PARTIALLY RESOLVED. New findings: M3T0-R2-F1 and R2-F2 (MINOR) and R2-F3 (NOTE), all verified and ACCEPTED, **not applied**. Record: `docs/reviews/M3-T0-review-02.md`. T0 is not accepted. Corrections and Review 03 await authorization.  
**Status update (2026-10-18, append-only):** under "Authorization: M3 T0 — Review 02 Corrections and Independent Review 03", R2-F1, R2-F2, R2-F3 and IM-1 are corrected in the T0 records and experiments: perturbed-motion values are labelled sampled estimates; the stage-domain drag envelope is corrected; the new checks recompute what they protect (`check_review02.py`, with mutation evidence); and the P6 axis-fit residual is reproduced (`t0_axis_ablation.py`). Dispositions are in `docs/reviews/M3-T0-review-02.md`. Review 03 follows. T0 is not accepted.  
**Status update (2026-10-18, append-only):** **Review 03 (Codex, at `51e110b`): REQUEST_CHANGES.**
- R2-F1, R2-F3, IM-1, F1, F3, F4 and F5 are RESOLVED.
- R2-F2 and F2 are PARTIALLY RESOLVED.
- New finding M3T0-R3-F1 (MINOR): the stage-domain drag envelope does not cover numerical height error at downward density jumps. It is verified and ACCEPTED, **not applied**.
- Record: `docs/reviews/M3-T0-review-03.md`. T0 is not accepted. A correction pass and any Review 04 await authorization.  
**Status update (2026-10-19, append-only):** under "Authorization I-4: M3 T0 — R3-F1 Correction and Independent Review 04", M3T0-R3-F1 is corrected in the T0 records and experiments:
- The stage-domain drag envelope now bounds the model's drag at its computed height. It uses a derived height-error bound (ε_h = 9.02e-9 m at 120 km) and derived rounding factors for the density, drag, gravity and RK4 stage arithmetic.
- This holds under the floating-point assumptions A-FP-1 … A-FP-3. A-FP-2, the libm accuracy, is unresolved and measured on macOS x86_64 (the M1/M2 reference host) only.
- The P1 bounds are unchanged at the quoted precision, and the P1 recommendation is unchanged.
- The new checks (`check_review03.py`) use an independent high-precision height oracle (`t0_oracle.py`), with mutation evidence. The empirical side is `t0_height_error.py`.
- Dispositions are in `docs/reviews/M3-T0-review-03.md`. Review 04 follows. T0 is not accepted.  
**Status update (2026-10-19, append-only):** **Review 04 (Codex, at `44260ef`): REQUEST_CHANGES.**
- R2-F1, R2-F3, IM-1, F1, F3, F4 and F5 are RESOLVED.
- R3-F1, R2-F2 and F2 are PARTIALLY RESOLVED: the density-jump cases are covered, but the global drag envelope omits underflow.
- New finding M3T0-R4-F1 (MINOR): above about 181 890 km the density is subnormal, and the model's drag exceeds the envelope (2.01× at 190 681 km). No stage below 0 m is shown at the published floors. It is verified and ACCEPTED, **not applied**.
- Record: `docs/reviews/M3-T0-review-04.md`. T0 is not accepted. A correction pass and any Review 05 await authorization.  
**Status update (2026-10-19, append-only):** under "Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05", M3T0-R4-F1 is corrected in the T0 records and experiments:
- The floating-point model now carries the absolute error of subnormal results (IEEE gradual underflow; libm absolute term for subnormal outputs). The drag envelope gains an absolute part, bounded up to the height above which the computed density is exactly 0. No altitude restriction is introduced.
- The three P1 bounds are unchanged to the last bit, and the P1 recommendation is unchanged. The quotation of the drag-free bound to the nearest centimetre is clarified (IM-2).
- A-FP-2 remains an assumption, measured on macOS x86_64 only. It is weakened to "within 2^5 ulps" for the published bounds.
- New checks: `check_review04.py`, with mutation evidence. Dispositions are in `docs/reviews/M3-T0-review-04.md`. Review 05 follows. T0 is not accepted.  
**Status update (2026-10-19, append-only):** **Review 05 (Codex, at `88f9752`): REQUEST_CHANGES.**
- R2-F1, R2-F3, IM-1, IM-2, F1, F3, F4 and F5 are RESOLVED.
- R4-F1, R3-F1, R2-F2 and F2 are PARTIALLY RESOLVED: the original point and both illustrative vehicles are covered, but the unrestricted envelope contract is not.
- New findings, both MINOR, verified and ACCEPTED, **not applied**:
  - M3T0-R5-F1: the conversion to the ballistic coefficient keeps a relative-only rounding factor. A subnormal b (mass 17 × 2^-1074 kg) gives drag 1.94× the envelope. It does not affect the published floors, which use B 25.8, B 100 and the drag-free limit.
  - M3T0-R5-F2: the empirical maximum 0.983 is scoped as the whole subnormal regime, but the committed transition scan reaches 0.99999999999886 at subnormal densities.
- Record: `docs/reviews/M3-T0-review-05.md`. T0 is not accepted. A correction pass and any Review 06 await authorization.  
**Status update (2026-10-19, append-only):** under "Authorization I-6 — M3 T0 Review 05 corrections only", M3T0-R5-F1 and R5-F2 are corrected in the T0 records and experiments:
- R5-F1: the drag envelope bounds cd·area/mass with the absolute error of every underflowing rounding of the conversion between the ballistic coefficient and the mass, for either construction (E4a). It equals the previous bound wherever the conversion is normal. A vehicle with cd·area ≤ 2^-1075 has exactly zero force (E4b). No vehicle condition is introduced, and the domain is unchanged.
- The three P1 bounds and every other termination result are unchanged to the last bit. The P1 recommendation is unchanged.
- R5-F2: 0.983 is scoped to the coefficient-rounding subset. The committed transition scan reaches 0.99999999999886 at subnormal densities. The Review 04 record is amended, not rewritten.
- A-FP-2 remains an unresolved assumption, measured on macOS x86_64 only.
- New checks: `check_review05.py`, with mutation evidence. Dispositions are in `docs/reviews/M3-T0-review-05.md`. T0 is not accepted. Any Review 06 needs separate authorization.  
**Status update (2026-10-20, append-only):** **Review 06 (Codex, at `fcd5997`): REQUEST_CHANGES.**
- R5-F2, R2-F1, R2-F3, IM-1, IM-2, F1, F3, F4 and F5 are RESOLVED.
- R5-F1, R4-F1, R3-F1, R2-F2 and F2 are PARTIALLY RESOLVED: both Review 05 counterexamples are covered, but the unrestricted envelope contract is not.
- New findings, verified and ACCEPTED, **not applied**:
  - M3T0-R6-F1 (MINOR): under C1 a positive mass can round to a ballistic coefficient of exactly 0 (mass ≤ 16 × 2^-1074 kg with cd·area = 33 m²). The model's drag is finite and nonzero; the envelope raises a division by zero. The statement above that E4a needs "no vehicle condition" therefore does not yet hold for b = 0. It does not affect the published floors, which use B 25.8, B 100 and the drag-free limit.
  - M3T0-R6-F2 (NOTE): `_up`/`_dn` do not handle every overflow or sign as their docstring claims; no published result is affected.
  - M3T0-R6-F3 (NOTE): E4b's zero-force cap inherits A-FP-2 through the density bound; it was classified as derived under A-FP-1 only.
- The 5 287-point random search quoted in the Review 04 record is unreproduced historical evidence.
- Record: `docs/reviews/M3-T0-review-06.md`. T0 is not accepted. A correction pass and any Review 07 await authorization.  
**Status update (2026-10-20, append-only):** under "Authorization I-8 — M3 T0 Review 06 Corrections", M3T0-R6-F1, R6-F2 and R6-F3 are corrected in the T0 records and experiments:
- R6-F1: E4a covers a ballistic coefficient of exactly 0 under C1 through the positive-mass fact mass ≥ 2^-1074 (R(0) = max(cd·area/2^-1074, R(2^-1074))). The Review 06 masses are within the corrected envelope (ratio 0.9999999999988 at k = 1). Every positive ballistic coefficient, the three P1 bounds and every pre-existing termination result are unchanged to the last bit. The P1 recommendation is unchanged.
- R6-F2: the rounding helpers handle infinite and out-of-range values and reject NaN. An envelope of +∞ certifies nothing, and invalid inputs raise an error instead of receiving a bound.
- R6-F3: E4b's cap c₀ ≤ 5/8 depends on A-FP-2 (it holds for LIBM_ULP ≤ 91910196476947); E4b is classified as derived under A-FP-1 and A-FP-2.
- The 5 287-point random search quoted in the Review 04 record is marked UNREPRODUCED. The switch point b* is quoted for the stored φ_B (7.416912861690675e-309, used by the implementation) and the exact φ_B (1.1125369292536007e-308).
- A-FP-2 remains an unresolved assumption, measured on macOS x86_64 only.
- New checks: `check_review06.py`, with mutation evidence. Dispositions are in `docs/reviews/M3-T0-review-06.md`. T0 is not accepted. Any Review 07 needs separate authorization.  
**Status update (2026-10-20, append-only):** **Review 07 (Codex, at `0357196`): REQUEST_CHANGES.**
- R6-F1, R6-F3, both Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5 are RESOLVED.
- R6-F2 is PARTIALLY RESOLVED: the helpers are fixed and no false certification was found, but an unbounded enclosure does not always give need = +∞ (R7-F1).
- New findings, both NOTE, verified and ACCEPTED, **not applied**:
  - M3T0-R7-F1: when M2 ≤ 0 the stage condition returns need = −M2, which is finite (for example 55 992 m at h0 = 1 m, b = 2^-1074). The step is still not certified; the statement "need = +∞" is too strong.
  - M3T0-R7-F2: two summaries keep "b_R ≤ b" without the b > 0 restriction.
- No floor, bound or certification is affected. Record: `docs/reviews/M3-T0-review-07.md`. T0 is not accepted. A correction pass and any Review 08 await authorization.  
**Status update (2026-10-20, append-only):** under "Authorization I-10 — M3 T0 Review 07 Corrections and Independent Review 08", M3T0-R7-F1 and R7-F2 are corrected. Both are documentation corrections: no executable statement, value, floor, bracket or threshold changed.
- R7-F1: a step is certified only when need < 0. The stage condition reports a non-certification on two paths: need = −M2, finite and ≥ 0, when M2 ≤ 0 (up to h0 = 55 749.393 m, for every vehicle), and need = +∞ when M2 > 0 with an unbounded envelope or a stage value outside the binary64 range.
- R7-F2: "b_R ≤ b" is qualified with b > 0; at b = 0, b_R = φ_B/R(0) > 0.
- A-FP-2 remains an unresolved assumption, measured on macOS x86_64 only.
- New checks: `check_review07.py`, with mutation evidence. Dispositions are in `docs/reviews/M3-T0-review-07.md`. T0 is not accepted. Review 08 follows under I-10.  
**Status update (2026-10-21, append-only):** **Review 08 (Codex, at `95fff22`): REQUEST_CHANGES.**
- R7-F2, R6-F1, R6-F2, R6-F3, both Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1, R2-F2, R2-F3, IM-1, IM-2 and F1–F5 are RESOLVED.
- R7-F1 is PARTIALLY RESOLVED, through one new NOTE, verified and ACCEPTED, **not applied**:
  - M3T0-R8-F1: a computed h0 ≤ β (8.88e-9 m) is attainable by strictly exterior bound states (for example 2^-30 m on the equator), and the stage condition then raises `ValueError` instead of returning the finite need stated above for M2 ≤ 0 and for the drag-free vehicle; the Review 07 record's claim that such heights are outside the domain is false. The step is still not certified.
- Reviewer observation, reproduced, not applied: dropping M3 from the stage minimum passes all 261 checks (a coverage gap; the published results are unchanged under it).
- No floor, bound or certification is affected. Record: `docs/reviews/M3-T0-review-08.md`. T0 is not accepted. A correction pass and any Review 09 await authorization.  
**Status update (2026-10-21, append-only):** under "Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09", M3T0-R8-F1 is corrected in the documentation, and the coverage gap is closed by new checks. No executable statement, value, floor, bracket or threshold changed.
- R8-F1: every value the stage condition returns needs a computed h0 > β (8.88e-9 m). A computed h0 ≤ β raises `ValueError`, for B_V1 and the drag-free vehicle, including for strictly exterior states just above the ellipsoid (r = [a + k·2^-30, 0, 0] m, k = 1 … 9). The finite need on the M2 ≤ 0 path quoted in the I-10 note above, and the drag-free vehicle's finite need, hold for h0 > β only. The decision is on the computed height, not the mathematical height.
- Coverage: an injected envelope that is +∞ at the first stage only must give need = +∞; the reviewer's M3-dropped mutant is now detected.
- A-FP-2 remains an unresolved assumption, measured on macOS x86_64 only. New checks: `check_review08.py`, with mutation evidence. Dispositions are in `docs/reviews/M3-T0-review-08.md`. T0 is not accepted. Review 09 follows under I-11.  
**Status update (2026-10-21, append-only):** **Review 09 (Codex, at `f04f995`): PASS (unconditional).**
- Every tracked finding is RESOLVED: R8-F1, R7-F1, R7-F2, R6-F1 … R6-F3, both Review 06 remarks, R5-F1, R5-F2, R4-F1, R3-F1, R2-F1 … R2-F3, IM-1, IM-2, F1–F5 and the Review 08 M3 coverage observation.
- Two new NOTEs, verified and ACCEPTED, **not applied** (I-11 §7): M3T0-R9-F1, a mutant that drops M3 only when it is finite passes all 288 checks (a coverage gap; the code is correct); M3T0-R9-F2, the pole check and the quoted −2.03e-10 m use the F-defined polar radius instead of the model's E2 ellipsoid (−2.04e-10 m there; no classification changes).
- No floor, bound or certification is affected. Record: `docs/reviews/M3-T0-review-09.md`. Acceptance dossier: `docs/reviews/M3-T0-acceptance-dossier.md`. **T0 is not accepted**; it awaits the owner's decision. Not merged; T1 and T2 not started.  
**Authority:** "TARS — M3 T0 Reference-Configuration Spike Authorization" (Tech Lead, I-15, 2026-10-18), T0 only.  
**Branch:** `milestone-3-t0-reference-spike`, created from `main` = `86df2c3ff189db26f42bd273b6fe71de502c51a3`.

## 1. Preflight (I-15 §2)
| Check | Result |
|---|---|
| `origin/main` contains the accepted merge commit | `origin/main` = `86df2c3`, after `git fetch --all --prune`. PR #4: MERGED 2026-10-18T04:48:19Z, merge commit `86df2c3` (parents `d92ab89`, `93e356a`) |
| CI on `86df2c3` | All four jobs succeeded: `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform` |
| Worktree clean | Yes. T0 used worktree `nickel-page-8a63927f`, a separate worktree from the M3 planning worktree (`actually-splash`, branch `milestone-3-planning`), which was not touched |
| Discrepancies with I-15 | None. The local checkout of `main` (`/Users/…/projects/tars`, at `63bec8d`) is stale but an ancestor of `origin/main`; it was not modified |
| Deferred decisions | None treated as approved. Every OPEN, DEFERRED, T0 → owner and NOT AUTHORIZED item in `M3-decision-matrix.md` is unchanged |

## 2. Baseline and checkpoint validation (I-15 §7)
Both runs used `toolbox/scripts/run_m1_proof.sh` (9 steps) and `run_m2_proof.sh` (20 steps) in fresh scratch clones, so no evidence was written into the repository. Host: macOS 26.2 x86_64, i9-9880H.

| Revision | M1 Proof | M2 Proof | pytest | m2_proof checks |
|---|---|---|---|---|
| `86df2c3` (baseline) | PASS, 9/9 | PASS, 20/20 | 1185 passed | 228/228, 0 failed |
| `294e1f5` (T0 checkpoint) | PASS, 9/9 | PASS, 20/20 | 1185 passed | 228/228, 0 failed |

- **M1/M2 numerical behaviour preserved:** apart from its revision fields, the M2 Proof report at `294e1f5` is identical to the baseline's.
- **Pinned digests unchanged:** all five match `approved_digests.py` on the branch (m1.json `446e75ee…`, m2.json `9d4eab47…`, GMAT M2 manifest `f8d6bd78…`, snapshot `a2cddf4b…`, M2 golden `dc3baf7a…`).
- **No production changes:** `git diff --name-only 86df2c3 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty at `294e1f5` and at this report's commit.
- **CI on `294e1f5`** (run 39138140001): all four jobs succeeded. The run for the superseded intermediate commit `3729ffd` was cancelled (M2 lesson: the Intel runners queue).
- **Deviation:** the M2 wrapper logs `working_tree_clean_excluding_evidence: no` at both revisions.
  - Cause: in the same clone, the M1 wrapper had just rewritten `proof/records/evidence/M1/proof_run.log`, which the M2 wrapper does not exclude.
  - No source file was modified.
  - It is the same at the baseline, so it is a property of running both wrappers in one clone.
- **T0 reproducibility:** every T0 experiment was run twice from a clean state. All outputs, including the 67 GMAT run files, were byte-identical. The planning experiments (VAL-0018) were rerun in a scratch copy and reproduced; see VAL-0019.

## 3. Administrative corrections (I-15 §3)
- **Append-only status amendments:** PR #4 merged at `86df2c3`; instruction sources I-14 and I-15 added; T0 authorized. Recorded in:
  - `M3-decision-matrix.md` ("Planning merge and T0 authorization"; Gates rows);
  - `M3-proposal.md`;
  - `docs/milestones/README.md`.
- **T0 pointer notes** appended to DR-0024, DR-0025, DR-0027 and DR-0028.
- **Untouched:** no accepted decision, its evidence, or a historical review record was edited.

### Branch protection and rulesets (inspected 2026-10-18; no setting changed)
**Findings**
- `main`: `protected: false`. `GET …/branches/main/protection` returns 404 ("Branch not protected").
- Repository rulesets: none. Rules applying to `main`: none.
- The repository is public. Merge, squash and rebase merges are all allowed, although the project's practice is merge commits (PRs #1–#4).
- **Consequence:** nothing enforces the gates. A direct push, a force push, or a merge with failing CI would all succeed.

**Recommendation** (needs your separate authorization):
1. Add a ruleset (or classic protection) on `main`:
   - require a pull request;
   - require the status checks `check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)` and `m2-cross-platform`, with "require branches to be up to date";
   - block force pushes and deletion;
   - require conversation resolution.
2. Allow merge commits only, matching the merge-commit policy (disable squash and rebase merges).
3. **PR reviews:** GitHub does not let a PR's author approve it, and the PRs are opened from the owner's account. A required approval therefore needs one of:
   - a second reviewer account;
   - an owner bypass, used only for owner-approved merges;
   - 0 required approvals, keeping the Tech Lead's written approval as the gate.

   This is your choice. The implementer recommends required checks plus "require PR", with an explicit owner bypass.

## 4. T0 results (I-15 §4)
Full record: VAL-0019. Code and data: `docs/science/experiments/m3-t0/`. Highlights:
- **A. GMAT reference configurations.**
  - Generated by an additive splice of the committed M1/M2 generators. With perturbations off, the splice reproduces the committed scripts and GMAT's reports byte for byte.
  - Exact configuration: generated `.cof`, the pinned table, explicit flattening, TOEEq at the epoch, `Earth.NutationUpdateInterval` = 0.
  - J2 is matched to 0.076 mm once GMAT's polar-motion axis is applied (a diagnostic).
  - The geodetic-drag GMAT path depends on GMAT configuration at the 0.14–0.38 m level, unexplained: **ESCALATED_FOR_INVESTIGATION** (DR-0029 P6).
- **B. Atmosphere and drag.**
  - Every boundary has been exercised, and GMAT's band rule and densities are confirmed around all 27 boundaries.
  - GMAT fails closed below 0 km.
  - The M1 250 km altitude is exactly a band base.
  - RK4 stiffness: unstable below 51.2 km for B 25.8 at dt = 10 s (exact threshold 51 244.55 m; corrected after Review 01 F2 from the 5 km grid value).
  - The third RK4 stage (the input of k3) sits 117 m below the committed path (corrected after Review 01 F3).
  - A Hermite crossing location is accurate to the RK4 error.
  - Geodetic height has been validated against exact, published and GMAT points.
  - v_rel conventions are verified (FC-2, FC-5, FC-8).
- **C. Frames.**
  - J-ax-1 is used throughout. In GMAT the M3 frame I is realised as TOEEq fixed at the epoch.
  - The limitation is quantified against GMAT's real Earth: 0.19–0.58 m final and up to 1.08 m maximum over 10 orbits; up to 4 cm in geodetic height (polar motion 0.349″).
  - No rotating frame or other pole model is substituted. The GMAT-axis runs are labelled diagnostics.
- **D. Regression.**
  - Exact for M1 and M2 GMAT (byte-identical).
  - The M3-form configuration passes every M1 GMAT gate.
  - The spike's RK4 is bitwise equal to the M1 golden.
  - No tolerance was relaxed.

## 5. Decision requests (I-15 §5)
DR-0029 (OPEN) contains P1–P10:
- P1–P5: proposals for DR-0027 A-4, A-5, A-6, A-s and B-4;
- P6–P8: proposals for Q-G2-1, Q-G2-5 and Q-G2-7;
- P9: proposals for the DR-0024 Q9 values;
- P10 (new): the identity of the pinned J2 value;
- a requested ruling on whether Q-G2-1 option (b) falls inside DR-0028's prohibition.

Nothing is approved or closed.

## 6. Readiness recommendation (not authorization)
- **T1 (J2):** READY from the T0 standpoint, once P10 is decided.
- **T2 (drag):** BLOCKED on P1–P5, P8 and P9.
- **T4/T5:** need P6 and P7. Geodetic GMAT gates also wait on the escalated investigation.

## 7. Open items
- **Codex review:** waits for I-15 §8.
- **Escalated:** the geodetic-drag GMAT configuration sensitivity (DR-0029 P6).
- **Owner decisions:** P1–P10 (DR-0029).
- **Branch-protection settings:** await separate authorization.
