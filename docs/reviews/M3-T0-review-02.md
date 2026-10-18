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
