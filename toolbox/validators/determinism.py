"""Cross-process determinism check (DR-0006).

Runs the mission in N fresh Python processes and requires byte-identical
events.jsonl files. Fresh processes catch hidden state that an in-process repeat
would miss (for example, hash randomization or module-level caches).

Usage:
    uv run python toolbox/validators/determinism.py [--scenario PATH] [--runs 2]

Exit code 0 if all hashes match, 1 otherwise. Prints a JSON result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_MISSION = REPO_ROOT / "toolbox" / "scripts" / "run_mission.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--scenario", type=Path, default=REPO_ROOT / "scenarios" / "m1_leo_250km.json"
    )
    parser.add_argument("--runs", type=int, default=2)
    args = parser.parse_args(argv)

    hashes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(args.runs):
            out = Path(tmp) / f"run{i}"
            subprocess.run(
                [
                    sys.executable,
                    str(RUN_MISSION),
                    "--scenario",
                    str(args.scenario),
                    "--out",
                    str(out),
                ],
                check=True,
                capture_output=True,
            )
            hashes.append(hashlib.sha256((out / "events.jsonl").read_bytes()).hexdigest())

    passed = len(set(hashes)) == 1
    print(
        json.dumps({"validator": "determinism_cross_process", "passed": passed, "sha256": hashes})
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
