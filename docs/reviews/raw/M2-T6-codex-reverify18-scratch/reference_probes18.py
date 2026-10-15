# ruff: noqa
import runpy

for name in ["overflow_velocity_probe", "anchor_phase", "anchor_acceptance"]:
    print("RUN", name, flush=True)
    try:
        runpy.run_path("review_scratch/" + name + ".py", run_name="__main__")
    except SystemExit as e:
        assert e.code == 0
