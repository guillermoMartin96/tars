# ruff: noqa
import math
from pathlib import Path
import numpy as np
import tars.sim.simulator as sm
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec, SpacecraftSpec, TankSpec, BurnRejectedError, plan_burn


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


e = EngineSpec(490, 312)
source = Path(sm.__file__).read_text()
old = source.replace("max(float(y[_PROP]), 0.0)", "float(y[_PROP])")


def run(clamp, dt, duration, tank, dry=1000):
    exec(compile(source if clamp else old, sm.__file__, "exec"), sm.__dict__)
    s = sm.Simulator(
        [1, 0, 0],
        [10000, 0, 0],
        Zero(),
        RK4(),
        dt,
        spacecraft=SpacecraftSpec(dry, e, TankSpec(tank)),
    )
    s.schedule_burn("prograde", 0, duration)
    while s.t < duration + dt:
        s.step()
    return s._y.tobytes(), s.engine_transitions


for dt in [0.1, 0.3, 1, 10]:
    for duration in [0.1, 1, 3, 77.3]:
        a = run(True, dt, duration, 300)
        b = run(False, dt, duration, 300)
        assert a[0] == b[0]
        assert [
            (x.r.tobytes(), x.v.tobytes(), x.propellant_kg, x.delta_v_sensed_mps) for x in a[1]
        ] == [(x.r.tobytes(), x.v.tobytes(), x.propellant_kg, x.delta_v_sensed_mps) for x in b[1]]
print("NONDEPLETION byte-identical unclamped/clamped: 16 cases, including transition states")
exec(compile(source, sm.__file__, "exec"), sm.__dict__)
# Watch every stage and the effective mass passed to thrust.
minimum = math.inf
masses = []
original = sm.thrust_acceleration
sm.thrust_acceleration = lambda engine, direction, mass: (
    masses.append(mass) or original(engine, direction, mass)
)


class Watch(RK4):
    def step(self, f, t, y, dt):
        def wrapped(t, y):
            global minimum
            minimum = min(minimum, float(y[6]))
            return f(t, y)

        return super().step(wrapped, t, y, dt)


s = sm.Simulator(
    [1, 0, 0],
    [10000, 0, 0],
    Zero(),
    Watch(),
    0.1,
    spacecraft=SpacecraftSpec(1e-20, e, TankSpec(e.mass_flow_kgps)),
)
s.schedule_burn("prograde", 0, 1)
for _ in range(12):
    s.step()
assert min(masses) >= 1e-20 and s.propulsion_snapshot().propellant_kg == 0
print(
    "N4 stage minimum",
    minimum,
    "effective mass minimum",
    min(masses),
    "final propellant",
    s.propulsion_snapshot().propellant_kg,
)
sm.thrust_acceleration = original
for policy in ["reject", "burn_to_depletion"]:
    tank = e.mass_flow_kgps * 0.1
    s = sm.Simulator(
        [1, 0, 0],
        [1, 0, 0],
        Zero(),
        RK4(),
        1e9 + 1,
        spacecraft=SpacecraftSpec(1000, e, TankSpec(tank)),
    )
    p = s.schedule_burn(
        "prograde", 1e9, tank / e.mass_flow_kgps if policy == "reject" else 1, policy
    )
    residual = tank - p.propellant_used_kg
    before = s._committed_propellant_kg
    try:
        s.schedule_burn("prograde", p.cutoff_t_s, 1, "burn_to_depletion")
    except BurnRejectedError as err:
        print("QUEUED tiny residual", policy, err.reason.value)
    else:
        raise AssertionError("expected unrepresentable tiny residual")
    assert s._committed_propellant_kg == before == residual
    s.step()
    actual = s.propulsion_snapshot().propellant_kg
    assert abs(actual - residual) < 2 * math.ulp(tank)
    before = s._y.tobytes()
    try:
        s.schedule_burn("prograde", s.t, 1, "burn_to_depletion")
    except BurnRejectedError as err:
        print("EXECUTED tiny residual", policy, err.reason.value)
    else:
        raise AssertionError("expected unrepresentable tiny residual")
    assert before == s._y.tobytes()
    print(
        "RESIDUAL", policy, "planned", residual, "actual", actual, "discrepancy", actual - residual
    )
# Tiny propellant itself is burnable where time permits.
tank = e.mass_flow_kgps * 1e-12
s = sm.Simulator(
    [1, 0, 0], [1, 0, 0], Zero(), RK4(), 1e-12, spacecraft=SpacecraftSpec(1000, e, TankSpec(tank))
)
s.schedule_burn("prograde", 0, 2e-12, "burn_to_depletion")
s.step()
assert s.propulsion_snapshot().propellant_kg == 0
print("TINY tank representable burn succeeds")
tank = e.mass_flow_kgps * (1e-6 + 1e-12)
s = sm.Simulator(
    [1, 0, 0], [1, 0, 0], Zero(), RK4(), 2e-6, spacecraft=SpacecraftSpec(1000, e, TankSpec(tank))
)
p = s.schedule_burn("prograde", 0, 1e-6)
residual = s._committed_propellant_kg
q = s.schedule_burn("prograde", p.cutoff_t_s, 2e-12, "burn_to_depletion")
assert 0 < q.propellant_used_kg <= residual
s.step()
assert s.propulsion_snapshot().propellant_kg >= 0
assert abs(s.propulsion_snapshot().propellant_kg - (residual - q.propellant_used_kg)) < 1e-21
print(
    "SUBSEQUENT tiny residual succeeds",
    residual,
    "used",
    q.propellant_used_kg,
    "remaining",
    s.propulsion_snapshot().propellant_kg,
)
