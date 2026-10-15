"""REV-012 investigation harness: GMAT epoch bookkeeping and stop-time quantization.

Research only (VAL-0010); not project code and not a Proof gate.

Subcommands:
  generate                      write the GMAT scripts into scripts/
  run --gmat-console PATH       run every script with GmatConsole, store reports/
  reproduce --gmat-console PATH re-run the committed M1 reference and M2 probe scripts
                                and compare their reports byte-for-byte
  analyze                       compute results.json from the committed reports

The analysis tests two mechanisms read in the GMAT R2026a source (see README.md):
  M-a  Propagate keeps the spacecraft epoch as a double A1 Modified Julian Date and sets
       it to baseEpoch + elapsed/86400 at the end of every Propagate command, so each
       command adds one rounding of the epoch.
  M-b  For a time stopping condition the final step is
       dt = goal - ElapsedSecs(previous step), where ElapsedSecs is evaluated from that
       double epoch, and dt is then rounded to a whole microsecond (TIME_ROUNDOFF).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from tars.astro import kepler
from tars.sim.scenario import load_scenario
from tars.validation.gmat import parse_report

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCRIPTS = HERE / "scripts"
REPORTS = HERE / "reports"
SCENARIO = REPO / "scenarios" / "m1_leo_250km.json"
M1_SCRIPT = REPO / "toolbox" / "references" / "gmat" / "m1_two_body.script"
M1_REPORT = REPO / "toolbox" / "references" / "gmat" / "m1_two_body_report.txt"
PROBE_DIR = REPO / "docs" / "science" / "experiments" / "m2-planning"
DEFAULT_GMAT = Path.home() / "Applications" / "GMAT R2026a" / "bin" / "GmatConsole"

DAY = 86400.0
TIME_ROUNDOFF = 1.0e-6  # GMAT src/base/command/PropagationEnabledCommand.hpp
TT_MINUS_A1 = 32.184 - 0.0343817  # s; TT = TAI + 32.184 s, A.1 = TAI + 0.0343817 s

# Spacecraft of the M2 planning probe (VAL-0009).
F, ISP, G0, DRY, PROP = 490.0, 312.0, 9.80665, 1000.0, 300.0
MDOT = F / (ISP * G0)
T_IGN = 600.0
T_END = 53_700.0
BURN_DURATIONS = (1.0, 10.0, 17.3, 60.0, 77.3, 120.7, 333.3)

# GMAT R2026a accepts ModJulian epochs in [6116.0, 58127.5]. These span four binades,
# so one ulp of the epoch spans 7.9e-8 s to 6.3e-7 s.
EPOCHS = {
    "a7000": ("A1ModJulian", "7000.5"),
    "a12000": ("A1ModJulian", "12000.5"),
    "a31041": ("A1ModJulian", "31041.5"),
    "a50000": ("A1ModJulian", "50000.5"),
    "m1tt": ("TTGregorian", "01 Jan 2026 00:00:00.000"),  # the M1 / probe epoch
}

STATE = (
    "GMAT Sat.X = 6628.137;\n"
    "GMAT Sat.Y = 0.0;\n"
    "GMAT Sat.Z = 0.0;\n"
    "GMAT Sat.VX = 0.0;\n"
    "GMAT Sat.VY = 4.8169050670943;\n"
    "GMAT Sat.VZ = 6.077421678863729;\n"
)
XYZ = (
    "Sat.EarthMJ2000Eq.X Sat.EarthMJ2000Eq.Y Sat.EarthMJ2000Eq.Z "
    "Sat.EarthMJ2000Eq.VX Sat.EarthMJ2000Eq.VY Sat.EarthMJ2000Eq.VZ"
)

# Segment cases: name -> (epoch key, segment seconds, segments per report row, rows)
SEGMENT_CASES: dict[str, tuple[str, float, int, int]] = {}
for _key in EPOCHS:
    SEGMENT_CASES[f"seg60_{_key}"] = (_key, 60.0, 1, 895)  # the M1 pattern
    SEGMENT_CASES[f"single_{_key}"] = (_key, 53_700.0, 1, 1)  # one Propagate command
SEGMENT_CASES["seg10x6_m1tt"] = ("m1tt", 10.0, 6, 895)  # 5370 commands
SEGMENT_CASES["seg300_m1tt"] = ("m1tt", 300.0, 1, 179)

# Burn cases: name -> (epoch key, burn seconds, (initial step, max step) of the burn
# propagator, (initial step, max step) of the coast propagator)
PROBE_STEPS = (10.0, 60.0)  # the VAL-0009 probe used these for every phase
BURN_CASES: dict[str, tuple[str, float, tuple[float, float], tuple[float, float]]] = {}
for _key in EPOCHS:
    for _t in BURN_DURATIONS:
        BURN_CASES[f"burn_{_key}_{_t:g}"] = (_key, _t, PROBE_STEPS, PROBE_STEPS)
# Methodology variants. "burnstep": ask for one natural step over the whole burn.
BURN_CASES["burnstep_m1tt_77.3"] = ("m1tt", 77.3, (77.3, 77.3), PROBE_STEPS)
BURN_CASES["burnstep_m1tt_60"] = ("m1tt", 60.0, (60.0, 60.0), PROBE_STEPS)
# "aligned": every step before a stop is MaxStep-limited and lands on the microsecond grid.
for _key in ("a7000", "a50000", "m1tt"):
    for _t in (77.3, 120.7, 333.3):
        BURN_CASES[f"aligned_{_key}_{_t:g}"] = (_key, _t, (1.0, 1.0), (60.0, 60.0))


def _header(epoch_key: str, burn: bool) -> str:
    fmt, epoch = EPOCHS[epoch_key]
    text = (
        "GMAT Earth.Mu = 398600.4418;\n"
        "GMAT Earth.EquatorialRadius = 6378.137;\n"
        "Create Spacecraft Sat;\n"
        f"GMAT Sat.DateFormat = {fmt};\n"
        f"GMAT Sat.Epoch = '{epoch}';\n"
        "GMAT Sat.CoordinateSystem = EarthMJ2000Eq;\n"
        "GMAT Sat.DisplayStateType = Cartesian;\n" + STATE
    )
    if burn:
        text += (
            f"GMAT Sat.DryMass = {DRY:g};\n"
            "GMAT Sat.Tanks = {Tank1};\n"
            "GMAT Sat.Thrusters = {Eng1};\n"
            "Create ChemicalTank Tank1;\n"
            "GMAT Tank1.AllowNegativeFuelMass = false;\n"
            f"GMAT Tank1.FuelMass = {PROP:g};\n"
            "Create ChemicalThruster Eng1;\n"
            "GMAT Eng1.CoordinateSystem = Local;\n"
            "GMAT Eng1.Origin = Earth;\n"
            "GMAT Eng1.Axes = VNB;\n"
            "GMAT Eng1.ThrustDirection1 = 1;\n"
            "GMAT Eng1.ThrustDirection2 = 0;\n"
            "GMAT Eng1.ThrustDirection3 = 0;\n"
            "GMAT Eng1.DutyCycle = 1;\n"
            "GMAT Eng1.ThrustScaleFactor = 1;\n"
            "GMAT Eng1.DecrementMass = true;\n"
            "GMAT Eng1.Tank = {Tank1};\n"
            "GMAT Eng1.MixRatio = [1];\n"
            f"GMAT Eng1.GravitationalAccel = {G0!r};\n"
            f"GMAT Eng1.C1 = {F:g};\n"
            f"GMAT Eng1.K1 = {ISP:g};\n"
            "Create FiniteBurn FB;\n"
            "GMAT FB.Thrusters = {Eng1};\n"
        )
    text += (
        "Create ForceModel FM;\n"
        "GMAT FM.CentralBody = Earth;\n"
        "GMAT FM.PrimaryBodies = {};\n"
        "GMAT FM.PointMasses = {Earth};\n"
        "GMAT FM.Drag = None;\n"
        "GMAT FM.SRP = Off;\n"
        "GMAT FM.RelativisticCorrection = Off;\n"
        "GMAT FM.ErrorControl = RSSStep;\n"
    )
    return text


def _propagator(name: str, initial: float, max_step: float) -> str:
    return (
        f"Create Propagator {name};\n"
        f"GMAT {name}.FM = FM;\n"
        f"GMAT {name}.Type = PrinceDormand78;\n"
        f"GMAT {name}.InitialStepSize = {initial!r};\n"
        f"GMAT {name}.Accuracy = 1e-13;\n"
        f"GMAT {name}.MinStep = 0;\n"
        f"GMAT {name}.MaxStep = {max_step!r};\n"
        f"GMAT {name}.MaxStepAttempts = 50;\n"
        f"GMAT {name}.StopIfAccuracyIsViolated = true;\n"
    )


def _report_file(name: str, placeholder: str, add: str | None = None) -> str:
    text = (
        f"Create ReportFile {name};\n"
        f"GMAT {name}.Filename = '{placeholder}';\n"
        f"GMAT {name}.Precision = 17;\n"
        f"GMAT {name}.WriteHeaders = false;\n"
        f"GMAT {name}.LeftJustify = On;\n"
        f"GMAT {name}.ZeroFill = Off;\n"
        f"GMAT {name}.FixedWidth = true;\n"
        f"GMAT {name}.Delimiter = ' ';\n"
        f"GMAT {name}.ColumnWidth = 26;\n"
    )
    if add:
        text += f"GMAT {name}.Add = {{{add}}};\n"
    return text


STATE_COLUMNS = ["x", "y", "z", "vx", "vy", "vz"]
SEG_COLUMNS = ["label_s", "elapsed_secs", "a1mjd", "da_days", "tt_minus_a1_s", *STATE_COLUMNS]
BURN_COLUMNS = ["a1mjd", "elapsed_secs", *STATE_COLUMNS, "mass"]
STEP_COLUMNS = ["a1mjd", "mass"]


def segment_script(name: str) -> str:
    epoch_key, h, inner, rows = SEGMENT_CASES[name]
    seg_row = "ElapsedS Sat.ElapsedSecs Sat.A1ModJulian DA OFFTT " + XYZ
    body = (
        f"%% REV-012 segment case {name}: {rows} rows x {inner} x Propagate {h!r} s.\n"
        + _header(epoch_key, burn=False)
        + _propagator("P", 60.0, 60.0)  # M1 propagator settings
        + _report_file("R", "__OUT__")
        + "Create Variable I J ElapsedS A0 DA OFFTT;\n"
        "BeginMissionSequence;\n"
        "A0 = Sat.A1ModJulian;\n"
        "ElapsedS = 0;\n"
        "DA = 0;\n"
        "OFFTT = (Sat.TTModJulian - Sat.A1ModJulian) * 86400;\n"
        f"Report R {seg_row};\n"
        f"For I = 1:{rows};\n"
    )
    prop = f"Propagate P(Sat) {{Sat.ElapsedSecs = {h!r}}};\n"
    if inner > 1:
        body += f"   For J = 1:{inner};\n      {prop}   EndFor;\n"
    else:
        body += f"   {prop}"
    body += (
        f"   ElapsedS = {h * inner!r} * I;\n"
        "   DA = Sat.A1ModJulian - A0;\n"
        "   OFFTT = (Sat.TTModJulian - Sat.A1ModJulian) * 86400;\n"
        f"   Report R {seg_row};\n"
        "EndFor;\n"
    )
    return body


def burn_script(name: str) -> str:
    epoch_key, t_burn, burn_steps, coast_steps = BURN_CASES[name]
    row = "Sat.A1ModJulian Sat.ElapsedSecs " + XYZ + " Sat.TotalMass"
    variant = burn_steps != coast_steps
    text = (
        f"%% REV-012 burn case {name}: coast {T_IGN!r} s, burn {t_burn!r} s, "
        f"coast to {T_END!r} s.\n"
        + _header(epoch_key, burn=True)
        + _propagator("P", *coast_steps)
        + (_propagator("PB", *burn_steps) if variant else "")
        + _report_file("R", "__OUT__")
        + _report_file("S", "__STEPS__", add="Sat.A1ModJulian, Sat.TotalMass")
        + "BeginMissionSequence;\n"
        "Toggle S Off;\n"
        f"Report R {row};\n"
        f"Propagate P(Sat) {{Sat.ElapsedSecs = {T_IGN!r}}};\n"
        f"Report R {row};\n"
        "Toggle S On;\n"
        "BeginFiniteBurn FB(Sat);\n"
        f"Propagate {'PB' if variant else 'P'}(Sat) {{Sat.ElapsedSecs = {t_burn!r}}};\n"
        "EndFiniteBurn FB(Sat);\n"
        "Toggle S Off;\n"
        f"Report R {row};\n"
        f"Propagate P(Sat) {{Sat.ElapsedSecs = {T_END - T_IGN - t_burn!r}}};\n"
        f"Report R {row};\n"
    )
    return text


# Streamed grid: one Propagate command, InitialStepSize = MaxStep = 60 s, rows written by a
# ReportFile subscriber at every integrator step (candidate methodology, not M1's).
STREAM_CASES = {f"stream60_{k}": k for k in ("a7000", "a50000", "m1tt")}
STREAM_COLUMNS = ["a1mjd", *STATE_COLUMNS]


def stream_script(name: str) -> str:
    return (
        f"%% REV-012 stream case {name}: one Propagate {T_END!r} s, a row per 60 s step.\n"
        + _header(STREAM_CASES[name], burn=False)
        + _propagator("P", 60.0, 60.0)
        + _report_file("R", "__OUT__", add="Sat.A1ModJulian, " + XYZ.replace(" ", ", "))
        + "BeginMissionSequence;\n"
        f"Propagate P(Sat) {{Sat.ElapsedSecs = {T_END!r}}};\n"
    )


def cmd_generate(_: argparse.Namespace) -> None:
    SCRIPTS.mkdir(exist_ok=True)
    for name in SEGMENT_CASES:
        (SCRIPTS / f"{name}.script").write_text(segment_script(name))
    for name in BURN_CASES:
        (SCRIPTS / f"{name}.script").write_text(burn_script(name))
    for name in STREAM_CASES:
        (SCRIPTS / f"{name}.script").write_text(stream_script(name))
    total = len(SEGMENT_CASES) + len(BURN_CASES) + len(STREAM_CASES)
    print(f"wrote {total} scripts to {SCRIPTS}")


def _run_gmat(console: Path, script_text: str, outputs: dict[str, Path]) -> str:
    """Run one script; placeholder -> destination. Returns the console log."""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        produced = {}
        for placeholder in outputs:
            produced[placeholder] = tmpdir / f"{placeholder.strip('_').lower()}.txt"
            script_text = script_text.replace(placeholder, str(produced[placeholder]))
        script = tmpdir / "case.script"
        script.write_text(script_text)
        proc = subprocess.run(
            [str(console), "--run", str(script)],
            cwd=console.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        log = proc.stdout + proc.stderr
        if proc.returncode != 0 or "Execution Failed" in log:
            raise RuntimeError(f"GMAT failed (rc={proc.returncode}):\n{log[-2000:]}")
        for placeholder, dest in outputs.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(produced[placeholder], dest)
        return log


def _gmat_version(console: Path) -> str:
    proc = subprocess.run(
        [str(console), "--version"], cwd=console.parent, capture_output=True, text=True
    )
    lines = [ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if "Build" in ln]
    return lines[-1] if lines else "unknown"


def _provenance(console: Path) -> dict[str, str]:
    rev = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    return {
        "gmat_console": str(console),
        "gmat_console_sha256": hashlib.sha256(console.read_bytes()).hexdigest(),
        "gmat_build": _gmat_version(console),
        "host_platform": platform.platform(),
        "host_machine": platform.machine(),
        "tars_git_revision": rev,
    }


def cmd_run(args: argparse.Namespace) -> None:
    console = Path(args.gmat_console)
    REPORTS.mkdir(exist_ok=True)
    names = sorted(p.stem for p in SCRIPTS.glob("*.script"))
    for name in names:
        text = (SCRIPTS / f"{name}.script").read_text()
        outputs = {"__OUT__": REPORTS / f"{name}.txt"}
        if "__STEPS__" in text:
            outputs["__STEPS__"] = REPORTS / f"{name}.steps.txt"
        _run_gmat(console, text, outputs)
        print("ran", name)
    (HERE / "run_provenance.json").write_text(
        json.dumps(_provenance(console), indent=1, sort_keys=True) + "\n"
    )


def cmd_reproduce(args: argparse.Namespace) -> None:
    console = Path(args.gmat_console)
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        m1_out = Path(tmp) / "m1.txt"
        text = M1_SCRIPT.read_text().replace("'m1_two_body_report.txt'", "'__OUT__'")
        _run_gmat(console, text, {"__OUT__": m1_out})
        result["m1_reference_report_byte_identical"] = m1_out.read_bytes() == (
            M1_REPORT.read_bytes()
        )
        probe_out = Path(tmp) / "probe.txt"
        text = (PROBE_DIR / "m2_burn_probe.script").read_text().replace("__G__", "9.80665")
        _run_gmat(console, text, {"__OUT__": probe_out})
        committed = PROBE_DIR / "gmat_probe_report_g9.80665.txt"
        result["m2_probe_report_byte_identical"] = probe_out.read_bytes() == committed.read_bytes()
    result["provenance"] = _provenance(console)
    (HERE / "reproduce.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result, indent=1))


# ----------------------------------------------------------------------------- analysis


def _rows(path: Path, columns: list[str]) -> list[dict[str, float]]:
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            values = [float(tok) for tok in line.split()]
            if len(values) != len(columns):
                raise ValueError(f"{path.name}: expected {len(columns)} columns: {line!r}")
            out.append(dict(zip(columns, values, strict=True)))
    return out


def _rv(row: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    r = np.array([row["x"], row["y"], row["z"]]) * 1e3
    v = np.array([row["vx"], row["vy"], row["vz"]]) * 1e3
    return r, v


def _along_track(dr: np.ndarray, v: np.ndarray) -> float:
    """Time offset (s) equivalent to a position difference along the velocity."""
    return float(np.dot(dr, v) / np.dot(v, v))


def _ulp_s(epoch_days: float) -> float:
    return math.ulp(epoch_days) * DAY


def analyze_segment(name: str, mu: float) -> dict[str, object]:
    _, h, inner, _ = SEGMENT_CASES[name]
    rows = _rows(REPORTS / f"{name}.txt", SEG_COLUMNS)
    a0 = rows[0]["a1mjd"]
    r0, v0 = _rv(rows[0])
    epoch = a0  # mechanism M-a: epoch <- epoch + h/86400 (double) per Propagate command
    exact_epoch = exact_da = 0
    max_pos_err = max_dt = max_elapsed_vs_epoch = 0.0
    tt_off = []
    drift = []
    for k, row in enumerate(rows):
        if k > 0:
            for _ in range(inner):
                epoch = epoch + h / DAY
        exact_epoch += row["a1mjd"] == epoch
        exact_da += row["da_days"] == epoch - a0
        drift.append(row["da_days"] * DAY - row["label_s"])
        max_elapsed_vs_epoch = max(
            max_elapsed_vs_epoch, abs(row["elapsed_secs"] - row["da_days"] * DAY)
        )
        tt_off.append(row["tt_minus_a1_s"] - TT_MINUS_A1)
        r = _rv(row)[0]
        rk, vk = kepler.propagate(r0, v0, row["label_s"], mu)
        max_pos_err = max(max_pos_err, float(np.linalg.norm(r - rk)))
        max_dt = max(max_dt, abs(_along_track(r - rk, vk)))
    commands = (len(rows) - 1) * inner
    ulp = _ulp_s(a0)
    return {
        "a1_epoch0": repr(a0),
        "epoch_ulp_s": ulp,
        "segment_s": h,
        "propagate_commands": commands,
        "rows": len(rows),
        "rows_epoch_bit_exact_vs_model_M_a": f"{exact_epoch}/{len(rows)}",
        "rows_da_bit_exact_vs_model_M_a": f"{exact_da}/{len(rows)}",
        "final_epoch_drift_s": drift[-1],
        "mean_drift_per_command_ulp": drift[-1] / commands / ulp if commands else 0.0,
        "elapsed_secs_minus_epoch_difference_max_s": max_elapsed_vs_epoch,
        "tt_minus_a1_deviation_s": {"min": min(tt_off), "max": max(tt_off)},
        "gmat_vs_kepler_at_label_pos_max_m": max_pos_err,
        "gmat_vs_kepler_at_label_time_offset_max_s": max_dt,
    }


def _final_step(goal: float, prev_achieved: float) -> float:
    return math.floor((goal - prev_achieved) / TIME_ROUNDOFF + 0.5) * TIME_ROUNDOFF


def predict_stop(base_epoch: float, goal: float, step_epochs: list[float], step_times: list[float]):
    """Mechanism M-b: duration GMAT integrates for {ElapsedSecs = goal}.

    step_epochs / step_times are the accepted natural steps (epoch double, true elapsed s).
    Returns (previous step time, final step, predicted total).
    """
    prev_t, prev_epoch = 0.0, base_epoch
    for ep, t in zip(step_epochs, step_times, strict=True):
        achieved = (ep - base_epoch) * DAY
        if achieved >= goal:
            break
        prev_t, prev_epoch = t, ep
    prev_achieved = (prev_epoch - base_epoch) * DAY
    final = _final_step(goal, prev_achieved)
    return prev_t, final, prev_t + final


def analyze_stream(name: str, mu: float) -> dict[str, object]:
    rows = _rows(REPORTS / f"{name}.txt", STREAM_COLUMNS)
    a0 = rows[0]["a1mjd"]
    r0, v0 = _rv(rows[0])
    exact = 0
    max_pos_err = max_dt = max_drift = 0.0
    for k, row in enumerate(rows):
        t = 60.0 * k
        exact += row["a1mjd"] == a0 + t / DAY  # one rounding per row, no accumulation
        max_drift = max(max_drift, abs((row["a1mjd"] - a0) * DAY - t))
        r = _rv(row)[0]
        rk, vk = kepler.propagate(r0, v0, t, mu)
        max_pos_err = max(max_pos_err, float(np.linalg.norm(r - rk)))
        max_dt = max(max_dt, abs(_along_track(r - rk, vk)))
    extra: dict[str, float] = {}
    if name == "stream60_m1tt":
        # Same epoch and propagator as the committed M1 reference (895 x 60 s commands).
        ref = parse_report(M1_REPORT.read_text())
        dr = [float(np.linalg.norm(_rv(a)[0] - b.r)) for a, b in zip(rows, ref, strict=True)]
        dv = [float(np.linalg.norm(_rv(a)[1] - b.v)) for a, b in zip(rows, ref, strict=True)]
        extra = {"vs_committed_m1_reference_pos_max_m": max(dr)}
        extra["vs_committed_m1_reference_vel_max_mps"] = max(dv)
    return {
        **extra,
        "rows": len(rows),
        "expected_rows": int(T_END / 60.0) + 1,
        "epoch_ulp_s": _ulp_s(a0),
        "rows_epoch_equal_a0_plus_t_single_rounding": f"{exact}/{len(rows)}",
        "epoch_drift_max_s": max_drift,
        "gmat_vs_kepler_at_60k_pos_max_m": max_pos_err,
        "gmat_vs_kepler_at_60k_time_offset_max_s": max_dt,
    }


def analyze_burn(name: str, mu: float) -> dict[str, object]:
    t_burn = BURN_CASES[name][1]
    rows = _rows(REPORTS / f"{name}.txt", BURN_COLUMNS)
    steps = _rows(REPORTS / f"{name}.steps.txt", STEP_COLUMNS)
    r0, v0 = _rv(rows[0])
    r1 = _rv(rows[1])[0]
    r2, v2 = _rv(rows[2])
    r3 = _rv(rows[3])[0]
    m_before, m_after = rows[1]["mass"], rows[2]["mass"]
    t_mass = (m_before - m_after) / MDOT
    # Ignition: GMAT state at the end of the 600 s coast vs exact Kepler at 600 s.
    rk, vk = kepler.propagate(r0, v0, T_IGN, mu)
    dt_ign = _along_track(r1 - rk, vk)
    # Final coast is Keplerian: GMAT final vs Kepler from GMAT cutoff over the nominal time.
    rk3, vk3 = kepler.propagate(r2, v2, T_END - T_IGN - t_burn, mu)
    dt_final = _along_track(r3 - rk3, vk3)
    # Per-step data published during the burn (first row is the burn start).
    base = rows[1]["a1mjd"]
    inner = steps[1:-1]
    pred_prev, pred_final, pred_total = predict_stop(
        base,
        t_burn,
        [s["a1mjd"] for s in inner],
        [(m_before - s["mass"]) / MDOT for s in inner],
    )
    # Same model for the coast to ignition is not observable step-by-step here.
    return {
        "burn_s": t_burn,
        "a1_burn_start": repr(base),
        "epoch_ulp_s": _ulp_s(base),
        "published_steps_in_burn": len(steps),
        "burn_duration_from_mass_minus_nominal_s": t_mass - t_burn,
        "model_M_b_previous_step_s": pred_prev,
        "model_M_b_final_step_s": pred_final,
        "model_M_b_duration_minus_nominal_s": pred_total - t_burn,
        "mass_vs_model_M_b_s": t_mass - pred_total,
        "mass_after_minus_analytic_kg": m_after - (m_before - MDOT * t_burn),
        "ignition_time_offset_vs_kepler_s": dt_ign,
        "ignition_pos_vs_kepler_m": float(np.linalg.norm(r1 - rk)),
        "final_coast_time_offset_vs_kepler_s": dt_final,
        "cutoff_elapsed_secs_minus_nominal_s": rows[2]["elapsed_secs"] - (T_IGN + t_burn),
    }


def _dop(y0: np.ndarray, mu: float, t_ign: float, t_burn: float, t_end: float) -> np.ndarray:
    def rhs(_t: float, y: np.ndarray, on: bool) -> np.ndarray:
        r, v, m = y[:3], y[3:6], y[6]
        a = -mu * r / np.linalg.norm(r) ** 3
        if on:
            a = a + (F / m) * v / np.linalg.norm(v)
        return np.concatenate([v, a, [-MDOT if on else 0.0]])

    y = y0
    for a, b, on in (
        (0.0, t_ign, False),
        (t_ign, t_ign + t_burn, True),
        (t_ign + t_burn, t_end, False),
    ):
        sol = solve_ivp(rhs, (a, b), y, method="DOP853", rtol=1e-13, atol=1e-9, args=(on,))
        y = sol.y[:, -1]
    return y


def attribution(case: str, burn: dict[str, object], mu: float) -> dict[str, object]:
    """Explain a GMAT 77.3 s burn case's final state with its measured timing offsets."""
    rows = _rows(REPORTS / f"{case}.txt", BURN_COLUMNS)
    r0, v0 = _rv(rows[0])
    r3, v3 = _rv(rows[3])
    y0 = np.concatenate([r0, v0, [DRY + PROP]])
    nominal = _dop(y0, mu, T_IGN, 77.3, T_END)
    d_ign = float(burn["ignition_time_offset_vs_kepler_s"])
    d_burn = float(burn["burn_duration_from_mass_minus_nominal_s"])
    d_fin = float(burn["final_coast_time_offset_vs_kepler_s"])
    corrected = _dop(y0, mu, T_IGN + d_ign, 77.3 + d_burn, T_END + d_ign + d_burn + d_fin)

    # Sensitivities by central differences of 1e-4 s, scaled to 1 microsecond.
    h = 1e-4

    def sens(fn) -> float:
        dp = fn(h)[:3] - fn(-h)[:3]
        return float(np.linalg.norm(dp) / (2 * h) * 1e-6)

    return {
        "case": case,
        "gmat_vs_dop853_nominal_final_pos_m": float(np.linalg.norm(r3 - nominal[:3])),
        "gmat_vs_dop853_nominal_final_vel_mps": float(np.linalg.norm(v3 - nominal[3:6])),
        "gmat_vs_dop853_with_measured_offsets_final_pos_m": float(
            np.linalg.norm(r3 - corrected[:3])
        ),
        "gmat_vs_dop853_with_measured_offsets_final_vel_mps": float(
            np.linalg.norm(v3 - corrected[3:6])
        ),
        "offsets_used_s": {"ignition": d_ign, "burn_duration": d_burn, "final_stop": d_fin},
        "final_pos_sensitivity_m_per_us": {
            "burn_duration": sens(lambda d: _dop(y0, mu, T_IGN, 77.3 + d, T_END)),
            "ignition_shift_same_duration": sens(lambda d: _dop(y0, mu, T_IGN + d, 77.3, T_END)),
            "final_time": float(np.linalg.norm(nominal[3:6]) * 1e-6),
        },
    }


