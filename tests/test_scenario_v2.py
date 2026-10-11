"""Scenario schema version 2 (M2 task T4; DR-0010, DR-0014)."""

import copy
import json

import pytest
from pydantic import ValidationError

from tars.sim.scenario import Scenario, ScenarioV2, load_scenario, parse_scenario
from tests.conftest import M1_SCENARIO, M2_SLICE_SCENARIO

M1_SCENARIO_HASH = "603152ad308651aed1bc5193a81cb249b7d5770fb0f0fb76ab0356c44ff281bd"


def _slice() -> dict:
    return json.loads(M2_SLICE_SCENARIO.read_text())


def _parse(data: dict):
    return parse_scenario(json.dumps(data))


def test_slice_scenario_matches_dr_0010():
    s = load_scenario(M2_SLICE_SCENARIO)
    assert type(s) is ScenarioV2 and s.schema_version == 2
    assert (s.initial_orbit.altitude_m, s.initial_orbit.inclination_deg) == (250000.0, 51.6)
    assert s.dt_s == 10.0 and s.integrator == "rk4" and s.force_models == ("point_mass_gravity",)
    sc = s.spacecraft
    assert (sc.dry_mass_kg, sc.propellant_kg) == (1000.0, 300.0)
    assert (sc.engine.thrust_n, sc.engine.isp_s) == (490.0, 312.0)
    assert s.stop.duration_s == 53700.0 and s.stop.orbits is None and s.stop_tick == 5370
    (entry,) = s.commands
    assert entry.submit_t_s == 0.0
    assert entry.command["ignition_t_s"] == 600.0 and entry.command["duration_s"] == 77.3
    assert entry.command["direction"] == "prograde"


def test_version_1_is_unchanged():
    s = load_scenario(M1_SCENARIO)
    assert type(s) is Scenario
    assert s.config_hash() == M1_SCENARIO_HASH  # recorded in proof/references


@pytest.mark.parametrize(
    "extra",
    [
        {"spacecraft": {"dry_mass_kg": 1.0, "propellant_kg": 0.0, "engine": {}}},
        {"commands": []},
        {"stop": {"orbits": 10, "duration_s": 100.0}},
    ],
)
def test_version_1_does_not_accept_version_2_fields(extra):
    data = {**json.loads(M1_SCENARIO.read_text()), **extra}
    with pytest.raises(ValidationError):
        _parse(data)


@pytest.mark.parametrize("version", [2.0, "2", True, None, 3])
def test_only_the_integer_2_selects_version_2(version):
    data = {**_slice(), "schema_version": version}
    with pytest.raises(ValidationError):
        _parse(data)
    with pytest.raises(ValidationError):
        ScenarioV2.model_validate(data)


def test_version_2_without_propulsion_is_allowed():
    data = _slice()
    del data["spacecraft"], data["commands"]
    s = _parse(data)
    assert s.spacecraft is None and s.commands == ()


@pytest.mark.parametrize(
    "stop",
    [
        {},
        {"orbits": 1, "duration_s": 100.0},
        {"duration_s": 100.0, "max_duration_periods": 1.1},
        {"duration_s": 0.0},
        {"duration_s": -10.0},
        {"duration_s": 15.0},  # not a multiple of dt = 10 s
        {"duration_s": 1e-300},
        {"duration_s": True},
        {"duration_s": "100"},
        {"orbits": 0},
        {"orbits": 1.5},
        {"orbits": True},
    ],
)
def test_invalid_stop_rejected(stop):
    with pytest.raises(ValidationError):
        _parse({**_slice(), "stop": stop})


@pytest.mark.parametrize("raw", ['{"duration_s": Infinity}', '{"duration_s": NaN}'])
def test_non_finite_stop_rejected(raw):
    text = json.dumps({**_slice(), "stop": "__STOP__"}).replace('"__STOP__"', raw)
    with pytest.raises(ValidationError):
        parse_scenario(text)


def test_orbits_stop_in_version_2():
    s = _parse({**_slice(), "stop": {"orbits": 2}})
    assert s.stop.orbits == 2 and s.stop_tick is None and s.stop.max_duration_periods == 1.1


def test_tick_grid_is_exact():
    """Time is tick * dt (ADR-0002): stop and submission times must be exactly
    n * dt_s, not merely close (no rounding rule to document or get wrong)."""
    data = {**_slice(), "dt_s": 0.1, "telemetry": {"sample_interval_s": 0.1}}
    data["commands"] = []
    assert _parse({**data, "stop": {"duration_s": 0.5}}).stop_tick == 5  # 5 * 0.1 == 0.5
    with pytest.raises(ValidationError, match="tick grid"):
        _parse({**data, "stop": {"duration_s": 0.3}})  # 3 * 0.1 == 0.30000000000000004


@pytest.mark.parametrize(
    "times,match",
    [
        ([5.0], "tick grid"),
        ([-10.0], "greater than or equal"),
        ([20.0, 10.0], "non-decreasing"),
        ([53700.0], "at or after the stop"),
        ([60000.0], "at or after the stop"),
    ],
)
def test_invalid_submit_times_rejected(times, match):
    data = _slice()
    entry = data["commands"][0]
    data["commands"] = [{**copy.deepcopy(entry), "submit_t_s": t} for t in times]
    with pytest.raises(ValidationError, match=match):
        _parse(data)


