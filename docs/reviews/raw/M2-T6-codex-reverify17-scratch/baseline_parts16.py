# ruff: noqa
import copy, importlib.util, contextlib, io
from pathlib import Path
from tars.validation import reference_snapshot as s

spec = importlib.util.spec_from_file_location("tool16", "toolbox/scripts/reference_snapshot.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
base = s.load_approved()
for label, part, value in [
    ("o9.arcs", "step_s", 12345.0),
    ("orbit.node_crossings", "powered_1", 999.0),
]:
    d = copy.deepcopy(base)
    key = next(k for k in d["records"] if "/" + label + "#" in k)
    d["records"][key]["parts"][part]["values"] = [value] * len(
        d["records"][key]["parts"][part]["values"]
    )
    path = Path("review_scratch") / (label + ".corrupt16.json.gz")
    s.write_json(path, d)
    with contextlib.redirect_stdout(io.StringIO()):
        problems = t.verify_baseline(d)
    print(key, part, d["records"][key]["parts"][part]["values"], "problems", problems, flush=True)
    assert not problems
