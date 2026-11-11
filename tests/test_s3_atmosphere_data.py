"""S3 dataset nodes S3-T-01a, S3-T-01c, S3-T-02 ... S3-T-04 and S3-T-16 (M3 T2 S3; proposal v4
sections 5, 10.2, 10.3; PC-7(S3)).

Subject: the density component ``tars.sim.atmosphere`` (checked loader, private parser, pinned
digest) and the package data file. The component is imported **inside** each test body, so its
absence is the declared red reason (``MOD(tars.sim.atmosphere)``), never a collection error.
Route D-S3-14 (b): the package data file is absent until BC; S3-T-01c then fails with the tagged
assertion ``S3-T-01c/SAME`` (declared FILE reason). S3-T-02 (b) runs a fresh ``python -I`` import
of a temporary copy of ``src/tars`` and fails, while the component is absent, on the tagged
assertion ``S3-T-02b/CAT`` (the probe observes ``ModuleNotFoundError``).

Every assertion carries a tag ``S3-T-nn[x]/<ASPECT>`` (v4 section 10.1). In S3-T-02 the category
``/CAT`` is asserted before the call-count order ``/ORDER`` for each fixture (section 5.3).

Tamper fixtures (v4 section 10.2), built from the pinned bytes of the protected T0 copy; each
construction rule and sha256 is frozen below. F-T1 changes row 5's rho0 ``3.206e-4`` (the file's
spelling of v4's ``3.206e-04``) to ``3.207e-4``; F-T6 is the V-5 token ``3.206e-0x`` in the same
place.

Path binding PB-1: every repository path is resolved from ``ROOT``; no cwd, environment variable,
absolute path or the checkout's ``tars.__file__`` is used. Densities are UNVERIFIED ABOVE 1000 KM
(P5); these nodes check data, loading and parsing only.
"""

import hashlib
import importlib
import json
import math
import shutil
import struct
import subprocess
import sys
import warnings
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIN = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
DATA_NAME = "EarthExponentialAtmosphereData.txt"
PACKAGE_DATA = ROOT / "src/tars/sim/data" / DATA_NAME
T0_COPY = ROOT / "docs/science/experiments/m3-t0/data" / DATA_NAME
SRC_TARS = ROOT / "src/tars"
COMPONENT = "tars.sim.atmosphere"
LABEL = "densities are UNVERIFIED ABOVE 1000 KM (P5)"

