"""M3 T2 S1, T-07: failure-path characterization (PC-7(S1) §8; I-40 OD-2; I-41).

Regression guards, green at BASE ``ee602c5`` and required unchanged after S1. They pin the
exception type, message and precedence of every failure path that ForceContext
construction sits on. Under I-41 (option B for the coast closure) no T-07 case changes,
including (a) and (b) at dt = +inf; (i) pins the finite-dt counterexample found in I-40
and (j) shows that dt = +inf admits no split tick. (k) pins the powered ordering (Review R-01)
and (l) the coast closure's insensitivity to float64 ndarray subclasses (Review R-02, I-44).
"""

import json
import math
import warnings

import numpy as np
import pytest
from pydantic import ValidationError

from tars.astro.elements import circular_orbit_state
from tars.sim.constants import WGS84
from tars.sim.forces import CompositeForceModel, PointMassGravity, ZonalJ2Gravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import BurnRejectedError, EngineSpec, SpacecraftSpec, TankSpec
from tars.sim.scenario import parse_scenario
from tars.sim.simulator import Simulator
from tests.conftest import M1_SCENARIO, M2_SLICE_SCENARIO

J2 = 1.08262668e-3
ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
R0, V0 = circular_orbit_state(
    radius=WGS84.equatorial_radius + 250_000.0,
    inclination=math.radians(51.6),
    raan=0.0,
    arg_latitude=0.0,
    mu=WGS84.mu,
)


def _spacecraft(dry=1000.0, prop=300.0, engine=ENGINE):
    return SpacecraftSpec(dry_mass_kg=dry, engine=engine, tank=TankSpec(propellant_kg=prop))


def _pm():
    return PointMassGravity(WGS84.mu)


def _pm_j2():
    return CompositeForceModel([_pm(), ZonalJ2Gravity(WGS84.mu, WGS84.equatorial_radius, J2)])


class _FreeSpace:
    name = "free_space"

    def acceleration(self, t, r, v):
        return np.zeros(3)


class _Raise:
    name = "raise"

    def __init__(self, exc):
        self.exc = exc

    def acceleration(self, t, r, v):
        raise self.exc


class _NanAfter:
    name = "nan_after"

    def __init__(self, t_fail):
        self.t_fail = t_fail

    def acceleration(self, t, r, v):
        return np.full(3, np.nan) if t >= self.t_fail else _pm().acceleration(t, r, v)


