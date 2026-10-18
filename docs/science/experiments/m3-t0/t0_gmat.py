# ruff: noqa: E501  -- research spike; long lines are GMAT script text and table rows.
"""M3 T0: executable GMAT R2026a reference configurations (research only; no Proof gate).

What it does:
* builds every M3 configuration by an *additive* splice of the project's own committed M1/M2
  GMAT generators (`tars.validation.gmat.m1_script`, `tars.validation.gmat_m2.m2_script`);
  with perturbations disabled the splice is the identity, which is checked byte for byte
  against the committed M1/M2 scripts and, after running GMAT, their committed reports
  (regression, task §4 D);
* the M3 "exact configuration" form (DR-0024 §3.2, DR-0025 Q8): a generated .cof with the
  pinned GM, a and C20; Exponential drag reading the pinned table (digest checked); explicit
  Earth.Flattening; states exchanged in GMAT's true-of-epoch axes (TOEEq) fixed at the
  scenario epoch, which is how the M3 inertial frame I (DR-0028 J-ax-1: +Z = spin axis by
  assumption, fixed in I) is realised in GMAT;
* runs each configuration in GmatConsole and compares it with the independent spike model
  (t0_model.py, SciPy DOP853, rtol 1e-13);
* DR-0025 Q-G2-1 option (b) feasibility: recovers GMAT's Earth-fixed +Z axis in TOE axes from
  the reported Earth-fixed and TOE positions, then re-runs the spike model with J2 and the
  ellipsoid about that axis (an explicitly labelled diagnostic, not the M3 model);
* measures GMAT's density at both sides of every table boundary (drag/no-drag spacecraft
  pairs propagated 1 ms; rho from the velocity difference), the lower edge and above 1000 km;
* geodetic test points through GMAT's own conversion (Q-G2-7 candidate source 4).

GMAT outputs are written to `gmat_runs/` (scripts with <RUN>/<GMAT> placeholders, reports,
metadata with digests). Nothing is written to toolbox/references (DR-0009).

Usage:
  uv run --no-sync python t0_gmat.py --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" \
      --out t0_gmat_results.json [--cases <name> ...]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import t0_model as m

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "toolbox" / "scripts"))

from tars.sim.runner import run_scenario  # noqa: E402
from tars.sim.scenario import load_scenario  # noqa: E402
from tars.validation import gmat as gmat_m1  # noqa: E402
from tars.validation import gmat_m2, m2  # noqa: E402
from tars.validation.m2_missions import MISSIONS  # noqa: E402
from tars.validation.thresholds import load_thresholds  # noqa: E402

RUNS = HERE / "gmat_runs"
REF = REPO / "toolbox" / "references" / "gmat"
M1_SCENARIO = REPO / "scenarios" / "m1_leo_250km.json"
A1_MINUS_TT_DAYS = (
    0.0343817 - 32.184
) / 86400.0  # GMAT A1 = TAI + 0.0343817 s; TT = TAI + 32.184 s


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------- GMAT runner
@dataclass
class Gmat:
    console: Path

    @property
    def root(self) -> Path:
        return self.console.parent.parent

    def provenance(self) -> dict:
        version = subprocess.run(
            [str(self.console), "--version"],
            cwd=self.console.parent,
            capture_output=True,
            text=True,
        ).stdout
        data = self.root / "data"
        return {
            "gmat_console_sha256": sha(self.console),
            "gmat_version_output": sorted(
                {
                    ln.strip()
                    for ln in version.splitlines()
                    if ln.strip().startswith(("Build Date", "GMAT", "Version"))
                }
            ),
            "atmosphere_table_sha256": sha(
                data / "atmosphere/earth/EarthExponentialAtmosphereData.txt"
            ),
            "eop_file_sha256": sha(data / "planetary_coeff/eopc04_08.62-now"),
            "nutation_file_sha256": sha(data / "planetary_coeff/NUTATION.DAT"),
            "leap_seconds_sha256": sha(data / "time/tai-utc.dat"),
            "host": platform.platform(),
        }

    def run(
        self,
        name: str,
        script: str,
        aux: dict[str, str] | None = None,
        expect_fail: bool = False,
        archive_reports: bool = True,
    ) -> dict:
        """Run `script` (placeholders <RUN>, <GMAT>) and archive script, aux files and reports."""
        RUNS.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for fname, text in (aux or {}).items():
                (tmp / fname).write_text(text)
            text = script.replace("<RUN>", str(tmp)).replace("<GMAT>", str(self.root))
            (tmp / f"{name}.script").write_text(text)
            proc = subprocess.run(
                [str(self.console), "--run", str(tmp / f"{name}.script")],
                cwd=self.console.parent,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            log = proc.stdout + proc.stderr
            failed = proc.returncode != 0 or "Execution Failed" in log
            reports = {p.name: p.read_text() for p in sorted(tmp.glob("*.txt"))}
            (RUNS / f"{name}.script").write_text(script)
            # Identity-regression reports equal committed references: digests only, no copies.
            for fname, body in reports.items() if archive_reports else ():
                (RUNS / f"{name}__{fname}").write_text(body)
            for fname, body in (aux or {}).items():
                (RUNS / f"{name}__{fname}").write_text(body)
            errors = [
                ln.strip().replace(str(tmp), "<RUN>")
                for ln in log.splitlines()
                if any(k in ln for k in ("ERROR", "Exception", "exception", "inside", "Failed"))
            ]
        if failed and not expect_fail:
            raise RuntimeError(f"{name}: GMAT failed: {errors[-5:]}")
        meta = {
            "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
            "reports_sha256": {
                k: hashlib.sha256(v.encode()).hexdigest() for k, v in reports.items()
            },
            "aux_sha256": {
                k: hashlib.sha256(v.encode()).hexdigest() for k, v in (aux or {}).items()
            },
            "failed": failed,
            "errors": errors,
        }
        (RUNS / f"{name}__metadata.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n"
        )
        return {"reports": reports, **meta}


# ------------------------------------------------------------------ M3 configuration splice
@dataclass(frozen=True)
class M3:
    """M3 exact-configuration form. j2/drag False with this object still selects the M3
    form (TOE axes, generated .cof); only `None` (no M3 object) is the identity."""

    j2: bool = False
    drag: bool = False
    flattening: float = 0.0
    cd: float = 2.2
    area_m2: float = 15.0
    dry_mass_kg: float | None = 850.0  # None: keep the base script's mass (M2)
    table: str = "<GMAT>/data/atmosphere/earth/EarthExponentialAtmosphereData.txt"
    toe_epoch_a1mjd: float = 31041.5 + A1_MINUS_TT_DAYS  # 2026-01-01 00:00 TT
    # GMAT holds Earth's precession-nutation matrix for this many seconds (default 60); T0
    # found the default moves the J2 reference by 8 cm along-track. None keeps the default.
    nutation_update_interval_s: float | None = 0.0
    extra_columns: tuple[str, ...] = (
        "Sat.EarthFixed.X",
        "Sat.EarthFixed.Y",
        "Sat.EarthFixed.Z",
        "Sat.Earth.Altitude",
    )


def cof(c20: float) -> str:
    return (
        "COMMENT   1\n"
        "CCCCC  TARS M3 T0 spike: degree-2 zonal only (generated)                 CCCCC\n"
        f"POTFIELD  2  2  1 {m.MU:.14e} {m.A_WGS84:.14e} 1.00000000000000e+00\n"
        f"RECOEF    2  0   {c20:.14e}\n"
        "RECOEF    2  1    0.00000000000000e+00 0.00000000000000e+00\n"
        "RECOEF    2  2    0.00000000000000e+00 0.00000000000000e+00\n"
        "END\n"
    )


def _sub_once(pattern: str, repl: str, text: str) -> str:
    new, n = re.subn(pattern, repl, text, flags=re.M)
    if n != 1:
        raise ValueError(f"splice pattern matched {n} times (expected 1): {pattern}")
    return new


def splice(base: str, p: M3 | None) -> tuple[str, dict[str, str]]:
    """Add the M3 force model to a committed-generator script. p=None returns base unchanged."""
    if p is None:
        return base, {}
    s = _sub_once(
        r"^(GMAT Earth\.EquatorialRadius = .*;)$",
        r"\1\n"
        + (
            f"GMAT Earth.NutationUpdateInterval = {p.nutation_update_interval_s!r};\n"
            if p.nutation_update_interval_s is not None
            else ""
        )
        + f"GMAT Earth.Flattening = {p.flattening!r};\n"
        + "Create CoordinateSystem TOE;\nGMAT TOE.Origin = Earth;\nGMAT TOE.Axes = TOEEq;\n"
        + f"GMAT TOE.Epoch = {p.toe_epoch_a1mjd!r};",
        base,
    )
    s = _sub_once(
        r"^GMAT Sat\.CoordinateSystem = EarthMJ2000Eq;$", "GMAT Sat.CoordinateSystem = TOE;", s
    )
    sc = f"GMAT Sat.DragArea = {p.area_m2!r};"
    if re.search(r"^GMAT Sat\.Cd = .*;$", s, flags=re.M):
        s = _sub_once(r"^GMAT Sat\.Cd = .*;$", f"GMAT Sat.Cd = {p.cd!r};\n{sc}", s)
    else:
        s = _sub_once(
            r"^(GMAT Sat\.VZ = .*;)$",
            r"\1" + f"\nGMAT Sat.Cd = {p.cd!r};\n{sc}\nGMAT Sat.DryMass = {p.dry_mass_kg!r};",
            s,
        )
    fm = re.search(r"^GMAT (\w+)\.PrimaryBodies = \{\};$", s, flags=re.M).group(1)
    grav = (
        f"GMAT {fm}.PrimaryBodies = {{Earth}};\nGMAT {fm}.PointMasses = {{}};\n"
        f"GMAT {fm}.GravityField.Earth.Degree = {2 if p.j2 else 0};\n"
        f"GMAT {fm}.GravityField.Earth.Order = 0;\n"
        f"GMAT {fm}.GravityField.Earth.PotentialFile = '<RUN>/t0.cof';\n"
        f"GMAT {fm}.GravityField.Earth.TideModel = 'None';"
    )
    drag = (
        f"GMAT {fm}.Drag.AtmosphereModel = Exponential;\nGMAT {fm}.Drag.InputFile = '{p.table}';"
        if p.drag
        else f"GMAT {fm}.Drag = None;"
    )
    s = _sub_once(
        rf"^GMAT {fm}\.PrimaryBodies = \{{\}};\nGMAT {fm}\.PointMasses = \{{Earth\}};\nGMAT {fm}\.Drag = None;$",
        grav + "\n" + drag,
        s,
    )
    extra = " " + " ".join(p.extra_columns) if p.extra_columns else ""
    if "Report M1Report" in s:
        s, n = re.subn(
            r"^(\s*Report M1Report [^;]*);$",
            lambda mm: mm.group(1).replace("EarthMJ2000Eq", "TOE") + extra + ";",
            s,
            flags=re.M,
        )
        if n != 2:
            raise ValueError(f"expected 2 M1 Report commands, found {n}")
    else:
        s = _sub_once(
            r"^(GMAT S\.Add = \{)(.*)(\};)$",
            lambda mm: (
                mm.group(1)
                + mm.group(2).replace("EarthMJ2000Eq", "TOE")
                + ", "
                + ", ".join(p.extra_columns)
                + mm.group(3)
            ),
            s,
        )
    s = s.replace(
        "%% Model: point-mass Earth",
        "%% T0 SPIKE (not a reference): M3 exact configuration spliced in.\n%% Base model: point-mass Earth",
        1,
    )
    return s, {"t0.cof": cof(m.C20_EGM2008_TIDE_FREE if p.j2 else 0.0)}


def with_state(script: str, r: np.ndarray, v: np.ndarray) -> str:
    for comp, val in zip(
        ("X", "Y", "Z", "VX", "VY", "VZ"), [*(r / 1000.0), *(v / 1000.0)], strict=True
    ):
        script = _sub_once(
            rf"^GMAT Sat\.{comp} = .*;$", f"GMAT Sat.{comp} = {float(val)!r};", script
        )
    return script


def parse_rows(text: str) -> np.ndarray:
    rows = []
    for ln in text.splitlines():
        parts = ln.split()
        if not parts:
            continue
        try:
            rows.append([float(x) for x in parts])
        except ValueError:
            continue  # header lines
    return np.array(rows)


# ------------------------------------------------------------------------ spike comparisons
def m1_base(report: str = "m1_two_body_report.txt", scenario_path: Path = M1_SCENARIO) -> str:
    return gmat_m1.m1_script(load_scenario(scenario_path), report)


def compare_m1_form(rows: np.ndarray, cfg: m.Config, y0: np.ndarray, mass: float) -> dict:
    """rows: ElapsedS, TTMJD, X..VZ (km, TOE), SMA, ECC, INC, Period, EF X/Y/Z, Altitude."""
    t = rows[:, 0]
    sol = m.dop853(m.rhs(cfg), np.concatenate([y0, [mass]]), float(t[-1]), t_eval=t)
    g = rows[:, 2:8] * 1000.0
    dpos = np.linalg.norm(g[:, :3] - sol.y[:3].T, axis=1)
    dvel = np.linalg.norm(g[:, 3:6] - sol.y[3:6].T, axis=1)
    return {
        "rows": len(t),
        "t_end_s": float(t[-1]),
        "initial_state_echo_m": float(dpos[0]),
        "max_pos_diff_m": float(dpos.max()),
        "final_pos_diff_m": float(dpos[-1]),
        "final_vel_diff_mps": float(dvel[-1]),
        "final_spike_state_m": sol.y[:6, -1].tolist(),
    }


def _axis_basis(t: np.ndarray, t_end: float) -> np.ndarray:
    """[1, s, s^2, cos(w t), sin(w t)]: slow precession/nutation drift plus polar motion,
    which is fixed in the Earth and so circles the celestial pole once per sidereal day."""
    s = t / t_end
    th = m.OMEGA_E * t
    return np.stack([np.ones_like(t), s, s * s, np.cos(th), np.sin(th)], axis=1)


def fit_axis(t: np.ndarray, r_toe: np.ndarray, z_ef: np.ndarray) -> tuple[np.ndarray, float]:
    """Least squares for z_EF = u(t) . r_TOE, u(t) = sum_k c_k basis_k(t) (15 unknowns).

    r_TOE must span three dimensions (two non-coplanar orbits): one orbit plane leaves the
    out-of-plane component of u undetermined."""
    b = _axis_basis(t, float(t.max()))
    a = np.hstack([r_toe * b[:, [k]] for k in range(b.shape[1])])
    coef, *_ = np.linalg.lstsq(a, z_ef, rcond=None)
    resid = z_ef - a @ coef
    return coef.reshape(b.shape[1], 3), float(np.sqrt(np.mean(resid**2)))


def axis_function(coef: np.ndarray, t_end: float):
    c = np.asarray(coef)

    def u(time: float) -> np.ndarray:
        vec = _axis_basis(np.array([float(time)]), t_end)[0] @ c
        return vec / np.linalg.norm(vec)

    return u


def case_axis(g: Gmat) -> dict:
    """DR-0025 Q-G2-1 option (b): GMAT's Earth-fixed +Z axis expressed in TOE axes.

    Two point-mass spacecraft in perpendicular planes (the M1 orbit, and a polar orbit with
    its node on +Y) are propagated together for 53 700 s; their TOE and Earth-fixed
    positions every 60 s determine u(t), the third row of GMAT's TOE -> Earth-fixed rotation."""
    p = M3(j2=False, drag=False, flattening=m.F_WGS84, extra_columns=())
    base, aux = splice(m1_base("<RUN>/m1_two_body_report.txt"), p)
    r_b = np.array([0.0, 6628.137, 0.0])
    v_b = np.array([0.0, 0.0, math.sqrt(m.MU / 6628137.0) / 1000.0])
    extra = "\n".join(
        [
            "Create Spacecraft SatB;",
            "GMAT SatB.DateFormat = TTGregorian;",
            "GMAT SatB.Epoch = '01 Jan 2026 00:00:00.000';",
            "GMAT SatB.CoordinateSystem = TOE;",
            "GMAT SatB.DisplayStateType = Cartesian;",
            *[
                f"GMAT SatB.{c} = {float(x)!r};"
                for c, x in zip(("X", "Y", "Z", "VX", "VY", "VZ"), [*r_b, *v_b], strict=True)
            ],
        ]
    )
    s = _sub_once(r"^(Create Spacecraft Sat;)$", extra + "\n\\1", base)
    s = _sub_once(r"^   Propagate TwoBodyProp\(Sat\) ", "   Propagate TwoBodyProp(Sat, SatB) ", s)
    cols = "ElapsedS Sat.TOE.X Sat.TOE.Y Sat.TOE.Z Sat.EarthFixed.Z SatB.TOE.X SatB.TOE.Y SatB.TOE.Z SatB.EarthFixed.Z SatB.ElapsedSecs"
    s, n = re.subn(
        r"^(\s*)Report M1Report [^;]*;$",
        lambda mm: mm.group(1) + "Report M1Report " + cols + ";",
        s,
        flags=re.M,
    )
    if n != 2:
        raise ValueError("axis probe: report splice")
    res = g.run("axis_probe", s, aux)
    rows = parse_rows(res["reports"]["m1_two_body_report.txt"])
    if not np.allclose(rows[:, 0], rows[:, 9], atol=1e-6):
        raise ValueError("the two spacecraft are not at the same elapsed time")
    t = np.concatenate([rows[:, 0], rows[:, 0]])
    r = np.vstack([rows[:, 1:4], rows[:, 5:8]])
    z = np.concatenate([rows[:, 4], rows[:, 8]])
    coef, rms = fit_axis(t, r, z)
    u = axis_function(coef, float(rows[-1, 0]))
    u0, u1 = u(0.0), u(float(rows[-1, 0]))
    return {
        "coefficients": coef.tolist(),
        "basis": "1, t/t_end, (t/t_end)^2, cos(omega_E t), sin(omega_E t)",
        "polar_motion_circle_radius_arcsec": math.degrees(
            float(np.linalg.norm(coef[3, :2]) + np.linalg.norm(coef[4, :2])) / 2.0
        )
        * 3600.0,
        "t_end_s": float(rows[-1, 0]),
        "fit_rms_residual_m": rms * 1000.0,
        "norm_minus_1_at_start": float(np.linalg.norm(coef[0]) - 1.0),
        "tilt_from_z_at_start_arcsec": math.degrees(math.acos(min(1.0, u0[2]))) * 3600.0,
        "tilt_from_z_at_end_arcsec": math.degrees(math.acos(min(1.0, u1[2]))) * 3600.0,
        "axis_motion_over_run_arcsec": math.degrees(math.acos(min(1.0, float(u0 @ u1)))) * 3600.0,
        "u_start": u0.tolist(),
        "u_end": u1.tolist(),
        "rows": len(rows),
    }


