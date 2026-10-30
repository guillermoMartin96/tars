"""M3 T2 S1: ForceContext, the context-aware protocol and the legacy adapter (DQ-3 (a),
DQ-5 (a); PC-7(S1) §9a T-01 … T-06; I-41 option B for the coast closure; I-44 owned coast
snapshot).

The new interface is imported inside each test, so before S1 every test fails on its own
(AttributeError from the absent name), never as a collection error.
"""

import gc
import math
import random
import weakref

import numpy as np
import pytest

from tars.astro.elements import circular_orbit_state
from tars.sim import forces
from tars.sim import simulator as simulator_module
from tars.sim.constants import WGS84
from tars.sim.forces import PointMassGravity, ZonalJ2Gravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec, SpacecraftSpec, TankSpec
from tars.sim.simulator import Simulator

J2 = 1.08262668e-3
DRY, PROP = 1000.0, 300.0
ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
R0, V0 = circular_orbit_state(
    radius=WGS84.equatorial_radius + 250_000.0,
    inclination=math.radians(51.6),
    raan=0.0,
    arg_latitude=0.0,
    mu=WGS84.mu,
)
INVALID = [math.nan, math.inf, -math.inf, 0.0, -0.0, -1.0, -5e-324]


def _spacecraft(prop=PROP):
    return SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=prop))


# ------------------------------------------------------------------ T-01 (U-1, INV-5)


def test_t01_a_context_is_immutable():
    ctx = forces.ForceContext(1300.0)
    with pytest.raises(AttributeError):
        ctx.total_mass_kg = 1.0
    with pytest.raises(AttributeError):
        ctx._mass = 1.0
    with pytest.raises(AttributeError):
        del ctx._mass
    with pytest.raises(AttributeError):
        ctx.extra = 1
    assert not hasattr(ctx, "__dict__")
    assert ctx.total_mass_kg == 1300.0


@pytest.mark.parametrize(
    "mass", [1300, np.float64(1300.0), np.float32(1300.0), np.int64(1300), np.array(1300.0)]
)
def test_t01_b_mass_is_an_owned_builtin_float(mass):
    for ctx in (forces.ForceContext(mass), forces.ForceContext.deferred(mass)):
        assert type(ctx.total_mass_kg) is float
        assert ctx.total_mass_kg == 1300.0


@pytest.mark.parametrize("mass", [True, False, np.bool_(True), "1300", [1300.0], object()])
def test_t01_b_unsupported_mass_types_raise_type_error(mass):
    with pytest.raises(TypeError):
        forces.ForceContext(mass)
    with pytest.raises(TypeError):
        forces.ForceContext.deferred(mass)


@pytest.mark.parametrize("mass", INVALID)
def test_t01_c_invalid_mass_is_rejected_at_construction(mass):
    with pytest.raises(ValueError, match="total_mass_kg must be finite and positive"):
        forces.ForceContext(mass)


@pytest.mark.parametrize("mass", INVALID)
def test_t01_c_deferred_invalid_mass_is_rejected_when_read(mass):
    ctx = forces.ForceContext.deferred(mass)  # construction accepts it (I-41)
    for _ in range(2):  # every read rejects it; nothing is cached or coerced
        with pytest.raises(ValueError, match="total_mass_kg must be finite and positive"):
            ctx.total_mass_kg  # noqa: B018


def test_t01_d_absent_mass_is_none_never_zero():
    ctx = forces.ForceContext()
    assert ctx.total_mass_kg is None
    assert forces.ForceContext(None).total_mass_kg is None
    with pytest.raises(ValueError):
        forces.ForceContext(0.0)


@pytest.mark.parametrize("mass", [10**400, -(10**400), np.longdouble(1e300) * 1e300])
def test_t01_e_construction_never_raises_overflow_or_zero_division(mass):
    for make in (forces.ForceContext, forces.ForceContext.deferred):
        try:
            ctx = make(mass)
            ctx.total_mass_kg  # noqa: B018
        except (OverflowError, ZeroDivisionError) as err:  # pragma: no cover - the failure
            pytest.fail(f"{type(err).__name__} escaped: step() would misreport it")
        except ValueError:
            pass


def test_t01_smallest_positive_mass_is_valid():
    assert forces.ForceContext(5e-324).total_mass_kg == 5e-324


# ------------------------------------------------------------------ T-02 (U-2, INV-1)


class _Recorder:
    name = "recorder"

    def __init__(self, result=None, exc=None):
        self.calls, self.result, self.exc = [], result, exc

    def acceleration(self, t, r, v):
        self.calls.append((t, r, v))
        if self.exc is not None:
            raise self.exc
        return self.result


