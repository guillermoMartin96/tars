# ruff: noqa
from pathlib import Path
import pytest
import tars.sim.simulator as sm

source = Path(sm.__file__).read_text()
assert "[-mdot, engine.thrust_n / mass]" in source
exec(
    compile(
        source.replace("[-mdot, engine.thrust_n / mass]", "[-2 * mdot, engine.thrust_n / mass]"),
        sm.__file__,
        "exec",
    ),
    sm.__dict__,
)
raise SystemExit(
    pytest.main(["-q", "-p", "no:cacheprovider", "tests/test_simulator_propulsion.py"])
)
