# ruff: noqa
import importlib.util,math
from unittest.mock import patch
from tars.validation import m2
from tars.validation.thresholds import load_scoped_thresholds
s=importlib.util.spec_from_file_location('t','tests/test_gmat_m2.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
s=importlib.util.spec_from_file_location('c','toolbox/scripts/gmat_m2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
p=t._proof_module();original=m2.audit_run
mission=c.BY_NAME['m2_prograde_burn'];clean=c.run_scenario(mission.build());audit=original(mission.build(),mission.expected,clean)
for key in ('sensed_delta_v_rel_error_max','final_propellant_kg','sample_delta_v_rel_error_max'):
 for bad in (math.nan,math.inf,-math.inf):
  def poisoned(*a,**k):
   import copy
   out=copy.deepcopy(audit)
   for metrics in out.metrics.values():
    if key in metrics:metrics[key]=bad
   return out
  with patch.object(m2,'audit_run',poisoned),patch.object(c,'run_scenario',return_value=clean):
   rejected,check=c._evaluate(mission.name)
   gates=p.Gates(load_scoped_thresholds(missions=frozenset(c.BY_NAME)))
   p._audit_checks(gates,mission.name,mission.name,poisoned())
   print(key,bad,'standalone rejects',rejected,'O9 pass',check and check.passed,'Proof records',gates.non_finite_report_only,flush=True)
   assert not rejected and check.passed and gates.non_finite_report_only
