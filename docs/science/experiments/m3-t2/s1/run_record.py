"""M3 T2 S1: the S1 run record (PC-7(S1) §9; not DL-5).

Identifies one gate-evidence run: the commit, the interpreter and platform strings and the
uv.lock digest. It makes no reproducibility claim. A field that cannot be observed is
written "not recorded".

Usage (from the repository root):
    uv run python docs/science/experiments/m3-t2/s1/run_record.py LABEL [OUT.json]
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


def _observe(fn) -> str:
    try:
        return str(fn())
    except Exception:
        return "not recorded"


def record(label: str) -> dict[str, str]:
    def head() -> str:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()

    return {
        "label": label,
        "commit": _observe(head),
        "sys.version": _observe(lambda: sys.version),
        "platform.platform()": _observe(platform.platform),
        "platform.machine()": _observe(platform.machine),
        "uv.lock sha256": _observe(
            lambda: hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest()
        ),
    }


def main() -> None:
    text = json.dumps(record(sys.argv[1]), indent=2) + "\n"
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
