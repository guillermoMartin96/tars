import copy,json,math,sys,traceback
from pathlib import Path
from pydantic import ValidationError
from tars.sim.scenario import ScenarioV2
from tars.sim.runner import initial_state,run_scenario
from tars.sim.forces import PointMassGravity
from tars.sim.simulator import Simulator
import numpy as np
base=json.loads(Path('scenarios/m2_prograde_burn.json').read_text());base.update(commands=[],stop={'duration_s':10.})
cube=math.exp(math.log(sys.float_info.max)/3);radii=[]
for sign in [-math.inf,math.inf]:
 r=cube
 for _ in range(300):
  radii.append(r);r=math.nextafter(r,sign)
counts={};found=None
for radius in radii:
 for raan,inc,arg in [(0.,51.6,0.),(123.,63.,53.),(315.,179.,310.),(20.,45.,70.)]:
  d=copy.deepcopy(base);d['initial_orbit'].update(altitude_m=radius,inclination_deg=inc,raan_deg=raan,arg_latitude_deg=arg)
  try:s=ScenarioV2.model_validate(d)
  except ValidationError:continue
  try:
   r,v=initial_state(s);PointMassGravity(s.constants.mu).acceleration(0,r,v)
  except Exception as e:
   if found is None:
    found=d;Path('review_scratch/initial_norm.json').write_text(json.dumps(d));print('initial crash',radius,np.linalg.norm(r),type(e).__name__,e)
print('initial boundary crash found',found is not None)
# Additional start-of-run and singular-stage probes.
for name,updates in [('empty_forces',{'force_models':[]}),('small_altitude',{'initial_orbit':{**base['initial_orbit'],'altitude_m':5e-324}})]:
 d={**base,**updates}
 try:
  s=ScenarioV2.model_validate(d);r=run_scenario(s,False);print(name,r.status,r.failure_cause)
 except Exception as e:
  Path('review_scratch/'+name+'.json').write_text(json.dumps(d));print(name,type(e).__name__,e)
# M1 timeout operation order preserved.
from tars.sim.scenario import load_scenario
s=load_scenario('scenarios/m1_leo_250km.json');print('M1 timeout',s.timeout_ticks)
