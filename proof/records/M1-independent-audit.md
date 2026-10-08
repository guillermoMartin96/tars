# Proof Record — Milestone 1 independent-audit remediation

**Result:** PASS under the existing prototype definition of done.

**Proven executable revision:** `e5f5e536a37240d379c6370130f4c03d40ff48f7`, branch
`review/m1-independent-audit`; local verification began 2026-10-08T21:11:26Z from a
clean worktree. Later changes add only records/evidence, README links, and Markdown
whitespace cleanup. The original M1 record and evidence are preserved.

**Scope:** F1–F4 in [the independent-audit follow-up](../../docs/reviews/M1-independent-audit-02.md).
No physical-model, scenario, timestep, integrator, threshold, permission, or approved
decision change. No Critical/High finding remains open; no new Decision Request.

## Executed local checks

Evidence: [`evidence/M1-independent-audit/`](evidence/M1-independent-audit/).
`execution.json` records the exact revision, interpreter, pinned-package verification,
platform, commands, exit codes, and reference hashes. `proof_run.log` contains stdout
and stderr. Python 3.12.15, NumPy 2.5.3, Pydantic 2.13.5, SciPy 1.18.1, pytest 9.1.1,
and Ruff 0.16.10 were already installed and matched `uv.lock`; no setup was executed.

- Lint and format: PASS (89 Python files).
- Full tests: **212 passed in 21.22 s** (118 original cases retained, 94 added cases).
- Non-GMAT Proof: **7/7 PASS** (mission, invariants, Kepler, period, convergence,
  in-process determinism, architecture).
- Committed GMAT comparison: **9/9 approved gates PASS**.
- Cross-process determinism: PASS, both logs have SHA-256
  `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`, unchanged from M1.
- Golden-state comparison: PASS; zero position/velocity differences on local macOS x86_64.
- Mission CLI: success, ten passages, final tick 5371 at 53 710 s; output events parse
  and round-trip in the full test suite. `mission_summary.json` preserves the summary.
- Reference integrity: 896 rows, 12 finite numeric columns each; script and report
  SHA-256 match original metadata. References were read, not regenerated.
- Additional closed-form circular check at all **5371** propagated ticks: PASS using
  the existing Kepler-reference limits. Evidence: `independent_circular.json`.

## Numerical results versus unchanged approved limits

- Energy relative drift: 3.82693e-10 <= 1e-9.
- Angular-momentum relative drift: 1.91347e-10 <= 5e-10.
- Eccentricity-vector drift: 5.85589e-10 <= 1.2e-9.
- SMA drift: 0.00253654 m <= 0.006 m.
- Kepler position/velocity error: 0.298364 m / 0.000349092 m/s <= 0.6 m / 0.0007 m/s.
- Maximum per-orbit/cumulative node timing error: 5.23407e-6 s / 3.84703e-5 s
  <= 1e-5 s / 8e-5 s.
- Fitted order: 4.32893; deviation 0.32893 <= 0.5.
- GMAT-vs-Kepler position/velocity: 7.16326e-6 m / 8.36897e-9 m/s
  <= 1e-4 m / 1e-7 m/s.
- Initial SMA/state differences: 1.86265e-9 m / 0 m <= 1e-6 m / 1e-6 m.
- GMAT period difference: 9.09495e-13 s <= 1e-8 s.
- Committed-script initial position/velocity differences: zero, within DR-0009 bounds.

All-tick circular errors are 0.2983640986 m and 0.0003490919 m/s. This additional
oracle avoids the project universal-variable propagator. It confirms the existing
finite results; it does not add a Proof requirement or approve a new tolerance.

## Newly executed CI evidence

[CI run 37844928252](https://github.com/guillermoMartin96/tars/actions/runs/37844928252)
at the proven executable revision completed successfully. The fetched run metadata
and selected output lines are preserved in `ci_run.json`.

- Linux x86_64 (AMD EPYC): **212 tests passed**; all configured CI steps pass.
  Golden-state differences: 2.88968e-6 m and 3.38663e-9 m/s.
- macOS arm64 (Apple M1): **212 tests passed**; all configured CI steps pass.
  Golden-state differences: 8.76167e-7 m and 1.03610e-9 m/s.
- Both remain below approved bounds of 1e-4 m and 1e-7 m/s. Replay is byte-identical
  within each platform; cross-platform event hashes are allowed to differ.

These are fresh runs of this remediation, observed through GitHub Actions; they are
distinct from the original M1 CI evidence and from locally executed checks.

## Reproduction without setup or historical-evidence replacement

Use an existing Python 3.12 environment matching `uv.lock`. For this host:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/src:$PWD"
PY=/Users/guillermomartin/projects/tars/.venv/bin/python
RUFF=/Users/guillermomartin/projects/tars/.venv/bin/ruff
"$RUFF" check --no-cache .
"$RUFF" format --check --no-cache .
"$PY" -m pytest -q -p no:cacheprovider
"$PY" toolbox/validators/m1_proof.py --out /tmp/tars-m1-remediation-proof.json
"$PY" toolbox/scripts/gmat_m1.py compare
"$PY" toolbox/validators/determinism.py
"$PY" toolbox/validators/cross_platform.py
"$PY" toolbox/scripts/run_mission.py --scenario scenarios/m1_leo_250km.json \
  --out /tmp/tars-m1-remediation-mission
```

Reproduce the additional all-tick reference with the same interpreter/environment:

```python
import math
import numpy as np
from tars.sim.scenario import load_scenario
from tars.sim.runner import initial_state, run_scenario
from tars.sim.simulator import Simulator
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.validation.thresholds import Check, load_thresholds

s = load_scenario("scenarios/m1_leo_250km.json")
run = run_scenario(s)
r0, v0 = initial_state(s)
n = math.sqrt(s.constants.mu / np.linalg.norm(r0) ** 3)
sim = Simulator(r0, v0, PointMassGravity(s.constants.mu), RK4(), s.dt_s)
pe = ve = 0.0
for _ in range(run.final.tick):
    sim.step()
    x = sim.snapshot()
    theta = n * x.t
    r = r0 * math.cos(theta) + (v0 / n) * math.sin(theta)
    v = -n * r0 * math.sin(theta) + v0 * math.cos(theta)
    pe = max(pe, float(np.linalg.norm(x.r - r)))
    ve = max(ve, float(np.linalg.norm(x.v - v)))
th = load_thresholds()
check = Check(
    "kepler_reference",
    {"position_error_max_m": pe, "velocity_error_max_mps": ve},
    th.for_validator("kepler_reference"),
    th.status,
)
assert check.passed
print(pe, ve)
```

## Limitations and evidence boundaries

Fresh GMAT execution, tool-installation verification, and realistic-force generation
were not performed. The original finite GMAT reference remains the external evidence.
J2/drag omission, spherical altitude, equatorial exclusion, and the Tech Lead's
REV-012 epoch-column deferral remain as documented. General starting phases count
node passages, not complete revolutions; changing this behavior is deferred outside
this remediation. F3 is resolved through explicit documentation and behavioral tests.

Original review dispositions and approved records remain intact. The original audit
was independent of the original implementer; remediation was performed by the audit
agent and is not represented as a newly independent peer review. No Milestone 2 work
was undertaken. The PR requires Tech Lead approval and must not be merged by the agent.
