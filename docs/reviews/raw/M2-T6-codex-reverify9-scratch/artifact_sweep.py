# ruff: noqa
import importlib.util
import json
import shutil
from pathlib import Path
from unittest.mock import patch
from tars.validation import gmat_m2 as g
from tars.validation.thresholds import (
    load_thresholds,
    load_scoped_thresholds,
    M1_THRESHOLDS,
    M2_THRESHOLDS,
)
from tars.sim.runner import run_scenario

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
for name in g.GMAT_MISSIONS:
    run = run_scenario(cli.BY_NAME[name].build())
    for key in ("script", "report", "console", "metadata", "manifest", "history"):
        dst = Path("review_scratch") / ("artifact-" + name + "-" + key)
        shutil.copytree(g.reference_dir(), dst, dirs_exist_ok=True)
        target = (
            g.approved_manifest_path(dst)
            if key in ("manifest", "history")
            else g.reference_files(name, dst)[key]
        )
        if key in ("manifest", "history", "metadata"):
            data = json.loads(target.read_text())
            if key == "manifest":
                data["references"][name]["report_sha256"] = "0" * 64
            elif key == "history":
                data["history"] = data["history"][-3:]
                previous = None
                for h in data["history"]:
                    h["previous_record_sha256"] = previous
                    previous = g.record_digest(h)
            else:
                data["gmat_console_sha256"] = "0" * 64
            target.write_text(json.dumps(data))
        else:
            target.write_text(target.read_text() + "\nTAMPERED\n")
        with (
            patch.object(g, "reference_dir", return_value=dst),
            patch.object(cli, "run_scenario", return_value=run),
        ):
            try:
                reasons, check = cli._evaluate(name)
                passed = not reasons and check is not None and check.passed
                print(name, key, "accepted", passed, "reasons", reasons, flush=True)
                assert not passed
            except (ValueError, KeyError) as e:
                print(name, key, "rejected exception", str(e), flush=True)
for path, loader in ((M1_THRESHOLDS, load_thresholds), (M2_THRESHOLDS, load_scoped_thresholds)):
    for edit in ("inflate", "delete", "nan"):
        raw = json.loads(path.read_text())
        raw["limits"] = {} if edit == "delete" else raw["limits"]

        def mutate(obj):
            for k, v in obj.items():
                if isinstance(v, dict):
                    mutate(v)
                elif v is not None:
                    obj[k] = 1e100 if edit == "inflate" else float("nan")

        if edit != "delete":
            mutate(raw["limits"])
        out = Path("review_scratch") / (path.stem + "-" + edit + ".json")
        out.write_text(json.dumps(raw))
        try:
            loader(out)
        except ValueError as e:
            print(path.name, edit, "rejected", str(e), flush=True)
        else:
            raise AssertionError((path, edit))
