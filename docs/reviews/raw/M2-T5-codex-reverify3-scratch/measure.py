import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario, initial_state
rows=[]
variants=[]
for mission in MISSIONS:
    s=mission.build();variants.append((mission.name,s,mission.expected))
    if any(x.status=='accepted' for x in mission.expected) and s.spacecraft is not None:
        variants.extend((s.name+'/dt'+str(dt),m2.convergence_variant(s,dt),mission.expected) for dt in m2.O8_DTS[1:])
    if mission.impulsive_limit:
        variants.extend((v.name,v,mission.expected) for v in m2.impulsive_variants(s))
base=MISSIONS[0].build()
variants.extend(('boundary/'+str(c),m2.boundary_variant(base,c),MISSIONS[0].expected) for c in m2.BOUNDARY_CASES)
for name,s,expected in variants:
    run=run_scenario(s);done=run.events[-1];h=done.t
    predicted=m2.predict_burns(s,expected);veh=m2.vehicle(s)
    r,v=initial_state(s);y=np.r_[r,v,0 if veh is None else veh.propellant_kg]
    ticks=np.arange(done.tick+1)*s.dt_s
    alts=[np.linalg.norm(r)-s.constants.equatorial_radius]
    spans=[]
    # Integrate only at physical discontinuities, independently of audit mark segmentation.
    bounds=sorted({0.,h,*[t for b in predicted for t in (b.ignition_t_s,b.cutoff_t_s) if 0<t<h]})
    for a,b in zip(bounds,bounds[1:]):
        burn=next((x for x in predicted if x.ignition_t_s<=a and b<=x.cutoff_t_s),None)
        sign=0 if burn is None else m2.SIGN[burn.direction]
        def rhs(t,z):
            rr,vv=z[:3],z[3:6]
            acc=-s.constants.mu*rr/np.linalg.norm(rr)**3
            if sign:acc=acc+sign*veh.thrust_n/(veh.dry_mass_kg+z[6])*vv/np.linalg.norm(vv)
            return np.r_[vv,acc,-veh.mass_flow_kgps if sign else 0.]
        sol=solve_ivp(rhs,(a,b),y,method='DOP853',rtol=2.3e-14,atol=1e-10,dense_output=True)
        assert sol.success
        ts=ticks[(ticks>a)&(ticks<=b)]
        alts.extend((np.linalg.norm(sol.sol(ts)[:3],axis=0)-s.constants.equatorial_radius).tolist())
        y=sol.y[:,-1];spans.append([a,b])
    assert len(alts)==done.tick+1
    audit=m2.audit_run(s,expected,run)
    rows.append(dict(name=name,horizon=h,ticks=len(alts),min_error=abs(done.min_altitude_m-min(alts)),max_error=abs(done.max_altitude_m-max(alts)),audit=audit.metrics['orbit_events'],reference_difference=max(abs(min(alts)-audit.reference.alt_min),abs(max(alts)-audit.reference.alt_max)),bounds=spans))
    print(name,rows[-1]['min_error'],rows[-1]['max_error'],flush=True)
open('review_scratch/measure.json','w').write(json.dumps(rows,indent=2))
