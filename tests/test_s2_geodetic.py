"""S2 gate tests for the geodetic component (M3 T2 S2; proposal v11 §3.11 Part A).

G-01 to G-07, G-09 to G-11 and G-13 to G-17. G-08 and G-12 are in
``test_s2_geodetic_conformance.py``; G-17a and G-17b in ``test_s2_dl4_points.py``.

Red-first (§3.14): the component is imported inside each test function, so its absence
fails each node for its declared reason (a per-test ImportError or AttributeError, or an
assertion), never a collection error (I-40 §9a). G-10 and G-13 are guards (exempt).

Every expected exception is checked by type and attribute, never by ``pytest.raises
(ValueError)`` alone: GeodeticDomainError is itself a ValueError (I77-04).
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import struct
import subprocess
import sys
import types
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

from tests import s2_dl4_point_sets as gen
from tests.conftest import REPO_ROOT

GEODESY = REPO_ROOT / "src" / "tars" / "sim" / "geodesy.py"
LISTING = REPO_ROOT / "tests" / "s2_dl4_points.txt"

CATEGORY = {
    "not_binary64": "input",
    "non_finite": "input",
    "origin": "geometric",
    "evolute_region": "geometric",
    "numerical_failure": "failure",
    "overflow": "numerical",
    "non_convergence": "numerical",
}
MESSAGE = {
    "not_binary64": "geodetic input: an integer component is not exactly a binary64 value",
    "non_finite": "geodetic input: a component is NaN or infinite",
    "origin": "geodetic input: the origin has no geodetic height",
    "evolute_region": "geodetic input: the point lies in the evolute region (DR-0029 P8)",
    "numerical_failure": (
        "geodetic evaluation failed; the cause is undetermined and this is not a domain "
        "classification"
    ),
    "overflow": "geodetic evaluation: a result left the binary64 range",
    "non_convergence": "geodetic evaluation: the DQ-1 stop test was not met within 60 iterations",
}

# §3.7.6 boundary pairs on the model ellipsoid: the inside point by hex; the outside point
# is the next binary64 up. Located independently of the component's predicate (I-73
# f05_guard_crosscheck: M1 parametric evolute and M2 normal count); re-located by M1
# bisection in the commit-D derivation output (OB-19).
RAYS = {
    "+x": ("0x1.4d93586d13537p+15", lambda t: (t, 0.0, 0.0)),
    "x=y": ("0x1.d7bf41722e7d2p+14", lambda t: (t, t, 0.0)),
    "+z": ("0x1.4eb29f7eac4c2p+15", lambda t: (0.0, 0.0, t)),
    "-z": ("0x1.4eb29f7eac4c2p+15", lambda t: (0.0, 0.0, -t)),
    "(1,0,1)": ("0x1.d88a1b7a7d48dp+13", lambda t: (t, 0.0, t)),
    "(2,0,1)": ("0x1.4103325e24047p+13", lambda t: (2 * t, 0.0, t)),
    "(1,0,2)": ("0x1.4141e0b866058p+13", lambda t: (t, 0.0, 2 * t)),
    "(1,1,1)": ("0x1.8955006bb0fcap+13", lambda t: (t, t, t)),
}
OUTSIDE_HEX = {
    "+x": "0x1.4d93586d13538p+15",
    "x=y": "0x1.d7bf41722e7d3p+14",
    "+z": "0x1.4eb29f7eac4c3p+15",
    "-z": "0x1.4eb29f7eac4c3p+15",
    "(1,0,1)": "0x1.d88a1b7a7d48ep+13",
    "(2,0,1)": "0x1.4103325e24048p+13",
    "(1,0,2)": "0x1.4141e0b866059p+13",
    "(1,1,1)": "0x1.8955006bb0fcbp+13",
}

G14_REJECTION_POINTS = (
    (42697.67270722267, 0.0, 30.0),
    (42697.67270722267, 0.0, 1.0),
    (42697.67270722267, 0.0, 1e-3),
    (42701.94247445068, 0.0, 1.0),
    (44832.55634253897, 0.0, 30.0),
)


def _geo():
    from tars.sim import geodesy

    return geodesy


def _bits(v: float) -> bytes:
    return struct.pack("<d", v)


def _reason(geo, r) -> str | None:
    """The component's outcome: None if accepted, else the GeodeticDomainError reason."""
    try:
        geo.geodetic(r)
    except geo.GeodeticDomainError as exc:
        return exc.reason
    return None