# --------------------------------------------------------------------------------- cases
def case_regression_identity(g: Gmat) -> dict:
    """Perturbations disabled: the splice is the identity; GMAT reproduces committed bytes."""
    out = {}
    base, aux = splice(m1_base(), None)
    committed = (REF / "m1_two_body.script").read_text()
    res = g.run(
        "reg_m1_identity",
        base.replace("'m1_two_body_report.txt'", "'<RUN>/m1_two_body_report.txt'"),
        aux,
        archive_reports=False,
    )
    out["m1"] = {
        "script_identical_to_committed": base == committed,
        "script_sha256": hashlib.sha256(base.encode()).hexdigest(),
        "committed_script_sha256": sha(REF / "m1_two_body.script"),
        "report_identical_to_committed": res["reports"]["m1_two_body_report.txt"]
        == (REF / "m1_two_body_report.txt").read_text(),
    }
    for mission in MISSIONS:
        name = mission.name
        if not (REF / "m2" / f"{name}.script").exists():
            continue
        scn = mission.build()
        predicted = m2.predict_burns(scn, mission.expected)
        text, _ = splice(
            gmat_m2.m2_script(scn, predicted, scn.stop.duration_s, f"{name}_report.txt"), None
        )
        run_text, _ = splice(
            gmat_m2.m2_script(scn, predicted, scn.stop.duration_s, f"<RUN>/{name}_report.txt"), None
        )
        res = g.run(f"reg_{name}_identity", run_text, archive_reports=False)
        out[name] = {
            "script_identical_to_committed": text == (REF / "m2" / f"{name}.script").read_text(),
            "report_identical_to_committed": res["reports"][f"{name}_report.txt"]
            == (REF / "m2" / f"{name}_report.txt").read_text(),
        }
    return out


