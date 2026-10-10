"""REV-012 / DR-0016 evidence is reproducible from the committed GMAT reports (VAL-0010).

GMAT is not needed: the reports under docs/science/experiments/rev-012/reports are
re-analysed with the investigation harness. These tests check that recorded evidence
reproduces; they are not physics accuracy gates.
"""

import importlib.util
import json

import numpy as np
import pytest

from tars.sim.scenario import load_scenario
from tests.conftest import REPO_ROOT

EVIDENCE = REPO_ROOT / "docs" / "science" / "experiments" / "rev-012"


@pytest.fixture(scope="module")
def harness():
    spec = importlib.util.spec_from_file_location("rev012", EVIDENCE / "rev012.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def recorded():
    return json.loads((EVIDENCE / "results.json").read_text())


@pytest.fixture(scope="module")
def mu(harness):
    return load_scenario(str(harness.SCENARIO)).constants.mu


@pytest.fixture(scope="module")
def attribution(harness, mu):
    out = {}
    for case in ("burn_m1tt_77.3", "aligned_m1tt_77.3"):
        out[case] = harness.attribution(case, harness.analyze_burn(case, mu), mu)
    return out


def test_attribution_reproduces_recorded_evidence(attribution, recorded):
    """Recomputed GMAT-vs-DOP853 differences equal the recorded ones.

    rel 1e-6 allows only for platform-dependent last bits of the DOP853 reference
    (DR-0006); any change in method or data would differ by orders of magnitude more.
    """
    for case, result in attribution.items():
        for key in (
            "gmat_vs_dop853_nominal_final_pos_m",
            "gmat_vs_dop853_nominal_final_vel_mps",
            "gmat_vs_dop853_with_measured_offsets_final_pos_m",
        ):
            assert result[key] == pytest.approx(recorded["attribution"][case][key], rel=1e-6, abs=0)


def test_aligned_stepping_gives_the_reported_improvement(attribution):
    """DR-0016: about 1.2 cm (natural stepping, the VAL-0009 probe) to 12 um (aligned).

    Checked at the precision the figures were reported: 1.17 cm and 12 um.
    """
    natural = attribution["burn_m1tt_77.3"]["gmat_vs_dop853_nominal_final_pos_m"]
    aligned = attribution["aligned_m1tt_77.3"]["gmat_vs_dop853_nominal_final_pos_m"]
    assert round(natural * 100, 2) == 1.17  # cm
    assert round(aligned * 1e6) == 12  # um
    # Natural stepping's residual is the microsecond stop rounding: with GMAT's measured
    # boundary offsets applied, the reference agrees at the aligned level.
    corrected = attribution["burn_m1tt_77.3"]["gmat_vs_dop853_with_measured_offsets_final_pos_m"]
    assert corrected < aligned


def test_microsecond_stop_rounding_predicts_every_burn_duration(harness, mu):
    """Mechanism M-b predicts GMAT's burn duration (from its mass) in all 35 natural cases.

    Bound: duration is inferred from two mass readings, each resolved to ulp(m0), so
    the measurement resolution is 2 ulp(1300 kg) / mdot (about 2.8e-12 s).
    """
    resolution = 2.0 * float(np.spacing(1300.0)) / harness.MDOT
    natural = [name for name in harness.BURN_CASES if name.startswith("burn_")]
    assert len(natural) == 35
    for name in natural:
        burn = harness.analyze_burn(name, mu)
        measured = burn["burn_duration_from_mass_minus_nominal_s"]
        assert abs(measured - burn["model_M_b_duration_minus_nominal_s"]) <= resolution
    probe = harness.analyze_burn("burn_m1tt_77.3", mu)["burn_duration_from_mass_minus_nominal_s"]
    assert probe == pytest.approx(-1.847e-7, abs=1e-10)  # the VAL-0009 shortfall
