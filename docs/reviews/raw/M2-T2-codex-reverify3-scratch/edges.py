# ruff: noqa
import math, random
import tars.sim.propulsion as p
from stages import Zero, Watch
from tars.sim.simulator import Simulator

engine = p.EngineSpec(490, 312)
# Accepted exact-depletion plan fails before cutoff for an allowed small dry mass.
tank = engine.mass_flow_kgps
s = Simulator(
    [1, 0, 0],
    [10000, 0, 0],
    Zero(),
    Watch(),
    0.1,
    spacecraft=p.SpacecraftSpec(1e-20, engine, p.TankSpec(tank)),
)
plan = s.schedule_burn("prograde", 0, 1)
try:
    for _ in range(10):
        s.step()
except Exception as e:
    print("SMALL_DRY_FAILURE", s.tick, type(e).__name__, str(e))
# Count step-down operations over edge and random inputs.
original = p.math.nextafter
calls = 0
maximum = 0


def counted(a, b):
    global calls
    calls += 1
    if calls > 100:
        raise RuntimeError("step-down >100")
    return original(a, b)


p.math.nextafter = counted
rng = random.Random(17)
accepted = rejected = 0
cases = [
    (t, d)
    for t in [0.0, 5e-324, 1e-300, 1.0, 1e9, 1e15, 1e308, -1.0, -1e9, -1e308]
    for d in [5e-324, 1e-320, 1e-300, 1.2e-16, 0.1, 1.0, 1e9, 1e308]
]
cases += [
    (
        math.ldexp(rng.uniform(-1, 1), rng.randrange(-1000, 1000)),
        math.ldexp(rng.uniform(0.5, 1), rng.randrange(-1000, 1000)),
    )
    for _ in range(20000)
]
for t, d in cases:
    for policy in ["reject", "burn_to_depletion"]:
        tank = engine.mass_flow_kgps * d
        if not math.isfinite(tank) or tank == 0:
            continue
        calls = 0
        try:
            plan = p.plan_burn(
                engine,
                tank,
                t,
                tank / engine.mass_flow_kgps if policy == "reject" else d * 2,
                policy,
                earliest_t_s=min(t, 0),
            )
            assert 0 < plan.burn_duration_s <= tank / engine.mass_flow_kgps
            accepted += 1
        except p.BurnRejectedError:
            rejected += 1
        maximum = max(maximum, calls)
print(
    "STEP_DOWN",
    len(cases),
    "cases",
    accepted,
    "accepted",
    rejected,
    "rejected",
    "max calls",
    maximum,
)
for d in [0, -1]:
    try:
        p.plan_burn(engine, 1, 0, d)
    except p.BurnRejectedError as e:
        print("NONPOSITIVE", d, e.reason)
