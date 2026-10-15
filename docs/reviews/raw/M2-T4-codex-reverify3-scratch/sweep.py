import copy,json,math,traceback,warnings,itertools
from pathlib import Path
from collections import Counter
from pydantic import ValidationError
from tars.sim.scenario import ScenarioV2,Scenario
from tars.sim.runner import run_scenario
from tars.sim.simulator import Simulator
warnings.filterwarnings('ignore',category=RuntimeWarning)
root=Path('review_scratch'); base=json.loads(Path('scenarios/m2_prograde_burn.json').read_text()); base.update(commands=[],stop={'duration_s':10.0})
counts=Counter(); crashes={}; saved=[]
original=Simulator.step
class LongRun(Exception):pass
def capped(self):
 if self.tick>=2:raise LongRun()
 return original(self)
Simulator.step=capped

def probe(name,data):
 try:s=ScenarioV2.model_validate(data)
 except ValidationError:counts['invalid']+=1;return
 except Exception as e:
  counts['validation crash']+=1;key=('validation',type(e).__name__,traceback.extract_tb(e.__traceback__)[-1].lineno)
 else:
  try:r=run_scenario(s,False);counts['recorded '+r.status+':'+str(r.failure_cause)]+=1;return
  except LongRun:counts['long run']+=1;return
  except Exception as e:
   counts['run crash']+=1;key=('run',type(e).__name__,traceback.extract_tb(e.__traceback__)[-1].filename,traceback.extract_tb(e.__traceback__)[-1].lineno)
  if key not in crashes:
   crashes[key]=name; (root/(name+'.json')).write_text(json.dumps(data));(root/(name+'.trace')).write_text(traceback.format_exc());saved.append(name)
  return
 if key not in crashes:
  crashes[key]=name;(root/(name+'.json')).write_text(json.dumps(data));(root/(name+'.trace')).write_text(traceback.format_exc());saved.append(name)

values=[5e-324,1e-308,1e-200,1e-100,1e-10,1.,10.,1e50,1e100,1e102,1e103,1e150,1e200,1e300,1e308]
for field in ['dt','altitude','inclination','sample','duration','submit','orbits','guard','dry','prop','thrust','isp']:
 for i,v in enumerate(values):
  d=copy.deepcopy(base)
  if field=='dt':d.update(dt_s=v,stop={'duration_s':v},telemetry={'sample_interval_s':v})
  elif field in ['altitude','inclination']:d['initial_orbit'][field+'_m' if field=='altitude' else 'inclination_deg']=v
  elif field=='sample':d['telemetry']['sample_interval_s']=v
  elif field=='duration':d['stop']={'duration_s':v}
  elif field=='submit':d['commands']=[{'submit_t_s':v,'command':{}}];d['stop']={'orbits':1}
  elif field=='orbits':d['stop']={'orbits':max(1,int(v))}
  elif field=='guard':d['stop']={'orbits':1,'max_duration_periods':v}
  elif field in ['dry','prop']:d['spacecraft']['dry_mass_kg' if field=='dry' else 'propellant_kg']=v
  else:d['spacecraft']['engine']['thrust_n' if field=='thrust' else 'isp_s']=v
  probe(f'{field}_{i}',d)
for p in [309,400,1000]:
 d=copy.deepcopy(base);d['stop']={'orbits':10**p};probe(f'huge_orbits_{p}',d)
for i,(dt,alt) in enumerate(itertools.product(values,values)):
 d=copy.deepcopy(base);d.update(dt_s=dt,stop={'duration_s':dt},telemetry={'sample_interval_s':dt});d['initial_orbit']['altitude_m']=alt;probe(f'coast_{i}',d)
cmd={'schema_version':1,'type':'BurnCommand','command_id':'probe','issuer':'review','ignition_t_s':0.,'direction':'prograde','duration_s':1.}
for i,(mass,thrust,isp,dt) in enumerate(itertools.product([1e-300,1e-100,1.,1e100,1e300],[1e-300,1.,1e100,1e300],[1e-300,1.,1e100,1e300],[1e-300,1e-100,1.,1e100])):
 d=copy.deepcopy(base);d.update(dt_s=dt,stop={'duration_s':dt},telemetry={'sample_interval_s':dt});d['spacecraft']={'dry_mass_kg':mass,'propellant_kg':mass,'engine':{'thrust_n':thrust,'isp_s':isp}};d['commands']=[{'submit_t_s':0.,'command':{**cmd,'duration_s':dt,'on_insufficient_propellant':'burn_to_depletion'}}];probe(f'burn_{i}',d)
print(counts);print(crashes);print('saved',saved)
import random
rng=random.Random(4)
for i in range(4000):
 exp=lambda lo=-320,hi=308:10.**rng.uniform(lo,hi)
 dt=exp();d=copy.deepcopy(base);d.update(dt_s=dt,stop={'duration_s':dt},telemetry={'sample_interval_s':dt})
 d['initial_orbit'].update(altitude_m=exp(-10,103),inclination_deg=rng.uniform(.001,179.999),raan_deg=rng.uniform(0,359.999),arg_latitude_deg=rng.uniform(0,359.999))
 if i%2:
  d['spacecraft']={'dry_mass_kg':exp(),'propellant_kg':exp(),'engine':{'thrust_n':exp(),'isp_s':exp()}}
  d['commands']=[{'submit_t_s':0.,'command':{**cmd,'direction':rng.choice(['prograde','retrograde']),'duration_s':dt,'on_insufficient_propellant':'burn_to_depletion'}}]
 probe(f'random_{i}',d)
print('expanded',counts);print(crashes)
