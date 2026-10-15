# ruff: noqa
import math, random
from decimal import Decimal, localcontext
from tars.sim.propulsion import *

rng = random.Random(1722)
acc = rej = false = down = 0
for k in range(10000):
    e = EngineSpec(10 ** rng.uniform(-3, 6), 10 ** rng.uniform(1.7, 3.7))
    dry = 10 ** rng.uniform(0, 6)
    prop = 10 ** rng.uniform(-3, 6)
    t = rng.uniform(0, 1e9)
    dep = prop / e.mass_flow_kgps
    d = dep * rng.choice([1.0, 2.0, rng.uniform(0.0001, 0.99)])
    a = min(d, dep)
    cut = t + a
    b = cut - t
    if b > dep:
        down += 1
    while b > dep:
        cut = math.nextafter(cut, -math.inf)
        b = cut - t
    with localcontext() as ctx:
        ctx.prec = 100
        md = Decimal(e.mass_flow_kgps)
        m = Decimal(dry) + max(Decimal(prop) - md * Decimal(max(a, b)), Decimal(0))
        x = md * abs(Decimal(a) - Decimal(b)) / m
        exact = (Decimal(e.thrust_n) / md) * (1 + x).ln()
    try:
        p = plan_burn(e, prop, t, d, "burn_to_depletion", dry_mass_kg=dry)
    except BurnRejectedError:
        rej += 1
        if b > 0 and e.mass_flow_kgps * b > 0 and exact <= Decimal(1e-7):
            false += 1
            print("false rejection", e, dry, prop, t, d, exact)
    else:
        acc += 1
        assert exact <= Decimal(1e-7)
print("ORDINARY_10000 accepted", acc, "rejected", rej, "false_rejections", false, "stepdowns", down)
