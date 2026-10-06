import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from tars.astro.elements import elements_to_rv, keplerian_period, specific_energy
from tars.astro.kepler import propagate, stumpff_c, stumpff_s
from tars.sim.constants import WGS84


def test_vallado_example_2_4_kepler():
    """Vallado (2013) Example 2-4, 40-minute propagation (values transcribed)."""
    r, v = propagate(
        np.array([1131.340, -2282.343, 6672.423]),
        np.array([-5.64305, 4.30333, 2.42879]),
        40 * 60.0,
        WGS84.mu / 1e9,
    )
    np.testing.assert_allclose(r, [-4219.7527, 4363.0292, -3958.7666], rtol=0, atol=1e-3)
    np.testing.assert_allclose(v, [3.689866, -1.916735, -6.112511], rtol=0, atol=1e-6)


@pytest.mark.parametrize("z", [-50.0, -0.11, -0.09, -1e-8, 0.0, 1e-8, 0.09, 0.11, 30.0, 3000.0])
def test_stumpff_series_and_closed_forms_agree(z):
    def c_ref(z):
        if z > 0:
            return (1 - math.cos(math.sqrt(z))) / z
        if z < 0:
            return (math.cosh(math.sqrt(-z)) - 1) / -z
        return 0.5

    def s_ref(z):
        if z > 0:
            s = math.sqrt(z)
            return (s - math.sin(s)) / s**3
        if z < 0:
            s = math.sqrt(-z)
            return (math.sinh(s) - s) / s**3
        return 1 / 6

    tol = 1e-12 if abs(z) > 1e-3 else 1e-6  # closed forms lose precision near 0
    assert stumpff_c(z) == pytest.approx(c_ref(z), rel=tol)
    assert stumpff_s(z) == pytest.approx(s_ref(z), rel=tol)


def _dop853(r0, v0, t_end, mu):
    def f(t, y):
        r = y[:3]
        return np.concatenate([y[3:], -mu * r / np.linalg.norm(r) ** 3])

    sol = solve_ivp(
        f, (0.0, t_end), np.concatenate([r0, v0]), method="DOP853", rtol=1e-13, atol=1e-6
    )
    return sol.y[:3, -1], sol.y[3:, -1]


@pytest.mark.parametrize(
    "a,e,t_end",
    [(6628137.0, 0.0, 3000.0), (7.5e6, 0.15, 20000.0), (2.4e7, 0.72, 50000.0)],
)
def test_kepler_matches_independent_dop853(a, e, t_end):
    """Independent cross-check: SciPy DOP853 at tight tolerance (not our code)."""
    r0, v0 = elements_to_rv(a, e, 0.9, 0.4, 1.3, 0.2, WGS84.mu)
    r, v = propagate(r0, v0, t_end, WGS84.mu)
    r_ref, v_ref = _dop853(r0, v0, t_end, WGS84.mu)
    assert np.linalg.norm(r - r_ref) < 1e-3  # metres
    assert np.linalg.norm(v - v_ref) < 1e-6  # m/s


def test_kepler_returns_to_start_after_whole_periods():
    r0, v0 = elements_to_rv(6628137.0, 0.0, math.radians(51.6), 0.0, 0.0, 0.0, WGS84.mu)
    period = keplerian_period(6628137.0, WGS84.mu)
    r, v = propagate(r0, v0, 10 * period, WGS84.mu)
    assert np.linalg.norm(r - r0) < 1e-6
    assert np.linalg.norm(v - v0) < 1e-9


def test_kepler_conserves_energy_and_handles_hyperbola():
    r0, v0 = np.array([7.0e6, 0.0, 0.0]), np.array([0.0, 12000.0, 500.0])  # hyperbolic
    assert specific_energy(r0, v0, WGS84.mu) > 0
    r, v = propagate(r0, v0, 5000.0, WGS84.mu)
    assert specific_energy(r, v, WGS84.mu) == pytest.approx(
        specific_energy(r0, v0, WGS84.mu), rel=1e-10
    )
    np.testing.assert_allclose(np.cross(r, v), np.cross(r0, v0), rtol=1e-11)


def test_zero_time_returns_copy():
    r0, v0 = np.array([7.0e6, 0.0, 0.0]), np.array([0.0, 7500.0, 0.0])
    r, v = propagate(r0, v0, 0.0, WGS84.mu)
    np.testing.assert_array_equal(r, r0)
    np.testing.assert_array_equal(v, v0)
    assert r is not r0
