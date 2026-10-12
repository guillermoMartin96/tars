# ruff: noqa
import importlib.util, math
from unittest.mock import patch
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import Check,load_scoped_thresholds
from tars.sim.runner import run_scenario
s=importlib.util.spec_from_file_location('p','toolbox/validators/m2_proof.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
m=next(x for x in MISSIONS if any(e.end_cause=='propellant_depleted' for e in m2.predict_burns(x.build(),x.expected)))
s=m.build();run=run_scenario(s);pred=m2.predict_burns(s,m.expected)
events=[e.model_copy(update={'propellant_kg':1e-8}) if e.type=='BurnEnded' and e.end_cause=='propellant_depleted' else e for e in run.events]
limits=load_scoped_thresholds(missions=frozenset(x.name for x in MISSIONS)).for_validator('o1_mass_law',m.name)
for bad in (None,math.inf,-math.inf,math.nan):
 def evaluate():
  o1,_,_=m2.mass_and_rocket_metrics(s,events,pred);c=Check('o1',o1,limits,'provisional');print(m.name,'residual +1e-8, ulp',bad,o1,'passes',c.passed,flush=True)
 if bad is None:evaluate()
 else:
  with patch.object(m2,'_ulp',return_value=bad):evaluate()
for bad in (math.inf,-math.inf,math.nan):
 with patch.object(m2,'_ulp',return_value=bad):
  gates=p.Gates(load_scoped_thresholds(missions=frozenset(x.name for x in MISSIONS)))
  checks,_=p.mission_checks(m,gates,quick=False)
  print('FULL clean run with invalid bound',bad,'checks',len(checks),'failed',[c.validator for c in checks if not c.passed],'report nonfinite',gates.non_finite_report_only,flush=True)
