| Finding | Status | Evidence |
|---|---|---|
| REV-T1-01 | RESOLVED | Both float32 reproductions match normalized Python-float plans. Tiny-burn cutoff is `600.0000099999997`, with positive consumption. Collapsed `1e16 + 1` and overflowing `1e308 + 1e308` schedules reject. |
| REV-T1-02 | RESOLVED | Original overflowing exhaust-velocity and mass-flow specifications raise `PropulsionSpecError`. Mass-flow underflow and overflowing spacecraft total mass also reject. |
| REV-T1-03 | RESOLVED | The original `0.1/mdot` request completes under both policies, consuming `0.1 kg`. Six fuel amounts and adjacent representable durations confirm: shorter completes, equal completes, longer rejects or explicitly depletes. |
| REV-T1-04 | RESOLVED | Extreme-ratio results are finite: `1418.3924172843322` and `4144653.167389282`. Near-equal masses agree with independent 100-digit Decimal references within approximately one ulp. |
| REV-T1-05 | RESOLVED | The exact frozen-Prograde monkeypatch now produces **2 failures, 116 passes**. Both successive-velocity tracking and the independent orbital reference detect it; orbital position error stalls near `34.10 m`. |
| REV-T1-06 | RESOLVED | Bool/string masses reject with `ValueError` subclasses; two-component velocity rejects. Original `1e±200` vectors normalize correctly. Additional large and subnormal vectors give read-only, unaliased directions. |

### N1 — Positive burn consumption can still underflow to zero

**Severity:** Low  
**Claim:** Derived-quantity validation still permits a positive-duration, positive-thrust burn with zero planned consumption. This is a newly identified residual boundary limitation, not a regression introduced by the fix.  
**Evidence:** `plan_burn(EngineSpec(1e-308, 312), 300, 0, 1e-100)` returns `completed`, positive mass flow `3.268321195444e-312`, and `propellant_used_kg=0.0`; multiplication underflows at `propulsion.py:342`.  
**Suggested fix:** Reject unrepresentable positive consumption, or explicitly document and approve this supported-range limitation.

No other fix-induced defects found. The time-domain sufficiency rule and clamping behave consistently at the tested boundaries. The stricter `abs=0` comparisons pass. The Ruff exclusion preserves verbatim evidence: removing it makes the formatter request changes to the Python block in raw review A; normal repository lint and formatting pass.

The rejection vocabulary escalation remains valid: `invalid_input` is absent from approved DR-0014 §4, despite the enum claiming to be a subset. Before T3 freezes event schemas, either map internal malformed-input failures to `schema_invalid` and approve a schedule-specific code, or approve a vocabulary amendment. The permissive test allowed-set does not establish approval.

Reproduction scripts and logs are under `review_scratch/`; `src/` and `tests/` were unchanged. This archive has no `.git`, so revision identity could not be independently verified.

**CONDITIONAL PASS** — all six original findings resolved; disposition N1 and settle rejection vocabulary. Ran targeted tests (**118 passed**), full suite (**327 passed**), both Ruff checks, original boundary reproductions, scale probes, Decimal references, and frozen-Prograde mutation (**2 expected failures**).