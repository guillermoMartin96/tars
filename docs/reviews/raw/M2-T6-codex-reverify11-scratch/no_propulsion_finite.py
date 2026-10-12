# ruff: noqa
import importlib.util, math
from tars.sim.runner import run_scenario
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS

spec = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
s = next(m for m in MISSIONS if m.name == "m2_invalid_commands_no_propulsion").build()
r = run_scenario(s)
good = p._cli_summary(r)
assert not m2.cli_summary_violations(r.events, good, s)
for field in [
    "final_propellant_kg",
    "final_total_mass_kg",
    "final_engine_state",
    "active_burn_id_at_stop",
    "pending_burn_ids_at_stop",
]:
    for value in [math.nan, math.inf, -math.inf]:
        assert m2.cli_summary_violations(r.events, {**good, field: value}, s)
print("all 15 non-finite no-propulsion summary mutations rejected")