@pytest.mark.parametrize(
    "payload",
    [np.array([1.0, -0.0, 5e-324]), np.array([np.nan, np.inf, -1e308]), "not an array", None],
)
def test_t02_adapter_passes_identical_objects_once_and_returns_the_result(payload):
    model = _Recorder(result=payload)
    state = dict(vars(model))
    adapter = forces.LegacyForceAdapter(model)
    t, r, v = -0.0, np.array([7e6, 0.0, -0.0]), np.array([5e-324, np.nan, 1.0])
    out = adapter.acceleration(t, r, v, forces.ForceContext(1300.0))
    assert out is payload
    assert len(model.calls) == 1
    (ct, cr, cv) = model.calls[0]
    assert ct is t and cr is r and cv is v
    model.calls.clear()
    assert vars(model) == {**state, "calls": []} and adapter.model is model
    assert adapter.name == "recorder"


@pytest.mark.parametrize(
    "exc",
    [
        ValueError("x"),
        FloatingPointError("x"),
        OverflowError("x"),
        ZeroDivisionError("x"),
        KeyboardInterrupt(),
    ],
)
def test_t02_adapter_propagates_the_identical_exception(exc):
    adapter = forces.LegacyForceAdapter(_Recorder(exc=exc))
    with pytest.raises(type(exc)) as err:
        adapter.acceleration(0.0, np.zeros(3), np.zeros(3), forces.ForceContext())
    assert err.value is exc
    assert err.value.__context__ is None and err.value.__cause__ is None


def test_t02_adapter_is_immutable():
    adapter = forces.LegacyForceAdapter(_Recorder())
    with pytest.raises(AttributeError):
        adapter.model = None
    with pytest.raises(AttributeError):
        del adapter.model


# ------------------------------------------------------------------------ T-03 (DQ-5)


@pytest.mark.parametrize(
    "model",
    [PointMassGravity(WGS84.mu), ZonalJ2Gravity(WGS84.mu, WGS84.equatorial_radius, J2)],
    ids=["point_mass", "zonal_j2"],
)
def test_t03_legacy_models_through_the_adapter_are_bit_identical(model):
    rng = random.Random(20261028)  # seed recorded
    adapter = forces.LegacyForceAdapter(model)
    for _ in range(2000):
        r = np.array([rng.uniform(-4e7, 4e7) for _ in range(3)])
        v = np.array([rng.uniform(-1e4, 1e4) for _ in range(3)])
        t = rng.uniform(0.0, 1e6)
        direct = model.acceleration(t, r, v)
        for ctx in (forces.ForceContext(), forces.ForceContext(rng.uniform(1.0, 1e4))):
            via = adapter.acceleration(t, r, v, ctx)
            assert [x.hex() for x in via.tolist()] == [x.hex() for x in direct.tolist()]


# -------------------------------------------- T-04 … T-06 (U-3, INV-3, I-7 (a), OD-4)


class _StageSpy:
    """RK4 whose derivative calls are recorded: (t, stage y) per evaluation."""

    name = "rk4"
    order = 4

    def __init__(self):
        self.stages = []

    def step(self, f, t, y, dt):
        def spied(ts, ys):
            self.stages.append((ts, ys.copy()))
            return f(ts, ys)

        return RK4().step(spied, t, y, dt)


def _record_contexts(monkeypatch):
    """Replace the simulator's adapter by one that records each context it receives."""
    seen = []
    original = forces.LegacyForceAdapter

    class Recording(original):
        __slots__ = ()

        def acceleration(self, t, r, v, ctx):
            seen.append(ctx)
            return super().acceleration(t, r, v, ctx)

    monkeypatch.setattr(simulator_module, "LegacyForceAdapter", Recording)
    return seen


def _stage_mass(y):
    return DRY + max(float(y[6]), 0.0)


def _run(monkeypatch, sim_args, burn=None, ticks=3):
    seen = _record_contexts(monkeypatch)
    spy = _StageSpy()
    sim = Simulator(R0, V0, PointMassGravity(WGS84.mu), spy, 10.0, **sim_args)
    if burn is not None:
        sim.schedule_burn("prograde", *burn)
    for _ in range(ticks):
        sim.step()
    assert len(seen) == len(spy.stages) > 0
    return seen, spy.stages


@pytest.mark.parametrize(
    "burn", [None, (0.0, 30.0), (3.0, 4.0), (5.0, 12.0)], ids=["coast", "full", "inside", "split"]
)
def test_t04_t05_context_mass_is_the_stage_mass_bit_for_bit(monkeypatch, burn):
    seen, stages = _run(monkeypatch, {"spacecraft": _spacecraft()}, burn)
    for ctx, (_, y) in zip(seen, stages, strict=True):
        assert type(ctx.total_mass_kg) is float
        assert ctx.total_mass_kg.hex() == _stage_mass(y).hex()
    if burn is not None:  # stage-derived, not committed: the masses vary within each burn step
        assert len({ctx.total_mass_kg for ctx in seen}) > 1
        # Some RK4 stage carries a mass other than its sub-step's committed start (stage 1).
        starts = [seen[i - i % 4].total_mass_kg for i in range(len(seen))]
        assert any(c.total_mass_kg != m0 for c, m0 in zip(seen, starts, strict=True))


