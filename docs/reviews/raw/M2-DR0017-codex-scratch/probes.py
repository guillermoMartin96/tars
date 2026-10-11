# ruff: noqa
import math, random
from decimal import Decimal, localcontext
import numpy as np
from tars.sim.propulsion import *
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


def oracle(e, dry, prop, d, D):
    with localcontext() as ctx:
        ctx.prec = 100
        a = Decimal(dry) + max(Decimal(prop) - Decimal(e.mass_flow_kgps) * Decimal(d), Decimal(0))
        b = Decimal(dry) + max(Decimal(prop) - Decimal(e.mass_flow_kgps) * Decimal(D), Decimal(0))
        return Decimal(e.exhaust_velocity_mps) * abs((a / b).ln())


for name, e, dry, prop, t, d in [
    ("end_mass_cancellation", EngineSpec(3e-7, 3e-7 / 9.80665), 3.0, 1e16, 3.0, 1e16 - 2),
    ("numerator_underflow", EngineSpec(1e-280, 1e20 / 9.80665), 1e-310, 1e-310, 1e-10, 1e-11),
]:
    s = Simulator(
        np.zeros(3),
        np.array([1.0, 0, 0]),
        Zero(),
        RK4(),
        1.0,
        spacecraft=SpacecraftSpec(dry, e, TankSpec(prop)),
    )
    p = s.schedule_burn("prograde", t, d)
    print(
        name,
        "SCHEDULE ACCEPTED",
        p,
        "independent_error",
        oracle(e, dry, prop, d, p.burn_duration_s),
    )
e = EngineSpec(490, 312)
print("massless standalone", plan_burn(e, 300, 1e15, 0.1))
for field in ("ignition_t_s", "duration_s", "earliest_t_s", "dry_mass_kg"):
    for bad in (math.nan, math.inf, -math.inf, 10**10000):
        kw = dict(ignition_t_s=0.0, duration_s=1.0, earliest_t_s=0.0, dry_mass_kg=1000.0)
        kw[field] = bad
        try:
            plan_burn(e, 300, **kw)
        except BurnRejectedError as err:
            assert err.reason is BurnRejection.SCHEMA_INVALID
        else:
            raise AssertionError(field)
print("16 nonfinite/huge-input cases schema_invalid")
for t, d in [(1e308, 1e308), (1e15, 0.001)]:
    try:
        plan_burn(e, 1e308, t, d, dry_mass_kg=1000.0)
    except BurnRejectedError as err:
        assert err.reason is BurnRejection.BURN_UNSCHEDULABLE
    else:
        raise AssertionError((t, d))
print("overflow and collapsed event time: burn_unschedulable")
rng = random.Random(17)
accepted = 0
rejected = 0
for _ in range(3000):
    e = EngineSpec(10 ** rng.uniform(-3, 5), 10 ** rng.uniform(1, 4))
    dry = 10 ** rng.uniform(-3, 5)
    prop = 10 ** rng.uniform(-3, 3)
    t = 10 ** rng.uniform(-5, 16)
    dep = prop / e.mass_flow_kgps
    d = dep * rng.uniform(0.01, 2)
    intended = min(d, dep)
    cutoff = t + intended
    D = cutoff - t
    while D > dep:
        cutoff = math.nextafter(cutoff, -math.inf)
        D = cutoff - t
    expected = oracle(e, dry, prop, intended, D)
    try:
        p = plan_burn(e, prop, t, d, policy="burn_to_depletion", dry_mass_kg=dry)
    except BurnRejectedError as err:
        assert err.reason is BurnRejection.BURN_UNSCHEDULABLE
        rejected += 1
    else:
        accepted += 1
        assert D > 0 and p.burn_duration_s <= dep
        assert expected <= Decimal(1e-7), (e, dry, prop, t, d, p, expected)
print(
    "3000 randomized normal-envelope cases",
    accepted,
    "accepted",
    rejected,
    "rejected; accepted exact errors within budget",
)
