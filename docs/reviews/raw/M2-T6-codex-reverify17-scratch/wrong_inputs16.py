# ruff: noqa
import copy, importlib.util, contextlib, io
from pathlib import Path
from tars.validation import reference_snapshot as s
from tars.validation import m2

sp = importlib.util.spec_from_file_location("tool_input", "toolbox/scripts/reference_snapshot.py")
t = importlib.util.module_from_spec(sp)
sp.loader.exec_module(t)
b = s.load_approved()


def put(rec, p, arr):
    import numpy as np

    a = np.asarray(arr)
    rec["parts"][p] = {"shape": list(a.shape), "values": [float(v) for v in a.ravel()]}


for tag in ["o5_wrong_flight", "o3_wrong_duration"]:
    d = copy.deepcopy(b)
    if tag == "o5_wrong_flight":
        k = next(
            k
            for k, r in d["records"].items()
            if "/o5.kepler#" in k and r["parts"]["flight_s"]["values"]
        )
        rec = d["records"][k]
        sc = t._scenarios()[k.split("/")[0]][0]
        flight = t._arr(rec, "flight_s") * 10
        r, v = t.kepler_uv(
            t._arr(rec, "seed_r_m"), t._arr(rec, "seed_v_mps"), flight, sc.constants.mu
        )
        put(rec, "flight_s", flight)
        put(rec, "r_m", r)
        put(rec, "v_mps", v)
        print("mutation", tag, k, "10x flight times and recomputed r/v", flush=True)
    else:
        import numpy as np

        veh = m2.vehicle(t._scenarios()["m2_prograde_burn"][0])
        duration = 100.0
        dv, disp = t._free_space_closed_form(veh, duration)
        for k, rec in d["records"].items():
            if not k.startswith("o3_free_space/"):
                continue
            if "/o3.closed_form#" in k:
                put(rec, "dv_mps", [dv])
                put(rec, "disp_m", [disp])
                continue
            sign = 1 if "/prograde/" in k else -1
            x0, v0 = t._arr(rec, "start_r_m"), t._arr(rec, "start_v_mps")
            u = v0 / np.linalg.norm(v0)
            put(rec, "duration_s", [duration])
            put(rec, "r_m", x0 + v0 * duration + sign * disp * u)
            put(rec, "v_mps", v0 + sign * dv * u)
            put(rec, "propellant_kg", [veh.propellant_kg - veh.mass_flow_kgps * duration])
        print("mutation", tag, "all O3 expectations changed from 77.3 to 100 s", flush=True)
    p = Path("review_scratch") / f"{tag}.json.gz"
    s.write_json(p, d)
    with contextlib.redirect_stdout(io.StringIO()):
        problems = t.verify_baseline(d)
    print(tag, "problems", problems, flush=True)
    assert not problems
