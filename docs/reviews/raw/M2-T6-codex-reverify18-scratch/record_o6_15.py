# ruff: noqa
import importlib.util, sys
from pathlib import Path
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import reference_snapshot as snap

spec = importlib.util.spec_from_file_location("proof_record15", "toolbox/validators/m2_proof.py")
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
original = kepler.propagate
hits = 0


def phase(r, v, dt, mu):
    global hits
    f = sys._getframe(1)
    while f:
        if f.f_code.co_name == "impulsive_row":
            hits += 1
            return original(r, v, dt * 10, mu)
        f = f.f_back
    return original(r, v, dt, mu)


rec = snap.Session("record", "m2_proof")
with patch.object(kepler, "propagate", side_effect=phase):
    rc = proof.main(["--out", "review_scratch/record_o6_proof15.json"], recorder=rec)
print("recording proof exit", rc, "raw wrong-time returns", hits)
base = snap.load_approved()
for key, value in rec.recorded.items():
    if "/o6/o6.midpoint#" in key:
        base["records"][key] = {**value, "entrypoints": base["records"][key]["entrypoints"]}
path = Path("review_scratch/record_o6_candidate15.json.gz")
snap.write_json(path, base)
spec = importlib.util.spec_from_file_location(
    "baseline_tool15", "toolbox/scripts/reference_snapshot.py"
)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
problems = tool.verify_baseline(base)
print("candidate independent baseline check", problems)
assert rc == 0 and hits == 20 and not problems
