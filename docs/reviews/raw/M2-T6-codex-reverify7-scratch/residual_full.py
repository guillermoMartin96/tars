# ruff: noqa
import importlib.util,math,dataclasses
from unittest.mock import patch
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import load_scoped_thresholds
from tars.sim.runner import run_scenario
s=importlib.util.spec_from_file_location('p','toolbox/validators/m2_proof.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
m=next(x for x in MISSIONS if x.name=='m2_burn_to_depletion');res=1e-10
cache={}
def mutated_run(scenario,*a,**k):
 key=scenario.model_dump_json()
 if key not in cache:
  clean=run_scenario(scenario,*a,**k);veh=m2.vehicle(scenario);starts={e.burn_id:e for e in clean.events if e.type=='BurnStarted'}
  ev=[e.model_copy(update={'propellant_kg':res,'total_mass_kg':veh.dry_mass_kg+res,'propellant_used_kg':starts[e.burn_id].propellant_kg-res}) if e.type=='BurnEnded' and e.end_cause=='propellant_depleted' else e.model_copy(update={'residual_propellant_kg':res}) if e.type=='PropellantDepleted' else e for e in clean.events]
  cache[key]=dataclasses.replace(clean,events=ev)
 return cache[key]
for bound in (None,math.inf,-math.inf,math.nan):
 with patch.object(p,'run_scenario',side_effect=mutated_run):
  def evaluate():
   gates=p.Gates(load_scoped_thresholds(missions=frozenset(x.name for x in MISSIONS)))
   checks,_=p.mission_checks(m,gates,quick=False)
   print('residual',res,'bound',bound,'checks',len(checks),'failed',[(c.validator,c.failures) for c in checks if not c.passed],'missing',gates.missing,'nonfinite',gates.non_finite_report_only,flush=True)
  if bound is None:evaluate()
  else:
   with patch.object(m2,'_ulp',return_value=bound):evaluate()