def case_regression_m3_form(g: Gmat) -> dict:
    """Perturbations disabled in the M3 exact-configuration form (TOE axes, generated degree-0
    .cof): judged by the approved, unchanged M1 GMAT gates (proof/thresholds/m1.json)."""
    p = M3(j2=False, drag=False, flattening=0.0, extra_columns=())
    s, aux = splice(m1_base("<RUN>/m1_two_body_report.txt"), p)
    res = g.run("reg_m1_m3form", s, aux)
    text = res["reports"]["m1_two_body_report.txt"]
    # The parser accepts only the M1 column names; the TOE columns are the M3 frame I here.
    relabelled = text.replace("Sat.TOE.", "Sat.EarthMJ2000Eq.")
    scenario = load_scenario(M1_SCENARIO)
    run = run_scenario(scenario)
    metrics = gmat_m1.compare(gmat_m1.parse_report(relabelled), run.samples, scenario)
    gates = load_thresholds().for_validator("gmat_reference")
    checks = {
        k: {"value": metrics[k], "limit": gates[k], "pass": metrics[k] <= gates[k]}
        for k in gates
        if k in metrics
    }
    return {
        "metrics": metrics,
        "gates_m1_json": checks,
        "all_applicable_gates_pass": all(c["pass"] for c in checks.values()),
    }


