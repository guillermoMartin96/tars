"""DR-0027 B / review M3P2-F3: density consequences of the three disputed table cells.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python q10_residual_consequences.py <q10_table_check_results.json> <out.json>

Reads only the per-row values recorded by q10_table_check.py, so it needs neither
source file. Each source is evaluated as its own piecewise-exponential table:
rho(h) = rho_base * exp(-(h - h_base) / H), using the band whose base is the highest
base not above h. The author's file has no 1000 km row, so above 900 km its 900 km band
applies. Below its lowest base (0.010 km) the author's table selects no band; that
interval is reported, not evaluated.
"""

import json
import math
import sys


def table(rows):
    return [tuple(float(x) for x in row) for row in rows]


def density(rows, h_km):
    band = None
    for row in rows:
        if row[0] <= h_km:
            band = row
    if band is None:
        return None
    h0, rho0, scale = band
    return rho0 * math.exp(-(h_km - h0) / scale)


def main(results_path, out_path):
    with open(results_path, encoding="ascii") as fh:
        q10 = json.load(fh)
    gmat = table(c["gmat"] for c in q10["comparison"])
    author = table(c["vallado_file"] for c in q10["comparison"] if c["vallado_file"])

    samples_km = [0.0, 0.005, 0.010, 1.0, 10.0, 24.999, 25.0, 899.999, 900.0, 950.0]
    samples_km += [999.999, 1000.0, 1100.0, 1500.0, 2000.0]
    ratios = []
    for h in samples_km:
        g, a = density(gmat, h), density(author, h)
        ratios.append(
            {
                "h_km": h,
                "rho_gmat": g,
                "rho_author": a,
                "gmat_over_author_minus_1": None if a is None else g / a - 1.0,
            }
        )

    lowest_g, lowest_a = gmat[0], author[0]
    upper_25 = gmat[1]
    below_25_author = lowest_a[1] * math.exp(-(upper_25[0] - lowest_a[0]) / lowest_a[2])
    result = {
        "lowest_band": {
            "author_over_gmat_closed_form": math.exp((lowest_a[0] - lowest_g[0]) / lowest_g[2]),
            "gmat_over_author_minus_1_closed_form": math.exp(
                -(lowest_a[0] - lowest_g[0]) / lowest_g[2]
            )
            - 1.0,
            "applies_for_km": [lowest_a[0], upper_25[0]],
            "author_selects_no_band_below_km": lowest_a[0],
            "jump_at_25_km_gmat": q10["boundaries"][0]["relative_jump"],
            "jump_at_25_km_author": upper_25[1] / below_25_author - 1.0,
        },
        "samples": ratios,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(result, fh, indent=1)
        fh.write("\n")
    print(json.dumps(result["lowest_band"], indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
