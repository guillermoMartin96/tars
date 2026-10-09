"""Centralized physical constants (DR-0003, SCI-0005).

Physics code must receive constants as parameters; no other module may hard-code
these values. A test enforces that the WGS 84 literals appear only in this file.
"""

from __future__ import annotations

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
