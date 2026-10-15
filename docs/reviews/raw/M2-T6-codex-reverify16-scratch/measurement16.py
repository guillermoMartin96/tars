# ruff: noqa
import json, hashlib, math
from pathlib import Path
from tars.validation import reference_snapshot as s

maxima = {}
pins = {
    "031c7e7bcebb6ae11ba872c9648971da8478c1f981292d3a7fe8acfe7b59e99e",
    hashlib.sha256(s.snapshot_path().read_bytes()).hexdigest(),
}
for p in Path("measurements").glob("*.json"):
    d = json.loads(p.read_text())
    assert d["candidate_sha256"] in pins or (
        p.name == "reference-host-deviation.json"
        and all(v == 0 for v in d["max_deviation_by_class"].values())
    )
    for k, v in d["max_deviation_by_class"].items():
        maxima[k] = max(maxima.get(k, 0), v)
for c, v in sorted(maxima.items()):
    tol = s.TOLERANCES[tuple(c.split(":"))]
    if v:
        choices = [m * 10**e for e in range(-20, 5) for m in [1, 2, 5]]
        assert math.isclose(tol, min(x for x in choices if x >= 10 * v), rel_tol=1e-14)
    print(c, v, tol)
print("17 measurements checked")
