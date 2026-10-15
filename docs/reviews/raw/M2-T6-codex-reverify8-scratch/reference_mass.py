# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
from tars.validation import m2
original_reference = m2.dop853_reference

def poisoned_reference(*args, **kwargs):
    ref = original_reference(*args, **kwargs)
    for y in ref.values():
        y[6] = -1.0
    return ref

with patch.object(m2, 'dop853_reference', poisoned_reference):
    rejected, check = cli._evaluate('m2_prograde_burn')
    print('DOP853 reference propellant=-1 kg at every mark:', rejected, check and check.passed)
    assert not rejected and check.passed
spec = importlib.util.spec_from_file_location('proof', 'toolbox/validators/m2_proof.py')
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
with patch.object(m2, 'dop853_reference', poisoned_reference):
    code = proof.main(['--out', 'review_scratch/poison_reference_mass.json'])
    report = json.load(open('review_scratch/poison_reference_mass.json'))
    print('POISONED MASS PROOF exit', code, 'checks', len(report['results']), 'passed', report['passed'])
    assert code == 0 and report['passed'] and len(report['results']) == 213
