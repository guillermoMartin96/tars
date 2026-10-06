import re

import pytest

from tars.sim.constants import WGS84, EarthConstants
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