TRAJECTORY_CASES = {
    # name: (M3 spec, spike config, initial-state override or None, description)
    "j2": (M3(j2=True), m.Config(j2=m.J2_FROM_C20), None, "J2 only, M1 orbit"),
    "j2_default_nutation_interval": (
        M3(j2=True, nutation_update_interval_s=None),
        m.Config(j2=m.J2_FROM_C20),
        None,
        "J2 only, M1 orbit, GMAT's default Earth.NutationUpdateInterval (60 s): evidence only",
    ),
    "drag1_sph": (
        M3(drag=True, flattening=0.0, table="<RUN>/one_band_250.txt"),
        m.Config(
            drag=m.Drag(2.2, 15.0, table=m.ONE_BAND_250, height="spherical", below="extrapolate")
        ),
        None,
        "drag only, one-band (250 km row) table, spherical height (smooth configuration)",
    ),
    "drag_sph": (
        M3(drag=True, flattening=0.0),
        m.Config(drag=m.Drag(2.2, 15.0, height="spherical")),
        None,
        "drag only, full table, spherical height",
    ),
    "drag_geod": (
        M3(drag=True, flattening=m.F_WGS84),
        m.Config(drag=m.Drag(2.2, 15.0)),
        None,
        "drag only, full table, geodetic height (WGS 84)",
    ),
    "j2_drag_geod": (
        M3(j2=True, drag=True, flattening=m.F_WGS84),
        m.Config(j2=m.J2_FROM_C20, drag=m.Drag(2.2, 15.0)),
        None,
        "J2 + drag, geodetic: the approved M3 physics on the M1 orbit",
    ),
    "j2_drag_geod_i97": (
        M3(j2=True, drag=True, flattening=m.F_WGS84),
        m.Config(j2=m.J2_FROM_C20, drag=m.Drag(2.2, 15.0)),
        m.circular_state(250_000.0, 97.0),
        "J2 + drag, geodetic, circular 250 km, i = 97 deg (retrograde: node advances)",
    ),
    "j2_drag_geod_ecc": (
        M3(j2=True, drag=True, flattening=m.F_WGS84),
        m.Config(j2=m.J2_FROM_C20, drag=m.Drag(2.2, 15.0)),
        m.perigee_state(250_000.0, 800_000.0, 51.6),
        "J2 + drag, geodetic, 250 x 800 km, i = 51.6 deg (crosses 12 band boundaries)",
    ),
}


