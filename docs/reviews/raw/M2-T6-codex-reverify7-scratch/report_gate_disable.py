# ruff: noqa
import importlib.util,inspect
from unittest.mock import patch
s=importlib.util.spec_from_file_location('t','tests/test_gmat_m2.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
p=t._proof_module();ns=dict(p.__dict__)
source=inspect.getsource(p.main);line='    checks.append(_exact("report_only_metrics_finite", gates.non_finite_report_only))\n';assert line in source
exec(source.replace(line,''),ns);p.main=ns['main']
with patch.object(t,'_proof_module',return_value=p):
 t.test_report_only_metrics_must_be_finite()
 print('report-only new test still PASSES with terminal Proof check removed')
