| Finding | Status | Evidence |
|---|---|---|
| N1 — Executed past depletion | **PARTIAL** | Original `t=1e9`, dry mass `1e-10 kg` reproduction now executes successfully; represented duration is `0.09999990463256836 s`. Removing step-down fails **8 tests**. Negative RK4 stage propellant remains possible; see N4. |
| N2 — Huge-integer rejection diagnostics | **PARTIAL** | All four numeric `plan_burn` fields reject `10**10000` as `schema_invalid`; unsafe-repr mutation fails **2 tests**. Direct `plan_burn(..., policy=10**10000)` still raises an unstructured `ValueError` at `propulsion.py:368`. Apply `_describe()` there too. |
| N3 — Retrograde/multiple-burn transition coverage | **RESOLVED** | New tests check all four shared-boundary transitions against a Decimal oracle and both orbital directions against independent references. Retrograde-only zero-state mutant now fails **2 tests**, with **193 passing**. |

### N4 — Accepted depletion plans can evaluate negative propellant during RK4

**Severity:** Medium  
**Claim:** Conservative event timing does not prevent accumulated integration round-off from producing negative propellant inside derivative evaluations. The cutoff floor runs too late.

**Evidence:** Reference engine, tank `ṁ × 1 s`, ignition `0`, commanded duration `1 s`, timestep `0.1 s`: RK4 evaluates cutoff-stage propellant as `−5.204170427930421e-17 kg`. With valid dry mass `1e-20 kg`, the accepted plan raises `PropulsionSpecError` on its tenth step because total mass becomes negative. With ordinary dry mass, the cutoff floor conceals the negative stage.

Reproduction: [edges.py](review_scratch/edges.py), output [edges.txt](review_scratch/edges.txt); expanded stage observations: [stages.txt](review_scratch/stages.txt).

**Suggested fix:** Use nonnegative analytic propellant consistently for stage mass and committed accounting, or otherwise enforce the depletion invariant before derivative evaluation. Test stage values and repeated-step depletion with very small dry mass.

### N5 — Conservative depletion cutoff discards unburned propellant

**Severity:** Medium  
**Claim:** For `burn_to_depletion`, shortening the represented interval leaves planned consumption equal to the entire tank. The simulator then removes the actual residual at cutoff.

**Evidence:** Reference engine, ignition `1e9 s`, tank `ṁ × 0.1 s`, commanded duration `1 s`:

- Executed duration: `0.09999990463256836 s`.
- Integrated consumption: `0.01601475858478767 kg`.
- Planned consumption: `0.01601477385766618 kg`.
- Unburned residual forcibly removed: `1.527287851049719e-8 kg`.

`propulsion.py:421` recomputes consumption only for `COMPLETED`; `simulator.py:137` zeros the depleted-policy tank. This contradicts DR-0017’s statements that accounting matches execution and that D1 preserves a residual. Evidence: [reverify.txt](review_scratch/reverify.txt) and [stages.txt](review_scratch/stages.txt).

**Suggested fix:** Compute consumption from the represented interval for both policies and retain its residual. Define the conservative cutoff’s end-cause semantics explicitly, and test subsequent reservation and rocket-equation accounting.

The cutoff loop terminated across **20,080 edge/random input pairs**, exercising both policies, negative ignitions with matching `earliest_t_s`, ignition near zero, huge times and subnormal durations. The maximum observed step-down count was **one**. Zero/negative durations reject before the loop; nonfinite or collapsed cutoffs reject. No termination regression was observed, though the source should document its floating-point iteration bound.

DR-0017 is now framed appropriately: it presents alternatives, a recommendation, tradeoffs and depletion semantics. Before approval, it needs these corrections:

- Fix the D1 residual/accounting description to match the implementation—or fix N5.
- Treat `1e-7 m/s` as a proposed absolute allocation. Comparing it with one `dt=10 s` case cannot establish that timing error is *never* dominant at finer timesteps.
- Specify whether the budget applies per burn or cumulatively, and justify it against mission accuracy requirements.
- Define `m_min` over both intended and represented intervals, including depletion and queued burns. `plan_burn` currently receives no dry mass, so B requires more than a predicate change.
- Clarify that a thrust-magnitude error bound alone does not establish trajectory-error bounds for velocity-dependent pointing and gravity.

I do **not** classify the provisional 1 µs acceptance rule as a defect while DR-0017 is open. Nevertheless, accepted plans can still violate physical mass invariants through N4 and N5.

**FAIL** — Ran full pytest (**401 passed**), ruff lint/format (**passed**), determinism (**`7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`**), adapted reproductions, three mutations and edge/stage probes; review scripts and evidence are under `review_scratch/`, with `src/` and `tests/` unchanged.