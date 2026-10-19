"""M3 T0: reproduction of the DR-0029 P6 "quadratic-only fit" residual (Review 01/02 IM-1).

DR-0029 P6 option (b) states that recovering GMAT's Earth-fixed +Z axis needs the diurnal
polar-motion term, because a fit without it leaves a residual of about 1 m. This script
computes that number from committed data, with no GMAT run.

Quantity. GMAT's axis probe (`t0_gmat.py` -> `case_axis`) propagates two point-mass
spacecraft (the M1 orbit, and a polar orbit with its node on +Y) for 53 700 s and reports,
every 60 s, each spacecraft's position in GMAT's TOE frame (TOEEq at the scenario epoch,
2026-01-01 TT) and its Z coordinate in GMAT's EarthFixed frame. The Earth-fixed Z of a
point is u(t) . r_TOE, where u(t) is GMAT's Earth-fixed +Z axis expressed in TOE axes. The
fit models
    u(t) = sum_k c_k phi_k(t),
        phi = [1, s, s^2, cos(omega_E t), sin(omega_E t)],  s = t / t_end,
and solves z_EF = u(t) . r_TOE by linear least squares over both spacecraft (3 unknowns per
basis function). The residual is
    e_i = z_EF,i - u(t_i) . r_TOE,i     [m]  (GMAT reports km; converted by 1000)
    RMS = sqrt(mean_i e_i^2)  over N = 2 x 896 equations (t = 0, 60, ..., 53 700 s).

"full" uses all five basis functions (the fit used by `t0_gmat.py`); "quadratic-only"
drops the diurnal pair (the IM-1 figure). The RMS is a fit residual of an axis model, in
metres of Earth-fixed Z at orbital radius; it is not a trajectory error and not a threshold.

Provenance. The data file is `gmat_runs/axis_probe__m1_two_body_report.txt`; its sha256 is
the one GMAT's run metadata recorded (`axis_probe__metadata.json`). The full fit must
reproduce `t0_gmat_results.json` -> `axis` -> `fit_rms_residual_m`.

Research only; adopting option (b), and any tolerance built on these numbers, is an owner
decision (DR-0029 P6, DR-0028 scope ruling).
Usage: uv run --no-sync python t0_axis_ablation.py <out.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import t0_model as m

HERE = Path(__file__).resolve().parent
REPORT = HERE / "gmat_runs" / "axis_probe__m1_two_body_report.txt"
METADATA = HERE / "gmat_runs" / "axis_probe__metadata.json"
STORED = HERE / "t0_gmat_results.json"
BASES = {"full": (0, 1, 2, 3, 4), "quadratic_only": (0, 1, 2)}
# Agreement required between this script and `t0_gmat.py` for the full fit, and between a
# rerun and the recorded quadratic-only value. It exceeds the worst-case rounding scale of
# the least-squares solve (cond x eps x max|z|, `rounding_scale_m`: 5.7e-7 m for the full
# fit) and is 78 times smaller than the full-fit residual (7.8e-5 m). Reruns on one platform
# agree bit for bit; the tolerance covers other BLAS builds.
TOLERANCE_M = 1e-6


def rows() -> np.ndarray:
    out = []
    for line in REPORT.read_text().splitlines():
        parts = line.split()
        try:
            out.append([float(x) for x in parts])
        except ValueError:
            continue  # the report repeats its header line
    return np.array(out)


def design(t: np.ndarray, r: np.ndarray, t_end: float, cols: tuple[int, ...]) -> np.ndarray:
    s = t / t_end
    th = m.OMEGA_E * t
    phi = np.stack([np.ones_like(t), s, s * s, np.cos(th), np.sin(th)], axis=1)[:, cols]
    return np.hstack([r * phi[:, [k]] for k in range(phi.shape[1])])


def fit(cols: tuple[int, ...]) -> dict:
    d = rows()
    t = np.concatenate([d[:, 0], d[:, 0]])
    r = np.vstack([d[:, 1:4], d[:, 5:8]])  # km
    z = np.concatenate([d[:, 4], d[:, 8]])  # km
    a = design(t, r, float(d[-1, 0]), cols)
    coef, *_ = np.linalg.lstsq(a, z, rcond=None)
    e = (z - a @ coef) * 1000.0
    sv = np.linalg.svd(a, compute_uv=False)
    return {
        "basis_columns": list(cols),
        "equations": len(z),
        "unknowns": int(a.shape[1]),
        "epochs": len(d),
        "t_first_s": float(d[0, 0]),
        "t_last_s": float(d[-1, 0]),
        "step_s": float(d[1, 0] - d[0, 0]),
        "rms_residual_m": float(np.sqrt(np.mean(e * e))),
        "max_abs_residual_m": float(np.max(np.abs(e))),
        "condition_number": float(sv[0] / sv[-1]),
        # cond * eps * max|z|: the scale of residual changes rounding can cause
        "rounding_scale_m": float(sv[0] / sv[-1] * np.finfo(float).eps * np.abs(z).max() * 1e3),
    }


def main() -> None:
    meta = json.loads(METADATA.read_text())
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    stored = json.loads(STORED.read_text())["axis"]["fit_rms_residual_m"]
    out = {
        "data_file": str(REPORT.relative_to(HERE)),
        "data_sha256": digest,
        "data_sha256_matches_gmat_metadata": digest
        == meta["reports_sha256"]["m1_two_body_report.txt"],
        "units": "metres of GMAT EarthFixed Z (report values in km x 1000)",
        "rms_definition": "sqrt(mean over both spacecraft and all epochs of e_i^2)",
        "tolerance_m": TOLERANCE_M,
        "fits": {name: fit(cols) for name, cols in BASES.items()},
        "stored_full_fit_rms_m": stored,
    }
    out["full_fit_reproduces_t0_gmat"] = (
        abs(out["fits"]["full"]["rms_residual_m"] - stored) <= TOLERANCE_M
    )
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
