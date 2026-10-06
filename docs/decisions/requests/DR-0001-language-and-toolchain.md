# Decision Request: Language and toolchain for the headless simulator

**Status:** RESOLVED  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-05  
**Related milestone/issue:** Milestone 1 — Orbit

## Problem
No implementation language or environment had been chosen. The only Python interpreter on the development machine is the macOS system Python 3.9.6, which reached end-of-life in October 2025.

## Constraints
- The deterministic core must run without an LLM.
- The Playbook pre-approves NumPy, SciPy, Pydantic, and pytest.
- The environment must be reproducible, with pinned dependencies (needed for D6 determinism).

## Options
### A — Python 3.12 managed by uv (with numpy, pydantic, pytest, ruff)
**Pros**
- Matches the Playbook's pre-approved ecosystem.
- `uv.lock` gives exact, reproducible dependency pins.
- Python is installed in user space, with no system changes.

**Cons**
- Pure-Python stepping is slower than compiled code. That is acceptable at M1 scale (about 5 400 steps).

### B — System Python 3.9
**Pros**
- Already present.

**Cons**
- End-of-life, no lockfile workflow, and machine-specific.

## Recommendation
A.

## Impact
- Architecture: none beyond language choice.
- Science/validation: none.
- Dependencies: numpy, pydantic, pytest (pre-approved); ruff (dev-only linter).
- Development effort: low.
- Token/compute impact: deterministic tooling reduces LLM checking.
- Reversibility: moderate (language choice).

## Blocked work
- All code.

## Work continuing independently
- Decision records and scientific assumptions.

## Requested response
`A` / `B` / `discuss`

## Resolution
**Decision:** APPROVED — A.  
**Reasoning/notes:** Use Python 3.12 managed by uv with numpy, pydantic, pytest, and ruff. Do not depend on system Python.  
**Follow-up:** `pyproject.toml` + `uv.lock`; `.python-version` pinned to 3.12.
