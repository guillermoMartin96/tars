| Finding | Status | Evidence |
|---|---|---|
| N1 — Execution past depletion | **RESOLVED** | Original large-time cases succeed under both policies. Across 20,080 edge/random pairs, accepted intervals never exceed depletion; maximum step-down count: one. Removing step-down fails 8 tests. |
| N2 — Huge-integer diagnostics | **RESOLVED** | All four numeric fields and `plan_burn(policy=10**10000)` return `schema_invalid`. Reverting policy formatting fails 1 test; reverting scalar formatting fails 2. |
| N3 — Transition-state coverage | **RESOLVED** | Retrograde-only transition-state mutation fails 2 tests. |
| N4 — Negative RK4-stage mass | **RESOLVED** | Original raw stage still reaches `−5.204170427930421e−17 kg`, but effective mass remains at least the valid dry mass, `1e−20 kg`; execution succeeds. Removing the clamp fails 1 test. |
| N5 — Discarded residual | **RESOLVED** | Both policies plan consumption `0.01601475858478767 kg` and retain approximately `1.52728785e−8 kg`. Actual-versus-planned residual differs by only `−3.47e−18 kg`. Restoring full-tank consumption fails 2 tests. |

Clamp and accounting checks found no new implementation regression:

- **16 non-depletion comparisons** against the unclamped implementation were byte-identical, including transition states. M1 determinism retains the expected hash.
- The clamp does not validate arbitrary negative stage values; it could conceal an unrelated accounting bug locally. No such bug was reproduced. A doubled-consumption mutation, with the clamp retained, fails **17 tests**.
- Cutoff flooring zeros an analytically empty tank and bounds negative integration round-off; positive residuals remain.
- A subsequent burn successfully consumes a representable tiny remainder of `1.60147738558e−13 kg`. Unrepresentable subsequent intervals return `burn_unschedulable` without changing the retained fuel or reservations.

Reproductions and outputs are in [review_scratch](review_scratch/), particularly [probes.txt](review_scratch/probes.txt), [stages.txt](review_scratch/stages.txt), and [edges.txt](review_scratch/edges.txt).

### N6 — DR-0017 retains an unsupported accuracy claim

**Severity:** Low  
**Claim:** The Impact section contradicts the corrected budget discussion.

**Evidence:** [DR-0017](docs/decisions/requests/DR-0017-burn-timing-fidelity-and-depletion-boundary.md:93) still says “timing representation provably sub-dominant to integration error.” Option B correctly acknowledges that integration error can fall below the proposed allocation at finer timesteps and that no mission-level requirement currently justifies the budget.

**Suggested fix:** Replace that Impact statement with “Explicit per-burn timing-error allocation; depletion semantics explicit.” Keep sub-dominance claims limited to the measured reference case.

DR-0017 incorporates the substantive requested corrections: D1a/D1b, retained-residual accounting, a per-burn absolute allocation, mass over both intervals with queued consumption, the required scheduling context, and the trajectory-bound limitation. It is **decision-ready after the N6 wording correction**. “Plan = execution exactly” should also say “to round-off,” consistent with its implementation description.

**CONDITIONAL PASS** — T2 implementation is complete apart from DR-0017’s open decision and the minor text correction above; the provisional 1 µs rule is not a defect. Ran full pytest (**404 passed**), ruff lint/format (**passed**), M1 proof (**PASS**), determinism (**`7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`**), reproductions, edge/stage probes, and seven mutations. No `src/` or `tests/` edits.