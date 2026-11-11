"""S3 density nodes S3-T-05 ... S3-T-11, S3-T-13 and S3-T-14 (M3 T2 S3; proposal v4 sections 6,
9, 10.3; PC-7(S3)).

Subject: ``tars.sim.atmosphere.density`` and ``density_one_band_250`` (D-S3-09 (a1): domain
h_m >= 0), imported **inside** each test body so the component's absence is the declared red reason
``MOD(tars.sim.atmosphere)``. S3-T-06 reads the component source; its absence is the tagged
assertion ``S3-T-06/PRESENT`` (declared FILE reason).

Every density assertion compares observations through the test-side adapter
(``tests/s3_observation.py``) against the DL-4 twin (``tests/s3_dl4_density_twin.py``), so a wrong
value, a wrong category or an unexpected exception is an ``AssertionError`` carrying the node's tag
(v4 section 10.1). Points come from the frozen listing ``tests/s3_dl4_points.txt`` (set membership
includes the duplicates removed from the listing, resolved to their kept entries).

Path binding PB-1: every repository path is resolved from ``ROOT``. Densities are UNVERIFIED ABOVE
1000 KM (P5); equality with the twin is same-platform output conformance, not accuracy.
"""

import ast
import builtins
import importlib
import json
import math
import struct
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = "tars.sim.atmosphere"
COMPONENT_SOURCE = ROOT / "src/tars/sim/atmosphere.py"
LISTING = ROOT / "tests/s3_dl4_points.txt"
S3_TEST_FILES = (
    "tests/test_s3_package_data.py",
    "tests/test_s3_atmosphere_data.py",
    "tests/test_s3_density.py",
    "tests/test_s3_density_conformance.py",
    "tests/test_s3_witnesses.py",
)
COMPONENT_IMPORTS = {"math", "hashlib", "pathlib", "struct", "dataclasses", "typing"}
COMPONENT_MATH_ATTRS = {"exp", "isfinite"}
SUBSET_ROW_LITERALS = (7.248e-11, 45.546)
EVALUATIONS = 1000


def _load():
    return importlib.import_module(COMPONENT)


def _listing():
    """(kept entries, token by (set, index) including removed duplicates)."""
    gen = importlib.import_module("tests.s3_dl4_point_sets")
    text = LISTING.read_text(encoding="ascii")
    kept = gen.parse_listing(text)
    token = {(s, i): t for s, i, t in kept}
    for a, b, c, d in gen.parse_header(text)["removed_duplicates"]:
        token[(a, b)] = token[(c, d)]
    return gen, kept, token


def _set_tokens(name: str) -> list[str]:
    gen, _, token = _listing()
    return [token[(name, i)] for i in range(gen.EXPECTED_COUNTS[name])]


def _mismatches(fn, twin_fn, tokens):
    from tests.s3_observation import observe, parse_token

    out = []
    for tok in tokens:
        x = parse_token(tok)
        got, want = observe(fn, x), observe(twin_fn, x)
        if got != want:
            out.append((tok, got, want))
    return out


def _p_e_floats() -> list[float]:
    from tests.s3_observation import parse_token

    return [parse_token(t) for t in _set_tokens("P-E")]


# --- S3-T-05: purity, eager immutable table, repetition ---------------------------------


