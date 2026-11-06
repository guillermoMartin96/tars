"""Geodetic height and latitude on the model ellipsoid (M3 T2 S2; DQ-1 (α); DR-0029 P8).

``geodetic(r) -> (h, phi)``: the DQ-1 (α) operation sequence of packet r1 §5
(``docs/milestones/M3-T2-authorization-packet-r1.md`` lines 89-94), operation for
operation, behind a domain guard, with post-evaluation numerical rules (S2 proposal v11
§3.7, §3.8 and §3.9; OD-12, I-97).

Check order (the first failing check wins; §3.8):

0. structure and normalization: ``len(r) == 3``; components read as ``r[0], r[1], r[2]``
   (exceptions from that access propagate unchanged); each component reduced to a trusted
   built-in value by ``type()``: ``bool`` -> TypeError; ``float`` subclass ->
   ``float.__float__`` (the stored binary64); ``int`` subclass -> ``int.__index__``;
   anything else -> TypeError;
1. ``not_binary64``: an integer that is not exactly a binary64 value;
2. ``non_finite``: a NaN or infinite component;
3. ``origin``: x == y == z == 0.0 (either signed zero);
4. ``evolute_region``: the exact pre-filter (§3.7.5), then the exact rational predicate
   (§3.7.4) on the closed region;
5. evaluation, E.1: DQ-1 steps 2 to 5 inside a ``try`` that covers exactly E.1 and catches
   only ArithmeticError and ValueError (N1 -> ``numerical_failure``, cause chained);
6. N2 ``numerical_failure``: p, phi or h is NaN;
7. N3 ``overflow``: p, phi or h is infinite;
8. N4 ``non_convergence``: the stop test was not met within 60 iterations;
9. N5: return (h, phi).

What acceptance means: DQ-1's own stop test was met within its limit and the outputs are
finite. It is NOT a demonstration of accuracy (§3.21; OD-12 item 3). Accepted points below
the ellipsoid are report-only (P8). ``numerical_failure`` has an undetermined cause and is
not a domain classification (§3.18 item 15). GeodeticDomainError subclasses ValueError, so
a broad ``except ValueError`` would also catch it (F-17).
"""

from __future__ import annotations

import math
from fractions import Fraction

from tars.sim.constants import WGS84, WGS84_INVERSE_FLATTENING

# The evaluation library (§3.7.10 E.1). Bound to math at import and used ONLY inside E.1;
# fault injection (G-16) replaces it for one test. The post-checks never use it.
_LIB = math
_isnan = math.isnan
_isinf = math.isinf

# DQ-1 step 1 (r1 §5): a from constants.py; F = 1.0/INV_F; e2 = F*(2.0 - F). Correctly
# rounded, so the bits are the same on every platform (X-P2, G-02).
_A = WGS84.equatorial_radius
_F = 1.0 / WGS84_INVERSE_FLATTENING
_E2 = _F * (2.0 - _F)

# Guard constants (§3.7.4), exact rationals on the model ellipsoid: K = a^2 e2^2, W = 1 - e2.
_K = Fraction(_A) ** 2 * Fraction(_E2) ** 2
_W = 1 - Fraction(_E2)
# Pre-filter (§3.7.5): r in E implies |x|, |y|, |z| < 2^16. A proven-sound shortcut, not a
# threshold; it changes no classification.
_PREFILTER = 65536.0

_REASONS = {
    "not_binary64": (
        "input",
        "geodetic input: an integer component is not exactly a binary64 value",
    ),
    "non_finite": ("input", "geodetic input: a component is NaN or infinite"),
    "origin": ("geometric", "geodetic input: the origin has no geodetic height"),
    "evolute_region": (
        "geometric",
        "geodetic input: the point lies in the evolute region (DR-0029 P8)",
    ),
    "numerical_failure": (
        "failure",
        "geodetic evaluation failed; the cause is undetermined and this is not a domain "
        "classification",
    ),
    "overflow": ("numerical", "geodetic evaluation: a result left the binary64 range"),
    "non_convergence": (
        "numerical",
        "geodetic evaluation: the DQ-1 stop test was not met within 60 iterations",
    ),
}


