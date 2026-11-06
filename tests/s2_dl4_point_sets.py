"""Component-free generator of the DL-4 point sets (M3 T2 S2; proposal v11 §3.10).

It implements the §3.10 generation rules, in the §3.10 set order and within-set order, and
labels every entry with the test-side **listing geometric label**: an exact transcription of
§3.7.4 with the origin test first (``origin``, ``evolute_region`` or ``passes``). No rule
refers to any production or twin outcome. It imports no component and no ``tars`` module,
only ``math``, ``fractions``, ``random``, ``struct`` and typing support (§3.6). It is not
collected by pytest.

Entry classes (§3.10 RG-POL-0):
- class X (exactly determined): S-EQ, S-AX, S-NEAR, S-BIG, DG-INT, DG-CUSP, S-RAND(ii) and
  PS-A indices 12 to 15. Every coordinate is a stated binary64 constant (decimal or hex), an
  IEEE-encoding neighbour of one, or correctly rounded +, -, *, / on such values; S-RAND(ii)
  adds ``random.Random(20261104)`` through ``uniform``. No libm function is called for them.
- class P (platform library): PS-A indices 0 to 11 (cos, sin), PS-A', PS-OPS, PS-GRID,
  DG-DEEP and S-RAND(i) (the forward expression: sin, cos, sqrt; and radians).

Exact self-checks (RG-POL-4; asserted in every run, any environment; a failure is stop 15):
b_r by the rational midpoint test and the three S-AX hex values; each class X constant
against its exact definition by a rational nearest-value test (d_k = RN(10^-k), RN(sqrt 2),
and pc's three steps); each set's count. They raise ``SelfCheckError``.

The DG-CUSP witness-slot comparison is not an exact self-check (it rests on premises X-1 and
X-2). ``generate()`` returns it with its output; the generation run asserts it (OT-8), and a
re-run reports it as a class X coordinate comparison (OT-9, OT-13; G-17b).
"""

from __future__ import annotations

import math
import random
import struct
from fractions import Fraction
from typing import NamedTuple

# --- The model ellipsoid (r1 §5 step 1; §3.7.1), as test-side literals ------------------
A = 6378137.0
INV_F = 298.257223563
F = 1.0 / INV_F
E2 = F * (2.0 - F)
B_T0 = A * (1.0 - F)  # t0_model.B_WGS84 at K, used only for PS-A's axis points

# Exact rationals for the guard predicate (§3.7.4): K = a^2 e2^2, W = 1 - e2.
_K = Fraction(A) ** 2 * Fraction(E2) ** 2
_W = 1 - Fraction(E2)

SET_ORDER: tuple[str, ...] = (
    "S-EQ",
    "S-AX",
    "S-NEAR",
    "S-BIG",
    "PS-A",
    "PS-A'",
    "PS-OPS",
    "PS-GRID",
    "DG-INT",
    "DG-CUSP",
    "DG-DEEP",
    "S-RAND(i)",
    "S-RAND(ii)",
)
SET_COUNTS: dict[str, int] = {
    "S-EQ": 167,
    "S-AX": 310,
    "S-NEAR": 60,
    "S-BIG": 8,
    "PS-A": 16,
    "PS-A'": 640,
    "PS-OPS": 6498,
    "PS-GRID": 2072,
    "DG-INT": 22,
    "DG-CUSP": 7282,
    "DG-DEEP": 3590,
    "S-RAND(i)": 1000,
    "S-RAND(ii)": 1000,
}
TOTAL_ENTRIES = 22665

CLASS_X_SETS = ("S-EQ", "S-AX", "S-NEAR", "S-BIG", "DG-INT", "DG-CUSP", "S-RAND(ii)")
PS_A_CLASS_X_INDICES = (12, 13, 14, 15)
CLASS_X_COUNT = 8853

LABELS = ("origin", "evolute_region", "passes")

