import importlib.util, json
from tars.validation import gmat_m2 as g
spec=importlib.util.spec_from_file_location('proof','toolbox/validators/m2_proof.py'); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
# Replace each O9 integrity/numerical metric producer in turn by zero-error results.
base=json.load(open('review_scratch/m2.json'))
o9=[x for x in base['results'] if x['validator'].startswith('o9_gmat')]
for result in o9:
 for key in result['thresholds']:
  mutant=dict(result['metrics']); mutant[key]=0.0
  assert all(mutant[k]<=v for k,v in result['thresholds'].items())
print('Zeroing each O9 metric preserves passing baseline (tests must explicitly exercise each metric).')
# Show the integration compares lists rather than independent event coverage.
print('O9 metrics default absent StateSampled and BurnStarted/BurnEnded to zero; one mass observation suffices.')
