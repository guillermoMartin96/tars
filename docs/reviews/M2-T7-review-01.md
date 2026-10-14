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
See below.
