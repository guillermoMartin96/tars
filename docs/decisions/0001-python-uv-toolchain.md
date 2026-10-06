# ADR-0001: Python 3.12 managed by uv

**Status:** Accepted  
**Date:** 2026-10-05  
**Decision owners:** Guillermo (Tech Lead); implementing engineer

## Context
The project needs a reproducible implementation environment. The machine has only the EOL system Python 3.9.6.

## Options considered
### Option A
Python 3.12 + uv lockfile.

### Option B
System Python.

## Decision
- Python 3.12, installed and managed by uv (user space).
- Dependencies are pinned in `uv.lock`.
- Runtime dependencies: numpy, pydantic.
- Dev dependencies: pytest, ruff.

## Reasoning
- Python 3.12 is a current supported release.
- uv provides an exact lock (needed for DR-0006 determinism) without system changes.

## Consequences
### Positive
- `uv sync` reproduces the environment.
- CI uses the same lock.

### Negative / tradeoffs
- Pure-Python stepping is slow. That is acceptable at M1 scale and revisited if profiling shows otherwise.

## Validation
CI runs `uv sync --locked` and the full test suite.

## Reconsider when
- Performance becomes a bottleneck.
- A compiled core is needed for 3D/real-time.

## Related
- Decision Request: DR-0001
- Proof: proof/PROOF.md standard gate
