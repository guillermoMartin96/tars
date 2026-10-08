import json

import pytest
from pydantic import ValidationError

from tars.sim.scenario import Scenario
from tests.conftest import M1_SCENARIO


def test_m1_scenario_matches_dr_0007(m1_scenario):
    s = m1_scenario
    assert s.initial_orbit.altitude_m == 250000.0
    assert s.initial_orbit.inclination_deg == 51.6
    assert (s.initial_orbit.raan_deg, s.initial_orbit.arg_latitude_deg) == (0.0, 0.0)
    assert s.epoch == "2026-01-01T00:00:00" and s.time_scale == "TT"
    assert s.earth_constants == "WGS84"
    assert s.force_models == ("point_mass_gravity",)
    assert s.integrator == "rk4" and s.dt_s == 10.0
    assert s.stop.orbits == 10
    assert s.sample_every_ticks == 6


def test_config_hash_is_stable_and_sensitive(m1_scenario):
    assert m1_scenario.config_hash() == m1_scenario.config_hash()
    assert m1_scenario.with_dt(5.0).config_hash() != m1_scenario.config_hash()


@pytest.mark.parametrize(
    "patch",
    [
        {"dt_s": 0.0},
        {"telemetry": {"sample_interval_s": 15.0}},  # not a multiple of dt
        {"integrator": "euler"},
        {"force_models": ["j2"]},
        {"earth_constants": "EGM96"},
        {"unexpected_field": 1},
        {
            "initial_orbit": {
                "kind": "circular",
                "altitude_m": -1.0,
                "inclination_deg": 0,
                "raan_deg": 0,
                "arg_latitude_deg": 0,
            }
        },
    ],
)
def test_invalid_scenarios_rejected(patch):
    data = {**json.loads(M1_SCENARIO.read_text()), **patch}
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


@pytest.mark.parametrize("inc", [0.0, 180.0])
def test_equatorial_orbits_rejected(inc):
    """REV-007: ascending-node orbit counting needs a non-equatorial orbit."""
    data = json.loads(M1_SCENARIO.read_text())
    data["initial_orbit"]["inclination_deg"] = inc
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize(
    "section,field",
    [
        ("initial_orbit", "altitude_m"),
        ("stop", "max_duration_periods"),
        ("telemetry", "sample_interval_s"),
        (None, "dt_s"),
    ],
)
def test_non_finite_scenario_numbers_rejected(section, field, value):
    data = json.loads(M1_SCENARIO.read_text())
    target = data if section is None else data[section]
    target[field] = value
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)
    with pytest.raises(ValidationError):
        Scenario.model_validate_json(json.dumps(data))
