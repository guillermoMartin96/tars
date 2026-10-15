# ruff: noqa
import importlib.util, math, inspect
from unittest.mock import patch
import numpy as np
from tars.validation import m2
from tars.astro import kepler
from tars.validation.thresholds import load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS


def module(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    x = importlib.util.module_from_spec(s)
    s.loader.exec_module(x)
    return x


p = module("proof", "toolbox/validators/m2_proof.py")
c = module("cli", "toolbox/scripts/gmat_m2.py")


def mission():
    gates = p.Gates(load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)))
    checks, _ = p.mission_checks(c.BY_NAME["m2_prograde_burn"], gates, quick=False)
    return {
        "checks": len(checks),
        "failed": [x.validator for x in checks if not x.passed],
        "missing": gates.missing,
    }


with patch.object(m2, "simpson_bound", return_value=math.inf):
    rejected, check = c._evaluate("m2_prograde_burn")
    print("infinite Simpson bound standalone", rejected, check and check.passed, flush=True)
    print("infinite Simpson bound full", mission(), flush=True)
orig = kepler.propagate
for field in ["r_x", "v_z"]:
    hits = {}

    def poisoned(*a, **k):
        rr, vv = orig(*a, **k)
        caller = inspect.currentframe().f_back
        if (
            caller.f_code.co_name in ("orbit_checks", "_node_crossings")
            and caller.f_locals.get("_") == 79
        ):
            hits[caller.f_code.co_name] = hits.get(caller.f_code.co_name, 0) + 1
            rr = rr.copy()
            vv = vv.copy()
            if field == "r_x":
                rr[0] = math.nan
            else:
                vv[2] = math.inf
        return rr, vv

    with patch.object(kepler, "propagate", poisoned):
        rejected, check = c._evaluate("m2_prograde_burn")
        print(
            "node unused component",
            field,
            "standalone",
            rejected,
            check and check.passed,
            flush=True,
        )
        print("node unused component", field, "full", mission(), "hits", hits, flush=True)
orig_audit = m2.audit_run
for key in ["sensed_delta_v_rel_error_max", "final_propellant_kg"]:

    def bad(*a, **k):
        audit = orig_audit(*a, **k)
        for metrics in audit.metrics.values():
            if key in metrics:
                metrics[key] = math.nan
        return audit

    with patch.object(m2, "audit_run", bad):
        print("report only", key, mission(), flush=True)