def _assert_unchanged(sim, r, v):
    assert sim.tick == 0
    np.testing.assert_array_equal(sim.snapshot().r, r)
    np.testing.assert_array_equal(sim.snapshot().v, v)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_t07_a_infinite_dt_coast_point_mass_is_non_finite():
    sim = Simulator(R0, V0, _pm(), RK4(), math.inf, spacecraft=_spacecraft())
    with pytest.raises(FloatingPointError, match=r"^non-finite state produced at tick 1$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_t07_b_infinite_dt_coast_point_mass_and_j2_fails_in_j2():
    sim = Simulator(R0, V0, _pm_j2(), RK4(), math.inf, spacecraft=_spacecraft())
    with pytest.raises(ValueError, match=r"^position must be finite$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_t07_c_infinite_dt_m1_path_is_non_finite():
    sim = Simulator(R0, V0, _pm(), RK4(), math.inf)
    with pytest.raises(FloatingPointError, match=r"^non-finite state produced at tick 1$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)


def test_t07_d_non_finite_powered_stage_fails_before_any_mass_use():
    sim = Simulator(R0, V0, _NanAfter(1.5), RK4(), 10.0, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", ignition_t_s=1.0, duration_s=2.0)
    with pytest.raises(FloatingPointError, match=r"^non-finite state during a burn at t = 2\.0$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)


def test_t07_e_thrust_over_mass_overflow():
    engine = EngineSpec(thrust_n=1e100, isp_s=1e100)
    sim = Simulator(R0, V0, _pm(), RK4(), 1e-300, spacecraft=_spacecraft(1e-300, 1e-300, engine))
    sim.schedule_burn("prograde", 0.0, 1e-300, policy="burn_to_depletion")
    with pytest.raises(FloatingPointError, match=r"^thrust acceleration overflows at t = 0\.0$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)


@pytest.mark.parametrize("exc_type", [OverflowError, ZeroDivisionError])
@pytest.mark.parametrize("path", ["m1", "coast", "powered"])
def test_t07_f_python_arithmetic_errors_are_converted_by_step(exc_type, path):
    original = exc_type("sentinel")
    craft = None if path == "m1" else _spacecraft()
    sim = Simulator(R0, V0, _Raise(original), RK4(), 10.0, spacecraft=craft)
    if path == "powered":
        sim.schedule_burn("prograde", 0.0, 5.0)
    expected = r"^numerical overflow at tick 1: sentinel$"
    with pytest.raises(FloatingPointError, match=expected) as err:
        sim.step()
    assert err.value.__cause__ is original
    _assert_unchanged(sim, R0, V0)


@pytest.mark.parametrize("path", ["m1", "coast", "powered"])
def test_t07_f_other_force_errors_propagate_as_the_identical_object(path):
    original = ValueError("sentinel")
    craft = None if path == "m1" else _spacecraft()
    sim = Simulator(R0, V0, _Raise(original), RK4(), 10.0, spacecraft=craft)
    if path == "powered":
        sim.schedule_burn("prograde", 0.0, 5.0)
    with pytest.raises(ValueError) as err:
        sim.step()
    assert err.value is original
    _assert_unchanged(sim, R0, V0)


def test_t07_g_pointing_law_error_precedes_the_force_model():
    sim = Simulator(
        R0, np.zeros(3), _Raise(RuntimeError("force")), RK4(), 10.0, spacecraft=_spacecraft()
    )
    sim.schedule_burn("prograde", 0.0, 5.0)
    with pytest.raises(
        ValueError, match=r"^velocity-tracking direction is undefined for zero velocity$"
    ):
        sim.step()
    _assert_unchanged(sim, R0, np.zeros(3))


@pytest.mark.parametrize("path", [M1_SCENARIO, M2_SLICE_SCENARIO])
@pytest.mark.parametrize("dt", [math.inf, -math.inf, math.nan])
def test_t07_h_scenarios_reject_non_finite_dt(path, dt):
    data = json.loads(path.read_text())
    data["dt_s"] = dt
    with pytest.raises(ValidationError, match="dt_s"):
        parse_scenario(json.dumps(data))


def _overflowing_tick_end(dt):
    """I-40 counterexample: finite dt, tick 2 ends at (1 + 1) dt = +inf, so the last coast
    sub-step of a split tick has infinite length (NaN stage propellant)."""
    engine = EngineSpec(thrust_n=5e-324, isp_s=1e-10)  # F/m underflows to 0: r stays finite
    sim = Simulator(
        np.array([7e6, 0.0, 0.0]),
        np.array([0.0, 1e-290, 0.0]),
        _FreeSpace(),
        RK4(),
        dt,
        spacecraft=_spacecraft(engine=engine),
    )
    sim.step()
    assert sim.tick == 1 and math.isfinite(sim.t) and (sim.tick + 1) * sim.dt == math.inf
    sim.schedule_burn("prograde", sim.t * 1.2, sim.t * 0.1, policy="burn_to_depletion")
    return sim


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.parametrize("dt", [1e308, 8.98846567431158e307])
def test_t07_i_finite_dt_with_overflowing_tick_end_is_non_finite(dt):
    sim = _overflowing_tick_end(dt)
    before = (sim.snapshot(), sim.propulsion_snapshot())
    with pytest.raises(FloatingPointError, match=r"^non-finite state produced at tick 2$"):
        sim.step()
    assert sim.tick == 1 and sim.propulsion_snapshot() == before[1]
    np.testing.assert_array_equal(sim.snapshot().r, before[0].r)


def test_t07_j_infinite_dt_admits_no_burn_so_no_split_tick():
    """dt = +inf: t = 0 * inf is NaN, so every burn is schema-invalid and a split tick (whose
    last coast sub-step would have infinite length) cannot arise; (a)/(b) are the only
    infinite-dt coast paths."""
    sim = Simulator(R0, V0, _pm(), RK4(), math.inf, spacecraft=_spacecraft())
    assert math.isnan(sim.t)
    with pytest.raises(BurnRejectedError, match=r"^schema_invalid: earliest_t_s must be finite"):
        sim.schedule_burn("prograde", 1.0, 2.0)
    assert sim.propulsion_snapshot().pending_burn_ids == ()


class _StageWriter:
    """Legacy model that writes into the RK4 stage array behind its r view (stage arrays
    are writable; only the committed state is read-only, REV-004)."""

    name = "stage_writer"

    def __init__(self, t_write, index, value):
        self.t_write, self.index, self.value = t_write, index, value

    def acceleration(self, t, r, v):
        if t == self.t_write and r.base is not None and r.base.flags.writeable:
            r.base[self.index] = self.value
        return np.zeros(3)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_t07_k_finiteness_check_precedes_powered_context_construction(value):
    """Review R-01 (I-41): a stage propellant made non-finite by a model is reported by the
    powered closure's finiteness check, before any context exists (pins I-39A §10 M-14)."""
    model = _StageWriter(1.0, 6, value)
    sim = Simulator(R0, V0, model, RK4(), 10.0, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", ignition_t_s=1.0, duration_s=2.0)
    before = (sim.snapshot(), sim.propulsion_snapshot())
    with pytest.raises(FloatingPointError, match=r"^non-finite state during a burn at t = 2\.0$"):
        sim.step()
    _assert_unchanged(sim, R0, V0)
    assert sim.propulsion_snapshot() == before[1] and sim.engine_transitions == ()


class _RaisingGetitem(np.ndarray):
    """float64 ndarray subclass (inside Integrator's NDArray[np.float64] annotation) whose
    scalar read of the stage propellant raises."""

    def __getitem__(self, key):
        if key == 6:
            raise LookupError("stage propellant read through the subclass")
        return super().__getitem__(key)


def _masked_propellant(y):
    return np.ma.array(y, mask=[False] * 6 + [True, False])


def _raising_getitem(y):
    return y.view(_RaisingGetitem)


class _WrappingEuler:
    """Custom integrator: one forward-Euler derivative call on a wrapped copy of the state."""

    name, order = "euler_wrapped", 1

    def __init__(self, wrap):
        self.wrap = wrap

    def step(self, f, t, y, dt):
        return y + dt * np.asarray(f(t, self.wrap(y.copy())), dtype=float)


@pytest.mark.parametrize(
    "wrap", [_masked_propellant, _raising_getitem], ids=["masked_propellant", "raising_getitem"]
)
def test_t07_l_coast_closure_does_not_read_the_stage_through_a_subclass(wrap):
    """Review R-02 (I-44): BASE's coast closure never indexes the stage propellant, so a
    custom integrator's float64 subclass stage commits with no warning. It still does, with
    warnings raised as errors, and the committed state equals the unwrapped integrator's."""
    craft = _spacecraft()
    plain = Simulator(R0, V0, _FreeSpace(), _WrappingEuler(np.asarray), 0.5, spacecraft=craft)
    plain.step()
    sim = Simulator(R0, V0, _FreeSpace(), _WrappingEuler(wrap), 0.5, spacecraft=craft)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        sim.step()
    assert sim.tick == 1
    got, want = sim.snapshot(), plain.snapshot()
    for a, b in ((got.r, want.r), (got.v, want.v)):
        assert [x.hex() for x in a.tolist()] == [x.hex() for x in b.tolist()]
    assert sim.propulsion_snapshot() == plain.propulsion_snapshot()
