# ruff: noqa
import os
from pathlib import Path
from tars.validation import m2


def pytest_configure(config):
    s = Path(m2.__file__).read_text()
    mode = os.environ["DISABLE_FIX"]
    if mode == "roundtrip":
        s = s.replace(
            "if not (r_err <= KEPLER_ROUNDTRIP_REL_TOL and v_err <= KEPLER_ROUNDTRIP_REL_TOL):",
            "if False:",
        )
    elif mode == "nodes":
        s = s.replace(
            'raise RuntimeError(f"DOP853 dense output disagrees with its solver nodes on {where}")',
            "pass",
        )
    elif mode == "stencil":
        s = s.replace(
            'raise RuntimeError(f"DOP853 dense output non-finite near the ticks on {where}")',
            "pass",
        )
    elif mode == "cli":
        s = s.replace("if any(f not in summary for f in fields):", "if False:")
        s = s.replace(
            "got = tuple(summary[f] for f in fields)", "got = (None, None, None, None, [])"
        )
    exec(compile(s, m2.__file__, "exec"), m2.__dict__)
