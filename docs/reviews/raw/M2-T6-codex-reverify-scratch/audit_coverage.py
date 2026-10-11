# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])
run = run_scenario(mission.build())
for kind, field, val, predicate in [
    (
        "PropulsionSampled",
        "thrust_acceleration_mps2",
        (1.0, 1.0, 1.0),
        lambda e: e.engine_state == "burning",
    ),
    ("PropulsionSampled", "delta_v_sensed_mps", 1000.0, lambda e: e.engine_state == "burning"),
]:
    ev = list(run.events)
    idx = next(i for i, e in enumerate(ev) if e.type == kind and predicate(e))
    ev[idx] = ev[idx].model_copy(update={field: val})
    mut = dataclasses.replace(run, events=ev)
    with patch.object(cli, "run_scenario", return_value=mut):
        rejected, check = cli._evaluate(name)
        audit = m2.audit_run(mission.build(), mission.expected, mut)
        print(
            "corrupt_" + field,
            json.dumps(
                {
                    "rejected": rejected,
                    "passed": check.passed if check else None,
                    "accounting": audit.metrics.get("accounting"),
                }
            ),
        )
# Explicit coverage on DR-0018 boundary variants, using synthetic row labels only:
for stop in [590.0, 600.0, 650.0, 670.0, 680.0]:
    s = mission.build()
    s = s.model_copy(update={"stop": s.stop.model_copy(update={"duration_s": stop})})
    r = run_scenario(s)
    pred = m2.predict_burns(s, mission.expected)
    arcs = gmat_m2.plan_arcs(s, pred, stop)
    labels = {t: None for i, a in enumerate(arcs) for t in a.row_times(i == 0)}
    print("coverage_stop", stop, gmat_m2.coverage_problems(s, pred, r.events, labels, stop))
