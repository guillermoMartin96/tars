import json, copy
from pathlib import Path
import numpy as np
from tars.sim.scenario import ScenarioV2, parse_scenario
from tars.sim import runner
from tars.sim.simulator import Simulator
from tars.sim.integrators import RK4
from tars.events import to_jsonl
base=json.loads(Path('scenarios/m2_prograde_burn.json').read_text()); base['stop']={'duration_s':30.0}
class Number(int): pass
p=copy.deepcopy(base); p['commands'][0]['command']['duration_s']=Number(5)
s=ScenarioV2.model_validate(p)
sim=Simulator(*runner.initial_state(s),runner.build_force_model(s),RK4(),s.dt_s,spacecraft=s.spacecraft.to_spec())
print('SUBCLASS direct',sim.submit(s.commands[0].command).status.value,'runner',runner.run_scenario(s).receipts[0].status.value)
a=copy.deepcopy(base); b=copy.deepcopy(base)
a['commands']=[{'command':{'x':b'abc'}}]; b['commands']=[{'command':{'x':'abc'}}]
sa=ScenarioV2.model_validate(a); sb=ScenarioV2.model_validate(b)
print('HASH bytes/str identical',sa.config_hash()==sb.config_hash())
try: s.with_dt(5.0)
except Exception as e: print('WITH_DT',type(e).__name__,str(e).splitlines()[2:4])
# Explicit multi-event and stop probes.
cmd=copy.deepcopy(base['commands'][0]['command'])
def run(cmds,stop=30.):
 d=copy.deepcopy(base); d['commands']=cmds; d['stop']={'duration_s':stop}; return runner.run_scenario(parse_scenario(json.dumps(d)))
for label,commands in [('back_to_back',[{'command':{**cmd,'command_id':'a','ignition_t_s':1.,'duration_s':2.}},{'command':{**cmd,'command_id':'b','ignition_t_s':3.,'duration_s':4.}}]),('stop_ignition',[{'command':{**cmd,'ignition_t_s':30.}}]),('stop_cutoff',[{'command':{**cmd,'ignition_t_s':20.,'duration_s':10.}}]),('stop_active',[{'command':{**cmd,'ignition_t_s':20.,'duration_s':20.}}]),('stop_pending',[{'command':{**cmd,'ignition_t_s':40.}}])]:
 r=run(commands); print(label,[(e.type,e.tick,e.event_t_s,e.burn_id) for e in r.events if e.type in ('BurnStarted','BurnEnded','PropellantDepleted')],r.final_propulsion.engine_state.value)
orig=runner.build_force_model
class Escape:
 def acceleration(self,t,r,v): return 1000*v/np.linalg.norm(v)
runner.build_force_model=lambda s:Escape()
r=run([{'submit_t_s':20.,'command':{**cmd,'ignition_t_s':20.}}]); print('ESCAPE',r.completed.failure_cause,r.completed.tick,r.unsubmitted_command_ids,len(r.receipts))
runner.build_force_model=orig
r1=run([{'command':cmd}]); r2=run([{'command':cmd}]); print('REPLAY',to_jsonl(r1.events)==to_jsonl(r2.events))
