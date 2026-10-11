"""GMAT finite-burn reference for Milestone 2 (T6; DR-0015 option A, DR-0016 A).

GMAT R2026a is an independent physics reference: its trajectory, mass and burn
timing come from GMAT's own ChemicalThruster/FiniteBurn model and PrinceDormand78
integrator, configured from the scenario's raw inputs. Nothing GMAT is given or
judged against comes from simulator output.

Generation follows DR-0016 (aligned stepping):
- The mission is split into arcs at every predicted ignition and cutoff, and at the
  telemetry grid. Each arc is one ``Propagate`` whose propagator has
  ``InitialStepSize = MaxStep = h`` with h dividing the arc: 60 s (the telemetry
  interval) on grid-aligned coasts, 1 s during burns, and the arc length itself for
  the short realignment arcs before or after a burn. Every stop then lands on a
  natural step, so GMAT's microsecond stop rounding (VAL-0010 M-b) is a no-op.
- Rows stream from one ReportFile subscriber at every integrator step, labelled by an
  arc counter. Row *times* are assigned from the known step schedule, never from
  GMAT's epoch or ElapsedSecs columns, which carry the per-command epoch re-rounding
  (VAL-0010 M-a). The epoch column is kept only to verify the step spacing.
- Mandatory alignment verification (DR-0016): row counts per arc, step spacing from
  the epoch column, burn duration from GMAT's mass, and coast rows against exact
  Kepler propagation of each arc's GMAT start state.

GMAT works in km and km/s; conversion happens only here (ADR-0002).
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

import numpy as np

from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.scenario import ScenarioV2
from tars.validation.gmat import _gmat_epoch
from tars.validation.m2 import PredictedBurn, expected_initial_state, vehicle

BURN_STEP_S = 1.0  # DR-0016: burns at 1 s steps (a divisor of the microsecond grid)
STREAM_COLUMNS = (
    "ARC",
    "Sat.A1ModJulian",
    "Sat.EarthMJ2000Eq.X",
    "Sat.EarthMJ2000Eq.Y",
    "Sat.EarthMJ2000Eq.Z",
    "Sat.EarthMJ2000Eq.VX",
    "Sat.EarthMJ2000Eq.VY",
    "Sat.EarthMJ2000Eq.VZ",
    "Sat.TotalMass",
)
_THRUSTER = {"prograde": ("EngPro", "FBPro", 1), "retrograde": ("EngRetro", "FBRetro", -1)}


@dataclass(frozen=True)
class Arc:
    """One aligned Propagate: [start, end] with fixed step h; burn direction or None."""

    index: int
    start_s: float
    end_s: float
    step_s: float
    direction: str | None

    @property
    def length_s(self) -> float:
        return self.end_s - self.start_s

    @property
    def steps(self) -> int:
        """Number of integrator steps: full steps of h plus a final partial one."""
        n = math.floor(self.length_s / self.step_s + 1e-9)
        return n if math.isclose(n * self.step_s, self.length_s, rel_tol=0, abs_tol=1e-9) else n + 1

    def row_times(self, first: bool) -> list[float]:
        """Label times of the rows this arc streams.

        GMAT R2026a writes the state at the start of the first Propagate, then one row
        per integrator step; later Propagates do not repeat their start state
        (measured on the reference run). The last step lands exactly on ``end_s``.
        """
        times = [self.start_s + k * self.step_s for k in range(1, self.steps)]
        return [*([self.start_s] if first else []), *times, self.end_s]


def plan_arcs(
    scenario: ScenarioV2, predicted: Sequence[PredictedBurn], horizon_s: float
) -> list[Arc]:
    """Arcs from the predicted burns (scenario inputs) and the telemetry grid."""
    grid = scenario.telemetry.sample_interval_s
    cuts = sorted(
        {0.0, horizon_s}
        | {b.ignition_t_s for b in predicted if b.ignition_t_s < horizon_s}
        | {min(b.cutoff_t_s, horizon_s) for b in predicted if b.ignition_t_s < horizon_s}
    )
    arcs: list[Arc] = []

    def add(a: float, b: float, h: float, direction: str | None) -> None:
        if b > a:
            arcs.append(Arc(len(arcs) + 1, a, b, h, direction))

    for a, b in pairwise(cuts):
        burn = next((p for p in predicted if p.ignition_t_s <= a and b <= p.cutoff_t_s), None)
        if burn is not None:
            add(a, b, min(BURN_STEP_S, b - a), burn.direction)
            continue
        first = math.ceil(a / grid) * grid
        last = math.floor(b / grid) * grid
        if first >= last:  # no full grid interval inside: one step
            add(a, b, b - a, None)
            continue
        add(a, first, first - a, None)
        add(first, last, grid, None)
        add(last, b, b - last, None)
    return arcs


def m2_script(
    scenario: ScenarioV2,
    predicted: Sequence[PredictedBurn],
    horizon_s: float,
    report_path: str = "report.txt",
) -> str:
    """GMAT script reproducing the scenario's physics and accepted burns (DR-0016 A)."""
    if scenario.force_models != ("point_mass_gravity",):
        raise ValueError("M2 GMAT script supports point-mass gravity only (DR-0002)")
    veh = vehicle(scenario)
    if veh is None:
        raise ValueError("M2 GMAT reference needs a spacecraft")
    c = scenario.constants
    r0, v0 = expected_initial_state(scenario)
    r_km = [float(x) / 1000.0 for x in r0]
    v_kms = [float(x) / 1000.0 for x in v0]
    arcs = plan_arcs(scenario, predicted, horizon_s)
    steps = sorted({a.step_s for a in arcs})
    prop_name = {h: f"P{i}" for i, h in enumerate(steps)}
    directions = sorted({a.direction for a in arcs if a.direction})

    lines = [
        "%% M2 finite-burn reference case for GMAT R2026a (T6; DR-0015 A, DR-0016 A).",
        f"%% GENERATED by toolbox/scripts/gmat_m2.py from scenario '{scenario.name}'"
        " -- do not edit.",
        f"%% scenario_hash: {scenario.config_hash()}",
        "%% Model: point-mass Earth; ideal constant-thrust engine, a = F/m, velocity-tracking",
        "%% VNB pointing; standard gravity g0 overridden (GMAT default differs, VAL-0009).",
        "",
        f"GMAT Earth.Mu = {c.mu / 1e9!r};",
        f"GMAT Earth.EquatorialRadius = {c.equatorial_radius / 1000.0!r};",
        "",
        "Create Spacecraft Sat;",
        "GMAT Sat.DateFormat = TTGregorian;",
        f"GMAT Sat.Epoch = '{_gmat_epoch(scenario.epoch)}';",
        "GMAT Sat.CoordinateSystem = EarthMJ2000Eq;",
        "GMAT Sat.DisplayStateType = Cartesian;",
        f"GMAT Sat.X = {r_km[0]!r};",
        f"GMAT Sat.Y = {r_km[1]!r};",
        f"GMAT Sat.Z = {r_km[2]!r};",
        f"GMAT Sat.VX = {v_kms[0]!r};",
        f"GMAT Sat.VY = {v_kms[1]!r};",
        f"GMAT Sat.VZ = {v_kms[2]!r};",
        f"GMAT Sat.DryMass = {veh.dry_mass_kg!r};",
        "GMAT Sat.Cd = 2.2;",
        "GMAT Sat.Cr = 1.8;",
        "GMAT Sat.Tanks = {Tank1};",
        f"GMAT Sat.Thrusters = {{{', '.join(_THRUSTER[d][0] for d in directions)}}};",
        "",
        "Create ChemicalTank Tank1;",
        "GMAT Tank1.AllowNegativeFuelMass = false;",
        f"GMAT Tank1.FuelMass = {veh.propellant_kg!r};",
    ]
    for d in directions:
        eng, fb, sign = _THRUSTER[d]
        lines += [
            "",
            f"Create ChemicalThruster {eng};",
            f"GMAT {eng}.CoordinateSystem = Local;",
            f"GMAT {eng}.Origin = Earth;",
            f"GMAT {eng}.Axes = VNB;",
            f"GMAT {eng}.ThrustDirection1 = {sign};",
            f"GMAT {eng}.ThrustDirection2 = 0;",
            f"GMAT {eng}.ThrustDirection3 = 0;",
            f"GMAT {eng}.DutyCycle = 1;",
            f"GMAT {eng}.ThrustScaleFactor = 1;",
            f"GMAT {eng}.DecrementMass = true;",
            f"GMAT {eng}.Tank = {{Tank1}};",
            f"GMAT {eng}.MixRatio = [1];",
            f"GMAT {eng}.GravitationalAccel = {STANDARD_GRAVITY!r};",
            f"GMAT {eng}.C1 = {veh.thrust_n!r};",
            *(f"GMAT {eng}.C{k} = 0;" for k in range(2, 17)),
            f"GMAT {eng}.K1 = {veh.isp_s!r};",
            *(f"GMAT {eng}.K{k} = 0;" for k in range(2, 17)),
            f"Create FiniteBurn {fb};",
            f"GMAT {fb}.Thrusters = {{{eng}}};",
        ]
    lines += [
        "",
        "Create ForceModel FM;",
        "GMAT FM.CentralBody = Earth;",
        "GMAT FM.PrimaryBodies = {};",
        "GMAT FM.PointMasses = {Earth};",
        "GMAT FM.Drag = None;",
        "GMAT FM.SRP = Off;",
        "GMAT FM.RelativisticCorrection = Off;",
        "GMAT FM.ErrorControl = RSSStep;",
    ]
    for h in steps:
        p = prop_name[h]
        lines += [
            "",
            f"Create Propagator {p};",
            f"GMAT {p}.FM = FM;",
            f"GMAT {p}.Type = PrinceDormand78;",
            f"GMAT {p}.InitialStepSize = {h!r};",
            f"GMAT {p}.Accuracy = 1e-13;",
            f"GMAT {p}.MinStep = 0;",
            f"GMAT {p}.MaxStep = {h!r};",
            f"GMAT {p}.MaxStepAttempts = 50;",
            f"GMAT {p}.StopIfAccuracyIsViolated = true;",
        ]
    lines += [
        "",
        "Create ReportFile S;",
        f"GMAT S.Filename = '{report_path}';",
        "GMAT S.Precision = 17;",
        "GMAT S.WriteHeaders = false;",
        "GMAT S.LeftJustify = On;",
        "GMAT S.ZeroFill = Off;",
        "GMAT S.FixedWidth = true;",
        "GMAT S.Delimiter = ' ';",
        "GMAT S.ColumnWidth = 26;",
        f"GMAT S.Add = {{{', '.join(STREAM_COLUMNS)}}};",
        "",
        "Create Variable ARC;",
        "",
        "BeginMissionSequence;",
    ]
    active: str | None = None
    for arc in arcs:
        if arc.direction != active:
            if active is not None:
                lines.append(f"EndFiniteBurn {_THRUSTER[active][1]}(Sat);")
            if arc.direction is not None:
                lines.append(f"BeginFiniteBurn {_THRUSTER[arc.direction][1]}(Sat);")
            active = arc.direction
        lines.append(f"ARC = {arc.index};")
        lines.append(
            f"Propagate {prop_name[arc.step_s]}(Sat) {{Sat.ElapsedSecs = {arc.length_s!r}}};"
        )
    if active is not None:
        lines.append(f"EndFiniteBurn {_THRUSTER[active][1]}(Sat);")
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class Row:
    arc: int
    a1mjd: float
    r: np.ndarray  # m
    v: np.ndarray  # m/s
    mass_kg: float


