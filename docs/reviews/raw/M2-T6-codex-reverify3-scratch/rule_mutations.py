# ruff: noqa
import inspect, subprocess, sys
from pathlib import Path
import pytest
from tars.validation import gmat_m2 as g
from tars.validation import thresholds as th

source = inspect.getsource(g.history_problems)
variants = {
    "timestamp": ("if stamp.tzinfo is None or stamp.year < 2026:", "if False:", "old-timestamp"),
    "revision": (
        'if not re.fullmatch(r"[0-9a-f]{40}", rev) or set(rev) == {"0"}:',
        "if False:",
        "zero-revision",
    ),
    "reason": (
        'if not isinstance(h["reason"], str) or not h["reason"].strip():',
        "if False:",
        "null-reason",
    ),
    "digest": (
        'if not re.fullmatch(r"[0-9a-f]{64}", str(h["report_sha256"])):',
        "if False:",
        "bad-digest",
    ),
    "mission": ('if h["mission"] not in GMAT_MISSIONS:', "if False:", "unknown-mission"),
    "order": ("if last_time is not None and stamp < last_time:", "if False:", "reordered"),
    "chain-deletion": ('if h["previous_record_sha256"] != previous:', "if False:", "deleted"),
    "chain-edit": ('if h["previous_record_sha256"] != previous:', "if False:", "edited"),
}
if len(sys.argv) == 1:
    for key in [*variants, "limits"]:
        p = subprocess.run([sys.executable, __file__, key], capture_output=True, text=True)
        Path(f"review_scratch/disabled_{key}.log").write_text(p.stdout + p.stderr)
        print(key, "expected test failure:", p.returncode == 1, flush=True)
        assert p.returncode == 1
else:
    key = sys.argv[1]

    class Plugin:
        def pytest_collection_modifyitems(self, items):
            if key == "limits":
                th._require_finite_limits = lambda *a, **k: None
            else:
                old, new, _ = variants[key]
                assert old in source
                ns = dict(g.__dict__)
                exec(source.replace(old, new), ns)
                g.history_problems = ns["history_problems"]

    target = (
        "tests/test_gmat_m2.py::test_threshold_loaders_reject_non_finite_or_negative_limits"
        if key == "limits"
        else f"tests/test_gmat_m2.py::test_every_history_record_is_validated[{variants[key][2]}]"
    )
    sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", target], plugins=[Plugin()]))
