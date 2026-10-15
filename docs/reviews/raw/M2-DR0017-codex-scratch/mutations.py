# ruff: noqa: E501
import os
import subprocess
from pathlib import Path

source = Path("src/tars/sim/propulsion.py").read_text()
simsource = Path("src/tars/sim/simulator.py").read_text()
mutants = {
    "zero_error": source.replace(
        "return engine.exhaust_velocity_mps * math.log1p(mdot * abs(intended - executed) / end_mass)",
        "return 0.0",
    ),
    "initial_mass": source.replace(
        "dry_mass_kg + propellant_kg - mdot * max(intended, executed)",
        "dry_mass_kg + propellant_kg",
    ),
    "wrong_end_mass_min": source.replace(
        "mdot * max(intended, executed)", "mdot * min(intended, executed)"
    ),
    "naive_log": source.replace(
        "math.log1p(mdot * abs(intended - executed) / end_mass)",
        "math.log(1.0 + mdot * abs(intended - executed) / end_mass)",
    ),
    "command_on_depletion": source.replace("intended = burn  #", "intended = duration_s  #"),
    "no_step_down": source.replace("while represented > depletion_s:", "while False:"),
    "discard_residual": source.replace(
        "used = min(mdot * burn, propellant_kg)",
        "used = propellant_kg if cause is BurnEndCause.PROPELLANT_DEPLETED else min(mdot * burn, propellant_kg)",
    ),
    "schedule_bypass": source,
    "no_event_cause": source,
}
for name, changed in mutants.items():
    payload = "import tars.sim.propulsion as p\nexec(" + repr(changed) + ", p.__dict__)\n"
    if name in ("schedule_bypass", "no_event_cause"):
        changed_sim = (
            simsource.replace("dry_mass_kg=self._spacecraft.dry_mass_kg,", "dry_mass_kg=None,")
            if name == "schedule_bypass"
            else simsource.replace(
                'end_cause=burn.plan.end_cause if kind == "cutoff" else None,', "end_cause=None,"
            )
        )
        payload += "import tars.sim.simulator as s\nexec(" + repr(changed_sim) + ", s.__dict__)\n"
    payload += "import pytest\nraise SystemExit(pytest.main(['-q','-p','no:cacheprovider','tests/test_propulsion.py','tests/test_simulator_propulsion.py']))\n"
    result = subprocess.run(
        [".venv/bin/python", "-c", payload],
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    Path("review_scratch/" + name + ".txt").write_text(result.stdout + result.stderr)
    print(
        name,
        result.returncode,
        result.stdout.splitlines()[-1] if result.stdout.splitlines() else result.stderr[-200:],
        flush=True,
    )
