# Decision Request: M2 validation strategy, GMAT finite-burn reference, REV-012, and candidate tolerances

**Status:** CONDITIONALLY APPROVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-09  
**Related milestone/issue:** Milestone 2 — Propulsion ([plan](../../milestones/M2-propulsion.md))

## Problem
A finite burn breaks the M1 oracle: there is no closed-form solution for a powered arc in a gravity field. M2 needs a set of independent references that together prove the propulsion physics. Each M2 gate also needs a tolerance with a justified basis. This request covers:
- the oracles;
- whether and how GMAT gates M2;
- the deferred REV-012 epoch drift, whose trigger M2 reaches;
- the *method* and *candidate values* for thresholds.

Final threshold values follow the M1 precedent (DR-0008). They are re-measured on the implemented code across platforms, then submitted for approval in a dedicated threshold DR before any Proof claims them.

## Proposed oracles (converging evidence, playbook/science.md)
| # | Oracle | What it proves | Independence |
|---|---|---|---|
| O1 | **Mass law:** propellant used = F·T/(Isp·g0) | mass flow and cutoff timing are exact | analytic |
| O2 | **Rocket equation:** sensed Δv = Isp·g0·ln(m0/mf) | thrust acceleration F/m integrated correctly, independent of gravity and direction | analytic |
| O3 | **Free-space powered motion** (unit level, no gravity, fixed direction): v(t) = v0 + c·ln(m0/m)·û and x(t) = x0 + v0·t + c·[t − (m/ṁ)·ln(m0/m)]·û, with c = Isp·g0 | thrust + mass + integrator coupling, no orbital effects | analytic (derived from the rocket equation; derivation in the M2 plan) |
| O4 | **Independent high-accuracy reference:** SciPy DOP853 (rtol 1e-13), integrated across burn boundaries | full powered-arc trajectory | independent integrator; SciPy is already a dev-only test dependency (VAL-0001) |
| O5 | **Post-burn Kepler:** coast arcs vs exact two-body propagation of the cutoff state | the coast after the burn is pure two-body | existing validated oracle (VAL-0001) |
| O6 | **Impulsive limit:** at fixed Δv, finite − impulsive SMA ∝ T_burn² (order 2) | the finite-burn model converges to textbook impulsive maneuver theory (vis-viva with Δv from the rocket equation) | analytic theory + convergence order |
| O7 | **Direction signs:** prograde increases SMA and energy; retrograde decreases them; inclination and RAAN unchanged to round-off for in-plane burns | pointing and frame definitions | analytic |
| O8 | **RK4 convergence order** through a burn (step splitting) | integrator correctness with discontinuities | numerical self-consistency |
| O9 | **GMAT R2026a finite burn** (`ChemicalThruster` VNB, `DecrementMass`, `GravitationalAccel = 9.80665`) | external trusted tool | external; VAL-0009 |

## Options — role of GMAT
### A — GMAT gated, after the REV-012 investigation (recommended)
- Generate the GMAT M2 script deterministically from the approved scenario, as in M1 (`gmat_m1.py` pattern, extended).
- Commit the script, report and metadata with provenance and the DR-0009 replacement guard.
- Gate:
  - ours vs GMAT;
  - GMAT vs O4;
  - GMAT mass vs O1;
  - exact configuration checks, including the `GravitationalAccel` line and thruster parameters (the VAL-0009 trap).
- **Precondition:** investigate REV-012 (GMAT epoch bookkeeping) first. Its trigger ("before the first time-dependent force model") is reached. VAL-0009 attributes the GMAT burn residual (1.85e-7 s shorter burn) to sub-µs epoch quantization, the same family. The investigation documents the cause or bounds it, and fixes how comparison times are aligned (ElapsedSecs vs GMAT epoch).

**Pros**
- Follows the validation hierarchy (GMAT primary reference).
- Honors the Tech Lead's REV-012 deferral condition.
- VAL-0009 shows 1.2 cm agreement, so the gate is feasible.

**Cons**
- REV-012 work comes first. Budget: one focused investigation; escalate if unresolved.

### B — GMAT gated now; bound the epoch effect analytically, REV-012 left open
**Pros**
- Faster.

**Cons**
- Contradicts the recorded deferral trigger. Leaves an unexplained mechanism in a gated comparison.

### C — GMAT informational only for M2; gates from O1–O8
**Pros**
- No external-tool dependency for the Proof.

**Cons**
- Drops the primary external reference for the first new physics since M1. Contrary to playbook/science.md.

## Candidate tolerances (measured basis; NOT approved; to be re-measured)
Measured values are from VAL-0008/0009 on the reference host, using the research scripts, not project code. The candidates follow the DR-0008 convention: about 2× measured for truncation-type errors; magnitude-relative bounds for round-off-type quantities (testing.md lesson); analytic bounds where a mechanism is known.

