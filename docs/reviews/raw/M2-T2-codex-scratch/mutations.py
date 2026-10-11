import sys
from pathlib import Path
import tars.sim.simulator as module
import pytest
source=Path('src/tars/sim/simulator.py').read_text()
mutations={
 'zero_transition_state': ('            r=y[:3],\n            v=y[3:6],','            r=np.zeros(3),\n            v=np.zeros(3),'),
 'double_sensed_dv': ('[-mdot, engine.thrust_n / mass]', '[-mdot, 2 * engine.thrust_n / mass]'),
 'constant_mass': ('mass = spacecraft.dry_mass_kg + float(y[_PROP])','mass = spacecraft.initial_mass_kg'),
 'no_inside_splits': ('if t0 < t < t1','if False'),
}
old,new=mutations[sys.argv[1]]
assert old in source
exec(compile(source.replace(old,new),module.__file__,'exec'),module.__dict__)
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','tests/test_simulator_propulsion.py','tests/test_simulator.py','tests/test_propulsion.py']))
