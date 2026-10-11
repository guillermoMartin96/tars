import json, traceback, subprocess
from pathlib import Path
from tars.sim.scenario import parse_scenario
from tars.sim.runner import run_scenario
p=Path('review_scratch/duration_large_radius.json')
d=json.loads(Path('scenarios/m2_prograde_burn.json').read_text()); d['commands']=[]; d['stop']={'duration_s':10.0}; d['initial_orbit']['altitude_m']=1e103
p.write_text(json.dumps(d))
s=parse_scenario(p.read_text()); print('valid duration scenario',s.stop_tick,s.timeout_ticks)
try: run_scenario(s)
except Exception: traceback.print_exc()
r=subprocess.run(['.venv/bin/python','toolbox/scripts/run_mission.py','--scenario',str(p),'--out','review_scratch/extreme'],capture_output=True,text=True)
print('CLI exit',r.returncode,r.stderr)