# --- Stated class X constants (§3.10), each exact-checked in every run ------------------
B_R_HEX = "0x1.83fc4141c97d0p+22"  # b_r = RN(b_model), IEEE encoding 0x41583fc4141c97d0
B_R_DOWN_HEX = "0x1.83fc4141c97cfp+22"  # nextDown(b_r)
B_R_UP_HEX = "0x1.83fc4141c97d1p+22"  # nextUp(b_r) = b+
D_K_HEX = {
    12: "0x1.19799812dea11p-40",
    9: "0x1.12e0be826d695p-30",
    6: "0x1.0c6f7a0b5ed8dp-20",
    4: "0x1.a36e2eb1c432dp-14",
    2: "0x1.47ae147ae147bp-7",
}
SQRT2_HEX = "0x1.6a09e667f3bcdp+0"  # RN(sqrt 2)
# pc = RN(RN(a*e2) / RN(sqrt(RN(1 - e2)))); the square-root step is stated by hex and
# exact-checked, so no libm sqrt is called.
SQRT_ONE_MINUS_E2_HEX = "0x1.fe488a57b0c1fp-1"
PC_HEX = "0x1.4eb29f7eac4c2p+15"
# Exact powers of two (S-NEAR, S-BIG) from hex literals.
TINY_HEX = (
    "0x0.0000000000001p-1022",  # 2^-1074
    "0x0.0000000000003p-1022",  # 3 * 2^-1074
    "0x0.0000001000000p-1022",  # 2^-1050
    "0x0.8000000000000p-1022",  # 2^-1023
    "0x0.fffffffffffffp-1022",  # 2^-1022 - 2^-1074
)
P512_HEX = "0x1.0000000000000p+512"
P511_HEX = "0x1.0000000000000p+511"

# §3.7.6 boundary pairs (I-73 f05_guard_crosscheck.out): the inside point of each ray, by
# hex; the first-outside point is its IEEE-encoding successor.
RAYS: tuple[tuple[str, str], ...] = (
    ("+x", "0x1.4d93586d13537p+15"),
    ("x=y", "0x1.d7bf41722e7d2p+14"),
    ("+z", "0x1.4eb29f7eac4c2p+15"),
    ("-z", "0x1.4eb29f7eac4c2p+15"),
    ("(1,0,1)", "0x1.d88a1b7a7d48dp+13"),
    ("(2,0,1)", "0x1.4103325e24047p+13"),
    ("(1,0,2)", "0x1.4141e0b866058p+13"),
    ("(1,1,1)", "0x1.8955006bb0fcap+13"),
)

# DG-CUSP named witnesses and their fixed slots (§3.10 DG-CUSP, v8).
DG_CUSP_WITNESS_SLOTS: tuple[tuple[int, tuple[float, float, float]], ...] = (
    (9, (42697.67270722267, 0.0, 30.0)),
    (6, (42697.67270722267, 0.0, 1.0)),
    (3, (42697.67270722267, 0.0, 1e-3)),
    (51, (42701.94247445068, 0.0, 1.0)),
    (117, (float.fromhex("0x1.b8a74054b25cap+15"), 0.0, float.fromhex("0x1.0624dd2f1a9fcp-10"))),
    (7281, (44832.55634253897, 0.0, 30.0)),
)

# P8 literal lists at K: t0_geodetic.py (blob 33b0e6f7cfdc57b97680770afc974a4131b4a18e),
# lines 26-56, transcribed.
LATS_DEG = (
    -90.0,
    -89.999999,
    -75.0,
    -51.6,
    -30.0,
    -1e-7,
    0.0,
    1e-7,
    15.0,
    33.3,
    45.0,
    51.6,
    60.0,
    80.0,
    89.999999,
    90.0,
)
LONS_DEG = (0.0, 44.4, 135.0, -100.0)
HEIGHTS_M = (
    -10_000.0,
    -100.0,
    0.0,
    1.0,
    25_000.0,
    100_000.0,
    250_000.0,
    900_000.0,
    1_000_000.0,
    2_000_000.0,
)

S_RAND_SEED = 20261104

# Sign triples: sx outermost, sz innermost, + before - (§3.10 order).
SIGNS = tuple((sx, sy, sz) for sx in (1.0, -1.0) for sy in (1.0, -1.0) for sz in (1.0, -1.0))


class SelfCheckError(Exception):
    """An exact self-check failed (RG-POL-4; OT-6, OT-7): stop 15."""


class Entry(NamedTuple):
    set: str
    index: int
    x: float
    y: float
    z: float
    label: str


