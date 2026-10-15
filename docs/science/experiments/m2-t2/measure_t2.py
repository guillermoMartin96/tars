"""T2 measurement: the production simulator on the DR-0010 reference burn (VAL-0012).

Research evidence, not a Proof gate. Compares the simulator (RK4, exact step
splitting) with the independent DOP853 reference committed in VAL-0008 and with
analytic oracles.

Usage: uv run --no-sync python docs/science/experiments/m2-t2/measure_t2.py
"""

from __future__ import annotations

import json
import math
from itertools import pairwise
from pathlib import Path

import numpy as np

from tars.astro import kepler
from tars.astro.elements import rv_to_elements
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import EngineSpec, SpacecraftSpec, TankSpec, rocket_equation_delta_v
from tars.sim.runner import initial_state
from tars.sim.scenario import load_scenario
from tars.sim.simulator import Simulator

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PLANNING = REPO / "docs" / "science" / "experiments" / "m2-planning" / "burn_results.json"

ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
DRY, PROP = 1000.0, 300.0
T_IGN, T_BURN, T_END = 600.0, 77.3, 53_700.0


def run(dt: float) -> dict[str, object]:
    scenario = load_scenario(REPO / "scenarios" / "m1_leo_250km.json")
    mu = scenario.constants.mu
    r0, v0 = initial_state(scenario)
    spacecraft = SpacecraftSpec(DRY, ENGINE, TankSpec(PROP))
    sim = Simulator(r0, v0, PointMassGravity(mu), RK4(), dt, spacecraft=spacecraft)
    plan = sim.schedule_burn("prograde", ignition_t_s=T_IGN, duration_s=T_BURN)
    transitions = {}
    while sim.t < T_END:
        sim.step()
        for event in sim.engine_transitions:
            transitions[event.kind] = event
    s, p = sim.snapshot(), sim.propulsion_snapshot()
    cutoff = transitions["cutoff"]
    # Post-burn coast vs the exact Kepler propagation of the simulator's own cutoff state.
    r_k, v_k = kepler.propagate(cutoff.r, cutoff.v, T_END - cutoff.t, mu)
    m0 = DRY + PROP
    sensed = p.delta_v_sensed_mps - transitions["ignition"].delta_v_sensed_mps
    rocket = rocket_equation_delta_v(ENGINE.exhaust_velocity_mps, m0, m0 - plan.propellant_used_kg)
    return {
        "dt": dt,
        "final_r": s.r.tolist(),
        "final_v": s.v.tolist(),
        "propellant_used_minus_analytic_kg": (PROP - p.propellant_kg) - plan.propellant_used_kg,
        "sensed_dv_minus_rocket_equation_rel": (sensed - rocket) / rocket,
        "coast_vs_kepler_from_cutoff_pos_m": float(np.linalg.norm(s.r - r_k)),
        "coast_vs_kepler_from_cutoff_vel_mps": float(np.linalg.norm(s.v - v_k)),
        "sma_after_burn_m": rv_to_elements(cutoff.r, cutoff.v, mu).a,
    }


def main() -> None:
    planning = json.loads(PLANNING.read_text())
    ref = np.array(planning["ref_final_state"])
    rows = []
    for dt in (20.0, 10.0, 5.0, 2.5):
        row = run(dt)
        row["vs_dop853_pos_m"] = float(np.linalg.norm(np.array(row["final_r"]) - ref[:3]))
        row["vs_dop853_vel_mps"] = float(np.linalg.norm(np.array(row["final_v"]) - ref[3:6]))
        rows.append(row)
    orders = [math.log2(a["vs_dop853_pos_m"] / b["vs_dop853_pos_m"]) for a, b in pairwise(rows)]
    planning_dt10 = next(r for r in planning["rk4_split_track"] if r["dt"] == 10.0)
    out = {
        "reference": "VAL-0008 DOP853 (rtol 1e-13), docs/science/experiments/m2-planning",
        "rows": rows,
        "observed_orders_pos": orders,
        "planning_script_dt10_vs_dop853_pos_m": planning_dt10["pos_err_m"],
        "sma_after_burn_planning_m": planning["sma_after_m"],
    }
    (HERE / "results.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: v for k, v in r.items() if k not in ("final_r", "final_v")})


if __name__ == "__main__":
    main()
