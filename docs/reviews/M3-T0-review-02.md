# M3 T0 Review 02 (independent review of the Review 01 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a1515c-9912-7b73-86ed-a47afd2116b1`.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review02-prompt.md`.

**Reviewed commit:** **`ead2a8417edfbb0855034098c8d85566e3fe7938`** (the correction checkpoint).
- The review ran in a fresh clone with its own `uv sync --locked` environment and a private GMAT R2026a copy. The implementer checked that copy against the installation: console and atmosphere-table digests match, and the only differing file is GMAT's own run log.
- The prompt was kept outside the repository during the review.

**Authority:** "TARS M3 T0 — Review 01 Correction Authorization" (Tech Lead, 2026-10-18), §4–§5. Its text is reproduced verbatim in the prompt.

**Files:**
- prompt: `raw/M3-T0-codex-review02-prompt.md`;
- raw output: `raw/M3-T0-codex-review02.md`, the reviewer's saved report;
- reviewer scripts and logs: `raw/M3-T0-codex-review02-evidence/` (`*.py.txt`; `SHA256SUMS`);
- the implementer's reproduction of the new findings: `raw/M3-T0-codex-review02-evidence/implementer-reproduction/`.

**Omitted** as derivable or large: the reviewer's copies of the diffs, the extracted `bdcaacf` tree, the mutant tree and the validator JSON.

**Verdict:** **REQUEST_CHANGES**. The new findings are 2 MINOR and 1 NOTE.

**Stop rule applied (correction authorization §5):**
- Every finding is recorded, and the new findings were independently reproduced by the implementer.
- The complete output is preserved.
- **No new finding is fixed, Review 03 is not started, and T0 is not accepted.** Authorization is requested.

## Review 01 findings: resolution assessed by Review 02
| Finding | Review 02 | Basis (reviewer) |
|---|---|---|
| M3T0-F1 (MAJOR) | **PARTIALLY RESOLVED** | The chord/curvature theorem, Hessian bound, normal angle and two-body maximisation were verified independently: 2000 analytic Hessians; 1000 domains with an independent stationary-root maximisation, agreeing to 5.33e-15 m/s². The perturbed "trajectory bound" uses a sampled maximum of U as if it were a supremum (R2-F1) |
| M3T0-F2 (MAJOR) | **PARTIALLY RESOLVED** | The exact thresholds (16 roots to 4.62e-14 in λdt), V_b, the counterexamples and the same-tick semantics are verified. The added sufficient stage-domain derivation has an invalid drag-envelope step (R2-F2) |
| M3T0-F3 (MINOR) | **RESOLVED** | Stage offsets reproduced; records name k3 |
| M3T0-F4 (MINOR) | **RESOLVED** | GMAT rerun reproduces 6.95223445873689e-6 m |
| M3T0-F5 (NOTE) | **RESOLVED** | Decision matrix separates the technical map from the owner's gate (record inspection) |

The reviewer also confirmed:
- the Review 01 record at `bdcaacf` is an exact prefix of the current record;
- the raw Review 01 files are unchanged;
- every changed path is under `docs/`;
- the five pinned digests match;
- all 85 tracked T0 experiment files reproduce byte for byte, including the GMAT harness;
- `check_review01.py` gives 11 failed and 1 passed at `bdcaacf` (via `git archive`) and 12 passed at `ead2a84`;
- the M1 validator passes, the M2 validator passes 228/228, and both GMAT compares pass;
- J-ax-1 is used throughout;
- the change of the P1 recommendation to V_b is disclosed and no owner option is defaulted.

**Not verified by the reviewer:**
- the full pytest run, which was started and deliberately interrupted;
- the Proof wrapper runs, which were prohibited;
- CI, because there is no network;
- external sources;
- other platforms.