def _raises_reason(geo, r, reason: str):
    """Assert that geodetic(r) raises GeodeticDomainError with ``reason`` (exact type)."""
    try:
        geo.geodetic(r)
    except geo.GeodeticDomainError as exc:
        assert exc.reason == reason, (r, exc.reason)
        assert exc.category == CATEGORY[reason], (r, exc.category)
        assert str(exc) == MESSAGE[reason], (r, str(exc))
        return exc
    except BaseException as exc:  # any other exception is a failure of this node
        raise AssertionError(f"{r!r}: expected {reason}, got {type(exc).__name__}: {exc}") from exc
    raise AssertionError(f"{r!r}: expected {reason}, but it was accepted")


def _raises_type(geo, r, exc_type):
    try:
        geo.geodetic(r)
    except BaseException as exc:
        assert type(exc) is exc_type, (r, type(exc))
        assert not isinstance(exc, geo.GeodeticDomainError)
        return exc
    raise AssertionError(f"{r!r}: expected {exc_type.__name__}, but it was accepted")


def _accepted(geo, r) -> tuple[float, float]:
    try:
        out = geo.geodetic(r)
    except geo.GeodeticDomainError as exc:
        raise AssertionError(f"{r!r}: expected accepted, got {exc.reason}") from exc
    assert type(out) is tuple and len(out) == 2
    h, phi = out
    assert type(h) is float and type(phi) is float
    assert math.isfinite(h) and math.isfinite(phi)
    return h, phi


def _frozen():
    return gen.parse_listing(LISTING.read_text())


# --- G-01, U-10 (1/f part) ------------------------------------------------------------


def test_g01_inverse_flattening_is_the_nga_value():
    from tars.sim.constants import WGS84_INVERSE_FLATTENING

    # NGA.STND.0036_1.0.0_WGS84 (2014): 1/f = 298.257223563.
    assert float("298.257223563") == WGS84_INVERSE_FLATTENING
    assert type(WGS84_INVERSE_FLATTENING) is float


# --- G-02, X-P2 -------------------------------------------------------------------------


def test_g02_derived_f_and_e2_are_correctly_rounded_step_by_step():
    """_F = RN(1/RN(298.257223563)); _E2 = RN(_F * RN(2 - _F)), each step from exact
    rationals (Fraction -> float is correctly rounded), and fixed hex strings."""
    geo = _geo()
    inv = float(Fraction("298.257223563"))
    f = float(1 / Fraction(inv))
    two_minus_f = float(2 - Fraction(f))
    e2 = float(Fraction(f) * Fraction(two_minus_f))
    assert _bits(geo._F) == _bits(f)
    assert _bits(geo._E2) == _bits(e2)
    assert geo._F.hex() == "0x1.b775a84f3e128p-9"
    assert geo._E2.hex() == "0x1.b6b90f1fe94f0p-8"
    assert geo._A == 6378137.0


# --- G-03, U-20 domain ----------------------------------------------------------------


def test_g03_point_inside_the_evolute_region():
    _raises_reason(_geo(), (30_000.0, 30_000.0, 0.0), "evolute_region")


def test_g03_all_eight_signed_zero_origins():
    geo = _geo()
    for sx, sy, sz in gen.SIGNS:
        _raises_reason(geo, (sx * 0.0, sy * 0.0, sz * 0.0), "origin")


def test_g03_non_origin_subnormal_is_in_the_evolute_region():
    _raises_reason(_geo(), (5e-324, 0.0, 0.0), "evolute_region")


@pytest.mark.parametrize("ray", list(RAYS))
def test_g03_boundary_pair_inside_point(ray):
    inside_hex, make = RAYS[ray]
    _raises_reason(_geo(), make(float.fromhex(inside_hex)), "evolute_region")


@pytest.mark.parametrize("ray", list(RAYS))
def test_g03_boundary_pair_outside_point_geometric(ray):
    """Exact on all platforms: neither origin nor evolute_region (U-20, r2 §8.2 ±1 ulp)."""
    inside_hex, make = RAYS[ray]
    outside = gen.next_up(float.fromhex(inside_hex))
    assert outside.hex() == OUTSIDE_HEX[ray]
    assert _reason(_geo(), make(outside)) not in ("origin", "evolute_region")


