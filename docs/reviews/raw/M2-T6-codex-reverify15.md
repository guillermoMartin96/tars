### F52 — O5’s margin underestimates the permitted vector deviation

**Severity:** Medium

**Claim:** Snapshot tolerances apply per component, but `o5_snapshot_shifts()` uses that component tolerance as the bound for a Euclidean vector error. The required bound is up to `sqrt(3) × tolerance`. An undetected reference deviation can therefore reverse an O5 check while passing the margin check.

Blocking under DR-0020 A because it changes `o5_coast_kepler.coast_position_error_max_m` and its acceptance decision. Violates **DR-0021 condition 4**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/margin15.py
```

The probe changes raw Kepler output by evaluating 1.6 ns late. Validator helpers remain unchanged. The position shift has norm **12.4073 µm**, with every component below **10 µm**; velocity components also remain within tolerance.

Identical simulator observations produce:

- Clean reference: **0.6000009998261402 m**, O5 fails.
- Corrupted reference: **0.5999885925256035 m**, O5 passes.
- Snapshot problems: none.
- Margin problems: none.

This demonstrates an **O5 check reversal**, without claiming an overall Proof reversal. Evidence: `review_scratch/margin15.log`. VAL-0015’s claimed O5 worst-shift bound is consequently inaccurate.

**Suggested fix:** Use the appropriate vector-norm bounds for position and velocity margins, and retain this acceptance-reversal regression.

### F53 — Candidate baseline approval accepts corrupted O6 references

**Severity:** Medium

**Claim:** `verify-baseline` does not independently validate O6 midpoint states or impulsive SMA. Corrupted O6 outputs can pass both the recording Proof used by generation and the candidate’s baseline verification.

Blocking under DR-0020 A because it affects the **baseline approval decision**, commanded-time correctness, and subsequently trusted O6 reported and gated values. Violates **DR-0021 condition 2**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/record_o6_15.py
PYTHONPATH=src .venv/bin/python review_scratch/baseline_corruption15.py
```

The first probe applies F51’s original **10× flight-time mutation** only to raw Kepler returns:

- Recording Proof: **215 checks pass**, exit 0.
- Both O6 result records change.
- `verify_baseline` accepts the captured corrupted O6 records without problems.

The second changes all ten artifact O6 midpoints to **zero position and velocity**, with **SMA = −1e30 m**. The actual `verify-baseline` CLI still reports **PASS**, exit 0.

Runtime digest authentication correctly rejects the edited artifact; this finding concerns candidate approval. Evidence: `review_scratch/record_o6_15.log` and `review_scratch/baseline_corruption15.log`.

**Suggested fix:** Independently verify candidate O6 states at their required flight times and reconcile impulsive SMA. Add rejection regressions for wrong-time outputs and invalid artifact O6 values.

### Summary

**Verdict: FAIL.** F52 and F53 are blocking.

- **F42–F43:** remain **ACCEPTED RESIDUAL RISK** under DR-0020. F42 still preserves reported metrics; the snapshot rejects its changed vectors. F43’s original mutation is rejected.
- **F44–F49:** resolved for their reported mechanisms.
- **F50–F51:** resolved in runtime verification. The joint-reference probe is rejected, and the wrong-time O6 Proof fails `reference_snapshot`. Disabling comparison causes all three targeted corruption regressions to fail.
- **DR-0021:** coverage/exclusions, immutability, authenticated runtime verification, regressions and preserved gates were verified. Conditions **2 and 4** have the gaps above. Measurement tolerances follow the documented rule; both O6 families’ 32 perturbation corners satisfy their bounds.
- **Fresh M2 Proof:** exactly **215 passing checks**. The original **213 complete check records are unchanged**, plus the two required passing exact snapshot checks.
- **All nine required commands pass**, including **1,058 tests** and Ruff.
- Verified unchanged T5/M1 limits and golden assets; matching threshold, manifest and snapshot pins; applicable GMAT position gates above 15 µm; DR-0017/DR-0018 separation; provisional thresholds; no T7 expansion; GMAT reports byte-identical to `1de827e`.
- Artifact, threshold, reference-row, simulator-data and snapshot-ledger mutation sweeps reject their tested corruptions, apart from the findings above.
- All **138 protected tracked files remain unchanged**.