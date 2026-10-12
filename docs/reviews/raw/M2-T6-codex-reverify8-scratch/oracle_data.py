import importlib.util
import json
from unittest.mock import patch
import numpy as np
from scipy.integrate import solve_ivp
from tars.astro import kepler

spec = importlib.util.spec_from_file_location('cli', 'toolbox/scripts/gmat_m2.py')
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)

def poisoned_solver(*args, **kwargs):
    result = solve_ivp(*args, **kwargs)
    original = result.sol
    def dense(t):
        y = original(t).copy()
        y[3:] = np.nan
        return y
    result.sol = dense
    return result

with patch('scipy.integrate.solve_ivp', poisoned_solver):
    rejected, check = cli._evaluate('m2_prograde_burn')
    print('dense velocity/propellant NaN:', rejected, check and check.passed, flush=True)

original = kepler.propagate
import inspect

def poisoned_kepler(*args, **kwargs):
    r, v = original(*args, **kwargs)
    if inspect.currentframe().f_back.f_code.co_name == 'alignment_metrics':
        v = np.full_like(v, np.nan)
    return r, v

with patch.object(kepler, 'propagate', poisoned_kepler):
    rejected, check = cli._evaluate('m2_prograde_burn')
    print('coast Kepler velocity NaN:', rejected, check and check.passed, flush=True)
