import json,itertools,numpy as np
from pathlib import Path
b={p.name:json.loads((p/'bundle.json').read_text()) for p in Path('t7-bundles').iterdir()}; out=[]
for a,c in itertools.combinations(b,2):
 for m,f in b[a]['mission_finals'].items():
  g=b[c]['mission_finals'][m];out.append((np.linalg.norm(np.array(f['r'])-g['r']),np.linalg.norm(np.array(f['v'])-g['v']),a,c,m))
print('pairwise',max(out)); print('velocity',max(out,key=lambda t:t[1]))
