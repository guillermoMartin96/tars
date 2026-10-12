# Decision Request: Verdict relevance for findings about independent-reference outputs (clarifies DR-0019 B)

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-11  
**Related milestone/issue:** M2 T6; DR-0019 (approved B); review record `docs/reviews/M2-T6-review-01.md`, re-verifications 8–11

## Problem
DR-0019 B puts "invalid outputs from independent references" in scope, with the constraint that bad data must never pass merely by flowing through an unmodified helper. Under that scope, re-verifications 8–11 produced 18 findings (F29–F46).
- All are fixed except the two below.
- Several of the fixed ones were corruptions that could not change any verdict. They were fixed anyway, with general consistency checks:
  - Kepler round trip and two-body invariants;
  - dense output reconciled with every solver node;
  - complete stencil validation;
  - reference propellant on the mass law.

Two findings from round 11 remain, and they cannot be closed by checking one reference's outputs against each other:

| Finding | Corruption | Consumed quantity | Effect on any verdict |
|---|---|---|---|
| **F42** | Kepler output negated in **both** the forward and the round-trip call, so the round trip cancels | O6 consumes only the SMA after the midpoint impulse | None. Negating r and v preserves energy, so the SMA is unchanged |
| **F43** | DOP853 interior solver nodes **and** dense output negated *consistently*; endpoints and propellant kept | Interior nodes: none. Dense output: only \|r\| for the altitude extrema | None. \|r\| is unchanged, and every consumed state (segment ends, marks) is exact |

Detecting either needs a *second independent propagator or integrator* to cross-check the first. The same question then applies to that one: a consistent corruption of both would pass. There is no fixed point.

The decision is whether a reference-output finding must show a corruption that **could change a verdict**: a gated metric, an exact check, or a reported value.

## Constraints
- DR-0019 B and its constraint stand. Bad simulator, GMAT, reference, threshold or workflow data must never pass through unmodified helpers.
- No gate, threshold or measured value changes.
- The T6 condition of an unconditional PASS stands.

## Options
### A — Verdict-relevance criterion (recommended)
A reference-output finding is in scope when the corrupted data **could change a verdict or a reported value**.
- Corruptions confined to values no check consumes are not false passes.
- Correlated corruptions of a reference's internal representation that leave every consumed quantity exactly unchanged are not false passes either.
- **Consumed reference outputs keep full validation**, as now:
  - finite;
  - physically consistent (two-body invariants, mass law, round trip, solver-node reconciliation);
  - compared with independent references where the Proof requires it.

Then one final Codex round under DR-0019 B with this criterion stated, requiring an unconditional PASS.

**Pros**
- Matches the purpose of a false-pass review: a wrong Proof verdict.
- Bounded.
- Keeps every check built so far.

**Cons**
- Accepts that a reference could, in principle, carry internally inconsistent values that nothing uses.

### B — Add second references for cross-validation
- An independent integrator (for example SciPy Radau or LSODA) cross-checks DOP853 at every consumed mark.
- An independent Kepler formulation cross-checks `tars.astro.kepler`.

**Pros**
- Closes F42 and F43 for single-reference corruption.

**Cons**
- Roughly doubles reference cost.
- Does not close consistent corruption of both references, so the same question returns.

### C — Continue review rounds without a criterion
**Cons**
- Unbounded: each round can construct a new invariant-preserving corruption of unconsumed or internal reference data.

## Recommendation
**A.** Every consumed reference quantity is already validated for finiteness and physical consistency, and compared where the Proof requires. F42 and F43 change no verdict. Stating the criterion makes the PASS meaningful and bounded, and it narrows nothing that matters to the Proof's correctness.

## Impact
- Architecture: none.
- Science/validation: no gate or value change. It clarifies what a reference-output finding must demonstrate.
- Development effort:
  - A: one review round;
  - B: moderate (second references);
  - C: open-ended.
- Reversibility: high.

## Blocked work
- The final T6 review round and the T6 checkpoint.

## Work continuing independently
- F44–F46 from round 11 are fixed and mutation-tested; they are in scope under every option. Nothing else has started.

## Requested response
`A` / `B` / `C` / `discuss`.

## Resolution
**Decision:** <pending>  
**Reasoning/notes:**  
**Follow-up:**