def case_trajectories(g: Gmat, axis: dict) -> dict:
    out = {}
    u = axis_function(axis["coefficients"], axis["t_end_s"])
    r0, v0 = (np.array(x, dtype=float) for x in gmat_m1.initial_state(load_scenario(M1_SCENARIO)))
    for name, (p, cfg, state, desc) in TRAJECTORY_CASES.items():
        s, aux = splice(m1_base("<RUN>/m1_two_body_report.txt"), p)
        if state is not None:
            s = with_state(s, *state)
        if "one_band" in p.table:
            aux["one_band_250.txt"] = "250.0, 7.248e-11, 45.546\n"
        res = g.run(f"traj_{name}", s, aux)
        rows = parse_rows(res["reports"]["m1_two_body_report.txt"])
        y0 = np.concatenate(state) if state is not None else np.concatenate([r0, v0])
        rec = {"description": desc, "vs_spike_J_ax_1": compare_m1_form(rows, cfg, y0, 850.0)}
        diag = replace(cfg, axis_fn=u)
        rec["vs_spike_with_gmat_axis_DIAGNOSTIC"] = compare_m1_form(rows, diag, y0, 850.0)
        if cfg.drag is not None and cfg.drag.height == "geodetic":
            rep = replace(diag, drag=replace(cfg.drag, height="geodetic_gmat_replica"))
            rec["vs_spike_with_gmat_axis_and_gmat_height_rule_DIAGNOSTIC"] = compare_m1_form(
                rows, rep, y0, 850.0
            )
        out[name] = rec
        print(
            name,
            json.dumps(
                {k: v.get("final_pos_diff_m") for k, v in rec.items() if isinstance(v, dict)}
            ),
            flush=True,
        )
    return out


