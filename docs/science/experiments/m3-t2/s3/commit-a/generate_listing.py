"""Commit-A listing generation for M3 T2 S3 (proposal v4 section 8.4, section 15.1 phase A).

Runs the committed generator ``tests/s3_dl4_point_sets.py`` on the rows from the twin's own
parser, writes the frozen listing ``tests/s3_dl4_points.txt`` and this directory's
``listing-generation-record.json`` (listing identity, generator and twin identities, per-set
counts, removed duplicates, and the r2 section 7.1 environment record of THIS process, built by
the existing S2 ENV node per owner decision D-S3-04 (a)). Run from the repository root with
``uv run python docs/science/experiments/m3-t2/s3/commit-a/generate_listing.py``.

The listing is exp-free (no libm transcendental), so it does not depend on the platform's libm;
S3-T-18 asserts byte-identical regeneration on every platform. Densities are UNVERIFIED ABOVE
1000 KM; this record contains no density value.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))

from tests import s3_dl4_point_sets as gen  # noqa: E402
from tests.test_s2_environment_record import build_record  # noqa: E402

LISTING = ROOT / "tests/s3_dl4_points.txt"
RECORD = Path(__file__).resolve().parent / "listing-generation-record.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def main() -> None:
    started = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    status_before = _git("status", "--porcelain=v1", "--untracked-files=all")
    result = gen.generate(gen.twin_rows())
    text = gen.render_listing(result)
    LISTING.write_bytes(text.encode("ascii"))
    header = gen.parse_header(text)
    record = {
        "record": "S3 commit-A listing generation record (proposal v4 section 8.4)",
        "proposal_v4_sha256": "0b90e9cfb1c2e6d9348c566ac9a6b313a6c1164bdadd3e4bf34e5c86270154e6",
        "generated_utc": started,
        "base_commit": _git("rev-parse", "HEAD"),
        "worktree_state_before_generation": status_before.splitlines(),
        "component_src_tars_sim_atmosphere_py_exists": (
            ROOT / "src/tars/sim/atmosphere.py"
        ).exists(),
        "generator": {
            "path": "tests/s3_dl4_point_sets.py",
            "sha256": _sha256(ROOT / "tests/s3_dl4_point_sets.py"),
            "git_blob": _git("hash-object", "tests/s3_dl4_point_sets.py"),
        },
        "twin": {
            "path": "tests/s3_dl4_density_twin.py",
            "sha256": _sha256(ROOT / "tests/s3_dl4_density_twin.py"),
            "git_blob": _git("hash-object", "tests/s3_dl4_density_twin.py"),
            "data_source": "docs/science/experiments/m3-t0/data/EarthExponentialAtmosphereData.txt",
            "data_source_sha256": _sha256(
                ROOT / "docs/science/experiments/m3-t0/data/EarthExponentialAtmosphereData.txt"
            ),
        },
        "listing_path": "tests/s3_dl4_points.txt",
        "listing_sha256": _sha256(LISTING),
        "listing_bytes": LISTING.stat().st_size,
        "listing_git_blob": _git("hash-object", "tests/s3_dl4_points.txt"),
        "seed": f"0x{gen.SEED:08X}",
        "counts_before_dedup": result["counts"],
        "removed_duplicates": [list(d) for d in result["removed"]],
        "known_duplicates_present": sorted(list(d) for d in gen.KNOWN_DUPLICATES),
        "random_collisions": [
            list(d) for d in result["removed"] if tuple(d) not in gen.KNOWN_DUPLICATES
        ],
        "final_count": header["final_count"],
        "body_sha256": header["body_sha256"],
        "environment_fields": {
            "sys.version": sys.version,
            "platform.platform()": platform.platform(),
            "platform.machine()": platform.machine(),
            "uv.lock sha256": _sha256(ROOT / "uv.lock"),
            "interpreter executable sha256": _sha256(Path(os.path.realpath(sys.executable))),
        },
        "environment_record_r2_7_1": build_record(),
        "label": "densities are UNVERIFIED ABOVE 1000 KM (P5); this record holds no density",
        "limitation": (
            "integrity and generation identity only; not a numerical equality gate on densities"
        ),
    }
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=False) + "\n")
    print(json.dumps({k: record[k] for k in ("listing_sha256", "final_count", "listing_bytes")}))


if __name__ == "__main__":
    main()
