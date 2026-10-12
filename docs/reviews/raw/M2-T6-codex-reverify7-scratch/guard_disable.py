# ruff: noqa
exec(open('review_scratch/round7.py').read().split("for b in ('normal'")[0])
src=inspect.getsource(t._reducer_calls)
src=src.replace('if name in _UFUNC_METHODS and isinstance(fn, ast.Attribute):','if False:')
ns=dict(t.__dict__);exec(src,ns)
with patch.object(t,'_reducer_calls',ns['_reducer_calls']):
 for snippet in ('e = np.maximum.reduce(errors)','e = np.fmax.reduce(errors)','e = np.minimum.reduce(errors)','e = np.fmin.reduce(errors)'):
  run('disabled ufunc guard '+snippet,t.test_the_guard_detects_common_unsafe_forms,(snippet,),True)
