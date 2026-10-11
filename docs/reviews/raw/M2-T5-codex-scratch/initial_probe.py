import importlib.util
import numpy as np
from tars.sim import runner
spec = importlib.util.spec_from_file_location('proof_cli', 'toolbox/validators/m2_proof.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
original = runner.initial_state
rotation = np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
def wrong_initial(scenario):
    r,v = original(scenario)
    return rotation @ r, rotation @ v
runner.initial_state = wrong_initial
code = p.main(['--out', 'review_scratch/initial_mutant_full.json'])
print('INITIAL_ROTATION_MUTANT_RESULT', code)
