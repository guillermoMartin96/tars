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
