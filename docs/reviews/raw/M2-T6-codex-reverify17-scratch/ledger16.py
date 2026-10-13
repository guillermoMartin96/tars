# ruff: noqa
from pathlib import Path
import copy, json, math, hashlib
import numpy as np
from tars.validation import reference_snapshot as s

base = s.load_approved()
key = next(iter(base["records"]))
for tag in ("value", "key", "counter", "entrypoint", "seed", "nan", "removed"):
    d = copy.deepcopy(base)
    rec = d["records"][key]
    if tag == "value":
        next(iter(rec["parts"].values()))["values"][0] += 1.0
    elif tag == "key":
        d["records"]["bogus#0"] = d["records"].pop(key)
    elif tag == "counter":
        d["records"][key.rsplit("#", 1)[0] + "#999999"] = d["records"].pop(key)
    elif tag == "entrypoint":
        rec["entrypoints"] = ["bogus"]
    elif tag == "seed":
        rec["seed"] = "sim" if rec["seed"] == "ref" else "ref"
    elif tag == "nan":
        next(iter(rec["parts"].values()))["values"][0] = math.nan
    else:
        del d["records"][key]
    p = Path("review_scratch") / f"snapshot-{tag}.json.gz"
    s.write_json(p, d)
    with s.session("m2_proof", path=p) as sess:
        pass
    assert sess.finish()
    print(tag, sess.finish())
# Runtime data: labels/counters/seed/shape and missing observations.
rec = base["records"][key]
prefix, label = key.rsplit("/", 1)
label = label.rsplit("#", 1)[0]
parts = {k: np.array(v["values"]).reshape(v["shape"]) for k, v in rec["parts"].items()}
for tag in ("label", "counter", "seed", "shape", "missing"):
    with s.session("m2_proof") as sess, s.scope(*prefix.split("/")):
        if tag == "counter":
            sess.pin(label, rec["seed"], parts, rec["exact"])
        if tag != "missing":
            ps = copy.deepcopy(parts)
            if tag == "shape":
                ps[next(iter(ps))] = np.array([1.0, 2.0, 3.0, 4.0])
            sess.pin(
                label + "bad" if tag == "label" else label,
                "sim" if tag == "seed" and rec["seed"] == "ref" else rec["seed"],
                ps,
                rec["exact"],
            )
    probs = sess.finish(complete=tag == "missing")
    assert probs
    print("runtime", tag, probs[:2])
