import json
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS,ACCEPT
from tars.sim.runner import run_scenario
from tars.sim.simulator import Simulator
base=MISSIONS[0].build()
variants=m2.impulsive_variants(base)
rows=[]
original=Simulator._powered_derivative
for factor in [1.,1.000001]:
 for mode in ['normal'] if factor==1 else ['mass_flow','sensed_integrand']:
  def changed(self,burn):
   fn=original(self,burn)
   if burn is None:return fn
   def rhs(t,y):
    out=fn(t,y);out[6 if mode=='mass_flow' else 7]*=factor;return out
   return rhs
  Simulator._powered_derivative=changed
  for variant in variants:
   r=run_scenario(variant);b=m2.predict_burns(variant,(ACCEPT,))[0];veh=m2.vehicle(variant)
   a=m2.audit_run(variant,(ACCEPT,),r)
   e=next(e for e in r.events if e.type=='BurnEnded')
   rows.append({'mode':mode,'factor':factor,'thrust':veh.thrust_n,'raw_error':abs(e.sensed_delta_v_mps-b.delta_v_mps),'bound':m2.simpson_bound(veh,b,variant.dt_s),'o2':a.metrics['o2_rocket_equation'],'sample':a.metrics['accounting']['sample_delta_v_excess_over_simpson_rel_max'],'violations':sum(map(len,a.violations.values()))})
Simulator._powered_derivative=original
open('review_scratch/numerical.json','w').write(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
