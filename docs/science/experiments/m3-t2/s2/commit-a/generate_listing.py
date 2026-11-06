"""S2 commit A: the generation run of the frozen DL-4 listing (proposal v11 §3.10).

Run once, on the host, before any component exists:

    uv run python docs/science/experiments/m3-t2/s2/commit-a/generate_listing.py

It runs the committed generator ``tests/s2_dl4_point_sets.py`` (whose exact self-checks
raise on failure, OT-6/OT-7), asserts the DG-CUSP witness-slot comparison (OT-8: a failure
is stop 15 and the file is not written), writes ``tests/s2_dl4_points.txt`` and records its
sha256 and the generation environment in ``listing-generation-record.json`` beside this
script. It refuses to run if the component ``src/tars/sim/geodesy.py`` exists, or if either
output already exists (the frozen file is never regenerated in place, RG-POL-1).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))

from tests import s2_dl4_point_sets as gen  # noqa: E402
from tests.test_s2_dl4_points import environment_fields  # noqa: E402

LISTING = ROOT / "tests" / "s2_dl4_points.txt"
RECORD = HERE / "listing-generation-record.json"
V11_SHA256 = "f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def main() -> None:
    if (ROOT / "src/tars/sim/geodesy.py").exists():
        sys.exit("refused: the component exists; the listing must precede it")
    if LISTING.exists() or RECORD.exists():
        sys.exit("refused: the frozen listing or its record already exists (RG-POL-1)")
    started = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    generation = gen.generate()
    failed = [s for s in generation.slot_checks if not s.equal]
    if failed:
        sys.exit(f"stop 15 (OT-8): witness slots differ: {failed}")
    text = gen.format_listing(generation.entries)
    LISTING.write_bytes(text.encode())
    entries = generation.entries
    record = {
        "record": "S2 commit-A listing generation record (proposal v11 section 3.10, RG-POL-5)",
        "proposal_v11_sha256": V11_SHA256,
        "generated_utc": started,
        "base_commit": git("rev-parse", "HEAD"),
        "worktree_state_at_generation": git("status", "--porcelain"),
        "component_src_tars_sim_geodesy_py_exists": False,
        "generator": {
            "path": "tests/s2_dl4_point_sets.py",
            "sha256": hashlib.sha256(
                (ROOT / "tests/s2_dl4_point_sets.py").read_bytes()
            ).hexdigest(),
            "git_blob": git("hash-object", "tests/s2_dl4_point_sets.py"),
        },
        "listing_path": "tests/s2_dl4_points.txt",
        "listing_sha256": hashlib.sha256(LISTING.read_bytes()).hexdigest(),
        "listing_bytes": LISTING.stat().st_size,
        "listing_git_blob": git("hash-object", "tests/s2_dl4_points.txt"),
        "entries": len(entries),
        "per_set_counts": {name: gen.SET_COUNTS[name] for name in gen.SET_ORDER},
        "labels": dict(Counter(e.label for e in entries)),
        "labels_by_set": {
            name: dict(Counter(e.label for e in entries if e.set == name)) for name in gen.SET_ORDER
        },
        "class_x_entries": sum(gen.is_class_x(e.set, e.index) for e in entries),
        "witness_slots_asserted": [
            {"index": s.index, "witness_hex": [v.hex() for v in s.expected], "equal": s.equal}
            for s in generation.slot_checks
        ],
        "environment": environment_fields(),
        "environment_info": {
            "sys.executable": sys.executable,
            "interpreter realpath": os.path.realpath(sys.executable),
            "note": (
                "RG-POL-5: 'the generation environment' is a run whose 'environment' fields "
                "equal these. Equal recorded fields do not prove that the library and build "
                "are identical (I-83, r83:83)."
            ),
        },
    }
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=False) + "\n")
    print(json.dumps({k: record[k] for k in ("listing_sha256", "entries", "labels")}))


if __name__ == "__main__":
    main()
