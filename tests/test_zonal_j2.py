"""M3 T1: unit validation of the J2 force component (DR-0025 VO-1; VAL-0020).

The oracles here do not reuse the implementation's expression:
- the gradient check differentiates a separately coded potential with forward-mode
  dual numbers (exact derivative rules, only + - * / and sqrt);
- the invariants use the separately coded potential energy;
- the symmetry checks are exact consequences of axisymmetry about +Z.

Tolerances are derived in VAL-0020; none is fitted to measured output. Approximate
comparisons with first-order secular theory are informational and live in
``docs/science/experiments/m3-t1/`` (not here), because no tolerance is justified.
"""

import math

import numpy as np
import pytest

from tars.astro.elements import elements_to_rv
from tars.sim.constants import WGS84, WGS84_EGM2008_TIDE_FREE
from tars.sim.forces import CompositeForceModel, PointMassGravity, ZonalJ2Gravity
from tars.sim.integrators import RK4

MU = WGS84_EGM2008_TIDE_FREE.mu
RE = WGS84_EGM2008_TIDE_FREE.equatorial_radius
J2 = WGS84_EGM2008_TIDE_FREE.j2
U = 2.0**-53  # unit roundoff of binary64


def gamma(n: int) -> float:
    """Higham's gamma_n = n u / (1 - n u): bound on n compounded roundings."""
    return n * U / (1.0 - n * U)


def j2_model(j2: float = J2) -> ZonalJ2Gravity:
    return ZonalJ2Gravity(MU, RE, j2)


# ----------------------------------------------------------------- separately coded oracles
class Dual:
    """Forward-mode dual number: value and gradient with respect to (x, y, z).

    With ``absolute=True`` every value is replaced by its magnitude and every
    subtraction by an addition. That evaluates the same computational graph with all
    terms made non-negative, which is the quantity that bounds the rounding error of
    the ordinary evaluation (Higham, Accuracy and Stability of Numerical Algorithms,
    2nd ed., section 3.1: |computed - exact| <= gamma_n * |graph evaluated in absolute values|).
    """

    def __init__(self, val: float, grad: tuple[float, ...], absolute: bool = False) -> None:
        self.absolute = absolute
        self.val = abs(val) if absolute else val
        self.grad = tuple(abs(g) for g in grad) if absolute else tuple(grad)

    def lift(self, c: "Dual | float") -> "Dual":
        return c if isinstance(c, Dual) else Dual(float(c), (0.0, 0.0, 0.0), self.absolute)

    def _new(self, val: float, grad) -> "Dual":
        return Dual(val, tuple(grad), self.absolute)

    def __add__(self, o):
        o = self.lift(o)
        return self._new(self.val + o.val, (a + b for a, b in zip(self.grad, o.grad, strict=True)))

    __radd__ = __add__

    def __sub__(self, o):
        o = self.lift(o)
        if self.absolute:
            return self + o
        return self._new(self.val - o.val, (a - b for a, b in zip(self.grad, o.grad, strict=True)))

    def __rsub__(self, o):
        return self.lift(o) - self

    def __mul__(self, o):
        o = self.lift(o)
        return self._new(
            self.val * o.val,
            (a * o.val + self.val * b for a, b in zip(self.grad, o.grad, strict=True)),
        )

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = self.lift(o)
        q = self.val / o.val
        if self.absolute:
            return self._new(
                q, ((a + q * b) / o.val for a, b in zip(self.grad, o.grad, strict=True))
            )
        return self._new(q, ((a - q * b) / o.val for a, b in zip(self.grad, o.grad, strict=True)))

    def __rtruediv__(self, o):
        return self.lift(o) / self

    def sqrt(self) -> "Dual":
        s = math.sqrt(self.val)
        return self._new(s, (a / (2.0 * s) for a in self.grad))


