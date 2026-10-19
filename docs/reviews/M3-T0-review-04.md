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
