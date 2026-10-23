"""M3 T1: show that the J2 unit tests are load-bearing (VAL-0020; test-quality evidence).

Each mutant changes one line of the production code in a temporary copy of ``src``.
The T1 tests (tests/test_zonal_j2.py, tests/test_constants.py) are then run against the
copy, which is put first on PYTHONPATH. A mutant is DETECTED when pytest fails. The
unmutated copy must pass (control). For each mutant the failing tests and pytest's
failure type and message (from pytest's JUnit XML) are recorded; ``by_assertion`` is true
when at least one failure is an assertion (``AssertionError``, including a ``pytest.raises``
match failure) or a missing expected exception (``DID NOT RAISE``), rather than an
unexpected error.

Mutants added after Codex Review 01 (I-19): the reviewer's eight mutants (four of which
survived the Review 01 tests) and mutants that remove each M3T1-R1-F1/F2 protection.
Mutants added after Codex Review 02 (I-20): removal of each M3T1-R2-F1/F2 protection. The
anchors of four original mutants follow the R2-F1 rewrite of the component expression
(``k * c * x`` -> ``kc * x``, same defects).
Mutant added after Codex Review 03 (I-21): the reviewer's ``upper_subnormal_ignored``
(M3T1-R3-O1), which survived the Review 03 tests. I-21 writes its results to a new file and
keeps the 46-mutant results of I-20 (``t1_mutation_check_results.json``) unchanged.

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
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path.cwd()
FORCES = "tars/sim/forces.py"
CONSTANTS = "tars/sim/constants.py"
TESTS = ["tests/test_zonal_j2.py", "tests/test_constants.py"]

# (id, file, original text, replacement, defect)
MUTANTS = [
    ("sign", FORCES, "k0 = -1.5 *", "k0 = 1.5 *", "acceleration sign reversed"),
    ("magnitude", FORCES, "k0 = -1.5 *", "k0 = -1.4 *", "coefficient 3/2 -> 1.4"),
    (
        "z_factor",
        FORCES,
        "d = 3.0 - 5.0 * s2",
        "d = 2.0 - 5.0 * s2",
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
        "kc * y,",
        "kc * y * (1.0 + 1e-9),",
        "x/y asymmetry 1e-9 (not axisymmetric)",
    ),
    (
        "z_scale_1e9",
        FORCES,
        "kd * z]",
        "kd * z * (1.0 + 1e-9)]",
        "z component scaled by 1e-9",
    ),
    (
        "power",
        FORCES,
        "r5 = r2 * r2 * r_norm",
        "r5 = r2 * r2 * r_norm * 1.000001",
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
        "a = np.array([kc * x,",
        "a = np.array([kc * x + 1e-300,",
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
    # ---- Codex Review 01 reviewer mutants (I-19 §6)
    (
        "r1_negative_j2_abs",
        FORCES,
        "k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius",
        "k0 = -1.5 * abs(self.j2) * self.mu * self.equatorial_radius * self.equatorial_radius",
        "sign of J2 ignored (survived Review 01)",
    ),
    (
        "r1_small_coefficient_error",
        FORCES,
        "k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius",
        "k0 = -1.5 * (1 + 2**-51) * self.j2 * self.mu * self.equatorial_radius"
        " * self.equatorial_radius",
        "coefficient 4 ulp high (survived Review 01)",
    ),
    (
        "r1_far_field_zero",
        FORCES,
        "r_norm = math.sqrt(r2)\n",
        "r_norm = math.sqrt(r2)\n        if r_norm > 7 * self.equatorial_radius:\n"
        "            return np.zeros(3)\n",
        "zero beyond 7 R (survived Review 01)",
    ),
    (
        "r1_high_lat_band",
        FORCES,
        "c = 1.0 - 5.0 * s2\n",
        "c = 1.0 - 5.0 * s2\n        if 0.99 < s2 < 0.9999:\n            c *= 1.01\n",
        "1 % x/y error for 0.99 < sin^2 lat < 0.9999 (survived Review 01)",
    ),
    (
        "r1_off_axis_band",
        FORCES,
        "c = 1.0 - 5.0 * s2\n",
        "c = 1.0 - 5.0 * s2\n        if 0.36 < s2 < 0.37:\n            c *= 1.01\n",
        "1 % x/y error for 0.36 < sin^2 lat < 0.37",
    ),
    (
        "r1_unnormalized",
        FORCES,
        "k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius",
        "k0 = -1.5 * (self.j2 / math.sqrt(5)) * self.mu * self.equatorial_radius"
        " * self.equatorial_radius",
        "unnormalized C20 scaling used as J2",
    ),
    (
        "r1_mu_radius_swap",
        FORCES,
        "k0 = -1.5 * self.j2 * self.mu * self.equatorial_radius * self.equatorial_radius",
        "k0 = -1.5 * self.j2 * self.equatorial_radius * self.mu * self.mu",
        "mu and R swapped in the coefficient",
    ),
    (
        "r1_p2_wrong",
        FORCES,
        "c = 1.0 - 5.0 * s2",
        "c = 1.0 - 3.0 * s2",
        "x/y latitude coefficient 5 -> 3",
    ),
    # ---- removal of each M3T1-R1-F1 / F2 protection (I-19 §3-§4)
    (
        "f1_setattr_allowed",
        FORCES,
        'raise AttributeError(f"ZonalJ2Gravity is immutable: cannot set {name!r}")',
        "object.__setattr__(self, name, value)",
        "attributes can be reassigned",
    ),
    (
        "f1_delattr_allowed",
        FORCES,
        'raise AttributeError(f"ZonalJ2Gravity is immutable: cannot delete {name!r}")',
        "object.__delattr__(self, name)",
        "attributes can be deleted",
    ),
    (
        "f1_instance_dict",
        FORCES,
        '__slots__ = ("equatorial_radius", "j2", "mu")',
        '__slots__ = ("equatorial_radius", "j2", "mu", "__dict__")',
        "instance __dict__ available",
    ),
    (
        "f2_infinite_parameters_accepted",
        FORCES,
        "math.isfinite(mu)\n            and mu > 0.0\n"
        "            and math.isfinite(equatorial_radius)\n            and equatorial_radius > 0.0",
        "mu > 0.0\n            and equatorial_radius > 0.0",
        "infinite mu or R accepted",
    ),
    (
        "f2_coefficient_range_unchecked",
        FORCES,
        "if not math.isfinite(k) or (j2 != 0.0 and abs(k) < _MIN_NORMAL):",
        "if False:",
        "overflowing or subnormal -(3/2) J2 mu R^2 accepted",
    ),
    (
        "f2_position_unchecked",
        FORCES,
        "if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):",
        "if False:",
        "non-finite position not rejected",
    ),
    (
        "f2_underflow_reported_as_origin",
        FORCES,
        "if x == 0.0 and y == 0.0 and z == 0.0:",
        "if True:",
        "|r|^2 underflow classified as the origin",
    ),
    (
        "f2_r5_unchecked",
        FORCES,
        "if not _MIN_NORMAL <= r5 < math.inf:",
        "if False:",
        "r^5 overflow/underflow not reported (silent zero)",
    ),
    (
        "f2_scaled_coefficient_unchecked",
        FORCES,
        "if k0 != 0.0 and not _MIN_NORMAL <= abs(k) < math.inf:",
        "if False:",
        "overflowing or subnormal scaled coefficient not reported",
    ),
    (
        "f2_result_unchecked",
        FORCES,
        "if not np.all(np.isfinite(a)):",
        "if False:",
        "overflowing result returned",
    ),
    # ---- removal of each M3T1-R2-F1 / F2 protection (I-20 §2)
    (
        "r2f1_component_products_unchecked",
        FORCES,
        "if _underflows(kc, k, c) or _underflows(kd, k, d):",
        "if False:",
        "component-product underflow returned silently",
    ),
    (
        "r2f1_xy_factor_unchecked",
        FORCES,
        "if _underflows(kc, k, c) or _underflows(kd, k, d):",
        "if _underflows(kd, k, d):",
        "k (1 - 5 s^2) underflow returned silently",
    ),
    (
        "r2f1_z_factor_unchecked",
        FORCES,
        "if _underflows(kc, k, c) or _underflows(kd, k, d):",
        "if _underflows(kc, k, c):",
        "k (3 - 5 s^2) underflow returned silently",
    ),
    (
        "r2f1_coefficient_p1_unchecked",
        FORCES,
        "_underflows(p1, -1.5, j2)\n            or ",
        "",
        "-(3/2) J2 underflow accepted",
    ),
    (
        "r2f1_coefficient_p2_unchecked",
        FORCES,
        "or _underflows(p2, p1, mu)\n            ",
        "",
        "-(3/2) J2 mu underflow accepted",
    ),
    (
        "r2f1_coefficient_p3_unchecked",
        FORCES,
        "\n            or _underflows(p3, p2, equatorial_radius)",
        "",
        "-(3/2) J2 mu R underflow accepted",
    ),
    (
        "r2f1_exactness_ignored",
        FORCES,
        "return abs(product) < _MIN_NORMAL and Fraction(a) * Fraction(b) != product",
        "return abs(product) < _MIN_NORMAL",
        "exact zeros and exact subnormal products rejected as underflow",
    ),
    (
        "r3_upper_subnormal_band_ignored",
        FORCES,
        "return abs(product) < _MIN_NORMAL and",
        "return abs(product) < _MIN_NORMAL / 2 and",
        "inexact products in [MIN_NORMAL/2, MIN_NORMAL) not treated as underflow",
    ),
    (
        "r2f2_parameters_not_converted",
        FORCES,
        'mu = _owned_float("mu", mu)',
        '_owned_float("mu", mu)',
        "mu stored as the caller's object",
    ),
    (
        "r2f2_type_unchecked",
        FORCES,
        "if isinstance(scalar, bool) or not isinstance("
        "scalar, int | float | np.integer | np.floating):",
        "if False:",
        "any float()-convertible input accepted",
    ),
    (
        "r2f2_bool_accepted",
        FORCES,
        "if isinstance(scalar, bool) or not isinstance(",
        "if not isinstance(",
        "bool accepted as a number",
    ),
    (
        "r2f2_zero_d_array_rejected",
        FORCES,
        "value[()] if isinstance(value, np.ndarray) and value.ndim == 0 else value",
        "value",
        "zero-dimensional arrays rejected",
    ),
    (
        "r2f2_numpy_integer_rejected",
        FORCES,
        "int | float | np.integer | np.floating",
        "int | float | np.floating",
        "NumPy integer scalars rejected",
    ),
    (
        "r2f2_numpy_floating_rejected",
        FORCES,
        "int | float | np.integer | np.floating",
        "int | float | np.integer",
        "NumPy floating scalars (not float64) rejected",
    ),
    (
        "r2f2_overflow_not_converted",
        FORCES,
        "except OverflowError:",
        "except ZeroDivisionError:",
        "huge int raises OverflowError instead of ValueError",
    ),
]


def run(src: Path, junit: Path) -> tuple[int, list[dict]]:
    junit.unlink(missing_ok=True)
    env = dict(os.environ, PYTHONPATH=str(src))
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"]
    proc = subprocess.run([*cmd, *TESTS], cwd=ROOT, env=env, capture_output=True, text=True)
    failures = []
    if junit.exists():
        for case in ET.parse(junit).iter("testcase"):
            for kind in ("failure", "error"):
                for node in case.iter(kind):
                    failures.append(
                        {
                            "kind": kind,
                            "test": f"{case.get('classname')}::{case.get('name')}",
                            "type": node.get("type") or "",
                            "message": (node.get("message") or "")[:200],
                        }
                    )
    return proc.returncode, failures


def is_assertion(failure: dict) -> bool:
    """An assertion (incl. a pytest.raises match failure) or a missing expected exception."""
    return failure["kind"] == "failure" and (
        failure["type"] in ("AssertionError", "Failed")
        or failure["message"].startswith(("assert ", "AssertionError", "Failed: DID NOT RAISE"))
    )


def main(out_path: str) -> None:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        shutil.copytree(ROOT / "src", src)
        junit = Path(tmp) / "junit.xml"
        control, _ = run(src, junit)
        for mid, rel, old, new, defect in MUTANTS:
            path = src / rel
            original = path.read_text()
            if original.count(old) != 1:
                raise SystemExit(f"{mid}: anchor occurs {original.count(old)} times")
            path.write_text(original.replace(old, new))
            code, failures = run(src, junit)
            path.write_text(original)
            results.append(
                {
                    "id": mid,
                    "file": rel,
                    "defect": defect,
                    "pytest_exit": code,
                    "detected": code != 0,
                    "by_assertion": any(is_assertion(f) for f in failures),
                    "failures": failures,
                }
            )
    summary = {
        "control_pytest_exit": control,
        "control_passes": control == 0,
        "mutants": results,
        "detected": sum(r["detected"] for r in results),
        "detected_by_assertion": sum(r["by_assertion"] for r in results),
        "total": len(results),
        "surviving": [r["id"] for r in results if not r["detected"]],
    }
    Path(out_path).write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"control exit {control}; detected {summary['detected']}/{summary['total']}"
        f" ({summary['detected_by_assertion']} by assertion); surviving {summary['surviving']}"
    )
    if control != 0 or summary["detected_by_assertion"] != summary["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1])
