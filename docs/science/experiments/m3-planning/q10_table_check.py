"""DR-0024 Q10: compare the GMAT exponential-atmosphere table with the author's data file.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python q10_table_check.py <GMAT table> <Vallado ATMOSEXP.DAT> <out.json>

<GMAT table> is data/atmosphere/earth/EarthExponentialAtmosphereData.txt.

The GMAT file is comma-separated (base altitude km, density kg/m^3, scale height km).
The author's file (CelesTrak/fundamentals-of-astrodynamics, software/misc/pascal/ATMOSEXP.DAT)
is whitespace-separated with the same three columns.

The script reports, row by row, whether the two sources agree exactly as printed
(decimal comparison of the parsed numbers), and quantifies the value discontinuity of the
GMAT table at every band boundary: the density of the band below, evaluated at the
boundary, against the tabulated base density of the band above.
"""

import hashlib
import itertools
import json
import math
import sys
from decimal import Decimal


def read_rows(path, sep):
    rows = []
    with open(path, encoding="ascii") as fh:
        for line in fh:
            if not line.strip():
                continue
            parts = line.split(",") if sep == "," else line.split()
            rows.append(tuple(Decimal(p.strip()) for p in parts))
    return rows


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main(gmat_path, vallado_path, out_path):
    gmat = read_rows(gmat_path, ",")
    vallado = read_rows(vallado_path, None)
    by_alt = {round(float(r[0])): r for r in vallado}

    comparison = []
    for row in gmat:
        alt = round(float(row[0]))
        other = by_alt.get(alt)
        if other is None and alt == 0:
            other = by_alt.get(0)
        entry = {
            "gmat": [str(x) for x in row],
            "vallado_file": [str(x) for x in other] if other else None,
        }
        if other is None:
            entry["status"] = "absent_from_author_file"
        else:
            diffs = [
                name
                for name, a, b in zip(("base_km", "rho", "H_km"), row, other, strict=True)
                if a != b
            ]
            entry["status"] = "identical" if not diffs else "differs"
            entry["differing_fields"] = diffs
        comparison.append(entry)

    boundaries = []
    for (h0, r0, s0), (h1, r1, s1) in itertools.pairwise(gmat):
        below = float(r0) * math.exp(-(float(h1) - float(h0)) / float(s0))
        boundaries.append(
            {
                "boundary_km": float(h1),
                "rho_below_at_boundary": below,
                "rho_above_base": float(r1),
                "relative_jump": (float(r1) - below) / below,
                "scale_height_below_km": float(s0),
                "scale_height_above_km": float(s1),
            }
        )

    result = {
        "inputs": {
            "gmat_table_sha256": sha256(gmat_path),
            "vallado_file_sha256": sha256(vallado_path),
            "gmat_rows": len(gmat),
            "vallado_rows": len(vallado),
        },
        "summary": {
            status: sum(1 for c in comparison if c["status"] == status)
            for status in ("identical", "differs", "absent_from_author_file")
        },
        "comparison": comparison,
        "boundaries": boundaries,
        "max_abs_relative_jump": max(abs(b["relative_jump"]) for b in boundaries),
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(result, fh, indent=1)
        fh.write("\n")
    print(json.dumps(result["summary"]))
    for c in comparison:
        if c["status"] != "identical":
            print(c)


if __name__ == "__main__":
    main(*sys.argv[1:4])
