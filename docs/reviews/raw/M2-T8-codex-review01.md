### T8-F1 — Evidence publication can fail while reporting success
**Severity:** Medium  
**Claim:** Failed evidence publication can still produce `overall: PASS` and exit 0.  
**Evidence:** `toolbox/scripts/run_m2_proof.sh:59–65` prints the verdict before unchecked `mkdir` and `cp` operations. Executing these exact publication statements with an existing file as the destination produced three filesystem errors, `overall: PASS`, and exit 0. Reproduction: `review_scratch/publish_probe/result.txt`. Validator-step failures themselves are correctly retained in `FAILED`.  
**Suggested fix:** Check publication operations and required artifacts, propagate failures to the exit status, and print the final verdict after publication succeeds.

### T8-F2 — The runner can overwrite M1 evidence
**Severity:** Medium  
**Claim:** The guarantee that the runner “never writes the M1 evidence” is false.  
**Evidence:** Line 11 accepts an unrestricted destination. Passing `proof/records/evidence/M1` makes lines 60–63 overwrite files there, including `proof_run.log` and `m1_non_gmat.json`. There is no destination guard. I did not execute this against M1 evidence.  
**Suggested fix:** Resolve the destination and reject the M1 evidence directory and its descendants, including path and symlink aliases, before running checks.

### T8-F3 — Cleanliness reporting fails open
**Severity:** Medium  
**Claim:** A failed Git cleanliness query can be reported as a clean tree.  
**Evidence:** Line 16 checks captured stdout without checking Git’s exit status. With an absolute evidence path outside the repository, Git exits 128; its empty stdout produces `CLEAN=yes`. An isolated index containing a staged README deletion reproduced this without changing the checkout: `review_scratch/cleanliness_probe.txt`. The query is correctly positioned before evidence publication.  
**Suggested fix:** Require a successful Git query. Normalize repository-local exclusions, and omit the exclusion for destinations outside the repository.

### T8-F4 — “Complete M2 suite” omits a required CI gate
**Severity:** Medium  
**Claim:** The runner does not cover every CI gate despite its complete-suite description.  
**Evidence:** It collects one platform’s record and runs the golden comparison, but never invokes `m2_cross_platform.py gate`. `.github/workflows/ci.yml:86–116` separately requires the three-platform, same-revision comparison. Missing or disagreeing remote-platform evidence cannot affect this runner’s verdict. The README and T8 delivered-scope claim overstate its coverage.  
**Suggested fix:** Accept and validate the required platform evidence through the existing gate, or explicitly describe this as the local suite and require separate CI gate evidence before claiming full Proof completion.

### T8-F5 — Audited-run count confuses runs with report groups
**Severity:** Low  
**Claim:** P1’s “all 16 audited runs” count is inaccurate.  
**Evidence:** `proof/records/M2-propulsion.md:266` counts 16 aggregated report groups. The validator audits **28 individual runs**: six canonical missions, eight O8 auxiliary runs, ten O6 variants, and four stop-boundary variants. `_merge_audits()` combines auxiliary results into fewer groups.  
**Suggested fix:** Say “28 audited runs, aggregated into 16 report groups.”

**Summary**

**Verdict: REQUEST_CHANGES**

Verified at HEAD `adb3710`, without tracked-file changes:

- Full suite: **1,185 passed, three expected overflow warnings, 1,733.44 seconds**.
- Ruff: clean; **153 files** formatted.
- M2 Proof: **228/228**, exactly matching committed validator names, metrics, thresholds and pass statuses. Mission results also match.
- Snapshot: **48,310 records and 982,324 values** verified; baseline verification succeeded.
- Reproduced maximum O4 position error **0.3127442515 m**, GMAT–DOP853 disagreement **4.6591902702e-6 m**, and maximum threshold utilization **0.6597269452**.
- M1 Proof **7/7**; both GMAT comparisons, all five cross-process determinism runs, and all four M2 missions succeeded. Mission summaries match committed evidence exactly.
- M1 golden hash reproduced: `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- Fresh golden differences: **0 m / 0 m/s**. Archived three-platform gate reproduced **7.2320546225e-6 m / 8.4286904175e-9 m/s**.
- No protected implementation assets changed since `963dbe7`; required M1 assets are unchanged against `origin/main` (`63bec8d`).
- Physics, architecture, events, replay, approved limitations and earlier dispositions are otherwise consistent with the milestone evidence. No open earlier Critical/High issue was found. P12 remains explicitly pending; its named T8 review file is not yet present.

`uv` was unavailable, so the wrapper received static review and isolated shell probes; all requested Python checks ran through the prepared environment.

**M2 is not ready for the Tech Lead’s final milestone review until the T8 workflow/report findings are resolved and dispositioned.**