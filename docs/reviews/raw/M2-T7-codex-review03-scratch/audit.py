import json,hashlib,subprocess,math,itertools,copy,struct
from pathlib import Path
from tars.validation import m2_cross_platform as x
from tars.validation.approved_digests import APPROVED_THRESHOLD_SHA256
p=Path('proof/records/evidence/M2-T7/cross-platform')
m=json.loads((p/'MANIFEST.json').read_text()); rs={n:json.loads((p/n).read_text()) for n in m['records']}
old=json.loads(Path('review_scratch/old_m2.json').read_text()); new=json.loads(Path('proof/thresholds/m2.json').read_text())
assert all(new['limits'][k]==v for k,v in old['limits'].items())
assert hashlib.sha256(Path('proof/thresholds/m2.json').read_bytes()).hexdigest()==APPROVED_THRESHOLD_SHA256['m2']
print('Old limits identical; pin valid')
for n,d in m['sha256'].items(): assert hashlib.sha256((p/n).read_bytes()).hexdigest()==d
assert (p/'reference-host.json').read_bytes()==Path('proof/references/m2_final_states.json').read_bytes()
bundle=json.loads(Path('t7-reference-host/bundle.json').read_text())['mission_finals']
a=rs['reference-host.json']['missions']; b=rs['macos-15-intel.json']['missions']
assert a==b
for name,v in a.items():
 for k in ('r','v'):
  assert all(struct.pack('d',u)==struct.pack('d',w) for u,w in zip(v[k],bundle[name][k]))
 assert v['events_sha256']==bundle[name]['events_sha256']
print('Manifest valid; golden byte-identical; reference/Intel missions identical; T7 floats bit-identical')
worst={name:[0.,0.] for name in a}
for (na,ra),(nb,rb) in itertools.combinations(rs.items(),2):
 vals=[]
 for name in a:
  dr,dv=(math.sqrt(sum((u-v)**2 for u,v in zip(ra['missions'][name][k],rb['missions'][name][k]))) for k in ('r','v'))
  vals.append((dr,dv)); worst[name]=[max(worst[name][0],dr),max(worst[name][1],dv)]
 print('PAIR',na,nb,max(t[0] for t in vals),max(t[1] for t in vals))
print('MISSIONS',worst)
for n,r in rs.items(): print('PROVENANCE',n,r['revision'],r['tree_clean'],r['platform'],r['ci'])
ci=[(n,copy.deepcopy(r)) for n,r in rs.items() if r['ci']]
ci[0][1]['ci']['runner_os']='Windows'
ci[0][1]['ci']['github_run_attempt']='999'
ci[0][1]['sha256']=x.record_digest(ci[0][1])
z=x.gate(ci,revision=m['revision'],run_id=m['ci_run_id'])
print('Contradictory OS and mixed attempts accepted:',not z.violations,z.metrics)
for f in ('proof/thresholds/m1.json','proof/references/m1_final_state.json','toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz','toolbox/references/gmat/m2/APPROVED_DIGESTS.json'):
 assert subprocess.check_output(['git','show',f'77995b9:{f}'])==Path(f).read_bytes()
print('M1 thresholds/golden, snapshot, GMAT manifest unchanged')
