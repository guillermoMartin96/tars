# ruff: noqa
import importlib.util, json, sys
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


cli = module("cli", "toolbox/scripts/run_mission.py")
mission = next(m for m in MISSIONS if m.name.endswith("_no_propulsion"))
s = mission.build()
run = run_scenario(s)
summary = cli._propulsion_summary(run)
for field, value in [
    ("final_propellant_kg", 1e9),
    ("final_total_mass_kg", 1e9),
    ("final_engine_state", "burning"),
    ("active_burn_id_at_stop", "burn#999999"),
    ("pending_burn_ids_at_stop", ["burn#999999"]),
]:
    bad = {**summary, field: value}
    violations = m2.cli_summary_violations(run.events, bad, s)
    print(field, value, "violations", violations)
    assert not violations
counts = {"corrupted": 0}


def profile(frame, event, arg):
    if (
        event == "return"
        and frame.f_code.co_name == "_propulsion_summary"
        and isinstance(arg, dict)
        and frame.f_locals["result"].final_propulsion is None
    ):
        arg.update(
            final_propellant_kg=1e9,
            final_total_mass_kg=1e9,
            final_engine_state="burning",
            active_burn_id_at_stop="burn#999999",
            pending_burn_ids_at_stop=["burn#999999"],
        )
        counts["corrupted"] += 1


proof = module("proof", "toolbox/validators/m2_proof.py")
sys.setprofile(profile)
rc = proof.main(["--out", "review_scratch/no_propulsion_summary_m2.json"])
sys.setprofile(None)
print("proof", rc, counts)
a = json.load(open("review_scratch/m2.json"))
b = json.load(open("review_scratch/no_propulsion_summary_m2.json"))
print("identical results", a["results"] == b["results"])
assert rc == 0 and a["results"] == b["results"] and counts["corrupted"] > 0
