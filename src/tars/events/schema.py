"""Event schemas, versioned and serialized as JSON Lines (ADR-0005)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

SCHEMA_VERSION = 1

Vec3 = Annotated[list[float], Field(min_length=3, max_length=3)]


class _EventBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

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
    """Emitted at the first tick at/after an ascending-node crossing."""

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


Event = Annotated[
    SimulationStarted | StateSampled | OrbitCompleted | SimulationCompleted | ValidationResult,
    Field(discriminator="type"),
]
_EVENT_ADAPTER: TypeAdapter[Event] = TypeAdapter(Event)


def parse_event(line: str) -> Event:
    return _EVENT_ADAPTER.validate_json(line)


def to_jsonl(events: Iterable[BaseModel]) -> str:
    return "".join(event.model_dump_json() + "\n" for event in events)


def read_jsonl(text: str) -> list[Event]:
    return [parse_event(line) for line in text.splitlines() if line.strip()]