def test_equal_submit_times_keep_file_order():
    data = _slice()
    entry = data["commands"][0]
    data["commands"] = [
        {"submit_t_s": 10.0, "command": {**entry["command"], "command_id": f"c{i}"}}
        for i in range(3)
    ]
    s = _parse(data)
    assert [e.command["command_id"] for e in s.commands] == ["c0", "c1", "c2"]


def test_command_payload_is_not_validated_by_the_scenario():
    """The simulator is the only command validator: invalid commands are representable."""
    data = _slice()
    data["commands"] = [
        {"command": {"type": "BurnCommand", "unexpected": [1, {"x": True}], "duration_s": "7"}},
        {"command": {}},
    ]
    s = _parse(data)
    assert s.commands[0].command["unexpected"] == [1, {"x": True}]
    assert s.commands[0].submit_t_s == 0.0  # default


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_command_payload_must_be_standard_json(token):
    """Non-finite numbers would serialize ambiguously in the canonical form (hash)."""
    data = _slice()
    data["commands"][0]["command"]["duration_s"] = "__X__"
    text = json.dumps(data).replace('"__X__"', token)
    with pytest.raises(ValidationError, match="non-finite"):
        parse_scenario(text)
    nested = json.dumps({**_slice(), "commands": [{"command": {"a": ["__X__"]}}]})
    with pytest.raises(ValidationError, match="non-finite"):
        parse_scenario(nested.replace('"__X__"', token))


@pytest.mark.parametrize(
    "command",
    [[], "BurnCommand", None, 1],
)
def test_command_payload_must_be_an_object(command):
    data = _slice()
    data["commands"] = [{"command": command}]
    with pytest.raises(ValidationError):
        _parse(data)


@pytest.mark.parametrize(
    "spacecraft",
    [
        {"dry_mass_kg": 0.0, "propellant_kg": 1.0, "engine": {"thrust_n": 1.0, "isp_s": 1.0}},
        {"dry_mass_kg": 1.0, "propellant_kg": -1.0, "engine": {"thrust_n": 1.0, "isp_s": 1.0}},
        {"dry_mass_kg": 1.0, "propellant_kg": 1.0, "engine": {"thrust_n": 0.0, "isp_s": 1.0}},
        {"dry_mass_kg": 1.0, "propellant_kg": 1.0, "engine": {"thrust_n": 1.0, "isp_s": -1.0}},
        {"dry_mass_kg": True, "propellant_kg": 1.0, "engine": {"thrust_n": 1.0, "isp_s": 1.0}},
        {"dry_mass_kg": "1", "propellant_kg": 1.0, "engine": {"thrust_n": 1.0, "isp_s": 1.0}},
        {"dry_mass_kg": 1.0, "propellant_kg": 1.0, "engine": {"thrust_n": 1.0}},
        {"dry_mass_kg": 1.0, "propellant_kg": 1.0, "engine": {"thrust_n": 1, "isp_s": 1, "x": 1}},
        # Finite inputs whose derived mass flow F/(Isp g0) overflows (REV-T1-02).
        {"dry_mass_kg": 1.0, "propellant_kg": 1.0, "engine": {"thrust_n": 1e308, "isp_s": 1e-5}},
        {"dry_mass_kg": 1e308, "propellant_kg": 1e308, "engine": {"thrust_n": 1.0, "isp_s": 1.0}},
    ],
)
def test_invalid_spacecraft_rejected(spacecraft):
    with pytest.raises(ValidationError):
        _parse({**_slice(), "spacecraft": spacecraft})


def test_spacecraft_spec_conversion():
    spec = load_scenario(M2_SLICE_SCENARIO).spacecraft.to_spec()
    assert spec.dry_mass_kg == 1000.0 and spec.tank.propellant_kg == 300.0
    assert spec.engine.thrust_n == 490.0 and spec.engine.isp_s == 312.0


def test_integer_json_numbers_are_accepted_as_floats():
    data = _slice()
    engine = {"thrust_n": 490, "isp_s": 312}
    data["spacecraft"] = {"dry_mass_kg": 1000, "propellant_kg": 300, "engine": engine}
    data["stop"] = {"duration_s": 53700}
    s = _parse(data)
    assert type(s.spacecraft.dry_mass_kg) is float and type(s.stop.duration_s) is float
    # Same values, same canonical form: the hash does not depend on "1000" vs "1000.0".
    assert s.config_hash() == load_scenario(M2_SLICE_SCENARIO).config_hash()


def test_config_hash_covers_the_timeline_and_spacecraft():
    base = _parse(_slice()).config_hash()
    for mutate in (
        lambda d: d["commands"][0]["command"].update(duration_s=77.4),
        lambda d: d["commands"][0].update(submit_t_s=10.0),
        lambda d: d["spacecraft"].update(propellant_kg=299.0),
        lambda d: d["stop"].update(duration_s=53710.0),
    ):
        data = _slice()
        mutate(data)
        assert _parse(data).config_hash() != base


@pytest.mark.parametrize("text", ["not json", "[1, 2]", '{"schema_version": 2'])
def test_malformed_files_raise_validation_errors(text):
    with pytest.raises(ValidationError):
        parse_scenario(text)
