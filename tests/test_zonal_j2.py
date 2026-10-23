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
import sys
from fractions import Fraction

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


def test_parameters_are_immutable_after_construction():
    """M3T1-R1-F1: no attribute can be reassigned, deleted or added, so the visible
    parameters always match the values the acceleration uses."""
    model = j2_model()
    r = np.array([RE, 0.0, 0.0])
    before = model.acceleration(0.0, r, np.zeros(3)).tobytes()
    for name in ("mu", "equatorial_radius", "j2", "name", "version", "extra"):
        with pytest.raises(AttributeError):
            setattr(model, name, 0.0)
        with pytest.raises(AttributeError):
            delattr(model, name)
    assert not hasattr(model, "__dict__")
    assert (model.mu, model.equatorial_radius, model.j2) == (MU, RE, J2)
    assert (model.name, model.version) == ("zonal_j2", 1)
    assert model.acceleration(0.0, r, np.zeros(3)).tobytes() == before


def constructed(*args):
    """The model, or the exception its construction raised, so that a wrongly rejected
    supported input fails an assertion rather than erroring."""
    try:
        return ZonalJ2Gravity(*args)
    except (TypeError, ValueError, OverflowError) as e:
        return e


def test_parameters_are_owned_snapshots_not_caller_references():
    """M3T1-R2-F2: parameters are converted to built-in floats at construction, so mutating a
    caller's zero-dimensional array afterwards changes neither the visible parameters nor the
    acceleration."""
    reference = j2_model()
    r = np.array([RE, 0.0, 0.0])
    expected = reference.acceleration(0.0, r, np.zeros(3)).tobytes()
    mu, radius, j2 = np.array(MU), np.array(RE), np.array(J2)
    model = constructed(mu, radius, j2)
    assert isinstance(model, ZonalJ2Gravity), model
    mu[...], radius[...], j2[...] = -1.0, -RE, 0.0
    assert all(type(p) is float for p in (model.mu, model.equatorial_radius, model.j2))
    assert (model.mu, model.equatorial_radius, model.j2) == (MU, RE, J2)
    assert model.acceleration(0.0, r, np.zeros(3)).tobytes() == expected


@pytest.mark.parametrize(
    "convert",
    [
        float,
        np.float64,
        np.float32,
        np.longdouble,
        lambda v: np.array(v, dtype=np.float32),
        lambda v: np.array(v),
    ],
)
def test_supported_numeric_types_are_converted_to_binary64(convert):
    """M3T1-R2-F2: every supported real type gives the model built from the same values as
    built-in floats (float32 values widen exactly), with binary64 arithmetic and result."""
    values = [convert(v) for v in (MU, RE, J2)]
    model = constructed(*values)
    assert isinstance(model, ZonalJ2Gravity), model
    reference = ZonalJ2Gravity(*(float(v) for v in values))
    r = np.array([RE, 2.0e6, 3.0e6])
    a = model.acceleration(0.0, r, np.zeros(3))
    assert a.dtype == np.float64
    assert a.tobytes() == reference.acceleration(0.0, r, np.zeros(3)).tobytes()
    assert all(type(p) is float for p in (model.mu, model.equatorial_radius, model.j2))


def test_float16_parameter_is_supported():
    """M3T1-R2-F2: float16 is a supported floating type (its range cannot hold mu or R)."""
    r = np.array([RE, 2.0e6, 3.0e6])
    model = constructed(MU, RE, np.float16(J2))
    assert isinstance(model, ZonalJ2Gravity), model
    a = model.acceleration(0.0, r, np.zeros(3))
    b = ZonalJ2Gravity(MU, RE, float(np.float16(J2))).acceleration(0.0, r, np.zeros(3))
    assert a.dtype == np.float64 and a.tobytes() == b.tobytes()


def test_integer_parameters_are_supported():
    """M3T1-R2-F2: int and NumPy integer scalars are real numbers and are converted."""
    model = constructed(1, np.int64(1), 0.5)
    assert isinstance(model, ZonalJ2Gravity), model
    a = model.acceleration(0.0, np.array([2.0, 0, 0]), np.zeros(3))
    b = ZonalJ2Gravity(1.0, 1.0, 0.5).acceleration(0.0, np.array([2.0, 0, 0]), np.zeros(3))
    assert a.tobytes() == b.tobytes()


