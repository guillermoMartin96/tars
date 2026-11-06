"""DL-4 geodetic twin (M3 T2 S2; r2 DL-4, D-8; S2 proposal v11 §3.10).

The DQ-1 (α) operation sequence, re-coded in the test from the packet r1 §5 text, not from
the component. It is compared bit for bit with the component on the same platform (G-08).
It shows output conformance only, not numerical correctness (F5), and not which operations
the component performed (R2-F1). Its independence comes from review (IN-2), not authorship.

The text transcribed is r1 lines 89-94, `docs/milestones/M3-T2-authorization-packet-r1.md`
at K, blob 4537bcadfdea219d740ca95cf4005412d1e29002, verbatim:

    **Operation sequence to reproduce** (`docs/science/experiments/m3-t0/t0_model.py` at
    `a57de3f`, lines 38–42 and 144–162; T0 files are protected and unchanged):
    1. Constants: a = 6378137.0; INV_F = 298.257223563; F = 1.0/INV_F; e2 = F·(2.0 − F). E1's
       "model ellipsoid" is defined by these binary64 values.
    2. x, y, z as binary64; p = hypot(x, y).
    3. Start: φ = atan2(z, p·(1.0 − e2)).
    4. Iterate at most 60 times: s = sin φ; n = a/√(1.0 − e2·s·s); φ_new = atan2(z + e2·n·s,
       p). Stop after the update when |φ_new − φ| ≤ 1e-15.
    5. Height: s = sin φ, c = cos φ; h = p·c + z·s − a·√(1.0 − e2·s·s).

(The quoted lines are wrapped here for the line-length limit; no word is changed.)

The twin has no domain guard and catches nothing. It is called only on listing entries
labelled ``passes`` and only with normalized built-in floats (§3.10). It is never evaluated
at a geometric reject. This module is not collected by pytest (its name does not start
with ``test_``) and imports only ``math`` and typing support (G-12a).
"""

from __future__ import annotations

import math
from typing import Any, NamedTuple

# Step 1 constants, typed from the r1 §5 text (test-side literals are allowed: the
# literal-location tests scan src/ only).
A = 6378137.0
INV_F = 298.257223563
F = 1.0 / INV_F
E2 = F * (2.0 - F)

MAX_ITERATIONS = 60
STOP_TOLERANCE = 1e-15


class TwinRecord(NamedTuple):
    """The twin's record. ``p`` only classifies the expected outcome (G-08); it is never
    compared with a component value. ``iterations`` and ``last_step`` are bookkeeping for
    the RP-9 census; no floating-point operation is added for them."""

    p: float
    h: float
    phi: float
    converged: bool
    iterations: int
    last_step: float


def twin_geodetic(x: float, y: float, z: float, lib: Any = math) -> TwinRecord:
    """r1 §5 steps 2 to 5, operation for operation. Every elementary call goes through
    ``lib`` (in S2 always ``math``; the parameter lets DL-3 supply a witness library)."""
    # Step 2.
    p = lib.hypot(x, y)
    # Step 3.
    phi = lib.atan2(z, p * (1.0 - E2))
    # Step 4: at most 60 times; stop after the update when |phi_new - phi| <= 1e-15.
    converged = False
    iterations = 0
    last_step = math.nan
    for k in range(1, MAX_ITERATIONS + 1):
        s = lib.sin(phi)
        n = A / lib.sqrt(1.0 - E2 * s * s)
        phi_new = lib.atan2(z + E2 * n * s, p)
        last_step = abs(phi_new - phi)
        stop = last_step <= STOP_TOLERANCE
        phi = phi_new
        iterations = k
        if stop:
            converged = True
            break
    # Step 5.
    s = lib.sin(phi)
    c = lib.cos(phi)
    h = p * c + z * s - A * lib.sqrt(1.0 - E2 * s * s)
    return TwinRecord(p, h, phi, converged, iterations, last_step)


# --- G-08 adapter (§3.10 "Required agreement"; not part of the r1 transcription) -------


class TwinStopError(Exception):
    """The twin raised an exception other than ArithmeticError or ValueError: stop 3.
    The point is never skipped and conformance is never assumed."""


class TwinOutcome(NamedTuple):
    """Expected component outcome at a ``passes`` entry, from the twin record."""

    outcome: str  # "accepted" | "overflow" | "non_convergence" | "numerical_failure"
    record: TwinRecord | None  # None only when the twin raised a caught type


def twin_outcome(x: float, y: float, z: float) -> TwinOutcome:
    """Classify the twin's result under the §3.7.10 N1-N5 order (§3.10 adapter)."""
    try:
        rec = twin_geodetic(x, y, z)
    except (ArithmeticError, ValueError):
        return TwinOutcome("numerical_failure", None)
    except Exception as exc:  # any other type: STOP, never skipped (stop 3)
        raise TwinStopError(f"twin raised {type(exc).__name__} at {(x, y, z)!r}") from exc
    values = (rec.p, rec.h, rec.phi)
    if any(math.isnan(v) for v in values):
        return TwinOutcome("numerical_failure", rec)
    if any(math.isinf(v) for v in values):
        return TwinOutcome("overflow", rec)
    if not rec.converged:
        return TwinOutcome("non_convergence", rec)
    return TwinOutcome("accepted", rec)
