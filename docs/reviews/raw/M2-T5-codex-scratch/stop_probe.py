import importlib.util
from tars.sim import runner
from tars.sim.scenario import ScenarioV2
spec = importlib.util.spec_from_file_location('proof_cli', 'toolbox/validators/m2_proof.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
original = runner.run_scenario
def premature(scenario, *args, **kwargs):
    if scenario.stop.duration_s is not None and scenario.stop.duration_s > 3000:
        raw = scenario.model_dump(mode='json')
        raw['stop'] = {'duration_s': 3000.0}
        scenario = ScenarioV2.model_validate(raw)
    return original(scenario, *args, **kwargs)
runner.run_scenario = premature
p.run_scenario = premature
print('PREMATURE_STOP_MUTANT_RESULT', p.main(['--out', 'review_scratch/stop_mutant_full.json']))
