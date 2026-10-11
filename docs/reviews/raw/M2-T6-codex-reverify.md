### F8 — Generation metadata and manifest history can change without rejection
**Severity:** Medium  
**Claim:** The approved manifest binds script, report, and console bytes, but not metadata. Its replacement history is never validated.

**Evidence:** `review_scratch/sweep.py` changed the revision to forty zeros, timestamp to `1900-01-01`, host to `invented`, and replacement reason to `null`. `_evaluate` returned no rejection and a passing check. Separately, replacing manifest history with an inconsistent report digest also passed. See `sweep.log`; relevant code is `gmat_m2.py:550–567,618–624`.

**Suggested fix:** Bind metadata into the approved artifact set. Validate history structure and require its latest mission record to agree with the committed metadata and digests.

### F9 — Interrupted publication can leave an accepted partial replacement
**Severity:** Medium  
**Claim:** Writing the manifest last does not provide the claimed atomic publication.

**Evidence:** `review_scratch/workflow_probes.py` injected an exception immediately before manifest replacement during a byte-identical reproduction. The metadata changed, the old manifest remained, and subsequent evaluation **passed**. Individual artifacts are replaced sequentially at `toolbox/scripts/gmat_m2.py:218–224`.

**Suggested fix:** Publish complete versioned artifact sets through one atomic pointer, or invalidate the old commit marker before replacement and bind every artifact to the new marker. Test interruptions at each publication step.

### F10 — Reproduction does not authenticate the executable it runs
**Severity:** Medium  
**Claim:** The reproduction test establishes byte equality using an executable at a fixed pathname; it does not establish reproduction by the approved binary.

**Evidence:** `review_scratch/workflow_probes.py` substituted a scratch executable that merely copied committed reports. All three reproduction-test bodies passed. `tests/test_gmat_m2.py:330–341` checks neither executable digest nor console provenance.

The installed executable used in this review independently matched the approved SHA-256, and its three real reproductions passed. This finding does not imply fabrication of the committed references.

**Suggested fix:** Verify the executable digest before reproduction and validate its successful console outcome. Describe authenticated reproduction as independent reproducibility evidence: it cannot prove the historical origin of stored bytes.

### F11 — Preview generation can overwrite references through symlinks
**Severity:** Medium  
**Claim:** `generate` checks the output directory, but follows existing output-file symlinks into the reference directory.

**Evidence:** `review_scratch/sweep.py` created a preview filename pointing to a copied committed script. With the wrong-generator mutation, `generate` returned **0** and overwrote that reference with `WRONG GENERATOR`. See `sweep.log` and `toolbox/scripts/gmat_m2.py:55–64`.

**Suggested fix:** Reject output-file symlinks or publish previews using temporary files and replacement that does not follow the existing destination. Check each destination’s relationship to protected references.

### F12 — Standalone workflows discard numerical simulator-audit failures
**Severity:** Medium  
**Claim:** `_evaluate` checks `audit.violations` but discards `audit.metrics`, so its “clean audit” can contain failed T5 numerical gates.

**Evidence:** `review_scratch/audit_coverage.py` independently corrupted a burning sample’s:

- thrust acceleration to `(1, 1, 1)`, producing relative acceleration error **3.595**;
- sensed delta-v to **1000 m/s**, producing relative sample error **34.158**.

Both evaluations returned no rejection and **passed**. The applicable T5 accounting limits are `1e-12`. See `audit_coverage.log` and `toolbox/scripts/gmat_m2.py:82–83`.

**Suggested fix:** Apply the existing scoped thresholds and coverage checks to the audit metrics before accepting a staged reference or standalone comparison.

### F13 — Boundary coverage misses the same-tick reporting exception
**Severity:** Low  
**Claim:** Expected ignition coverage uses physical ignition time rather than the independently predicted reporting tick.

**Evidence:** `review_scratch/field_sweep.py` stopped the same-tick submission/ignition mission at **600 s**. The valid log defers `BurnStarted` to tick 61, but `coverage_problems` demanded it at the horizon and rejected the log. See `field_sweep.log` and `gmat_m2.py:668–669`.

This is a false rejection in the general coverage helper; the affected depletion mission is excluded from the three committed O9 references.

**Suggested fix:** Determine boundary-event inclusion from `_expected_report_tick`, including same-tick submission semantics, and test their intersection with DR-0018 stops.

## Summary

**Verdict: FAIL.** The committed numerical evidence passes, but reference publication, provenance, preview protection, and standalone audit acceptance retain demonstrated defects.

**F1–F7 status:**

- **F1:** Numerical rejection and preservation on validation failure resolved; publication atomicity remains defective under F9.
- **F2:** Resolved: moved, duplicated, and missing assignments are rejected.
- **F3:** Original missing-provenance, failed-console, and unapproved fabricated-report probes are rejected. Partially resolved overall; F8 and F10 remain.
- **F4:** Direct-directory bypass resolved; partially resolved overall because of F11.
- **F5:** Original deleted-observation probes resolved. Boundary coverage has the F13 limitation.
- **F6:** Resolved: removing any of the 15 mandatory O9 limits rejects comparison.
- **F7:** Resolved: disabling each of the 15 numerical metrics fails its targeted test, including coast alignment. Reverting/disabling each F1–F6 fix control also fails a targeted test.

**Verified:**

- Full suite: **890 passed**, two expected overflow warnings.
- T6 suite: **61 passed**, including three real GMAT reproductions.
- Ruff lint and formatting passed.
- M2 Proof: **212/212 passed**; M1 Proof passed.
- GMAT M2 comparison, determinism, golden-state/cross-platform comparison, and GMAT M1 comparison passed.
- All **18 row mutations** across the three references were rejected.
- Git-history comparison confirmed all three reports are **byte-identical to `1de827e`**.
- T5 validator and simulator code, M1 thresholds, and golden artifacts remain unchanged. Existing T5 gates were not loosened.
- DOP853 comparison position limits remain **30 µm**, above the **11–15 µm** floor; thresholds remain provisional.
- DR-0017 and DR-0018 remain separate; no T7 implementation scope was introduced.
- Every tracked snapshot file remains unchanged. Review probes and logs are under `review_scratch/`.