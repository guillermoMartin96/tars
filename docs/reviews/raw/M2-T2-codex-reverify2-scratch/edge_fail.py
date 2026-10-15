# ruff: noqa
from tars.sim.propulsion import EngineSpec
from stages import Zero
from types import SimpleNamespace
sc = SimpleNamespace(engine=EngineSpec(490,312))
from tars.sim.propulsion import SpacecraftSpec, TankSpec, plan_burn
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4

mdot = sc.engine.mass_flow_kgps
tank = mdot * 0.1
intended = tank / mdot
craft = SpacecraftSpec(1e-10, sc.engine, TankSpec(tank))
s = Simulator([1, 0, 0], [1, 0, 0], Zero(), RK4(), 1e9 + 1, spacecraft=craft)
p = s.schedule_burn("prograde", 1e9, intended)
print("ACCEPTED", p)
try:
    s.step()
except Exception as e:
    print("STEP FAILED", type(e).__name__, str(e), "tick", s.tick)
print("overdraw kg", mdot * p.burn_duration_s - tank, "dry mass kg", craft.dry_mass_kg)
