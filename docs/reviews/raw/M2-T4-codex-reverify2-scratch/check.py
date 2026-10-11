from pathlib import Path
import shutil, subprocess, os, json, math
from tars.sim.scenario import load_scenario, ScenarioV2
from tars.astro.elements import keplerian_period
root=Path.cwd(); scratch=root/'review_scratch'
for name in ['guard_product','orbit_tick_ratio']:
 p=root/f'docs/reviews/raw/M2-T4-codex-reverify-scratch/{name}.json'
 r=subprocess.run([str(root/'.venv/bin/python'),'toolbox/scripts/run_mission.py','--scenario',str(p),'--out',str(scratch/name)],capture_output=True,text=True)
 print(name,r.returncode,r.stderr.strip())
s=load_scenario('scenarios/m1_leo_250km.json')
old=math.ceil(s.stop.max_duration_periods*s.stop.orbits*keplerian_period(s.constants.equatorial_radius+s.initial_orbit.altitude_m,s.constants.mu)/s.dt_s)
print('M1 limit',old,s.timeout_ticks)
base=json.loads(Path('scenarios/m2_prograde_burn.json').read_text())
for altitude in [1e103,1e308]:
 for stop in [{'orbits':1},{'duration_s':10.0}]:
  data={**base,'commands':[],'stop':stop,'initial_orbit':{**base['initial_orbit'],'altitude_m':altitude}}
  try:
   v=ScenarioV2.model_validate(data)
   from tars.sim.runner import run_scenario
   r=run_scenario(v,False)
   print('extreme',altitude,stop,'result',r.status,r.failure_cause)
  except Exception as e: print('extreme',altitude,stop,type(e).__name__,str(e)[:160])
oldroot=scratch/'old'
for folder in ['src','tests','toolbox','scenarios','proof','docs']:
 shutil.copytree(root/folder,oldroot/folder,dirs_exist_ok=True)
sections=Path('T4-N1.diff').read_text().split('diff --git ')
patch=''.join('diff --git '+part for part in sections[1:] if part.startswith('a/src/'))
(scratch/'reverse.patch').write_text(patch)
r=subprocess.run(['patch','-R','-p1','-i',str(scratch/'reverse.patch')],cwd=oldroot,capture_output=True,text=True)
print('reconstruct',r.returncode,r.stdout)
env={**os.environ,'PYTHONPATH':str(oldroot/'src')}
r=subprocess.run([str(root/'.venv/bin/python'),'-m','pytest','-q','-p','no:cacheprovider','tests/test_scenario_v2.py','tests/test_cli.py','-k','unrepresentable_orbits_timeout or timeout_ticks_matches'],cwd=oldroot,env=env,capture_output=True,text=True)
(scratch/'old-tests.txt').write_text(r.stdout+r.stderr)
print('old tests',r.returncode,r.stdout[-1600:])
