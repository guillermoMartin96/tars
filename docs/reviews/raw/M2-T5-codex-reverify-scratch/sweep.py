import copy
import dataclasses
import importlib.util
import json
from pathlib import Path
import numpy as np
from tars.sim import runner
from tars.validation import m2
from tars.validation.thresholds import load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS
spec=importlib.util.spec_from_file_location('proof_cli','toolbox/validators/m2_proof.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
original=runner.run_scenario
cache={}
mutation=lambda r:r
initial=runner.initial_state
mode='normal'
def cached(scenario,record_samples=True):
    if mode=='rotated':
        return mutation(original(scenario,record_samples))
    if mode=='short' and scenario.stop.duration_s>3000:
        raw=scenario.model_dump(mode='json'); raw['stop']={'duration_s':3000.0}
        scenario=type(scenario).model_validate(raw)
    key=(scenario.config_hash(),record_samples)
    if key not in cache: cache[key]=original(scenario,record_samples)
    return mutation(copy.deepcopy(cache[key]))
runner.run_scenario=p.run_scenario=cached
ref_original=m2.dop853_reference
refs={}
def ref_cached(scenario,r,v,b,marks):
    key=(scenario.config_hash(),tuple(r),tuple(v),tuple(marks))
    if key not in refs: refs[key]=ref_original(scenario,r,v,b,marks)
    return refs[key]
m2.dop853_reference=ref_cached
results={}
def all_checks():
    thresholds=load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
    checks=[]
    for mission in MISSIONS: checks+=p.mission_checks(mission,thresholds,False)[0]
    checks+=p.boundary_checks()[0]
    from tars.validation.thresholds import Check
    checks.append(Check('o3_free_space',m2.free_space_metrics(m2.vehicle(MISSIONS[0].build()),p.O3_DURATION_S),thresholds.for_validator('o3_free_space'),'provisional'))
    checks.append(p._exact('thresholds_all_consumed',thresholds.unused()))
    return checks

def execute(name,fn):
    global mutation
    mutation=fn
    try:
        checks=all_checks()
        results[name]={'passed':all(c.passed for c in checks),'checks':len(checks),'failed':[c.validator for c in checks if not c.passed]}
    except Exception as e: results[name]={'exception':repr(e)}
    print(name,results[name],flush=True)
    Path('review_scratch/sweep-results.json').write_text(json.dumps(results,indent=2))

def event_mut(typ,updates,where=lambda e:True):
    def change(r):
        r.events=[e.model_copy(update=updates(e) if callable(updates) else updates) if e.type==typ and where(e) else e for e in r.events]
        return r
    return change

def result_mut(**updates):
    def change(r):
        for k,v in updates.items(): setattr(r,k,v(r) if callable(v) else v)
        return r
    return change

execute('baseline',lambda r:r)
rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
runner.initial_state=lambda s:tuple(rot@x for x in initial(s)); mode='rotated'
execute('F1_rotated_initial',lambda r:r)
runner.initial_state=initial; mode='short'
execute('F2_stop_3000',lambda r:r); mode='normal'
execute('F3_doubled_powered_sample',event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==630))
execute('F3_bogus_boundary_completion',event_mut('SimulationCompleted',{'r':[1e9,0.,0.],'v':[1e6,0.,0.]},lambda e:e.t==660))
execute('F4_delete_depletion',lambda r:dataclasses.replace(r,events=[e for e in r.events if e.type!='PropellantDepleted']))
probes={
'SimulationStarted':{'scenario_name':'wrong','scenario_hash':'0'*64,'software_version':'wrong','epoch':'wrong','time_scale':'wrong','seed':999,'earth_constants':{},'force_models':[],'integrator':'wrong','dt':999.},
'SpacecraftConfigured':{'timing_delta_v_budget_mps':999.,'direction_laws':('radial',)},
'CommandAccepted':{'issuer':'wrong','planned_burn_duration_s':999.,'planned_propellant_used_kg':999.,'timing_delta_v_error_mps':999.},
'CommandRejected':{'issuer':'wrong','detail':'wrong','schema_errors':()},
'BurnStarted':{'planned_end_cause':'propellant_depleted','r':(0.,0.,0.),'v':(0.,0.,0.),'thrust_unit_vector':(0.,0.,0.),'propellant_kg':999.,'total_mass_kg':999.},
'BurnEnded':{'planned_propellant_used_kg':999.,'total_mass_kg':999.},
'PropellantDepleted':{'residual_propellant_kg':999.},
'StateSampled':{'altitude_m':-999.},
'OrbitCompleted':{'orbit_number':999,'crossing_t':-999.},
'SimulationCompleted':{'orbits_completed':999,'min_altitude_m':-999.,'max_altitude_m':999.},
}
for typ,fields in probes.items():
    for field,value in fields.items(): execute(typ+'.'+field,event_mut(typ,{field:value}))
execute('OrbitCompleted.deleted',lambda r:dataclasses.replace(r,events=[e for e in r.events if e.type!='OrbitCompleted']))
execute('RunResult.receipts',result_mut(receipts=[]))
execute('RunResult.samples',result_mut(samples=[]))
execute('RunResult.crossing_times',result_mut(crossing_times=[]))
execute('RunResult.status_failure_cause',result_mut(status='failure',failure_cause='escape'))
execute('RunResult.initial',result_mut(initial=None))
execute('RunResult.final.t',result_mut(final=lambda r:dataclasses.replace(r.final,t=-999.)))
execute('RunResult.final_propulsion.t',result_mut(final_propulsion=lambda r:dataclasses.replace(r.final_propulsion,t=-999.) if r.final_propulsion else None))
execute('RunResult.final_propulsion.plans',result_mut(final_propulsion=lambda r:dataclasses.replace(r.final_propulsion,active_direction='radial',pending_plans=()) if r.final_propulsion else None))
execute('RunResult.unsubmitted',result_mut(unsubmitted_command_ids=['bogus']))
execute('PropulsionSampled.nonfinal_schedule',event_mut('PropulsionSampled',{'pending_burn_ids':('burn#999999',)},lambda e:e.t<500))
execute('PropulsionSampled.nonfinal_dv',event_mut('PropulsionSampled',{'delta_v_sensed_mps':999.},lambda e:e.t==630))
execute('PropulsionSampled.nonfinal_mass',event_mut('PropulsionSampled',lambda e:{'propellant_kg':e.propellant_kg-1.,'total_mass_kg':e.total_mass_kg-1.,'thrust_acceleration_mps2':tuple(x*e.total_mass_kg/(e.total_mass_kg-1.) for x in e.thrust_acceleration_mps2)},lambda e:650<=e.t<=670))
execute('PropulsionSampled.nongrid_direction',event_mut('PropulsionSampled',lambda e:{'thrust_acceleration_mps2':tuple(-x for x in e.thrust_acceleration_mps2)},lambda e:e.t==610))
execute('PropulsionSampled.engine_off',event_mut('PropulsionSampled',{'engine_state':'idle','active_burn_id':None,'thrust_acceleration_mps2':(0.,0.,0.)},lambda e:610<=e.t<=670))
def no_burn_wrong(r):
    if r.scenario.spacecraft is None or r.scenario.spacecraft.propellant_kg==0:
        r.events=[e.model_copy(update={'r':tuple(2*x for x in e.r),'v':tuple(2*x for x in e.v)}) if e.type in ('SimulationStarted','StateSampled','SimulationCompleted') else e for e in r.events]
        r.final=dataclasses.replace(r.final,r=2*r.final.r,v=2*r.final.v)
    return r
execute('NoBurn.double_all_states',no_burn_wrong)
