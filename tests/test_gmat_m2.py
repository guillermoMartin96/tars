"""T6: GMAT M2 reference (O9). The committed references verify and pass; corrupted
references are rejected; simulator physics mutants are caught against GMAT."""

from __future__ import annotations

import dataclasses
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tars.sim import propulsion as propulsion_module
from tars.sim import simulator as simulator_module
from tars.sim.propulsion import Prograde
from tars.sim.runner import run_scenario
from tars.validation import gmat_m2, m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import M2_THRESHOLDS, REPO_ROOT, load_thresholds

BY_NAME = {m.name: m for m in MISSIONS}
LIMITS = json.loads(M2_THRESHOLDS.read_text())["limits"]["o9_gmat"]
GATES_M1 = load_thresholds().for_validator("gmat_reference")
TOL = (
    GATES_M1["script_initial_position_difference_m"],
    GATES_M1["script_initial_velocity_difference_mps"],
)
GMAT_CONSOLE = Path.home() / "Applications" / "GMAT R2026a" / "bin" / "GmatConsole"
CLI = REPO_ROOT / "toolbox" / "scripts" / "gmat_m2.py"


def _limits(name):
    return {**LIMITS["all"], **LIMITS.get(name, {})}


def _failures(name, metrics):
    return [k for k, lim in _limits(name).items() if not metrics[k] <= lim]


def _compare(name, events=None):
    mission = BY_NAME[name]
    scenario = mission.build()
    events = run_scenario(scenario).events if events is None else events
    return gmat_m2.compare_committed(name, scenario, mission.expected, events, *TOL)


def _labelled(name):
    mission = BY_NAME[name]
    scenario = mission.build()
    predicted = m2.predict_burns(scenario, mission.expected)
    arcs = gmat_m2.plan_arcs(scenario, predicted, scenario.stop.duration_s)
    rows = gmat_m2.parse_stream(gmat_m2.reference_files(name)["report"].read_text())
    return scenario, predicted, arcs, rows


# ------------------------------------------------------------------ generator


def test_slice_arc_plan_is_aligned():
    _, _, arcs, _ = _labelled("m2_prograde_burn")
    got = [(a.start_s, a.end_s, a.step_s, a.direction) for a in arcs]
    assert got == [
        (0.0, 600.0, 60.0, None),
        (600.0, 677.3, 1.0, "prograde"),
        (677.3, 720.0, 720.0 - 677.3, None),
        (720.0, 53700.0, 60.0, None),
    ]
    # Every telemetry time is a row time, so every sample has a GMAT state.
    times = {t for i, a in enumerate(arcs) for t in a.row_times(first=i == 0)}
    assert {k * 60.0 for k in range(896)} <= times


def test_adjacent_burns_switch_thrusters_without_a_coast():
    _, _, arcs, _ = _labelled("m2_invalid_commands")
    burns = [(a.start_s, a.end_s, a.direction) for a in arcs if a.direction]
    assert burns == [
        (1200.0, 1230.0, "prograde"),
        (1230.0, 1240.0, "retrograde"),
        (2400.0, 2420.0, "retrograde"),
    ]
    script = gmat_m2.reference_files("m2_invalid_commands")["script"].read_text()
    assert "EndFiniteBurn FBPro(Sat);\nBeginFiniteBurn FBRetro(Sat);" in script


def test_script_pins_every_engine_coefficient_and_g0():
    """VAL-0009: GMAT's default GravitationalAccel is 9.81; thrust and Isp polynomials
    have defaults. The generated script fixes every one from the scenario."""
    script = gmat_m2.reference_files("m2_retrograde_burn")["script"].read_text()
    assert "GMAT EngRetro.GravitationalAccel = 9.80665;" in script
    assert "GMAT EngRetro.C1 = 490.0;" in script and "GMAT EngRetro.K1 = 312.0;" in script
    assert all(
        f"GMAT EngRetro.C{k} = 0;" in script and f"GMAT EngRetro.K{k} = 0;" in script
        for k in range(2, 17)
    )
    assert (
        "GMAT EngRetro.ThrustDirection1 = -1;" in script and "GMAT EngRetro.Axes = VNB;" in script
    )
    assert "GMAT Sat.DryMass = 1000.0;" in script and "GMAT Tank1.FuelMass = 300.0;" in script