class GeodeticDomainError(ValueError):
    """The single domain/numerical error of ``geodetic`` (D-S2-4 (d)).

    Attributes:
        reason: one of ``not_binary64``, ``non_finite``, ``origin``, ``evolute_region``,
            ``numerical_failure``, ``overflow``, ``non_convergence``.
        category: fixed by the reason: ``input``, ``geometric``, ``numerical`` or
            ``failure`` (``numerical_failure`` only; D-S2-4 (j)).
    """

    def __init__(self, reason: str) -> None:
        category, message = _REASONS[reason]
        super().__init__(message)
        self.reason = reason
        self.category = category


def _normalize(v: object) -> float | int:
    """Step 0: the trusted built-in value of one component (D-S2-4 (h), (h'-1))."""
    t = type(v)
    if issubclass(t, bool):
        raise TypeError("geodetic input: bool is not a coordinate")
    if issubclass(t, float):
        return float.__float__(v)  # type: ignore[arg-type]
    if issubclass(t, int):
        return int.__index__(v)  # type: ignore[arg-type]
    raise TypeError(f"geodetic input: unsupported component type {t.__name__}")


def _to_binary64(v: float | int) -> float:
    """Step 1 on a normalized value: an int must be exactly a binary64 value."""
    if type(v) is float:
        return v
    try:
        f = float(v)
    except OverflowError:
        raise GeodeticDomainError("not_binary64") from None
    if f != v:
        raise GeodeticDomainError("not_binary64")
    return f


def _in_evolute_region(x: float, y: float, z: float) -> bool:
    """Step 4 on finite built-in floats, not the origin (§3.7.4, §3.7.5). Exact."""
    if abs(x) >= _PREFILTER or abs(y) >= _PREFILTER or abs(z) >= _PREFILTER:
        return False
    p2 = Fraction(x) ** 2 + Fraction(y) ** 2
    z2 = Fraction(z) ** 2
    d = _K - p2 - _W * z2
    return d >= 0 and d**3 >= 27 * _K * _W * p2 * z2


def geodetic(r) -> tuple[float, float]:
    """Geodetic height h [m] and latitude phi [rad] of r = (x, y, z) [m], returned as
    (h, phi). Raises GeodeticDomainError (reason, category) or TypeError; see the module
    docstring for the check order. Accepted means DQ-1's stop test was met; it is not a
    statement of accuracy."""
    # Step 0: structure (caller code; its exceptions propagate unchanged) and normalization.
    if len(r) != 3:
        raise TypeError("geodetic input: r must have exactly 3 components")
    c0, c1, c2 = r[0], r[1], r[2]
    n0, n1, n2 = _normalize(c0), _normalize(c1), _normalize(c2)
    # Step 1: not_binary64.
    x, y, z = _to_binary64(n0), _to_binary64(n1), _to_binary64(n2)
    # Step 2: non_finite.
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise GeodeticDomainError("non_finite")
    # Step 3: origin.
    if x == 0.0 and y == 0.0 and z == 0.0:
        raise GeodeticDomainError("origin")
    # Step 4: evolute_region.
    if _in_evolute_region(x, y, z):
        raise GeodeticDomainError("evolute_region")
    # Step 5: E.1, DQ-1 steps 2 to 5 (r1 §5), unchanged; the try covers exactly E.1.
    try:
        p = _LIB.hypot(x, y)
        phi = _LIB.atan2(z, p * (1.0 - _E2))
        converged = False
        for _k in range(1, 61):
            s = _LIB.sin(phi)
            n = _A / _LIB.sqrt(1.0 - _E2 * s * s)
            phi_new = _LIB.atan2(z + _E2 * n * s, p)
            stop = abs(phi_new - phi) <= 1e-15
            phi = phi_new
            if stop:
                converged = True
                break
        s = _LIB.sin(phi)
        c = _LIB.cos(phi)
        h = p * c + z * s - _A * _LIB.sqrt(1.0 - _E2 * s * s)
    except (ArithmeticError, ValueError) as exc:  # N1
        raise GeodeticDomainError("numerical_failure") from exc
    # Post-checks (outside the try), in order N2 to N5.
    if _isnan(p) or _isnan(phi) or _isnan(h):
        raise GeodeticDomainError("numerical_failure")
    if _isinf(p) or _isinf(phi) or _isinf(h):
        raise GeodeticDomainError("overflow")
    if not converged:
        raise GeodeticDomainError("non_convergence")
    return h, phi