@pytest.mark.parametrize(
    "value",
    [
        "6378137.0",
        b"1",
        [RE],
        (RE,),
        np.array([RE]),
        np.array("1.0"),
        True,
        np.bool_(True),
        1 + 0j,
        np.complex128(1.0),
        Fraction(1, 3),
        None,
    ],
)
def test_unsupported_parameter_types_are_rejected(value):
    """M3T1-R2-F2: only int (not bool), float, NumPy integer and floating scalars, and
    zero-dimensional arrays of those are accepted; strings, containers, booleans, complex
    and other numeric types are rejected even where float() could convert them."""
    for args in ((value, RE, J2), (MU, value, J2), (MU, RE, value)):
        with pytest.raises(TypeError, match="must be a real number"):
            ZonalJ2Gravity(*args)


def test_unrepresentable_integer_parameter_is_rejected():
    """M3T1-R2-F2: an int beyond the binary64 range is a value error, not an OverflowError."""
    error = constructed(10**400, RE, J2)
    assert type(error) is ValueError and "not representable as a binary64" in str(error)


@pytest.mark.parametrize(
    ("mu", "radius", "j2"),
    [(np.array(math.nan), RE, J2), (MU, np.float32(-1.0), J2), (MU, RE, np.array(np.inf))],
)
def test_converted_parameters_keep_the_validation_contract(mu, radius, j2):
    """M3T1-R2-F2: conversion precedes, and does not weaken, the parameter validation."""
    with pytest.raises(ValueError, match="must be finite"):
        ZonalJ2Gravity(mu, radius, j2)


@pytest.mark.parametrize(
    ("mu", "radius", "j2"),
    [
        (math.inf, RE, J2),
        (math.nan, RE, J2),
        (MU, math.inf, J2),
        (MU, math.nan, J2),
        (1e300, 1e10, J2),  # -(3/2) J2 mu R^2 overflows
        (1e-300, 1e-10, 1e-3),  # -(3/2) J2 mu R^2 is subnormal
    ],
)
def test_non_finite_or_unrepresentable_parameters_are_rejected(mu, radius, j2):
    """M3T1-R1-F2, invalid-domain parameters: rejected at construction (DR-0024 R6), with
    the diagnostic naming the offending input."""
    if math.isfinite(mu) and math.isfinite(radius):
        message = r"-\(3/2\) J2 mu R\^2 is not a finite normal"
    else:
        message = "mu and equatorial_radius must be finite and positive"
    with pytest.raises(ValueError, match=message):
        ZonalJ2Gravity(mu, radius, j2)


@pytest.mark.parametrize(
    "r", [[math.inf, 0.0, 0.0], [math.nan, 0.0, 0.0], [0.0, -math.inf, 0.0], [1e7, 0.0, math.nan]]
)
def test_non_finite_position_is_rejected(r):
    """M3T1-R1-F2, invalid-domain state: rejected before any arithmetic."""
    with pytest.raises(ValueError, match="position must be finite"):
        j2_model().acceleration(0.0, np.array(r), np.zeros(3))


def exact_equatorial_x(x: float, mu: float = MU, radius: float = RE, j2: float = J2) -> float:
    """Correctly rounded a_x on the equator, y = z = 0: -(3/2) J2 mu R^2 / x^4 (exact rationals)."""
    return float(
        Fraction(-3, 2) * Fraction(j2) * Fraction(mu) * Fraction(radius) ** 2 / Fraction(x) ** 4
    )


@pytest.mark.parametrize(
    ("x", "message"),
    [
        (1e62, r"\|r\|\^5"),
        (1e70, r"\|r\|\^5"),
        (1e100, r"\|r\|\^5"),
        (1e200, r"\|r\|\^5"),
        (1e-60, "coefficient"),
        (1e-100, r"\|r\|\^5"),
        (1e-200, "underflows to zero"),
        (5e-324, "underflows to zero"),
    ],
)
def test_arithmetic_outside_the_numerical_domain_raises_instead_of_a_silent_result(x, message):
    """M3T1-R1-F2: intermediate overflow or underflow is reported, never returned as a zero
    or non-finite acceleration. At x = 1e62 the exact answer (-2.6e-223) is representable but
    r^5 overflows, which before the correction returned exactly 0. The message names the
    intermediate that left the normal range (r^5; the scaled coefficient, which overflows at
    1e-60; r^2, which underflows to zero for a non-zero position)."""
    with pytest.raises(ValueError, match="numerical domain: .*" + message):
        j2_model().acceleration(0.0, np.array([x, 0.0, 0.0]), np.zeros(3))