def test_generator_is_deterministic_and_matches_the_committed_scripts():
    for name in gmat_m2.GMAT_MISSIONS:
        mission = BY_NAME[name]
        scenario = mission.build()
        predicted = m2.predict_burns(scenario, mission.expected)
        a = gmat_m2.m2_script(scenario, predicted, scenario.stop.duration_s, f"{name}_report.txt")
        b = gmat_m2.m2_script(scenario, predicted, scenario.stop.duration_s, f"{name}_report.txt")
        assert a == b
        committed = gmat_m2.reference_files(name)["script"].read_text()
        assert gmat_m2.split_script(a)[0] == gmat_m2.split_script(committed)[0]


def test_generator_refuses_unsupported_scenarios():
    no_prop = BY_NAME["m2_invalid_commands_no_propulsion"].build()
    with pytest.raises(ValueError, match="spacecraft"):
        gmat_m2.m2_script(no_prop, [], 53700.0)


def test_depletion_is_not_a_gmat_mission():
    """VAL-0009 finding 4 / T6 measurement: GMAT cannot propagate to exact depletion."""
    assert "m2_burn_to_depletion" not in gmat_m2.GMAT_MISSIONS


# ------------------------------------------------------------------ committed references


@pytest.mark.parametrize("name", gmat_m2.GMAT_MISSIONS)
def test_committed_reference_verifies_and_passes(name):
    result = _compare(name)
    assert result.violations == []
    assert _failures(name, result.metrics) == []
    # Classification: ours vs GMAT is our RK4 error (equal to ours vs DOP853).
    assert (
        result.metrics["gmat_vs_dop853_final_position_error_m"]
        < 1e-4 * result.metrics["ours_vs_gmat_final_position_error_m"]
    )


def test_tampered_report_is_rejected(tmp_path, monkeypatch):
    name = "m2_prograde_burn"
    src = gmat_m2.reference_dir()
    dst = tmp_path / "m2"
    shutil.copytree(src, dst)
    report = dst / f"{name}_report.txt"
    report.write_text(report.read_text().replace("1300 ", "1299 ", 1))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("sha256" in v for v in _compare(name).violations)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("GravitationalAccel = 9.80665;", "GravitationalAccel = 9.81;"),
        ("C1 = 490.0;", "C1 = 491.0;"),
        ("K3 = 0;", "K3 = 1;"),
        ("Accuracy = 1e-13;", "Accuracy = 1e-11;"),
    ],
)
def test_configuration_change_in_the_committed_script_is_rejected(tmp_path, monkeypatch, old, new):
    name = "m2_prograde_burn"
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    script = dst / f"{name}.script"
    script.write_text(script.read_text().replace(old, new, 1))
    meta = dst / f"{name}_metadata.json"
    data = json.loads(meta.read_text())
    import hashlib

    data["script_sha256"] = hashlib.sha256(script.read_bytes()).hexdigest()  # even if re-hashed
    meta.write_text(json.dumps(data))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("regenerated script" in v for v in _compare(name).violations)


def test_wrong_metadata_constants_are_rejected(tmp_path, monkeypatch):
    name = "m2_retrograde_burn"
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    meta = dst / f"{name}_metadata.json"
    data = json.loads(meta.read_text())
    data["constants"]["standard_gravity_mps2"] = 9.81
    meta.write_text(json.dumps(data))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("metadata constants" in v for v in _compare(name).violations)


def test_missing_row_breaks_the_alignment_count():
    _, _, arcs, rows = _labelled("m2_prograde_burn")
    _, v = gmat_m2.label_rows(rows[:500] + rows[501:], arcs)
    assert any("not step-aligned" in x for x in v)


def test_unaligned_step_is_detected():
    """An adaptive step cut (row epochs off the schedule by 1 s) fails verification."""
    scenario, predicted, arcs, rows = _labelled("m2_prograde_burn")
    shifted = [
        dataclasses.replace(r, a1mjd=r.a1mjd + 1.0 / 86400.0) if i == 300 else r
        for i, r in enumerate(rows)
    ]
    labelled, _ = gmat_m2.label_rows(shifted, arcs)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    assert metrics["step_spacing_error_max_s"] > LIMITS["all"]["step_spacing_error_max_s"]


