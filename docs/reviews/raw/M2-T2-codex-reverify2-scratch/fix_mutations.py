# ruff: noqa
import sys
from pathlib import Path
import pytest
import tars.sim.propulsion as p
s=Path(p.__file__).read_text()
if sys.argv[1]=='cutoff':
 old='    while represented > depletion_s:'; new='    while False:'
else:
 old='got {_describe(value)}';new='got {value!r}'
assert old in s
exec(compile(s.replace(old,new),p.__file__,'exec'),p.__dict__)
# Reload simulator imports to use mutated class objects.
import importlib, tars.sim.simulator as sm
importlib.reload(sm)
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','tests/test_simulator_propulsion.py','tests/test_propulsion.py']))
