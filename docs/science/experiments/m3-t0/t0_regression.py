"""M3 T0: perturbations-disabled regression of the spike model against the M1 baseline.

1. The spike's fixed-step RK4 with every M3 perturbation disabled, from the M1 initial state
   for the M1 golden's 5371 ticks, compared with the committed M1 golden final state
   (`proof/references/m1_final_state.json`; read only). Bitwise equality is expected only on
   the golden's reference host (DR-0006; playbook testing lessons); elsewhere the difference
   is reported against the approved M1 cross-platform bound (m1.json, read only).
2. Identity (DR-0025 Q11): with J2 = 0 and no drag the spike acceleration is bitwise the
   point-mass acceleration at sampled states.

Usage: uv run --no-sync python t0_regression.py <out.json>
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import t0_model as m

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from tars.sim.runner import initial_state  # noqa: E402
from tars.sim.scenario import load_scenario  # noqa: E402


def main() -> None:
    golden = json.loads((REPO / "proof/references/m1_final_state.json").read_text())
    bounds = json.loads((REPO / "proof/thresholds/m1.json").read_text())["limits"]["cross_platform"]
    scenario = load_scenario(REPO / "scenarios/m1_leo_250km.json")
    r0, v0 = (np.array(x, dtype=float) for x in initial_state(scenario))
    y = np.concatenate([r0, v0, [0.0]])
    f = m.rhs(m.Config())
    dt = scenario.dt_s
    for i in range(golden["final_tick"]):
        y = m.rk4_step(f, i * dt, y, dt)
    dr = float(np.linalg.norm(y[:3] - np.array(golden["final_r_m"])))
    dv = float(np.linalg.norm(y[3:6] - np.array(golden["final_v_mps"])))
    host = {
        "machine": platform.machine(),
        "cpu_brand_not_checked": True,
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    identity = []
    for alt, inc in ((250e3, 51.6), (180e3, 97.0), (800e3, 0.0)):
        r, v = m.circular_state(alt, inc)
        a_off = m.acceleration(m.Config(j2=0.0, drag=None), 0.0, r, v, 850.0)
        rn = float(np.linalg.norm(r))
        a_pm = (-m.MU / rn**3) * r
        identity.append(bool(np.array_equal(a_off, a_pm)))
    out = {
        "golden_platform": golden["platform"],
        "this_host": host,
        "ticks": golden["final_tick"],
        "final_position_difference_m": dr,
        "final_velocity_difference_mps": dv,
        "bitwise_equal_to_golden": bool(
            np.array_equal(y[:3], golden["final_r_m"])
            and np.array_equal(y[3:6], golden["final_v_mps"])
        ),
        "m1_cross_platform_bound_m_mps": [
            bounds["final_position_difference_m"],
            bounds["final_velocity_difference_mps"],
        ],
        "within_m1_cross_platform_bound": dr <= bounds["final_position_difference_m"]
        and dv <= bounds["final_velocity_difference_mps"],
        "perturbations_off_acceleration_bitwise_point_mass": identity,
    }
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