@pytest.mark.parametrize(("field", "delta"), [("r", 1e-3), ("mass_kg", 1e-6)])
def test_corrupted_gmat_rows_fail_against_independent_references(field, delta):
    """GMAT itself is checked: a 1 mm state or 1 mg mass error fails GMAT vs DOP853 or
    GMAT vs the mass law, so a bad reference cannot vouch for the simulator."""
    name = "m2_prograde_burn"
    mission = BY_NAME[name]
    scenario, predicted, arcs, rows = _labelled(name)

    def bump(r):
        return dataclasses.replace(r, **{field: getattr(r, field) + delta})

    rows = [bump(r) if 100 <= i < 102 else r for i, r in enumerate(rows)]
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    events = run_scenario(scenario).events
    metrics = gmat_m2.o9_metrics(scenario, predicted, events, labelled, ref)
    limits = _limits(name)
    failed = [k for k, x in metrics.items() if k in limits and not x <= limits[k]]
    assert any(k.startswith("gmat_") for k in failed)  # GMAT vs an independent reference
    del mission


# ------------------------------------------------------------------ simulator mutants vs GMAT


def _mutant_failures(name, monkeypatch, apply):
    apply(monkeypatch)
    result = _compare(name)
    assert result.violations == []  # the reference itself is untouched
    return _failures(name, result.metrics)


def test_thrust_scale_mutant_fails_o9(monkeypatch):
    original = simulator_module.thrust_acceleration
    failures = _mutant_failures(
        "m2_prograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(
            simulator_module, "thrust_acceleration", lambda *a: original(*a) * (1 + 1e-5)
        ),
    )
    assert "ours_vs_gmat_final_position_error_m" in failures


def test_wrong_g0_mutant_fails_o9_mass(monkeypatch):
    failures = _mutant_failures(
        "m2_prograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(propulsion_module, "STANDARD_GRAVITY", 9.81),
    )
    assert "ours_vs_gmat_mass_error_max_kg" in failures


def test_frozen_pointing_mutant_fails_o9(monkeypatch):
    held = {}

    def frozen(self, t, r, v):
        held.setdefault("u", np.array(v) / np.linalg.norm(v))
        return held["u"]

    failures = _mutant_failures(
        "m2_prograde_burn", monkeypatch, lambda mp: mp.setattr(Prograde, "direction", frozen)
    )
    assert "ours_vs_gmat_final_position_error_m" in failures


def test_swapped_direction_mutant_fails_o9(monkeypatch):
    laws = dict(simulator_module.DIRECTION_LAWS)
    laws["retrograde"] = laws["prograde"]
    failures = _mutant_failures(
        "m2_retrograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(simulator_module, "DIRECTION_LAWS", laws),
    )
    assert "ours_vs_gmat_burn_boundary_position_error_max_m" in failures


def test_cutoff_timing_mutant_fails_o9(monkeypatch):
    original = simulator_module.plan_burn

    def late(engine, propellant, ignition, duration, *a, **k):
        return original(engine, propellant, ignition, duration * (1 + 1e-9), *a, **k)

    failures = _mutant_failures(
        "m2_prograde_burn", monkeypatch, lambda mp: mp.setattr(simulator_module, "plan_burn", late)
    )
    assert (
        "ours_vs_gmat_mass_error_max_kg" in failures
        or "ours_vs_gmat_burn_boundary_position_error_max_m" in failures
    )


# ------------------------------------------------------------------ workflow


def test_run_refuses_to_replace_a_committed_reference():
    proc = subprocess.run(
        [sys.executable, str(CLI), "run", "--gmat-console", sys.executable, "--gmat-version", "x"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2 and "--replace-reason" in proc.stderr


def test_cli_refuses_missions_without_a_reference():
    proc = subprocess.run(
        [sys.executable, str(CLI), "compare", "--missions", "m2_burn_to_depletion"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


@pytest.mark.slow
@pytest.mark.skipif(
    not GMAT_CONSOLE.exists(), reason="GMAT R2026a not installed (CI never runs GMAT)"
)
@pytest.mark.parametrize("name", gmat_m2.GMAT_MISSIONS)
def test_gmat_reproduces_the_committed_report(tmp_path, name):
    files = gmat_m2.reference_files(name)
    report = tmp_path / "report.txt"
    script = tmp_path / "case.script"
    script.write_text(files["script"].read_text().replace(f"'{name}_report.txt'", f"'{report}'"))
    subprocess.run(
        [str(GMAT_CONSOLE), "--run", str(script)],
        cwd=GMAT_CONSOLE.parent,
        capture_output=True,
        check=True,
    )
    assert report.read_bytes() == files["report"].read_bytes()
