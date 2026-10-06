# ADR-0006: Validation references and determinism strategy

**Status:** Accepted  
**Date:** 2026-10-05  
**Decision owners:** Guillermo (Tech Lead, via DR-0005/DR-0006/DR-0007); implementing engineer

## Context
M1 Proof needs trusted references and a testable definition of determinism. CI must not depend on GMAT.

## Decision
**Oracle 1 — analytic Kepler propagator** (`tars.astro.kepler`)
- The exact two-body solution.
- Itself checked against published textbook worked examples, so it is not validated only against our own integrator.

**Oracle 2 — GMAT** (external)
- GMAT scripts are committed under `toolbox/references/gmat/`. The exported reports (CSV) are committed alongside them with the GMAT version and configuration.
- CI never runs GMAT. Whether CI should also run the comparison against the committed reference, which needs no GMAT install, is **pending DR-0009** (review REV-003). That decision interprets DR-0007's "keep GMAT external validation outside required CI". Until then the comparison runs locally through `toolbox/scripts/run_m1_proof.sh`.

**Determinism**
- Same platform with pinned `uv.lock`: two runs must produce byte-identical `events.jsonl` (compared by SHA-256).
- Cross-platform agreement uses a measured, documented tolerance.

## Reasoning
- Two independent references, one mathematical and one external tool, provide converging evidence (playbook/science.md).

## Consequences
### Positive
- Fast, reproducible CI.
- GMAT comparisons can be re-run by anyone with the pinned version.

### Negative / tradeoffs
- The committed GMAT CSV must be regenerated whenever the scenario changes. The validator checks that the scenario hash matches.

## Validation
- The validators have their own tests.

## Reconsider when
- An additional independent reference is adopted (dependency DR required).

## Related
- Decision Requests: DR-0005, DR-0006, DR-0007
- Proof: proof/physics.md
