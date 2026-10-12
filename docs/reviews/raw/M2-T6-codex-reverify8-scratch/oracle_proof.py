# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
import sys
spec = importlib.util.spec_from_file_location('proof', 'toolbox/validators/m2_proof.py')
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
mode = sys.argv[1]
if mode == 'dense':
    context = patch('scipy.integrate.solve_ivp', poisoned_solver)
else:
    import inspect
    original = kepler.propagate
    def poisoned_kepler(*args, **kwargs):
        r, v = original(*args, **kwargs)
        if inspect.currentframe().f_back.f_code.co_name == 'alignment_metrics':
            v = np.full_like(v, np.nan)
        return r, v
    context = patch.object(kepler, 'propagate', poisoned_kepler)
with context:
    code = proof.main(['--out', f'review_scratch/poison_{mode}.json'])
    report = json.load(open(f'review_scratch/poison_{mode}.json'))
    print('POISONED PROOF', mode, 'exit', code, 'checks', len(report['results']), 'passed', report['passed'])
    assert code == 0 and report['passed'] and len(report['results']) == 213
