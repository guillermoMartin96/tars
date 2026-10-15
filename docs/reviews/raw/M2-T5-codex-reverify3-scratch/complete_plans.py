import dataclasses,json
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario
rows=[]
scenarios=[(m.name,m.build()) for m in MISSIONS]
scenarios += [(str(c),m2.boundary_variant(MISSIONS[0].build(),c)) for c in m2.BOUNDARY_CASES]
for name,s in scenarios:
 r=run_scenario(s)
 assert not m2.check_result_consistency(s,r.events,r)
 for i,rec in enumerate(r.receipts):
  if rec.plan is None:continue
  for f in dataclasses.fields(rec.plan):
   val='fabricated' if f.name in ('policy','end_cause') else 999.
   receipts=list(r.receipts);receipts[i]=dataclasses.replace(rec,plan=dataclasses.replace(rec.plan,**{f.name:val}))
   v=m2.check_result_consistency(s,r.events,dataclasses.replace(r,receipts=receipts))
   rows.append(dict(scenario=name,where='receipt',field=f.name,rejected=bool(v)))
 fp=r.final_propulsion
 if fp:
  for where,plans in [('active_plan',[fp.active_plan] if fp.active_plan else []),('pending_plans',list(fp.pending_plans))]:
   for i,plan in enumerate(plans):
    for f in dataclasses.fields(plan):
     val='fabricated' if f.name in ('policy','end_cause') else 999.
     bad=dataclasses.replace(plan,**{f.name:val})
     if where=='active_plan':bfp=dataclasses.replace(fp,active_plan=bad)
     else:
      pp=list(plans);pp[i]=bad;bfp=dataclasses.replace(fp,pending_plans=tuple(pp))
     v=m2.check_result_consistency(s,r.events,dataclasses.replace(r,final_propulsion=bfp))
     rows.append(dict(scenario=name,where=where,field=f.name,rejected=bool(v)))
 for version in [999,True,1.,'1',None]:
  events=[e.model_copy(update={'schema_version':version}) for e in r.events]
  rows.append(dict(scenario=name,where='schema_version',field=repr(version),rejected=bool(m2.check_event_order(s,events))))
print('cases',len(rows),'accepted mutants',[x for x in rows if not x['rejected']])
open('review_scratch/complete-plans.json','w').write(json.dumps(rows,indent=2))
