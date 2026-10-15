# ruff: noqa
import math
import numpy as np
from tars.validation import reference_snapshot as snap

for seed in ["ref", "gmat", "sim"]:
    with snap.session("m2_proof") as rec:
        choices = [
            (max(map(abs, p["values"]), default=0), k, name)
            for k, r in rec.approved.items()
            if r["seed"] == seed and not r["exact"]
            for name, p in r["parts"].items()
            if snap.unit_of(name) == "s"
        ]
        largest, key, name = max(choices)
        r = rec.approved[key]
        parts = {p: np.array(v["values"]).reshape(v["shape"]) for p, v in r["parts"].items()}
        arr = parts[name]
        ix = np.argmax(np.abs(arr))
        x = arr.flat[ix]
        arr.flat[ix] = math.nextafter(math.nextafter(float(x), math.inf), math.inf)
        scope, labeln = key.rsplit("/", 1)
        label, n = labeln.split("#")
        rec.scopes = scope.split("/")
        rec.counters[scope + "/" + label] = int(n)
        snap.pin(label, seed, r["exact"], **parts)
        shift = abs(arr.flat[ix] - x)
        rule = 10 * math.ulp(largest)
        tol = snap.TOLERANCES[(seed, "s")]
        print(
            seed,
            key,
            name,
            "maximum",
            largest,
            "required 10ulp",
            rule,
            "actual tolerance",
            tol,
            "two-ulp deviation",
            shift,
            "problems",
            rec.finish(complete=False),
        )
        assert tol < rule and tol < shift <= rule and rec.finish(complete=False)
