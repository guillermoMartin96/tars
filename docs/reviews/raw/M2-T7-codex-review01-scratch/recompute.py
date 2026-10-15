import json,gzip,hashlib,itertools,math
from pathlib import Path
import numpy as np
bs={p.name:json.loads((p/'bundle.json').read_text()) for p in Path('t7-bundles').iterdir()}
ps={k:json.loads((Path('t7-bundles')/k/'m2_proof.json').read_text()) for k in bs}
rows={}; bad=[]
for lab,b in bs.items():
 for f,h in b['outputs_sha256'].items():
  p=Path('t7-bundles')/lab/f
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:bad.append((lab,f))
 for f,h in b['inputs_sha256'].items():
  if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h:bad.append(('input',lab,f))
 for r in ps[lab]['results']:
  if r['threshold_status']=='approved':continue
  for m,l in r['thresholds'].items():
   key=(r['validator'].split('[')[0],m,l)
   rows.setdefault(key,{}).setdefault(r['validator'],{})[lab]=r['metrics'][m]
print('digest mismatches',bad)
a=json.loads(Path('proof/records/evidence/M2-T7/analysis.json').read_text())
for row in a['gated']:
 vals=rows[(row['group'],row['metric'],row['provisional_limit'])]
 worst=max(v for d in vals.values() for v in d.values()); spread=max(max(d.values())-min(d.values()) for d in vals.values())
 assert worst==row['worst'] and spread==row['max_cross_platform_spread'] and len(vals)==row['checks']
 print(row['group'],row['metric'], 'worst',f'{worst:.9g}','spread',f'{spread:.9g}','margin',row['margin_ratio'])
print('analysis equality',a==json.loads(Path('review_scratch/analysis/analysis.json').read_text()))
for k,p in ps.items():
 for r in p['results']:
  if r['validator'].startswith('o6_impulsive_limit'):print('O6',k,r)
