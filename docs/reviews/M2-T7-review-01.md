# Review M2-T7-01 — three-platform measurement and threshold decision preparation

**Scope:** T7 deliverables: `toolbox/scripts/m2_t7_measure.py`, `.github/workflows/m2-t7-measure.yml`, `proof/records/evidence/M2-T7/`, VAL-0016, DR-0023, and the T7 status records. T7 is measurement and decision preparation only: no threshold, reference value, snapshot tolerance or check may change.

## Round 1
**Reviewer:** Codex, session `01a137f0-3406-73c0-a625-fe96feacc08e`, at `843ba09`. **Raw:** `raw/M2-T7-codex-review01.md`, `raw/M2-T7-codex-review01-scratch/`.

**Verdict: REQUEST_CHANGES.** The reviewer confirmed:
- every proposed value is supported;
- the analyzer output matches the committed `analysis.json`;
- the worst cases, spreads, margins, final-state drift and reference variation all recompute independently;
- the digests match;
- the platforms are the DR-0008 matrix with no substitution;
- nothing in scope changed.

The findings concern the stated rationale and some reported figures.

**All six are `ACCEPTED` and corrected. No proposed value changed.**

| # | Sev. | Finding | Correction |
|---|---|---|---|
| T7-F1 | Med | DR-0023 treated the 4.66 µm GMAT–DOP853 disagreement as a reference-error bound and called it "not noise", conflating reproducibility with accuracy | Described as the disagreement between the committed GMAT rows and the **approved DOP853 baseline**. It is platform-independent because both sides are pinned. Zero spread shows reproducibility, not accuracy. Agreement of two numerical references does not bound either one's absolute error (DR-0023 error budget and FU-1; VAL-0016) |
| T7-F2 | Low | The FU-1 re-baselining bound added a coordinate maximum (8.10 µm) to a Euclidean residual | The analyzer now also reports **Euclidean drift** for 3-vectors (`max_vector_norm_*`). The raw reference drifts 8.62 µm. The bound is 2 × (4.66 + 8.62) ≈ 26.6 µm, and the recommended 30 µm keeps headroom. While adding this I found and fixed a bug: values are stored flattened, so the norm was first computed only for single-vector parts. The shape is now restored before norms are taken |
| T7-F3 | Med | The stated detection guarantees ignored the existing residual's direction | Guaranteed detection is above limit + residual: 34.7 µm for the 30 µm gate, 14.7 µm for the 10 µm option. Detection in a favourable direction starts at 25.3 µm and 5.3 µm |
| T7-F4 | Low | 0.0405 was labelled a "shift", and the printed sum mixed missions | Per mission, worst over the 11 bundles (macOS arm64): prograde 0.004102 + 0.035602 = 0.039703; retrograde 0.003851 + 0.036642 = **0.040493**. Option (b): 0.004172 and 0.003923. VAL-0015's arithmetic line is corrected too |
| T7-F5 | Low | VAL-0016 claimed zero spread for every round-off metric; the O9 boundary-position spread was understated; the simulator-vs-GMAT spread was mis-attributed | Round-off metrics vary by at most 3.3e-16. O9 boundary position spread is 5.2e-10 m (6.4e-9 m for invalid-commands) and velocity ≤ 9.4e-12 m/s. Simulator vs GMAT is 7.2e-6 m. The 1.1e-5 m spread belongs to O4 and O5 |
| T7-F6 | Low | Determinism coverage overstated as "all six M2 scenario files" | Cross-process for the **four** M2 scenario files and M1, and in process for all six missions (the Proof). VAL-0016 and the Proof record are corrected |

`analysis.json` was regenerated with the corrected analyzer, from the same 11 bundles.

## Round 2
**Reviewer:** Codex, session `01a1380d-c632-74f0-aa96-0fe350a30cbe`, at `8fe709f`. **Raw:** `raw/M2-T7-codex-review02.md`.

**Verdict: PASS (unconditional; no new findings).**
- T7-F1 to T7-F6 are resolved. The corrected figures match the evidence: Euclidean reference drift 8.619305 µm, the detection bounds, the spreads and the determinism coverage.
- The analyzer's restored shapes and vector norms are correct.
- Independently recomputed: the worst cases, spreads, margins, final-state drift, reference variation and O6 bounds (maximum combined bound 0.040492872 < 0.05). The regenerated `analysis.json` matches the committed file.
- Digests and provenance match the DR-0008 matrix with no substitution. Reference reproducibility is distinguished from accuracy. The FU-1, O6 and unchanged-threshold proposals are supported.
- Nothing in scope changed: `m2.json` stays provisional and no T8 work appears.
- 1,101 tests, Ruff, the M2 Proof (215/215), the M1 Proof and the GMAT comparison all pass.

**T7 review closed: PASS.** CI is green on Ubuntu and macOS (run 38496630761). **T7 now stops at the DR-0023 threshold decision gate.**

## Round 3 — DR-0023 application and the cross-platform final-state gate
**Reviewer:** Codex, session `01a13c44-15f2-7d11-a381-f5b3d8bf52b0`, at `fbdbe77` (a git clone, with metadata). **Raw:** `raw/M2-T7-codex-review03.md`. **Prompt:** `raw/M2-T7-codex-review03-prompt.md`.

**Verdict: REQUEST_CHANGES (one High finding).**

Verified as correct:
- every pre-existing `m2.json` limit is unchanged, and the pin matches;
- the FU-1 and O6 text meets the DR-0023 conditions;
- all 215 earlier M2 checks are present with identical metrics and thresholds, plus 13 additions;
- the M1 golden, the snapshot and GMAT pins, and the CI steps are unchanged;
- the VAL-0017 figures recompute exactly, including 7.232054622489096e-6 m and 8.428690417483863e-9 m/s;
- the archive digests and the golden's byte identity hold;
- the Euclidean norm and inclusive boundaries are correct;
- 1,174 tests pass;
- mutating missing-platform detection, Rosetta rejection, input matching or the Euclidean norm makes tests fail.

On platform coverage, the reviewer found that the GitHub Intel runner satisfies the OS/architecture matrix and that the pinned golden preserves the reference-host baseline. Requiring the local host to run every revision would be a Tech Lead decision.

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| T7-F7 | High | The gate never cross-checked the declared OS against independent OS provenance. A Linux record relabelled `Darwin`/`macos-x86_64`, with its checksum recomputed, filled the macOS x86_64 slot. The gate passed with no macOS x86_64 evidence. This is bad workflow data, inside the DR-0019 B scope, and it changes an acceptance decision | **ACCEPTED, fixed.** `record_problems` now requires two independent OS signals to agree with the declared platform: (1) `ci.runner_os` (GitHub `Linux`/`macOS`) must map to `platform.system`, and a missing or unknown value fails; (2) `environment.os` (`platform.platform()`) must start with `Linux-`/`macOS-` for the declared system and name the declared machine as a token, so CI-less records are covered too. New regressions cover the reviewer's exact reproduction (archived Linux record relabelled, with and without CI provenance, library and CLI), contradictory or missing runner OS and environment OS (eight cases), and consistent provenance in all four archived records. Mutation check: disabling either new check makes five regressions fail. No threshold, contract or scope change |

**Also fixed (found in CI, not by the reviewer):** `test_proof_fails_closed_on_an_unusable_or_disagreeing_golden[perturbed]` expected exactly 1.5e-4 m. On Linux the run differs from the macOS x86_64 golden by its genuine platform drift, so the value was 1.5068e-4 m. The assertion now allows 1e-5 m (measured drift ≤ 7.3e-6 m). The gate itself was right; only the test was too strict.
