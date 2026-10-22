import math
import re
from dataclasses import fields
from fractions import Fraction

import pytest

from tars.sim.constants import (
    EGM2008_C20_TIDE_FREE,
    WGS84,
    WGS84_EGM2008_TIDE_FREE,
    EarthConstants,
    EarthJ2Constants,
    j2_from_c20,
)
from tests.conftest import REPO_ROOT


def test_wgs84_defining_parameters():
    # NGA.STND.0036_1.0.0_WGS84 (2014).
    assert WGS84.mu == 3.986004418e14
    assert WGS84.equatorial_radius == 6378137.0


def test_constants_are_immutable_and_validated():
    with pytest.raises(AttributeError):
        WGS84.mu = 1.0  # type: ignore[misc]
    with pytest.raises(ValueError):
        EarthConstants("bad", mu=-1.0, equatorial_radius=1.0)


def test_wgs84_literals_only_in_constants_module():
    """DR-0003: constants are centralized, never scattered through code."""
    pattern = re.compile(r"3\.986004418e14|398600\.4418|6378137(\.0)?\b|6378\.137")
    offenders = [
        path.relative_to(REPO_ROOT)
        for path in (REPO_ROOT / "src").rglob("*.py")
        if path.name != "constants.py" and pattern.search(path.read_text())
    ]
    assert offenders == []


def test_standard_gravity_literal_only_in_constants_module():
    """SCI-0009: g0 is defined once; a stray 9.81 or 9.80665 would bypass it."""
    pattern = re.compile(r"9\.80665|\b9\.81\b")
    offenders = [
        path.relative_to(REPO_ROOT)
        for path in (REPO_ROOT / "src").rglob("*.py")
        if path.name != "constants.py" and pattern.search(path.read_text())
    ]
    assert offenders == []


# --- M3 J2 identity (DR-0029 P10: canonical C̄2,0, J2 derived) -------------------------


def _is_nearest(value: float, exact: Fraction) -> bool:
    """True if ``value`` is a binary64 nearest to ``exact`` (correct rounding)."""
    err = abs(Fraction(value) - exact)
    neighbours = (math.nextafter(value, -math.inf), math.nextafter(value, math.inf))
    return all(err <= abs(Fraction(n) - exact) for n in neighbours)


def test_c20_is_the_published_nga_value():
    # NGA.STND.0036_1.0.0_WGS84 Table 5.1, EGM2008 tide-free: -0.484165143790815e-3.
    # The shortest repr reproduces the published 15 digits, so the double carries them.
    assert float("-0.484165143790815e-3") == EGM2008_C20_TIDE_FREE
    assert repr(EGM2008_C20_TIDE_FREE) == "-0.000484165143790815"
    assert WGS84_EGM2008_TIDE_FREE.c20 == EGM2008_C20_TIDE_FREE


def test_m3_set_reuses_the_wgs84_gm_and_radius():
    # DR-0024 Q2/Q3: the existing WGS 84 GM and a, unchanged.
    assert WGS84_EGM2008_TIDE_FREE.mu == WGS84.mu
    assert WGS84_EGM2008_TIDE_FREE.equatorial_radius == WGS84.equatorial_radius


def test_j2_is_derived_not_stored():
    # P10: one canonical value. J2 is a property of the set, not a constructor field.
    assert "j2" not in {f.name for f in fields(EarthJ2Constants)}
    with pytest.raises(TypeError):
        EarthJ2Constants("x", mu=1.0, equatorial_radius=1.0, c20=-1e-3, j2=1e-3)  # type: ignore[call-arg]
    assert WGS84_EGM2008_TIDE_FREE.j2 == j2_from_c20(EGM2008_C20_TIDE_FREE)


def test_j2_derivation_is_correctly_rounded_binary64():
    """J2 = fl(-fl(sqrt(5)) * C̄2,0): both operations correctly rounded (IEEE 754).

    Checked with exact rational arithmetic, independently of the implementation's
    expression: sqrt(5) is a nearest double to sqrt(5), and the product is a nearest
    double to the exact product of the two doubles.
    """
    s = math.sqrt(5.0)
    lo, hi = math.nextafter(s, 0.0), math.nextafter(s, math.inf)
    # s is nearest to sqrt(5) iff 5 lies between the squares of the midpoints around s.
    assert ((Fraction(lo) + Fraction(s)) / 2) ** 2 < 5 < ((Fraction(s) + Fraction(hi)) / 2) ** 2
    j2 = WGS84_EGM2008_TIDE_FREE.j2
    assert _is_nearest(j2, -Fraction(s) * Fraction(EGM2008_C20_TIDE_FREE))


def test_j2_binary64_value_is_the_p10_recorded_value():
    # DR-0029 P10 records the binary64 derived value 1.0826261738522227e-3. The shortest
    # repr identifies the double uniquely; the hex form makes the bit pattern explicit.
    # This is an expected value for the derivation, not a second source of J2 (P10).
    j2 = WGS84_EGM2008_TIDE_FREE.j2
    assert repr(j2) == "0.0010826261738522227"
    assert j2.hex() == float("1.0826261738522227e-3").hex()


def test_q1_decimal_is_the_11_digit_display_form_of_derived_j2():
    # DR-0024 Q1 writes 1.0826261739e-3: the derived value rounded to 11 significant
    # digits. It is not equal to the canonical value (P10: display only).
    j2 = WGS84_EGM2008_TIDE_FREE.j2
    assert f"{j2:.10e}" == "1.0826261739e-03"
    assert j2 != 1.0826261739e-3


def test_j2_identity_constants_validated():
    with pytest.raises(ValueError):
        EarthJ2Constants("bad", mu=0.0, equatorial_radius=1.0, c20=-1e-3)
    with pytest.raises(ValueError):
        EarthJ2Constants("bad", mu=1.0, equatorial_radius=1.0, c20=math.nan)
    with pytest.raises(AttributeError):
        WGS84_EGM2008_TIDE_FREE.c20 = 0.0  # type: ignore[misc]


def test_c20_literal_only_in_constants_and_no_j2_literal_anywhere():
    """P10: C̄2,0 is written once (constants.py); no derived-J2 literal exists in src."""
    c20 = re.compile(r"0\.484165143790815|4\.84165143790815")
    j2 = re.compile(r"1\.08262617|0\.00108262617")
    c20_offenders, j2_offenders = [], []
    for path in (REPO_ROOT / "src").rglob("*.py"):
        text = path.read_text()
        if path.name != "constants.py" and c20.search(text):
            c20_offenders.append(path.relative_to(REPO_ROOT))
        if j2.search(text):
            j2_offenders.append(path.relative_to(REPO_ROOT))
    assert c20_offenders == []
    assert j2_offenders == []
