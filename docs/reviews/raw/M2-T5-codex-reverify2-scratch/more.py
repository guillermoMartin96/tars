exec(open('review_scratch/fast.py').read().split("execute('baseline'")[0].replace('fast-results.json','more-results.json'))
def sample_extrema(r):
    alts=[e.altitude_m for e in r.events if e.type=='StateSampled']
    done=r.events[-1]
    print('extrema gap',r.scenario.name,min(alts)-done.min_altitude_m,done.max_altitude_m-max(alts),flush=True)
    return event_mut('SimulationCompleted',{'min_altitude_m':min(alts),'max_altitude_m':max(alts)})(r)
execute('completion.sample_extrema_instead_of_tick_extrema',sample_extrema)
def snapshot_plan_field(r):
    fp=r.final_propulsion
    if fp:
        def corrupt(plan):return dataclasses.replace(plan,ignition_t_s=999.,commanded_duration_s=999.,mass_flow_kgps=999.,burn_duration_s=999.,end_cause='fabricated',policy='fabricated',timing_delta_v_error_mps=999.)
        r.final_propulsion=dataclasses.replace(fp,active_plan=corrupt(fp.active_plan) if fp.active_plan else None,pending_plans=tuple(corrupt(x) for x in fp.pending_plans))
    return r
execute('snapshot.plan.unchecked_fields',snapshot_plan_field)
