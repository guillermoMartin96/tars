# ruff: noqa
import math, random, json
from decimal import Decimal, localcontext
from tars.sim.propulsion import *


def oracle(e, dry, prop, a, b):
    with localcontext() as ctx:
        ctx.prec = 180
        md = Decimal(e.mass_flow_kgps)
        c = Decimal(e.exhaust_velocity_mps)
        m = Decimal(dry) + max(Decimal(prop) - md * Decimal(max(a, b)), Decimal(0))
        x = md * abs(Decimal(a) - Decimal(b)) / m
        l = (
            sum(((-1) ** (j + 1)) * x**j / Decimal(j) for j in range(1, 11))
            if x < Decimal("1e-20")
            else (1 + x).ln()
        )
        return +(c * l)


rng = random.Random(17017)
checked = under = overbudget = accepted = stepdown = 0
examples = []
meaningful_under = 0
largest_under = None
for k in range(20000):
    try:
        e = EngineSpec(10 ** rng.uniform(-300, 300), 10 ** rng.uniform(-300, 306))
        dry = 10 ** rng.uniform(-310, 300)
        prop = 10 ** rng.uniform(-310, 300)
        SpacecraftSpec(dry, e, TankSpec(prop))
        dep = prop / e.mass_flow_kgps
        if not math.isfinite(dep) or dep <= 0:
            continue
        a = dep * rng.choice([rng.random(), 1.0, 1.0 - 10 ** rng.uniform(-17, -2)])
        b = math.nextafter(a, 0.0) if k % 2 else a * rng.random()
        if not 0 < b <= a <= dep:
            continue
        if k % 3:
            a, b = b, a
        got = timing_delta_v_error_mps(e, dry, prop, a, b)
        exact = oracle(e, dry, prop, a, b)
        checked += 1
        if Decimal(got) < exact:
            under += 1
            if exact > Decimal(1e-7):
                meaningful_under += 1
            if largest_under is None or exact > largest_under[0]:
                largest_under = (exact, got, e, dry, prop, a, b)
            if len(examples) < 5:
                examples.append(
                    dict(
                        F=e.thrust_n,
                        isp=e.isp_s,
                        dry=dry,
                        prop=prop,
                        a=a,
                        b=b,
                        got=got,
                        exact=str(exact),
                    )
                )
    except (PropulsionSpecError, OverflowError):
        pass
print("MEANINGFUL_UNDER", meaningful_under, "largest", largest_under, flush=True)
print("EXTREME", checked, "underestimates", under, "examples", json.dumps(examples), flush=True)
# force a just-over-budget error with subnormal x
for c in [1e300, 1e305, 1e307, 1e308]:
    t = 1e9
    d = 0.1
    D = (t + d) - t
    f = float(Decimal(2) * Decimal(1e-7) / abs(Decimal(d) - Decimal(D)))
    for k in range(20000):
        f = math.nextafter(f, math.inf)
        e = EngineSpec(f, c / 9.80665)
        exact = oracle(e, 1.0, 1.0, d, D)
        got = timing_delta_v_error_mps(e, 1.0, 1.0, d, D)
        if exact > Decimal(1e-7) and got <= 1e-7:
            p = plan_burn(e, 1.0, t, d, dry_mass_kg=1.0)
            print("FALSE_ACCEPT", repr(e), repr(p), "exact", exact, flush=True)
            break
# normal scheduling and ordinary-mission acceptance
for k in range(3000):
    e = EngineSpec(10 ** rng.uniform(-3, 5), 10 ** rng.uniform(1, 4))
    dry = 10 ** rng.uniform(-3, 5)
    prop = 10 ** rng.uniform(-3, 3)
    t = 10 ** rng.uniform(-5, 16)
    dep = prop / e.mass_flow_kgps
    d = dep * rng.uniform(0.01, 2)
    a = min(d, dep)
    cut = t + a
    D = cut - t
    if D > dep:
        stepdown += 1
    while D > dep:
        cut = math.nextafter(cut, -math.inf)
        D = cut - t
    exact = oracle(e, dry, prop, a, D)
    try:
        p = plan_burn(e, prop, t, d, "burn_to_depletion", dry_mass_kg=dry)
    except BurnRejectedError:
        continue
    accepted += 1
    assert exact <= Decimal(1e-7)
print("NORMAL", accepted, "accepted; stepdown", stepdown, flush=True)
e = EngineSpec(490, 312)
n = reject = false = 0
maxerr = 0
for k in range(10001):
    t = 1e9 * k / 10000
    for d in [77.3, 0.1, 1.0, 300 / e.mass_flow_kgps, 3000.0]:
        a = min(d, 300 / e.mass_flow_kgps)
        cut = t + a
        D = cut - t
        while D > 300 / e.mass_flow_kgps:
            cut = math.nextafter(cut, -math.inf)
            D = cut - t
        exact = oracle(e, 1000.0, 300.0, a, D)
        maxerr = max(maxerr, float(exact))
        n += 1
        try:
            plan_burn(e, 300, t, d, "burn_to_depletion", dry_mass_kg=1000.0)
        except BurnRejectedError:
            reject += 1
            false += exact <= Decimal(1e-7)
print("REFERENCE", n, "reject", reject, "false_reject", false, "max_exact", maxerr)
