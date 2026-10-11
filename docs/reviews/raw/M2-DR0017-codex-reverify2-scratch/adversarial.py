# ruff: noqa
import math, random, sys
from decimal import Decimal, localcontext
import numpy as np
from tars.sim.propulsion import *
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4

rng = random.Random(1701702)


class Zero:
    def acceleration(self, t, r, v):
        return np.zeros(3)


def positive():
    return math.ldexp(rng.uniform(0.5, 1), rng.randint(-1073, 1024))


n = under = 0
orders = [0, 0]
sub = overflow = cancel = 0
with localcontext() as ctx:
    ctx.prec = 800
    for k in range(160000):
        try:
            e = EngineSpec(positive(), positive())
            dry = positive()
            prop = positive()
            SpacecraftSpec(dry, e, TankSpec(prop))
        except (PropulsionSpecError, OverflowError):
            continue
        dep = prop / e.mass_flow_kgps
        if not math.isfinite(dep) or dep <= 0:
            continue
        a = dep * rng.choice([1.0, rng.random(), 1 - 2 ** -rng.randint(1, 53)])
        b = math.nextafter(a, 0.0) if k % 2 else a * rng.random()
        if not 0 < b < a:
            continue
        if k % 3:
            a, b = b, a
        got = timing_delta_v_error_mps(e, dry, prop, a, b)
        rem = max(Decimal(prop) - Decimal(e.mass_flow_kgps) * Decimal(max(a, b)), Decimal(0))
        exact_upper = Decimal(e.thrust_n) * abs(Decimal(a) - Decimal(b)) / (Decimal(dry) + rem)
        n += 1
        orders[a > b] += 1
        sub += 0 < got < sys.float_info.min
        overflow += math.isinf(got)
        cancel += rem < Decimal(prop) * Decimal("1e-10")
        if Decimal(got) < exact_upper:
            under += 1
            print("UNDER A_MAX", e, dry, prop, a, b, got, exact_upper)
            break
    print(
        "NEW FULL RANGE",
        n,
        "below exact a_max",
        under,
        "orderings",
        orders,
        "subnormal results",
        sub,
        "overflow results",
        overflow,
        "near cancellation",
        cancel,
        flush=True,
    )
    assert under == 0
    # Overflowing mass-flow product at rounded depletion, subnormal mass and slack.
    for e, dry, prop in [
        (EngineSpec(1e308, 1e-1), 1.0, 1e308),
        (EngineSpec(8e-323, 1.0), 5e-324, 5e-324),
        (EngineSpec(1.0, 1.0), 1e-300, 1e308),
    ]:
        dep = prop / e.mass_flow_kgps
        if not math.isfinite(dep):
            continue
        a = dep
        b = math.nextafter(a, 0.0)
        g = timing_delta_v_error_mps(e, dry, prop, a, b)
        exact = (
            Decimal(e.thrust_n)
            * abs(Decimal(a) - Decimal(b))
            / (
                Decimal(dry)
                + max(Decimal(prop) - Decimal(e.mass_flow_kgps) * Decimal(a), Decimal(0))
            )
        )
        assert math.isinf(g) or Decimal(g) >= exact
        print("DIRECTED", e, dry, prop, "bound", g, "exact_upper", exact)
    accepted = rejected = down = 0
    for k in range(3000):
        e = EngineSpec(10 ** rng.uniform(-4, 6), 10 ** rng.uniform(1, 5))
        dry = 10 ** rng.uniform(-2, 6)
        prop = 10 ** rng.uniform(-3, 6)
        s = Simulator(
            [1, 0, 0],
            [1, 0, 0],
            Zero(),
            RK4(),
            1.0,
            spacecraft=SpacecraftSpec(dry, e, TankSpec(prop)),
        )
        t = rng.uniform(0, 1e9)
        for j in range(8):
            available = s._committed_propellant_kg
            if available == 0:
                break
            dep = available / e.mass_flow_kgps
            d = dep * rng.choice([1.0, 2.0, rng.uniform(0.01, 0.9)])
            intended = min(d, dep)
            D = (t + intended) - t
            down += D > dep
            before = (s._committed_propellant_kg, len(s._pending), s._y.tobytes())
            try:
                p = s.schedule_burn("prograde", t, d, "burn_to_depletion")
            except BurnRejectedError:
                assert before == (s._committed_propellant_kg, len(s._pending), s._y.tobytes())
                rejected += 1
                break
            rem = max(
                Decimal(available)
                - Decimal(e.mass_flow_kgps) * Decimal(max(intended, p.burn_duration_s)),
                Decimal(0),
            )
            upper = (
                Decimal(e.thrust_n)
                * abs(Decimal(intended) - Decimal(p.burn_duration_s))
                / (Decimal(dry) + rem)
            )
            assert Decimal(p.timing_delta_v_error_mps) >= upper and upper <= Decimal(1e-7)
            accepted += 1
            t = p.cutoff_t_s
    print(
        "QUEUED",
        accepted,
        "accepted bounds verified",
        rejected,
        "atomic rejections",
        "stepdown candidates",
        down,
    )
