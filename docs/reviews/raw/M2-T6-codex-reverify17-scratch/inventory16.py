# ruff: noqa
from tars.validation import reference_snapshot as s

b = s.load_approved()
for label in ["orbit.node_crossings", "o9.gmat_node_crossings", "o9.arcs", "o3.expected_cutoff"]:
    rows = [(k, r) for k, r in b["records"].items() if "/" + label + "#" in k]
    print(label, len(rows))
    print(
        [
            (k, {p: (v["shape"], v["values"][:8]) for p, v in r["parts"].items()})
            for k, r in rows[:3]
        ]
    )
