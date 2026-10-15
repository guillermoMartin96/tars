### T7-F7 — Linux evidence can satisfy the required macOS x86_64 slot

**Severity:** High

**Claim:** The gate accepts contradictory OS provenance, allowing a three-platform acceptance decision without macOS x86_64 evidence.

**Evidence:** `record_problems()` checks CI architecture and revision but never cross-checks `ci.runner_os` against `platform.system`.

I copied the archived Linux record, changed only its platform ID to `macos-x86_64`, its system to `Darwin`, and recomputed its record checksum. Its CI provenance and environment still identify Linux. Combining this record with the original Linux and arm64 records produced:

- CLI exit status **0** and zero evidence violations.
- Position difference: **3.7602478010319506e-6 m**.
- Velocity difference: **4.417525721178428e-9 m/s**.

The required Intel macOS evidence was absent. This changes evidence data only, within the stated threat model.

Reproduction and results are in `review_scratch/wrong_platform.py` and `review_scratch/wrong-platform/report.json`.

**Suggested fix:** Require valid CI OS provenance and cross-check GitHub’s `Linux`/`macOS` values against the declared platform system. Add library and CLI regressions for missing OS provenance, contradictory OS fields and this relabelled Linux record. Verify that removing the check makes those tests fail.

**Summary**

**REQUEST_CHANGES**

Verified:

- Full suite: **1,174 passed**, with three warnings from deliberate overflow tests. Ruff lint and formatting passed.
- All requested standalone commands passed: M1/M2 Proof, M1 cross-platform comparison, both GMAT comparisons, archive gate and local collection.
- All **215 earlier M2 checks** retain identical metrics, thresholds and outcomes. Mission reports are identical. The new report contains **228 checks**, comprising 13 additions.
- Every pre-existing M2 numerical limit is unchanged. The approved digest matches and changed alongside the threshold file in `27e5b8b`.
- FU-1 documents the pinned baseline, host dependence, noise measurements and approximately **34.7 µm guaranteed / 25.3 µm favourable** detection figures without claiming absolute accuracy. O6 remains unchanged; its proposed SMA class requires separate approval.
- M1 thresholds and golden, the specified M1 event digest, snapshot baseline 3, GMAT manifest pin and existing tolerances are unchanged. No existing CI step was removed or weakened.
- Independent recomputation reproduces all VAL-0017 mission and pair maxima, including **7.232054622489096e-6 m** and **8.428690417483863e-9 m/s** overall. Manifest checksums, archived provenance, golden byte identity and reference-host/Intel/T7 mission-final identities checked successfully.
- Euclidean metrics and inclusive boundaries are correct. Golden failure tests pass. Removing missing-platform detection, Rosetta rejection, input matching or the Euclidean position norm caused the corresponding scratch regression tests to fail.
- The GitHub Intel runner satisfies the stated OS/architecture matrix; the pinned golden preserves the reference-host baseline. Requiring that specific local host to execute every revision would need a Tech Lead decision.
- The working tree remains clean; all review files are under `review_scratch/`.