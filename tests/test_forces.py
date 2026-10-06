import numpy as np
import pytest

from tars.sim.constants import WGS84
from tars.sim.forces import CompositeForceModel, PointMassGravity


def test_point_mass_gravity_magnitude_and_direction():
    gravity = PointMassGravity(WGS84.mu)
    r = np.array([3.0e6, -4.0e6, 5.0e6])
    a = gravity.acceleration(0.0, r, np.zeros(3))
    r_norm = np.linalg.norm(r)
    assert np.linalg.norm(a) == pytest.approx(WGS84.mu / r_norm**2, rel=1e-15)
    np.testing.assert_allclose(a / np.linalg.norm(a), -r / r_norm, rtol=0, atol=1e-15)


def test_surface_gravity_is_physically_plausible():
    # mu / a^2 at the equatorial radius ~ 9.798 m/s^2 (no rotation, no J2).
    gravity = PointMassGravity(WGS84.mu)
    a = gravity.acceleration(0.0, np.array([WGS84.equatorial_radius, 0, 0]), np.zeros(3))
    assert np.linalg.norm(a) == pytest.approx(9.798, abs=1e-3)


def test_gravity_singular_at_origin():
    with pytest.raises(ValueError):
        PointMassGravity(WGS84.mu).acceleration(0.0, np.zeros(3), np.zeros(3))


class _Constant:
    name = "constant"

    def __init__(self, a):
        self.a = np.asarray(a, dtype=float)

    def acceleration(self, t, r, v):
        return self.a


def test_composite_sums_components():
    model = CompositeForceModel([_Constant([1, 2, 3]), _Constant([0.5, 0, -1])])
    np.testing.assert_array_equal(model.acceleration(0.0, np.ones(3), np.zeros(3)), [1.5, 2, 2])
    assert model.component_names == ["constant", "constant"]
    with pytest.raises(ValueError):
        CompositeForceModel([])