def parse_stream(text: str) -> list[Row]:
    rows = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != len(STREAM_COLUMNS):
            raise ValueError(f"GMAT report line {number}: {len(fields)} columns")
        f = [float(x) for x in fields]
        if not all(math.isfinite(x) for x in f) or f[0] != int(f[0]):
            raise ValueError(f"GMAT report line {number}: invalid value")
        rows.append(Row(int(f[0]), f[1], np.array(f[2:5]) * 1e3, np.array(f[5:8]) * 1e3, f[8]))
    return rows


_STATE_LINE = re.compile(r"^GMAT Sat\.(X|Y|Z|VX|VY|VZ) = (.+);$")
_STATE_KEYS = ("X", "Y", "Z", "VX", "VY", "VZ")


def split_script(script: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Script lines with the six initial-state literals replaced *in place* by a
    placeholder, and those literals as r [m], v [m/s].

    Positions are preserved, so moving or duplicating a state assignment changes the
    normalized lines (review M2-T6 F2). Missing or repeated components raise.
    """
    lines, values = [], {}
    for line in script.splitlines():
        m = _STATE_LINE.match(line)
        if m:
            if m.group(1) in values:
                raise ValueError(f"Sat.{m.group(1)} assigned more than once")
            values[m.group(1)] = float(m.group(2))
            lines.append(f"GMAT Sat.{m.group(1)} = <initial state>;")
        else:
            lines.append(line)
    if set(values) != set(_STATE_KEYS):
        raise ValueError(f"initial-state assignments {sorted(values)} incomplete")
    r = np.array([values["X"], values["Y"], values["Z"]]) * 1e3
    v = np.array([values["VX"], values["VY"], values["VZ"]]) * 1e3
    return lines, r, v


# --------------------------------------------------------------- labelling and checks


def label_rows(rows: Sequence[Row], arcs: Sequence[Arc]) -> tuple[dict[float, Row], list[str]]:
    """Assign each row its scheduled time; any count mismatch is a violation (DR-0016)."""
    v: list[str] = []
    by_arc: dict[int, list[Row]] = {}
    for row in rows:
        by_arc.setdefault(row.arc, []).append(row)
    if sorted(by_arc) != [a.index for a in arcs]:
        v.append(f"arcs in report {sorted(by_arc)} != planned {[a.index for a in arcs]}")
    if [r.arc for r in rows] != sorted(r.arc for r in rows):
        v.append("report rows are not in arc order")
    labelled: dict[float, Row] = {}
    for i, arc in enumerate(arcs):
        times = arc.row_times(first=i == 0)
        got = by_arc.get(arc.index, [])
        if len(got) != len(times):
            v.append(f"arc {arc.index}: {len(got)} rows, expected {len(times)} (not step-aligned)")
            continue
        labelled.update(zip(times, got, strict=True))
    return labelled, v


def alignment_metrics(
    labelled: dict[float, Row],
    arcs: Sequence[Arc],
    predicted: Sequence[PredictedBurn],
    mu: float,
    mass_flow_kgps: float,
) -> dict[str, float]:
    """DR-0016 mandatory alignment verification.

    - Step spacing: consecutive rows' GMAT epochs differ by the scheduled step (to the
      epoch's resolution, ~3e-7 s per value, plus per-command re-rounding, M-a).
    - Burn duration from GMAT's own mass: (m_start - m_end) / mdot vs the scheduled arc.
    - Coast arcs vs exact Kepler propagation of GMAT's arc-start state: the rows are at
      their labelled times.
    """
    from tars.astro import kepler

    times = sorted(labelled)
    spacing = 0.0
    for a, b in pairwise(times):
        d = (labelled[b].a1mjd - labelled[a].a1mjd) * 86400.0
        spacing = max(spacing, abs(d - (b - a)))
    duration = 0.0
    for arc in arcs:
        if arc.direction is None or arc.start_s not in labelled or arc.end_s not in labelled:
            continue
        used = labelled[arc.start_s].mass_kg - labelled[arc.end_s].mass_kg
        duration = max(duration, abs(used / mass_flow_kgps - arc.length_s))
    kep = 0.0
    for arc in arcs:
        if arc.direction is not None or arc.start_s not in labelled:
            continue
        s0 = labelled[arc.start_s]
        for t in times:
            if arc.start_s < t <= arc.end_s:
                r, _ = kepler.propagate(s0.r, s0.v, t - arc.start_s, mu)
                kep = max(kep, float(np.linalg.norm(labelled[t].r - r)))
    return {
        "step_spacing_error_max_s": spacing,
        "burn_duration_from_mass_error_max_s": duration,
        "coast_vs_kepler_position_error_max_m": kep,
    }


def _expected_mass(t: float, veh, predicted: Sequence[PredictedBurn]) -> float:
    """Analytic total mass at t from the scenario inputs (mass law, burns in order)."""
    prop = veh.propellant_kg
    for b in predicted:
        if t <= b.ignition_t_s:
            break
        if t >= b.cutoff_t_s:
            prop = b.propellant_after_kg
        else:
            prop = b.propellant_before_kg - veh.mass_flow_kgps * (t - b.ignition_t_s)
            break
    return veh.dry_mass_kg + prop


def _node_crossings(states: dict[float, tuple[np.ndarray, np.ndarray]], mu: float) -> list[float]:
    """Ascending-node crossings between consecutive states, refined by bisection on
    exact Kepler propagation (coast arcs; burns never contain a crossing here)."""
    from tars.astro import kepler

    out = []
    times = sorted(states)
    for a, b in pairwise(times):
        (ra, va), (rb, _) = states[a], states[b]
        if ra[2] < 0.0 <= rb[2]:
            lo, hi = 0.0, b - a
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if kepler.propagate(ra, va, mid, mu)[0][2] < 0.0:
                    lo = mid
                else:
                    hi = mid
            out.append(a + hi)
    return out


def o9_metrics(
    scenario: ScenarioV2,
    predicted: Sequence[PredictedBurn],
    events: Sequence,
    labelled: dict[float, Row],
    reference: dict,
) -> dict[str, float]:
    """O9: GMAT against independent references, and the simulator against GMAT.

    ``reference`` is the DOP853 reference (independent RHS) at every labelled time.
    Classification (as M1): if ours-vs-GMAT ~ ours-vs-DOP853 and GMAT-vs-DOP853 is
    far smaller, the difference is our RK4 error, not a modelling disagreement.
    """
    veh = vehicle(scenario)
    assert veh is not None
    mu = scenario.constants.mu
    times = sorted(labelled)
    g_pos = g_vel = g_mass = 0.0
    for t in times:
        row, y = labelled[t], reference[t]
        g_pos = max(g_pos, float(np.linalg.norm(row.r - y[:3])))
        g_vel = max(g_vel, float(np.linalg.norm(row.v - y[3:6])))
        g_mass = max(g_mass, abs(row.mass_kg - _expected_mass(t, veh, predicted)))
    end = times[-1]
    states = [e for e in events if e.type == "StateSampled"]
    s_pos = s_vel = 0.0
    for s in states:
        row = labelled.get(s.t)
        if row is None:
            s_pos = s_vel = math.inf  # every sample time must be a GMAT row
            continue
        s_pos = max(s_pos, float(np.linalg.norm(np.array(s.r) - row.r)))
        s_vel = max(s_vel, float(np.linalg.norm(np.array(s.v) - row.v)))
    b_pos = b_vel = 0.0
    for e in events:
        if e.type in ("BurnStarted", "BurnEnded"):
            row = labelled.get(e.event_t_s)
            if row is None:
                b_pos = b_vel = math.inf
                continue
            b_pos = max(b_pos, float(np.linalg.norm(np.array(e.r) - row.r)))
            b_vel = max(b_vel, float(np.linalg.norm(np.array(e.v) - row.v)))
    m_err = 0.0
    compared_mass = 0
    for p in events:
        if p.type == "PropulsionSampled" and p.t in labelled:
            m_err = max(m_err, abs(p.total_mass_kg - labelled[p.t].mass_kg))
            compared_mass += 1
    done = events[-1]
    final = labelled.get(done.t)
    ours_crossings = [e.crossing_t for e in events if e.type == "OrbitCompleted"]
    gmat_crossings = _node_crossings({t: (labelled[t].r, labelled[t].v) for t in times}, mu)
    if len(ours_crossings) == len(gmat_crossings):
        node = max(
            (abs(a - b) for a, b in zip(ours_crossings, gmat_crossings, strict=True)), default=0.0
        )
    else:
        node = math.inf
    return {
        "gmat_vs_dop853_position_error_max_m": g_pos,
        "gmat_vs_dop853_velocity_error_max_mps": g_vel,
        "gmat_vs_dop853_final_position_error_m": float(
            np.linalg.norm(labelled[end].r - reference[end][:3])
        ),
        "gmat_mass_vs_analytic_error_max_kg": g_mass,
        "ours_vs_gmat_sample_position_error_max_m": s_pos,
        "ours_vs_gmat_sample_velocity_error_max_mps": s_vel,
        "ours_vs_gmat_burn_boundary_position_error_max_m": b_pos,
        "ours_vs_gmat_burn_boundary_velocity_error_max_mps": b_vel,
        "ours_vs_gmat_final_position_error_m": math.inf
        if final is None
        else float(np.linalg.norm(np.array(done.r) - final.r)),
        "ours_vs_gmat_final_velocity_error_mps": math.inf
        if final is None
        else float(np.linalg.norm(np.array(done.v) - final.v)),
        "ours_vs_gmat_mass_error_max_kg": m_err if compared_mass else math.inf,
        "ours_vs_gmat_node_crossing_error_max_s": node,
        "gmat_rows": float(len(times)),
        "mass_samples_compared": float(compared_mass),
    }


# Approved GMAT install (toolbox/references/gmat/README.md, "Installed reference tool"):
# GMAT R2026a, NASA-signed GmatConsole. Its sha256 is pinned; a reference produced by
# any other binary is rejected (review M2-T6 F3).
APPROVED_GMAT = {
    "gmat_version": "R2026a",
    "gmat_build_date": "Mar 26 2026  19:40:08",
    "gmat_console_sha256": "1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2",
}
CONSOLE_SUCCESS = "*** GMAT Integration test (Console version) successful! ***"


def is_approved_console(path) -> bool:
    """The executable is the approved GMAT install, by content digest (review F10)."""
    import hashlib
    from pathlib import Path

    p = Path(path)
    return (
        p.is_file()
        and hashlib.sha256(p.read_bytes()).hexdigest() == APPROVED_GMAT["gmat_console_sha256"]
    )


MODEL = (
    "Earth point mass; ChemicalThruster VNB +-1, C1 = F, K1 = Isp, other coefficients 0, "
    "GravitationalAccel = g0, DecrementMass; PrinceDormand78, Accuracy 1e-13; aligned "
    "stepping (DR-0016): coasts 60 s, burns 1 s, realignment arcs one step"
)


def provenance_problems(
    name: str,
    metadata: dict,
    files: dict,
    scenario: ScenarioV2,
    regenerated_script: str,
    position_tol_m: float,
    velocity_tol_mps: float,
    approved: dict | None,
) -> list[str]:
    """The committed reference is what the scenario generates, produced by the approved
    GMAT binary, with a successful bound console log and approved digests.

    What this can and cannot establish (review M2-T6 F3): it makes silent or accidental
    substitution detectable (a different generator, binary, script, report or log, or
    an unreviewed digest change). It cannot prove the rows came from GMAT: a deliberate
    forger could fabricate every artifact. External origin is established by the
    reproduction test, which re-runs the approved GMAT and requires byte-identical
    reports wherever GMAT is installed, and by review of the approved-digest manifest.
    """
    import datetime as _dt
    import hashlib

    problems = []
    digests = {
        key: hashlib.sha256(files[key].read_bytes()).hexdigest()
        for key in ("script", "report", "console")
    }
    expected_meta = {
        "mission": name,
        "scenario": scenario.name,
        "scenario_hash": scenario.config_hash(),
        "script_sha256": digests["script"],
        "report_sha256": digests["report"],
        "console_sha256": digests["console"],
        "model": MODEL,
        "command": ["GmatConsole", "--run", f"<temp copy of {name}.script, absolute report path>"],
        **APPROVED_GMAT,
    }
    for key, want in expected_meta.items():
        if metadata.get(key) != want:
            problems.append(f"metadata {key} {metadata.get(key)!r} != {want!r}")
    revision = str(metadata.get("tars_git_revision", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", revision) or set(revision) == {"0"}:
        problems.append("metadata tars_git_revision missing or invalid")
    try:
        stamp = _dt.datetime.fromisoformat(str(metadata.get("generated_utc")))
        if stamp.tzinfo is None or stamp.year < 2026:  # references exist from M2 (2026)
            problems.append("metadata generated_utc implausible")
    except ValueError:
        problems.append("metadata generated_utc missing")
    if not isinstance(metadata.get("host_platform"), str) or not metadata["host_platform"]:
        problems.append("metadata host_platform missing")
    if "replace_reason" not in metadata:
        problems.append("metadata replace_reason missing")
    log = files["console"].read_text()
    if CONSOLE_SUCCESS not in log or "Execution Failed" in log or "Exception" in log:
        problems.append("console log does not record a successful GMAT run")
    # Approved digests (reviewed manifest): every artifact, metadata included, is bound;
    # a changed reference must change the manifest (reviews M2-T6 F3, F8).
    meta_digest = hashlib.sha256(files["metadata"].read_bytes()).hexdigest()
    entries = None if approved is None else approved.get("references")
    if entries is None or entries.get(name) != {
        "script_sha256": digests["script"],
        "report_sha256": digests["report"],
        "console_sha256": digests["console"],
        "metadata_sha256": meta_digest,
    }:
        problems.append("reference digests are not in the approved manifest")
    problems += history_problems(name, metadata, approved)
    try:
        other_c, r_c, v_c = split_script(files["script"].read_text())
    except ValueError as err:
        return [*problems, f"committed script: {err}"]
    other_n, r_n, v_n = split_script(regenerated_script)
    if other_c != other_n:
        diff = [f"{a!r} != {b!r}" for a, b in zip(other_c, other_n, strict=False) if a != b]
        counts = f"{len(other_c)} vs {len(other_n)} lines"
        problems.append(f"GMAT script differs from regenerated script: {diff[:3]} ({counts})")
    if not (
        np.linalg.norm(r_c - r_n) <= position_tol_m
        and np.linalg.norm(v_c - v_n) <= velocity_tol_mps
    ):
        problems.append("GMAT script initial state differs beyond the approved bound")
    veh = vehicle(scenario)
    c = scenario.constants
    constants = {
        "name": c.name,
        "mu_km3_s2": c.mu / 1e9,
        "equatorial_radius_km": c.equatorial_radius / 1000.0,
        "standard_gravity_mps2": STANDARD_GRAVITY,
        "thrust_n": None if veh is None else veh.thrust_n,
        "isp_s": None if veh is None else veh.isp_s,
        "dry_mass_kg": None if veh is None else veh.dry_mass_kg,
        "propellant_kg": None if veh is None else veh.propellant_kg,
    }
    if metadata.get("constants") != constants:
        problems.append(f"metadata constants {metadata.get('constants')} != {constants}")
    return problems


# --------------------------------------------------------------- committed references

GMAT_MISSIONS = ("m2_prograde_burn", "m2_retrograde_burn", "m2_invalid_commands")
"""Missions with a committed GMAT reference. ``m2_burn_to_depletion`` is excluded:
GMAT's stop-condition step overshoots the cutoff and drives the tank negative, which
``AllowNegativeFuelMass = false`` rejects (VAL-0009 finding 4; measured in T6). Its
depletion is validated analytically (O1, O2, DR-0017 D1a), as DR-0015 provides."""


def reference_dir():
    from tars.validation.thresholds import REPO_ROOT

    return REPO_ROOT / "toolbox" / "references" / "gmat" / "m2"


HISTORY_KEYS = frozenset(
    {"mission", "generated_utc", "tars_git_revision", "reason", "report_sha256",
     "previous_record_sha256"}
)  # fmt: skip


def record_digest(record: dict) -> str:
    """sha256 of a history record's canonical JSON (the chain link)."""
    import hashlib
    import json

    return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()


def history_problems(name: str, metadata: dict, approved: dict | None) -> list[str]:
    """The manifest history is a valid, chained, chronological record of every
    generation, and this reference's latest record is its committed generation
    (reviews M2-T6 F8, F14).

    Every record must name a GMAT mission and carry a plausible UTC timestamp, a
    non-null 40-hex revision, a non-empty reason and a 64-hex report digest. Records
    are in non-decreasing time order, and each holds the digest of the previous record
    (the first holds null). Editing, inserting, reordering or deleting records inside
    the history therefore breaks the chain. A wholesale rewrite of the whole chain is
    detectable only by reviewing the manifest's version-control history.
    """
    import datetime as _dt

    if approved is None:
        return ["approved manifest missing"]
    history = approved.get("history")
    if not isinstance(history, list) or not history:
        return ["approved manifest history is missing"]
    problems: list[str] = []
    previous: str | None = None
    last_time = None
    for i, h in enumerate(history):
        if not isinstance(h, dict) or set(h) != HISTORY_KEYS:
            return [f"history record {i} is malformed"]
        if h["mission"] not in GMAT_MISSIONS:
            problems.append(f"history record {i}: unknown mission {h['mission']!r}")
        try:
            stamp = _dt.datetime.fromisoformat(str(h["generated_utc"]))
            if stamp.tzinfo is None or stamp.year < 2026:
                raise ValueError
        except ValueError:
            problems.append(f"history record {i}: implausible generated_utc")
            stamp = None
        if stamp is not None:
            if last_time is not None and stamp < last_time:
                problems.append(f"history record {i}: out of chronological order")
            last_time = stamp
        rev = str(h["tars_git_revision"])
        if not re.fullmatch(r"[0-9a-f]{40}", rev) or set(rev) == {"0"}:
            problems.append(f"history record {i}: invalid revision")
        if not isinstance(h["reason"], str) or not h["reason"].strip():
            problems.append(f"history record {i}: missing reason")
        if not re.fullmatch(r"[0-9a-f]{64}", str(h["report_sha256"])):
            problems.append(f"history record {i}: invalid report digest")
        if h["previous_record_sha256"] != previous:
            problems.append(f"history record {i}: chain broken")
        previous = record_digest(h)
    mine = [h for h in history if h["mission"] == name]
    if not mine:
        return [*problems, "approved manifest has no history for this reference"]
    latest = {k: v for k, v in mine[-1].items() if k != "previous_record_sha256"}
    want = {
        "mission": name,
        "generated_utc": metadata.get("generated_utc"),
        "tars_git_revision": metadata.get("tars_git_revision"),
        "reason": metadata.get("replace_reason") or "initial reference",
        "report_sha256": metadata.get("report_sha256"),
    }
    if latest != want:
        problems.append(f"latest history record {latest} != metadata {want}")
    return problems


def approved_manifest_path(base=None):
    return (reference_dir() if base is None else base) / "APPROVED_DIGESTS.json"


def load_approved(base=None) -> dict | None:
    import json

    path = approved_manifest_path(base)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data if isinstance(data, dict) else None


def reference_files(name: str, base=None) -> dict[str, object]:
    d = reference_dir() if base is None else base
    return {
        "script": d / f"{name}.script",
        "report": d / f"{name}_report.txt",
        "console": d / f"{name}_console.log",
        "metadata": d / f"{name}_metadata.json",
    }


@dataclass
class O9Result:
    metrics: dict[str, float]
    violations: list[str]
    alignment: dict[str, float]


O9_REPORT_ONLY = frozenset({"gmat_rows", "mass_samples_compared"})


def coverage_problems(
    scenario: ScenarioV2,
    predicted: Sequence[PredictedBurn],
    events: Sequence,
    labelled: dict[float, Row],
    horizon: float,
) -> list[str]:
    """Every observation O9 must compare exists (review M2-T6 F5), from the scenario:
    each telemetry time and the horizon; each predicted ignition and cutoff up to the
    horizon (DR-0018: no cutoff expected after it); each propulsion sample on a GMAT
    row at the contract cadence."""
    from tars.validation.m2 import _expected_report_tick

    v: list[str] = []
    dt, grid = scenario.dt_s, scenario.telemetry.sample_interval_s
    want_states = {k * grid for k in range(int(horizon // grid) + 1)} | {horizon}
    got_states = {e.t for e in events if e.type == "StateSampled"}
    if got_states != want_states:
        v.append(
            f"StateSampled times differ from the grid ({len(got_states)} vs {len(want_states)})"
        )
    # Inclusion by the independently predicted report tick, so a same-tick submission
    # whose ignition is reported at k + 1 is not expected at a stop at k (review F13).
    final_tick = round(horizon / dt)
    want_bounds = set()
    for b in predicted:
        same = b.submit_tick * dt == b.ignition_t_s
        if _expected_report_tick(b.ignition_t_s, dt, same) <= final_tick:
            want_bounds.add(("BurnStarted", b.ignition_t_s))
        if _expected_report_tick(b.cutoff_t_s, dt, False) <= final_tick:
            want_bounds.add(("BurnEnded", b.cutoff_t_s))
    got_bounds = {(e.type, e.event_t_s) for e in events if e.type in ("BurnStarted", "BurnEnded")}
    if got_bounds != want_bounds:
        v.append(f"burn boundaries {sorted(got_bounds)} != predicted {sorted(want_bounds)}")
    want_prop = {t for t in want_states}
    for b in predicted:
        same = b.submit_tick * dt == b.ignition_t_s
        k0 = _expected_report_tick(b.ignition_t_s, dt, same)
        k1 = _expected_report_tick(b.cutoff_t_s, dt, False)
        want_prop |= {k * dt for k in range(k0, k1 + 1) if k * dt <= horizon}
    want_prop &= set(labelled)
    got_prop = {e.t for e in events if e.type == "PropulsionSampled"} & set(labelled)
    if got_prop != want_prop:
        v.append(f"PropulsionSampled on GMAT rows: {len(got_prop)}, expected {len(want_prop)}")
    return v


def compare_committed(
    name: str,
    scenario: ScenarioV2,
    expected,
    events: Sequence,
    position_tol_m: float,
    velocity_tol_mps: float,
    base=None,
) -> O9Result:
    """Verify and compare one committed (or staged, ``base``) GMAT reference."""
    import json

    from tars.validation.m2 import dop853_reference, horizon_s, predict_burns

    files = reference_files(name, base)
    missing = [str(p) for p in files.values() if not p.exists()]
    if missing:
        return O9Result({}, [f"missing reference files: {missing}"], {})
    metadata = json.loads(files["metadata"].read_text())
    predicted = predict_burns(scenario, expected)
    horizon = horizon_s(scenario, events)
    regenerated = m2_script(scenario, predicted, horizon, f"{name}_report.txt")
    v = provenance_problems(
        name, metadata, files, scenario, regenerated, position_tol_m, velocity_tol_mps,
        load_approved(base),
    )  # fmt: skip
    arcs = plan_arcs(scenario, predicted, horizon)
    labelled, label_v = label_rows(parse_stream(files["report"].read_text()), arcs)
    v += label_v
    if label_v or not labelled:
        return O9Result({}, v, {})
    v += coverage_problems(scenario, predicted, events, labelled, horizon)
    veh = vehicle(scenario)
    assert veh is not None
    alignment = alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, veh.mass_flow_kgps
    )
    r0, v0 = expected_initial_state(scenario)
    reference = dop853_reference(scenario, r0, v0, predicted, sorted(labelled))
    metrics = {**alignment, **o9_metrics(scenario, predicted, events, labelled, reference)}
    return O9Result(metrics, v, alignment)


def missing_gates(metrics: dict[str, float], limits: dict[str, float]) -> list[str]:
    """O9 metrics without a limit (review F6): fail closed, as m2_proof does."""
    return sorted(k for k in metrics if k not in limits and k not in O9_REPORT_ONLY)
