# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
from pathlib import Path
from tars.validation import gmat_m2 as g
import shutil
base=Path('review_scratch/history-rewrite')
shutil.copytree(g.reference_dir(),base,dirs_exist_ok=True)
path=g.approved_manifest_path(base)
data=json.loads(path.read_text())
before=len(data['history'])
del data['history'][:9]
previous=None
for record in data['history']:
    record['previous_record_sha256']=previous
    previous=g.record_digest(record)
path.write_text(json.dumps(data))
for name in g.GMAT_MISSIONS:
    rejected, check=cli._evaluate(name,base=base)
    print('history',before,'->',len(data['history']),name,'rejected',rejected,'passed',check and check.passed,flush=True)
    assert not rejected and check.passed
