# ruff: noqa
import json, hashlib, pathlib, re
from tars.validation import approved_digests as pins, reference_snapshot as s

old = json.load(open("previous-m2-report.json"))
new = json.load(open("review_scratch/m2.json"))
a = old["results"]
b = new["results"]
assert len(a) == 213 and len(b) == 215
extras = [x for x in b if x["validator"] in ["reference_snapshot", "reference_snapshot_margins"]]
assert [x for x in b if x not in extras] == a
assert [x["validator"] for x in extras] == ["reference_snapshot", "reference_snapshot_margins"]
assert all(x["passed"] for x in b)
assert (
    hashlib.sha256(s.snapshot_path().read_bytes()).hexdigest()
    == pins.APPROVED_REFERENCE_SNAPSHOT_SHA256
)
print(
    "213 records identical; exactly two passing new checks; all 215 pass; baseline 3 digest authenticated"
)
print(json.dumps(extras, indent=2))