@pytest.mark.parametrize("ray", list(RAYS))
def test_g03_boundary_pair_outside_point_accepted(ray):
    """[OPT-b] Outcome assertion: accepted (a rejection here is stop 5, never a change
    of the point set)."""
    _, make = RAYS[ray]
    _accepted(_geo(), make(float.fromhex(OUTSIDE_HEX[ray])))


# --- G-04, non-finite inputs ------------------------------------------------------------


def test_g04_non_finite_component_in_each_position():
    geo = _geo()
    for bad in (math.nan, math.inf, -math.inf):
        for pos in range(3):
            r = [7.0e6, 0.0, 1.0]
            r[pos] = bad
            _raises_reason(geo, tuple(r), "non_finite")


def test_g04_mixed_non_finite_cases():
    geo = _geo()
    for r in (
        (math.nan, math.inf, 0.0),
        (math.inf, -math.inf, math.nan),
        (0.0, math.nan, 0.0),
        (0.0, 0.0, math.inf),
        (0.0, math.nan, 7.0e6),
        (30_000.0, 30_000.0, math.nan),
    ):
        _raises_reason(geo, r, "non_finite")


# --- G-05, overflow ---------------------------------------------------------------------


def test_g05_overflow_rows_far_from_the_edge():
    geo = _geo()
    for r in ((1.5e308, 1.5e308, 0.0), (1.5e308, 0.0, 1.5e308)):
        exc = _raises_reason(geo, r, "overflow")
        assert type(exc) is geo.GeodeticDomainError
        assert not isinstance(exc, OverflowError)


def test_g05_large_finite_rows_are_accepted():
    geo = _geo()
    p512 = float.fromhex("0x1p+512")
    p511 = float.fromhex("0x1p+511")
    for r in (
        (1e308, 0.0, 1e308),
        (1e300, 1e300, 1e300),
        (p512, 0.0, 0.0),
        (gen.next_down(p512), 0.0, 0.0),
        (gen.next_up(p512), 0.0, 0.0),
        (0.0, 0.0, p512),
        (p511, p511, p511),
        (p512, p512, p512),
    ):
        _accepted(geo, r)


def test_g05_no_overflow_or_zero_division_error_escapes():
    geo = _geo()
    for r in (
        (1.5e308, 1.5e308, 0.0),
        (1.5e308, 0.0, 1.5e308),
        (1e308, 0.0, 1e308),
        (1e300, 1e300, 1e300),
        (float.fromhex("0x1p+512"),) * 3,
        (7.0e6, 0.0, 1.0),
    ):
        try:
            geo.geodetic(r)
        except geo.GeodeticDomainError:
            pass
        except (OverflowError, ZeroDivisionError) as exc:
            raise AssertionError(f"{r!r}: {type(exc).__name__} escaped") from exc


# --- G-06, error type, precedence and normalization -------------------------------------


def test_g06_error_class_is_a_value_error_with_reason_and_category():
    geo = _geo()
    assert issubclass(geo.GeodeticDomainError, ValueError)
    assert not issubclass(geo.GeodeticDomainError, ArithmeticError)


@pytest.mark.parametrize(
    ("r", "reason"),
    [
        ((math.nan, 0.0, 0.0), "non_finite"),
        ((math.inf, 0.0, 0.0), "non_finite"),
        ((0.0, -0.0, 0.0), "origin"),
        ((5e-324, 0.0, 0.0), "evolute_region"),
        ((10**400, 0, 0), "not_binary64"),
        ((2**53 + 1, 0, 0), "not_binary64"),
        ((42697.67270722267, 0.0, 30.0), "non_convergence"),
        ((1.5e308, 0.0, 1.5e308), "overflow"),  # [F-11] libm-dependent, 18% margin
    ],
)
def test_g06_section_3_8_order_table(r, reason):
    _raises_reason(_geo(), r, reason)


def test_g06_fraction_component_is_a_type_error():
    _raises_type(_geo(), (Fraction(1, 3), 0.0, 7.0e6), TypeError)


@pytest.mark.parametrize(
    "r",
    [
        (7.0e6, 0.0),
        (7.0e6, 0.0, 1.0, 0.0),
        ("7e6", 0.0, 1.0),
        (True, 0.0, 1.0),
        (None, 0.0, 1.0),
        (Fraction(7_000_000), 0.0, 1.0),
        (Decimal("7e6"), 0.0, 1.0),
        (np.float32(7.0e6), 0.0, 1.0),
        (np.int64(7_000_000), 0.0, 1.0),
        (np.longdouble(7.0e6), 0.0, 1.0),
    ],
)
def test_g06_structure_and_type_errors(r):
    _raises_type(_geo(), r, TypeError)