def thrust_m2(burn_start: float, burn_end: float, force: float, isp: float):
    g0 = 9.80665

    def thrust(t, r, v, mass):
        if burn_start <= t < burn_end:
            return force / mass * v / np.linalg.norm(v), -force / (isp * g0)
        return np.zeros(3), 0.0

    return thrust


def case_burn(g: Gmat) -> dict:
    """J2 + drag + the M2 prograde burn (M2 generator spliced; mass from the M2 tank)."""
    mission = next(x for x in MISSIONS if x.name == "m2_prograde_burn")
    scn = mission.build()
    predicted = m2.predict_burns(scn, mission.expected)
    base = gmat_m2.m2_script(
        scn, predicted, scn.stop.duration_s, "<RUN>/m2_prograde_burn_report.txt"
    )
    p = M3(j2=True, drag=True, flattening=m.F_WGS84, dry_mass_kg=None)
    s, aux = splice(base, p)
    res = g.run("traj_j2_drag_geod_burn", s, aux)
    rows = parse_rows(res["reports"]["m2_prograde_burn_report.txt"])
    # columns: ARC, A1MJD, X..VZ (TOE, km), TotalMass, EF X/Y/Z, Altitude
    a1 = rows[:, 1]
    t = np.round((a1 - a1[0]) * 86400.0, 6)
    cfg = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(2.2, 15.0))
    burn = predicted[0]
    start = float(burn.start_t if hasattr(burn, "start_t") else 600.0)
    end = start + 77.3
    thrust = thrust_m2(start, end, 490.0, 312.0)
    f = m.rhs(cfg, thrust)
    y = np.concatenate([rows[0, 2:5] * 1000.0, rows[0, 5:8] * 1000.0, [1300.0]])
    states = {}
    seg_edges = [0.0, start, end, float(t[-1])]
    for a, b in itertools.pairwise(seg_edges):
        grid = t[(t >= a) & (t <= b)]
        sol = m.dop853(lambda tt, yy, a=a: f(tt + a, yy), y, b - a, t_eval=grid - a)
        for k, tk in enumerate(grid):
            states[float(tk)] = sol.y[:, k]
        y = (
            sol.y[:, -1]
            if sol.t[-1] == b - a
            else m.dop853(lambda tt, yy, a=a: f(tt + a, yy), y, b - a).y[:, -1]
        )
    dpos = [np.linalg.norm(rows[i, 2:5] * 1000.0 - states[float(tk)][:3]) for i, tk in enumerate(t)]
    dmass = [abs(rows[i, 8] - states[float(tk)][6]) for i, tk in enumerate(t)]
    return {
        "description": "M2 prograde burn (490 N, 312 s, 77.3 s at t = 600 s; 1000 + 300 kg) with J2 + drag "
        "geodetic, A 15 m^2 (spike test value), Cd 2.2",
        "burn_window_s": [start, end],
        "rows": len(t),
        "max_pos_diff_m": float(max(dpos)),
        "final_pos_diff_m": float(dpos[-1]),
        "max_mass_diff_kg": float(max(dmass)),
        "final_mass_gmat_kg": float(rows[-1, 8]),
    }


def case_decay(g: Gmat) -> dict:
    """180 km circular decay to a GMAT stop at geodetic altitude 80 km (a SPIKE test value)."""
    p = M3(j2=True, drag=True, flattening=m.F_WGS84, extra_columns=())
    s, aux = splice(m1_base("<RUN>/m1_two_body_report.txt"), p)
    r0, v0 = m.circular_state(180_000.0, 51.6)
    s = with_state(s, r0, v0)
    s = _sub_once(
        r"^For I = 1:\d+;\n(?:.*\n)*?EndFor;\n",
        "Propagate TwoBodyProp(Sat) {Sat.Earth.Altitude = 80.0};\nReport M1Report Sat.ElapsedSecs Sat.TTModJulian Sat.TOE.X Sat.TOE.Y Sat.TOE.Z Sat.TOE.VX Sat.TOE.VY Sat.TOE.VZ Sat.Earth.SMA Sat.Earth.ECC Sat.TOE.INC Sat.Earth.OrbitPeriod Sat.Earth.Altitude;\n",
        s,
    )
    res = g.run("traj_decay_to_80km", s, aux)
    last = [ln for ln in res["reports"]["m1_two_body_report.txt"].splitlines() if ln.strip()][-1]
    final = np.array([float(x) for x in last.split()])
    t_gmat, h_gmat = float(final[0]), float(final[-1]) * 1000.0
    cfg = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(2.2, 15.0))

    def ev(t, y):
        return m.geodetic_iterative(y[:3])[1] - 80_000.0

    ev.terminal, ev.direction = True, -1
    sol = m.dop853(m.rhs(cfg), np.concatenate([r0, v0, [850.0]]), 2 * 86400.0, events=ev)
    t_spike = float(sol.t_events[0][0])
    return {
        "gmat_stop_elapsed_s": t_gmat,
        "gmat_altitude_at_stop_m": h_gmat,
        "spike_crossing_s": t_spike,
        "gmat_minus_spike_s": t_gmat - t_spike,
        "final_pos_diff_m": float(np.linalg.norm(final[2:5] * 1000.0 - sol.y_events[0][0][:3])),
    }