def seeds(r, absolute: bool = False):
    return tuple(
        Dual(float(r[k]), tuple(1.0 if j == k else 0.0 for j in range(3)), absolute)
        for k in range(3)
    )


def j2_potential(x, y, z, j2: float = J2):
    """J2 term of the potential, coded from SCI-0013 independently of the acceleration:
    U2 = -(mu J2 R^2 / 2) (3 z^2 / r^5 - 1 / r^3), so that a_J2 = grad U2."""
    r2 = x * x + y * y + z * z
    r = r2.sqrt() if isinstance(r2, Dual) else math.sqrt(r2)
    r3 = r2 * r
    r5 = r3 * r2
    return (-0.5 * MU * j2 * RE * RE) * (3.0 * z * z / r5 - 1.0 / r3)


def specific_energy(r, v, j2: float = J2) -> float:
    """E = v^2/2 - mu/r - U2: conserved for the autonomous axisymmetric field (Q2)."""
    x, y, z = (float(c) for c in r)
    return 0.5 * float(v @ v) - MU / math.sqrt(x * x + y * y + z * z) - j2_potential(x, y, z, j2)


def h_z(r, v) -> float:
    return float(r[0] * v[1] - r[1] * v[0])


def sample_points():
    pts = []
    for radius in (RE, 1.05 * RE, 1.6 * RE, 6.6 * RE):
        for lat in (-90.0, -61.0, -35.264, -12.0, 0.0, 7.5, 35.264, 48.0, 77.0, 90.0):
            for lon in (0.0, 37.0, 123.0, 250.0):
                la, lo = math.radians(lat), math.radians(lon)
                pts.append(
                    radius
                    * np.array(
                        [math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)]
                    )
                )
    pts.append(np.array([4.1e6, -2.7e6, 5.0e6]))
    pts.append(np.array([-6.9e6, 1.3e5, -2.2e5]))
    return pts


# ----------------------------------------------------------------- component checks
def test_identity_and_version():
    model = j2_model()
    assert model.name == "zonal_j2"
    assert model.version == 1


def test_parameters_validated():
    for mu, re_, j2 in ((0.0, RE, J2), (MU, -1.0, J2), (MU, RE, math.inf), (MU, RE, math.nan)):
        with pytest.raises(ValueError):
            ZonalJ2Gravity(mu, re_, j2)
    with pytest.raises(ValueError):
        j2_model().acceleration(0.0, np.zeros(3), np.zeros(3))


def test_known_answers_equator_and_pole():
    """FC-6: at r = R x-hat, a = -(3/2) J2 mu / R^2 x-hat (inward);
    at r = R z-hat, a = +3 J2 mu / R^2 z-hat (outward along +Z).
    Tolerance: each side has at most 16 roundings, so 2 gamma_16 relative (VAL-0020)."""
    tol = 2 * gamma(16)
    a_eq = j2_model().acceleration(0.0, np.array([RE, 0.0, 0.0]), np.zeros(3))
    expected_eq = -1.5 * J2 * MU / (RE * RE)
    assert a_eq[0] < 0.0
    assert abs(a_eq[0] - expected_eq) <= tol * abs(expected_eq)
    assert a_eq[1] == 0.0 and a_eq[2] == 0.0
    a_pole = j2_model().acceleration(0.0, np.array([0.0, 0.0, RE]), np.zeros(3))
    expected_pole = 3.0 * J2 * MU / (RE * RE)
    assert a_pole[2] > 0.0
    assert abs(a_pole[2] - expected_pole) <= tol * abs(expected_pole)
    assert a_pole[0] == 0.0 and a_pole[1] == 0.0


