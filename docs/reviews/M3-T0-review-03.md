# M3 T0 Review 03 (independent review of the Review 02 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a152bd-789d-72e3-bf3f-624b5deaaed0`.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review03-prompt.md`.

**Reviewed commit:** **`51e110bf1981f9761042f5cf0e87c9f0c7c1962e`** (the validation record of the correction commit `14d98f0`).
- The review ran in a fresh clone with its own `uv sync --locked` environment and a private GMAT R2026a copy, whose console digest matches the installation.
- The prompt was kept outside the repository during the review. It reproduces the Tech Lead's authorization for this pass verbatim, and points to the earlier prompts, which hold the I-15 texts and the Review 01 correction authorization verbatim.

**Authority:** "Authorization: M3 T0 — Review 02 Corrections and Independent Review 03" (Tech Lead, 2026-10-18), §8–§9.

**Files:**
- prompt: `raw/M3-T0-codex-review03-prompt.md`;
- raw output: `raw/M3-T0-codex-review03.md`, the reviewer's saved report. It is identical to the CLI's final message except for a trailing newline, and absolute scratch paths are redacted to `<snap>`/`<scratch>`;
- reviewer scripts and logs: `raw/M3-T0-codex-review03-evidence/` (`*.py.txt`; `SHA256SUMS`);
- the implementer's reproduction: `raw/M3-T0-codex-review03-evidence/implementer-reproduction/`.

**Omitted** as large or derivable: the reviewer's copies of the diffs, the extracted `5548d11` and `bdcaacf` trees, the rerun result JSON files (the reviewer reports they are byte-identical to the committed ones) and its copies of the records.

**Verdict:** **REQUEST_CHANGES**, with one new MINOR finding.

**Stop rule applied (authorization §9):**
- The finding is recorded and was independently reproduced by the implementer.
- The complete output is preserved.
- **R3-F1 is not corrected, Review 04 is not started, and T0 is not accepted.** Authorization is requested.

## Resolution assessed by Review 03
| Item | Review 03 | Basis (reviewer) |
|---|---|---|
| M3T0-R2-F1 | **RESOLVED** | Perturbed rows carry sampled estimates without `bound_m`; the cubic is correct; refinement exceeds sampling; the records disclaim a perturbed bound and block uses that need one |
| M3T0-R2-F2 | **PARTIALLY RESOLVED** | The real-arithmetic envelope, the per-band derivative and the monotonicity in h0 are correct, and the original counterexample is covered. Floating-point height evaluation is not covered (R3-F1) |
| M3T0-R2-F3 | **RESOLVED** | The zeroed sweep and floors are detected; recomputation, coverage, units, provenance and mutation checks protect those quantities. The boundary-testing weakness is part of R3-F1 |
| IM-1 | **RESOLVED** | The rerun is byte-identical; an independent QR fit gives 0.98566509553 m RMS; the data digest, frames, units, 1792 equations, 60 s sampling and RMS definition agree. It is evidence, not a threshold |
| M3T0-F1 | **RESOLVED** | Theorem retained, two-body bound verified, perturbed estimates separated |
| M3T0-F2 | **PARTIALLY RESOLVED** | Thresholds, speed bound, counterexamples and same-tick semantics reproduce. The sufficient-domain argument lacks the numerical-height coverage of R3-F1 |
| M3T0-F3 | **RESOLVED** | k2/k3/k4 offsets +116.312773 / −115.734153 / +1.161267 m |
| M3T0-F4 | **RESOLVED** | GMAT rerun reproduces 6.95223445873689e-6 m |
| M3T0-F5 | **RESOLVED** | The owner's gate controls; the dependency map is subordinate |

