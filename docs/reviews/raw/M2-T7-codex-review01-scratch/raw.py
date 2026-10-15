import json,gzip,math,itertools
from pathlib import Path
import numpy as np
root=Path('t7-bundles'); base=json.load(gzip.open(root/'reference-host/record.json.gz'))['records']; bs={p.name:json.loads((p/'bundle.json').read_text()) for p in root.iterdir()}; ana=json.loads(Path('review_scratch/analysis/analysis.json').read_text())
print('sample record',next(iter(base.items())))
for lab,b in bs.items():
 if lab=='reference-host':continue
 rec=json.load(gzip.open(root/lab/'record.json.gz'))['records']; assert rec.keys()==base.keys(); cls={}; labels={}
 for k,r in rec.items():
  g=base[k];assert r['parts'].keys()==g['parts'].keys()
  for name,part in r['parts'].items():
   x=np.array(part['values']);y=np.array(g['parts'][name]['values']);assert x.shape==y.shape
   d=float(np.max(np.abs(x-y))) if x.size else 0
   unit='m' if name.endswith('_m') else 'mps' if name.endswith('_mps') else 's' if name.endswith('_s') else 'kg' if name.endswith('_kg') else '1'
   key=r['seed']+':'+unit;cls[key]=max(cls.get(key,0),d)
   label=k.rpartition('#')[0].rpartition('/')[2]+'.'+name;labels[label]=max(labels.get(label,0),d)
 assert labels==ana['reference_record_drift_vs_reference'][lab]['by_label']
 print(lab,'raw',cls,'O6',{k:v for k,v in labels.items() if 'sma_impulsive' in k})
 for name,f in b['mission_finals'].items():
  g=bs['reference-host']['mission_finals'][name];d=ana['final_state_drift_vs_reference'][lab][name]
  assert float(np.linalg.norm(np.array(f['r'])-g['r']))==d['dr_m'];assert float(np.linalg.norm(np.array(f['v'])-g['v']))==d['dv_mps']
print('maximum final drift',max(x['dr_m'] for d in ana['final_state_drift_vs_reference'].values() for x in d.values()), max(x['dv_mps'] for d in ana['final_state_drift_vs_reference'].values() for x in d.values()))
print('verify maxima',{k:max(d.get(k,0) for d in ana['reference_verify_deviation'].values()) for k in ana['reference_verify_deviation']['reference-host']})
print('O6 records',[(k,r) for k,r in base.items() if 'sma_impulsive_m' in r['parts']][:6])
