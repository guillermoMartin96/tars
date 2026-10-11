exec(open('review_scratch/fast.py').read().split("execute('baseline'")[0].replace('fast-results.json','new-results.json'))
execute('baseline',lambda r:r)
def receipt_field(field,value):
    def change(r):
        r.receipts=[dataclasses.replace(x,**{field:value(x) if callable(value) else value}) for x in r.receipts]
        return r
    return change
execute('receipt.command_absent',receipt_field('command',None))
execute('receipt.schema_errors',receipt_field('schema_errors',('fabricated',)))
execute('receipt.detail',receipt_field('detail','fabricated'))
for field in ['ignition_t_s','commanded_duration_s','mass_flow_kgps','timing_delta_v_error_mps']:
    execute('receipt.plan.'+field,receipt_field('plan',lambda x:dataclasses.replace(x.plan,**{field:999.}) if x.plan else None))
execute('receipt.plan.policy',receipt_field('plan',lambda x:dataclasses.replace(x.plan,policy='burn_to_depletion') if x.plan else None))
execute('RunResult.scenario',result_mut(scenario=lambda r:r.scenario.model_copy(update={'name':'fabricated'})))
def extra_idle_plan(r):
    if r.final_propulsion and r.receipts and r.receipts[0].plan and not r.final_propulsion.active_burn_id:
        r.final_propulsion=dataclasses.replace(r.final_propulsion,active_plan=r.receipts[0].plan)
    return r
execute('idle.active_plan',extra_idle_plan)
execute('event.schema_version',lambda r:dataclasses.replace(r,events=[e.model_copy(update={'schema_version':999}) for e in r.events]))
execute('rejection.detail',event_mut('CommandRejected',{'detail':'fabricated'}))
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
