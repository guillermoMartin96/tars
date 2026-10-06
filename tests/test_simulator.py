import math

import numpy as np
import pytest

from tars.astro.kepler import propagate
from tars.sim.constants import WGS84
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.simulator import AscendingNodeDetector, Simulator, _hermite_root
from tars.sim.state import StateSnapshot

R0 = np.array([6628137.0, 0.0, 0.0])
V0 = np.array([0.0, 7754.845 * math.cos(0.9), 7754.845 * math.sin(0.9)])


def _sim(dt=10.0, detectors=()):
    return Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), dt, detectors)


def test_time_comes_from_integer_ticks():
    sim = _sim(dt=0.1)
    for _ in range(1000):
        sim.step()
    assert sim.tick == 1000
    assert sim.t == 1000 * 0.1  # exactly n*dt, no accumulated rounding


def test_no_public_api_mutates_physical_state():
    """Architecture invariant 1: state changes only through step()."""
    sim = _sim()
    public = {name for name in dir(sim) if not name.startswith("_")}
    assert public == {"dt", "tick", "t", "snapshot", "step"}
    for prop in ("dt", "tick", "t"):
        with pytest.raises(AttributeError):
            setattr(sim, prop, 0)
    snap = sim.snapshot()
    with pytest.raises(ValueError):
        snap.v[0] = 1.0
    np.testing.assert_array_equal(sim.snapshot().v, V0)


def test_single_step_local_error_is_fifth_order():
    """RK4 local (one-step) error is O(dt^5): halving dt divides it by ~2^5 = 32."""

    def one_step_error(dt):
        sim = _sim(dt=dt)
        sim.step()
        r_ref, _ = propagate(R0, V0, dt, WGS84.mu)
        return np.linalg.norm(sim.snapshot().r - r_ref)

    ratio = one_step_error(20.0) / one_step_error(10.0)
    assert ratio == pytest.approx(32.0, rel=0.05)


def test_rejects_invalid_dt():
    with pytest.raises(ValueError):
        Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 0.0)


def test_non_finite_state_raises():
    class Explode:
        name = "explode"

        def acceleration(self, t, r, v):
            return np.array([np.inf, 0.0, 0.0])

    sim = Simulator(R0, V0, Explode(), RK4(), 1.0)
    with pytest.raises(FloatingPointError):
        sim.step()
    assert sim.tick == 0  # state not advanced


@pytest.mark.parametrize(
    "p0,m0,p1,m1", [(-1.0, 2.0, 1.0, 2.0), (-0.3, 0.1, 2.0, 5.0), (-1e-9, 1.0, 1.0, 1.0)]
)
def test_hermite_root(p0, m0, p1, m1):
    s = _hermite_root(p0, m0, p1, m1)
    assert 0.0 <= s <= 1.0
    value = (
        (2 * s**3 - 3 * s**2 + 1) * p0
        + (s**3 - 2 * s**2 + s) * m0
        + (-2 * s**3 + 3 * s**2) * p1
        + (s**3 - s**2) * m1
    )
    assert abs(value) < 1e-12


def test_ascending_node_detector_interpolates_crossing():
    # Straight-line motion z(t) = -5 + 2 t crosses at t = 2.5 exactly.
    det = AscendingNodeDetector()
    prev = StateSnapshot(tick=2, t=2.0, r=[0, 0, -1.0], v=[0, 0, 2.0])
    curr = StateSnapshot(tick=3, t=3.0, r=[0, 0, 1.0], v=[0, 0, 2.0])
    found = det.observe(prev, curr)
    assert found.crossing_t == pytest.approx(2.5, abs=1e-14) and found.tick == 3
    assert det.observe(curr, prev) is None  # descending crossing is ignored


def test_force_models_cannot_mutate_simulator_state():
    """REV-004: a force model mutating its r/v arguments must not corrupt owned state."""

    class Rogue:
        name = "rogue"

        def acceleration(self, t, r, v):
            v += 1.0
            return np.zeros(3)

    sim = Simulator(R0, V0, Rogue(), RK4(), 10.0)
    with pytest.raises(ValueError):
        sim.step()
    np.testing.assert_array_equal(sim.snapshot().v, V0)