def test_g06_numpy_float64_is_accepted_bit_identical_to_float():
    geo = _geo()
    a = geo.geodetic((np.float64(7.0e6), np.float64(0.0), np.float64(1.0)))
    b = geo.geodetic((7.0e6, 0.0, 1.0))
    assert [_bits(v) for v in a] == [_bits(v) for v in b]


def test_g06_float_subclass_whose_abs_raises_is_normalized():
    geo = _geo()
    called = []

    class F(float):
        def __abs__(self):
            called.append("__abs__")
            raise OverflowError("trap")

    assert geo.geodetic((F(7.0e6), 0.0, 1.0)) == geo.geodetic((7.0e6, 0.0, 1.0))
    assert called == []


def test_g06_float_subclass_overrides_never_run():
    geo = _geo()
    called = []

    class F(float):
        def __eq__(self, other):
            called.append("__eq__")
            return True

        __hash__ = float.__hash__

        def __mul__(self, other):
            called.append("__mul__")
            return 0.0

        def __float__(self):
            called.append("__float__")
            return 0.0

    assert geo.geodetic((F(7.0e6), 0.0, 1.0)) == geo.geodetic((7.0e6, 0.0, 1.0))
    # __eq__ returning True does not make it the origin.
    assert geo.geodetic((F(7.0e6), F(0.0), F(1.0))) == geo.geodetic((7.0e6, 0.0, 1.0))
    assert called == []


def test_g06_int_subclass_overrides_never_run():
    geo = _geo()
    called = []

    class I(int):  # noqa: E742
        def __index__(self):
            called.append("__index__")
            return 1

        def __int__(self):
            called.append("__int__")
            return 1

        def __float__(self):
            called.append("__float__")
            return 1.0

        def __eq__(self, other):
            called.append("__eq__")
            return True

        __hash__ = int.__hash__

    assert geo.geodetic((I(7_000_000), 0, 1)) == geo.geodetic((7.0e6, 0.0, 1.0))
    assert called == []


def test_g06_class_faking_object_is_a_type_error():
    geo = _geo()

    class Fake:
        """Claims float through __class__ and converts to 7e6, so an isinstance-based
        normalization would accept it (the designated killer of that mutant)."""

        @property
        def __class__(self):
            return float

        def __float__(self):
            return 7.0e6

    assert isinstance(Fake(), float)
    _raises_type(geo, (Fake(), 0.0, 1.0), TypeError)


def test_g06_structural_key_error_propagates_unchanged():
    geo = _geo()
    sentinel = KeyError("caller")

    class Seq:
        def __len__(self):
            return 3

        def __getitem__(self, i):
            raise sentinel

    try:
        geo.geodetic(Seq())
    except BaseException as exc:
        assert exc is sentinel
    else:
        raise AssertionError("accepted")


def test_g06_sv1_getitem_value_error_sentinel_propagates_by_identity():
    geo = _geo()

    class SentinelError(ValueError):
        pass

    sentinel = SentinelError("caller __getitem__")

    class Seq:
        def __len__(self):
            return 3

        def __getitem__(self, i):
            raise sentinel

    try:
        geo.geodetic(Seq())
    except BaseException as exc:
        assert exc is sentinel
        assert not isinstance(exc, geo.GeodeticDomainError)
    else:
        raise AssertionError("accepted")


def test_g06_sv2_len_overflow_error_sentinel_propagates_by_identity():
    geo = _geo()

    class SentinelError(OverflowError):
        pass

    sentinel = SentinelError("caller __len__")

    class Seq:
        def __len__(self):
            raise sentinel

        def __getitem__(self, i):
            return 0.0

    try:
        geo.geodetic(Seq())
    except BaseException as exc:
        assert exc is sentinel
        assert not isinstance(exc, geo.GeodeticDomainError)
    else:
        raise AssertionError("accepted")


def test_g06_fixed_message_and_category_per_reason():
    geo = _geo()
    for reason, category in CATEGORY.items():
        exc = geo.GeodeticDomainError(reason)
        assert exc.reason == reason
        assert exc.category == category
        assert str(exc) == MESSAGE[reason]


# --- G-07, interface --------------------------------------------------------------------


