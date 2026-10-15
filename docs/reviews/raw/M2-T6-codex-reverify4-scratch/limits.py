# ruff: noqa
import copy, json
from pathlib import Path
from tars.validation.thresholds import *
from tars.validation.m2_missions import MISSIONS

for tag, path, loader, group, depth in [
    ("m1", M1_THRESHOLDS, load_thresholds, "kepler_reference", 2),
    (
        "m2",
        M2_THRESHOLDS,
        lambda p: load_scoped_thresholds(p, missions=frozenset(m.name for m in MISSIONS)),
        "o9_gmat",
        3,
    ),
]:
    original = json.loads(path.read_text())
    for where in ["root", "group", "scope", "leaf"]:
        if tag == "m1" and where == "scope":
            continue
        for val in [{}, [], 5, None, "bad"]:
            d = copy.deepcopy(original)
            if where == "root":
                d["limits"] = val
            elif where == "group":
                d["limits"][group] = val
            elif where == "scope":
                d["limits"][group]["all"] = val
            else:
                target = d["limits"][group] if depth == 2 else d["limits"][group]["all"]
                target[next(iter(target))] = val
            f = Path("review_scratch/limit.json")
            f.write_text(json.dumps(d))
            try:
                loader(f)
                outcome = "ACCEPT"
            except Exception as e:
                outcome = type(e).__name__
            print(tag, where, repr(val), outcome)
