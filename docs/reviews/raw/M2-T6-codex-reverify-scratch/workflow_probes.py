# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])
import subprocess, re, tempfile

# Crash at manifest publication after otherwise validated writes, with unchanged
# script/report/console bytes (the permitted byte-identical reproduction case).
d = refs("atomic_crash")
before = {p.name: p.read_bytes() for p in d.iterdir()}
console = Path.home() / "Applications/GMAT R2026a/bin/GmatConsole"
old_run = subprocess.run
old_replace = Path.replace
log = (original / f"{name}_console.log").read_text()


def fake_run(args, **kwargs):
    if args[0] == "git":
        return subprocess.CompletedProcess(args, 0, "1" * 40 + "\n", "")
    if str(args[0]) != str(console):
        return old_run(args, **kwargs)
    script = Path(args[2]).read_text()
    report = Path(re.search(r"GMAT S.Filename = '([^']+)';", script)[1])
    shutil.copyfile(original / f"{name}_report.txt", report)
    return subprocess.CompletedProcess(args, 0, log, "")


def crash_replace(self, target):
    if self.name == "APPROVED_DIGESTS.json.new":
        raise OSError("injected crash before commit marker")
    return old_replace(self, target)


with (
    patch.object(gmat_m2, "reference_dir", return_value=d),
    patch.object(subprocess, "run", side_effect=fake_run),
    patch.object(Path, "replace", crash_replace),
):
    try:
        cli.main(
            [
                "run",
                "--missions",
                name,
                "--gmat-console",
                str(console),
                "--gmat-version",
                "R2026a",
                "--replace-reason",
                "review injected interruption",
            ]
        )
    except OSError as e:
        print("atomic_crash", str(e))
rejected, check = cli._evaluate(name, base=d)
print(
    "atomic_crash changed",
    [p.name for p in d.iterdir() if p.name in before and p.read_bytes() != before[p.name]],
    "old_manifest",
    before["APPROVED_DIGESTS.json"] == (d / "APPROVED_DIGESTS.json").read_bytes(),
    "accepted",
    not rejected and check.passed,
)
# Reproduction test trusts the pathname: a report copier satisfies it.
fake = scratch / "GmatConsole"
fake.write_text(
    "#!/usr/bin/env python3\nimport sys,re,shutil\nfrom pathlib import Path\ns=Path(sys.argv[2]).read_text()\nname=re.search(\"scenario '([^']+)'\",s)[1]\nout=re.search(\"GMAT S.Filename = '([^']+)';\",s)[1]\nshutil.copyfile("
    + repr(str(original))
    + '+"/"+name+"_report.txt",out)\n'
)
fake.chmod(0o755)
spec = importlib.util.spec_from_file_location("test", root / "tests/test_gmat_m2.py")
test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test)
test.GMAT_CONSOLE = fake
for n in gmat_m2.GMAT_MISSIONS:
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        test.test_gmat_reproduces_the_committed_report(Path(tmp), n)
    print("unapproved_report_copier_reproduction", n, "PASS")
