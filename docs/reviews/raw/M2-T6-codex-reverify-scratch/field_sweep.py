# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])
s = mission.build()
pred = m2.predict_burns(s, mission.expected)
script = gmat_m2.m2_script(s, pred, s.stop.duration_s, f"{name}_report.txt")
d = refs("field_sweep")
files = gmat_m2.reference_files(name, d)
meta = json.loads(files["metadata"].read_text())
approved = gmat_m2.load_approved(d)
from tars.validation.thresholds import load_thresholds, load_scoped_thresholds, ScopedThresholds

limits = load_thresholds().for_validator("gmat_reference")
tol = (
    limits["script_initial_position_difference_m"],
    limits["script_initial_velocity_difference_mps"],
)
for key in meta:
    edited = dict(meta)
    edited.pop(key)
    v = gmat_m2.provenance_problems(name, edited, files, s, script, *tol, approved)
    print("metadata_missing", key, "REJECT" if v else "PASS")
# Exhaustive absence/null coverage: share the baseline result and run to isolate limits.
result = gmat_m2.compare_committed(name, s, mission.expected, run_scenario(s).events, *tol)
base = load_scoped_thresholds(missions=frozenset(cli.BY_NAME))
original_limits = base.limits
for key in original_limits["o9_gmat"]["all"]:
    data = json.loads(json.dumps(original_limits))
    data["o9_gmat"]["all"].pop(key)
    with (
        patch.object(cli.gmat_m2, "compare_committed", return_value=result),
        patch.object(
            cli, "load_scoped_thresholds", return_value=ScopedThresholds("provisional", data)
        ),
    ):
        rejected, check = cli._evaluate(name)
        print("threshold_missing", key, "REJECT" if rejected else "PASS")
# Coverage before ignition, at ignition/cutoff, inside a burn, and same-tick submission.
mission = next(m for m in MISSIONS if m.name == "m2_burn_to_depletion")
s = mission.build()
s = s.model_copy(update={"stop": s.stop.model_copy(update={"duration_s": 600.0})})
r = run_scenario(s)
pred = m2.predict_burns(s, mission.expected)
arcs = gmat_m2.plan_arcs(s, pred, 600.0)
labels = {t: None for i, a in enumerate(arcs) for t in a.row_times(i == 0)}
print("same_tick_at_horizon", gmat_m2.coverage_problems(s, pred, r.events, labels, 600.0))