def test_subnormal_scaled_coefficient_raises_instead_of_an_inaccurate_result():
    """M3T1-R1-F2: if -(3/2) J2 mu R^2 / r^5 is subnormal it has lost relative precision, and
    the finite-looking product would be inaccurate (here by about 3e-8 relative). Parameters
    mu = R = 1, J2 = 0.7 * 2^-1000 (coefficient normal), r = 2^10 (coefficient / r^5 is
    1.05 * 2^-1050, subnormal)."""
    model = ZonalJ2Gravity(1.0, 1.0, 0.7 * 2.0**-1000)
    with pytest.raises(ValueError, match="numerical domain: coefficient"):
        model.acceleration(0.0, np.array([2.0**10, 0.0, 0.0]), np.zeros(3))


def test_result_overflow_raises():
    """M3T1-R1-F2: r^5 and the coefficient are normal but the product overflows (only for
    parameters far beyond physical ones)."""
    model = ZonalJ2Gravity(1e300, 1.0, -1.7e8 / 1.5)
    with pytest.raises(ValueError, match="acceleration overflows"):
        model.acceleration(0.0, np.array([0.0, 0.0, 1.1]), np.zeros(3))


def exact_acceleration(r, mu: float, radius: float, j2: float) -> list[float]:
    """Correctly rounded J2 acceleration at the binary64 position r, from exact rationals; |r|
    is bracketed by an integer square root and both ends must round to the same value."""
    x, y, z = (Fraction(float(c)) for c in r)
    r2 = x * x + y * y + z * z
    scale = 2**1200
    lo = Fraction(math.isqrt(int(r2 * scale * scale)), scale)
    k0 = Fraction(-3, 2) * Fraction(j2) * Fraction(mu) * Fraction(radius) ** 2
    s2 = z * z / r2
    ends = [
        [
            float(k0 / (r2 * r2 * n) * f)
            for f in (x * (1 - 5 * s2), y * (1 - 5 * s2), z * (3 - 5 * s2))
        ]
        for n in (lo, lo + Fraction(1, scale))
    ]
    assert ends[0] == ends[1]
    return ends[0]


# Off-axis states where the coefficient k is normal but k (1 - 5 s^2) or k (3 - 5 s^2) is
# below the normal range and inexact (R = 1, J2 = 1/2). The first is Review 02's
# reproduction: k = -2^-1022, 1 - 5 s^2 = 2^-53.
COMPONENT_UNDERFLOW_CASES = [
    (5.1827254193540115e-108, [1e40, 0.0, 4.9999999999999995e39], 0),
    (5.1827254193540115e-108, [0.0, 1e40, 4.9999999999999995e39], 1),
    (1.3 * 2.931792231242491e-107, [1e40, 0.0, 1.224744871391589e40], 2),
]


@pytest.mark.parametrize(("mu", "r", "component"), COMPONENT_UNDERFLOW_CASES)
def test_component_product_underflow_raises_instead_of_a_silent_result(mu, r, component):
    """M3T1-R2-F1: the exact component is a normal binary64 number, but the product of the
    coefficient and the latitude factor underflows, which before the correction returned it
    as zero or as an inaccurate subnormal-scaled value without a diagnostic."""
    exact = exact_acceleration(r, mu, 1.0, 0.5)[component]
    assert abs(exact) >= sys.float_info.min
    with pytest.raises(ValueError, match="numerical domain: a component product underflows"):
        ZonalJ2Gravity(mu, 1.0, 0.5).acceleration(0.0, np.array(r), np.zeros(3))


