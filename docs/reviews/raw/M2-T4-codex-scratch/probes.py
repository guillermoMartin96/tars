import copy, json, importlib.util, hashlib
from pathlib import Path
import numpy as np
from tars.sim import runner
from tars.sim.scenario import ScenarioV2, parse_scenario
base=json.loads(Path('scenarios/m2_prograde_burn.json').read_text())
def short():
 d=copy.deepcopy(base); d['stop']={'duration_s':30.0}; return d
# A failed first step retains tick zero but must show the submitted pending burn.
d=short(); original=runner.build_force_model
class Bad:
 def acceleration(self,t,r,v): return np.full(3,np.inf)
runner.build_force_model=lambda s: Bad()
r=runner.run_scenario(parse_scenario(json.dumps(d)))
print('FINAL SAMPLE',r.completed.tick,r.completed.failure_cause,[(e.tick,e.engine_state,e.pending_burn_ids) for e in r.events if e.type=='PropulsionSampled'],'snapshot',r.final_propulsion.engine_state,r.final_propulsion.pending_burn_ids)
runner.build_force_model=original
# Python payloads that are not standard JSON.
for payload in [{'x':(float('nan'),)}, {'x':b'abc'}, {'x':{1,2}}]:
 d=short(); d['commands']=[{'command':payload}]
 try:
  s=ScenarioV2.model_validate(d); print('PYTHON PAYLOAD accepted',repr(payload),'canonical',s.canonical_json()[-230:]); runner.run_scenario(s)
 except Exception as e: print('PYTHON PAYLOAD error',type(e).__name__,str(e)[:140])
# Finite but overflowed tick ratio.
d=short(); d['stop']={'duration_s':1e308}; d['dt_s']=1e-10; d['telemetry']={'sample_interval_s':1e-10}
try: parse_scenario(json.dumps(d))
except Exception as e: print('TICK RATIO',type(e).__name__,str(e)[:100])
# Failure on the second file replacement.
spec=importlib.util.spec_from_file_location('cli','toolbox/scripts/run_mission.py'); cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(cli)
out=Path('review_scratch/atomic'); out.mkdir(exist_ok=True)
(out/'events.jsonl').write_text('old events'); (out/'summary.json').write_text('old summary')
orig=cli.os.replace
def fail(src,dst):
 if Path(dst).name=='summary.json': raise OSError('injected summary replace failure')
 return orig(src,dst)
cli.os.replace=fail
try: cli.main(['--scenario','scenarios/m2_prograde_burn.json','--out',str(out)])
except OSError as e: print('PAIR FAILURE',str(e),'events_changed',(out/'events.jsonl').read_text()!='old events','summary',(out/'summary.json').read_text())
finally: cli.os.replace=orig
