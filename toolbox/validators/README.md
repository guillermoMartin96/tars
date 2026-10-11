# Validators

Deterministic Proof checks. They exit non-zero on failure and write machine-readable results. The logic lives in `src/tars/validation/` (unit-tested in `tests/test_validation.py`, `tests/test_gmat.py`); the files here are thin CLIs.

| Validator | Proves | Used by |
|---|---|---|
| `m1_proof.py` | Mission success, two-body invariants, Kepler-reference error, node-crossing period, RK4 convergence order, in-process determinism, architecture scan. Thresholds come from `proof/thresholds/m1.json`. | proof/physics.md, proof/architecture.md, CI |
| `cross_platform.py` | Final state within the approved bound of the committed golden state (DR-0006, DR-0008) | proof/physics.md, CI |
| `determinism.py` | Byte-identical event logs from fresh processes (DR-0006); `--scenario` for each M2 scenario | proof/mission.md, CI |
| `m2_proof.py` | M2 (T5): oracles O1–O8 (DR-0015) on the reference missions, and exact contract checks: event order and cadence, command/burn traceability, declared receipts, mass bookkeeping, rejected commands change nothing, determinism, DR-0018 stop boundary, same-tick reporting. Thresholds from `proof/thresholds/m2.json` (**provisional** until T7). Logic in `src/tars/validation/m2.py`; missions and declared receipts in `src/tars/validation/m2_missions.py`; false-pass tests in `tests/test_m2_validation.py`. Needs the dev group (SciPy DOP853). | proof/physics.md, proof/mission.md, CI |

The GMAT comparisons are `toolbox/scripts/gmat_m1.py compare` (M1) and `toolbox/scripts/gmat_m2.py compare` (M2 O9, also run inside `m2_proof.py`); see `toolbox/references/gmat/README.md`.