## New findings
| ID | Severity | Finding (reviewer) | Implementer's independent reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R2-F1 | MINOR | `phase_sweep` (`t0_termination.py:166–174`) and the midpoint construction (`:187–207`) take the maximum of U over 0.25 s / 101 samples and present dt²/8 × that maximum as a bound. That maximum is not a supremum. Example: 180 km circular, 51.6°, J2 + drag: sampled U(2645.25 s) = 0.06313395420676038; refined U(2645.3148 s) = 0.06313395427588553 m/s². The theorem itself is correct. No dip above a reported bound is shown | **VERIFIED** with my own fine-grid refinement (5001 points over ±0.25 s, no optimiser): excess 6.91e-11 m/s², which changes the bound by 8.6e-10 m. **Root cause:** for perturbed motion the bound is evaluated numerically, so the records call a numerical estimate of sup U a bound without an enclosure or error allowance. The two-body bound is unaffected because it is maximised analytically over r | **ACCEPTED**; not applied |
| M3T0-R2-F2 | MINOR | The sufficient stage-domain derivation (`t0_termination.py:405–437`) bounds drag at a stage by ρ_sup(L)·(s + ω_E(a + L))²/(2B) at the lower height bound L. Density is bounded at L, but the rotation-speed term grows with height, so the product is not bounded. Counterexample: L = 79 999.9 m, actual height 80 000 m, s = 11 000 m/s retrograde at the equator, B 25.76 kg/m² (bound state): claimed 48.658376978072056, actual 48.65837703993666 m/s². The quoted floors are not shown to fail: 4000 random near-escape states above them had a minimum stage height of 14 555 m | **VERIFIED** (identical values recomputed: ρ_sup(L) = ρ(80 km) = 1.905e-5 kg/m³, underestimate 6.19e-8 m/s²). **Root cause:** the envelope evaluated the whole drag expression at the stage's lower height bound, but the co-rotation speed ω_E\|r\| needs an upper bound on the stage radius. A stage can also lie above h0, which the derivation did not bound. The lemma is invalid, although the effect is numerically tiny | **ACCEPTED**; not applied |
| M3T0-R2-F3 | NOTE | `check_review01.py` does not protect the new guarantees. With the sweep replaced by `{max_dip_m: 0, bound_m: 0}` and the stage floors set to 0, all 12 checks pass. The b²/a → a mutation is detected (1 check fails). There is no check of `sufficient_stage_condition` or of the sweep coverage | **VERIFIED** (my own mutant copy: "12 passed") | **ACCEPTED**; not applied |

### IM-1 (implementer item; Review 02 comment)
- **Reviewer's reproduction:** the reviewer reproduced the DR-0029 P6 figure from the committed axis-probe report with a quadratic-only two-orbit least-squares fit: **0.9856650955520649 m RMS**.
- **Implementer's check:** the implementer wrote an independent fit and got the same value (`implementer-reproduction/im1_fit.log`).
- **What remains:** the number is therefore supported by a committed artifact, but no committed script computes it and DR-0029 does not name the quantity (RMS) or the procedure. The reviewer does not raise it as a defect.
- **Status:** IM-1 stays OPEN, outside the correction scope. A proposed correction is to name the quantity and procedure in DR-0029 P6, or to add the fit to `t0_gmat.py`.

## Proposed corrections (for authorization; none applied)
1. **R2-F1:**
   - In the records and JSON, label the perturbed-motion values as sampled estimates of the bound, and keep guaranteed bounds to the analytic two-body bound.
   - Alternatively, compute a conservative continuous bound, for example from a bound on dU/dt over each sampling interval plus the dense-output error.
   - Add a check that refines between samples.
2. **R2-F2:**
   - Bound density at each stage's lower height bound, and co-rotation speed at its upper radius bound (r0 plus the stage displacement), including stages above h0.
   - Alternatively, maximise ρ·(s + ω_E\|r\|)² over the admissible height interval, including band jumps.
   - Re-justify the monotonicity in h0 and the root selection, recompute the three floors, and correct DR-0029 P1, P4 and VAL-0019.
3. **R2-F3:**
   - Add checks that assert the sweep matrix (orbits × physics × phases).
   - Add an independent test of `sufficient_stage_condition`: random admissible states above the floor stay in the domain, and the floor is self-consistent.
   - Add checks that recompute rather than read stored bounds.
4. **IM-1:** as above, if authorized.
5. **After correction:**
   - rerun the experiments twice;
   - run the checks before and after;
   - run the M1/M2 Proof, digests and CI;
   - run Review 03, which needs authorization.

## Lessons (proposed, not yet codified)
- A numerical maximum over samples is an estimate. A bound needs an enclosure, such as a derivative bound over each interval, or a separate analytic argument.
- In an envelope argument, bound each monotone factor at its own worst end of the admissible interval. Do not evaluate a product of factors with opposite monotonicity at one end.
- A regression check that only reads stored results cannot protect a derivation. It must recompute the guaranteed quantity, or check coverage.

## Dispositions after the Review 02 correction pass (appended 2026-10-18)
**Authority:** "Authorization: M3 T0 — Review 02 Corrections and Independent Review 03" (Tech Lead, 2026-10-18).
- The findings above are preserved unchanged.
- Each correction is listed below, with its regression evidence.
- Evidence directory: `raw/M3-T0-review03-correction-evidence/`; scratch paths are redacted.

