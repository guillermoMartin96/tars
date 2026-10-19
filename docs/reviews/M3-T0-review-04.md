# M3 T0 Review 04 (independent review of the R3-F1 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15584-ef03-73a3-9737-73cefea3c014`.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review04-prompt.md`.

**Reviewed commit:** **`44260efd29a4c3ff464542f88bccb46010201ec4`** (the validation record of the correction commit `489d4e7`).
- The review ran in a fresh clone with its own `uv sync --locked` environment and a private GMAT R2026a copy, whose console digest matches the installation.
- The prompt was kept outside the repository during the review. It reproduces the Tech Lead's authorization for this pass verbatim, and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim.
- **Prompt error (implementer's):** the prompt gave the pinned checkpoint as `44260ef3`, which is not a prefix of `44260efd…`. The reviewer reports that the lookup failed and that it identified the intended commit unambiguously from the branch and history (the clone's detached HEAD). It then generated the diffs against `HEAD`. The other identifiers in the prompt (`489d4e7`, `44260ef`) were correct.

**Authority:** "Authorization I-4: M3 T0 — R3-F1 Correction and Independent Review 04" (Tech Lead, 2026-10-19), §5–§6.

**Files:**
- prompt: `raw/M3-T0-codex-review04-prompt.md`;
- raw output: `raw/M3-T0-codex-review04.md`, the CLI's final message. It is identical to the reviewer's saved report `review_scratch/M3-T0-codex-review04.md` except for a trailing newline. Absolute paths are redacted to `<snap>`/`<scratch>`/`<home>`/`<tmp>`; the review itself contains none;
- reviewer scripts and logs: `raw/M3-T0-codex-review04-evidence/` (`*.py.txt`; `command-ledger.md`; `execution.json`; `SHA256SUMS`);
- the implementer's reproduction: `raw/M3-T0-codex-review04-evidence/implementer-reproduction/`.

**Omitted** as large or derivable: the reviewer's copies of the two diffs, its extracted `c6c0fff` tree, its rerun result JSON files (it reports them byte-identical to the committed ones), `m2.json` (the M2 validator output; `m2.log` is kept) and `__pycache__`.

**Verdict:** **REQUEST_CHANGES**, with one new MINOR finding.

**Stop rule applied (authorization §6):**
- The finding is recorded and was independently reproduced by the implementer.
- The complete output is preserved.
- **R4-F1 is not corrected, Review 05 is not started, and T0 is not accepted.** Authorization is requested.
- Not merged; T1 and T2 not started; DR-0029 P1–P10 and DR-0028 P6(b) not approved; branch protection and the M1/M2 baselines unchanged.

## Resolution assessed by Review 04
| Item | Review 04 | Basis (reviewer) |
|---|---|---|
| M3T0-R3-F1 | **PARTIALLY RESOLVED** | The 120/200/250 km cases and all 12 downward-jump cases are covered; the oracle is independent; the selection-height widening is present. The replacement global computed-force guarantee is invalid through R4-F1 |
| M3T0-R2-F1 | **RESOLVED** | Perturbed values are sampled estimates, not certified bounds; refinement between samples exceeds sampling; uses that need a perturbed bound remain blocked |
| M3T0-R2-F2 | **PARTIALLY RESOLVED** | The radius-product correction and the original 80 km counterexample pass; the global envelope used by the sufficient-condition proof fails through R4-F1 |
| M3T0-R2-F3 | **RESOLVED** | The reviewer's own zeroed-evidence mutant fails 22 selected checks; coverage, recomputation, units and provenance protections exist |
| IM-1 | **RESOLVED** | A byte-identical rerun reproduces 0.9856650955520649 m RMS; quantity, data, frames, units, 60 s sampling and the RMS procedure are documented; no threshold is approved |
| M3T0-F1 | **RESOLVED** | The chord/curvature argument holds; the two-body bound checks and the rerun pass; perturbed estimates are separated |
| M3T0-F2 | **PARTIALLY RESOLVED** | Thresholds, speed bound, the failing-stage example and same-tick semantics reproduce. The sufficient-condition proof depends on the defective global force enclosure |
| M3T0-F3 | **RESOLVED** | k2/k3/k4 offsets +116.312773 / −115.734153 / +1.161267 m; the records identify k3 |
| M3T0-F4 | **RESOLVED** | The GMAT rerun reproduces 6.95e-6 m, below the unchanged 1e-4 m gate |
| M3T0-F5 | **RESOLVED** | The owner's gate controls (P10 before T1, P1–P10 before T2); the dependency map is subordinate |

