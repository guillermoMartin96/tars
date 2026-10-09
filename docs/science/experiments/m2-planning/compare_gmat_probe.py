# ruff: noqa  -- planning-experiment script kept as run (VAL-0008/0009); not project code.
"""Compare GMAT finite-burn probe reports with the DOP853 reference (research only)."""

import json
import sys

import numpy as np

ref = json.load(open(sys.argv[1]))
out = {}
for name in sys.argv[2:]:
    rows = [list(map(float, l.split())) for l in open(name) if l.strip()]
    burn_end, final = np.array(rows[1]), np.array(rows[2])
    rf = np.array(ref["ref_final_state"])
    rc = np.array(ref["ref_cutoff_state"])
    m_an = ref["config"]["dry"] + ref["config"]["prop"] - ref["prop_used_analytic"]
    out[name.split("/")[-1]] = dict(
        cutoff_pos_diff_m=float(np.linalg.norm(burn_end[1:4] * 1e3 - rc[:3])),
        cutoff_vel_diff_mps=float(np.linalg.norm(burn_end[4:7] * 1e3 - rc[3:6])),
        final_pos_diff_m=float(np.linalg.norm(final[1:4] * 1e3 - rf[:3])),
        final_vel_diff_mps=float(np.linalg.norm(final[4:7] * 1e3 - rf[3:6])),
        mass_after_minus_analytic_kg=float(burn_end[7] - m_an),
        sma_after_minus_ref_m=float(burn_end[8] * 1e3 - ref["sma_after_m"]),
        implied_burn_duration_diff_s=float((m_an - burn_end[7]) / ref["config"]["mdot"]),
        mjd_ulp_s=float(np.spacing(burn_end[0]) * 86400.0),
    )
print(json.dumps(out, indent=1))
