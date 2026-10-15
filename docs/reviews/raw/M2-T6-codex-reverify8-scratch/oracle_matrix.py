# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
import inspect
original_kepler = kepler.propagate
for bad in (np.nan, np.inf, -np.inf):
    for component in (3, 4, 5, 6):
        def solver(*args, **kwargs):
            result = solve_ivp(*args, **kwargs)
            original = result.sol
            def dense(t):
                y = original(t).copy()
                y[component] = bad
                return y
            result.sol = dense
            return result
        with patch('scipy.integrate.solve_ivp', solver):
            rejected, check = cli._evaluate('m2_prograde_burn')
            print('dense', component, repr(bad), 'accepted', not rejected and check.passed, flush=True)
            assert not rejected and check.passed
    def oracle(*args, **kwargs):
        r, v = original_kepler(*args, **kwargs)
        if inspect.currentframe().f_back.f_code.co_name == 'alignment_metrics':
            v = np.full_like(v, bad)
        return r, v
    with patch.object(kepler, 'propagate', oracle):
        rejected, check = cli._evaluate('m2_prograde_burn')
        print('Kepler coast velocity', repr(bad), 'accepted', not rejected and check.passed, flush=True)
        assert not rejected and check.passed
