"""Machine-readable scenario configuration (ADR-0005).

Two schema versions are supported:
- **Version 1 (`Scenario`, M1).** Unchanged, so M1 files, their hashes and their event
  logs are byte-identical.
- **Version 2 (`ScenarioV2`, M2 task T4; DR-0010, DR-0014).** Adds an optional
  `spacecraft`, a `commands` timeline and `stop.duration_s`.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from tars.astro.elements import keplerian_period
from tars.sim.constants import EARTH_CONSTANTS, EarthConstants
from tars.sim.propulsion import EngineSpec, PropulsionSpecError, SpacecraftSpec, TankSpec


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class CircularOrbit(_Strict):
    """Circular initial orbit; altitude is above the spherical datum (SCI-0006)."""

    kind: Literal["circular"] = "circular"
    altitude_m: float = Field(gt=0.0)
    # Equatorial orbits are excluded: orbit counting uses ascending-node crossings,
    # which do not exist for i = 0 or 180 deg (REV-007).
    inclination_deg: float = Field(gt=0.0, lt=180.0)
    raan_deg: float = Field(ge=0.0, lt=360.0)
    arg_latitude_deg: float = Field(ge=0.0, lt=360.0)


class StopCondition(_Strict):
    orbits: int = Field(gt=0, description="Number of ascending-node passages after the start")
    # Guard against non-termination, as a multiple of the nominal Keplerian period.
    max_duration_periods: float = Field(default=1.1, gt=1.0)


class Telemetry(_Strict):
    sample_interval_s: float = Field(gt=0.0)


class Scenario(_Strict):
    schema_version: Literal[1] = 1
    name: str = Field(min_length=1)
    description: str = ""
    epoch: str = Field(description="ISO-8601 epoch label; metadata only in M1 (SCI-0007)")
    time_scale: Literal["TT"] = "TT"
    seed: int = Field(ge=0, description="Recorded for replay; M1 has no stochastic behavior")
    earth_constants: Literal["WGS84"] = "WGS84"
    force_models: tuple[Literal["point_mass_gravity"], ...] = Field(
        default=("point_mass_gravity",), min_length=1
    )
    integrator: Literal["rk4"] = "rk4"
    dt_s: float = Field(gt=0.0)
    initial_orbit: CircularOrbit
    stop: StopCondition
    telemetry: Telemetry

    @model_validator(mode="after")
    def _sampling_on_tick_grid(self) -> Scenario:
        ratio = self.telemetry.sample_interval_s / self.dt_s
        if not math.isfinite(ratio):  # finite inputs can overflow (T4 review F5)
            raise ValueError("telemetry.sample_interval_s / dt_s is not representable")
        if ratio < 1.0 or not math.isclose(ratio, round(ratio), rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("telemetry.sample_interval_s must be a positive multiple of dt_s")
        if len(set(self.force_models)) != len(self.force_models):
            raise ValueError("force_models must not repeat")
        self._nominal_period()  # initial orbit representable (re-verification 2, M1)
        self.timeout_ticks  # noqa: B018 -- validates the orbits-stop guard (review N1)
        return self

    def _nominal_period(self) -> float:
        """Keplerian period of the initial circular orbit.

        Raises ValueError if it is not representable: then neither r^3 in point-mass
        gravity nor the period is, and the run would overflow at its first step.
        """
        c = self.constants
        try:
            period = keplerian_period(c.equatorial_radius + self.initial_orbit.altitude_m, c.mu)
        except OverflowError:
            period = math.inf
        if not math.isfinite(period):
            raise ValueError("initial orbit is not numerically representable (r^3 overflows)")
        return period

    @property
    def timeout_ticks(self) -> int | None:
        """Tick limit of an orbits stop: max_duration_periods x orbits nominal Keplerian
        periods (M1 semantics). None for a duration stop.

        Raises ValueError if the limit is not representable (e.g. a huge guard factor
        or a tiny dt), so such input is invalid rather than a runtime overflow.
        """
        orbits = getattr(self.stop, "orbits", None)
        if orbits is None:
            return None
        try:
            ticks = self.stop.max_duration_periods * orbits * self._nominal_period() / self.dt_s
        except OverflowError:  # e.g. orbits = 10**309 cannot become a float (K2)
            ticks = math.inf
        if not math.isfinite(ticks):
            raise ValueError("the orbits-stop tick limit is not representable")
        return math.ceil(ticks)

    @property
    def sample_every_ticks(self) -> int:
        return round(self.telemetry.sample_interval_s / self.dt_s)

    @property
    def constants(self) -> EarthConstants:
        return EARTH_CONSTANTS[self.earth_constants]

    def canonical_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    def config_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

    def with_dt(self, dt_s: float) -> Scenario:
        """Copy with a different step (used by the convergence study)."""
        return self.model_validate(
            {**self.model_dump(), "dt_s": dt_s, "telemetry": {"sample_interval_s": dt_s}}
        )


# ------------------------------------------------------------------ schema version 2


class _StrictV2(BaseModel):
    """New version-2 blocks are strict: no bool or string coercion into numbers."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False, strict=True)


