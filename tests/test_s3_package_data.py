"""S3-T-01b: the package data file's identity (M3 T2 S3, proposal v4 section 10.3; PC-7(S3)).

Subject: ``src/tars/sim/data/EarthExponentialAtmosphereData.txt`` (route D-S3-14 (b): absent until
BC). The file is opened inside the test body; its absence is the tagged assertion failure
``S3-T-01b/PRESENT`` (declared red reason FILE, v4 section 15.2), never an escaping
``FileNotFoundError``. The pin is the DR-0027 B-1 digest, written here in full.

Path binding PB-1: the path is resolved from ``ROOT``; no cwd, environment variable or absolute
path.
Densities are UNVERIFIED ABOVE 1000 KM (P5); this node checks bytes only.
"""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DATA = ROOT / "src/tars/sim/data/EarthExponentialAtmosphereData.txt"
PIN = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
SIZE = 661


def test_s3_t01b_package_data_identity():
    try:
        raw = PACKAGE_DATA.read_bytes()
    except FileNotFoundError:
        raw = None
    assert raw is not None, "S3-T-01b/PRESENT package data file absent"
    assert hashlib.sha256(raw).hexdigest() == PIN, "S3-T-01b/DIGEST"
    assert len(raw) == SIZE, f"S3-T-01b/SIZE {len(raw)}"
