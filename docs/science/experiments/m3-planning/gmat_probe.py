# ruff: noqa  -- planning-experiment script kept as run; not project code.
"""M3 planning GMAT feasibility probe (research only; no Proof gate; not a reference).

Question: can GMAT R2026a serve as an exact-configuration external reference for the
candidate M3 physics (J2 about the frame z axis; piecewise-exponential drag with spherical
altitude and an atmosphere co-rotating about z), and what does GMAT actually apply?

Cases (all from the M1 initial state, propagated 53 700 s in one Propagate command):
  j2_jgm3_2026     Degree 2 / order 0 from GMAT's JGM3.cof, epoch 2026-01-01 TT
  j2_custom_2026   custom .cof: GM 3.986004418e14, R 6378137 m, C20 = EGM2008 tide-free
  j2_custom_2000   the same at epoch 2000-01-01 12:00 TT (pole of date ~ J2000 pole)
  c20zero_fileGM   custom .cof with C20 = 0 and GM = 3.986004415e14, Earth.Mu = 3.986004418e14:
                   reveals which GM the gravity field applies
  drag_sph_2026    degree-0 custom field + Exponential drag, Earth.Flattening = 0
  drag_geod_2026   the same with the default flattening (geodetic altitude)
  drag_sph_2000    drag_sph at epoch 2000-01-01 12:00 TT
  *_TOE            the same, with the initial state given and the final state reported in GMAT's
                   true-of-epoch axes (TOEEq) fixed at the scenario epoch
Each GMAT final state is compared with SciPy DOP853 runs of the Python candidate models in
perturbation_experiment.py.

Usage: uv run --no-sync python gmat_probe.py <repo>/src <repo>/scenarios/m1_leo_250km.json <GmatConsole> <out.json>
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import perturbation_experiment as pe

pe.load(sys.argv[1], sys.argv[2])
CONSOLE = Path(sys.argv[3])
OUT = Path(sys.argv[4])
T_END = 53_700.0
EXP_FILE = CONSOLE.parent.parent / "data/atmosphere/earth/EarthExponentialAtmosphereData.txt"
C20_EGM2008_TF = -0.484165143790815e-3


def cof(gm: float, radius: float, c20: float) -> str:
    return (
        "COMMENT   1\n"
        "CCCCC  TARS M3 planning probe: degree-2 zonal only                       CCCCC\n"
        f"POTFIELD  2  2  1 {gm:.14e} {radius:.14e} 1.00000000000000e+00\n"
        f"RECOEF    2  0   {c20:.14e}\n"
        "RECOEF    2  1    0.00000000000000e+00 0.00000000000000e+00\n"
        "RECOEF    2  2    0.00000000000000e+00 0.00000000000000e+00\n"
        "END\n"
    )


def script(
    epoch: str,
    cof_path: str,
    degree: int,
    drag: bool,
    flattening: float | None,
    report: str,
    toe_a1mjd: float | None = None,
) -> str:
    r, v = [float(x) for x in pe.R0 / 1000.0], [float(x) for x in pe.V0 / 1000.0]
    lines = [
        "GMAT Earth.Mu = 398600.4418;",
        "GMAT Earth.EquatorialRadius = 6378.137;",
    ]
    if flattening is not None:
        lines.append(f"GMAT Earth.Flattening = {flattening!r};")
    cs = "EarthMJ2000Eq"
    if toe_a1mjd is not None:
        # True-of-epoch axes fixed at the scenario epoch: GMAT's J2 axis at the epoch is then
        # (up to polar motion and pole drift during the run) this frame's z axis.
        cs = "TOE"
        lines += [
            "Create CoordinateSystem TOE;",
            "GMAT TOE.Origin = Earth;",
            "GMAT TOE.Axes = TOEEq;",
            f"GMAT TOE.Epoch = {toe_a1mjd!r};",
        ]
    lines += [
        "Create Spacecraft Sat;",
        "GMAT Sat.DateFormat = TTGregorian;",
        f"GMAT Sat.Epoch = '{epoch}';",
        f"GMAT Sat.CoordinateSystem = {cs};",
        "GMAT Sat.DisplayStateType = Cartesian;",
        f"GMAT Sat.X = {r[0]!r};",
        f"GMAT Sat.Y = {r[1]!r};",
        f"GMAT Sat.Z = {r[2]!r};",
        f"GMAT Sat.VX = {v[0]!r};",
        f"GMAT Sat.VY = {v[1]!r};",
        f"GMAT Sat.VZ = {v[2]!r};",
        "GMAT Sat.DryMass = 850.0;",
        "GMAT Sat.DragArea = 15.0;",
        "GMAT Sat.Cd = 2.2;",
        "Create ForceModel FM;",
        "GMAT FM.CentralBody = Earth;",
        "GMAT FM.PrimaryBodies = {Earth};",
        "GMAT FM.PointMasses = {};",
        f"GMAT FM.GravityField.Earth.Degree = {degree};",
        "GMAT FM.GravityField.Earth.Order = 0;",
        f"GMAT FM.GravityField.Earth.PotentialFile = '{cof_path}';",
        "GMAT FM.GravityField.Earth.TideModel = 'None';",
        "GMAT FM.SRP = Off;",
        "GMAT FM.RelativisticCorrection = Off;",
        "GMAT FM.ErrorControl = RSSStep;",
    ]
    if drag:
        lines += [
            "GMAT FM.Drag.AtmosphereModel = Exponential;",
            f"GMAT FM.Drag.InputFile = '{EXP_FILE}';",
        ]
    else:
        lines.append("GMAT FM.Drag = None;")
    lines += [
        "Create Propagator Prop;",
        "GMAT Prop.FM = FM;",
        "GMAT Prop.Type = PrinceDormand78;",
        "GMAT Prop.InitialStepSize = 60.0;",
        "GMAT Prop.Accuracy = 1e-13;",
        "GMAT Prop.MinStep = 0;",
        "GMAT Prop.MaxStep = 60.0;",
        "GMAT Prop.MaxStepAttempts = 50;",
        "Create ReportFile R;",
        f"GMAT R.Filename = '{report}';",
        "GMAT R.Precision = 16;",
        "GMAT R.WriteHeaders = false;",
        "BeginMissionSequence;",
        f"Report R Sat.ElapsedSecs Sat.{cs}.X Sat.{cs}.Y Sat.{cs}.Z Sat.{cs}.VX Sat.{cs}.VY Sat.{cs}.VZ;",
        f"Propagate Prop(Sat) {{Sat.ElapsedSecs = {T_END}}};",
        f"Report R Sat.ElapsedSecs Sat.{cs}.X Sat.{cs}.Y Sat.{cs}.Z Sat.{cs}.VX Sat.{cs}.VY Sat.{cs}.VZ;",
    ]
    return "\n".join(lines) + "\n"


def run_case(tmp: Path, name: str, **kw) -> np.ndarray:
    report = tmp / f"{name}_report.txt"
    text = script(report=str(report), **kw)
    path = tmp / f"{name}.script"
    path.write_text(text)
    (HERE / "gmat_scripts").mkdir(exist_ok=True)
    (HERE / "gmat_scripts" / f"{name}.script").write_text(
        text.replace(str(tmp), "<tmp>").replace(str(CONSOLE.parent.parent), "<GMAT>")
    )
    proc = subprocess.run(
        [str(CONSOLE), "--run", str(path)],
        cwd=CONSOLE.parent,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if proc.returncode != 0 or not report.exists():
        raise RuntimeError(f"{name}: GMAT failed\n{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}")
    rows = [list(map(float, ln.split())) for ln in report.read_text().splitlines() if ln.strip()]
    first, last = np.array(rows[0]), np.array(rows[-1])
    assert abs(last[0] - T_END) < 1e-6, last[0]
    return first[1:] * 1000.0, last[1:] * 1000.0


def main() -> None:
    import hashlib, platform

    version = subprocess.run(
        [str(CONSOLE), "--version"], cwd=CONSOLE.parent, capture_output=True, text=True
    ).stdout
    results = {
        "gmat_console_sha256": hashlib.sha256(CONSOLE.read_bytes()).hexdigest(),
        "gmat_version_output": [
            ln.strip()
            for ln in version.splitlines()
            if "Build Date" in ln or "Console Application" in ln
        ],
        "host": platform.platform(),
        "t_end_s": T_END,
        "cases": {},
    }
    py = {}
    mu, re = pe.MU_WGS84, pe.RE_WGS84
    j2 = -math.sqrt(5.0) * C20_EGM2008_TF
    b = 850.0 / (2.2 * 15.0)
    py["kepler_wgs84"] = pe.dop(pe.make_accel(mu, re), pe.R0, pe.V0, T_END).y[:, -1]
    py["kepler_gm415"] = pe.dop(pe.make_accel(3.986004415e14, re), pe.R0, pe.V0, T_END).y[:, -1]
    py["j2_z"] = pe.dop(pe.make_accel(mu, re, j2=j2), pe.R0, pe.V0, T_END).y[:, -1]
    py["j2_jgm3_constants_z"] = pe.dop(
        pe.make_accel(3.986004415e14, 6378136.3, j2=-math.sqrt(5.0) * -4.84165374886470e-04),
        pe.R0,
        pe.V0,
        T_END,
    ).y[:, -1]
    py["drag_sph_z"] = pe.dop(pe.make_accel(mu, re, drag=b), pe.R0, pe.V0, T_END).y[:, -1]
    py["drag_geod_z"] = pe.dop(
        pe.make_accel(mu, re, drag=b, altitude="geodetic"), pe.R0, pe.V0, T_END
    ).y[:, -1]

    e2026, e2000 = "01 Jan 2026 00:00:00.000", "01 Jan 2000 12:00:00.000"
    # A1 = TT - 32.184 s + 0.0343817 s (GMAT A1 definition); GMAT ModJulian = JD - 2430000.
    a1_2026 = 31041.5 - (32.184 - 0.0343817) / 86400.0
    jgm3 = str(CONSOLE.parent.parent / "data/gravity/earth/JGM3.cof")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "j2.cof").write_text(cof(3.986004418e14, 6378137.0, C20_EGM2008_TF))
        (tmp / "zero_fileGM415.cof").write_text(cof(3.986004415e14, 6378137.0, 0.0))
        (tmp / "zero_wgs84.cof").write_text(cof(3.986004418e14, 6378137.0, 0.0))
        cases = {
            "j2_jgm3_2026": (
                dict(epoch=e2026, cof_path=jgm3, degree=2, drag=False, flattening=None),
                "j2_jgm3_constants_z",
            ),
            "j2_custom_2026": (
                dict(
                    epoch=e2026, cof_path=str(tmp / "j2.cof"), degree=2, drag=False, flattening=None
                ),
                "j2_z",
            ),
            "j2_custom_2000": (
                dict(
                    epoch=e2000, cof_path=str(tmp / "j2.cof"), degree=2, drag=False, flattening=None
                ),
                "j2_z",
            ),
            "c20zero_fileGM415": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_fileGM415.cof"),
                    degree=2,
                    drag=False,
                    flattening=None,
                ),
                "kepler_gm415",
            ),
            "drag_sph_2026": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=0.0,
                ),
                "drag_sph_z",
            ),
            "drag_geod_2026": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=None,
                ),
                "drag_geod_z",
            ),
            "j2_custom_2026_TOE": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "j2.cof"),
                    degree=2,
                    drag=False,
                    flattening=None,
                    toe_a1mjd=a1_2026,
                ),
                "j2_z",
            ),
            "drag_sph_2026_TOE": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=0.0,
                    toe_a1mjd=a1_2026,
                ),
                "drag_sph_z",
            ),
            "drag_geod_2026_TOE_defaultf": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=None,
                    toe_a1mjd=a1_2026,
                ),
                "drag_geod_z",
            ),
            "drag_geod_2026_TOE_wgs84f": (
                dict(
                    epoch=e2026,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=pe.F_WGS84,
                    toe_a1mjd=a1_2026,
                ),
                "drag_geod_z",
            ),
            "drag_sph_2000": (
                dict(
                    epoch=e2000,
                    cof_path=str(tmp / "zero_wgs84.cof"),
                    degree=0,
                    drag=True,
                    flattening=0.0,
                ),
                "drag_sph_z",
            ),
        }
        for name, (kw, ref) in cases.items():
            y0, y1 = run_case(tmp, name, **kw)
            entry = {
                "python_model": ref,
                "initial_state_echo_diff_m": float(np.linalg.norm(y0[:3] - pe.R0)),
                "final_pos_diff_vs_python_m": float(np.linalg.norm(y1[:3] - py[ref][:3])),
                "final_vel_diff_vs_python_mps": float(np.linalg.norm(y1[3:] - py[ref][3:])),
            }
            if name == "c20zero_fileGM415":
                entry["final_pos_diff_vs_kepler_wgs84_m"] = float(
                    np.linalg.norm(y1[:3] - py["kepler_wgs84"][:3])
                )
            results["cases"][name] = entry
            print(name, json.dumps(entry))
    OUT.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