def test_g07_returns_h_then_phi_as_builtin_floats():
    geo = _geo()
    out = geo.geodetic((7.0e6, 0.0, 0.0))
    assert type(out) is tuple and len(out) == 2
    h, phi = out
    assert type(h) is float and type(phi) is float
    assert h == 7.0e6 - 6378137.0  # (h, phi): the height comes first
    assert _bits(phi) == _bits(0.0)


def test_g07_list_tuple_and_float64_ndarray_are_bit_identical():
    geo = _geo()
    for x, y, z in ((7.0e6, -1.0e5, 3.3e6), (0.0, 0.0, 7.0e6), (1e300, 1e300, 1e300)):
        a = geo.geodetic([x, y, z])
        b = geo.geodetic((x, y, z))
        c = geo.geodetic(np.array([x, y, z], dtype=np.float64))
        assert [_bits(v) for v in a] == [_bits(v) for v in b] == [_bits(v) for v in c]


def test_g07_inputs_are_not_mutated():
    geo = _geo()
    lst = [7.0e6, 0.0, 1.0]
    arr = np.array(lst, dtype=np.float64)
    geo.geodetic(lst)
    geo.geodetic(arr)
    assert lst == [7.0e6, 0.0, 1.0]
    assert arr.tolist() == [7.0e6, 0.0, 1.0]


# --- G-09, X-P1 and U-24 --------------------------------------------------------------

_G09_POINTS = (
    (7.0e6, 0.0, 1.0),
    (4.0e6, 3.0e6, 3.5e6),
    (-2.0e6, 5.0e6, -4.0e6),
    (0.0, 0.0, 7.0e6),
    (30_000.0, 0.0, 30_000.0),
)


def _g09_outputs(geo) -> list[str]:
    return [",".join(v.hex() for v in geo.geodetic(r)) for r in _G09_POINTS]


def test_g09_repeated_in_process_evaluation_is_byte_identical():
    geo = _geo()
    first = _g09_outputs(geo)
    for _ in range(3):
        assert _g09_outputs(geo) == first


def test_g09_second_subprocess_is_byte_identical():
    geo = _geo()
    code = (
        "import json; from tars.sim.geodesy import geodetic\n"
        f"pts = {list(_G09_POINTS)!r}\n"
        "print(json.dumps([','.join(v.hex() for v in geodetic(r)) for r in pts]))\n"
    )
    res = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=REPO_ROOT
    )
    assert json.loads(res.stdout) == _g09_outputs(geo)


def test_g09_module_state_is_unchanged_after_calls():
    geo = _geo()
    before = {k: id(v) for k, v in vars(geo).items()}
    for r in (*_G09_POINTS, (30_000.0, 30_000.0, 0.0), (math.nan, 0.0, 0.0)):
        _reason(geo, r)
    assert {k: id(v) for k, v in vars(geo).items()} == before


def test_g09_architecture_scan_covers_geodesy():
    from tars.validation.architecture import scan

    assert GEODESY.exists()
    assert scan(REPO_ROOT / "src" / "tars") == []


# --- G-10, X-P4 (A-FP-1 at run time) [F-08]; a guard ---------------------------------
#
# Every operand is built at run time from a string, so CPython cannot fold the
# expression at compile time (which would test the compiler's host, not this run).


def _h(s: str) -> float:
    return float.fromhex(s)


def test_g10_w1_round_to_nearest_excludes_toward_zero_and_down():
    # 1 + 3*2^-54 == 1 + 2^-52. False under round-toward-zero and round-down.
    assert _h("0x1p+0") + _h("0x3p-54") == _h("0x1.0000000000001p+0")


def test_g10_w2_round_to_nearest_excludes_up():
    # 1 + 2^-54 == 1. False under round-up.
    assert _h("0x1p+0") + _h("0x1p-54") == _h("0x1p+0")


def test_g10_w3_ties_to_even_excludes_ties_away():
    # 1 + 2^-53 == 1. False under ties-away.
    assert _h("0x1p+0") + _h("0x1p-53") == _h("0x1p+0")


def test_g10_w4_tie_to_even_upward():
    # (1 + 2^-52) + 2^-53 == 1 + 2^-51, tie to even.
    assert _h("0x1.0000000000001p+0") + _h("0x1p-53") == _h("0x1.0000000000002p+0")


def test_g10_w5_no_flush_to_zero():
    # 2^-1022 / 2 != 0. False under flush-to-zero.
    assert _h("0x1p-1022") / _h("0x1p+1") != _h("0x0p+0")


