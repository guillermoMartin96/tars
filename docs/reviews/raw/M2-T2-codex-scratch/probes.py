import numpy as np
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4
from tars.sim.propulsion import *
class Zero:
 def acceleration(self,t,r,v): return np.zeros(3)
sc=SpacecraftSpec(1000,EngineSpec(490,312),TankSpec(300))
def sim(dt=10,force=None): return Simulator([1,0,0],[1,0,0],force or Zero(),RK4(),dt,spacecraft=sc)
for x in [-np.inf,'-1',True,np.array(-1), np.float32(1),np.bool_(True)]:
 s=sim(); s.step()
 try: p=s.schedule_burn('prograde',x,1); print('input',repr(x),'accepted',p)
 except Exception as e: print('input',repr(x),type(e).__name__,str(e))
s=sim(1e15+10); p=s.schedule_burn('prograde',1e15,.1); s.step(); print('duration rounding',p.burn_duration_s,p.cutoff_t_s-p.ignition_t_s,'planned used',p.propellant_used_kg,'actual used',300-s.propulsion_snapshot().propellant_kg)
s=sim();s.schedule_burn('prograde',1,1);s.step(); e=s.engine_transitions[0];e.r.flags.writeable=True;e.r[0]=999;print('transition mutable',s.engine_transitions[0].r,'physical',s.snapshot().r)
class Fail:
 def __init__(self): self.bad=True
 def acceleration(self,t,r,v):
  if self.bad and t>=2: return np.full(3,np.nan)
  return np.zeros(3)
f=Fail();s=sim(force=f);s.schedule_burn('prograde',1,2)
try:s.step()
except Exception as e:print('failed step',type(e).__name__,'tick',s.tick,'state',s.propulsion_snapshot())
f.bad=False;s.step();print('retried events',[(e.kind,e.t) for e in s.engine_transitions],'used',300-s.propulsion_snapshot().propellant_kg,'expected',sc.engine.mass_flow_kgps*2)
