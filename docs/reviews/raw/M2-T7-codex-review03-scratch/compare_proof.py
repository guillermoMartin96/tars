import json
from pathlib import Path
before=json.loads(Path('m2_proof_before.json').read_text())
after=json.loads(Path('review_scratch/m2.json').read_text())
a={c['validator']:c for c in before['results']};b={c['validator']:c for c in after['results']}
assert len(a)==len(before['results'])==215
assert len(b)==len(after['results'])==228
assert a.keys()<=b.keys()
for n,c in a.items():
 for k in ('thresholds','metrics','passed'):
  assert c[k]==b[n][k],(n,k,c[k],b[n][k])
print('PASS: all 215 earlier checks retain identical metrics, thresholds and verdicts; 13 additions; total 228; overall',after['passed'])
print('Mission reports identical:',before['missions']==after['missions'])
print('Additions:',sorted(b.keys()-a.keys()))