def test_acceleration_is_the_gradient_of_the_separately_coded_potential():
    """DR-0025 Q3 (gradient oracle). Forward-mode dual numbers replace the complex step:
    the same exact-derivative idea, using only correctly rounded operations, so the bound
    rests on no libm assumption. Bound (VAL-0020), per component:
        |a - grad U2| <= gamma_64 * (|a|_abs + |grad U2|_abs),
    where |.|_abs is the same expression evaluated in absolute values and 64 bounds the
    roundings along any path of either evaluation (counted by inspection: at most 13 for
    the acceleration, at most 40 for the dual-number gradient)."""
    model = j2_model()
    for r in sample_points():
        grad = np.array(j2_potential(*seeds(r)).grad)
        grad_abs = np.array(j2_potential(*seeds(r, absolute=True)).grad)
        a = model.acceleration(0.0, r, np.zeros(3))
        a_abs = acceleration_abs(r)
        assert np.all(np.abs(a - grad) <= gamma(64) * (a_abs + grad_abs)), (r, a, grad)


def acceleration_abs(r) -> np.ndarray:
    """The acceleration expression of SCI-0013 evaluated with every term non-negative."""
    x, y, z = (abs(float(c)) for c in r)
    r2 = x * x + y * y + z * z
    s2 = z * z / r2
    k = 1.5 * abs(J2) * MU * RE * RE / (r2 * r2 * math.sqrt(r2))
    return np.array([k * (1 + 5 * s2) * x, k * (1 + 5 * s2) * y, k * (3 + 5 * s2) * z])


def test_gradient_oracle_detects_a_wrong_coefficient():
    """The bound is tight enough to fail for a plausible coding error (z factor 3 -> 2)."""

    class Wrong(ZonalJ2Gravity):
        def acceleration(self, t, r, v):
            a = super().acceleration(t, r, v)
            x, y, z = (float(c) for c in r)
            r2 = x * x + y * y + z * z
            return a - np.array([0.0, 0.0, self._k / (r2 * r2 * math.sqrt(r2)) * z])

    model = Wrong(MU, RE, J2)
    failures = 0
    for r in sample_points():
        grad = np.array(j2_potential(*seeds(r)).grad)
        grad_abs = np.array(j2_potential(*seeds(r, absolute=True)).grad)
        a = model.acceleration(0.0, r, np.zeros(3))
        failures += not np.all(np.abs(a - grad) <= gamma(64) * (acceleration_abs(r) + grad_abs))
    assert failures > 0


def test_axisymmetry_is_exact():
    """Rotating r by 90 deg about +Z rotates a exactly; reflecting z reflects a_z exactly."""
    model = j2_model()
    for r in sample_points():
        a = model.acceleration(0.0, r, np.zeros(3))
        a_rot = model.acceleration(0.0, np.array([-r[1], r[0], r[2]]), np.zeros(3))
        assert a_rot.tobytes() == np.array([-a[1], a[0], a[2]]).tobytes()
        a_ref = model.acceleration(0.0, np.array([r[0], r[1], -r[2]]), np.zeros(3))
        assert np.array_equal(a_ref, np.array([a[0], a[1], -a[2]]))


def test_radial_sign_changes_at_sin2_latitude_one_third():
    """a_J2 . r = -(3/2) J2 mu R^2 / r^4 (1 - 3 sin^2 lat): inward below |lat| = 35.26 deg,
    outward above (exact sign of a closed form; margins far above roundoff)."""
    model = j2_model()
    for lat, sign in ((0.0, -1), (20.0, -1), (-20.0, -1), (50.0, +1), (-50.0, +1), (90.0, +1)):
        la = math.radians(lat)
        r = 1.1 * RE * np.array([math.cos(la), 0.0, math.sin(la)])
        assert math.copysign(1.0, float(model.acceleration(0.0, r, np.zeros(3)) @ r)) == sign


def test_j2_zero_is_exactly_zero_and_leaves_point_mass_unchanged():
    """DR-0025 Q11: J2 = 0 contributes exactly zero, so point mass + J2(0) is bitwise point mass."""
    pm = PointMassGravity(MU)
    both = CompositeForceModel([pm, j2_model(0.0)])
    for r in sample_points():
        a0 = j2_model(0.0).acceleration(0.0, r, np.zeros(3))
        assert np.all(a0 == 0.0)
        assert both.acceleration(0.0, r, np.zeros(3)).tobytes() == (
            CompositeForceModel([pm]).acceleration(0.0, r, np.zeros(3)).tobytes()
        )


