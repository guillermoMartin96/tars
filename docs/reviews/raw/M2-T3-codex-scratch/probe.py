import sys,json,dataclasses
sys.path.insert(0,'tests')
from test_commands import _sim,_cmd,DRY,ENGINE,_executed_burn
from tars.sim.commands import BurnCommand
from tars.sim.burn_events import command_event,burn_ended_event,propulsion_sampled_event
from tars.events import parse_event
from pydantic import ValidationError

def run(label, f):
 try: print(label,repr(f()))
 except Exception as e: print(label,type(e).__name__,str(e)[:300])

s=_sim(); before=(s._seen_command_ids.copy(),s._burn_count,s.propulsion_snapshot())
r=s.submit(_cmd(duration_s=0.0))
print('rejection registry',before[0],s._seen_command_ids,'burn count',s._burn_count,'retry',s.submit(_cmd()).reason)
for value in ['a\n','é','a\x00','a'*65]:
 run('id '+repr(value),lambda value=value: BurnCommand(**_cmd(command_id=value)))
for value in [True,1.0,'1']:
 run('version '+repr(value),lambda value=value: BurnCommand(**_cmd(schema_version=value)).schema_version)
for value in [10**1000,1e308,-1e308,5e-324]:
 run('duration '+str(value)[:30],lambda value=value: _sim().submit(_cmd(duration_s=value)).reason)
for value in ['\ud800','\x00\n','é']:
 def probe(value=value):
  r=_sim().submit(_cmd(issuer=value)); return (r.status,command_event(r).model_dump_json())
 run('issuer '+ascii(value),probe)
s=_sim();cmd=BurnCommand(**_cmd());r=s.submit(cmd);ev=command_event(r)
cmd.__dict__['duration_s']=123.0
print('receipt alias',r.command is cmd,r.command.duration_s,r.plan.commanded_duration_s,command_event(r).commanded_duration_s,ev.commanded_duration_s)
for overrides in [{'issuer':[]},{'command_id':[]},{'duration_s':'bad'},{'schema_version':2},{'direction':'bad'}]:
 run('model_copy '+repr(overrides),lambda overrides=overrides: _sim().submit(BurnCommand(**_cmd()).model_copy(update=overrides)))
s=_sim(); s.schedule_burn('prograde',600.,10.,command_id='same');r=s.submit(_cmd(command_id='same',ignition_t_s=700.,duration_s=10.))
print('duplicate low-level correlation',[(b.burn_id,b.command_id) for b in s._pending],r.status)
s,receipt,tr=_executed_burn(); ign,it,itt=tr['ignition']; cut,ct,ctt=tr['cutoff']
base=burn_ended_event(ign,cut,tick=ct,t=ctt,dry_mass_kg=DRY,engine=ENGINE)
changed=dataclasses.replace(cut,t=cut.t+1.,propellant_kg=cut.propellant_kg-1.,delta_v_sensed_mps=cut.delta_v_sensed_mps+2.)
ev=burn_ended_event(ign,changed,tick=ct,t=ctt,dry_mass_kg=DRY,engine=ENGINE)
print('outcome mutation',[(k,getattr(base,k),getattr(ev,k)) for k in ['executed_duration_s','propellant_used_kg','sensed_delta_v_mps','planned_propellant_used_kg']])
for updates in [{'schema_version':True},{'schema_version':1.0},{'command_id':'bad\n#'}, {'burn_id':''}]:
 data=base.model_dump(mode='json');data.update(updates)
 run('event JSON '+repr(updates),lambda data=data:parse_event(json.dumps(data)).model_dump())
print('sample keys',propulsion_sampled_event(s.propulsion_snapshot()).model_dump().keys())