| Gate | Measured | Candidate | Basis |
|---|---|---|---|
| O1 propellant used vs analytic, relative to initial mass | 3.8e-15 | ≤ 1e-12 | round-off class; RK4 exact for linear mass; cross-platform headroom |
| O2 sensed Δv vs rocket equation, relative to Δv | 1.2e-14 | ≤ 1e-12 | round-off class |
| O3 free-space position / velocity, relative | not yet measured | set from measurement | to be measured in T1 |
| O4 ours vs DOP853 at first tick after cutoff | 7.7e-4 m, 1.2e-6 m/s | ≤ 2e-3 m, ≤ 3e-6 m/s | ≈ 2× measured |
| O4 ours vs DOP853 at 53 700 s | 0.290 m, 3.35e-4 m/s | ≤ 0.6 m, ≤ 7e-4 m/s | ≈ 2× measured; equals the approved M1 limits for the same horizon and dt |
| O5 coast vs Kepler from cutoff state | measured with project code | set from measurement | expected ≈ M1 RK4 coast error |
| O6 impulsive-limit order (worst pair) | 1.9952 | \|p − 2\| ≤ 0.05 | 10× measured deviation (0.0048); first pair pre-asymptotic |
| O6 slice: \|ΔSMA_finite/ΔSMA_impulsive − 1\| | 2.6e-6 | ≤ 1e-5 | ≈ 4× measured; physical finite-burn effect, scenario-specific |
| O7 signs | exact | sign checks; ΔINC, ΔRAAN ≤ round-off bound to be measured | — |
| O8 fitted RK4 order through burn, dt ∈ {10, 5, 2.5, 1} | pairs 10→5: 4.31; 5→2.5: 4.18 | \|p − 4\| ≤ 0.5 | as approved for M1 (DR-0008). The 20→10 pair is pre-asymptotic (4.47) and excluded. |
| O9 ours vs GMAT at 53 700 s | ≈ 0.29 m expected | ≤ 0.6 m, ≤ 7e-4 m/s | our RK4 error dominates, as in M1 |
| O9 GMAT vs DOP853 at 53 700 s | 1.17e-2 m, 1.34e-5 m/s | ≤ 2.5e-2 m, ≤ 3e-5 m/s | ≈ 2× measured; mechanism quantified in VAL-0009 (REV-012 to confirm) |
| O9 GMAT propellant vs analytic | 3.0e-8 kg | ≤ 1e-7 kg | analytic: ṁ × (1 MJD ulp ≈ 3.14e-7 s per burn boundary × 2) = 1.0e-7 kg |
| O9 GMAT configuration | — | exact | regenerated script equality (incl. `GravitationalAccel`, C1, K1, masses); metadata constants |
| Determinism, same platform | — | byte-identical | DR-0006 |
| Cross-platform, M2 golden final state | not yet measured | set from CI measurement | DR-0006 method; M1 bounds not assumed to transfer (a burn may amplify ulp differences) |
| **M1 regression** | — | M1 events sha256 = `7a4e1877…` on reference host; all approved M1 gates unchanged | DR-0013 4A |

## Recommendation
**Option A** (GMAT gated after the REV-012 investigation), oracles O1–O9, and the threshold *method* above. Approval of candidate *values* is requested later in a threshold DR, after re-measurement on the implemented simulator across three platforms, like DR-0008.

## Impact
- Architecture: new `toolbox/validators/m2_proof.py`, GMAT M2 workflow (`gmat_m2` or a generalized `gmat_m1.py`), `proof/thresholds/m2.json`. `KNOWN_VALIDATORS` is extended so M2 groups are consumed (REV-010 guard).
- Science/validation: seven analytic/independent oracles plus GMAT; REV-012 closed or bounded.
- Dependencies: none new (SciPy stays dev-only).
- Development effort: moderate to high (validators, GMAT workflow, three-platform measurement).
- Token/compute impact: low; all deterministic.
- Reversibility: high until thresholds are approved.

## Blocked work
- GMAT M2 reference generation (until REV-012 is investigated); threshold approval (until measurement).

## Work continuing independently
- REV-012 investigation (needs no propulsion code); O1–O3 unit tests once DR-0011 is approved.

## Requested response
`A` / `B` / `C`; approve or amend the oracle set and the threshold method.

## Resolution
**Decision:** CONDITIONALLY APPROVED (Tech Lead, 2026-10-09).

**Approved now:**
- the validation **methodology**: oracles O1–O9, converging evidence, and the threshold method (re-measure on the implementation across platforms, then a threshold DR);
- GMAT as a gated reference in principle (option A).

**Not approved / conditions:**
- **No numerical tolerance is final.** The "Candidate" column above remains candidate values only.
- **No GMAT acceptance gate is final.**
- Neither may be finalized until (1) REV-012 has been investigated and its findings reviewed, and (2) measurements on the implemented code are available.
- GMAT validation thresholds and the M1 baseline must not be modified silently.

**Reasoning/notes:** The REV-012 investigation was authorized the same day in an isolated worktree.  
**Follow-up:** REV-012 findings (VAL-0010); threshold DR after T5/T6 measurements; `proof/thresholds/m2.json` only after that approval.

