### F49 — Unchecked Kepler tick outputs can reverse O9 acceptance

**Severity:** Medium

**Claim:** The new coast extrema consumer independently checks the segment-end Kepler result, but does not reconcile the separately returned tick states with an independent state. Corrupting their time of flight preserves energy, angular momentum and the correlated round trip, yet changes consumed radii. This is blocking under DR-0019 B because invalid independent-reference data passes through unmodified validator helpers, and under DR-0020 A because it changes `orbit_events[m2_prograde_burn].max_altitude_error_m` and reverses standalone O9 acceptance.

**Evidence:** Run `PYTHONPATH=src .venv/bin/python review_scratch/anchor_phase.py`. The probe changes only raw independent Kepler return data for the coast tick-radius calls in `_anchor_segment`, using states at 1.001 times the requested flight time; segment-end anchoring and every validator helper remain unchanged. All 213 Proof checks pass, but the prograde maximum-altitude error changes from 0.004306526854634285 m to 0.0043405452743172646 m. Exactly one check record changes.

Run `PYTHONPATH=src .venv/bin/python review_scratch/anchor_acceptance.py`. The same simulator output is rejected with the clean reference (`max_altitude_error_m = 0.01301 m > 0.013 m`) and accepted with the corrupted reference (approximately 0.0129759816 m): `_evaluate` returns no rejection reasons and a passing O9 check. See `anchor_phase.log` and `anchor_acceptance.log`.

**Suggested fix:** Independently reconcile every consumed coast tick state or radius, including separately evaluated endpoint ticks, with the existing DOP853 trajectory under justified consistency bounds. Add regressions for changed reported extrema and this acceptance reversal. Update the reference-consumer inventory and validation claims.

### Summary

**Verdict: FAIL.** F49 is blocking within the approved scope.

- **F42–F43:** remain accepted residual risk, not fixed. Their exact mutations again leave all 213 check records identical; their non-relevance conclusions remain correct for those mechanisms. The inventory is stale: dense radii no longer feed extrema, and the new Kepler tick consumer is relevant to F49.
- **F44–F46:** remain resolved. **F47–F48:** resolved for the reported mechanisms. Translation and correlated interior r/v scaling no longer change the consumed extrema; the original 0.1 m acceptance reversal stays rejected; 1e200 velocities are rejected. Disabling coast anchoring, burn anchoring, anchor-based extrema, start-node identity and `within()` causes respectively 1, 1, 2, 1 and 1 targeted failures.
- All eight required commands pass: **1,016 tests**, Ruff lint/format, both GMAT comparisons, both Proof validators, determinism and cross-platform validation. The artifact/threshold, GMAT-row and simulator/missing-observation sweeps reject the other tested corruptions (24, 18 and 26 cases). Generated GMAT scripts match the committed scripts byte-for-byte.
- Fresh M2 Proof matches all **213 checks and 777 metrics**, and all other report fields except the CPU description, in `previous-m2-report.json`. Against d36c4c4, only `min_altitude_error_m` and `max_altitude_error_m` change: 27 metric entries, maximum delta **1.955777406692505e-8 m**. Every check passes.
- T5 baseline limits, M1 gates, golden assets and loaded thresholds are unchanged. Threshold/manifest pins match; applicable O9 position gates respect the 15 micrometre floor. Thresholds remain provisional; DR-0017/DR-0018 separation remains intact; no T7 scope was introduced. All GMAT reports are byte-identical to 1de827e. Commit 1017c55 splits every reference at telemetry-grid times and builds the node-bisection test reference before poisoning Kepler.
- README, VAL-0014 and the decisions preserve the approved scope and threshold policy. The broad reference-validation claims and review consumer inventory need the F49 correction. All **133 protected snapshot files** remain unchanged. Review evidence is under `review_scratch/`.
