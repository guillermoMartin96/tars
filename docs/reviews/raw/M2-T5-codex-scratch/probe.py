import importlib.util
import json
from pathlib import Path
from tars.sim import runner
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS, ACCEPT
spec = importlib.util.spec_from_file_location('proof_cli', 'toolbox/validators/m2_proof.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
original = runner.run_scenario
counts = {'corrupted_powered_samples': 0, 'removed_depletion_events': 0}
def wrong_log(*args, **kwargs):
    run = original(*args, **kwargs)
    intervals = [(e.event_t_s, next((x.event_t_s for x in run.events if x.type == 'BurnEnded' and x.burn_id == e.burn_id), run.final.t)) for e in run.events if e.type == 'BurnStarted']
    out = []
    for e in run.events:
        if e.type == 'PropellantDepleted':
            counts['removed_depletion_events'] += 1
            continue
        if e.type == 'StateSampled' and e.t == 630.0 and any(a < e.t < b for a,b in intervals):
            e = e.model_copy(update={'r': [2*x for x in e.r]})
            counts['corrupted_powered_samples'] += 1
        out.append(e)
    run.events = out
    return run
runner.run_scenario = wrong_log
p.run_scenario = wrong_log
code = p.main(['--out', 'review_scratch/mutant_full.json'])
print('MUTANT_RESULT', code, counts)
runner.run_scenario = original
base = MISSIONS[0].build()
variant = m2.boundary_variant(base, m2.BOUNDARY_CASES[0])
run = original(variant)
longer = original(m2.boundary_variant(base, m2.BOUNDARY_CASES[0], stop_s=base.stop.duration_s))
run.events[-1] = run.events[-1].model_copy(update={'r': [1e9, 2e9, 3e9], 'v': [1e6, 2e6, 3e6]})
print('BOUNDARY_COMPLETION_MUTANT', m2.boundary_violations(variant, run, longer, (ACCEPT,)))
