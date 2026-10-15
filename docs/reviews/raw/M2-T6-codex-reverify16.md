### F54 — Baseline coverage can approve missing or unverified data

**Severity:** Medium

**Claim:** `verify-baseline` tracks coverage of supplied records rather than requiring the complete expected inventory and verifying every part. Blocking because corrupted candidates receive a passing **baseline approval decision**, violating DR-0021 conditions **1 and 2**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/baseline_parts16.py
PYTHONPATH=src .venv/bin/python review_scratch/baseline_keys16.py
```

Every mutation is accepted without problems:

- GMAT arc `step_s` values changed to **12,345 seconds**.
- A powered-crossing count changed to **999**.
- An O5 counter changed to `#999999`.
- An entrypoint changed to `bogus`.
- All O5 records removed.
- An unknown `o9.unverified` record added.

The actual CLI also approves the corrupted arc artifact; see `review_scratch/arcs_cli16.log`. Coverage at `toolbox/scripts/reference_snapshot.py:390` checks only supplied keys, and the O9 loop marks records covered before determining whether their label is supported.

**Suggested fix:** Require the expected keys, counters, entrypoints and part schemas; reject unknown labels; mark each part verified only after evaluating it.

### F55 — Baseline node verification does not establish the crossing sequence

**Severity:** Medium

**Claim:** Checking that each supplied time is an ascending-node root does not establish completeness, uniqueness or order. Blocking because it falsely approves references used by `node_crossing_time_error_max_s`, `ours_vs_gmat_node_crossing_error_max_s` and crossing-count invariants. Violates DR-0021 condition **2**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/nodes16.py
```

Across all **31** reference and GMAT crossing records, baseline verification accepts:

- Every crossing replaced by that record’s first crossing, preserving list length.
- Empty crossing lists.
- Removal of all crossing records.

The actual CLI approves the duplicate-crossing artifact; see `review_scratch/nodes_duplicate_cli16.log`. The loops verify only supplied roots and never independently enumerate the required sequence.

**Suggested fix:** Independently derive the complete crossing sequence and powered-interval count, then compare counts, ordering and times.

### F56 — Baseline verification trusts corrupted evaluation inputs

**Severity:** Medium

**Claim:** O5 flight times and O3 case inputs are taken from the candidate without establishing that they describe the required observations. Self-consistent expectations for another time therefore pass. Blocking because this changes the **baseline approval decision** and the physical expectations underlying O5/O3 checks. Violates DR-0021 condition **2**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/wrong_inputs16.py
```

Both candidates return no problems:

- O5 flight times multiplied by **10**, with position and velocity recomputed consistently.
- All O3 expectations recomputed for **100 seconds**, replacing the required **77.3-second** interval.

No verifier implementation is modified.

**Suggested fix:** Independently establish the required observation schedule and O3 case inputs before recomputing their outputs.

### F57 — Lost session ledger silently disables runtime verification

**Severity:** High

**Claim:** After successful authentication, corrupting `Session.approved` to `None` silently skips both value comparisons and completeness checks. Blocking because it restores the demonstrated **O9 acceptance reversal** and allows changed O6 results through a passing Proof. Violates DR-0021 conditions **1 and 5**.

**Evidence:** Run:

```sh
PYTHONPATH=src .venv/bin/python review_scratch/session_f50_16.py
PYTHONPATH=src .venv/bin/python review_scratch/session_corrupt16.py
```

These mutate session data after authentication and raw reference outputs; snapshot helpers remain unchanged.

- F50: clean references reject **0.01301 m**; coordinated corruption accepts **0.0129759816 m**.
- F51: **20 wrong-time Kepler returns**, changed O6 metrics, and **215 passing Proof checks**.
- The report retains baseline 2’s digest and claims **48,279 records verified**, while reporting **zero values verified**.

`Session.pin()` returns unchecked runtime data when the ledger is absent; `finish()` also skips coverage in that state.

**Suggested fix:** Fail closed when a verification session loses its authenticated ledger. Protect session integrity and distinguish consumed records from records actually verified. Add these session-corruption regressions.

### Summary

**Verdict: FAIL.** F54–F57 are blocking. F54–F56 concern candidate approval; runtime digest authentication correctly rejects their edited artifacts.

- **F42–F43:** remain **ACCEPTED RESIDUAL RISK**. Their original probes were rechecked.
- **F44–F49:** remain resolved for their reported mechanisms.
- **F50–F51:** resolved with intact sessions; F57 demonstrates a separate bypass.
- **F52:** resolved. The original margin probe is now rejected.
- **F53:** its reported O6 mechanisms are resolved; the broader independent-approval claim remains incomplete through F54–F56.
- **All nine required commands pass:** **1,076 tests**, Ruff, both Proofs, both GMAT comparisons, determinism, cross-platform and baseline verification.
- **Fresh M2 Proof:** exactly **215 passing checks** against baseline 2; all **213 previous complete check records unchanged**, plus the two required passing exact snapshot checks.
- Targeted regressions pass and fail when their corresponding mechanisms are disabled. Both O6 families’ **32 perturbation corners** satisfy their bounds.
- Verified baseline-2 provenance, justification and comparison: identical keys and **920,849 common values bit-identical**.
- Verified unchanged T5/M1 limits and golden assets; matching digest pins; applicable GMAT gates above the floor; DR-0017/DR-0018 separation; provisional thresholds; no T7 expansion; GMAT reports byte-identical to `1de827e`.
- Documentation’s complete-verification assurances require correction for these findings. All **156 protected tracked files remain unchanged**.