@pytest.mark.parametrize(
    ("mu", "radius", "j2", "product"),
    [
        (2.0**1000, 1.0, 3 * 2.0**-1074, 1),  # -(3/2) J2 = -4.5 * 2^-1074
        (2.0**-1000 * (1 + 2.0**-52), 2.0**600, 2.0**-60, 2),  # ... * mu
        (2.0**-1028, 35.2, 0.5, 3),  # ... * R (the first two products exact)
    ],
)
def test_coefficient_product_underflow_raises_instead_of_an_inaccurate_result(
    mu, radius, j2, product
):
    """M3T1-R2-F1 (same defect in the coefficient): -(3/2) J2 mu R^2 is evaluated as
    ((-(3/2) J2) mu) R) R. In each case exactly one of the first three products rounds
    inexactly below the normal range while the coefficient is normal, so the coefficient is
    inaccurate (11 % in the first case): construction is rejected."""
    p = [-1.5 * j2]
    p += [p[0] * mu, p[0] * mu * radius]
    factors = [(-1.5, j2), (p[0], mu), (p[1], radius)]
    inexact = [
        abs(q) < sys.float_info.min and Fraction(a) * Fraction(b) != q
        for q, (a, b) in zip(p, factors, strict=True)
    ]
    assert inexact == [i == product - 1 for i in range(3)]
    assert abs(p[2] * radius) >= sys.float_info.min
    with pytest.raises(ValueError, match="intermediate product underflows"):
        ZonalJ2Gravity(mu, radius, j2)


SUBNORMAL_UNIT = Fraction(1, 2**1074)  # the smallest subnormal, 2^-1074, exactly


def test_coefficient_product_underflow_in_the_upper_subnormal_band_raises():
    """M3T1-R3-O1: an inexact product strictly between MIN_NORMAL/2 and MIN_NORMAL (2^51 and
    2^52 units of 2^-1074) is an underflow, not only one below MIN_NORMAL/2. Construction,
    in those units: mu = 2^52 + 1 (the normal MIN_NORMAL + 2^-1074) and J2 = 1/2, so
    -(3/2) J2 = -3/4 exactly and -(3/2) J2 mu is exactly -(3 * 2^50 + 3/4) units, which
    rounds (not a tie) to -(3 * 2^50 + 1) units. R = 2^10 makes the last two products exact
    and k normal, so only the underflow check can reject the construction."""
    mu, radius, j2 = (2**52 + 1) * 2.0**-1074, 2.0**10, 0.5
    assert Fraction(mu) == (2**52 + 1) * SUBNORMAL_UNIT and mu >= sys.float_info.min
    p1 = -1.5 * j2
    p2 = p1 * mu
    assert Fraction(p1) == Fraction(-3, 4)
    exact = Fraction(p1) * Fraction(mu)
    assert exact == -(3 * 2**50 + Fraction(3, 4)) * SUBNORMAL_UNIT
    assert Fraction(p2) == -(3 * 2**50 + 1) * SUBNORMAL_UNIT != exact  # inexact
    for q in (exact, Fraction(p2)):
        assert 2**51 * SUBNORMAL_UNIT < abs(q) < 2**52 * SUBNORMAL_UNIT
    assert sys.float_info.min / 2 < abs(p2) < sys.float_info.min
    assert Fraction(p2 * radius) == Fraction(p2) * Fraction(radius)
    assert abs(p2 * radius * radius) >= sys.float_info.min
    with pytest.raises(ValueError, match="intermediate product underflows"):
        ZonalJ2Gravity(mu, radius, j2)


def test_exact_product_in_the_upper_subnormal_band_is_not_underflow():
    """M3T1-R3-O1 companion: with mu = 2^52 units (MIN_NORMAL) the same product is exactly
    -3 * 2^50 units, in the same band, and is accepted; the result is the formula."""
    mu, radius, j2 = 2.0**-1022, 2.0**10, 0.5
    p2 = -1.5 * j2 * mu
    assert Fraction(p2) == Fraction(-3, 4) * Fraction(mu) == -3 * 2**50 * SUBNORMAL_UNIT
    assert sys.float_info.min / 2 < abs(p2) < sys.float_info.min
    r = np.array([1.0, 0.0, 0.0])
    a = evaluated((mu, radius, j2), r)
    assert isinstance(a, np.ndarray), a
    expected = exact_acceleration(r, mu, radius, j2)
    assert abs(a[0] - expected[0]) <= 2 * gamma(16) * abs(expected[0])
    assert a[1] == 0.0 and a[2] == 0.0


def evaluated(args, r):
    """The acceleration, or the exception construction or evaluation raised, so that a wrongly
    rejected legitimate result fails an assertion rather than erroring."""
    try:
        return ZonalJ2Gravity(*args).acceleration(0.0, np.array(r), np.zeros(3))
    except ValueError as e:
        return e