@pytest.mark.parametrize("dry", [DRY, 1e-3])
def test_t04_negative_round_off_propellant_gives_the_dry_mass_exactly(monkeypatch, dry):
    """U-3. At dry = 1e-3 kg, dry - 1e-17 is a different binary64, so the clamp is observable;
    at 1000 kg the subtraction rounds back to 1000 (both are pinned)."""
    assert (dry - 1e-17 != dry) is (dry == 1e-3)
    seen = _record_contexts(monkeypatch)
    craft = SpacecraftSpec(dry_mass_kg=dry, engine=ENGINE, tank=TankSpec(propellant_kg=PROP))
    sim = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0, spacecraft=craft)
    for law in (None, "burn"):
        y = np.concatenate([R0, V0, [-1e-17, 0.0]])
        burn = None
        if law == "burn":
            sim.schedule_burn("prograde", 0.0, 5.0)
            burn = sim._pending[0]
        seen.clear()
        sim._powered_derivative(burn)(0.0, y)
        (ctx,) = seen
        assert ctx.total_mass_kg.hex() == dry.hex()


def test_t06_massless_path_carries_absent_mass(monkeypatch):
    seen, _ = _run(monkeypatch, {})
    for ctx in seen:
        try:
            mass = ctx.total_mass_kg
        except ValueError as err:
            pytest.fail(f"massless context carries a supplied (invalid) mass: {err}")
        assert mass is None


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_t04_invalid_coast_stage_mass_is_carried_and_rejected_on_read(monkeypatch):
    """I-41: a coast stage of infinite length (dt = +inf) has NaN propellant. Its context
    is built without raising and its mass is neither repaired nor clamped: reading it
    raises. The step then fails exactly as at BASE (T-07 (a))."""
    seen = _record_contexts(monkeypatch)
    sim = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), math.inf, spacecraft=_spacecraft())
    with pytest.raises(FloatingPointError, match=r"^non-finite state produced at tick 1$"):
        sim.step()
    assert len(seen) == 4
    assert seen[0].total_mass_kg == DRY + PROP
    rejected = r"^total_mass_kg must be finite and positive, got nan$"
    for ctx in seen[1:]:
        with pytest.raises(ValueError, match=rejected):
            ctx.total_mass_kg  # noqa: B018


# ------------------------------- T-04 coast snapshot (U-1 owned binary64; I-44, Review R-02)


class _WriteAfter:
    """Euler; writes the stage propellant after the derivative call has returned."""

    name, order = "write_after", 1

    def step(self, f, t, y, dt):
        stage = y.copy()
        k = f(t, stage)
        stage[6] = 123.0
        return y + dt * k


class _SharedBufferRK4:
    """Classical RK4 evaluating every stage in one reused buffer, written again at the end."""

    name, order = "rk4_shared_buffer", 4

    def step(self, f, t, y, dt):
        buf, h = y.copy(), 0.5 * dt
        k1 = f(t, buf)
        buf[:] = y + h * k1
        k2 = f(t + h, buf)
        buf[:] = y + h * k2
        k3 = f(t + h, buf)
        buf[:] = y + dt * k3
        k4 = f(t + dt, buf)
        buf[6] = -7.0
        return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


class _RowViewRK4:
    """Classical RK4 whose stages are row views of one 2-D workspace, zeroed at the end."""

    name, order = "rk4_row_views", 4

    def step(self, f, t, y, dt):
        ws, h = np.empty((4, y.size)), 0.5 * dt
        ws[0] = y
        k1 = f(t, ws[0])
        ws[1] = y + h * k1
        k2 = f(t + h, ws[1])
        ws[2] = y + h * k2
        k3 = f(t + h, ws[2])
        ws[3] = y + dt * k3
        k4 = f(t + dt, ws[3])
        ws[:, 6] = -7.0
        return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


class _ZeroForce:
    name = "zero_force"

    def acceleration(self, t, r, v):
        return np.zeros(3)


