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
