# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])


def older(d):
    p = d / "APPROVED_DIGESTS.json"
    man = json.loads(p.read_text())
    h = next(h for h in man["history"] if h["mission"] == name)
    h.update(
        generated_utc="1900-01-01",
        tars_git_revision="0" * 40,
        reason=None,
        report_sha256="not-a-digest",
    )
    p.write_text(json.dumps(man))


evaluate("older_history_corruption", older)


def unknown(d):
    p = d / "APPROVED_DIGESTS.json"
    man = json.loads(p.read_text())
    man["history"].append(
        dict(
            mission="invented",
            generated_utc=None,
            tars_git_revision=None,
            reason=None,
            report_sha256=None,
        )
    )
    p.write_text(json.dumps(man))


evaluate("unknown_history_record", unknown)


# Deleting history: retain only the current records.
def erase(d):
    p = d / "APPROVED_DIGESTS.json"
    man = json.loads(p.read_text())
    man["history"] = [
        next(h for h in reversed(man["history"]) if h["mission"] == n)
        for n in gmat_m2.GMAT_MISSIONS
    ]
    p.write_text(json.dumps(man))


evaluate("erase_replacement_history", erase)
# Audit numeric gates: remove one mandatory threshold at a time.
run = run_scenario(mission.build())
audit = m2.audit_run(mission.build(), mission.expected, run)
print("audit_groups", list(audit.metrics))
from tars.validation.thresholds import load_scoped_thresholds

orig = cli.load_scoped_thresholds
for group, metrics in audit.metrics.items():
    lim = orig(missions=frozenset(cli.BY_NAME)).for_validator(group, name)
    for key in lim:

        def missing(*a, group=group, key=key, **k):
            result = orig(*a, **k)
            for scope in result.limits.get(group, {}).values():
                scope.pop(key, None)
            return result

        with patch.object(cli, "load_scoped_thresholds", missing):
            rejected, check = cli._evaluate(name)
            assert rejected or not check.passed, (group, key)
print("all_audit_threshold_deletions_rejected")
