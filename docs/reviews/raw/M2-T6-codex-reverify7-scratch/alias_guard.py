# ruff: noqa
import importlib.util,math
from pathlib import Path
from unittest.mock import patch
from tars.validation import m2
s=importlib.util.spec_from_file_location('t','tests/test_gmat_m2.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
p=t._proof_module();orig=Path.read_text
source=orig(Path('toolbox/validators/m2_proof.py')).replace('import math','import math\nfrom numpy import fmax as reducer').replace('m2.worst(x) if k not in dst else m2.worst(dst[k], x)','float(reducer.reduce([dst.get(k, -math.inf), x]))')
def read(path,*a,**k):return source if str(path).endswith('toolbox/validators/m2_proof.py') else orig(path,*a,**k)
with patch.object(Path,'read_text',read):
 t.test_every_max_min_call_in_the_validators_is_reviewed();print('actual allowlist PASSES aliased fmax.reduce merge')
ns=dict(p.__dict__);exec(compile(source,'<aliased unsafe merge>','exec'),ns)
good=m2.Audit({}, {'o4_reference':{'sample_position_error_max_m':0.1}}, {})
bad=m2.Audit({}, {'o4_reference':{'sample_position_error_max_m':math.nan}}, {})
print('original poisoned merge',p._merge_audits([('good',good),('bad',bad)]).metrics)
print('aliased poisoned merge',ns['_merge_audits']([('good',good),('bad',bad)]).metrics)
assert ns['_merge_audits']([('good',good),('bad',bad)]).metrics['o4_reference']['sample_position_error_max_m']==0.1
