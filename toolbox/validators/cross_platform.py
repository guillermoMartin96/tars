"""Cross-platform agreement check against the committed golden M1 final state.

Usage:
    uv run python toolbox/validators/cross_platform.py           # check (exit 1 on failure)
    uv run python toolbox/validators/cross_platform.py --write   # regenerate golden (reference
                                                                 # platform only; review the diff)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tars.sim.runner import run_scenario
from tars.sim.scenario import load_scenario
from tars.validation.cross_platform import GOLDEN_M1, compare_to_golden, golden_record, load_golden
from tars.validation.thresholds import REPO_ROOT, Check, load_thresholds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--scenario", type=Path, default=REPO_ROOT / "scenarios" / "m1_leo_250km.json"
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    result = run_scenario(load_scenario(args.scenario), record_samples=False)
    if args.write:
        GOLDEN_M1.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN_M1.write_text(json.dumps(golden_record(result), indent=2) + "\n")
        print(f"wrote {GOLDEN_M1.relative_to(REPO_ROOT)}")
        return 0

    golden = load_golden()
    thresholds = load_thresholds()
    check = Check(
        "cross_platform",
        compare_to_golden(result, golden),
        thresholds.for_validator("cross_platform"),
        thresholds.status,
        f"golden platform: {golden['platform']}",
    )
    print(json.dumps(check.to_event().model_dump(mode="json")))
    return 0 if check.passed else 1


if __name__ == "__main__":
    sys.exit(main())
