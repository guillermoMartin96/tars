# ruff: noqa
import importlib.util,inspect,math,pytest
from pathlib import Path
from unittest.mock import patch
from tars.validation import m2,gmat_m2
s=importlib.util.spec_from_file_location('tg','tests/test_gmat_m2.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
def run(label,fn,args=(),expect_fail=False):
 mp=pytest.MonkeyPatch()
 try:
  fn(mp,*args) if 'monkeypatch' in inspect.signature(fn).parameters else fn(*args)
  failed=False
 except AssertionError: failed=True
 finally: mp.undo()
 print(label,'test failed' if failed else 'test passed',flush=True)
 assert failed==expect_fail,label
for b in ('normal','infinite'): run('Simpson '+b,t.test_infinite_simpson_allowance_cannot_hide_an_error,(b,))
run('Simpson integrated',t.test_infinite_simpson_allowance_fails_the_integrated_mission)
run('node integrated',t.test_poisoned_node_oracle_fails_the_integrated_mission)
with patch.object(m2,'excess_over',lambda err,allowance:max(err-allowance,0.0)):
 run('disabled excess unit',t.test_excess_over_rejects_non_finite_inputs,expect_fail=True)
 run('disabled excess standalone',t.test_infinite_simpson_allowance_cannot_hide_an_error,('infinite',),True)
 run('disabled excess integrated',t.test_infinite_simpson_allowance_fails_the_integrated_mission,expect_fail=True)
def disable(mod,fn):
 src=inspect.getsource(getattr(mod,fn));assert 'if not (np.all(np.isfinite(rr)) and np.all(np.isfinite(vv))):' in src
 ns=dict(mod.__dict__);exec(src.replace('if not (np.all(np.isfinite(rr)) and np.all(np.isfinite(vv))):','if False:'),ns);return ns[fn]
for mod,fn in ((m2,'orbit_checks'),(gmat_m2,'_node_crossings')):
 with patch.object(mod,fn,disable(mod,fn)):
  run('disabled '+fn,t.test_poisoned_node_oracle_fails_the_integrated_mission,expect_fail=True)
orig=Path.read_text
for expr in ['np.maximum.reduce(errors)','np.minimum.reduce(errors)','np.fmax.reduce(errors)','np.fmin.reduce(errors)','np.maximum(a,b)','np.minimum(a,b)','np.fmax.accumulate(errors)','np.fmin.reduceat(errors,[0])','np.maximum.outer(a,b)','np.minimum.at(errors,[0],0)']:
 def read(p,*a,**k):
  src=orig(p,*a,**k)
  return src+'\ndef unsafe(np,errors,a,b):\n    e = '+expr+'\n' if str(p).endswith('src/tars/validation/m2.py') else src
 with patch.object(Path,'read_text',read):run('actual guard '+expr,t.test_every_max_min_call_in_the_validators_is_reviewed,expect_fail=True)
