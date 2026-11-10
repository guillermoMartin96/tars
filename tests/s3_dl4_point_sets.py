"""S3 DL-4 point-set generator (test-side; M3 T2 S3, proposal v4 section 8.4).

Generates the S3 point listing from the 28 rows parsed by the twin's own parser, in this
order (counts before de-duplication):

- P-A (U-12): 0.0; then for i = 1 ... 27: nd(M_i), M_i, nu(M_i), with M_i = base_i * 1000.0 (82).
- P-B (U-14): the raise list (7 decimal strings through ``float()``); the whole trap interval
  -(k * 2^-1074) for k = 1 ... 500; then +0.0, -0.0, 5e-324; then the tokens nan, -nan, inf,
  -inf (514).
- P-C (U-15): nd(1e6), 1e6, nu(1e6), 1.001e6, 1.1e6, 1.5e6, 2.0e6 (7).
- P-D (U-16): for e = 21 ... 1023, ldexp(1.0, e) then ldexp(1.5, e); then sys.float_info.max;
  then the transition neighbourhoods: with Decimal precision 60 and the top row's decimal
  strings (b, rho0, H), T_sub = b - H*ln(2^-1022/rho0) and T_zero = b - H*ln(2^-1075/rho0)
  (km); for T in (T_sub, T_zero) and j = -64 ... 64: float(str((T + j) * 1000)) (2265).
- P-E (bands): rng = random.Random(0x5333444C); for band i = 0 ... 27, 32 draws: lo = M_i;
  hi = M_{i+1} (i < 27) or 2.0e6 (top band); u = rng.random(); d = hi - lo; p = d * u;
  h = lo + p, each a separately rounded binary64 operation; if h >= hi: h = nd(hi) (896).

Identity is the 64-bit pattern (non-finite tokens by their text); the first occurrence in
listing order is kept and every removed duplicate is listed in the header. The 6 known
deterministic duplicates are asserted. Only exact IEEE operations, correctly rounded
conversions, ``random.random()`` and ``decimal`` are used, so the output does not depend on
libm: no ``math.exp``/``log``, no ``fma``/``fsum`` (S3-T-18). Stdlib only, no ``tars`` import.
"""

from __future__ import annotations

import hashlib
import importlib
import math
import random
import struct
import sys
from decimal import Context, Decimal

FORMAT = "s3-dl4-points/1"
SEED = 0x5333444C
SET_ORDER = ("P-A", "P-B", "P-C", "P-D", "P-E")
EXPECTED_COUNTS = {"P-A": 82, "P-B": 514, "P-C": 7, "P-D": 2265, "P-E": 896}
# (set, index-in-set, kept-as-set, kept-as-index)
KNOWN_DUPLICATES = {
    ("P-B", 7, "P-B", 0),  # k = 1: -5e-324
    ("P-B", 506, "P-B", 1),  # k = 500: -2.47e-321
    ("P-B", 507, "P-A", 0),  # +0.0
    ("P-C", 0, "P-A", 79),  # nd(1e6)
    ("P-C", 1, "P-A", 80),  # 1e6
    ("P-C", 2, "P-A", 81),  # nu(1e6)
}
RAISE_LIST = ("-5e-324", "-2.47e-321", "-2.475e-321", "-1e-300", "-1e-9", "-1", "-1e5")
NONFINITE = ("nan", "-nan", "inf", "-inf")


class GenerationError(Exception):
    pass


def nd(x: float) -> float:
    return math.nextafter(x, -math.inf)


def nu(x: float) -> float:
    return math.nextafter(x, math.inf)


def twin_rows():
    """The 28 rows from the twin's own parser (v4 section 8.4 inputs)."""
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    return twin.TABLE


def _top_row_strings() -> tuple[str, str, str]:
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    raw = twin.DATA_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != twin.PIN:
        raise GenerationError("data digest")
    last = raw.decode("ascii").split("\n")[-2]
    b, rho0, h = last.split(", ")
    return b, rho0, h


def p_a_points(rows) -> list:
    pts = [0.0]
    for i in range(1, 28):
        m = rows[i][0] * 1000.0
        pts += [nd(m), m, nu(m)]
    return pts


def p_b_points() -> list:
    pts: list = [float(s) for s in RAISE_LIST]
    tiny = math.ldexp(1.0, -1074)
    pts += [-(k * tiny) for k in range(1, 501)]
    pts += [0.0, -0.0, 5e-324]
    pts += list(NONFINITE)
    return pts


