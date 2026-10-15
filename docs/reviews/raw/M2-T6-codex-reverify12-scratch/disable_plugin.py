# ruff: noqa
import os
from pathlib import Path
from tars.validation import m2, gmat_m2


def pytest_configure(config):
    mode = os.environ["DISABLE_FIX"]
    mod = gmat_m2 if mode == "epoch" else m2
    s = Path(mod.__file__).read_text()
    if mode == "velocity":
        old = 'raise RuntimeError(f"DOP853 stencil velocity inconsistent on {where}")'
        new = "pass"
    elif mode == "propellant":
        old = "if not (m_p >= 0.0 and err <= tol):"
        new = 'if not where.startswith("stencil") and not (m_p >= 0.0 and err <= tol):'
    elif mode == "nodes":
        old = '_check_solver_nodes(sol, f"[{a}, {b}]")  # every segment (F45)'
        new = "pass  # intentionally disable F45 in memory"
    else:
        old = "v += epoch_anchor_problems(labelled, scenario)"
        new = "pass  # intentionally disable F46 in memory"
    assert old in s
    exec(compile(s.replace(old, new), mod.__file__, "exec"), mod.__dict__)
