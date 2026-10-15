import json,subprocess,os,traceback
from pathlib import Path
from tars.sim.scenario import Scenario,ScenarioV2
for cls,path in [(Scenario,'scenarios/m1_leo_250km.json'),(ScenarioV2,'scenarios/m2_prograde_burn.json')]:
 d=json.loads(Path(path).read_text());d.update(stop={'orbits':10**309})
 try:cls.model_validate(d)
 except Exception as e:print(cls.__name__,type(e).__name__,str(e))
for name in ['initial_norm','empty_forces']:
 r=subprocess.run(['.venv/bin/python','toolbox/scripts/run_mission.py','--scenario','review_scratch/'+name+'.json','--out','review_scratch/'+name+'_out'],capture_output=True,text=True,env={**os.environ,'PYTHONPATH':'src'})
 Path('review_scratch/'+name+'.cli.txt').write_text('exit='+str(r.returncode)+'\n'+r.stdout+r.stderr)
 print(name,r.returncode,r.stderr.splitlines()[-1])
