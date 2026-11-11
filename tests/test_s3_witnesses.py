"""S3-T-22: the frozen-witness node (M3 T2 S3; proposal v4 sections 10.3, 11.3 (a); D-S3-17 (a);
PC-7(S3)).

The witness inputs below were discovered in phase P by twin-model discovery (mutated copies of the
commit-A twin, outside every checkout). They are DISCOVERY, NOT KILL EVIDENCE. They are transferred
here under X-1 from ``WITNESSES.json`` (sha256
``678cb821355772579b6f43b87e552c0ca5185c9aa21336780b4f65a890f0ab53``; ``DISCOVERY-MANIFEST.json``
sha256 ``dc62354a366e78639d85960ef5bf2ae01536e369c78085d5dceaf6d59b01e274``), kept in the external
S3 implementation evidence packet. Kills are established only by the phase-D campaign on the
committed BC; an ordinary run of this node is output conformance only (v4 section 13.3).

At every witness input the component's observation equals the twin's, unmutated, on the host and
in each CI job. The component is imported inside the test body (declared red reason
``MOD(tars.sim.atmosphere)``). Densities are UNVERIFIED ABOVE 1000 KM (P5).
"""

import importlib
from pathlib import Path

WITNESSES_SHA256 = "678cb821355772579b6f43b87e552c0ca5185c9aa21336780b4f65a890f0ab53"
# (candidate mutant, listing position, binary64 hex token)
WITNESSES = (
    ("M-07", "P-A:2", "0x1.86a0000000000p+14"),
    ("M-08b", "P-A:0", "0x0.0p+0"),
    ("M-09", "P-A:1", "0x1.869ffffffffffp+14"),
    ("M-10", "P-A:34", "0x1.fbcffffffffffp+16"),
    ("M-11", "P-A:9", "0x1.3880000000001p+15"),
    ("M-12", "P-A:3", "0x1.86a0000000001p+14"),
    ("M-14", "P-A:1", "0x1.869ffffffffffp+14"),
    ("M-17", "P-A:80", "0x1.e848000000000p+19"),
)


def test_s3_t22_frozen_witness_inputs():
    atmosphere = importlib.import_module("tars.sim.atmosphere")
    twin = importlib.import_module("tests.s3_dl4_density_twin")
    gen = importlib.import_module("tests.s3_dl4_point_sets")
    from tests.s3_observation import observe, parse_token

    listing = (Path(__file__).resolve().parents[1] / "tests/s3_dl4_points.txt").read_text(
        encoding="ascii"
    )
    token_at = {f"{s}:{i}": t for s, i, t in gen.parse_listing(listing)}
    off = [(m, label, tok) for m, label, tok in WITNESSES if token_at.get(label) != tok]
    assert off == [], f"S3-T-22/LISTING {off}"
    diff = []
    for mutant, label, tok in WITNESSES:
        x = parse_token(tok)
        got, want = observe(atmosphere.density, x), observe(twin.density, x)
        if got != want:
            diff.append((mutant, label, tok, got, want))
    assert diff == [], f"S3-T-22/OBS {diff}"
