import importlib.util, sys
import numpy as np
from tars.sim.simulator import Simulator
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec,SpacecraftSpec,TankSpec
spec=importlib.util.spec_from_file_location('old_sim','review_scratch/m1_simulator.py');old=importlib.util.module_from_spec(spec);sys.modules['old_sim']=old;spec.loader.exec_module(old)
sc=SpacecraftSpec(1000,EngineSpec(490,312),TankSpec(300))
for dt in (10.,.1,7/3):
 sims=[old.Simulator([6628137,0,0],[0,7755,100],PointMassGravity(3.986004418e14),RK4(),dt),*[Simulator([6628137,0,0],[0,7755,100],PointMassGravity(3.986004418e14),RK4(),dt,spacecraft=s) for s in (None,sc)]]
 for _ in range(600):
  for s in sims:s.step()
 states=[np.concatenate([s.snapshot().r,s.snapshot().v]).tobytes() for s in sims]
 print(dt,'pre-T2 vs no spacecraft vs spacecraft coast byte-identical',len(set(states))==1)
