import json,gzip,itertools,math
from pathlib import Path
import numpy as np
base=json.load(gzip.open('t7-bundles/reference-host/record.json.gz'))['records']
for p in Path('t7-bundles').iterdir():
 proof=json.loads((p/'m2_proof.json').read_text());rec=json.load(gzip.open(p/'record.json.gz'))['records'];maximum=(0,'')
 for k,r in rec.items():
  if r['seed']!='ref':continue
  for name,part in r['parts'].items():
   x=np.array(part['values']).reshape(part['shape']);y=np.array(base[k]['parts'][name]['values']).reshape(part['shape'])
   if name.endswith('_m') and x.size and x.ndim and x.shape[-1]==3:
    d=float(np.max(np.linalg.norm(x-y,axis=-1)))
    if d>maximum[0]:maximum=(d,k)
 print(p.name,'raw position norm',maximum)
 for m,info in proof['missions'].items():
  rows=info.get('impulsive_family')
  if not rows:continue
  worst=max(abs(math.log2(a['sma_finite_minus_impulsive_m']/b['sma_finite_minus_impulsive_m']))-2 for a,b in zip(rows,rows[1:])) if False else max(abs(math.log2(a['sma_finite_minus_impulsive_m']/b['sma_finite_minus_impulsive_m'])-2) for a,b in zip(rows,rows[1:]))
  for delta in (1e-5,2e-8):
   shift=max(abs(math.log2((a['sma_finite_minus_impulsive_m']-ea)/(b['sma_finite_minus_impulsive_m']-eb))-math.log2(a['sma_finite_minus_impulsive_m']/b['sma_finite_minus_impulsive_m'])) for a,b in zip(rows,rows[1:]) for ea,eb in itertools.product((-delta,delta),repeat=2))
   print(m,delta,'worst',worst,'shift',shift,'sum',worst+shift)
