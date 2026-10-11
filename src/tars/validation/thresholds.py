"""Versioned Proof thresholds and the common validator result type."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from tars.events.schema import ValidationResult

REPO_ROOT = Path(__file__).resolve().parents[3]
M1_THRESHOLDS = REPO_ROOT / "proof" / "thresholds" / "m1.json"
M2_THRESHOLDS = REPO_ROOT / "proof" / "thresholds" / "m2.json"


@dataclass(frozen=True)
class Thresholds:
    status: Literal["provisional", "approved"]
    limits: dict[str, dict[str, float | None]]

    def for_validator(self, name: str) -> dict[str, float]:
        """Gated (non-null) upper limits for one validator."""
        return {k: v for k, v in self.limits.get(name, {}).items() if v is not None}


# Every threshold group must be consumed by a validator; a typo must not silently
# disable gating (REV-010).
KNOWN_VALIDATORS = frozenset(
    {
        "mission", "invariants", "kepler_reference", "period", "convergence",
        "determinism", "architecture", "gmat_reference", "cross_platform",
    }
)  # fmt: skip


def load_thresholds(path: Path = M1_THRESHOLDS) -> Thresholds:
    data = json.loads(path.read_text())
    unknown = sorted(set(data["limits"]) - KNOWN_VALIDATORS)
    if unknown:
        raise ValueError(f"threshold groups match no validator: {unknown}")
    if data["status"] not in ("provisional", "approved"):
        raise ValueError(f"invalid threshold status {data['status']!r}")
    return Thresholds(status=data["status"], limits=data["limits"])


# M2 groups (DR-0015 oracles O1-O8 and telemetry accounting). Limits are scoped per
# mission: "all", or a reference-mission name; a mission entry overrides "all".
M2_KNOWN_VALIDATORS = frozenset(
    {
        "o1_mass_law", "o2_rocket_equation", "o3_free_space", "o4_reference",
        "o5_coast_kepler", "o6_impulsive_limit", "o7_direction", "o8_convergence",
        "accounting",
    }
)  # fmt: skip


@dataclass
class ScopedThresholds:
    """M2 thresholds: ``limits[group][scope][metric]``, scope "all" or a mission name.

    Every (group, scope) entry must be consumed by a validator; ``unused()`` lists
    those that were not, so a misspelt mission cannot silently disable a gate.
    """

    status: Literal["provisional", "approved"]
    limits: dict[str, dict[str, dict[str, float | None]]]
    _used: set[tuple[str, str]] = field(default_factory=set)

    def for_validator(self, name: str, mission: str = "all") -> dict[str, float]:
        group = self.limits.get(name, {})
        merged: dict[str, float | None] = {}
        for scope in ("all", mission):
            if scope in group:
                self._used.add((name, scope))
                merged.update(group[scope])
        return {k: v for k, v in merged.items() if v is not None}

    def unused(self) -> list[str]:
        return sorted(
            f"{g}/{s}" for g, scopes in self.limits.items() for s in scopes
            if (g, s) not in self._used
        )  # fmt: skip


def load_scoped_thresholds(
    path: Path = M2_THRESHOLDS, missions: frozenset[str] = frozenset()
) -> ScopedThresholds:
    data = json.loads(path.read_text())
    unknown = sorted(set(data["limits"]) - M2_KNOWN_VALIDATORS)
    if unknown:
        raise ValueError(f"threshold groups match no validator: {unknown}")
    scopes = {s for group in data["limits"].values() for s in group}
    bad = sorted(scopes - missions - {"all"})
    if bad:
        raise ValueError(f"threshold scopes match no mission: {bad}")
    if data["status"] not in ("provisional", "approved"):
        raise ValueError(f"invalid threshold status {data['status']!r}")
    return ScopedThresholds(status=data["status"], limits=data["limits"])


@dataclass
class Check:
    """Outcome of one validator: metrics compared with upper-limit thresholds."""

    validator: str
    metrics: dict[str, float]
    thresholds: dict[str, float]
    threshold_status: Literal["provisional", "approved"]
    notes: str = ""
    failures: list[str] = field(init=False)

    def __post_init__(self) -> None:
        missing = sorted(set(self.thresholds) - set(self.metrics))
        if missing:
            raise KeyError(f"{self.validator}: thresholds for unknown metrics {missing}")
        self.failures = [
            f"{name}={self.metrics[name]:.6g} > {limit:.6g}"
            for name, limit in sorted(self.thresholds.items())
            if not self.metrics[name] <= limit  # NaN fails
        ]

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_event(self) -> ValidationResult:
        return ValidationResult(
            tick=0,
            t=0.0,
            validator=self.validator,
            passed=self.passed,
            metrics=self.metrics,
            thresholds=self.thresholds,
            threshold_status=self.threshold_status,
            notes=self.notes if self.passed else "; ".join([*self.failures, self.notes]),
        )
