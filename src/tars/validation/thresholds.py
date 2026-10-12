"""Versioned Proof thresholds and the common validator result type."""

from __future__ import annotations

import json
import math
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


def _require_finite_limits(limits: object, depth: int, where: str = "limits") -> None:
    """Exact nesting, then every metric leaf null or a finite, nonnegative real number
    (reviews M2-T6 F15, F17). JSON such as 1e999 parses as infinity and would disable a
    gate; an object at a metric leaf would crash the checks.

    ``depth`` is the number of mapping levels above the metric leaves: 2 for M1
    (group -> metric), 3 for M2 (group -> scope -> metric).
    """
    if depth > 0:
        if not isinstance(limits, dict):
            raise ValueError(f"threshold {where} must be an object")
        for key, value in limits.items():
            _require_finite_limits(value, depth - 1, f"{where}.{key}")
        return
    if limits is None:
        return
    if isinstance(limits, bool) or not isinstance(limits, (int, float)):
        raise ValueError(f"threshold {where} is not a number: {limits!r}")
    if not math.isfinite(limits) or limits < 0:
        raise ValueError(f"threshold {where} must be finite and nonnegative: {limits!r}")


def _authenticate(raw: bytes, key: str) -> None:
    """The threshold file is the reviewed one (review M2-T6 F33): finite but inflated
    limits would otherwise disable gates while passing every structural check."""
    import hashlib

    from tars.validation.approved_digests import APPROVED_THRESHOLD_SHA256

    digest = hashlib.sha256(raw).hexdigest()
    if digest != APPROVED_THRESHOLD_SHA256[key]:
        raise ValueError(
            f"{key} thresholds are not the approved file (sha256 {digest}); a reviewed "
            "change must update tars.validation.approved_digests"
        )


def load_thresholds(path: Path = M1_THRESHOLDS, authenticate: bool = True) -> Thresholds:
    """Load M1 thresholds. ``authenticate=False`` only for tests of malformed files."""
    raw = path.read_bytes()
    if authenticate:
        _authenticate(raw, "m1")
    data = json.loads(raw)
    unknown = sorted(set(data["limits"]) - KNOWN_VALIDATORS)
    if unknown:
        raise ValueError(f"threshold groups match no validator: {unknown}")
    if data["status"] not in ("provisional", "approved"):
        raise ValueError(f"invalid threshold status {data['status']!r}")
    _require_finite_limits(data["limits"], depth=2)
    return Thresholds(status=data["status"], limits=data["limits"])


# M2 groups (DR-0015 oracles O1-O8 and telemetry accounting). Limits are scoped per
# mission: "all", or a reference-mission name; a mission entry overrides "all".
M2_KNOWN_VALIDATORS = frozenset(
    {
        "o1_mass_law", "o2_rocket_equation", "o3_free_space", "o4_reference",
        "o5_coast_kepler", "o6_impulsive_limit", "o7_direction", "o8_convergence",
        "accounting", "orbit_events", "o9_gmat",
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
    path: Path = M2_THRESHOLDS, missions: frozenset[str] = frozenset(), authenticate: bool = True
) -> ScopedThresholds:
    """Load M2 thresholds. ``authenticate=False`` only for tests of malformed files."""
    raw = path.read_bytes()
    if authenticate:
        _authenticate(raw, "m2")
    data = json.loads(raw)
    unknown = sorted(set(data["limits"]) - M2_KNOWN_VALIDATORS)
    if unknown:
        raise ValueError(f"threshold groups match no validator: {unknown}")
    scopes = {s for group in data["limits"].values() for s in group}
    bad = sorted(scopes - missions - {"all"})
    if bad:
        raise ValueError(f"threshold scopes match no mission: {bad}")
    if data["status"] not in ("provisional", "approved"):
        raise ValueError(f"invalid threshold status {data['status']!r}")
    _require_finite_limits(data["limits"], depth=3)
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
        # A gated metric must be finite and within its limit: NaN, +inf and -inf all
        # fail (review M2-T6 F20; -inf would otherwise satisfy any upper limit).
        self.failures = [
            f"{name}={self.metrics[name]:.6g} > {limit:.6g}"
            if math.isfinite(self.metrics[name])
            else f"{name}={self.metrics[name]!r} is not finite"
            for name, limit in sorted(self.thresholds.items())
            if not (math.isfinite(self.metrics[name]) and self.metrics[name] <= limit)
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
