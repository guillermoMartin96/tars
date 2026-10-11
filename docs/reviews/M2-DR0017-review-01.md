# External Review: DR-0017 implementation (final T2 verification)

**Reviewer/model:** OpenAI Codex CLI, model `gpt-6.1-sol` (separate provider), session `01a12877-2546-73c3-996c-fe08567a9e3e`.  
**Date:** 2026-10-10  
**Reviewed revision:** `5b47206`, diff `c01b468..5b47206` (src and tests).  
**Scope:** the implementation of DR-0017 (B + D1a) against the Tech Lead's seven safeguards; regressions to T1/T2 fixes and M1.  
**Raw:** `raw/M2-DR0017-codex.md`; prompt and reviewer probes alongside.

## Summary
**Verdict: FAIL.**

| Safeguard | Status |
|---|---|
| 3 non-finite/unrepresentable inputs | MET |
| 4 vocabulary | MET |
| 5 D1a | MET |
| 6 machine-readable end cause | MET |
| 1 budget enforced | NOT MET (F1) |
| 2 actual acceleration / limitations | PARTIAL |
| 7 boundary tests | PARTIAL (F2) |

The reviewer confirmed no bypass of the check through the public simulator path, and that all earlier T1/T2 fixes and M1 bit-identity hold.

## Findings

### F1 — Floating-point evaluation permits over-budget burns
**Severity:** High  
**Reviewer claim:** the exact formula is right, but its evaluation can underestimate the error. Two configurations that pass spec validation were accepted by `schedule_burn`:
- **Cancellation:** a 1e16 kg tank on a 3 kg dry mass is reported as 8.6e-8 m/s; the exact value is 1.01e-7 m/s.
- **Underflow:** subnormal masses, where ṁ·dt underflows, are reported as 0; the exact value is 2551 m/s. That burn executed.

**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:**
- A rejection bound must never underestimate.
- A seeded search found 6 670 ill-conditioned configurations where an unslackened end mass underestimates by up to 38 %, so the fix must be a conservative bound, not just a reformulation.

**Resolution/evidence:** Fixed in `c64e73d`.
- `timing_delta_v_error_mps()` (now public):
  - uses an end-mass lower bound with the cancellation uncertainty subtracted;
  - forms `F/m_end` before multiplying by dt;
  - applies a small relative inflation;
  - treats NaN as inf.
- Tests:
  - both reviewer configurations are rejected through the simulator;
  - the estimate is never below exact (60-digit arithmetic) at arithmetic extremes, including the 38 % case;
  - a seeded 1 500-case property over huge-tank / small-dry-mass configurations near depletion.
- Mutants removing the slack, or restoring the underflow-prone form, fail.

### F2 — Tests permit the wrong end-mass choice
**Severity:** Medium  
**Reviewer claim:** replacing `max(intended, executed)` with `min` survives all 457 tests, and no test brackets the budget closely.  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `c64e73d`.
- Unit test of the reported value against 60-digit exact for large interval differences in both orderings. The min/max mutant fails 4 tests.
- A 4 000-case scan with a high-acceleration vehicle: about 1 870 cases fall within 2× of the budget, including 16 just over and 19 just under within 1 %.
- The approved value 1e-7 m/s is pinned.
- Mutants shifting the constant or the comparison by 1 % in either direction fail.
- **Implementer observation:** the first scan read the budget from the module and so adapted to a mutated constant. It now uses the approved literal.

### F3 — ADR retained the superseded microsecond bound
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** ADR-0007 is corrected in the commit that records this review. The floor corrects integration round-off only (≤ 3e-13 kg). The D1a timing residual is described separately: retained, not absorbed, and bounded by the DR-0017 budget. The timing-budget note describes the conservative evaluation.

**Equivalent mutant noted:** mapping NaN to 0 instead of inf survives. With validated finite, positive inputs the expression yields inf, not NaN, so the guard is unreachable defence.

## Re-test (implementer) at `c64e73d`
- 470 tests pass; T1/T2 suites pass with `-W error`; ruff clean.
- M1 Proof PASS; GMAT compare PASS.
- Determinism and cross-platform bit-identical to `7a4e1877…`.
- VAL-0012 unchanged.

## Proof gate
- [x] No Critical findings
- [x] High finding F1 fixed
- [x] Every finding dispositioned
- [x] Accepted fixes re-tested by the implementer
- [ ] Reviewer re-verification (requested)

**Review gate result:** BLOCKED, pending re-verification.
