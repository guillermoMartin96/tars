### T7-F1 — Snapshot reproducibility is overstated as reference accuracy

**Severity:** Medium  
**Claim:** DR-0023 calls the 4.66 µm GMAT–DOP853 disagreement “not noise” and treats reference agreement as a reference-error bound.

**Evidence:** DR-0023’s error budget and FU-1 section conflate reproducibility with accuracy. Snapshot substitution explains the zero O9 reference-metric spread, but freezes the baseline’s numerical error too. Raw references vary across hosts by more than the frozen disagreement. Agreement between two numerical references does not independently bound either reference’s absolute error.

**Suggested fix:** Describe 4.66 µm as the measured disagreement against the approved baseline. Retain the platform-reproducibility conclusion, but distinguish it from reference accuracy and numerical uncertainty.

### T7-F2 — FU-1 combines coordinate drift with a vector-norm error

**Severity:** Low  
**Claim:** The re-baselining calculation uses incompatible measures.

**Evidence:** `record_drift()` computes maximum absolute coordinate differences. Its 8.104543667 µm result is added to O9’s Euclidean-norm disagreement of 4.659190270 µm. Independently recomputed maximum Euclidean position drift is **8.619305144 µm**, at `m2_retrograde_burn/o9/dop853.segment#971` on `ubuntu-latest-38492704906`. The corresponding doubled bound is approximately **26.557 µm**, rather than 25.6 µm.

**Suggested fix:** Label coordinate maxima explicitly and use Euclidean drift, or a conservative vector bound, in the FU-1 calculation. The recommended 30 µm value still has headroom.

### T7-F3 — Claimed regression-detection guarantees are incorrect

**Severity:** Medium  
**Claim:** DR-0023 says the 30 µm gate catches “any” change above about 25 µm; the tighter option claims detection above about 5 µm.

**Evidence:** A perturbation can partially cancel the existing residual. For an existing residual norm of 4.659 µm, the reverse triangle inequality gives a direction-independent sufficient detection bound above **34.659 µm** for the 30 µm gate, and above **14.659 µm** for the 10 µm gate. Subtracting the existing residual from the limit describes favorable-direction headroom, not guaranteed detection.

**Suggested fix:** Correct the consequences stated for both options. Distinguish directional sensitivity from guaranteed detection by the numerical gate.

### T7-F4 — O6’s bound is mislabeled and its printed sum mixes missions

**Severity:** Low  
**Claim:** DR-0023 describes 0.0405 as the possible metric shift and prints `0.0041 + 0.0366 = 0.0405`.

**Evidence:** Independent corner calculations from the bundled impulsive families give:

- Prograde: deviation **0.004101766729**, shift **0.035601593999**, sum **0.039703360727**.
- Retrograde: deviation **0.003850502040**, shift **0.036642369712**, sum **0.040492871753**.

Thus 0.0405 is the maximum **deviation plus shift**, not the shift alone. The printed operands combine maxima from different missions and sum to approximately 0.0407.

**Suggested fix:** Report the per-mission calculations and identify 0.040492872 as the maximum combined bound. The unchanged 0.05 recommendation remains supported.

### T7-F5 — Published spread claims contradict the evidence

**Severity:** Low  
**Claim:** VAL-0016 reports zero spread for every round-off metric; DR-0023 understates O9 boundary-position spread.

**Evidence:** Independent recomputation confirms:

- O2 reported rocket-equation relative-error spread: **1.213533923e-16**.
- O7 inclination-change spread: **3.330669074e-16**.
- Accounting unit-vector spread: **1.665334537e-16**.
- O9 invalid-command boundary-position spread: **6.397299023e-9 m**, contradicting the matrix’s combined `≤ 9.4e-12` statement.
- O9 simulator-versus-GMAT position spread peaks at **7.231065107e-6 m**, rather than the 1.1e-5 m attributed to it in VAL-0016.

**Suggested fix:** Correct the summaries and separate position and velocity spreads with their units. The analyzer’s underlying figures are correct.

### T7-F6 — Cross-process determinism coverage is overstated

**Severity:** Low  
**Claim:** VAL-0016 says cross-process determinism was measured for “all six M2 scenario files.”

**Evidence:** There are four M2 scenario files. Every bundle contains four M2 cross-process results plus M1. The generated `m2_invalid_commands_empty_tank` and `m2_invalid_commands_no_propulsion` missions have **in-process** replay checks in `m2_proof.py`, not cross-process results in these bundles.

**Suggested fix:** State the actual coverage: four scenario files measured across processes, six missions checked in process. If cross-process coverage of both generated variants is intended, collect it explicitly.

### Summary

**Verdict: REQUEST_CHANGES**

Verified:

- **1101 tests passed**, with three overflow warnings from numerical-extreme tests.
- Ruff lint and formatting passed.
- M2 Proof passed **215/215**; M1 Proof and GMAT comparison passed.
- Analyzer output exactly matches committed `analysis.json`.
- Independent calculations confirm threshold worst cases, comparable-check spreads, margins, final-state drift, reference variation and O6 bounds.
- All recorded input/output digests match; committed bundle files match the supplied bundles.
- Bundle provenance matches the DR-0008 platform matrix, with no substitution.
- The supplied diff preserves thresholds, references, snapshot tolerances, checks and acceptance semantics. `m2.json` remains unchanged and provisional; regression checks pass; no T8 implementation appears.

The proposed numerical values remain supported. Correct the reported figures and decision rationale before approval.