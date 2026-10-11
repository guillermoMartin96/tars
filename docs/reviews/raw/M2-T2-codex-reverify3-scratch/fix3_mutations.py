# ruff: noqa
import sys, importlib
from pathlib import Path
import pytest
import tars.sim.propulsion as p
import tars.sim.simulator as sm

mode = sys.argv[1]
module = sm if mode == "clamp" else p
s = Path(module.__file__).read_text()
replacements = {
    "clamp": ("max(float(y[_PROP]), 0.0)", "float(y[_PROP])"),
    "policy": ("unknown policy {_describe(policy)}", "unknown policy {policy!r}"),
    "residual": (
        "    used = min(mdot * burn, propellant_kg)\n",
        "    if cause is BurnEndCause.COMPLETED:\n        used = min(mdot * burn, propellant_kg)\n",
    ),
}
a, b = replacements[mode]
assert a in s
exec(compile(s.replace(a, b), module.__file__, "exec"), module.__dict__)
if module is p:
    importlib.reload(sm)
raise SystemExit(
    pytest.main(
        [
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/test_propulsion.py",
            "tests/test_simulator_propulsion.py",
        ]
    )
)
