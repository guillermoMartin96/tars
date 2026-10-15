import json,copy
from pathlib import Path
from tars.validation import m2_cross_platform as xp
p=Path('proof/records/evidence/M2-T7/cross-platform')
a=json.loads((p/'ubuntu-latest.json').read_text())
b=json.loads((p/'macos-latest.json').read_text())
fake=copy.deepcopy(a)
fake['platform']['id']='macos-x86_64'
fake['platform']['system']='Darwin'
fake['sha256']=xp.record_digest(fake)
out=Path('review_scratch/wrong-platform');out.mkdir(exist_ok=True)
for name,r in [('linux',a),('arm',b),('labelled-macos-intel',fake)]: (out/f'{name}.json').write_text(json.dumps(r))
r=xp.gate([('linux',a),('arm',b),('labelled-macos-intel',fake)],revision=a['revision'],run_id=a['ci']['github_run_id'])
print('violations:',r.violations,'metrics:',r.metrics)
