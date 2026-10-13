# ruff: noqa
import copy, importlib.util, contextlib, io
from pathlib import Path
from tars.validation import reference_snapshot as s

sp = importlib.util.spec_from_file_location("tool_keys", "toolbox/scripts/reference_snapshot.py")
t = importlib.util.module_from_spec(sp)
sp.loader.exec_module(t)
b = s.load_approved()
for tag in ["counter", "entrypoint", "missing_o5", "unknown_o9"]:
    d = copy.deepcopy(b)
    k = next(k for k in d["records"] if "/o5.kepler#" in k)
    if tag == "counter":
        d["records"][k.rsplit("#", 1)[0] + "#999999"] = d["records"].pop(k)
    elif tag == "entrypoint":
        d["records"][k]["entrypoints"] = ["bogus"]
    elif tag == "missing_o5":
        for k in list(d["records"]):
            if "/o5.kepler#" in k:
                del d["records"][k]
    else:
        d["records"]["m2_prograde_burn/o9/o9.unverified#999999"] = copy.deepcopy(d["records"][k])
    p = Path("review_scratch") / f"baseline-keys-{tag}16.json.gz"
    s.write_json(p, d)
    with contextlib.redirect_stdout(io.StringIO()):
        problems = t.verify_baseline(d)
    print(tag, "problems", problems, flush=True)
    assert not problems