class SlotCheck(NamedTuple):
    index: int
    expected: tuple[float, float, float]
    generated: tuple[float, float, float]
    equal: bool


class Generation(NamedTuple):
    entries: list[Entry]
    slot_checks: list[SlotCheck]


class ClassXConstants(NamedTuple):
    b_r: float
    b_down: float
    b_up: float
    d_k: dict[int, float]
    sqrt2: float
    pc: float
    cusp: float
    tiny: tuple[float, ...]
    p512: float
    p511: float


# --- Exact helpers --------------------------------------------------------------------


def _encoding(v: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", v))[0]


def _from_encoding(n: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", n))[0]


def next_up(v: float) -> float:
    """IEEE-encoding successor of a positive finite binary64 (no libm call)."""
    if not (v > 0.0 and v < float.fromhex("0x1.fffffffffffffp+1023")):
        raise SelfCheckError(f"next_up domain: {v!r}")
    return _from_encoding(_encoding(v) + 1)


def next_down(v: float) -> float:
    """IEEE-encoding predecessor of a positive finite binary64 (no libm call)."""
    if not (v > 0.0 and v == v):
        raise SelfCheckError(f"next_down domain: {v!r}")
    return _from_encoding(_encoding(v) - 1)


def same_bits(u: float, v: float) -> bool:
    return struct.pack("<d", u) == struct.pack("<d", v)


def _is_nearest(v: float, exact: Fraction) -> bool:
    """True iff the positive normal binary64 ``v`` is RN(exact), ties to even."""
    err = abs(Fraction(v) - exact)
    lo, hi = next_down(v), next_up(v)
    err_lo, err_hi = abs(Fraction(lo) - exact), abs(Fraction(hi) - exact)
    if err < err_lo and err < err_hi:
        return True
    if err in (err_lo, err_hi):
        return _encoding(v) % 2 == 0
    return False


def _is_nearest_sqrt(v: float, radicand: Fraction) -> bool:
    """True iff ``v`` = RN(sqrt(radicand)): radicand lies strictly between the squares of
    the midpoints around v (ties are impossible for a non-square rational radicand)."""
    lo, hi = Fraction(next_down(v)), Fraction(next_up(v))
    mid_lo, mid_hi = (lo + Fraction(v)) / 2, (Fraction(v) + hi) / 2
    return mid_lo**2 < radicand < mid_hi**2


def _check(condition: bool, what: str) -> None:
    if not condition:
        raise SelfCheckError(what)


def listing_label(x: float, y: float, z: float) -> str:
    """The listing geometric label: §3.7.4 transcribed, exact rationals, origin first.

    r in E  <=>  D' >= 0 and D'^3 >= 27 K W p^2 z^2,  D' = K - p^2 - W z^2,
    with K = a^2 e2^2 and W = 1 - e2 on the model ellipsoid. Closed region.
    """
    if x == 0.0 and y == 0.0 and z == 0.0:
        return "origin"
    p2 = Fraction(x) ** 2 + Fraction(y) ** 2
    z2 = Fraction(z) ** 2
    d = _K - p2 - _W * z2
    if d >= 0 and d**3 >= 27 * _K * _W * p2 * z2:
        return "evolute_region"
    return "passes"


def is_class_x(set_name: str, index: int) -> bool:
    """RG-POL-0 entry class: True for class X, False for class P."""
    if set_name in CLASS_X_SETS:
        return True
    return set_name == "PS-A" and index in PS_A_CLASS_X_INDICES


# --- Class X constants, exact-checked (OT-6) -------------------------------------------


def class_x_constants() -> ClassXConstants:
    """Build every stated class X constant and exact-check it. Raises SelfCheckError."""
    b2 = Fraction(A) ** 2 * (1 - Fraction(E2))  # b_model^2, exact
    lo = float.fromhex(B_R_HEX)
    hi = next_up(lo)
    _check(Fraction(lo) ** 2 < b2 < Fraction(hi) ** 2, "b_model is not bracketed by b_r, b_r+")
    mid = (Fraction(lo) + Fraction(hi)) / 2
    _check(b2 != mid**2, "b_model tie at the midpoint")
    b_r = lo if b2 < mid**2 else hi
    _check(b_r.hex() == B_R_HEX, f"b_r = {b_r.hex()} != {B_R_HEX}")
    _check(_encoding(b_r) == 0x41583FC4141C97D0, "b_r IEEE encoding")
    b_down, b_up = next_down(b_r), next_up(b_r)
    _check(b_down.hex() == B_R_DOWN_HEX, f"nextDown(b_r) = {b_down.hex()}")
    _check(b_up.hex() == B_R_UP_HEX, f"nextUp(b_r) = {b_up.hex()}")

    d_k = {}
    for k, hx in D_K_HEX.items():
        d = float.fromhex(hx)
        _check(_is_nearest(d, Fraction(1, 10**k)), f"d_{k} is not RN(10^-{k})")
        d_k[k] = d
    sqrt2 = float.fromhex(SQRT2_HEX)
    _check(_is_nearest_sqrt(sqrt2, Fraction(2)), "RN(sqrt 2)")

    one_minus_e2 = 1.0 - E2
    _check(_is_nearest(one_minus_e2, 1 - Fraction(E2)), "pc step 1: RN(1 - e2)")
    root = float.fromhex(SQRT_ONE_MINUS_E2_HEX)
    _check(_is_nearest_sqrt(root, Fraction(one_minus_e2)), "pc step 2: RN(sqrt(RN(1 - e2)))")
    c = A * E2
    _check(_is_nearest(c, Fraction(A) * Fraction(E2)), "pc step 3a: RN(a * e2)")
    pc = c / root
    _check(_is_nearest(pc, Fraction(c) / Fraction(root)), "pc step 3b: RN(RN(a e2) / root)")
    _check(pc.hex() == PC_HEX, f"pc = {pc.hex()} != {PC_HEX}")

    tiny = tuple(float.fromhex(h) for h in TINY_HEX)
    exact_tiny = (
        Fraction(1, 2**1074),
        Fraction(3, 2**1074),
        Fraction(1, 2**1050),
        Fraction(1, 2**1023),
        Fraction(1, 2**1022) - Fraction(1, 2**1074),
    )
    for v, q in zip(tiny, exact_tiny, strict=True):
        _check(Fraction(v) == q, f"S-NEAR t = {v.hex()} is not exact")
    p512, p511 = float.fromhex(P512_HEX), float.fromhex(P511_HEX)
    _check(Fraction(p512) == 2**512 and Fraction(p511) == 2**511, "S-BIG powers of two")
    return ClassXConstants(b_r, b_down, b_up, d_k, sqrt2, pc, c, tiny, p512, p511)


# --- The forward expression (class P) ---------------------------------------------------


def forward(lat: float, lon: float, h: float) -> tuple[float, float, float]:
    """t0_model.geodetic_to_cartesian at K (t0_model.py:133-141), same operations and order."""
    s, c = math.sin(lat), math.cos(lat)
    n = A / math.sqrt(1.0 - E2 * s * s)
    return ((n + h) * c * math.cos(lon), (n + h) * c * math.sin(lon), (n * (1.0 - E2) + h) * s)


# --- The §3.10 rules --------------------------------------------------------------------


def _sets(k: ClassXConstants) -> dict[str, list[tuple[float, float, float]]]:
    b_r, b_down, b_up = k.b_r, k.b_down, k.b_up
    d_k, sqrt2, pc, cusp = k.d_k, k.sqrt2, k.pc, k.cusp
    tiny, p512, p511 = k.tiny, k.p512, k.p511
    out: dict[str, list[tuple[float, float, float]]] = {}

    # S-EQ (167): boundary values ascending, each with its 8 sign triples; scan; end.
    eq = []
    for x0 in (next_down(A), A, next_up(A)):
        for sx, sy, sz in SIGNS:
            eq.append((sx * x0, sy * 0.0, sz * 0.0))
    for j in range(1, 143):
        eq.append((A + 250000.0 * j, 0.0, 0.0))
    eq.append((4.2e7, 0.0, 0.0))
    out["S-EQ"] = eq

    # S-AX (310): {nextDown(b_r), b_r, nextUp(b_r)} x 8 signs; scan +z before -z; ends.
    ax = []
    for z0 in (b_down, b_r, b_up):
        for sx, sy, sz in SIGNS:
            ax.append((sx * 0.0, sy * 0.0, sz * z0))
    for j in range(1, 143):
        for sz in (1.0, -1.0):
            ax.append((0.0, 0.0, sz * (b_up + 250000.0 * j)))
    for sz in (1.0, -1.0):
        ax.append((0.0, 0.0, sz * 4.2e7))
    out["S-AX"] = ax

    # S-NEAR (60): t outermost, then z, then (t,0,z), (0,t,z), (t,t,z).
    near = []
    for t in tiny:
        for z in (b_up, -b_up, 7.0e6, -7.0e6):
            near.extend(((t, 0.0, z), (0.0, t, z), (t, t, z)))
    out["S-NEAR"] = near

    # S-BIG (8): as listed.
    out["S-BIG"] = [
        (1e308, 0.0, 1e308),
        (1e300, 1e300, 1e300),
        (p512, 0.0, 0.0),
        (next_down(p512), 0.0, 0.0),
        (next_up(p512), 0.0, 0.0),
        (0.0, 0.0, p512),
        (p511, p511, p511),
        (p512, p512, p512),
    ]

    # PS-A (16): t0_geodetic.exact_answers() at K, lines 111-126.
    psa = []
    for rho in (A - 10_000.0, A, A + 250_000.0, A + 2_000_000.0):
        for lon in (0.0, 0.7, 2.0):
            psa.append((rho * math.cos(lon), rho * math.sin(lon), 0.0))
    for z in (B_T0 - 10_000.0, B_T0, B_T0 + 250_000.0, -(B_T0 + 250_000.0)):
        psa.append((0.0, 0.0, z))
    out["PS-A"] = psa

    # PS-A' (640): LATS_DEG x LONS_DEG x HEIGHTS_M, as t0_geodetic.py builds them.
    out["PS-A'"] = [
        forward(math.radians(la), math.radians(lo), h)
        for la in LATS_DEG
        for lo in LONS_DEG
        for h in HEIGHTS_M
    ]

    # PS-OPS (6 498): height outermost, then i ascending, then longitude {0, 37 deg}.
    ops_heights = (-10_000.0, -1_000.0, 0.0, 1.0, 80_000.0, 120_000.0, 400_000.0)
    ops_heights += (2_000_000.0, 36_000_000.0)
    out["PS-OPS"] = [
        forward(math.radians(i * 0.5), lon, h)
        for h in ops_heights
        for i in range(-180, 181)
        for lon in (0.0, math.radians(37.0))
    ]

    # PS-GRID (2 072): i ascending, then j ascending, then height.
    grid_heights = (0.0, 1.0, 100_000.0, 120_000.0, 400_000.0, 2_000_000.0, 36_000_000.0)
    out["PS-GRID"] = [
        forward(math.radians(5.0 * i), math.radians(45.0 * j), h)
        for i in range(-18, 19)
        for j in range(8)
        for h in grid_heights
    ]

    # DG-INT (22): the six I-73 §B points; then each ray's inside and first-outside point.
    dg_int = [
        (1.0, 0.0, pc * (1 + 1e-9)),
        (1e-3, 0.0, pc * (1 + 1e-3)),
        (100.0, 0.0, pc * (1 + 1e-6)),
        (15121.263417223743, 0.0, 15121.263417223743),
        (23722.193304103585, 0.0, 7907.3977680345279),
        (30000.0, 0.0, 30000.0),
    ]
    for name, inside_hex in RAYS:
        for t in (float.fromhex(inside_hex), next_up(float.fromhex(inside_hex))):
            if name == "+x":
                dg_int.append((t, 0.0, 0.0))
            elif name == "x=y":
                dg_int.append((t, t, 0.0))
            elif name == "+z":
                dg_int.append((0.0, 0.0, t))
            elif name == "-z":
                dg_int.append((0.0, 0.0, -t))
            elif name == "(1,0,1)":
                dg_int.append((t, 0.0, t))
            elif name == "(2,0,1)":
                dg_int.append((2 * t, 0.0, t))
            elif name == "(1,0,2)":
                dg_int.append((t, 0.0, 2 * t))
            else:  # (1,1,1)
                dg_int.append((t, t, t))
    out["DG-INT"] = dg_int

    # DG-CUSP (7 282): near-cusp (k outermost, z, variants); edge scan (z outermost, i);
    # then (44 832.55634253897, 0, 30) at index 7 281. No membership test, no conditional.
    cusp_pts = []
    for kk in (12, 9, 6, 4, 2):
        x_k = cusp * (1 + d_k[kk])
        for z in (1e-6, 1e-3, 1.0, 30.0, 1000.0):
            cusp_pts.extend(((x_k, 0.0, z), (x_k / sqrt2, x_k / sqrt2, z), (x_k, 0.0, -z)))
    for z in (1e-3, 1.0, 30.0, 300.0, 1000.0, 3000.0):
        for i in range(1201):
            cusp_pts.append((cusp * (1.30 + 0.0005 * i), 0.0, z))
    cusp_pts.append((44832.55634253897, 0.0, 30.0))
    out["DG-CUSP"] = cusp_pts

    # DG-DEEP (3 590): height outermost, then i ascending, longitude 0.
    deep_heights = (-1e5, -1e6, -3e6, -5e6, -6e6, -6.2e6, -6.3e6, -6.32e6, -6.33e6, -6.335e6)
    out["DG-DEEP"] = [
        forward(math.radians(0.5 * i), 0.0, h) for h in deep_heights for i in range(-179, 180)
    ]

    # S-RAND (2 000): one generator; (i) lat, lon, height per point; then (ii) x, y, z.
    rng = random.Random(S_RAND_SEED)
    rand_i = []
    for _ in range(1000):
        la = rng.uniform(-90.0, 90.0)
        lo = rng.uniform(-180.0, 180.0)
        hn = rng.uniform(0.0, 36_000_000.0)
        rand_i.append(forward(math.radians(la), math.radians(lo), hn))
    out["S-RAND(i)"] = rand_i
    rand_ii = []
    for _ in range(1000):
        x = rng.uniform(-6.4e6, 6.4e6)
        y = rng.uniform(-6.4e6, 6.4e6)
        z = rng.uniform(-6.4e6, 6.4e6)
        rand_ii.append((x, y, z))
    out["S-RAND(ii)"] = rand_ii
    return out


def generate() -> Generation:
    """Run every rule. Exact self-checks raise SelfCheckError (stop 15). The DG-CUSP
    witness-slot comparisons are returned, never raised (RG-POL-4, RG-POL-8)."""
    constants = class_x_constants()
    sets = _sets(constants)
    _check(tuple(sets) == SET_ORDER, "set order")
    entries: list[Entry] = []
    for name in SET_ORDER:
        pts = sets[name]
        _check(len(pts) == SET_COUNTS[name], f"{name} count {len(pts)} != {SET_COUNTS[name]}")
        for i, (x, y, z) in enumerate(pts):
            entries.append(Entry(name, i, x, y, z, listing_label(x, y, z)))
    _check(len(entries) == TOTAL_ENTRIES, "total count")
    cusp = sets["DG-CUSP"]
    slots = []
    for idx, witness in DG_CUSP_WITNESS_SLOTS:
        got = cusp[idx]
        equal = all(same_bits(u, v) for u, v in zip(got, witness, strict=True))
        slots.append(SlotCheck(idx, witness, got, equal))
    return Generation(entries, slots)


HEADER = "# set,index,x,y,z,label  (S2 DL-4 frozen listing; proposal v11 section 3.10)"


def format_listing(entries: list[Entry]) -> str:
    lines = [HEADER]
    for e in entries:
        lines.append(f"{e.set},{e.index},{e.x.hex()},{e.y.hex()},{e.z.hex()},{e.label}")
    return "\n".join(lines) + "\n"


def parse_listing(text: str) -> list[Entry]:
    """Parse the frozen file's own text (no generation, no platform-library call)."""
    lines = text.split("\n")
    if lines[0] != HEADER or lines[-1] != "":
        raise ValueError("listing header or final newline")
    entries = []
    for line in lines[1:-1]:
        s, i, x, y, z, label = line.split(",")
        if label not in LABELS:
            raise ValueError(f"unknown label {label!r}")
        entries.append(
            Entry(s, int(i), float.fromhex(x), float.fromhex(y), float.fromhex(z), label)
        )
    return entries