# ----------------------------------------------------------------- propagation checks
def propagate(model, r0, v0, dt: float, steps: int):
    def f(t, y):
        return np.concatenate([y[3:], model.acceleration(t, y[:3], y[3:])])

    y = np.concatenate([r0, v0])
    rk4 = RK4()
    out = [y]
    for k in range(steps):
        y = rk4.step(f, k * dt, y, dt)
        out.append(y)
    return np.array(out)


def eccentric_state(inc_deg: float):
    """Perigee 300 km, apogee 1000 km (e ~ 0.05), RAAN 30 deg, argp 40 deg, at perigee."""
    rp, ra = RE + 300e3, RE + 1000e3
    a, e = 0.5 * (rp + ra), (ra - rp) / (ra + rp)
    return elements_to_rv(
        a, e, math.radians(inc_deg), math.radians(30.0), math.radians(40.0), 0.0, MU
    )


def test_j2_zero_propagation_is_bitwise_point_mass():
    r0, v0 = eccentric_state(51.6)
    pm = PointMassGravity(MU)
    a = propagate(CompositeForceModel([pm, j2_model(0.0)]), r0, v0, 10.0, 600)
    b = propagate(CompositeForceModel([pm]), r0, v0, 10.0, 600)
    assert a.tobytes() == b.tobytes()


def test_polar_orbit_plane_is_exactly_invariant():
    """DR-0025 Q11 'no node motion at i = 90 deg'. In the x-z plane the y components of
    point-mass and J2 accelerations are exactly zero, so y = v_y = 0 for every RK4 step."""
    radius = RE + 250e3
    r0, v0 = np.array([radius, 0.0, 0.0]), np.array([0.0, 0.0, math.sqrt(MU / radius)])
    ys = propagate(CompositeForceModel([PointMassGravity(MU), j2_model()]), r0, v0, 10.0, 5370)
    assert np.all(ys[:, 1] == 0.0) and np.all(ys[:, 4] == 0.0)


@pytest.mark.parametrize("inc_deg", [28.5, 51.6, 97.0])
def test_invariant_drift_is_integrator_truncation(inc_deg):
    """DR-0025 Q2: E and h_z are exact invariants of point mass + J2. RK4 does not conserve
    them, so the check is structural (VAL-0020): RK4's global error is O(dt^4) (ADR-0004),
    so a correct model's drift falls by about 4^4 = 256 when dt goes from 20 s to 5 s,
    while a non-conservative or non-axisymmetric force drifts independently of dt (ratio
    about 1). The decision boundary 1/2 was fixed before measuring and separates the two
    hypotheses by more than two orders of magnitude on each side. Ten orbits."""
    r0, v0 = eccentric_state(inc_deg)
    model = CompositeForceModel([PointMassGravity(MU), j2_model()])
    period = 2.0 * math.pi * math.sqrt((0.5 * (2 * RE + 1300e3)) ** 3 / MU)
    drift = {}
    for dt in (20.0, 5.0):
        ys = propagate(model, r0, v0, dt, round(10 * period / dt))
        e0, hz0 = specific_energy(r0, v0), h_z(r0, v0)
        drift[dt] = (
            max(abs(specific_energy(y[:3], y[3:]) - e0) for y in ys) / abs(e0),
            max(abs(h_z(y[:3], y[3:]) - hz0) for y in ys) / abs(hz0),
        )
    for k in range(2):
        assert drift[5.0][k] <= 0.5 * drift[20.0][k], drift


def test_wgs84_set_used_by_point_mass_is_unchanged():
    assert PointMassGravity(WGS84.mu).mu == MU
