# ruff: noqa
import math, importlib.util, sys
import numpy as np
from pathlib import Path
from decimal import Decimal, localcontext
from tars.sim.propulsion import *
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4
from tars.sim.forces import PointMassGravity


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


for name, e, dry, prop, t, d in [
    ("cancellation", EngineSpec(3e-7, 3e-7 / 9.80665), 3.0, 1e16, 3.0, 9999999999999998.0),
    ("underflow", EngineSpec(1e-280, 1e20 / 9.80665), 1e-310, 1e-310, 1e-10, 1e-11),
]:
    s = Simulator(
        [1, 0, 0], [1, 0, 0], Zero(), RK4(), 1.0, spacecraft=SpacecraftSpec(dry, e, TankSpec(prop))
    )
    try:
        s.schedule_burn("prograde", t, d)
    except BurnRejectedError as err:
        print(name, err.reason.value)
        assert err.reason == BurnRejection.BURN_UNSCHEDULABLE
    else:
        raise AssertionError(name)
e = EngineSpec(490, 312)
for field in ("ignition_t_s", "duration_s", "earliest_t_s", "dry_mass_kg"):
    for bad in (math.nan, math.inf, -math.inf, 10**10000):
        kw = dict(ignition_t_s=0.0, duration_s=1.0, earliest_t_s=0.0, dry_mass_kg=1000.0)
        kw[field] = bad
        try:
            plan_burn(e, 300, **kw)
        except BurnRejectedError as err:
            assert err.reason == BurnRejection.SCHEMA_INVALID
        else:
            raise AssertionError(field)
print("16 malformed timing cases schema_invalid")
for t, d in [(1e308, 1e308), (1e15, 0.001)]:
    try:
        plan_burn(e, 1e308, t, d, dry_mass_kg=1000.0)
    except BurnRejectedError as err:
        assert err.reason == BurnRejection.BURN_UNSCHEDULABLE
    else:
        raise AssertionError(t)
print("overflow / collapsed interval rejected")
# New false accept, > budget by about 1e-16 m/s.
e = EngineSpec(8.388608006147431, 1e308 / 9.80665)
s = Simulator(
    [1, 0, 0], [1, 0, 0], Zero(), RK4(), 1e9 + 1.0, spacecraft=SpacecraftSpec(1.0, e, TankSpec(1.0))
)
p = s.schedule_burn("prograde", 1e9, 0.1)
with localcontext() as ctx:
    ctx.prec = 400
    dt = abs(Decimal(0.1) - Decimal(p.burn_duration_s))
    md = Decimal(e.mass_flow_kgps)
    m = Decimal(2) - md * Decimal(max(0.1, p.burn_duration_s))
    x = md * dt / m
    exact = Decimal(e.exhaust_velocity_mps) * (1 + x).ln()
    actual = (Decimal(e.thrust_n) / md) * (1 + x).ln()
    print(
        "N1",
        repr(e),
        repr(p),
        "x_float",
        (e.thrust_n / 2) * float(dt) / e.exhaust_velocity_mps,
        "exact_c_log",
        exact,
        "actual_integrated_acceleration",
        actual,
    )
    assert exact > Decimal(1e-7) and actual > Decimal(1e-7) and p.timing_delta_v_error_mps <= 1e-7
s.step()
assert np.isfinite(s._y).all()
print("N1 EXECUTED finite", s._y, "causes", [(x.kind, x.end_cause) for x in s.engine_transitions])
# Archived pre-T2 implementation against current coast.
spec = importlib.util.spec_from_file_location(
    "archived_m1", Path("docs/reviews/raw/M2-DR0017-codex-scratch/m1_simulator.py")
)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
for dt in [10.0, 0.1, 7 / 3]:
    force = PointMassGravity(3.986004418e14)
    args = ([6628137.0, 0, 0], [0, 7700.0, 1000.0], force, RK4(), dt)
    sims = [
        mod.Simulator(*args),
        Simulator(*args),
        Simulator(*args, spacecraft=SpacecraftSpec(1000.0, EngineSpec(490, 312), TankSpec(300.0))),
    ]
    for k in range(1000):
        for sim in sims:
            sim.step()
        states = [sim.snapshot() for sim in sims]
        assert len({x.r.tobytes() + x.v.tobytes() for x in states}) == 1
    print("1000 coast ticks bit-identical", dt)
