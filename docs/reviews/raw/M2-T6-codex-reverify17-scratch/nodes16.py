# ruff: noqa
import copy, importlib.util, contextlib, io
from pathlib import Path
from tars.validation import reference_snapshot as s

sp = importlib.util.spec_from_file_location("tool_nodes", "toolbox/scripts/reference_snapshot.py")
t = importlib.util.module_from_spec(sp)
sp.loader.exec_module(t)
b = s.load_approved()
for kind in ["duplicate", "empty", "missing"]:
    d = copy.deepcopy(b)
    keys = [
        k for k in d["records"] if "/orbit.node_crossings#" in k or "/o9.gmat_node_crossings#" in k
    ]
    for k in keys:
        p = d["records"][k]["parts"]["crossings_s"]
        if kind == "duplicate":
            p["values"] = [p["values"][0]] * len(p["values"]) if p["values"] else []
        elif kind == "empty":
            p["values"] = []
            p["shape"] = [0]
        else:
            del d["records"][k]
    path = Path("review_scratch") / f"nodes-{kind}16.json.gz"
    s.write_json(path, d)
    with contextlib.redirect_stdout(io.StringIO()):
        ps = t.verify_baseline(d)
    print(kind, "mutated records", len(keys), "problems", ps, flush=True)
    assert not ps
