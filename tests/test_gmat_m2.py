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
    assert any("report_sha256" in v or "approved manifest" in v for v in _compare(name).violations)


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
    """Gate failures, plus coverage violations (e.g. a burn boundary at the wrong time)."""
    apply(monkeypatch)
    result = _compare(name)
    if result.violations:
        assert all("!=" in v or "expected" in v or "differ" in v for v in result.violations)
        return ["coverage", *result.violations]
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
    assert {"ours_vs_gmat_mass_error_max_kg", "coverage"} & set(failures)


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


# ------------------------------------------------------------------ review M2-T6 fixes


def _cli():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gmat_m2_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_refs(tmp_path):
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    return dst


def _rehash(dst, name, manifest=True):
    """Make metadata (and optionally the approved manifest) consistent with edited files."""
    import hashlib

    files = gmat_m2.reference_files(name, dst)
    meta = json.loads(files["metadata"].read_text())
    for key in ("script", "report", "console"):
        meta[f"{key}_sha256"] = hashlib.sha256(files[key].read_bytes()).hexdigest()
    files["metadata"].write_text(json.dumps(meta))
    if manifest:
        man = json.loads((dst / "APPROVED_DIGESTS.json").read_text())
        man["references"][name] = {
            k: meta[k] for k in ("script_sha256", "report_sha256", "console_sha256")
        }
        (dst / "APPROVED_DIGESTS.json").write_text(json.dumps(man))


def test_run_validates_a_staged_reference_and_replaces_nothing_on_failure(tmp_path, monkeypatch):
    """F1: a numerically bad GMAT output is rejected before anything is committed."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    before = {p.name: p.read_bytes() for p in dst.iterdir()}
    bad = tmp_path / "bad_report.txt"
    lines = gmat_m2.reference_files(name)["report"].read_text().splitlines()
    fields = lines[400].split()
    fields[2] = repr(float(fields[2]) + 1e-3)  # +1 m in x (km)
    lines[400] = " ".join(fields)
    bad.write_text("\n".join(lines) + "\n")
    console = tmp_path / "GmatConsole"
    console.write_text(
        "#!/bin/sh\n"
        'out=$(sed -n "s/^GMAT S.Filename = \'\\(.*\\)\';$/\\1/p" "$2")\n'
        f"cp '{bad}' \"$out\"\n"
        "echo '*** GMAT Integration test (Console version) successful! ***'\n"
    )
    console.chmod(0o755)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    cli = _cli()
    args = ["run", "--missions", name, "--gmat-console", str(console)]
    code = cli.main([*args, "--gmat-version", "R2026a", "--replace-reason", "test"])
    assert code == 1
    assert {p.name: p.read_bytes() for p in dst.iterdir()} == before


def test_numerical_gates_apply_to_a_consistent_but_wrong_reference(tmp_path, monkeypatch):
    """F1: the evaluation used by run and compare applies the numerical O9 gates."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    report = dst / f"{name}_report.txt"
    lines = report.read_text().splitlines()
    fields = lines[400].split()
    fields[2] = repr(float(fields[2]) + 1e-3)
    lines[400] = " ".join(fields)
    report.write_text("\n".join(lines) + "\n")
    _rehash(dst, name)
    rejected, check = _cli()._evaluate(name, base=dst)
    assert rejected == [] and check is not None and not check.passed


