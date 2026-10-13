# ruff: noqa
import itertools
from tars.validation import m2, reference_snapshot as s
from tars.validation.m2_missions import MISSIONS

for m in MISSIONS:
    if not m.impulsive_limit:
        continue
    rows = m2.impulsive_family(m.build())
    d = s.TOLERANCES["sim", "m"]
    shifts = m2.o6_snapshot_shifts(rows, d)
    base = m2.impulsive_metrics(rows)
    for corner in itertools.product([-d, d], repeat=5):
        moved = [
            {
                **r,
                "sma_finite_minus_impulsive_m": r["sma_finite_minus_impulsive_m"] - e,
                "sma_change_impulsive_m": r["sma_change_impulsive_m"] + e,
            }
            for r, e in zip(rows, corner)
        ]
        out = m2.impulsive_metrics(moved)
        for k, limit in shifts.items():
            assert abs(out[k] - base[k]) <= limit * (1 + 1e-9)
    print(m.name, "32 corners bounded", shifts, flush=True)
