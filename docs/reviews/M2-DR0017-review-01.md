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

## Addendum: reviewer re-verification (\`c64e73d\`)
**Reviewer:** Codex \`gpt-6.1-sol\`, session \`01a1287f-3d48-73c2-a125-d00c2d533b81\`.  
**Raw:** \`raw/M2-DR0017-codex-reverify.md\`; prompt and scripts are alongside.  
**Verdict:** FAIL.
- F2 and F3 RESOLVED; safeguards 3–7 MET.
- No false rejections in 50 005 reference cases up to 1e9 s.
- All 15 mutations caught; M1 bit-identical.
- Safeguard 1 NOT MET and F1 PARTIAL, because of N1.

### N1 — Subnormal logarithm argument defeats the conservative estimate
**Severity:** Medium  
**Reviewer claim:**
- With Isp ≈ 1e307 s, `(F/m)·dt/c` is subnormal and loses relative precision.
- A burn with exact error 1.0000000005e-7 m/s was accepted as 9.99999998e-8 m/s and executed. The excess is ~5e-17 m/s, physically negligible, but the safeguard is unconditional.
- The reviewer's broader search also found underestimates in both interval orderings.

**Implementer disposition:** \`ACCEPTED\`  
**Implementer reasoning:**
- The implementer's own seeded search over the full float range found 2 112 underestimates in 30 000 cases at \`c64e73d\`, and 111 after a first scaling fix.
- Root causes:
  - subnormal log arguments;
  - intermediate under- and overflow;
  - in subnormal-ṁ regimes, F/ṁ ≠ Isp·g0, so the "exact" log form is not even the quantity the simulator integrates.
- The robust answer is the decision's own quantity. Actual acceleration × executed-interval difference, F·|dt|/m_end, is a guaranteed upper bound on ∫F/m dt, and it is tight in practice.

**Resolution/evidence:** Fixed in \`494fa27\`.
- Bound `a_max·|dt|`, with:
  - an end-mass lower bound;
  - frexp/ldexp scaling;
  - outward rounding (16 ulp + 4 smallest subnormals);
  - overflow → inf → reject.
- Tests:
  - the reviewer's N1 configuration is rejected through the simulator;
  - exact ≤ bound ≤ exact·(1+x) against a 60-digit integral of F/m;
  - a seeded adversarial property over the full float range (3 000 cases in CI; 0 underestimates in 90 000 offline over 3 seeds);
  - no false rejection of the reference vehicle up to 1e9 s (5 000 cases; maximum 2.5e-8 m/s).
- Mutation: removing any component of the bound (end-mass choice, slack, scaling, subnormal floor, relative inflation), or shifting the budget or comparison by 1 %, fails tests.
- Re-test:
  - 473 tests pass; ruff clean;
  - M1 Proof PASS; GMAT compare PASS;
  - determinism and cross-platform bit-identical to \`7a4e1877…\`;
  - VAL-0012 unchanged.

## Addendum 2: final re-verifications
**Re-verification 2** (`fd2c418`; session `01a12889-ab04-77e1-97ac-e1ffedb43d14`; raw `raw/M2-DR0017-codex-reverify2.md`): **CONDITIONAL PASS.**
- N1/F1 RESOLVED; safeguards 1 and 3–7 MET.
- Zero underestimates in 92 874 new adversarial cases plus 12 225 repeated cases.
- The reviewer independently confirmed the a_max·|dt| argument, including the dynamics clamp and the propellant floor.
- Zero false rejections in 50 005 reference cases.
- M1 bit-identical.
- New: **N2 (Low)**. Documentation retained a universal c·|ln| identity and an unqualified x/2 excess.

### N2 — Documentation retained an invalid exact logarithmic identity
**Severity:** Low  
**Implementer disposition:** `ACCEPTED`  
**Resolution/evidence:** Fixed in `d8829a2` (documentation only).
- ∫F/m dt is stated as authoritative. The c·|ln| identity is qualified (unrounded ṁ, unclamped mass). The excess is given as x/ln(1+x) − 1, asymptotically x/2.
- While writing the fix, the implementer first wrote the excess formula incorrectly and corrected it before commit (numerically checked).

**Final verification** (`d8829a2`; session `01a1288c-911d-7cd1-8cc0-5121fd2aabbd`; raw `raw/M2-DR0017-codex-final.md`): N2 RESOLVED; diff is documentation-only (identical executable AST); 473 passed; ruff clean; determinism `7a4e1877…`; safeguards 1–7 MET; no new findings. **Final T2 verdict: PASS.**

## Proof gate
- [x] No Critical findings
- [x] All findings (F1 High, F2, F3, N1, N2) resolved and re-verified by the reviewer
- [x] Every finding dispositioned
- [x] CI green on ubuntu-latest and macos-latest at `d8829a2` (run 38101527076)

**Review gate result: PASS** (reviewer final verdict for T2: PASS).
