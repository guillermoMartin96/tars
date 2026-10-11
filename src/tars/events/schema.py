"""Event schemas, versioned and serialized as JSON Lines (ADR-0005)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

SCHEMA_VERSION = 1

Vec3 = Annotated[list[float], Field(min_length=3, max_length=3)]


class _EventBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    schema_version: Literal[1] = SCHEMA_VERSION
    tick: int = Field(ge=0)
    t: float = Field(description="Elapsed seconds since the scenario epoch")


class SimulationStarted(_EventBase):
    type: Literal["SimulationStarted"] = "SimulationStarted"
    scenario_name: str
    scenario_hash: str
    software_version: str
    epoch: str
    time_scale: str
    seed: int
    earth_constants: dict[str, Any]
    force_models: list[str]
    integrator: str
    dt: float
    r: Vec3
    v: Vec3


class StateSampled(_EventBase):
    type: Literal["StateSampled"] = "StateSampled"
    r: Vec3
    v: Vec3
    altitude_m: float


class OrbitCompleted(_EventBase):
    """Emitted at the first tick at/after an ascending-node crossing.

    Counts node passages; full revolutions coincide only for an ascending-node start.
    """

    type: Literal["OrbitCompleted"] = "OrbitCompleted"
    orbit_number: int = Field(ge=1)
    crossing_t: float = Field(description="Interpolated crossing time [s]")


class SimulationCompleted(_EventBase):
    type: Literal["SimulationCompleted"] = "SimulationCompleted"
    status: Literal["success", "failure"]
    failure_cause: Literal["impact", "escape", "timeout", "non_finite"] | None = None
    orbits_completed: int
    r: Vec3
    v: Vec3
    min_altitude_m: float
    max_altitude_m: float


class ValidationResult(_EventBase):
    type: Literal["ValidationResult"] = "ValidationResult"
    validator: str
    passed: bool
    metrics: dict[str, float]
    thresholds: dict[str, float]
    threshold_status: Literal["provisional", "approved"]
    notes: str = ""


# ------------------------------------------------------------------ M2 propulsion events
# Additive types under schema_version 1 (DR-0014 section 5); M1 event types and their bytes
# are unchanged. M2 events are strict and immutable: vectors are tuples, numbers finite.

Vec3T = tuple[float, float, float]
RejectionCode = Literal[
    "schema_invalid",
    "non_positive_duration",
    "ignition_in_past",
    "overlaps_scheduled_burn",
    "engine_busy",
    "no_propellant",
    "insufficient_propellant",
    "duplicate_command_id",
    "no_propulsion_configured",
    "burn_unschedulable",
]  # DR-0014 section 4 + 2026-10-10 amendment; stable machine-readable vocabulary
EndCause = Literal["completed", "propellant_depleted"]
Direction = Literal["prograde", "retrograde"]
Policy = Literal["reject", "burn_to_depletion"]


class _StrictEventBase(_EventBase):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False, strict=True)


class SpacecraftConfigured(_StrictEventBase):
    """Spacecraft and propulsion configuration in effect (emitted once, after start)."""

    type: Literal["SpacecraftConfigured"] = "SpacecraftConfigured"
    dry_mass_kg: float
    propellant_kg: float
    thrust_n: float
    isp_s: float
    standard_gravity_mps2: float
    exhaust_velocity_mps: float
    mass_flow_kgps: float
    timing_delta_v_budget_mps: float
    direction_laws: tuple[str, ...]


class CommandAccepted(_StrictEventBase):
    """A BurnCommand was accepted. Commanded intent and the resulting plan."""

    type: Literal["CommandAccepted"] = "CommandAccepted"
    command_id: str
    issuer: str
    burn_id: str
    direction: Direction
    on_insufficient_propellant: Policy
    commanded_ignition_t_s: float
    commanded_duration_s: float
    planned_burn_duration_s: float
    planned_cutoff_t_s: float
    planned_propellant_used_kg: float
    planned_end_cause: EndCause
    timing_delta_v_error_mps: float | None


class CommandRejected(_StrictEventBase):
    """A command was rejected with an approved reason code; nothing changed."""

    type: Literal["CommandRejected"] = "CommandRejected"
    command_id: str | None
    issuer: str | None
    reason: RejectionCode
    detail: str


class BurnStarted(_StrictEventBase):
    """Engine ignition at the exact event time ``event_t_s`` (may lie inside a tick)."""

    type: Literal["BurnStarted"] = "BurnStarted"
    command_id: str | None
    burn_id: str
    direction: Direction
    commanded_ignition_t_s: float
    commanded_duration_s: float
    planned_cutoff_t_s: float
    planned_end_cause: EndCause
    event_t_s: float
    r: Vec3T
    v: Vec3T
    thrust_unit_vector: Vec3T
    propellant_kg: float
    total_mass_kg: float


class BurnEnded(_StrictEventBase):
    """Engine cutoff at ``event_t_s``: executed outcome next to commanded intent."""

    type: Literal["BurnEnded"] = "BurnEnded"
    command_id: str | None
    burn_id: str
    direction: Direction
    end_cause: EndCause
    commanded_duration_s: float
    ignition_t_s: float
    event_t_s: float
    executed_duration_s: float
    planned_propellant_used_kg: float
    propellant_used_kg: float
    sensed_delta_v_mps: float
    rocket_equation_delta_v_mps: float
    r: Vec3T
    v: Vec3T
    propellant_kg: float
    total_mass_kg: float


class PropellantDepleted(_StrictEventBase):
    """The tank was emptied by a burn (to within event-time resolution, DR-0017 D1a)."""

    type: Literal["PropellantDepleted"] = "PropellantDepleted"
    command_id: str | None
    burn_id: str
    event_t_s: float
    residual_propellant_kg: float


class PropulsionSampled(_StrictEventBase):
    """Propulsion telemetry sample (truth state)."""

    type: Literal["PropulsionSampled"] = "PropulsionSampled"
    propellant_kg: float
    total_mass_kg: float
    delta_v_sensed_mps: float
    engine_state: Literal["idle", "scheduled", "burning"]
    active_burn_id: str | None
    pending_burn_ids: tuple[str, ...]


Event = Annotated[
    SimulationStarted
    | StateSampled
    | OrbitCompleted
    | SimulationCompleted
    | ValidationResult
    | SpacecraftConfigured
    | CommandAccepted
    | CommandRejected
    | BurnStarted
    | BurnEnded
    | PropellantDepleted
    | PropulsionSampled,
    Field(discriminator="type"),
]
_EVENT_ADAPTER: TypeAdapter[Event] = TypeAdapter(Event)


def parse_event(line: str) -> Event:
    return _EVENT_ADAPTER.validate_json(line)


def to_jsonl(events: Iterable[BaseModel]) -> str:
    return "".join(event.model_dump_json() + "\n" for event in events)


def read_jsonl(text: str) -> list[Event]:
    return [parse_event(line) for line in text.splitlines() if line.strip()]
