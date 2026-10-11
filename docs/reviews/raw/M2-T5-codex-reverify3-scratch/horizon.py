import inspect,json
import numpy as np
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario,initial_state
source=inspect.getsource(m2.dop853_reference).replace('        if t <= horizon\n','')
ns=dict(vars(m2));exec(source,ns);unclipped=ns['dop853_reference']
rows=[]
for case in m2.BOUNDARY_CASES:
 s=m2.boundary_variant(MISSIONS[0].build(),case);run=run_scenario(s);p=m2.predict_burns(s,MISSIONS[0].expected)
 r,v=initial_state(s);marks=[0.,run.final.t]
 ref=m2.dop853_reference(s,r,v,p,marks);old=unclipped(s,r,v,p,marks)
 rows.append(dict(case=str(case),horizon=run.final.t,predicted_cutoff=p[0].cutoff_t_s,new_extrema=[ref.alt_min,ref.alt_max],unclipped_extrema=[old.alt_min,old.alt_max],difference=max(abs(ref.alt_min-old.alt_min),abs(ref.alt_max-old.alt_max)),same_end_state=bool(np.array_equal(ref[run.final.t],old[run.final.t]))))
print(json.dumps(rows,indent=2));open('review_scratch/horizon.json','w').write(json.dumps(rows,indent=2))
