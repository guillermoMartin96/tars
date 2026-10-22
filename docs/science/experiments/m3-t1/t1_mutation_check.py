"""M3 T1: show that the J2 unit tests are load-bearing (VAL-0020; test-quality evidence).

Each mutant changes one line of the production code in a temporary copy of ``src``.
The T1 tests (tests/test_zonal_j2.py, tests/test_constants.py) are then run against the
copy, which is put first on PYTHONPATH. A mutant is DETECTED when pytest fails. The
unmutated copy must pass (control).

Usage (from the repository root):
    uv run python docs/science/experiments/m3-t1/t1_mutation_check.py OUT.json
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
FORCES = "tars/sim/forces.py"
CONSTANTS = "tars/sim/constants.py"
TESTS = ["tests/test_zonal_j2.py", "tests/test_constants.py"]

# (id, file, original text, replacement, defect)
MUTANTS = [
    ("sign", FORCES, "self._k = -1.5 *", "self._k = 1.5 *", "acceleration sign reversed"),
    ("magnitude", FORCES, "self._k = -1.5 *", "self._k = -1.4 *", "coefficient 3/2 -> 1.4"),
    (
        "z_factor",
        FORCES,
        "k * (3.0 - 5.0 * s2) * z",
        "k * (2.0 - 5.0 * s2) * z",
        "z factor 3 -> 2 (non-conservative)",
    ),
    (
        "s2_coeff",
        FORCES,
        "c = 1.0 - 5.0 * s2",
        "c = 1.0 - 4.0 * s2",
        "latitude coefficient 5 -> 4 in x, y",
    ),
    (
        "xy_asym",
        FORCES,
        "k * c * y,",
        "k * c * y * (1.0 + 1e-9),",
        "x/y asymmetry 1e-9 (not axisymmetric)",
    ),
    (
        "z_scale_1e9",
        FORCES,
        "k * (3.0 - 5.0 * s2) * z]",
        "k * (3.0 - 5.0 * s2) * z * (1.0 + 1e-9)]",
        "z component scaled by 1e-9",
    ),
    (
        "power",
        FORCES,
        "(r2 * r2 * r_norm)",
        "(r2 * r2 * r_norm * 1.000001)",
        "radial dependence perturbed",
    ),
    (
        "axis",
        FORCES,
        "x, y, z = float(r[0]), float(r[1]), float(r[2])",
        "x, z, y = float(r[0]), float(r[1]), float(r[2])",
        "symmetry axis +Y instead of +Z",
    ),
    (
        "j2_zero_offset",
        FORCES,
        "return np.array([k * c * x,",
        "return np.array([k * c * x + 1e-300,",
        "J2 = 0 not exactly zero",
    ),
    (
        "sqrt5_decimal",
        CONSTANTS,
        "return -math.sqrt(5.0) * c20",
        "return -2.2360679775 * c20",
        "sqrt(5) replaced by a decimal",
    ),
    (
        "sqrt5_ulp",
        CONSTANTS,
        "return -math.sqrt(5.0) * c20",
        "return -(math.sqrt(5.0) * (1.0 + 2.0**-52)) * c20",
        "sqrt(5) one ulp high",
    ),
    (
        "j2_sign",
        CONSTANTS,
        "return -math.sqrt(5.0) * c20",
        "return math.sqrt(5.0) * c20",
        "J2 sign reversed",
    ),
    (
        "c20_digit",
        CONSTANTS,
        "EGM2008_C20_TIDE_FREE = -0.484165143790815e-3",
        "EGM2008_C20_TIDE_FREE = -0.484165143790816e-3",
        "C20 last digit changed",
    ),
    (
        "decimal_j2",
        CONSTANTS,
        "return -math.sqrt(5.0) * c20",
        "return 1.0826261739e-3 + 0.0 * c20",
        "decimal J2 used as the canonical value",
    ),
]


def run(src: Path) -> int:
    env = dict(os.environ, PYTHONPATH=str(src))
    cmd = [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *TESTS]
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True).returncode


def main(out_path: str) -> None:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        shutil.copytree(ROOT / "src", src)
        control = run(src)
        for mid, rel, old, new, defect in MUTANTS:
            path = src / rel
            original = path.read_text()
            if original.count(old) != 1:
                raise SystemExit(f"{mid}: anchor occurs {original.count(old)} times")
            path.write_text(original.replace(old, new))
            code = run(src)
            path.write_text(original)
            results.append(
                {
                    "id": mid,
                    "file": rel,
                    "defect": defect,
                    "pytest_exit": code,
                    "detected": code != 0,
                }
            )
    summary = {
        "control_pytest_exit": control,
        "control_passes": control == 0,
        "mutants": results,
        "detected": sum(r["detected"] for r in results),
        "total": len(results),
    }
    Path(out_path).write_text(json.dumps(summary, indent=2) + "\n")
    print(f"control exit {control}; detected {summary['detected']}/{summary['total']}")
    if control != 0 or summary["detected"] != summary["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1])
