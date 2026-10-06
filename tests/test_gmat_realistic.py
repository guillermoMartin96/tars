"""Tests for the informational realistic-model GMAT tooling (DR-0005; not an M1 gate)."""

import json

import numpy as np
import pytest

from tars.sim.runner import run_scenario
from tars.validation import gmat_realistic as gr
from tests.conftest import REPO_ROOT

INFO = REPO_ROOT / "toolbox" / "references" / "gmat" / "informational"


def test_ric_decomposition():
    r, v = np.array([7e6, 0.0, 0.0]), np.array([0.0, 7.5e3, 0.0])
    assert gr.ric(np.array([1.0, 2.0, 3.0]), r, v) == pytest.approx((1.0, 2.0, 3.0))


def test_analytic_j2_rate_matches_sci_0001(m1_scenario):
    c = m1_scenario.constants
    rate = gr.analytic_j2_raan_rate_deg_per_day(6628137.0, 51.6, c.mu, c.equatorial_radius)
    assert rate == pytest.approx(-5.41, abs=0.005)


def test_scripts_configure_each_case(m1_scenario):
    by_name = {c.name: gr.realistic_script(m1_scenario, c, "r.txt") for c in gr.CASES}
    assert "GMAT FM.GravityField.Earth.Degree = 2;" in by_name["j2_only"]
    assert "GMAT FM.GravityField.Earth.Order = 0;" in by_name["j2_only"]
    assert "GMAT FM.Drag = None;" in by_name["gravity_4x4"]
    assert "GMAT FM.Drag.F107 = 150.0;" in by_name["realistic_f150"]
    assert "GMAT FM.Drag.AtmosphereModel = JacchiaRoberts;" in by_name["realistic_f70"]
    assert all("np." not in s and "INFORMATIONAL" in s for s in by_name.values())


def test_committed_summary_is_reproducible_from_committed_reports(m1_scenario):
    metadata = json.loads((INFO / "metadata.json").read_text())
    assert metadata["scenario_hash"] == m1_scenario.config_hash()
    summary = json.loads((INFO / "summary.json").read_text())
    samples = run_scenario(m1_scenario).samples
    for case in gr.CASES:
        rows = gr.parse_report((INFO / f"{case.name}_report.txt").read_text())
        assert len(rows) == 896
        got = gr.divergence(rows, samples, m1_scenario)
        for key, value in summary[case.name].items():
            assert got[key] == pytest.approx(value, rel=1e-9, abs=1e-6), (case.name, key)
