# ruff: noqa
import importlib.util, json
from pathlib import Path
from unittest.mock import patch
from tars.validation import thresholds as t
from tars.validation.m2_missions import MISSIONS

for label, source, loader, group, key in [
    ("M1", t.M1_THRESHOLDS, t.load_thresholds, "kepler_reference", "position_error_max_m"),
    (
        "M2",
        t.M2_THRESHOLDS,
        t.load_scoped_thresholds,
        "o9_gmat",
        "gmat_vs_dop853_position_error_max_m",
    ),
]:
    data = json.loads(source.read_text())
    scope = data["limits"][group] if label == "M1" else data["limits"][group]["all"]
    scope[key] = {}
    path = Path("review_scratch") / f"object-{label}.json"
    path.write_text(json.dumps(data))
    th = loader(
        path, **({"missions": frozenset(m.name for m in MISSIONS)} if label == "M2" else {})
    )
    limits = (
        th.for_validator(group) if label == "M1" else th.for_validator(group, "m2_prograde_burn")
    )
    print(label, "loader accepted", repr(limits[key]), flush=True)
    try:
        t.Check(group, {k: 0.0 for k in limits}, limits, th.status)
    except Exception as e:
        print(label, "downstream", type(e).__name__, str(e), flush=True)
    if label == "M2":
        spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
        c = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(c)
        orig = c.load_scoped_thresholds

        def bad_loader(*a, **k):
            return t.load_scoped_thresholds(path, missions=frozenset(c.BY_NAME))

        with patch.object(c, "load_scoped_thresholds", bad_loader):
            try:
                print("evaluate:", c._evaluate("m2_prograde_burn"))
            except Exception as e:
                print("evaluate raised", type(e).__name__, str(e), flush=True)
