import dataclasses,json
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario
limits=json.load(open('proof/thresholds/m2.json'))['limits']
rows=[]
for mission in MISSIONS:
 s=mission.build();r=run_scenario(s);d=r.events[-1];alts=[e.altitude_m for e in r.events if e.type=='StateSampled']
 r.events[-1]=d.model_copy(update={'min_altitude_m':min(alts),'max_altitude_m':max(alts)})
 a=m2.audit_run(s,mission.expected,r)
 failures=[f'{g}.{k}' for g,ms in a.metrics.items() for k,lim in {**limits[g]['all'],**limits[g].get(mission.name,{})}.items() if k in ms and not ms[k]<=lim]
 rows.append({'mission':mission.name,'minimum_error_m':min(alts)-d.min_altitude_m,'maximum_error_m':d.max_altitude_m-max(alts),'violations':a.violations,'gate_failures':failures})
open('review_scratch/extrema.json','w').write(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
