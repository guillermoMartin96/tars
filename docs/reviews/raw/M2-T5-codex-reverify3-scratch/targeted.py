exec(open('review_scratch/fast.py').read().split("execute('baseline'")[0].replace('fast-results.json','targeted-results.json'))

def main_slice(r):
    return r.scenario.name in ('m2_prograde_burn','m2_retrograde_burn')
def scoped(fn,predicate=main_slice):
    return lambda r:fn(r) if predicate(r) else r
execute('F3.literal_630_auxiliary_samples',event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==630))
execute('Propulsion.nonfinal_pending',event_mut('PropulsionSampled',{'pending_burn_ids':('burn#999999',)},lambda e:e.t==120))
execute('Propulsion.powered_nonfinal_dv',event_mut('PropulsionSampled',{'delta_v_sensed_mps':999.},lambda e:e.t==610 and e.engine_state=='burning'))
execute('Propulsion.powered_nonfinal_mass',event_mut('PropulsionSampled',lambda e:{'propellant_kg':e.propellant_kg-1.,'total_mass_kg':e.total_mass_kg-1.,'thrust_acceleration_mps2':tuple(x*e.total_mass_kg/(e.total_mass_kg-1.) for x in e.thrust_acceleration_mps2)},lambda e:610<=e.t<=650 and e.engine_state=='burning'))
execute('Propulsion.powered_engine_off',event_mut('PropulsionSampled',{'engine_state':'idle','active_burn_id':None,'thrust_acceleration_mps2':(0.,0.,0.)},lambda e:610<=e.t<=650 and e.engine_state=='burning'))
execute('CommandRejected.schema_invalid_duration',event_mut('CommandRejected',{'commanded_duration_s':999.},lambda e:e.reason=='schema_invalid'))
execute('CommandRejected.schema_invalid_policy',event_mut('CommandRejected',{'on_insufficient_propellant':'burn_to_depletion'},lambda e:e.reason=='schema_invalid'))
load_original=load_scoped_thresholds
def missing_o4(*args,**kwargs):
    data=json.loads(Path('proof/thresholds/m2.json').read_text()); del data['limits']['o4_reference']
    path=Path('review_scratch/missing-o4.json');path.write_text(json.dumps(data))
    return load_original(path=path,missions=kwargs.get('missions',frozenset()))
load_scoped_thresholds=missing_o4
execute('Threshold.missing_O4_and_corrupt_powered',scoped(event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==660)))
load_scoped_thresholds=load_original