def _tick_count(value: float, dt_s: float, name: str) -> int:
    """Number of ticks n with n * dt_s == value exactly (time is tick * dt; ADR-0002)."""
    ratio = value / dt_s
    if not math.isfinite(ratio):  # e.g. 1e308 / 1e-10 (T4 review F5)
        raise ValueError(f"{name} = {value!r} / dt_s is not representable")
    n = round(ratio)
    if n * dt_s != value:
        raise ValueError(
            f"{name} = {value!r} is not on the tick grid: no integer n gives n * dt_s == {name}"
        )
    return n


class EngineConfig(_StrictV2):
    thrust_n: float = Field(gt=0.0)
    isp_s: float = Field(gt=0.0)


class SpacecraftConfig(_StrictV2):
    """Spacecraft inputs for the propulsion model (DR-0010: reference-case parameters)."""

    dry_mass_kg: float = Field(gt=0.0)
    propellant_kg: float = Field(ge=0.0)
    engine: EngineConfig

    @model_validator(mode="after")
    def _physically_representable(self) -> SpacecraftConfig:
        try:
            self.to_spec()
        except PropulsionSpecError as err:  # e.g. derived mass flow overflows
            raise ValueError(str(err)) from None
        return self

    def to_spec(self) -> SpacecraftSpec:
        return SpacecraftSpec(
            dry_mass_kg=self.dry_mass_kg,
            engine=EngineSpec(thrust_n=self.engine.thrust_n, isp_s=self.engine.isp_s),
            tank=TankSpec(propellant_kg=self.propellant_kg),
        )


def _standard_json_copy(value: Any, where: str) -> Any:
    """A deep copy of ``value`` made of exact standard-JSON types only (T4 review F2).

    Allowed: ``dict`` with ``str`` keys, ``list``, ``str``, ``int``, finite ``float``,
    ``bool`` and ``None``, exact types only (no subclasses, tuples, sets or bytes).
    Anything else could serialize ambiguously in the canonical form, and so weaken the
    scenario hash, or be changed by copying. A copy of exact JSON types is
    type-preserving, so the runner submits exactly what the scenario holds.
    """
    kind = type(value)
    if kind is float:
        if not math.isfinite(value):
            raise ValueError(f"{where}: non-finite number")
        return value
    if kind in (str, int, bool) or value is None:
        return value
    if kind is list:
        return [_standard_json_copy(item, f"{where}[{i}]") for i, item in enumerate(value)]
    if kind is dict:
        out = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(f"{where}: keys must be strings")
            out[key] = _standard_json_copy(item, f"{where}.{key}")
        return out
    raise ValueError(f"{where}: {kind.__name__} is not a standard JSON value")