**The reviewer also reports:**
- **ε_h:** it re-derived the support-function, stationarity, H″ = −H − M, contraction and stopping-rule steps and found them sound. It found no counterexample to ε_h: 1 200 further log-height samples to about 1e9 m (with a separate latitude iteration that reuses the evidence script's decimal trigonometry) stay within 0.191 of ε_h. The committed figures rerun byte for byte (2.0564148063e-9 m, ratio 0.2166677265, 13 050 points). A-FP-2 is honestly labelled an unresolved platform assumption (cos 1.4132 ulp, 0.9361 × 2^-52 relative reproduced); the exp sample covers only −50 … 0.
- **Envelope (real-valued):** the selection allowance and the height-to-radius inequality are consistent; the in-band logarithmic derivative is negative for every scale height, so the candidate set (lower endpoint plus bases above, band-above rule) is proved for that expression. Its own 166 equatorial checks at every base and adjacent binary64 values pass.
- **Stage condition and floors:** the computed-height convention, the stage inequalities, M_k > 0 and the monotonicity are correct for the stated recurrence. The published bracket ends reproduce (124 456.68544510857, 118 633.50894662621, 111 511.96182508787 m), with needs about −7.17e-7, −1.00e-6 and −8.43e-7 m; the two-decimal floors and the P1 recommendation are unchanged. No stage below 0 m was observed at the published floors.
- **Oracle:** shares no height or band-selection implementation with `t0_model.py` (it imports constants, the table path and the digest helper). The remaining `min(low, true_h)` in `check_review02.py` accounts for a constructed point slightly below the requested limit and is not the former self-referential substitution.
- **Mutation:** the classification requires a declared detecting check. It reran 7 mutants and reproduced the supplied failure sets (÷10: 10 failures; ×0.9: 3; exact-base band: 34; combined: 33, where the reverted Review 02 test passes and Review 03 detects; wrong lower limit 25, model-height oracle 3, zeroed evidence 22 on declared subsets). The ×0.9 mutant protects agreement with the derivation, not a demonstrated behavioural failure; the records disclose this. The remaining 18 supplied mutant results are documentation evidence.
- **Its own runs:** checks 92/92; all nine T0 experiments, including GMAT and `t0_height_error.py`, reproduce the committed bytes (no tracked file changed); M1 validator PASS; M2 validator PASS (not `--quick`); GMAT M1/M2 compares pass; the five digests and the GMAT console and table digests match; VAL-0019's script and table digests match. Red-before on `c6c0fff` with the alias shim: the reviewer case and the 12 jump cases fail (13 failed, 29 deselected).
- **Scope:** only `docs/` changed since `86df2c3`; no production code, dependency, constant, table, frame, threshold, golden, reference, contract or M1/M2 validation semantics changed; DR-0029 P1–P10 and DR-0028 P6(b) remain open with no default; the geodetic-drag discrepancy stays escalated.
- **Not verified by the reviewer:**
  - the Proof wrapper runs (prohibited) and a fresh full pytest run;
  - CI (no network);
  - the full 25-mutant matrix (7 rerun);
  - the second fresh-clone reproduction;
  - other platforms, a global libm theorem, branch protection and the external source provenance;
  - the cause of the escalated geodetic-drag discrepancy.

## New finding
| ID | Severity | Finding (reviewer) | Implementer's independent reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R4-F1 | MINOR | The floating-point drag enclosure drops underflow errors that violate its bound (`t0_termination.py:446–457` arithmetic/domain assumptions, `:567–571` density/drag factors, `:640–675` global envelope; `t0_model.py:118`, `:288`; repeated in DR-0029 P1/P4, VAL-0019, the T0 report, the decision matrix and the Review 03 correction section). Round-to-nearest does not give fl(x op y) = (x op y)(1 + δ), \|δ\| ≤ u, for subnormal results, and the derivation discards their absolute errors. The declared domain excludes overflow but not underflow, and has no upper height. Counterexample: r = [197059137.0, 0, 0] m, v = 0, V1 (850 kg, Cd 2.2, 15 m²), J2 + drag, L = 190 681 000 m (exact true height, equal to the computed height), s = 0, a bound state. The computed density is 1.3e-322 against exact 1.263e-322 kg/m³; model drag 1.0202e-315 against `drag_envelope` 5.0632e-316 m/s², ratio 2.0150. exp itself is normal and within A-FP-2. The reviewer states that this disproves the global envelope lemma but does **not** show an RK4 stage below 0 m at a published floor, or that those floors must change | **VERIFIED** with the independent oracle (`implementer-reproduction/repro_r4.py.txt`, `.log`): at 190 681 km the model's drag is 2.0150× both `t0_oracle.drag` and the envelope. At 15 000, 100 000 and 183 320 km the ratio is 1 within 1.3e-12. The oracle density in the top band (base 1000 km, 3.019e-15 kg/m³, scale 268 km) becomes subnormal above 181 889 968 m, so the violated region is above that height. The committed 92 checks pass, so none of them covers the region.<br>**Root cause:** assumption A-FP-1 was used as an unconditional relative-error model, but it fails once results become subnormal, and the stated domain does not exclude subnormal results. The envelope tends to zero with the density, so an absolute underflow error, however small, is not negligible relative to it | **ACCEPTED**; not applied |

**Implementer's preliminary observation (not a disposition and not reviewed):** the stage condition evaluates the envelope as a supremum over true heights ≥ L_k with L_k near the floors (about 120 km), where the envelope is of order 1e-2 m/s² and is attained at low candidates. A computed drag of order 1e-315 m/s² at subnormal heights cannot exceed it. This suggests, but does not prove, that the published floors are unaffected and that only the general envelope lemma and its stated domain are wrong. Establishing this, or a corrected enclosure, is correction work for a future authorization.

## Proposed correction (for authorization; none applied)
1. **State the arithmetic model correctly.** A-FP-1 gives fl(x op y) = (x op y)(1 + δ) + η with \|δ\| ≤ u and \|η\| ≤ 2^-1075 (η = 0 for + and −, and for results in the normal range). The derivation should use this mixed model, or show that no result in its domain is subnormal.
2. **Either** carry absolute underflow terms through the density and drag factors (E2–E3) into a conservative envelope, then rejustify the supremum and the stage argument over the existing domain; **or** prove that the stage condition uses only envelopes at L ≤ some explicit height where no underflow occurs, and restrict the *stated lemma* (not the model, the table or the physics) to that range, with the restriction disclosed. Do not narrow the domain silently. If neither can be established rigorously, withdraw the affected guarantee and keep it blocked.
3. **Add regressions:** the reviewer's point, a scan of the top band across the subnormal onset, with high-precision or component-wise norms; and a mutant that removes the underflow term.
4. **Update** DR-0029 P1/P4, VAL-0019, the T0 report, the decision matrix and the Review 03 correction section; recompute the floors and state whether they change.
5. **Keep everything else fixed:** the pinned table, the approved physics and constants, and the M1/M2 baselines.
6. **Afterwards:** rerun everything, the Proof, the digests and CI, then any Review 05, which needs authorization.

## Lessons (proposed, not yet codified)
- A relative-error rounding model is a theorem only in the normal range. A derivation that states "IEEE binary64, round to nearest" as its assumption must carry the underflow term or show it cannot occur.
- A stated domain must be checked at its extremes, not only where the guarantee is used: "exterior points; no overflow" silently included heights where the force underflows.
- Pin every identifier in a review prompt by its full hash. A mistyped short hash cost the reviewer a failed lookup; the full SHA was available.

## Correction pass (Authorization I-5, 2026-10-19)
**Authority:** "Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05" (Tech Lead), §2–§6. The scope is R4-F1 only. T0 remains BLOCKED. DR-0029 P1–P10 and DR-0028 P6(b) stay OPEN, and the GMAT geodetic-drag discrepancy stays ESCALATED_FOR_INVESTIGATION. The finding above and the reviewer's language are preserved unchanged. The superseded state is `c15fbd4`.

**Approach selected: A (underflow-aware bound).** Approach B (a restricted altitude domain) would still need a bound on the computed force in the subnormal regime: a committed state may lie at any height above the floor, and the envelope is a supremum over all heights above its lower limit. Approach A was therefore both preferable and necessary. It produced a defensible bound without restricting the domain, so Approach C (withdrawal) was not needed.

| ID | Disposition | Correction |
|---|---|---|
| M3T0-R4-F1 | **ACCEPTED; CORRECTED** (for Review 05 to assess) | The rounding model is now mixed absolute and relative, with gradual underflow (A-FP-1 to A-FP-3, restated). E1–E6 carry the absolute error of every underflowing operation. The envelope gains an absolute part, bounded over every selection height at which the computed density can be nonzero (up to h_zero, above which it is exactly 0). The three floors are unchanged to the last bit. `drag_envelope_relative_only` keeps the superseded envelope to reproduce the finding |
| IM-2 (implementer, found in this pass) | **ACCEPTED; recorded, no floor changed** | DR-0029 quotes the floors to the nearest centimetre. The drag-free bound 111 511.96182508787 m therefore appears as 111 511.96 m, which is 1.8 mm below it and does not itself satisfy the condition (`check_review04.py`, 2-decimal test). DR-0029 now states that the governing values are the bracket ends, and that 111 511.97 m is a sufficient 2-decimal value. No reviewer had flagged this. How bounds are quoted in a decision is the owner's choice |

### Mathematical justification
- **Arithmetic model (A-FP-1, from IEEE 754 with gradual underflow).**
  - With u = 2^-53 and η₀ = 2^-1075: fl(x × y) and fl(x ÷ y) equal (x op y)(1 + δ) + η, with |δ| ≤ u, |η| ≤ η₀ and δη = 0.
  - fl(x ± y) = (x ± y)(1 + δ): a sum that underflows is exact.
  - fl(√x) = √x(1 + δ): a square root is never subnormal.
  - Multiplying by 0.5 is exact unless the result is subnormal.
  - Any result of magnitude ≤ η₀ rounds to 0.
- **Library model (A-FP-2).** |f̂ − f| ≤ UF·|f| + ν, with UF = LIBM_ULP·2^-52 and ν = LIBM_ULP·2^-1074. This is the "within LIBM_ULP ulps" statement written in absolute form for subnormal results. No relative tolerance is assumed for subnormal outputs, including exp rounding to 0.
- **E1, E2 (height and kilometre conversion).** p, sin and atan2 may be subnormal near the axis or the equator, and p·c, z·s, e2·s·s and e2·N·s may underflow.
  - Their absolute errors enter the per-step latitude error through the vector (p, z + e2 N s), whose norm is ≥ b − Q, plus ν for atan2.
  - They enter the final formula as (1 + u)³ν(|r| + 1 + UF) + 2(1 + u)²η₀ + a(1 + u)⁶(3e2(1 + UF)ν + 2η₀)/(2√(1 − e²)(1 − ρ₃)).
  - The kilometre division may underflow, adding 1000η₀ to β_sel.
  - α gains about 1e-323 and β about 1e-316 m. ε_h is unchanged in binary64.
- **E3 (density).**
  - The exponent's division may underflow, contributing e^{η₀}. The exp result has the absolute term ν, and the product with ρ₀ has η₀.
  - ρ̂ ≤ F_ρ e^{η₀} ρ(h_s) e^{θ_x X} + N_ρ, with N_ρ = (1 + u)²ρ₀,max·ν + η₀ ≤ 2.95 × 2^-1074.
  - **Zero-density height.** In the top band, once (1 + u)ρ₀((1 + UF)e^{η₀}e^{−(1−θ_x)X} + ν) < η₀ the product rounds to 0. That holds above the selection height h_zero = 191 735 430.72 m, bounded outward in 60-digit decimals; it is 9.5e-8 m above the oracle's exact onset. There ρ̂ = 0, every later product is 0, and the force is exactly 0.
- **E4 (drag).** The model computes the coefficient k = fl(fl(fl(fl(0.5ρ̂)·cd)·area)/mass). Each of these may underflow.
  - k ≤ (1 + u)³(cd·area/mass)·0.5ρ̂ + W, with W ≤ η₀(1 + φ_B/B·((1 + u)³ + (1 + u)²/cd + (1 + u)/(cd·area))) ≈ 1.06η₀ for V1. The leading 1 is the last division: the R4-F1 mechanism, where 0.51 × 2^-1074 rounds up to 2^-1074.
  - The vector v_rel gains √2(1 + u)η₀, the dot product 3(1 + u)²η₀, and each of the two products with v_rel η₀.
  - With S = |v| + ω|r| ≥ ωb, the relative factors gain at most (1 + τ), with τ ≈ 1e-327.
  - Result: |d̂| ≤ F_D′ρ(h_s)e^{θ_x X}S²/(2B) + (F_A N_ρ/(2B) + K_W W)S² + K_1η₀S + 2η₀.
  - The absolute part is maximised at S_max = s + ω_E(a + (h_zero + β_sel)/(1 − α_sel)), because a nonzero force needs h_s ≤ h_zero. The relative part keeps the in-band monotonicity and the candidate set of Review 03.
- **E5, E6 (gravity and RK4 stages).**
  - The three products of the gravity vector and the J2 products 5zz, x(1 − zz) and k(·) underflow by at most (1 + 2.1|k||r|)η₀ ≤ 1.05η₀ per component, giving G^ + 4η₀.
  - Each stage product c·k and 5a adds (1 + u)√3η₀ ≤ 2η₀ to the stage bounds.
- **Monotonicity in h0** is unchanged: the new absolute terms do not depend on h0, and the envelope's absolute part is constant in its lower limit and increasing in its speed.

### Effect on P1
- **Floors.** The three published floors (bracket ends) are unchanged to the last bit: 124 456.68544510857, 118 633.50894662621 and 111 511.96182508787 m. Bracketed to 1e-9 m, the roots coincide before and after the correction (`floor_comparison`). The margins at the floors are 7.2e-7, 1.0e-6 and 8.4e-7 m, and the stage conditions M2, M3, M4 > 0 hold at the floors.
- **Why they cannot move.** The absolute part is about 1e-315 m/s², against G^ ≈ 9.9 m/s².
- **Recommendation.** The P1 recommendation is unchanged.

### A-FP-2 status
- **Required.** No bound on the height, density or force exists without some accuracy statement for sin, cos, atan2, hypot, exp and pow, and no verified library is in the locked environment.
- **Weakened (`libm_sensitivity`, derived).** Every constant is non-decreasing in LIBM_ULP:
  - the published bracket ends hold for every libm within 2^5 (B 25.8), 2^6 (B 100) and 2^7 (drag-free) ulps;
  - the 2-decimal values rounded up hold within 2^19, 2^17 and 2^20 ulps.
- **Remains conditional.**
  - It is measured on macOS x86_64 only. For subnormal results the absolute errors are at most 0.74 × 2^-1074 (exp).
  - [source] The glibc manual (sourceware.org, "Errors in Math Functions", read 2026-10-19) states that the library "does not aim for correctly rounded results" and aims for "a few ulp". Its testsuite flags only errors above 9 ulp. That is documentation of intent, not a bound, but 9 ulp is within the 2^5 = 32 ulp that the published bracket ends tolerate.
  - No Apple libm accuracy statement was found.
  - CI does not collect the T0 checks, so neither the libm measurement nor the gradual-underflow probe has run on the CI platforms.

### Evidence classification
| Class | Items |
|---|---|
| **Proved (exact arithmetic)** | Everything in Review 03's row (unchanged). Also: rounding to 0 at or below η₀ makes the force exactly 0 above h_zero; the absolute part is non-decreasing in |r| and attained at S_max; the new terms do not change the monotonicity in h0 |
| **Derived under A-FP-1 … A-FP-3 (mixed model)** | ε_h and ε_sel with their underflow parts; N_ρ, W, τ, F_A, K_W, K_1; h_zero; the corrected envelope; G^ + 4η₀ and the stage terms; the three floors (unchanged); the libm sensitivity |
| **Numerically verified** (independent oracle, not a proof) | The R4-F1 point and the transition scan are covered by the corrected envelope and exceed every purely relative enclosure. So are the binary64 neighbours of the smallest-normal, coefficient-rounding and zero boundaries. Above h_zero, density and drag are exactly 0. Every band base and the lower edge are covered. High-altitude RK4 stages stay within their bounds. A second implementation reproduces the constants, the envelope, the floors and the sensitivity (`check_review04.py`) |
| **Empirical observations** | The largest observed ratio of model drag to envelope in the subnormal regime is 0.983 (B 100, at the coefficient's rounding height). A random search of 5 287 points found no violation of the corrected envelope and 161 of the superseded one. The libm subnormal-result maxima on this host are exp 0.74, hypot 0.59 and atan2 0.50 × 2^-1074 |
| **Unresolved assumptions** | **A-FP-2** (now ≤ 2 ulps relative plus 2 × 2^-1074 absolute; sufficient up to 2^5 ulps for the published bracket ends), measured on macOS x86_64 only. **A-FP-1's gradual underflow** and **A-FP-3**: standard, probed at run time on the host only |
| **Owner decisions still required** | DR-0029 P1–P10, including κ and v̂ for P1; whether a guarantee conditional on A-FP-2 is acceptable; how bounds are quoted (IM-2). DR-0028 P6(b). The escalated GMAT geodetic-drag discrepancy |

### Validation of the correction commit `a1feb79` (appended 2026-10-19)
Evidence is in `docs/reviews/raw/M3-T0-review05-correction-evidence/`; scratch, home and temporary paths are redacted. Environment: macOS 26.2 x86_64 (the M1/M2 reference host), Python 3.12.15, the locked `uv` environment.

| Check | Result |
|---|---|
| Full existing T0 regression suite and new R4-F1 checks | `check_review01.py` … `check_review04.py`: 140/140 pass (`checks_after.log`). Red before, at `c15fbd4` with the documented shim: `check_review04.py` 17 of 48 fail (`checks04_before_c15fbd4.log`) |
| Independent high-precision comparisons | All expected values in `check_review04.py` come from `t0_oracle.py` (60-digit decimals) and a second implementation in exact rationals; part of the 140 above |
| Mutation tests | `mutation_check_review02.py`: the control passes 140/140; 34/34 corruptions detected by a declared check; 1 declared equivalent; about 24 min (`mutation_check_review04.json`). Run on the tree before the last record edits; no script changed after it |
| M1 Proof (`run_m1_proof.sh`, fresh clone at `a1feb79`) | PASS, 9/9 steps; `working_tree_clean_excluding_evidence: yes` (`m1_proof_run.log`). A separate full pytest run in the same clone after the Proof: 1185 passed, 3 warnings (`pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Five pinned digests | All match (`pinned_digests.log`) |
| Production and protected files | `git diff --name-only 86df2c3 a1feb79 -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty |
| T0 reproducibility | A third fresh clone ran every T0 experiment twice, including the GMAT harness, `t0_height_error.py` and `t0_axis_ablation.py`. `git status` is empty after each run, so all 94 tracked experiment files are byte-identical; the checks then pass 140/140 (`reproducibility_twice.log`) |
| CI on `a1feb79` | Run 39325494494 (https://github.com/guillermoMartin96/tars/actions/runs/39325494494): all four jobs succeeded (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`), verified via the GitHub API after completion. CI does not collect the T0 checks (`testpaths = ["tests"]`) |
