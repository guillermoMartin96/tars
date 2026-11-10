"""S3 test-side self-tests S3-T-17 ... S3-T-20 (M3 T2 S3, proposal v4 section 10.3; PC-7(S3)).

These nodes test the test-side modules committed in A: the DL-4 density twin
(``tests/s3_dl4_density_twin.py``), the point-set generator (``tests/s3_dl4_point_sets.py``)
with its frozen listing (``tests/s3_dl4_points.txt``), and the observation adapter
(``tests/s3_observation.py``). Every subject is imported (or, for S3-T-17, opened) inside the
test body, so an absent subject is a test failure for the declared reason, never a collection
error (v4 section 10.1, section 15.2):

- S3-T-17: FILE(tests/s3_dl4_density_twin.py) -> tagged assertion ``S3-T-17/PRESENT``;
- S3-T-18: MOD(s3_dl4_point_sets);
- S3-T-19: MOD(s3_dl4_density_twin); green input: the protected T0 copy (D-S3-14 (b));
- S3-T-20: MOD(s3_observation).

Path binding PB-1: every repository path is resolved from ``ROOT`` below; no current working
directory, environment variable or absolute path is used. This module never imports the
density component.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]

PIN = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
T0_COPY = ROOT / "docs/science/experiments/m3-t0/data/EarthExponentialAtmosphereData.txt"
TWIN_SOURCE = ROOT / "tests/s3_dl4_density_twin.py"
GENERATOR_SOURCE = ROOT / "tests/s3_dl4_point_sets.py"
LISTING = ROOT / "tests/s3_dl4_points.txt"
COMMIT_A_RECORD = ROOT / "docs/science/experiments/m3-t2/s3/commit-a/listing-generation-record.json"

TWIN_STDLIB_ALLOWLIST = {"math", "hashlib", "pathlib", "struct", "__future__"}
FORBIDDEN_NAMES = {"importlib", "__import__", "runpy"}
PB1_FORBIDDEN_CALLS = {("os", "getcwd"), ("Path", "cwd"), ("os", "environ")}


def _bits(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def _pb1_violations(source: str) -> list[str]:
    """PB-1: no os.getcwd, Path.cwd, os.environ, or absolute path string literal."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and (node.value.id, node.attr) in PB1_FORBIDDEN_CALLS
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


# --- S3-T-17: twin independence by AST (subject: the twin source file) ------------------


def test_s3_t17_twin_independence_ast():
    assert TWIN_SOURCE.is_file(), "S3-T-17/PRESENT twin source absent"
    source = TWIN_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    tars_imports = [m for m in imported if m == "tars" or m.startswith("tars.")]
    assert not tars_imports, f"S3-T-17/AST twin imports tars: {tars_imports}"
    outside = sorted({m.split(".")[0] for m in imported} - TWIN_STDLIB_ALLOWLIST)
    assert not outside, f"S3-T-17/AST twin imports outside the stdlib allowlist: {outside}"
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
            if isinstance(node.value, ast.Name) and (node.value.id, node.attr) == (
                "sys",
                "modules",
            ):
                names.add("sys.modules")
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and (node.value == "tars" or node.value.startswith("tars."))
        ):
            names.add(f"string {node.value!r}")
    bad = sorted(
        names & (FORBIDDEN_NAMES | {"sys.modules"}) | {n for n in names if n.startswith("string ")}
    )
    assert not bad, f"S3-T-17/AST twin references {bad}"
    for path in (Path(__file__), TWIN_SOURCE):
        viol = _pb1_violations(path.read_text(encoding="utf-8"))
        assert not viol, f"S3-T-17/PB1 {path.name}: {viol}"


# --- S3-T-18: frozen listing and generator (subject: s3_dl4_point_sets) -----------------


def test_s3_t18_listing_frozen_and_regenerated():
    gen = importlib.import_module("tests.s3_dl4_point_sets")
    record = json.loads(COMMIT_A_RECORD.read_text())
    frozen = LISTING.read_bytes()
    assert hashlib.sha256(frozen).hexdigest() == record["listing_sha256"], (
        "S3-T-18/SHA frozen listing differs from the commit-A record"
    )
    header = gen.parse_header(frozen.decode("ascii"))
    assert (
        header["body_sha256"]
        == hashlib.sha256(gen.listing_body(frozen.decode("ascii")).encode("ascii")).hexdigest()
    ), "S3-T-18/BODY header body sha256 does not verify"
    assert header["counts_before_dedup"] == gen.EXPECTED_COUNTS, "S3-T-18/COUNTS per-set counts"
    known = [d for d in header["removed_duplicates"] if tuple(d) in gen.KNOWN_DUPLICATES]
    assert len(known) == 6, f"S3-T-18/DUP the 6 known duplicates are not all listed: {known}"
    assert header["final_count"] == record["final_count"], "S3-T-18/COUNTS final count"
    regenerated = gen.render_listing(gen.generate(gen.twin_rows()))
    assert regenerated.encode("ascii") == frozen, "S3-T-18/REGEN regeneration is not byte-identical"
    tree = ast.parse(GENERATOR_SOURCE.read_text(encoding="utf-8"))
    pe = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "p_e_points"]
    assert len(pe) == 1, "S3-T-18/AST P-E mapping function p_e_points not found"
    pe_names = {n.id for n in ast.walk(pe[0]) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(pe[0]) if isinstance(n, ast.Attribute)
    }
    banned = sorted(pe_names & {"fma", "fsum", "Fraction", "Decimal"})
    assert not banned, f"S3-T-18/AST P-E mapping references {banned}"
    stmts = {ast.unparse(n) for n in ast.walk(pe[0]) if isinstance(n, ast.Assign)}
    for s in ("d = hi - lo", "p = d * u", "h = lo + p"):
        assert s in stmts, f"S3-T-18/AST P-E statement {s!r} not present separately"
    all_names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not (all_names & {"exp", "log", "log2", "log10", "fma", "fsum"}), (
        "S3-T-18/AST generator uses a libm transcendental or fused operation"
    )


