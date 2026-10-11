exec(open('review_scratch/fast.py').read().split("execute('baseline'")[0].replace('fast-results.json','extra-results.json'))

def shift_depletion(r):
    ids={e.burn_id for e in r.events if e.type=='BurnEnded' and e.end_cause=='propellant_depleted'}
    out=[]
    for e in r.events:
        u={}
        if getattr(e,'burn_id',None) in ids:
            if e.type in ('CommandAccepted','BurnStarted'):u['planned_cutoff_t_s']=e.planned_cutoff_t_s+1e-5
            if e.type in ('PropellantDepleted','BurnEnded'):u['event_t_s']=e.event_t_s+1e-5
            if e.type=='BurnEnded':u['executed_duration_s']=u['event_t_s']-e.ignition_t_s
        out.append(e.model_copy(update=u) if u else e)
    r.events=out
    return r
execute('Depletion.time_shift_10us',shift_depletion)

def wrong_ignition(r):
    if 'invalid_commands' in r.scenario.name or 'burn_to_depletion' in r.scenario.name:
        r.events=[e.model_copy(update={'r':tuple(1.000001*x for x in e.r),'v':tuple(1.000001*x for x in e.v)}) if e.type=='BurnStarted' else e for e in r.events]
    return r
execute('BurnStarted.scaled_state_non_O6',wrong_ignition)

load_original=load_scoped_thresholds
def missing_o4(*args,**kwargs):
    data=json.loads(Path('proof/thresholds/m2.json').read_text()); del data['limits']['o4_reference']
    path=Path('review_scratch/missing-o4.json');path.write_text(json.dumps(data))
    return load_original(path=path,missions=kwargs.get('missions',frozenset()))
load_scoped_thresholds=missing_o4
execute('Thresholds.missing_O4_plus_doubled_powered_sample',event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==660))
load_scoped_thresholds=load_original

schedule=m2.Simulator.schedule_burn
def twice(self,*args,**kwargs):
    if isinstance(self._force_model,m2.FreeSpace):kwargs['duration_s']*=2
    return schedule(self,*args,**kwargs)
# Field name read from Simulator constructor in source; see below.
mutation=lambda r:r
m2.Simulator.schedule_burn=twice
execute('O3.double_commanded_duration',lambda r:r)
m2.Simulator.schedule_burn=schedule
execute('F3.actual_powered_sample_660',event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==660))
load_scoped_thresholds=missing_o4
execute('Thresholds.missing_O4_plus_doubled_660',event_mut('StateSampled',lambda e:{'r':[2*x for x in e.r]},lambda e:e.t==660))
load_scoped_thresholds=load_original
execute('CommandRejected.schema_invalid_duration',event_mut('CommandRejected',{'commanded_duration_s':999.},lambda e:e.reason=='schema_invalid'))
execute('CommandRejected.schema_invalid_policy',event_mut('CommandRejected',{'on_insufficient_propellant':'burn_to_depletion'},lambda e:e.reason=='schema_invalid'))

def ended_mass(r):
    if r.final.t>1000:
        r=event_mut('BurnStarted',{'total_mass_kg':999.})(r)
    return r
execute('BurnStarted.total_mass_completed_missions',ended_mass)
