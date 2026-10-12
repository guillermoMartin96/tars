### F49 — Unchecked Kepler tick outputs can reverse O9 acceptance

**Severity:** Medium

**Claim:** `_anchor_segment` checks the coast segment-end Kepler result, but separately evaluated tick states lack independent reconciliation. Corrupted time-of-flight outputs preserve energy, angular momentum and the correlated round trip while changing consumed radii.

Blocking under **DR-0019 B** because invalid independent-reference data passes through unchanged validator helpers, and **DR-0020 A** because it changes `orbit_events[m2_prograde_burn].max_altitude_error_m` and reverses O9 acceptance.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/anchor_phase.py
PYTHONPATH=src .venv/bin/python review_scratch/anchor_acceptance.py
```

The probes corrupt only independent Kepler return data for coast tick-radius calls, returning states at **1.001 × requested flight time**. Segment-end anchoring and validator implementations remain unchanged.

- Full Proof: **all 213 checks pass**, but maximum-altitude error changes from **0.004306526854634285 m** to **0.0043405452743172646 m**. Exactly one check record changes.
- Acceptance reversal: identical simulator data fails against the clean reference (**0.01301 m > 0.013 m**) and passes against the corrupted reference (**≈0.0129759816 m**). Standalone O9 returns no rejection reasons and PASS.

Evidence: `review_scratch/anchor_phase.log` and `review_scratch/anchor_acceptance.log`.

**Suggested fix:** Independently reconcile every consumed coast tick state or radius with the existing DOP853 trajectory, including separately evaluated endpoint ticks. Add regressions for changed reported extrema and this acceptance reversal. Update the documented reference-consumer inventory.

### Summary

**Verdict: FAIL.** F49 is blocking.

- **F42–F43:** remain **accepted residual risk**, not fixed. Their exact mutations again leave all 213 check records identical. Their non-relevance conclusions remain correct for those mechanisms. The consumer inventory needs updating for the new Kepler extrema path.
- **F44–F46:** remain resolved. **F47–F48:** resolved for their reported mechanisms. Translation, interior r/v scaling, the original 0.1 m acceptance reversal and 1e200 velocities were re-probed. Disabling coast anchoring, burn anchoring, anchor-based extrema, start-node identity and `within()` causes **1, 1, 2, 1 and 1** targeted failures respectively.
- **All eight required commands pass**, including **1,016 tests**, Ruff, both GMAT comparisons, both Proof validators, determinism and cross-platform validation.
- Fresh M2 Proof matches **213 checks, 777 metrics and every other report field except CPU metadata** in `previous-m2-report.json`. Against d36c4c4, only the two altitude-error metrics change, by at most **1.955777406692505e-8 m**.
- T5 limits, M1 gates, golden assets and loaded thresholds remain unchanged. Pins match; applicable O9 position gates respect the **15 µm floor**. Thresholds remain provisional, DR-0017/DR-0018 separation is preserved, and no T7 scope appears.
- GMAT reports are byte-identical to **1de827e**; generated scripts match committed scripts. The 1017c55 grid split and CI test-ordering fix are verified.
- Documentation’s broad reference-validation claims need correction for F49. All **133 protected snapshot files** remain unchanged. Full review and evidence are under `review_scratch/`.