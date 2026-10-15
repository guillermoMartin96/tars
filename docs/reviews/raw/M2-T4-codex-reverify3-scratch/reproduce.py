import subprocess,os,json,shutil
from pathlib import Path
root=Path.cwd(); scratch=root/'review_scratch'
for name,p in [('original',root/'docs/reviews/raw/M2-T4-codex-reverify2-scratch/duration_large_radius.json')]+[(n,scratch/(n+'.json')) for n in ['dt_8','huge_orbits_309','coast_188','burn_40']]:
 r=subprocess.run([str(root/'.venv/bin/python'),'toolbox/scripts/run_mission.py','--scenario',str(p),'--out',str(scratch/(name+'_out'))],env={**os.environ,'PYTHONPATH':'src'},capture_output=True,text=True,timeout=10)
 (scratch/(name+'.cli.txt')).write_text(f'exit={r.returncode}\n'+r.stdout+r.stderr);print(name,r.returncode,r.stderr[-300:])
old=scratch/'old';old.mkdir(exist_ok=True)
for folder in ['src','tests','scenarios','toolbox']:
 shutil.copytree(root/folder,old/folder,dirs_exist_ok=True)
sections=(root/'T4-M1.diff').read_text().split('diff --git ')
patch=''.join('diff --git '+s for s in sections[1:] if s.startswith('a/src/'))
(scratch/'reverse.patch').write_text(patch)
r=subprocess.run(['patch','-R','-p1','-i',str(scratch/'reverse.patch')],cwd=old,capture_output=True,text=True);print('reverse',r.returncode,r.stdout)
r=subprocess.run([str(root/'.venv/bin/python'),'-m','pytest','-q','-p','no:cacheprovider','tests/test_scenario_v2.py','tests/test_cli.py','-k','unrepresentable_initial_orbit'],cwd=old,env={**os.environ,'PYTHONPATH':str(old/'src'),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
(scratch/'old-tests.txt').write_text(r.stdout+r.stderr);print('old tests',r.returncode,r.stdout[-1000:])
