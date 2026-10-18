"""DR-0028 amendment 6: assertion-removal sweep of dr0028_node_signed_verification.py.

Planning research artifact (not production code, not a Proof gate). A measurement, not a check:
it has no verdict and does not decide anything.

Usage:
    python dr0028_node_signed_assertion_sweep.py <out.json>

Every `failures.append(...)` statement in the verification script is an assertion. For each one
in turn, a copy of the script is made with only that statement replaced by `pass` (located with
the ast module, so the rest of the file is untouched), and the copy is run as a separate
`python -I` process. The sweep records whether that single removal is detected (exit 1 with a
FAIL verdict) or survives (exit 0), or ends the process with an exception. A surviving removal
means no built-in mutant depends on that particular assertion alone: either another assertion of
the same test rejects every designated mutant, or no mutant exercises it.

Exit status 0 when every copy ran and the output was written; it says nothing about how many
removals were detected. Standard library only.
"""

import ast
import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")


def assertion_sites(text):
    """The `failures.append(...)` statements, as (first line, last line, column)."""
    sites = []
    for node in ast.walk(ast.parse(text)):
        if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)):
            continue
        func = node.value.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "append"
            and isinstance(func.value, ast.Name)
            and func.value.id == "failures"
        ):
            sites.append((node.lineno, node.end_lineno, node.col_offset))
    return sorted(sites)


def enclosing_function(tree, line):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.lineno <= line <= node.end_lineno:
            return node.name
    return None


def main(out_path):
    text = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        for first, last, col in assertion_sites(text):
            removed = " " * col + "pass  # assertion removed\n"
            mutated = [*lines[: first - 1], removed, *lines[last:]]
            copy, out = workdir / f"line{first}.py", workdir / f"line{first}.json"
            copy.write_text("".join(mutated), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-I", str(copy), str(out)],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            stderr = proc.stderr.strip()
            if stderr:
                outcome = "exception: " + stderr.splitlines()[-1]
            else:
                verdict = json.loads(out.read_text(encoding="ascii"))["verdict"]
                outcome = "detected" if proc.returncode == 1 and verdict == "FAIL" else "survives"
            results.append(
                {
                    "line": first,
                    "function": enclosing_function(tree, first),
                    "assertion": lines[first - 1].strip(),
                    "exit_code": proc.returncode,
                    "outcome": outcome,
                }
            )
    report = {
        "script": SCRIPT.name,
        "kind": "measurement (no verdict)",
        "assertion_sites": len(results),
        "detected": sum(1 for r in results if r["outcome"] == "detected"),
        "survives": sum(1 for r in results if r["outcome"] == "survives"),
        "exception": sum(1 for r in results if r["outcome"].startswith("exception")),
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
