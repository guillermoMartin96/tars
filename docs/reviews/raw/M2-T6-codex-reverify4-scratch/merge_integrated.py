# ruff: noqa
exec(open("review_scratch/hazards.py").read().split("original=scipy")[0])
orig = m2.audit_run
poisoned = []


def audit(s, expected, run):
    result = orig(s, expected, run)
    if s.dt_s == 2.5:
        result.metrics["o4_reference"]["sample_position_error_max_m"] = math.nan
        result.metrics["o5_coast_kepler"]["coast_position_error_max_m"] = math.nan
        poisoned.append(s.name)
    return result


with patch.object(m2, "audit_run", audit):
    gates = p.Gates(load_scoped_thresholds(missions=names))
    checks, _ = p.mission_checks(mission, gates, quick=False)
    print(
        "poisoned",
        poisoned,
        "checks",
        len(checks),
        "failed",
        [x.validator for x in checks if not x.passed],
        "missing",
        gates.missing,
    )
    for x in checks:
        if "/o8_aux" in x.validator and x.validator.startswith(("o4", "o5")):
            print(x.validator, x.metrics, x.passed)