# --- S3-T-19: twin self-tests (subject: s3_dl4_density_twin; input: the T0 copy) --------


def test_s3_t19_twin_self_tests():
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    raw = T0_COPY.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN, (
        "S3-T-19a/PIN twin source bytes differ from the pin"
    )
    assert twin.DATA_PATH.resolve() == T0_COPY.resolve(), (
        "S3-T-19a/PATH twin does not read the T0 copy"
    )
    rows = twin.TABLE
    lines = raw.decode("ascii").splitlines()
    assert len(rows) == 28 == len(lines), "S3-T-19a/ROWS"
    for row, line in zip(rows, lines, strict=True):
        strings = line.split(", ")
        for value, text in zip(row, strings, strict=True):
            assert _bits(value) == _bits(float(text)), f"S3-T-19a/PARSE {text}"
            assert Fraction(value) == Fraction(float(text)), f"S3-T-19a/PARSE {text}"
    # (b) categories at P-B (raise list, trap interval, zeros, non-finite tokens).
    raise_list = ["-5e-324", "-2.47e-321", "-2.475e-321", "-1e-300", "-1e-9", "-1", "-1e5"]
    for text in raise_list:
        assert _twin_category(twin, float(text)) == "below_zero", f"S3-T-19b/CAT {text}"
    for k in range(1, 501):
        x = -float.fromhex("0x1p-1074") * k
        assert _twin_category(twin, x) == "below_zero", f"S3-T-19b/CAT trap k={k}"
    for x in (0.0, -0.0, float.fromhex("0x0.0000000000001p-1022")):
        assert _twin_category(twin, x) is None, f"S3-T-19b/CAT {x!r} must evaluate"
    for tok in ("nan", "-nan", "inf", "-inf"):
        assert _twin_category(twin, float(tok)) == "nonfinite", f"S3-T-19b/CAT {tok}"
    # (c) band index at P-A: lower band below each base, the upper band at and above it.
    assert twin.band_index(0.0) == 0, "S3-T-19c/BAND 0.0"
    for i in range(1, 28):
        base = rows[i][0]
        assert twin.band_index(_next_down(base)) == i - 1, f"S3-T-19c/BAND below base {i}"
        assert twin.band_index(base) == i, f"S3-T-19c/BAND at base {i}"
        assert twin.band_index(_next_up(base)) == i, f"S3-T-19c/BAND above base {i}"
    # (d) at the 27 bases (metres) and at 0.0 the twin returns rho0 bitwise (A-LM-0).
    for i in range(28):
        h_m = rows[i][0] * 1000.0
        assert _bits(twin.density(h_m)) == _bits(rows[i][1]), f"S3-T-19d/BASE row {i}"


def _twin_category(twin, x: float) -> str | None:
    try:
        twin.density(x)
    except twin.TwinDensityError as exc:
        return exc.category
    return None


def _next_down(x: float) -> float:
    return math.nextafter(x, -math.inf)


def _next_up(x: float) -> float:
    return math.nextafter(x, math.inf)


# --- S3-T-20: adapter self-tests (subject: s3_observation) -------------------------------


class _CategorizedError(Exception):
    category = "below_zero"


class DatasetIntegrityError(Exception):  # name-matched by observe_parse, test-side stub
    def __init__(self, reason: str, rule: str | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.rule = rule


def test_s3_t20_adapter_self_tests():
    obs = importlib.import_module("tests.s3_observation")

    def value_stub(x: float) -> float:
        return x

    def categorized_stub(x: float) -> float:
        raise _CategorizedError

    def unexpected_stub(x: float) -> float:
        raise ZeroDivisionError

    assert obs.observe(value_stub, 1.5) == ("value", "3ff8000000000000"), "S3-T-20/VALUE"
    assert obs.observe(categorized_stub, 1.0) == ("raised", "below_zero"), "S3-T-20/CAT"
    assert obs.observe(unexpected_stub, 1.0) == ("raised", "unexpected:ZeroDivisionError"), (
        "S3-T-20/UNEXPECTED"
    )
    assert obs.observe(value_stub, 0.0) != obs.observe(value_stub, -0.0), "S3-T-20/SIGNED-ZERO"
    assert obs.observe(value_stub, 0.0) == ("value", "0000000000000000"), "S3-T-20/BITS"

    def parse_ok(raw: bytes) -> tuple:
        return (1, 2, 3)

    def parse_rule(raw: bytes) -> tuple:
        raise DatasetIntegrityError("invalid_content", "V-6")

    def parse_unexpected(raw: bytes) -> tuple:
        raise UnicodeDecodeError("ascii", b"\xa0", 0, 1, "x")

    assert obs.observe_parse(parse_ok, b"") == ("accepted", 3), "S3-T-20/PARSE-ACCEPT"
    assert obs.observe_parse(parse_rule, b"") == ("raised", "invalid_content", "V-6"), (
        "S3-T-20/PARSE-RULE"
    )
    assert obs.observe_parse(parse_unexpected, b"") == ("unexpected", "UnicodeDecodeError"), (
        "S3-T-20/PARSE-UNEXPECTED"
    )
    assert _bits(obs.parse_token("-nan")) != _bits(obs.parse_token("nan")), "S3-T-20/TOKEN-NAN-SIGN"
    assert obs.parse_token("0x1.8p+0") == 1.5, "S3-T-20/TOKEN"