**The reviewer also reports:**
- Its own runs: checks 50/50; mutation harness reproduced (15 detected, 1 equivalent, the control passing); full pytest 1185 passed; M1 validator PASS; M2 validator PASS 228/228; GMAT M1/M2 compares pass. All T0 experiments, including the GMAT harness, reproduce the committed bytes; the five digests match; protected paths are clean.
- **A proof of the declared equivalent mutant.** Dividing the cubic by s r² gives F(r) = r/s + 2K − 4 + (2 − 4K)c/r + 2Kc²/r². F′ > 0 for r > 4Kc/(4K − 2) ≈ 85 396 m, far below a, so every stationary point of g is a minimum and no interior maximum can beat the endpoints. The implementer had recorded only a domain scan. This proof supports the classification; the reviewer notes that the scan alone does not establish it.
- **Not verified by the reviewer:**
  - the Proof wrapper runs (prohibited);
  - CI (no network);
  - branch protection;
  - other platforms and BLAS builds;
  - the printed atmosphere-source provenance;
  - the cause of the escalated geodetic-drag discrepancy.

## New finding
| ID | Severity | Finding (reviewer) | Implementer's independent reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R3-F1 | MINOR | The drag-envelope guarantee omits numerical height error at density discontinuities (`t0_termination.py:439–463, 549–583`; `check_review02.py:430–439`; DR-0029 P1 lines 81–88; VAL-0019 and the Review 02 dispositions repeat it). The derivation bounds exact geodetic height, but the force evaluates density at the numerically recovered height. A tiny downward error can cross a downward density jump. Counterexample: r = [5420209.728043159, 3584286.6758661848, 1.8499824933775928] m, v = [6067.454938935459, −9175.29239664793, 0] m/s, L = 120 000 m, s = 11 000 m/s, B 25.76. True height (80 digits) 120 000.0000000000233 m; model height 119 999.99999999907 m; envelope 0.06230417914238045, model drag 0.06230901450414247 m/s². Similar cases at 50, 90, 110, 140, 200 and 250 km. The committed adversarial check takes `min(low, h_model)`, which widens the envelope and hides the case. No RK4 stage below 0 m is shown at the published floors | **VERIFIED** with 60-digit decimal arithmetic and an independent foot-point method (Newton on the Lagrange parameter, square roots only; `implementer-reproduction/repro_r3.py.txt`, `.log`): true height 120 000.0000000000233 m, model height 119 999.99999999907 m, excess 4.835e-6 m/s² (7.76e-5 relative). An independent search on points constructed at every downward jump finds violations at the 200 km and 250 km bases (relative excess up to 1.5e-5). The table has 12 downward jumps (50, 90, 110, 120, 140, 200, 250, 450, 600, 700, 900, 1000 km).<br>**Root cause:** the derivation treats "height" as exact geometry, but the implemented force is a function of the computed height, and the density is discontinuous in it. The implementer's own check then evaluated the envelope at the computed height, `min(low, h_model)`, which is the defect itself rather than a test of it | **ACCEPTED**; not applied |

## Proposed correction (for authorization; none applied)
1. **State the distinction.** In the derivation, separate exact geometric height from the model's computed height, and state the guarantee for the implemented force.
2. **Derive and justify an enclosure** |h_model − h_true| ≤ ε_h over the supported domain (the geodetic iteration's convergence and rounding error). Use evidence such as the high-precision comparison above; do not use an arbitrary multiplier.
3. **Widen the envelope's lower limit** to L − ε_h, so that a band reachable through that error is included. Propagate this through `stage_lower_heights` and the fail-closed edge at 0 m, then recompute the floors.
4. **Add checks** with exact-base, downward-jump points that keep the original lower bound and use high-precision true heights. Remove the `min(low, h_model)` substitution. Add mutants for both.
5. **Keep everything else fixed:** the pinned table, the supported domain and the approved physics.
6. **Afterwards:** rerun everything, the Proof, the digests and CI, then Review 04, which needs authorization.

## Lessons (proposed, not yet codified)
- When a model input is discontinuous (here density in height), a bound proved for exact arguments does not bound the implemented function. The error in the computed argument must be enclosed and crossed explicitly.
- A test that adapts its expected bound to the implementation's internal value (`min(low, h_model)`) tests the implementation against itself. Expected values must come from the stated assumptions.
- An equivalence classification should rest on a proof where one is available; a domain scan is supporting evidence only.
