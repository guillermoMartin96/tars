### F58 — Mutable session data bypasses the authenticated snapshot

**Severity:** High

**Claim:** Authentication protects the artifact at load time, but subsequent session-data corruption can silently change the verification baseline or disable verification. Blocking because it changes O6 reported values and restores the O9 acceptance reversal. Violates DR-0021 conditions **1 and 5**.

**Evidence:** Executable reproductions, with validator helpers unchanged:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/ledger_values17.py
PYTHONPATH=src .venv/bin/python review_scratch/mode_corrupt17.py
PYTHONPATH=src .venv/bin/python review_scratch/session_f50_17.py
```

- Editing `Session.approved` after authentication lets **20 wrong-time Kepler returns** pass all **215 Proof checks**, still in **verify mode**. Prograde O6 order deviation changes from **0.00410160284** to **0.00419211171**. The report claims baseline 3’s digest, **48,310 records verified**, **982,324 values verified**, and **zero deviation**.
- Changing session data to `mode="record"` and `approved=None` also permits a passing Proof, with **zero values verified**.
- That second corruption restores F50: clean references reject **0.01301 m** against **0.013 m**; coordinated corrupted references accept **0.0129759816 m**, with no snapshot problems.

`Session.pin()` trusts the mutable ledger and takes the record-mode branch before its ledger guard. Nested sessions reuse this state without checking its integrity.

**Suggested fix:** Bind verification mode and authenticated contents to protected state, validate their integrity before accepting results, and require verification sessions at Proof/compare entrypoints. Add both session mutations as regressions.

### F59 — Zero-deviation time tolerances use the wrong maximum

**Severity:** Medium

**Claim:** The documented ten-ulp rule is incorrectly applied to all three continuous time classes. Blocking because it changes the `reference_snapshot` acceptance decision for deviations inside the documented reproducibility allowance. Violates DR-0021 condition **4**. This produces false rejection, rather than concealing an acceptance reversal.

**Evidence:**

```sh
PYTHONPATH=src .venv/bin/python review_scratch/zero_rule17.py
```

The `ref:s` and `gmat:s` maxima are approximately **53,100 s**; `sim:s` reaches **53,700 s**. Ten ulp is therefore **7.2759576e-11 s**, before rounding. All three tolerances are **1e-11 s**, justified using **6,000 s**.

The probe perturbs reference-output data by two ulp, **1.4551915e-11 s**. Unmodified snapshot helpers reject each class despite the deviation being within the stated ten-ulp allowance.

**Suggested fix:** Recalculate zero-measured bounds from the actual class maxima and apply the documented rule, or obtain and document a reviewed justification for a different rule. Add a regression checking these maxima.

### Summary

**Verdict: FAIL.** F58 and F59 are blocking.

- **F42–F43:** remain **ACCEPTED RESIDUAL RISK** under DR-0020.
- **F44–F49:** remain resolved.
- **F50–F51:** resolved with intact sessions; F58 demonstrates broader bypasses.
- **F52–F53:** remain resolved.
- **F54–F57:** resolved for their reported mechanisms. All eight requested probes now reject their original mutations. Corresponding regression tests fail when their mechanisms are disabled.
- **All nine requested commands pass:** **1,092 tests**, three warnings; Ruff; both Proofs; both GMAT comparisons; determinism; cross-platform; baseline verification.
- **Fresh M2 Proof:** exactly **215 passing checks against baseline 3**. All **213 previous complete check records are unchanged**, plus exactly the two required passing exact checks.
- Verified complete candidate inventory and independent per-part recomputation, baseline provenance/change comparisons, all **24 measurements**, substitution, O5 margins, and both O6 families’ **32 perturbation corners**. Conditions 1/5 remain incomplete through F58; condition 4 through F59.
- Verified unchanged T5/M1 limits and golden assets, matching pins, applicable GMAT gates above the floor, DR-0017/DR-0018 separation, provisional thresholds, no T7 expansion, and GMAT reports byte-identical to `1de827e`.
- Documentation needs correction for F58’s authentication assurances and F59’s tolerance calculation. All **163 protected tracked files remain unchanged**.