def _probe_spacecraft(
    name: str, r_ef_km: list[float], v_ef_kms: list[float], area: float, mass: float
) -> str:
    lines = [
        f"Create Spacecraft {name};",
        f"GMAT {name}.DateFormat = TTGregorian;",
        f"GMAT {name}.Epoch = '01 Jan 2026 00:00:00.000';",
        f"GMAT {name}.CoordinateSystem = EarthFixed;",
        f"GMAT {name}.DisplayStateType = Cartesian;",
    ]
    for comp, val in zip(("X", "Y", "Z", "VX", "VY", "VZ"), [*r_ef_km, *v_ef_kms], strict=True):
        lines.append(f"GMAT {name}.{comp} = {float(val)!r};")
    lines += [
        f"GMAT {name}.Cd = 2.2;",
        f"GMAT {name}.DragArea = {area!r};",
        f"GMAT {name}.DryMass = {mass!r};",
    ]
    return "\n".join(lines)


def case_density_probes(g: Gmat) -> dict:
    """GMAT's density at both sides of every boundary, at the bases, below 0 and above 1000 km.

    Pairs of spacecraft at the same Earth-fixed equatorial state (geodetic height = x - a
    exactly), one with Exponential drag and one without, are propagated TAU seconds; then
    rho = |dv_D - dv_N| / (0.5 Cd (A/m) v_rel^2 TAU). A/m gives ~1 m/s^2 of drag at every height.
    """
    tau = 1.0e-3
    speed = 7.0  # km/s, Earth-fixed (atmosphere-relative) eastward
    heights_km = [0.5]
    for b in m.TABLE[1:]:
        heights_km += [b.base_km - 1.0, b.base_km, b.base_km + 1.0]
    heights_km += [1100.0, 1500.0, 2000.0]
    body, cmds = [], []
    plan = []
    for i, h in enumerate(heights_km):
        rho_expect = m.density(h * 1000.0)
        am = 1.0 / (0.5 * rho_expect * 2.2 * (speed * 1000.0) ** 2)  # m^2/kg for ~1 m/s^2
        mass = 1.0
        x = (m.A_WGS84 / 1000.0) + h
        for tag in ("D", "N"):
            body.append(_probe_spacecraft(f"P{i}{tag}", [x, 0.0, 0.0], [0.0, speed, 0.0], am, mass))
        plan.append((h, am))
        cmds.append(f"Propagate PD(P{i}D) {{P{i}D.ElapsedSecs = {tau!r}}};")
        cmds.append(f"Propagate PN(P{i}N) {{P{i}N.ElapsedSecs = {tau!r}}};")
        cmds.append(f"K = {i};")
        cmds.append(
            f"Report R K P{i}D.EarthMJ2000Eq.VX P{i}D.EarthMJ2000Eq.VY P{i}D.EarthMJ2000Eq.VZ P{i}N.EarthMJ2000Eq.VX P{i}N.EarthMJ2000Eq.VY P{i}N.EarthMJ2000Eq.VZ P{i}D.Earth.Altitude;"
        )
    fm = []
    for nm, drag in (("FMD", True), ("FMN", False)):
        fm += [
            f"Create ForceModel {nm};",
            f"GMAT {nm}.CentralBody = Earth;",
            f"GMAT {nm}.PrimaryBodies = {{Earth}};",
            f"GMAT {nm}.GravityField.Earth.Degree = 0;",
            f"GMAT {nm}.GravityField.Earth.Order = 0;",
            f"GMAT {nm}.GravityField.Earth.PotentialFile = '<RUN>/t0.cof';",
            f"GMAT {nm}.SRP = Off;",
        ]
        fm += (
            [
                f"GMAT {nm}.Drag.AtmosphereModel = Exponential;",
                f"GMAT {nm}.Drag.InputFile = '<GMAT>/data/atmosphere/earth/EarthExponentialAtmosphereData.txt';",
            ]
            if drag
            else [f"GMAT {nm}.Drag = None;"]
        )
    props = []
    for nm, f in (("PD", "FMD"), ("PN", "FMN")):
        props += [
            f"Create Propagator {nm};",
            f"GMAT {nm}.FM = {f};",
            f"GMAT {nm}.Type = PrinceDormand78;",
            f"GMAT {nm}.InitialStepSize = {tau!r};",
            f"GMAT {nm}.Accuracy = 1e-13;",
            f"GMAT {nm}.MinStep = 0;",
            f"GMAT {nm}.MaxStep = {tau!r};",
        ]
    script = (
        "\n".join(
            [
                "GMAT Earth.Mu = 398600.4418;",
                "GMAT Earth.EquatorialRadius = 6378.137;",
                f"GMAT Earth.Flattening = {m.F_WGS84!r};",
                *body,
                *fm,
                *props,
                "Create ReportFile R;",
                "GMAT R.Filename = '<RUN>/probe.txt';",
                "GMAT R.Precision = 17;",
                "GMAT R.WriteHeaders = false;",
                "Create Variable K;",
                "BeginMissionSequence;",
                *cmds,
            ]
        )
        + "\n"
    )
    res = g.run("density_probes", script, {"t0.cof": cof(0.0)})
    rows = parse_rows(res["reports"]["probe.txt"])
    out = []
    for (h, am), row in zip(plan, rows, strict=True):
        dv = (row[1:4] - row[4:7]) * 1000.0
        rho = float(np.linalg.norm(dv)) / (0.5 * 2.2 * am * (speed * 1000.0) ** 2 * tau)
        k = m.band_index(h)
        hyp = {"spike_band_rule": m.density(h * 1000.0)}
        if k > 0:
            lo = m.TABLE[k - 1]
            hyp["lower_band_formula"] = lo.rho0 * math.exp(-(h - lo.base_km) / lo.scale_km)
        out.append(
            {
                "h_km": h,
                "gmat_altitude_km": float(row[7]),
                "gmat_rho": rho,
                "rel_diff_vs_spike_band_rule": rho / hyp["spike_band_rule"] - 1.0,
                "rel_diff_vs_lower_band_formula": (rho / hyp["lower_band_formula"] - 1.0)
                if k > 0
                else None,
            }
        )
    # Below the lower edge: GMAT's behaviour (expected to fail; measured, not assumed).
    below = script.replace(
        "GMAT P0D.X = " + repr((m.A_WGS84 / 1000.0) + 0.5),
        "GMAT P0D.X = " + repr((m.A_WGS84 / 1000.0) - 0.001),
    )
    res_b = g.run("density_probe_below_zero", below, {"t0.cof": cof(0.0)}, expect_fail=True)
    return {
        "tau_s": tau,
        "method": "drag/no-drag pair, equatorial Earth-fixed state, |v_rel| = 7 km/s eastward",
        "probes": out,
        "max_abs_rel_diff_vs_spike_band_rule": max(
            abs(p["rel_diff_vs_spike_band_rule"]) for p in out
        ),
        "below_zero_probe": {"failed": res_b["failed"], "errors": res_b["errors"][-3:]},
    }


