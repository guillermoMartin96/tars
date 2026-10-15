# ruff: noqa
import dataclasses, importlib.util, math
from unittest.mock import patch
from tars.sim.runner import run_scenario
from tars.validation import m2
from tars.validation.thresholds import load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS


def module(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    x = importlib.util.module_from_spec(s)
    s.loader.exec_module(x)
    return x


p = module("proof", "toolbox/validators/m2_proof.py")
c = module("cli", "toolbox/scripts/gmat_m2.py")


def wrong_sensed(s):
    run = run_scenario(s)
    ends = [e for e in run.events if e.type == "BurnEnded"]
    if not ends:
        return run
    end = ends[0]
    eps = 1e-6
    events = []
    for e in run.events:
        if e is end:
            e = e.model_copy(update={"sensed_delta_v_mps": e.sensed_delta_v_mps + eps})
        elif e.type == "PropulsionSampled" and e.t >= end.event_t_s:
            e = e.model_copy(update={"delta_v_sensed_mps": e.delta_v_sensed_mps + eps})
        events.append(e)
    fp = dataclasses.replace(
        run.final_propulsion, delta_v_sensed_mps=run.final_propulsion.delta_v_sensed_mps + eps
    )
    return dataclasses.replace(run, events=events, final_propulsion=fp)


for infinite in [False, True]:
    with (
        patch.object(p, "run_scenario", wrong_sensed),
        patch.object(c, "run_scenario", wrong_sensed),
    ):

        def check():
            rejected, result = c._evaluate("m2_prograde_burn")
            print(
                "wrong sensed +1e-6, infinite bound",
                infinite,
                "standalone",
                rejected,
                result and result.passed,
                flush=True,
            )
            gates = p.Gates(load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)))
            checks, _ = p.mission_checks(c.BY_NAME["m2_prograde_burn"], gates, quick=False)
            print(
                "wrong sensed +1e-6, infinite bound",
                infinite,
                "full",
                len(checks),
                "failed",
                [x.validator for x in checks if not x.passed],
                "missing",
                gates.missing,
                flush=True,
            )

        if infinite:
            with patch.object(m2, "simpson_bound", return_value=math.inf):
                check()
        else:
            check()
