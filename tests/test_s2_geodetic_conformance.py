"""S2 DL-4 conformance tests (M3 T2 S2; proposal v11 §3.10, §3.11 G-08 and G-12).

Commit A holds G-12a (twin independence, a guard) and the twin sanity tests, none of which
needs the component.
"""

from __future__ import annotations

import ast
import struct

from tests.conftest import REPO_ROOT

TWIN = REPO_ROOT / "tests" / "s2_dl4_geodetic_twin.py"


def _imported_modules(path) -> set[str]:
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add("." * node.level + (node.module or ""))
    return names


# --- G-12a: the twin imports no tars module, only math and typing support ---------------


def test_g12a_twin_imports_only_math_and_typing():
    modules = _imported_modules(TWIN)
    assert modules <= {"__future__", "math", "typing"}, modules
    assert not any(m == "tars" or m.startswith(("tars.", ".")) for m in modules)


# --- Twin sanity (no component) --------------------------------------------------------


def test_twin_constants_are_r1_step_1():
    from tests.s2_dl4_geodetic_twin import E2, INV_F, A, F

    assert A == 6378137.0
    assert INV_F == 298.257223563
    assert F == 1.0 / 298.257223563
    assert E2.hex() == "0x1.b6b90f1fe94f0p-8"  # §3.7.4 [F-15]: e2 = F*(2.0 - F)


def test_twin_equator_gives_plus_zero_latitude_and_h_x_minus_a():
    """Equator (x, 0, 0), x >= a: phi = +0 and h = x - a (the binary64 difference), under
    A-LM-0's exact values at zero; DQ-1 meets its stop test at update 1."""
    from tests.s2_dl4_geodetic_twin import A, twin_geodetic

    for x in (A, A + 1.0, 7.0e6, 4.2e7):
        rec = twin_geodetic(x, 0.0, 0.0)
        assert struct.pack("<d", rec.phi) == struct.pack("<d", 0.0)
        assert rec.h == x - A
        assert rec.converged is True
        assert rec.iterations == 1


def test_twin_records_the_cap_without_convergence_as_not_converged():
    """A scripted library whose atan2 never settles: 60 updates, converged False. No
    exception is caught by the twin."""
    from tests.s2_dl4_geodetic_twin import twin_geodetic

    class Lib:
        calls = 0

        def hypot(self, x, y):
            return 7.0e6

        def atan2(self, y, x):
            Lib.calls += 1
            return 0.1 + Lib.calls * 1e-10

        def sin(self, v):
            return 0.0

        def cos(self, v):
            return 1.0

        def sqrt(self, v):
            return 1.0

    rec = twin_geodetic(7.0e6, 0.0, 1.0, lib=Lib())
    assert rec.converged is False
    assert rec.iterations == 60
    assert Lib.calls == 61  # the start plus 60 updates