class TimelineEntry(_StrictV2):
    """One timeline submission (DR-0014): ``command`` is passed to ``Simulator.submit()``
    verbatim at ``submit_t_s``.

    The payload is deliberately *not* validated as a command here: the simulator is the
    only command validator, so a scenario can contain an invalid command and observe
    its rejection (invalid-command missions). It must only be standard JSON, and it is
    stored as a private deep copy, so the caller cannot change it after validation.
    """

    submit_t_s: float = Field(default=0.0, ge=0.0)
    command: dict[str, Any]

    @field_validator("command", mode="before")
    @classmethod
    def _standard_json(cls, value: Any) -> Any:
        if type(value) is not dict:
            raise ValueError("command must be a JSON object")
        return _standard_json_copy(value, "command")


class StopConditionV2(_StrictV2):
    """Exactly one of ``orbits`` (M1 semantics, timeout guard included) or
    ``duration_s`` (stop at simulation time ``duration_s``; DR-0010 #4)."""

    orbits: int | None = Field(default=None, gt=0)
    # Timeout guard of an orbits stop; null for a duration stop, so the serialized form
    # validates again (T4 review F4).
    max_duration_periods: float | None = Field(default=None, gt=1.0)
    duration_s: float | None = Field(default=None, gt=0.0)

    @model_validator(mode="before")
    @classmethod
    def _orbits_default_guard(cls, data: Any) -> Any:
        orbits_stop = isinstance(data, dict) and data.get("orbits") is not None
        if orbits_stop and data.get("max_duration_periods") is None:
            return {**data, "max_duration_periods": 1.1}  # M1 default
        return data

    @model_validator(mode="after")
    def _exactly_one(self) -> StopConditionV2:
        if (self.orbits is None) == (self.duration_s is None):
            raise ValueError("stop needs exactly one of orbits or duration_s")
        if self.duration_s is not None and self.max_duration_periods is not None:
            raise ValueError("max_duration_periods applies only to an orbits stop")
        return self


def _require_int_two(value: object) -> object:
    if type(value) is not int:  # Literal[2] alone would accept 2.0 (cf. REV-T3-06)
        raise ValueError("schema_version must be the integer 2")
    return value


class ScenarioV2(Scenario):
    """Scenario schema version 2 (M2): propulsion, command timeline, duration stop."""

    schema_version: Annotated[Literal[2], BeforeValidator(_require_int_two)] = 2  # type: ignore[assignment]
    stop: StopConditionV2  # type: ignore[assignment]
    spacecraft: SpacecraftConfig | None = None
    commands: tuple[TimelineEntry, ...] = ()

    @model_validator(mode="after")
    def _timeline_on_tick_grid(self) -> ScenarioV2:
        if self.stop.duration_s is not None:
            _tick_count(self.stop.duration_s, self.dt_s, "stop.duration_s")
        previous = 0.0
        for i, entry in enumerate(self.commands):
            _tick_count(entry.submit_t_s, self.dt_s, f"commands[{i}].submit_t_s")
            if entry.submit_t_s < previous:
                raise ValueError("commands must be in non-decreasing submit_t_s order")
            if self.stop.duration_s is not None and entry.submit_t_s >= self.stop.duration_s:
                raise ValueError(f"commands[{i}] is submitted at or after the stop time")
            previous = entry.submit_t_s
        return self

    @property
    def stop_tick(self) -> int | None:
        """Final tick of a duration stop; None for an orbits stop."""
        if self.stop.duration_s is None:
            return None
        return _tick_count(self.stop.duration_s, self.dt_s, "stop.duration_s")

    def submit_tick(self, entry: TimelineEntry) -> int:
        return _tick_count(entry.submit_t_s, self.dt_s, "submit_t_s")


def parse_scenario(text: str) -> Scenario:
    """Validate scenario JSON; ``"schema_version": 2`` (the integer) selects version 2."""
    try:
        version = json.loads(text).get("schema_version")
    except (ValueError, AttributeError):  # not JSON or not an object: v1 reports it
        version = None
    if type(version) is int and version == 2:
        return ScenarioV2.model_validate_json(text)
    return Scenario.model_validate_json(text)


def load_scenario(path: str | Path) -> Scenario:
    return parse_scenario(Path(path).read_text())
