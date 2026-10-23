"""M3 T1: status of Codex Review 02's three exploratory surviving mutants (I-20 §3).

Each mutant is re-applied, with the reviewer's text, to a temporary copy of the corrected
``src`` and the T1 tests are run against the copy. This is status evidence for the record,
not part of the committed mutation campaign (``t1_mutation_check.py``), and not a search
for further survivors.

Usage (from the repository root):
    uv run python docs/science/experiments/m3-t1/t1_review02_survivors.py OUT.json
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
TESTS = ["tests/test_zonal_j2.py", "tests/test_constants.py"]
C = "        c = 1.0 - 5.0 * s2\n"

# id: (anchor, replacement, the reviewer's description)
MUTANTS = {
    "canonical_one_ulp": (
        "        k = k0 / r5\n",
        "        k = (k0 * (1.0 + 2.0**-52) if self.mu > 1e10 else k0) / r5\n",
        "one-ulp coefficient perturbation confined to mu > 1e10",
    ),
    "narrow_band": (
        C,
        C + "        if 0.123456 < s2 < 0.123457:\n            c *= 1.00000001\n",
        "1e-8 x/y factor error confined to 0.123456 < s^2 < 0.123457",
    ),
    "near_min_normal_zero": (
        C,
        C + "        if 0.0 < abs(k) < 2 * _MIN_NORMAL:\n            return np.zeros(3)\n",
        "all zeros whenever 0 < |k| < 2 MIN_NORMAL",
    ),
}


def main(out_path: str) -> None:
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        for mid, (old, new, defect) in MUTANTS.items():
            src = Path(tmp) / mid
            shutil.copytree(ROOT / "src", src)
            forces = src / "tars/sim/forces.py"
            text = forces.read_text()
            if text.count(old) != 1:
                raise SystemExit(f"{mid}: anchor occurs {text.count(old)} times")
            forces.write_text(text.replace(old, new))
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *TESTS],
                cwd=ROOT,
                env=dict(os.environ, PYTHONPATH=str(src)),
                capture_output=True,
                text=True,
            )
            lines = proc.stdout.strip().splitlines()
            results[mid] = {
                "defect": defect,
                "pytest_exit": proc.returncode,
                "survives": proc.returncode == 0,
                "failed_tests": [ln.split(" ")[1] for ln in lines if ln.startswith("FAILED")],
            }
    Path(out_path).write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(
        ", ".join(f"{k}: {'survives' if v['survives'] else 'killed'}" for k, v in results.items())
    )


if __name__ == "__main__":
    main(sys.argv[1])