def test_s3_t05a_no_io_during_evaluation(monkeypatch):
    atmosphere = _load()
    points = _p_e_floats()
    counts = {"Path.read_bytes": 0, "Path.open": 0, "builtins.open": 0}

    def counting(name, real):
        def wrapper(*args, **kwargs):
            counts[name] += 1
            return real(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(Path, "read_bytes", counting("Path.read_bytes", Path.read_bytes))
    monkeypatch.setattr(Path, "open", counting("Path.open", Path.open))
    monkeypatch.setattr(builtins, "open", counting("builtins.open", builtins.open))
    for k in range(EVALUATIONS):
        atmosphere.density(points[k % len(points)])
    monkeypatch.undo()
    assert counts == {"Path.read_bytes": 0, "Path.open": 0, "builtins.open": 0}, (
        f"S3-T-05a/IO {counts}"
    )


FRESH_IMPORT = r"""
import json
import sys

sys.path.insert(0, sys.argv[1])
import tars.sim.atmosphere as module

table = vars(module).get("_TABLE")
print("S3-FRESH " + json.dumps({
    "has_table": "_TABLE" in vars(module),
    "table_type": type(table).__name__,
    "rows": len(table) if isinstance(table, tuple) else None,
    "module_file": module.__file__,
}))
"""


def test_s3_t05b_eager_table_and_unchanged_module_state(tmp_path):
    atmosphere = _load()
    script = tmp_path / "s3_fresh_import.py"
    script.write_text(FRESH_IMPORT, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", str(script), str(ROOT / "src")],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=tmp_path,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("S3-FRESH ")]
    rec = json.loads(lines[0][len("S3-FRESH ") :]) if len(lines) == 1 else {"stderr": proc.stderr}
    assert rec.get("has_table") is True and rec.get("table_type") == "tuple", (
        f"S3-T-05b/EAGER {rec}"
    )
    assert rec.get("rows") == 28, f"S3-T-05b/EAGER {rec}"
    assert Path(rec["module_file"]).resolve().is_relative_to((ROOT / "src").resolve()), (
        f"S3-T-05b/BIND {rec}"
    )

    def snapshot():
        return {k: (id(v), repr(v)) for k, v in vars(atmosphere).items() if not k.startswith("__")}

    before = snapshot()
    points = _p_e_floats()
    for k in range(EVALUATIONS):
        atmosphere.density(points[k % len(points)])
        atmosphere.density_one_band_250(points[k % len(points)])
    after = snapshot()
    changed = sorted(set(before) ^ set(after) | {k for k in before if before[k] != after.get(k)})
    assert changed == [], f"S3-T-05b/VARS {changed}"


def test_s3_t05c_repeated_evaluation_bitwise():
    atmosphere = _load()
    from tests.s3_observation import observe

    points = _p_e_floats()
    first = [observe(atmosphere.density, points[k % len(points)]) for k in range(EVALUATIONS)]
    second = [observe(atmosphere.density, points[k % len(points)]) for k in range(EVALUATIONS)]
    diff = [k for k in range(EVALUATIONS) if first[k] != second[k]]
    assert diff == [], f"S3-T-05c/REPEAT {diff[:5]}"
    assert all(o[0] == "value" for o in first), "S3-T-05c/REPEAT non-value"


# --- S3-T-06: static guard and component AST --------------------------------------------


PB1_FORBIDDEN = {("os", "getcwd"), ("Path", "cwd"), ("os", "environ")}


def _pb1_violations(source: str) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and (node.value.id, node.attr) in PB1_FORBIDDEN
        ):
            found.append(f"{node.value.id}.{node.attr}")
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and len(node.value) > 1
            and (PurePosixPath(node.value).is_absolute() or PureWindowsPath(node.value).drive)
        ):
            found.append(f"absolute literal {node.value!r}")
    return found


