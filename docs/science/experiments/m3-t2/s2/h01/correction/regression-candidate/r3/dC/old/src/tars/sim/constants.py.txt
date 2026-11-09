"""Centralized physical constants (DR-0003, SCI-0005).

Physics code must receive constants as parameters; no other module may hard-code
these values. A test enforces that the WGS 84 literals appear only in this file.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EarthConstants:
    """Earth constants needed by the M1 model.

    Attributes:
        name: Identifier of the constants source, recorded in events.
        mu: Geocentric gravitational constant GM [m^3/s^2].
        equatorial_radius: Reference (equatorial) radius [m]; altitude datum (SCI-0006).
    """

    name: str
    mu: float
    equatorial_radius: float

    def __post_init__(self) -> None:
        if not (self.mu > 0.0 and self.equatorial_radius > 0.0):
            raise ValueError("mu and equatorial_radius must be positive")


# NGA.STND.0036_1.0.0_WGS84 (2014), defining parameters.
WGS84 = EarthConstants(
    name="WGS84",
    mu=3.986004418e14,
    equatorial_radius=6378137.0,
)

EARTH_CONSTANTS: dict[str, EarthConstants] = {WGS84.name: WGS84}

# Earth's second zonal harmonic, approximate (SCI-0001; Vallado 2013 §9.6). Informational
# only: used to compare GMAT's J2 node drift with the first-order analytic rate. The M1
# force model does NOT include J2 (DR-0002).
EARTH_J2_APPROX = 1.0826e-3

# Standard acceleration of gravity g_n, exact by definition (3rd CGPM, 1901; NIST CODATA).
# Converts specific impulse [s] to effective exhaust velocity c = Isp * g0 (SCI-0009). It is
# a units convention, not local gravity. GMAT's ChemicalThruster default is 9.81 (VAL-0009).
STANDARD_GRAVITY = 9.80665


# M3 J2 identity (DR-0024 Q1-Q3, DR-0029 P10; SCI-0013). The canonical stored value is the
# EGM2008 tide-free normalized coefficient C̄2,0 from NGA.STND.0036_1.0.0_WGS84 (2014)
# Table 5.1. J2 is always derived from it; no J2 literal is stored anywhere (P10). The
# decimal J2 written in DR-0024 Q1 is the 11-digit display form of the derived value.
EGM2008_C20_TIDE_FREE = -0.484165143790815e-3


def j2_from_c20(c20: float) -> float:
    """Unnormalized J2 from the fully normalized C̄2,0: J2 = -C2,0 = -sqrt(5) C̄2,0.

    The degree-2, order-0 normalization factor is sqrt(2n + 1) = sqrt(5). Only a
    correctly rounded square root and one multiplication are used (IEEE 754), so the
    binary64 result does not depend on a libm implementation.
    """
    return -math.sqrt(5.0) * c20


@dataclass(frozen=True)
class EarthJ2Constants:
    """Earth constants for the M3 J2 model: GM, J2 reference radius and C̄2,0.

    J2 is a derived property, never a stored field, so there is exactly one canonical
    value (DR-0029 P10).

    Attributes:
        name: Identifier of the constant set.
        mu: Geocentric gravitational constant GM [m^3/s^2].
        equatorial_radius: J2 reference radius [m] (DR-0024 Q2).
        c20: Fully normalized C̄2,0 (dimensionless; canonical).
    """

    name: str
    mu: float
    equatorial_radius: float
    c20: float

    def __post_init__(self) -> None:
        if not (self.mu > 0.0 and self.equatorial_radius > 0.0):
            raise ValueError("mu and equatorial_radius must be positive")
        if not math.isfinite(self.c20):
            raise ValueError("c20 must be finite")

    @property
    def j2(self) -> float:
        """Unnormalized J2, derived from ``c20``."""
        return j2_from_c20(self.c20)


# WGS 84 GM and a (unchanged, DR-0024 Q2/Q3) with the EGM2008 tide-free C̄2,0 (Q1).
WGS84_EGM2008_TIDE_FREE = EarthJ2Constants(
    name="WGS84_EGM2008_TIDE_FREE",
    mu=WGS84.mu,
    equatorial_radius=WGS84.equatorial_radius,
    c20=EGM2008_C20_TIDE_FREE,
)