FIXTURE_SHA256 = {
    "F-T1": "5593b8d47e320cd24b936ebbf084e22693805895ab01553448ce0befa372fa81",
    "F-T2": "058780c55a85c251409e26cd6f3320181a4ee48746694bbde569b92a8b6ed67f",
    "F-T3": "4766421613d54028b1d0af32fc9eaecde1cc883d55dd88beeb78109e8a2d12af",
    "F-T4": "f3cd6fe323c39d504716a79c68ce0806fe415e4b7491d43904aced57fbf44c3c",
    "F-T5": "946b55d4c71327681ae3e3218efc8773c1f63b8b3a39724f2a4f138f4fa81ddd",
    "F-T6": "c9b603549546a5c8f2efb04c058a6fbd77ec774d4f63c88aa2860577566329b0",
    "F-T7": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
TAMPER_IDS = tuple(FIXTURE_SHA256)

# S3-T-16: the 84 binary64 values of the table (row-major: base_km, rho0, H_km), as exact hex.
EXPECTED_HEX = (
    "0x0.0p+0", "0x1.399999999999ap+0", "0x1.cfef9db22d0e5p+2",
    "0x1.9000000000000p+4", "0x1.3f67f4dbdf8f4p-5", "0x1.965604189374cp+2",
    "0x1.e000000000000p+4", "0x1.22a6f3f52fc26p-6", "0x1.aba5e353f7ceep+2",
    "0x1.4000000000000p+5", "0x1.044f1a1986b9cp-8", "0x1.e374bc6a7ef9ep+2",
    "0x1.9000000000000p+5", "0x1.151611ba3ca75p-10", "0x1.0c395810624ddp+3",
    "0x1.e000000000000p+5", "0x1.502c683dd6fb2p-12", "0x1.edb22d0e56042p+2",
    "0x1.1800000000000p+6", "0x1.6fd728706191fp-14", "0x1.a322d0e560419p+2",
    "0x1.4000000000000p+6", "0x1.3f9b20825686fp-16", "0x1.7322d0e560419p+2",
    "0x1.6800000000000p+6", "0x1.c7cdabe7466d2p-19", "0x1.5872b020c49bap+2",
    "0x1.9000000000000p+6", "0x1.1c6169e53c7e6p-21", "0x1.7820c49ba5e35p+2",
    "0x1.b800000000000p+6", "0x1.9eefd18001147p-24", "0x1.d0d4fdf3b645ap+2",
    "0x1.e000000000000p+6", "0x1.a2d85fba9427dp-26", "0x1.2f22d0e560419p+3",
    "0x1.0400000000000p+7", "0x1.23820d9e8ad09p-27", "0x1.945a1cac08312p+3",
    "0x1.1800000000000p+7", "0x1.0839f491369c9p-28", "0x1.02624dd2f1aa0p+4",
    "0x1.2c00000000000p+7", "0x1.1c7fa67512855p-29", "0x1.685e353f7ced9p+4",
    "0x1.6800000000000p+7", "0x1.2c62f6b0effcbp-31", "0x1.dbd70a3d70a3dp+4",
    "0x1.9000000000000p+7", "0x1.32a75efa28581p-32", "0x1.28d70a3d70a3dp+5",
    "0x1.f400000000000p+7", "0x1.3ec539a9d9915p-34", "0x1.6c5e353f7ced9p+5",
    "0x1.2c00000000000p+8", "0x1.a96109fb3c9bcp-36", "0x1.ad0624dd2f1aap+5",
    "0x1.5e00000000000p+8", "0x1.4ee285c2fe815p-37", "0x1.aa624dd2f1aa0p+5",
    "0x1.9000000000000p+8", "0x1.061fa26b2c1fap-38", "0x1.d41eb851eb852p+5",
    "0x1.c200000000000p+8", "0x1.be23495b592ffp-40", "0x1.e69fbe76c8b44p+5",
    "0x1.f400000000000p+8", "0x1.88350d313b064p-41", "0x1.fe9374bc6a7f0p+5",
    "0x1.2c00000000000p+9", "0x1.476964b4dfbc9p-43", "0x1.1f570a3d70a3dp+6",
    "0x1.5e00000000000p+9", "0x1.45852a961bed2p-45", "0x1.62ab020c49ba6p+6",
    "0x1.9000000000000p+9", "0x1.a58973ecbede6p-47", "0x1.f28f5c28f5c29p+6",
    "0x1.c200000000000p+9", "0x1.79f12c33e0f47p-48", "0x1.6a1999999999ap+7",
    "0x1.f400000000000p+9", "0x1.b31570d2d5481p-49", "0x1.0c00000000000p+8",
)  # fmt: skip


class S3Record(UserWarning):
    """A per-run S3 record emitted into the pytest warnings summary (D-S3-07 (a))."""


def _emit(prefix: str, payload: dict) -> None:
    body = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(body.encode()).hexdigest()
    warnings.warn(f"{prefix} sha256={digest} {body}", S3Record, stacklevel=1)


def _bits(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def _pinned_bytes() -> bytes:
    raw = T0_COPY.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN, "S3-T-02/FIXTURE T0 copy digest"
    return raw


def _tamper(fid: str, raw: bytes) -> bytes:
    row5 = b"60.0, 3.206e-4,"
    assert raw.count(row5) == 1, "S3-T-02/FIXTURE row 5"
    data = {
        "F-T1": lambda: raw.replace(row5, b"60.0, 3.207e-4,"),
        "F-T2": lambda: raw.replace(b"\n", b"\r\n"),
        "F-T3": lambda: raw.replace(b"\n", b"\r"),
        "F-T4": lambda: raw[:-1],
        "F-T5": lambda: raw + b"\n",
        "F-T6": lambda: raw.replace(row5, b"60.0, 3.206e-0x,"),
        "F-T7": lambda: b"",
    }[fid]()
    assert hashlib.sha256(data).hexdigest() == FIXTURE_SHA256[fid], f"S3-T-02/FIXTURE {fid}"
    assert data != raw, f"S3-T-02/FIXTURE {fid} equals the pin"
    return data


def _nearest_binary64(text: str) -> float:
    """The nearest binary64 to a decimal string, from exact rational arithmetic (``Fraction``);
    the result is checked against both neighbours (ties to even)."""
    exact = Fraction(text)
    f = float(exact)
    err = abs(Fraction(f) - exact)
    for g in (math.nextafter(f, -math.inf), math.nextafter(f, math.inf)):
        g_err = abs(Fraction(g) - exact)
        assert err < g_err or (err == g_err and _bits(f) % 2 == 0), f"not nearest: {text}"
    return f


def _decimal_rows(raw: bytes) -> list[list[str]]:
    return [line.split(", ") for line in raw.decode("ascii").split("\n")[:-1]]


# --- S3-T-01a: the component's pinned digest literal -------------------------------------


def test_s3_t01a_component_digest_literal():
    atmosphere = importlib.import_module(COMPONENT)
    assert atmosphere.DATASET_SHA256 == PIN, "S3-T-01a/LITERAL"


# --- S3-T-01c: the package file versus the twin's source (route (b): the T0 copy) ---------


def test_s3_t01c_package_file_equals_twin_source():
    try:
        package = PACKAGE_DATA.read_bytes()
    except FileNotFoundError:
        package = None
    assert package is not None, "S3-T-01c/SAME package data file absent"
    twin_source = T0_COPY.read_bytes()
    _emit(
        "S3-DATA",
        {
            "package_file": "src/tars/sim/data/" + DATA_NAME,
            "package_file_sha256": hashlib.sha256(package).hexdigest(),
            "twin_source": "docs/science/experiments/m3-t0/data/" + DATA_NAME,
            "twin_source_sha256": hashlib.sha256(twin_source).hexdigest(),
            "pin": PIN,
            "label": LABEL,
        },
    )
    assert package == twin_source, "S3-T-01c/SAME package bytes differ from the T0 copy"


# --- S3-T-02 (a): in-process checked-load order and category -----------------------------


@pytest.mark.parametrize("fid", (*TAMPER_IDS, "pinned"))
def test_s3_t02a_checked_load_in_process(fid, tmp_path, monkeypatch):
    atmosphere = importlib.import_module(COMPONENT)
    from tests.s3_observation import observe

    raw = _pinned_bytes()
    data = raw if fid == "pinned" else _tamper(fid, raw)
    path = tmp_path / DATA_NAME
    path.write_bytes(data)
    real = atmosphere._parse_and_validate
    calls = []

    def sentinel(payload):
        calls.append(len(payload))
        return real(payload)

    monkeypatch.setattr(atmosphere, "_parse_and_validate", sentinel)
    if fid == "pinned":
        rows = atmosphere._load_checked(path)
        assert len(calls) == 1, f"S3-T-02a/ORDER control calls={len(calls)}"
        assert rows == atmosphere._TABLE, "S3-T-02a/CAT control table"
        return
    obs = observe(atmosphere._load_checked, path)
    assert obs == ("raised", "digest_mismatch"), f"S3-T-02a/CAT {fid} {obs}"
    assert len(calls) == 0, f"S3-T-02a/ORDER {fid} calls={len(calls)}"


# --- S3-T-02 (b), (c): fresh import of a temporary copy of src/tars ----------------------

PROBE = r"""
import json
import sys
from pathlib import Path

src = Path(sys.argv[1]).resolve()
mode = sys.argv[2]
sys.path.insert(0, str(src))
component = (src / "tars" / "sim" / "atmosphere.py").resolve()
calls = [0]


def profile(frame, event, arg):
    code = frame.f_code
    if event == "call" and code.co_name == "_parse_and_validate":
        if Path(code.co_filename).resolve() == component:
            calls[0] += 1


sys.setprofile(profile)
try:
    import tars.sim.atmosphere as module
except Exception as exc:
    sys.setprofile(None)
    reason = getattr(exc, "reason", None)
    rule = getattr(exc, "rule", None)
    record = {"outcome": "raised", "qualname": type(exc).__qualname__,
              "reason": reason if isinstance(reason, str) else None,
              "rule": rule if isinstance(rule, str) else None}
else:
    if mode == "direct":
        module._parse_and_validate(module._DATA_PATH.read_bytes())
    sys.setprofile(None)
    record = {"outcome": "imported", "qualname": None, "reason": None, "rule": None,
              "module_file": str(Path(module.__file__).resolve()),
              "data_path": str(Path(module._DATA_PATH).resolve())}
tars_module = sys.modules.get("tars")
record["tars_file"] = str(Path(tars_module.__file__).resolve()) if tars_module else None
record["calls"] = calls[0]
print("S3-PROBE " + json.dumps(record, sort_keys=True))
"""


def _copy_tree(tmp_path: Path) -> Path:
    src = tmp_path / "copy" / "src"
    shutil.copytree(SRC_TARS, src / "tars", ignore=shutil.ignore_patterns("__pycache__"))
    return src


def _probe(tmp_path: Path, src: Path, mode: str) -> dict:
    script = tmp_path / "s3_probe.py"
    script.write_text(PROBE, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", str(script), str(src), mode],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=tmp_path,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("S3-PROBE ")]
    if proc.returncode != 0 or len(lines) != 1:
        return {
            "outcome": "probe_failed",
            "qualname": None,
            "reason": None,
            "rule": None,
            "calls": None,
            "returncode": proc.returncode,
            "stderr": proc.stderr[-400:],
        }
    return json.loads(lines[0][len("S3-PROBE ") :])


def _under(path: str | None, root: Path) -> bool:
    return path is not None and Path(path).is_relative_to(root.resolve())


@pytest.mark.parametrize("fid", (*TAMPER_IDS, "pinned", "instrumentation"))
def test_s3_t02b_fresh_import_order(fid, tmp_path):
    raw = _pinned_bytes()
    data = raw if fid in ("pinned", "instrumentation") else _tamper(fid, raw)
    src = _copy_tree(tmp_path)
    target = src / "tars" / "sim" / "data" / DATA_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    obs = _probe(tmp_path, src, "direct" if fid == "instrumentation" else "import")
    if fid in ("pinned", "instrumentation"):
        expected_calls = 1 if fid == "pinned" else 2
        assert obs["outcome"] == "imported", f"S3-T-02b/CAT control {fid} {obs}"
        assert obs["calls"] == expected_calls, f"S3-T-02b/ORDER control {fid} {obs}"
        assert _under(obs["module_file"], src) and _under(obs["data_path"], src), (
            f"S3-T-02b/BIND {obs}"
        )
    else:
        assert (obs["outcome"], obs["reason"]) == ("raised", "digest_mismatch"), (
            f"S3-T-02b/CAT {fid} {obs}"
        )
        assert obs["calls"] == 0, f"S3-T-02b/ORDER {fid} {obs}"
    assert _under(obs["tars_file"], src), f"S3-T-02b/BIND {obs}"


def test_s3_t02c_missing_file(tmp_path):
    atmosphere = importlib.import_module(COMPONENT)
    from tests.s3_observation import observe

    obs = observe(atmosphere._load_checked, tmp_path / "absent" / DATA_NAME)
    assert obs == ("raised", "missing"), f"S3-T-02c/CAT in-process {obs}"
    src = _copy_tree(tmp_path)
    target = src / "tars" / "sim" / "data" / DATA_NAME
    target.unlink()
    rec = _probe(tmp_path, src, "import")
    assert (rec["outcome"], rec["reason"]) == ("raised", "missing"), f"S3-T-02c/CAT {rec}"
    assert rec["calls"] == 0, f"S3-T-02c/ORDER {rec}"
    assert _under(rec["tars_file"], src), f"S3-T-02c/BIND {rec}"


# --- S3-T-03: 28 rows; parsed values equal the decimal strings and the twin ---------------


def test_s3_t03_parsed_table():
    atmosphere = importlib.import_module(COMPONENT)
    twin = importlib.import_module("tests.s3_dl4_density_twin")

    table = atmosphere._TABLE
    assert isinstance(table, tuple) and len(table) == 28, "S3-T-03/COUNT"
    assert all(len(row) == 3 and all(type(v) is float for v in row) for row in table), (
        "S3-T-03/TYPE"
    )
    strings = _decimal_rows(PACKAGE_DATA.read_bytes())
    assert len(strings) == 28, "S3-T-03/COUNT strings"
    diff = [
        (i, j, strings[i][j], table[i][j].hex())
        for i in range(28)
        for j in range(3)
        if _bits(table[i][j]) != _bits(_nearest_binary64(strings[i][j]))
        or _bits(table[i][j]) != _bits(float(strings[i][j]))
    ]
    assert diff == [], f"S3-T-03/VALUE strings {diff[:5]}"
    twin_diff = [
        (i, j) for i in range(28) for j in range(3) if _bits(table[i][j]) != _bits(twin.TABLE[i][j])
    ]
    assert twin_diff == [], f"S3-T-03/VALUE twin {twin_diff[:5]}"


# --- S3-T-04: V-rules through the private parser seam ------------------------------------


def _lines(raw: bytes) -> list[str]:
    return raw.decode("ascii").split("\n")[:-1]


def _build(lines: list[str], end: str = "\n") -> bytes:
    return ("\n".join(lines) + end).encode("ascii")


def _with_line(raw: bytes, index: int, text: str) -> bytes:
    lines = _lines(raw)
    lines[index] = text
    return _build(lines)


V_FIXTURES = {
    "V-1-nbsp": ("V-1", lambda r: r.replace(b"60.0, 3.206e-4,", b"60.0\xa0, 3.206e-4,")),
    "V-2-no-final-lf": ("V-2", lambda r: r[:-1]),
    "V-2-crlf": ("V-2", lambda r: r.replace(b"\n", b"\r\n")),
    "V-2-blank-line": ("V-2", lambda r: r + b"\n"),
    "V-3-27-rows": ("V-3", lambda r: _build(_lines(r)[:27])),
    "V-3-29-rows": ("V-3", lambda r: _build([*_lines(r), "1100.0, 1.0e-15, 300.0"])),
    "V-4-2-fields": ("V-4", lambda r: _with_line(r, 5, "60.0, 3.206e-4")),
    "V-4-4-fields": ("V-4", lambda r: _with_line(r, 5, "60.0, 3.206e-4, 7.714, 1.0")),
    "V-5-token": ("V-5", lambda r: _with_line(r, 5, "60.0, 3.206e-0x, 7.714")),
    "V-6-inf-H": ("V-6", lambda r: _with_line(r, 5, "60.0, 3.206e-4, inf")),
    "V-6-1e999-rho0": ("V-6", lambda r: _with_line(r, 5, "60.0, 1e999, 7.714")),
    "V-7-base-1": ("V-7", lambda r: _with_line(r, 0, "1.0, 1.225, 7.249")),
    "V-8-equal-bases": ("V-8", lambda r: _with_line(r, 2, "25.0, 1.774e-2, 6.682")),
    "V-9a-rho0-zero": ("V-9a", lambda r: _with_line(r, 5, "60.0, 0.0, 7.714")),
    "V-9a-rho0-negative": ("V-9a", lambda r: _with_line(r, 5, "60.0, -1e-5, 7.714")),
    "V-9b-H-zero": ("V-9b", lambda r: _with_line(r, 5, "60.0, 3.206e-4, 0.0")),
    "V-9b-H-negative": ("V-9b", lambda r: _with_line(r, 5, "60.0, 3.206e-4, -7")),
}


@pytest.mark.parametrize("name", tuple(V_FIXTURES))
def test_s3_t04_validity_rule(name):
    atmosphere = importlib.import_module(COMPONENT)
    from tests.s3_observation import observe_parse

    rule, build = V_FIXTURES[name]
    fixture = build(_pinned_bytes())
    assert hashlib.sha256(fixture).hexdigest() != PIN, f"S3-T-04/FIXTURE {name}"
    obs = observe_parse(atmosphere._parse_and_validate, fixture)
    assert obs == ("raised", "invalid_content", rule), f"S3-T-04/{rule} fixture={name} {obs}"


def test_s3_t04_rule_precedence():
    atmosphere = importlib.import_module(COMPONENT)
    from tests.s3_observation import observe_parse

    fixture = _with_line(_pinned_bytes(), 5, "60.0, nan, 7.714")
    obs = observe_parse(atmosphere._parse_and_validate, fixture)
    assert obs == ("raised", "invalid_content", "V-6"), f"S3-T-04/PREC {obs}"


def test_s3_t04_pinned_bytes_accepted():
    atmosphere = importlib.import_module(COMPONENT)
    from tests.s3_observation import observe_parse

    obs = observe_parse(atmosphere._parse_and_validate, _pinned_bytes())
    assert obs == ("accepted", 28), f"S3-T-04/ACCEPT {obs}"


# --- S3-T-16: the parsed table as 84 hex tokens (per-platform, exact expectation) --------


def test_s3_t16_table_hex():
    atmosphere = importlib.import_module(COMPONENT)

    derived = tuple(
        _nearest_binary64(s).hex() for row in _decimal_rows(T0_COPY.read_bytes()) for s in row
    )
    assert derived == EXPECTED_HEX, "S3-T-16/EXPECT committed expectation != exact derivation"
    tokens = [v.hex() for row in atmosphere._TABLE for v in row]
    _emit(
        "S3-TABLE-HEX",
        {
            "tokens": tokens,
            "count": len(tokens),
            "order": "row-major base_km,rho0,H_km",
            "label": LABEL,
        },
    )
    assert tuple(tokens) == EXPECTED_HEX, "S3-T-16/TABLE"
