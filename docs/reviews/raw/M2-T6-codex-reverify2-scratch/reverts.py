# ruff: noqa
import sys, os, subprocess
from pathlib import Path
import pytest
from tars.validation import gmat_m2 as g

root = Path.cwd()
case = sys.argv[1] if len(sys.argv) > 1 else None
if case is None:
    for case in ["F8-digest", "F8-history", "F9", "F10", "F11", "F12", "F13"]:
        p = subprocess.run([sys.executable, __file__, case], capture_output=True, text=True)
        (root / "review_scratch" / f"{case}.log").write_text(p.stdout + p.stderr)
        print(case, p.returncode, flush=True)
    sys.exit()


class Plugin:
    def pytest_collection_modifyitems(self, session, config, items):
        if case == "F8-history":
            g.history_problems = lambda *a, **k: []
        if case == "F8-digest":
            old = g.provenance_problems

            def unbound(*a, **k):
                return [
                    v
                    for v in old(*a, **k)
                    if v != "reference digests are not in the approved manifest"
                ]

            g.provenance_problems = unbound
        if case == "F10":
            g.is_approved_console = lambda p: True
        if case == "F13":
            old = g.coverage_problems

            def physical(s, p, ev, lab, h):
                errors = old(s, p, ev, lab, h)
                want = {
                    (kind, t)
                    for b in p
                    for kind, t in [("BurnStarted", b.ignition_t_s), ("BurnEnded", b.cutoff_t_s)]
                    if t <= h
                }
                got = {(e.type, e.event_t_s) for e in ev if e.type in ("BurnStarted", "BurnEnded")}
                return errors + (["burn boundaries physical inclusion"] if want != got else [])

            g.coverage_problems = physical
        for module in {i.module for i in items}:
            if case not in ("F9", "F11", "F12"):
                continue
            old = module._cli

            def cli(old=old):
                c = old()
                if case == "F9":

                    def publish(name, staged, sm, manifest):
                        files = g.reference_files(name)
                        for key in ("script", "report", "console", "metadata"):
                            c._atomic_write(files[key], staged[key].read_bytes())
                        c._atomic_write(g.approved_manifest_path(), sm.read_bytes())

                    c._publish = publish
                elif case == "F11":

                    def generate(args):
                        out = Path(args.out)
                        out.mkdir(exist_ok=True)
                        for name in args.missions:
                            (out / f"{name}.script").write_text(
                                c._script(name, f"{name}_report.txt")
                            )
                        return 0

                    c.cmd_generate = generate
                elif case == "F12":
                    from tars.validation import m2

                    oldaudit = m2.audit_run

                    def audit(*a, **k):
                        r = oldaudit(*a, **k)
                        r.metrics.clear()
                        return r

                    c.m2.audit_run = audit
                return c

            module._cli = cli


names = {
    "F8-digest": "test_metadata_and_history_are_bound_to_the_manifest[host]",
    "F8-history": "test_metadata_and_history_are_bound_to_the_manifest[history]",
    "F9": "test_interrupted_publication_never_leaves_an_accepted_mix",
    "F10": "test_unapproved_executables_are_not_authenticated",
    "F11": "test_generate_refuses_symlinks_into_the_references",
    "F12": "test_standalone_evaluation_applies_the_audit_gates",
    "F13": "test_coverage_uses_the_same_tick_report_rule",
}
sys.exit(
    pytest.main(
        ["-q", "-p", "no:cacheprovider", str(root / "tests/test_gmat_m2.py") + "::" + names[case]],
        plugins=[Plugin()],
    )
)