@pytest.mark.parametrize("edit", ["move", "duplicate", "drop"])
def test_state_assignments_must_stay_in_place_once(tmp_path, monkeypatch, edit):
    """F2: moving, duplicating or dropping an initial-state assignment is rejected."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    script = dst / f"{name}.script"
    lines = script.read_text().splitlines()
    state = [
        ln
        for ln in lines
        if ln.startswith("GMAT Sat.") and ln.split()[1][4:] in gmat_m2._STATE_KEYS
    ]
    if edit == "move":
        lines = [ln for ln in lines if ln not in state] + state
    elif edit == "duplicate":
        lines.append(state[0])
    else:
        lines.remove(state[0])
    script.write_text("\n".join(lines) + "\n")
    _rehash(dst, name)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert _compare(name).violations


@pytest.mark.parametrize(
    "change", ["drop_fields", "failed_console", "other_binary", "unapproved_digest"]
)
def test_provenance_is_required(tmp_path, monkeypatch, change):
    """F3: provenance fields, the approved binary, a successful bound console log and the
    approved-digest manifest are all required."""
    name = "m2_retrograde_burn"
    dst = _copy_refs(tmp_path)
    files = gmat_m2.reference_files(name, dst)
    if change == "drop_fields":
        meta = json.loads(files["metadata"].read_text())
        keep = ("scenario_hash", "constants", "script_sha256", "report_sha256")
        files["metadata"].write_text(json.dumps({k: meta[k] for k in keep}))
    elif change == "failed_console":
        files["console"].write_text("Execution Failed: not GMAT\n")
        _rehash(dst, name)
    elif change == "other_binary":
        meta = json.loads(files["metadata"].read_text())
        meta["gmat_console_sha256"] = "0" * 64
        files["metadata"].write_text(json.dumps(meta))
    else:
        lines = files["report"].read_text().splitlines()
        files["report"].write_text("\n".join(lines) + "\n\n")  # same rows, new digest
        _rehash(dst, name, manifest=False)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert _compare(name).violations


def test_fabricated_reference_needs_a_manifest_change(tmp_path, monkeypatch):
    """F3: DOP853 rows passed off as GMAT are numerically consistent; the reviewed
    manifest (and the reproduction test, where GMAT exists) are what reject them."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    scenario, predicted, arcs, rows = _labelled(name)
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    veh = m2.vehicle(scenario)
    out = []
    for t, row in sorted(labelled.items()):
        y = ref[t]
        mass = gmat_m2._expected_mass(t, veh, predicted)
        vals = [row.arc, row.a1mjd, *(y[:3] / 1e3), *(y[3:6] / 1e3), mass]
        out.append(" ".join(repr(float(x)) for x in vals))
    (dst / f"{name}_report.txt").write_text("\n".join(out) + "\n")
    _rehash(dst, name, manifest=False)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    violations = _compare(name).violations
    assert violations == ["reference digests are not in the approved manifest"]


def test_generate_never_writes_into_the_references(tmp_path, monkeypatch):
    """F4: generate writes previews only; run guards every existing artifact."""
    cli = _cli()
    assert cli.main(["generate", "--out", str(gmat_m2.reference_dir())]) == 2
    out = tmp_path / "preview"
    assert cli.main(["generate", "--out", str(out), "--missions", "m2_prograde_burn"]) == 0
    assert (out / "m2_prograde_burn.script").exists()
    dst = tmp_path / "m2"
    dst.mkdir()
    shutil.copy(gmat_m2.reference_files("m2_prograde_burn")["script"], dst)  # script only
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    code = cli.main(
        [
            "run",
            "--missions",
            "m2_prograde_burn",
            "--gmat-console",
            sys.executable,
            "--gmat-version",
            "x",
        ]
    )
    assert code == 2


@pytest.mark.parametrize("drop", ["StateSampled", "BurnEnded", "PropulsionSampled"])
def test_missing_observations_are_not_vacuous_passes(drop):
    """F5: O9 requires every expected observation, from the scenario."""
    name = "m2_prograde_burn"
    run = run_scenario(BY_NAME[name].build())
    keep_first = drop == "PropulsionSampled"
    events, seen = [], False
    for e in run.events:
        if e.type == drop and (not keep_first or seen):
            continue
        seen = seen or e.type == drop
        events.append(e)
    assert any(
        "expected" in v or "differ" in v or "!=" in v for v in _compare(name, events).violations
    )


def test_standalone_compare_fails_closed_without_thresholds(tmp_path, monkeypatch):
    """F6: missing O9 limits reject the comparison instead of passing it."""
    from tars.validation.thresholds import ScopedThresholds

    data = json.loads(M2_THRESHOLDS.read_text())
    del data["limits"]["o9_gmat"]["all"]["coast_vs_kepler_position_error_max_m"]
    cli = _cli()
    monkeypatch.setattr(
        cli, "load_scoped_thresholds", lambda **_: ScopedThresholds("provisional", data["limits"])
    )
    rejected, check = cli._evaluate("m2_prograde_burn")
    assert check is None and any("without a threshold" in r for r in rejected)


