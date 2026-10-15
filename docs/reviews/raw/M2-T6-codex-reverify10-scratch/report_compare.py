# ruff: noqa
import json, struct
from pathlib import Path

fresh = json.loads(Path("review_scratch/m2.json").read_text())
old = json.loads(Path("previous-m2-report-1270b09.json").read_text())
impl = json.loads(Path("previous-m2-report.json").read_text())
assert len(fresh["results"]) == 213 and len(old["results"]) == 212
print("SUPPLIED baseline has 212 records, not stated 213")
assert fresh["results"] == impl["results"]
count = 0
new = []
by = {r["validator"]: r for r in fresh["results"]}
for a in old["results"]:
    b = by[a["validator"]]
    c = json.loads(json.dumps(b))
    if c["validator"].startswith("o9_gmat["):
        metric = c["metrics"].pop("coast_vs_kepler_velocity_error_max_mps")
        limit = c["thresholds"].pop("coast_vs_kepler_velocity_error_max_mps")
        assert metric <= limit
        new.append((c["validator"], metric, limit))
    assert a == c, a["validator"]
    for k, v in a["metrics"].items():
        assert struct.pack("!d", v) == struct.pack("!d", b["metrics"][k])
        count += 1
print(
    "212 supplied old records identical except new O9 velocity metric/threshold; prior metric bits",
    count,
)
print("new passing metrics", new)
print("fresh results identical to implementer report", len(impl["results"]))
for k in fresh:
    if k != "platform":
        assert fresh[k] == impl[k], k
print("all other report contents identical except platform")
