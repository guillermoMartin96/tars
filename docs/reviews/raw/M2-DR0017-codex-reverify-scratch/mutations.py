# ruff: noqa
import os, subprocess
from pathlib import Path

s = Path("src/tars/sim/propulsion.py").read_text()
ss = Path("src/tars/sim/simulator.py").read_text()
changes = {
    "zero_error": ("return error if not math.isnan(error) else math.inf", "return 0.0"),
    "initial_mass": (
        "dry_mass_kg + max(propellant_kg - burned - slack, 0.0)",
        "dry_mass_kg + propellant_kg",
    ),
    "wrong_end_mass_min": (
        "longer = max(intended_s, executed_s)",
        "longer = min(intended_s, executed_s)",
    ),
    "naive_log": ("math.log1p(x)", "math.log(1.0 + x)"),
    "no_slack": ("slack = 2.0 * (math.ulp(propellant_kg) + math.ulp(burned))", "slack = 0.0"),
    "old_numerator": (
        "(engine.thrust_n / end_mass) * dt / c",
        "engine.mass_flow_kgps * dt / end_mass",
    ),
    "command_on_depletion": ("intended = burn  #", "intended = duration_s  #"),
    "no_step_down": ("while represented > depletion_s:", "while False:"),
    "discard_residual": (
        "used = min(mdot * burn, propellant_kg)",
        "used = propellant_kg if cause is BurnEndCause.PROPELLANT_DEPLETED else min(mdot * burn, propellant_kg)",
    ),
    "budget_plus1pct": (
        "TIMING_DELTA_V_BUDGET_MPS = 1.0e-7",
        "TIMING_DELTA_V_BUDGET_MPS = 1.01e-7",
    ),
    "budget_minus1pct": (
        "TIMING_DELTA_V_BUDGET_MPS = 1.0e-7",
        "TIMING_DELTA_V_BUDGET_MPS = .99e-7",
    ),
    "compare_plus1pct": (
        "timing_error <= TIMING_DELTA_V_BUDGET_MPS",
        "timing_error <= TIMING_DELTA_V_BUDGET_MPS * 1.01",
    ),
    "compare_minus1pct": (
        "timing_error <= TIMING_DELTA_V_BUDGET_MPS",
        "timing_error <= TIMING_DELTA_V_BUDGET_MPS * .99",
    ),
}
for name in [*changes, "schedule_bypass", "no_event_cause"]:
    changed = s if name not in changes else s.replace(*changes[name])
    simchanged = ss
    if name == "schedule_bypass":
        simchanged = ss.replace("dry_mass_kg=self._spacecraft.dry_mass_kg,", "dry_mass_kg=None,")
    if name == "no_event_cause":
        simchanged = ss.replace(
            'end_cause=burn.plan.end_cause if kind == "cutoff" else None,', "end_cause=None,"
        )
    assert changed != s or simchanged != ss, name
    payload = "import tars.sim.propulsion as p\nexec(" + repr(changed) + ",p.__dict__)\n"
    if simchanged != ss:
        payload += "import tars.sim.simulator as sm\nexec(" + repr(simchanged) + ",sm.__dict__)\n"
    payload += "import pytest\nraise SystemExit(pytest.main(['-q','-p','no:cacheprovider','tests/test_propulsion.py','tests/test_simulator_propulsion.py']))"
    r = subprocess.run(
        [".venv/bin/python", "-c", payload],
        env={**os.environ, "PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    Path("review_scratch/mutant_" + name + ".txt").write_text(r.stdout + r.stderr)
    print(name, r.returncode, r.stdout.splitlines()[-1], flush=True)