def _event_edit(events, kind, **update):
    first = next(i for i, e in enumerate(events) if kind(e))
    return [e.model_copy(update=update) if i == first else e for i, e in enumerate(events)]


ROW_CASES = {
    "step_spacing_error_max_s": ("a1mjd", 300, 1.0 / 86400.0),
    "burn_duration_from_mass_error_max_s": ("mass_kg", 88, -1e-6),  # burn-end row, 677.3 s
    "coast_vs_kepler_position_error_max_m": ("r", 300, 1e-3),
    "gmat_vs_dop853_position_error_max_m": ("r", 500, 1e-3),
    "gmat_vs_dop853_velocity_error_max_mps": ("v", 500, 1e-6),
    "gmat_vs_dop853_final_position_error_m": ("r", -1, 1e-3),
    "gmat_mass_vs_analytic_error_max_kg": ("mass_kg", 500, 1e-6),
}


def _at(kind, tick=None):
    return lambda e: e.type == kind and (tick is None or e.tick == tick)


_FAR = [1e7, 0.0, 0.0]
_FAST = [1e4, 0.0, 0.0]
EVENT_CASES = {
    "ours_vs_gmat_sample_position_error_max_m": (_at("StateSampled", 600), {"r": _FAR}),
    "ours_vs_gmat_sample_velocity_error_max_mps": (_at("StateSampled", 600), {"v": _FAST}),
    "ours_vs_gmat_burn_boundary_position_error_max_m": (_at("BurnEnded"), {"r": tuple(_FAR)}),
    "ours_vs_gmat_burn_boundary_velocity_error_max_mps": (_at("BurnEnded"), {"v": tuple(_FAST)}),
    "ours_vs_gmat_final_position_error_m": (_at("SimulationCompleted"), {"r": _FAR}),
    "ours_vs_gmat_final_velocity_error_mps": (_at("SimulationCompleted"), {"v": _FAST}),
    "ours_vs_gmat_mass_error_max_kg": (_at("PropulsionSampled", 64), {"total_mass_kg": 1290.0}),
    "ours_vs_gmat_node_crossing_error_max_s": (_at("OrbitCompleted"), {"crossing_t": 5000.0}),
}


def test_every_o9_metric_has_a_targeted_test():
    """F7: each gated O9 metric is exercised by its own corruption below."""
    assert set(ROW_CASES) | set(EVENT_CASES) == set(LIMITS["all"])


@pytest.mark.parametrize("metric", sorted(ROW_CASES))
def test_each_reference_metric_fails_on_its_corruption(metric):
    name = "m2_prograde_burn"
    scenario, predicted, arcs, rows = _labelled(name)
    field, index, delta = ROW_CASES[metric]
    index = index % len(rows)
    rows = [
        dataclasses.replace(r, **{field: getattr(r, field) + delta}) if i == index else r
        for i, r in enumerate(rows)
    ]
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    metrics |= gmat_m2.o9_metrics(scenario, predicted, run_scenario(scenario).events, labelled, ref)
    assert metrics[metric] > _limits(name)[metric]


@pytest.mark.parametrize("metric", sorted(EVENT_CASES))
def test_each_simulator_metric_fails_on_its_corruption(metric):
    name = "m2_prograde_burn"
    kind, update = EVENT_CASES[metric]
    events = _event_edit(run_scenario(BY_NAME[name].build()).events, kind, **update)
    scenario, predicted, arcs, rows = _labelled(name)
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    metrics = gmat_m2.o9_metrics(scenario, predicted, events, labelled, ref)
    assert metrics[metric] > _limits(name)[metric]


def test_split_script_requires_each_state_component_exactly_once():
    """F2 defense in depth: the position-preserving comparison also rejects these."""
    script = gmat_m2.reference_files("m2_prograde_burn")["script"].read_text()
    x_line = next(ln for ln in script.splitlines() if ln.startswith("GMAT Sat.X = "))
    with pytest.raises(ValueError, match="more than once"):
        gmat_m2.split_script(script + x_line + "\n")
    with pytest.raises(ValueError, match="incomplete"):
        gmat_m2.split_script(script.replace(x_line + "\n", ""))
