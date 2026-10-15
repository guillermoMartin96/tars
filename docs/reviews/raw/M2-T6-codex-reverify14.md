### F50 — Correlated tick-reference corruption reverses O9 acceptance

**Severity:** Medium

**Claim:** Matching corruption of Kepler tick outputs and DOP853 dense tick positions passes the F49 comparison. The surrounding stencil validates velocity but does not reconcile the corrupted center position.

Blocking under **DR-0019 B** because invalid reference data passes through unchanged helpers, and **DR-0020 A** because it changes `orbit_events[m2_prograde_burn].max_altitude_error_m` and reverses O9 acceptance. The documented method limit does not exempt this contract-relevant corruption.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/joint_reference.py
```

The probe returns Kepler states at **1.001× requested flight time**, including reverse calls, and matching DOP853 positions at interior coast ticks. Endpoints, solver nodes, stencil samples and validator helpers remain unchanged.

Identical simulator data:

- Clean reference: rejected, **0.01301 m > 0.013 m**.
- Corrupted references: accepted, **0.01297598157543689 m**; `_evaluate` returns no rejection reasons and a passing O9 check.

Evidence: `review_scratch/joint_reference.log`.

**Suggested fix:** Validate consumed tick positions against surrounding trajectory positions using a physically bounded positional-continuity check. Retain existing checks and add this joint-corruption acceptance-reversal regression.

### F51 — O6 accepts wrong-time Kepler outputs that change reported metrics

**Severity:** Medium

**Claim:** O6’s invariants and round trip do not establish the commanded midpoint’s flight time. A correlated forward/backward time-scale error changes the consumed post-impulse SMA. This differs from F42’s SMA-preserving sign negation.

Blocking under **DR-0019 B** because invalid independent-reference outputs pass through unchanged helpers, and **DR-0020 A** because gated and reported `o6_impulsive_limit` values change.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/o6_phase.py
PYTHONPATH=src .venv/bin/python review_scratch/o6_proof.py o6
```

Only raw Kepler returns in `impulsive_row` change, using **10× requested flight time** in both directions. The full Proof still passes **all 213 checks**, while both prograde and retrograde O6 records change.

For prograde:

- `order_deviation_from_2_max`: **0.004101602837031981 → 0.004192111708762436**.
- `slice_finite_minus_impulsive_sma_m`: **−0.1306562079116702 → −0.130659656599164**.

Evidence: `review_scratch/o6_proof.log` and `review_scratch/o6_phase_m2.json`.

**Suggested fix:** Independently reconcile the consumed midpoint state or post-impulse SMA at the required flight time. Add a wrong-time output regression.

### Summary

**Verdict: FAIL.** F50 and F51 are blocking.

- **F42:** accepted residual risk for its exact mechanism; re-probing leaves all 213 check records identical.
- **F43:** remains recorded as accepted residual risk; its original mutation is now rejected by F49.
- **F44–F49:** resolved for their reported mechanisms. Both original F49 probes reject. All **14 targeted tests pass**; disabling tick reconciliation causes **five targeted failures**. The revised F47 rejection assertions are stricter.
- **All eight required commands pass**, including **1,019 tests**.
- Fresh M2 Proof preserves **213 checks, 777 metrics and all other fields except CPU metadata**. It is therefore not literally byte-identical.
- Verified unchanged T5 limits, M1 gates, golden assets and loaded thresholds; matching pins; applicable O9 position gates above the **15 µm floor**; provisional thresholds; DR-0017/DR-0018 separation; no T7 scope; GMAT reports byte-identical to `1de827e`; generated scripts matching committed scripts.
- Artifact, threshold, reference-row, simulator-data and missing-observation sweeps reject their mutations. All **133 protected tracked files remain unchanged**.

**Note:** Documentation is partly stale: F43’s rationale and unused-value inventory omit F49’s full-vector dense-position consumer; VAL-0014’s epoch description omits F46’s configured-epoch anchor. Full findings and evidence are under `review_scratch/`.