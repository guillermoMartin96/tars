# ruff: noqa
import dataclasses, json
from tars.validation import gmat_m2 as g, m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import load_scoped_thresholds
from tars.sim.runner import run_scenario

for mission in MISSIONS:
    if mission.name not in g.GMAT_MISSIONS:
        continue
    s = mission.build()
    p = m2.predict_burns(s, mission.expected)
    arcs = g.plan_arcs(s, p, s.stop.duration_s)
    rows = g.parse_stream(g.reference_files(mission.name)["report"].read_text())
    labelled, _ = g.label_rows(rows, arcs)
    ref = m2.dop853_reference(s, *m2.expected_initial_state(s), p, sorted(labelled))
    ev = run_scenario(s).events
    lim = load_scoped_thresholds(missions=frozenset(x.name for x in MISSIONS)).for_validator(
        "o9_gmat", mission.name
    )
    for tag, mut in [
        ("swap_same_arc_rows", lambda r: r[:30] + [r[31], r[30]] + r[32:]),
        ("duplicate_row_preserve_count", lambda r: r[:30] + [r[31]] + r[31:]),
        (
            "wrong_arc_boundary",
            lambda r: [
                dataclasses.replace(x, arc=x.arc + 1) if i == 30 else x for i, x in enumerate(r)
            ],
        ),
        (
            "epoch_step_shift",
            lambda r: [
                dataclasses.replace(x, a1mjd=x.a1mjd + 1 / 86400) if i == 30 else x
                for i, x in enumerate(r)
            ],
        ),
        (
            "burn_mass_offset",
            lambda r: [
                dataclasses.replace(x, mass_kg=x.mass_kg + 1e-6)
                if x.arc == next(a.index for a in arcs if a.direction)
                else x
                for x in r
            ],
        ),
        (
            "velocity_offset",
            lambda r: [
                dataclasses.replace(x, v=x.v + 1e-5) if i == 30 else x for i, x in enumerate(r)
            ],
        ),
    ]:
        lab, v = g.label_rows(mut(rows), arcs)
        metrics = (
            {}
            if v
            else {
                **g.alignment_metrics(lab, arcs, p, s.constants.mu, m2.vehicle(s).mass_flow_kgps),
                **g.o9_metrics(s, p, ev, lab, ref),
            }
        )
        fail = [k for k, l in lim.items() if metrics.get(k, float("inf")) > l]
        print(
            json.dumps({"mission": mission.name, "probe": tag, "violations": v, "failures": fail}),
            flush=True,
        )
        assert v or fail
