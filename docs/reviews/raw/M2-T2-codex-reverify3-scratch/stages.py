# ruff: noqa
import numpy as np
from tars.sim.propulsion import *
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


class Watch(RK4):
    def __init__(self):
        self.minimum = 1e300
        self.bad = []

    def step(self, f, t, y, dt):
        def wrapped(t, y):
            self.minimum = min(self.minimum, float(y[6]))
            if y[6] < 0:
                self.bad.append((t, float(y[6])))
            return f(t, y)

        result = super().step(wrapped, t, y, dt)
        if result[6] < 0:
            self.bad.append(("result", float(result[6])))
        return result


engine = EngineSpec(490, 312)
for duration in [0.1, 1.0, 3.0, 10.0, 77.3, 100.0, 1000.0]:
    for n in [1, 3, 7, 10, 100, 1000]:
        tank = engine.mass_flow_kgps * duration
        w = Watch()
        s = Simulator(
            [1, 0, 0],
            [10000, 0, 0],
            Zero(),
            w,
            duration / n,
            spacecraft=SpacecraftSpec(1000, engine, TankSpec(tank)),
        )
        p = s.schedule_burn("prograde", 0, tank / engine.mass_flow_kgps)
        for _ in range(n + 2):
            s.step()
        if w.bad:
            print("NEGATIVE", duration, n, "plan", p, "minimum", w.minimum, "bad", w.bad[:4])
# original large-time case
for policy in ["reject", "burn_to_depletion"]:
    tank = engine.mass_flow_kgps * 0.1
    w = Watch()
    s = Simulator(
        [1, 0, 0],
        [1, 0, 0],
        Zero(),
        w,
        1e9 + 1,
        spacecraft=SpacecraftSpec(1e-10, engine, TankSpec(tank)),
    )
    p = s.schedule_burn(
        "prograde", 1e9, tank / engine.mass_flow_kgps if policy == "reject" else 1, policy
    )
    s.step()
    print(
        "ORIGINAL",
        policy,
        "minimum",
        w.minimum,
        "remaining",
        s.propulsion_snapshot().propellant_kg,
        "used",
        p.propellant_used_kg,
        "actual",
        engine.mass_flow_kgps * p.burn_duration_s,
    )
# all numeric huge-int fields
for field in ["propellant_kg", "ignition_t_s", "duration_s", "earliest_t_s"]:
    args = dict(propellant_kg=1, ignition_t_s=0, duration_s=1, earliest_t_s=0)
    args[field] = 10**10000
    try:
        plan_burn(engine, **args)
    except BurnRejectedError as e:
        print("HUGE", field, e.reason, e.detail)
try:
    plan_burn(engine, 1, 0, 1, policy=10**10000)
except Exception as e:
    print("HUGE POLICY", type(e).__name__, str(e)[:100])
