# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
from pathlib import Path
from tars.sim import simulator
from tars.validation.thresholds import M2_THRESHOLDS
source = json.loads(M2_THRESHOLDS.read_text())
for scopes in source['limits'].values():
    for metrics in scopes.values():
        for key, value in metrics.items():
            if value is not None:
                metrics[key] = 1e100
mutated = Path('review_scratch/inflated_m2_thresholds.json')
mutated.write_text(json.dumps(source))
original_read = Path.read_text

def read_threshold_data(path, *args, **kwargs):
    return original_read(mutated if path == M2_THRESHOLDS else path, *args, **kwargs)

original_thrust = simulator.thrust_acceleration
with patch.object(simulator, 'thrust_acceleration', lambda *args: original_thrust(*args) * (1 + 1e-5)):
    rejected, check = cli._evaluate('m2_prograde_burn')
    print('wrong thrust, approved thresholds:', rejected, check and check.passed, flush=True)
    assert rejected or not check.passed
    with patch.object(Path, 'read_text', read_threshold_data):
        rejected, check = cli._evaluate('m2_prograde_burn')
        print('wrong thrust, tampered finite thresholds:', rejected, check and check.passed, flush=True)
        assert not rejected and check.passed
with patch.object(simulator, 'thrust_acceleration', lambda *args: original_thrust(*args) * (1 + 1e-5)), patch.object(Path, 'read_text', read_threshold_data):
    spec = importlib.util.spec_from_file_location('proof', 'toolbox/validators/m2_proof.py')
    proof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proof)
    code = proof.main(['--out', 'review_scratch/poison_thresholds.json'])
    report = json.load(open('review_scratch/poison_thresholds.json'))
    print('POISONED THRESHOLD PROOF exit', code, 'checks', len(report['results']), 'passed', report['passed'])
