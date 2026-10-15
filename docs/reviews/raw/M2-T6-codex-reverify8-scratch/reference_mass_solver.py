# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])

def poisoned_mass_solver(*args, **kwargs):
    result = solve_ivp(*args, **kwargs)
    # Alter only the terminal solver output: no later segment is seeded from it.
    if args[1][1] == 53700.0:
        result.y[6, -1] = -1.0
    return result

with patch('scipy.integrate.solve_ivp', poisoned_mass_solver):
    rejected, check = cli._evaluate('m2_prograde_burn')
    print('DOP853 terminal propellant=-1 kg:', rejected, check and check.passed, flush=True)
    assert not rejected and check.passed
    spec = importlib.util.spec_from_file_location('proof', 'toolbox/validators/m2_proof.py')
    proof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proof)
    code = proof.main(['--out', 'review_scratch/poison_mass_solver.json'])
    report = json.load(open('review_scratch/poison_mass_solver.json'))
    print('POISONED MASS SOLVER PROOF exit', code, 'checks', len(report['results']), 'passed', report['passed'])
    assert code == 0 and report['passed'] and len(report['results']) == 213