def test_g10_w6_no_denormals_are_zero():
    # 2^-1074 * 1.0 == 2^-1074 != 0. False under denormals-are-zero.
    tiny = _h("0x0.0000000000001p-1022")
    product = tiny * _h("0x1p+0")
    assert product == tiny
    assert product != _h("0x0p+0")


def test_g10_w7_subnormal_tie_to_even():
    # 2^-1074 / 2 == 0, the subnormal tie to even.
    assert _h("0x0.0000000000001p-1022") / _h("0x1p+1") == _h("0x0p+0")


# --- G-11, RQ-6 support (a guard) -----------------------------------------------------


def test_g11_geodesy_imports_only_math_fractions_numbers_typing_and_constants():
    assert GEODESY.exists(), "src/tars/sim/geodesy.py is absent"
    tree = ast.parse(GEODESY.read_text())
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add("." * node.level + (node.module or ""))
    allowed = {"__future__", "math", "fractions", "numbers", "typing", "tars.sim.constants"}
    assert modules <= allowed, modules
    assert not any("numpy" in m for m in modules)


# --- G-13, scope (a guard; the full path check is the host script) --------------------

# Blob ids at K 83d573bdb4933f5d2376423d6b8e9f3348a4ab6f.
K_BLOBS = {
    "src/tars/sim/forces.py": "6b082683f5c6c3fcf2c3861f5b08c733458b5534",
    "src/tars/sim/simulator.py": "22ca0abfd9770322da3cb7db75eea730d5c71cd9",
    "docs/science/assumptions.md": "063e58778c3b4acdff5719bbdf80c20315b88fd0",
}
# sha256 of the newline-joined sha256s of ast.dump(stmt) for every top-level statement at K.
K_AST = {
    "src/tars/sim/constants.py": (
        13,
        "75ec916ecb9d7f9f055066c5434b0ac853facae88370d3a3e26b4d2f4f433bd1",
    ),
    "tests/test_constants.py": (
        20,
        "e3a51c05fdd0fc84c74294af45ca9088c40d278ed0647cc83a4d7b27521048ef",
    ),
}
ADDED = {
    "src/tars/sim/constants.py": ("Assign", "WGS84_INVERSE_FLATTENING"),
    "tests/test_constants.py": (
        "FunctionDef",
        "test_wgs84_inverse_flattening_literal_only_in_constants_module",
    ),
}