def test_exact_subnormal_intermediates_are_not_underflow():
    """M3T1-R2-F1: a product below the normal range that is exact is not an underflow and is
    accepted. Here -(3/2) J2 = -3 * 2^-1074 is exact and the result is the formula."""
    r = np.array([2.0**10, 0.0, 0.0])
    a = evaluated((2.0**1000, 1.0, 2 * 2.0**-1074), r)
    assert isinstance(a, np.ndarray), a
    expected = exact_acceleration(r, 2.0**1000, 1.0, 2 * 2.0**-1074)
    assert abs(a[0] - expected[0]) <= 2 * gamma(16) * abs(expected[0])
    assert a[1] == 0.0 and a[2] == 0.0


def test_legitimate_zero_components_are_returned():
    """M3T1-R2-F1: exact zeros are not arithmetic underflow. With the coefficient at the edge
    of the normal range (Review 02's parameters): at z^2/r^2 = 1/5 the factor 1 - 5 s^2 is
    exactly 0 (power-of-two coordinates, so the computed factor is exactly 0 too) and the x
    component is an exact zero although k (1 - 5 s^2) is below the normal range; y = 0 gives
    an exact zero. The z component is the formula. J2 = 0 gives exact zeros everywhere."""
    mu = 5.1827254193540115e-106
    r = np.array([2.0**134, 0.0, 2.0**133])
    a = evaluated((mu, 1.0, 0.5), r)
    assert isinstance(a, np.ndarray), a
    expected = exact_acceleration(r, mu, 1.0, 0.5)
    assert expected[0] == 0.0 and expected[1] == 0.0
    assert a[0] == 0.0 and a[1] == 0.0
    assert abs(a[2] - expected[2]) <= 2 * gamma(16) * abs(expected[2])
    zero = evaluated((5.1827254193540115e-108, 1.0, 0.0), [1e40, 0.0, 5e39])
    assert isinstance(zero, np.ndarray), zero
    assert not zero.any()


def test_subnormal_result_components_are_returned():
    """M3T1-R2-F1: a final component may be subnormal; the coefficient and both factor
    products are normal, so only the last multiplication rounds into the subnormal range
    (absolute error at most half the smallest subnormal). mu = R = 1, J2 = 1/2,
    r = (2^200, 2^-50, 0)."""
    r = np.array([2.0**200, 2.0**-50, 0.0])
    a = evaluated((1.0, 1.0, 0.5), r)
    assert isinstance(a, np.ndarray), a
    expected = exact_acceleration(r, 1.0, 1.0, 0.5)
    assert 0.0 < abs(expected[1]) < sys.float_info.min
    assert abs(a[1] - expected[1]) <= 2.0**-1074
    assert a[0] == expected[0]


@pytest.mark.parametrize("x", [1e-50, 1e-20, RE, 1e40, 1e61])
def test_inside_the_numerical_domain_results_are_the_formula(x):
    """The domain checks change nothing inside the numerical domain: the result is within
    2 gamma_16 of the exactly rounded closed form, including just below the r^5 overflow
    onset (about 4.5e61 m) and far inside the Earth (the physical boundary is not the
    component's: DR-0029 P1-P9)."""
    a = j2_model().acceleration(0.0, np.array([x, 0.0, 0.0]), np.zeros(3))
    expected = exact_equatorial_x(x)
    assert expected != 0.0
    assert abs(a[0] - expected) <= 2 * gamma(16) * abs(expected)
    assert a[1] == 0.0 and a[2] == 0.0


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


@pytest.mark.parametrize("j2", [0.5, -0.5, 0.375])
@pytest.mark.parametrize("e", [1, 10, 50, 100, 200])
def test_known_answers_are_exact_in_power_of_two_units(j2, e):
    """M3T1-R1-F4. With mu = R = 1 and r = 2^e on the equator and the pole, every operation
    of the closed form and of the formula is exact in binary64 (powers of two times 3/2, 3,
    5 and J2 = +-1/2 or 3/8), so the result must equal the exact rational value bit for bit:
    a_x = -(3/2) J2 / r^4 at r x-hat, a_z = +3 J2 / r^4 at r z-hat. This pins the coefficient
    to the last bit, the sign of J2 (prolate J2 < 0 reverses the field) and the radial law
    out to 2^200 reference radii."""
    model = ZonalJ2Gravity(1.0, 1.0, j2)
    r = 2.0**e
    a_eq = model.acceleration(0.0, np.array([r, 0.0, 0.0]), np.zeros(3))
    a_pole = model.acceleration(0.0, np.array([0.0, 0.0, r]), np.zeros(3))
    assert a_eq[0] == float(Fraction(-3, 2) * Fraction(j2) / Fraction(r) ** 4)
    assert a_pole[2] == float(3 * Fraction(j2) / Fraction(r) ** 4)
    assert a_eq[1] == a_eq[2] == a_pole[0] == a_pole[1] == 0.0


