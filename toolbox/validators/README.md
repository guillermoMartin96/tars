# Validators

Deterministic Proof checks. They exit non-zero on failure and write machine-readable results. The logic lives in `src/tars/validation/` (unit-tested in `tests/test_validation.py`, `tests/test_gmat.py`); the files here are thin CLIs.

| Validator | Proves | Used by |
|---|---|---|
| `m1_proof.py` | Mission success, two-body invariants, Kepler-reference error, node-crossing period, RK4 convergence order, in-process determinism, architecture scan. Thresholds come from `proof/thresholds/m1.json`. | proof/physics.md, proof/architecture.md, CI |
| `determinism.py` | Byte-identical event logs from fresh processes (DR-0006) | proof/mission.md, CI |

The GMAT comparison is `toolbox/scripts/gmat_m1.py compare` (see `toolbox/references/gmat/README.md`).
