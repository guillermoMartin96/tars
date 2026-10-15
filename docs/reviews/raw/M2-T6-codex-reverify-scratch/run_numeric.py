# ruff: noqa
exec((__import__("pathlib").Path(__file__).parent / "sweep.py").read_text().split("\nevaluate(")[0])
import subprocess, re, tempfile

console = Path.home() / "Applications/GMAT R2026a/bin/GmatConsole"
old_run = subprocess.run
d = refs("numeric_run")
before = {p.name: p.read_bytes() for p in d.iterdir()}
log = (original / f"{name}_console.log").read_text()
lines = (original / f"{name}_report.txt").read_text().splitlines()
fields = lines[400].split()
fields[2] = repr(float(fields[2]) + 0.001)
lines[400] = " ".join(fields)
bad = "\n".join(lines) + "\n"


def fake(args, **kwargs):
    if args[0] == "git":
        return subprocess.CompletedProcess(args, 0, "1" * 40 + "\n", "")
    if str(args[0]) != str(console):
        return old_run(args, **kwargs)
    script = Path(args[2]).read_text()
    report = Path(re.search(r"GMAT S.Filename = '([^']+)';", script)[1])
    report.write_text(bad)
    return subprocess.CompletedProcess(args, 0, log, "")


with (
    patch.object(gmat_m2, "reference_dir", return_value=d),
    patch.object(subprocess, "run", side_effect=fake),
    patch.object(tempfile, "tempdir", str(scratch)),
):
    code = cli.main(
        [
            "run",
            "--missions",
            name,
            "--gmat-console",
            str(console),
            "--gmat-version",
            "R2026a",
            "--replace-reason",
            "numeric rejection probe",
        ]
    )
print(
    "valid_provenance_bad_numerics",
    code,
    "directory_unchanged",
    before == {p.name: p.read_bytes() for p in d.iterdir()},
)