def case_geodetic_points(g: Gmat) -> dict:
    """Q-G2-7 source 4: GMAT's geodetic altitude/latitude for forward-constructed points."""
    pts = []
    for lat_d in (-89.999999, -51.6, 0.0, 33.3, 45.0, 60.0, 80.0, 89.999999, 90.0):
        for h in (0.0, 100_000.0, 250_000.0, 1_000_000.0):
            pts.append((lat_d, 44.4, h))
    body = [_probe_spacecraft("G", [7000.0, 0.0, 0.0], [0.0, 7.0, 0.0], 1.0, 1.0)]
    cmds = []
    for i, (lat_d, lon_d, h) in enumerate(pts):
        r = m.geodetic_to_cartesian(math.radians(lat_d), math.radians(lon_d), h) / 1000.0
        cmds += [
            f"G.X = {float(r[0])!r};",
            f"G.Y = {float(r[1])!r};",
            f"G.Z = {float(r[2])!r};",
            f"K = {i};",
            "Report R K G.Earth.Altitude G.Earth.Latitude G.EarthFixed.X G.EarthFixed.Y G.EarthFixed.Z;",
        ]
    script = (
        "\n".join(
            [
                "GMAT Earth.Mu = 398600.4418;",
                "GMAT Earth.EquatorialRadius = 6378.137;",
                f"GMAT Earth.Flattening = {m.F_WGS84!r};",
                *body,
                "Create ReportFile R;",
                "GMAT R.Filename = '<RUN>/geod.txt';",
                "GMAT R.Precision = 17;",
                "GMAT R.WriteHeaders = false;",
                "Create Variable K;",
                "BeginMissionSequence;",
                *cmds,
            ]
        )
        + "\n"
    )
    res = g.run("geodetic_points", script)
    rows = parse_rows(res["reports"]["geod.txt"])
    out = []
    for (lat_d, lon_d, h), row in zip(pts, rows, strict=True):
        out.append(
            {
                "lat_deg": lat_d,
                "h_m": h,
                "gmat_h_minus_exact_m": float(row[1]) * 1000.0 - h,
                "gmat_lat_minus_exact_deg": float(row[2]) - lat_d,
                "ef_echo_m": float(
                    np.linalg.norm(
                        row[3:6] * 1000.0
                        - m.geodetic_to_cartesian(math.radians(lat_d), math.radians(lon_d), h)
                    )
                ),
            }
        )
    return {"points": out, "max_abs_h_err_m": max(abs(p["gmat_h_minus_exact_m"]) for p in out)}


CASES = {
    "axis": case_axis,
    "regression_identity": case_regression_identity,
    "regression_m3_form": case_regression_m3_form,
    "trajectories": case_trajectories,
    "burn": case_burn,
    "decay": case_decay,
    "density_probes": case_density_probes,
    "geodetic_points": case_geodetic_points,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gmat-console", required=True, type=Path)
    ap.add_argument("--cases", nargs="*", default=list(CASES))
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    g = Gmat(args.gmat_console.expanduser())
    table = g.root / "data/atmosphere/earth/EarthExponentialAtmosphereData.txt"
    if sha(table) != m.TABLE_SHA256:
        raise SystemExit("GMAT's atmosphere table does not match the pinned digest (DR-0027 B-1)")
    results = json.loads(args.out.read_text()) if args.out.exists() else {}
    results["provenance"] = g.provenance()
    for name in args.cases:
        print(f"== {name}", flush=True)
        fn = CASES[name]
        results[name] = fn(g, results["axis"]) if name == "trajectories" else fn(g)
        args.out.write_text(json.dumps(results, indent=2, sort_keys=True, default=float) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in results.items()
                if k in ("regression_identity", "regression_m3_form")
            },
            indent=1,
            default=float,
        )
    )


if __name__ == "__main__":
    main()
