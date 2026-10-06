"""Versioned Proof thresholds and the common validator result type."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from tars.events.schema import ValidationResult

REPO_ROOT = Path(__file__).resolve().parents[3]
M1_THRESHOLDS = REPO_ROOT / "proof" / "thresholds" / "m1.json"


@dataclass(frozen=True)
class Thresholds:
    status: Literal["provisional", "approved"]
    limits: dict[str, dict[str, float | None]]

    def for_validator(self, name: str) -> dict[str, float]:
        """Gated (non-null) upper limits for one validator."""
        return {k: v for k, v in self.limits.get(name, {}).items() if v is not None}


def load_thresholds(path: Path = M1_THRESHOLDS) -> Thresholds:
    data = json.loads(path.read_text())
    return Thresholds(status=data["status"], limits=data["limits"])


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