@pytest.mark.parametrize("integrator", [_WriteAfter, _SharedBufferRK4, _RowViewRK4])
def test_t04_coast_context_is_an_owned_snapshot_of_the_stage_mass(monkeypatch, integrator):
    """U-1: the coast context owns the stage mass at the derivative call. Later writes to the
    stage storage (after the call, by buffer reuse, through views) do not change it, and
    repeated reads agree. Zero force keeps every stage mass at DRY + PROP."""
    seen = _record_contexts(monkeypatch)
    Simulator(R0, V0, _ZeroForce(), integrator(), 0.5, spacecraft=_spacecraft()).step()
    assert len(seen) == integrator.order
    for ctx in seen:
        first, second = ctx.total_mass_kg, ctx.total_mass_kg
        assert type(first) is float
        assert first.hex() == second.hex() == (DRY + PROP).hex()


def test_t04_coast_context_does_not_keep_the_stage_alive(monkeypatch):
    seen, stages = _record_contexts(monkeypatch), []

    class _Keep:
        name, order = "euler_kept_stage", 1

        def step(self, f, t, y, dt):
            stage = y.copy()
            stages.append(weakref.ref(stage))
            return y + dt * f(t, stage)

    Simulator(R0, V0, _ZeroForce(), _Keep(), 0.5, spacecraft=_spacecraft()).step()
    gc.collect()
    ((ctx,), (stage,)) = seen, stages
    assert stage() is None
    assert ctx.total_mass_kg == DRY + PROP


class _RaisingGetitem(np.ndarray):
    def __getitem__(self, key):
        if key == 6:
            raise LookupError("stage propellant read through the subclass")
        return super().__getitem__(key)


@pytest.mark.parametrize(
    "wrap",
    [
        lambda y: np.ma.array(y, mask=[False] * 6 + [True, False]),
        lambda y: y.view(_RaisingGetitem),
    ],
    ids=["masked_propellant", "raising_getitem"],
)
def test_t04_coast_mass_is_the_stored_propellant_of_a_subclass_stage(monkeypatch, wrap):
    """I-44: for a float64 ndarray subclass the coast mass is built from the stored binary64
    element, not from the subclass's indexing (a mask is not interpreted), and reading it
    raises nothing."""
    seen = _record_contexts(monkeypatch)

    class _Wrapping:
        name, order = "euler_wrapped", 1

        def step(self, f, t, y, dt):
            return y + dt * np.asarray(f(t, wrap(y.copy())), dtype=float)

    Simulator(R0, V0, _ZeroForce(), _Wrapping(), 0.5, spacecraft=_spacecraft()).step()
    ((ctx,),) = (seen,)
    assert ctx.total_mass_kg.hex() == (DRY + PROP).hex()


# ------------------- T-04 powered snapshot (plan amendment A-1, I-46 D2; Review 03 N-01)


class _StageMassAtCall:
    """Wraps an integrator's derivative: records the mass of each plain float64 stage at the
    call, before the derivative runs (INV-3). The wrapped integrator is unchanged."""

    def __init__(self, integrator):
        self.integrator, self.masses = integrator, []
        self.name, self.order = integrator.name, integrator.order

    def step(self, f, t, y, dt):
        def recording(ts, ys):
            self.masses.append(_stage_mass(ys))
            return f(ts, ys)

        return self.integrator.step(recording, t, y, dt)


@pytest.mark.parametrize("integrator", [_WriteAfter, _SharedBufferRK4, _RowViewRK4])
def test_t04_powered_context_is_an_owned_snapshot_of_the_stage_mass(monkeypatch, integrator):
    """A-1 T-04 (d): T-04 (a) on the powered path. The burn covers the whole first tick, so
    every derivative call goes to the powered closure. Propellant flows, so each call's
    expected mass is its stage mass recorded at the call, not DRY + PROP."""
    seen = _record_contexts(monkeypatch)
    recorder = _StageMassAtCall(integrator())
    sim = Simulator(R0, V0, _ZeroForce(), recorder, 0.5, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", 0.0, 30.0)
    sim.step()
    assert len(seen) == len(recorder.masses) == integrator.order
    for ctx, expected in zip(seen, recorder.masses, strict=True):
        first, second = ctx.total_mass_kg, ctx.total_mass_kg
        assert type(first) is float
        assert type(second) is float
        assert first.hex() == second.hex() == expected.hex()


def test_t04_powered_context_does_not_keep_the_stage_alive(monkeypatch):
    """A-1 T-04 (e): T-04 (b) on the powered path, with the T-04 (d) burn."""
    seen, stages = _record_contexts(monkeypatch), []

    class _Keep:
        name, order = "euler_kept_stage", 1

        def step(self, f, t, y, dt):
            stage = y.copy()
            stages.append(weakref.ref(stage))
            return y + dt * f(t, stage)

    recorder = _StageMassAtCall(_Keep())
    sim = Simulator(R0, V0, _ZeroForce(), recorder, 0.5, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", 0.0, 30.0)
    sim.step()
    gc.collect()
    ((ctx,), (stage,), (expected,)) = seen, stages, recorder.masses
    assert stage() is None
    assert ctx.total_mass_kg == expected
