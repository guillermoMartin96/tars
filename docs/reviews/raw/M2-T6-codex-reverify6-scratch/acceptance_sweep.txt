# ruff: noqa
import importlib.util, json, shutil, dataclasses, copy
from pathlib import Path
from unittest.mock import patch
from tars.validation import gmat_m2 as g, m2
from tars.validation.thresholds import load_scoped_thresholds
from tars.sim.runner import run_scenario

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
name = "m2_prograde_burn"
mission = c.BY_NAME[name]
run = run_scenario(mission.build())
# Use a cached clean simulation to keep acceptance probes focused on validators.
with patch.object(c, "run_scenario", return_value=run):
    for tag, edit, rechain in [
        (
            "old-values",
            lambda h: h[0].update(
                generated_utc="1900-01-01",
                tars_git_revision="0" * 40,
                reason=None,
                report_sha256="bad",
            ),
            True,
        ),
        ("unknown", lambda h: h.append({**h[-1], "mission": "invented"}), True),
        ("delete", lambda h: h.__delitem__(slice(0, 3)), False),
        ("reorder", lambda h: h.__setitem__(slice(0, 2), [h[1], h[0]]), True),
        ("chain-edit", lambda h: h[0].update(reason="edited"), False),
        ("rewrite-limit", lambda h: h.__delitem__(slice(0, 9)), True),
    ]:
        d = Path("review_scratch") / ("probe-" + tag)
        shutil.copytree(g.reference_dir(), d, dirs_exist_ok=True)
        f = d / "APPROVED_DIGESTS.json"
        man = json.loads(f.read_text())
        edit(man["history"])
        if rechain:
            prev = None
            for h in man["history"]:
                h["previous_record_sha256"] = prev
                prev = g.record_digest(h)
        f.write_text(json.dumps(man))
        rejected, check = c._evaluate(name, base=d)
        passed = not rejected and check.passed
        print(tag, json.dumps({"rejected": rejected, "passed": passed}), flush=True)
        assert passed == (tag == "rewrite-limit")
    audit = m2.audit_run(mission.build(), mission.expected, run)
    groups = {
        group: list(
            load_scoped_thresholds(missions=frozenset(c.BY_NAME)).for_validator(group, name)
        )
        for group in [*audit.metrics, "o9_gmat"]
    }
    orig = c.load_scoped_thresholds
    for group, keys in groups.items():
        for key in keys:

            def missing(*a, **k):
                th = orig(*a, **k)
                for scope in th.limits[group].values():
                    scope.pop(key, None)
                return th

            with patch.object(c, "load_scoped_thresholds", missing):
                rejected, check = c._evaluate(name)
                assert rejected or not check.passed, (group, key)
    print("mandatory threshold deletions rejected:", sum(map(len, groups.values())), flush=True)
# Invalid event numbers via model_copy exercise audit/schema fail-closed path.
for kind, field, val in [
    ("StateSampled", "r", (float("nan"),) * 3),
    ("PropulsionSampled", "total_mass_kg", float("nan")),
    ("PropulsionSampled", "thrust_acceleration_mps2", (float("nan"),) * 3),
    ("PropulsionSampled", "delta_v_sensed_mps", 1000.0),
]:
    ev = list(run.events)
    i = (
        next(
            i
            for i, e in enumerate(ev)
            if e.type == kind and e.tick == 64
            if kind == "PropulsionSampled"
        )
        if kind == "PropulsionSampled"
        else next(i for i, e in enumerate(ev) if e.type == kind and e.tick > 0)
    )
    ev[i] = ev[i].model_copy(update={field: val})
    mut = dataclasses.replace(run, events=ev)
    with patch.object(c, "run_scenario", return_value=mut):
        rejected, check = c._evaluate(name)
        print(
            "event " + field,
            json.dumps({"rejected": rejected, "passed": check.passed if check else None}),
            flush=True,
        )
        assert rejected or not check.passed