@pytest.mark.parametrize("factor", [1.0, 7.5, 60.0, 1000.0])
def test_known_answers_at_far_field_radii(factor):
    """M3T1-R1-F4: the equator and pole known answers of test_known_answers_equator_and_pole
    for the canonical constants at radii out to 1000 R (same 2 gamma_16 derivation)."""
    tol = 2 * gamma(16)
    model = j2_model()
    radius = factor * RE
    a_eq = model.acceleration(0.0, np.array([radius, 0.0, 0.0]), np.zeros(3))
    a_pole = model.acceleration(0.0, np.array([0.0, 0.0, radius]), np.zeros(3))
    expected_eq = exact_equatorial_x(radius)
    expected_pole = float(
        3 * Fraction(J2) * Fraction(MU) * Fraction(RE) ** 2 / Fraction(radius) ** 4
    )
    assert abs(a_eq[0] - expected_eq) <= tol * abs(expected_eq)
    assert abs(a_pole[2] - expected_pole) <= tol * abs(expected_pole)


def dense_latitude_points():
    """Deterministic coverage of every latitude band (M3T1-R1-F4): every 0.5 deg, plus
    latitudes within 1e-1 ... 1e-4 deg of either pole (sin^2 lat up to 1 - 3e-12), at four
    longitudes and radii from R to 60 R."""
    lats = [-90.0 + 0.5 * k for k in range(361)]
    for d in (1e-1, 1e-2, 1e-3, 1e-4):
        lats += [90.0 - d, -90.0 + d]
    pts = []
    for radius in (RE, 1.3 * RE, 7.5 * RE, 60.0 * RE):
        for lat in lats:
            for lon in (0.0, 45.0, 101.0, 213.0):
                la, lo = math.radians(lat), math.radians(lon)
                pts.append(
                    radius
                    * np.array(
                        [math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)]
                    )
                )
    return pts


@pytest.mark.parametrize("j2", [J2, -J2])
def test_gradient_holds_at_every_latitude_band(j2):
    """M3T1-R1-F4: the gradient check of the test below on a dense latitude grid, for J2 and
    for -J2 (the oracle's potential takes J2 as a parameter, so a sign-insensitive
    implementation fails). A 1 % error confined to any latitude band wider than 0.5 deg, or to
    0.99 < sin^2 lat < 0.9999 (84.3 ... 89.4 deg), falls on grid points."""
    model = j2_model(j2)
    for r in dense_latitude_points():
        grad = np.array(j2_potential(*seeds(r), j2=j2).grad)
        grad_abs = np.array(j2_potential(*seeds(r, absolute=True), j2=j2).grad)
        a = model.acceleration(0.0, r, np.zeros(3))
        assert np.all(np.abs(a - grad) <= gamma(64) * (acceleration_abs(r, j2) + grad_abs)), (
            r,
            a,
            grad,
        )


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


def acceleration_abs(r, j2: float = J2) -> np.ndarray:
    """The acceleration expression of SCI-0013 evaluated with every term non-negative."""
    x, y, z = (abs(float(c)) for c in r)
    r2 = x * x + y * y + z * z
    s2 = z * z / r2
    k = 1.5 * abs(j2) * MU * RE * RE / (r2 * r2 * math.sqrt(r2))
    return np.array([k * (1 + 5 * s2) * x, k * (1 + 5 * s2) * y, k * (3 + 5 * s2) * z])


def test_gradient_oracle_detects_a_wrong_coefficient():
    """The bound is tight enough to fail for a plausible coding error (z factor 3 -> 2)."""

    class Wrong(ZonalJ2Gravity):
        def acceleration(self, t, r, v):
            a = super().acceleration(t, r, v)
            x, y, z = (float(c) for c in r)
            r2 = x * x + y * y + z * z
            k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius
            return a - np.array([0.0, 0.0, k0 / (r2 * r2 * math.sqrt(r2)) * z])

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
    """a_J2 . r = -(3/2) J2 mu R^2 / r^3 (1 - 3 sin^2 lat): inward below |lat| = 35.26 deg,
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
