# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])
d = refs("infinite_limit")
f = gmat_m2.reference_files(name, d)
lines = f["report"].read_text().splitlines()
row = lines[60].split()
row[2] = str(float(row[2]) + 0.001)
lines[60] = " ".join(row)
f["report"].write_text("\n".join(lines) + "\n")
meta = json.loads(f["metadata"].read_text())
meta["report_sha256"] = hashlib.sha256(f["report"].read_bytes()).hexdigest()
f["metadata"].write_text(json.dumps(meta))
p = d / "APPROVED_DIGESTS.json"
man = json.loads(p.read_text())
man["references"][name]["report_sha256"] = meta["report_sha256"]
man["references"][name]["metadata_sha256"] = hashlib.sha256(f["metadata"].read_bytes()).hexdigest()
next(h for h in reversed(man["history"]) if h["mission"] == name)["report_sha256"] = meta[
    "report_sha256"
]
p.write_text(json.dumps(man))
r, c = cli._evaluate(name, base=d)
print("finite_limit", r, c.failures if c else None, flush=True)
orig = cli.load_scoped_thresholds
path = scratch / "infinite_thresholds.json"
data = json.loads(Path("proof/thresholds/m2.json").read_text())
data["limits"]["o9_gmat"]["all"]["gmat_vs_dop853_position_error_max_m"] = float("inf")
path.write_text(json.dumps(data).replace(": Infinity", ": 1e999"))


def bad(*a, **k):
    return orig(path=path, **k)


with patch.object(cli, "load_scoped_thresholds", bad):
    r, c = cli._evaluate(name, base=d)
    print(
        "infinite_limit",
        r,
        c.passed if c else None,
        c.metrics["gmat_vs_dop853_position_error_max_m"] if c else None,
        flush=True,
    )
