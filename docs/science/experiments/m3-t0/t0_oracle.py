"""High-precision reference quantities for the M3 T0 checks (research only; Review 03 M3T0-R3-F1).

An oracle independent of the model's altitude and band-selection code (`t0_model`):

- `true_height(r)`: the geodetic height of a binary64 position, i.e. the exact distance from
  r to the model's ellipsoid E (semi-major axis a = A_WGS84, squared eccentricity e^2 =
  E2_WGS84, both taken as the exact values of the binary64 constants, so b^2 = a^2 (1 - e^2)
  exactly). The foot point q = (p a^2 / (a^2 + t), z b^2 / (b^2 + t)) is found by Newton's
  method on the Lagrange parameter t in 60-digit decimal arithmetic, then h = |r - q|.
  F(t) = p^2 a^2 / (a^2 + t)^2 + z^2 b^2 / (b^2 + t)^2 - 1 is convex and decreasing for
  t > -b^2, and F(0) >= 0 outside E, so Newton from t = 0 increases monotonically to the
  root. Only +, -, *, / and one square root are used: no latitude, no trigonometry.
- `table()`: the pinned atmosphere table read as decimal strings (not binary64).
- `density(h)`: the table density at an exact height h [m], with GMAT's band rule (an
  exact base belongs to the band above), in decimal arithmetic.
- `drag(r, v, mass, cd, area)`: rho(true height) |v - omega Z x r|^2 / (2 B), B = mass /
  (cd area), in decimal arithmetic.
- `top_band_height(rho)`: the exact height in the unbounded top band at which the table
  density equals rho (Review 04 M3T0-R4-F1: used to place points at the smallest normal
  density 2^-1022 and at the rounding-to-zero threshold 2^-1075 of binary64).

Precision: 60 significant digits; the Newton loop stops when the correction is below
1e-45 of a^2, so the height carries far more correct digits than the 1e-9 m effects tested.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from itertools import pairwise
from pathlib import Path

import t0_model as m

D = Decimal

PREC = 60
A = D(m.A_WGS84)
E2 = D(m.E2_WGS84)
A2 = A * A
with localcontext() as _c:
    _c.prec = PREC
    B2 = A2 * (1 - E2)
OMEGA = D(m.OMEGA_E)


def table(path: Path = m.TABLE_COPY) -> tuple[tuple[D, D, D], ...]:
    """(base [m], rho0 [kg/m^3], scale height [m]) from the decimal strings of the file."""
    if m.sha256(path) != m.TABLE_SHA256:
        raise ValueError("atmosphere table digest mismatch")
    rows = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            h, rho, s = (D(x.strip()) for x in line.split(","))
            rows.append((h * 1000, rho, s * 1000))
    return tuple(rows)


TABLE = table()


def true_height(r) -> D:
    """Exact-arithmetic geodetic height of the binary64 point r (outside the ellipsoid)."""
    with localcontext() as c:
        c.prec = PREC
        x, y, z = (D(float(v)) for v in r)
        pp, zz = x * x + y * y, z * z
        t = D(0)
        for _ in range(500):
            ua, wb = A2 + t, B2 + t
            f = pp * A2 / (ua * ua) + zz * B2 / (wb * wb) - 1
            df = -2 * pp * A2 / (ua * ua * ua) - 2 * zz * B2 / (wb * wb * wb)
            step = f / df
            t -= step
            if abs(step) <= A2 * D("1e-45"):
                break
        else:
            raise RuntimeError("foot-point iteration did not converge")
        if t < 0:
            raise ValueError("point inside the ellipsoid")
        p = pp.sqrt()
        fp, fz = p * A2 / (A2 + t), z * B2 / (B2 + t)
        return ((p - fp) ** 2 + (z - fz) ** 2).sqrt()


def band(h: D) -> int:
    """GMAT's rule: the last band whose base is <= h (an exact base belongs to the band
    above). Written independently of `t0_model.band_index`."""
    if h < TABLE[0][0]:
        raise ValueError("below the table's lower edge")
    return max(i for i, row in enumerate(TABLE) if row[0] <= h)


def density(h: D) -> D:
    with localcontext() as c:
        c.prec = PREC
        base, rho0, scale = TABLE[band(h)]
        return rho0 * (-(h - base) / scale).exp()


def drag(r, v, mass: float, cd: float, area: float) -> D:
    """Reference drag magnitude at the true height of r [m/s^2]."""
    with localcontext() as c:
        c.prec = PREC
        x, y, _ = (D(float(q)) for q in r)
        vx, vy, vz = (D(float(q)) for q in v)
        rel = (vx + OMEGA * y) ** 2 + (vy - OMEGA * x) ** 2 + vz**2
        return density(true_height(r)) * rel * D(cd) * D(area) / (2 * D(mass))


def downward_jumps() -> tuple[D, ...]:
    """Bases where the density drops going up: limit from below > value at the base."""
    out = []
    with localcontext() as c:
        c.prec = PREC
        for (b0, r0, s0), (b1, r1, _) in pairwise(TABLE):
            if r0 * (-(b1 - b0) / s0).exp() > r1:
                out.append(b1)
    return tuple(out)


def top_band_height(rho: D) -> D:
    """Exact height [m] in the top band at which rho0 exp(-(h - base) / H) = rho."""
    with localcontext() as c:
        c.prec = PREC
        base, rho0, scale = TABLE[-1]
        return base + scale * (rho0 / rho).ln()
