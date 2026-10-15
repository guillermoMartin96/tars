# ruff: noqa
import copy
from pathlib import Path
from tars.validation import reference_snapshot as s

b = s.load_approved()
for kind in ["value", "key", "counter", "entrypoint", "missing", "nan", "seed", "exact"]:
    d = copy.deepcopy(b)
    k = next(iter(d["records"]))
    r = d["records"][k]
    if kind == "value":
        next(iter(r["parts"].values()))["values"][0] += 1
    elif kind == "key":
        d["records"]["bogus"] = d["records"].pop(k)
    elif kind == "counter":
        d["records"][k.split("#")[0] + "#99999"] = d["records"].pop(k)
    elif kind == "entrypoint":
        r["entrypoints"] = ["bogus"]
    elif kind == "missing":
        del d["records"][k]
    elif kind == "nan":
        next(iter(r["parts"].values()))["values"][0] = float("nan")
    elif kind == "seed":
        r["seed"] = "sim"
    elif kind == "exact":
        r["exact"] = not r["exact"]
    p = Path("review_scratch") / ("auth-" + kind + "17.json.gz")
    s.write_json(p, d)
    try:
        s.load_approved(p)
    except s.SnapshotError:
        print("artifact", kind, "REJECTED")
    else:
        raise AssertionError(kind)
for kind in ["counter", "empty-ledger", "missing-record", "key"]:
    with s.session("m2_proof") as rec:
        k = next(
            k
            for k, r in rec.approved.items()
            if r["entrypoints"] == ["m2_proof"] and "/o6.delta_v#" in k
        )
        r = rec.approved[k]
        scope, labeln = k.rsplit("/", 1)
        label, n = labeln.split("#")
        rec.scopes = scope.split("/")
        rec.counters[scope + "/" + label] = int(n)
        if kind == "counter":
            rec.counters[scope + "/" + label] = 99999
        elif kind == "empty-ledger":
            rec.approved = {}
        elif kind == "missing-record":
            del rec.approved[k]
        elif kind == "key":
            rec.approved[k + "bogus"] = rec.approved.pop(k)
        s.pin(
            label,
            r["seed"],
            r["exact"],
            **{p: s.np.asarray(v["values"]).reshape(v["shape"]) for p, v in r["parts"].items()},
        )
        assert rec.finish(complete=False)
        print("session", kind, "REJECTED")
