import math, json, importlib.util
from pathlib import Path
import numpy as np
from probes import sim,sc,Zero
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4
from tars.sim.propulsion import SpacecraftSpec,TankSpec
s=sim()
try:s.schedule_burn('prograde',10**1000,1)
except Exception as e:print('huge integer',type(e).__name__)
# Several events, back-to-back and gap inside a single tick; independent free-space oracle.
s=sim(10);s.schedule_burn('prograde',1,2);s.schedule_burn('prograde',3,1);s.schedule_burn('prograde',5,2);s.step()
mdot=490/(312*9.80665); c=312*9.80665
x,v,m=1.,1.,1300.; now=0.
for start,dur in [(1,2),(3,1),(5,2)]:
 x+=v*(start-now);mf=m-mdot*dur
 x+=v*dur+c*(dur-mf/mdot*math.log(m/mf))
 v+=c*math.log(m/mf);m=mf;now=start+dur
x+=v*(10-now)
print('multi-events',[(e.kind,e.t) for e in s.engine_transitions],'errors x/v/prop',s.snapshot().r[0]-x,s.snapshot().v[0]-v,s.propulsion_snapshot().propellant_kg-(m-1000))
s=sim();s.schedule_burn('prograde',0,20);s.step();p=s.schedule_burn('retrograde',25,2);s.step();s.step(); print('mid-burn future plan',p.cutoff_t_s,'used',300-s.propulsion_snapshot().propellant_kg,'expected',mdot*22)
# Depletion with a representable but lengthened event interval.
s=Simulator([1,0,0],[1,0,0],Zero(),RK4(),1e15+10,spacecraft=SpacecraftSpec(1000,sc.engine,TankSpec(mdot*.2)))
p=s.schedule_burn('prograde',1e15,.2,policy='burn_to_depletion');s.step();print('rounded depletion interval',p.cutoff_t_s-p.ignition_t_s,'floor residual removed kg',mdot*((p.cutoff_t_s-p.ignition_t_s)-p.burn_duration_s),'dv',s.propulsion_snapshot().delta_v_sensed_mps,'rocket',c*math.log((1000+mdot*.2)/1000))
spec=importlib.util.spec_from_file_location('measure','docs/science/experiments/m2-t2/measure_t2.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
measured=[mod.run(dt) for dt in (20.,10.,5.,2.5)]
saved=json.loads(Path('docs/science/experiments/m2-t2/results.json').read_text())['rows']
print('VAL0012 rerun fields identical',all(all(row[k]==saved[i][k] for k in row) for i,row in enumerate(measured)))
Path('review_scratch/val0012.json').write_text(json.dumps(measured,indent=2)+'\n')
