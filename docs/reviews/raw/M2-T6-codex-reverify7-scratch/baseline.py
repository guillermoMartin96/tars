# ruff: noqa
import json,subprocess,struct,hashlib
from pathlib import Path
from tars.validation.thresholds import load_thresholds,load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS
repo='/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4'
def old(rev,p):return subprocess.check_output(['git','-C',repo,'show',rev+':'+p])
a=load_thresholds();b=load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
assert a.limits==json.loads(old('a0169e7','proof/thresholds/m1.json'))['limits']
d=dict(b.limits);d.pop('o9_gmat');assert d==json.loads(old('a0169e7','proof/thresholds/m2.json'))['limits']
print('M1/T5 loaded limits unchanged',a.status,b.status)
for k,v in b.limits['o9_gmat']['all'].items():
 if 'position' in k:assert v>=15e-6;print('O9 position floor',k,v)
for p in Path('toolbox/references/gmat/m2').glob('*_report.txt'):
 assert p.read_bytes()==old('1de827e',str(p));print('identical 1de827e',p,hashlib.sha256(p.read_bytes()).hexdigest())
paths=subprocess.check_output(['git','-C',repo,'ls-tree','-r','--name-only','a0169e7'],text=True).splitlines()
selected=[p for p in paths if p.startswith(('src/tars/sim/','src/tars/astro/','scenarios/','proof/references/','toolbox/references/gmat/')) and not p.startswith('toolbox/references/gmat/m2/') and p!='toolbox/references/gmat/README.md']
for p in selected:assert Path(p).read_bytes()==old('a0169e7',p),p
print('Protected baseline files unchanged',len(selected))
tracked=subprocess.check_output(['git','-C',repo,'ls-tree','-r','--name-only','d7d77ae','src','tests','toolbox','scenarios','proof'],text=True).splitlines()
for p in tracked:assert Path(p).read_bytes()==old('d7d77ae',p),p
print('Snapshot protected files identical',len(tracked))
x=json.loads(Path('previous-m2-report.json').read_text());y=json.loads(Path('review_scratch/m2.json').read_text())
xr=x['results'];yr=y['results'];assert len(xr)==212 and len(yr)==213
by={r['validator']:r for r in yr}
count=0
for r in xr:
 assert r==by[r['validator']],r['validator']
 for k,v in r['metrics'].items():assert struct.pack('!d',v)==struct.pack('!d',by[r['validator']]['metrics'][k]);count+=1
print('212 old results identical; metric bits',count,'added',[r['validator'] for r in yr if r['validator'] not in {s['validator'] for s in xr}])
print('top-level differing keys',[k for k in x if x[k]!=y[k]])
