# ruff: noqa
import math
import numpy as np
import tars.sim.simulator as sm
from tars.sim.integrators import RK4
from tars.sim.propulsion import (
    BurnRejectedError,
    EngineSpec,
    SpacecraftSpec,
    TankSpec,
    plan_burn,
)


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


sc = SpacecraftSpec(1000, EngineSpec(490, 312), TankSpec(300))


def sim(dt=10, force=None, craft=sc):
    return sm.Simulator([1, 0, 0], [1, 0, 0], force or Zero(), RK4(), dt, spacecraft=craft)


def rejection(fn):
    try:
        return ("accepted", fn())
    except BurnRejectedError as e:
        return e.reason.value
    except Exception as e:
        return type(e).__name__ + ": " + str(e)[:150]


bad = [-np.inf, np.inf, np.nan, "-1", True, np.array(-1), np.bool_(True), None, 10**1000]
for mode in ("idle", "pending", "active"):
    s = sim()
    if mode == "active":
        s.schedule_burn("prograde", 0, 20)
    s.step()
    if mode == "pending":
        s.schedule_burn("prograde", 20, 1)
    for x in bad:
        assert rejection(lambda: s.schedule_burn("prograde", x, 1)) == "schema_invalid"
        assert rejection(lambda: s.schedule_burn("prograde", 0, x)) == "schema_invalid"
    print("F2 invalid ignition/duration", mode, "PASS")
print("np.float32 past", rejection(lambda: s.schedule_burn("prograde", np.float32(1), 1)))
for field in ("propellant_kg", "ignition_t_s", "duration_s", "earliest_t_s"):
    for x in bad:
        args = dict(propellant_kg=300, ignition_t_s=1, duration_s=1, earliest_t_s=0)
        args[field] = x
        assert rejection(lambda: plan_burn(sc.engine, **args)) == "schema_invalid"
print("burn_scalar all four plan inputs PASS")
print("huge integer > repr limit", rejection(lambda: s.schedule_burn("prograde", 10**10000, 1)))
print(
    "invalid policy with past ignition",
    rejection(lambda: s.schedule_burn("prograde", 0, 1, policy="bogus")),
)
for tank, duration, policy in [
    (300, 0.1, "reject"),
    (sc.engine.mass_flow_kgps * 0.2, 0.2, "burn_to_depletion"),
]:
    z = sim(1e15 + 10, craft=SpacecraftSpec(1000, sc.engine, TankSpec(tank)))
    print(
        "F3 original",
        policy,
        rejection(lambda: z.schedule_burn("prograde", 1e15, duration, policy)),
    )
z = sim()
z.schedule_burn("prograde", 1, 1)
z.step()
for e in z.engine_transitions:
    for arr in (e.r, e.v):
        try:
            arr.flags.writeable = True
        except ValueError:
            pass
        else:
            raise AssertionError("writable event")
        assert isinstance(arr.base, bytes)
print("F4 r/v immutable backing PASS")


class Fail:
    def __init__(self, kind):
        self.kind, self.bad = kind, True

    def acceleration(self, t, r, v):
        if self.bad and t >= 2:
            if self.kind == "nan":
                return np.full(3, np.nan)
            raise RuntimeError("force failure")
        return np.zeros(3)


for kind in ("nan", "raise", "direction", "thrust"):
    force = Fail(kind if kind in ("nan", "raise") else "raise")
    if kind in ("direction", "thrust"):
        force.bad = False
    z = sim(force=force)
    p = z.schedule_burn("prograde", 1, 2)
    before = (
        z._y.tobytes(),
        z.tick,
        z.propulsion_snapshot(),
        z.engine_transitions,
        z._committed_propellant_kg,
    )
    old_law = sm.DIRECTION_LAWS["prograde"].direction
    old_thrust = sm.thrust_acceleration
    if kind == "direction":

        def fail_law(t, r, v):
            raise RuntimeError("direction failure")

        sm.DIRECTION_LAWS["prograde"].direction = fail_law
    if kind == "thrust":

        def fail_thrust(*args):
            raise ValueError("thrust failure")

        sm.thrust_acceleration = fail_thrust
    try:
        z.step()
    except (RuntimeError, ValueError, FloatingPointError):
        pass
    else:
        raise AssertionError("did not fail")
    finally:
        sm.DIRECTION_LAWS["prograde"].direction = old_law
        sm.thrust_acceleration = old_thrust
    after = (
        z._y.tobytes(),
        z.tick,
        z.propulsion_snapshot(),
        z.engine_transitions,
        z._committed_propellant_kg,
    )
    assert before == after
    force.bad = False
    z.step()
    assert [(e.kind, e.t) for e in z.engine_transitions] == [("ignition", 1), ("cutoff", 3)]
    assert abs(300 - z.propulsion_snapshot().propellant_kg - p.propellant_used_kg) < 1e-12
    print("F1 rollback/retry", kind, "PASS")

mdot = sc.engine.mass_flow_kgps
for ignition, intended in [(1.0, 1.2e-16), (1e9, 0.1), (1e9, 0.09999999)]:
    for policy, duration in [("reject", intended), ("burn_to_depletion", intended * 2)]:
        tank = mdot * intended
        if policy == "reject":
            duration = tank / mdot
        p = plan_burn(sc.engine, tank, ignition, duration, policy=policy)
        print(
            "edge",
            ignition,
            intended,
            policy,
            "represented",
            p.burn_duration_s,
            "mass discrepancy",
            mdot * p.burn_duration_s - p.propellant_used_kg,
            "cause",
            p.end_cause,
        )

# Re-run original multiple events and schedule-during-active checks.
z = sim()
plans = [z.schedule_burn("prograde", t, d) for t, d in [(1, 2), (3, 1), (5, 2)]]
z.step()
x, v, m, now = 1.0, 1.0, 1300.0, 0.0
for p in plans:
    x += v * (p.ignition_t_s - now)
    d = p.burn_duration_s
    mf = m - mdot * d
    x += v * d + sc.engine.exhaust_velocity_mps * (d - mf / mdot * math.log(m / mf))
    v += sc.engine.exhaust_velocity_mps * math.log(m / mf)
    m = mf
    now = p.cutoff_t_s
x += v * (10 - now)
print(
    "original multi-event errors",
    z.snapshot().r[0] - x,
    z.snapshot().v[0] - v,
    z.propulsion_snapshot().propellant_kg - (m - 1000),
)
z = sim()
z.schedule_burn("prograde", 0, 20)
z.step()
z.schedule_burn("retrograde", 25, 2)
z.step()
z.step()
print("original active future consumption", 300 - z.propulsion_snapshot().propellant_kg, mdot * 22)
