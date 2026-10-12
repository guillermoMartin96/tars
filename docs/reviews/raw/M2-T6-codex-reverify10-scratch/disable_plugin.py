# ruff: noqa
import os
from pathlib import Path
from tars.validation import m2, gmat_m2


def pytest_configure(config):
    mode = os.environ["DISABLE_FIX"]
    if mode == "F34":
        s = Path(m2.__file__).read_text()
        s = s.replace("if not np.all(np.isfinite(times)):", "if False:")
        s = s.replace(
            "np.all(np.isfinite(st)) and np.all(np.diff(st) > 0.0) and st[0] == a and st[-1] == b",
            "True",
        )
        s = s.replace("if not (m_p >= 0.0 and err <= tol):", "if m_p < 0.0 or err > tol:")
        exec(compile(s, m2.__file__, "exec"), m2.__dict__)
    elif mode == "F35":
        m2._check_dense_consistency = lambda *a: None
    elif mode == "F36-invariants":
        from tars.astro import kepler

        m2.kepler_state = kepler.propagate
        gmat_m2.kepler_state = kepler.propagate
    elif mode == "F36-velocity":
        original = gmat_m2.alignment_metrics

        def disabled(*a, **k):
            out = original(*a, **k)
            out["coast_vs_kepler_velocity_error_max_mps"] = 0.0
            return out

        gmat_m2.alignment_metrics = disabled
    elif mode == "F37":
        original = m2.cli_summary_violations

        def disabled(*a, **k):
            return [v for v in original(*a, **k) if "unsubmitted_command_ids" not in v]

        m2.cli_summary_violations = disabled
