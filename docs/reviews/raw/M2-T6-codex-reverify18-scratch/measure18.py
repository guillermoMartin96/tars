# ruff: noqa
import json, math
from pathlib import Path
from tars.validation import reference_snapshot as s

maxima = {}
files = list(Path("measurements").glob("*.json"))
for p in files:
    d = json.loads(p.read_text())
    assert d["candidate_sha256"] in {
        "031c7e7bcebb6ae11ba872c9648971da8478c1f981292d3a7fe8acfe7b59e99e",
        "1355cb3a6643de36b485644e749c31941b402988216f51c9cfb2152b63f8bcc9",
        "a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b",
    } or not any(d["max_deviation_by_class"].values())
    for k, v in d["max_deviation_by_class"].items():
        maxima[k] = max(maxima.get(k, 0), v)
for c, v in sorted(maxima.items()):
    tol = s.TOLERANCES[tuple(c.split(":"))]
    assert v == s.MEASURED.get(tuple(c.split(":")), 0.0)
    assert tol >= 10 * v
    print(c, v, tol)
print(len(files), "measurements checked")