def _git_blob(path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _added(stmt, kind: str, name: str) -> bool:
    if kind == "Assign":
        return (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == name
        )
    return isinstance(stmt, ast.FunctionDef) and stmt.name == name


def test_g13_protected_files_are_byte_identical_to_k():
    for rel, blob in K_BLOBS.items():
        assert _git_blob(REPO_ROOT / rel) == blob, rel


@pytest.mark.parametrize("rel", list(K_AST))
def test_g13_existing_statements_are_ast_identical_to_k(rel):
    tree = ast.parse((REPO_ROOT / rel).read_text())
    kind, name = ADDED[rel]
    assert len([s for s in tree.body if _added(s, kind, name)]) <= 1
    kept = [s for s in tree.body if not _added(s, kind, name)]
    count, digest = K_AST[rel]
    lines = [hashlib.sha256(ast.dump(s).encode()).hexdigest() for s in kept]
    assert len(lines) == count
    assert hashlib.sha256("\n".join(lines).encode()).hexdigest() == digest


# --- G-14, non-convergence: fixed outcomes on every platform ----------------------------


@pytest.mark.parametrize("r", G14_REJECTION_POINTS)
def test_g14_rejection_points_raise_non_convergence(r):
    _raises_reason(_geo(), r, "non_convergence")


def test_g14_named_acceptance_points_are_accepted():
    geo = _geo()
    _accepted(geo, (30_000.0, 0.0, 30_000.0))
    for ray, (_inside, make) in RAYS.items():
        _accepted(geo, make(float.fromhex(OUTSIDE_HEX[ray])))


@pytest.mark.parametrize("set_name", ["S-EQ", "S-AX", "S-NEAR", "S-BIG"])
def test_g14_enumerated_acceptance_sets_are_accepted(set_name):
    geo = _geo()
    entries = [e for e in _frozen() if e.set == set_name]
    assert len(entries) == gen.SET_COUNTS[set_name]
    bad = [(e.index, _reason(geo, (e.x, e.y, e.z))) for e in entries]
    bad = [b for b in bad if b[1] is not None]
    assert bad == [], f"stop 16: {set_name} entries not accepted: {bad[:10]}"


# --- G-15, protected-set availability ------------------------------------------------


@pytest.mark.parametrize("set_name", ["PS-A", "PS-A'", "PS-OPS", "PS-GRID"])
def test_g15_protected_sets_are_accepted(set_name):
    geo = _geo()
    entries = [e for e in _frozen() if e.set == set_name]
    assert len(entries) == gen.SET_COUNTS[set_name]
    bad = []
    for e in entries:
        try:
            h, phi = geo.geodetic((e.x, e.y, e.z))
        except geo.GeodeticDomainError as exc:
            bad.append((e.index, exc.reason))
            continue
        if not (math.isfinite(h) and math.isfinite(phi)):
            bad.append((e.index, "non-finite output"))
    assert bad == [], f"stop 16: {set_name} entries not accepted: {bad[:10]}"


# --- G-16, fault-injection handling (complete fixtures) --------------------------------

_POINT = (7.0e6, 0.0, 1.0)
_BASE = {"hypot": 7.0e6, "atan2": 0.0, "sin": 0.0, "cos": 1.0, "sqrt": 1.0}
_SCHED_00 = ["hypot", "atan2", "sin", "sqrt", "atan2", "sin", "cos", "sqrt"]
_SCHED_07 = ["hypot", "atan2", *(["sin", "sqrt", "atan2"] * 60), "sin", "cos", "sqrt"]


class _Raise:
    def __init__(self, exc):
        self.exc = exc


def _fixture(rules: dict, log: list):
    """A fresh library object defining exactly the declared calls; no fallback to math
    and no __getattr__. A rule is a constant, a callable of the 0-based call index for
    that function, or _Raise(exc)."""
    counts = dict.fromkeys(rules, 0)

    def make(name):
        rule = rules[name]

        def fn(*args):
            i = counts[name]
            counts[name] += 1
            log.append(name)
            value = rule(i) if callable(rule) else rule
            if isinstance(value, _Raise):
                raise value.exc
            return value

        return fn

    return types.SimpleNamespace(**{name: make(name) for name in rules})


def _run_case(monkeypatch, rules, schedule, *, isnan=None):
    geo = _geo()
    log: list = []
    lib = _fixture(rules, log)
    assert set(vars(lib)) == set(rules)
    monkeypatch.setattr(geo, "_LIB", lib)
    if isnan is not None:
        monkeypatch.setattr(geo, "_isnan", isnan)
    else:
        assert geo._isnan is math.isnan and geo._isinf is math.isinf
    try:
        outcome = ("returned", geo.geodetic(_POINT))
    except BaseException as exc:
        outcome = ("raised", exc)
    monkeypatch.undo()
    assert geo._LIB is math and geo._isnan is math.isnan and geo._isinf is math.isinf
    assert log == schedule, (log[:12], len(log))
    return outcome


def _expect_reason(outcome, reason, cause=None):
    geo = _geo()
    kind, value = outcome
    assert kind == "raised", outcome
    assert type(value) is geo.GeodeticDomainError, type(value)
    assert value.reason == reason
    assert value.category == CATEGORY[reason]
    if cause is not None:
        assert type(value.__cause__) is cause, type(value.__cause__)


def _rules(**over):
    rules = dict(_BASE)
    rules.update(over)
    return rules


def _atan2_never_converging(i):
    return 0.1 + i * 1e-10


def test_g16_fi00_control(monkeypatch):
    kind, value = _run_case(monkeypatch, _rules(), _SCHED_00)
    assert kind == "returned"
    assert value == (621863.0, 0.0)


def test_g16_fi01_sin_nan(monkeypatch):  # departs from S-4, S-9
    _expect_reason(_run_case(monkeypatch, _rules(sin=math.nan), _SCHED_00), "numerical_failure")


def test_g16_fi02_sqrt_raises_value_error(monkeypatch):  # S-4
    out = _run_case(monkeypatch, _rules(sqrt=_Raise(ValueError("injected"))), _SCHED_00[:4])
    _expect_reason(out, "numerical_failure", ValueError)


def test_g16_fi03_sqrt_zero_divides(monkeypatch):  # S-2, S-9
    out = _run_case(monkeypatch, _rules(sqrt=0.0), _SCHED_00[:4])
    _expect_reason(out, "numerical_failure", ZeroDivisionError)


def test_g16_fi04_atan2_raises_overflow_error(monkeypatch):  # S-5
    out = _run_case(monkeypatch, _rules(atan2=_Raise(OverflowError("injected"))), _SCHED_00[:2])
    _expect_reason(out, "numerical_failure", OverflowError)


def test_g16_fi05_sin_raises_type_error_propagates(monkeypatch):
    sentinel = TypeError("injected")
    kind, value = _run_case(monkeypatch, _rules(sin=_Raise(sentinel)), _SCHED_00[:3])
    assert kind == "raised" and value is sentinel


def test_g16_fi06_missing_cos_propagates_attribute_error(monkeypatch):
    rules = _rules()
    del rules["cos"]
    kind, value = _run_case(monkeypatch, rules, _SCHED_00[:6])
    assert kind == "raised" and type(value) is AttributeError


def test_g16_fi07_overflow_before_non_convergence(monkeypatch):  # S-6, S-9
    out = _run_case(monkeypatch, _rules(hypot=math.inf, atan2=_atan2_never_converging), _SCHED_07)
    _expect_reason(out, "overflow")


def test_g16_fi08_nan_before_overflow_and_non_convergence(monkeypatch):  # S-6
    out = _run_case(monkeypatch, _rules(hypot=math.nan, atan2=_atan2_never_converging), _SCHED_07)
    _expect_reason(out, "numerical_failure")


def test_g16_fi09_nan_before_overflow(monkeypatch):  # S-4, S-6
    out = _run_case(monkeypatch, _rules(hypot=math.inf, sin=math.nan), _SCHED_00)
    _expect_reason(out, "numerical_failure")


def test_g16_fi10_huge_cos_overflows(monkeypatch):  # S-9 (I-75 countermodel)
    _expect_reason(_run_case(monkeypatch, _rules(cos=1e308), _SCHED_00), "overflow")


def test_g16_fi11_stop_test_met_at_update_60_is_accepted(monkeypatch):
    def atan2(i):
        return (59 - i) * 1e-10 if i <= 59 else 1e-15

    kind, value = _run_case(monkeypatch, _rules(atan2=atan2), _SCHED_07)
    assert kind == "returned", value
    h, phi = value
    assert _bits(phi) == _bits(1e-15)
    assert h == 621863.0


def test_g16_fi12_stop_test_first_met_at_61_is_non_convergence(monkeypatch):
    def atan2(i):
        return (60 - i) * 1e-10 if i <= 60 else 1e-15

    _expect_reason(_run_case(monkeypatch, _rules(atan2=atan2), _SCHED_07), "non_convergence")


def test_g16_fi13_failure_in_final_height_before_non_convergence(monkeypatch):  # S-4
    def sqrt(i):
        return 1.0 if i < 60 else _Raise(ValueError("injected"))

    out = _run_case(monkeypatch, _rules(atan2=_atan2_never_converging, sqrt=sqrt), _SCHED_07)
    _expect_reason(out, "numerical_failure", ValueError)


def test_g16_fi14_sin_raises_name_error_propagates(monkeypatch):
    sentinel = NameError("injected")
    kind, value = _run_case(monkeypatch, _rules(sin=_Raise(sentinel)), _SCHED_00[:3])
    assert kind == "raised" and value is sentinel


def test_g16_fi15_post_check_exception_is_not_wrapped(monkeypatch):
    class SentinelError(ValueError):
        pass

    sentinel = SentinelError("injected into _isnan")

    def isnan(v):
        raise sentinel

    kind, value = _run_case(monkeypatch, _rules(), _SCHED_00, isnan=isnan)
    assert kind == "raised" and value is sentinel


# --- G-17, listing geometric outcomes -------------------------------------------------


def test_g17_every_listing_entry_has_its_geometric_outcome():
    geo = _geo()
    entries = _frozen()
    assert len(entries) == gen.TOTAL_ENTRIES
    bad = []
    rejects = 0
    for e in entries:
        reason = _reason(geo, (e.x, e.y, e.z))
        if e.label in ("origin", "evolute_region"):
            rejects += 1
            if reason != e.label:
                bad.append((e.set, e.index, e.label, reason))
        elif reason in ("origin", "evolute_region"):
            bad.append((e.set, e.index, e.label, reason))
    assert bad == [], f"stop 15: {bad[:10]}"
    assert rejects == 64