def cmd_analyze(_: argparse.Namespace) -> None:
    mu = load_scenario(str(SCENARIO)).constants.mu
    out: dict[str, object] = {
        "model": {
            "time_roundoff_s": TIME_ROUNDOFF,
            "mdot_kg_per_s": MDOT,
            "tt_minus_a1_s": TT_MINUS_A1,
        },
        "segments": {n: analyze_segment(n, mu) for n in SEGMENT_CASES},
        "burns": {n: analyze_burn(n, mu) for n in BURN_CASES},
        "streams": {n: analyze_stream(n, mu) for n in STREAM_CASES},
    }
    burns = out["burns"]
    assert isinstance(burns, dict)
    # burn_m1tt_77.3 is the VAL-0009 probe (identical script settings and output).
    out["attribution"] = {
        c: attribution(c, burns[c], mu) for c in ("burn_m1tt_77.3", "aligned_m1tt_77.3")
    }
    (HERE / "results.json").write_text(json.dumps(out, indent=1) + "\n")
    print("wrote results.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate").set_defaults(fn=cmd_generate)
    for name, fn in (("run", cmd_run), ("reproduce", cmd_reproduce)):
        p = sub.add_parser(name)
        p.add_argument("--gmat-console", default=str(DEFAULT_GMAT))
        p.set_defaults(fn=fn)
    sub.add_parser("analyze").set_defaults(fn=cmd_analyze)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
