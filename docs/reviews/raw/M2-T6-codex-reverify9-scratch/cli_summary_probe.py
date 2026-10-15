# ruff: noqa
import importlib.util
import json
from tars.sim.runner import run_scenario
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import Check

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/run_mission.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
mission = next(m for m in MISSIONS if m.name == "m2_invalid_commands")
run = run_scenario(mission.build())
summary = cli._propulsion_summary(run)
assert summary["unsubmitted_command_ids"] == []
for bad in (["inv-burn-A"], ["invented-command"], None):
    corrupted = {**summary, "unsubmitted_command_ids": bad}
    violations = m2.cli_summary_violations(run.events, corrupted)
    check = Check(
        "cli_summary[m2_invalid_commands]",
        {"violations": float(len(violations))},
        {"violations": 0.0},
        "approved",
    )
    print(
        json.dumps(
            {"corrupted_unsubmitted_ids": bad, "violations": violations, "passed": check.passed}
        )
    )
    assert check.passed