| Finding | Root cause | Correction | Regression evidence | Status |
|---|---|---|---|---|
| M3T0-R2-F1 | For perturbed motion, a numerical estimate of sup U was called a bound, without an enclosure | **Classified as empirical; no bound claimed.**<br>- `t0_termination.py`: every J2 + drag value is a `sampled_estimate_m` with `estimate_kind` "…not a bound". `bound_m` is kept only for two-body rows and cases, labelled certified.<br>- The two-body maximisation is closed-form: the endpoints and the real roots of g'(r) = 0, which is a cubic. Its values are unchanged bit for bit.<br>- The between-sample refinement is recorded (+8.6e-10 m).<br>- DR-0029 P2, VAL-0019, the matrix and the README separate certified bounds from estimates. DR-0029 records that A5-b needs no perturbed bound, and that any use needing a guaranteed J2 + drag magnitude stays blocked | `check_review02.py`:<br>- sweep coverage of 9 orbits × 2 physics × 40 phases;<br>- each stored dip recomputed at its stored location;<br>- the stored dip shown to be at least the dips at five other phases;<br>- the two-body bound reproduced by a second maximisation method (brentq on an analytic g');<br>- the between-sample extremum;<br>- the labels;<br>- the record wording | Corrected; for Review 03 |
| M3T0-R2-F2 | The envelope evaluated the whole drag expression at the stage's lower height bound, although co-rotation speed grows with height | `drag_envelope` takes the supremum over h ≥ L of ρ(h)(s + ω_E(a + h))²/(2B), with both factors at the same h (\|r\| ≤ a + h).<br>- Inside every band that product decreases (a > 2H), so the supremum is attained at L or at a band base above L. This also covers stages above h0.<br>- Monotonicity in h0 is derived: the condition has a single root, and root finding needs no scan.<br>- Floors: 124 456.69 m (moved 1.1e-7 m), 118 633.51 m and 111 511.96 m, unchanged.<br>- The Review 02 counterexample is covered exactly; the superseded envelope fails it.<br>- The domain is unchanged: every bound state, any direction, no thrust | `check_review02.py`:<br>- the counterexample;<br>- adversarial drag points (band bases, just below upward jumps, equatorial retrograde, above h0);<br>- the per-band monotonicity premise;<br>- the floors by a second implementation (bisection) to 1 mm, with monotonicity on a grid;<br>- RK4 steps from 300 bound states per vehicle in the fail-closed model.<br>`termination` → `stress`: 2000 states per vehicle, smallest stage margin 0.10 m | Corrected; for Review 03 |
| M3T0-R2-F3 | Checks read stored values instead of recomputing them | `check_review02.py` has 38 recomputing checks, including a byte-for-byte rerun of `t0_termination.py` and unit checks. Two F1 checks in `check_review01.py` are amended for the relabelling. `mutation_check_review02.py` adds 16 mutants and a control, each mutant with declared detecting checks | - Red before: 11 of 50 fail at `5548d11` (`checks_before_5548d11.log`). The amended `check_review01.py` still gives 11 failed and 1 passed at `bdcaacf`.<br>- Green after: 50 of 50 pass (`checks_after.log`).<br>- Mutation (`mutation_check_review02.json`): 15 of 15 corruptions detected, including the exact Review 02 mutant (30 failures); 1 declared equivalent with its justifying check; the control passes | Corrected; for Review 03 |
| IM-1 | No committed procedure computed the P6 figure, and the quantity was not named | `t0_axis_ablation.py` → `t0_axis_ablation_results.json`:<br>- quadratic-only axis fit: 0.9856650955520649 m RMS; with the diurnal term: 7.8e-5 m;<br>- 1792 equations at 60 s sampling;<br>- data digest equal to GMAT's metadata, and the full fit reproduces `t0_gmat_results.json`;<br>- tolerance 1e-6 m, justified.<br>DR-0029 P6 names the quantity, frame, units, RMS definition, data, command, expected value and tolerance. Not a threshold; the DR-0028 ruling stays open | `check_review02.py` IM-1 checks (an independent fit; the provenance digest; the record wording) | Reproduced; for Review 03 |

**Not changed:**
- no approved physics, constant, frame, threshold, golden, reference or M1/M2 contract;
- no file outside `docs/`;
- DR-0029 P1–P10 and DR-0028 P6 (b) stay OPEN;
- the geodetic-drag discrepancy stays ESCALATED_FOR_INVESTIGATION.
