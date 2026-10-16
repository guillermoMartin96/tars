# M3 planning checkpoint — independent review 05

**Scope:** the corrections authorized by the Tech Lead's instruction "M3 Planning — Review 04 Corrections and Final Verification" (I-4), in commit `b411b5f`. They cover:
- the M3P4-F1 correction (pole tilt and ascending node);
- the M3P4-F2 correction (local solar time);
- a readiness assessment of the whole planning package.

No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a145bc-4dcb-7420-9e2c-65fd0be536c5`, run at `1c53d0e` on a git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review05-prompt.md`. It carries I-1 §1–8, I-2 §1–7, I-3 §1–8 and I-4 §1–7 verbatim, plus the full review history, and instructs independent verification.
- Raw output: `raw/M3-planning-codex-review05.md`.

**Instruction for this outcome (I-4 §5):** "If Codex returns REQUEST_CHANGES: Record every finding and its severity. Do not implement further corrections. Do not run another review. Stop for my authorization."
- **The finding below has not been applied.**
- No further review has been run.
- The planning branch is not merged, T0 has not begun, and M3 planning is not accepted.

## Verdict
**REQUEST_CHANGES:** one MINOR finding, with no BLOCKER or MAJOR finding. It concerns the signs of two first-order formulas in DR-0028 "Resolution amendment 1", item 1. It does not concern any decision, bound, magnitude, constant or historical record.

**The reviewer confirmed independently:**
- **Node geometry:**
  - the exact bound |Δi| ≤ δ;
  - the first-order magnitudes δ|sin(Ω−φ)|/sin i (node point) and δ|cot i sin(Ω−φ)| (node longitude);
  - the envelopes, conditioning limits, dimensions and dependence on the longitude origin.
- **Review-04 example:** reproduced as 90.259805543688°, with node-point shift 0.299997943861° and Δi 0.000340085438°.
- **Near-equatorial values:** reproduced. The script's output JSON is byte-identical on rerun.
- **Solar time:** the cancellation of θ is verified, and the McKinley §II definition was retrieved and confirmed. The missing ephemeris, time connection and mean-Sun convention are correctly identified. The prohibitions are intact.
- **History and regressions:**
  - all four earlier review records are preserved, with all findings and dispositions;
  - the withdrawn Q4 quotation is still 558 bytes and byte-exact;
  - the registers are additions only (218/0 and 43/0).
- **Atmosphere:** 27 boundary jumps within 1.11e-16; the residual script's output is byte-identical on rerun.
- **Scope:**
  - 47 files changed, all under `docs/`;
  - the only removed lines since `16b6888` are three index/status lines;
  - J-ax-1, the identity transformation, co-rotation, FC-1…FC-10, the constants, the retention rule and the deferred items are intact.
- **Local checks:** M1 Proof 7/7, M2 Proof 228/228, golden comparison zero, GMAT comparisons, Ruff.
- **Not verified by the reviewer:** full pytest, and remote CI (no network).

## Dispositions (recorded; not applied)
**M3P5-F1** (MINOR, mathematical consistency)

**Finding.** In DR-0028 "Resolution amendment 1", item 1, the signed estimates Δi ≈ δ cos(Ω − φ) and ΔΩ ≈ −δ cot i sin(Ω − φ) have reversed signs for the stated convention. That convention is a passive R = Rot(e, −δ), with changes taken as B minus A. With that convention, h_B = h_A − δ e × h_A, so Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ).

The preserved review-04 example shows the contradiction: its computed ΔΩ is +0.2598°, but the printed formula gives −0.2598°. The script takes absolute values, so its sweeps cannot detect sign errors.

**Disposition: ACCEPTED.** The implementer verified the finding independently, with i = 30°, φ = 0, δ = 0.15° and R = Rx(−δ):

| Ω | Computed Δi (B − A) | Printed Δi | Computed ΔΩ | Printed ΔΩ |
|---|---|---|---|---|
| 0° | −0.150000000° | +0.150000000° | — | — |
| 90° | — | — | +0.259805544° | −0.259807621° |

- The derivation in the amendment used +δ e × h, which is the active sense, while the amendment and the script state the passive convention.
- All magnitudes, bounds and envelopes are unaffected, and so are SCI-0013 status update 3 and the DR-0024 log entry, which state magnitudes only.

**Proposed change (not made):**
- Append a linked correction to DR-0028 amendment 1 that defines Δ as B minus A for the passive convention and gives the corrected signs. Keep the original formulas, with a pointer to the correction.
- Add signed known-answer comparisons, for example Ω = 0° and Ω = 90°, to `dr0028_node_sensitivity.py` and its results.

## Validation evidence at the reviewed commits (implementer)
- **`b411b5f`**, isolated clone:
  - full pytest: 1185 passed, exit 0;
  - M1 Proof: overall PASS, exit 0;
  - M2 Proof: overall PASS, 21 steps exit 0.
  - Regenerated Proof evidence differed only in run metadata (revision, tree_clean, record sha256, temporary paths, uv messages).
- **Documentation checks:** docs-only scope against `d92ab89`; relative-link check, 0 broken; Ruff format and lint pass; the node script's output is byte-identical on rerun; constants and digests unchanged.
- **CI:** the run for the final commit is listed in the checkpoint report.

## Status after this review
- This is not an unconditional PASS, so the I-4 §5 stop condition applies.
- **No acceptance report has been prepared.** The branch is not ready for acceptance, it is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** authorization to correct M3P5-F1, and whether to run another review.
