# ruff: noqa
from pathlib import Path
from tars.validation import reference_snapshot as s
import subprocess, os

base = s.load_approved()
keys = [k for k in base["records"] if "/o6/o6.midpoint#" in k]
assert len(keys) == 10
for k in keys:
    p = base["records"][k]["parts"]
    p["r_m"]["values"] = [0.0, 0.0, 0.0]
    p["v_mps"]["values"] = [0.0, 0.0, 0.0]
    p["sma_impulsive_m"]["values"] = [-1e30]
path = Path("review_scratch/invalid-o6-baseline.json.gz")
s.write_json(path, base)
result = subprocess.run(
    [".venv/bin/python", "toolbox/scripts/reference_snapshot.py", "verify-baseline", str(path)],
    capture_output=True,
    text=True,
)
print("mutated", len(keys), "O6 midpoints to zero r/v and SMA=-1e30")
print("verify-baseline exit", result.returncode, result.stdout, result.stderr)
with s.session("m2_proof", path=path) as sess:
    pass
print("runtime verification", sess.finish())
assert result.returncode == 0
