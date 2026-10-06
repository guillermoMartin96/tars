"""Analytic two-body propagation with universal variables (validation oracle).

Solves the Kepler problem exactly (to floating-point precision) for any conic.
References: Curtis (2014) Algorithms 3.3-3.4; Vallado (2013) §2.3, Algorithm 8.

For bound orbits the requested time is first reduced modulo the period, which
keeps the universal anomaly small and avoids precision loss over many orbits.
"""

from __future__ import annotations

import math

import numpy as np

from tars.sim.state import Vector

_SERIES_LIMIT = 0.1
_SERIES_TERMS = 12


def stumpff_c(z: float) -> float:
    """C(z) = (1 - cos sqrt z) / z, with its series used near z = 0."""
    if abs(z) < _SERIES_LIMIT:
        # sum_k (-z)^k / (2k + 2)!
        return sum((-z) ** k / math.factorial(2 * k + 2) for k in range(_SERIES_TERMS))
    if z > 0.0:
        return (1.0 - math.cos(math.sqrt(z))) / z
    return (math.cosh(math.sqrt(-z)) - 1.0) / (-z)


def stumpff_s(z: float) -> float:
    """S(z) = (sqrt z - sin sqrt z) / sqrt(z)^3, with its series used near z = 0."""
    if abs(z) < _SERIES_LIMIT:
        # sum_k (-z)^k / (2k + 3)!
        return sum((-z) ** k / math.factorial(2 * k + 3) for k in range(_SERIES_TERMS))
    if z > 0.0:
        sz = math.sqrt(z)
        return (sz - math.sin(sz)) / sz**3
    sz = math.sqrt(-z)
    return (math.sinh(sz) - sz) / sz**3


def propagate(
    r0: Vector,
    v0: Vector,
    dt: float,
    mu: float,
    rtol: float = 1e-15,
    max_iter: int = 100,
) -> tuple[Vector, Vector]:
    """Exact two-body state (r, v) after ``dt`` seconds from (r0, v0)."""
    r0 = np.asarray(r0, dtype=np.float64)
    v0 = np.asarray(v0, dtype=np.float64)
    if dt == 0.0:
        return r0.copy(), v0.copy()
    sqrt_mu = math.sqrt(mu)
    r0n = float(np.linalg.norm(r0))
    vr0 = float(np.dot(r0, v0)) / r0n
    alpha = 2.0 / r0n - float(np.dot(v0, v0)) / mu  # 1/a

    if alpha > 0.0:
        period = 2.0 * math.pi / (sqrt_mu * alpha**1.5)
        dt = math.fmod(dt, period)

    chi = sqrt_mu * abs(alpha) * dt if alpha != 0.0 else sqrt_mu * dt / r0n
    for _ in range(max_iter):
        z = alpha * chi * chi
        c, s = stumpff_c(z), stumpff_s(z)
        F = (
            r0n * vr0 / sqrt_mu * chi * chi * c
            + (1.0 - alpha * r0n) * chi**3 * s
            + r0n * chi
            - sqrt_mu * dt
        )
        dF = r0n * vr0 / sqrt_mu * chi * (1.0 - z * s) + (1.0 - alpha * r0n) * chi * chi * c + r0n
        delta = F / dF
        chi -= delta
        if abs(delta) <= rtol * max(1.0, abs(chi)):
            break
    else:
        raise RuntimeError("universal Kepler equation did not converge")

    z = alpha * chi * chi
    c, s = stumpff_c(z), stumpff_s(z)
    f = 1.0 - chi * chi / r0n * c
    g = dt - chi**3 / sqrt_mu * s
    r = f * r0 + g * v0
    rn = float(np.linalg.norm(r))
    fdot = sqrt_mu / (rn * r0n) * (z * chi * s - chi)
    gdot = 1.0 - chi * chi / rn * c
    v = fdot * r0 + gdot * v0
    return r, v
