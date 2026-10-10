# External Review: Milestone 1 "Orbit"

**Reviewer/model:** independent Claude reviewer agent (claude-opus-5-5), spawned with no implementation context, read-only. **Independence caveat:** the reviewer is the same model family as the implementer. For stronger independence, the Tech Lead may run a second review with a different provider (playbook/git.md permits ChatGPT and others).  
**Date:** 2026-10-05  
**Reviewed revision:** `ca468e3` (branch `milestone-1-orbit`)  
**Fixes applied in:** `95fc224` (code); this record and the doc corrections in the following commit  
**Scope:**
- Scientific correctness of all M1 physics and oracles.
- Validation integrity (could a validator pass when physics is wrong).
- Architecture invariants.
- Proof/process compliance against CLAUDE.md, the playbook and proof/*.md.

## Summary
The reviewer reproduced every evidence number at `ca468e3`. It verified the gravity, RK4, element conversion, universal-variable propagation, Hermite node-root, period, SMA and energy formulas, and found **no Critical issues** and no shared bug between oracle and simulator. The main weakness was gate strength rather than physics:
- the GMAT gate did not gate constants or reference validity;
- DR-0008's μ-mismatch figure was wrong.

It also found hardening gaps (force models could mutate state; scan bypasses), a stale Proof record, and edge cases relevant to future milestones.

## Findings

### REV-001 — GMAT comparison doesn't gate constants or reference validity; DR-0008's μ-mismatch rationale is wrong
**Severity:** High  
**Reviewer claim:**
- Only the ours-vs-GMAT position is gated.
- The SMA, period, GMAT-vs-Kepler and initial-state metrics, and the metadata constants, were unchecked, contrary to SCI-0005, the README and DR-0008.
- With the same Cartesian start, a μ mismatch shifts the period by 2·Δμ/μ (0.63 m over 10 orbits), not 0.16 m. A mismatch of either sign can pass 0.6 m.

**Evidence:**
- Synthetic GMAT rows with μ = 3.986004421e14 pass (ours vs GMAT 0.33 m).
- Independently reproduced by the implementer: Δa = 4.99 mm and ΔT = 8.08e-6 s per orbit, giving 0.627 m.

**Affected code/Proof:** `src/tars/validation/gmat.py`, `toolbox/scripts/gmat_m1.py`, `proof/thresholds/m1.json`, SCI-0005, DR-0008, GMAT README  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** The finding is correct, and the error was mine (an equal-radius assumption). Current results are valid (initial SMA difference 1.9e-9 m), but the gate could pass a mismatch in future. New numeric gates are new Proof tolerances, which need Tech Lead approval (DR-0004).  
**Resolution/evidence:**
- Exact checks implemented, needing no tolerance:
  - the committed script must equal the regenerated script (`Earth.Mu` line included);
  - the metadata constants must equal the scenario's;
  - the script and report hashes must match.
  - Tests: `test_provenance_checks_are_exact` and `test_committed_reference_passes_provenance_checks`.
- `test_compare_detects_mismatched_mu` now asserts the corrected 8.08e-6 s and 0.627 m.
- SCI-0005 and the README are corrected, and an erratum is appended to DR-0008.
- The numeric gates were escalated in DR-0009.
- **Resolved after DR-0009 approval (option A, 2026-10-05):**
  - all nine `gmat_reference` gates are in `proof/thresholds/m1.json`;
  - CI runs the committed-reference compare;
  - `test_approved_gates_reject_mu_mismatch_of_either_sign` shows the reviewer's passing case (μ = 3.986004421e14) and a 1e-12 relative mismatch now fail.

---

### REV-002 — A truncated GMAT reference passes
**Severity:** Medium  
**Reviewer claim:** No row-count or coverage check exists. A 2-row report passes.  
**Evidence:** truncation experiment (2 rows: 7.3e-5 m, PASS).  
**Affected code/Proof:** `gmat.compare`, `gmat_m1.py run`  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct; a completeness requirement is exact and needs no tolerance.  
**Resolution/evidence:**
- `compare` requires the row times to equal exactly 0, 60, …, 53 700 s (896 rows).
- `run` validates a new report before storing and hashing it.
- Test: `test_truncated_reference_is_rejected` (1, 89 and 894 rows).

---

### REV-003 — CI doesn't run the GMAT comparison, contrary to ADR-0006 and DR-0005
**Severity:** Medium  
**Reviewer claim:** ADR-0006 and DR-0005 say CI compares against the committed CSV, but ci.yml does not.  
**Evidence:** `.github/workflows/ci.yml` has no compare step.  
**Affected code/Proof:** ADR-0006, DR-0005, CI  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** The documents and CI were inconsistent. The Tech Lead's DR-0007 instruction ("keep GMAT external validation outside required CI") takes precedence over my ADR wording, so I did not change CI unilaterally.  
**Resolution/evidence:**
- ADR-0006 and DR-0005 are corrected to match DR-0007.
- The comparison runs in `run_m1_proof.sh`.
- Adding it to CI is recommended in DR-0009.
- The documentation inconsistency is resolved; the CI addition is a Tech Lead choice.

---

### REV-004 — Force models can mutate simulator-owned state in place
**Severity:** Medium  
**Reviewer claim:** `Simulator._y` was writable, and the k1 stage passed views of it to `acceleration()`. A force model doing `v += 1` corrupted the state.  
**Evidence:** experiment showing the +1 m/s leak.  
**Affected code/Proof:** `src/tars/sim/simulator.py`; architecture invariant 1  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct, and important before thrust and agent-driven forces exist.  
**Resolution/evidence:**
- The state array is set read-only on every assignment, so in-place mutation raises.
- Test: `test_force_models_cannot_mutate_simulator_state`.

---

### REV-005 — Architecture scan misses common nondeterminism and layering bypasses
**Severity:** Medium  
**Reviewer claim:** None of the following were flagged: `np.random` attribute access, relative imports, `datetime`/`os.urandom`, or `importlib`.  
**Evidence:** experiment found 0 violations.  
**Affected code/Proof:** `src/tars/validation/architecture.py`  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- Relative imports are resolved.
- Attribute chains are resolved through import aliases.
- `datetime`, `os` and `importlib` are forbidden in the physics core.
- Test: `test_architecture_scan_catches_review_rev005_bypasses`.
- The repository still passes the scan.

---

### REV-006 — Proof record stale; proven revision not identified
**Severity:** Medium  
**Reviewer claim:** `proof/records/M1-orbit.md` predated DR-0008, GMAT and the evidence, and had no SHA.  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Rewritten in `f0f62c3`, after the review record was first committed (`d1ff803`). It now has the proven revision `dfe4615`, evidence links, the GMAT and VAL-0004/0005 results, this review, and BLOCKED status. The re-verification found it NOT RESOLVED at `d1ff803` and resolved at `f0f62c3`.

---

### REV-007 — Node-based orbit counting breaks for equatorial orbits, which the schema allowed
**Severity:** Low  
**Evidence:** at i = 0° the run times out; at i = 180° crossings are detected from round-off noise.  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- The schema now requires 0° < i < 180°.
- Test: `test_equatorial_orbits_rejected`.
- If equatorial missions are needed, count orbits by argument of latitude or true longitude.

---

### REV-008 — Kepler oracle fails on some cases it claimed to handle
**Severity:** Low  
**Evidence:**
- An elliptic case cycled at 1 ulp above rtol.
- 226 of 500 hyperbolic cases did not converge, from a poor initial guess.

**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- Newton stops at the round-off floor, when corrections stop shrinking at ≤ 1e-12 relative.
- Vallado's Algorithm 8 hyperbolic initial guess is used.
- The docstring now states the tested ranges.
- Tests: `test_rev008_roundoff_limited_elliptic_case_converges` (4 000 random ellipses) and `test_rev008_hyperbolic_cases_converge_and_match_dop853` (500 hyperbolas; DOP853 agreement 1e-9 relative).

---

### REV-009 — Metrics use only the 60 s samples; the "final" metric isn't the final state
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- The runner always samples the final state, at tick 5371 (t = 53 710 s).
- Test: `test_final_state_is_sampled_and_validated`.
- The golden events hash was regenerated; the final state is unchanged.

---

### REV-010 — Misspelled threshold groups silently disable gating
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- `load_thresholds` rejects groups that match no validator.
- Test: `test_threshold_groups_must_match_validators`.

---

### REV-011 — `period_metrics` assumes an ascending-node start
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:**
- It raises unless the initial state is on the ascending node.
- Test: `test_period_metrics_require_ascending_node_start`.

---

### REV-012 — GMAT epoch column drifts from the ElapsedS label (informational)
**Severity:** Low  
**Evidence:** the drift reaches −1.07e-4 s by 53 640 s. GMAT vs Kepler at the ElapsedS times is 7 µm, so the states are at the labelled times.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** No impact for time-invariant M1 dynamics. The cause is unverified; the hypothesis is rounding in GMAT's MJD epoch bookkeeping.  
**Resolution/evidence:** Documented in the GMAT README, with an action for the first time-dependent force model.

## Addendum: reviewer re-verification of fixes
**Reviewer:** the same independent reviewer agent.  
**Revisions:** `d1ff803` verified fully, `80e1fc4` checked for regressions, `f0f62c3` checked briefly. Each was checked in a clean `git archive` copy.  
**Regression check:** 109 tests pass; m1_proof PASS on all 7 checks; GMAT compare and cross-platform validators exit 0.

| Finding | Re-verification | Notes |
|---|---|---|
| REV-001 | PARTIAL, correctly escalated | Exact provenance checks work. A μ of 3.986004421e14 still passes the current numeric gate, so DR-0009 is needed. Reviewer tested DR-0009 option A: the real reference passes (margins 2–1.1e4×); Δμ/μ of ±7.5e-10, 1e-12 and 2e-13 all fail regardless of sign. |
| REV-002 | RESOLVED | 2, 90 and 895-row truncations and a duplicated row are rejected |
| REV-003 | RESOLVED (docs) | ADR-0006 should say "pending DR-0009", not "superseded". Done in this commit. |
| REV-004 | RESOLVED | Residual: deliberate writes via `v.base`; not preventable in Python and not a finding |
| REV-005 | RESOLVED | Residual: `__import__`, `getattr(np, "random")`, star imports. Acceptable for a static backstop to replay. |
| REV-006 | Resolved at `f0f62c3` | Not resolved at `d1ff803` |
| REV-007 | RESOLVED | Near-equatorial orbits (1e-9°) still count correctly |
| REV-008 | RESOLVED within stated ranges | 0/4000 ellipses and 0/500 perigee hyperbolas fail. 6/500 far-hyperbolic back-propagations (\|r\| ~1e9 m) do not converge; outside the documented range and M1 use. |
| REV-009 – REV-012 | RESOLVED | — |

### REV-013 — The review record claimed re-verification before it happened
**Severity:** Medium (process)  
**Reviewer claim:**
- At `d1ff803` the gate box "fixes re-verified by the reviewer (see addendum)" was ticked with no addendum.
- The REV-006 resolution described a rewrite that had not happened yet.

**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. I wrote both in anticipation of work in progress, which proof/definition-of-done.md forbids ("claiming tests/checks were run when they were not").  
**Resolution/evidence:**
- This addendum now exists.
- REV-006's resolution is tied to its actual commit.
- The re-test box cites the actual evidence.
- Lesson recorded in playbook/delegation.md: write review and Proof records only after the work they describe is committed.

### REV-014 — Cross-platform final-state bound reused for the script's initial-state literals
**Severity:** Low  
**Reviewer claim:** the bound approved for 10-orbit accumulated differences (1e-4 m, 1e-7 m/s) is applied to initial-state literals that differ by about 1 ulp. That is a tolerance used for a quantity it was not approved for.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. It is harmless (it only loosens a check that was added after the review), but it is not an approved tolerance for this quantity.  
**Resolution/evidence:**
- Approved in DR-0009 (1e-6 m, 1e-9 m/s). `gmat_m1.py compare` now uses these bounds in place of the interim cross-platform bound.

### REV-015 — Evidence at `d1ff803` was stale
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Regenerated at `dfe4615` (overall PASS, clean tree). It will be regenerated again after DR-0009 changes.

## Proof gate
- [x] All Critical findings resolved (none raised)
- [x] All High findings resolved: REV-001 resolved via DR-0009
- [x] Every substantive finding has an explicit disposition
- [x] Accepted fixes have been re-tested: 109 tests and the full suite at `dfe4615`; independently re-verified by the reviewer (addendum below)
- [x] No escalated scientific claims remain without authoritative evidence. REV-001's physics was independently re-derived by the implementer.

**Review gate result:** PASS. REV-001 was resolved via DR-0009, every finding is dispositioned, and accepted fixes were re-tested and re-verified.

## Post-merge note (2026-10-10): REV-012 root cause
REV-012's "cause unverified" hypothesis is now verified: per-command double-MJD epoch re-rounding in GMAT (VAL-0010, DR-0016). M1 is unaffected. The disposition above is unchanged.
