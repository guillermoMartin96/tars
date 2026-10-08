"""Machine-readable scenario configuration (ADR-0005)."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tars.sim.constants import EARTH_CONSTANTS, EarthConstants


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
    orbits: int = Field(gt=0)
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
    force_models: tuple[Literal["point_mass_gravity"], ...] = ("point_mass_gravity",)
    integrator: Literal["rk4"] = "rk4"
    dt_s: float = Field(gt=0.0)
    initial_orbit: CircularOrbit
    stop: StopCondition
    telemetry: Telemetry

    @model_validator(mode="after")
    def _sampling_on_tick_grid(self) -> Scenario:
        ratio = self.telemetry.sample_interval_s / self.dt_s
        if ratio < 1.0 or not math.isclose(ratio, round(ratio), rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("telemetry.sample_interval_s must be a positive multiple of dt_s")
        if len(set(self.force_models)) != len(self.force_models):
            raise ValueError("force_models must not repeat")
        return self

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


def load_scenario(path: str | Path) -> Scenario:
    return Scenario.model_validate_json(Path(path).read_text())