def p_c_points() -> list:
    return [nd(1e6), 1e6, nu(1e6), 1.001e6, 1.1e6, 1.5e6, 2.0e6]


def p_d_points() -> list:
    pts = []
    for e in range(21, 1024):
        pts += [math.ldexp(1.0, e), math.ldexp(1.5, e)]
    pts.append(sys.float_info.max)
    ctx = Context(prec=60)
    b, rho0, scale = (Decimal(s) for s in _top_row_strings())
    two = Decimal(2)
    t_sub = ctx.subtract(b, ctx.multiply(scale, ctx.divide(ctx.power(two, -1022), rho0).ln(ctx)))
    t_zero = ctx.subtract(b, ctx.multiply(scale, ctx.divide(ctx.power(two, -1075), rho0).ln(ctx)))
    for t in (t_sub, t_zero):
        for j in range(-64, 65):
            pts.append(float(str(ctx.multiply(ctx.add(t, Decimal(j)), Decimal(1000)))))
    return pts


def p_e_points(rows) -> list:
    rng = random.Random(SEED)
    pts = []
    for i in range(28):
        lo = rows[i][0] * 1000.0
        hi = rows[i + 1][0] * 1000.0 if i < 27 else 2.0e6
        for _ in range(32):
            u = rng.random()
            d = hi - lo
            p = d * u
            h = lo + p
            if h >= hi:
                h = nd(hi)
            pts.append(h)
    return pts


def _identity(x) -> str:
    if isinstance(x, str):
        return "tok:" + x
    return "bits:" + struct.pack("<d", x).hex()


def _token(x) -> str:
    return x if isinstance(x, str) else x.hex()


def generate(rows) -> dict:
    sets = {
        "P-A": p_a_points(rows),
        "P-B": p_b_points(),
        "P-C": p_c_points(),
        "P-D": p_d_points(),
        "P-E": p_e_points(rows),
    }
    counts = {name: len(sets[name]) for name in SET_ORDER}
    if counts != EXPECTED_COUNTS:
        raise GenerationError(f"per-set counts {counts}")
    seen: dict[str, tuple[str, int]] = {}
    kept, removed = [], []
    for name in SET_ORDER:
        for index, x in enumerate(sets[name]):
            key = _identity(x)
            if key in seen:
                removed.append((name, index, *seen[key]))
                continue
            seen[key] = (name, index)
            kept.append((name, index, _token(x)))
    if not set(removed) >= KNOWN_DUPLICATES:
        raise GenerationError(f"known duplicates missing: {KNOWN_DUPLICATES - set(removed)}")
    return {"counts": counts, "removed": removed, "kept": kept}


def render_listing(gen: dict) -> str:
    body = "".join(f"{s},{i},{t}\n" for s, i, t in gen["kept"])
    counts = " ".join(f"{k}={v}" for k, v in gen["counts"].items())
    removed = ";".join(f"{a}:{b}>{c}:{d}" for a, b, c, d in gen["removed"])
    header = (
        f"# {FORMAT}\n# seed 0x{SEED:08X}\n# counts-before-dedup {counts}\n"
        f"# removed-duplicates {removed}\n# final-count {len(gen['kept'])}\n"
        f"# body-sha256 {hashlib.sha256(body.encode('ascii')).hexdigest()}\n"
    )
    return header + body


def listing_body(text: str) -> str:
    return "".join(line + "\n" for line in text.split("\n")[:-1] if not line.startswith("#"))


def parse_header(text: str) -> dict:
    head = [line[2:] for line in text.split("\n") if line.startswith("# ")]
    out: dict = {"format": head[0]}
    for line in head[1:]:
        key, _, value = line.partition(" ")
        if key == "counts-before-dedup":
            out["counts_before_dedup"] = {
                k: int(v) for k, v in (item.split("=") for item in value.split())
            }
        elif key == "removed-duplicates":
            dups = []
            for item in value.split(";") if value else []:
                left, right = item.split(">")
                a, b = left.split(":")
                c, d = right.split(":")
                dups.append((a, int(b), c, int(d)))
            out["removed_duplicates"] = dups
        elif key == "final-count":
            out["final_count"] = int(value)
        elif key == "body-sha256":
            out["body_sha256"] = value
        elif key == "seed":
            out["seed"] = value
    return out


def parse_listing(text: str) -> list[tuple[str, int, str]]:
    return [
        (s, int(i), t) for s, i, t in (line.split(",") for line in listing_body(text).splitlines())
    ]
