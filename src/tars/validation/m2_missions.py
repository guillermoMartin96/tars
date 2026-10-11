"""Milestone 2 reference missions and their declared expected outcomes (T5).

The expected receipt for every timeline entry is written down here by hand, from the
approved rejection rules and precedence (DR-0014, contract
docs/contracts/m2-commands-and-events.md). It is never derived from a simulator run,
so a validator comparing it with the event log is an independent check of
P7 ("rejected with the correct reason").

Two missions are *derived variants* of ``m2_invalid_commands`` (same timeline):
- ``empty_tank``: the spacecraft carries 0 kg of propellant. ``no_propellant`` is
  only reachable with an empty tank: after a burn to depletion the tank keeps the
  DR-0017 D1a residual (at most mdot * 2 ulp(cutoff)), so it is not empty.
- ``no_propulsion``: no spacecraft block. ``no_propulsion_configured`` precedes every
  command-level check (DR-0014 amendment, 2026-10-11).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from tars.sim.scenario import ScenarioV2, load_scenario
from tars.validation.thresholds import REPO_ROOT

SCENARIOS = REPO_ROOT / "scenarios"


@dataclass(frozen=True)
class Expected:
    """Expected receipt of one timeline entry."""

    status: Literal["accepted", "rejected"]
    reason: str | None = None


ACCEPT = Expected("accepted")


def reject(reason: str) -> Expected:
    return Expected("rejected", reason)


@dataclass(frozen=True)
class Mission:
    """A reference mission: scenario plus hand-declared expectations.

    Attributes:
        name: Mission label used in reports.
        build: Returns the scenario (loaded from ``scenarios/`` or derived).
        expected: Expected receipt per timeline entry, in timeline order.
        physics: Run the trajectory oracles O4, O5, O7, O8 (missions with burns).
        impulsive_limit: Run the O6 impulsive-limit family on this mission's burn.
        control_of: For a mission with rejected commands, check that a control run
            with only the accepted entries is physically bit-identical.
    """

    name: str
    build: Callable[[], ScenarioV2]
    expected: tuple[Expected, ...]
    physics: bool = True
    impulsive_limit: bool = False
    control_of: bool = False


def _load(name: str) -> Callable[[], ScenarioV2]:
    def build() -> ScenarioV2:
        scenario = load_scenario(SCENARIOS / f"{name}.json")
        assert isinstance(scenario, ScenarioV2)
        return scenario

    return build


def derive(name: str, change: Callable[[dict[str, Any]], None]) -> Callable[[], ScenarioV2]:
    """A variant of a committed scenario, edited as raw JSON and validated again."""

    def build() -> ScenarioV2:
        raw = json.loads((SCENARIOS / f"{name}.json").read_text())
        change(raw)
        return ScenarioV2.model_validate_json(json.dumps(raw))

    return build


def _empty_tank(raw: dict[str, Any]) -> None:
    raw["name"] += "_empty_tank"
    raw["spacecraft"]["propellant_kg"] = 0.0


def _no_propulsion(raw: dict[str, Any]) -> None:
    raw["name"] += "_no_propulsion"
    del raw["spacecraft"]


# Timeline of m2_invalid_commands, in order (see the scenario file):
#  0 inv-schema-001        direction "radial"                 schema_invalid
#  1 inv-schema-002        extra field "throttle"             schema_invalid
#  2 inv-burn-A            prograde 1200 s, 30 s              accepted burn#000001
#  3 inv-burn-A (again)    same ID                            duplicate_command_id
#  4 inv-retry-001         duration 0                         non_positive_duration
#  5 inv-overlap-001       ignition 1210 s inside burn A      overlaps_scheduled_burn
#  6 inv-greedy-001        5000 s burn, policy reject         insufficient_propellant
#  7 inv-unschedulable-001 ignition 1e9 s, duration 1e-9 s    burn_unschedulable
#  8 inv-adjacent-001      ignition at A's cutoff, 1230 s     accepted burn#000002
#  9 inv-retry-001 (t=60)  corrected duration 20 s            accepted burn#000003
# 10 inv-past-001 (t=600)  ignition 300 s                     ignition_in_past
# 11 inv-busy-001 (t=1220) ignition 1225 s while A burns      engine_busy
_INVALID = (
    reject("schema_invalid"),
    reject("schema_invalid"),
    ACCEPT,
    reject("duplicate_command_id"),
    reject("non_positive_duration"),
    reject("overlaps_scheduled_burn"),
    reject("insufficient_propellant"),
    reject("burn_unschedulable"),
    ACCEPT,
    ACCEPT,
    reject("ignition_in_past"),
    reject("engine_busy"),
)
# Empty tank: nothing is accepted, so the repeated ID is not a duplicate. Duration and
# chronology precede the propellant checks; overlap and busy cannot occur.
_EMPTY_TANK = (
    reject("schema_invalid"),
    reject("schema_invalid"),
    reject("no_propellant"),
    reject("no_propellant"),
    reject("non_positive_duration"),
    reject("no_propellant"),
    reject("no_propellant"),
    reject("no_propellant"),
    reject("no_propellant"),
    reject("no_propellant"),
    reject("ignition_in_past"),
    reject("no_propellant"),
)
# No spacecraft: schema first, then no_propulsion_configured for every other entry.
_NO_PROPULSION = (
    reject("schema_invalid"),
    reject("schema_invalid"),
    *(reject("no_propulsion_configured"),) * 10,
)

MISSIONS: tuple[Mission, ...] = (
    Mission("m2_prograde_burn", _load("m2_prograde_burn"), (ACCEPT,), impulsive_limit=True),
    Mission("m2_retrograde_burn", _load("m2_retrograde_burn"), (ACCEPT,), impulsive_limit=True),
    # The residual after depletion (DR-0017 D1a) is not an empty tank: a reject-policy
    # burn needs more than it and a burn_to_depletion burn of the residual lasts
    # ~7e-14 s, below the clock resolution at t = 1800 s (cutoff not representable).
    Mission(
        "m2_burn_to_depletion",
        _load("m2_burn_to_depletion"),
        (ACCEPT, reject("insufficient_propellant"), reject("burn_unschedulable")),
        control_of=True,
    ),
    Mission("m2_invalid_commands", _load("m2_invalid_commands"), _INVALID, control_of=True),
    Mission(
        "m2_invalid_commands_empty_tank",
        derive("m2_invalid_commands", _empty_tank),
        _EMPTY_TANK,
        physics=False,
        control_of=True,
    ),
    Mission(
        "m2_invalid_commands_no_propulsion",
        derive("m2_invalid_commands", _no_propulsion),
        _NO_PROPULSION,
        physics=False,
        control_of=True,
    ),
)
