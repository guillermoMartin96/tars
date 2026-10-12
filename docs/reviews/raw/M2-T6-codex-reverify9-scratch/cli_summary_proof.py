# ruff: noqa
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
mutations = 0


def corrupt_returned_data(frame, event, arg):
    global mutations
    if (
        event == "return"
        and frame.f_code.co_name == "_propulsion_summary"
        and frame.f_code.co_filename.endswith("/toolbox/scripts/run_mission.py")
    ):
        # Edit the real producer's returned dictionary in place; replace no code.
        arg["unsubmitted_command_ids"] = ["invented-command"]
        mutations += 1


sys.setprofile(corrupt_returned_data)
try:
    rc = proof.main(["--out", "review_scratch/cli_summary_m2.json"])
finally:
    sys.setprofile(None)
print("proof exit:", rc, "corrupted CLI summary dictionaries:", mutations)
assert rc == 0 and mutations > 0
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/cli_summary_m2.json"))
print("all check records identical:", clean["results"] == bad["results"])
assert clean["results"] == bad["results"]
