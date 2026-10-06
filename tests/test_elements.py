import math

import numpy as np
import pytest

from tars.astro.elements import (
    circular_orbit_state,
    elements_to_rv,
    keplerian_period,
    rv_to_elements,
)
from tars.sim.constants import WGS84

MU_KM = WGS84.mu / 1e9  # km^3/s^2 for textbook examples quoted in km


def test_vallado_example_2_5_rv2coe():
    """Vallado (2013) Example 2-5 (values transcribed; printed precision)."""
    el = rv_to_elements(
        np.array([6524.834, 6862.875, 6448.296]), np.array([4.901327, 5.533756, -1.976341]), MU_KM
    )
    assert el.a == pytest.approx(36127.343, abs=0.01)
    assert el.e == pytest.approx(0.832853, abs=1e-6)
    assert math.degrees(el.i) == pytest.approx(87.870, abs=1e-3)
    assert math.degrees(el.raan) == pytest.approx(227.898, abs=1e-3)
    assert math.degrees(el.argp) == pytest.approx(53.38, abs=1e-2)
    assert math.degrees(el.nu) == pytest.approx(92.335, abs=1e-3)


@pytest.mark.parametrize(
    "a,e,i,raan,argp,nu",
    [
        (7.0e6, 0.01, 0.5, 1.0, 2.0, 3.0),
        (2.6e7, 0.7, 1.1, 4.0, 0.3, 5.9),
        (6.9e6, 0.001, 2.5, 6.0, 4.5, 0.1),  # retrograde
    ],
)
def test_elements_round_trip(a, e, i, raan, argp, nu):
    r, v = elements_to_rv(a, e, i, raan, argp, nu, WGS84.mu)
    el = rv_to_elements(r, v, WGS84.mu)
    assert el.a == pytest.approx(a, rel=1e-12)
    assert el.e == pytest.approx(e, rel=1e-9)
    for got, want in [(el.i, i), (el.raan, raan), (el.argp, argp), (el.nu, nu)]:
        assert math.remainder(got - want, 2 * math.pi) == pytest.approx(0.0, abs=1e-9)
    r2, v2 = elements_to_rv(el.a, el.e, el.i, el.raan, el.argp, el.nu, WGS84.mu)
    np.testing.assert_allclose(r2, r, rtol=0, atol=1e-6)
    np.testing.assert_allclose(v2, v, rtol=0, atol=1e-9)


def test_circular_orbit_uses_argument_of_latitude():
    radius = WGS84.equatorial_radius + 250e3
    r, v = circular_orbit_state(radius, math.radians(51.6), 0.3, 1.2, WGS84.mu)
    el = rv_to_elements(r, v, WGS84.mu)
    assert el.e < 1e-11
    assert el.argp == 0.0
    assert el.u == pytest.approx(1.2, abs=1e-12)
    assert el.nu == el.u
    assert np.linalg.norm(r) == pytest.approx(radius, rel=1e-15)
    assert np.linalg.norm(v) == pytest.approx(math.sqrt(WGS84.mu / radius), rel=1e-15)
    assert np.dot(r, v) == pytest.approx(0.0, abs=1e-6)


def test_m1_initial_state_is_on_ascending_node():
    radius = WGS84.equatorial_radius + 250e3
    r, v = circular_orbit_state(radius, math.radians(51.6), 0.0, 0.0, WGS84.mu)
    assert r[2] == 0.0 and v[2] > 0.0
    # Inclination from the angular momentum vector.
    h = np.cross(r, v)
    assert math.degrees(math.acos(h[2] / np.linalg.norm(h))) == pytest.approx(51.6, abs=1e-12)


def test_equatorial_orbit_has_defined_angles():
    r, v = elements_to_rv(7.0e6, 0.1, 0.0, 0.0, 1.0, 0.5, WGS84.mu)
    el = rv_to_elements(r, v, WGS84.mu)
    assert el.raan == 0.0
    assert el.argp == pytest.approx(1.0, abs=1e-9)
    assert el.nu == pytest.approx(0.5, abs=1e-9)


def test_m1_keplerian_period():
    # Plan §2.2: r = 6 628 137 m -> T = 5370.296 s.
    assert keplerian_period(WGS84.equatorial_radius + 250e3, WGS84.mu) == pytest.approx(
        5370.296, abs=1e-3
    )


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        elements_to_rv(7e6, 1.2, 0, 0, 0, 0, WGS84.mu)
    with pytest.raises(ValueError):
        keplerian_period(-1.0, WGS84.mu)
    with pytest.raises(ValueError):
        rv_to_elements(np.array([7e6, 0, 0]), np.array([1.0, 0, 0]), WGS84.mu)
