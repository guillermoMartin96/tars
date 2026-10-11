# ruff: noqa
import importlib.util, tempfile
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("tests_g", Path("tests/test_gmat_m2.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
with tempfile.TemporaryDirectory(dir="review_scratch") as tmp:
    d = Path(tmp).resolve()
    fake = d / "GmatConsole"
    fake.write_text(
        '#!/bin/sh\necho "*** GMAT Integration test (Console version) successful! ***"\n'
    )
    fake.chmod(0o755)
    with patch.object(t, "GMAT_CONSOLE", fake):
        for name in t.gmat_m2.GMAT_MISSIONS:
            try:
                t.test_gmat_reproduces_the_committed_report(d, name)
            except AssertionError as e:
                print(name, "REJECTED", str(e))
            else:
                raise AssertionError("substituted binary accepted")