def test_s3_t06_static_guard_and_component_ast():
    assert COMPONENT_SOURCE.is_file(), "S3-T-06/PRESENT component source absent"
    from tars.validation import architecture

    violations = architecture.scan(ROOT / "src/tars")
    assert violations == [], f"S3-T-06/GUARD {violations}"
    tree = ast.parse(COMPONENT_SOURCE.read_text(encoding="utf-8"))
    problems = []
    math_attrs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in COMPONENT_IMPORTS or alias.asname:
                    problems.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level or root not in COMPONENT_IMPORTS or root == "math":
                problems.append(f"from {node.module} import")
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            problems.append(f"** at line {node.lineno}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"pow", "__import__", "eval", "exec"}:
                problems.append(f"{node.func.id}() at line {node.lineno}")
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "math":
                math_attrs.add(node.attr)
            if node.value.id in {"numpy", "np", "importlib"}:
                problems.append(f"{node.value.id}.{node.attr}")
        elif isinstance(node, ast.Name) and node.id in {"__import__", "importlib", "numpy"}:
            problems.append(f"name {node.id}")
    if not math_attrs <= COMPONENT_MATH_ATTRS:
        problems.append(f"math attributes {sorted(math_attrs - COMPONENT_MATH_ATTRS)}")
    if "exp" not in math_attrs:
        problems.append("math.exp absent")
    assert problems == [], f"S3-T-06/AST {problems}"
    pb1 = {
        rel: _pb1_violations((ROOT / rel).read_text(encoding="utf-8"))
        for rel in S3_TEST_FILES
        if (ROOT / rel).is_file()
    }
    assert all(v == [] for v in pb1.values()), f"S3-T-06/PB1 {pb1}"


# --- S3-T-07 ... S3-T-11: P4, bases, neighbours, top band, far range -------------------


def test_s3_t07_guard_and_categories():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    from tests.s3_observation import observe, parse_token

    tokens = _set_tokens("P-B")
    diff = _mismatches(atmosphere.density, twin.density, tokens)
    assert diff == [], f"S3-T-07/OBS {len(diff)} {diff[:5]}"
    nonfinite = ("nan", "-nan", "inf", "-inf")
    in_range = ("0x0.0p+0", "-0x0.0p+0", "0x0.0000000000001p-1022")
    band0 = observe(twin.density, 0.0)
    assert band0[0] == "value" and all(
        observe(twin.density, parse_token(t)) == band0 for t in in_range[:2]
    ), "S3-T-07/TWIN band-0 values"
    assert observe(twin.density, 5e-324)[0] == "value", "S3-T-07/TWIN 5e-324"
    below = [t for t in tokens if t not in in_range and t not in nonfinite]
    assert len(below) == 507, f"S3-T-07/TWIN raise-list and trap count {len(below)}"
    assert all(observe(twin.density, parse_token(t)) == ("raised", "below_zero") for t in below), (
        "S3-T-07/TWIN below_zero"
    )
    assert all(observe(twin.density, float(t)) == ("raised", "nonfinite") for t in nonfinite), (
        "S3-T-07/TWIN nonfinite"
    )


def test_s3_t08_exact_bases():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    from tests.s3_observation import bits_hex, observe, parse_token

    _, _, token = _listing()
    points = [token[("P-A", 0)]] + [token[("P-A", 3 * i - 1)] for i in range(1, 28)]
    want_points = [0.0] + [twin.TABLE[i][0] * 1000.0 for i in range(1, 28)]
    assert [parse_token(t) for t in points] == want_points, "S3-T-08/POINTS"
    diff = []
    for i, tok in enumerate(points):
        got = observe(atmosphere.density, parse_token(tok))
        want = ("value", bits_hex(twin.TABLE[i][1]))
        if got != want:
            diff.append((i, tok, got, want))
    assert diff == [], f"S3-T-08/OBS {diff[:5]}"


def test_s3_t09_base_neighbours():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    from tests.s3_observation import parse_token

    _, _, token = _listing()
    lower = [token[("P-A", 3 * i - 2)] for i in range(1, 28)]
    upper = [token[("P-A", 3 * i)] for i in range(1, 28)]
    diff = _mismatches(atmosphere.density, twin.density, lower + upper)
    assert diff == [], f"S3-T-09/OBS {len(diff)} {diff[:5]}"
    bands = [
        (twin.band_index(parse_token(lo) / 1000.0), twin.band_index(parse_token(hi) / 1000.0))
        for lo, hi in zip(lower, upper, strict=True)
    ]
    assert bands == [(i - 1, i) for i in range(1, 28)], "S3-T-09/BAND twin bands"


def test_s3_t10_top_band_no_cutoff():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    from tests.s3_observation import bits_hex, observe

    tokens = _set_tokens("P-C")
    diff = _mismatches(atmosphere.density, twin.density, tokens)
    assert diff == [], f"S3-T-10/OBS {diff}"
    top = observe(atmosphere.density, 1e6)
    assert top == ("value", bits_hex(twin.TABLE[27][1])), f"S3-T-10/TOP {top}"
    far = [observe(atmosphere.density, x) for x in (1.001e6, 1.1e6, 1.5e6, 2.0e6)]
    assert all(o[0] == "value" and o[1] != bits_hex(0.0) for o in far), f"S3-T-10/NOCUT {far}"


def test_s3_t11_far_range_values():
    atmosphere = _load()
    from tests.s3_observation import observe, parse_token

    obs = [observe(atmosphere.density, parse_token(t)) for t in _set_tokens("P-D")]
    bad = [o for o in obs if o[0] != "value"]
    assert bad == [], f"S3-T-11/VALUE {len(bad)} {bad[:5]}"
    values = [_from_bits(o[1]) for o in obs]
    assert any(0.0 < v < sys.float_info.min for v in values), "S3-T-11/SUBNORMAL none"
    assert any(o[1] == "0000000000000000" for o in obs), "S3-T-11/ZERO no exact +0.0"


def _from_bits(hex16: str) -> float:
    return struct.unpack("<d", struct.pack("<Q", int(hex16, 16)))[0]


# --- S3-T-13: input type contract (D-S3-10 (a): exactly built-in float) -----------------


class _FloatSubclass(float):
    pass


def test_s3_t13_type_contract():
    atmosphere = _load()
    import numpy

    from tests.s3_observation import observe

    witnesses = (
        1,
        True,
        numpy.float64(1.0),
        numpy.float64("nan"),
        _FloatSubclass(1.0),
        "1.0",
        None,
    )
    diff = [
        (fn.__name__, repr(w), observe(fn, w))
        for fn in (atmosphere.density, atmosphere.density_one_band_250)
        for w in witnesses
        if observe(fn, w) != ("raised", "unsupported_type")
    ]
    assert diff == [], f"S3-T-13/OBS {diff}"


# --- S3-T-14: the one-band 250 km subset (D-S3-09 (a1)) --------------------------------


def _row_bits(rows):
    from tests.s3_observation import bits_hex

    return [tuple(bits_hex(v) for v in row) for row in rows]


def test_s3_t14a_subset_row():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")

    assert isinstance(atmosphere._SUBSET, tuple) and len(atmosphere._SUBSET) == 1, (
        "S3-T-14a/ROW count"
    )
    assert _row_bits(atmosphere._SUBSET) == _row_bits(twin.SUBSET), "S3-T-14a/ROW"


def test_s3_t14b_derivation_sensitivity():
    atmosphere = _load()

    table = atmosphere._TABLE
    assert table[17][0] == 250.0, "S3-T-14b/SENTINEL row 17 base"
    make = getattr(type(table[17]), "_make", tuple)
    sentinel = tuple(make((row[0], 1.5, 2.5)) if i == 17 else row for i, row in enumerate(table))
    derived = atmosphere._derive_one_band_subset(sentinel)
    assert _row_bits(derived) == _row_bits(((250.0, 1.5, 2.5),)), f"S3-T-14b/DERIVE {derived}"


def test_s3_t14c_no_subset_literals():
    _load()
    tree = ast.parse(COMPONENT_SOURCE.read_text(encoding="utf-8"))
    found = [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and type(node.value) in (int, float)
        and any(float(node.value) == lit for lit in SUBSET_ROW_LITERALS)
    ]
    assert found == [], f"S3-T-14c/LITERAL {found}"


def test_s3_t14d_a1_domain_witnesses():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    from tests.s3_observation import bits_hex, observe

    fn = atmosphere.density_one_band_250
    assert observe(fn, -1.0) == ("raised", "below_zero"), "S3-T-14d/A1-P4 h=-0x1.0p+0"
    assert observe(fn, -5e-324) == ("raised", "below_zero"), (
        "S3-T-14d/A1-P4 h=-0x0.0000000000001p-1022"
    )
    for x in (0.0, -0.0):
        got, want = observe(fn, x), observe(twin.density_one_band_250, x)
        assert got[0] == "value" and got == want, f"S3-T-14d/A1-VALUE h={x.hex()} {got} {want}"
    base = 250000.0
    for x in (math.nextafter(base, -math.inf), base, math.nextafter(base, math.inf)):
        got, want = observe(fn, x), observe(twin.density_one_band_250, x)
        assert got[0] == "value" and got == want, f"S3-T-14d/A1-BASE h={x.hex()} {got} {want}"
    assert observe(fn, base) == ("value", bits_hex(twin.SUBSET[0][1])), "S3-T-14d/A1-BASE rho0"


def test_s3_t14e_subset_at_every_listing_point():
    atmosphere = _load()
    twin = importlib.import_module("tests.s3_dl4_density_twin")

    _, kept, _ = _listing()
    diff = _mismatches(
        atmosphere.density_one_band_250, twin.density_one_band_250, [t for _, _, t in kept]
    )
    assert diff == [], f"S3-T-14e/OBS {len(diff)} {diff[:5]}"
