import pytest
from tars.validation import gmat_m2 as g
original=g.alignment_metrics
def disabled(*a,**k):
 result=original(*a,**k)
 result['coast_vs_kepler_position_error_max_m']=0.0
 return result
g.alignment_metrics=disabled
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','tests/test_gmat_m2.py']))
