"""S3-T-12: DL-4 output conformance of the density component with the twin (M3 T2 S3; proposal v4
sections 8, 10.3, 13.2; D-S3-01 (a); PC-7(S3)).

At every point of the frozen listing ``tests/s3_dl4_points.txt``, the component's observation
equals the twin's (all 64 bits, or the same error category), on the host and in each CI job. This
is same-platform output conformance (r2 D-8), not accuracy; a faulty shared ``math.exp`` passes it
(DL-4's F5 limitation). No mutant result is inferred from an ordinary run (v4 section 13.3).

Records emitted into the pytest warnings summary (D-S3-07 (a)), each with the sha256 of its body:
``S3-POINTS`` (listing sha256 and count), ``S3-DL4`` (points compared and the differences, asserted
empty in this job) and ``S3-XP3`` (the component's observation per point; REPORT-ONLY, RQ-3).

The component is imported inside the test body (declared red reason ``MOD(tars.sim.atmosphere)``).
Path binding PB-1: paths are resolved from ``ROOT``. Densities are UNVERIFIED ABOVE 1000 KM (P5).
"""

import hashlib
import importlib
import json
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / "tests/s3_dl4_points.txt"
LABEL = "densities are UNVERIFIED ABOVE 1000 KM (P5)"


class S3Record(UserWarning):
    """A per-run S3 record emitted into the pytest warnings summary (D-S3-07 (a))."""


def _emit(prefix: str, payload: dict) -> None:
    body = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(body.encode()).hexdigest()
    warnings.warn(f"{prefix} sha256={digest} {body}", S3Record, stacklevel=1)


def test_s3_t12_dl4_conformance_every_listing_point():
    atmosphere = importlib.import_module("tars.sim.atmosphere")
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    gen = importlib.import_module("tests.s3_dl4_point_sets")
    from tests.s3_observation import observe, parse_token

    raw = LISTING.read_bytes()
    kept = gen.parse_listing(raw.decode("ascii"))
    _emit(
        "S3-POINTS",
        {
            "listing": "tests/s3_dl4_points.txt",
            "listing_sha256": hashlib.sha256(raw).hexdigest(),
            "count": len(kept),
            "label": LABEL,
        },
    )
    xp3 = []
    differences = []
    for s, i, tok in kept:
        x = parse_token(tok)
        got, want = observe(atmosphere.density, x), observe(twin.density, x)
        xp3.append([s, i, tok, *got])
        if got != want:
            differences.append([s, i, tok, list(got), list(want)])
    _emit(
        "S3-DL4",
        {
            "check": "S3-T-12 DL-4 bitwise output conformance (same run, same platform)",
            "points_compared": len(kept),
            "differences": differences,
            "limitation": "output conformance, not accuracy; shared math.exp (F5)",
            "label": LABEL,
        },
    )
    _emit(
        "S3-XP3",
        {
            "report_only": "RQ-3: cross-platform differences are reported, never gated",
            "columns": ["set", "index", "token", "kind", "observation"],
            "rows": xp3,
            "label": LABEL,
        },
    )
    assert differences == [], f"S3-T-12/OBS {len(differences)} {differences[:5]}"
