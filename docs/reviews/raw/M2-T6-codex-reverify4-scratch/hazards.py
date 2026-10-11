# ruff: noqa
import importlib.util, math, copy
from unittest.mock import patch
import numpy as np
import scipy.integrate
from tars.validation import m2
from tars.validation.thresholds import load_scoped_thresholds, Check
from tars.validation.m2_missions import MISSIONS


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    x = importlib.util.module_from_spec(s)
    s.loader.exec_module(x)
    return x


p = module("proof", "toolbox/validators/m2_proof.py")
c = module("cli", "toolbox/scripts/gmat_m2.py")
mission = c.BY_NAME["m2_prograde_burn"]
names = frozenset(m.name for m in MISSIONS)
original = scipy.integrate.solve_ivp
calls = 0
bad = 0


def poisoned(*a, **k):
    global calls, bad
    sol = original(*a, **k)
    # Poison dense output on one non-extremal initial coast segment only.
    if a[1] == (0.0, 60.0):
        old = sol.sol

        def dense(t):
            global bad
            y = old(t).copy()
            y[:3] = math.nan
            bad += 1
            return y

        sol.sol = dense
    return sol


with patch.object(scipy.integrate, "solve_ivp", poisoned):
    rejected, check = c._evaluate(mission.name)
    print("dense standalone", bad, rejected, check.passed if check else None, flush=True)
    gates = p.Gates(load_scoped_thresholds(missions=names))
    checks, _ = p.mission_checks(mission, gates, quick=True)
    print(
        "dense integrated",
        bad,
        "failed",
        [x.validator for x in checks if not x.passed],
        "missing",
        gates.missing,
        flush=True,
    )
# Auxiliary O4 result: individually fails, discarded when merged after a finite audit.
from tars.sim.runner import run_scenario

s = mission.build()
audit = m2.audit_run(s, mission.expected, run_scenario(s))
invalid = copy.deepcopy(audit)
invalid.metrics["o4_reference"]["sample_position_error_max_m"] = math.nan
limits = load_scoped_thresholds(missions=names).for_validator("o4_reference", mission.name)
print(
    "individual NaN O4 passed",
    Check("o4", invalid.metrics["o4_reference"], limits, "provisional").passed,
)
merged = p._merge_audits([("dt5", audit), ("dt2", invalid)])
gates = p.Gates(load_scoped_thresholds(missions=names))
checks = p._audit_checks(gates, "aux", mission.name, merged)
print(
    "merged NaN O4 value",
    merged.metrics["o4_reference"]["sample_position_error_max_m"],
    "failed",
    [x.validator for x in checks if not x.passed],
    flush=True,
)
